__version__ = "$Id$"

# Cache info about sound files

import MMurl
import urllib

# Used to get full info
def getfullinfo(url):
	url = MMurl.canonURL(url)
	url = urllib.unquote(url)
	import win32dxm
	duration = win32dxm.GetMediaDuration(url)
	if duration < 0:
		duration = 0
	bandwidth = 1
	markers = []
	return duration, bandwidth, markers

import FileCache
allinfo_cache = FileCache.FileCache(getfullinfo)

def get(url):
	nframes, framerate, markers = allinfo_cache.get(url)
	if nframes == 0: nframes = framerate
	duration = float(nframes) / framerate
	return duration

def getmarkers(url):
	nframes, framerate, markers = allinfo_cache.get(url)
	if not markers:
		return []
	xmarkers = []
	invrate = 1.0 / framerate
	for id, pos, name in markers:
		xmarkers.append((id, pos*invrate, name))
	return xmarkers
