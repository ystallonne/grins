
/*************************************************************************
Copyright 1991-2001 by Oratrix Development BV, Amsterdam, The Netherlands.

                        All Rights Reserved

/*************************************************************************/

#include "Python.h"

#include <windows.h>

#include "winuser_globals.h"

#include "mtpycall.h"

#pragma warning(disable: 4786)
#include <map>

struct PyWnd
	{
	PyObject_HEAD
	HWND m_hWnd;
	std::map<UINT, PyObject*> *m_phooks;

	static PyTypeObject type;
	static PyMethodDef methods[];
	static std::map<HWND, PyWnd*> wnds;
	static PyWnd *createInstance()
		{
		PyWnd *instance = PyObject_NEW(PyWnd, &type);
		if (instance == NULL) return NULL;
		instance->m_hWnd = NULL;
		instance->m_phooks = NULL;
		return instance;
		}

	static void dealloc(PyWnd *instance) 
		{ 
		if(instance->m_phooks != NULL)
			{
			std::map<UINT, PyObject*>::iterator it;
			for(it = instance->m_phooks->begin();it!=instance->m_phooks->end();it++)
				Py_XDECREF((*it).second);
			delete instance->m_phooks;
			}
		PyMem_DEL(instance);
		}

	static PyObject *getattr(PyWnd *instance, char *name)
		{ 
		return Py_FindMethod(methods, (PyObject*)instance, name);
		}

	static void debug_report()
		{
		char sz[80];
		wsprintf(sz, "wnds size=%d", wnds.size());
		MessageBox(NULL, sz, "PyWnd", MB_OK);
		}
	DECLARE_WND_CLASS("PyWnd")
	};

std::map<HWND, PyWnd*> PyWnd::wnds;

HINSTANCE GetAppHinstance() 
	{ static HINSTANCE h = GetModuleHandle(NULL); return h;}


LONG APIENTRY PyWnd_WndProc(HWND hWnd, UINT uMsg, UINT wParam, LONG lParam)
{	
	switch(uMsg)
		{
		case WM_NCCREATE:
			{
			LONG res = DefWindowProc(hWnd, uMsg, wParam, lParam);
			PyWnd *pywnd = PyWnd::createInstance();
			pywnd->m_hWnd = hWnd;
			pywnd->m_phooks = new std::map<UINT, PyObject*>();
			PyWnd::wnds[hWnd] = pywnd;
			return res;
			}
		case WM_NCDESTROY:
			{
			MSG msg = {hWnd, uMsg, wParam, lParam, 0, {0, 0}};
			std::map<HWND, PyWnd*>::iterator wit = PyWnd::wnds.find(hWnd);
			if(wit != PyWnd::wnds.end())
				{
				PyWnd *pywnd = (*wit).second;
				PyWnd::wnds.erase(wit);
				pywnd->m_hWnd = NULL;
				Py_DECREF(pywnd);
				}
			if(PyWnd::wnds.size()==0)
				PostQuitMessage(0);
			return 0;
			}
		}

	MSG msg = {hWnd, uMsg, wParam, lParam, 0, {0, 0}};
	std::map<HWND, PyWnd*>::iterator wit = PyWnd::wnds.find(hWnd);
	if(wit != PyWnd::wnds.end())
		{
		PyWnd *pywnd = (*wit).second;
		std::map<UINT, PyObject*>& hooks = *pywnd->m_phooks;
		std::map<UINT, PyObject*>::iterator hit = hooks.find(uMsg);
		if(hit != hooks.end())
			{
			PyCallbackBlock cbblock;
			PyObject *method = (*hit).second;
			PyObject *arglst = Py_BuildValue("((iiiii(ii)))",
				msg.hwnd,msg.message,msg.wParam,msg.lParam,msg.time,msg.pt.x,msg.pt.y);
			PyObject *retobj = PyEval_CallObject(method, arglst);

			// xxx: elaborate on specific messages
			if (retobj == NULL)
				return DefWindowProc(hWnd, uMsg, wParam, lParam);
			else if(retobj == Py_None)
				{
				Py_DECREF(retobj);
				return 0;
				}
			else
				{
				long retval = PyInt_AsLong(retobj);
				Py_DECREF(retobj);
				if(retval == 0) return 0;
				else return DefWindowProc(hWnd, uMsg, wParam, lParam);
				}
			}
		}
	return DefWindowProc(hWnd, uMsg, wParam, lParam);
}



PyObject* Winuser_RegisterClassEx(PyObject *self, PyObject *args)
	{
	char *className;
	HMENU hMenu = 0;
	if (!PyArg_ParseTuple(args, "s|i", &className, &hMenu))
		return NULL;
	WNDCLASSEX wcx = PyWnd::GetWndClass();
	wcx.lpszClassName = className;
	wcx.hIcon = LoadIcon(NULL, IDI_APPLICATION);
	wcx.hCursor = LoadCursor(NULL, IDI_APPLICATION);
	ATOM atom = ::RegisterClassEx(&wcx); 
	if(atom == 0){
		seterror("RegisterClassEx", GetLastError());
		return NULL;
		}
	return Py_BuildValue("i", int(atom));
	}

PyObject* Winuser_CreateWindowEx(PyObject *self, PyObject *args)
	{
	DWORD dwExStyle;
	char *pstrWndClass;
	char *szWindowName;
	DWORD dwStyle;
	POINT pt;
	SIZE size;
	PyWnd *parent = NULL;
	UINT nID = 0;
	LPVOID lpCreateParam = NULL;
	if (!PyArg_ParseTuple(args, "iszi(ii)(ii)|O!i", &dwExStyle, &pstrWndClass, &szWindowName, &dwStyle,
		&pt.x, &pt.y, &size.cx, &size.cy, &PyWnd::type, &parent, &nID))
		return NULL;

	HWND hWnd = ::CreateWindowEx(dwExStyle, pstrWndClass, szWindowName,
			dwStyle, pt.x,pt.y, size.cx,
			size.cx, ((parent!=NULL)?parent->m_hWnd:NULL), (HMENU)nID,
			GetAppHinstance(), lpCreateParam);
	std::map<HWND, PyWnd*>::iterator wit = PyWnd::wnds.find(hWnd);
	if(wit == PyWnd::wnds.end())
		{
		seterror("Internal error");
		return NULL;
		}
	Py_INCREF((*wit).second);
	return (PyObject*)(*wit).second;
	}

PyObject* Winuser_CreateWindowFromHandle(PyObject *self, PyObject *args)
{
	HWND hwnd;
	if (!PyArg_ParseTuple(args, "i", &hwnd))
		return NULL;
	PyWnd *pywnd = PyWnd::createInstance();
	if(pywnd==NULL) return NULL;
	pywnd->m_hWnd = hwnd;
	return (PyObject*)pywnd;
}

PyObject* Winuser_GetDesktopWindow(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	PyWnd *pywnd = PyWnd::createInstance();
	if(pywnd==NULL) return NULL;
	pywnd->m_hWnd = ::GetDesktopWindow();
	return (PyObject*)pywnd;
}


///////////////////////////////////////////
// module

#define ASSERT_ISWINDOW(wnd) if((wnd) == NULL || !IsWindow(wnd)) {seterror("Not a window"); return NULL;}

static PyObject* PyWnd_ShowWindow(PyWnd *self, PyObject *args)
	{
	int nCmdShow = SW_SHOW;
	if (!PyArg_ParseTuple(args, "|i", &nCmdShow))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	BOOL res = ShowWindow(self->m_hWnd, nCmdShow);
	return Py_BuildValue("i", int(res));
	}

static PyObject* PyWnd_UpdateWindow(PyWnd *self, PyObject *args)
	{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	BOOL res = UpdateWindow(self->m_hWnd);
	if(!res){
		seterror("UpdateWindow", GetLastError());
		return NULL;
		}
	return none();
	}

static PyObject* PyWnd_DestroyWindow(PyWnd *self, PyObject *args)
	{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	if(!IsWindow(self->m_hWnd))
		{
		seterror("DestroyWindow against not a window");
		return NULL;
		}
	
	// DestroyWindow sends (WM_NCDESTROY, WM_DESTROY)
	BOOL res;
	Py_BEGIN_ALLOW_THREADS
	res = ::DestroyWindow(self->m_hWnd);
	Py_END_ALLOW_THREADS
	if(!res){
		seterror("DestroyWindow", GetLastError());
		return NULL;
		}
	return none();
	}

static PyObject* PyWnd_InvalidateRect(PyWnd *self, PyObject *args)
{
	PyObject *pyrc; 
	BOOL bErase;
	if (!PyArg_ParseTuple(args, "Oi", &pyrc, &bErase))
		return NULL;
	RECT rc, *prc = NULL;
	if(pyrc != Py_None)
		{
		if(!PyArg_ParseTuple(pyrc, "iiii", &rc.left, &rc.top, &rc.right, &rc.bottom)) 
			{
			seterror("first argument should be a rect tuple or None");
			return NULL;
			}
		prc = &rc;
		}
	ASSERT_ISWINDOW(self->m_hWnd)
	BOOL res = ::InvalidateRect(self->m_hWnd, prc, bErase);
	if(!res){
		seterror("InvalidateRect", GetLastError());
		return NULL;
		}
	return none();
}

static PyObject* PyWnd_GetClientRect(PyWnd *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	RECT rc;
	BOOL res = GetClientRect(self->m_hWnd, &rc);
	if(!res){
		seterror("GetClientRect", GetLastError());
		return NULL;
		}
	return Py_BuildValue("iiii", rc.left, rc.top, rc.right, rc.bottom);
}

static PyObject* PyWnd_RedrawWindow(PyWnd *self, PyObject *args)
{
	PyObject *pyrc;	      // update rectangle
	HRGN hrgn;            // handle to update region
	UINT flags;           // array of redraw flags
	if (!PyArg_ParseTuple(args, "Oii", &pyrc, &hrgn, &flags))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	RECT rc, *prc = NULL;
	if(pyrc != Py_None)
		{
		if(!PyArg_ParseTuple(pyrc, "iiii", &rc.left, &rc.top, &rc.right, &rc.bottom)) 
			{
			seterror("first argument should be a rect tuple or None");
			return NULL;
			}
		prc = &rc;
		}
	BOOL res = RedrawWindow(self->m_hWnd, prc, hrgn, flags);
	if(!res){
		seterror("RedrawWindow", GetLastError());
		return NULL;
		}
	return none();
}

static PyObject* PyWnd_GetDC(PyWnd *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	HDC hdc = ::GetDC(self->m_hWnd);
	return Py_BuildValue("i", hdc);
}

static PyObject* PyWnd_ReleaseDC(PyWnd *self, PyObject *args)
{
	HDC hdc;
	if (!PyArg_ParseTuple(args, "i", &hdc))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	int res = ::ReleaseDC(self->m_hWnd, hdc);
	if(res == 0)
		{
		seterror("ReleaseDC failed");
		return NULL;
		}
	return none();
}

static PyObject* PyWnd_BeginPaint(PyWnd *self, PyObject *args)
{
	PAINTSTRUCT ps;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	HDC hdc  = ::BeginPaint(self->m_hWnd, &ps);
	PyObject *obRet = Py_BuildValue("(ii(iiii)iis#)",
		ps.hdc,
		ps.fErase,
		ps.rcPaint.left, ps.rcPaint.top, ps.rcPaint.right, ps.rcPaint.bottom,
		ps.fRestore,
		ps.fIncUpdate,
		ps.rgbReserved, sizeof(ps.rgbReserved));
	return obRet;
}

static PyObject* PyWnd_EndPaint(PyWnd *self, PyObject *args)
{
	PAINTSTRUCT ps;
	PyObject *obString;
	if (!PyArg_ParseTuple(args, "(ii(iiii)iiO)",
		&ps.hdc,
		&ps.fErase,
		&ps.rcPaint.left, &ps.rcPaint.top, &ps.rcPaint.right, &ps.rcPaint.bottom,
		&ps.fRestore,
		&ps.fIncUpdate,
		&obString))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	if (!PyString_Check(obString) || PyString_Size(obString) != sizeof(ps.rgbReserved))
		{
		seterror("Invalid paintstruct");
		return NULL;
		}
	memcpy(ps.rgbReserved, PyString_AsString(obString), sizeof(ps.rgbReserved));
	::EndPaint(self->m_hWnd, &ps);
	return none();
}


static PyObject* PyWnd_GetSafeHwnd(PyWnd *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	if(!IsWindow(self->m_hWnd))
		return Py_BuildValue("i", 0);
	return Py_BuildValue("i", self->m_hWnd);
}

static PyObject* PyWnd_IsWindow(PyWnd *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, "")) return NULL;
	return Py_BuildValue("i", IsWindow(self->m_hWnd));
}

static PyObject* PyWnd_PostMessage(PyWnd *self, PyObject *args)
{
	UINT message;
	WPARAM wParam = 0;
	LPARAM lParam = 0;
	if (!PyArg_ParseTuple(args, "i|ii", &message, &wParam, &lParam))
		return NULL;
	BOOL res = ::PostMessage(self->m_hWnd, message, wParam, lParam);
	if(!res){
		seterror("PostMessage", GetLastError());
		return NULL;
		}
	return none();
}

static PyObject* PyWnd_SendMessage(PyWnd *self, PyObject *args)
{
	UINT message;
	WPARAM wParam = 0;
	LPARAM lParam = 0;
	if (!PyArg_ParseTuple(args, "i|ii", &message, &wParam, &lParam))
		return NULL;
	long rc = ::SendMessage(self->m_hWnd, message, wParam, lParam);
	return Py_BuildValue("l",rc);
}

static PyObject* PyWnd_HookMessage(PyWnd *self, PyObject *args)
{
	PyObject *method;
	UINT message;
	if (!PyArg_ParseTuple(args,"Oi",&method, &message))
		return NULL;
	if (method!=Py_None && !PyCallable_Check(method))
		{
		seterror("The first parameter must be a callable object");
		return NULL;
		}
	if(self->m_phooks == NULL)
		{
		seterror("Cannot hook message for foreign windows");
		return NULL;
		}
	ASSERT_ISWINDOW(self->m_hWnd)

	// find previous
	std::map<UINT, PyObject*>::iterator it = self->m_phooks->find(message);
	PyObject *prevMethod = NULL;
	if(it != self->m_phooks->end())
		{
		prevMethod = (*it).second;
		self->m_phooks->erase(it);
		}

	// add new
	if (method!=Py_None) 
		{
		Py_INCREF(method);
		(*self->m_phooks)[message] = method;
		}
	Py_XDECREF(prevMethod);
	return none();
}

static PyObject* PyWnd_MessageBox(PyWnd *self, PyObject *args)
{
	char *text;
	char *caption;
	UINT type = MB_OK;
	if (!PyArg_ParseTuple(args, "ss|i", &text, &caption, &type))
		return NULL;
	int res;
	Py_BEGIN_ALLOW_THREADS
	res = MessageBox(self->m_hWnd,text, caption, type);
	Py_END_ALLOW_THREADS
	return Py_BuildValue("i", res);
}

static PyObject* PyWnd_SetMenu(PyWnd *self, PyObject *args)
{
	HMENU hMenu;
	if (!PyArg_ParseTuple(args, "i", &hMenu))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	BOOL res = SetMenu(self->m_hWnd, hMenu);
	if(!res){
		seterror("SetMenu", GetLastError());
		return NULL;
		}
	return none();
}

static PyObject* PyWnd_DrawMenuBar(PyWnd *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	BOOL res = DrawMenuBar(self->m_hWnd);
	if(!res){
		seterror("PostMessage", GetLastError());
		return NULL;
		}
	return none();
}

static PyObject* PyWnd_SetClassLong(PyWnd *self, PyObject *args)
	{
	int nIndex;
	LONG dwNewLong;
	if (!PyArg_ParseTuple (args, "il",&nIndex,&dwNewLong))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	DWORD dwOldLong = SetClassLong(self->m_hWnd, nIndex, dwNewLong);
	return Py_BuildValue("l",dwOldLong);
	}
 
static PyObject* PyWnd_SetWindowLong(PyWnd *self, PyObject *args)
	{
	int nIndex;
	LONG newLong;
	if (!PyArg_ParseTuple (args, "il",&nIndex,&newLong))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	LONG oldLong=::SetWindowLong(self->m_hWnd, nIndex, newLong);
	return Py_BuildValue("l",oldLong);
	}

static PyObject* PyWnd_GetWindowLong(PyWnd *self, PyObject *args)
	{
	int nIndex;
	if (!PyArg_ParseTuple (args, "i", &nIndex))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	LONG val = ::GetWindowLong(self->m_hWnd, nIndex);
	return Py_BuildValue("l", val);
	}
 
static PyObject* PyWnd_SetWindowPos(PyWnd *self, PyObject *args)
{
	HWND insertAfter;
	int x,y,cx,cy;
	int flags;
	if (!PyArg_ParseTuple(args,"i(iiii)i",
		        (int*)(&insertAfter), &x, &y, &cx, &cy, &flags))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	SetWindowPos(self->m_hWnd, insertAfter, x, y, cx, cy, flags);
	return none();
}

static PyObject* PyWnd_MoveWindow(PyWnd *self, PyObject *args)
{
	int x,y,cx,cy;
	BOOL bRepaint = TRUE;
	if (!PyArg_ParseTuple(args,"i(iiii)|i", &x, &y, &cx, &cy, &bRepaint))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	MoveWindow(self->m_hWnd, x, y, cx, cy, bRepaint);
	return none();
}

static PyObject* PyWnd_SetTimer(PyWnd *self, PyObject *args)
	{
	UINT nIDEvent, nElapse;
	if (!PyArg_ParseTuple(args, "ii",&nIDEvent,&nElapse))
		return NULL;
	ASSERT_ISWINDOW(self->m_hWnd)
	UINT id = SetTimer(self->m_hWnd, nIDEvent, nElapse, NULL);
	if(id==0){
		seterror("SetTimer", GetLastError());
		return NULL;
		}	
	return Py_BuildValue("i", id);
	}

static PyObject* PyWnd_KillTimer(PyWnd *self, PyObject *args)
	{
	UINT nID;
	if (!PyArg_ParseTuple(args, "i",&nID))
		return NULL;
	BOOL res = KillTimer(self->m_hWnd, nID);
	if(!res){
		seterror("KillTimer", GetLastError());
		return NULL;
		}	
	return none();
	}

PyMethodDef PyWnd::methods[] = {
	{"ShowWindow", (PyCFunction)PyWnd_ShowWindow, METH_VARARGS, ""},
	{"UpdateWindow", (PyCFunction)PyWnd_UpdateWindow, METH_VARARGS, ""},
	{"DestroyWindow", (PyCFunction)PyWnd_DestroyWindow, METH_VARARGS, ""},
	{"InvalidateRect", (PyCFunction)PyWnd_InvalidateRect, METH_VARARGS, ""},
	{"GetClientRect", (PyCFunction)PyWnd_GetClientRect, METH_VARARGS, ""},
	{"RedrawWindow", (PyCFunction)PyWnd_RedrawWindow, METH_VARARGS, ""},
	{"GetDC", (PyCFunction)PyWnd_GetDC, METH_VARARGS, ""},
	{"ReleaseDC", (PyCFunction)PyWnd_ReleaseDC, METH_VARARGS, ""},
	{"BeginPaint", (PyCFunction)PyWnd_BeginPaint, METH_VARARGS, ""},
	{"EndPaint", (PyCFunction)PyWnd_EndPaint, METH_VARARGS, ""},
	{"GetSafeHwnd", (PyCFunction)PyWnd_GetSafeHwnd, METH_VARARGS, ""},
	{"IsWindow", (PyCFunction)PyWnd_IsWindow, METH_VARARGS, ""},
	{"PostMessage", (PyCFunction)PyWnd_PostMessage, METH_VARARGS, ""},
	{"SendMessage", (PyCFunction)PyWnd_SendMessage, METH_VARARGS, ""},
	{"HookMessage", (PyCFunction)PyWnd_HookMessage, METH_VARARGS, ""},
	{"MessageBox", (PyCFunction)PyWnd_MessageBox, METH_VARARGS, ""},
	{"SetMenu", (PyCFunction)PyWnd_SetMenu, METH_VARARGS, ""},
	{"DrawMenuBar", (PyCFunction)PyWnd_DrawMenuBar, METH_VARARGS, ""},
	{"SetClassLong", (PyCFunction)PyWnd_SetClassLong, METH_VARARGS, ""},
	{"SetWindowLong", (PyCFunction)PyWnd_SetWindowLong, METH_VARARGS, ""},
	{"GetWindowLong", (PyCFunction)PyWnd_GetWindowLong, METH_VARARGS, ""},
	{"SetWindowPos", (PyCFunction)PyWnd_SetWindowPos, METH_VARARGS, ""},
	{"MoveWindow", (PyCFunction)PyWnd_MoveWindow, METH_VARARGS, ""},
	{"SetTimer", (PyCFunction)PyWnd_SetTimer, METH_VARARGS, ""},
	{"KillTimer", (PyCFunction)PyWnd_KillTimer, METH_VARARGS, ""},
	{NULL, (PyCFunction)NULL, 0, NULL}		// sentinel
};

PyTypeObject PyWnd::type = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,					// ob_size
	"PyWnd",			// tp_name
	sizeof(PyWnd),		// tp_basicsize
	0,					// tp_itemsize
	
	// methods
	(destructor)PyWnd::dealloc,	// tp_dealloc
	(printfunc)0,				// tp_print
	(getattrfunc)PyWnd::getattr,// tp_getattr
	(setattrfunc)0,	// tp_setattr
	(cmpfunc)0,		// tp_compare
	(reprfunc)0,	// tp_repr
	0,				// tp_as_number
	0,				// tp_as_sequence
	0,				// tp_as_mapping
	(hashfunc)0,	// tp_hash
	(ternaryfunc)0,	// tp_call
	(reprfunc)0,	// tp_str

	// Space for future expansion
	0L,0L,0L,0L,

	"PyWnd Type" // Documentation string
	};
