// Machine generated IDispatch wrapper class(es) created by Microsoft Visual C++

// NOTE: Do not modify the contents of this file.  If this class is regenerated by
//  Microsoft Visual C++, your modifications will be overwritten.


#include "stdafx.h"
#include "websterpro.h"


// Dispatch interfaces referenced by this interface
#include "Font.h"

/////////////////////////////////////////////////////////////////////////////
// CWebsterPro

IMPLEMENT_DYNCREATE(CWebsterPro, CWnd)

/////////////////////////////////////////////////////////////////////////////
// CWebsterPro properties

short CWebsterPro::GetBorderStyle()
{
	short result;
	GetProperty(DISPID_BORDERSTYLE, VT_I2, (void*)&result);
	return result;
}

void CWebsterPro::SetBorderStyle(short propVal)
{
	SetProperty(DISPID_BORDERSTYLE, VT_I2, propVal);
}

COleFont CWebsterPro::GetFont()
{
	LPDISPATCH pDispatch;
	GetProperty(DISPID_FONT, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFont(LPDISPATCH propVal)
{
	SetProperty(DISPID_FONT, VT_DISPATCH, propVal);
}

OLE_HANDLE CWebsterPro::GetHWnd()
{
	OLE_HANDLE result;
	GetProperty(DISPID_HWND, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetHWnd(OLE_HANDLE propVal)
{
	SetProperty(DISPID_HWND, VT_I4, propVal);
}

BOOL CWebsterPro::GetEnabled()
{
	BOOL result;
	GetProperty(DISPID_ENABLED, VT_BOOL, (void*)&result);
	return result;
}

void CWebsterPro::SetEnabled(BOOL propVal)
{
	SetProperty(DISPID_ENABLED, VT_BOOL, propVal);
}

long CWebsterPro::GetBevelStyleInner()
{
	long result;
	GetProperty(0x1, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetBevelStyleInner(long propVal)
{
	SetProperty(0x1, VT_I4, propVal);
}

long CWebsterPro::GetBevelStyleOuter()
{
	long result;
	GetProperty(0x2, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetBevelStyleOuter(long propVal)
{
	SetProperty(0x2, VT_I4, propVal);
}

long CWebsterPro::GetBevelWidth()
{
	long result;
	GetProperty(0x3, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetBevelWidth(long propVal)
{
	SetProperty(0x3, VT_I4, propVal);
}

COleFont CWebsterPro::GetFontHeading1()
{
	LPDISPATCH pDispatch;
	GetProperty(0x1e, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontHeading1(LPDISPATCH propVal)
{
	SetProperty(0x1e, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontHeading2()
{
	LPDISPATCH pDispatch;
	GetProperty(0x1f, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontHeading2(LPDISPATCH propVal)
{
	SetProperty(0x1f, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontHeading3()
{
	LPDISPATCH pDispatch;
	GetProperty(0x20, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontHeading3(LPDISPATCH propVal)
{
	SetProperty(0x20, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontHeading4()
{
	LPDISPATCH pDispatch;
	GetProperty(0x21, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontHeading4(LPDISPATCH propVal)
{
	SetProperty(0x21, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontHeading5()
{
	LPDISPATCH pDispatch;
	GetProperty(0x22, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontHeading5(LPDISPATCH propVal)
{
	SetProperty(0x22, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontHeading6()
{
	LPDISPATCH pDispatch;
	GetProperty(0x23, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontHeading6(LPDISPATCH propVal)
{
	SetProperty(0x23, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontMenu()
{
	LPDISPATCH pDispatch;
	GetProperty(0x24, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontMenu(LPDISPATCH propVal)
{
	SetProperty(0x24, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontDir()
{
	LPDISPATCH pDispatch;
	GetProperty(0x25, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontDir(LPDISPATCH propVal)
{
	SetProperty(0x25, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontBlockQuote()
{
	LPDISPATCH pDispatch;
	GetProperty(0x26, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontBlockQuote(LPDISPATCH propVal)
{
	SetProperty(0x26, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontExample()
{
	LPDISPATCH pDispatch;
	GetProperty(0x27, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontExample(LPDISPATCH propVal)
{
	SetProperty(0x27, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontPreformatted()
{
	LPDISPATCH pDispatch;
	GetProperty(0x28, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontPreformatted(LPDISPATCH propVal)
{
	SetProperty(0x28, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontListing()
{
	LPDISPATCH pDispatch;
	GetProperty(0x29, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontListing(LPDISPATCH propVal)
{
	SetProperty(0x29, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontNormal()
{
	LPDISPATCH pDispatch;
	GetProperty(0x2a, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontNormal(LPDISPATCH propVal)
{
	SetProperty(0x2a, VT_DISPATCH, propVal);
}

COleFont CWebsterPro::GetFontAddress()
{
	LPDISPATCH pDispatch;
	GetProperty(0x2b, VT_DISPATCH, (void*)&pDispatch);
	return COleFont(pDispatch);
}

void CWebsterPro::SetFontAddress(LPDISPATCH propVal)
{
	SetProperty(0x2b, VT_DISPATCH, propVal);
}

unsigned long CWebsterPro::GetBevelColorTop()
{
	unsigned long result;
	GetProperty(0x4, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetBevelColorTop(unsigned long propVal)
{
	SetProperty(0x4, VT_I4, propVal);
}

unsigned long CWebsterPro::GetBevelColorDark()
{
	unsigned long result;
	GetProperty(0x5, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetBevelColorDark(unsigned long propVal)
{
	SetProperty(0x5, VT_I4, propVal);
}

unsigned long CWebsterPro::GetBevelColorLight()
{
	unsigned long result;
	GetProperty(0x6, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetBevelColorLight(unsigned long propVal)
{
	SetProperty(0x6, VT_I4, propVal);
}

long CWebsterPro::GetUrlWindowStyle()
{
	long result;
	GetProperty(0x7, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetUrlWindowStyle(long propVal)
{
	SetProperty(0x7, VT_I4, propVal);
}

long CWebsterPro::GetTitleWindowStyle()
{
	long result;
	GetProperty(0x8, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetTitleWindowStyle(long propVal)
{
	SetProperty(0x8, VT_I4, propVal);
}

CString CWebsterPro::GetPageURL()
{
	CString result;
	GetProperty(0x9, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetPageURL(LPCTSTR propVal)
{
	SetProperty(0x9, VT_BSTR, propVal);
}

CString CWebsterPro::GetPageTitle()
{
	CString result;
	GetProperty(0xa, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetPageTitle(LPCTSTR propVal)
{
	SetProperty(0xa, VT_BSTR, propVal);
}

unsigned long CWebsterPro::GetAnchorColor()
{
	unsigned long result;
	GetProperty(0xb, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetAnchorColor(unsigned long propVal)
{
	SetProperty(0xb, VT_I4, propVal);
}

CString CWebsterPro::GetHomePage()
{
	CString result;
	GetProperty(0xc, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetHomePage(LPCTSTR propVal)
{
	SetProperty(0xc, VT_BSTR, propVal);
}

CString CWebsterPro::GetDownloadDir()
{
	CString result;
	GetProperty(0xd, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetDownloadDir(LPCTSTR propVal)
{
	SetProperty(0xd, VT_BSTR, propVal);
}

long CWebsterPro::GetPagesToCache()
{
	long result;
	GetProperty(0xe, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetPagesToCache(long propVal)
{
	SetProperty(0xe, VT_I4, propVal);
}

OLE_COLOR CWebsterPro::GetBackColor()
{
	OLE_COLOR result;
	GetProperty(DISPID_BACKCOLOR, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetBackColor(OLE_COLOR propVal)
{
	SetProperty(DISPID_BACKCOLOR, VT_I4, propVal);
}

BOOL CWebsterPro::GetIgnoreBaseInFile()
{
	BOOL result;
	GetProperty(0xf, VT_BOOL, (void*)&result);
	return result;
}

void CWebsterPro::SetIgnoreBaseInFile(BOOL propVal)
{
	SetProperty(0xf, VT_BOOL, propVal);
}

long CWebsterPro::GetLoadStatus()
{
	long result;
	GetProperty(0x2c, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetLoadStatus(long propVal)
{
	SetProperty(0x2c, VT_I4, propVal);
}

OLE_COLOR CWebsterPro::GetForeColor()
{
	OLE_COLOR result;
	GetProperty(DISPID_FORECOLOR, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetForeColor(OLE_COLOR propVal)
{
	SetProperty(DISPID_FORECOLOR, VT_I4, propVal);
}

long CWebsterPro::GetMaxSockets()
{
	long result;
	GetProperty(0x10, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetMaxSockets(long propVal)
{
	SetProperty(0x10, VT_I4, propVal);
}

long CWebsterPro::GetMaxPageLoads()
{
	long result;
	GetProperty(0x11, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetMaxPageLoads(long propVal)
{
	SetProperty(0x11, VT_I4, propVal);
}

long CWebsterPro::GetMarginHorizontal()
{
	long result;
	GetProperty(0x12, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetMarginHorizontal(long propVal)
{
	SetProperty(0x12, VT_I4, propVal);
}

long CWebsterPro::GetMarginVertical()
{
	long result;
	GetProperty(0x13, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetMarginVertical(long propVal)
{
	SetProperty(0x13, VT_I4, propVal);
}

BOOL CWebsterPro::GetLoadImages()
{
	BOOL result;
	GetProperty(0x14, VT_BOOL, (void*)&result);
	return result;
}

void CWebsterPro::SetLoadImages(BOOL propVal)
{
	SetProperty(0x14, VT_BOOL, propVal);
}

BOOL CWebsterPro::GetShowReferer()
{
	BOOL result;
	GetProperty(0x15, VT_BOOL, (void*)&result);
	return result;
}

void CWebsterPro::SetShowReferer(BOOL propVal)
{
	SetProperty(0x15, VT_BOOL, propVal);
}

CString CWebsterPro::GetAuthenticName()
{
	CString result;
	GetProperty(0x16, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetAuthenticName(LPCTSTR propVal)
{
	SetProperty(0x16, VT_BSTR, propVal);
}

CString CWebsterPro::GetAuthenticPassword()
{
	CString result;
	GetProperty(0x17, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetAuthenticPassword(LPCTSTR propVal)
{
	SetProperty(0x17, VT_BSTR, propVal);
}

CString CWebsterPro::GetFromName()
{
	CString result;
	GetProperty(0x18, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetFromName(LPCTSTR propVal)
{
	SetProperty(0x18, VT_BSTR, propVal);
}

CString CWebsterPro::GetBrowserName()
{
	CString result;
	GetProperty(0x19, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetBrowserName(LPCTSTR propVal)
{
	SetProperty(0x19, VT_BSTR, propVal);
}

long CWebsterPro::GetButtonMask()
{
	long result;
	GetProperty(0x1a, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetButtonMask(long propVal)
{
	SetProperty(0x1a, VT_I4, propVal);
}

CString CWebsterPro::GetProxyServerHTTP()
{
	CString result;
	GetProperty(0x1b, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetProxyServerHTTP(LPCTSTR propVal)
{
	SetProperty(0x1b, VT_BSTR, propVal);
}

long CWebsterPro::GetProxyPortHTTP()
{
	long result;
	GetProperty(0x1c, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetProxyPortHTTP(long propVal)
{
	SetProperty(0x1c, VT_I4, propVal);
}

long CWebsterPro::GetImageCacheKB()
{
	long result;
	GetProperty(0x1d, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetImageCacheKB(long propVal)
{
	SetProperty(0x1d, VT_I4, propVal);
}

CString CWebsterPro::GetShortcutDir()
{
	CString result;
	GetProperty(0x4b, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetShortcutDir(LPCTSTR propVal)
{
	SetProperty(0x4b, VT_BSTR, propVal);
}

LPDISPATCH CWebsterPro::GetProxyExclusionsHTTP()
{
	LPDISPATCH result;
	GetProperty(0x51, VT_DISPATCH, (void*)&result);
	return result;
}

void CWebsterPro::SetProxyExclusionsHTTP(LPDISPATCH propVal)
{
	SetProperty(0x51, VT_DISPATCH, propVal);
}

long CWebsterPro::GetScrollbarStyleVertical()
{
	long result;
	GetProperty(0x52, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetScrollbarStyleVertical(long propVal)
{
	SetProperty(0x52, VT_I4, propVal);
}

long CWebsterPro::GetScrollbarStyleHorizontal()
{
	long result;
	GetProperty(0x53, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetScrollbarStyleHorizontal(long propVal)
{
	SetProperty(0x53, VT_I4, propVal);
}

long CWebsterPro::GetScrollPosVertical()
{
	long result;
	GetProperty(0x54, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetScrollPosVertical(long propVal)
{
	SetProperty(0x54, VT_I4, propVal);
}

long CWebsterPro::GetScrollPosHorizontal()
{
	long result;
	GetProperty(0x55, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetScrollPosHorizontal(long propVal)
{
	SetProperty(0x55, VT_I4, propVal);
}

long CWebsterPro::GetPageWidth()
{
	long result;
	GetProperty(0x56, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetPageWidth(long propVal)
{
	SetProperty(0x56, VT_I4, propVal);
}

long CWebsterPro::GetPageHeight()
{
	long result;
	GetProperty(0x57, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetPageHeight(long propVal)
{
	SetProperty(0x57, VT_I4, propVal);
}

long CWebsterPro::GetDisplayLeft()
{
	long result;
	GetProperty(0x58, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetDisplayLeft(long propVal)
{
	SetProperty(0x58, VT_I4, propVal);
}

long CWebsterPro::GetDisplayTop()
{
	long result;
	GetProperty(0x59, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetDisplayTop(long propVal)
{
	SetProperty(0x59, VT_I4, propVal);
}

long CWebsterPro::GetDisplayWidth()
{
	long result;
	GetProperty(0x5a, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetDisplayWidth(long propVal)
{
	SetProperty(0x5a, VT_I4, propVal);
}

long CWebsterPro::GetDisplayHeight()
{
	long result;
	GetProperty(0x5b, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetDisplayHeight(long propVal)
{
	SetProperty(0x5b, VT_I4, propVal);
}

LPDISPATCH CWebsterPro::GetCachedPages()
{
	LPDISPATCH result;
	GetProperty(0x5c, VT_DISPATCH, (void*)&result);
	return result;
}

void CWebsterPro::SetCachedPages(LPDISPATCH propVal)
{
	SetProperty(0x5c, VT_DISPATCH, propVal);
}

LPDISPATCH CWebsterPro::GetHistoryPages()
{
	LPDISPATCH result;
	GetProperty(0x5d, VT_DISPATCH, (void*)&result);
	return result;
}

void CWebsterPro::SetHistoryPages(LPDISPATCH propVal)
{
	SetProperty(0x5d, VT_DISPATCH, propVal);
}

BOOL CWebsterPro::GetReloadIncludesObjects()
{
	BOOL result;
	GetProperty(0x60, VT_BOOL, (void*)&result);
	return result;
}

void CWebsterPro::SetReloadIncludesObjects(BOOL propVal)
{
	SetProperty(0x60, VT_BOOL, propVal);
}

BOOL CWebsterPro::GetPaletteForceBackground()
{
	BOOL result;
	GetProperty(0x61, VT_BOOL, (void*)&result);
	return result;
}

void CWebsterPro::SetPaletteForceBackground(BOOL propVal)
{
	SetProperty(0x61, VT_BOOL, propVal);
}

BOOL CWebsterPro::GetKeepForwardHistory()
{
	BOOL result;
	GetProperty(0x62, VT_BOOL, (void*)&result);
	return result;
}

void CWebsterPro::SetKeepForwardHistory(BOOL propVal)
{
	SetProperty(0x62, VT_BOOL, propVal);
}

CString CWebsterPro::GetCookiesDir()
{
	CString result;
	GetProperty(0x64, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetCookiesDir(LPCTSTR propVal)
{
	SetProperty(0x64, VT_BSTR, propVal);
}

long CWebsterPro::GetCookieControl()
{
	long result;
	GetProperty(0x65, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetCookieControl(long propVal)
{
	SetProperty(0x65, VT_I4, propVal);
}

long CWebsterPro::GetSelectionState()
{
	long result;
	GetProperty(0x6c, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetSelectionState(long propVal)
{
	SetProperty(0x6c, VT_I4, propVal);
}

long CWebsterPro::GetSelectionStartOffset()
{
	long result;
	GetProperty(0x6d, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetSelectionStartOffset(long propVal)
{
	SetProperty(0x6d, VT_I4, propVal);
}

long CWebsterPro::GetSelectionLength()
{
	long result;
	GetProperty(0x6e, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetSelectionLength(long propVal)
{
	SetProperty(0x6e, VT_I4, propVal);
}

CString CWebsterPro::GetProxyServerUserNameHTTP()
{
	CString result;
	GetProperty(0x6f, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetProxyServerUserNameHTTP(LPCTSTR propVal)
{
	SetProperty(0x6f, VT_BSTR, propVal);
}

CString CWebsterPro::GetProxyServerPasswordHTTP()
{
	CString result;
	GetProperty(0x70, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::SetProxyServerPasswordHTTP(LPCTSTR propVal)
{
	SetProperty(0x70, VT_BSTR, propVal);
}

BOOL CWebsterPro::GetNoFrames()
{
	BOOL result;
	GetProperty(0x72, VT_BOOL, (void*)&result);
	return result;
}

void CWebsterPro::SetNoFrames(BOOL propVal)
{
	SetProperty(0x72, VT_BOOL, propVal);
}

long CWebsterPro::GetPageObjectHandle()
{
	long result;
	GetProperty(0x79, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetPageObjectHandle(long propVal)
{
	SetProperty(0x79, VT_I4, propVal);
}

long CWebsterPro::GetFocusPageObjectHandle()
{
	long result;
	GetProperty(0x7a, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetFocusPageObjectHandle(long propVal)
{
	SetProperty(0x7a, VT_I4, propVal);
}

long CWebsterPro::GetButtonEnabledMask()
{
	long result;
	GetProperty(0x7c, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetButtonEnabledMask(long propVal)
{
	SetProperty(0x7c, VT_I4, propVal);
}

long CWebsterPro::GetMenuControl()
{
	long result;
	GetProperty(0x7d, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetMenuControl(long propVal)
{
	SetProperty(0x7d, VT_I4, propVal);
}

long CWebsterPro::GetAnimationControl()
{
	long result;
	GetProperty(0x7e, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetAnimationControl(long propVal)
{
	SetProperty(0x7e, VT_I4, propVal);
}

long CWebsterPro::GetLayoutControl()
{
	long result;
	GetProperty(0x7f, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetLayoutControl(long propVal)
{
	SetProperty(0x7f, VT_I4, propVal);
}

long CWebsterPro::GetPaletteHandle()
{
	long result;
	GetProperty(0x80, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetPaletteHandle(long propVal)
{
	SetProperty(0x80, VT_I4, propVal);
}

long CWebsterPro::GetPrintBackgroundColors()
{
	long result;
	GetProperty(0x81, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetPrintBackgroundColors(long propVal)
{
	SetProperty(0x81, VT_I4, propVal);
}

long CWebsterPro::GetToolTipStyle()
{
	long result;
	GetProperty(0x83, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetToolTipStyle(long propVal)
{
	SetProperty(0x83, VT_I4, propVal);
}

long CWebsterPro::GetCursorHandle()
{
	long result;
	GetProperty(0x84, VT_I4, (void*)&result);
	return result;
}

void CWebsterPro::SetCursorHandle(long propVal)
{
	SetProperty(0x84, VT_I4, propVal);
}

CString CWebsterPro::Get_PageURL()
{
	CString result;
	GetProperty(0x0, VT_BSTR, (void*)&result);
	return result;
}

void CWebsterPro::Set_PageURL(LPCTSTR propVal)
{
	SetProperty(0x0, VT_BSTR, propVal);
}

/////////////////////////////////////////////////////////////////////////////
// CWebsterPro operations

void CWebsterPro::Refresh()
{
	InvokeHelper(DISPID_REFRESH, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

short CWebsterPro::SaveToDisk(LPCTSTR FileName)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x2d, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		FileName);
	return result;
}

short CWebsterPro::Cancel()
{
	short result;
	InvokeHelper(0x2e, DISPATCH_METHOD, VT_I2, (void*)&result, NULL);
	return result;
}

long CWebsterPro::GetContentSize(LPCTSTR URL)
{
	long result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x2f, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		URL);
	return result;
}

long CWebsterPro::GetContentSizeRead(LPCTSTR URL)
{
	long result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x30, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		URL);
	return result;
}

CString CWebsterPro::GetContentType(LPCTSTR URL)
{
	CString result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x31, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		URL);
	return result;
}

CString CWebsterPro::GetRedirectedURL(LPCTSTR URL)
{
	CString result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x32, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		URL);
	return result;
}

short CWebsterPro::GetHiddenFlag(LPCTSTR URL)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x33, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL);
	return result;
}

short CWebsterPro::SetHiddenFlag(LPCTSTR URL, BOOL Hidden)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR VTS_BOOL;
	InvokeHelper(0x34, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL, Hidden);
	return result;
}

short CWebsterPro::DismissPage(LPCTSTR URL)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x35, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL);
	return result;
}

long CWebsterPro::GetLinkCount(LPCTSTR URL)
{
	long result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x36, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		URL);
	return result;
}

CString CWebsterPro::GetLinkURL(LPCTSTR URL, long Index)
{
	CString result;
	static BYTE parms[] =
		VTS_BSTR VTS_I4;
	InvokeHelper(0x37, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		URL, Index);
	return result;
}

CString CWebsterPro::GetContent(LPCTSTR URL, long StartOffset, long Length)
{
	CString result;
	static BYTE parms[] =
		VTS_BSTR VTS_I4 VTS_I4;
	InvokeHelper(0x38, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		URL, StartOffset, Length);
	return result;
}

short CWebsterPro::GetStatus(LPCTSTR URL)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x39, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL);
	return result;
}

CString CWebsterPro::GetTitle(LPCTSTR URL)
{
	CString result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x3a, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		URL);
	return result;
}

CString CWebsterPro::GetText(LPCTSTR URL, long StartOffset, long Length)
{
	CString result;
	static BYTE parms[] =
		VTS_BSTR VTS_I4 VTS_I4;
	InvokeHelper(0x3b, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		URL, StartOffset, Length);
	return result;
}

short CWebsterPro::LoadPage(LPCTSTR URL, short Hidden)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR VTS_I2;
	InvokeHelper(0x3c, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL, Hidden);
	return result;
}

long CWebsterPro::GetTextSize(LPCTSTR URL)
{
	long result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x3d, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		URL);
	return result;
}

void CWebsterPro::GoHome()
{
	InvokeHelper(0x3e, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

void CWebsterPro::ShowHistory()
{
	InvokeHelper(0x3f, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

void CWebsterPro::ShowStatus()
{
	InvokeHelper(0x40, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

void CWebsterPro::PageBack()
{
	InvokeHelper(0x41, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

void CWebsterPro::PageForth()
{
	InvokeHelper(0x42, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

void CWebsterPro::Reload()
{
	InvokeHelper(0x43, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

void CWebsterPro::ShowDir()
{
	InvokeHelper(0x44, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

short CWebsterPro::ShowOpenFileDialog(LPCTSTR DefaultFile)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x45, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		DefaultFile);
	return result;
}

short CWebsterPro::ShowURLDialog(LPCTSTR DefaultURL)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x46, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		DefaultURL);
	return result;
}

long CWebsterPro::PrintToDC(long hDC, long lPageNum, BOOL bPreview)
{
	long result;
	static BYTE parms[] =
		VTS_I4 VTS_I4 VTS_BOOL;
	InvokeHelper(0x47, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		hDC, lPageNum, bPreview);
	return result;
}

long CWebsterPro::Paginate(long hDC, long lPageLeft, long lPageTop, long lPageRight, long lPageBottom, long plTotalPages)
{
	long result;
	static BYTE parms[] =
		VTS_I4 VTS_I4 VTS_I4 VTS_I4 VTS_I4 VTS_I4;
	InvokeHelper(0x48, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		hDC, lPageLeft, lPageTop, lPageRight, lPageBottom, plTotalPages);
	return result;
}

void CWebsterPro::EndPrint()
{
	InvokeHelper(0x49, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

long CWebsterPro::DoPrint(BOOL bShowPrinterDialog, long fromPage, long toPage)
{
	long result;
	static BYTE parms[] =
		VTS_BOOL VTS_I4 VTS_I4;
	InvokeHelper(0x4a, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		bShowPrinterDialog, fromPage, toPage);
	return result;
}

CString CWebsterPro::GetHTTPHeader(LPCTSTR URL)
{
	CString result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x4c, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		URL);
	return result;
}

short CWebsterPro::AddToFavorites(LPCTSTR URL, BOOL bShowSaveDialog)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR VTS_BOOL;
	InvokeHelper(0x4d, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL, bShowSaveDialog);
	return result;
}

short CWebsterPro::ShowFavoritesDialog()
{
	short result;
	InvokeHelper(0x4e, DISPATCH_METHOD, VT_I2, (void*)&result, NULL);
	return result;
}

short CWebsterPro::LoadHeader(LPCTSTR URL, short Hidden)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR VTS_I2;
	InvokeHelper(0x4f, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL, Hidden);
	return result;
}

short CWebsterPro::PostText(LPCTSTR URL, LPCTSTR TextToPost, short Hidden)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR VTS_BSTR VTS_I2;
	InvokeHelper(0x50, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL, TextToPost, Hidden);
	return result;
}

LPDISPATCH CWebsterPro::GetEmbeddedObjectURLs(LPCTSTR URL)
{
	LPDISPATCH result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x5e, DISPATCH_METHOD, VT_DISPATCH, (void*)&result, parms,
		URL);
	return result;
}

long CWebsterPro::GetObjectAtXY(long x, long y, BSTR* pObjectURL, BSTR* pHyperlinkURL, long* plReserved1)
{
	long result;
	static BYTE parms[] =
		VTS_I4 VTS_I4 VTS_PBSTR VTS_PBSTR VTS_PI4;
	InvokeHelper(0x5f, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		x, y, pObjectURL, pHyperlinkURL, plReserved1);
	return result;
}

long CWebsterPro::FindString(BOOL bShowFindDialog, LPCTSTR StringToFind, BOOL MatchCase, BOOL Reverse)
{
	long result;
	static BYTE parms[] =
		VTS_BOOL VTS_BSTR VTS_BOOL VTS_BOOL;
	InvokeHelper(0x66, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		bShowFindDialog, StringToFind, MatchCase, Reverse);
	return result;
}

long CWebsterPro::SelectText(long StartOffset, long Length)
{
	long result;
	static BYTE parms[] =
		VTS_I4 VTS_I4;
	InvokeHelper(0x67, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		StartOffset, Length);
	return result;
}

long CWebsterPro::SelectAllText()
{
	long result;
	InvokeHelper(0x68, DISPATCH_METHOD, VT_I4, (void*)&result, NULL);
	return result;
}

long CWebsterPro::CopySelectedText()
{
	long result;
	InvokeHelper(0x69, DISPATCH_METHOD, VT_I4, (void*)&result, NULL);
	return result;
}

void CWebsterPro::ClearTextSelection()
{
	InvokeHelper(0x6a, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

void CWebsterPro::ScrollToSelectedText()
{
	InvokeHelper(0x6b, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}

long CWebsterPro::SaveObjectToFile(LPCTSTR ObjectUrl, LPCTSTR FileName, BOOL bShowSaveDialog)
{
	long result;
	static BYTE parms[] =
		VTS_BSTR VTS_BSTR VTS_BOOL;
	InvokeHelper(0x71, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		ObjectUrl, FileName, bShowSaveDialog);
	return result;
}

LPDISPATCH CWebsterPro::GetFrameURLs(LPCTSTR URL)
{
	LPDISPATCH result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x73, DISPATCH_METHOD, VT_DISPATCH, (void*)&result, parms,
		URL);
	return result;
}

long CWebsterPro::GetSingleObjectHandle(LPCTSTR URL)
{
	long result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x74, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		URL);
	return result;
}

CString CWebsterPro::GetURLByObjectHandle(long hObject)
{
	CString result;
	static BYTE parms[] =
		VTS_I4;
	InvokeHelper(0x75, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		hObject);
	return result;
}

long CWebsterPro::GetObjecthWnd(LPCTSTR URL)
{
	long result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x76, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		URL);
	return result;
}

long CWebsterPro::GethWndByObjectHandle(long hObject)
{
	long result;
	static BYTE parms[] =
		VTS_I4;
	InvokeHelper(0x77, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		hObject);
	return result;
}

LPDISPATCH CWebsterPro::GetFrameObjectHandles(long hObject)
{
	LPDISPATCH result;
	static BYTE parms[] =
		VTS_I4;
	InvokeHelper(0x78, DISPATCH_METHOD, VT_DISPATCH, (void*)&result, parms,
		hObject);
	return result;
}

short CWebsterPro::Navigate(LPCTSTR URL, long NavFlags, long nHandle, LPCTSTR TargetName, LPCTSTR TextToPost, LPCTSTR ExtraHeaders)
{
	short result;
	static BYTE parms[] =
		VTS_BSTR VTS_I4 VTS_I4 VTS_BSTR VTS_BSTR VTS_BSTR;
	InvokeHelper(0x7b, DISPATCH_METHOD, VT_I2, (void*)&result, parms,
		URL, NavFlags, nHandle, TargetName, TextToPost, ExtraHeaders);
	return result;
}

long CWebsterPro::Paginate2(long hDC, long lPageLeft, long lPageTop, long lPageRight, long lPageBottom, long* plTotalPages)
{
	long result;
	static BYTE parms[] =
		VTS_I4 VTS_I4 VTS_I4 VTS_I4 VTS_I4 VTS_PI4;
	InvokeHelper(0x82, DISPATCH_METHOD, VT_I4, (void*)&result, parms,
		hDC, lPageLeft, lPageTop, lPageRight, lPageBottom, plTotalPages);
	return result;
}

void CWebsterPro::AboutBox()
{
	InvokeHelper(0xfffffdd8, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}
