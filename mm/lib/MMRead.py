__version__ = "$Id$"

# MMRead -- Multimedia tree reading interface

# These routines raise an exception if the input is ill-formatted,
# but first they print a nicely formatted error message


from MMExc import *		# Exceptions
import MMParser
import MMNode
import MMCache
import sys
import os


# Read a CMF file, given by url
#
def ReadFile(url):
	if os.name == 'mac':
		import splash
		splash.splash('loaddoc')	# Show "loading document" splash screen
	rv = ReadFileContext(url, _newctx())
	if os.name == 'mac':
		splash.splash('initdoc')	# and "Initializing document" (to be removed in mainloop)
	return rv

def ReadFileContext(url, context):
	import os, MMurl, posixpath
	utype, str = MMurl.splittype(url)
	host, path = MMurl.splithost(str)
	dir = posixpath.dirname(path)
	if host:
		dir = '//%s%s' % (host, dir)
	if utype:
		dir = '%s:%s' % (utype, dir)
	context.setdirname(dir)
	if not utype and not host:
		root = MMCache.loadcache(MMurl.url2pathname(url), context)
	else:
		root = None
	if root:
		_fixcontext(root)
		return root
	# no cache file, parse the file and create the cache (if possible)
	u = MMurl.urlopen(url)
	root = ReadOpenFileContext(u, url, context)
	if not utype and not host:
		import MMWrite
		MMWrite.fixroot(root)
		MMCache.dumpcache(root, MMurl.url2pathname(url))
		MMWrite.unfixroot(root)
	return root


# Read a CMF file that is already open (for reading)
#
def ReadOpenFile(fp, filename):
	return ReadOpenFileContext(fp, filename, _newctx())

def ReadOpenFileContext(fp, filename, context):
	p = MMParser.MMParser(fp, context)
	return _readparser(p, filename)


# Read a CMF file from a string
#
def ReadString(string, name):
	return ReadStringContext(string, name, _newctx())

def ReadStringContext(string, name, context):
	import StringIO
	p = MMParser.MMParser(StringIO.StringIO(string), context)
	return _readparser(p, name)


# Private functions to read nodes

def _newctx():
	return MMNode.MMNodeContext(MMNode.MMNode)

def _readparser(p, filename):
	#
	# Read a single node (this is a whole tree!) from the file.
	# If an error occurs, format a nice error message, and
	# re-raise the exception as an MSyntaxError.
	#
	try:
		root = p.getnode()
	except EOFError:
		tb = sys.exc_traceback
		p.reporterror(filename, 'Unexpected EOF', sys.stderr)
		raise MSyntaxError, 'Unexpected EOF', tb
	except MSyntaxError, msg:
		if hasattr(sys, 'exc_info'):
			tb = sys.exc_info()[2]
		else:
			tb = sys.exc_traceback
		if type(msg) is type(()):
			gotten, expected = msg
			msg = 'got "'+gotten+'", expected "'+expected+'"'
		p.reporterror(filename, 'Syntax error: ' + msg, sys.stderr)
		raise MSyntaxError, msg, tb
	except MTypeError, msg:
		if hasattr(sys, 'exc_info'):
			tb = sys.exc_info()[2]
		else:
			tb = sys.exc_traceback
		if type(msg) is type(()):
			gotten, expected = msg
			msg = 'got "'+gotten+'", expected "'+expected+'"'
		p.reporterror(filename, 'Type error: ' + msg, sys.stderr)
		raise MSyntaxError, msg, tb
	#
	# Make sure that there is no garbage in the file after the node.
	#
	token = p.peektoken()
	if token <> '':
		msg = 'Node ends before EOF'
		p.reporterror(filename, msg, sys.stderr)
		raise MSyntaxError, msg
	#
	_fixcontext(root)
	return root

def _fixcontext(root):
##	#
##	# Move the style dictionary from the root attribute list
##	# to the context.
##	#
##	try:
##		root.context.addstyles(root.GetRawAttr('styledict'))
##		root.DelAttr('styledict')
##	except NoSuchAttrError:
##		pass
	#
	# Move the hyperlink list from the root attribute list
	# to the context.
	#
	try:
		root.context.addhyperlinks(root.GetRawAttr('hyperlinks'))
		root.DelAttr('hyperlinks')
	except NoSuchAttrError:
		pass
	#
	# Move the channel list from the root attribute list
	# to the context.
	#
	try:
		root.context.addchannels(root.GetRawAttr('channellist'))
		root.DelAttr('channellist')
	except NoSuchAttrError:
		pass

	try:
		root.context.addlayouts(root.GetRawAttr('layouts'))
		root.DelAttr('layouts')
	except NoSuchAttrError:
		pass
