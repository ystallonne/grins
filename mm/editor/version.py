__version__ = "$Id$"
import sys
from patchlevel import patchlevel
import features
if features.lightweight:
	if sys.platform == 'mac':
		shortversion = 'grinslite-%s-1.5beta'%sys.platform
		version = 'Lite for RealSystem G2, v1.5beta ' + patchlevel
	else:
		shortversion = 'grinslite-%s-1.5'%sys.platform
		version = 'Lite for RealSystem G2, v1.5 ' + patchlevel
else:
	if sys.platform == 'mac':
		shortversion = 'grinspro-%s-1.5beta'%sys.platform
		version = 'Pro for RealSystem G2, v1.5beta ' + patchlevel
	else:
		shortversion = 'grinspro-%s-1.5'%sys.platform
		version = 'Pro for RealSystem G2, v1.5 ' + patchlevel
	
