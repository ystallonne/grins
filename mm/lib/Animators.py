__version__ = "$Id$"


import MMAttrdefs
import string

class Animator:
	def __init__(self, attr, domval, values, dur, mode='linear', times=None, splines=None):
		self._attr = attr
		self._domval = domval
		self._dur = dur
		self._values = values
		self._times = times
		self._splines = splines
		self._mode = mode

		# assertions
		if len(values)==0: raise AssertionError
		if len(values)==1:
			if mode != 'discrete': raise AssertionError
		if times:
			if len(times)!=len(values): raise AssertionError
		if splines and times:
			if len(splines) != len(times)-1: raise AssertionError

		# set calc mode
		if mode=='discrete': self._inrepol = self._discrete
		elif mode=='paced': self._inrepol = self._paced
		elif mode=='spline': self._inrepol = self._spline
		else: self._inrepol = self._linear

		# return value transformation (for example int())
		self._transf = None

		# construct boundaries of time intervals
		self._efftimes = []
		if not times:
			# create uniform intervals
			# for now assume also uniform intervals for 'paced' mode
			n = len(values)
			# for discrete mode n is the number of intervals
			if mode == 'discrete': n = n + 1
			if n <= 2:
				self._efftimes = [0, dur]
			else:
				tau = dur/float(n-1)
				t = 0.0
				for i in range(n):
					self._efftimes.append(t)
					t = t + tau
		else:
			# scale times to dur
			self._efftimes = []
			for p in times:
				self._efftimes.append(p*dur)	

	def getDOMValue(self):
		return self._domval

	def getAttrName(self):
		return self._attr

	def getValue(self, t):
		if t<0 or t>self._dur:
			return self._domval
		if self._dur == 0:
			return self._values[0]
		v = self._inrepol(t)
		if self._transf:
			return self._transf(v)
		return v

	# t in [0, dur]
	def _getinterval(self, t):
		tl = self._efftimes
		n = len(tl)
		for i in range(n-1):
			if t >= tl[i] and t < tl[i+1]:
				return i, (t - tl[i]) / (tl[i+1] - tl[i])
		# t == dur
		return n-2, 1.0

	def _discrete(self, t):
		n = len(self._values)
		if n==1: return self._values[0]
		ix, pdt = self._getinterval(t)
		return self._values[ix]

	def _linear(self, t):
		vl = self._values
		dur = self._dur
		n = len(vl)
		if t==dur:
			return vl[n-1]
		elif t==0 or n==1:
			return vl[0]
		ix, pdt = self._getinterval(t)
		return vl[ix] + (vl[ix+1]-vl[ix])*pdt

	def _paced(self, t):
		return self._linear(t) 

	def _spline(self, t):
		vl = self._values
		dur = self._dur
		el = self._splines
		n = len(vl)
		if n<2 or len(el)!=n-1:
			raise IndexError('values and splines missmatch')
		if t==dur: 
			return vl[len(vl)-1]
		elif t==0:
			return vl[0]
		ix, pdt = self._getinterval(t)
		return vl[ix] + (vl[ix+1]-vl[ix])*self.bezier(pdt, el[ix])

	# temporary parametric form
	def bezier(self, t, e = (0,0,1,1)):
		res = 20
		step = 1.0/float(res)
		s = 0.0
		for i in range(res+1):
			sc = 1.0-s
			b = 3.0*sc*sc*s
			c = 3.0*sc*s*s
			d = s*s*s
			tp = b*e[0] + c*e[2] + d
			if tp >= t: 
				return b*e[1] + c*e[3] + d
			s = s + step

	# return values transformations
	def _round(self, val):
		return int(val+0.5)


class ConstAnimator(Animator):
	def __init__(self, attr, domval, val, dur):
		Animator.__init__(self, attr, domval, (val,), dur, mode='discrete')


# SequenceAnimator can be used for example for 2D or 3D positions
class SequenceAnimator(Animator):	
	def __init__(self, attr, domval, values, dur, mode='linear', times=None, splines=None):
		Animator.__init__(self, attr, domval, values, dur, mode, times, splines)
		self.__animators = []
		# create an animator for each component
		# ...

	def getValue(self, t):
		if t<0 or t>self._dur:
			return self._domval
		if self._dur == 0:
			return self._values[0]
		n = len(self.__animators)
		l = []
		for anim in self.__animators:
			l.append(self.__animators.getValue(t))
		return tuple(l)


# Impl. rem:
# * on syntax error: we must ignore animation
# * we need an attr types map
# * use f(0) if duration is undefined
# * ignore keyTimes if dur indefinite


# Animation semantics parser
class AnimateElementParser:
	# args anim and target are MMNode objects
	# anim  represents the animate element node
	def __init__(self, anim, target):
		self.__anim = anim
		self.__target = target

		self.__attrname = ''
		self.__domval = None
		self.__enable = 0
		self.__grinsext = 0

		self.__hasValidTarget = self.__checkTarget()

		self.__additive = MMAttrdefs.getattr(self.__anim, 'additive')
		self.__calcMode = MMAttrdefs.getattr(self.__anim, 'calcMode')
		self.__accumulate = MMAttrdefs.getattr(self.__anim, 'accumulate')

	def getAnimator(self):
		if not self.__hasValidTarget:
			print 'invalid target syntax error'
			return None

		nvalues = self.__countInterpolationValues()
		if nvalues==0 or (nvalues==1 and mode!='discrete'):
			print 'values syntax error'
			return None

		attr = self.__attrname
		domval = self.__domval
		dur = self.getDuration()
		mode = self.__calcMode 
		times = self.__getInterpolationKeyTimes() 
		splines = self.__getInterpolationKeySplines()

		# src attribute animation
		if self.__attrname=='file':
			values = self.__getAlphaInterpolationValues()
			mode = 'discrete' # override calc mode
			return Animator(attr, domval, values, dur, mode, times, splines)
		
		## Begin temp grins extensions
		# position animation
		if self.__grinsext:
			values = self.__getNumInterpolationValues()
			anim = Animator(attr, domval, values, dur, mode, times, splines)
			anim._transf = anim._round # pixels
			return anim
		## End temp grins extensions

		return ConstAnimator(attr, domval, domval, dur)

	def getAttrName(self):
		return self.__attrname
							
	def getDuration(self):
		return MMAttrdefs.getattr(self.__anim, 'duration')

	def getFrom(self):
		return MMAttrdefs.getattr(self.__anim, 'from')

	def getTo(self):
		return MMAttrdefs.getattr(self.__anim, 'to')

	def getBy(self):
		return MMAttrdefs.getattr(self.__anim, 'by')

	def getValues(self):
		return MMAttrdefs.getattr(self.__anim, 'values')

	def getKeyTimes(self):
		return MMAttrdefs.getattr(self.__anim, 'keyTimes')

	def getKeySplines(self):
		return MMAttrdefs.getattr(self.__anim, 'keySplines')

	# check that we have a valid target
	def __checkTarget(self):
		self.__attrname = MMAttrdefs.getattr(self.__anim, 'attributeName')
		if not self.__attrname:
			print 'failed to get attributeName', self.__anim
			return 0

		self.__domval = MMAttrdefs.getattr(self.__target, self.__attrname)

		if not self.__domval:
			self.__checkExtensions()

		if not self.__domval:
			print 'Failed to get original DOM value for attr',self.__attrname,'from node',self.__target
			return 0
		return 1

	# return list of interpolation values
	def __getNumInterpolationValues(self):	
		# if 'values' are given ignore 'from/to/by'
		values =  self.getValues()
		if values:
			try:
				return tuple(map(string.atof, string.split(values,';')))
			except ValueError:
				return ()
		
		# 'from' is optional
		# use dom value if missing
		v1 = self.getFrom()
		if not v1:
			v1 = self.__domval
		if type(v1) == type(''): 
			v1 = string.atof(v1)

		# we must have a 'to' value (expl or through 'by')
		v2 = self.getTo()
		dv = self.getBy()
		if v2:
			v2 = string.atof(v2)
		elif dv:
			dv = string.atof(dv)
			v2 = v1 + dv
		else:
			return ()
		return v1, v2

	# return list of interpolation strings
	def __getAlphaInterpolationValues(self):
		
		# if values are given ignore from/to/by
		values =  self.getValues()
		if values:
			return string.split(values,';')
		
		# 'from' is optional
		# use dom value if missing
		v1 = self.getFrom()
		if not v1:
			v1 = self.__domval

		# we must have an expl 'to' value
		v2 = self.getTo()
		if not v2:
			return ()
		return v1, v2

	# len of interpolation list values
	# len == 0 is a syntax error
	# len == 1 and mode != 'discrete' is a syntax error
	def __countInterpolationValues(self):
		values =  self.getValues()
		if values:
			l = string.split(values,';')
			return len(l)

		n = 0
		v1 = self.getFrom()
		if v1: n = n + 1
		elif mode != 'discrete': n = n + 1

		v2 = self.getTo()
		dv = self.getBy()
		if v2 or dv: n = n + 1
		return n

	# return keyTimes or an empty list on failure
	def __getInterpolationKeyTimes(self):
		keyTimes = self.getKeyTimes()
		if not keyTimes: return ()
		tl = string.split(values,';')

		# len of values must be equal to len of keyTimes
		lvl = self.__countInterpolationValues()
		if mode=='discrete': lvl = lvl + 1
		if  lvl != len(tl):
			print 'values vs times mismatch'		 
			return ()
			
		tt = tuple(map(string.atof, tl))

		# check boundary constraints
		first = tt[0]
		last = tt[len(tt)-1]
		if self.__calcMode == 'linear' or self.__calcMode == 'spline':
			if first!=0.0 or last!=1.0: 
				print 'keyTimes range error'
				return ()
		elif self.__calcMode == 'discrete':
			if first!=0.0: 
				print 'not sero start keyTime'
				return ()
		elif self.__calcMode == 'paced':
			print 'ignoring keyTimes for paced mode'
			return ()
		
		# values should be increasing and in [0,1]
		if first>1.0 or first<0:return ()
		for i in  range(1,len(tt)):
			if tt[i] < tt[i-1]:
				print 'keyTimes order mismatch'
				return ()
			if tt[i]>1.0 or tt[i]<0:
				print 'keyTimes range error'
				return ()
		return tt

	# return keySplines or an empty list on failure
	def __getInterpolationKeySplines(self):
		if self.__calcMode != 'spline':
			print 'splines while not in spline calc mode'
			return []
		keySplines = self.getKeySplines()
		if not keySplines: return ()
		sl = string.split(values,';')
		
		# len of keySplines must be equal to num of intervals (=len(keyTimes)-1)
		tt = self.getInterpolationKeyTimes()
		if tt and len(sl) != len(tt)-1:
			print 'intervals vs splines mismatch'
			return []
		if not tt and len(sl) != 1:
			print 'intervals vs splines mismatch'
			return []

		rl = []
		for e in sl:
			try:
				x1, y1, x2, y2 = map(string.atof, string.split(e))
			except:
				print 'splines parsing error'
				return []
			if x1<0.0 or x1>1.0 or x2<0.0 or x2>1.0 or y1<0.0 or y1>1.0 or y2<0.0 or y2>1.0:
				print 'splines range error'
				return []
			rl.append((x1, y1, x2, y2))
		return rl


	# temp
	def __checkExtensions(self):
		d = self.__target.GetChannel().attrdict
		if not self.__domval and d.has_key('base_winoff'):
			# check for temp grins extensions
			self.__grinsext = 1
			base_winoff = d['base_winoff']
			if self.__attrname == 'region.left':
				self.__domval = base_winoff[0]
			elif self.__attrname == 'region.top':
				self.__domval = base_winoff[1]
			elif self.__attrname == 'region.width':
				self.__domval = base_winoff[2]
			elif self.__attrname == 'region.height':
				self.__domval = base_winoff[3]

	# temp
	def _dump(self):
		print '----------------------'
		print 'animate attr:', self.__attrname
		for name, value in self.__anim.attrdict.items():
			print name, '=', `value`
		print '----------------------'
		print 'target element',self.__target		
		for name, value in self.__target.attrdict.items():
			print name, '=', `value`
		print 'target element channel'		
		for name, value in self.__target.GetChannel().attrdict.items():
			print name, '=', `value`
		print '----------------------'







