#ifndef INC_MEMFILE
#define INC_MEMFILE

#ifndef _WINDOWS_
#include <windows.h>
#endif

class memfile
	{
	public:
	memfile();
	~memfile();
	void copy(const memfile& other);
	void reserve(DWORD dwBytes);

	// file-mem and mem-file transfer
	bool open(LPCTSTR szFileName);
	bool saveas(LPCTSTR szFileName);

	BYTE* data() const { return m_begin;}
	DWORD size() const { return m_size;}
	DWORD capacity() const { return m_capacity;}
	BYTE* rdata() const {return m_prdata;}
	
	DWORD sizeg() const { return m_end-m_prdata;}
	void seekg(int pos) { m_prdata = m_begin + pos;}
	bool emptyg(){ return m_prdata == m_end;}

	// file type read/write support
	int read(BYTE *b, int nb)
		{
		int nr = m_end - m_prdata;
		int nt = (nr>=nb)?nb:nr;
		if(nt>0)
			{
			memcpy(b, m_prdata, nt);
			m_prdata += nt;
			}
		return nt;
		}

	bool safe_read(BYTE *b, int nb) 
		{ return read(b, nb) == nb;}

	BYTE get_byte()
		{
		if(m_prdata == m_end) throw_range_error();
		return *m_prdata++;
		}

	WORD get_be_ushort()
		{
		BYTE b[2];
		if(!safe_read(b, 2)) throw_range_error();
		return (b[1]<<8)| b[0];
		}

	void skip(int nb)
		{
		int nr = m_end - m_prdata;
		int nt = (nr>=nb)?nb:nr;
		if(nt>0)
			m_prdata += nt;
		if(nt!=nb) throw_range_error();
		}

	int write(const BYTE *b, int nb)
   		{
		memcpy(m_prdata, b, nb);
		m_prdata+=nb;
		return nb;
		}
	
	int write(int v){return write((BYTE*)&v, sizeof(int));}

	HANDLE get_handle() const { return m_hf;}
	
	FILE* get_as_cfile()
		{
		if(m_hf != INVALID_HANDLE_VALUE)
			CloseHandle(m_hf);
		m_hf = INVALID_HANDLE_VALUE;
		#ifdef UNICODE
		return _wfopen(m_pfname, L"rb");
		#else
		return fopen(m_pfname, "rb");
		#endif
		}

	private:
	void throw_range_error()
		{
		#ifdef STD_CPP
		throw std::range_error("index out of range");
		#else
		//throw "index out of range";
		#endif
		}

	BYTE *m_begin;
	BYTE *m_end;
	DWORD m_size;
	DWORD m_capacity;

	// file type read/write support
	BYTE *m_prdata;

	// in place processing
	HANDLE m_hf;
	TCHAR *m_pfname;
	};

inline memfile::memfile():
	m_begin(NULL), m_end(NULL),
	m_size(0),
	m_capacity(0),
	m_prdata(NULL),
	m_hf(INVALID_HANDLE_VALUE)
	{
	reserve(1572864UL);
	}

inline memfile::~memfile()
	{
	if(m_hf != INVALID_HANDLE_VALUE)
		CloseHandle(m_hf);

	if(m_begin)
		::HeapFree(GetProcessHeap(),0,m_begin);

	if(m_pfname)
		delete[] m_pfname;
	}

inline void memfile::reserve(DWORD dwBytes)
	{
	if(m_begin==NULL)
		{
		m_begin=(BYTE*)::HeapAlloc(GetProcessHeap(),0,dwBytes);
		if(m_begin==NULL)
			{
			//AfxMessageBox("Memory allocation failure");
			return;
			}
		m_capacity=::HeapSize(GetProcessHeap(),0,m_begin);
		}
	else
		{
		if(dwBytes>m_capacity)
			{
			m_begin = (BYTE*)::HeapReAlloc(GetProcessHeap(),0,m_begin,dwBytes); 
			m_capacity=::HeapSize(GetProcessHeap(),0,m_begin);
			}
		}
	m_prdata=m_begin; // init read/write pointer 
	}

inline bool memfile::open(LPCTSTR szFileName)
	{
	HANDLE hf = CreateFile(szFileName,  
		GENERIC_READ,  
		FILE_SHARE_READ,  // 0 = not shared or FILE_SHARE_READ  
		0,  // lpSecurityAttributes 
		OPEN_EXISTING,  
		FILE_ATTRIBUTE_READONLY,  
		NULL); 

	if(hf == INVALID_HANDLE_VALUE) 
		return false;
	DWORD dwSize =::GetFileSize(hf,NULL);
	if (dwSize == 0xFFFFFFFF)
		{
		CloseHandle(hf);
		return false;
		}

	reserve(dwSize);
	m_size = 0;
	if(!ReadFile(hf, m_begin, dwSize, &m_size, 0)) 
		{ 
		CloseHandle(hf);
		return false;
		}
	m_prdata = m_begin; // init read pointer
	m_end = m_begin + m_size;

	// keep handle open 
	//CloseHandle(hf);
	SetFilePointer(hf, 0, NULL, FILE_BEGIN);
	m_hf = hf;

	m_pfname = new TCHAR[lstrlen(szFileName)+1];
	lstrcpy(m_pfname, szFileName);
	return true;
	}

inline bool memfile::saveas(LPCTSTR szFileName)
	{
	if(!SetFileAttributes(szFileName, FILE_ATTRIBUTE_ARCHIVE))
		{
		DWORD dw=GetLastError();
		if(dw!=2) // no can not find file
			return false;
		}
 
	HANDLE hf = CreateFile(szFileName,  
		GENERIC_READ|GENERIC_WRITE,  
		FILE_SHARE_READ,  
		0,  
		OPEN_ALWAYS,  
		FILE_ATTRIBUTE_NORMAL,  
		NULL); 

	if(hf == INVALID_HANDLE_VALUE)
		return false;
	DWORD dwNumBytesWritten = 0;
	if(!::WriteFile(hf, data(), size(),&dwNumBytesWritten,0))
		return false;

	if(dwNumBytesWritten!=size())
		return false;
	CloseHandle(hf);	
	return true;
	}

inline void memfile::copy(const memfile& other)
	{
	if(this==&other) return;
	memcpy(m_begin,other.data(),other.size());
	m_size=other.size();
	}

#endif
