__version__ = "$Id$"

# Module to handle various system attributes
import os
import windowinterface


# Defaults:
default_settings = {
	'system_bitrate' :				14400,	# Slow modem
	'system_captions' : 			0,		# Don't show captions
	'system_language' : 			'',		# No language preference
	'system_overdub_or_caption' :	'caption',
										# Captions preferred over overdub
	'system_screen_size' :			windowinterface.getscreensize(),
										# Size of screen
	'system_screen_depth':			windowinterface.getscreendepth(),
										# Depth of screen
	'system_required':				(),	# Needs special handling in match...
}

user_settings = {}

# Which of these should match exactly:
EXACT=['system_captions', 'system_language', 'system_overdub_or_captions']
ELEMENT=['system_required']
ALL=['system_bitrate', 'system_captions', 'system_language',
     'system_overdub_or_caption', 'system_screen_size',
     'system_screen_depth', 'system_required']

# Where is the preferences file:
if os.name == 'posix':
	PREFSFILENAME=os.environ['HOME']+'/.grins'
elif os.name == 'mac':
	PREFSFILENAME='Grins Preferences'
else:
	PREFSFILENAME='grprefs.txt'

def restore():
	global user_settings
	user_settings = {}
	if os.path.exists(PREFSFILENAME):
		execfile(PREFSFILENAME, user_settings)
		
restore()

def factory_defaults():
	global user_settings
	user_settings = {}
	
def get(name):
	real_value = None
	if user_settings.has_key(name):
		real_value = user_settings[name]
	if real_value is None:		
		try:
			real_value = default_settings[name]
		except KeyError:
			print 'Warning: unknown system attribute', name
			return 0
	return real_value

def match(name, wanted_value):
	real_value = get(name)
	if name in EXACT:
		return (real_value == wanted_value)
	elif name in ELEMENT:
		return (wanted_value in real_value)
	else:
		return (real_value >= wanted_value)

def getsettings():
	return ALL
	
def set(setting, value):
	user_settings[setting] = value
	
def save():
	try:
		fp = open(PREFSFILENAME, 'w')
	except IOError:
		return 0
	for name, value in user_settings.items():
		fp.write('%s = %s\n'%(name, `value`))
	fp.close()
	
	
