/* this ALWAYS GENERATED file contains the definitions for the interfaces */


/* File created by MIDL compiler version 3.01.75 */
/* at Fri Dec 03 17:05:12 1999
 */
/* Compiler settings for .\nsscore.idl:
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

#ifndef __nsscore_h__
#define __nsscore_h__

#ifdef __cplusplus
extern "C"{
#endif 

/* Forward Declarations */ 

#ifndef __INSSServerContext_FWD_DEFINED__
#define __INSSServerContext_FWD_DEFINED__
typedef interface INSSServerContext INSSServerContext;
#endif 	/* __INSSServerContext_FWD_DEFINED__ */


#ifndef __INSSUserContext_FWD_DEFINED__
#define __INSSUserContext_FWD_DEFINED__
typedef interface INSSUserContext INSSUserContext;
#endif 	/* __INSSUserContext_FWD_DEFINED__ */


#ifndef __INSSPresentationContext_FWD_DEFINED__
#define __INSSPresentationContext_FWD_DEFINED__
typedef interface INSSPresentationContext INSSPresentationContext;
#endif 	/* __INSSPresentationContext_FWD_DEFINED__ */


#ifndef __INSSCommandContext_FWD_DEFINED__
#define __INSSCommandContext_FWD_DEFINED__
typedef interface INSSCommandContext INSSCommandContext;
#endif 	/* __INSSCommandContext_FWD_DEFINED__ */


/* header files for imported files */
#include "oaidl.h"
#include "ocidl.h"
#include "propmap.h"

void __RPC_FAR * __RPC_USER MIDL_user_allocate(size_t);
void __RPC_USER MIDL_user_free( void __RPC_FAR * ); 

/****************************************
 * Generated header for interface: __MIDL_itf_nsscore_0000
 * at Fri Dec 03 17:05:12 1999
 * using MIDL 3.01.75
 ****************************************/
/* [local] */ 


//+-------------------------------------------------------------------------
//
//  Microsoft NetShow
//  Copyright (C) Microsoft Corporation 1998.
//
//  Automatically generated by Midl from nsscore.idl
//
//  DO NOT EDIT THIS FILE.
//
//--------------------------------------------------------------------------


extern RPC_IF_HANDLE __MIDL_itf_nsscore_0000_v0_0_c_ifspec;
extern RPC_IF_HANDLE __MIDL_itf_nsscore_0000_v0_0_s_ifspec;

#ifndef __INSSServerContext_INTERFACE_DEFINED__
#define __INSSServerContext_INTERFACE_DEFINED__

/****************************************
 * Generated header for interface: INSSServerContext
 * at Fri Dec 03 17:05:12 1999
 * using MIDL 3.01.75
 ****************************************/
/* [unique][version][helpstring][uuid][object] */ 



EXTERN_C const IID IID_INSSServerContext;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    interface DECLSPEC_UUID("98999822-2002-11d1-8c94-00a0c903a1a2")
    INSSServerContext : public IUnknown
    {
    public:
    };
    
#else 	/* C style interface */

    typedef struct INSSServerContextVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *QueryInterface )( 
            INSSServerContext __RPC_FAR * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ void __RPC_FAR *__RPC_FAR *ppvObject);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *AddRef )( 
            INSSServerContext __RPC_FAR * This);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *Release )( 
            INSSServerContext __RPC_FAR * This);
        
        END_INTERFACE
    } INSSServerContextVtbl;

    interface INSSServerContext
    {
        CONST_VTBL struct INSSServerContextVtbl __RPC_FAR *lpVtbl;
    };

    

#ifdef COBJMACROS


#define INSSServerContext_QueryInterface(This,riid,ppvObject)	\
    (This)->lpVtbl -> QueryInterface(This,riid,ppvObject)

#define INSSServerContext_AddRef(This)	\
    (This)->lpVtbl -> AddRef(This)

#define INSSServerContext_Release(This)	\
    (This)->lpVtbl -> Release(This)


#endif /* COBJMACROS */


#endif 	/* C style interface */




#endif 	/* __INSSServerContext_INTERFACE_DEFINED__ */


#ifndef __INSSUserContext_INTERFACE_DEFINED__
#define __INSSUserContext_INTERFACE_DEFINED__

/****************************************
 * Generated header for interface: INSSUserContext
 * at Fri Dec 03 17:05:12 1999
 * using MIDL 3.01.75
 ****************************************/
/* [unique][version][helpstring][uuid][object] */ 



EXTERN_C const IID IID_INSSUserContext;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    interface DECLSPEC_UUID("4639f850-2003-11d1-8c94-00a0c903a1a2")
    INSSUserContext : public IUnknown
    {
    public:
    };
    
#else 	/* C style interface */

    typedef struct INSSUserContextVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *QueryInterface )( 
            INSSUserContext __RPC_FAR * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ void __RPC_FAR *__RPC_FAR *ppvObject);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *AddRef )( 
            INSSUserContext __RPC_FAR * This);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *Release )( 
            INSSUserContext __RPC_FAR * This);
        
        END_INTERFACE
    } INSSUserContextVtbl;

    interface INSSUserContext
    {
        CONST_VTBL struct INSSUserContextVtbl __RPC_FAR *lpVtbl;
    };

    

#ifdef COBJMACROS


#define INSSUserContext_QueryInterface(This,riid,ppvObject)	\
    (This)->lpVtbl -> QueryInterface(This,riid,ppvObject)

#define INSSUserContext_AddRef(This)	\
    (This)->lpVtbl -> AddRef(This)

#define INSSUserContext_Release(This)	\
    (This)->lpVtbl -> Release(This)


#endif /* COBJMACROS */


#endif 	/* C style interface */




#endif 	/* __INSSUserContext_INTERFACE_DEFINED__ */


#ifndef __INSSPresentationContext_INTERFACE_DEFINED__
#define __INSSPresentationContext_INTERFACE_DEFINED__

/****************************************
 * Generated header for interface: INSSPresentationContext
 * at Fri Dec 03 17:05:12 1999
 * using MIDL 3.01.75
 ****************************************/
/* [unique][version][helpstring][uuid][object] */ 



EXTERN_C const IID IID_INSSPresentationContext;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    interface DECLSPEC_UUID("4639f851-2003-11d1-8c94-00a0c903a1a2")
    INSSPresentationContext : public IUnknown
    {
    public:
    };
    
#else 	/* C style interface */

    typedef struct INSSPresentationContextVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *QueryInterface )( 
            INSSPresentationContext __RPC_FAR * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ void __RPC_FAR *__RPC_FAR *ppvObject);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *AddRef )( 
            INSSPresentationContext __RPC_FAR * This);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *Release )( 
            INSSPresentationContext __RPC_FAR * This);
        
        END_INTERFACE
    } INSSPresentationContextVtbl;

    interface INSSPresentationContext
    {
        CONST_VTBL struct INSSPresentationContextVtbl __RPC_FAR *lpVtbl;
    };

    

#ifdef COBJMACROS


#define INSSPresentationContext_QueryInterface(This,riid,ppvObject)	\
    (This)->lpVtbl -> QueryInterface(This,riid,ppvObject)

#define INSSPresentationContext_AddRef(This)	\
    (This)->lpVtbl -> AddRef(This)

#define INSSPresentationContext_Release(This)	\
    (This)->lpVtbl -> Release(This)


#endif /* COBJMACROS */


#endif 	/* C style interface */




#endif 	/* __INSSPresentationContext_INTERFACE_DEFINED__ */


#ifndef __INSSCommandContext_INTERFACE_DEFINED__
#define __INSSCommandContext_INTERFACE_DEFINED__

/****************************************
 * Generated header for interface: INSSCommandContext
 * at Fri Dec 03 17:05:12 1999
 * using MIDL 3.01.75
 ****************************************/
/* [unique][version][helpstring][uuid][object] */ 



EXTERN_C const IID IID_INSSCommandContext;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    interface DECLSPEC_UUID("33309E72-37CD-11d1-9E9F-006097D2D7CF")
    INSSCommandContext : public IUnknown
    {
    public:
        virtual HRESULT STDMETHODCALLTYPE GetRequestContext( 
            /* [out] */ IPropertyMap __RPC_FAR *__RPC_FAR *ppProps) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE GetResponseContext( 
            /* [out] */ IPropertyMap __RPC_FAR *__RPC_FAR *ppProps) = 0;
        
    };
    
#else 	/* C style interface */

    typedef struct INSSCommandContextVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *QueryInterface )( 
            INSSCommandContext __RPC_FAR * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ void __RPC_FAR *__RPC_FAR *ppvObject);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *AddRef )( 
            INSSCommandContext __RPC_FAR * This);
        
        ULONG ( STDMETHODCALLTYPE __RPC_FAR *Release )( 
            INSSCommandContext __RPC_FAR * This);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *GetRequestContext )( 
            INSSCommandContext __RPC_FAR * This,
            /* [out] */ IPropertyMap __RPC_FAR *__RPC_FAR *ppProps);
        
        HRESULT ( STDMETHODCALLTYPE __RPC_FAR *GetResponseContext )( 
            INSSCommandContext __RPC_FAR * This,
            /* [out] */ IPropertyMap __RPC_FAR *__RPC_FAR *ppProps);
        
        END_INTERFACE
    } INSSCommandContextVtbl;

    interface INSSCommandContext
    {
        CONST_VTBL struct INSSCommandContextVtbl __RPC_FAR *lpVtbl;
    };

    

#ifdef COBJMACROS


#define INSSCommandContext_QueryInterface(This,riid,ppvObject)	\
    (This)->lpVtbl -> QueryInterface(This,riid,ppvObject)

#define INSSCommandContext_AddRef(This)	\
    (This)->lpVtbl -> AddRef(This)

#define INSSCommandContext_Release(This)	\
    (This)->lpVtbl -> Release(This)


#define INSSCommandContext_GetRequestContext(This,ppProps)	\
    (This)->lpVtbl -> GetRequestContext(This,ppProps)

#define INSSCommandContext_GetResponseContext(This,ppProps)	\
    (This)->lpVtbl -> GetResponseContext(This,ppProps)

#endif /* COBJMACROS */


#endif 	/* C style interface */



HRESULT STDMETHODCALLTYPE INSSCommandContext_GetRequestContext_Proxy( 
    INSSCommandContext __RPC_FAR * This,
    /* [out] */ IPropertyMap __RPC_FAR *__RPC_FAR *ppProps);


void __RPC_STUB INSSCommandContext_GetRequestContext_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE INSSCommandContext_GetResponseContext_Proxy( 
    INSSCommandContext __RPC_FAR * This,
    /* [out] */ IPropertyMap __RPC_FAR *__RPC_FAR *ppProps);


void __RPC_STUB INSSCommandContext_GetResponseContext_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);



#endif 	/* __INSSCommandContext_INTERFACE_DEFINED__ */


/* Additional Prototypes for ALL interfaces */

/* end of Additional Prototypes */

#ifdef __cplusplus
}
#endif

#endif
