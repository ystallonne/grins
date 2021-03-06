#ifndef INC_PYWINTOOLBOX
#define INC_PYWINTOOLBOX

/* Definitions needed to include/declare/define the
** right things.
*/

#define staticforward extern
#define WITHOUT_FRAMEWORKS
#undef USE_TOOLBOX_OBJECT_GLUE

/* Python includes */
#include "Python.h"
#include "pymactoolbox.h"

/* QuickTime includes */
#include <QTML.h>
#include <TextUtils.h>
#include <Files.h>
#include <Events.h>
#include <Movies.h>

/* Windows includes */
#include <windows.h>

/* Routines specific to Qt/Windows */
int ToEventRecord(PyObject *obj, EventRecord  *pe);

/* Mac routines we need (aside from those in pymactoolbox.h */
extern PyObject *PyMac_GetOSErrException(void);

/* Windows Direct Draw Python Objects */
#include <ddraw.h>

typedef struct {
	PyObject_HEAD
	IDirectDraw* pI;
} DirectDrawObject;

typedef struct {
	PyObject_HEAD
	IDirectDrawSurface* pI;
} DirectDrawSurfaceObject;

void UrlConvert(char *pszUrl);
PyObject* OSType_FromLong(long t);

#endif

