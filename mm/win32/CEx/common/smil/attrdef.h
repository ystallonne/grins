
/************************************************************************
Copyright 1991-2002 by Oratrix Development BV, Amsterdam, The Netherlands.

                        All Rights Reserved

*************************************************************************/

/////////////////
// XXX: Under dev
//  

namespace smil {


#ifndef INC_XML_ATTRIBUTE_DEF
#include "xml/attribute_def.h"
#endif


//
struct time_attr_reader
	{
	static bool read(std::string repr, double& v) 
		{
		}
	};

struct time_attr_writer
	{
	static std::string write(const double& v)
		{
		// later
		}
	};

xml::attribute_def<double, time_attr_reader, time_attr_writer> 
begin_def("begin", 0.0, "Start delay of object");

// addToAttrsMap(begin_def)

//
struct rgbtuble
	{
	};

struct color_reader
	{
	static bool read(std::string repr, rgbtuble& v) 
		{
		}
	};

struct color_writer
	{
	static std::string write(const rgbtuble& v) 
		{
		}
	};

xml::attribute_def<rgbtuble, color_reader, color_writer> 
borderColor_def("borderColor", rgbtuble(0,0,0), "Color for transition border (wipe only)");

// addToAttrsMap(borderColor_def)

//
template<const char** values>
struct str_enum
	{
	std::string m_value;
	};

template<const char** values>
struct str_enum_reader
	{
	static bool read(std::string repr, str_enum<values>& v)
		{
		}
	};

template<const char** values>
struct str_enum_writer
	{
	static std::string write(const str_enum<values>& v) 
		{
		}
	};

const char* calcMode_enum[] = {"discrete", "linear", "paced", "spline"};

xml::attribute_def<str_enum<calcMode_enum>, str_enum_reader<calcMode_enum>, str_enum_writer<calcMode_enum> > 
calcMode_def("calcMode", "linear", "Interpolation mode for the animation");

// addToAttrsMap(calcMode_def)

} // namespace smil