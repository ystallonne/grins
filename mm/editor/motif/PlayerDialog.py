"""Dialog for the Player control panel.

The PlayerDialog is a window that displays VCR-like controls to
control the player plus an interface to turn channels on and off and
an interface to turn options on and off.

"""

__version__ = "$Id$"

import windowinterface, WMEVENTS
from usercmd import *
import imgformat, imgconvert
import playbutton, playbuttonunselect
import pausebutton, pausebuttonunselect
import stopbutton, stopbuttonunselect

_BLACK = 0, 0, 0
_GREY = 100, 100, 100
_GREEN = 0, 255, 0
_YELLOW = 255, 255, 0
_BGCOLOR = 200, 200, 200
_FOCUSLEFT = 244, 244, 244
_FOCUSTOP = 204, 204, 204
_FOCUSRIGHT = 40, 40, 40
_FOCUSBOTTOM = 91, 91, 91

STOPPED, PAUSING, PLAYING = range(3)

class PlayerDialog:
	adornments = {
		'shortcuts': {
			'p': PLAY,
			'P': PAUSE,
			's': STOP,
			},
		'menubar': [
			('Close', [
				('Close', CLOSE_WINDOW),
				]),
			('Play', [
				('Play', PLAY, 't'),
				('Pause', PAUSE, 't'),
				('Stop', STOP, 't'),
				]),
			('Channels', CHANNELS),
			('Options', [
				('Calculate timing', CALCTIMING),
				('Keep Channel View in sync', SYNCCV),
				('Dump scheduler data', SCHEDDUMP),
				]),
			],
		'toolbar': [
			({'label': playbuttonunselect.reader(),
			  'labelInsensitive': imgconvert.stackreader(
				  imgformat.grey, playbuttonunselect.reader()),
			  'select': playbutton.reader(),
			  'selectInsensitive': playbutton.reader(),
			  }, PLAY, 't'),
			({'label': pausebuttonunselect.reader(),
			  'labelInsensitive': imgconvert.stackreader(
				  imgformat.grey, pausebuttonunselect.reader()),
			  'select': pausebutton.reader(),
			  'selectInsensitive': imgconvert.stackreader(
				  imgformat.grey, pausebutton.reader()),
			  }, PAUSE, 't'),
			({'label': stopbuttonunselect.reader(),
			  'labelInsensitive': imgconvert.stackreader(
				  imgformat.grey, stopbuttonunselect.reader()),
			  'select': stopbutton.reader(),
			  'selectInsensitive': imgconvert.stackreader(
				  imgformat.grey, stopbutton.reader()),
			  }, STOP, 't'),
			],
		'close': [ CLOSE_WINDOW, ],
		}
	adornments2 = {
		'close': [ CLOSE_WINDOW, ],
		}

	def __init__(self, coords, title):
		"""Create the Player dialog.

		Create the dialog window (non-modal, so does not grab
		the cursor) but do not pop it up (i.e. do not display
		it on the screen).

		Arguments (no defaults):
		coords -- the coordinates (x, y, width, height) of the
			control panel in mm
		title -- string to be displayed as window title
		"""

		self.__window = None
		self.__title = title
		self.__coords = coords
		self.__state = -1
		self.__channels = []

	def close(self):
		"""Close the dialog and free resources."""
		if self.__window is not None:
			self.__window.close()
		self.__window = None
		del self.__channels

	def settitle(self, title):
		"""Set (change) the title of the window.

		Arguments (no defaults):
		title -- string to be displayed as new window title.
		"""
		self.__title = title
		if self.__window is not None:
			self.__window.settitle(title)

	def setchannels(self, channels):
		"""Set the list of channels.

		Arguments (no defaults):
		channels -- a list of tuples (name, onoff) where name
			is the channel name which is to be presented
			to the user, and onoff indicates whether the
			channel is on or off (1 if on, 0 if off)
		"""

		self.__channels = channels
		self.__channeldict = {}
		menu = []
		for i in range(len(channels)):
			channel, onoff = channels[i]
			self.__channeldict[channel] = i
			menu.append((channel, (channel,), 't', onoff))
		if self.__window is None:
			return
		self.__window.set_dynamiclist(CHANNELS, menu)

	def setchannel(self, channel, onoff):
		"""Set the on/off status of a channel.

		Arguments (no defaults):
		channel -- the name of the channel whose status is to
			be set
		onoff -- the new status
		"""

		i = self.__channeldict.get(channel)
		if i is None:
			raise RuntimeError, 'unknown channel'
		if self.__channels[i][1] == onoff:
			return
		self.__channels[i] = channel, onoff
		if self.__window is not None:
			self.setchannels(self.__channels)

	def setstate(self, state):
		"""Set the playing state of the control panel.

		Arguments (no defaults):
		state -- the new state:
			STOPPED -- the player is in the stopped state
			PLAYING -- the player is in the playing state
			PAUSING -- the player is in the pausing state
		"""

		ostate = self.__state
		self.__state = state
		if self.__window is not None and state != ostate:
			if state == STOPPED:
				self.__window.set_commandlist(self.stoplist)
			if state == PLAYING:
				self.__window.set_commandlist(self.playlist)
			if state == PAUSING:
				self.__window.set_commandlist(self.pauselist)
			self.setchannels(self.__channels)
			self.__window.set_toggle(PLAY, state != STOPPED)
			self.__window.set_toggle(PAUSE, state == PAUSING)
			self.__window.set_toggle(STOP, state == STOPPED)

	def hide(self):
		"""Hide the control panel."""

		if self.__window is None:
			return
		self.__window.close()
		self.__window = None

	def show(self, subwindowof=None):
		"""Show the control panel."""

		if self.__window is not None:
			self.__window.pop()
			return
		x, y, w, h = self.__coords
		if subwindowof is not None:
			raise 'kaboo kaboo'
		self.__window = w = windowinterface.newwindow(
			x, y, 0, 0, self.__title, resizable = 0,
			adornments = self.adornments,
			commandlist = self.stoplist)
		if self.__channels:
			self.setchannels(self.__channels)

	def __close_callback(self, dummy, window, event, val):
		self.close_callback()

	def getgeometry(self):
		"""Get the coordinates of the control panel.

		The return value is a tuple giving the coordinates
		(x, y, width, height) in mm of the player control
		panel.
		"""

		pass

	def setcursor(self, cursor):
		"""Set the cursor to a named shape.

		Arguments (no defaults):
		cursor -- string giving the name of the desired cursor shape
		"""
		if self.__window is not None:
			return self.__window.setcursor(cursor)

	def get_adornments(self, channel):
		return self.adornments2
