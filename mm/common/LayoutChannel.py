__version__ = "$Id$"

from Channel import *
#
# This rather boring channel is used for laying-out other channels
#
class LayoutChannel(ChannelWindow):

	def __init__(self, name, attrdict, scheduler, ui):
		ChannelWindow.__init__(self, name, attrdict, scheduler, ui)
		self.is_layout_channel = 1
		self._activeMediaNumber = 0

	def do_arm(self, node, same=0):
		print 'LayoutChannel: cannot play nodes on a layout channel'
		return 1

	def create_window(self, pchan, pgeom, units = None):
##		menu = []
		if pchan:
##			if hasattr(self._player, 'editmgr'):
##				menu.append(('', 'raise', (self.popup, ())))
##				menu.append(('', 'lower', (self.popdown, ())))
##				menu.append(None)
##				menu.append(('', 'select in timeline view',
##					     (self.focuscall, ())))
##				menu.append(None)
##				menu.append(('', 'highlight',
##					     (self.highlight, ())))
##				menu.append(('', 'unhighlight',
##					     (self.unhighlight, ())))
			transparent = self._attrdict.get('transparent', 0)
			self._curvals['transparent'] = (transparent, 0)
			z = self._attrdict.get('z', 0)
			self._curvals['z'] = (z, 0)
			if self.want_default_colormap:
				self.window = pchan.window.newcmwindow(pgeom,
						transparent = transparent,
						z = z,
						type_channel = self._window_type,
						units = units)
			else:
				self.window = pchan.window.newwindow(pgeom,
						transparent = transparent,
						z = z,
						type_channel = self._window_type,
						units = units)
##			if hasattr(self._player, 'editmgr'):
##				menu.append(None)
##				menu.append(('', 'resize',
##					     (self.resize_window, (pchan,))))
		else:
			# no basewindow, create a top-level window
			adornments = self._player.get_adornments(self)
			units = self._attrdict.get('units',
						   windowinterface.UNIT_MM)
			width, height = self._attrdict.get('winsize', (50, 50))
			self._curvals['winsize'] = ((width, height), (50,50))
			x, y = self._attrdict.get('winpos', (None, None))
			if self.want_default_colormap:
				self.window = windowinterface.newcmwindow(x, y,
					width, height, self._name,
					visible_channel = self._visible,
					type_channel = self._window_type,
					units = units, adornments = adornments,
					commandlist = self.commandlist)
			else:
				self.window = windowinterface.newwindow(x, y,
					width, height, self._name,
					visible_channel = self._visible,
					type_channel = self._window_type,
					units = units, adornments = adornments,
					commandlist = self.commandlist)
##			if hasattr(self._player, 'editmgr'):
##				menu.append(('', 'select in timeline view',
##					     (self.focuscall, ())))
		if self._attrdict.has_key('bgcolor'):
			self.window.bgcolor(self._attrdict['bgcolor'])
		if self._attrdict.has_key('fgcolor'):
			self.window.fgcolor(self._attrdict['fgcolor'])
		self._curvals['bgcolor'] = self._attrdict.get('bgcolor'), None
		self._curvals['fgcolor'] = self._attrdict.get('fgcolor'), None
		self.window.register(WMEVENTS.ResizeWindow, self.resize, None)
		self.window.register(WMEVENTS.Mouse0Press, self.mousepress, None)
		self.window.register(WMEVENTS.Mouse0Release, self.mouserelease,
				     None)
##		if menu:
##			self.window.create_menu(menu, title = self._name)


	def do_show(self, pchan):
		# create a window for this channel
		pgeom = None
		units = self._attrdict.get('units',
					   windowinterface.UNIT_SCREEN)
		if pchan:
			#
			# Find the base window offsets, or ask for them.
			#
			if self._played_node:
				try:
					pgeom = MMAttrdefs.getattr(self._played_node, 'base_winoff')
				except KeyError:
					pass
			if pgeom:
				self._wingeom = pgeom
			elif self._attrdict.has_key('base_winoff'):
				self._wingeom = pgeom = self._attrdict['base_winoff']
			elif self._player.playing:
				windowinterface.showmessage(
					'No geometry for subchannel %s known' % self._name,
					mtype = 'error', grab = 1)
				pchan._subchannels.remove(self)
				pchan = None
			else:
##				pchan.window.create_box(
##					'Draw a subwindow for %s in %s' %
##						(self._name, pchan._name),
##					self._box_callback,
##					units = units)
##				return None
				#
				# Window without position/size. Set to whole parent, and remember
				# in the attributes. (Note: technically wrong, changing the attrdict
				# without using the edit mgr).
				# Or should I skip the curvals stuff below, to do this correctly?
				#
				self._wingeom = pgeom = (0.0, 0.0, 1.0, 1.0)
				units = windowinterface.UNIT_SCREEN
				self._attrdict['base_winoff'] = pgeom
				self._attrdict['units'] = units
			self._curvals['base_winoff'] = pgeom, None
		
		# we have to render visible the channel at start according to the 
		# showBackground attribute
		if self._hasBackgroundAtStart():
			self._setVisible(1)
		return 1

	def play(self, node):
		print 'can''t play LayoutChannel'

	# A channel pass active (when one more media play inside).
	# We have to render visible all channel which are at least one media playing inside
	def updateToActiveState(self):
		ch = self
		chToVisible = None
		while ch != None:
			if not ch._hasBackgroundAtStart():
				if ch._activeMediaNumber <= 0:
						chToVisible = ch
				ch._activeMediaNumber = ch._activeMediaNumber+1
				ch = ch._get_parent_channel()
			else:
				break

		# if found, render it visible
		if chToVisible:
			chToVisible._setVisible(1)
			
	# A channel pass inactive (when no media play inside anymore).
	# We have to rendered unvisible all channel according to the showBackground attribute
	def updateToInactiveState(self):
		ch = self
		# looking for the first channel (in hierarchy) which pass inactive
		chToUnvisible = None
		while ch != None:
			if not ch._hasBackgroundAtStart():
				ch._activeMediaNumber = ch._activeMediaNumber-1
				if ch._activeMediaNumber <= 0:
					if self._attrdict['showBackground'] == 'whenActive':
						chToUnvisible = ch
				ch = ch._get_parent_channel()
			else:
				break

		# if found, render it invisible (and all channels inside)
		if chToUnvisible:
			chToUnvisible._setVisible(0)
			
	# Set this channel visible/unvisible according to the showBackground attribute
	
	###################################### WARNING ###################################
	# for now, we destroy the window when the channel pass inactive (only method which
	# actually work). We also destroy all windows inside
	# we can't use hide/show because they modify a lot of things (structure of channel,
	# state in some case, ...). Otherwise you have a crash in a lot of cases.
	# The best method whould be call hide/show without destroy and rebuild the window, 
	# but it doesn't work actually
	##################################################################################
	def _setVisible(self, fl):
		if self.window == None and fl:
			ChannelWindow._setVisible(self,fl)
			for subch in self._subchannels:
			        if subch._attrdict['showBackground'] != 'whenActive' or \
			                subch._activeMediaNumber > 0:
					subch._setVisible(fl)
			
		elif self.window != None and not fl:
			for subch in self._subchannels:
				subch._setVisible(fl)
			ChannelWindow._setVisible(self,fl)
		
			