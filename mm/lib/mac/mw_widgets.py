import Win
import Qd
import QuickDraw
import List
import Lists
import Controls
import ControlAccessor

import img
import imgformat
import mac_image

#
# Stuff needed from other mw_ modules
#
import mw_globals
import mw_menucmd

class _Widget:
	def __init__(self, wid, item):
		tp, h, rect = wid.GetDialogItem(item) # XXXX To be fixed
		wid.SetDialogItem(item, tp,
		      mw_globals.toplevel._dialog_user_item_handler, rect)
		
class _ListWidget:
	def __init__(self, wid, item, content=[], multi=0):
		self.control = wid.GetDialogItemAsControl(item)
		h = self.control.GetControlDataHandle(Controls.kControlListBoxPart, 
			Controls.kControlListBoxListHandleTag)
		self.list = List.as_List(h)
		self.list.LAddRow(len(content), 0)
##?		self.list.LSetDrawingMode(0)
##		# wid is the window (dialog) where our list is going to be in
##		# rect is it's item rectangle (as in dialog item)
##		self.rect = rect
##		rect2 = rect[0]+1, rect[1]+1, rect[2]-16, rect[3]-1
##		self.list = List.LNew(rect2, (0, 0, 1, len(content)),
##					 (0,0), 0, wid,	0, 0, 0, 1)
		if not multi:
			self.list.selFlags = Lists.lOnlyOne
		self._data = []
		self._setcontent(0, len(content), content)
		self.wid = wid
##?		self.list.LSetDrawingMode(1)
##		Win.InvalRect(self.rect)
##		self._redraw() # DBG
	
	def _setcontent(self, fr, to, content):
		for y in range(fr, to):
			item = content[y-fr]
			self.list.LSetCell(item, (0, y))
		self._data[fr:to] = content
		
	def _delete(self, fr=None, count=1):
		if fr is None:
			self.list.LDelRow(0,0)
			self._data = []
		else:
			self.list.LDelRow(count, fr)
			del self._data[fr:fr+count]
			
	def _insert(self, where=-1, count=1):
		if where == -1:
			where = 32766
			self._data = self._data + [None]*count
		else:
			self._data[where:where] = [None]*count
		return self.list.LAddRow(count, where)
		
	def delete(self, fr=None, count=1):
##?		Qd.SetPort(self.wid)
##?		self.list.LSetDrawingMode(0)
		self._delete(fr, count)
##?		self.list.LSetDrawingMode(1)
##?		Win.InvalRect(self.rect)
##		self._redraw() # DBG
		
	def set(self, content):
##?		Qd.SetPort(self.wid)
##?		self.list.LSetDrawingMode(0)
		self._delete()
		self._insert(count=len(content))
		self._setcontent(0, len(content), content)
##?		self.list.LSetDrawingMode(1)
##?		Win.InvalRect(self.rect)
##		self._redraw() # DBG
		
	def get(self):
		return self._data
		
	def getitem(self, item):
		return self._data[item]
		
	def insert(self, where=-1, content=[]):
##?		Qd.SetPort(self.wid)
##?		self.list.LSetDrawingMode(0)
		where = self._insert(where, len(content))
		self._setcontent(where, where+len(content), content)
##?		self.list.LSetDrawingMode(1)
##?		Win.InvalRect(self.rect)
##		self._redraw() # DBG
		
	def replace(self, where, what):
##?		Qd.SetPort(self.wid)
##?		self.list.LSetDrawingMode(0)
		self._setcontent(where, where+1, [what])
##?		self.list.LSetDrawingMode(1)
##?		Win.InvalRect(self.rect)
##		self._redraw() # DBG
		
	def deselectall(self):
		while 1:
			ok, pt = self.list.LGetSelect(1, (0,0))
			if not ok: return
			self.list.LSetSelect(0, pt)
			
	def select(self, num):
		self.deselectall()
		if num is None or num < 0:
			return
		self.list.LSetSelect(1, (0, num))
		
	def getselect(self):
		ok, (x, y) = self.list.LGetSelect(1, (0,0))
		if not ok:
			return None
		return y
		
##	def getselectvalue(self):
##		num = self.getselect()
##		if num is None:
##			return None
##		return self._data[num]
			
## 	def click(self, where, modifiers):
## 		is_double = self.list.LClick(where, modifiers)
## 		ok, (x, y) = self.list.LGetSelect(1, (0, 0))
## 		if ok:
## 			return y, is_double
## 		else:
## 			return None, is_double
## 			
## 	# draw a frame around the list, List Manager doesn't do that
## 	def drawframe(self):
## 		Qd.SetPort(self.wid)
## 		Qd.EraseRect(self.rect)
## 		Qd.FrameRect(self.rect)
## 		
## 	def _redraw(self, rgn=None):
## 		if rgn == None:
## 			rgn = self.wid.GetWindowPort().visRgn
## 		self.drawframe()
## 		self.list.LUpdate(rgn)
## 		
## 	def _activate(self, onoff):
## ##		print 'ACTIVATE', self, onoff
## 		self.list.LActivate(onoff)
		
class _ImageWidget(_Widget):
	def __init__(self, wid, item, image=None):
		_Widget.__init__(self, wid, item)
		tp, h, rect = wid.GetDialogItem(item)
		# wid is the window (dialog) where our image is going to be in
		# rect is it's item rectangle (as in dialog item)
		self.rect = rect
		self.image = image
		self.wid = wid
		Win.InvalRect(self.rect)
			
	def setfromfile(self, image):
		Win.InvalRect(self.rect)
		self.image_data = None

		if not image:
			return
		format = imgformat.macrgb16
		try:
			rdr = img.reader(format, image)
			bits = rdr.read()
		except (img.error, IOError):
			return
		
		pixmap = mac_image.mkpixmap(rdr.width, rdr.height, format, bits)
		self.image_data = (rdr.width, rdr.height, (pixmap, bits))
				
	def _redraw(self, rgn=None):
		if rgn == None:
			rgn = self.wid.GetWindowPort().visRgn
		Qd.SetPort(self.wid)
		if not self.image_data:
			Qd.EraseRect(self.rect)
		else:
			w, h, (pixmap, dataref) = self.image_data
			dl, dt, dr, db = self.rect
			#
			# If there is enough room center the image
			#
			if dr-dl > w:
				dl = dl + ((dr-dl)-w)/2
				dr = dl + w
			if db-dt > h:
				dt = dt + ((db-dt)-h)/2
				db = dt + h
				
			srcrect = 0, 0, w, h
			dstrect = dl, dt, dr, db
			fgcolor = self.wid.GetWindowPort().rgbFgColor
			bgcolor = self.wid.GetWindowPort().rgbBkColor
			Qd.RGBBackColor((0xffff, 0xffff, 0xffff))
			Qd.RGBForeColor((0, 0, 0))
			Qd.CopyBits(pixmap,
			      self.wid.GetWindowPort().portBits,
			      srcrect, dstrect,
			      QuickDraw.srcCopy+QuickDraw.ditherCopy,
			      None)
			Qd.RGBBackColor(bgcolor)
			Qd.RGBForeColor(fgcolor)
		Qd.FrameRect(self.rect)

	def _activate(self, onoff):
		pass
				
class SelectWidget:
	def __init__(self, wid, ctlid, items=[], default=None, callback=None):
		self.wid = wid
		self.itemnum = ctlid
		self.menu = None
		self.choice = None
		self.control = self.wid.GetDialogItemAsControl(self.itemnum)
		self.setitems(items, default)
		if callback:
			raise 'Menu-callbacks not supported anymore'
		
	def delete(self):
		self.menu.delete()
		del self.menu
		del self.wid
		del self.control
		
	def setitems(self, items=[], default=None):
		items = items[:]
		if not items:
			items.append('')
		self.choice = None
		self.data = items
		if self.menu:
			self.menu.delete()
			del self.menu
		self.menu = mw_menucmd.SelectPopupMenu(items)
		mhandle, mid = self.menu.getpopupinfo()
		self.control.SetControlDataHandle(Controls.kControlMenuPart,
				Controls.kControlPopupButtonMenuHandleTag, mhandle)
##		ControlAccessor.SetControlData(self.control, Controls.kControlMenuPart,
##				Controls.kControlPopupButtonMenuIDTag, mid)
		self.control.SetControlMinimum(1)
		self.control.SetControlMaximum(len(items)+1)
		if default != None:
			self.select(default)
		
	def select(self, item):
		if item in self.data:
			item = self.data.index(item)
		self.control.SetControlValue(item+1)
		
##	def click(self, event=None):
##		self.usercallback()
		
	def getselect(self):
		item = self.control.GetControlValue()-1
		if 0 <= item < len(self.data):
			return self.data[item]
		return None
		
	def getselectindex(self):
		return self.control.GetControlValue()-1
