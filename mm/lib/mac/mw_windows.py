import Win
import Qd
import QuickDraw
import Dlg
import Ctl
import Controls
import Events
import MacOS
import mac_image
import imgformat
import img
import imageop
import sys
import math
import MenuTemplate
import usercmd

#
# Stuff we use from other mw_ modules
#
from WMEVENTS import *
import mw_globals
from mw_globals import error, Continue
from mw_globals import UNIT_MM, UNIT_SCREEN, UNIT_PXL
from mw_globals import RESET_CANVAS, DOUBLE_HEIGHT, DOUBLE_WIDTH
from mw_globals import FALSE, TRUE
from mw_globals import _X, _Y, _WIDTH, _HEIGHT
from mw_globals import ARR_LENGTH, ARR_SLANT, ARR_HALFWIDTH
import mw_displaylist
import mw_menucmd
import mw_widgets

#
# Scrollbar constants
#
SCROLLBARSIZE=16		# Full size, overlapping 1 pixel with window border
# Parts of the scrollbar we track:
TRACKED_PARTS=(Controls.inUpButton, Controls.inDownButton,
		Controls.inPageUp, Controls.inPageDown)

#
# Cache for image sizes
#
_size_cache = {}

#
# Globals for create_box()
#
_rb_message = """\
Use left mouse button to draw a box.
Click `OK' when ready or `Cancel' to cancel."""
_rb_done = '_rb_done'			# exception to stop create_box loop
_in_create_box = None

class _WindowGroup:
	"""A windowgroup serves two purposes: it is an "invisible window",
	something that menu commands are attached to (which then become active
	if this group is active) and it is a grouping mechanism (each window
	belongs to a windowgroup). Together this has the effect of enabling
	the right commands for both the current, topmost, window and the
	document it belongs to"""
	
	def __init__(self, title, cmdlist):
		self._title = title
		self._cmds_toggled = {}
		self._dict = {}
		self._dynamic_list_dict = {}
		self.set_commandlist(cmdlist)
		
	def __repr__(self):
		return '<WindowGroup %s>'%self._title
	
	def settitle(self, title):
		self._title = title
		mw_globals.toplevel._changed_group_commands() # XXXX Is this good enough?
		
	def close(self):
		mw_globals.toplevel._close_windowgroup(self)
		del self._dict
		
	def pop(self):
		# NOTE: This method should only be called for groups, not windows
		mw_globals.toplevel._install_group_commands(self)
		
	def create_menu(self, menu, title):
		pass
		
	def set_dynamiclist(self, cmd, list):
		self._dynamic_list_dict[cmd] = list
		mw_globals.toplevel._changed_group_commands()
		
	def set_toggle(self, cmd, onoff):
		self._cmds_toggled[cmd] = onoff
		mw_globals.toplevel._changed_group_commands()
		
	def get_toggle(self, cmd):
		if self._cmds_toggled.has_key(cmd):
			return self._cmds_toggled[cmd]
		return 0
		
	def toggle_toggle(self, cmd):
		old = self.get_toggle(cmd)
		self.set_toggle(cmd, not old)
		
	def _set_cmd_dict(self, dict):
		self._dict = dict
		mw_globals.toplevel._changed_group_commands()
		
	def set_commandlist(self, list):
		dict = {}
		for item in list:
			cmd = item.__class__
### This code does not work anymore with per-window button commands.
### but we work around it by adding those commands to the UNUSED_COMMANDS
### set.
			if __debug__:
				if not mw_globals._all_commands.has_key(cmd):
					print 'Warning: user has no way to issue command', cmd
			dict[cmd] = item
		self._set_cmd_dict(dict)
		
	def has_command(self, cmd):
		return self._dict.has_key(cmd)
		
	def get_command_callback(self, cmd):
		if self._dict.has_key(cmd):
			return self._dict[cmd].callback
		return None

	def call_command(self, cmd):
		callback = self.get_command_callback(cmd)
		if not callback:
			print 'No callback for command', cmd
		else:
			func, arglist = callback
			apply(func, arglist)
			
	def get_command_dynamic_list(self, cmd):
		if self._dynamic_list_dict.has_key(cmd):
			return self._dynamic_list_dict[cmd]
		return None
			
	def close_window_command(self):
		# First see whether there's a WindowExit handler
		if self.has_command(MenuTemplate.CLOSE_WINDOW):
			self.call_command(MenuTemplate.CLOSE_WINDOW)
			return 1
		if self._eventhandlers.has_key(WindowExit):
			func, arg = self._eventhandlers[WindowExit]
			func(arg, self, WindowExit, (0, 0, 0))
			return 1
		return 0

class _CommonWindow:
	"""Code common to toplevel window and subwindow"""
		
	def __init__(self, parent, wid, z=0):
		self._z = z
		for i in range(len(parent._subwindows)):
			if self._z >= parent._subwindows[i]._z:
				parent._subwindows.insert(i, self)
				break
		else:
			parent._subwindows.append(self)
		self._parent = parent
		self._wid = wid
		self._subwindows = []
		self._displists = []
		self._bgcolor = parent._bgcolor
		self._fgcolor = parent._fgcolor
		self._clip = None
		self._button_region = None
		self._active_displist = None
		self._eventhandlers = {}
		self._redrawfunc = None
		self._clickfunc = None
		self._accelerators = {}
		self._active_movie = 0
		self._popupmenu = None
		self._outline_color = None
		self._rb_dialog = None
		self._wtd_cursor = ''
		
	def close(self):
		"""Close window and all subwindows"""
		if self._parent is None:
			return		# already closed
		if self._rb_dialog:
			self._rb_cancel()
		self._set_movie_active(0)
		Qd.SetPort(self._wid)
		self._parent._subwindows.remove(self)
		Win.InvalRect(self.qdrect())
		self._parent._close_wid(self._wid)
		self._parent = None

		for win in self._subwindows[:]:
			win.close()
		for dl in self._displists[:]:
			dl.close()

		if self._clip:
			Qd.DisposeRgn(self._clip)
		del self._clip
		
		if self._button_region:
			Qd.DisposeRgn(self._button_region)
		del self._button_region
		
		del self._subwindows
		del self._displists
		del self._active_displist
		del self._eventhandlers
		del self._redrawfunc
		del self._clickfunc
		del self._wid
		del self._accelerators
		
	def getrect(self):
		return self._rect

	def _set_movie_active(self, isactive):
		if isactive == self._active_movie:
			return
		self._active_movie = isactive
		mw_globals.toplevel._set_movie_active(isactive)
			
	def _close_wid(self, wid):
		"""Called by children to close wid. Only implements real close
		at TopLevel"""
		pass

	def _clipchanged(self):
		"""Called when the clipping region is possibly changed"""
		if not self._parent or not self._wid:
			return
		if self._clip:
			Qd.DisposeRgn(self._clip)
		self._clip = None
		# And inform our children...
		for ch in self._subwindows:
			ch._clipchanged()
			
	def _buttonschanged(self):
		"""Buttons have changed, zap the mouse region cache. This escalates upwards"""
		if not self._parent or not self._wid:
			return
		if self._button_region:
			Qd.DisposeRgn(self._button_region)
			self._button_region = None
		# And inform our parent...
		self._parent._buttonschanged()
		
	def _zapregions(self):
		"""Invalidate button regions because of mousemove. Escalates downwards"""
		if self._button_region:
			Qd.DisposeRgn(self._button_region)
			self._button_region = None
		for win in self._subwindows:
			win._zapregions()
		
	def is_closed(self):
		"""Return true if window is closed"""
		return self._parent is None

	def newwindow(self, (x, y, w, h), pixmap = 0, transparent = 0, z=0,
		      type_channel = None):
		"""Create a new subwindow"""
		rv = _SubWindow(self, self._wid, (x, y, w, h), 0, pixmap,
				transparent, z)
		self._clipchanged()
		return rv

	def newcmwindow(self, (x, y, w, h), pixmap = 0, transparent = 0, z=0,
			type_channel = None):
		"""Create a new subwindow"""
		rv = _SubWindow(self, self._wid, (x, y, w, h), 1, pixmap,
				transparent, z)
		self._clipchanged()
		return rv

	def fgcolor(self, color):
		"""Set foregroundcolor to 3-tuple 0..255"""
		self._fgcolor = self._convert_color(color)

	def bgcolor(self, color):
		"""Set backgroundcolor to 3-tuple 0..255"""
		self._bgcolor = self._convert_color(color)
		
	def showwindow(self, color=(255, 0, 0)):
		"""Highlight the window"""
		self._outline_color = self._convert_color(color)
		Qd.SetPort(self._wid)
		Win.InvalRect(self.qdrect())
		
	def dontshowwindow(self):
		"""Don't highlight the window"""
		if not self._outline_color is None:
			self._outline_color = None
			Qd.SetPort(self._wid)
			Win.InvalRect(self.qdrect())
		pass

	def setcursor(self, cursor):
		if cursor == 'watch':
			cursor = ''
		self._wtd_cursor = cursor
		## Warn parent? self._parent.setcursor(cursor)

	def newdisplaylist(self, *bgcolor):
		"""Return new, empty display list"""
		if bgcolor != ():
			bgcolor = self._convert_color(bgcolor[0])
		else:
			bgcolor = self._bgcolor
		return mw_displaylist._DisplayList(self, bgcolor)

	def setredrawfunc(self, func):
		if func is None or callable(func):
			self._redrawfunc = func
		else:
			raise error, 'invalid function'

	def setclickfunc(self, func):
		"""Intercept low-level mouse clicks (mac-specific)"""
		if func is None or callable(func):
			self._clickfunc = func
		else:
			raise error, 'invalid function'

	def register(self, event, func, arg):
		if func is None or callable(func):
			self._eventhandlers[event] = (func, arg)
		else:
			raise error, 'invalid function'

	def unregister(self, event):
		del self._eventhandlers[event]

	def destroy_menu(self):
		self._accelerators = {}
		self._popupmenu = None
		pass

	def create_menu(self, list, title = None):
		self._accelerators = {}
		self._popupmenu = mw_menucmd.FullPopupMenu(list, title,
						self._accelerators)

	def _image_size(self, file):
		"""Backward compatability: return wh of image given filename"""
		if _size_cache.has_key(file):
			return _size_cache[file]
		try:
			reader = img.reader(None, file)
		except img.error, arg:
			raise error, arg
		width = reader.width
		height = reader.height
		_size_cache[file] = width, height
		return width, height

	def _prepare_image(self, file, crop, scale, center, coordinates):
		# width, height: width and height of window
		# xsize, ysize: width and height of unscaled (original) image
		# w, h: width and height of scaled (final) image
		# depth: depth of window (and image) in bytes
		oscale = scale
		format = imgformat.macrgb16
		depth = format.descr['size'] / 8

		try:
			reader = img.reader(format, file)
		except img.error, arg:
			raise error, arg
		w = xsize = reader.width
		h = ysize = reader.height
		_size_cache[file] = xsize, ysize
			
		top, bottom, left, right = crop
		top = int(top * ysize + 0.5)
		bottom = int(bottom * ysize + 0.5)
		left = int(left * xsize + 0.5)
		right = int(right * xsize + 0.5)
		if coordinates is None:
			x, y, width, height = self._convert_coordinates((0,0,1,1))
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

		
		if hasattr(reader, 'transparent'):
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
			mask = (mac_image.mkbitmap(w, h, imgformat.xbmpacked,
						   bitmap), bitmap)
		else:
			mask = None
		try:
			image = reader.read()
		except:
			raise error, 'unspecified error reading image'
		if scale != 1:
			w = int(xsize * scale + .5)
			h = int(ysize * scale + .5)
			image = imageop.scale(image, depth,
					      xsize, ysize, w, h)

		if center:
			x, y = x + (width - (w - left - right)) / 2, \
			       y + (height - (h - top - bottom)) / 2
		xim = mac_image.mkpixmap(w, h, format, image)
		return (xim, image), mask, left, top, \
		       x, y, w - left - right, h - top - bottom

	def _convert_coordinates(self, coordinates):
		"""Convert fractional xywh in our space to pixel-xywh
		in toplevel-window relative pixels"""

		xf, yf = self._scrollsizefactors()		
		x, y = coordinates[:2]
		x, y = x*xf, y*yf
		px = int(self._rect[_WIDTH] * x)  + self._rect[_X]
		py = int(self._rect[_HEIGHT] * y)  + self._rect[_Y]
		if len(coordinates) == 2:
			return px, py
		w, h = coordinates[2:]
		w, h = w*xf, h*yf
		pw = int(self._rect[_WIDTH] * w)
		ph = int(self._rect[_HEIGHT] * h)
		return px, py, pw, ph
		
	def _scrolloffset(self):
		"""Return the x,y to be added to coordinates to convert them to QD
		values"""
		return 0, 0
		
	def _scrollsizefactors(self):
		"""Return the factor with which to multiply x/y sizes before returning
		them to upper layers, i.e. 1 divided by the amount of the window visible"""
		return 1, 1
		
	def _convert_qdcoords(self, coordinates):
		"""Convert QD coordinates to fractional xy or xywh coordinates"""
		x0, y0 = coordinates[:2]
		wx, wy, ww, wh = self._convert_coordinates((0,0,1,1))
		xscrolloff, yscrolloff = self._scrolloffset()
		# XXXXSCROLL scrollsizefactors!
		wx, wy = wx+xscrolloff, wy+yscrolloff
		x, y = x0-wx, y0-wy
		if len(coordinates) == 2:
			rv = float(x)/ww, float(y)/wh
		else:
			x1, y1 = coordinates[2:]
			w, h = x1-x0, y1-y0
			rv = float(x)/ww, float(y)/wh, float(w)/ww, float(h)/wh
		return rv
		
	def _convert_color(self, (r, g, b)):
		"""Convert 8-bit r,g,b tuple to 16-bit r,g,b tuple"""
		return r*0x101, g*0x101, b*0x101


	def qdrect(self):
		"""return our xywh rect (in pixels) as quickdraw ltrb style.
		This is the on-screen rectangle, not the full drawing area"""
		return self._rect[0], self._rect[1], \
		       self._rect[0]+self._rect[2], \
			self._rect[1]+self._rect[3]
			
	def _activate(self, active):
		for ch in self._subwindows:
			ch._activate(active)
		if active:
			evt = WindowActivate
		else:
			evt = WindowDeactivate
		try:
			func, arg = self._eventhandlers[evt]
		except KeyError:
			sys.exc_traceback = None
			return
		func(arg, self, (0, 0, 0))
		
	def _get_button_region(self):
		"""Return the region that contains all buttons, in global coordinates"""
		if not self._button_region:
			self._button_region = Qd.NewRgn()
			for ch in self._subwindows:
				rgn = ch._get_button_region()
				Qd.UnionRgn(self._button_region, rgn, self._button_region)
			if self._active_displist:
				rgn = self._active_displist._get_button_region()
				# XXXX Should we AND with clip?
				Qd.UnionRgn(self._button_region, rgn, self._button_region)
				Qd.DisposeRgn(rgn)
		return self._button_region
		
	def _iscontrolclick(self, down, where, event):
		# Overriden for toplevel window
		return 0
				
	def _contentclick(self, down, where, event, shifted):
		"""A click in our content-region. Note: this method is extended
		for top-level windows (to do global-to-local coordinate
		transforms)"""
		#
		# If we are rubberbanding handle that first.
		#
		if self._rb_dialog and down:
				if self._rb_mousedown(where, shifted):
					return
		#
		# First see whether the click is in any of our children
		#
		for ch in self._subwindows:
			if Qd.PtInRect(where, ch.qdrect()):
				try:
					ch._contentclick(down, where, event,
							 shifted)
				except Continue:
					pass
				else:
					return
		#
		# Then, check for a click in a control
		#
		if self._iscontrolclick(down, where, event):
			return
		#
		# Next, check for popup menu, if we have one
		#
		if shifted and self._popupmenu:
			# Convert coordinates back to global
			Qd.SetPort(self._wid)
			# XXXX Is this correct? y, x??
			y, x = Qd.LocalToGlobal(where)
			self._popupmenu.popup(x, y, event, window=self)
			return
		#
		# It is really in our canvas. Do we have a low-level
		# click handler?
		#
		if self._clickfunc:
			self._clickfunc(down, where, event)
			return
		#
		# Convert to our type of event and call the
		# appropriate handler.
		#
		if not shifted:
			if down:
				evttype = Mouse0Press
			else:
				evttype = Mouse0Release
		else:
			if down:
				evttype = Mouse2Press
			else:
				evttype = Mouse2Release

		try:
			func, arg = self._eventhandlers[evttype]
		except KeyError:
			sys.exc_traceback = None
			return # Not wanted
			
		x, y = self._convert_qdcoords(where)
		
		buttons = []
		if self._active_displist:
			for b in self._active_displist._buttons:
				if b._inside(x, y):
					buttons.append(b)
				
		func(arg, self, evttype, (x, y, buttons))
		
	def _keyboardinput(self, char, where, event):
		#
		# First see whether position is in any of our children
		#
		for ch in self._subwindows:
			if Qd.PtInRect(where, ch.qdrect()):
				try:
					handled = ch._keyboardinput(char,
							      where, event)
				except Continue:
					pass
				else:
					return handled
		#
		# Next, check any popup menu accelerators
		#
		try:
			func, args = self._accelerators[char]
		except KeyError:
			pass
		else:
			apply(func, args)
			return 1
		#
		# Finally check for a KeyboardInput handler
		#
		try:
			func, arg = self._eventhandlers[KeyboardInput]
		except KeyError:
			return 0
		else:
			func(arg, self, KeyboardInput, char)
			return 1
		
	def _do_resize2(self):
		for w in self._subwindows:
			w._do_resize2()
		try:
			func, arg = self._eventhandlers[ResizeWindow]
		except KeyError:
			pass
		else:
			func(arg, self, ResizeWindow, None)
		
	def _redraw(self, rgn=None):
		"""Set clipping and color, redraw, redraw children"""
		if self._parent is None:
			return
		if not self._clip:
			self._mkclip()
			
		# First do opaque subwindows, topmost first
		still_to_do = []
		for child in self._subwindows:
			if child._transparent == 0 or \
			   (child._transparent == -1 and
			    child._active_displist):
				child._redraw(rgn)
			else:
				still_to_do.append(child)
		
		# Next do ourselves
		saveclip = Qd.NewRgn()
		Qd.GetClip(saveclip)
		Qd.SetClip(self._clip)
		if not self._outline_color is None:
			Qd.RGBForeColor(self._outline_color)
			rect = self.qdrect()
			Qd.FrameRect(rect)
		Qd.RGBBackColor(self._bgcolor)
		Qd.RGBForeColor(self._fgcolor)
		if self._redrawfunc:
			self._redrawfunc()
		else:
			self._do_redraw()
		Qd.SetClip(saveclip)
		Qd.DisposeRgn(saveclip)
		
		# Then do transparent children bottom-to-top
		still_to_do.reverse()
		for child in still_to_do:
					child._redraw(rgn)
					
		# Last, do the rubber box, if rubberboxing
		if self._rb_dialog:
			self._rb_redraw()
					
	def _do_redraw(self):
		"""Do actual redraw"""
		if self._active_displist:
			self._active_displist._render()
		elif self._transparent == 0 or self._istoplevel:
			Qd.EraseRect(self.qdrect())
			
	def _macsetwin(self):
		"""Start drawing (by upper layer) in this window"""
		Qd.SetPort(self._wid)
		
	def create_box(self, msg, callback, box = None):
		global _in_create_box
		if _in_create_box:
			raise 'Recursive create_box'
		if self.is_closed():
			apply(callback, ())
			return
		_in_create_box = self
		self.pop()
		if msg:
			msg = msg + '\n\n' + _rb_message
		else:
			msg = _rb_message
		self._rb_dl = self._active_displist
		if self._rb_dl:
			d = self._rb_dl.clone()
		else:
			d = self.newdisplaylist()
		self._rb_transparent = []
		sw = self._subwindows[:]
		sw.reverse()
		for win in sw:
			b = win._sizes
			if b != (0, 0, 1, 1):
				d.drawbox(b)
		d.render()
		self._rb_display = d
		if box:
			x0, y0, w, h = self._convert_coordinates(box)
			self._rb_box = (x0, y0, x0+w, y0+h)
		else:
			self._rb_box = None
		self._rb_dragpoint = None
		Qd.SetPort(self._wid)
		Win.InvalRect(self.qdrect())
		self._rb_finished = 0
		self._rb_dialog = showmessage(
			msg, mtype = 'message', grab = 0,
			callback = (self._rb_done, ()),
			cancelCallback = (self._rb_cancel, ()))
		self._rb_callback = callback

		mw_globals.toplevel.grabwids([self._rb_dialog._dialog, self._wid])
		while not self._rb_finished:
			mw_globals.toplevel._eventloop(100)
		mw_globals.toplevel.grab(None)

	# supporting methods for create_box
	def _rb_finish(self):
		global _in_create_box
		_in_create_box = None
		if self._rb_dl and not self._rb_dl.is_closed():
			self._rb_dl.render()
		self._rb_display.close()
		del self._rb_callback
		self._rb_dialog.close()
		self._rb_dialog = None
		del self._rb_dl
		del self._rb_display

	def _rb_cvbox(self):
		if self._rb_box is None:
			return ()
		x0, y0, x1, y1 = self._rb_box
		xscrolloff, yscrolloff = self._scrolloffset()
		x0, y0 = x0+xscrolloff, y0+yscrolloff
		x1, y1 = x1+xscrolloff, y1+yscrolloff
		return self._convert_qdcoords((x0, y0, x1, y1))

	def _rb_done(self):
		callback = self._rb_callback
		self._rb_finish()
		apply(callback, self._rb_cvbox())
		self._rb_finished = 1

	def _rb_cancel(self):
		callback = self._rb_callback
		self._rb_finish()
		apply(callback, ())
		self._rb_finished = 1


	def _rb_redraw(self):
		if not self._rb_box:
			return
		if not self._clip:
			self.mkclip()
		Qd.SetClip(self._clip)
		Qd.RGBForeColor((0xffff, 0, 0))
		if not self._rb_dragpoint is None:
			port = self._wid.GetWindowPort()
			oldmode = port.pnMode
			Qd.PenMode(QuickDraw.patXor)
		self._rb_doredraw()
		if not self._rb_dragpoint is None:
			Qd.PenMode(oldmode)
		
	def _rb_movebox(self, where, final=0):
		x, y = where
		xscrolloff, yscrolloff = self._scrolloffset()
		x, y = x-xscrolloff, y-yscrolloff
		x0, y0, x1, y1 = self._rb_box
		if self._rb_dragpoint == 0:	# top left
			x0, y0 = x, y
		elif self._rb_dragpoint == 1: # top right
			x0, y1 = x, y
		elif self._rb_dragpoint == 2: # bottom left
			x1, y0 = x, y
		elif self._rb_dragpoint == 3: # bottom right
			x1, y1 = x, y
		elif self._rb_dragpoint == 4: # center (move)
			oldx = (x0+x1)/2
			oldy = (y0+y1)/2
			diffx = x-oldx
			diffy = y-oldy
			x0 = x0 + diffx
			x1 = x1 + diffx
			y0 = y0 + diffy
			y1 = y1 + diffy
		else:
			raise 'funny dragpoint', self._rb_dragpoint
		x0, y0 = self._rb_constrain((x0, y0))
		x1, y1 = self._rb_constrain((x1, y1))
		#
		# New box computed. Return if same as old one.
		#
		if self._rb_box == (x0, y0, x1, y1):
			return
		#
		# Otherwise first erase old box, then draw the new one.
		#
		if not self._clip:
			self.mkclip()
		Qd.SetClip(self._clip)
		port = self._wid.GetWindowPort()
		oldmode = port.pnMode
		Qd.RGBForeColor((0xffff, 0, 0))
		Qd.PenMode(QuickDraw.patXor)

		self._rb_doredraw()
		if final:
			Qd.PenMode(oldmode)
			if x0 > x1:
				x0, x1 = x1, x0
			if y0 > y1:
				y0, y1 = y1, y0
		self._rb_box = x0, y0, x1, y1
		self._rb_doredraw()
		Qd.PenMode(oldmode)
		
	def _rb_doredraw(self):
		xscroll, yscroll = self._scrolloffset()
		x0, y0, x1, y1 = self._rb_box
		if x0 > x1: x0, x1 = x1, x0
		if y0 > y1: y0, y1 = y1, y0
		if x0 != x1 or y0 != y1:
			Qd.FrameRect((x0+xscroll, y0+yscroll, x1+xscroll, y1+yscroll))
		smallboxes = self._rb_smallboxes(scroll=1)
		for box in smallboxes:
			Qd.PaintRect(box)
			
	def _rb_smallboxes(self, scroll=0):
		x0, y0, x1, y1 = self._rb_box
		if scroll:
			xscroll, yscroll = self._scrolloffset()
			x0, y0 = x0+xscroll, y0+yscroll
			x1, y1 = x1+xscroll, y1+yscroll
		points = [
			(x0, y0),
			(x0, y1),
			(x1, y0),
			(x1, y1),
			((x0+x1)/2, (y0+y1)/2)]
		smallboxes = []
		for x, y in points:
			smallboxes.append(x-2, y-2, x+2, y+2)
		return smallboxes

	def _rb_constrain(self, where):
		x0, y0, x1, y1 = self.qdrect()
		xscrolloff, yscrolloff = self._scrolloffset()
		x0, y0 = x0 - xscrolloff, y0 - yscrolloff
		x1, y1 = x1 - xscrolloff, y1 - yscrolloff
		x, y = where
		if x < x0: x = x0
		if x > x1: x = x1
		if y < y0: y = y0
		if y > y1: y = y1
		return x, y

	def _rb_mousedown(self, where, shifted): # XXXXSCROLL
		# called on mouse press
		self._rb_display.render()
		x, y = where
		xscrolloff, yscrolloff = self._scrolloffset()
		x, y = x - xscrolloff, y - yscrolloff
		dragpoint = None
		if self._rb_box:
			smallboxes = self._rb_smallboxes()
			for i in range(len(smallboxes)):
				x0, y0, x1, y1 = smallboxes[i]
				if x0 <= x <= x1 and y0 <= y <= y1:
					dragpoint = i
					break
			else:
				#
				# Hmm. Should we start a new box?
				#
				MacOS.SysBeep()
				return 1
		if dragpoint is None:
			x, y = self._rb_constrain((x, y))
			self._rb_box = (x, y, x, y)
			dragpoint = 3
		self._rb_dragpoint = dragpoint
		Qd.SetPort(self._wid)
		Win.InvalRect(self.qdrect())
#### Not needed: the render() above has scheduled a redraw anyway
##		if not self._clip:
##			self.mkclip()
##		Qd.SetClip(self._clip)
##		port = self._wid.GetWindowPort()
##		oldmode = port.pnMode
##		Qd.RGBForeColor((0xffff, 0, 0))
##		Qd.PenMode(QuickDraw.patXor)
##		self._do_redraw()
##		Qd.PenMode(oldmode)
		mw_globals.toplevel.setmousetracker(self._rb_mousemove)

	def _rb_mousemove(self, event):
		"""Called on mouse moved with button down and final mouseup"""
		what, message, when, where, modifiers = event
		Qd.SetPort(self._wid)
		where = Qd.GlobalToLocal(where)
		if what == Events.mouseUp:
			self._rb_movebox(where, 1)
			self._rb_dragpoint = None
			mw_globals.toplevel.setmousetracker(None)
			Win.InvalRect(self.qdrect())
		else:
			self._rb_movebox(where, 0)

def calc_extra_size(adornments, canvassize):
	"""Return the number of pixels needed for toolbar and scrollbars"""
	extraw = 0
	extrah = 0
	minw = 0
	minh = 0
	if adornments and adornments.has_key('toolbar'):
		resid, width, height = MenuTemplate.TOOLBAR
		extrah = extrah + height
		minw = width
	# XXXX Add scrollbar size if applicable
	if canvassize:
		extraw = extraw + SCROLLBARSIZE - 1
		extrah = extrah + SCROLLBARSIZE - 1
	return extraw, extrah, minw, minh
		
class _ScrollMixin:
	"""Mixin class for scrollable/resizable toplevel windows"""
	
	def __init__(self, canvassize=None):
		self._canvassize = canvassize
		self._canvaspos = (0, 0)
		self._barx = None
		self._bary = None
		#
		if not canvassize:
			return
		#
		# Get measurements
		#
		horleft, verttop, vertright, horbot, vertleft, hortop = self._initscrollbarposition()
		#
		# Create vertical scrollbar
		#
		rect = vertleft, verttop, vertright, hortop+1
		self._bary = Ctl.NewControl(self._wid, rect, "", 1, 0, 0, 0, 16, 0)
		self._bary.HiliteControl(255)
		#
		# Create horizontal scrollbar
		#
		rect = horleft, hortop, vertleft+1, horbot
		self._barx = Ctl.NewControl(self._wid, rect, "", 1, 0, 0, 0, 16, 0)
		self._barx.HiliteControl(255)
		#
		# And install callbacks
		#
		self._add_control(self._barx, self._xscrollcallback, self._xscrollcallback)
		self._add_control(self._bary, self._yscrollcallback, self._yscrollcallback)
		
	def close(self):
		if self._barx:
			self._del_control(self._barx)
			self._del_control(self._bary)
			del self._barx
			del self._bary
		
	def _xscrollcallback(self, bar, part):
		ten_percent = (self._rect[_WIDTH]/10)
		page = self._rect[_WIDTH]-ten_percent
		self._anyscrollcallback(bar, part, ten_percent, page)
		
	def _anyscrollcallback(self, bar, part, line, page):
		if line < 1: line = 1
		if page < 1: page = 1
		old_x, old_y = self._canvaspos
		value = bar.GetControlValue()
		if part == Controls.inUpButton:
			value = value - line
		elif part == Controls.inPageUp:
			value = value - page
		elif part == Controls.inDownButton:
			value = value + line
		elif part == Controls.inPageDown:
			value = value + page
		bar.SetControlValue(value)
		new_x = self._barx.GetControlValue()
		new_y = self._bary.GetControlValue()
		Qd.SetPort(self._wid)
		# See whether we can use scrollrect. Only possible if no updates pending.
		updrgn = Qd.NewRgn()
		self._wid.GetWindowUpdateRgn(updrgn)
		if Qd.EmptyRgn(updrgn):
			# Scroll, and get the new vacated region back
			Qd.ScrollRect(self.qdrect(), old_x-new_x, old_y-new_y, updrgn)
		else:
			# ok, update the whole window
			Qd.RectRgn(updrgn, self.qdrect())
		Win.InvalRgn(updrgn)
		Qd.DisposeRgn(updrgn)
		self._canvaspos = new_x, new_y
		
	def _yscrollcallback(self, bar, part):
		ten_percent = (self._rect[_HEIGHT]/10)
		page = self._rect[_HEIGHT]-ten_percent
		self._anyscrollcallback(bar, part, ten_percent, page)
		
	def _canscroll(self):
		"""Return true if this window may be scrolled"""
		return not not self._canvassize
		
	def _scrolloffset(self):
		if not self._canvassize:
			return 0, 0
		xoff, yoff = self._canvaspos
		return -xoff, -yoff
		
	def _needs_grow_cursor(self):
		if self._barx:
			return 0
		return self._resizable
		
	def _redraw(self):
		if self._barx:
			self._wid.DrawGrowIcon()
		
	def _initscrollbarposition(self):
		l, t, w, h = self._rect
		r, b = l+w, t+h
		newr, newb = r - (SCROLLBARSIZE-1), b - (SCROLLBARSIZE-1)
		self._rect = l, t, newr-l, newb-t
		return l-1, t-1,  r+1, b+1, newr, newb
		
	def _resized(self):
		"""Move/resize scrollbars and update self._rect after a resize"""
		if not self._barx:
			return

		horleft, verttop, vertright, horbot, vertleft, hortop = self._initscrollbarposition()

		rect = vertleft, verttop, vertright, hortop+1
		self._movescrollbar(self._bary, rect)

		rect = horleft, hortop, vertleft+1, horbot
		self._movescrollbar(self._barx, rect)

	def _movescrollbar(self, bar, rect):
		l, t, r, b = rect
		bar.HideControl()
		bar.MoveControl(l, t)
		bar.SizeControl(r-l, (b-t))
		bar.ShowControl()
		
	def _clipvisible(self, clip):
		"""AND the visible region into the region clip"""
		pass
		
	def _activate(self, onoff):
		if not self._barx:
			return
		if onoff:
			hilite = 0
		else:
			hilite = 255
		self._barx.HiliteControl(hilite)
		self._bary.HiliteControl(hilite)
		self._wid.DrawGrowIcon()
		
	def _scrollsizefactors(self):
		if self._canvassize is None:
			return 1, 1
		return self._canvassize
		
	def setcanvassize(self, how):
		if self._canvassize is None:
			print 'setcanvassize call for non-resizable window!'
			return
		w, h = self._canvassize
		if how == DOUBLE_WIDTH:
			w = w * 2
		elif how == DOUBLE_HEIGHT:
			h = h * 2
		else:
			w, h = 1.0, 1.0
		self._canvassize = (w, h)
		self._adjust_scrollbar_max()
		self._do_resize0()
		
	def _adjust_scrollbar_max(self):
		"""Adjust scrollbar maximum for new window/canvassize. This may update
		the canvassize, because scrollbars cannot go beyond 32767"""
		# XXXX Keep x,y position
		# XXXX Check that canvassizes >= 1.0
		wwindow, hwindow = self._rect[2:]
		wfactor, hfactor = self._canvassize
		wcanvas, hcanvas = wfactor*wwindow, hfactor*hwindow
		if wcanvas > 32766:
			wcanvas = 32766
			wfactor = 32766.0/wwindow
		if hcanvas > 32766:
			hcanvas = 32766
			hfactor = 32766.0/hwindow
		self._canvassize = wfactor, hfactor
		self._adjustbar(self._barx, wwindow, wcanvas)
		self._adjustbar(self._bary, hwindow, hcanvas)
		self._canvaspos = self._barx.GetControlValue(), self._bary.GetControlValue()
		
	def _adjustbar(self, bar, windowsize, canvassize):
		"""Adjust a scrollbar for a new maximum"""
		if canvassize <= windowsize:
			bar.SetControlValue(0)
			bar.SetControlMaximum(0)
			bar.HiliteControl(255)
		else:
			newmax = canvassize - windowsize
			oldvalue = bar.GetControlValue()
			if oldvalue:
				# XXXX Should be done better
				oldmax = bar.GetControlMaximum()
				factor = float(newmax)/oldmax
				hw = windowsize/2
				newvalue = int(oldvalue*factor+hw*factor-hw)
			else:
				newvalue = 0
			bar.SetControlValue(newvalue)
			bar.SetControlMaximum(newmax)
			bar.HiliteControl(0)
			
		

class _AdornmentsMixin:
	"""Class to handle toolbars and other adornments on toplevel windows"""
	def __init__(self, adornments):
		self._cmd_to_cntl = {}
		self._cntl_to_cmd = {}
		self._cntl_handlers = {}
		self._keyboard_shortcuts = {}
		self._add_adornments(adornments)
		
	def _add_adornments(self, adornments):
		if not adornments:
			return
		if adornments.has_key('toolbar'):
			#
			# Create the buttons
			#
			for type, resid, cmd in adornments['toolbar']:
				try:
					cntl = Ctl.GetNewControl(resid, self._wid)
				except Ctl.Error, arg:
					print 'CNTL resource %d not found: %s'%(resid, arg)
				else:
					self._add_control(cntl, self._toolbar_callback)
					self._cmd_to_cntl[cmd] = cntl
					self._cntl_to_cmd[cntl] = cmd
			#
			# Create the toolbar
			#
			resid, width, height = MenuTemplate.TOOLBAR
			try:
				cntl = Ctl.GetNewControl(resid, self._wid)
			except Ctl.Error, arg:
				print 'CNTL resource %d not found: %s'%(resid, arg)
			cntl.HiliteControl(255)
			self._cmd_to_cntl[None] = cntl
			#
			# Adjust window bounds
			#
			x, y, w, h = self._rect
			self._rect = x, y+height, w, h-height
		if adornments.has_key('shortcuts'):
			self._keyboard_shortcuts = adornments['shortcuts']
			for k in self._keyboard_shortcuts.keys():
				mw_globals._all_commands[k] = 1
			
	def close(self):
		del self._cmd_to_cntl
		del self._cntl_to_cmd
		del self._cntl_handlers

	def _add_control(self, cntl, callback, trackhandler=None):
		self._cntl_handlers[cntl] = (callback, trackhandler)
			
	def _del_control(self, cntl):
		del self._cntl_handlers[cntl]
			
	def _resized(self):
		"""Adjust self._rect after a resize"""
		if not self._cmd_to_cntl:
			return
		x, y, w, h = self._rect
		resid, width, height = MenuTemplate.TOOLBAR
		self._rect = x, y+height, w, h-height
			
	def _iscontrolclick(self, down, local, event):
		if down:
			# Check for control
			ptype, ctl = Ctl.FindControl(local, self._wid)
			if ptype and ctl and self._cntl_handlers.has_key(ctl):
				control_callback, track_callback = self._cntl_handlers[ctl]
				if ptype in TRACKED_PARTS and track_callback:
					dummy = ctl.TrackControl(local, track_callback)
				else:
					part = ctl.TrackControl(local)
					if part:
						control_callback(ctl, part)
				return 1
		# Otherwise if the click is outside the real inner section we ignore it.
		if not Qd.PtInRect(local, self.qdrect()):
##			if down:
##				MacOS.SysBeep()
			return 1
		return 0
		
	def _toolbar_callback(self, ctl, part):
##		print 'DBG controlhit', ctl, part, self._cntl_to_cmd[ctl]
		cmd = self._cntl_to_cmd[ctl]
		self.call_command(cmd)
		
	def _check_for_shortcut(self, key):
		if self._keyboard_shortcuts.has_key(key):
			self.call_command(self._keyboard_shortcuts[key])
			return 1
		return 0
			
	def set_commandlist(self, cmdlist):
		enabled = {}
		# First pass: enable all commands featuring in cmdlist
		for item in cmdlist:
			cmd = item.__class__
			if self._cmd_to_cntl.has_key(cmd):
				cntl = self._cmd_to_cntl[cmd]
				cntl.HiliteControl(0)
				enabled[cmd] = 1
		# Second pass: disable the others
		for cmd in self._cmd_to_cntl.keys():
			if not enabled.has_key(cmd):
				cntl = self._cmd_to_cntl[cmd]
				cntl.HiliteControl(255)
	
	def set_toggle(self, cmd, onoff):
		if self._cmd_to_cntl.has_key(cmd):
			cntl = self._cmd_to_cntl[cmd]
			value = cntl.GetControlMinimum() + onoff
			cntl.SetControlValue(value)
		
class _Window(_ScrollMixin, _AdornmentsMixin, _WindowGroup, _CommonWindow):
	"""Toplevel window"""
	
	def __init__(self, parent, wid, x, y, w, h, defcmap = 0, pixmap = 0, 
			title="", adornments=None, canvassize = None, commandlist=None,
			resizable=1):
		
		self._istoplevel = 1
		self._resizable = resizable
		_CommonWindow.__init__(self, parent, wid)
		
		self._transparent = 0
		
		#
		# Note: the toplevel init routine is called with pixel coordinates,
		# not fractional coordinates
		#
		# Also, note the order here is important: the initializers modify
		# self._rect, and the toolbar has to span the window with the scroll
		# bars below it.
		#
		self._rect = 0, 0, w, h
		_AdornmentsMixin.__init__(self, adornments)
		#
		# Note: currently canvassize is always either None or (w, h). The (w,h)
		# is a bad choice (to be fixed), so we work around it.
		#
		if canvassize:
			_ScrollMixin.__init__(self, (1,1))
		else:
			_ScrollMixin.__init__(self, None)

		_x_pixel_per_mm, _y_pixel_per_mm = \
				 mw_globals.toplevel._getmmfactors()

		hf, vf = self._scrollsizefactors()
		self._hfactor = parent._hfactor / (hf*float(w) / _x_pixel_per_mm)
		self._vfactor = parent._vfactor / (vf*float(h) / _y_pixel_per_mm)
		_WindowGroup.__init__(self, title, commandlist)

		self.arrowcache = {}
		self._next_create_box = []
	
	def __repr__(self):
		return '<Window %s>'%self._title
	
	def close(self):
		_ScrollMixin.close(self)
		_AdornmentsMixin.close(self)
		_CommonWindow.close(self)
		self.arrowcache = {}
		# XXXX Not WindowGroup?
		
	def settitle(self, title):
		"""Set window title"""
		if not self._wid:
			return  # Or raise error?
		_WindowGroup.settitle(self, title)
		if title == None:
			title = ''
		self._wid.SetWTitle(title)
		
	def set_toggle(self, cmd, onoff):
		_AdornmentsMixin.set_toggle(self, cmd, onoff)
		_WindowGroup.set_toggle(self, cmd, onoff)
		
	def set_commandlist(self, cmdlist):
		_AdornmentsMixin.set_commandlist(self, cmdlist)
		_WindowGroup.set_commandlist(self, cmdlist)
		
	def getgeometry(self, units=UNIT_MM):
		rect = self._wid.GetWindowPort().portRect
		Qd.SetPort(self._wid)
		x, y = Qd.LocalToGlobal((0,0))
		w, h = rect[2]-rect[0], rect[3]-rect[1]
		_x_pixel_per_mm, _y_pixel_per_mm = \
				 mw_globals.toplevel._getmmfactors()
		_screen_top_offset = mw_globals.toplevel._getmbarheight()
		if units == UNIT_MM:
			rv = (float(x)/_x_pixel_per_mm,
			      float(y-_screen_top_offset)/_y_pixel_per_mm,
			      float(w)/_x_pixel_per_mm,
			      float(h)/_y_pixel_per_mm)
		elif units == UNIT_PXL:
			rv = x, y-_screen_top_offset, w, h
		elif units == UNIT_SCREEN:
			l, t, r, b = Qd.qd.screenBits.bounds
			scrw = r-l
			scrh = b-t-_screen_top_offset
			rv = (float(x)/scrw, float(y-_screen_top_offset)/scrh,
			      float(w)/scrw, float(h)/scrh)
		else:
			raise error, 'bad units specified'
		return rv

	def pop(self):
		"""Pop window to top of window stack"""
		if not self._wid or not self._parent:
			return
		self._wid.SelectWindow()
		mw_globals.toplevel._mouseregionschanged()

	def push(self):
		"""Push window to bottom of window stack"""
		if not self._wid or not self._parent:
			return
		self._wid.SendBehind(0)
		
	def _is_on_top(self):
		return 1
		
	def _goaway(self):
		"""User asked us to go away. Tell upper layers
		(but don't go yet)"""
		if not self.close_window_command():
			print 'No way to close this window!', self
		
	def _contentclick(self, down, where, event, shifted):
		"""A mouse click in our data-region"""
		if not self._wid or not self._parent:
			return
		Qd.SetPort(self._wid)
		where = Qd.GlobalToLocal(where)
		_CommonWindow._contentclick(self, down, where, event, shifted)

	def _keyboardinput(self, char, where, event):
		"""A character typed in our data-region"""
		if not self._wid or not self._parent:
			return
		if self._check_for_shortcut(char):
			return 1
		Qd.SetPort(self._wid)
		where = Qd.GlobalToLocal(where)
		return _CommonWindow._keyboardinput(self, char, where, event)

	def _mkclip(self):
		if not self._wid or not self._parent:
			return
		if self._clip:
			raise 'Clip already valid!'
		# create region for whole window

		self._clip = Qd.NewRgn()
		Qd.RectRgn(self._clip, self.qdrect())
		self._clipvisible(self._clip)
		#
		# subtract all subwindows, insofar they aren't transparent
		# at the moment
		#
		for w in self._subwindows:
			if w._transparent == 0 or \
			   (w._transparent == -1 and w._active_displist):
				r = Qd.NewRgn()
				Qd.RectRgn(r, w.qdrect())
				Qd.DiffRgn(self._clip, r, self._clip)
				Qd.DisposeRgn(r)
				
	def _redraw(self, rgn=None):
		_CommonWindow._redraw(self, rgn)
		if rgn is None:
			rgn = self._wid.GetWindowPort().visRgn
		Ctl.UpdateControls(self._wid, rgn)
		_ScrollMixin._redraw(self)
		
	def _activate(self, onoff):
		_CommonWindow._activate(self, onoff)
##		_WindowGroup._activate(self, onoff)
		_ScrollMixin._activate(self, onoff)

	def _resize_callback(self, width, height):
		self.arrowcache = {}
		mycreatebox = _in_create_box
		if mycreatebox:
			next_create_box = mycreatebox._next_create_box
			mycreatebox._next_create_box = []
			try:
				mycreatebox._rb_cancel()
			except _rb_done:
				pass
			mycreatebox._next_create_box[0:0] = next_create_box
			
		for d in self._displists[:]:
			d.close()
		self._wid.SizeWindow(width, height, 1)
		Qd.SetPort(self._wid)
		Win.InvalRect(self.qdrect())
		self._clipchanged()

		x, y = self._rect[:2]
		self._rect = x, y, width, height
		_AdornmentsMixin._resized(self)
		_ScrollMixin._resized(self)
		self._do_resize0()
		if mycreatebox:
			mycreatebox._rb_end()
			raise _rb_done
		
	def _do_resize0(self):
		"""Common code for resize and double width/height"""
		x, y, width, height = self._rect

		# convert pixels to mm
		parent = self._parent
		_x_pixel_per_mm, _y_pixel_per_mm = \
				 mw_globals.toplevel._getmmfactors()
		hf, vf = self._scrollsizefactors()
		self._hfactor = parent._hfactor / (hf*float(width)
						   / _x_pixel_per_mm)
		self._vfactor = parent._vfactor / (vf*float(height) /
						   _y_pixel_per_mm)

		for w in self._subwindows:
			w._do_resize1()
		# call resize callbacks
		self._do_resize2()

	def hitarrow(self, point, src, dst):
		# return 1 iff (x,y) is within the arrow head
		sx, sy = self._convert_coordinates(src)
		dx, dy = self._convert_coordinates(dst)
		x, y = self._convert_coordinates(point)
		lx = dx - sx
		ly = dy - sy
		if lx == ly == 0:
			angle = 0.0
		else:
			angle = math.atan2(lx, ly)
		cos = math.cos(angle)
		sin = math.sin(angle)
		# translate
		x, y = x - dx, y - dy
		# rotate
		nx = x * cos - y * sin
		ny = x * sin + y * cos
		# test
		if ny > 0 or ny < -ARR_LENGTH:
			return FALSE
		if nx > -ARR_SLANT * ny or nx < ARR_SLANT * ny:
			return FALSE
		return TRUE

class _SubWindow(_CommonWindow):
	"""Window "living in" with a toplevel window"""

	def __init__(self, parent, wid, coordinates, defcmap = 0, pixmap = 0, 
			transparent = 0, z = 0):
		
		self._istoplevel = 0
		_CommonWindow.__init__(self, parent, wid, z)
		
		x, y, w, h = parent._convert_coordinates(coordinates)
		xscrolloff, yscrolloff = parent._scrolloffset()
		x, y = x+xscrolloff, y+yscrolloff
		if parent._canscroll():
			raise 'Subwindow in scrollable parent not implemented'
		self._rect = x, y, w, h
		if w <= 0 or h <= 0:
			raise 'Empty subwindow', coordinates
		self._sizes = coordinates
		
		hf, vf = self._scrollsizefactors()
		self._hfactor = parent._hfactor / (hf*self._sizes[_WIDTH])
		self._vfactor = parent._vfactor / (vf*self._sizes[_HEIGHT])
		
		if parent._transparent:
			self._transparent = parent._transparent
		else:
			self._transparent = transparent
		
		self.arrowcache = {}
		self._next_create_box = []

		# XXXX pixmap to-be-done
		
		# XXXX Should we do redraw of parent or something??

	def settitle(self, title):
		"""Set window title"""
		raise error, 'can only settitle at top-level'
		
	def getgeometry(self, units=UNIT_MM):
		return self._sizes

	def pop(self):
		"""Pop to top of subwindow stack"""
		if not self._parent:
			return
		parent = self._parent
		if parent._subwindows[0] is self:
			return
		parent._subwindows.remove(self)
		
		for i in range(len(parent._subwindows)):
			if self._z >= parent._subwindows[i]._z:
				parent._subwindows.insert(i, self)
				break
		else:
			parent._subwindows.append(self)
		parent._clipchanged()
		Qd.SetPort(self._wid)
		if self._transparent <= 0:
			Win.InvalRect(self.qdrect())
		parent.pop()

	def push(self):
		"""Push to bottom of subwindow stack"""
		if not self._parent:
			return
		parent = self._parent
		if parent._subwindows[-1] is self:
			return
		parent._subwindows.remove(self)
		for i in range(len(parent._subwindows)-1,-1,-1):
			if self._z <= parent._subwindows[i]._z:
				parent._subwindows.insert(i+1, self)
				break
		else:
			parent._subwindows.insert(0, self)
		parent._clipchanged()
		Qd.SetPort(self._wid)
		Win.InvalRect(self.qdrect())
		parent.push()
		
	def _is_on_top(self):
		"""Return true if no other subwindow overlaps us"""
		if not self._parent:
			return 0
		# XXXX This is not good enough, really...
		return (self._parent._subwindows[0] is self)

	def _mkclip(self):
		if not self._parent:
			return
		if self._clip:
			raise 'Clipregion already valid!'
			
		# create region for our subwindow
		self._clip = Qd.NewRgn()
		Qd.RectRgn(self._clip, self.qdrect())
		# subtract all our subsubwindows
		for w in self._subwindows:
			if w._transparent == 0 or \
			   (w._transparent == -1 and w._active_displist):
				r = Qd.NewRgn()
				Qd.RectRgn(r, w.qdrect())
				Qd.DiffRgn(self._clip, r, self._clip)
				Qd.DisposeRgn(r)
		# subtract our higher-stacked siblings
		for w in self._parent._subwindows:
			if w == self:
				# Stop when we meet ourselves
				break
			if w._transparent == 0 or \
			   (w._transparent == -1 and w._active_displist):
				r = Qd.NewRgn()
				Qd.RectRgn(r, w.qdrect())
				Qd.DiffRgn(self._clip, r, self._clip)
				Qd.DisposeRgn(r)

	def _do_resize1(self):
		# calculate new size of subwindow after resize
		# close all display lists
		parent = self._parent
		## XXXX Should have crop=1?
		x, y, w, h = parent._convert_coordinates(self._sizes)
		xscrolloff, yscrolloff = parent._scrolloffset()
		x, y = x+xscrolloff, y+yscrolloff
		self._rect = x, y, w, h
		w, h = self._sizes[2:]
		if w == 0:
			w = float(self._rect[_WIDTH]) / parent._rect[_WIDTH]
		if h == 0:
			h = float(self._rect[_HEIGHT]) / parent._rect[_HEIGHT]
		hf, vf = self._scrollsizefactors()
		self._hfactor = parent._hfactor / (hf*w)
		self._vfactor = parent._vfactor / (vf*h)
		# We don't have to clear _clip, our parent did that.
		self._active_displist = None
		for d in self._displists[:]:
			d.close()
		for w in self._subwindows:
			w._do_resize1()
			
	def _add_control(self, ctl, callback, tracker=None):
		"""Add a control. Propagate up to the toplevel window"""
		self._parent._add_control(ctl, callback, tracker)
		
	def _del_control(self, ctl):
		"""Delete a control. Propagate up to the toplevel window"""
		self._parent._del_control(ctl)
		
	def _canscroll(self):
		"""Return true if this window or any of its ancestors is scrollable"""
		return self._parent._canscroll()

class DialogWindow(_Window):
	def __init__(self, resid, title='Dialog', default=None, cancel=None,
				cmdbuttons=None):
		wid = Dlg.GetNewDialog(resid, -1)
		if cmdbuttons:
			self._item_to_cmd = cmdbuttons
		else:
			self._item_to_cmd = {}
		self._itemhandler = None
		x0, y0, x1, y1 = wid.GetWindowPort().portRect
		w, h = x1-x0, y1-y0
		cmdlist = [
			usercmd.COPY(callback=(wid.DialogCopy, ())),
			usercmd.PASTE(callback=(wid.DialogPaste, ())),
			usercmd.CUT(callback=(wid.DialogCut, ())),
			usercmd.DELETE(callback=(wid.DialogDelete, ())),
		]
		if not default is None:
			self._do_defaulthit = self._optional_defaulthit
			self.__default = default
			wid.SetDialogDefaultItem(default)
		if not cancel is None:
			self._do_cancelhit = self._optional_cancelhit
			self.__cancel = cancel
			cmdlist.append(
				usercmd.CLOSE_WINDOW(callback=(self._do_cancelhit, ())))
			wid.SetDialogCancelItem(cancel)
		_Window.__init__(self, mw_globals.toplevel, wid, 0, 0, w, h, 
				commandlist=cmdlist, resizable=0)
		mw_globals.toplevel._register_wid(wid, self)
		Qd.SetPort(wid)
		self._widgetdict = {}
		self._is_shown = 0 # XXXX Is this always true??!?
		self.title = title
		
	def __repr__(self):
		return '<DialogWindow %s>'%self.title
	
	def show(self):
		self.settitle(self.title)
		self._wid.ShowWindow()
		self._is_shown = 1
		
	def hide(self):
		self._wid.HideWindow()
		self.grabdone()
		self.settitle(None)
		self._is_shown = 0
		
	def is_showing(self):
		return self._is_shown
		
	def close(self):
		if not self._parent:
			return
		self.hide()
		del self._widgetdict
		del self._item_to_cmd
		del self._itemhandler
		_Window.close(self)

	def grabdone(self):
		self.__grab_done = 1

	def rungrabbed(self):
		self.__grab_done = 0
		mw_globals.toplevel.grab(self)
		while not self.__grab_done:
			mw_globals.toplevel._eventloop(100)
		mw_globals.toplevel.grab(None)
		
	def addwidget(self, num, widget):
		self._widgetdict[num] = widget
		
	def set_itemhandler(self, handler):
		self._itemhandler = handler
		
	def do_itemhit(self, item, event):
		if self._item_to_cmd.has_key(item):
			self.call_command(self._item_to_cmd[item])
			return 1
		if self._itemhandler:
			if self._itemhandler(item, event):
				return 1
		print 'Dialog %s item %d event %s'%(self, item, event)
		return 0

	#
	# If the dialog has a default item the next method is copied to _do_defaulthit.
	# The event handling will then call this when return is pressed.
	#
	def _optional_defaulthit(self):
		tp, h, rect = self._wid.GetDialogItem(self.__default)
		h.as_Control().HiliteControl(Controls.inButton)
		self.do_itemhit(self.__default, None)
	#
	# Similarly for cancel, which is bound to close window (not to cmd-dot yet)
	#
	def _optional_cancelhit(self):
		tp, h, rect = self._wid.GetDialogItem(self.__cancel)
		h.as_Control().HiliteControl(Controls.inButton)
		self.do_itemhit(self.__cancel, None)
		
	def do_itemdraw(self, item):
		try:
			w = self._widgetdict[item]
		except KeyError:
			print 'Unknown user item', item
		else:
			w._redraw()
		
	def _redraw(self, rgn):
		pass
			
	def _activate(self, onoff):
		for w in self._widgetdict.values():
			w._activate(onoff)
			
	def ListWidget(self, item, content=[]):
		widget = mw_widgets._ListWidget(self._wid, item, content)
		self.addwidget(item, widget)
		return widget

	def set_commandlist(self, cmdlist):
		# First build the cmd->item mapping from the item->cmd mapping
		cmd_to_item = {}
		for item, cmd in self._item_to_cmd.items():
			cmd_to_item[cmd] = item
		# First pass: enable all commands featuring in cmdlist
		for item in cmdlist:
			cmd = item.__class__
			if cmd_to_item.has_key(cmd):
				item = cmd_to_item[cmd]
				tp, h, rect = self._wid.GetDialogItem(item)
				cntl = h.as_Control()
				cntl.HiliteControl(0)
				del cmd_to_item[cmd]
		# Second pass: disable the others
		for item in cmd_to_item.values():
			tp, h, rect = self._wid.GetDialogItem(item)
			cntl = h.as_Control()
			cntl.HiliteControl(255)
		# And pass the command list on to the Window/Menu stuff
		_Window.set_commandlist(self, cmdlist)
