#ifdef __sgi
#include <audio.h>
#endif
#ifdef sun
#include <multimedia/libaudio.h>
#endif
#include <stropts.h>
#include <poll.h>
#include "Python.h"
#include "modsupport.h"
#include "pythread.h"
#include "mmmodule.h"

#ifdef MM_DEBUG
static soundchannel_debug = 0;
#define dprintf(args)	(soundchannel_debug && printf args)
#else
#define dprintf(args)
#endif
#define denter(func)	dprintf(( # func "(%lx)\n", (long) self))
#define ERROR(func, errortype, msg)	{				\
		dprintf((# func "(%lx): " msg "\n", (long) self));	\
		PyErr_SetString(errortype, msg);			\
		}


struct sound_data {
	FILE *f;		/* file from which to read samples */
	PyObject *file;		/* file object from which f is gotten */
	int nchannels;		/* # of channels (mono or stereo) */
	int framesize;		/* size of frame in bytes */
	int nframes;		/* # of frames to play */
	int framerate;		/* sampling frequency */
	long offset;		/* offset in file of first sample */
	int bufsize;		/* size of sampbuf in frames */
	char *sampbuf;		/* buffer used for read/writing samples */
	int framesread;		/* # of frames in sampbuf */
#ifdef sun
	int ulaw;		/* convert to u-law */
#endif
};
struct sound {
	PyThread_type_sema s_sema;	/* semaphore to protect s_flag */
	int s_flag;
#ifdef __sgi
	ALport s_port;		/* audio port used for playing sound */
#endif
#ifdef sun
	int s_port;		/* file descriptor of audio device */
#endif
	double s_playrate;	/* speed with which to play samples */
	double s_queuesize;	/* queue size in seconds */
	struct sound_data s_play;
	struct sound_data s_arm;
	int s_pipefd[2];
};
/* values for s_flag */
#define PORT_OPEN	0x01
#define STOP		0x02
#define PAUSE		0x04

#define PRIV	((struct sound *) self->mm_private)

/*
 * module-global variables
 */
static int device_used;
static long old_rate, sound_rate;
static PyThread_type_sema device_sema;

static int
sound_init(self)
	mmobject *self;
{
	long buf[2];
	PyObject *v;

	denter(sound_init);
	self->mm_private = malloc(sizeof(struct sound));
	if (self->mm_private == NULL) {
		(void) PyErr_NoMemory();
		return 0;
	}
	PRIV->s_queuesize = 0;
	v = PyDict_GetItemString(self->mm_attrdict, "queuesize");
	if (v) {
		if (PyInt_Check(v))
			PRIV->s_queuesize = (double) PyInt_AsLong(v);
		else if (PyFloat_Check(v))
			PRIV->s_queuesize = PyFloat_AsDouble(v);
		else {
			ERROR(sound_init, PyExc_TypeError, "bad type for queusize");
			free(self->mm_private);
			self->mm_private = NULL;
			return 0;
		}
		if (PRIV->s_queuesize < 0) {
			ERROR(sound_init, PyExc_RuntimeError, "queusize can't be negative");
			free(self->mm_private);
			self->mm_private = NULL;
			return 0;
		}
	}
	PRIV->s_play.sampbuf = NULL;
	PRIV->s_arm.sampbuf = NULL;
	PRIV->s_arm.file = NULL;
	PRIV->s_play.file = NULL;
	PRIV->s_sema = PyThread_allocate_sema(1);
	if (PRIV->s_sema == NULL) {
		ERROR(sound_init, PyExc_RuntimeError, "cannot allocate semaphore");
		free(self->mm_private);
		self->mm_private = NULL;
		return 0;
	}
	PRIV->s_flag = 0;
	PRIV->s_port = NULL;
	if (pipe(PRIV->s_pipefd) < 0) {
		ERROR(sound_init, PyExc_RuntimeError, "cannot create pipe");
		PyThread_free_sema(PRIV->s_sema);
		free(self->mm_private);
		self->mm_private = NULL;
		return 0;
	}
	return 1;
}

static void
sound_dealloc(self)
	mmobject *self;
{
	long buf[2];

	denter(sound_dealloc);
	if (self->mm_private == NULL)
		return;
	if (PRIV->s_play.sampbuf)
		free(PRIV->s_play.sampbuf);
	if (PRIV->s_arm.sampbuf)
		free(PRIV->s_arm.sampbuf);
	Py_XDECREF(PRIV->s_arm.file);
	Py_XDECREF(PRIV->s_play.file);
	(void) close(PRIV->s_pipefd[0]);
	(void) close(PRIV->s_pipefd[1]);
	free(self->mm_private);
}

static int
sound_arm(self, file, delay, duration, attrlist, anchorlist)
	mmobject *self;
	PyObject *file;
	int delay, duration;
	PyObject *attrlist, *anchorlist;
{
	int length, value, i;
	char *name;
	PyObject *n, *v;

	denter(sound_arm);
	if (!PyDict_Check(attrlist)) {
		ERROR(sound_arm, PyExc_RuntimeError, "attributes not a dictionary");
		return 0;
	}
	PRIV->s_arm.nchannels = 1;
	PRIV->s_arm.framerate = 8000;
	PRIV->s_arm.framesize = 1;
	PRIV->s_arm.offset = 0;
	PRIV->s_playrate = 1.0;
#ifdef sun
	PRIV->s_arm.ulaw = 0;
#endif
	v = PyDict_GetItemString(attrlist, "nchannels");
	if (v && PyInt_Check(v))
		PRIV->s_arm.nchannels = PyInt_AsLong(v);
	v = PyDict_GetItemString(attrlist, "nsampframes");
	if (v && PyInt_Check(v))
		PRIV->s_arm.nframes = PyInt_AsLong(v) * PRIV->s_arm.nchannels;
	v = PyDict_GetItemString(attrlist, "sampwidth");
	if (v && PyInt_Check(v))
		PRIV->s_arm.framesize = PyInt_AsLong(v) * PRIV->s_arm.nchannels;
	v = PyDict_GetItemString(attrlist, "samprate");
	if (v && PyInt_Check(v))
		PRIV->s_arm.framerate = PyInt_AsLong(v);
	v = PyDict_GetItemString(attrlist, "offset");
	if (v && PyInt_Check(v))
		PRIV->s_arm.offset = PyInt_AsLong(v);
	Py_XDECREF(PRIV->s_arm.file);
	PRIV->s_arm.file = file;
	Py_INCREF(PRIV->s_arm.file);
	PRIV->s_arm.f = PyFile_AsFile(file);
	return 1;
}

static void
sound_armer(self)
	mmobject *self;
{
#ifdef __sgi
	int maxbufsize = PRIV->s_arm.nchannels == 1 ? 262139 : 131069;
#endif
	denter(sound_armer);

	if (PRIV->s_arm.sampbuf) {
		free(PRIV->s_arm.sampbuf);
		PRIV->s_arm.sampbuf = NULL;
	}
	PRIV->s_arm.bufsize = PRIV->s_arm.framerate;
	if (PRIV->s_queuesize > 0)
		PRIV->s_arm.bufsize *= PRIV->s_queuesize;
#ifdef __sgi
	if (PRIV->s_arm.bufsize > maxbufsize)
		PRIV->s_arm.bufsize = maxbufsize;
#endif
	if (PRIV->s_arm.bufsize > PRIV->s_arm.nframes)
		PRIV->s_arm.bufsize = PRIV->s_arm.nframes;
	PRIV->s_arm.sampbuf = malloc(PRIV->s_arm.bufsize*PRIV->s_arm.framesize);

	dprintf(("sound_armer(%lx): nchannels: %d, nframes: %d, nframes: %d, framesize: %d, framerate: %d, offset: %d, file: %lx (fd= %d), bufsize = %d\n",
		 (long) self,
		 PRIV->s_arm.nchannels, PRIV->s_arm.nframes,
		 PRIV->s_arm.nframes / PRIV->s_arm.nchannels,
		 PRIV->s_arm.framesize, PRIV->s_arm.framerate,
		 PRIV->s_arm.offset, PRIV->s_arm.f, fileno(PRIV->s_arm.f),
		 PRIV->s_arm.bufsize));

	fseek(PRIV->s_arm.f, PRIV->s_arm.offset, 0);
	PRIV->s_arm.framesread = fread(PRIV->s_arm.sampbuf, PRIV->s_arm.framesize, PRIV->s_arm.bufsize, PRIV->s_arm.f);
}

static int
sound_play(self)
	mmobject *self;
{
	denter(sound_play);
	PRIV->s_flag = 0;
	if (PRIV->s_play.sampbuf)
		free(PRIV->s_play.sampbuf);
	Py_XDECREF(PRIV->s_play.file);
	PRIV->s_play = PRIV->s_arm;
	PRIV->s_arm.sampbuf = NULL;
	PRIV->s_arm.file = NULL;
	return 1;
}

#ifdef sun
static unsigned
audio_get_filled(port)
	int port;
{
	unsigned val;
	audio_get_play_samples(port, &val);
	dprintf(("audio_get_play_samples: %d\n", val));
	return val;
}

static void
audio_set_eof(port, val)
	int port;
	unsigned val;
{
	audio_set_play_eof(port, &val);
}

static unsigned
audio_get_eof(port)
	int port;
{
	unsigned val;
	audio_get_play_eof(port, &val);
	return val;
}
#endif

static void
sound_player(self)
	mmobject *self;
{
#ifdef __sgi
	long buf[2];
	ALconfig config;
	int portfd;
#endif
#ifdef sun
	Audio_hdr hdr;
	Audio_info audio_info;
#endif
	int nframes = PRIV->s_play.nframes;
	int n;
	int rate;
	struct pollfd pollfd[2];
	int npollfd = 2;
	int timeout = -1;

	denter(sound_player);

	/* check for multiple active sound channels */
	(void) PyThread_down_sema(device_sema, WAIT_SEMA);
#ifdef __sgi
	if (device_used++ == 0) {
		/* first one to open the device */
		buf[0] = AL_OUTPUT_RATE;
		ALgetparams(AL_DEFAULT_DEVICE, buf, 2L);
		sound_rate = old_rate = buf[1];
	}
	if (sound_rate != PRIV->s_play.framerate) {
		if (device_used > 1)
			printf("Warning: two channels with different sampling rates active\n");
		buf[0] = AL_OUTPUT_RATE;
		buf[1] = PRIV->s_play.framerate;
		ALsetparams(AL_DEFAULT_DEVICE, buf, 2L);
		sound_rate = PRIV->s_play.framerate;
	}
#endif
#ifdef sun
	if (device_used > 1) {
		printf("Warning: only one active soundchannel at the time is supported\n");
		PyThread_up_sema(device_sema);
		return;
	}
	device_used++;
#endif
	PyThread_up_sema(device_sema);

	/* open an audio port */
	(void) PyThread_down_sema(PRIV->s_sema, WAIT_SEMA);
#ifdef __sgi
	config = ALnewconfig();
	ALsetwidth(config, PRIV->s_play.framesize / PRIV->s_play.nchannels);
	ALsetchannels(config, PRIV->s_play.nchannels);
	ALsetqueuesize(config, PRIV->s_play.bufsize);
	
	PRIV->s_port = ALopenport("sound channel", "w", config);
	portfd = ALgetfd(PRIV->s_port);
#endif
#ifdef sun
	PRIV->s_port = open("/dev/audio", 1);
	if (PRIV->s_port < 0) {
		printf("Warning: cannot open audio device\n");
		PyThread_up_sema(PRIV->s_sema);
		(void) PyThread_down_sema(device_sema, WAIT_SEMA);
		device_used--;
		PyThread_up_sema(device_sema);
		return;
	}
	hdr.sample_rate = PRIV->s_play.framerate;
	hdr.samples_per_unit = 1;
	hdr.bytes_per_unit = PRIV->s_play.framesize / PRIV->s_play.nchannels;
	hdr.channels = PRIV->s_play.nchannels;
	hdr.encoding = AUDIO_ENCODING_LINEAR;
	hdr.data_size = PRIV->s_play.nframes * PRIV->s_play.framesize;
	switch (audio_set_play_config(PRIV->s_port, &hdr)) {
	case AUDIO_SUCCESS:
		dprintf(("sound_player(%lx): audio_set_play_config successful\n", (long) self));
		break;
	case AUDIO_ERR_ENCODING:
	case AUDIO_ERR_NOEFFECT:
	default: {
		/* linear didn't work, assume default is u-law */
		int i;
		short *ps = (short *) PRIV->s_play.sampbuf;
		char *pc = PRIV->s_play.sampbuf;
		dprintf(("sound_player(%lx): audio_set_play_config unsuccessful\n", (long) self));
		dprintf(("sound_player(%lx): using u-law\n", (long) self));
		PRIV->s_play.ulaw = 1;
		break;
		}
	}
	audio_set_eof(PRIV->s_port, 0);
	audio_getinfo(PRIV->s_port, &audio_info);
	audio_info.play.buffer_size = PRIV->s_play.bufsize;
	audio_setinfo(PRIV->s_port, &audio_info);
#endif
	PRIV->s_flag |= PORT_OPEN;
	PyThread_up_sema(PRIV->s_sema);

	rate = 0;
	while (nframes > 0
#ifdef __sgi
	       || ALgetfilled(PRIV->s_port) > 0
#endif
#ifdef sun
	       || audio_get_eof(PRIV->s_port) == 0
#endif
	       ) {
		if (PRIV->s_play.framesread > 0) {
			n = PRIV->s_play.framesread;
			PRIV->s_play.framesread = 0;
		} else if (nframes > 0) {
			n = nframes;
			if (n > PRIV->s_play.bufsize)
				n = PRIV->s_play.bufsize;
			n = fread(PRIV->s_play.sampbuf, PRIV->s_play.framesize,
				  n, PRIV->s_play.f);
			if (n <= 0) {
				dprintf(("sound_player(%lx): fread returned %d at %ld (nframes = %d)\n", (long) self, n, ftell(PRIV->s_play.f), nframes));
				n = 0;
				nframes = 0;
			} else {
				dprintf(("sound_player(%lx): fread %d frames\n", (long) self, n));
			}
		} else
			n = 0;

#ifdef __sgi
		if (n == 0) {
#if 0
#ifdef _SYSTYPE_SVR4		/* IRIX 5.2 */
			/* there's a bug in the IRIX 5.2 implementation */
			/* of ALsetfillpoint, hence the division by 2 */
			if (PRIV->s_play.nchannels == 1)
				ALsetfillpoint(PRIV->s_port,
					       ALgetqueuesize(config) / 2);
			else
#endif
#endif
			ALsetfillpoint(PRIV->s_port, ALgetqueuesize(config));
		} else
			ALsetfillpoint(PRIV->s_port, n);
		pollfd[1].fd = portfd;
#endif
#ifdef sun
		if (n == 0) {
			npollfd = 1;
			timeout = 50;
		}
		pollfd[1].fd = PRIV->s_port;
#endif
		pollfd[1].events = POLLOUT;
		pollfd[1].revents = 0;
		pollfd[0].fd = PRIV->s_pipefd[0];
		pollfd[0].events = POLLIN;
		pollfd[0].revents = 0;
		dprintf(("sound_player(%lx): polling\n", (long) self));
		if (poll(pollfd, npollfd, timeout) < 0) {
			perror("poll");
			break;
		}
		dprintf(("sound_player(%lx): poll returned %x %x\n", (long) self, pollfd[0].revents, pollfd[1].revents));
		if (pollfd[0].revents & POLLIN) {
			char c;
			long filled;
			dprintf(("sound_player(%lx): reading from pipe\n", (long) self));
			(void) read(PRIV->s_pipefd[0], &c, 1);
			dprintf(("sound_player(%lx): read %c\n", (long) self, c));
			(void) PyThread_down_sema(PRIV->s_sema, WAIT_SEMA);
			if (c == 'p' || c == 'r') {
#ifdef __sgi
				filled = ALgetfilled(PRIV->s_port);
#endif
#ifdef sun
				audio_pause_play(PRIV->s_port);
#endif
			}
#ifdef __sgi
			ALcloseport(PRIV->s_port);
#endif
			if (c == 'p' || c == 'r') {
				fseek(PRIV->s_play.f, -(filled + n) * PRIV->s_play.framesize, 1);
				dprintf(("sound_player(%lx): filled = %ld, nframes before = %ld\n", (long) self, filled, nframes));
				nframes += filled;
			}
			if (c == 'p') {
				dprintf(("sound_player(%lx): waiting to continue\n", (long) self));
				PyThread_up_sema(PRIV->s_sema);
				(void) read(PRIV->s_pipefd[0], &c, 1);
				dprintf(("sound_player(%lx): continue playing, read %c\n", (long) self, c));
				(void) PyThread_down_sema(PRIV->s_sema,
							  WAIT_SEMA);
			}
			if (c == 'r') {
#ifdef __sgi
				PRIV->s_port = ALopenport("sound channel", "w",
							  config);
				portfd = ALgetfd(PRIV->s_port);
#endif
#ifdef sun
				audio_resume_play(PRIV->s_port);
#endif
				PyThread_up_sema(PRIV->s_sema);
				continue;
			} else {
				dprintf(("sound_player(%lx): stopping with playing\n", (long) self));
#ifdef sun
				audio_flush_play(PRIV->s_port);
#endif
				goto Py_Cleanup;
			}
		}
		if (pollfd[1].revents & (POLLERR|POLLHUP|POLLNVAL)) {
			dprintf(("sound_player(%lx): pollfd[1].revents=%x\n", (long) self, pollfd[1].revents));
			break;
		}
		if (n == 0)
			continue;
		nframes -= n;
#ifdef sun
		if (PRIV->s_play.ulaw) {
			int i;
			short *ps = (short *) PRIV->s_play.sampbuf;
			char *pc = PRIV->s_play.sampbuf;
			int factor = PRIV->s_play.framerate / 8000;
			if (factor == 0)
				factor = 1;
			if (PRIV->s_play.nchannels == 1)
				for (i = 0; i < n; i += factor, ps += factor)
					*pc++ = audio_s2u(*ps);
			else
				for (i = 0; i < n; i += factor, ps += PRIV->s_play.nchannels * factor)
					*pc++ = audio_s2u((ps[0] + ps[1]) / 2);
			n = pc - PRIV->s_play.sampbuf;
		}
#endif
		if (PRIV->s_playrate > 1) {
			int s = PRIV->s_play.bufsize / 30;
			char *p = PRIV->s_play.sampbuf;
			while (n > 0) {
				if (s > n)
					s = n;
				if (rate == 0) {
					dprintf(("sound_player(%lx): write %d frames\n", (long) self, s));
#ifdef __sgi
					ALwritesamps(PRIV->s_port, p, s);
#endif
#ifdef sun
					write(PRIV->s_port, p,
					      PRIV->s_play.ulaw ?
						s :
						s * PRIV->s_play.framesize);
#endif
				}
				rate++;
				if (rate >= PRIV->s_playrate)
					rate = 0;
				n -= s;
				p += s * PRIV->s_play.framesize;
			}
		} else {
			dprintf(("sound_player(%lx): write %d frames\n", (long) self, n));
#ifdef __sgi
			ALwritesamps(PRIV->s_port, PRIV->s_play.sampbuf, n * PRIV->s_play.nchannels);
#endif
#ifdef sun
			write(PRIV->s_port, PRIV->s_play.sampbuf,
			      PRIV->s_play.ulaw ? n : n * PRIV->s_play.framesize);
			if (nframes == 0)
				audio_play_eof(PRIV->s_port);
#endif
		}
	}
	(void) PyThread_down_sema(PRIV->s_sema, WAIT_SEMA);
#ifdef __sgi
	ALcloseport(PRIV->s_port);
#endif
#ifdef sun
	close(PRIV->s_port);
#endif
 Py_Cleanup:
	PRIV->s_port = NULL;
	PRIV->s_flag &= ~PORT_OPEN;
	PyThread_up_sema(PRIV->s_sema);
	(void) PyThread_down_sema(device_sema, WAIT_SEMA);
#ifdef __sgi
	if (--device_used == 0) {
		/* last one to close the audio port */
		buf[0] = AL_OUTPUT_RATE;
		buf[1] = old_rate;
		ALsetparams(AL_DEFAULT_DEVICE, buf, 2L);
	}
#endif
#ifdef sun
	device_used--;
#endif
	PyThread_up_sema(device_sema);
}

static int
sound_resized(self, x, y, w, h)
	mmobject *self;
	int x, y, w, h;
{
	denter(sound_resized);
	return 1;
}

static int
sound_armstop(self)
	mmobject *self;
{
	denter(sound_armstop);
	return 1;
}

static int
sound_playstop(self)
	mmobject *self;
{
	denter(sound_stop);
	(void) PyThread_down_sema(PRIV->s_sema, WAIT_SEMA);
	if (PRIV->s_flag & PORT_OPEN) {
		PRIV->s_flag |= STOP;
		(void) write(PRIV->s_pipefd[1], "s", 1);
	}
	PyThread_up_sema(PRIV->s_sema);
	return 1;
}

static int
sound_finished(self)
	mmobject *self;
{
	denter(sound_finished);
	return 1;
}

static int
sound_setrate(self, rate)
	mmobject *self;
	double rate;
{
	char msg;

	dprintf(("sound_setrate(%lx,%g)\n", (long) self, rate));
	(void) PyThread_down_sema(PRIV->s_sema, WAIT_SEMA);
	if (rate == 0) {
		PRIV->s_flag |= PAUSE;
		msg = 'p';
	} else {
		PRIV->s_flag &= ~PAUSE;
		msg = 'r';
		PRIV->s_playrate = rate;
	}
	/* it can happen that the channel has already been stopped but the */
	/* player thread hasn't reacted yet.  Hence the check on STOPPLAY. */
	if ((self->mm_flags & (PLAYING | STOPPLAY)) == PLAYING) {
		dprintf(("sound_setrate(%lx): writing %c\n", (long) self, msg));
		(void) write(PRIV->s_pipefd[1], &msg, 1);
	}
	PyThread_up_sema(PRIV->s_sema);
	return 1;
}

static struct mmfuncs sound_channel_funcs = {
	sound_armer,
	sound_player,
	sound_resized,
	sound_arm,
	sound_armstop,
	sound_play,
	sound_playstop,
	sound_finished,
	sound_setrate,
	sound_init,
	sound_dealloc,
};

static channelobject *sound_chan_obj;

static void
soundchannel_dealloc(self)
	channelobject *self;
{
	dprintf(("soundchannel_dealloc: called\n"));
	if (self != sound_chan_obj) {
		dprintf(("soundchannel_dealloc: arg != sound_chan_obj\n"));
	}
	PyMem_DEL(self);
	sound_chan_obj = NULL;
}

static PyObject *
soundchannel_getattr(self, name)
	channelobject *self;
	char *name;
{
	PyErr_SetString(PyExc_AttributeError, name);
	return NULL;
}

static PyTypeObject Soundchanneltype = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,			/*ob_size*/
	"channel:sound",	/*tp_name*/
	sizeof(channelobject),	/*tp_size*/
	0,			/*tp_itemsize*/
	/* methods */
	(destructor)soundchannel_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	(getattrfunc)soundchannel_getattr, /*tp_getattr*/
	0,			/*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
};

static PyObject *
soundchannel_init(self, args)
	channelobject *self;
	PyObject *args;
{
	channelobject *p;

	if (!PyArg_NoArgs(args))
		return NULL;
	if (sound_chan_obj == 0) {
		dprintf(("soundchannel_init: creating new object\n"));
		sound_chan_obj = PyObject_NEW(channelobject, &Soundchanneltype);
		if (sound_chan_obj == NULL)
			return NULL;
		sound_chan_obj->chan_funcs = &sound_channel_funcs;
	} else {
		dprintf(("soundchannel_init: return old object\n"));
		Py_INCREF(sound_chan_obj);
	}

	return (PyObject *) sound_chan_obj;
}

static PyMethodDef soundchannel_methods[] = {
	{"init",		(PyCFunction)soundchannel_init},
	{NULL,			NULL}
};

void
initsoundchannel()
{
#ifdef MM_DEBUG
	soundchannel_debug = getenv("SOUNDDEBUG") != 0;
#endif
	dprintf(("initsoundchannel\n"));
	(void) Py_InitModule("soundchannel", soundchannel_methods);
	device_sema = PyThread_allocate_sema(1);
	if (device_sema == NULL)
		Py_FatalError("soundchannelmodule: can't allocate semaphore");
}
