__version__ = "$Id$"

# Main program for the CMIF player.

import sys
import os

try:
	sys.path.remove('')
except:
	pass

## if os.name == 'posix' and __file__ != '<frozen>':
## 	import fastimp
## 	fastimp.install()

import getopt

def usage(msg):
	sys.stdout = sys.stderr
	print msg
	print 'usage: grins file ...'
	print 'file ...   : one or more SMIL or CMIF files or URLs'
	sys.exit(2)

from MainDialog import MainDialog
from usercmd import *

from version import version

class Main(MainDialog):
	def __init__(self, opts, files):
		import windowinterface, features
		if hasattr(features, 'expiry_date') and features.expiry_date:
			import time
			import version
			tm = time.localtime(time.time())
			yymmdd = tm[:3]
			if yymmdd > features.expiry_date:
				rv = windowinterface.GetOKCancel(
				   "This beta copy of GRiNS has expired.\n\n"
				   "Do you want to check www.oratrix.com for a newer version?")
				if rv == 0:
					url = 'http://www.oratrix.com/indir/%s/update.html'%version.shortversion
					windowinterface.htmlwindow(url)
				sys.exit(0)
		self.tmpopts = opts
		self.tmpfiles = files
		if hasattr(features, 'license_features_needed') and features.license_features_needed:
			import license
			self.tmplicensedialog = license.WaitLicense(self.do_init,
					   features.license_features_needed)
		else:
			self.do_init()
				
	def do_init(self, license=None):
		# We ignore the license, not needed in the player
		import MMurl, TopLevel, windowinterface
		opts, files = self.tmpopts, self.tmpfiles
		del self.tmpopts
		del self.tmpfiles
		self._tracing = 0
		self.nocontrol = 0	# For player compatability
		self._closing = 0
		self._mm_callbacks = {}
		self.tops = []
		self.last_location = ''
		try:
			import mm, posix, fcntl, FCNTL
		except ImportError:
			pass
		else:
			pipe_r, pipe_w = posix.pipe()
			mm.setsyncfd(pipe_w)
			self._mmfd = pipe_r
			windowinterface.select_setcallback(pipe_r,
						self._mmcallback,
						(posix.read, fcntl.fcntl, FCNTL))
		self.commandlist = [
			OPEN(callback = (self.open_callback, ())),
			OPENFILE(callback = (self.openfile_callback, ())),
			OPEN_RECENT(callback = self.open_recent_callback),	# Dynamic cascade
#			RELOAD(callback = (self.reload_callback, ())), 
			PREFERENCES(callback = (self.preferences_callback, ())),
			CHECKVERSION(callback=(self.checkversion_callback, ())),
			EXIT(callback = (self.close_callback, ())),
			]
		import settings
		if settings.get('debug'):
			self.commandlist = self.commandlist + [
				TRACE(callback = (self.trace_callback, ())),
				DEBUG(callback = (self.debug_callback, ())),
				CRASH(callback = (self.crash_callback, ())),
				]
		MainDialog.__init__(self, 'GRiNS')
		# first open all files
		for file in files:
			self.openURL_callback(MMurl.guessurl(file))
		self._update_recent(None)
		# then play them
		for top in self.tops:
			top.player.playsubtree(top.root)

	def openURL_callback(self, url):
		import windowinterface
		windowinterface.setwaiting()
		from MMExc import MSyntaxError
		import TopLevel
		self.last_location = url
		try:
			top = TopLevel.TopLevel(self, url)
		except IOError:
			import windowinterface
			windowinterface.showmessage('error opening document %s' % url)
		except MSyntaxError:
			import windowinterface
			windowinterface.showmessage('parsing document %s failed' % url)
		else:
			self.tops.append(top)
			top.show()
			top.player.show()
			self._update_recent(url)

	def open_recent_callback(self, url):
		self.openURL_callback(url)
		
	def _update_recent(self, url):
		if not hasattr(self, 'set_recent_list'):
			return
		import settings
		import posixpath
		recent = settings.get('recent_documents')
		if url:
			if url in recent:
				recent.remove(url)
			recent.insert(0, url)
			if len(recent) > 5:
				recent = recent[:5]
			settings.set('recent_documents', recent)
			settings.save()
		doclist = []
		for url in recent:
			base = posixpath.basename(url)
			doclist.append( (base, (url,)))
		self.set_recent_list(doclist)

#	def reload_callback(self):
#		# er.. on which toplevel?
#		print "DEBUG: grins.py: reload_callback called."
#		print "DEBUG: self.tops is: ", self.tops
#		for i in self.tops:
#			i.reload_callback()

	def close_callback(self, exitcallback=None):
		for top in self.tops[:]:
			top.destroy()
		if sys.platform == 'mac':
			import MacOS
			MacOS.OutputSeen()
		if exitcallback:
			rtn, arg = exitcallback
			apply(rtn, arg)
		else:
			raise SystemExit, 0

	def crash_callback(self):
		raise 'Crash requested by user'

	def debug_callback(self):
		import pdb
		pdb.set_trace()

	def trace_callback(self):
		import trace
		if self._tracing:
			trace.unset_trace()
			self._tracing = 0
		else:
			self._tracing = 1
			trace.set_trace()

	def preferences_callback(self):
		import Preferences
		Preferences.showpreferences(1, self.prefschanged)

	def prefschanged(self):
		for top in self.tops:
			top.prefschanged()

	def checkversion_callback(self):
		import MMurl
		import version
		import windowinterface
		import settings
		import string
## For this verion we send the user to the web and let them check for themselves
		url = 'http://www.oratrix.com/indir/%s/update.html'%version.shortversion
##		url = 'http://www.oratrix.com/indir/%s/updatecheck.txt'%version.shortversion
##		try:
##			fp = MMurl.urlopen(url)
##			data = fp.read()
##			fp.close()
##		except:
##			windowinterface.showmessage('Unable to check for upgrade. You can try again later, or visit www.oratrix.com with your webbrowser.')
##			return
##		if not data:
##			windowinterface.showmessage('You are running the latest version of the software')
##			return
##		cancel = windowinterface.GetOKCancel('There appears to be a newer version!\nDo you want to hear more?')
##		if cancel:
##			return
##		data = string.strip(data)
##		# Pass the version and the second item of the license along.
##		id = string.split(settings.get('license'), '-')[1]
##		url = '%s?version=%s&id=%s'%(data, version.shortversion, id)
		windowinterface.htmlwindow(url)

	def closetop(self, top):
		if self._closing:
			return
		self._closing = 1
		self.tops.remove(top)
		top.hide()
		if len(self.tops) == 0:
			# no TopLevels left: exit
			sys.exit(0)
		self._closing = 0

	def run(self):
		import windowinterface
		windowinterface.mainloop()

	def setmmcallback(self, dev, callback):
		if callback:
			self._mm_callbacks[dev] = callback
		elif self._mm_callbacks.has_key(dev):
			del self._mm_callbacks[dev]

	def _mmcallback(self, read, fcntl, FCNTL):
		# set in non-blocking mode
		dummy = fcntl(self._mmfd, FCNTL.F_SETFL, FCNTL.O_NDELAY)
		# read a byte
		devval = read(self._mmfd, 1)
		# set in blocking mode
		dummy = fcntl(self._mmfd, FCNTL.F_SETFL, 0)
		# return if nothing read
		if not devval:
			return
		devval = ord(devval)
		dev, val = devval >> 2, devval & 3
		if self._mm_callbacks.has_key(dev):
			func = self._mm_callbacks[dev]
			func(val)
		else:
			print 'Warning: unknown device in mmcallback'

def main():
	try:
		opts, files = getopt.getopt(sys.argv[1:], 'qj:')
	except getopt.error, msg:
		usage(msg)
	if not files and sys.platform not in ('mac', 'win32'):
		usage('No files specified')

	if sys.argv[0] and sys.argv[0][0] == '-':
		sys.argv[0] = 'grins'

	try:
		import splash
	except ImportError:
		splash = None
	else:
		splash.splash(version = 'GRiNS ' + version)

##	import Help
##	if hasattr(Help, 'sethelpprogram'):
##		Help.sethelpprogram('player')
		
	import settings
	kbd_int = KeyboardInterrupt
	if ('-q', '') in opts:
		sys.stdout = open('/dev/null', 'w')
	elif settings.get('debug'):
		try:
			import signal, pdb
		except ImportError:
			pass
		else:
			signal.signal(signal.SIGINT,
				      lambda s, f, pdb=pdb: pdb.set_trace())
			kbd_int = 'dummy value to prevent interrupts to be caught'

## 	for fn in files:
## 		try:
## 			# Make sure the files exist first...
## 			f = open(fn, 'r')
## 			f.close()
## 		except IOError, msg:
## 			import types
## 			if type(msg) is types.InstanceType:
## 				msg = msg.strerror
## 			else:
## 				msg = msg[1]
## 			sys.stderr.write('%s: cannot open: %s\n' % (fn, msg))
## 			sys.exit(2)

## 	# patch the module search path
## 	# so we are less dependent on where we are called
## 	sys.path.append(findfile('lib'))
## 	sys.path.append(findfile('video'))

##	import mimetypes, grins_mimetypes
##	mimetypes.types_map.update(grins_mimetypes.mimetypes)

	import Channel
	import GLLock

	GLLock.init()
	import windowinterface
	windowinterface.usewindowlock(GLLock.gl_lock)

	m = Main(opts, files)

	if splash is not None:
		splash.unsplash()

	try:
		try:
			m.run()
		except kbd_int:
			print 'Interrupt.'
		except SystemExit, sts:
			if type(sts) is type(m):
				if sts.code:
					print 'Exit %d' % sts.code
			elif sts:
				print 'Exit', sts
			sys.last_traceback = None
			sys.exc_traceback = None
			sys.exit(sts)
		except:
			sys.stdout = sys.stderr
			if hasattr(sys, 'exc_info'):
				exc_type, exc_value, exc_traceback = sys.exc_info()
			else:
				exc_type, exc_value, exc_traceback = sys.exc_type, sys.exc_value, sys.exc_traceback
			if __debug__:
				import traceback, pdb
				print
				print '\t-------------------------------------------------'
				print '\t| Fatal error - Please mail this output to      |'
				print '\t| grins-support@oratrix.com with a description  |'
				print '\t| of the circumstances.                         |'
				print '\t-------------------------------------------------'
				print
				traceback.print_exception(exc_type, exc_value, exc_traceback)
				print
				pdb.post_mortem(exc_traceback)
			else:
				import traceback
				print
				print 'GRiNS crash, please e-mail this output to grins-support@cwi.nl:'
				traceback.print_exception(exc_type, exc_value, exc_traceback)
	finally:
		import windowinterface
		windowinterface.close()


# A copy of cmif.findfile().  It is copied here rather than imported
# because the result is needed to extend the Python search path to
# find the cmif module!

# WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING
# *********  If you change this, also change ../lib/cmif.py   ***********
# WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING

cmifpath = None

def findfile(name):
	global cmifpath
	if os.path.isabs(name):
		return name
	if cmifpath is None:
		if os.environ.has_key('CMIFPATH'):
			import string
			var = os.environ['CMIFPATH']
			cmifpath = string.splitfields(var, ':')
		elif os.environ.has_key('CMIF'):
			cmifpath = [os.environ['CMIF']]
		else:
			import sys
			cmifpath = [os.path.split(sys.executable)[0]]
			try:
				link = os.readlink(sys.executable)
			except (os.error, AttributeError):
				pass
			else:
				cmifpath.append(os.path.dirname(os.path.join(os.path.dirname(sys.executable), link)))
	for dir in cmifpath:
		fullname = os.path.join(dir, name)
		if os.path.exists(fullname):
			return fullname
	return name


# Call the main program

main()
