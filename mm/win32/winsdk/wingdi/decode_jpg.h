#ifndef INC_DECODE_JPG
#define INC_DECODE_JPG

#ifndef INC_MEMFILE
#include "../common/memfile.h"
#endif

#ifndef INC_SURFACE
#include "surface.h"
#endif

#ifndef INC_PARSE_I
#include "decode_i.h"
#endif

#ifndef JPEGLIB_H
#undef HAVE_STDDEF_H
#undef HAVE_STDLIB_H
extern "C" {
#include "../../../../lib-src/jpeg/jpeglib.h"
}
#define HAVE_STDDEF_H
#define HAVE_STDLIB_H
#endif


class JpgDecoder : public ImgDecoder
	{
	public:
	typedef unsigned int JDIMENSION;
	typedef unsigned char JSAMPLE;
	typedef JSAMPLE* JSAMPROW;	
	typedef JSAMPROW* JSAMPARRAY;

	JpgDecoder(memfile& mf, HDC hDC, ERROR_FUNCT ef);
	virtual ~JpgDecoder();

	virtual bool can_decode();
	virtual DIBSurf* decode();

	private:
	void write_pixel_rows(j_decompress_ptr cinfo, surface<le::trible> *psurf);

	JSAMPARRAY m_dbuffer;
	JDIMENSION m_dbuffer_height;
	JDIMENSION m_cur_output_row;
	};

inline JpgDecoder::JpgDecoder(memfile& mf, HDC hDC, ERROR_FUNCT ef)
:	ImgDecoder(mf, hDC, ef), 
	m_dbuffer(NULL), m_dbuffer_height(1),
	m_cur_output_row(0)
	{
	}

inline JpgDecoder::~JpgDecoder()
	{
	if(m_dbuffer != NULL)
		{
		for(JDIMENSION i=0;i<m_dbuffer_height;i++)
			delete[] m_dbuffer[i];
		delete[] m_dbuffer;
		}
	}

inline bool JpgDecoder::can_decode()
	{
	m_mf.seekg(0);
    uchar_t b1 = m_mf.get_byte();
    uchar_t b2 = m_mf.get_byte();
    if((b1 == 0xFF) && (b2 == 0xD8))
		return true;
	return false;
	}
inline DIBSurf* JpgDecoder::decode()
	{
	if(m_mf.get_handle() == INVALID_HANDLE_VALUE)
		{
		(*m_ef)("JpgDecoder::decode", "invalid file handle");
		return NULL;
		}

	jpeg_decompress_struct cinfo;
	jpeg_error_mgr jerr;

	// Initialize the JPEG decompression object with default error handling.
	cinfo.err = jpeg_std_error(&jerr);
	jpeg_create_decompress(&cinfo);

	// Specify data source for decompression
	m_mf.reset_file_pointer();
	jpeg_stdio_src(&cinfo, m_mf.get_handle());

	// Read file header, set default decompression parameters
	int res = jpeg_read_header(&cinfo, TRUE);

	// Calculate output image dimensions so we can allocate space
	jpeg_calc_output_dimensions(&cinfo);
	
	// Start decompressor
	jpeg_start_decompress(&cinfo);
		
	JDIMENSION row_width = cinfo.output_width * cinfo.output_components;
	
	// release/create buffer
	if(m_dbuffer != NULL)
		{
		for(JDIMENSION i=0;i<m_dbuffer_height;i++)
			delete[] m_dbuffer[i];
		delete[] m_dbuffer;
		m_dbuffer = NULL;
		}
	m_dbuffer_height = 1;
	m_dbuffer = new JSAMPROW[m_dbuffer_height];
	for(JDIMENSION i=0;i<m_dbuffer_height;i++)
		m_dbuffer[i] = new JSAMPLE[row_width];

	int width = cinfo.output_width;
	int height = cinfo.output_height;

	// create a bmp surface
	le::trible *pBits = NULL;
	BITMAPINFO *pbmpi = GetBmpInfo24(width, height);
	HBITMAP hBmp = CreateDIBSection(m_hDC, pbmpi, DIB_RGB_COLORS, (void**)&pBits, NULL, 0);
	if(hBmp==NULL || pBits==NULL)
		{
		(*m_ef)("CreateDIBSection", "");
		return NULL;
		}

	surface<le::trible> *psurf = new surface<le::trible>(width, height, 24, pBits);

	// Process data
	m_cur_output_row = 0;
	while(cinfo.output_scanline < cinfo.output_height) 
		{
		int num_scanlines = jpeg_read_scanlines(&cinfo, m_dbuffer, m_dbuffer_height);
		if(cinfo.out_color_space == JCS_RGB && cinfo.quantize_colors != TRUE)
			write_pixel_rows(&cinfo, psurf);
		}

	// cleanup
	jpeg_finish_decompress(&cinfo);
	jpeg_destroy_decompress(&cinfo);
	return new DIBSurf(hBmp, psurf);
	}

inline void JpgDecoder::write_pixel_rows(j_decompress_ptr cinfo, surface<le::trible> *psurf)
	{
	JSAMPROW inptr = m_dbuffer[0];
	le::trible* outptr = psurf->get_row(m_cur_output_row);
	for(JDIMENSION col = 0; col < cinfo->output_width; col++) 
		{
		le::trible t;
		t.r = *inptr++;
		t.g = *inptr++;
		t.b = *inptr++;
		*outptr++ = t;
		}
	m_cur_output_row++;
	}
	
#endif // INC_DECODE_JPG
