__version__ = "$Id$"

#
#	SVG data types
#

import re
import string
import math

################
# common patterns

_S = '[ \t\r\n]+'
_opS = '[ \t\r\n]*'
_D = '[ ,\t\r\n]+'
_opD = '[ ,\t\r\n]*'
_sign = r'(?P<sign>[+-]?)'

intPat = r'(?P<int>\d+)'
signedIntPat = _sign + _opS + intPat

n1pat = r'((?P<int1>\d+)(\.(?P<dec1>\d+))?)'
n2pat = r'((?P<int2>\d+)\.)'
n3pat = r'(\.(?P<dec3>\d+))'
numberPat = '(' + n1pat + '|' + n2pat + '|' + n3pat + ')'
signedNumberPat = _sign + _opS + numberPat

lengthUnitsPat = r'(?P<units>(px)|(pt)|(pc)|(mm)|(cm)|(in)|(%))'

angleUnitsPat = r'(?P<units>(deg)|(grad)|(rad))'

freqUnitsPat = r'(?P<units>(Hz)|(kHz))'

timeUnitsPat = r'(?P<units>s|ms)?'

fargPat = r'(?P<arg>[(][^)]*[)])'

transformPat = _opD + r'(?P<op>matrix|translate|scale|rotate|skewX|skewY)' + _opS + fargPat 

percentPat = numberPat + _opS + '%$'

from svgcolors import svgcolors
color = re.compile('(?:'
		   '#(?P<hex>[0-9a-fA-F]{3}|'		# #f00
			    '[0-9a-fA-F]{6})|'		# #ff0000
			   'rgb' + _opS + r'\(' +		# rgb(R,G,B)
			   _opS + '(?:(?P<ri>[0-9]+)' + _opS + ',' + # rgb(255,0,0)
			   _opS + '(?P<gi>[0-9]+)' + _opS + ',' +
			   _opS + '(?P<bi>[0-9]+)|' +
			   _opS + '(?P<rp>[0-9]+)' + _opS + '%' + _opS + ',' + # rgb(100%,0%,0%)
			   _opS + '(?P<gp>[0-9]+)' + _opS + '%' + _opS + ',' +
			   _opS + '(?P<bp>[0-9]+)' + _opS + '%)' + _opS + r'\))$')

# style type="text/css" parsing
bracketsPat = r'(?P<arg>[{][^}]*[}])' # braces content
classdefPat = r'[.](?P<cname>[a-zA-Z_:][-a-zA-Z0-9._]*)' + _opS + bracketsPat
textcssPat = _opS + classdefPat + _opS

# <!ENTITY parsing
entityNamePat = r'(?P<name>[a-zA-Z_:][-a-zA-Z0-9._:]*)' # entity name
quoteDef = r'(?P<arg>["][^"]*["])' # quote content
entityPat = _opS + '<!ENTITY' + _S + entityNamePat + _S + quoteDef + _opS + '>'

# simple sync val
ideventPat = r'((?P<name>[a-zA-Z_:][-a-zA-Z0-9_:]*)\.(?P<event>(begin)|(end)))'
syncvalPat = ideventPat + '?' + _opS + _sign + _opS + numberPat + '?' + timeUnitsPat

################
# utilities

class StringTokenizer:
	def __init__(self, str, delim=' \t\n\r\f'):
		self.__str = str
		self.__delim = delim
		self.__pos = 0
		self.__maxpos = len(str)
	def hasMoreTokens(self):
		return (self.__pos < self.__maxpos)
	def nextToken(self):
		if self.__pos >= self.__maxpos:
			raise None
		start = self.__pos
		while self.__pos < self.__maxpos and self.__delim.find(self.__str[self.__pos])<0:
			self.__pos = self.__pos + 1
		if start == self.__pos and self.__delim.find(self.__str[self.__pos])>=0:
			self.__pos = self.__pos + 1
		return self.__str[start:self.__pos]

class StringSplitter:
	def __init__(self, str, delim=' ,'):
		self.__str = str
		self.__delim = delim
		self.__pos = 0
		self.__maxpos = len(str)
	def hasMoreTokens(self):
		while self.__pos < self.__maxpos and self.__delim.find(self.__str[self.__pos])>=0:
			self.__pos = self.__pos + 1
		return (self.__pos < self.__maxpos)
	def nextToken(self):
		while self.__pos < self.__maxpos and self.__delim.find(self.__str[self.__pos])>=0:
			self.__pos = self.__pos + 1
		if self.__pos == self.__maxpos:
			return None
		start = self.__pos
		while self.__pos < self.__maxpos and self.__delim.find(self.__str[self.__pos])<0:
			self.__pos = self.__pos + 1
		return self.__str[start:self.__pos]

def splitlist(str, delims=' ,'):
	st = StringSplitter(str, delims)
	L = []
	token = st.nextToken()
	while token:
		L.append(token)
		token = st.nextToken()
	return L

def actof(nsign, intg, decg):
	if intg is None and decg is None:
		return None
	if intg is None:
		intg = '0'
	if decg is None:
		decg = '0'
	if not nsign or nsign=='+':
		return string.atof('%s.%s' % (intg, decg))
	else:
		return -string.atof('%s.%s' % (intg, decg))

def ff(val):
	if val < 0:
		val = -val
		sign = '-'
	else:
		sign = ''
	str = '%f' % val
	if '.' in str:
		while str[-1] == '0':
			str = str[:-1]
		if str[-1] == '.':
			str = str[:-1]
	while len(str) > 1 and str[0] == '0' and str[1] in '0123456789':
		str = str[1:]
	if not str:
		str = '0'
	return sign + str

def deg2rad(deg):
	return (deg/180.0)*math.pi
	
################
# base classes

# base class for animateable attributes
class Animateable:
	def __init__(self):
		self.animators = []

	def appendAnimator(self, a):
		self.animators.append(a)

	def removeAnimator(self, a):
		self.animators.remove(a)

	def hasAnimator(self, a):
		return a in self.animators

	def getPresentValue(self, below = None):
		if not self.animators:
			return self.getValue()
		cv = self.getValue()
		for a in self.animators:
			if below and id(a) == id(below):
				break
			if a.isAdditive() and not a.isEffValueAnimator():
				cv = self.addValues(cv, a.getCurrValue())
			else:
				cv = a.getCurrValue()
		displayValue = cv
		displayValue = self.convertAndClamp(displayValue)
		return displayValue

	def isAdditionDefined(self):
		return 1

	# override this method to force range
	def convertAndClamp(self, val):
		return val

	# override this method to override addition
	def addValues(self, val1, val2):
		return val1 + val2

	# override this method to override distance
	def distValues(self, v1, v2):
		return math.fabs(v2-v1)

class SVGAttr(Animateable):
	def __init__(self, node, attr, str, default):
		self._node = node
		self._attr = attr
		self._value = None
		self._default = default
		Animateable.__init__(self)


################
# svg types

# import path related svg types
from svgpath import PathSeg, SVGPath

class SVGEnum(SVGAttr):
	def __init__(self, node, attr, val, default=None):
		SVGAttr.__init__(self, node, attr, val, default)
		self._value = val

	def getValue(self):
		if self._value is not None:
			return self._value
		return self._default

	def isDefault(self):
		return self._value is None or self._value == self._default

	def isAdditionDefined(self):
		return 0

	def getPresentValue(self, below=None):
		if not self.animators:
			return self.getValue()
		n = len(self.animators)
		a = self.animators[n-1]
		return a.getCurrValue()

class SVGInteger(SVGAttr):
	classre = re.compile(_opS + signedIntPat + _opS)
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		if str:
			str = string.strip(str)
			mo = SVGInteger.classre.match(str)
			if mo is not None:
				self._value = mo.group('int')

	def getValue(self):
		if self._value is not None:
			return self._value
		return self._default

	def isDefault(self):
		return self._value == self._default

class SVGNumber(SVGAttr):
	classre = re.compile(signedNumberPat + '$')
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		if str:
			str = string.strip(str)
			mo = SVGNumber.classre.match(str)
			if mo is not None:
				i, d = mo.group('int1') or mo.group('int2'), mo.group('dec1') or mo.group('dec3')
				self._value = actof(mo.group('sign'), i, d)
	def getValue(self):
		if self._value is not None:
			return self._value
		return self._default

	def isDefault(self):
		return self._value is None or self._value == self._default

class SVGGEZeroNumber(SVGNumber):
	def __init__(self, node, attr, str, default=None):
		SVGNumber.__init__(self, node, attr, str, default)
		assert self._value is None or self._value>=0, 'number should be GE to zero'

class SVGCount(SVGNumber):
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		if str == 'indefinite':
			SVGAttr.__init__(self, node, attr, None, default)
			self._value = 'indefinite'
		else:
			SVGAttr.__init__(self, node, attr, str, default)
			assert self._value is None or self._value>=0, 'SVGCount should be GE to zero'

class SVGNumberList(SVGAttr):
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		if str:
			sl = splitlist(str)
			self._value = []
			for s in sl:
				self._value.append(string.atoi(s))

	def __repr__(self):
		s = ''
		for num in self._value:
			s = s + '%s ' % ff(num)
		return s[:-1]

	def getValue(self):
		if self._value is not None:
			return self._value
		return self._default

	def isDefault(self):
		return self._value is None or len(self._value)==0

class SVGPercent(SVGAttr):
	classre = re.compile(percentPat)
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		if str:
			str = string.strip(str)
			mo = SVGPercent.classre.match(str)
			if mo is not None:
				i, d = mo.group('int1') or mo.group('int2'), mo.group('dec1') or mo.group('dec3')
				self._value = actof(None, i, d)

	def __repr__(self):
		return '%s' % ff(self._value) + '%'

	def getValue(self):
		if self._value is not None:
			return self._value
		return self._default

	def isDefault(self):
		return self._value == self._default

class SVGLength(SVGAttr):
	classre = re.compile(signedNumberPat + lengthUnitsPat + '?$')
	#unitstopx = {'px':1.0, 'pt':1.25, 'pc':15.0, 'mm': 3.543307, 'cm':35.43307, 'in':90.0}
	unitstopx = {'px': 1.0, 'pt': 1.0, 'pc': 12.0, 'mm': 2.8346456, 'cm': 28.346456, 'in': 72.0}
	defaultunit = 'px'
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		self._units = None
		if str is None:
			return
		if str == 'none':
			self._value = 'none'
			return
		if str:
			str = string.strip(str)
			mo = self.classre.match(str)
			if mo is not None:
				i, d = mo.group('int1') or mo.group('int2'), mo.group('dec1') or mo.group('dec3')
				self._value = actof(mo.group('sign'), i, d)
				if self._value is not None and self._value<0 and self.__class__ == SVGLength:
					assert 0, 'length can not be negative'
				if self._value is not None:
					self._units = mo.group('units')

	def __repr__(self):
		if self._value is None:
			return ''
		elif self._value is 'none':
			return 'none'
		elif self._units is None:
			return '%s' % ff(self._value)
		else:	
			return '%s%s' % (ff(self._value), self._units)
	
	def getValue(self, units='px'):
		if self._value is not None:
			if self._units=='%':
				pass # find parent size
			f1 = self.unitstopx.get(self._units or 'px')
			pixels = f1*self._value
			if units == 'px':
				return int(pixels)
			f2 = self.unitstopx.get(units)
			return pixels/f2
		return self._default

	def getUnits(self):
		return self._units

	def isDefault(self):
		return self._value == self._default

	def getDeviceValue(self, tm, f):
		val = self.getValue()
		if self._units is not None:
			tm = tm.copy()
			tm.inverse()
			if f == 'w':
				return int(tm.UWtoDW(val))
			elif f == 'h':
				return int(tm.UHtoDH(val))
		return val
	
	def getElement(self):
		return self._node
	
	def setValue(self, val, units='px'):
		self._value = val
		self._units = units
			
class SVGWidth(SVGLength):
	pass

class SVGHeight(SVGLength):
	pass

# like SVGLength but can be negative
class SVGCoordinate(SVGLength):
	pass

class SVGPoint(SVGAttr):
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		if str:
			L = splitlist(str, ' ,')
			assert len(L) == 2, 'invalid point'
			xstr, ystr = L
			self._value = SVGLength(node, xstr).getLength(), SVGLength(node, ystr).getLength()

	def getValue(self):
		if self._value is not None:
			return self._value
		return self._default

	def isDefault(self):
		return self._value is None or self._value == self._default

class XMLName:
	classre = re.compile('[a-zA-Z_:][-a-zA-Z0-9._:]*')
	def __init__(self, node, attr, str, default=None):
		self._node = node
		self._attr = attr
		self._value = None
		self._default = default
		if str:
			str = string.strip(str)
			mo = self.classre.match(str)
			if mo is None:
				print 'invalid XML name', str
			self._value = str

	def getValue(self):
		return self._value		

class SVGAngle(SVGAttr):
	classre = re.compile(signedNumberPat + angleUnitsPat + '?$')
	svgunits = ('deg', 'grad', 'rad',)
	unitstorad = {'deg':math.pi/180.0, 'grad':math.pi/200.0, 'rad':1.0}
	defaultunit = 'deg'
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		self._units = None
		if str:
			str = string.strip(str)
			mo = SVGAngle.classre.match(str)
			if mo is not None:
				i, d = mo.group('int1') or mo.group('int2'), mo.group('dec1') or mo.group('dec3')
				self._value = actof(mo.group('sign'), i, d)
				if self._value is not None:
					units = mo.group('units')
					if units is None:
						units = SVGAngle.defaultunit
					self._units = units

	def __repr__(self):
		return '%s%s' % (ff(self._value), self._units)
	
	def getValue(self, units='rad'):
		if self._value is not None:
			f1 = self.unitstorad.get(self._units)
			val = f1*self._value
			if units == 'rad':
				return val
			f2r = 1.0/self.unitstorad.get(units)
			return val*f2r
		return self._default

	def isDefault(self):
		return self._value == self._default

class SVGAnimRotate(SVGAngle):
	def __init__(self, node, attr, str, default=None):
		if str in ('auto', 'auto-reverse'):
			SVGAngle.__init__(self, node, attr, None, default)
			self._value = str
		else:
			SVGAngle.__init__(self, node, attr, str, default)

	def __repr__(self):
		if self._value in ('auto', 'auto-reverse'):
			return self._value
		return '%s%s' % (ff(self._value), self._units)

	def getValue(self, units='rad'):
		if self._value in ('auto', 'auto-reverse'):
			return self._value
		return SVGAngle.getValue(self, units)

class SVGColor(SVGAttr):
	classre = color
	def __init__(self, node, attr, val, default=None):
		SVGAttr.__init__(self, node, attr, val, default)
		if val is None:
			return
		if val == 'none':
			self._value = 'none'
			return
		val = string.lower(val)
		if svgcolors.has_key(val):
			self._value = svgcolors[val]
			return
		res = SVGColor.classre.match(val)
		if res is None:
			print 'bad color specification', val
			return
		else:
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
		self._value = r, g, b

	def __repr__(self):
		if self._value is None or self._value == 'none':
			return 'none'
		return 'rgb(%d, %d, %d)' % self._value

	def getValue(self):
		if self._value is not None:
			return self._value
		return self._default

	def isDefault(self):
		return self._value is None or self.value == self._default

	def getPresentValue(self, below=None):
		if not self.animators:
			return self.getValue()
		cv = self.getValue()
		if cv is None or cv == 'none':
			cv = 0, 0, 0
		for a in self.animators:
			if below and id(a) == id(below):
				break
			if a.isAdditive() and not a.isEffValueAnimator():
				cv = self.addValues(cv, a.getCurrValue())
			else:
				cv = a.getCurrValue()
		displayValue = cv
		displayValue = self.convertAndClamp(displayValue)
		return displayValue

	# override this method to force range
	def convertAndClamp(self, v):
		n = len(v)
		r = []
		for i in range(n):
			val = int(v[i]+0.5)
			if val<0: r.append(0)
			elif val>255: r.append(255)
			else: r.append(val)
		return tuple(r)

	# override this method to override addition
	def addValues(self, v1, v2):
		n = len(v1)
		r = []
		for i in range(n):
			r.append(v1[i]+v2[i])
		return tuple(r)

class SVGFrequency(SVGAttr):
	classre = re.compile(_opS + numberPat + freqUnitsPat + _opS)
	svgunits = ('Hz', 'kHz')
	defaultunit = 'Hz'
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		self._units = None
		if str:
			str = string.strip(str)
			mo = SVGFrequency.classre.match(str)
			if mo is not None:
				i, d = mo.group('int1') or mo.group('int2'), mo.group('dec1') or mo.group('dec3')
				self._value = actof(None, i, d)
				if self._value is not None:
					units = mo.group('units')
					if units is None:
						units = SVGFrequency.defaultunit
					self._units = units

	def __repr__(self):
		return '%s%s' % (ff(self._value), self._units)
	
	def getValue(self, units='Hz'):
		if self._value is not None:
			if self._units == 'kHz':
				f1 = 1000.0
			val = f1*self._value
			if units == 'Hz':
				return val
			f2r = 0.001
			return 0.001*val
		return self._default

	def isDefault(self):
		return self._value == self._default

class SVGTime:
	classre = re.compile(signedNumberPat + timeUnitsPat + '$')
	svgunits = ('s', 'ms')
	defaultunit = 's'
	def __init__(self, node, attr, str, default=None):
		self._node = node
		self._attr = attr
		self._units = None
		self._value = None
		self._default = default
		if str:
			str = string.strip(str)
			if str == 'indefinite':
				self._value = 'indefinite'
				return
			mo = SVGTime.classre.match(str)
			if mo is not None:
				i, d = mo.group('int1') or mo.group('int2'), mo.group('dec1') or mo.group('dec3')
				self._value = actof(mo.group('sign'), i, d)
				if self._value is not None:
					units = mo.group('units')
					if units is None:
						units = SVGTime.defaultunit
					self._units = units

	def __repr__(self):
		return '%s%s' % (ff(self._value), self._units)
	
	def getValue(self, units='s'):
		if self._value is not None:
			if self._value == 'indefinite':
				return 'indefinite'
			if self._units == 'ms':
				val = 0.001*self._value
			else:
				val = self._value
			if units == 's':
				return val
			return 1000.0*val
		return self._default

	def isDefault(self):
		return self._value == self._default


class SyncArc:
	def __init__(self, node, attrobj):
		self.node = node
		self.target = attrobj # SyncVariant target

	def __repr__(self):
		return '%s.%s -> %s.%s' % (self.node.getTimeType(), self.target._syncevent, self.target._node.getTimeType(), self.target._attr)

	def getScrNode(self):
		return self.node

	# return type in ('begin', 'end', 'repeat', 'event')
	def getSrcEvent(self):
		return self.target._syncevent

	# params is repeat index or dom2event name
	def getSrcEventParams(self):
		return self.target._synceventparams

	def getTargetNode(self):
		return self.target._node

	# return in ('begin', 'end')
	def getTargetAttr(self):
		return self.target._attr

	# time t reference timer is self.node's parent timer
	# the time has to be translated to self.target parent timer
	def addInstanceTime(self, t, params=None):
		p1 = self.node.getTimeParent()
		if p1 is None: p1 = self.node
		p2 = self.getTargetNode().getTimeParent()
		if p2 is None: p2 = self.getTargetNode()
		if p1 != p2:
			# xxx: for oprimization use common ancestor
			t = p2.document2simple(p1.simple2document(t))
		if t != 'unresolved':
			self.target.addInstanceTime(t, params)

class SyncVariant:
	classre = re.compile(syncvalPat + '$')
	svgunits = ('s', 'ms')
	defaultunit = 's'
	def __init__(self, node, attr, str, default=None):
		# target node
		self._node = node

		# target attr
		self._attr = attr

		# source node specifiers
		self._syncbase = None # 'id', 'prev', 'implicit'
		self._syncbaseparams = None # id when syncbase == 'id' otherwise ignore

		# source node event specifiers
		self._syncevent = None # 'begin', 'end', 'repeat', 'event', 'implicit'

		# when syncevent=='repeat' synceventparams is the repeat index
		# when syncevent=='event' synceventparams is the dom2event name
		self._synceventparams = None 

		# target node offset specifiers
		self._offset = None # (+|-)? clock-value | implicit-0 | indefinite
		self._units = None

		# source event instance list
		self._insttimes = []

		# parse str
		if str:
			str = string.strip(str)
		if not str:
			return
		if str == 'indefinite':
			self._offset = 'indefinite'
			return
		mo = self.classre.match(str)
		if mo is not None:
			self._syncbase, self._syncevent = mo.group('name'), mo.group('event')
			i, d = mo.group('int1') or mo.group('int2'), mo.group('dec1') or mo.group('dec3')
			self._offset = actof(mo.group('sign'), i, d) or 0
			if self._offset is not None:
				units = mo.group('units')
				if units is None:
					units = self.defaultunit
				self._units = units
			else:
				self._offset = 0
				self._units = self.defaultunit
			if self._syncbase is None:
				self._syncbase = 'implicit'
			elif self._syncbase != 'prev':
				self._syncbaseparams = self._syncbase
				self._syncbase = 'id'

			if self._syncevent is None:
				self._syncevent = 'implicit'
			elif self._syncevent not in ('begin', 'end', 'repeat'):
				self._syncbaseparams = self._syncevent
				self._syncevent = 'event'
	
	def __repr__(self):
		if self._syncbaseparams is None:
			base = self._syncbase
		else:
			base = '%s(%s)' % (self._syncbase, `self._syncbaseparams`) 
		if self._synceventparams is None:
			event = self._syncevent
		else:
			base = '%s(%s)' % (self._syncevent, `self._synceventparams`) 
		return '%s.%s + %s' % (base, event, `self._offset`)

	def setEvent(self, event, params=None):
		self._syncbase = 'parent'

		# source node event specifiers
		self._syncevent = event # 'begin', 'end', 'repeat', 'event'

		# when syncevent=='repeat' synceventparams is the repeat index
		# when syncevent=='event' synceventparams is the dom2event name
		self._synceventparams = params 

	def setOffset(self, offset, units='s'):
		self._offset = offset 
		self._units = units
		
	def isEventBased(self):
		return self._syncevent == 'event'
			
	def hasPendingEvents(self):
		return self._syncevent == 'event' and len(self._insttimes)==0

	def reset(self):
		self._insttimes = []
	
	def addInstanceTime(self, t, params=None):
		if self._syncevent == 'repeat':
			if self._synceventparams is None: # repeat
				self._insttimes.append(t)	
			elif self._synceventparams == params: # repeat(index)
				self._insttimes.append(t)	
		else:
			self._insttimes.append(t)

	def getOffset(self, units='s'):
		if self._offset is not None:
			if self._offset == 'indefinite':
				return 'indefinite'
			if self._units == 'ms':
				val = 0.001*self._offset
			else:
				val = self._offset
			if units == 's':
				return val
			return 1000.0*val
		return self._default

	def createSyncArc(self):
		if self._syncbase == 'id':
			src = self._node.getDocument().getElementWithId(self._syncbaseparams)
			if src:
				arc = SyncArc(src, self)
				src.addSyncArc(arc)
		elif self._syncbase == 'prev':
			src = self._node.getPrevTimeSibling()
			if not src:
				src = self._node.getParent()
			if src:
				arc = SyncArc(src, self)
				src.addSyncArc(arc)
		elif self._syncbase == 'implicit':
			if self._syncevent == 'event':
				arc = SyncArc(self._node, self)
				self._node.addSyncArc(arc)
			elif self._attr == 'begin':
				parent = self._node.getTimeParent()
				if not parent: return
				ptype = parent.getTimeType()
				if ptype == 'par':
					self._syncbase = 'parent'
					self._syncevent = 'begin'
					arc = SyncArc(parent, self)
					parent.addSyncArc(arc)
				elif ptype == 'seq':
					self._syncbase = 'prev'
					self._syncevent = 'begin'
					src = self._node.getPrevTimeSibling()
					if not src:
						src = self._node.getTimeParent()
					if src:
						arc = SyncArc(src, self)
						src.addSyncArc(arc)
				elif ptype == 'excl':
					pass

	def isIndefinite(self):
		return self._offset == 'indefinite'

	def getValueList(self):
		offset = self.getOffset()
		if offset == 'indefinite':
			return []
		L = []
		for val in self._insttimes:
			L.append(val+offset)
		return L
				
class SyncVariantList:
	def __init__(self, node, attr, str, default=None):
		self._node = node
		self._attr = attr
		self._syncvarslist = []
		self._default = default
		self._explicit = 0
		if str:
			str = string.strip(str)
		if not str:
			return
		synclist = string.split(str, ';')
		for syncstr in synclist:
			if syncstr:
				self._syncvarslist.append(SyncVariant(node, attr, syncstr))
		self._explicit = len(self._syncvarslist) != 0	

	def __repr__(self):
		s = '%s =\"' % self._attr
		for syncvar in self._syncvarslist:
			s = s + repr(syncvar) + '; '
		s = s[:-2] + '\"'
		return s
					
	def reset(self):
		for syncvar in self._syncvarslist:
			syncvar.reset()

	def isEmpty(self):
		return len(self._syncvarslist) == 0

	def isExplicit(self):
		return self._explicit

	def createSyncArcs(self):
		for syncvar in self._syncvarslist:
			syncvar.createSyncArc()

	def getValueList(self):
		L = []
		for syncvar in self._syncvarslist:
			L = L + syncvar.getValueList()
		L.sort()
		for syncvar in self._syncvarslist:
			if syncvar.isIndefinite():
				L.append('indefinite')
		return L

	def beginIteration(self):
		L = []
		for syncvar in self._syncvarslist:
			L = L + syncvar.getValueList()
		L.sort()
		for syncvar in self._syncvarslist:
			if syncvar.isIndefinite():
				L.append('indefinite')
		self._ilist = L[:]
		self._iindex = 0

	def hasPendingEvents(self):
		for syncvar in self._syncvarslist:
			if syncvar.hasPendingEvents():
				return 1
		return 0

	def getNextGT(self, after):
		if not self._ilist:
			return None
		n = len(self._ilist)
		for i in range(self._iindex, n):
			v = self._ilist[i]
			self._iindex = i + 1
			if v == 'indefinite':
				if after != 'indefinite':
					return 'indefinite'
				else:
					return None
			elif after == 'indefinite':
				return None
			elif after == '-infinity':
				return v
			elif v > after:
				return v
		return None

	def getFirstGE(self, after):
		self.beginIteration()
		return self.getNextGE(after)

	def getNextGE(self, after):
		if not self._ilist:
			return None
		n = len(self._ilist)
		for i in range(self._iindex, n):
			v = self._ilist[i]
			self._iindex = i + 1
			if v == 'indefinite':
				return 'indefinite'
			elif after == 'indefinite':
				return None
			elif after == '-infinity':
				return v
			elif v >= after:
				return v
		return None
	
	# XXX: temp test
	def getValue(self):
		self.beginIteration()
		return self.getNextGT('-infinity')

	def addSync(self, src, event, evparams=None, offset=0):
		varlist = self._syncvarslist
		var = SyncVariant(self._node, self._attr, None)
		var.setEvent(event, evparams)
		var.setOffset(offset)
		varlist.append(var)
		arc = SyncArc(src, var)
		src.addSyncArc(arc)
		return arc

			
# fill:none; stroke:blue; stroke-width: 20
class SVGStyle:
	def __init__(self, node, attr, str, default=None):
		self._node = node
		self._attr = attr
		self._styleprops = {}
		self._default = default
		if not str:
			return
		stylelist = string.split(str, ';')
		for propdef in stylelist:
			if propdef:
				try:
					prop, val = string.split(propdef, ':')
					prop, val = string.strip(prop), string.strip(val)
				except:
					pass
				else:
					self._styleprops[prop] = val		
		for prop, val in self._styleprops.items():
			if val is not None and val != 'none':
				self._styleprops[prop] = CreateSVGAttr(self._node, prop, val)

	def __repr__(self):
		s = ''
		for prop, val in self._styleprops.items():
			if val is not None and type(val) != type(''):
				val = val.getValue()
			if val:
				s = s + prop + ':' + self.toString(prop, val) + '; '
		return s[:-2]

	def toString(self, prop, val):
		if prop == 'fill' or prop == 'stroke':
			if val == 'none':
				return 'none'
			else:
				return 'rgb(%d, %d, %d)' % val
		elif prop == 'stroke-width' or prop == 'font-size':
			return '%s' % ff(val)
		return val

	def getValue(self):
		return self._styleprops

	def isDefault(self):
		return self._styleprops is None or len(self._styleprops)==0
	
	def update(self, other):
		self._styleprops.update(other.getValue())

class SVGTextCss:
	classre = re.compile(textcssPat)
	def __init__(self, node, attr, str, default=None):
		self._node = node
		self._attr = attr
		self._textcssdefs = {}
		self._default = default
		mo = self.classre.match(str)
		while mo is not None:
			str = str[mo.end(0):]
			classname = mo.group(1)
			stylestr = mo.group(2)[1:-1] # remove brackets
			self._textcssdefs[classname] = SVGStyle(self._node, 'classstyle', stylestr)
			mo = SVGTextCss.classre.match(str)
	
	def __repr__(self):
		return ''

	def getValue(self):
		return self._textcssdefs

	def isDefault(self):
		return self._textcssdefs is None or len(self._textcssdefs)==0

class SVGEntityDefs:
	classre = re.compile(entityPat)
	def __init__(self, node, attr, str, default=None):
		self._node = node
		self._attr = attr
		self._units = None
		self._entitydefs = {}
		self._default = default
		if str:
			mo =  SVGEntityDefs.classre.match(str)
			while mo is not None:
				str = str[mo.end(0):]
				entityName = mo.group('name')
				entityDef = mo.group('arg')[1:-1]
				self._entitydefs[entityName] = entityDef
				mo =  SVGEntityDefs.classre.match(str)

	def __repr__(self):
		s = ''
		for key, val in self._entitydefs.items():
			s = s + '<!ENTITY ' + key + ' \"' + val + '\">\n'
		return s

	def getValue(self):
		return self._entitydefs

	def isDefault(self):
		return self._entitydefs is None or len(self._entitydefs)==0

class SVGPoints:
	def __init__(self, node, attr, str, default=None):
		self._node = node
		self._attr = attr
		self._points = []
		self._default = default
		st = StringSplitter(str, delim=' ,\t\n\r\f')
		while st.hasMoreTokens():
			x = st.nextToken()
			if st.hasMoreTokens():
				y = st.nextToken()
				try:
					x, y = string.atoi(x), string.atoi(y)
				except:
					pass
				else:
					self._points.append((x, y))

	def __repr__(self):
		s = ''
		for point in self._points:
			s = s + '%d, %d ' % point
		return s[:-1]

	def getValue(self):
		return self._points

	def isDefault(self):
		return self._points is None or len(self._points)==0

class SVGAspectRatio:
	aspectRatioPat = r'(?P<align>[a-zA-Z_:][-a-zA-Z0-9._:]*)' + '([ ]+(?P<meetOrSlice>[a-zA-Z_:][-a-zA-Z0-9._:]*))?'
	classre = re.compile(_opS + aspectRatioPat + _opS)
	alignEnum = ('none', 
		'xMinYMin', 'xMidYMin', 'xMaxYMin', 
		'xMinYMid', 'xMidYMid', 'xMaxYMid', 
		'xMinYMax', 'xMidYMax', 'xMaxYMax',)
	meetOrSliceEnum = ('meet', 'slice')
	alignDefault = 'xMidYMid'
	meetOrSliceDefault = 'meet'
	def __init__(self, node, attr, str, default=None):
		self._node = node
		self._attr = attr
		self._align = None
		self._meetOrSlice = None
		self._default = default
		if str:
			mo =  self.classre.match(str)
			if mo is not None:
				self._align = mo.group('align')
				self._meetOrSlice = mo.group('meetOrSlice')
				if self._align not in self.alignEnum:
					self._align = None
				if self._meetOrSlice not in self.meetOrSliceEnum:
					self._meetOrSlice = None

	def __repr__(self):
		s = ''
		if self._align is not None and self._align != self.alignDefault:
			s = s + self._align
		if self._meetOrSlice is not None and self._meetOrSlice != self.meetOrSliceDefault:
			s = s + ' ' + self._meetOrSlice
		return s

	def getValue(self):
		if self._align is None:
			align = self.alignDefault
		else:
			align = self._align
		if self._meetOrSlice is None:
			meetOrSlice = self.meetOrSliceDefault
		else:
			meetOrSlice = self._meetOrSlice
		return align, meetOrSlice

	def isDefault(self):
		return self._align is None or (self._align == self.alignDefault and (self._meetOrSlice is None or self._meetOrSlice=='meet'))

class SVGTransformList(SVGAttr):
	classre = re.compile(transformPat)
	classtransforms = ('matrix', 'translate', 'scale', 'rotate', 'skewX' , 'skewY',) 
	def __init__(self, node, attr, str, default=None):
		SVGAttr.__init__(self, node, attr, str, default)
		self._tflist = []
		self._default = default
		if not str:
			return 
		mo = SVGTransformList.classre.match(str)
		while mo is not None:
			str = str[mo.end(0):]
			arg = mo.group(2)[1:-1] # remove parens
			arg = splitlist(arg, ' ,')
			try:
				arg = map(string.atof, arg)
			except ValueError, arg:
				pass #print arg
			else:
				tfname = mo.group(1)
				if tfname in ('rotate', 'skewX', 'skewY'):
					arg = [(arg[0]/180.0)*math.pi,]
				self._tflist.append((tfname, arg))
			mo = self.classre.match(str)

	def __repr__(self):
		return ''

	def getValue(self):
		return self._tflist

	def isDefault(self):
		return self._tflist is None or len(self._tflist)==0

	#
	# Animateable interface
	#
	def getPresentValue(self, below = None):
		if not self.animators:
			return self.getValue()

		cv1 = self.getValue()[:]
		for a in self.animators:
			if below and id(a) == id(below):
				break
			if a.__class__.__name__ == 'MotionAnimator':
				if 1 or (a.isAdditive() and not a.isEffValueAnimator()):
					cv1 = cv1 + a.getCurrTransform()
				else:
					cv1 = a.getCurrTransform()

		cv2 = []
		for a in self.animators:
			if below and id(a) == id(below):
				break
			if a.__class__.__name__ != 'MotionAnimator':
				if a.isAdditive() and not a.isEffValueAnimator():
					cv2 = cv2 + a.getCurrTransform()
				else:
					cv2 = a.getCurrTransform()
		return cv1 + cv2

	# override this method to override distance
	# v1, and v2 are transform arguments
	def distValues(self, v1, v2):
		return math.fabs(v2-v1)


# SVG transformation matrix
# TM = [a, b, c, d, e, f]
# x = a*xu + c*yu + e
# y = b*xu + d*yu + f
# U: user coordinates
# V: viewport (or device) coordinates
# transform: ('matrix', 'translate', 'scale', 'rotate', 'skewX , 'skewY',) 
# reverse: [a b c d]^(-1) = [d -b -c  a]/det
# xu = ((+d)*x +(-c)*y + (c*f-d*e))/(a*d-b*c)
# yu = ((-b)*x +(+a)*y + (b*e-a*f))/(a*d-b*c)

class TM:
	identity = 1, 0, 0, 1, 0, 0
	def __init__(self, elements=None):
		if elements is not None:
			assert len(elements)==6, 'invalid argument'
			self.elements = elements[:]
		else:
			self.elements = TM.identity[:]
			
	def getElements(self):
		return self.elements
			
	def getTransform(self):
		return 'matrix', self.elements
			
	def __repr__(self):
		return '[' + '%s %s %s %s %s %s' % tuple(map(ff, self.elements)) + ']'
	
	# svg transforms
	def matrix(self, et):
		assert len(et)==6, 'invalid matrix transformation'
		a1, b1, c1, d1, e1, f1 = self.elements
		a2, b2, c2, d2, e2, f2 = et
		self.elements = a1*a2+c1*b2, b1*a2+d1*b2, a1*c2+c1*d2, b1*c2+d1*d2, a1*e2+c1*f2+e1, b1*e2+d1*f2+f1

	def translate(self, tt):
		assert len(tt)>0 and len(tt)<=2, 'invalid translate transformation'
		tx = tt[0]
		if len(tt)>1: ty = tt[1]
		else: ty = 0
		a, b, c, d, e, f = self.elements
		self.elements = a, b, c, d, e+a*tx+c*ty, f+b*tx+d*ty

	def scale(self, st):
		assert len(st)>0 and len(st)<=2, 'invalid scale transformation'
		sx = st[0]
		if len(st)>1: sy = st[1]
		else: sy = sx
		a, b, c, d, e, f = self.elements
		self.elements = a*sx, b*sx, c*sy, d*sy, e, f

	def rotate(self, at):
		r = at[0]
		a, b, c, d, e, f = self.elements
		sin, cos = math.sin(r), math.cos(r)
		self.elements = a*cos+c*sin, b*cos+d*sin, -a*sin+c*cos, -b*sin+d*cos, e, f

	def skewX(self, at):
		r = at[0]
		a, b, c, d, e, f = self.elements
		tan = math.tan(r)
		self.elements = a, b, c+a*tan, d+b*tan, e, f

	def skewY(self, at):
		r = at[0]
		a, b, c, d, e, f = self.elements
		tan = math.tan(r)
		self.elements = a+c*tan, b+d*tan, c, d, e, f
	
	def inverse(self):
		a, b, c, d, e, f = self.elements
		det = float(a*d - b*c)
		self.elements = d/det, -b/det, -c/det, a/det, (c*f-d*e)/det, (b*e-a*f)/det

	def apply(self, tf, arg):
		try:
			fo = getattr(self, tf)
			tm = fo(arg)
		except AttributeError, arg: 
			print 'invalid transform', `tf`
			print '(', arg, ')'

	def applyTfList(self, tflist):
		if not tflist: return
		for tf, arg in tflist:
			self.apply(tf, arg)
	
	# tm is a TM instance 
	def multiply(self, tm):
		self.matrix(tm.elements)

	# helpers
	def UPtoDP(self, point):
		a, b, c, d, e, f = self.elements
		xu, yu = point
		return a*xu + c*yu + e, b*xu + d*yu + f

	def URtoDR(self, rc):
		x, y = self.UPtoDP(rc[:2])
		w, h = self.UPtoDP(rc[2:])
		return x, y, w, h

	def UWtoDW(self, w):
		return self.UPtoDP((w, 0))[0]

	def UHtoDH(self, h):
		return self.UPtoDP((0, h))[1]

	def copy(self):
		return TM(self.elements)


########################################
stringtype = type('')
		
# entries: 
# attrname or element.attrname: (typeOrClass, defaultValue)

SVGAttrdefs = {'accent-height': (SVGHeight, None),
	'alignment-baseline': (stringtype, None),
	'alphabetic': (stringtype, None),
	'amplitude': (stringtype, None),
	'arabic-form': (stringtype, None),
	'ascent': (stringtype, None),
	'azimuth': (stringtype, None),
	'baseFrequency': (SVGFrequency, None),
	'baseline-shift': (stringtype, None),
	'bbox': (stringtype, None),
	'bias': (stringtype, None),
	'cap-height': (stringtype, None),
	'class': (stringtype, None),
	'clip': (stringtype, None),
	'clip-path': (stringtype, None),
	'clip-rule': (stringtype, None),
	'clipPathUnits': (stringtype, None),
	'color': (stringtype, None),
	'color-interpolation': (stringtype, None),
	'color-profile': (stringtype, None),
	'color-rendering': (stringtype, None),
	'contentScriptType': (stringtype, 'text/ecmascript'),
	'contentStyleType': (stringtype, 'text/css'),
	'cursor': (stringtype, None),
	'cx': (SVGCoordinate, 0),
	'cy': (SVGCoordinate, 0),
	'd': (SVGPath, None),
	'descent': (stringtype, None),
	'diffuseConstant': (stringtype, None),
	'direction': (stringtype, None),
	'display': (stringtype, None),
	'divisor': (stringtype, None),
	'dominant-baseline': (stringtype, None),
	'dx': (SVGCoordinate, None),
	'dy': (SVGCoordinate, None),
	'edgeMode': (stringtype, 'duplicate'),
	'elevation': (stringtype, None),
	'enable-background': (stringtype, None),
	'exponent': (stringtype, None),
	'externalResourcesRequired': (stringtype, None),
	'fill': (SVGColor, None),
	'fill-opacity': (stringtype, None),
	'fill-rule': (stringtype, None),
	'filter': (stringtype, None),
	'filterRes': (stringtype, None),
	'filterUnits': (stringtype, None),
	'flood-color': (stringtype, None),
	'flood-opacity': (stringtype, None),
	'font-family': (stringtype, None),
	'font-size': (SVGHeight, None),
	'font-size-adjust': (stringtype, None),
	'font-stretch': (stringtype, None),
	'font-style': (stringtype, None),
	'font-variant': (stringtype, None),
	'font-weight': (stringtype, None),
	'format': (stringtype, None),
	'fx': (stringtype, None),
	'fy': (stringtype, None),
	'g1': (stringtype, None),
	'g2': (stringtype, None),
	'glyph-name': (stringtype, None),
	'glyph-orientation-horizontal': (stringtype, None),
	'glyph-orientation-vertical': (stringtype, None),
	'glyphRef': (stringtype, None),
	'gradientTransform': (stringtype, None),
	'gradientUnits': (stringtype, None),
	'hanging': (stringtype, None),
	'height': (SVGHeight, None),
	'horiz-adv-x': (stringtype, None),
	'horiz-origin-x': (stringtype, None),
	'horiz-origin-y': (stringtype, None),
	'id': (XMLName, None),
	'ideographic': (stringtype, None),
	'image-rendering': (stringtype, None),
	'in': (stringtype, None),
	'in2': (stringtype, None),
	'intercept': (stringtype, None),
	'k': (stringtype, None),
	'k1': (stringtype, None),
	'k2': (stringtype, None),
	'k3': (stringtype, None),
	'k4': (stringtype, None),
	'kernelMatrix': (stringtype, None),
	'kernelUnitLength': (stringtype, None),
	'kerning': (stringtype, None),
	'lang': (stringtype, None),
	'lengthAdjust': (SVGLength, None),
	'letter-spacin': (stringtype, None),
	'lighting-color': (stringtype, None),
	'limitingConeAngle': (stringtype, None),
	'local': (stringtype, None),
	'marker-end': (stringtype, None),
	'marker-mid': (stringtype, None),
	'marker-start': (stringtype, None),
	'markerHeight': (stringtype, None),
	'markerUnits': (stringtype, None),
	'markerWidth': (stringtype, None),
	'mask': (stringtype, None),
	'maskContentUnits': (stringtype, None),
	'maskUnits': (stringtype, None),
	'mathematical': (stringtype, None),
	'media': (stringtype, None),
	'method': (stringtype, None),
	'mode': (stringtype, 'normal'),
	'name': (XMLName, None),
	'numOctaves': (stringtype, None),
	'offset': (stringtype, None),
	'opacity': (stringtype, None),
	'operator': (stringtype, 'erode'),
	'order': (stringtype, None),
	'orient': (stringtype, None),
	'orientation': (stringtype, None),
	'overflow': (stringtype, None),
	'overline-position': (stringtype, None),
	'overline-thickness': (stringtype, None),
	'panose-1': (stringtype, None),
	'pathLength': (SVGLength, None),
	'patternContentUnits': (stringtype, None),
	'patternTransform': (stringtype, None),
	'patternUnits': (stringtype, None),
	'pointer-events': (stringtype, None),
	'points': (SVGPoints, None),
	'pointsAtX': (stringtype, None),
	'pointsAtY': (stringtype, None),
	'pointsAtZ': (stringtype, None),
	'preserveAlpha': (stringtype, None),
	'preserveAspectRatio': (SVGAspectRatio, None),
	'primitiveUnits': (stringtype, None),
	'r': (SVGLength, None),
	'radius': (stringtype, None),
	'refX': (stringtype, None),
	'refY': (stringtype, None),
	'rendering-intent': (stringtype, 'auto'),
	'requiredExtensions': (stringtype, None),
	'requiredFeatures': (stringtype, None),
	'result': (stringtype, None),
	'rotate': (stringtype, None),
	'rx': (SVGLength, None),
	'ry': (SVGLength, None),
	'scale': (stringtype, None),
	'seed': (stringtype, None),
	'shape-rendering': (stringtype, None),
	'slope': (stringtype, None),
	'spacing': (stringtype, None),
	'specularConstant': (stringtype, None),
	'specularExponent': (stringtype, None),
	'spreadMethod': (stringtype, None),
	'startOffset': (stringtype, None),
	'stdDeviation': (stringtype, None),
	'stemh': (stringtype, None),
	'stemv': (stringtype, None),
	'stitchTiles': (stringtype, 'noStitch'),
	'stop-color': (stringtype, None),
	'stop-opacity': (stringtype, None),
	'strikethrough-position': (stringtype, None),
	'strikethrough-thickness': (stringtype, None),
	'stroke': (SVGColor, None),
	'stroke-dasharray': (stringtype, None),
	'stroke-dashoffset': (stringtype, None),
	'stroke-linecap': (stringtype, None),
	'stroke-linejoin': (stringtype, None),
	'stroke-miterlimit': (stringtype, None),
	'stroke-opacity': (stringtype, None),
	'stroke-width': (SVGWidth, None),
	'stroke-antialiasing':(stringtype, None),
	'style': (SVGStyle, None),
	'surfaceScale': (stringtype, None),
	'systemLanguage': (stringtype, None),
	'tableValues': (stringtype, None),
	'target': (stringtype, None),
	'targetX': (stringtype, None),
	'targetY': (stringtype, None),
	'text-anchor': (stringtype, None),
	'text-decoration': (stringtype, None),
	'text-rendering': (stringtype, None),
	'text-align': (stringtype, None),
	'text-antialiasing':(stringtype, None),
	'textLength': (SVGLength, None),
	'title': (stringtype, None),
	'transform': (SVGTransformList, None),
	'type': (stringtype, None),
	'u1': (stringtype, None),
	'u2': (stringtype, None),
	'underline-position': (stringtype, None),
	'underline-thickness': (stringtype, None),
	'unicode': (stringtype, None),
	'unicode-bidi': (stringtype, None),
	'unicode-range': (stringtype, None),
	'units-per-em': (stringtype, None),
	'v-alphabetic': (stringtype, None),
	'v-hanging': (stringtype, None),
	'v-ideographic': (stringtype, None),
	'v-mathematical': (stringtype, None),
	'values': (stringtype, None),
	'vert-adv-y': (stringtype, None),
	'vert-origin-x': (stringtype, None),
	'vert-origin-y': (stringtype, None),
	'viewBox': (SVGNumberList, None),
	'viewTarget': (stringtype, None),
	'visibility': (('hidden', 'visible'), None),
	'width': (SVGWidth, None),
	'widths': (stringtype, None),
	'word-spacing': (stringtype, None),
	'writing-mode': (stringtype, None),
	'x': (SVGCoordinate, 0),
	'x-height': (SVGHeight, None),
	'x1': (SVGCoordinate, 0),
	'x2': (SVGCoordinate, None),
	'xChannelSelector': (stringtype, 'A'),
	'xlink:actuate': (stringtype, 'onLoad'),
	'xlink:arcrole': (stringtype, None),
	'xlink:href': (stringtype, None),
	'xlink:role': (stringtype, None),
	'xlink:show': (stringtype, 'embed'),
	'xlink:title': (stringtype, None),
	'xlink:type': (stringtype, 'simple'),
	'xml:lang': (stringtype, None),
	'xml:space': (stringtype, None),
	'y': (SVGCoordinate, 0),
	'y1': (SVGCoordinate, 0),
	'y2': (SVGCoordinate, None),
	'yChannelSelector': (stringtype, 'A'),
	'z': (SVGCoordinate, 0),
	'zoomAndPan': (stringtype, 'magnify'),
	
	# time-animate elements
    'accumulate': (('sum', 'none'), 'none'),
	'additive': (('sum', 'replace'), 'replace'),
	'attributeName': (stringtype, None),
	'attributeType': (('CSS', 'XML', 'auto'), 'auto'),
	'begin': (SyncVariantList, None),
	'by': (stringtype, None),
	'calcMode': (('linear', 'paced', 'discrete', 'spline'), 'linear'),
	'animateMotion.calcMode': (('linear', 'paced', 'discrete', 'spline'), 'paced'),
	'dur': (SVGTime, None),
	'end': (SyncVariantList, None),
	'from': (stringtype, None),
	'keyPoints': (stringtype, None),
	'keySplines': (stringtype, None),
	'keyTimes': (stringtype, None),
	'max': (SVGTime, None),
	'min': (SVGTime, None),
	'origin': (('default',), 'default'),
	'path': (stringtype, None),
	'repeatCount': (SVGCount, None),
	'repeatDur': (SVGTime, None),
	'restart': (('always', 'whenNotActive', 'never', 'default'), 'always'),
	'rotate': (SVGAnimRotate, None),
	'to': (stringtype, None),
	'values': (stringtype, None),
	'animateTransform.type': (('translate', 'rotate', 'scale', 'skewX', 'skewY'), 'translate'),}

# add qualified fill smil attr
#smilfillenum = (('remove', 'freeze', 'hold', 'transition', 'auto', 'default'), 'remove')
svgfillenum = (('remove', 'freeze'), 'remove')
for tag in ('animate','set','animateMotion','animateColor','animateTransform',):
	qualifiedName = '%s.fill' % tag
	SVGAttrdefs[qualifiedName] = svgfillenum

def CreateSVGAttr(node, name, strval):
	tag = node.getType() 
	qualifiedName = '%s.%s' % (tag, name)
	info =  SVGAttrdefs.get(qualifiedName)
	if info is None:
		info = SVGAttrdefs.get(name)
	if info is None:
		print 'no spec for', name, strval
		return strval
	typeOrClassInfo, defval = info
	if typeOrClassInfo == stringtype:
		return strval
	elif type(typeOrClassInfo) == type(('',)):
		if strval is not None and strval not in typeOrClassInfo:
			strval = None
		return SVGEnum(node, name, strval, defval)
	try:
		return typeOrClassInfo(node, name, strval, defval)
	except:
		print 'CreateSVGAttr failed', name, strval, defval
		return strval

from svgdtd import SVG
def IsCSSAttr(name):
	return name in SVG.presentationAttrs.keys()
