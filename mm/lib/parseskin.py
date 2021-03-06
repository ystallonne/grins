__version__ = "$Id$"

class error(Exception):
    pass

# The syntax for a GRiNS skin description file is very simple:
#
# Comments start with the character # and extend to the end of the
# line; empty lines are ignored.
#
# Lines consist of a keyword and parameters, separated from each other
# by white space.  The available keywords and their parameters are:
#
# "image"       URL of image file (relative to skin definition file)
# "display"     4 numbers giving x, y, width, height
# "displayimage" URL of image file (relative to skin definition file)
# "displaybgcolor" 3 numbers in range 0 - 255 giving red, green, and blue values
# "key"         key shape coordinates
# command       shape coordinates
# component     URI
# profile       profile name
# SmilBaseSet   "SMIL-3GPP-R4" or "SMIL-3GPP-R5"
# SmilModules   list of SMIL module names
#
# The "image" is the URL of the image that is used for the skin.  The
# "displayimage" is the URL of an image that, if specified, is
# displayed in the "display" area when the document is being played.
# The "displaybgcolor" is the background color of the "display" area
# when the document is being played.
#
# The key is a single, possibly quoted, character.  If either ", ', or
# a space character needs to be specified, it must be surrounded with
# quotes, otherwise quotes are optional.  Use ' to quote " and v.v.
# Some special characters can also be specified: Use \t for TAB, \r
# for ENTER, \b for BACKSPACE, and \n for LINEFEED.
#
# The possible commands are:
# "skin", "open", "play", "pause", "stop", "exit", "tab".
#
# The possible shapes and coordinates are:
# "rect" with 4 numbers giving x, y, width, and height;
# "circle" with 3 numbers giving x, y, and radius;
# "poly" with an even number of numbers, each pair describing the x
# and y coordinates of a point.
#
# A special shape is "rocker".  The possible 'coordinates' for the
# "rocker" shape are "left", "right", "up", "down", "center".
#
# The component command may be repeated and all components are
# returned as a single list
#
# The profile can be one of (without the quotes):
#       "SMIL 2.0 Language Profile" (default)
#       "3GPP PSS5 Profile"
#       "3GPP PSS4 Profile"
#       "SMIL 2.0 Basic Language Profile"
#       "SMIL MMS Profile"
#
# In addition to the above commands, you can also have lines to set
# preference settings.  Any setting that can be set in the grprefs
# file can be set here with the same syntax.  E.g.
#       system_bitrate = 33600
#       centerskin = 0
#
# Example skin definition file:
#       image Classic.gif
#       display 0 0 240 268
#       play rect 12 272 18 18                  # Play Icon
#       pause rect 32 272 18 18                 # Pause Icon
#       stop rect 54 272 18 18                  # Stop
#       exit rect 143 275 18 18                 # Exit Button
#       open rect 86 272 18 18                  # Open File Button
#       skin rect 110 272 18 18
#       tab rocker right                        # right side of rocker panel
#       activate rocker center                  # center of rocker panel
#       profile 3GPP PSS5 Profile               # use 3GPP PSS5 profile

import string                           # for whitespace
import re
import settings

# we cheat: we're not nearly so fuzzy as we claim to be
mms = re.compile(r'\bmms\b', re.IGNORECASE)
pss4 = re.compile(r'\bpss4\b', re.IGNORECASE)
pss5 = re.compile(r'\bpss5\b', re.IGNORECASE)
basic = re.compile(r'\bbasic\b', re.IGNORECASE)

settingre = re.compile(r'(?P<key>[a-zA-Z][a-zA-Z0-9_]*)\s*=')

def parsegskin(file):
    dict = {}
    lineno = 0
    profile = settings.current_profile
    modules = []
    prefs = {}
    while 1:
        line = file.readline()
        if not line:
            break
        lineno = lineno + 1

        # ignore comments and empty lines
        # and strip off white space
        i = line.find('#')
        if i >= 0:
            line = line[:i]
        line = line.strip()
        if not line:
            continue

        res = settingre.match(line)
        if res is not None and \
           settings.default_settings.has_key(res.group('key')):
            exec line in prefs, prefs
            continue

        # first part is GRiNS command
        line = line.split(None, 1)
        if len(line) == 1:
            raise error, 'syntax error in skin on line %d' % lineno
        cmd, rest = line
        if cmd in ('image', 'displayimage'):
            if dict.has_key(cmd):
                # only one image allowed
                raise error, 'syntax error in skin on line %d: only one %s allowed' % (lineno, cmd)
            dict[cmd] = rest.strip()
            continue
        if cmd == 'displaybgcolor':
            try:
                bgcolor = map(lambda v: int(v, 0), rest.split())
            except ValueError:
                raise error, 'syntax error in skin on line %d' % lineno
            if len(bgcolor) != 3 or \
               not (0 <= bgcolor[0] <= 255) or \
               not (0 <= bgcolor[1] <= 255) or \
               not (0 <= bgcolor[2] <= 255):
                raise error, 'syntax error in skin on line %d' % lineno
            dict[cmd] = bgcolor
            continue
        if cmd == 'component':
            v = rest.strip()
            if dict.has_key('component'):
                dict['component'].append(v)
            else:
                dict['component'] = [v]
            continue
        if cmd == 'profile':
            if mms.search(rest) is not None:
                profile = settings.SMIL_MMS_MODULES
            elif pss4.search(rest) is not None:
                profile = settings.SMIL_PSS4_MODULES
            elif pss5.search(rest) is not None:
                profile = settings.SMIL_PSS5_MODULES
            elif basic.search(rest) is not None:
                profile = settings.SMIL_BASIC_MODULES
            else:
                profile = settings.SMIL_20_MODULES
            continue
        if cmd == 'SmilBaseSet':
            if rest == 'SMIL-3GPP-R4':
                profile = settings.SMIL_PSS4_MODULES
            elif rest == 'SMIL-3GPP-R5':
                profile = settings.SMIL_PSS5_MODULES
            continue
        if cmd == 'SmilModules':
            modules.extend(rest.split())
            continue
        if cmd == 'key':
            quote = None
            backslash = 0
            key = None
            rest = list(rest) # easier to manipiulate list
            while rest:
                c = rest[0]
                del rest[0]
                if quote is not None:
                    if c == quote:
                        quote = None
                    elif backslash:
                        if key is None:
                            if c == '\\':
                                key = '\\'
                            elif c == 'r':
                                key = '\r'
                            elif c == 't':
                                key = '\t'
                            elif c == 'n':
                                key = '\n'
                            elif c == 'b':
                                key = '\b'
                            else:
                                key = c
                        else:
                            raise error, 'syntax error in skin on line %d: only single character allowed for key' % lineno
                        backslash = 0
                    elif c == '\\':
                        backslash = 1
                    elif key is None:
                        key = c
                    else:
                        raise error, 'syntax error in skin on line %d: only single character allowed for key' % lineno
                elif c == '"' or c == "'":
                    quote = c
                elif c in string.whitespace:
                    if key is not None:
                        break
                elif backslash:
                    if key is None:
                        if c == '\\':
                            key = '\\'
                        elif c == 'r':
                            key = '\r'
                        elif c == 't':
                            key = '\t'
                        elif c == 'n':
                            key = '\n'
                        elif c == 'b':
                            key = '\b'
                        else:
                            key = c
                    else:
                        raise error, 'syntax error in skin on line %d: only single character allowed for key' % lineno
                    backslash = 0
                elif c == '\\':
                    backslash = 1
                elif key is None:
                    key = c
                else:
                    raise error, 'syntax error in skin on line %d: only single character allowed for key' % lineno
            if key is None:
                raise error, 'syntax error in skin on line %d: no key specified' % lineno
            rest = ''.join(rest) # reassemble string
        coords = rest.split()
        if cmd == 'display':
            # display area is always rectangular
            shape = 'rect'
        else:
            shape = coords[0]
            del coords[0]
        if shape == 'rocker':
            if len(coords) != 1:
                raise error, 'syntas error in skin on line %d' % lineno
            coords = coords[0]
            if coords == 'centre': # undocumented alternative spelling
                coords = 'center'
            if coords not in ('left','right','up','down','center'):
                raise error, 'syntas error in skin on line %d' % lineno
        else:
            try:
                coords = map(lambda v: int(v, 0), coords)
            except ValueError:
                raise error, 'syntax error in skin on line %d' % lineno
            if shape == 'poly' and coords[:2] == coords[-2:]:
                del coords[-2:]
            if (shape != 'rect' or len(coords) != 4) and \
               (shape != 'circle' or len(coords) != 3) and \
               (shape != 'poly' or len(coords) < 6 or len(coords) % 2 != 0):
                raise error, 'syntax error in skin on line %d' % lineno
        if cmd == 'display':
            if dict.has_key(cmd):
                # only one display allowed
                raise error, 'syntax error in skin on line %d' % lineno
            dict[cmd] = shape, coords
        elif cmd == 'key':
            if dict.has_key(cmd):
                dict[cmd].append((shape, coords, key))
            else:
                dict[cmd] = [(shape, coords, key)]
        else:
            if dict.has_key(cmd):
                dict[cmd].append((shape, coords))
            else:
                dict[cmd] = [(shape, coords)]
    if dict.has_key('image') and not dict.has_key('display'):
        raise error, 'display region missing from skin description file'
    settings.switch_profile(profile + modules)
    if prefs:
        try:
            settings.transaction()
        except settings.Error:
            skipcommit = 1
        else:
            skipcommit = 0
        for key, val in prefs.items():
            if key[:1] != '_':
                settings.set(key, val)
        if not skipcommit:
            settings.commit()
    return dict
