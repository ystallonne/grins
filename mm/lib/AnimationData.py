__version__ = "$Id$"

import string

import MMAttrdefs

# AnimationData pattern:
# <ref ...>
#   <animateMotion targetElement="xxx" values="x1, y1; x2, y2; x3, y3" keyTimes="0;0.3;1.0" dur="use_attr_edit"/>
#   <animate targetElement="xxx" attributeName="width" values="w1;w2;w3" keyTimes="0;0.3;1.0" dur="use_attr_edit"/>
#   <animate targetElement="xxx"  attributeName="height" values="h1;h2;h3" keyTimes="0;0.3;1.0" dur="use_attr_edit"/>
#   <animateColor targetElement="xxx" attributeName="backgroundColor" values="rgb1;rgb2;rgb3" keyTimes="0, 0.3, 1.0" dur="use_attr_edit"/>
# </ref>

class AnimationData:
	def __init__(self, node):
		self.node = node # animation target
		self.root = node.GetRoot()
		self.data = []   # a list of key frames (rect, color)
		self.times = []  # key times list

		# dom values for animated node
		# used for missing user values 
		self.dompos = None
		self.domwidth = None
		self.domheight = None
		self.domcolor = None
		self.initDomValues()
	
	#
	#  public
	#
	def isEmpty(self):
		return len(self.times)==0

	# animation editor call
	# set key times and data explicitly
	def setTimesData(self, times, data):
		assert len(times) == len(data), ''
		self.times = times
		self.data = data

	# animation editor call
	def getTimes(self):
		return self.times

	# animation editor call
	def getData(self):
		return self.data

	# read animate nodes and set self data
	def readData(self):
		children = self._getAnimateChildren()
		if not children:
			return

		str = MMAttrdefs.getattr(children[0], 'keyTimes')
		self.times = self._strToFloatList(str)

		animateMotionValues = [] 
		animateWidthValues = []
		animateHeightValues = [] 
		animateColorValues = []
		for anim in children:
			tag = anim.attrdict.get('atag')
			if tag == 'animateMotion':
				str = MMAttrdefs.getattr(anim, 'values')
				animateMotionValues = self._strToPosList(str)
			elif tag == 'animate':
				attributeName = MMAttrdefs.getattr(anim, 'attributeName')
				if attributeName == 'width':
					animateWidthValues = self._strToIntList(str)
				elif attributeName == 'height':
					animateHeightValues = self._strToIntList(str)
			elif tag == 'animateColor':
				animateColorValues = self._strToColorList(str)
		n = len(self.times)
		assert len(animateMotionValues) == n, ''
		assert len(animateWidthValues) == n, ''
		assert len(animateHeightValues) == n, ''
		assert len(animateColorValues) == n, ''
		for i in range(n):
			x, y = animateMotionValues[i]
			w = animateWidthValues[i]
			h = animateHeightValues[i]
			rect = x, y, w, h
			color = animateColorValues[i]
			self.data.append((rect, color))
	
	# create animate nodes from self data
	def applyData(self, editmgr):
		animateMotionValues, animateWidthValues,\
		animateHeightValues, animateColorValues = self._dataToValuesAttr()
		keyTimes = self._timesToKeyTimesAttr()
		
		existing = {}
		children = self._getAnimateChildren()
		if children:
			for anim in children:
				tag = anim.attrdict.get('atag')
				if tag == 'animateMotion':
					existing['pos'] = anim
				elif tag == 'animate':
					attributeName = MMAttrdefs.getattr(anim, 'attributeName')
					if attributeName == 'width':
						existing['width'] = anim
					elif attributeName == 'height':
						existing['height'] = anim
				elif tag == 'animateColor':
					existing['color'] = anim

		em = editmgr
		if not em.transaction():
			return 0
		
		anim = 	existing.get('pos')
		if anim is not None:
			self._updateNode(anim, keyTimes, animateMotionValues)
		else:
			anim = self.root.context.newanimatenode('animateMotion')
			anim.targetnode = self.node
			self._updateNode(anim, keyTimes, animateMotionValues)
			em.addnode(self.node, 0, anim)

		anim = 	existing.get('width')
		if anim is not None:
			self._updateNode(anim, keyTimes, animateWidthValues)
		else:
			anim = self.root.context.newanimatenode('animate')
			anim.targetnode = self.node
			self._updateNode(anim, keyTimes, animateWidthValues)
			em.addnode(self.node, 1, anim)

		anim = 	existing.get('height')
		if anim is not None:
			self._updateNode(anim, keyTimes, animateHeightValues)
		else:
			anim = self.root.context.newanimatenode('animate')
			anim.targetnode = self.node
			self._updateNode(anim, keyTimes, animateHeightValues)
			em.addnode(self.node, 2, anim)

		anim = 	existing.get('color')
		if anim is not None:
			self._updateNode(anim, keyTimes, animateColorValues)
		else:
			anim = self.root.context.newanimatenode('animate')
			anim.targetnode = self.node
			self._updateNode(anim, keyTimes, animateColorValues)
			em.addnode(self.node, 3, anim)
		
		em.commit()
		return 1

	#
	#  private
	#
	def _initDomValues(self):
		pass

	def _updateNode(self, node, times, values):
		node.attrdict['keyTimes'] = times
		node.attrdict['values'] = values

	def _getAnimateChildren(self):
		children = []
		for c in self.node.children:
			if c.GetType() == 'animate':
				children.append(c)
		return children

	def _dataToValuesAttr(self):
		animateMotionValues = [] 
		animateWidthValues = []
		animateHeightValues = [] 
		animateColorValues = []
		for rect, color in self.data:
			animateMotionValues.append(rect[:2])						
			animateWidthValues.append(rect[2])
			animateHeightValues.append(rect[3])
			animateColorValues.append(color)
		animateMotionValues = self._posListToStr(animateMotionValues)
		animateWidthValues = self._intListToStr(animateWidthValues)
		animateHeightValues = self._intListToStr(animateHeightValues)
		animateColorValues = self._colorListToStr(animateColorValues)
		return animateMotionValues, animateWidthValues, animateHeightValues, animateColorValues

	def _timesToKeyTimesAttr(self):
		return self._floatListToStr(self.times)

	def _intListToStr(self, sl):
		str = ''
		for val in sl:
			str = str + '%d;' % val
		return str[:-1]

	def _floatListToStr(self, sl):
		str = ''
		for val in sl:
			str = str + '%f;' % val
		return str[:-1]
		
	def _posListToStr(self, sl):
		str = ''
		for r, g, b in sl:
			str = str + '%d %d;' % (x, y)
		return str[:-1]

	def _colorListToStr(self, sl):
		str = ''
		for rgb in sl:
			if colors.rcolors.has_key(val):
				s = colors.rcolors[val]
			else:
				s = '#%02x%02x%02x' % rgb
			str = str + s + ';'
		return str[:-1]

	def _strToIntList(self, str):
		sl = string.split(str,';')
		vl = []
		for s in sl:
			if s: 
				vl.append(string.atoi(s))
		return vl	

	def _strToFloatList(self, str):
		sl = string.split(str,';')
		vl = []
		for s in sl:
			if s: 
				vl.append(string.atof(s))
		return vl	
		
	def _strToPosList(self, str):
		sl = string.split(str,';')
		vl = []
		for s in sl:
			if s: 
				pair = self._getNumPair(s)
				if pair:
					vl.append(string.atof(s))
		return vl	

	def _getNumPair(self, str):
		if not str: return None
		str = string.strip(str)
		sl = string.split(str)
		if len(sl)==2:
			x, y = sl
			return string.atoi(x), string.atoi(y)
		return None

	def _strToColorList(self, str):
		vl = []
		try:
			vl = map(convert_color, string.split(str,';'))
		except ValueError:
			pass
		return vl


############################
# should go normally to parse utilities
# copy/paste form SMILTreeRead

import SystemColors
import colors

def convert_color(val):
	val = val.lower()
	if colors.has_key(val):
		return colors[val]
	if val in ('transparent', 'inherit'):
		return val
	if SystemColors.colors.has_key(val):
		return SystemColors.colors[val]
	res = color.match(val)
	if res is None:
		self.syntax_error('bad color specification')
		return None
	hex = res.group('hex')
	if hex is not None:
		if len(hex) == 3:
			r = string.atoi(hex[0]*2, 16)
			g = string.atoi(hex[1]*2, 16)
			b = string.atoi(hex[2]*2, 16)
		else:
			r = string.atoi(hex[0:2], 16)
			g = string.atoi(hex[2:4], 16)
			b = string.atoi(hex[4:6], 16)
	else:
		r = res.group('ri')
		if r is not None:
			r = string.atoi(r)
			g = string.atoi(res.group('gi'))
			b = string.atoi(res.group('bi'))
		else:
			r = int(string.atof(res.group('rp')) * 255 / 100.0 + 0.5)
			g = int(string.atof(res.group('gp')) * 255 / 100.0 + 0.5)
			b = int(string.atof(res.group('bp')) * 255 / 100.0 + 0.5)
	if r > 255: r = 255
	if g > 255: g = 255
	if b > 255: b = 255
	return r, g, b


