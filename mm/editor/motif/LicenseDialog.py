__version__ = "$Id$"

# License dialog
import windowinterface
import Xm, Xmd, X

class LicenseDialog:
	def __init__(self):
		import splash, splashimg, imgconvert
		w = windowinterface.toplevel._main.CreateTemplateDialog('license', {'autoUnmanage': 0})
		tryb = w.CreatePushButton('try', {'labelString': 'Try'})
		tryb.ManageChild()
		tryb.AddCallback('activateCallback', self.__callback, (self.cb_try, ()))
		self.__try = tryb
		buy = w.CreatePushButton('buy', {'labelString': 'Buy now...'})
		buy.ManageChild()
		buy.AddCallback('activateCallback', self.__callback, (self.cb_buy, ()))
		eval = w.CreatePushButton('eval', {'labelString': 'Get evaluation license...'})
		eval.ManageChild()
		eval.AddCallback('activateCallback', self.__callback, (self.cb_eval, ()))
		self.__eval = eval
		key = w.CreatePushButton('key', {'labelString': 'Enter key...'})
		key.ManageChild()
		key.AddCallback('activateCallback', self.__callback, (self.cb_enterkey, ()))
		quit = w.CreatePushButton('quit', {'labelString': 'Quit'})
		quit.ManageChild()
		quit.AddCallback('activateCallback', self.__callback, (self.cb_quit, ()))
		visual = windowinterface.toplevel._main.visual
		fmt, rs, rm, gs, gm, bs, bm = splash.findformat(visual)
		rdr = imgconvert.stackreader(fmt, splashimg.reader())
		self.__imgsize = rdr.width, rdr.height
		data = rdr.read()
		depth = fmt.descr['align'] / 8
		xim = visual.CreateImage(visual.depth, X.ZPixmap, 0, data,
					 rdr.width, rdr.height, depth * 8,
					 rdr.width * depth)
		img = w.CreateDrawingArea('splash', {'width': rdr.width,
						     'height': rdr.height})
		img.AddCallback('exposeCallback', self.__expose,
				(xim, rdr.width, rdr.height))
		img.ManageChild()
		self.__img = img
		self.__msg = None
		self.__window = w

	def __expose(self, widget, (xim, width, height), call_data):
		widget.CreateGC({}).PutImage(xim, 0, 0, 0, 0, width, height)

	def show(self):
		self.__window.ManageChild()
		
	def close(self):
		self.__window.DestroyWidget()
		self.__window = None
		del self.__window
		del self.__try
		del self.__eval
		del self.__img
		del self.__msg
			
	def setdialoginfo(self):
		self.__try.SetSensitive(self.can_try)
		self.__eval.SetSensitive(self.can_eval)
		width, height = self.__imgsize
		if self.__msg is not None:
			self.__msg.DestroyWidget
		attrs = {'labelString': self.msg,
			 'alignment': Xmd.ALIGNMENT_CENTER,
			 'x': 10,
			 'y': height - 26,
			 'width': width - 20,
			 'background': 0xffffff,
			 'foreground': 0x061440}
		try:
			import splash
			self.__img.LoadQueryFont(splash.splashfont)
		except:
			pass
		else:
			attrs['fontList'] = splash.splashfont
		self.__msg = self.__img.CreateManagedWidget('message',
							    Xm.Label, attrs)

	def __callback(self, w, callback, call_data):
		apply(apply, callback)
