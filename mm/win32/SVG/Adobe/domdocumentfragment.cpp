// Machine generated IDispatch wrapper class(es) created by Microsoft Visual C++

// NOTE: Do not modify the contents of this file.  If this class is regenerated by
//  Microsoft Visual C++, your modifications will be overwritten.


#include "stdafx.h"
#include "domdocumentfragment.h"

// Dispatch interfaces referenced by this interface
#include "domnode.h"
#include "domnodelist.h"
#include "domnamednodemap.h"
#include "domdocument.h"


/////////////////////////////////////////////////////////////////////////////
// CDOMDocumentFragment properties

/////////////////////////////////////////////////////////////////////////////
// CDOMDocumentFragment operations

CString CDOMDocumentFragment::GetNodeName()
{
	CString result;
	InvokeHelper(0x2, DISPATCH_PROPERTYGET, VT_BSTR, (void*)&result, NULL);
	return result;
}

VARIANT CDOMDocumentFragment::GetNodeValue()
{
	VARIANT result;
	InvokeHelper(0x3, DISPATCH_PROPERTYGET, VT_VARIANT, (void*)&result, NULL);
	return result;
}

void CDOMDocumentFragment::SetNodeValue(const VARIANT& newValue)
{
	static BYTE parms[] =
		VTS_VARIANT;
	InvokeHelper(0x3, DISPATCH_PROPERTYPUT, VT_EMPTY, NULL, parms,
		 &newValue);
}

long CDOMDocumentFragment::GetNodeType()
{
	long result;
	InvokeHelper(0x4, DISPATCH_PROPERTYGET, VT_I4, (void*)&result, NULL);
	return result;
}

CDOMNode CDOMDocumentFragment::GetParentNode()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x6, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNodeList CDOMDocumentFragment::GetChildNodes()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x7, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNodeList(pDispatch);
}

CDOMNode CDOMDocumentFragment::GetFirstChild()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x8, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMDocumentFragment::GetLastChild()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x9, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMDocumentFragment::GetPreviousSibling()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xa, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMDocumentFragment::GetNextSibling()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xb, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNamedNodeMap CDOMDocumentFragment::GetAttributes()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xc, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNamedNodeMap(pDispatch);
}

CDOMNode CDOMDocumentFragment::insertBefore(LPDISPATCH newChild, const VARIANT& refChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH VTS_VARIANT;
	InvokeHelper(0xd, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild, &refChild);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMDocumentFragment::replaceChild(LPDISPATCH newChild, LPDISPATCH oldChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH VTS_DISPATCH;
	InvokeHelper(0xe, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild, oldChild);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMDocumentFragment::removeChild(LPDISPATCH childNode)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0xf, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		childNode);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMDocumentFragment::appendChild(LPDISPATCH newChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0x10, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild);
	return CDOMNode(pDispatch);
}

BOOL CDOMDocumentFragment::hasChildNodes()
{
	BOOL result;
	InvokeHelper(0x11, DISPATCH_METHOD, VT_BOOL, (void*)&result, NULL);
	return result;
}

CDOMDocument CDOMDocumentFragment::GetOwnerDocument()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x12, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMDocument(pDispatch);
}

CDOMNode CDOMDocumentFragment::cloneNode(BOOL deep)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_BOOL;
	InvokeHelper(0x13, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		deep);
	return CDOMNode(pDispatch);
}