__version__ = "$Id$"

import win32ui, win32con, win32api
Sdk=win32ui.GetWin32Sdk()
Afx=win32ui.GetAfx()

import GenWnd
import usercmd, usercmdui	
from WMEVENTS import *
	
WM_USER_OPEN = win32con.WM_USER+1
WM_USER_CLOSE = win32con.WM_USER+2
WM_USER_PLAY = win32con.WM_USER+3
WM_USER_STOP = win32con.WM_USER+4
WM_USER_PAUSE = win32con.WM_USER+5
WM_USER_GETSTATUS = win32con.WM_USER+6
WM_USER_SETHWND = win32con.WM_USER+7
WM_USER_UPDATE = win32con.WM_USER+8
WM_USER_MOUSE_CLICKED  = win32con.WM_USER+9
WM_USER_MOUSE_MOVED  = win32con.WM_USER+10
WM_USER_SETPOS = win32con.WM_USER+11
WM_USER_SETSPEED = win32con.WM_USER+12
WM_USER_GETPOS = win32con.WM_USER+13

STOPPED, PAUSING, PLAYING = range(3)
UNKNOWN = -1


class ListenerWnd(GenWnd.GenWnd):
	def __init__(self, toplevel):
		GenWnd.GenWnd.__init__(self)
		self._toplevel = toplevel
		self.create()
		self._docmap = {}
		self._slidermap = {}
		from __main__ import commodule
		commodule.SetPyListener(self)

		self.HookMessage(self.OnOpen, WM_USER_OPEN)
		self.HookMessage(self.OnClose, WM_USER_CLOSE)
		self.HookMessage(self.OnPlay, WM_USER_PLAY)
		self.HookMessage(self.OnStop, WM_USER_STOP)
		self.HookMessage(self.OnPause, WM_USER_PAUSE)
		self.HookMessage(self.OnSetWindow, WM_USER_SETHWND)
		self.HookMessage(self.OnUpdate, WM_USER_UPDATE)
		self.HookMessage(self.OnMouseClicked, WM_USER_MOUSE_CLICKED)
		self.HookMessage(self.OnMouseMoved, WM_USER_MOUSE_MOVED)
		self.HookMessage(self.OnSetPos, WM_USER_SETPOS)
		self.HookMessage(self.OnSetSpeed, WM_USER_SETSPEED)

	def OnDestroy(self, params):
		if self.__timerid:
			self.KillTimer(self.__timerid)

	def OnOpen(self, params):
		# lParam (params[3]) is a pointer to a c-string
		filename = Sdk.GetWMString(params[3])
		event = 'OnOpen'
		self._toplevel._peerdocid = params[2]
		try:
			func, arg = self._toplevel.get_embedded(event)
			func(arg, self, event, filename)
			self._docmap[params[2]] = self._toplevel.get_most_recent_docframe()
		except: pass
		self._toplevel._peerdocid = 0
		frame = self._docmap[params[2]] 
		self._slidermap[params[2]] = SliderPeer(frame._cmifdoc, params[2])
	
	def OnClose(self, params):
		id = params[2]
		frame = self._docmap.get(id)
		if frame: frame.SendMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.CLOSE].id)
		del self._docmap[id]
		del self._slidermap[id]

	def OnPlay(self, params):
		frame = self._docmap.get(params[2])
		if frame: frame.SendMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.PLAY].id)

	def OnStop(self, params):
		frame = self._docmap.get(params[2])
		if frame: frame.SendMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.STOP].id)

	def OnPause(self, params):
		frame = self._docmap.get(params[2])
		if frame: frame.SendMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.PAUSE].id)

	def OnSetWindow(self, params):
		frame = self._docmap.get(params[2])
		if frame: frame.setEmbeddedHwnd(params[3])

	def OnUpdate(self, params):
		frame = self._docmap.get(params[2])
		if frame: 
			wnd = frame.getEmbeddedWnd()
			if wnd: wnd.update()

	def OnMouseClicked(self, params):
		frame = self._docmap.get(params[2])
		if frame: 
			wnd = frame.getEmbeddedWnd()
			if wnd:
				x, y = win32api.LOWORD(params[3]),win32api.HIWORD(params[3])
				wnd.onMouseEvent((x,y),Mouse0Press)
				wnd.onMouseEvent((x,y),Mouse0Release)

	def OnMouseMoved(self, params):
		frame = self._docmap.get(params[2])
		if frame: 
			wnd = frame.getEmbeddedWnd()
			if wnd:
				x, y = win32api.LOWORD(params[3]),win32api.HIWORD(params[3])
				wnd.onMouseMoveEvent((x,y))

	def OnSetPos(self, params):
		pos = 0.001*params[3]
		self._slidermap[params[2]].setPos(pos)

	def OnSetSpeed(self, params):
		frame = self._docmap.get(params[2])
		speed = 0.001*params[3]
		self._slidermap[params[2]].setSpeed(speed)

	def GetPos(self, id):
		return int(1000*self._slidermap[id].getPos())

	def GetState(self, id):
		return self._slidermap[id].getState()

############################
class SliderPeer:
	def __init__(self, smildoc, peerid):
		self.__smildoc = smildoc
		self.__peerid = peerid
		player = smildoc.player
		ctx = player.userplayroot.GetContext()
		# indefinite: -1, unknown: 0, else: >0
		fulldur = player.userplayroot.calcfullduration(ctx)
		if not fulldur: fulldur = 0
		# update peer for dur
		try:
			from __main__ import commodule
			if id: commodule.AdviceSetDur(peerid, fulldur)
		except: pass
		self.updateposcallback = player.setstarttime
		self.timefunction = player.scheduler.timefunc
		self.canusetimefunction = player.isplaying
		self.getstatefunction = player.getstate
		self.__updatepeer = 1

	# set player pos
	def setPos(self, pos):
		self.__updatepeer = 0
		self.updateposcallback(pos)
		self.__updatepeer = 1

	def getPos(self):
		if self.canusetimefunction and\
			self.canusetimefunction() and self.timefunction:
			return self.timefunction()
		return 0

	def getState(self):
		return self.getstatefunction()

	# set player speed
	def setSpeed(self, speed):
		self.__updatepeer = 0
		pass # setspeed 
		self.__updatepeer = 1


############################
import win32window
import ddraw
from pywinlib.mfc import window
from appcon import *
import win32mu
import grinsRC

class EmbeddedWnd(win32window.DDWndLayer):
	def __init__(self, wnd, w, h, units, bgcolor, title='', id=0):
		self._cmdframe = wnd
		self._peerwnd = wnd
		self._smildoc = wnd.getgrinsdoc()
		self._rect = 0, 0, w, h
		self._title = title
		self._peerdocid = id
		try:
			from __main__ import commodule
			if id: commodule.AdviceSetSize(id, w, h)
		except: pass
		self._viewport = win32window.Viewport(self, 0, 0, w, h, bgcolor)
		win32window.DDWndLayer.__init__(self, self, bgcolor)
		self.createBackDDLayer(w, h, wnd.GetSafeHwnd())
		self.settitle(title)

	def setPeerDocID(self, id):
		self._peerdocid = id
		x, y, w, h = self._rect
		try:
			from __main__ import commodule
			if id: commodule.AdviceSetSize(id, w, h)
		except: pass

	def setPeerWindow(self, hwnd):
		if Sdk.IsWindow(hwnd):
			self.createPrimaryDDLayer(hwnd)
			self._peerwnd = window.Wnd(win32ui.CreateWindowFromHandle(hwnd))
			self.settitle(self._title)

	def settitle(self,title):
		import urllib
		title=urllib.unquote(title)
		self._title=title
		if self._peerwnd:
			parent = self._peerwnd.GetParent()
			if parent:
				parent.SetWindowText(title)

	#
	# paint
	#
	def update(self, rc=None, exclwnd=None):
		if not self._ddraw or not self._frontBuffer or not self._backBuffer:
			return
		if self._frontBuffer.IsLost():
			if not self._frontBuffer.Restore():
				# we can't do anything for this
				# system is busy with video memory
				#self.InvalidateRect(self.GetClientRect())
				return
		if self._backBuffer.IsLost():
			if not self._backBuffer.Restore():
				# and for this either
				# system should be out of memory
				#self.InvalidateRect(self.GetClientRect())
				return
		
		# do we have anything to update?
		if rc and (rc[2]==0 or rc[3]==0): 
			return 

		self.paint(rc, exclwnd)
		
		if rc is None:
			x, y, w, h = self._viewport._rect
			rcBack = x, y, x+w, y+h
		else:
			rc = self.rectAnd(rc, self._viewport._rect)
			rcBack = rc[0], rc[1], rc[0]+rc[2], rc[1]+rc[3]
		
		rcFront = self.getContextOsWnd().ClientToScreen(rcBack)
		try:
			self._frontBuffer.Blt(rcFront, self._backBuffer, rcBack)
		except ddraw.error, arg:
			print 'EmbeddedWnd.update', arg

	def paint(self, rc=None, exclwnd=None):
		if rc is None:
			x, y, w, h = self._viewport._rect
			rcPaint = x, y, x+w, y+h
		else:
			rc = self.rectAnd(rc, self._viewport._rect)
			rcPaint = rc[0], rc[1], rc[0]+rc[2], rc[1]+rc[3] 

		try:
			self._backBuffer.BltFill(rcPaint, self._ddbgcolor)
		except ddraw.error, arg:
			print 'EmbeddedWnd.paint',arg
			return

		if self._viewport:
			self._viewport.paint(rc, exclwnd)


	def getRGBBitCount(self):
		return self._pxlfmt[0]

	def getPixelFormat(self):
		returnself._pxlfmt

	def getDirectDraw(self):
		return self._ddraw

	def getContextOsWnd(self):
		return self._peerwnd

	def pop(self, poptop=1):
		pass

	def getwindowpos(self):
		return self._viewport._rect

	def closeViewport(self, viewport):
		del viewport
		self.destroyDDLayer()

	def getDrawBuffer(self):
		return self._backBuffer

	def updateMouseCursor(self):
		pass

	def imgAddDocRef(self, file):
		self._cmdframe.imgAddDocRef(file)

	def CreateSurface(self, w, h):
		ddsd = ddraw.CreateDDSURFACEDESC()
		ddsd.SetFlags(ddraw.DDSD_WIDTH | ddraw.DDSD_HEIGHT | ddraw.DDSD_CAPS)
		ddsd.SetCaps(ddraw.DDSCAPS_OFFSCREENPLAIN)
		ddsd.SetSize(w,h)
		dds = self._ddraw.CreateSurface(ddsd)
		dds.BltFill((0, 0, w, h), self._ddbgcolor)
		return dds

	def ltrb(self, xywh):
		x,y,w,h = xywh
		return x, y, x+w, y+h

	def xywh(self, ltrb):
		l,t,r,b = ltrb
		return l, t, r-l, b-t

	def rectAnd(self, rc1, rc2):
		# until we make calcs
		import win32ui
		rc, ans= win32ui.GetWin32Sdk().IntersectRect(self.ltrb(rc1),self.ltrb(rc2))
		if ans:
			return self.xywh(rc)
		return 0, 0, 0, 0

	#
	# Mouse input
	#
	def onMouseEvent(self, point, ev):
		return  self._viewport.onMouseEvent(point, ev)

	def onMouseMoveEvent(self, point):
		return  self._viewport.onMouseMove(0, point)

	def setcursor(self, strid):
		try:
			from __main__ import commodule
			if self._peerdocid:
				commodule.AdviceSetCursor(self._peerdocid, strid)
		except:
			pass

	#
	# OS windows 
	#
	def setClientRect(self, w, h):
		l1, t1, r1, b1 = self.GetWindowRect()
		l2, t2, r2, b2 = self.GetClientRect()
		dxe = dye = 0
		#if (self._exstyle & WS_EX_CLIENTEDGE):
		#	dxe = 2*win32api.GetSystemMetrics(win32con.SM_CXEDGE)
		#	dye = 2*win32api.GetSystemMetrics(win32con.SM_CYEDGE)
		wi = (r1-l1) - (r2-l2)
		wp = w + wi + dxe
		hi = (b1-t1) - (b2-t2)
		hp = h + hi + dye
		flags=win32con.SWP_NOMOVE | win32con.SWP_NOZORDER 		
		self.SetWindowPos(0, (0,0,wp,hp), flags)

	def createOsWnd(self, rect, color, title='Viewport'):
		brush=Sdk.CreateBrush(win32con.BS_SOLID,win32mu.RGB(color),0)
		cursor=Afx.GetApp().LoadStandardCursor(win32con.IDC_ARROW)
		icon=Afx.GetApp().LoadIcon(grinsRC.IDR_GRINSED)
		clstyle=win32con.CS_DBLCLKS
		style=win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CLIPCHILDREN
		exstyle = 0
		strclass=Afx.RegisterWndClass(clstyle,cursor,brush,icon)
		self.CreateWindowEx(exstyle,strclass,title,style,
			self.ltrb(rect), None, 0)		
		self.ShowWindow(win32con.SW_SHOW)

class showmessage:
	def __init__(self, text, mtype = 'message', grab = 1, callback = None,
		     cancelCallback = None, name = 'message',
		     title = 'GRiNS', parent = None, identity = None):
		self._res = win32con.IDOK
		if callback and self._res==win32con.IDOK:
			apply(apply,callback)
		elif cancelCallback and self._res==win32con.IDCANCEL:
			apply(apply,cancelCallback)








 