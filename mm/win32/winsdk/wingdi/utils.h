#ifndef INC_UTILS
#define INC_UTILS

#ifndef Py_PYTHON_H
#include "Python.h"
#endif

#ifndef _WINDOWS_
#include <windows.h>
#endif

#ifndef INC_CHARCONV
#include "../common/charconv.h"
#endif

#define seterror WinGDI_seterror

extern PyObject *WinGDI_ErrorObject;

inline PyObject* none() { Py_INCREF(Py_None); return Py_None;}

inline void seterror(const char *msg){ PyErr_SetString(WinGDI_ErrorObject, msg);}

inline void seterror(const char *funcname, const char *msg)
	{
	PyErr_Format(WinGDI_ErrorObject, "%s failed, %s", funcname, msg);
	PyErr_SetString(WinGDI_ErrorObject, msg);
	}

inline void seterror(const char *funcname, DWORD err)
	{
	TCHAR* pszmsg;
	FormatMessage( 
		 FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
		 NULL,
		 err,
		 MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
		 (TCHAR*) &pszmsg,
		 0,
		 NULL 
		);
	TextPtr tmsg(pszmsg);
	PyErr_Format(WinGDI_ErrorObject, "%s failed, error = %x, %s", funcname, err, tmsg.str());
	LocalFree(pszmsg);
	}

class PyPtListConverter
	{
	public:
	PyPtListConverter() 
	:	m_numpoints(0), m_ppt(NULL) {sz[0]='\0';}

	bool convert(PyObject *pyptlist)
		{
		if(m_ppt!=NULL) delete[] m_ppt;
		m_numpoints = PyList_Size(pyptlist);
		m_ppt = new POINT[m_numpoints];
		for(int i=0;i<m_numpoints;i++) 
			{
			PyObject * pypt = PyList_GetItem(pyptlist, i);
			if(!PyTuple_Check(pypt) || PyTuple_Size(pypt)!=2) 
				{
				strcpy(sz, "PyTuple_Check or PyTuple_Size");
				return false;
				}
			else if(!getPoint(pypt, m_ppt[i]))
				return false;
			}
		return true;
		}
	~PyPtListConverter(){if(m_ppt) delete[] m_ppt;}

	int getSize() const {return m_numpoints;}
	const POINT *getPoints() const {return m_ppt;}
	const char* getErrorStr() const {return sz;}

	private:
	bool getPoint(PyObject *pypt, POINT& pt)
		{
		PyObject *px = PyTuple_GetItem(pypt, 0);
		PyObject *py = PyTuple_GetItem (pypt, 1);
		if((!PyInt_Check(px)) || (!PyInt_Check(py)))
			{
			strcpy(sz, "PyInt_Check");
			return false;
			}
		pt.x = PyInt_AsLong(px);
		pt.y = PyInt_AsLong(py);
		return true;
		}
	char sz[80];
	int m_numpoints;
	POINT *m_ppt;
	};

class PyIntListConverter
	{
	public:
	PyIntListConverter() 
	:	m_num(0), m_pint(NULL), m_pbyte(NULL) {}

	bool convert(PyObject *pylist)
		{
		if(m_pint!=NULL) delete[] m_pint;
		m_num = PyList_Size(pylist);
		m_pint = new int[m_num];
		for(int i=0;i< m_num;i++) 
			{
			PyObject * pyval = PyList_GetItem(pylist, i);
			if(!PyInt_Check(pyval)) 
				return false;
			m_pint[i] = PyInt_AsLong(pyval);
			}
		return true;
		}
	~PyIntListConverter()
		{
		if(m_pint)delete[] m_pint;
		if(m_pbyte)delete[] m_pbyte;
		}

	int getSize() const {return m_num;}
	const int *getInts() const {return m_pint;}
	const BYTE *packInts()
		{
		if(!m_pint || m_num==0)
			return NULL;
		if(m_pbyte!=NULL) delete[] m_pbyte;
		m_pbyte = new BYTE[m_num];
		for(int i=0;i<m_num;i++) 
			m_pbyte[i]=BYTE(m_pint[i]);
		return m_pbyte;
		}
	private:
	int m_num;
	int *m_pint;
	BYTE *m_pbyte;
	};

class PyDictParser 
	{
	public:
	PyDictParser(PyObject *pydict)
		: m_pydict(pydict){}

	bool hasAttr(const char *name)
		{
		return PyDict_GetItemString(m_pydict, (char*)name)!=NULL;
		}

	int getIntAttr(const char *name, int defvalue=0)
		{
		PyObject *v = PyDict_GetItemString(m_pydict, (char*)name);
		if(v && PyInt_Check(v))
			return PyInt_AsLong(v);
		return defvalue;
		}

	const char* getStrAttr(const char *name, char *buf, int n, const char *pszdefault)
		{
		PyObject *v = PyDict_GetItemString(m_pydict, (char*)name);
		if(v && PyString_Check(v))
			{
			n = min(PyString_GET_SIZE(v), n);
			strncpy(buf, PyString_AsString(v), n-1);
			buf[n-1] = '\0';
			return buf;
			}
		n = min((int)strlen(pszdefault), n);
		strncpy(buf, pszdefault, n-1);
		buf[n-1] = '\0';
		return buf;
		}

	private:
	PyObject *m_pydict;
	};

inline HGDIOBJ GetGdiObjHandle(PyObject *obj)
	{
	if(obj == Py_None)
		return 0;
	if(PyInt_Check(obj))
		return (HGDIOBJ)PyInt_AsLong(obj);
	struct GdiObj { PyObject_HEAD; HGDIOBJ m_hGdiObj;};
	return ((GdiObj*)obj)->m_hGdiObj;
	}

inline int GetObjHandle(PyObject *obj)
	{
	if(obj == Py_None)
		return 0;
	if(PyInt_Check(obj))
		return PyInt_AsLong(obj);
	struct WrapperObj { PyObject_HEAD; int m_h;};
	return ((WrapperObj*)obj)->m_h;
	}

#endif // INC_UTILS

