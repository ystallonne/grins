__version__ = "$Id$"

""" @win32doc|_SourceView
This module contains the ui implementation of the source
viewer. It is an MFC EditView with the read only attribute set.
It is exposed to Python through the win32ui pyd as PyCEditView
"""

import win32ui,win32con
Sdk=win32ui.GetWin32Sdk()
Afx=win32ui.GetAfx()
import win32mu

import usercmd

from pywinlib.mfc import window, object, docview
import windowinterface
import afxres, commctrl

import grinsRC, components
from GenFormView import GenFormView

# XXX: this version is currently inactive 
# XXX: will be removed soon
# XXX: kept temporary for some days just for ref
class _SourceViewXXX(GenFormView):
	# Class contructor. Calls the base RichEditView constructor
	def __init__(self,doc,bgcolor=None):
		self.__showing = 0
		GenFormView.__init__(self, doc, grinsRC.IDD_SOURCEEDIT)
		self['edit'] = self.__editctrl = components.Edit(self, grinsRC.IDC_EDIT1)
		self['ok'] = self.__ok = components.Button(self,grinsRC.IDC_BUTTON1)
		self['apply'] = self.__apply = components.Button(self,grinsRC.IDC_BUTTON2)
		self['revert'] = self.__revert = components.Button(self,grinsRC.IDC_BUTTON3)
		self.__text=''
		self.__mother = None
		self.__readonly = 0
		self.__closecallback = None
		self.__map0 = []
		self.__map1 = []
		# call back dictionary, used ne GenFormView
		self._cbdict = {'ok': (self.__ok_callback, ()),
				'apply': (self.__apply_callback, ()),
				'revert': (self.__revert_callback, ()),
##				'edit': (self.__edit_callback, ()),
				}

	# Called by the framework after the OS window has been created
	def OnInitialUpdate(self):
		GenFormView.OnInitialUpdate(self)
		self.__showing = 1
		self.__editctrl.settext(self.__text)
		self.__editctrl.enable(1)
		self.__editctrl.setreadonly(self.__readonly)
		self.__ok.enable(1)
		self.__apply.enable(0)
		self.__revert.enable(0)

	def OnCmd(self, params):
		if self.__editctrl is None:
			# aparently closed
			return
		msg=win32mu.Win32Msg(params)
		id=msg.cmdid()
		if id == self.__editctrl._id:
			nmsg=msg.getnmsg()
			if nmsg == win32con.EN_CHANGE:
				self.__apply.enable(1)
				self.__revert.enable(1)
		elif id == self.__ok._id:
			self.__ok_callback()
		elif id == self.__apply._id:
			self.__apply_callback()
		elif id == self.__revert._id:
			self.__revert_callback()

	def __ok_callback(self):
		if self.__closecallback is not None:
			apply(apply, self.__closecallback)
		elif self.__mother is not None:
			self.__mother.close_callback()

	def __apply_callback(self):
		if self.__mother is not None:
			self.__mother.apply_callback()

	def __revert_callback(self):
		self.__editctrl.settext(self.__text)
		self.__apply.enable(0)
		self.__revert.enable(0)

	def setclosecmd(self, cmdid):
		self._closecmdid = cmdid

	def set_readonly(self, readonly):
		self.__readonly = readonly
		if self.__showing:
			self.__editctrl.setreadonly(readonly)

	def set_closecallback(self, callback):
		self.__closecallback = callback

	# Called by the framework to close this window.
	def OnClose(self):
		if self.__closecallback is not None:
			apply(apply, self.__closecallback)
		elif self.__mother is not None:
			self.__mother.close_callback()
		else:
			print "ERROR: You need to call _SourceView.setmother(self)"

	# cmif interface
	# Set the text to be shown
	def settext(self,text):
##		f = win32ui.CreateFont({"name":"courier new", "width":12, "height":12,})
##		self.__editctrl.SetFont(f)
##		self.__editctrl.SetWordWrap(0) # helps if you are psycic.
		self.__text=self.__convert2ws(text)
		# if already visible, update text in window
		if self.__showing:
			self.__editctrl.settext(self.__text)
			self.select_chars(0, 0)
##			self.__editctrl.setmodify(0) # No, this document has not been modified yet.

	def gettext(self):
		return self.__editctrl.gettext()

	def select_chars(self, startchar, endchar):
		# the text between startchar and endchar will be selected.
		e = self.__editctrl
		for p0, p1 in self.__map0:
			if p0 <= startchar:
				startchar = p1 + (startchar - p0)
				break
		for p0, p1 in self.__map0:
			if p0 <= endchar:
				endchar = p1 + (endchar - p0)
				break
		startline = len(self.__map1) - 1
		for p0, p1 in self.__map1:
			startline = startline - 1
			if p0 <= startchar:
				startchar = p1 + (startchar - p0)
				break
		endline = len(self.__map1) - 1
		for p0, p1 in self.__map1:
			endline = endline - 1
			if p0 <= endchar:
				endchar = p1 + (endchar - p0)
				break
		e.setsel(startchar, endchar)
		# magic number 23: number of lines in edit control
		if endline > e.getfirstvisibleline() + 23:
			# last line not visible, scroll down
			e.linescroll(endline - e.getfirstvisibleline() - 23)
		if startline < e.getfirstvisibleline():
			# first line not visible, scroll up
			e.linescroll(startline - e.getfirstvisibleline())

	def is_changed(self):
		# Return true or false depending on whether the source view has been changed.
		return self.__editctrl.getmodify()
	
	def set_mother(self, mother):
		self.__mother = mother

	# Convert the text from unix or mac to windows
	def __convert2ws(self,text):
		import string
		# together the following three mappings normalize
		# end-of-line sequences in any combination of the
		# three standards to the Windows standard

		# first map \r\n to \n (Windows to Unix)
		# must do this first since we don't want to convert
		# \r\n to \n\n in the next convertion
		rn = string.split(text, '\r\n')
		text = string.join(rn, '\n')
		# then map left over \r to \n (Mac to Unix)
		r = string.split(text, '\r')
		text = string.join(r, '\n')
		# finally map \n to \r\n (Unix to Windows)
		n = string.split(text, '\n')
		text = string.join(n, '\r\n')

		# calculate mappings of char positions
		pos0 = pos1 = 0
		for line in rn:
			self.__map0.append((pos0, pos1))
			pos0 = pos0 + len(line) + 2
			pos1 = pos1 + len(line) + 1
		self.__map0.reverse()
		pos0 = pos1 = 0
		for line in n:
			self.__map1.append((pos0, pos1))
			pos0 = pos0 + len(line) + 1
			pos1 = pos1 + len(line) + 2
		self.__map1.reverse()
		return text
	
	# Called by the framework to close the view		
	def close(self):
		# 1. clean self contents
		self.__text=None
		self.__mother = None
		self.__closecallback = None
		self.__editctrl = None
		self.__ok = None
		self.__apply = None
		self.__revert = None

		# 2. destroy OS window if it exists
		if hasattr(self,'_obj_') and self._obj_:
			self.GetParent().DestroyWindow()
		self._cbdict = None


###################################
import win32ui, win32con, afxres

import win32mu

from pywinlib.mfc import docview

import grinsRC, components
from GenView import GenView

class SourceViewTemplate(docview.RichEditDocTemplate):
	pass

class SourceViewDocument(docview.RichEditDoc):
	pass

class _SourceView(GenView, docview.RichEditView):
	def __init__(self, doc, bgcolor=None):
		self.__showing = 0
		self.__setting = 0
		# base init
		GenView.__init__(self, bgcolor)

		# important: a rich edit ctrl have to be created the right template and the right document
		# (see MFC doc: RichEditCtrl and architecture MDI).
		# If you don't do this, the application crash on some operations (drag and drop, ...)
		sourceTemplate = SourceViewTemplate()
		win32ui.GetApp().AddDocTemplate(sourceTemplate)
		doc = SourceViewDocument(sourceTemplate)
		
		docview.RichEditView.__init__(self, doc)

		# view decor
		self._dlgBar = win32ui.CreateDialogBar()
		self.__ok = components.Button(self._dlgBar,grinsRC.IDC_BUTTON1)
		self.__apply = components.Button(self._dlgBar,grinsRC.IDC_BUTTON2)
		self.__revert = components.Button(self._dlgBar,grinsRC.IDC_BUTTON3)

		self.__text=''
		self.__mother = None
		self.__readonly = 0
		self.__closecallback = None
		self.__map0 = []
		self.__map1 = []
		self.__listener = None
		self.__lineToSelect = None
		
	def OnCreate(self, cs):
		# create dialog bar and attach controls (though attachement effects are not used for buttons)
		# dialog bar is not needed if we are readonly (player)
		if self.__readonly: 
			return
		AFX_IDW_DIALOGBAR = 0xE805
		self._dlgBar.CreateWindow(self.GetParent(), grinsRC.IDD_SOURCEEDIT1, afxres.CBRS_ALIGN_BOTTOM, AFX_IDW_DIALOGBAR)
		self.__ok.attach_to_parent()
		self.__apply.attach_to_parent()
		self.__revert.attach_to_parent()

	# Called by the framework after the OS window has been created
	def OnInitialUpdate(self):
		self.__editctrl = self.GetRichEditCtrl()
		# redirect all command messages to self.OnCmd
		self.GetParent().HookMessage(self.OnCmd, win32con.WM_COMMAND)
		# allow to detect when the selection change
		self.GetParent().HookNotify(self.onSelChanged, win32con.EN_SELCHANGE)	

		self.GetParent().HookMessage(self.OnSetFocus,win32con.WM_SETFOCUS)

		# we are now showing of course
		self.__showing = 1

		self.settext(self.__text)

		# set text and readonly flag
		self.SetReadOnly(self.__readonly)
		
		# enable/disable dialog bar components according to MFC convention 
		self.enableDlgBarComponent(self.__ok, 1)
		self.enableDlgBarComponent(self.__apply, 0)
		self.enableDlgBarComponent(self.__revert, 0)

		# disable the default wrap behavior
		self.SetWordWrap(win32ui.CRichEditView_WrapNone)
		self.WrapChanged()
		
	def Paste(self):
		if not self.isClipboardEmpty():
			# call the ancestor's method
			self._obj_.Paste()
			
		self.__updateClipboardInfo()

	def Copy(self):
		# call the ancestor's method
		self._obj_.Copy()
		
		self.__updateClipboardInfo()

	def Cut(self):
		# call the ancestor's method
		self._obj_.Cut()
		
		self.__updateClipboardInfo()

	# this method update the listener in order that the menu item PASTE be refreshed
	# we have to call this method when the clipboard may change its contain. It's not the best way
	# but this framework doesn't allow to use the right solution as advised in Microsoft documentation
	# So, currently, we update the listener when either:
	# - the source view get the focus
	# - a copy/cut/paste opperation is done from the source view
	def __updateClipboardInfo(self):
		if self.__listener != None:
			self.__listener.onClipboardChanged()

	def OnSetFocus(self, params):
		self.__updateClipboardInfo()

	def OnCmd(self, params):
		if not self.is_showing():
			return
		editCtrl = self.GetRichEditCtrl()
		if not editCtrl: 
			return
		
		# crack win32 message
		msg=win32mu.Win32Msg(params)
		code = msg.HIWORD_wParam()
		id = msg.LOWORD_wParam()
		hctrl = msg._lParam

		# response/dispatch cmd
		if hctrl == editCtrl.GetSafeHwnd():
			if code == win32con.EN_CHANGE:
				if self.__editctrl.GetModify() and not self.__setting:
					self.enableDlgBarComponent(self.__apply, 1)
					self.enableDlgBarComponent(self.__revert, 1)
				if self.__lineToSelect:
					self.__lineToSelect = None
					self.select_line(self.__lineToSelect)
		elif id == self.__ok._id:
			self.__ok_callback()
		elif id == self.__apply._id:
			self.__apply_callback()
		elif id == self.__revert._id:
			self.__revert_callback()

	def __ok_callback(self):
		if self.__closecallback is not None:
			apply(apply, self.__closecallback)
		elif self.__mother is not None:
			self.__mother.close_callback()

	def __apply_callback(self):
		if self.__mother is not None:
			self.__mother.apply_callback()

	def __revert_callback(self):
		self.SetWindowText(self.__text)
		self.enableDlgBarComponent(self.__apply, 0)
		self.enableDlgBarComponent(self.__revert, 0)
		self.SetModify(0)

	def setclosecmd(self, cmdid):
		self._closecmdid = cmdid

	def set_readonly(self, readonly):
		self.__readonly = readonly
		if self.__showing:
			self.SetReadOnly(self.__readonly)

	def set_closecallback(self, callback):
		self.__closecallback = callback

	def gettext(self):
		text = self.GetWindowText()
		return self.__convert2un(text)

	# Set the text to be shown
	def settext(self, text):
		self.__text = self.__convert2ws(text)
		# if already visible, update text in window
		if self.__showing:
			# during the setting, the EN_CHANGE event is ignore
			self.__setting = 1
			self.SetWindowText(self.__text)
			self.SetModify(0)
			self.__setting = 0
			# raz apply and revert
			self.enableDlgBarComponent(self.__apply, 0)
			self.enableDlgBarComponent(self.__revert, 0)
				
	def set_mother(self, mother):
		self.__mother = mother
		
	# Convert the text from unix or mac to windows
	def __convert2ws(self, text):
		import string
		# together the following three mappings normalize
		# end-of-line sequences in any combination of the
		# three standards to the Windows standard

		# first map \r\n to \n (Windows to Unix)
		# must do this first since we don't want to convert
		# \r\n to \n\n in the next convertion
		rn = string.split(text, '\r\n')
		text = string.join(rn, '\n')
		# then map left over \r to \n (Mac to Unix)
		r = string.split(text, '\r')
		text = string.join(r, '\n')
		# finally map \n to \r\n (Unix to Windows)
		n = string.split(text, '\n')
		text = string.join(n, '\r\n')

		# calculate mappings of char positions
		pos0 = pos1 = 0
		for line in rn:
			self.__map0.append((pos0, pos1))
			pos0 = pos0 + len(line) + 2
			pos1 = pos1 + len(line) + 1
		self.__map0.reverse()
		pos0 = pos1 = 0
		for line in n:
			self.__map1.append((pos0, pos1))
			pos0 = pos0 + len(line) + 1
			pos1 = pos1 + len(line) + 2
		self.__map1.reverse()
		return text

	# Convert the text from windows to unix or mac
	def __convert2un(self, text):
		import string
		# first map \r\n to \n (Windows to Unix)
		rn = string.split(text, '\r\n')
		text = string.join(rn, '\n')
		# then map left over \r to \n (Mac to Unix)
		r = string.split(text, '\r')
		text = string.join(r, '\n')
		return text
		
	# Called by the framework to close the view		
	def close(self):
		# 1. clean self contents
		self.__text=None
		self.__mother = None
		self.__closecallback = None
		self.__ok = None
		self.__apply = None
		self.__revert = None

		# 2. destroy OS window if it exists
		if hasattr(self,'_obj_') and self._obj_:
			self.GetParent().DestroyWindow()
		self._cbdict = None

	# handler called by the system when the selection change
	def onSelChanged(self, std, extra):
		if self.__listener != None:
			self.__listener.onSelChanged()

	# Called by the framework to close this window.
	# XXX Spacial case for the source view. is it correct ???
	# see as well code in TopLevelWindow (when you close directly the main window)
	def OnClose(self):
		if self.__closecallback is not None:
			apply(apply, self.__closecallback)
		elif self.__mother is not None:
			self.__mother.close_callback()
		else:
			print "ERROR: You need to call _SourceView.setmother(self)"

	#
	# module interface
	#
	
	def setListener(self, listener):
		self.__listener = listener

	def removeListener(self):
		self.__listener = None
	
	# undo operation
	def Undo(self):
		return Sdk.SendMessage(self.GetSafeHwnd(),win32con.EM_UNDO,0,0)

	# select a line
	def select_line(self, line):
		if self.GetLineCount() < line:
			return
		startchar = self.LineIndex(line)
		if startchar >= 0:
			# determine the end char according to the next line
			# XXXX note EM_LINELENGTH doesn't work if there are a lot of lines ???
			# special case, if there is only one line
			lineCount = self.GetLineCount()
			if lineCount > 1:
				startend = self.LineIndex(line+1)
			else:
				# get the line length
				len = Sdk.SendMessage(self.GetSafeHwnd(),win32con.EM_LINELENGTH,0,0)
				startend = startchar+len
				
			if startend >= 0:
				self.SetSel((startchar, startend))
	
	# select a part of the text
	def select_chars(self, startchar, endchar, scroll = 1, pop = 0):
		# the text between startchar and endchar will be selected.
		for p0, p1 in self.__map0:
			if p0 <= startchar:
				startchar = p1 + (startchar - p0)
				break
		for p0, p1 in self.__map0:
			if p0 <= endchar:
				endchar = p1 + (endchar - p0)
				break
		startline = len(self.__map1) - 1
		for p0, p1 in self.__map1:
			startline = startline - 1
			if p0 <= startchar:
				startchar = p1 + (startchar - p0)
				break
		endline = len(self.__map1) - 1
		for p0, p1 in self.__map1:
			endline = endline - 1
			if p0 <= endchar:
				endchar = p1 + (endchar - p0)
				break
		self.SetSel((startchar, endchar))
		if pop: self.pop()

	def isChanged(self):
		# Return true if the text has been changed.
		return self.GetModify()
					
	# return true is there is any selection
	def isSelected(self):
		begin, end = self.GetSel()
		return end-begin > 0

	# return true if the system clipboard doen't contain text datas
	def isClipboardEmpty(self):
		Sdk=win32ui.GetWin32Sdk()
		n = Sdk.IsClipboardFormatAvailable(win32con.CF_TEXT)
		return n <= 0

	# return true if the undo is possible	
	def canUndo(self):
		return Sdk.SendMessage(self.GetSafeHwnd(),win32con.EM_CANUNDO,0,0)

	# should return the line pointed by the carret
	# XXX for now, return the first caractere of the line pointed by the carret
	def getCurrentCharIndex(self):
		# get the current char index (pointed by the carret)
		charIndex  = self.LineIndex(-1)
		# get the current line
		lineNumber = self.LineFromChar(charIndex)
		
		# the internal GRiNS representation has 1 caracteres for the end of line
		# windows needs 2 caracteres (CR and LF) for the end of line
		# substract the line number to map with the internal representation
		# XXX should use the current map table
		charIndex = charIndex - lineNumber

		return charIndex

	# return the line number	
	def getLineNumber(self):
		return self.GetLineCount()
	