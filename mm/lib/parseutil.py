import re, string
from xmllib import _opS

clock_val = (_opS +
	     r'(?:(?P<use_clock>'	# full/partial clock value
	     r'(?:(?P<hours>\d+):)?'		# hours: (optional)
	     r'(?P<minutes>[0-5][0-9]):'	# minutes:
	     r'(?P<seconds>[0-5][0-9])'      	# seconds
	     r'(?P<fraction>\.\d+)?'		# .fraction (optional)
	     r')|(?P<use_timecount>' # timecount value
	     r'(?P<timecount>\d+)'		# timecount
	     r'(?P<units>\.\d+)?'		# .fraction (optional)
	     r'(?P<metric>h|min|s|ms)?)'	# metric (optional)
	     r')' + _opS)
offsetvalue = re.compile('(?P<sign>[-+])?' + clock_val + '$')

error = 'parseutil.error'

def _syntax_error(msg):
	raise error, msg

def parsecounter(value, maybe_relative = 0, withsign = 0, syntax_error = _syntax_error, context = None):
	res = offsetvalue.match(value)
	if res:
		sign = res.group('sign')
		if sign and not withsign:
			if sign == '+':
				syntax_error('no sign allowed')
			else:
				raise error, 'no sign allowed'
			sign = None
		if sign and context is not None:
			if context.attributes.get('project_boston') == 0:
				import features
				syntax_error('sign not compatible with SMIL 1.0')
				if not features.editor:
					raise error, 'SMIL 2.0 presentation counter'
			context.attributes['project_boston'] = 1
		if res.group('use_clock'):
			h, m, s, f = res.group('hours', 'minutes',
					       'seconds', 'fraction')
			offset = 0
			if h is not None:
				offset = offset + string.atoi(h) * 3600
			m = string.atoi(m)
			if m >= 60:
				syntax_error('minutes out of range')
			s = string.atoi(s)
			if s >= 60:
				syntax_error('seconds out of range')
			offset = offset + m * 60 + s
			if f is not None:
				offset = offset + string.atof(f + '0')
		elif res.group('use_timecount'):
			tc, f, sc = res.group('timecount', 'units', 'metric')
			offset = string.atoi(tc)
			if f is not None:
				offset = offset + string.atof(f)
			if sc == 'h':
				offset = offset * 3600
			elif sc == 'min':
				offset = offset * 60
			elif sc == 'ms':
				offset = offset / 1000.0
			# else already in seconds
		else:
			raise error, 'internal error'
		if sign and sign == '-':
			offset = -offset
		return offset
	if maybe_relative:
		if value in ('begin', 'end'):
			return value
	raise error, 'not a clock value'