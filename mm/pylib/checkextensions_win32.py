"""Extension management for Windows.

Under Windows it is unlikely the .obj files are of use, as special compiler options
are needed (primarily to toggle the behaviour of "public" symbols.

I dont consider it worth parsing the MSVC makefiles for compiler options.  Even if
we get it just right, a specific freeze application may have specific compiler
options anyway (eg, to enable or disable specific functionality)

So my basic stragtegy is:

* Have some Windows INI files which "describe" one or more extension modules.
  (Freeze comes with a default one for all known modules - but you can specify
  your own).
* This description can include:
  - The MSVC .dsp file for the extension.  The .c source file names
    are extraced from there.
  - Specific compiler/linker options
  - Flag to indicate if Unicode compilation is expected.

At the moment the name and location of this INI file is hardcoded,
but an obvious enhancement would be to provide command line options.
"""

import os, string, sys
try:
    import win32api
except ImportError:
    win32api = None # User has already been warned

class CExtension:
    """An abstraction of an extension implemented in C/C++
    """
    def __init__(self, name, sourceFiles):
        self.name = name
        # A list of strings defining additional compiler options.
        self.sourceFiles = sourceFiles
        # A list of special compiler options to be applied to
        # all source modules in this extension.
        self.compilerOptions = []
        # A list of .lib files the final .EXE will need.
        self.linkerLibs = []

    def GetSourceFiles(self):
        return self.sourceFiles

    def AddCompilerOption(self, option):
        self.compilerOptions.append(option)
    def GetCompilerOptions(self):
        return self.compilerOptions

    def AddLinkerLib(self, lib):
        self.linkerLibs.append(lib)
    def GetLinkerLibs(self):
        return self.linkerLibs

def checkextensions(unknown, extra_inis):
    # Create a table of frozen extensions

    defaultMapName = os.path.join( os.path.split(sys.argv[0])[0], "extensions_win32.ini")
    if not os.path.isfile(defaultMapName):
        sys.stderr.write("WARNING: %s can not be found - standard extensions may not be found" % mapFileName)
    else:
        # must go on end, so other inis can override.
        extra_inis.append(defaultMapName)

    ret = []
    for mod in unknown:
        for ini in extra_inis:
#                       print "Looking for", mod, "in", win32api.GetFullPathName(ini),"...",
            if win32api and not os.path.isabs(ini):
                ini = win32api.GetFullPathName(ini)
            defn = get_extension_defn( mod, ini )
            if defn is not None:
#                               print "Yay - found it!"
                ret.append( defn )
                break
#                       print "Nope!"
        else: # For not broken!
            sys.stderr.write("No definition of module %s in any specified map file.\n" % (mod))

    return ret

def get_extension_defn(moduleName, mapFileName):
    if win32api is None: return None
    dsp = win32api.GetProfileVal(moduleName, "dsp", "", mapFileName)
    if dsp=="":
        print 'warning: dsp not found'
        return None

    # We allow environment variables in the file name
    dsp = win32api.ExpandEnvironmentStrings(dsp)
    # If the path to the .DSP file is not absolute, assume it is relative
    # to the description file.
    if not os.path.isabs(dsp):
        dsp = os.path.join( os.path.split(mapFileName)[0], dsp)
    # Parse it to extract the source files.
    sourceFiles = parse_dsp(dsp)
    if sourceFiles is None:
        print 'warning: no source files'
        return None

    module = CExtension(moduleName, sourceFiles)
    # Put the path to the DSP into the environment so entries can reference it.
    os.environ['dsp_path'] = os.path.split(dsp)[0]
    os.environ['ini_path'] = os.path.split(mapFileName)[0]

    cl_options = win32api.GetProfileVal(moduleName, "cl", "", mapFileName)
    if cl_options:
        module.AddCompilerOption(win32api.ExpandEnvironmentStrings(cl_options))

    exclude = win32api.GetProfileVal(moduleName, "exclude", "", mapFileName)
    exclude = string.split(exclude)

    if win32api.GetProfileVal(moduleName, "Unicode", 0, mapFileName):
        module.AddCompilerOption('/D UNICODE /D _UNICODE')

    libs = string.split(win32api.GetProfileVal(moduleName, "libs", "", mapFileName))
    for lib in libs:
        module.AddLinkerLib(win32api.ExpandEnvironmentStrings(lib))

    for exc in exclude:
        if exc in module.sourceFiles:
            modules.sourceFiles.remove(exc)

    return module

# Given an MSVC DSP file, locate C source files it uses
# returns a list of source files.
def parse_dsp(dsp):
#       print "Processing", dsp
    # For now, only support
    ret = []
    dsp_path, dsp_name = os.path.split(dsp)
    try:
        lines = open(dsp, "r").readlines()
    except IOError, msg:
        sys.stderr.write("%s: %s\n" % (dsp, msg))
        return None
    for line in lines:
        fields = string.split(string.strip(line), "=", 2)
        if fields[0]=="SOURCE":
            if string.lower(os.path.splitext(fields[1])[1]) in ['.cpp', '.c']:
                ret.append( win32api.GetFullPathName(os.path.join(dsp_path, fields[1] ) ) )
    return ret

def write_extension_table(fname, modules):
    fp = open(fname, "w")
    try:
        fp.write (ext_src_header)
        # Write fn protos
        for module in modules:
            # bit of a hack for .pyd's as part of packages.
            name = string.split(module.name,'.')[-1]
            fp.write('extern void init%s(void);\n' % (name) )
        # Write the table
        fp.write (ext_tab_header)
        for module in modules:
            name = string.split(module.name,'.')[-1]
            fp.write('\t{"%s", init%s},\n' % (name, name) )

        fp.write (ext_tab_footer)
        fp.write(ext_src_footer)
    finally:
        fp.close()


ext_src_header = """\
#include "Python.h"
"""

ext_tab_header = """\

static struct _inittab extensions[] = {
"""

ext_tab_footer = """\
        /* Sentinel */
        {0, 0}
};
"""

ext_src_footer = """\
extern DL_IMPORT(int) PyImport_ExtendInittab(struct _inittab *newtab);

int PyInitFrozenExtensions()
{
        return PyImport_ExtendInittab(extensions);
}

"""
