/* this ALWAYS GENERATED file contains the definitions for the interfaces */


/* File created by MIDL compiler version 3.01.75 */
/* at Fri Dec 03 17:05:13 1999
 */
/* Compiler settings for .\propmap.idl:
    Os (OptLev=s), W1, Zp8, env=Win32, ms_ext, c_ext
    error checks: none
*/
//@@MIDL_FILE_HEADING(  )
#include "rpc.h"
#include "rpcndr.h"
#ifndef COM_NO_WINDOWS_H
#include "windows.h"
#include "ole2.h"
#endif /*COM_NO_WINDOWS_H*/

#ifndef __propmap_h__
#define __propmap_h__

#ifdef __cplusplus
extern "C"{
#endif 

/* Forward Declarations */ 

#ifndef __IEnumPropertyMap_FWD_DEFINED__
#define __IEnumPropertyMap_FWD_DEFINED__
typedef interface IEnumPropertyMap IEnumPropertyMap;
#endif 	/* __IEnumPropertyMap_FWD_DEFINED__ */


#ifndef __IPropertyMap_FWD_DEFINED__
#define __IPropertyMap_FWD_DEFINED__
typedef interface IPropertyMap IPropertyMap;
#endif 	/* __IPropertyMap_FWD_DEFINED__ */


/* header files for imported files */
#include "oaidl.h"
#include "ocidl.h"

void __RPC_FAR * __RPC_USER MIDL_user_allocate(size_t);
void __RPC_USER MIDL_user_free( void __RPC_FAR * ); 

/****************************************
 * Generated header for interface: __MIDL_itf_propmap_0000
 * at Fri Dec 03 17:05:13 1999
 * using MIDL 3.01.75
 ****************************************/
/* [local] */ 


//+-------------------------------------------------------------------------
//
//  Microsoft NetShow
//  Copyright (C) Microsoft Corporation 1998.
//
//  Automatically generated by Midl from propmap.idl
//
//  DO NOT EDIT THIS FILE.
//
//--------------------------------------------------------------------------
#ifndef _LPENUMPROPERTYMAP_DEFINED
#define _LPENUMPROPERTYMAP_DEFINED


extern RPC_IF_HANDLE __MIDL_itf_propmap_0000_v0_0_c_ifspec;
extern RPC_IF_HANDLE __MIDL_itf_propmap_0000_v0_0_s_ifspec;

#ifndef __IEnumPropertyMap_INTERFACE_DEFINED__
#define __IEnumPropertyMap_INTERFACE_DEFINED__

/****************************************
 * Generated header for interface: IEnumPropertyMap
 * at Fri Dec 03 17:05:13 1999
 * using MIDL 3.01.75
 ****************************************/
/* [unique][uuid][object][local] */ 


typedef /* [unique] */ IEnumPropertyMap __RPC_FAR *LPENUMPROPERTYMAP;

typedef struct  _tagSTATPROPMAP
    {
    LPOLESTR pstrName;
    DWORD dwFlags;
    VARIANT variantValue;
    }	STATPROPMAP;

typedef struct _tagSTATPROPMAP __RPC_FAR *LPSTATPROPMAP;


EXTERN_C const IID IID_IEnumPropertyMap;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    interface DECLSPEC_UUID("c733e4a1-576e-11d0-b28c-00c04fd7cd22")
    IEnumPropertyMap : public IUnknown
    {
    public:
        virtual /* [local] */ HRESULT STDMETHODCALLTYPE Next( 
            /* [in] */ ULONG celt,
            /* [length_is][size_is][out] */ STATPROPMAP __RPC_FAR *rgelt,
            /* [out] */ ULONG __RPC_FAR *pceltFetched) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE Skip( 
            /* [in] */ ULONG celt) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE Reset( void) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE Clone( 
            /* [out] */ IEnumPropertyMap __RPC_FAR *__RPC_FAR *ppenum) = 0;
        
    };
    
#else 	/* C style interface */

    typedef struct IEnumPropertyMapVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *QueryInterface )( 
            IEnumPropertyMap __RPC_FAR * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ void __RPC_FAR *__RPC_FAR *ppvObject);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *AddRef )( 
            IEnumPropertyMap __RPC_FAR * This);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *Release )( 
            IEnumPropertyMap __RPC_FAR * This);
        
        /* [local] */ HRESULT ( STDMETHODCALLTYPE __RPC_FAR *Next )( 
            IEnumPropertyMap __RPC_FAR * This,
            /* [in] */ ULONG celt,
            /* [length_is][size_is][out] */ STATPROPMAP __RPC_FAR *rgelt,
            /* [out] */ ULONG __RPC_FAR *pceltFetched);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *Skip )( 
            IEnumPropertyMap __RPC_FAR * This,
            /* [in] */ ULONG celt);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *Reset )( 
            IEnumPropertyMap __RPC_FAR * This);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *Clone )( 
            IEnumPropertyMap __RPC_FAR * This,
            /* [out] */ IEnumPropertyMap __RPC_FAR *__RPC_FAR *ppenum);
        
        END_INTERFACE
    } IEnumPropertyMapVtbl;

    interface IEnumPropertyMap
    {
        CONST_VTBL struct IEnumPropertyMapVtbl __RPC_FAR *lpVtbl;
    };

    

#ifdef COBJMACROS


#define IEnumPropertyMap_QueryInterface(This,riid,ppvObject)	\
    (This)->lpVtbl -> QueryInterface(This,riid,ppvObject)

#define IEnumPropertyMap_AddRef(This)	\
    (This)->lpVtbl -> AddRef(This)

#define IEnumPropertyMap_Release(This)	\
    (This)->lpVtbl -> Release(This)


#define IEnumPropertyMap_Next(This,celt,rgelt,pceltFetched)	\
    (This)->lpVtbl -> Next(This,celt,rgelt,pceltFetched)

#define IEnumPropertyMap_Skip(This,celt)	\
    (This)->lpVtbl -> Skip(This,celt)

#define IEnumPropertyMap_Reset(This)	\
    (This)->lpVtbl -> Reset(This)

#define IEnumPropertyMap_Clone(This,ppenum)	\
    (This)->lpVtbl -> Clone(This,ppenum)

#endif /* COBJMACROS */


#endif 	/* C style interface */



/* [call_as] */ HRESULT STDMETHODCALLTYPE IEnumPropertyMap_RemoteNext_Proxy( 
    IEnumPropertyMap __RPC_FAR * This,
    /* [in] */ ULONG celt,
    /* [length_is][size_is][out] */ STATPROPMAP __RPC_FAR *rgelt,
    /* [out] */ ULONG __RPC_FAR *pceltFetched);


void __RPC_STUB IEnumPropertyMap_RemoteNext_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE IEnumPropertyMap_Skip_Proxy( 
    IEnumPropertyMap __RPC_FAR * This,
    /* [in] */ ULONG celt);


void __RPC_STUB IEnumPropertyMap_Skip_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE IEnumPropertyMap_Reset_Proxy( 
    IEnumPropertyMap __RPC_FAR * This);


void __RPC_STUB IEnumPropertyMap_Reset_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE IEnumPropertyMap_Clone_Proxy( 
    IEnumPropertyMap __RPC_FAR * This,
    /* [out] */ IEnumPropertyMap __RPC_FAR *__RPC_FAR *ppenum);


void __RPC_STUB IEnumPropertyMap_Clone_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);



#endif 	/* __IEnumPropertyMap_INTERFACE_DEFINED__ */


/****************************************
 * Generated header for interface: __MIDL_itf_propmap_0192
 * at Fri Dec 03 17:05:13 1999
 * using MIDL 3.01.75
 ****************************************/
/* [local] */ 


#endif
#ifndef _LPPROPERTYMAP
#define _LPPROPERTYMAP


extern RPC_IF_HANDLE __MIDL_itf_propmap_0192_v0_0_c_ifspec;
extern RPC_IF_HANDLE __MIDL_itf_propmap_0192_v0_0_s_ifspec;

#ifndef __IPropertyMap_INTERFACE_DEFINED__
#define __IPropertyMap_INTERFACE_DEFINED__

/****************************************
 * Generated header for interface: IPropertyMap
 * at Fri Dec 03 17:05:13 1999
 * using MIDL 3.01.75
 ****************************************/
/* [unique][uuid][object][local] */ 


typedef /* [unique] */ IPropertyMap __RPC_FAR *LPPROPERTYMAP;


EXTERN_C const IID IID_IPropertyMap;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    interface DECLSPEC_UUID("c733e4a2-576e-11d0-b28c-00c04fd7cd22")
    IPropertyMap : public IUnknown
    {
    public:
        virtual HRESULT STDMETHODCALLTYPE Write( 
            /* [in] */ LPCWSTR pstrName,
            /* [in] */ VARIANT variantValue,
            /* [in] */ DWORD dwFlags) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE Read( 
            /* [in] */ LPCWSTR pstrName,
            /* [out] */ VARIANT __RPC_FAR *pVariantValue) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE GetCount( 
            /* [out] */ ULONG __RPC_FAR *pCount) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE GetEnumMAP( 
            /* [out] */ LPENUMPROPERTYMAP __RPC_FAR *ppEnumMap) = 0;
        
    };
    
#else 	/* C style interface */

    typedef struct IPropertyMapVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *QueryInterface )( 
            IPropertyMap __RPC_FAR * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ void __RPC_FAR *__RPC_FAR *ppvObject);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *AddRef )( 
            IPropertyMap __RPC_FAR * This);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *Release )( 
            IPropertyMap __RPC_FAR * This);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *Write )( 
            IPropertyMap __RPC_FAR * This,
            /* [in] */ LPCWSTR pstrName,
            /* [in] */ VARIANT variantValue,
            /* [in] */ DWORD dwFlags);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *Read )( 
            IPropertyMap __RPC_FAR * This,
            /* [in] */ LPCWSTR pstrName,
            /* [out] */ VARIANT __RPC_FAR *pVariantValue);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *GetCount )( 
            IPropertyMap __RPC_FAR * This,
            /* [out] */ ULONG __RPC_FAR *pCount);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *GetEnumMAP )( 
            IPropertyMap __RPC_FAR * This,
            /* [out] */ LPENUMPROPERTYMAP __RPC_FAR *ppEnumMap);
        
        END_INTERFACE
    } IPropertyMapVtbl;

    interface IPropertyMap
    {
        CONST_VTBL struct IPropertyMapVtbl __RPC_FAR *lpVtbl;
    };

    

#ifdef COBJMACROS


#define IPropertyMap_QueryInterface(This,riid,ppvObject)	\
    (This)->lpVtbl -> QueryInterface(This,riid,ppvObject)

#define IPropertyMap_AddRef(This)	\
    (This)->lpVtbl -> AddRef(This)

#define IPropertyMap_Release(This)	\
    (This)->lpVtbl -> Release(This)


#define IPropertyMap_Write(This,pstrName,variantValue,dwFlags)	\
    (This)->lpVtbl -> Write(This,pstrName,variantValue,dwFlags)

#define IPropertyMap_Read(This,pstrName,pVariantValue)	\
    (This)->lpVtbl -> Read(This,pstrName,pVariantValue)

#define IPropertyMap_GetCount(This,pCount)	\
    (This)->lpVtbl -> GetCount(This,pCount)

#define IPropertyMap_GetEnumMAP(This,ppEnumMap)	\
    (This)->lpVtbl -> GetEnumMAP(This,ppEnumMap)

#endif /* COBJMACROS */


#endif 	/* C style interface */



HRESULT STDMETHODCALLTYPE IPropertyMap_Write_Proxy( 
    IPropertyMap __RPC_FAR * This,
    /* [in] */ LPCWSTR pstrName,
    /* [in] */ VARIANT variantValue,
    /* [in] */ DWORD dwFlags);


void __RPC_STUB IPropertyMap_Write_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE IPropertyMap_Read_Proxy( 
    IPropertyMap __RPC_FAR * This,
    /* [in] */ LPCWSTR pstrName,
    /* [out] */ VARIANT __RPC_FAR *pVariantValue);


void __RPC_STUB IPropertyMap_Read_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE IPropertyMap_GetCount_Proxy( 
    IPropertyMap __RPC_FAR * This,
    /* [out] */ ULONG __RPC_FAR *pCount);


void __RPC_STUB IPropertyMap_GetCount_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE IPropertyMap_GetEnumMAP_Proxy( 
    IPropertyMap __RPC_FAR * This,
    /* [out] */ LPENUMPROPERTYMAP __RPC_FAR *ppEnumMap);


void __RPC_STUB IPropertyMap_GetEnumMAP_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);



#endif 	/* __IPropertyMap_INTERFACE_DEFINED__ */


/****************************************
 * Generated header for interface: __MIDL_itf_propmap_0193
 * at Fri Dec 03 17:05:13 1999
 * using MIDL 3.01.75
 ****************************************/
/* [local] */ 


#endif


extern RPC_IF_HANDLE __MIDL_itf_propmap_0193_v0_0_c_ifspec;
extern RPC_IF_HANDLE __MIDL_itf_propmap_0193_v0_0_s_ifspec;

/* Additional Prototypes for ALL interfaces */

/* end of Additional Prototypes */

#ifdef __cplusplus
}
#endif

#endif
