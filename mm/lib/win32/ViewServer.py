__version__ = "$Id$"

""" @win32doc|ViewServer
This module implements a server for views apropriate to 
the architecture chosen.
The other modules request from this server a view 
using a standard interface.

The purpose of this module is to simplify the 
application's MainFrame
and to isolate dependencies between 
the implementations of the views and the modules 
that use them.
"""

# views types
from _LayoutView import _LayoutView
from _UsergroupView import _UsergroupView
from _UsergroupView import _UsergroupView
from _LinkView import _LinkView
from _CmifView import _CmifView
from _SourceView import _SourceView

# views served
_PlayerView=_CmifView
_HierarchyView=_CmifView
_ChannelView=_CmifView
_LinkView=_LinkView
_LayoutView=_LayoutView
_SourceView=_SourceView

# imports
import win32ui,win32con,win32mu
from pywin.mfc import window,object,docview,dialog
import appcon

from usercmd import *
import usercmdui
import sysmetrics

if appcon.IsPlayer:
	PLAYERVIEW=CLOSE
	HIERARCHYVIEW=None
	CHANNELVIEW=None
	LINKVIEW=None
	LAYOUTVIEW=None
	USERGROUPVIEW=None

appview={
	0:{'cmd':PLAYERVIEW,'title':'Player','id':'pview_','class':_PlayerView,'hosted':0},
	1:{'cmd':HIERARCHYVIEW,'title':'Structure view','id':'hview_','class':_HierarchyView,'hosted':0},
	2:{'cmd':CHANNELVIEW,'title':'Timeline view','id':'cview_','class':_ChannelView,'hosted':0},
	3:{'cmd':LINKVIEW,'title':'Hyperlinks','id':'leview_','class':_LinkView,'hosted':0},
	4:{'cmd':LAYOUTVIEW,'title':'Layout view','id':'lview_','class':_LayoutView,'hosted':1},
	5:{'cmd':USERGROUPVIEW,'title':'User groups','id':'ugview_','class':_UsergroupView,'hosted':0},
	6:{'cmd':SOURCE,'title':'Source','id':'sview_','class':_SourceView,'hosted':0},
	7:{'cmd':-1,'title':'','id':'cmifview_','class':_CmifView,'hosted':0},
}


# The ChildFrame purpose is to host the views in its client area
# according to the MDIFrameWnd pattern

class ChildFrame(window.MDIChildWnd):
	def __init__(self,view=None,decor=None):
		window.MDIChildWnd.__init__(self,win32ui.CreateMDIChild())
		self._view=view
		self._decor=decor
		self._context=None
		self._sizeFreeze=0

	# Create the OS window and hook messages
	def Create(self, title, rect = None, parent = None, maximize=0):
		self._title=title
		style = win32con.WS_CHILD | win32con.WS_OVERLAPPEDWINDOW
		self.CreateWindow(None, title, style, rect, parent)
		if maximize and parent:parent.maximize(self)
		self.HookMessage(self.onMdiActivate,win32con.WM_MDIACTIVATE)
		self.ShowWindow(win32con.SW_SHOW)

	# Change window style before creation
	def PreCreateWindow(self, csd):
		csd=self._obj_.PreCreateWindow(csd)
		cs=win32mu.CreateStruct(csd)
		return cs.to_csd()

	# Called by the framework when this window is activated or deactivated
	def onMdiActivate(self,params):
		return
		msg=win32mu.Win32Msg(params)
		if msg._lParam==self._hwnd:
			self._view.onActivate(1)
		elif msg._wParam==self._hwnd:
			self._view.onActivate(0)

	# Creates and activates the view 	
	# create view (will be created by default if)
	def OnCreateClient(self, cp, context):
		if context is not None and context.template is not None:
			context.template.CreateView(self, context)
		elif self._view:
			v=self._view
			v.createWindow(self)
			self.SetActiveView(v)
			self.RecalcLayout()
			v.OnInitialUpdate()
		self._hwnd=self.GetSafeHwnd()

	# Set the view from the view class passed as argument
	def setview(self,viewclass,id=None):
		doc=docview.Document(docview.DocTemplate())
		v = viewclass(doc)
		v.CreateWindow(self)
		self.SetActiveView(v)
		self.RecalcLayout()
		v.OnInitialUpdate()

	# Response to user close command. Delegate to view
	# the user is closing the wnd directly
	def OnClose(self):
		# we must let the view to decide:
		if hasattr(self._view,'OnClose'):
			self._view.OnClose()
		else:
			self._obj_.OnClose()

	# Called by the framework after the window has been created
	def InitialUpdateFrame(self, doc, makeVisible):
		pass
	
	# Returns the parent MDIFrameWnd	
	def getMDIFrame(self):
		return self.GetMDIFrame()

	# Returns the cmd class id	
	def GetUserCmdId(self,cmdcl):
		return self.GetMDIFrame().GetUserCmdId(cmdcl)

	# Target for commands that are enabled
	def OnUpdateCmdEnable(self,cmdui):
		cmdui.Enable(1)

	# Target for commands that are dissabled
	def OnUpdateCmdDissable(self,cmdui):
		cmdui.Enable(0)

	# Freeze window size
	def freezeSize(self):
		self._sizeFreeze=1
		l,t,r,b=self.GetWindowRect()
		self._rc_freeze=(0,0,r-l,b-t)
		self.ModifyStyle(win32con.WS_MAXIMIZEBOX|win32con.WS_THICKFRAME,0,0)


# This class implements a View Server. Any client can request
# a view by identifing the view by its string id
class ViewServer:
	def __init__(self,context):
		self._context=context
	
	# Create and initialize a new view object 
	def newview(self,x, y, w, h, title, units = appcon.UNIT_MM, adornments=None,canvassize=None, commandlist=None, strid='cmifview_'):
		viewno=self.getviewno(strid)
		viewclass=appview[viewno]['class'] 
		view=viewclass(self.getdoc())
		self.add_common_interface(view,viewno)
		x=0#if not x or x<0: x=0
		y=0#if not y or y<0: y=0
		if not w or not h:rc=None
		else:
			x,y,w,h=sysmetrics.to_pixels(x,y,w,h,units)
			rc=(x,y,x+w+2*sysmetrics.cxframe,y+h+sysmetrics.cycaption+2*sysmetrics.cyframe)
		f=ChildFrame(view)
		f.Create(title,rc,self._context,0)
		view.init((x,y,w,h),title,units,adornments,canvassize,commandlist)
		self._context.MDIActivate(f)
		if appcon.IsPlayer:
			self._context.setcoords((x, y, w, h),units)
		return view

	# Create a new view object 
	def newviewobj(self,strid):
		viewno=self.getviewno(strid)
		if not self.hosted(viewno):
			return self._newviewobj(viewno)
		else:
			viewclass=appview[viewno]['class']
			viewobj=viewclass()
			self.add_common_interface(viewobj,viewno)
			return viewobj

	# Show the view passed as argument
	def showview(self,view,strid):
		if not view or not view._obj_:
			return
		viewno=self.getviewno(strid)
		self.frameview(view,viewno)

	# Create the view with string id
	def createview(self,strid):
		viewno=self.getviewno(strid)
		view=self._newviewobj(viewno)
		self.frameview(view,viewno)
		return view

	# Create the view with view number
	def _newviewobj(self,viewno):
		viewclass=appview[viewno]['class'] 
		viewobj=viewclass(self.getdoc())
		self.add_common_interface(viewobj,viewno)
		return viewobj

	# Return the view number from its string id
	def getviewno(self,strid):
		for viewno in appview.keys():
			if appview[viewno]['id']==strid:
				return viewno
		raise error,'undefined requested view'

	# Create the child frame that will host this view
	def frameview(self,view,viewno):
		decor=''
		if viewno==self.getviewno('pview_'): decor='lview_'
		f=ChildFrame(view,decor)
		rc=self._context.getPrefRect()
		f.Create(appview[viewno]['title'],None,self._context,0)
		self._context.MDIActivate(f)
	
	# Returns the child frame that hosts this view
	# returns None if not exists
	def getviewframe(self,strid):
		return self.GetParent()

	# Returns the hosted attribute of this view (dialog bar or view)
	def hosted(self,viewno):
		return appview[viewno]['hosted']

	# Adds to the view interface some common attributes
	def add_common_interface(self,viewobj,viewno):
		viewobj.getformserver=self._context.getformserver
		viewobj.getframe=viewobj.GetParent
		viewobj._strid=appview[viewno]['id']
		viewobj._commandlist=[]
		viewobj._title=appview[viewno]['title']
		viewobj._closecmdid=usercmdui.class2ui[appview[viewno]['cmd']].id
