from Channel import *
from MMExc import *			# exceptions
from AnchorDefs import *
import windowinterface			# for windowinterface.error
from urllib import urlretrieve


class ImageChannel(ChannelWindow):
	node_attrs = ChannelWindow.node_attrs + ['scale', 'scalefilter', 'crop']

	def __init__(self, name, attrdict, scheduler, ui):
		ChannelWindow.__init__(self, name, attrdict, scheduler, ui)
		self._visible = 1

	def __repr__(self):
		return '<ImageChannel instance, name=' + `self._name` + '>'

	def do_arm(self, node, same=0):
		#print "----------------ImageChannel-----------------------"
		if same and self.armed_display:
		        return 1
		#print "----------------ImageChannel2-----------------------"
		if node.type != 'ext':
			self.errormsg(node, 'Node must be external')
			return 1
		f = self.getfileurl(node)
		try:
			f = urlretrieve(f)[0]
		except IOError:
			pass
		# remember coordinates for anchor editing (and only for that!)
		try:
			self._arm_imbox = self.armed_display.display_image_from_file(f, scale = MMAttrdefs.getattr(node, 'scale'), crop = MMAttrdefs.getattr(node, 'crop'))
		except (windowinterface.error, IOError), msg:
			if type(msg) == type(()):
				msg = msg[1]
			self.errormsg(node, f + ':\n' + msg)
			return 1
		try:
			alist = node.GetRawAttr('anchorlist')
			modanchorlist(alist)
		except NoSuchAttrError:
			alist = []
		self.armed_display.fgcolor(self.getbucolor(node))
		hicolor = self.gethicolor(node)
		imagex = int(self._arm_imbox[0] * self.window._rect[2] ) #+ self.window._rect[0]
		imagey = int(self._arm_imbox[1] * self.window._rect[3] ) #+ self.window._rect[1]
		imagew = int(self._arm_imbox[2] * self.window._rect[2] )
		imageh = int(self._arm_imbox[3] * self.window._rect[3] )
		#print "IMAGE DIMENSIONS-->", imagex, imagey, imagew, imageh
		for a in alist:
			args = a[A_ARGS]
			if len(args) == 0:
				args = [0,0,1,1]
			elif len(args) == 4:
				args = self.convert_args(f, args)
			if len(args) != 4:
				print 'ImageChannel: funny-sized anchor'
				continue
			if args == [0, 0, 1, 1]:
			    continue
			x, y, w, h = args[0], args[1], args[2], args[3]
			butx = int(x * imagew )
			buty = int(y * imageh )
			if butx == 0:
				butw = int(w * imagew)
			else:
				butw = int(w * imagew + 0.5)+2
			if butx == 0:
				buth = int(h * imageh)
			else:
				buth = int(h * imageh + 0.5)+2
			#print "BUTTON DIMENSIONS-->", butx, buty, butw, buth
			x = (float(butx) + float(imagex)) / (float(self.window._rect[2]) - 1.0)
			y = (float(buty) + float(imagey)) / (float(self.window._rect[3]) - 1.0)
			w = float(butw) / (float(self.window._rect[2]) - 1.0)
			h = float(buth) / (float(self.window._rect[3]) - 1.0)
			
			#print "x, y, w, h", x, y, w, h
			#b = self.armed_display.newbutton((x, y, w, h))
			#b = self.armed_display.newbutton((x+0.000000000005, y+0.000000000005, w+x+0.000000000005, h+y+0.000000000005))
			b = self.armed_display.newbutton((x, y, w+x, h+y))
			b.hiwidth(3)
			b.hicolor(hicolor)
			self.setanchor(a[A_ID], a[A_TYPE], b)
		return 1

	def defanchor(self, node, anchor, cb):
		if not self.window:
			windowinterface.showmessage('The window is not visible.\nPlease make it visible and try again.')
			return
		if self._armstate != AIDLE:
			raise error, 'Arm state must be idle when defining an anchor'
		if self._playstate != PIDLE:
			raise error, 'Play state must be idle when defining an anchor'
		windowinterface.setcursor('watch')
		self._anchor_context = AnchorContext()
		self.startcontext(self._anchor_context)
		self.syncarm = 1
		self.arm(node)
		self.syncplay = 1
		self.play(node)
		self._playstate = PLAYED
		self.syncarm = 0
		self.syncplay = 0
		self._anchor = anchor
		box = anchor[2]
		windowinterface.setcursor('')
		self._anchor_cb = cb
		msg = 'Draw anchor in ' + self._name + '.'
		if box == []:
			self.window.create_box(msg, self._box_cb)
		else:
			f = self.getfileurl(node)
			try:
				f = urlretrieve(f)[0]
			except IOError:
				pass
			box = self.convert_args(f, box)
			# convert coordinates from image size to window size.
			#print "defanchor.ArmIMBOX: ", self._arm_imbox
			#print "Box: ", box
			x = box[0] * self._arm_imbox[2] + self._arm_imbox[0]
			y = box[1] * self._arm_imbox[3] + self._arm_imbox[1]
			w = box[2] * self._arm_imbox[2]
			h = box[3] * self._arm_imbox[3]
			self.window.create_box(msg, self._box_cb, (x, y, w, h))

	def _box_cb(self, *box):
		self.stopcontext(self._anchor_context)
		if len(box) == 4:
			# convert coordinates from window size to image size.
			#print "BoxCB.ArmIMBOX: ", self._arm_imbox
			#print "Box: ", box
			x = (box[0] - self._arm_imbox[0]) / self._arm_imbox[2]
			y = (box[1] - self._arm_imbox[1]) / self._arm_imbox[3]
			w = box[2] / self._arm_imbox[2]
			h = box[3] / self._arm_imbox[3]
			arg = (self._anchor[0], self._anchor[1], [x, y, w, h])
		else:
			arg = self._anchor
		apply(self._anchor_cb, (arg,))
		del self._anchor_cb
		del self._anchor_context
		del self._anchor

	# Hack to convert pixel offsets into relative offsets and to make
	# the coordinates relative to the upper-left corner instead of
	# lower-left.  This only works for RGB images.
	# If the offsets are in the range [0..1], we don't need to do
	# the conversion since the offsets are already fractions of
	# the image.
	def convert_args(self, file, args):
		#print "-------convert_args---------"
		need_conversion = 1
		for a in args:
			if a != int(a):	# any floating point number
				need_conversion = 0
				break
		if not need_conversion:
			return args
		if args == (0, 0, 1, 1) or args == [0, 0, 1, 1]:
			# special case: full image
			return args
		xsize, ysize = self.window._image_size(file)
		x0, y0, x1, y1 = args[0], args[1], args[2], args[3]
		y0 = ysize - y0
		y1 = ysize - y1
		if x0 > x1:
			x0, x1 = x1, x0
		if y0 > y1:
			y0, y1 = y1, y0
		#print "-------out of convert_args---------"
		return float(x0)/float(xsize), float(y0)/float(ysize), \
			  float(x1-x0)/float(xsize), float(y1-y0)/float(ysize)
