#include "Std.h"
#include "PyCppApi.h"
#include "mtpycall.h"

// consts
#include "StdRma.h"

static char moduleName[] = "rma";
static char errorName[] =  "rma error";
PyObject *module_error;

#ifdef _WIN32
PyInterpreterState* PyCallbackBlock::s_interpreterState;
#endif

// Objects served by this module
extern PyObject* EngineObject_CreateInstance(PyObject *self, PyObject *args);

struct error {
	PN_RESULT res;
	char *name;
} errorlist [] = {
	{PNR_NOTIMPL, "PNR_NOTIMPL"},
	{PNR_OUTOFMEMORY,"PNR_OUTOFMEMORY"},
	{PNR_INVALID_PARAMETER,"PNR_INVALID_PARAMETER"},
	{PNR_NOINTERFACE,"PNR_NOINTERFACE"},
	{PNR_POINTER ,"PNR_POINTER"},
	{PNR_HANDLE,"PNR_HANDLE"},
	{PNR_ABORT,"PNR_ABORT"},
	{PNR_FAIL ,"PNR_FAIL"},
	{PNR_ACCESSDENIED,"PNR_ACCESSDENIED"},
	{PNR_OK,"PNR_OK"},

	{PNR_INVALID_OPERATION,"PNR_INVALID_OPERATION"},
	{PNR_INVALID_VERSION,"PNR_INVALID_VERSION"},
	{PNR_INVALID_REVISION,"PNR_INVALID_REVISION"},
	{PNR_NOT_INITIALIZED,"PNR_NOT_INITIALIZED"},
	{PNR_DOC_MISSING,"PNR_DOC_MISSING"},
	{PNR_UNEXPECTED ,"PNR_UNEXPECTED"},
	{PNR_NO_FILEFORMAT,"PNR_NO_FILEFORMAT"},
	{PNR_NO_RENDERER,"PNR_NO_RENDERER"},
	{PNR_INCOMPLETE,"PNR_INCOMPLETE"},
	{PNR_BUFFERTOOSMALL,"PNR_BUFFERTOOSMALL"},
	{PNR_UNSUPPORTED_VIDEO,"PNR_UNSUPPORTED_VIDEO"},
	{PNR_UNSUPPORTED_AUDIO,"PNR_UNSUPPORTED_AUDIO"},
	{PNR_INVALID_BANDWIDTH,"PNR_INVALID_BANDWIDTH"},
	{PNR_MISSING_COMPONENTS,"PNR_MISSING_COMPONENTS"},
	{PNR_ELEMENT_NOT_FOUND,"PNR_ELEMENT_NOT_FOUND"},
	{PNR_NOCLASS,"PNR_NOCLASS"},
	{PNR_CLASS_NOAGGREGATION,"PNR_CLASS_NOAGGREGATION"},
	{PNR_NOT_LICENSED,"PNR_NOT_LICENSED"},
	{PNR_NO_FILESYSTEM,"PNR_NO_FILESYSTEM"},

	{PNR_BUFFERING,"PNR_BUFFERING"},
	{PNR_PAUSED,"PNR_PAUSED"},
	{PNR_NO_DATA,"PNR_NO_DATA"},
	{PNR_STREAM_DONE,"PNR_STREAM_DONE"},
	{PNR_NET_SOCKET_INVALID,"PNR_NET_SOCKET_INVALID"},
	{PNR_NET_CONNECT,"PNR_NET_CONNECT"},
	{PNR_BIND,"PNR_BIND"},
	{PNR_SOCKET_CREATE,"PNR_SOCKET_CREATE"},
	{PNR_INVALID_HOST,"PNR_INVALID_HOST"},
	{PNR_NET_READ,"PNR_NET_READ"},
	{PNR_NET_WRITE,"PNR_NET_WRITE"},
	{PNR_NET_UDP,"PNR_NET_UDP"},
	{PNR_RETRY,"PNR_RETRY"},
	{PNR_SERVER_TIMEOUT,"PNR_SERVER_TIMEOUT"},
	{PNR_SERVER_DISCONNECTED,"PNR_SERVER_DISCONNECTED"},
	{PNR_WOULD_BLOCK,"PNR_WOULD_BLOCK"},
	{PNR_GENERAL_NONET,"PNR_GENERAL_NONET"},
	{PNR_BLOCK_CANCELED,"PNR_BLOCK_CANCELED"},
	{PNR_MULTICAST_JOIN,"PNR_MULTICAST_JOIN"},
	{PNR_GENERAL_MULTICAST,"PNR_GENERAL_MULTICAST"},
	{PNR_MULTICAST_UDP,"PNR_MULTICAST_UDP"},
	{PNR_AT_INTERRUPT,"PNR_AT_INTERRUPT"},
	{PNR_MSG_TOOLARGE,"PNR_MSG_TOOLARGE"},
	{PNR_NET_TCP,"PNR_NET_TCP"},
	{PNR_TRY_AUTOCONFIG,"PNR_TRY_AUTOCONFIG"},
	{PNR_NOTENOUGH_BANDWIDTH,"PNR_NOTENOUGH_BANDWIDTH"},
	{PNR_HTTP_CONNECT,"PNR_HTTP_CONNECT"},
	{PNR_PORT_IN_USE,"PNR_PORT_IN_USE"},

	{PNR_AT_END,"PNR_AT_END"},
	{PNR_INVALID_FILE,"PNR_INVALID_FILE"},
	{PNR_INVALID_PATH,"PNR_INVALID_PATH"},
	{PNR_RECORD,"PNR_RECORD"},
	{PNR_RECORD_WRITE,"PNR_RECORD_WRITE"},
	{PNR_TEMP_FILE,"PNR_TEMP_FILE"},
	{PNR_ALREADY_OPEN,"PNR_ALREADY_OPEN"},
	{PNR_SEEK_PENDING,"PNR_SEEK_PENDING"},
	{PNR_CANCELLED,"PNR_CANCELLED"},
	{PNR_FILE_NOT_FOUND,"PNR_FILE_NOT_FOUND"},
	{PNR_WRITE_ERROR,"PNR_WRITE_ERROR"},
	{PNR_FILE_EXISTS,"PNR_FILE_EXISTS"},
	{PNR_FILE_NOT_OPEN,"PNR_FILE_NOT_OPEN"},
	{PNR_ADVISE_PREFER_LINEAR,"PNR_ADVISE_PREFER_LINEAR"},
	{PNR_PARSE_ERROR,"PNR_PARSE_ERROR"},

	{PNR_BAD_SERVER,"PNR_BAD_SERVER"},
	{PNR_ADVANCED_SERVER,"PNR_ADVANCED_SERVER"},
	{PNR_OLD_SERVER,"PNR_OLD_SERVER"},
	{PNR_REDIRECTION,"PNR_REDIRECTION"},
	{PNR_SERVER_ALERT,"PNR_SERVER_ALERT"},
	{PNR_PROXY,"PNR_PROXY"},
	{PNR_PROXY_RESPONSE,"PNR_PROXY_RESPONSE"},
	{PNR_ADVANCED_PROXY,"PNR_ADVANCED_PROXY"},
	{PNR_OLD_PROXY,"PNR_OLD_PROXY"},
	{PNR_INVALID_PROTOCOL,"PNR_INVALID_PROTOCOL"},
	{PNR_INVALID_URL_OPTION,"PNR_INVALID_URL_OPTION"},
	{PNR_INVALID_URL_HOST,"PNR_INVALID_URL_HOST"},
	{PNR_INVALID_URL_PATH,"PNR_INVALID_URL_PATH"},
	{PNR_HTTP_CONTENT_NOT_FOUND,"PNR_HTTP_CONTENT_NOT_FOUND"},
	{PNR_NOT_AUTHORIZED ,"PNR_NOT_AUTHORIZED"},
	{PNR_UNEXPECTED_MSG,"PNR_UNEXPECTED_MSG"},
	{PNR_BAD_TRANSPORT,"PNR_BAD_TRANSPORT"},
	{PNR_NO_SESSION_ID,"PNR_NO_SESSION_ID"},
	{PNR_PROXY_DNR,"PNR_PROXY_DNR"},
	{PNR_PROXY_NET_CONNECT,"PNR_PROXY_NET_CONNECT"},

	{PNR_AUDIO_DRIVER,"PNR_AUDIO_DRIVER"},
	{PNR_LATE_PACKET,"PNR_LATE_PACKET"},
	{PNR_OVERLAPPED_PACKET,"PNR_OVERLAPPED_PACKET"},
	{PNR_OUTOFORDER_PACKET,"PNR_OUTOFORDER_PACKET"},
	{PNR_NONCONTIGUOUS_PACKET,"PNR_NONCONTIGUOUS_PACKET"},

	{PNR_OPEN_NOT_PROCESSED,"PNR_OPEN_NOT_PROCESSED"},

	{PNR_EXPIRED,"PNR_EXPIRED"},

	{PNR_INVALID_INTERLEAVER,"PNR_INVALID_INTERLEAVER"},
	{PNR_BAD_FORMAT,"PNR_BAD_FORMAT"},
	{PNR_CHUNK_MISSING,"PNR_CHUNK_MISSING"},
	{PNR_INVALID_STREAM,"PNR_INVALID_STREAM"},
	{PNR_DNR,"PNR_DNR"},
	{PNR_OPEN_DRIVER,"PNR_OPEN_DRIVER"},
	{PNR_UPGRADE ,"PNR_UPGRADE"},
	{PNR_NOTIFICATION,"PNR_NOTIFICATION"},
	{PNR_NOT_NOTIFIED,"PNR_NOT_NOTIFIED"},
	{PNR_STOPPED,"PNR_STOPPED"},
	{PNR_CLOSED,"PNR_CLOSED"},
	{PNR_INVALID_WAV_FILE,"PNR_INVALID_WAV_FILE"},
	{PNR_NO_SEEK,"PNR_NO_SEEK"},

	{PNR_DEC_INITED,"PNR_DEC_INITED"},
	{PNR_DEC_NOT_FOUND,"PNR_DEC_NOT_FOUND"},
	{PNR_DEC_INVALID,"PNR_DEC_INVALID"},
	{PNR_DEC_TYPE_MISMATCH,"PNR_DEC_TYPE_MISMATCH"},
	{PNR_DEC_INIT_FAILED,"PNR_DEC_INIT_FAILED"},
	{PNR_DEC_NOT_INITED,"PNR_DEC_NOT_INITED"},
	{PNR_DEC_DECOMPRESS,"PNR_DEC_DECOMPRESS"},
	{PNR_OBSOLETE_VERSION,"PNR_OBSOLETE_VERSION"},

	{PNR_ENC_FILE_TOO_SMALL,"PNR_ENC_FILE_TOO_SMALL"},
	{PNR_ENC_UNKNOWN_FILE,"PNR_ENC_UNKNOWN_FILE"},
	{PNR_ENC_BAD_CHANNELS,"PNR_ENC_BAD_CHANNELS"},
	{PNR_ENC_BAD_SAMPSIZE,"PNR_ENC_BAD_SAMPSIZE"},
	{PNR_ENC_BAD_SAMPRATE,"PNR_ENC_BAD_SAMPRATE"},
	{PNR_ENC_INVALID,"PNR_ENC_INVALID"},
	{PNR_ENC_NO_OUTPUT_FILE,"PNR_ENC_NO_OUTPUT_FILE"},
	{PNR_ENC_NO_INPUT_FILE,"PNR_ENC_NO_INPUT_FILE"},
	{PNR_ENC_NO_OUTPUT_PERMISSIONS,"PNR_ENC_NO_OUTPUT_PERMISSIONS"},
	{PNR_ENC_BAD_FILETYPE,"PNR_ENC_BAD_FILETYPE"},
	{PNR_ENC_INVALID_VIDEO,"PNR_ENC_INVALID_VIDEO"},
	{PNR_ENC_INVALID_AUDIO,"PNR_ENC_INVALID_AUDIO"},
	{PNR_ENC_NO_VIDEO_CAPTURE,"PNR_ENC_NO_VIDEO_CAPTURE"},
	{PNR_ENC_INVALID_VIDEO_CAPTURE,"PNR_ENC_INVALID_VIDEO_CAPTURE"},
	{PNR_ENC_NO_AUDIO_CAPTURE,"PNR_ENC_NO_AUDIO_CAPTURE"},
	{PNR_ENC_INVALID_AUDIO_CAPTURE,"PNR_ENC_INVALID_AUDIO_CAPTURE"},
	{PNR_ENC_TOO_SLOW_FOR_LIVE,"PNR_ENC_TOO_SLOW_FOR_LIVE"},
	{PNR_ENC_ENGINE_NOT_INITIALIZED,"PNR_ENC_ENGINE_NOT_INITIALIZED"},
	{PNR_ENC_CODEC_NOT_FOUND,"PNR_ENC_CODEC_NOT_FOUND"},
	{PNR_ENC_CODEC_NOT_INITIALIZED,"PNR_ENC_CODEC_NOT_INITIALIZED"},
	{PNR_ENC_INVALID_INPUT_DIMENSIONS,"PNR_ENC_INVALID_INPUT_DIMENSIONS"},
	{PNR_ENC_MESSAGE_IGNORED,"PNR_ENC_MESSAGE_IGNORED"},
	{PNR_ENC_NO_SETTINGS,"PNR_ENC_NO_SETTINGS"},
	{PNR_ENC_NO_OUTPUT_TYPES,"PNR_ENC_NO_OUTPUT_TYPES"},
	{PNR_ENC_IMPROPER_STATE,"PNR_ENC_IMPROPER_STATE"},
	{PNR_ENC_INVALID_SERVER,"PNR_ENC_INVALID_SERVER"},
	{PNR_ENC_INVALID_TEMP_PATH,"PNR_ENC_INVALID_TEMP_PATH"},
	{PNR_ENC_MERGE_FAIL,"PNR_ENC_MERGE_FAIL"},
	{PNR_BIN_DATA_NOT_FOUND,"PNR_BIN_DATA_NOT_FOUND"},    
	{PNR_BIN_END_OF_DATA,"PNR_BIN_END_OF_DATA"},    
	{PNR_BIN_DATA_PURGED,"PNR_BIN_DATA_PURGED"},
	{PNR_BIN_FULL,"PNR_BIN_FULL"},    
	{PNR_BIN_OFFSET_PAST_END,"PNR_BIN_OFFSET_PAST_END"},    
	{PNR_ENC_NO_ENCODED_DATA,"PNR_ENC_NO_ENCODED_DATA"},
	{PNR_ENC_INVALID_DLL,"PNR_ENC_INVALID_DLL"},

	{PNR_RMT_USAGE_ERROR,"PNR_RMT_USAGE_ERROR"},
	{PNR_RMT_INVALID_ENDTIME,"PNR_RMT_INVALID_ENDTIME"},
	{PNR_RMT_MISSING_INPUT_FILE,"PNR_RMT_MISSING_INPUT_FILE"},
	{PNR_RMT_MISSING_OUTPUT_FILE,"PNR_RMT_MISSING_OUTPUT_FILE"},
	{PNR_RMT_INPUT_EQUALS_OUTPUT_FILE,"PNR_RMT_INPUT_EQUALS_OUTPUT_FILE"},
	{PNR_RMT_UNSUPPORTED_AUDIO_VERSION,"PNR_RMT_UNSUPPORTED_AUDIO_VERSION"},
	{PNR_RMT_DIFFERENT_AUDIO,"PNR_RMT_DIFFERENT_AUDIO"},
	{PNR_RMT_DIFFERENT_VIDEO,"PNR_RMT_DIFFERENT_VIDEO"},
	{PNR_RMT_PASTE_MISSING_STREAM,"PNR_RMT_PASTE_MISSING_STREAM"},
	{PNR_RMT_END_OF_STREAM,"PNR_RMT_END_OF_STREAM"},
	{PNR_RMT_IMAGE_MAP_PARSE_ERROR,"PNR_RMT_IMAGE_MAP_PARSE_ERROR"},
	{PNR_RMT_INVALID_IMAGEMAP_FILE,"PNR_RMT_INVALID_IMAGEMAP_FILE"},
	{PNR_RMT_EVENT_PARSE_ERROR,"PNR_RMT_EVENT_PARSE_ERROR"},
	{PNR_RMT_INVALID_EVENT_FILE,"PNR_RMT_INVALID_EVENT_FILE"},
	{PNR_RMT_INVALID_OUTPUT_FILE,"PNR_RMT_INVALID_OUTPUT_FILE"},
	{PNR_RMT_INVALID_DURATION,"PNR_RMT_INVALID_DURATION"},
	{PNR_RMT_NO_DUMP_FILES,"PNR_RMT_NO_DUMP_FILES"},
	{PNR_RMT_NO_EVENT_DUMP_FILE,"PNR_RMT_NO_EVENT_DUMP_FILE"},
	{PNR_RMT_NO_IMAP_DUMP_FILE,"PNR_RMT_NO_IMAP_DUMP_FILE"},

	{PNR_PROP_NOT_FOUND,"PNR_PROP_NOT_FOUND"},
	{PNR_PROP_NOT_COMPOSITE,"PNR_PROP_NOT_COMPOSITE"},
	{PNR_PROP_DUPLICATE,"PNR_PROP_DUPLICATE"},
	{PNR_PROP_TYPE_MISMATCH,"PNR_PROP_TYPE_MISMATCH"},
	{PNR_PROP_ACTIVE,"PNR_PROP_ACTIVE"},
	{PNR_PROP_INACTIVE,"PNR_PROP_INACTIVE"},

	{PNR_COULDNOTINITCORE,"PNR_COULDNOTINITCORE"},
	{PNR_PERFECTPLAY_NOT_SUPPORTED,"PNR_PERFECTPLAY_NOT_SUPPORTED"},
	{PNR_NO_LIVE_PERFECTPLAY,"PNR_NO_LIVE_PERFECTPLAY"},
	{PNR_PERFECTPLAY_NOT_ALLOWED,"PNR_PERFECTPLAY_NOT_ALLOWED"},
	{PNR_NO_CODECS,"PNR_NO_CODECS"},
	{PNR_SLOW_MACHINE,"PNR_SLOW_MACHINE"},
	{PNR_FORCE_PERFECTPLAY,"PNR_FORCE_PERFECTPLAY"},
	{PNR_INVALID_HTTP_PROXY_HOST,"PNR_INVALID_HTTP_PROXY_HOST"},
	{PNR_INVALID_METAFILE,"PNR_INVALID_METAFILE"},
	{PNR_BROWSER_LAUNCH,"PNR_BROWSER_LAUNCH"},

	{PNR_RESOURCE_NOT_CACHED,"PNR_RESOURCE_NOT_CACHED"},
	{PNR_RESOURCE_NOT_FOUND,"PNR_RESOURCE_NOT_FOUND"},
	{PNR_RESOURCE_CLOSE_FILE_FIRST,"PNR_RESOURCE_CLOSE_FILE_FIRST"},
	{PNR_RESOURCE_NODATA,"PNR_RESOURCE_NODATA"},
	{PNR_RESOURCE_BADFILE,"PNR_RESOURCE_BADFILE"},
	{PNR_RESOURCE_PARTIALCOPY,"PNR_RESOURCE_PARTIALCOPY"},

	{PNR_PPV_NO_USER,"PNR_PPV_NO_USER"},
	{PNR_PPV_GUID_READ_ONLY,"PNR_PPV_GUID_READ_ONLY"},
	{PNR_PPV_GUID_COLLISION,"PNR_PPV_GUID_COLLISION"},
	{PNR_REGISTER_GUID_EXISTS,"PNR_REGISTER_GUID_EXISTS"},
	{PNR_PPV_AUTHORIZATION_FAILED,"PNR_PPV_AUTHORIZATION_FAILED"},
	{PNR_PPV_OLD_PLAYER,"PNR_PPV_OLD_PLAYER"},
	{PNR_PPV_ACCOUNT_LOCKED,"PNR_PPV_ACCOUNT_LOCKED"},

	{PNR_UPG_AUTH_FAILED,"PNR_UPG_AUTH_FAILED"},
	{PNR_UPG_CERT_AUTH_FAILED,"PNR_UPG_CERT_AUTH_FAILED"},
	{PNR_UPG_CERT_EXPIRED,"PNR_UPG_CERT_EXPIRED"},
	{PNR_UPG_CERT_REVOKED,"PNR_UPG_CERT_REVOKED"},
	{PNR_UPG_RUP_BAD,"PNR_UPG_RUP_BAD"},

	{PNR_AUTOCFG_SUCCESS,"PNR_AUTOCFG_SUCCESS"},
	{PNR_AUTOCFG_FAILED,"PNR_AUTOCFG_FAILED"},
	{PNR_AUTOCFG_ABORT,"PNR_AUTOCFG_ABORT"},

	{PNR_FAILED	,"PNR_FAILED"},
};

void seterror(const char *funcname, PN_RESULT res)
{
	for(error *p = errorlist; p->name; p++)
		if (p->res == res){
			PyErr_Format(module_error, "%s failed, error = %s (0x%x)", funcname, p->name, res);
			return;
		}
	PyErr_Format(module_error, "%s failed, error = %s (0x%x)", funcname, "PNR_UNKNOWN", res);
}
void seterror(const char *msg){PyErr_SetString(module_error, msg);}

char *geterrorstring(PN_RESULT res, char *pszBuffer){
	for(error *p = errorlist; p->name; p++)
		if (p->res == res){
			strcpy(pszBuffer, p->name);
			return pszBuffer;
		}
	strcpy(pszBuffer,"PNR_UNKNOWN");
	return pszBuffer;
	}

struct constentry {char* s;int n;};

static struct constentry _rma_const[] ={

	// RMA image formats
	{"RMA_RGB",RMA_RGB}, // Windows-compatible RGB formats
	{"RMA_RLE8",RMA_RLE8},
	{"RMA_RLE4",RMA_RLE4},
	{"RMA_BITFIELDS",RMA_BITFIELDS},
	{"RMA_I420",RMA_I420}, // planar YCrCb
	{"RMA_YV12",RMA_YV12}, // planar YVU420
	{"RMA_YUY2",RMA_YUY2}, // packed YUV422
	{"RMA_UYVY",RMA_UYVY}, // packed YUV422
	{"RMA_YVU9",RMA_YVU9}, // Intel YVU9

	// Non-standard FOURCC formats for backward compatibility only
	{"RMA_RGB3",RMA_RGB3_ID},
	{"RMA_RGB555",RMA_RGB555_ID},
	{"RMA_RGB565",RMA_RGB565_ID},
	{"RMA_RGB24",RMA_RGB24_ID},
	{"RMA_8BIT",RMA_8BIT_ID},
	{"RMA_YUV420",RMA_YUV420_ID},
	{NULL,0}
	};

// add symbolic constants to dictionary
static int 
SetItemEnum(PyObject *d,constentry e[])
	{
	PyObject *x;
	for(int i=0;e[i].s;i++)
		{
		x = PyInt_FromLong((long) e[i].n);
		if (x == NULL || PyDict_SetItemString(d, e[i].s, x) < 0)
			return -1;
		Py_DECREF(x);
		}
	return 0;
	}
#define FATAL_ERROR_IF(exp) if(exp){Py_FatalError("can't initialize module rma");return;}	

static struct PyMethodDef module_functions[] = {
    {"CreateEngine",EngineObject_CreateInstance,1}, 
	{NULL,NULL}
};

PY_API
void initrma()
{
	PyObject *module = Py_InitModule(moduleName,module_functions);
	PyObject *dict = PyModule_GetDict(module);
	module_error = PyString_FromString(errorName);
	PyDict_SetItemString(dict,"error",module_error);
	PyObject *copyright = PyString_FromString("Copyright 1999-2000 Oratrix");
	PyDict_SetItemString(dict,"copyright",copyright);
	Py_XDECREF(copyright);

#ifdef _WIN32
	PyCallbackBlock::init();
#endif
	
	FATAL_ERROR_IF(SetItemEnum(dict,_rma_const)<0)

	// Check for errors
	if (PyErr_Occurred())
		Py_FatalError("can't initialize module ddraw");
	
}
