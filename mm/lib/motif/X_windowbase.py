__version__ = "$Id$"

import Xt, Xm, Xmd, Xlib, X, Xcursorfont
import string, sys
import img

import splash
error = splash.error

Continue = 'Continue'

FALSE, TRUE = 0, 1
ReadMask, WriteMask = 1, 2
SINGLE, HTM, TEXT, MPEG = 0, 1, 2, 3

UNIT_MM, UNIT_SCREEN, UNIT_PXL = 0, 1, 2

RESET_CANVAS, DOUBLE_HEIGHT, DOUBLE_WIDTH = 0, 1, 2

Version = 'X'

toplevel = None

_def_useGadget = 1			# whether to use gadgets or not

from types import *
from WMEVENTS import *
r = Xlib.CreateRegion()
RegionType = type(r)
del r

[_X, _Y, _WIDTH, _HEIGHT] = range(4)

# The _Toplevel class represents the root of all windows.  It is never
# accessed directly by any user code.
class _Toplevel:
	# this is a hack to delay initialization of the Toplevel until
	# we actually need it.
	def __getattr__(self, attr):
		if not self._initialized: # had better exist...
			self._do_init()
			try:
				return self.__dict__[attr]
			except KeyError:
				pass
		raise AttributeError(attr)

	def __init__(self):
		self._initialized = 0
		global toplevel
		if toplevel:
			raise error, 'only one Toplevel allowed'
		toplevel = self

	def _do_init(self):
		if self._initialized:
			raise error, 'can only initialize once'
		self._initialized = 1
		self._closecallbacks = []
		self._subwindows = []
		self._bgcolor = 255, 255, 255 # white
		self._fgcolor =   0,   0,   0 # black
		self._hfactor = self._vfactor = 1.0
		self._cursor = ''
		self._image_size_cache = {}
		self._image_cache = {}
		self._cm_cache = {}
		self._immediate = []
		# file descriptor handling
		self._fdiddict = {}
		items = splash.init()
		for key, val in items:
			setattr(self, '_' + key, val)
		dpy = self._dpy
		main = self._main
		self._delete_window = dpy.InternAtom('WM_DELETE_WINDOW', FALSE)
		self._default_colormap = main.DefaultColormapOfScreen()
		self._default_visual = main.DefaultVisualOfScreen()
## 		self._default_colormap = self._colormap
## 		self._default_visual = self._visual
		self._mscreenwidth = main.WidthMMOfScreen()
		self._mscreenheight = main.HeightMMOfScreen()
		self._screenwidth = main.WidthOfScreen()
		self._screenheight = main.HeightOfScreen()
		self._hmm2pxl = float(self._screenwidth) / self._mscreenwidth
		self._vmm2pxl = float(self._screenheight) / self._mscreenheight
		self._dpi_x = int(25.4 * self._hmm2pxl + .5)
		self._dpi_y = int(25.4 * self._vmm2pxl + .5)
		self._handcursor = dpy.CreateFontCursor(Xcursorfont.hand2)
		self._watchcursor = dpy.CreateFontCursor(Xcursorfont.watch)
		self._channelcursor = dpy.CreateFontCursor(Xcursorfont.draped_box)
		self._linkcursor = dpy.CreateFontCursor(Xcursorfont.hand1)
		self._stopcursor = dpy.CreateFontCursor(Xcursorfont.pirate)
		main.RealizeWidget()

	def close(self):
		for func, args in self._closecallbacks:
			apply(func, args)
		for win in self._subwindows[:]:
			win.close()
		self._closecallbacks = []
		self._subwindows = []
		import os
		for entry in self._image_cache.values():
			try:
				os.unlink(entry[0])
			except:
				pass
		self._image_cache = {}

	def addclosecallback(self, func, args):
		self._closecallbacks.append(func, args)

	def newwindow(self, x, y, w, h, title, visible_channel = TRUE,
		      type_channel = SINGLE, pixmap = 0, units = UNIT_MM,
		      adornments = None, canvassize = None,
		      commandlist = None, resizable = 1):
		return _Window(self, x, y, w, h, title, 0, pixmap, units,
			       adornments, canvassize, commandlist, resizable)

	def newcmwindow(self, x, y, w, h, title, visible_channel = TRUE,
			type_channel = SINGLE, pixmap = 0, units = UNIT_MM,
			adornments = None, canvassize = None,
			commandlist = None, resizable = 1):
		return _Window(self, x, y, w, h, title, 1, pixmap, units,
			       adornments, canvassize, commandlist, resizable)

	def setcursor(self, cursor):
		for win in self._subwindows:
			win.setcursor(cursor)
		self._cursor = cursor
		self._main.Display().Flush()

	def pop(self):
		pass

	def push(self):
		pass

	def usewindowlock(self, lock):
		pass

	def mainloop(self):
		Xt.MainLoop()

	# timer interface
	def settimer(self, sec, cb):
		# sanity check
		func, args = cb
		if not callable(func):
			raise error, 'callback function not callable'
		id = _Timer()
		tid = Xt.AddTimeOut(int(sec * 1000), id.cb, cb)
		id.set(tid)
		return id

	def canceltimer(self, id):
		if id is not None:
			tid = id.get()
			if tid is not None:
				Xt.RemoveTimeOut(tid)
			else:
				print 'canceltimer of bad timer'
			id.destroy()

	# file descriptor interface
	def select_setcallback(self, fd, func, args, mask = ReadMask):
		import Xtdefs
		if type(fd) is not IntType:
			fd = fd.fileno()
		if self._fdiddict.has_key(fd):
			id = self._fdiddict[fd]
			Xt.RemoveInput(id)
			del self._fdiddict[fd]
		if func is None:
			return
		xmask = 0
		if mask & ReadMask:
			xmask = xmask | Xtdefs.XtInputReadMask
		if mask & WriteMask:
			xmask = xmask | Xtdefs.XtInputWriteMask
		self._fdiddict[fd] = Xt.AddInput(fd, xmask,
						 self._input_callback,
						 (func, args))

	def _input_callback(self, client_data, fd, id):
		func, args = client_data
		apply(func, args)

	def _convert_color(self, color, defcm):
		r, g, b = color
		if defcm:
			if self._cm_cache.has_key(`r,g,b`):
				return self._cm_cache[`r,g,b`]
			ri = int(r / 255.0 * 65535.0)
			gi = int(g / 255.0 * 65535.0)
			bi = int(b / 255.0 * 65535.0)
			cm = self._default_colormap
			try:
				color = cm.AllocColor(ri, gi, bi)
			except RuntimeError:
				# can't allocate color; find closest one
				m = 0
				color = None
				# use floats to guard against overflow
				rf = float(ri)
				gf = float(gi)
				bf = float(bi)
				for c in cm.QueryColors(range(256)):
					# calculate distance
					d = (rf-c[1])*(rf-c[1]) + \
					    (gf-c[2])*(gf-c[2]) + \
					    (bf-c[3])*(bf-c[3])
					if color is None or d < m:
						# found one that's closer
						m = d
						color = c
				color = self._colormap.AllocColor(color[1],
							color[2], color[3])
				print "Warning: colormap full, using 'close' color",
				print 'original:',`r,g,b`,'new:',`int(color[1]/65535.0*255.0),int(color[2]/65535.0*255.0),int(color[3]/65535.0*255.0)`
			# cache the result
			self._cm_cache[`r,g,b`] = color[0]
			return color[0]
		r = int(float(r) / 255. * float(self._red_mask) + .5)
		g = int(float(g) / 255. * float(self._green_mask) + .5)
		b = int(float(b) / 255. * float(self._blue_mask) + .5)
		c = (r << self._red_shift) | \
		    (g << self._green_shift) | \
		    (b << self._blue_shift)
		return c

	def getscreensize(self):
		"""Return screen size in pixels"""
		return self._screenwidth, self._screenheight

	def getscreendepth(self):
		"""Return screen depth"""
		return self._visual.depth

class _Timer:
	def set(self, id):
		self.__id = id

	def get(self):
		return self.__id

	def destroy(self):
		self.__id = None

	def cb(self, client_data, id):
		func, args = client_data
		self.__id = None
		apply(func, args)

class _ToolTip:
	def __init__(self):
		self.__tid = None
		self.__popupwidget = None
		self.__tooltips = {}

	def close(self):
		del self.__popupwidget
		del self.__tooltips

	def _addtthandler(self, widget, tooltip):
		self._deltthandler(widget)
		widget.AddEventHandler(X.EnterWindowMask|X.LeaveWindowMask, 0,
				       self.__tooltipeh, tooltip)
		self.__tooltips[widget] = tooltip
		for w in widget.children or []:
			if not w.IsSubclass(Xm.Gadget):
				self._addtthandler(w, tooltip)

	def _deltthandler(self, widget):
		if self.__popupwidget is not None:
			popup, w = self.__popupwidget
			if w is widget:
				popup.Popdown()
				popup.DestroyWidget()
				self.__popupwidget = None
		tt = self.__tooltips.get(widget)
		if tt is None:
			return
		del self.__tooltips[widget]
		widget.RemoveEventHandler(X.EnterWindowMask|X.LeaveWindowMask,
					  0, self.__tooltipeh, tt)

	def __tooltipeh(self, widget, tooltip, event):
		if self.__tid is not None:
			Xt.RemoveTimeOut(self.__tid)
			self.__tid = None
		if self.__popupwidget is not None:
			popup = self.__popupwidget[0]
			self.__popupwidget = None
			popup.Popdown()
			popup.DestroyWidget()
		if event.type == X.EnterNotify:
			self.__tid = Xt.AddTimeOut(500, self.__tooltipto,
						   (tooltip, widget))

	def __tooltipto(self, (tooltip, widget), id):
		self.__tid = None
		try:
			x, y = widget.TranslateCoords(0, 0)
		except:
			# maybe widget was already destroyed
			return
		if not widget.IsRealized() or not widget.IsManaged():
			# widget not visible so don't display tooltip
			return
		if callable(tooltip):
			tooltip = tooltip()
		elif type(tooltip) is type(()):
			tooltip = apply(apply, tooltip)
		# else assume string
		popup = widget.CreatePopupShell('help_popup', Xt.OverrideShell,
				{'visual': toplevel._default_visual,
				 'colormap': toplevel._default_colormap,
				 'depth': toplevel._default_visual.depth})
		self.__popupwidget = popup, widget
		label = popup.CreateManagedWidget('help_label', Xm.Label,
						  {'labelString': tooltip})
		# figure out placement
		val = widget.GetValues(['width', 'height'])
		w = val['width']
		h = val['height']
		# place below center of widget
		x = x+w/2
		y = y+h+5
		# see if it fits there
		val = label.GetValues(['width', 'height'])
		width = val['width']
		height = val['height']
		if x + width > toplevel._screenwidth:
			# too wide: extend to the left
			x = x - width
		if y + height > toplevel._screenheight:
			# too hight: place above widget
			y = y - h - 10 - height
		popup.SetValues({'x': x, 'y': y})
		popup.Popup(0)

class _MenubarSupport(_ToolTip):
	__pixmapcache = {}
	_delete_commands = []

	def __init__(self):
		self.__commandlist = []	# list of currently valid command insts
		self.__commanddict = {}	# mapping of command class to instance
		self.__widgetmap = {}	# mapping of command to list of widgets
		self.__accelmap = {}	# mapping of command to list of keys
		self.__dynamicmenu = {}
		_ToolTip.__init__(self)

	def close(self):
		del self.__commandlist
		del self.__commanddict
		del self.__widgetmap
		del self.__accelmap
		del self.__dynamicmenu
		_ToolTip.close(self)

	def set_commandlist(self, list):
		oldlist = self.__commandlist
		olddict = self.__commanddict
		newlist = []
		newdict = {}
		for cmd in list:
			c = cmd.__class__
			newlist.append(c)
			newdict[c] = cmd
		if newlist != oldlist:
			# there are changes...
			# first remove old commands
			for c in oldlist:
				if not newdict.has_key(c):
					for w in self.__widgetmap.get(c, []):
						w.SetSensitive(0)
						self._deltthandler(w)
				for key in self.__accelmap.get(c, []):
					del self._accelerators[key]
			# then add new commands
			for cmd in list:
				c = cmd.__class__
				if not olddict.has_key(c):
					for w in self.__widgetmap.get(c, []):
						w.SetSensitive(1)
						if cmd.help:
							self._addtthandler(w, cmd.help)
				for key in self.__accelmap.get(c, []):
					self._accelerators[key] = cmd.callback
		self.__commandlist = newlist
		self.__commanddict = newdict

	def _delete_callback(self, widget, client_data, call_data):
		for c in self._delete_commands:
			cmd = self.__commanddict.get(c)
			if cmd is not None and cmd.callback is not None:
				apply(apply, cmd.callback)
				return 1
		return 0
				
	def set_dynamiclist(self, command, list):
		cmd = self.__commanddict.get(command)
		if cmd is None:
			return
		if not cmd.dynamiccascade:
			raise error, 'non-dynamic command in set_dynamiclist'
		callback = cmd.callback
		menu = []
		for entry in list:
			entry = (entry[0], (callback, entry[1])) + entry[2:]
			menu.append(entry)
		for widget in self.__widgetmap.get(command, []):
			if self.__dynamicmenu.get(widget) == menu:
				continue
			submenu = widget.subMenuId
			for w in submenu.children or []:
				w.DestroyWidget()
			if not list:
				if widget.sensitive:
					widget.SetSensitive(0)
				continue
			if not widget.sensitive:
				widget.SetSensitive(1)
			_create_menu(submenu, menu,
				     toplevel._default_visual,
				     toplevel._default_colormap)
			self.__dynamicmenu[widget] = menu

	def set_toggle(self, command, onoff):
		for widget in self.__widgetmap.get(command, []):
			if widget.set != onoff:
				widget.ToggleButtonSetState(onoff, 0)
		
	def __menu_callback(self, widget, client_data, call_data):
		callback = self.__commanddict.get(client_data)
		if callback is not None and callback.callback is not None:
			apply(apply, callback.callback)

	def _create_shortcuts(self, shortcuts):
		for key, c in shortcuts.items():
			if not self.__accelmap.has_key(c):
				self.__accelmap[c] = []
			self.__accelmap[c].append(key)

	def _create_menu(self, menu, list):
		if len(list) > 40:
			menu.numColumns = (len(list) + 29) / 30
			menu.packing = Xmd.PACK_COLUMN
		widgetmap = self.__widgetmap
		for entry in list:
			if entry is None:
				dummy = menu.CreateManagedWidget('separator',
						 Xm.SeparatorGadget, {})
				continue
## 			if type(entry) is StringType:
## 				dummy = menu.CreateManagedWidget(
## 					'menuLabel', Xm.Label,
## 					{'labelString': entry})
## 				continue
			btype = 'p'		# default is pushbutton
			initial = 0
			labelString, callback = entry[:2]
			if len(entry) > 2:
				btype = entry[2]
				if type(btype) is TupleType:
					btype, initial = btype
			if type(callback) is ListType or \
			   callback.dynamiccascade:
				submenu = menu.CreatePulldownMenu('submenu',
					{'colormap': toplevel._default_colormap,
					 'visual': toplevel._default_visual,
					 'depth': toplevel._default_visual.depth,
					 'orientation': Xmd.VERTICAL})
				button = menu.CreateManagedWidget(
					'submenuLabel', Xm.CascadeButton,
					{'labelString': labelString,
					 'subMenuId': submenu})
				if labelString == 'Help':
					menu.menuHelpWidget = button
				if type(callback) is ListType:
					self._create_menu(submenu, callback)
				else:
					button.SetSensitive(0)
					if not widgetmap.has_key(callback):
						widgetmap[callback] = []
					widgetmap[callback].append(button)
			else:
				attrs = {'labelString': labelString,
					 'sensitive': 0}
				if self.__accelmap.has_key(callback):
					attrs['acceleratorText'] = string.join(self.__accelmap[callback], '|')
				if btype == 't':
					attrs['set'] = initial
					button = menu.CreateManagedWidget('menuToggle',
							Xm.ToggleButton, attrs)
					cbfunc = 'valueChangedCallback'
				else:
					button = menu.CreateManagedWidget('menuLabel',
							Xm.PushButton, attrs)
					cbfunc = 'activateCallback'
				button.AddCallback(cbfunc,
						   self.__menu_callback,
						   callback)
				if not widgetmap.has_key(callback):
					widgetmap[callback] = []
				widgetmap[callback].append(button)

	def _create_toolbar(self, tb, list, vertical, visual, colormap):
		import imgformat, imgconvert
		depth = toplevel._imgformat.descr['align'] / 8
		widgetmap = self.__widgetmap
		for entry in list:
			if entry is None:
				if vertical:
					orientation = Xmd.HORIZONTAL
				else:
					orientation = Xmd.VERTICAL
				dummy = tb.CreateManagedWidget(
					'tbSeparator',
					Xm.SeparatorGadget,
					{'orientation': orientation})
				continue
			label, callback = entry[:2]
			btype = 'p'
			initial = 0
			if len(entry) > 2:
				btype = entry[2]
				if type(btype) is TupleType:
					btype, initial = btype
			if btype == 't':
				widgettype = Xm.ToggleButton
				callbacktype = 'valueChangedCallback'
				attrs = {'set': initial}
				if type(label) is DictType and \
				   label.has_key('select'):
					attrs['indicatorOn'] = 0
			else:
				widgettype = Xm.PushButton
				callbacktype = 'activateCallback'
				attrs = {}
			attrs['sensitive'] = 0
			button = tb.CreateManagedWidget(
				'tbutton', widgettype, attrs)
			button.AddCallback(callbacktype,
					   self.__menu_callback,
					   callback)
			if not widgetmap.has_key(callback):
				widgetmap[callback] = []
			widgetmap[callback].append(button)
			if type(label) is StringType:
				button.labelString = label
				continue
			attrs = {'labelType': Xmd.PIXMAP,
				 'marginHeight': 0,
				 'marginWidth': 0}
			pixmaptypes = (
				'label',
				'labelInsensitive',
				'select',
				'selectInsensitive',
				'arm',
				)
			# calculate background RGB values in case
			# (some) images are transparent
			bg = button.background
			if visual.c_class == X.PseudoColor:
				r, g, b = colormap.QueryColor(bg)[1:4]
			else:
				s, m = splash._colormask(visual.red_mask)
				r = int(float((bg >> s) & m) / (m+1) * 256)
				s, m = splash._colormask(visual.green_mask)
				g = int(float((bg >> s) & m) / (m+1) * 256)
				s, m = splash._colormask(visual.blue_mask)
				b = int(float((bg >> s) & m) / (m+1) * 256)
			for pmtype in pixmaptypes:
				rdr = label.get(pmtype)
				if rdr is None:
					continue
				if self.__pixmapcache.has_key(rdr):
					pixmap = self.__pixmapcache[rdr]
				else:
					rdr = imgconvert.stackreader(toplevel._imgformat, rdr)
					if hasattr(rdr, 'transparent'):
						rdr.colormap[rdr.transparent] = r, g, b
					data = rdr.read()
					pixmap = toplevel._main.CreatePixmap(rdr.width,
									     rdr.height)
					ximage = visual.CreateImage(
						visual.depth, X.ZPixmap, 0, data,
						rdr.width, rdr.height,
						depth * 8, rdr.width * depth)
					pixmap.CreateGC({}).PutImage(ximage, 0, 0, 0, 0,
								     rdr.width, rdr.height)
					self.__pixmapcache[label[pmtype]] = pixmap
				attrs[pmtype + 'Pixmap'] = pixmap
			button.SetValues(attrs)

class _Window(_MenubarSupport):
	# Instances of this class represent top-level windows.  This
	# class is also used as base class for subwindows, but then
	# some of the methods are overridden.
	#
	# The following instance variables are used.  Unless otherwise
	# noted, the variables are used both in top-level windows and
	# subwindows.
	# _shell: the Xt.ApplicationShell widget used for the window
	#	(top-level windows only)
	# _form: the Xm.DrawingArea widget used for the window
	# _scrwin: the Xm.ScrolledWindow widget used for scrolling the canvas
	# _clipcanvas: the Xm.DrawingArea widget used by the Xm.ScrolledWindow
	# _colormap: the colormap used by the window (top-level
	#	windows only)
	# _visual: the visual used by the window (top-level windows
	#	only)
	# _depth: the depth of the window in pixels (top-level windows
	#	only)
	# _pixmap: if present, the backing store pixmap for the window
	# _gc: the graphics context with which the window (or pixmap)
	#	is drawn
	# _title: the title of the window (top-level window only)
	# _topwindow: the top-level window
	# _subwindows: a list of subwindows.  This list is also the
	#	stacking order of the subwindows (top-most first).
	#	This list is manipulated by the subwindow.
	# _parent: the parent window (for top-level windows, this
	#	refers to the instance of _Toplevel).
	# _displists: a list of _DisplayList instances
	# _active_displist: the currently rendered _displayList
	#	instance or None
	# _bgcolor: background color of the window
	# _fgcolor: foreground color of the window
	# _transparent: 1 if window has a transparent background (if a
	#	window is transparent, all its subwindows should also
	#	be transparent) -1 if window should be transparent if
	#	there is no active display list
	# _sizes: the position and size of the window in fractions of
	#	the parent window (subwindows only)
	# _rect: the position and size of the window in pixels
	# _region: _rect as an X Region
	# _clip: an X Region representing the visible area of the
	#	window
	# _hfactor: horizontal multiplication factor to convert pixels
	#	to relative sizes
	# _vfactor: vertical multipliction factor to convert pixels to
	#	relative sizes
	# _cursor: the desired cursor shape (only has effect for
	#	top-level windows)
	# _callbacks: a dictionary with callback functions and
	#	arguments
	# _accelerators: a dictionary of accelarators
	# _menu: the pop-up menu for the window
	# _showing: 1 if a box is shown to indicate the size of the
	#	window
	# _exp_reg: a region in which the exposed area is built up
	#	(top-level window only)
	def __init__(self, parent, x, y, w, h, title, defcmap = 0, pixmap = 0,
		     units = UNIT_MM, adornments = None,
		     canvassize = None, commandlist = None, resizable = 1):
		_MenubarSupport.__init__(self)
		menubar = toolbar = shortcuts = None
		if adornments is not None:
			shortcuts = adornments.get('shortcuts')
			menubar = adornments.get('menubar')
			toolbar = adornments.get('toolbar')
			toolbarvertical = adornments.get('toolbarvertical', 0)
			self._delete_commands = adornments.get('close', [])
		if shortcuts is not None:
			self._create_shortcuts(shortcuts)
		self._title = title
		parent._subwindows.insert(0, self)
		self._do_init(parent)
		self._topwindow = self
		self._exp_reg = Xlib.CreateRegion()

		if parent._visual.c_class == X.TrueColor:
			defcmap = FALSE
		if defcmap:
			self._colormap = parent._default_colormap
			self._visual = parent._default_visual
		else:
			self._colormap = parent._colormap
			self._visual = parent._visual
		self._depth = self._visual.depth
		# convert to pixels
		if units == UNIT_MM:
			if x is not None:
				x = int(float(x) * toplevel._hmm2pxl + 0.5)
			if y is not None:
				y = int(float(y) * toplevel._vmm2pxl + 0.5)
			w = int(float(w) * toplevel._hmm2pxl + 0.5)
			h = int(float(h) * toplevel._vmm2pxl + 0.5)
		elif units == UNIT_SCREEN:
			if x is not None:
				x = int(float(x) * toplevel._screenwidth + 0.5)
			if y is not None:
				y = int(float(y) * toplevel._screenheight + 0.5)
			w = int(float(w) * toplevel._screenwidth + 0.5)
			h = int(float(h) * toplevel._screenheight + 0.5)
		elif units == UNIT_PXL:
			if x is not None:
				x = int(x)
			if y is not None:
				y = int(y)
			w = int(w)
			h = int(h)
		else:
			raise error, 'bad units specified'
		# XXX--somehow set the position
		if x is None or y is None:
			geometry = None
		else:
			geometry = '+%d+%d' % (x, y)
		if not title:
			title = ''
		attrs = {'minWidth': min(w, 60),
			 'minHeight': min(h, 60),
			 'colormap': self._colormap,
			 'visual': self._visual,
			 'depth': self._depth,
			 'title': title}
		if geometry:
			attrs['geometry'] = geometry
		if title:
			attrs['iconName'] = title
		shell = parent._main.CreatePopupShell(
			'toplevelShell', Xt.TopLevelShell, attrs)
		shell.AddCallback('destroyCallback', self._destroy_callback, None)
		shell.AddWMProtocolCallback(parent._delete_window,
					    self._delete_callback, None)
		shell.deleteResponse = Xmd.DO_NOTHING
		self._shell = shell
		attrs = {'allowOverlap': 0}
		if not resizable:
			attrs['resizePolicy'] = Xmd.RESIZE_NONE
			attrs['noResize'] = 1
			attrs['resizable'] = 0
		form = shell.CreateManagedWidget('toplevelForm', Xm.Form,
						 attrs)
		fg = self._convert_color(self._fgcolor)
		bg = self._convert_color(self._bgcolor)
		attrs = {'height': max(h, 60),
			 'width': max(w, 60),
			 'resizePolicy': Xmd.RESIZE_NONE,
			 'background': bg,
			 'foreground': fg,
			 'borderWidth': 0,
			 'marginWidth': 0,
			 'marginHeight': 0,
			 'marginTop': 0,
			 'marginBottom': 0,
			 'shadowThickness': 0,
			 'leftAttachment': Xmd.ATTACH_FORM,
			 'rightAttachment': Xmd.ATTACH_FORM,
			 'topAttachment': Xmd.ATTACH_FORM,
			 'bottomAttachment': Xmd.ATTACH_FORM}
		self._menubar = None
		if menubar is not None:
			mb = form.CreateMenuBar(
				'menubar',
				{'leftAttachment': Xmd.ATTACH_FORM,
				 'rightAttachment': Xmd.ATTACH_FORM,
				 'topAttachment': Xmd.ATTACH_FORM})
			mb.ManageChild()
			attrs['topAttachment'] = Xmd.ATTACH_WIDGET
			attrs['topWidget'] = mb
			self._create_menu(mb, menubar)
			self._menubar = mb
		self._toolbar = None
		if toolbar is not None:
			# create a XmForm widget with 2 children:
			# an XmRowColumn widget for the toolbar and an
			# XmFrame widget to fill up the space.
			# The toolbar can be horizontal or vertical
			# depending on toolbarvertical.
			fattrs = {'leftAttachment': Xmd.ATTACH_FORM}
			tbattrs = {'marginWidth': 0,
				   'marginHeight': 0,
				   'spacing': 0,
				   'leftAttachment': Xmd.ATTACH_FORM,
				   'topAttachment': Xmd.ATTACH_FORM,
				   'navigationType': Xmd.NONE,
				   }
			if toolbarvertical:
				tbattrs['orientation'] = Xmd.VERTICAL
				tbattrs['rightAttachment'] = Xmd.ATTACH_FORM
				fattrs['bottomAttachment'] = Xmd.ATTACH_FORM
			else:
				tbattrs['orientation'] = Xmd.HORIZONTAL
				tbattrs['bottomAttachment'] = Xmd.ATTACH_FORM
				fattrs['rightAttachment'] = Xmd.ATTACH_FORM
			if self._menubar is not None:
				fattrs['topAttachment'] = Xmd.ATTACH_WIDGET
				fattrs['topWidget'] = self._menubar
			else:
				fattrs['topAttachment'] = Xmd.ATTACH_FORM
				attrs['topAttachment'] = Xmd.ATTACH_WIDGET
			fr = form.CreateManagedWidget('toolform', Xm.Form,
						      fattrs)
			tb = fr.CreateManagedWidget('toolbar', Xm.RowColumn,
						    tbattrs)
			frattrs = {'rightAttachment': Xmd.ATTACH_FORM,
				   'bottomAttachment': Xmd.ATTACH_FORM,
				   'shadowType': Xmd.SHADOW_OUT}
			if toolbarvertical:
				frattrs['leftAttachment'] = Xmd.ATTACH_FORM
				frattrs['topAttachment'] = Xmd.ATTACH_WIDGET
				frattrs['topWidget'] = tb
				attrs['leftAttachment'] = Xmd.ATTACH_WIDGET
				attrs['leftWidget'] = fr
			else:
				frattrs['leftAttachment'] = Xmd.ATTACH_WIDGET
				frattrs['leftWidget'] = tb
				frattrs['topAttachment'] = Xmd.ATTACH_FORM
				attrs['topWidget'] = fr
			void = fr.CreateManagedWidget('toolframe', Xm.Frame,
						      frattrs)
			self._toolbar = tb
			self._create_toolbar(tb, toolbar, toolbarvertical,
					     self._visual, self._colormap)
		if canvassize is not None and \
		   (menubar is None or (w > 0 and h > 0)):
			form = form.CreateScrolledWindow('scrolledWindow',
				{'scrollingPolicy': Xmd.AUTOMATIC,
				 'width': attrs['width'],
				 'height': attrs['height'],
				 'leftAttachment': Xmd.ATTACH_FORM,
				 'rightAttachment': Xmd.ATTACH_FORM,
				 'bottomAttachment': Xmd.ATTACH_FORM,
				 'topAttachment': attrs['topAttachment'],
				 'topWidget': attrs.get('topWidget',0)})
			form.ManageChild()
			self._scrwin = form
			for w in form.children:
				if w.Class() == Xm.DrawingArea:
					w.AddCallback('resizeCallback',
						self._scr_resize_callback,
						form)
					self._clipcanvas = w
					break
			width, height = canvassize
			# convert to pixels
			if units == UNIT_MM:
				width = int(float(width) * toplevel._hmm2pxl + 0.5)
				height = int(float(height) * toplevel._vmm2pxl + 0.5)
			elif units == UNIT_SCREEN:
				width = int(float(width) * toplevel._screenwidth + 0.5)
				height = int(float(height) * toplevel._screenheight + 0.5)
			elif units == UNIT_PXL:
				width = int(width)
				height = int(height)
			spacing = form.spacing
			attrs['width'] = width - spacing
			attrs['height'] = height - spacing
		self.setcursor(self._cursor)
		if commandlist is not None:
			self.set_commandlist(commandlist)
		if menubar is not None and w == 0 or h == 0:
			# no canvas (DrawingArea) needed
			self._form = None
			shell.Popup(0)
			self._rect = self._region = self._clip = \
				     self._pixmap = self._gc = None
			return
		form = form.CreateManagedWidget('toplevel',
						Xm.DrawingArea, attrs)
		self._form = form
		shell.Popup(0)

		val = form.GetValues(['width', 'height'])
		w, h = val['width'], val['height']
		self._rect = 0, 0, w, h
		self._region = Xlib.CreateRegion()
		apply(self._region.UnionRectWithRegion, self._rect)
		if pixmap:
			self._pixmap = form.CreatePixmap()
			gc = self._pixmap.CreateGC({'foreground': bg,
						    'background': bg})
			gc.FillRectangle(0, 0, w, h)
		else:
			self._pixmap = None
			gc = form.CreateGC({'background': bg})
		gc.foreground = fg
		self._gc = gc
		w = float(w) / toplevel._hmm2pxl
		h = float(h) / toplevel._vmm2pxl
		self._hfactor = parent._hfactor / w
		self._vfactor = parent._vfactor / h
		self._clip = Xlib.CreateRegion()
		apply(self._clip.UnionRectWithRegion, self._rect)
		form.AddCallback('exposeCallback', self._expose_callback, None)
		form.AddCallback('resizeCallback', self._resize_callback, None)
		form.AddCallback('inputCallback', self._input_callback, None)
		self._motionhandlerset = 0

	def _setmotionhandler(self):
		set = not self._buttonregion.EmptyRegion()
		if self._motionhandlerset == set:
			return
		if set:
			func = self._form.AddEventHandler
		else:
			func = self._form.RemoveEventHandler
		func(X.PointerMotionMask, FALSE, self._motion_handler, None)
		self._motionhandlerset = set

	def __repr__(self):
		try:
			title = `self._title`
		except AttributeError:
			title = '<NoTitle>'
		try:
			parent = self._parent
		except AttributeError:
			parent = None
		if parent is None:
			closed = ' (closed)'
		else:
			closed = ''
		return '<_Window instance at %x; title = %s%s>' % \
					(id(self), title, closed)

	def _do_init(self, parent):
		self._parent = parent
		self._subwindows = []
		self._displists = []
		self._active_displist = None
		self._bgcolor = parent._bgcolor
		self._fgcolor = parent._fgcolor
		self._cursor = parent._cursor
		self._curcursor = ''
		self._curpos = None
		self._buttonregion = Xlib.CreateRegion()
		self._callbacks = {}
		self._accelerators = {}
		self._menu = None
		self._transparent = 0
		self._showing = 0
		self._redrawfunc = None
		self._scrwin = None	# Xm.ScrolledWindow widget if any

	def close(self):
		if self._parent is None:
			return		# already closed
		_MenubarSupport.close(self)
		self._parent._subwindows.remove(self)
		self._parent = None
		for win in self._subwindows[:]:
			win.close()
		for dl in self._displists[:]:
			dl.close()
		if self._shell:
			self._shell.DestroyWidget()
		del self._shell
		del self._form
		del self._clip
		del self._topwindow
		del self._gc
		del self._pixmap
		del self._delete_commands

	def is_closed(self):
		return self._parent is None

	def showwindow(self):
		self._showing = 1
		gc = self._gc
		gc.SetClipMask(None)
		gc.foreground = self._convert_color((255,0,0))
		x, y, w, h = self._rect
		gc.DrawRectangle(x, y, w-1, h-1)
		if self._pixmap is not None:
			x, y, w, h = self._rect
			self._pixmap.CopyArea(self._form, gc,
					      x, y, w, h, x, y)
		toplevel._main.UpdateDisplay()

	def dontshowwindow(self):
		if self._showing:
			self._showing = 0
			x, y, w, h = self._rect
			r = Xlib.CreateRegion()
			r.UnionRectWithRegion(x, y, w, h)
			r1 = Xlib.CreateRegion()
			r1.UnionRectWithRegion(x+1, y+1, w-2, h-2)
			r.SubtractRegion(r1)
			self._topwindow._do_expose(r)
			if self._pixmap is not None:
				self._gc.SetRegion(r)
				self._pixmap.CopyArea(self._form, self._gc,
						      x, y, w, h, x, y)

	def getgeometry(self, units = UNIT_MM):
		x, y = self._shell.TranslateCoords(0, 0)
		for w in self._shell.children[0].children:
			if w.Class() == Xm.ScrolledWindow:
				val = w.GetValues(['width', 'height'])
				w = val['width']
				h = val['height']
				break
		else:
			w, h = self._rect[2:]
		if units == UNIT_MM:
			return float(x) / toplevel._hmm2pxl, \
			       float(y) / toplevel._vmm2pxl, \
			       float(w) / toplevel._hmm2pxl, \
			       float(h) / toplevel._vmm2pxl
		elif units == UNIT_SCREEN:
			return float(x) / toplevel._screenwidth, \
			       float(y) / toplevel._screenheight, \
			       float(w) / toplevel._screenwidth, \
			       float(h) / toplevel._screenheight
		elif units == UNIT_PXL:
			return x, y, w, h
		else:
			raise error, 'bad units specified'

	def setcanvassize(self, code):
		if self._scrwin is None:
			raise error, 'no scrollable window'
		# this triggers a resizeCallback
		sp = self._scrwin.spacing
		w = self._scrwin.width
		h = self._scrwin.height
		if code == RESET_CANVAS:
			self._form.SetValues({'width': w-sp, 'height': h-sp})
		elif code == DOUBLE_HEIGHT:
			attrs = {'height': self._form.height * 2}
			if self._clipcanvas.width == self._form.width:
				attrs['width'] = self._form.width - 27
			self._form.SetValues(attrs)
		elif code == DOUBLE_WIDTH:
			attrs = {'width': self._form.width * 2}
			if self._clipcanvas.height == self._form.height:
				attrs['height'] = self._form.height - 27
			self._form.SetValues(attrs)

	def newwindow(self, coordinates, pixmap = 0, transparent = 0, z = 0, type_channel = SINGLE):
		return _SubWindow(self, coordinates, 0, pixmap, transparent, z)

	def newcmwindow(self, coordinates, pixmap = 0, transparent = 0, z = 0, type_channel = SINGLE):
		return _SubWindow(self, coordinates, 1, pixmap, transparent, z)

	def fgcolor(self, color):
		r, g, b = color
		self._fgcolor = r, g, b

	def bgcolor(self, color):
		r, g, b = color
		self._bgcolor = r, g, b
		# set window background if nothing displayed on it
		if self._topwindow is self and not self._active_displist and \
		   not self._subwindows:
			self._form.background = self._convert_color(color)
		if not self._active_displist and self._transparent == 0:
			self._gc.SetRegion(self._clip)
			self._gc.foreground = self._convert_color(color)
			x, y, w, h = self._rect
			self._gc.FillRectangle(x, y, w, h)
			if self._pixmap is not None:
				self._pixmap.CopyArea(self._form, self._gc,
						      x, y, w, h, x, y)

	def setcursor(self, cursor):
		self._cursor = cursor
		if cursor == '' and self._curpos is not None and \
		   apply(self._buttonregion.PointInRegion, self._curpos):
			cursor = 'hand'
		_setcursor(self._shell, cursor)
		self._curcursor = cursor

	def newdisplaylist(self, bgcolor = None):
		if bgcolor is None:
			bgcolor = self._bgcolor
		return _DisplayList(self, bgcolor)

	def settitle(self, title):
		self._shell.SetValues({'title': title, 'iconName': title})

	def pop(self):
		self._shell.Popup(0)

	def push(self):
		self._form.LowerWindow()

	def setredrawfunc(self, func):
		if func is None or callable(func):
			self._redrawfunc = func
		else:
			raise error, 'invalid function'

	def register(self, event, func, arg):
		if func is None or callable(func):
			pass
		else:
			raise error, 'invalid function'
		if event in (ResizeWindow, KeyboardInput, Mouse0Press,
			     Mouse0Release, Mouse1Press, Mouse1Release,
			     Mouse2Press, Mouse2Release):
			self._callbacks[event] = func, arg
		elif event == WindowExit:
			try:
				widget = self._shell
			except AttributeError:
				raise error, 'only WindowExit event for top-level windows'
			widget.deleteResponse = Xmd.DO_NOTHING
			self._callbacks[event] = func, arg
		else:
			raise error, 'Internal error'

	def unregister(self, event):
		try:
			del self._callbacks[event]
		except KeyError:
			pass

	def destroy_menu(self):
		if self._menu:
			self._menu.DestroyWidget()
			for key in self._menuaccel:
				del self._accelerators[key]
		self._menu = None

	def create_menu(self, list, title = None):
		self.destroy_menu()
		menu = self._form.CreatePopupMenu('menu',
				{'colormap': self._colormap,
				 'visual': self._visual,
				 'depth': self._visual.depth})
		if self._visual.depth == 8:
			# make sure menu is readable, even on Suns
			menu.foreground = self._convert_color((0,0,0))
			menu.background = self._convert_color((255,255,255))
		if title:
			list = [title, None] + list
		_create_menu(menu, list, self._visual, self._colormap,
			     self._accelerators)
		self._menuaccel = []
		for entry in list:
			if type(entry) is TupleType:
				key = entry[0]
				if key:
					self._menuaccel.append(key)
		self._menu = menu

	def _convert_color(self, color):
		return self._parent._convert_color(color,
			self._colormap is not self._parent._colormap)

	def _convert_coordinates(self, coordinates, crop = 0):
		# convert relative sizes to pixel sizes relative to
		# upper-left corner of the window
		# if crop is set, constrain the coordinates to the
		# area of the window
		x, y = coordinates[:2]
		if len(coordinates) > 2:
			w, h = coordinates[2:]
		else:
			w, h = 0, 0
		rx, ry, rw, rh = self._rect
##		if not (0 <= x <= 1 and 0 <= y <= 1):
##			raise error, 'coordinates out of bounds'
		px = int((rw - 1) * x + 0.5) + rx
		py = int((rh - 1) * y + 0.5) + ry
		pw = ph = 0
		if crop:
			if px < 0:
				px, pw = 0, px
			if px >= rx + rw:
				px, pw = rx + rw - 1, px - rx - rw + 1
			if py < 0:
				py, ph = 0, py
			if py >= ry + rh:
				py, ph = ry + rh - 1, py - ry - rh + 1
		if len(coordinates) == 2:
			return px, py
##		if not (0 <= w <= 1 and 0 <= h <= 1 and
##			0 <= x + w <= 1 and 0 <= y + h <= 1):
##			raise error, 'coordinates out of bounds'
		pw = int((rw - 1) * w + 0.5) + pw
		ph = int((rh - 1) * h + 0.5) + ph
		if crop:
			if pw <= 0:
				pw = 1
			if px + pw > rx + rw:
				pw = rx + rw - px
			if ph <= 0:
				ph = 1
			if py + ph > ry + rh:
				ph = ry + rh - py
		return px, py, pw, ph

	def _mkclip(self):
		if self._parent is None:
			return
		# create region for whole window
		self._clip = region = Xlib.CreateRegion()
		apply(region.UnionRectWithRegion, self._rect)
		self._buttonregion = bregion = Xlib.CreateRegion()
		# subtract all subwindows
		for w in self._subwindows:
			if w._transparent == 0 or \
			   (w._transparent == -1 and w._active_displist):
				r = Xlib.CreateRegion()
				apply(r.UnionRectWithRegion, w._rect)
				region.SubtractRegion(r)
			w._mkclip()
			bregion.UnionRegion(w._buttonregion)
		# create region for all visible buttons
		if self._active_displist is not None:
			r = Xlib.CreateRegion()
			r.UnionRegion(self._clip)
			r.IntersectRegion(self._active_displist._buttonregion)
			bregion.UnionRegion(r)
		if self._topwindow is self:
			self._setmotionhandler()

	def _delclip(self, child, region):
		# delete child's overlapping siblings
		for w in self._subwindows:
			if w is child:
				break
			if w._transparent == 0 or \
			   (w._transparent == -1 and w._active_displist):
				r = Xlib.CreateRegion()
				apply(r.UnionRectWithRegion, w._rect)
				region.SubtractRegion(r)

	def _image_size(self, file):
		try:
			xsize, ysize = toplevel._image_size_cache[file]
		except KeyError:
			try:
				reader = img.reader(None, file)
			except img.error, arg:
				raise error, arg
			xsize = reader.width
			ysize = reader.height
			toplevel._image_size_cache[file] = xsize, ysize
		return xsize, ysize

	def _prepare_image(self, file, crop, scale, center, coordinates):
		# width, height: width and height of window
		# xsize, ysize: width and height of unscaled (original) image
		# w, h: width and height of scaled (final) image
		# depth: depth of window (and image) in bytes
		oscale = scale
		tw = self._topwindow
		format = toplevel._imgformat
		depth = format.descr['align'] / 8
		reader = None
		if toplevel._image_size_cache.has_key(file):
			xsize, ysize = toplevel._image_size_cache[file]
		else:
			try:
				reader = img.reader(format, file)
			except img.error, arg:
				raise error, arg
			xsize = reader.width
			ysize = reader.height
			toplevel._image_size_cache[file] = xsize, ysize
		top, bottom, left, right = crop
		if top + bottom >= 1.0 or left + right >= 1.0 or \
		   top < 0 or bottom < 0 or left < 0 or right < 0:
			raise error, 'bad crop size'
		top = int(top * ysize + 0.5)
		bottom = int(bottom * ysize + 0.5)
		left = int(left * xsize + 0.5)
		right = int(right * xsize + 0.5)
		if coordinates is None:
			x, y, width, height = self._rect
		else:
			x, y, width, height = self._convert_coordinates(coordinates)
		if scale == 0:
			scale = min(float(width)/(xsize - left - right),
				    float(height)/(ysize - top - bottom))
		elif scale == -1:
			scale = max(float(width)/(xsize - left - right),
				    float(height)/(ysize - top - bottom))
		top = int(top * scale + .5)
		bottom = int(bottom * scale + .5)
		left = int(left * scale + .5)
		right = int(right * scale + .5)
		key = '%s@%f' % (`file`, scale)
		try:
			cfile, w, h, mask = toplevel._image_cache[key]
			image = open(cfile, 'rb').read()
		except:			# reading from cache failed
			w, h = xsize, ysize
			if not reader:
				# we got the size from the cache, don't believe it
				del toplevel._image_size_cache[file]
				return self._prepare_image(file, crop, oscale, center, coordinates)
			if hasattr(reader, 'transparent'):
				import imageop, imgformat
				r = img.reader(imgformat.xrgb8, file)
				for i in range(len(r.colormap)):
					r.colormap[i] = 255, 255, 255
				r.colormap[r.transparent] = 0, 0, 0
				image = r.read()
				if scale != 1:
					w = int(xsize * scale + .5)
					h = int(ysize * scale + .5)
					image = imageop.scale(image, 1,
							xsize, ysize, w, h)
				bitmap = ''
				for i in range(h):
					# grey2mono doesn't pad lines :-(
					bitmap = bitmap + imageop.grey2mono(
						image[i*w:(i+1)*w], w, 1, 128)
				mask = tw._visual.CreateImage(1, X.XYPixmap, 0,
							bitmap, w, h, 8, 0)
			else:
				mask = None
			try:
				image = reader.read()
			except:
				raise error, sys.exc_value
			if scale != 1:
				import imageop
				w = int(xsize * scale + .5)
				h = int(ysize * scale + .5)
				image = imageop.scale(image, depth,
						      xsize, ysize, w, h)
			try:
				import tempfile
				cfile = tempfile.mktemp()
				open(cfile, 'wb').write(image)
				toplevel._image_cache[key] = cfile, w, h, mask
			except:
				print 'Warning: caching image failed'
				try:
					import os
					os.unlink(cfile)
				except:
					pass
		# x -- left edge of window
		# y -- top edge of window
		# width -- width of window
		# height -- height of window
		# w -- width of image
		# h -- height of image
		# left, right, top, bottom -- part to be cropped
		if center:
			x, y = x + (width - (w - left - right)) / 2, \
			       y + (height - (h - top - bottom)) / 2
		xim = tw._visual.CreateImage(tw._depth, X.ZPixmap, 0, image,
					     w, h, depth * 8, w * depth)
		return xim, mask, left, top, x, y, w - left - right, h - top - bottom

	def _destroy_callback(self, form, client_data, call_data):
		self._shell = None
		self.close()

	def _delete_callback(self, form, client_data, call_data):
		if _MenubarSupport._delete_callback(self, form, client_data,
						   call_data):
			return
		try:
			func, arg = self._callbacks[WindowExit]
		except KeyError:
			pass
		else:
			func(arg, self, WindowExit, None)

	def _input_callback(self, form, client_data, call_data):
		if self._parent is None:
			return		# already closed
		try:
			self._do_input_callback(form, client_data, call_data)
		except Continue:
			pass

	def _do_input_callback(self, form, client_data, call_data):
		event = call_data.event
		x, y = event.x, event.y
		for w in self._subwindows:
			if w._region.PointInRegion(x, y):
				try:
					w._do_input_callback(form, client_data, call_data)
				except Continue:
					pass
				else:
					return
		# not in a subwindow, handle it ourselves
		if event.type == X.KeyPress:
			string = Xlib.LookupString(event)[0]
			win = self
			while win is not toplevel:
				if win._accelerators.has_key(string):
					apply(apply, win._accelerators[string])
					return
				win = win._parent
			try:
				func, arg = self._callbacks[KeyboardInput]
			except KeyError:
				pass
			else:
				for c in string:
					func(arg, self, KeyboardInput, c)
		elif event.type == X.KeyRelease:
			pass
		elif event.type in (X.ButtonPress, X.ButtonRelease):
			if event.type == X.ButtonPress:
				if event.button == X.Button1:
					ev = Mouse0Press
				elif event.button == X.Button2:
					ev = Mouse1Press
				elif event.button == X.Button3:
					if self._menu:
						self._menu.MenuPosition(event)
						self._menu.ManageChild()
						return
					ev = Mouse2Press
				else:
					return	# unsupported mouse button
			else:
				if event.button == X.Button1:
					ev = Mouse0Release
				elif event.button == X.Button2:
					ev = Mouse1Release
				elif event.button == X.Button3:
					if self._menu:
						# ignore buttonrelease
						# when we have a menu
						return
					ev = Mouse2Release
				else:
					return	# unsupported mouse button
			try:
				func, arg = self._callbacks[ev]
			except KeyError:
				return
			x, y, width, height = self._rect
			x = float(event.x - x) / width
			y = float(event.y - y) / height
			buttons = []
			adl = self._active_displist
			if adl:
				for but in adl._buttons:
					if but._inside(x, y):
						buttons.append(but)
			func(arg, self, ev, (x, y, buttons))
		else:
			print 'unknown event',`event.type`

	def _expose_callback(self, form, client_data, call_data):
		# no _setcursor during expose!
		if self._parent is None:
			return		# already closed
		e = call_data.event
## 		print 'expose',`self`,e.x,e.y,e.width,e.height,e.count
		# collect redraw regions
		self._exp_reg.UnionRectWithRegion(e.x, e.y, e.width, e.height)
		if e.count == 0:
			# last of a series, do the redraw
			r = self._exp_reg
			self._exp_reg = Xlib.CreateRegion()
			pm = self._pixmap
			if pm is None:
				self._do_expose(r)
			else:
				self._gc.SetRegion(r)
				x, y, w, h = self._rect
				pm.CopyArea(form, self._gc, x, y, w, h, x, y)

	def _do_expose(self, region, recursive = 0):
		if self._parent is None:
			return
		# check if there is any overlap of our window with the
		# area to be drawn
		r = Xlib.CreateRegion()
		r.UnionRegion(self._region)
		r.IntersectRegion(region)
		if r.EmptyRegion():
			# no overlap
			return
		# first redraw opaque subwindow, top-most first
		for w in self._subwindows:
			if w._transparent == 0 or \
			   (w._transparent == -1 and w._active_displist):
				w._do_expose(region, 1)
		# then draw background window
		r = Xlib.CreateRegion()
		r.UnionRegion(self._clip)
		r.IntersectRegion(region)
		if not r.EmptyRegion():
			if self._transparent and not recursive:
				self._parent._do_expose(r)
			elif self._active_displist:
				self._active_displist._render(r)
			elif self._transparent == 0 or self._topwindow is self:
				gc = self._gc
				gc.SetRegion(r)
				gc.foreground = self._convert_color(self._bgcolor)
				apply(gc.FillRectangle, self._rect)
			if self._redrawfunc:
				self._gc.SetRegion(r)
				self._redrawfunc()
		# finally draw transparent subwindow, bottom-most first
		sw = self._subwindows[:]
		sw.reverse()
		for w in sw:
			if w._transparent == 1 or \
			   (w._transparent == -1 and not w._active_displist):
				w._do_expose(region, 1)
		if self._showing:
			self.showwindow()

	def _scr_resize_callback(self, w, form, call_data):
		if self.is_closed():
			return
		width = max(self._form.width, w.width)
		height = max(self._form.height, w.height)
		self._form.SetValues({'width': width, 'height': height})

	def _resize_callback(self, form, client_data, call_data):
		val = self._form.GetValues(['width', 'height'])
		x, y = self._rect[:2]
		width, height = val['width'], val['height']
		self._rect = x, y, width, height
		self._region = Xlib.CreateRegion()
		apply(self._region.UnionRectWithRegion, self._rect)
		# convert pixels to mm
		parent = self._parent
		w = float(width) / toplevel._hmm2pxl
		h = float(height) / toplevel._vmm2pxl
		self._hfactor = parent._hfactor / w
		self._vfactor = parent._vfactor / h
		if self._pixmap is None:
			pixmap = None
		else:
			pixmap = form.CreatePixmap()
			self._pixmap = pixmap
			bg = self._convert_color(self._bgcolor)
			gc = pixmap.CreateGC({'foreground': bg,
					      'background': bg})
			self._gc = gc
			gc.FillRectangle(0, 0, w, h)
		for d in self._displists[:]:
			d.close()
		for w in self._subwindows:
			w._do_resize1()
		self._mkclip()
		self._do_expose(self._region)
		if pixmap is not None:
			gc.SetRegion(self._region)
			pixmap.CopyArea(form, gc, 0, 0, width, height, 0, 0)
		# call resize callbacks
		self._do_resize2()

	def _do_resize2(self):
		for w in self._subwindows:
			w._do_resize2()
		try:
			func, arg = self._callbacks[ResizeWindow]
		except KeyError:
			pass
		else:
			func(arg, self, ResizeWindow, None)

	def _motion_handler(self, form, client_data, event):
		x, y = self._curpos = event.x, event.y
		if self._buttonregion.PointInRegion(x, y):
			cursor = 'hand'
		else:
			cursor = self._cursor
		if self._curcursor != cursor:
			_setcursor(form, cursor)
			self._curcursor = cursor

class _BareSubWindow:
	def __init__(self, parent, coordinates, defcmap, pixmap, transparent, z):
		if z < 0:
			raise error, 'invalid z argument'
		self._z = z
		x, y, w, h = parent._convert_coordinates(coordinates, crop = 1)
		self._rect = x, y, w, h
		self._sizes = coordinates
		x, y, w, h = coordinates
		if w == 0 or h == 0:
			showmessage('Creating subwindow with zero dimension',
				    mtype = 'warning', parent = parent)
		if w == 0:
			w = float(self._rect[_WIDTH]) / parent._rect[_WIDTH]
		if h == 0:
			h = float(self._rect[_HEIGHT]) / parent._rect[_HEIGHT]
		# conversion factors to convert from mm to relative size
		# (this uses the fact that _hfactor == _vfactor == 1.0
		# in toplevel)
		self._hfactor = parent._hfactor / w
		self._vfactor = parent._vfactor / h

		self._convert_color = parent._convert_color
		for i in range(len(parent._subwindows)):
			if self._z >= parent._subwindows[i]._z:
				parent._subwindows.insert(i, self)
				break
		else:
			parent._subwindows.append(self)
		self._do_init(parent)
		self._motion_handler = parent._motion_handler
		if parent._transparent:
			self._transparent = parent._transparent
		else:
			if transparent not in (-1, 0, 1):
				raise error, 'invalid value for transparent arg'
			self._transparent = transparent
		self._topwindow = parent._topwindow

		self._form = parent._form
		self._gc = parent._gc
		self._visual = parent._visual
		self._colormap = parent._colormap
		self._pixmap = parent._pixmap

		self._region = Xlib.CreateRegion()
		apply(self._region.UnionRectWithRegion, self._rect)
		parent._mkclip()
		if self._transparent == 0:
			self._do_expose(self._region)
			if self._pixmap is not None:
				x, y, w, h = self._rect
				self._gc.SetRegion(self._region)
				self._pixmap.CopyArea(self._form, self._gc,
						      x, y, w, h, x, y)

	def __repr__(self):
		return '<_BareSubWindow instance at %x>' % id(self)

	def close(self):
		parent = self._parent
		if parent is None:
			return		# already closed
		self._parent = None
		parent._subwindows.remove(self)
		for win in self._subwindows[:]:
			win.close()
		for dl in self._displists[:]:
			dl.close()
		parent._mkclip()
		parent._do_expose(self._region)
		if self._pixmap is not None:
			x, y, w, h = self._rect
			self._gc.SetRegion(self._region)
			self._pixmap.CopyArea(self._form, self._gc,
					      x, y, w, h, x, y)
		del self._pixmap
		del self._form
		del self._clip
		del self._topwindow
		del self._region
		del self._gc
		del self._convert_color
		del self._motion_handler

	def settitle(self, title):
		raise error, 'can only settitle at top-level'

	def getgeometry(self, units = UNIT_MM):
		return self._sizes

	def setcursor(self, cursor):
		self._cursor = cursor
		if cursor == '' and self._curpos is not None and \
		   apply(self._buttonregion.PointInRegion, self._curpos):
			cursor = 'hand'
		_setcursor(self._form, cursor)
		self._curcursor = cursor

	def pop(self):
		parent = self._parent
		# put self in front of all siblings with equal or lower z
		if self is not parent._subwindows[0]:
			parent._subwindows.remove(self)
			for i in range(len(parent._subwindows)):
				if self._z >= parent._subwindows[i]._z:
					parent._subwindows.insert(i, self)
					break
			else:
				parent._subwindows.append(self)
			# recalculate clipping regions
			parent._mkclip()
			# draw the window's contents
			if self._transparent == 0 or self._active_displist:
				self._do_expose(self._region)
				if self._pixmap is not None:
					x, y, w, h = self._rect
					self._gc.SetRegion(self._region)
					self._pixmap.CopyArea(self._form,
							      self._gc,
							      x, y, w, h, x, y)
		parent.pop()

	def push(self):
		parent = self._parent
		# put self behind all siblings with equal or higher z
		if self is parent._subwindows[-1]:
			# already at the end
			return
		parent._subwindows.remove(self)
		for i in range(len(parent._subwindows)-1,-1,-1):
			if self._z <= parent._subwindows[i]._z:
				parent._subwindows.insert(i+1, self)
				break
		else:
			parent._subwindows.insert(0, self)
		# recalculate clipping regions
		parent._mkclip()
		# draw exposed windows
		for w in self._parent._subwindows:
			if w is not self:
				w._do_expose(self._region)
		if self._pixmap is not None:
			x, y, w, h = self._rect
			self._gc.SetRegion(self._region)
			self._pixmap.CopyArea(self._form, self._gc,
					      x, y, w, h, x, y)

	def _mkclip(self):
		if self._parent is None:
			return
		_Window._mkclip(self)
		region = self._clip
		# subtract overlapping siblings
		self._parent._delclip(self, self._clip)

	def _delclip(self, child, region):
		_Window._delclip(self, child, region)
		self._parent._delclip(self, region)

	def _do_resize1(self):
		# calculate new size of subwindow after resize
		# close all display lists
		parent = self._parent
		self._pixmap = parent._pixmap
		self._gc = parent._gc
		x, y, w, h = parent._convert_coordinates(self._sizes, crop = 1)
		self._rect = x, y, w, h
		w, h = self._sizes[2:]
		if w == 0:
			w = float(self._rect[_WIDTH]) / parent._rect[_WIDTH]
		if h == 0:
			h = float(self._rect[_HEIGHT]) / parent._rect[_HEIGHT]
		self._hfactor = parent._hfactor / w
		self._vfactor = parent._vfactor / h
		self._region = Xlib.CreateRegion()
		apply(self._region.UnionRectWithRegion, self._rect)
		self._active_displist = None
		for d in self._displists[:]:
			d.close()
		for w in self._subwindows:
			w._do_resize1()

class _SubWindow(_BareSubWindow, _Window):
	def __repr__(self):
		return '<_SubWindow instance at %x>' % id(self)

class _DisplayList:
	def __init__(self, window, bgcolor):
		self._window = window
		window._displists.append(self)
		self._buttons = []
		self._buttonregion = Xlib.CreateRegion()
		self._fgcolor = window._fgcolor
		self._bgcolor = bgcolor
		self._linewidth = 1
		self._gcattr = {'foreground': window._convert_color(self._fgcolor),
				'background': window._convert_color(bgcolor),
				'line_width': 1}
		self._list = []
		if window._transparent <= 0:
			self._list.append(('clear',
					self._window._convert_color(bgcolor)))
		self._optimdict = {}
		self._cloneof = None
		self._clonestart = 0
		self._rendered = FALSE
		self._font = None
		self._imagemask = None

	def close(self):
		win = self._window
		if win is None:
			return
		for b in self._buttons[:]:
			b.close()
		win._displists.remove(self)
		self._window = None
		for d in win._displists:
			if d._cloneof is self:
				d._cloneof = None
		if win._active_displist is self:
			win._active_displist = None
			win._buttonregion = Xlib.CreateRegion()
			r = win._region
			if win._transparent == -1 and win._parent is not None and \
			   win._topwindow is not win:
				win._parent._mkclip()
				win._parent._do_expose(r)
			else:
				win._do_expose(r)
			if win._pixmap is not None:
				x, y, w, h = win._rect
				win._gc.SetRegion(win._region)
				win._pixmap.CopyArea(win._form, win._gc,
						     x, y, w, h, x, y)
			if win._transparent == 0:
				w = win._parent
				while w is not None and w is not toplevel:
					w._buttonregion.SubtractRegion(
						win._clip)
					w = w._parent
			win._topwindow._setmotionhandler()
		del self._cloneof
		del self._optimdict
		del self._list
		del self._buttons
		del self._font
		del self._imagemask
		del self._buttonregion

	def is_closed(self):
		return self._window is None

	def clone(self):
		w = self._window
		new = _DisplayList(w, self._bgcolor)
		# copy all instance variables
		new._list = self._list[:]
		new._font = self._font
		if self._rendered:
			new._cloneof = self
			new._clonestart = len(self._list)
			new._imagemask = self._imagemask
		for key, val in self._optimdict.items():
			new._optimdict[key] = val
		return new

	def render(self):
		window = self._window
		if window._transparent == -1 and window._active_displist is None:
			window._active_displist = self
			window._parent._mkclip()
			window._active_displist = None
		for b in self._buttons:
			b._highlighted = 0
		region = window._clip
		# draw our bit
		self._render(region)
		# now draw transparent subwindows
		windows = window._subwindows[:]
		windows.reverse()
		for w in windows:
			if w._transparent and w._active_displist:
				w._do_expose(region, 1)
		# now draw transparent windows that lie on top of us
		if window._topwindow is not window:
			i = window._parent._subwindows.index(window)
			windows = window._parent._subwindows[:i]
			windows.reverse()
			for w in windows:
				if w._transparent and w._active_displist:
					w._do_expose(region, 1)
		# finally, re-highlight window
		if window._showing:
			window.showwindow()
		if window._pixmap is not None:
			x, y, width, height = window._rect
			window._gc.SetRegion(window._clip)
			window._pixmap.CopyArea(window._form, window._gc,
						x, y, width, height, x, y)
		window._buttonregion = bregion = Xlib.CreateRegion()
		bregion.UnionRegion(self._buttonregion)
		bregion.IntersectRegion(window._clip)
		w = window._parent
		while w is not None and w is not toplevel:
			w._buttonregion.SubtractRegion(window._clip)
			w._buttonregion.UnionRegion(bregion)
			w = w._parent
		window._topwindow._setmotionhandler()
		toplevel._main.UpdateDisplay()

	def _render(self, region):
		self._rendered = TRUE
		w = self._window
		clonestart = self._clonestart
		if not self._cloneof or \
		   self._cloneof is not w._active_displist:
			clonestart = 0
		if w._active_displist and self is not w._active_displist and \
		   w._transparent and clonestart == 0:
			w._active_displist = None
			w._do_expose(region)
		gc = w._gc
		gc.ChangeGC(self._gcattr)
		gc.SetRegion(region)
		if clonestart == 0 and self._imagemask:
			# restrict to drawing outside the image
			if type(self._imagemask) is RegionType:
				r = Xlib.CreateRegion()
				r.UnionRegion(region)
				r.SubtractRegion(self._imagemask)
				gc.SetRegion(r)
			else:
				width, height = w._topwindow._rect[2:]
				r = w._form.CreatePixmap(width, height, 1)
				g = r.CreateGC({'foreground': 0})
				g.FillRectangle(0, 0, width, height)
				g.SetRegion(region)
				g.foreground = 1
				g.FillRectangle(0, 0, width, height)
				g.function = X.GXcopyInverted
				apply(g.PutImage, self._imagemask)
				gc.SetClipMask(r)
		for i in range(clonestart, len(self._list)):
			self._do_render(self._list[i], region)
		w._active_displist = self
		for b in self._buttons:
			if b._highlighted:
				b._do_highlight()

	def _do_render(self, entry, region):
		cmd = entry[0]
		w = self._window
		gc = w._gc
		if cmd == 'clear':
			gc.foreground = entry[1]
			apply(gc.FillRectangle, w._rect)
		elif cmd == 'image':
			mask = entry[1]
			if mask:
				# mask is clip mask for image
				width, height = w._topwindow._rect[2:]
				p = w._form.CreatePixmap(width, height, 1)
				g = p.CreateGC({'foreground': 0})
				g.FillRectangle(0, 0, width, height)
				g.SetRegion(region)
				g.foreground = 1
				g.FillRectangle(0, 0, width, height)
				apply(g.PutImage, (mask,) + entry[3:])
				gc.SetClipMask(p)
			else:
				gc.SetRegion(region)
			apply(gc.PutImage, entry[2:])
			if mask:
				gc.SetRegion(region)
		elif cmd == 'line':
			gc.foreground = entry[1]
			gc.line_width = entry[2]
			points = entry[3]
			x0, y0 = points[0]
			for x, y in points[1:]:
				gc.DrawLine(x0, y0, x, y)
				x0, y0 = x, y
		elif cmd == 'box':
			gc.foreground = entry[1]
			gc.line_width = entry[2]
			apply(gc.DrawRectangle, entry[3])
		elif cmd == 'fbox':
			gc.foreground = entry[1]
			apply(gc.FillRectangle, entry[2])
		elif cmd == 'marker':
			gc.foreground = entry[1]
			x, y = entry[2]
			radius = 5 # XXXX
			gc.FillArc(x-radius, y-radius, 2*radius, 2*radius,
				   0, 360*64)
		elif cmd == 'text':
			gc.foreground = entry[1]
			gc.SetFont(entry[2])
			apply(gc.DrawString, entry[3:])

	def fgcolor(self, color):
		if self._rendered:
			raise error, 'displaylist already rendered'
		self._fgcolor = color

	def linewidth(self, width):
		if self._rendered:
			raise error, 'displaylist already rendered'
		self._linewidth = width

	def newbutton(self, coordinates, z = 0):
		if self._rendered:
			raise error, 'displaylist already rendered'
		return _Button(self, coordinates, z)

	def display_image_from_file(self, file, crop = (0,0,0,0), scale = 0,
				    center = 1, coordinates = None):
		if self._rendered:
			raise error, 'displaylist already rendered'
		w = self._window
		image, mask, src_x, src_y, dest_x, dest_y, width, height = \
		       w._prepare_image(file, crop, scale, center, coordinates)
		if mask:
			self._imagemask = mask, src_x, src_y, dest_x, dest_y, width, height
		else:
			r = Xlib.CreateRegion()
			r.UnionRectWithRegion(dest_x, dest_y, width, height)
			self._imagemask = r
		self._list.append(('image', mask, image, src_x, src_y,
				   dest_x, dest_y, width, height))
		self._optimize((2,))
		x, y, w, h = w._rect
		return float(dest_x - x) / w, float(dest_y - y) / h, \
		       float(width) / w, float(height) / h

	def drawline(self, color, points):
		if self._rendered:
			raise error, 'displaylist already rendered'
		w = self._window
		p = []
		for point in points:
			p.append(w._convert_coordinates(point))
		self._list.append(('line', w._convert_color(color),
				   self._linewidth, p))
		self._optimize((1,))

	def drawbox(self, coordinates):
		if self._rendered:
			raise error, 'displaylist already rendered'
		w = self._window
		self._list.append(('box', w._convert_color(self._fgcolor),
				   self._linewidth,
				   w._convert_coordinates(coordinates)))
		self._optimize((1,))

	def drawfbox(self, color, coordinates):
		if self._rendered:
			raise error, 'displaylist already rendered'
		w = self._window
		self._list.append(('fbox', w._convert_color(color),
				   w._convert_coordinates(coordinates)))
		self._optimize((1,))

	def drawmarker(self, color, coordinates):
		if self._rendered:
			raise error, 'displaylist already rendered'
		w = self._window
		self._list.append(('marker', w._convert_color(color),
				   w._convert_coordinates(coordinates)))

	def usefont(self, fontobj):
		if self._rendered:
			raise error, 'displaylist already rendered'
		self._font = fontobj
		return self.baseline(), self.fontheight(), self.pointsize()

	def setfont(self, font, size):
		if self._rendered:
			raise error, 'displaylist already rendered'
		return self.usefont(findfont(font, size))

	def fitfont(self, fontname, str, margin = 0):
		if self._rendered:
			raise error, 'displaylist already rendered'
		return self.usefont(findfont(fontname, 10))

	def baseline(self):
		return self._font.baseline() * self._window._vfactor

	def fontheight(self):
		return self._font.fontheight() * self._window._vfactor

	def pointsize(self):
		return self._font.pointsize()

	def strsize(self, str):
		width, height = self._font.strsize(str)
		return float(width) * self._window._hfactor, \
		       float(height) * self._window._vfactor

	def setpos(self, x, y):
		self._curpos = x, y
		self._xpos = x

	def writestr(self, str):
		if self._rendered:
			raise error, 'displaylist already rendered'
		w = self._window
		list = self._list
		f = self._font._font
		base = self.baseline()
		height = self.fontheight()
		strlist = string.splitfields(str, '\n')
		oldx, oldy = x, y = self._curpos
		if len(strlist) > 1 and oldx > self._xpos:
			oldx = self._xpos
		oldy = oldy - base
		maxx = oldx
		for str in strlist:
			x0, y0 = w._convert_coordinates((x, y))
			list.append('text', self._window._convert_color(self._fgcolor), self._font._font, x0, y0, str)
			self._optimize((1,))
			self._curpos = x + float(f.TextWidth(str)) / w._rect[_WIDTH], y
			x = self._xpos
			y = y + height
			if self._curpos[0] > maxx:
				maxx = self._curpos[0]
		newx, newy = self._curpos
		return oldx, oldy, maxx - oldx, newy - oldy + height - base

	# Draw a string centered in a box, breaking lines if necessary
	def centerstring(self, left, top, right, bottom, str):
		fontheight = self.fontheight()
		baseline = self.baseline()
		width = right - left
		height = bottom - top
		curlines = [str]
		if height >= 2*fontheight:
			import StringStuff
			curlines = StringStuff.calclines([str], self.strsize, width)[0]
		nlines = len(curlines)
		needed = nlines * fontheight
		if nlines > 1 and needed > height:
			nlines = max(1, int(height / fontheight))
			curlines = curlines[:nlines]
			curlines[-1] = curlines[-1] + '...'
		x0 = (left + right) * 0.5	# x center of box
		y0 = (top + bottom) * 0.5	# y center of box
		y = y0 - nlines * fontheight * 0.5
		for i in range(nlines):
			str = string.strip(curlines[i])
			# Get font parameters:
			w = self.strsize(str)[0]	# Width of string
			while str and w > width:
				str = str[:-1]
				w = self.strsize(str)[0]
			x = x0 - 0.5*w
			y = y + baseline
			self.setpos(x, y)
			self.writestr(str)

	def _optimize(self, ignore = ()):
		entry = self._list[-1]
		x = []
		for i in range(len(entry)):
			if i not in ignore:
				z = entry[i]
				if type(z) is ListType:
					z = tuple(z)
				x.append(z)
		x = tuple(x)
		try:
			i = self._optimdict[x]
		except KeyError:
			pass
		else:
			del self._list[i]
			del self._optimdict[x]
			if i < self._clonestart:
				self._clonestart = self._clonestart - 1
			for key, val in self._optimdict.items():
				if val > i:
					self._optimdict[key] = val - 1
		self._optimdict[x] = len(self._list) - 1

class _Button:
	def __init__(self, dispobj, coordinates, z = 0):
		self._dispobj = dispobj
		self._z = z
		buttons = dispobj._buttons
		for i in range(len(buttons)):
			if buttons[i]._z <= z:
				buttons.insert(i, self)
				break
		else:
			buttons.append(self)
		window = dispobj._window
		self._coordinates = coordinates
		x, y, w, h = coordinates
		self._corners = x, y, x + w, y + h
		self._color = self._hicolor = dispobj._fgcolor
		self._width = self._hiwidth = dispobj._linewidth
		self._newdispobj = None
		self._highlighted = 0
		x, y, w, h = window._convert_coordinates(coordinates)
		dispobj._buttonregion.UnionRectWithRegion(x, y, w, h)
		if self._color == dispobj._bgcolor:
			return
		dispobj.drawbox(coordinates)

	def close(self):
		if self._dispobj is None:
			return
		self._dispobj._buttons.remove(self)
		self._dispobj = None
		if self._newdispobj:
			self._newdispobj.close()
			self._newdispobj = None

	def is_closed(self):
		return self._dispobj is None

	def hiwidth(self, width):
		self._hiwidth = width

	def hicolor(self, color):
		self._hicolor = color

	def highlight(self):
		dispobj = self._dispobj
		if dispobj is None:
			return
		window = dispobj._window
		if window._active_displist is not dispobj:
			raise error, 'can only highlight rendered button'
		# if button color and highlight color are all equal to
		# the background color then don't draw the box (and
		# don't highlight).
		if self._color == dispobj._bgcolor and \
		   self._hicolor == dispobj._bgcolor:
			return
		self._highlighted = 1
		self._do_highlight()
		if window._pixmap is not None:
			x, y, w, h = window._rect
			window._pixmap.CopyArea(window._form, window._gc,
						x, y, w, h, x, y)
		toplevel._main.UpdateDisplay()

	def _do_highlight(self):
		window = self._dispobj._window
		gc = window._gc
		gc.foreground = window._convert_color(self._hicolor)
		gc.line_width = self._hiwidth
		gc.SetRegion(window._clip)
		apply(gc.DrawRectangle, window._convert_coordinates(self._coordinates))

	def unhighlight(self):
		dispobj = self._dispobj
		if dispobj is None:
			return
		window = dispobj._window
		if window._active_displist is not dispobj:
			return
		if not self._highlighted:
			return
		self._highlighted = 0
		# calculate region to redisplay
		x, y, w, h = window._convert_coordinates(self._coordinates)
		lw = self._hiwidth / 2
		r = Xlib.CreateRegion()
		r.UnionRectWithRegion(x - lw, y - lw,
				      w + 2*lw + 1, h + 2*lw + 1)
		r1 = Xlib.CreateRegion()
		r1.UnionRectWithRegion(x + lw + 1, y + lw + 1,
				       w - 2*lw - 1, h - 2*lw - 1)
		r.SubtractRegion(r1)
		window._do_expose(r)
		if window._pixmap is not None:
			x, y, w, h = window._rect
			window._pixmap.CopyArea(window._form, window._gc,
						x, y, w, h, x, y)
		toplevel._main.UpdateDisplay()

	def _inside(self, x, y):
		# return 1 iff the given coordinates fall within the button
		if (self._corners[0] <= x <= self._corners[2]) and \
			  (self._corners[1] <= y <= self._corners[3]):
			return TRUE
		else:
			return FALSE

_fontmap = {
	  'Times-Roman': '-*-times-medium-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Times-Italic': '-*-times-medium-i-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Times-Bold': '-*-times-bold-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Utopia': '-*-utopia-medium-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Utopia-Italic': '-*-utopia-medium-i-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Utopia-Bold': '-*-utopia-bold-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Palatino': '-*-palatino-medium-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Palatino-Italic': '-*-palatino-medium-i-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Palatino-Bold': '-*-palatino-bold-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Helvetica': '-*-helvetica-medium-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Helvetica-Bold': '-*-helvetica-bold-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Helvetica-Oblique': '-*-helvetica-medium-o-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Courier': '-*-courier-medium-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Courier-Bold': '-*-courier-bold-r-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Courier-Oblique': '-*-courier-medium-o-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Courier-Bold-Oblique': '-*-courier-bold-o-normal-*-*-*-*-*-*-*-iso8859-1',
	  'Greek': ['-*-arial-regular-r-*-*-*-*-*-*-p-*-iso8859-7',
		    '-*-*-medium-r-*--*-*-*-*-*-*-iso8859-7'],
	  'Greek-Bold': ['-*-arial-bold-r-*--*-*-*-*-p-*-iso8859-7',
			 '-*-*-bold-r-*-*-*-*-*-*-*-*-iso8859-7'],
	  'Greek-Italic': '-*-arial-regular-i-*-*-*-*-*-*-p-*-iso8859-7',
	  }
fonts = _fontmap.keys()

_FOUNDRY = 1
_FONT_FAMILY = 2
_WEIGHT = 3
_SLANT = 4
_SET_WIDTH = 5
_PIXELS = 7
_POINTS = 8
_RES_X = 9
_RES_Y = 10
_SPACING = 11
_AVG_WIDTH = 12
_REGISTRY = 13
_ENCODING = 14

def _parsefontname(fontname):
	list = string.splitfields(fontname, '-')
	if len(list) != 15:
		raise error, 'fontname not well-formed'
	return list

def _makefontname(font):
	return string.joinfields(font, '-')

_fontcache = {}

def findfont(fontname, pointsize):
	key = fontname + `pointsize`
	try:
		return _fontcache[key]
	except KeyError:
		pass
	try:
		fontnames = _fontmap[fontname]
	except KeyError:
		raise error, 'Unknown font ' + `fontname`
	if type(fontnames) is StringType:
		fontnames = [fontnames]
	fontlist = []
	for fontname in fontnames:
		fontlist = toplevel._main.ListFonts(fontname)
		if fontlist:
			break
	if not fontlist:
		# if no matching fonts, use Courier, same encoding
		parsedfont = _parsefontname(fontname)
		font = '-*-courier-*-r-*-*-*-*-*-*-*-*-%s-%s' % \
		       (parsedfont[_REGISTRY], parsedfont[_ENCODING])
		fontlist = toplevel._main.ListFonts(font)
	if not fontlist:
		# if still no matching fonts, use any font, same encoding
		parsedfont = _parsefontname(fontname)
		font = '-*-*-*-*-*-*-*-*-*-*-*-*-%s-%s' % \
		       (parsedfont[_REGISTRY], parsedfont[_ENCODING])
		fontlist = toplevel._main.ListFonts(font)
	if not fontlist:
		# if still no matching fonts, use Courier, any encoding
		fontlist = toplevel._main.ListFonts('-*-courier-*-r-*-*-*-*-*-*-*-*-*-*')
	if not fontlist:
		# if still no matching fonts, use any font, any encoding
		fontlist = toplevel._main.ListFonts('-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
	if not fontlist:
		# if no fonts at all, give up
		raise error, 'no fonts available'
	pixelsize = pointsize * toplevel._dpi_y / 72.0
	bestsize = 0
	psize = pointsize
	scfont = None
	thefont = None
	smsize = 9999			# something big
	smfont = None
	for font in fontlist:
		try:
			parsedfont = _parsefontname(font)
		except:
			# XXX catch parsing errors from the mac
			continue
## scaled fonts don't look very nice, so this code is disabled
##		# scale the font if possible
##		if parsedfont[_PIXELS] == '0':
##			# scalable font
##			parsedfont[_PIXELS] = '*'
##			parsedfont[_POINTS] = `int(pointsize * 10)`
##			parsedfont[_RES_X] = `toplevel._dpi_x`
##			parsedfont[_RES_Y] = `toplevel._dpi_y`
##			parsedfont[_AVG_WIDTH] = '*'
##			thefont = _makefontname(parsedfont)
##			psize = pointsize
##			break
		# remember scalable font in case no other sizes available
		if parsedfont[_PIXELS] == '0':
			scfont = parsedfont
			continue
		p = string.atoi(parsedfont[_PIXELS])
		if p < smsize:
			smfont = font
		# either use closest, or use next smaller
		if abs(pixelsize - p) < abs(pixelsize - bestsize): # closest
##		if p <= pixelsize and p > bestsize: # biggest <= wanted
			bestsize = p
			thefont = font
			psize = p * 72.0 / toplevel._dpi_y
	if thefont is None:
		# didn't find a font
		if scfont is not None:
			# but we found a scalable font, so use it
			scfont[_PIXELS] = '*'
			scfont[_POINTS] = `int(pointsize * 10)`
			scfont[_RES_X] = `toplevel._dpi_x`
			scfont[_RES_Y] = `toplevel._dpi_y`
			scfont[_AVG_WIDTH] = '*'
			thefont = _makefontname(scfont)
			psize = pointsize
		elif smfont is not None:
			# nothing smaller, so take next bigger
			thefont = font
			psize = smsize * 72.0 / toplevel._dpi_y
		else:
			# no font available, complain.  Loudly.
			raise error, "can't find any fonts"
	fontobj = _Font(thefont, psize)
	_fontcache[key] = fontobj
	return fontobj

class _Font:
	def __init__(self, fontname, pointsize):
		self._font = toplevel._main.LoadQueryFont(fontname)
		self._pointsize = pointsize
		self._fontname = fontname
##		print 'Using', fontname

	def close(self):
		self._font = None

	def is_closed(self):
		return self._font is None

	def strsize(self, str):
		strlist = string.splitfields(str, '\n')
		maxwidth = 0
		f = self._font
		maxheight = len(strlist) * (f.ascent + f.descent)
		for str in strlist:
			width = f.TextWidth(str)
			if width > maxwidth:
				maxwidth = width
		return float(maxwidth) / toplevel._hmm2pxl, \
		       float(maxheight) / toplevel._vmm2pxl

	def baseline(self):
		return float(self._font.ascent) / toplevel._vmm2pxl

	def fontheight(self):
		f = self._font
		return float(f.ascent + f.descent) / toplevel._vmm2pxl

	def pointsize(self):
		return self._pointsize

class showmessage:
	def __init__(self, text, mtype = 'message', grab = 1, callback = None,
		     cancelCallback = None, name = 'message',
		     title = 'message', parent = None):
		if grab:
			dialogStyle = Xmd.DIALOG_FULL_APPLICATION_MODAL
			if parent is None:
				parent = toplevel
			while 1:
				if hasattr(parent, '_shell'):
					parent = parent._shell
					break
				if hasattr(parent, '_main'):
					parent = parent._main
					break
				if hasattr(parent, '_parent'):
					parent = parent._parent
				else:
					parent = toplevel
		else:
			dialogStyle = Xmd.DIALOG_MODELESS
			parent = toplevel._main
		if mtype == 'error':
			func = parent.CreateErrorDialog
		elif mtype == 'warning':
			func = parent.CreateWarningDialog
		elif mtype == 'information':
			func = parent.CreateInformationDialog
		elif mtype == 'question':
			func = parent.CreateQuestionDialog
		else:
			func = parent.CreateMessageDialog
		self._grab = grab
		w = func(name, {'messageString': text,
				'title': title,
				'dialogStyle': dialogStyle,
				'resizePolicy': Xmd.RESIZE_NONE,
				'visual': toplevel._default_visual,
				'depth': toplevel._default_visual.depth,
				'colormap': toplevel._default_colormap})
		w.MessageBoxGetChild(Xmd.DIALOG_HELP_BUTTON).UnmanageChild()
		if mtype == 'question' or cancelCallback:
			w.AddCallback('cancelCallback',
				      self._callback, cancelCallback)
		else:
			w.MessageBoxGetChild(Xmd.DIALOG_CANCEL_BUTTON).UnmanageChild()
		w.AddCallback('okCallback', self._callback, callback)
		w.AddCallback('destroyCallback', self._destroy, None)
		w.ManageChild()
		self._widget = w

	def close(self):
		if self._widget:
			w = self._widget
			self._widget = None
			w.UnmanageChild()
			w.DestroyWidget()

	def _callback(self, widget, callback, call_data):
		if not self._widget:
			return
		if callback:
			apply(callback[0], callback[1])
		if self._grab:
			self.close()

	def _destroy(self, widget, client_data, call_data):
		self._widget = None

class Dialog:
	def __init__(self, list, title = '', prompt = None, grab = 1,
		     vertical = 1, parent = None):
		if not title:
			title = ''
		if grab:
			dialogStyle = Xmd.DIALOG_FULL_APPLICATION_MODAL
			if parent is None:
				parent = toplevel
			while 1:
				if hasattr(parent, '_shell'):
					parent = parent._shell
					break
				if hasattr(parent, '_main'):
					parent = parent._main
					break
				if hasattr(parent, '_parent'):
					parent = parent._parent
				else:
					parent = toplevel
		else:
			dialogStyle = Xmd.DIALOG_MODELESS
			parent = toplevel._main
		w = parent.CreateFormDialog('dialog', {'title': title,
				 'dialogStyle': dialogStyle,
				 'resizePolicy': Xmd.RESIZE_NONE,
				 'visual': toplevel._default_visual,
				 'depth': toplevel._default_visual.depth,
				 'colormap': toplevel._default_colormap})
		if vertical:
			orientation = Xmd.VERTICAL
		else:
			orientation = Xmd.HORIZONTAL
		attrs = {'entryAlignment': Xmd.ALIGNMENT_CENTER,
			 'traversalOn': FALSE,
			 'orientation': orientation,
			 'topAttachment': Xmd.ATTACH_FORM,
			 'leftAttachment': Xmd.ATTACH_FORM,
			 'rightAttachment': Xmd.ATTACH_FORM}
		if _def_useGadget:
			label = Xm.LabelGadget
			separator = Xm.SeparatorGadget
			pushbutton = Xm.PushButtonGadget
		else:
			label = Xm.Label
			separator = Xm.Separator
			pushbutton = Xm.PushButton
		if prompt:
			l = w.CreateManagedWidget('label', label,
					{'labelString': prompt,
					 'topAttachment': Xmd.ATTACH_FORM,
					 'leftAttachment': Xmd.ATTACH_FORM,
					 'rightAttachment': Xmd.ATTACH_FORM})
			sep = w.CreateManagedWidget('separator', separator,
					{'topAttachment': Xmd.ATTACH_WIDGET,
					 'topWidget': l,
					 'leftAttachment': Xmd.ATTACH_FORM,
					 'rightAttachment': Xmd.ATTACH_FORM})
			attrs['topAttachment'] = Xmd.ATTACH_WIDGET
			attrs['topWidget'] = sep
		row = w.CreateManagedWidget('buttonrow', Xm.RowColumn, attrs)
		self._buttons = []
		for entry in list:
			if entry is None:
				if vertical:
					attrs = {'orientation': Xmd.HORIZONTAL}
				else:
					attrs = {'orientation': Xmd.VERTICAL}
				dummy = row.CreateManagedWidget('separator',
							separator,
							attrs)
				continue
			if type(entry) is TupleType:
				label, callback = entry[:2]
			else:
				label, callback = entry, None
			if callback and type(callback) is not TupleType:
				callback = (callback, (label,))
			b = row.CreateManagedWidget('button', pushbutton,
						    {'labelString': label})
			if callback:
				b.AddCallback('activateCallback',
					      self._callback, callback)
			self._buttons.append(b)
		self._widget = w
		self._menu = None
		w.AddCallback('destroyCallback', self._destroy, None)
		w.ManageChild()

	# destruction
	def _destroy(self, widget, client_data, call_data):
		self._widget = None
		self._menu = None
		self._buttons = []

	def close(self):
		w = self._widget
		self._widget = None
		w.UnmanageChild()
		w.DestroyWidget()

	# pop up menu
	def destroy_menu(self):
		if self._menu:
			self._widget.RemoveEventHandler(X.ButtonPressMask,
						FALSE, self._post_menu, None)
			self._menu.DestroyWidget()
		self._menu = None

	def create_menu(self, list, title = None):
		self.destroy_menu()
		menu = self._widget.CreatePopupMenu('dialogMenu',
				{'colormap': toplevel._default_colormap,
				 'visual': toplevel._default_visual,
				 'depth': toplevel._default_visual.depth})
		if title:
			list = [title, None] + list
		_create_menu(menu, list, toplevel._default_visual,
			     toplevel._default_colormap)
		self._menu = menu
		self._widget.AddEventHandler(X.ButtonPressMask, FALSE,
					     self._post_menu, None)

	def _post_menu(self, widget, client_data, call_data):
		if not self._menu:
			return
		if call_data.button == X.Button3:
			self._menu.MenuPosition(call_data)
			self._menu.ManageChild()

	# buttons
	def _callback(self, widget, callback, call_data):
		if callback:
			apply(callback[0], callback[1])

	def getbutton(self, button):
		if not 0 <= button < len(self._buttons):
			raise error, 'button number out of range'
		return self._buttons[button].set

	def setbutton(self, button, onoff = 1):
		if not 0 <= button < len(self._buttons):
			raise error, 'button number out of range'
		self._buttons[button].set = onoff

class MainDialog(Dialog):
	pass	# Same as Dialog, for X

_end_loop = '_end_loop'			# exception for ending a loop
class _MultChoice(Dialog):
	def __init__(self, prompt, msg_list, defindex, parent = None):
		self.looping = FALSE
		self.answer = None
		self.msg_list = msg_list
		list = []
		for msg in msg_list:
			list.append(msg, (self.callback, (msg,)))
		Dialog.__init__(self, list, title = None, prompt = prompt,
				grab = TRUE, vertical = FALSE, parent = parent)

	def run(self):
		self.looping = TRUE
		while self.looping:
			event = Xt.NextEvent()
			Xt.DispatchEvent(event)
		return self.answer

	def callback(self, msg):
		for i in range(len(self.msg_list)):
			if msg is self.msg_list[i]:
				self.answer = i
				self.looping = FALSE
				return

def multchoice(prompt, list, defindex, parent = None):
	return _MultChoice(prompt, list, defindex, parent = parent).run()

def beep():
	dpy = toplevel._main.Display()
	dpy.Bell(100)
	dpy.Flush()

def lopristarting():
	pass

def _colormask(mask):
	shift = 0
	while (mask & 1) == 0:
		shift = shift + 1
		mask = mask >> 1
	if mask < 0:
		width = 32 - shift	# assume integers are 32 bits
	else:
		width = 0
		while mask != 0:
			width = width + 1
			mask = mask >> 1
	return shift, (1 << width) - 1

def _generic_callback(widget, (func, args), call_data):
	apply(func, args)

def _create_menu(menu, list, visual, colormap, acc = None, widgets = {}):
	if len(list) > 40:
		menu.numColumns = (len(list) + 29) / 30
		menu.packing = Xmd.PACK_COLUMN
	if _def_useGadget:
		separator = Xm.SeparatorGadget
		label = Xm.LabelGadget
		cascade = Xm.CascadeButtonGadget
		toggle = Xm.ToggleButtonGadget
		pushbutton = Xm.PushButtonGadget
	else:
		separator = Xm.Separator
		label = Xm.Label
		cascade = Xm.CascadeButton
		toggle = Xm.ToggleButton
		pushbutton = Xm.PushButton
	accelerator = None
	for entry in list:
		if entry is None:
			dummy = menu.CreateManagedWidget('separator',
							 separator, {})
			continue
		if type(entry) is StringType:
			dummy = menu.CreateManagedWidget(
				'menuLabel', label,
				{'labelString': entry})
			widgets[entry] = dummy, None
			continue
		btype = 'p'		# default is pushbutton
		initial = 0
		if acc is None:
			labelString, callback = entry[:2]
			if len(entry) > 2:
				btype = entry[2]
				if len(entry) > 3:
					initial = entry[3]
		else:
			accelerator, labelString, callback = entry[:3]
			if len(entry) > 3:
				btype = entry[3]
				if len(entry) > 4:
					initial = entry[4]
		if type(callback) is ListType:
			submenu = menu.CreatePulldownMenu('submenu',
				{'colormap': colormap,
				 'visual': visual,
				 'depth': visual.depth,
				 'orientation': Xmd.VERTICAL})
			button = menu.CreateManagedWidget(
				'submenuLabel', cascade,
				{'labelString': labelString, 'subMenuId': submenu})
			subwidgets = {}
			widgets[labelString] = button, subwidgets
			_create_menu(submenu, callback, visual, colormap, acc,
				     subwidgets)
		else:
			if type(callback) is not TupleType:
				callback = (callback, (labelString,))
			attrs = {'labelString': labelString}
			if accelerator:
				if type(accelerator) is not StringType or \
				   len(accelerator) != 1:
					raise error, 'menu accelerator must be single character'
				acc[accelerator] = callback
				attrs['acceleratorText'] = accelerator
			if btype == 't':
				attrs['set'] = initial
				button = menu.CreateManagedWidget('menuToggle',
						toggle, attrs)
				cbfunc = 'valueChangedCallback'
			else:
				button = menu.CreateManagedWidget('menuLabel',
						pushbutton, attrs)
				cbfunc = 'activateCallback'
			button.AddCallback(cbfunc, _generic_callback, callback)
			widgets[labelString] = button, None

def _setcursor(form, cursor):
	if not form.IsRealized():
		return
	if cursor == 'hand':
		form.DefineCursor(toplevel._handcursor)
	elif cursor == '':
		form.UndefineCursor()
	elif cursor == 'watch':
		form.DefineCursor(toplevel._watchcursor)
	elif cursor == 'channel':
		form.DefineCursor(toplevel._channelcursor)
	elif cursor == 'link':
		form.DefineCursor(toplevel._linkcursor)
	elif cursor == 'stop':
		form.DefineCursor(toplevel._stopcursor)
	else:
		raise error, 'unknown cursor glyph'

def roundi(x):
	if x < 0:
		return roundi(x + 1024) - 1024
	return int(x + 0.5)
