
/***********************************************************
Copyright 1991-2001 by Oratrix Development BV, Amsterdam, The Netherlands.

                        All Rights Reserved

******************************************************************/

// audpipe.ax - A filter for converting audio

#include <streams.h>
#include <initguid.h>
#include "audpipe.h"

#include <wtypes.h>
#include <mmsystem.h>
#include <assert.h>

const AMOVIESETUP_MEDIATYPE sudPinTypes =
{
    &MEDIATYPE_Audio,             // MajorType
    &MEDIASUBTYPE_NULL            // MinorType
};

const AMOVIESETUP_PIN sudPins =
{
    L"Input",                     // The Pins name
    FALSE,                        // Is rendered
    FALSE,                        // Is an output pin
    FALSE,                        // Allowed none
    FALSE,                        // Allowed many
    &CLSID_NULL,                  // Connects to filter
    NULL,                         // Connects to pin
    1,                            // Number of types
    &sudPinTypes                // Pin details
};

const AMOVIESETUP_FILTER sudFilter =
{
    &CLSID_AudioPipe,			// Filter CLSID
    L"Audio Pipe",				// String name
    MERIT_DO_NOT_USE,           // Filter merit
    1,                          // Number of pins
    &sudPins                    // Pin details
};


CFactoryTemplate g_Templates[] = {
    { L"Audio Pipe"
    , &CLSID_AudioPipe
    , CAudioPipe::CreateInstance
    , NULL
    , &sudFilter },
};
int g_cTemplates = sizeof(g_Templates) / sizeof(g_Templates[0]);


#pragma warning(disable:4355)


class AudioPipeInputPin : public CRendererInputPin
	{
	public:
    AudioPipeInputPin(CBaseRenderer *pRenderer,
                      HRESULT *phr,
                      LPCWSTR Name)
	:	CRendererInputPin(pRenderer, phr, Name){}

	STDMETHODIMP GetAllocator(IMemAllocator ** ppAllocator)
		{
		HRESULT hr = CRendererInputPin::GetAllocator(ppAllocator);
		if(SUCCEEDED(hr))
			{
			ALLOCATOR_PROPERTIES props;
			GetAllocatorRequirements(&props);

			ALLOCATOR_PROPERTIES actual;
			ZeroMemory(&actual, sizeof(ALLOCATOR_PROPERTIES));
			
			(*ppAllocator)->Decommit();
			(*ppAllocator)->SetProperties(&props, &actual);
			}
		return hr;
		}

	STDMETHODIMP GetAllocatorRequirements(ALLOCATOR_PROPERTIES *pProps)
		{
		pProps->cBuffers = 1;
		pProps->cbBuffer = 4608;
		pProps->cbAlign = 1;
		pProps->cbPrefix = 0;
		return S_OK;
		}
	};


CAudioPipe::CAudioPipe(LPUNKNOWN pUnk,HRESULT *phr) :
    CBaseRenderer(CLSID_AudioPipe, NAME("Audio Pipe"), pUnk, phr),
	m_pAdviceSink(NULL)
{
} 

CAudioPipe::~CAudioPipe()
{
	if(m_pAdviceSink) m_pAdviceSink->Release();
}

CUnknown * WINAPI CAudioPipe::CreateInstance(LPUNKNOWN pUnk, HRESULT *phr)
{
    return new CAudioPipe(pUnk,phr);
} 

CBasePin *CAudioPipe::GetPin(int n)
{

    CAutoLock cRendererLock(&m_InterfaceLock);
    HRESULT hr = NOERROR;
    ASSERT(n == 0);

    // Should only ever be called with zero

    if (n != 0) {
	return NULL;
    }

    // Create the input pin if not already done so

    if (m_pInputPin == NULL) {
	m_pInputPin = new AudioPipeInputPin(this,&hr,L"In");
   }
    return m_pInputPin;
}


STDMETHODIMP
CAudioPipe::NonDelegatingQueryInterface(REFIID riid,void **ppv)
{
	if(riid == IID_IPipe)
        return GetInterface((IPipe*)this, ppv);	
    return CBaseRenderer::NonDelegatingQueryInterface(riid,ppv);
} 

HRESULT CAudioPipe::BreakConnect()
{
    return NOERROR;
} 

HRESULT CAudioPipe::CheckMediaType(const CMediaType *pmt)
{
    if (pmt->majortype != MEDIATYPE_Audio) {
		return E_INVALIDARG;
    }

    // Reject invalid format blocks
    if (pmt->formattype != FORMAT_WaveFormatEx) {
        return VFW_E_TYPE_NOT_ACCEPTED;
	}

    WAVEFORMATEX *pwfx = (WAVEFORMATEX *) pmt->Format();;

    // Reject compressed audio
    if (pwfx->wFormatTag != WAVE_FORMAT_PCM) {
        return VFW_E_TYPE_NOT_ACCEPTED;
    }

    // Accept only 8 or 16 bit
    if (pwfx->wBitsPerSample!=8 && pwfx->wBitsPerSample!=16) {
        return VFW_E_TYPE_NOT_ACCEPTED;
    }

    return NOERROR;
} 

HRESULT CAudioPipe::SetMediaType(const CMediaType *pmt)
{
    CAutoLock cInterfaceLock(&m_InterfaceLock);
    m_mtIn = *pmt;
	if(m_pAdviceSink) m_pAdviceSink->OnSetMediaType(pmt);
    return NOERROR;
}

void CAudioPipe::OnReceiveFirstSample(IMediaSample *pMediaSample)
{
} 

HRESULT CAudioPipe::DoRenderSample(IMediaSample *pMediaSample)
{
	if(m_pAdviceSink) m_pAdviceSink->OnRenderSample(pMediaSample);
    return NOERROR;
}


HRESULT CAudioPipe::Active()
{
	AdjustBufferSize();
	if(m_pAdviceSink) m_pAdviceSink->OnActive();
	return CBaseRenderer::Active();
} 

HRESULT CAudioPipe::Inactive()
{
	if(m_pAdviceSink) m_pAdviceSink->OnInactive();
	return CBaseRenderer::Inactive();
}

HRESULT CAudioPipe::SetRendererAdviceSink(IRendererAdviceSink *pI)
{
	if(m_pAdviceSink) m_pAdviceSink->Release();
	m_pAdviceSink = pI;
	m_pAdviceSink->AddRef();
	return S_OK;
}

HRESULT CAudioPipe::AdjustBufferSize()
	{
	if(m_pInputPin == NULL) return E_UNEXPECTED;
	if(m_pInputPin->Allocator() == NULL) return E_UNEXPECTED;
	
	ALLOCATOR_PROPERTIES props;
	m_pInputPin->GetAllocatorRequirements(&props);

	ALLOCATOR_PROPERTIES actual;
	ZeroMemory(&actual, sizeof(ALLOCATOR_PROPERTIES));

	m_pInputPin->Allocator()->Decommit();
	m_pInputPin->Allocator()->SetProperties(&props, &actual);

	return S_OK;
	}

////////////////////////////////////////////////
// Filter registration

STDAPI DllRegisterServer()
{
    return AMovieDllRegisterServer2(TRUE);
} 

STDAPI DllUnregisterServer()
{
    return AMovieDllRegisterServer2(FALSE);
} 

