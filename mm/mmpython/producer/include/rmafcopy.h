/****************************************************************************
 * 
 *	rmafcopy.h
 *
 *	$Id$
 *
 *	Copyright �1998 RealNetworks.
 *	All rights reserved.
 *
 *	Definition of the Interfaces for the RMFF File Copy SDK.
 *
 */

#ifndef _RMAFCOPY_H_
#define _RMAFCOPY_H_

struct IRMARMFileSink;
struct IRMAValues;
struct IRMAProgressSink;

// Prototype to create instance of RMFFCopy object and 
// typedef to get a pointer to this function from the dll
typedef PN_RESULT (PNEXPORT_PTR FPCREATEINSTANCE) (IUnknown** /*OUT*/ ppIUnknown);
STDAPI RMACreateRMFFCopy(IUnknown**  /*OUT*/	ppIUnknown);


/****************************************************************************
 * 
 *  Interface:
 *
 *	IRMARMFFCopy
 *
 *  Purpose:
 *
 *	Interface to rmff copy module
 *
 *  IRMARMFFCopy
 *
 *  {A8E28270-1A8C-11d2-B65F-00C0F0312253}
 *
 */

class Content;

DEFINE_GUID(IID_IRMARMFFCopy, 
0xa8e28270, 0x1a8c, 0x11d2, 0xb6, 0x5f, 0x0, 0xc0, 0xf0, 0x31, 0x22, 0x53);

#define CLSID_IRMARMFFCopy IID_IRMARMFFCopy


#undef  INTERFACE
#define INTERFACE   IRMARMFFCopy

DECLARE_INTERFACE_(IRMARMFFCopy, IUnknown)
{
    /*
     *	IUnknown methods
     */
    STDMETHOD(QueryInterface)	(THIS_
				REFIID riid,
				void** ppvObj) PURE;

    STDMETHOD_(ULONG32,AddRef)	(THIS) PURE;

    STDMETHOD_(ULONG32,Release)	(THIS) PURE;

    // *** IRMARMFFCopy methods ***
 
	// ***	Basic Interface ***
 
	// sets the specified .rm file as the input file.
	// Also specifies the file name of an input file to paste to the end of the 
	// first input file
	STDMETHOD(AddInputFile) (THIS_
				const char* szFileName) PURE;  

	// sets the specified .rm file as the output file
	STDMETHOD(SetOutputFile) (THIS_
				const char* szFileName) PURE;  

	// sets the start time for the copy in milliseconds
	STDMETHOD(SetStartTime) (THIS_
				UINT32 ulStartTime) PURE;  

	// sets the end time for the copy in milliseconds. Use 0 to indicate EOF
	STDMETHOD(SetEndTime) (THIS_
				UINT32 ulEndTime) PURE;  

	// sets the content header
	STDMETHOD(SetContent) (THIS_
				Content* pContent) PURE;  

	// sets the content header
	STDMETHOD(SetPropertyFlags) (THIS_
				UINT16 unFlags) PURE;  

    STDMETHOD(SetRMFileSink)	(THIS_
				IRMARMFileSink* pRMFileSink) PURE;

	STDMETHOD(RemoveRMFileSink)	(THIS_
				IRMARMFileSink* pRMFileSink) PURE;

	STDMETHOD(SetMetaInformation) (THIS_
		IRMAValues* pMetaInformation) PURE;

	// process the copy
	STDMETHOD(Process) (THIS) PURE;  
};


/****************************************************************************
 * 
 *  Interface:
 *
 *	IRMARMFFCopy2
 *
 *  Purpose:
 *
 *	Interface to rmff copy module
 *
 *  IRMARMFFCopy2
 *
 *  {4AFA6991-ADC0-11d3-8660-42525E000000}
 *
 */

DEFINE_GUID(IID_IRMARMFFCopy2, 
0x4afa6991, 0xadc0, 0x11d3, 0x86, 0x60, 0x42, 0x52, 0x5e, 0x0, 0x0, 0x0);

#define CLSID_IRMARMFFCopy2 IID_IRMARMFFCopy2

#undef  INTERFACE
#define INTERFACE   IRMARMFFCopy2

DECLARE_INTERFACE_(IRMARMFFCopy2, IRMARMFFCopy)
{
	/************************************************************************
     *	Method:
     *	    IRMARMFFCopy2::AddSaveProgressSink
     *	Purpose:
     *		Add sink which receives callbacks with save progress
	 */	
    STDMETHOD(AddSaveProgressSink)(IRMAProgressSink* pProgressSink) PURE;
    
	/************************************************************************
     *	Method:
     *	    IRMARMFFCopy2::RemoveSaveProgressSink
     *	Purpose:
     *		Remove progress-during-save sink
	 */	
    STDMETHOD(RemoveSaveProgressSink)(IRMAProgressSink* pProgressSink) PURE;
};

#endif //_RMAFCOPY_H_
