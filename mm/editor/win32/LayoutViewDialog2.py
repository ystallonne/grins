# experimental layout view

import windowinterface
from usercmd import *
IMPL_AS_FORM=1

class LayoutViewDialog2:
	def __init__(self):
		self.__window=None

	def createviewobj(self):
		f=self.toplevel.window

		# create an new view : return an instance of _LayoutView
		w=f.newviewobj('lview_')

		# get a handle for each control created from _LayoutView class and associate a callback 
		# note: if you modify the key names, you also have to modify them in _LayoutView class
		self.__viewportSelCtrl=w['ViewportSel']
		self.__viewportSelCtrl.setcb((self.__viewportSelCb, ()))

		self.__regionSelCtrl=w['RegionSel']
		self.__regionSelCtrl.setcb((self.__regionSelCb, ()))

		w.setContext(self.context)

		self.__window = w

	def destroy(self):
		if self.__window is None:
			return
		if hasattr(self.__window,'_obj_') and self.__window._obj_:
			self.__window.close()
		self.__window = None
		del self.__viewportSelCtrl
		del self.__regionSelCtrl

	def show(self):
		self.assertwndcreated()	
		self.__window.show()

	def is_showing(self):
		if self.__window is None:
			return 0
		return self.__window.is_showing()

	def hide(self):
		if self.__window is not None:
			self.__window.close()
			self.__window = None
			f=self.toplevel.window
			f.set_toggle(LAYOUTVIEW,0)


	def assertwndcreated(self):
		if self.__window is None or not hasattr(self.__window,'GetSafeHwnd'):
			self.createviewobj()
		if self.__window.GetSafeHwnd()==0:
			f=self.toplevel.window
			if IMPL_AS_FORM: # form
				f.showview(self.__window,'lview_')
				self.__window.show()
			else:# dlgbar
				self.__window.create(f)
				f.set_toggle(LAYOUTVIEW,1)

	def setViewportList(self, layouts, cur):
		# the core should be corected but 
		# in order to proceed let fill the hole here
		self.assertwndcreated()
		print 'to do'

	def setRegionList(self, channels, cur):
		# the core should be corected but 
		# in order to proceed let fill the hole here
		self.assertwndcreated()
		print 'to do'

	def __viewportSelCb(self):
		print 'viewport select callback not implemented yet'
		
	def __regionSelCb(self):
		print 'viewport select callback not implemented yet'
		
	def setwaiting(self):
		windowinterface.setwaiting()

	def setready(self):
		windowinterface.setready()

	def setcommandlist(self, commandlist):
		if self.__window:
			self.__window.set_commandlist(commandlist)

	# core required interface
	def setlayoutlist(self, layouts, cur):
		pass
	def setchannellist(self, channels, cur):
		pass
	def setotherlist(self, channels, cur):
		pass

