__version__ = "$Id$"

try:
	import Qt
except ImportError:
	Qt = None

import winqtcon

import ddraw

# support flags
qtenvironment = None
initialized = 0
refcount = 0 

# Qt should be initialized once per session (application instance)
# Here is referenced counted and thus can be called per use 
# (remember to call Terminate() per use if used this way)
def Initialize(incrref = 1):
	global initialized
	global refcount
	if initialized:
		if incrref:
			refcount = refcount + 1
		return 1
	if Qt is None:
		return 0
	try:
		Qt.InitializeQTML()
	except:
		return 0	
	Qt.EnterMovies()
	initialized = 1
	if incrref:
		refcount = refcount + 1
	return 1

# Qt session terminate (application exit instance)
def Terminate():
	global initialized
	global refcount
	if initialized:		
		refcount = refcount - 1
		if refcount == 0:
			Qt.ExitMovies()
			Qt.TerminateQTML()
			initialized = 0

# module level Qt lifetime
# keep alive Qt for module lifetime
class QtEnvironment:
	def __init__(self):
		Initialize()
	def __del__(self):
		global qtenvironment
		qtenvironment = None
		Terminate()

# pay (a delay) for Qt initializarion only if used
def HasQtSupport():
	global qtenvironment
	if qtenvironment is not None:
		return 1
	if Qt is not None and Initialize(incrref = 0):
		qtenvironment = QtEnvironment()
		return 1
	return 0

# avoid overhead of setting DD on each update when not needed
QtPlayerInstances = 0

class QtPlayer:
	def __init__(self):
		Initialize()
		self._movie = None
		self._videomedia = None
		self._videotrack = None
		self._audiomedia = None
		self._audiotrack = None
		self._ddobj = None
		self._dds = None
		self._rect = None
		global QtPlayerInstances
		QtPlayerInstances = QtPlayerInstances + 1

	def __del__(self):
		self._videomedia = None
		self._videotrack = None
		self._audiomedia = None
		self._audiotrack = None
		self._movie = None
		self._movie = None
		self._dds = None
		self._ddobj = None
		self._rect = None
		Terminate()
		global QtPlayerInstances
		QtPlayerInstances = QtPlayerInstances - 1

	def __repr__(self):
		s = '<%s instance' % self.__class__.__name__
		s = s + '>'
		return s

	def open(self, url, exporter = None, asaudio = 0):
		try:
			movieResRef = Qt.OpenMovieFileWin(url, 1)
		except Exception, arg:
			print arg
			return 0
		try:
			self._movie, d1, d2 = Qt.NewMovieFromFile(movieResRef, 0, 0)
		except Exception, arg:
			print arg
			Qt.CloseMovieFile(movieResRef)
			return 0
		Qt.CloseMovieFile(movieResRef)
		if not asaudio:
			l, t, r, b = self._movie.GetMovieBox()
			self._rect = l, t, r-l, b-t
		return 1

	def getMovieRect(self):
		return self._rect

	def getCurrentMovieRect(self):
		if self._movie:
			l, t, r, b = self._movie.GetMovieBox()
			return l, t, r-l, b-t
		return 0, 0

	def setMovieRect(self, rect):
		x, y, w, h = self._rect = rect
		if self._movie:
			self._movie.SetMovieBox((x, y, x+w, y+h))

	def setMovieActive(self, flag):
		if self._movie:
			self._movie.SetMovieActive(flag)


	def getVideoTracksInfo(self):
		if not self._movie or (self._videotrack and self._videomedia): 
			return
		try:
			self._videotrack = self._movie.GetMovieIndTrackType(1, winqtcon.VisualMediaCharacteristic, winqtcon.movieTrackCharacteristic)
			self._videomedia = self._videotrack.GetTrackMedia()
		except Qt.Error, arg:
			print 'getVideoTracksInfo', msg
			self._videomedia = None
			self._videotrack = None
	
	def getAudioTracksInfo(self):
		if not self._movie or (self._audiotrack and self._audiomedia): 
			return
		try:
			self._audiotrack = self._movie.GetMovieIndTrackType(1, winqtcon.AudioMediaCharacteristic, winqtcon.movieTrackCharacteristic)
			self._audiomedia = self._audiotrack.GetTrackMedia()
		except Qt.Error, arg:
			print 'getAudioTracksInfo', msg
			self._audiomedia = None
			self._audiotrack = None
		
	def getFrameRate(self):
		magic_frame_rate = 20
		if not self._movie: 
			return magic_frame_rate
		dur = self.getDuration()
		if not dur: 
			return magic_frame_rate
		self.getVideoTracksInfo()
		if self._videomedia:
			samples = self._videomedia.GetMediaSampleCount()
			import math
			return int(math.floor(samples/dur))
		return magic_frame_rate

	def createVideoDDS(self, ddobj, size = None):
		if self._rect is None:
			return
		if size is not None:
			w, h = size
		else:
			w, h = self._rect[2:]

		if ddobj is None:
			intefacePtr = Qt.GetDDObject()
			if intefacePtr:
				ddobj = ddraw.CreateDirectDrawWrapper(intefacePtr)
							
		if ddobj:
			self._ddobj = ddobj
			ddsd = ddraw.CreateDDSURFACEDESC()
			ddsd.SetFlags(ddraw.DDSD_WIDTH | ddraw.DDSD_HEIGHT | ddraw.DDSD_CAPS)
			ddsd.SetCaps(ddraw.DDSCAPS_OFFSCREENPLAIN)
			ddsd.SetSize(w, h)
			self._dds = ddobj.CreateSurface(ddsd)
			Qt.SetDDObject(self._ddobj)
			Qt.SetDDPrimarySurface(self._dds)

		self._movie.SetMovieBox((0, 0, w, h))
		self._movie.SetMovieActive(1)
			
	def run(self):
		if self._movie:
			self._movie.StartMovie()

	def stop(self):
		if self._movie:
			self._movie.StopMovie()
		
	def update(self):
		if self._movie:
			global QtPlayerInstances
			if self._dds is not None and QtPlayerInstances>1:
				Qt.SetDDObject(self._ddobj)
				Qt.SetDDPrimarySurface(self._dds)
			self._movie.MoviesTask(0)
			self._movie.UpdateMovie()
			return not self._movie.IsMovieDone()
		return 0

	def seek(self, secs):
		if self._movie:
			msecs = int(1000*secs)
			self._movie.SetMovieTimeValue(msecs)

	def getDuration(self):
		if self._movie:
			return 0.001*self._movie.GetMovieDuration()
		return 0

	def getTime(self):
		if self._movie:
			msecs = self._movie.GetMovieTime()[0]
			return msecs/1000.0
		return 0

	def getDataAsRGB24(self):
		if self._dds is not None:
			return self._dds.GetDataAsRGB24()
		return None

	def hasVideo(self):
		self.getVideoTracksInfo()
		return self._videomedia is not None

	def hasAudio(self):
		self.getAudioTracksInfo()
		return self._audiomedia is not None

	def openForEncoding(self, filename, ddobj):
		if not self.open(filename):
			return None
		self.createVideoDDS(ddobj)
		self.getVideoTracksInfo()
		if self._videomedia is None:
			return None
		#self.getAudioTracksInfo()
		framerate = self.getFrameRate()
		width, height = self.getMovieRect()[2:]
		self._movie.SetMoviePlayHints(winqtcon.hintsHighQuality, winqtcon.hintsHighQuality)
		self._movie.SetMovieTimeValue(0)
		self._movie.SetMovieActive(1)
		self._movie.MoviesTask(0)
		self._movie.UpdateMovie()
		return width, height, framerate

	def nextVideoData(self, sampletime):
		if sampletime is None: sampletime = 0
		flags = winqtcon.nextTimeMediaSample | winqtcon.nextTimeStep    
		sampletime, dur = self._videomedia.GetMediaNextInterestingTime(flags, sampletime, 1.0)
		self._movie.SetMovieTimeValue(sampletime)
		self._movie.MoviesTask(0)
		self._movie.UpdateMovie()
		return sampletime
