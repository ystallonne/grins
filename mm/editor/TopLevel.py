__version__ = "$Id$"

import os, posixpath
import sys
import string
import windowinterface
import MMAttrdefs, MMurl
from urlparse import urlparse, urlunparse
from MMExc import *
from EditMgr import EditMgr
import Timing
from ViewDialog import ViewDialog
from Hlinks import TYPE_JUMP, TYPE_CALL, TYPE_FORK
from usercmd import *
import mimetypes

# an empty document
EMPTY = """
<smil>
  <head>
    <meta name="title" content="root-layout"/>
    <layout>
      <root-layout id="root-layout" title="root-layout" width="640" height="480"/>
    </layout>
  </head>
  <body>
  </body>
</smil>
"""

from TopLevelDialog import TopLevelDialog

Error = 'TopLevel.Error'

class TopLevel(TopLevelDialog, ViewDialog):
	def __init__(self, main, url, new_file):
		import settings
		ViewDialog.__init__(self, 'toplevel_')
		self.select_fdlist = []
		self.select_dict = {}
		self._last_timer_id = None
		self.main = main
		self.new_file = new_file
		self._in_prefschanged = 0
		utype, host, path, params, query, fragment = urlparse(url)
		dir, base = posixpath.split(path)
		if (not utype or utype == 'file') and \
		   (not host or host == 'localhost'):
			# local file
			self.dirname = dir
		else:
			# remote file
			self.dirname = ''
		mtype = mimetypes.guess_type(base)[0]
		if mtype in ('application/x-grins-project', 'application/smil', 'application/x-grins-cmif'):
			self.basename = posixpath.splitext(base)[0]
		else:
			self.basename = base
		url = urlunparse((utype, host, path, params, query, None))
		self.filename = url
		self.window = None
		self.source = None
		self.read_it()

		self.commandlist = [
			PLAY(callback = (self.play_callback, ())),
			PLAYERVIEW(callback = (self.view_callback, (0,))),
			HIERARCHYVIEW(callback = (self.view_callback, (1,))),
			RESTORE(callback = (self.restore_callback, ())),
			CLOSE(callback = (self.close_callback, ())),
			PROPERTIES(callback = (self.prop_callback, ())),

			HIDE_PLAYERVIEW(callback = (self.hide_view_callback, (0,))),
			HIDE_HIERARCHYVIEW(callback = (self.hide_view_callback, (1,))),
			]
		if not settings.get('lightweight'):
			self.commandlist = self.commandlist + [
				CHANNELVIEW(callback = (self.view_callback, (2,))),
				LINKVIEW(callback = (self.view_callback, (3,))),
				LAYOUTVIEW(callback = (self.view_callback, (4,))),
				USERGROUPVIEW(callback = (self.view_callback, (5,))),
				HIDE_CHANNELVIEW(callback = (self.hide_view_callback, (2,))),
				HIDE_LINKVIEW(callback = (self.hide_view_callback, (3,))),
				HIDE_LAYOUTVIEW(callback = (self.hide_view_callback, (4,))),
				HIDE_USERGROUPVIEW(callback = (self.hide_view_callback, (5,))),
				]
		if hasattr(self, 'do_edit'):
			self.commandlist.append(EDITSOURCE(callback = (self.edit_callback, ())))
		#self.__save = None
		if self.main.cansave():
			self.commandlist = self.commandlist + [
				SAVE_AS(callback = (self.saveas_callback, ())),
				SAVE(callback = (self.save_callback, ())),
				EXPORT_SMIL(callback = (self.bandwidth_callback, (self.export_callback,))),
				UPLOAD_SMIL(callback = (self.bandwidth_callback, (self.upload_callback,))),
				]
			#self.__save = SAVE(callback = (self.save_callback, ()))
		import Help
		if hasattr(Help, 'hashelp') and Help.hashelp():
			self.commandlist.append(
				HELP(callback = (self.help_callback, ())))
		if hasattr(self.root, 'source') and \
		   hasattr(windowinterface, 'textwindow'):
			self.commandlist = self.commandlist + [
				SOURCE(callback = (self.source_callback, ())),
				HIDE_SOURCE(callback = (self.hide_source_callback, ())),
				]

		TopLevelDialog.__init__(self)
		self.makeviews()

	def __repr__(self):
		return '<TopLevel instance, url=' + `self.filename` + '>'

	def show(self):
		TopLevelDialog.show(self)
		if self.hierarchyview is not None:
			self.hierarchyview.show()

	def destroy(self):
		self.set_timer(0)
		self.editmgr.unregister(self)
		self.editmgr.destroy()
		self.destroyviews()
		self.hide()
		self.root.Destroy()
		import Clipboard
		type, data = Clipboard.getclip()
		if type == 'node' and data is not None:
			Clipboard.setclip('', None)
			data.Destroy()
		for v in self.views:
			if v is not None:
				v.toplevel = None
		self.views = []
		if self in self.main.tops:
			self.main.tops.remove(self)

	def timer_callback(self):
		self._last_timer_id = None
		self.player.timer_callback()

	def set_timer(self, delay):
		if self._last_timer_id is not None:
			windowinterface.canceltimer(self._last_timer_id)
			self._last_timer_id = None
		if delay:
			self._last_timer_id = windowinterface.settimer(delay,
				  (self.timer_callback, ()))

	#
	# View manipulation.
	#
	def makeviews(self):
		import settings

		import HierarchyView
		self.hierarchyview = HierarchyView.HierarchyView(self)

		import Player
		self.player = Player.Player(self)

		if not settings.get('lightweight'):
			import ChannelView
			self.channelview = ChannelView.ChannelView(self)

			import LinkEdit
			self.links = LinkEdit.LinkEdit(self)

			import LayoutView
			self.layoutview = LayoutView.LayoutView(self)

			import UsergroupView
			self.ugroupview = UsergroupView.UsergroupView(self)
		else:
			import LinkEditLight
			self.links = LinkEditLight.LinkEditLight(self)

			self.channelview = None
			self.layoutview = None
			self.ugroupview = None

		# Views that are destroyed by restore (currently all)
		self.views = [self.player, self.hierarchyview,
			      self.channelview, self.links, self.layoutview,
			      self.ugroupview]

	def hideviews(self):
		for v in self.views:
			if v is not None:
				v.hide()

	def destroyviews(self):
		for v in self.views:
			if v is not None:
				v.destroy()

	def checkviews(self):
		pass

	#
	# Callbacks.
	#
	def play_callback(self):
		self.setwaiting()
		self.player.show((self.player.playsubtree, (self.root,)))

	def source_callback(self):
		import SMILTreeWrite
		self.showsource(SMILTreeWrite.WriteString(self.root))

	def hide_source_callback(self):
		if self.source:
			self.showsource(None)

	def view_callback(self, viewno):
		self.setwaiting()
		view = self.views[viewno]
		if view is not None:
			view.show()
##		if view.is_showing():
##			view.hide()
##		else:
##			view.show()

	def hide_view_callback(self, viewno):
		view = self.views[viewno]
		if view is not None and view.is_showing():
			view.hide()

	def save_callback(self):
		if self.new_file:
			self.saveas_callback()
			return
		utype, host, path, params, query, fragment = urlparse(self.filename)
		if (utype and utype != 'file') or (host and host != 'localhost'):
			windowinterface.showmessage('Cannot save to remote URL',
						    mtype = 'warning')
			return
		file = MMurl.url2pathname(path)
		self.setwaiting()
		ok = self.save_to_file(file)

	def saveas_okcallback(self, filename):
		if not filename:
			return 'no file specified'
		self.setwaiting()
		if self.save_to_file(filename):
			self.filename = MMurl.pathname2url(filename)
			self.context.setbaseurl(self.filename)
			self.fixtitle()
		else:
			return 1

	def saveas_callback(self):
		cwd = self.dirname
		if cwd:
			cwd = MMurl.url2pathname(cwd)
			if not os.path.isabs(cwd):
				cwd = os.path.join(os.getcwd(), cwd)
		else:
			cwd = os.getcwd()
		filetypes = ['application/x-grins-project', 'application/smil']
		import settings
		if not settings.get('lightweight'):
			filetypes.append('application/x-grins-cmif')
		dftfilename = ''
		if self.filename:
			utype, host, path, params, query, fragment = urlparse(self.filename)
			dftfilename = os.path.split(MMurl.url2pathname(path))[-1]
		windowinterface.FileDialog('Save SMIL file:', cwd, filetypes,
					   dftfilename, self.saveas_okcallback, None)

	def export_okcallback(self, filename):
		if not filename:
			return 'no file specified'
		self.setwaiting()
		license = self.main.wanttosave()
		if not license:
			windowinterface.showmessage('Cannot obtain a license to save. Operation failed')
			return
		evallicense= (license < 0)
		if not self.save_to_file(filename, exporting = 1):
			return		# Error, don't save HTML file
		#
		# Invent HTML file name and SMIL file url, and generate webpage
		#
		htmlfilename = os.path.splitext(filename)[0] + '.html'
		smilurl = MMurl.pathname2url(filename)

		# Make a back-up of the original file...
		oldhtmlfilename = ''
		try:
			oldhtmlfilename = make_backup_filename(htmlfilename)
			os.rename(htmlfilename, oldhtmlfilename)
		except os.error:
			pass
		try:
			import HTMLWrite
			HTMLWrite.WriteFile(self.root, htmlfilename, smilurl, oldhtmlfilename,
						evallicense=evallicense)
		except IOError, msg:
			windowinterface.showmessage('HTML write failed.\n'+
						    'File: '+htmlfilename+'\n'+
						    'Error: '+msg[1])

	def bandwidth_callback(self, do_export_callback):
		import settings
		import BandwidthCompute
		bandwidth = settings.get('system_bitrate')
		if bandwidth > 1000000:
			bwname = "%dMbps"%(bandwidth/1000000)
		elif bandwidth % 1000 == 0:
			bwname = "%dkbps"%(bandwidth/1000)
		else:
			bwname = "%dbps"%bandwidth
		msg = 'Computing bandwidth usage at %s...'%bwname
		dialog = windowinterface.BandwidthComputeDialog(msg)
		bandwidth, prerolltime, delaycount, errorseconds, errorcount = \
			BandwidthCompute.compute_bandwidth(self.root)
		dialog.setinfo(prerolltime, errorseconds, delaycount, errorcount)
		dialog.done(do_export_callback, cancancel=1)

	def export_callback(self):
		ask = self.new_file
		if not ask:
			if mimetypes.guess_type(self.filename)[0] != 'application/x-grins-project':
				# We don't have a project file name. Ask for filename.
				ask = 1
			else:
				utype, host, path, params, query, fragment = urlparse(self.filename)
				if (utype and utype != 'file') or (host and host != 'localhost'):
					# The project file is remote. Ask for filename.
					ask = 1
				else:
					file = MMurl.url2pathname(path)
					base = os.path.splitext(file)[0]
					file = base + mimetypes.guess_extension('application/smil')
					self.setwaiting()
					self.export_okcallback(file)
					return 
		cwd = self.dirname
		if cwd:
			cwd = MMurl.url2pathname(cwd)
			if not os.path.isabs(cwd):
				cwd = os.path.join(os.getcwd(), cwd)
		else:
			cwd = os.getcwd()
		windowinterface.FileDialog('Publish SMIL file:', cwd, '*.smil',
					   '', self.export_okcallback, None)
	   
	def upload_callback(self):
		# XXXX The filename business confuses project file name and resulting SMIL file
		# XXXX name. To be fixed.
		#
		# XXXX The multi-stage password asking code here is ugly.
		if not self.filename:
			windowinterface.showmessage('Please save your work first')
			return
		filename, smilurl, self.w_ftpinfo, self.m_ftpinfo = self.get_upload_info()
			
		missing = ''
		attr = None
		if not self.w_ftpinfo[0] or not self.m_ftpinfo[0]:
			attr = 'project_ftp_host'
			missing = '\n- webserver and mediaserver FTP info'
		if not smilurl:
			if not attr: attr = 'project_smil_url'
			missing = missing + '\n- Mediaserver SMILfile URL'
		attrs = self.context.attributes
		if not attrs.has_key('project_html_page') or not attrs['project_html_page']:
			if not attr: attr = 'project_html_page'
			missing = missing + '\n- HTML template'

		if missing:
			if windowinterface.showquestion('Please set these parameters then try again:'+missing):
				self.prop_callback(attr)
			return
		else:
			# Do a sanity check on the SMILfile URL
			fn = MMurl.url2pathname(string.split(smilurl, '/')[-1])
		if os.path.split(filename)[1] != os.path.split(fn)[1]:
			# The SMIL upload filename and URL don't match. Warn.
			if not windowinterface.showquestion('Warning: Mediaserver SMIL URL appears incorrect:\n'+smilurl):
				return
		hostname, username, passwd, dirname = self.w_ftpinfo
		if username and not passwd:
			windowinterface.InputDialog('Enter password for %s at %s'%(username, hostname),
					'', self.upload_callback_2, passwd=1)
		else:
			self.upload_callback_2(passwd)
			
	def upload_callback_2(self, passwd):
		# This is the website password. See whether we also have to ask for the
		# media site password
		w_hostname, w_username, dummy, w_dirname = self.w_ftpinfo
		m_hostname, m_username, m_passwd, m_dirname = self.m_ftpinfo
		self.w_ftpinfo = w_hostname, w_username, passwd, w_dirname
		if m_hostname == w_hostname and m_username == w_username:
			self.upload_callback_3(passwd)
		elif m_username and not m_passwd:
			windowinterface.InputDialog('Enter password for %s at %s'%(m_username, m_hostname),
					'', self.upload_callback_3, passwd=1)
		else:
			self.upload_callback_3(m_passwd)
	
	def upload_callback_3(self, passwd):
		# Third stage of upload: we have the passwords
		m_hostname, m_username, dummy, m_dirname = self.m_ftpinfo
		self.m_ftpinfo = m_hostname, m_username, passwd, m_dirname
		filename, smilurl, d1, d2  = self.get_upload_info()
		self.save_to_ftp(filename, smilurl, self.w_ftpinfo, self.m_ftpinfo)
		del self.w_ftpinfo
		del self.m_ftpinfo
		
	def get_upload_info(self, w_passwd='', m_passwd=''):
		attrs = self.context.attributes

		# Website FTP parameters
		w_hostname = ''
		w_username = ''
		w_dirname = ''
		if attrs.has_key('project_ftp_host'):
			w_hostname = attrs['project_ftp_host']
		if attrs.has_key('project_ftp_user'):
			w_username = attrs['project_ftp_user']
		if attrs.has_key('project_ftp_dir'):
			w_dirname = attrs['project_ftp_dir']

		# Mediasite FTP params (default to same as website)
		m_hostname = ''
		m_username = ''
		m_dirname = ''
		if attrs.has_key('project_ftp_host_media'):
			m_hostname = attrs['project_ftp_host_media']
		if attrs.has_key('project_ftp_user_media'):
			m_username = attrs['project_ftp_user_media']
		if attrs.has_key('project_ftp_dir_media'):
			m_dirname = attrs['project_ftp_dir_media']
		if not m_hostname:
			m_hostname = w_hostname
		if not m_username:
			m_username = w_username
		if not m_dirname:
			m_dirname = w_dirname
			
		# Filename for SMIL file on media site
		# XXXX This may be wrong, because it uses the "project" filename
		utype, host, path, params, query, fragment = urlparse(self.filename)
		dir, filename = posixpath.split(path)
		filename = posixpath.splitext(filename)[0] + \
			   mimetypes.guess_extension('application/smil')
		
		# URL of the SMIL file as it appears on the net
		if attrs.has_key('project_smil_url'):
			smilurl = attrs['project_smil_url']
		else:
			smilurl = ''

		return (filename, smilurl,
				(w_hostname, w_username, w_passwd, w_dirname), 
				(m_hostname, m_username, m_passwd, m_dirname))

	def prop_callback(self, initattr = None):
		import AttrEdit
		AttrEdit.showdocumentattreditor(self, initattr = initattr)

	def edit_callback(self):
		if not self.editmgr.transaction():
			return
		self.setwaiting()
		import SMILTreeWrite, tempfile
		# XXXX This is wrong, probably
		tmp = tempfile.mktemp(mimetypes.guess_extension('application/x-grins-project'))
		self.__edittmp = tmp
		SMILTreeWrite.WriteFile(self.root, tmp)
		self.do_edit(tmp)

	def edit_finished_callback(self, tmp = None):
		import EditMgr, os
		self.editmgr.rollback()
		if tmp is None:
			try:
				os.unlink(self.__edittmp)
			except os.error:
				pass
			del self.__edittmp
			return
		showing = []
		for i in range(len(self.views)):
			if self.views[i] is not None and \
			   self.views[i].is_showing():
				showing.append(i)
		self.editmgr.unregister(self)
		self.editmgr.destroy() # kills subscribed views
		self.context.seteditmgr(None)
		self.root.Destroy()
		self.do_read_it(tmp)
		try:
			os.unlink(self.__edittmp)
		except os.error:
			pass
		del self.__edittmp
		self.context = self.root.GetContext()
		self.editmgr = EditMgr.EditMgr(self.root)
		self.context.seteditmgr(self.editmgr)
		self.editmgr.register(self)
		self.makeviews()
		for i in showing:
			self.views[i].show()
		self.changed = 1

	def fixtitle(self):
		utype, host, path, params, query, fragment = urlparse(self.filename)
		dir, base = posixpath.split(path)
		if (not utype or utype == 'file') and \
		   (not host or host == 'localhost'):
			# local file
			self.dirname = dir
		else:
			# remote file
			self.dirname = ''
		mtype = mimetypes.guess_type(base)[0]
		if mtype in ('application/x-grins-project', 'application/smil', 'application/x-grins-cmif'):
			self.basename = posixpath.splitext(base)[0]
		else:
			self.basename = base
		self.window.settitle(MMurl.unquote(self.basename))
		for v in self.views:
			if v is not None:
				v.fixtitle()

	def relative_url(self, url):
		# Make a URL relative to self.dirname, if possible
		utype, host, pathname, params, query, fragment = urlparse(url)
		if (utype and utype != 'file') or host or query or fragment:
			# nonlocal url
			return url
		pathname = MMurl.url2pathname(pathname)
		cwd = self.dirname
		if cwd:
			cwd = MMurl.url2pathname(cwd)
			if not os.path.isabs(cwd):
				cwd = os.path.join(os.getcwd(), cwd)
		else:
			# If we have no document dirname we use relative to cwd
			cwd = os.getcwd()
		if os.path.isdir(pathname):
			dir, file = pathname, os.curdir
		else:
			dir, file = os.path.split(pathname)
		# XXXX maybe should check that dir gets shorter!
		while len(dir) > len(cwd):
			dir, f = os.path.split(dir)
			file = os.path.join(f, file)
		if dir == cwd:
			pathname = file
		return MMurl.pathname2url(pathname)

	def pre_save(self):
		# Get rid of hyperlinks outside the current tree and clipboard
		# (XXX We shouldn't *save* the links to/from the clipboard,
		# but we don't want to throw them away either...)
		roots = [self.root]
		import Clipboard
		type, data = Clipboard.getclip()
		if type == 'node' and data is not None:
			roots.append(data)
		self.context.sanitize_hyperlinks(roots)
		# Get all windows to save their current geometry.
		for v in self.views:
			if v is not None:
				v.get_geometry()
				v.save_geometry()
		

	def save_to_file(self, filename, exporting = 0):
		license = self.main.wanttosave()
		if not license:
			windowinterface.showmessage('Cannot obtain a license to save. Operation failed')
			return 0
		evallicense= (license < 0)
		url = MMurl.pathname2url(filename)
		mimetype = mimetypes.guess_type(url)[0]
		if exporting and mimetype != 'application/smil':
			windowinterface.showmessage('Export to SMIL (*.smi or *.smil) files only')
			return
		if mimetype == 'application/x-grins-cmif':
			import settings
			if settings.get('lightweight'):
				windowinterface.showmessage('cannot write CMIF files in this version', mtype = 'error')
				return 0
		elif mimetype == 'application/smil':
			if not exporting:
				answer = windowinterface.multchoice('You will lose information by saving your project as SMIL.\nDo you want to continue?',
					['OK', 'Cancel'], 1)
				if answer != 0:
					return
		else:
			# Save a grins project file
			pass
		self.pre_save()
		# Make a back-up of the original file...
		try:
			os.rename(filename, make_backup_filename(filename))
		except os.error:
			pass
##		print 'saving to', filename, '...'
		try:
			if mimetype == 'application/x-grins-cmif':
				import MMWrite
				MMWrite.WriteFile(self.root, filename, evallicense=evallicense)
			else:
				cleanSMIL = (mimetype == 'application/smil')
				import SMILTreeWrite
				if exporting:
					# XXX enabling this currently crashes the application on Windows during video conversion
					progress = windowinterface.ProgressDialog("Publishing")
					progress.set('Publishing document...')
					progress = progress.set
				else:
					progress = None
				SMILTreeWrite.WriteFile(self.root, filename,
							cleanSMIL = cleanSMIL,
							copyFiles = exporting,
							evallicense=evallicense,
							progress = progress)
		except IOError, msg:
			windowinterface.showmessage('Save operation failed.\n'+
						    'File: '+filename+'\n'+
						    'Error: '+msg[1])
			return 0
##		print 'done saving.'
		if not exporting:
			self.main._update_recent(MMurl.pathname2url(filename))
			self.changed = 0
			self.new_file = 0
		self.setcommands(self.commandlist)
		return 1
		
	def save_to_ftp(self, filename, smilurl, w_ftpparams, m_ftpparams):
		license = self.main.wanttosave()
		if not license:
			windowinterface.showmessage('Cannot obtain a license to save. Operation failed')
			return 0
		evallicense= (license < 0)
		self.pre_save()
		#
		# Progress dialog
		#
		progress = windowinterface.ProgressDialog("Uploading", self.cancel_upload)
		progress.set("Generating document...")
		#
		# First save and upload the SMIL file (and the data items)
		#
		try:
			import SMILTreeWrite
			SMILTreeWrite.WriteFTP(self.root, filename, m_ftpparams,
						cleanSMIL = 1,
						copyFiles = 1,
						evallicense=evallicense,
						progress=progress.set)
		except IOError, msg:
			windowinterface.showmessage('Media upload failed:\n'+msg[1])
			return 0
		except KeyboardInterrupt:
			windowinterface.showmessage('Upload interrupted')
			return 0
		#
		# Next create and upload the HTML and RAM files
		#
		progress.set("Uploading webpage")
		#
		# Invent HTML file name and SMIL file url, and generate webpage
		#
		htmlfilename = os.path.splitext(filename)[0] + '.html'
		# XXXX We should generate from the previously saved HTML file
		oldhtmlfilename = ''
		try:
			import HTMLWrite
			HTMLWrite.WriteFTP(self.root, htmlfilename, smilurl, w_ftpparams, oldhtmlfilename,
						evallicense=evallicense)
		except IOError, msg:
			windowinterface.showmessage('Webpage upload failed:\n'+msg[1])
			return 0
		except KeyboardInterrupt:
			windowinterface.showmessage('Upload interrupted')
			return 0
		self.setcommands(self.commandlist) # Is this needed?? (Jack)
		return 1
		
	def cancel_upload(self):
		raise KeyboardInterrupt

	def restore_callback(self):
		if self.changed:
			l1 = 'Are you sure you want to re-read the file?\n'
			l2 = '(This will destroy the changes you have made)\n'
			l3 = 'Click OK to restore, Cancel to keep your changes'
			windowinterface.showmessage(
				l1+l2+l3, mtype = 'question',
				callback = (self.do_restore, ()),
				title = 'Destroy?')
			return
		self.do_restore()

	def do_restore(self):
		if not self.editmgr.transaction():
			return
		self.setwaiting()
		showing = []
		for i in range(len(self.views)):
			if self.views[i] is not None and \
			   self.views[i].is_showing():
				showing.append(i)
		self.editmgr.rollback()
		self.editmgr.unregister(self)
		self.editmgr.destroy() # kills subscribed views
		self.context.seteditmgr(None)
		self.root.Destroy()
		self.read_it()
		self.makeviews()
		for i in showing:
			self.views[i].show()

	def read_it(self):
		self.changed = 0
		if self.new_file:
			if type(self.new_file) == type(''):
				self.do_read_it(self.new_file)
			else:
				import SMILTreeRead
				self.root = SMILTreeRead.ReadString(EMPTY, self.filename)
		else:
			self.do_read_it(self.filename)
		self.context = self.root.GetContext()
		if self.new_file:
			self.context.baseurl = ''
			if type(self.new_file) == type(''):
				self.context.template = self.new_file
		self.editmgr = EditMgr(self.root)
		self.context.seteditmgr(self.editmgr)
		self.editmgr.register(self)

	def do_read_it(self, filename):
##		import time
##		print 'parsing', filename, '...'
##		t0 = time.time()
		mtype = mimetypes.guess_type(filename)[0]
		if mtype == None and sys.platform == 'mac':
			# On the mac we do something extra: for local files we attempt to
			# get creator and type, and if they are us we assume we're looking
			# at a SMIL file.
			import MacOS
			utype, host, path, params, query, fragment = urlparse(filename)
			if (not utype or utype == 'file') and \
			   (not host or host == 'localhost'):
				# local file
				fn = MMurl.url2pathname(path)
				try:
					ct, tp = MacOS.GetCreatorAndType(fn)
				except:
					pass
				else:
					if ct == 'GRIN' and tp == 'TEXT':
						mtype = 'application/x-grins-project'
		if mtype in ('application/smil', 'application/x-grins-project'):
			import SMILTreeRead
			# The progress dialog will disappear when we exit this function
			if mtype == 'application/smil':
				progress = windowinterface.ProgressDialog("Import")
				progress.set("Importing SMIL document...")
			self.root = SMILTreeRead.ReadFile(filename, self.printfunc, self.new_file)
##			# For the lightweight version we set SMIL files as being "new"
##			if light and mtype == 'application/smil':
##				# XXXX Not sure about this, this may mess up code in read_it
##				self.new_file = 1
		elif mtype == 'application/x-grins-cmif':
			import settings
			if settings.get('lightweight'):
				windowinterface.showmessage('cannot read CMIF files in this version', mtype = 'error')
				raise Error, filename
			import MMRead
			self.root = MMRead.ReadFile(filename)
		else:
			windowinterface.showmessage('%s is a media item.\nCreating new SMIL file around it.'%filename)
			import SMILTreeRead
			if mtype is None or \
			   (mtype[:6] != 'audio/' and \
			    mtype[:6] != 'video/'):
				dur = ' dur="indefinite"'
			else:
				dur = ''
			self.new_file = 1
			self.root = SMILTreeRead.ReadString('''\
<smil>
  <body>
    <ref%s src="%s"/>
  </body>
</smil>
''' % (dur, filename), filename, self.printfunc)
##		t1 = time.time()
##		print 'done in', round(t1-t0, 3), 'sec.'


	def printfunc(self, msg):
		windowinterface.showmessage('while reading %s\n\n' % self.filename + msg)

	def close_callback(self):
		self.setwaiting()
		if self.source and not self.source.is_closed():
			self.source.close()
		self.source = None
		self.close()

	def close(self):
		ok = self.close_ok()
		if ok:
			self.destroy()

	def close_ok(self):
		if not self.changed:
			return 1
		reply = self.mayclose()
		if reply == 2:
			return 0
		if reply == 1:
			return 1
		utype, host, path, params, query, fragment = urlparse(self.filename)
		if (utype and utype != 'file') or (host and host != 'localhost'):
			windowinterface.showmessage('Cannot save to URL',
						    mtype = 'warning')
			return 0
		file = MMurl.url2pathname(path)
		return self.save_to_file(file)

	def help_callback(self, params=None):
		import Help
		Help.showhelpwindow()

	def setwaiting(self):
		windowinterface.setwaiting()

	def prefschanged(self):
		# HACK: we don't want to set the file changed bit (in the
		# commit call below)
		self._in_prefschanged = 1
		if not self.editmgr.transaction():
			return
		self.root.ResetPlayability()
		self.editmgr.commit()
		self._in_prefschanged = 0
	#
	# EditMgr interface (as dependent client).
	# This is the first registered client; hence its commit routine
	# will be called first, so it can fix the timing for the others.
	# It also flushes the attribute cache maintained by MMAttrdefs.
	#
	def transaction(self):
		# Always allow transactions
		return 1

	def commit(self):
		# Fix the timing -- views may depend on this.
		if not self._in_prefschanged:
			self.changed = 1
		MMAttrdefs.flushcache(self.root)
		Timing.changedtimes(self.root)
		if self.source:
			# reshow source
			import SMILTreeWrite
			self.showsource(SMILTreeWrite.WriteString(self.root), optional=1)
		#if self.__save is not None:
		#	self.setcommands(self.commandlist + [self.__save])

	def rollback(self):
		# Nothing has happened.
		pass

	def kill(self):
		print 'TopLevel.kill() should not be called!'

	#
	# Global hyperjump interface
	#
	def jumptoexternal(self, anchor, atype):
		# XXXX Should check that document isn't active already,
		# XXXX and, if so, should jump that instance of the
		# XXXX document.
		import MMurl
		if type(anchor) is type(()):
			uid, aid = anchor
			if '/' not in uid:
				url = self.filename
			elif uid[-2:] == '/1':
				url = uid[:-2]
			else:
				url = uid
		else:
			url, aid = MMurl.splittag(anchor)
		url = MMurl.basejoin(self.filename, url)
		for top in self.main.tops:
			if top is not self and top.is_document(url):
				break
		else:
			try:
				top = TopLevel(self.main, url, 0)
			except:
				msg = sys.exc_value
				if type(msg) is type(self):
					if hasattr(msg, 'strerror'):
						msg = msg.strerror
					else:
						msg = msg.args[0]
				windowinterface.showmessage(
					'Open operation failed.\n'+
					'File: '+url+'\n'+
					'Error: '+`msg`)
				return 0
		top.show()
		node = top.root
		if type(anchor) is type (()) and  '/' not in uid:
			try:
				node = top.root.context.mapuid(uid)
			except NoSuchUIDError:
				print 'uid not found in document'
		elif hasattr(node, 'SMILidmap') and node.SMILidmap.has_key(aid):
			node = node.context.mapuid(node.SMILidmap[aid])
		top.player.show((top.player.playfromanchor, (node, aid)))
		if atype == TYPE_CALL:
			self.player.pause(1)
		elif atype == TYPE_JUMP:
			self.close()
		return 1

	def is_document(self, url):
		if self.filename == url:
			return 1
		if MMurl.canonURL(self.filename) == MMurl.canonURL(url):
			return 1
		return 0

	def _getlocalexternalanchors(self):
		fn = self.filename
		if not '/' in fn:
			fn = './' + fn
		rv = []
		alist = MMAttrdefs.getattr(self.root, 'anchorlist')
		for i, t, v in alist:
			rv.append((fn, i))
		return rv

	def getallexternalanchors(self):
		rv = []
		for top in self.main.tops:
			if top is not self:
				rv = rv + top._getlocalexternalanchors()
		return rv


if os.name == 'posix':
	def make_backup_filename(filename):
		return filename + '~'
else:
	def make_backup_filename(filename):
		return filename + '.BAK'
