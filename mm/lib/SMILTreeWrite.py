__version__ = "$Id$"

# MMWrite -- Multimedia tree writing interface


from MMExc import *		# Exceptions
from MMNode import alltypes, leaftypes, interiortypes
import MMCache
import MMAttrdefs
import Hlinks
import ChannelMap
import colors
from AnchorDefs import *
import features
import compatibility
import string
import os
import MMurl
import re

from SMIL import *

interiortypes = interiortypes + ['foreign']

def nameencode(value):
	"""Quote a value"""
	value = string.join(string.split(value,'&'),'&amp;')
	value = string.join(string.split(value,'>'),'&gt;')
	value = string.join(string.split(value,'<'),'&lt;')
	value = string.join(string.split(value,'"'),'&quot;')
	return '"' + value + '"'

NSGRiNSprefix = 'GRiNS'
NSQTprefix = 'qt'

# This string is written at the start of a SMIL file.
SMILdecl = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
doctype = '<!DOCTYPE smil PUBLIC "%s"\n%s"%s">\n' % (SMILpubid,' '*22,SMILdtd)
doctype2 = '<!DOCTYPE smil PUBLIC "%s"\n%s"%s">\n' % (SMILBostonPubid,' '*22,SMILBostonDtd)
xmlnsGRiNS = 'xmlns:%s' % NSGRiNSprefix
xmlnsQT = 'xmlns:%s' % NSQTprefix

nonascii = re.compile('[\200-\377]')

isidre = re.compile('^[a-zA-Z_][-A-Za-z0-9._]*$')

# A fileish object with indenting
class IndentedFile:
	def __init__(self, fp):
		self.fp = fp
		self.level = 0
		self.bol = 1
		self.charpos = 0

	def push(self):
		self.level = self.level + 2

	def pop(self):
		self.level = self.level - 2

	def write(self, data):
		lines = string.split(data, '\n')
		if not lines:
			return self.charpos, self.charpos
##		first = 1
		start = self.charpos
		for line in lines[:-1]:
			if self.bol:
				if self.level:
					self.fp.write(' '*self.level)
					self.charpos = self.charpos + self.level
				self.bol = 0
			if line:
##				if first:
##					start = self.charpos
##					first = 0
				self.fp.write(line)
				self.charpos = self.charpos + len(line)
			self.fp.write('\n')
			self.charpos = self.charpos + 1
			self.bol = 1

		line = lines[-1]
		if line:
			if self.bol:
				if self.level:
					self.fp.write(' '*self.level)
					self.charpos = self.charpos + self.level
				self.bol = 0
##			if first:
##				start = self.charpos
##				first = 0
			self.fp.write(line)
			self.charpos = self.charpos + len(line)
		return start, self.charpos

	def writeline(self, data):
		self.write(data)

	def writelines(self, data):
		self.write(string.join(data, '\n'))

	def close(self):
		self.fp.close()



# Write a node to a CMF file, given by filename

Error = 'Error'

def WriteFile(root, filename, cleanSMIL = 0, grinsExt = 1, copyFiles = 0, evallicense = 0, progress = None, convertURLs = 0, convertfiles = 1):
	fp = open(filename, 'w')
	try:
		writer = SMILWriter(root, fp, filename, cleanSMIL, grinsExt, copyFiles, evallicense, progress = progress, convertURLs = convertURLs, convertfiles = convertfiles)
	except Error, msg:
		from windowinterface import showmessage
		showmessage(msg, mtype = 'error')
		return
	writer.write()
	if os.name == 'mac':
		import macfs
		import macostools
		fss = macfs.FSSpec(filename)
		if features.compatibility == features.G2 and cleanSMIL:
			fss.SetCreatorType('PNst', 'PNRA')
		else:
			fss.SetCreatorType('GRIN', 'TEXT')
		macostools.touched(fss)

import FtpWriter
def WriteFTP(root, filename, ftpparams, cleanSMIL = 0, grinsExt = 1, copyFiles = 0, evallicense = 0, progress=None):
	host, user, passwd, dir = ftpparams
	try:
		conn = FtpWriter.FtpConnection(host, user=user, passwd=passwd, dir=dir)
		ftp = conn.Writer(filename, ascii=1)
		try:
			writer = SMILWriter(root, ftp, filename, cleanSMIL, grinsExt, copyFiles,
						evallicense, tmpcopy=1, progress=progress)
		except Error, msg:
			from windowinterface import showmessage
			showmessage(msg, mtype = 'error')
			return
		writer.write()
		#
		# Upload generated media items
		#
		srcdir, dstdir, filedict = writer.getcopyinfo()
		del writer
		del ftp
		if filedict and copyFiles:
			conn.chmkdir(dstdir)
			totfiles = len(filedict.keys())
			num = 0
			for filename in filedict.keys():
				num = num + 1
				binary = filedict[filename] # Either 'b' or '', or None for dummies
				if binary is None:
					continue
				ascii = not binary
				localfilename = os.path.join(srcdir, filename)
				remotefilename = os.path.split(filename)[1] # Remove the : for mac filenames
				ifp = open(localfilename, 'r'+binary)
				if progress:
					ifp.seek(0, 2)
					totsize = ifp.tell()
					ifp.seek(0, 0)
					progress("Uploading %s"%remotefilename, num, totfiles, 0, totsize)
				ofp = conn.Writer(remotefilename, ascii=ascii)
				while 1:
					data = ifp.read(16*1024)
					if not data:
						break
					ofp.write(data)
					if progress:
						progress("Uploading %s"%remotefilename, num, totfiles, ifp.tell(), totsize)
				ifp.close()
				ofp.close()
	except FtpWriter.all_errors, msg:
		from windowinterface import showmessage
		showmessage('Mediaserver upload failed: %s'%(msg,), mtype = 'error')
		return
	except IOError, arg:
		from windowinterface import showmessage
		showmessage('Mediaserver upload failed: %s'%(msg,), mtype = 'error')
		return

import StringIO
class MyStringIO(StringIO.StringIO):
	def close(self):
		pass

def WriteString(root, cleanSMIL = 0, evallicense = 0, set_char_pos = 0):
	fp = MyStringIO()
	writer = SMILWriter(root, fp, '<string>', cleanSMIL, evallicense=evallicense, set_char_pos = set_char_pos)
	writer.write()
	return fp.getvalue()

def WriteBareString(node, cleanSMIL = 0):
	fp = MyStringIO()
	writer = SMILWriter(node, fp, '<string>', cleanSMIL)
	writer.writebare()
	return fp.getvalue()

#
# Functions to encode data items
#
def fmtfloat(val, suffix = '', withsign = 0, prec = -1):
	if val < 0:
		val = -val
		sign = '-'
	elif withsign:
		sign = '+'
	else:
		sign = ''
	if prec >= 0:
		# round value
		val = val + 0.5 * 10.0 ** -prec
	str = '%g' % val
	if 'e' in str:
		str, x = string.split(str, 'e')
		strs = string.split(str, '.')
		if len(strs) == 1:
			str1 = strs[0]
			str2 = ''
		else:
			str1, str2 = strs
		if x[0] == '-':
			x = int(x[1:])
			str = '0'*x + str1 + str2
			str = str[:len(str1)] + '.' + str[len(str1):]
		else:
			x = int(x)
			str = str1 + str2 + '0'*x
			str = str[:len(str1) + x] + '.' + str[len(str1) + x:]
	if '.' in str:
		while str[-1] == '0':
			str = str[:-1]
		if str[-1] == '.':
			str = str[:-1]
	if prec >= 0 and '.' in str:
		str1, str2 = string.split(str, '.')
		if prec == 0:
			str = str1
		else:
			str2 = str2 + '0'*prec
			str = str1 + '.' + str2[:prec]
			# still remove trailing zeros
			while str[-1] == '0':
				str = str[:-1]
			if str[-1] == '.':
				str = str[:-1]
	while len(str) > 1 and str[0] == '0' and str[1] in '0123456789':
		str = str[1:]
	if not str:
		str = '0'
	return sign + str + suffix

def getid(writer, node):
	uid = node.GetUID()
	name = writer.uid2name[uid]
	if writer.ids_used[name]:
		return name

def getsrc(writer, node):
	ntype = node.GetType()
	chtype = node.GetChannelType()
	if chtype == 'brush':
		return None
	elif ntype == 'ext':
		val = node.GetAttrDef('file', None)
	elif ntype == 'imm':
		if chtype == 'html':
			mime = 'text/html'
##		elif chtype == 'RealPix':
##			mime = 'image/vnd.rn-realpix'
		else:
			mime = ''
		data = string.join(node.GetValues(), '\n')
		if data and data[-1] != '\n':
			# end with newline if not empty
			data = data + '\n'
		if nonascii.search(data):
			mime = mime + ';charset=ISO-8859-1'
		val = 'data:%s,%s' % (mime, MMurl.quote(data))
	else:
		return None

	if chtype == 'RealPix':
		# special case for RealPix nodes, which we should write
		# sometimes, but don't want to write always
		do_write = 0
		tmp_file_name = 0
		if not val and not writer.copydir:
			# no URL and not exporting, save as data: URL
			import base64, realnode
			node.SetAttr('file', MMurl.basejoin(writer.convertURLs, 'dummy.rp'))
			data = realnode.writenode(node, tostring = 1)
			node.DelAttr('file')
			return 'data:image/vnd.rn-realpix;base64,' + \
			       string.join(string.split(base64.encodestring(data), '\n'), '')
##			return 'data:image/vnd.rn-realpix;charset=ISO-8859-1,' + \
##			       MMurl.quote(data)
		if not val:
			val = writer.gen_rpfile()
			do_write = 1
			tmp_file_name = 1
			node.SetAttr('file', val)
		if hasattr(node, 'tmpfile') and not writer.copydir:
			# Also save if the node has changed and we're saving (not exporting)
			do_write = 1
		if do_write:
			import realnode
			realnode.writenode(node)
		if tmp_file_name:
			node.DelAttr('file')
	if not val:
		if writer.copydir:
			# Exporting without a URL is an error
			from windowinterface import showmessage
			node.set_infoicon('error', 'The URL field is empty')
			showmessage('No URL set for node %s\nThe document may not be playable.' % (node.GetRawAttrDef('name', '<unnamed>')))
		else:
			# If not exporting we insert a placeholder
			val = '#'
		return val
	ctx = node.GetContext()
	if not writer.copydir:
		if writer.convertURLs:
			val = MMurl.canonURL(ctx.findurl(val))
			if val[:len(writer.convertURLs)] == writer.convertURLs:
				val = val[len(writer.convertURLs):]
		return val
	url = ctx.findurl(val)
	if writer.copycache.has_key(url):
		# already seen and copied
		val = MMurl.basejoin(writer.copydirurl, MMurl.pathname2url(writer.copycache[url]))
		if features.compatibility == features.G2:
			val = MMurl.unquote(val)
		return val
	if chtype == 'RealPix':
		# special case code for RealPix file
		if not hasattr(node, 'slideshow'):
			import realnode
			node.slideshow = realnode.SlideShow(node)
		import realsupport
		rp = node.slideshow.rp
		otags = rp.tags
		ntags = []
		for i in range(len(otags)):
			attrs = otags[i].copy()
			ntags.append(attrs)
			if attrs.get('tag','fill') not in ('fadein', 'crossfade', 'wipe'):
				continue
			nurl = attrs.get('file')
			if not nurl:
				# XXX URL missing for transition
				import windowinterface
				msg = 'No URL specified in transition'
				windowinterface.showmessage(msg + '\nThe document will not be playable.')
				if node.children:
					node.children[i].set_infoicon('error', msg)
				else:
					node.set_infoicon('error', msg)
				continue
			nurl = ctx.findurl(nurl)
			if writer.copycache.has_key(nurl):
				nfile = writer.copycache[nurl]
			else:
				nfile = writer.copyfile(nurl, attrs)
				writer.copycache[nurl] = nfile
			attrs['file'] = MMurl.basejoin(writer.copydirurl, MMurl.pathname2url(nfile))
		rp.tags = ntags
		file = writer.newfile(url)
		val = MMurl.basejoin(writer.copydirurl, MMurl.pathname2url(file))
		ofile = node.GetRawAttrDef('file', None)
		node.SetAttr('file', val)
		realsupport.writeRP(os.path.join(writer.copydir, file), rp, node)
		if ofile:
			node.SetAttr('file', ofile)
		else:
			node.DelAttr('file')
		writer.files_generated[file] = ''
		rp.tags = otags
	else:
		try:
			file = writer.copyfile(url, node)
		except IOError, msg:
			import windowinterface
			windowinterface.showmessage('Cannot copy %s: %s\n'%(val, msg)+'The URL is left unchanged; the document may not be playable.')
			node.set_infoicon('error', msg)
			return val
	writer.copycache[url] = file
	val = MMurl.basejoin(writer.copydirurl, MMurl.pathname2url(file))
	if features.compatibility == features.G2:
		val = MMurl.unquote(val)
	return val

def translatecolor(val):
	if colors.rcolors.has_key(val):
		return colors.rcolors[val]
	else:
		return '#%02x%02x%02x' % val

def getcolor(writer, node):
	if node.GetChannelType() != 'brush':
		return None
	fgcolor = node.GetRawAttrDef('fgcolor', None)
	if fgcolor is None:
		return
	return translatecolor(fgcolor)

def getsubregionatt(writer, node, attr):
	from windowinterface import UNIT_PXL, UNIT_SCREEN

	val = node.getCssRawAttr(attr)
	if val is not None:
		# save only if subregion positioning is different than region
		if val == 0:
			return None

		if type(val) == type (0.0):
			return fmtfloat(100*val, '%', prec = 1)
		else:
			return str(val)
	return None

def getfitatt(writer, node, attr):
	try:
		val = node.getCssRawAttr(attr)
	except:
		fit = None
	else:
		fit = None		# 'hidden' is default
		if val == 0:
			fit = 'meet'
		elif val == -1:
			fit = 'slice'
		elif val == 1:
			fit = None	# 'hidden' is default
		elif val == -3:
			fit = 'fill'
		elif val == -4:
			fit = 'scroll'
	return fit

def getbgcoloratt(writer, node, attr):
	if not ChannelMap.isvisiblechannel(node.GetChannelType()):
		return None	
	# if transparent, there is no backgroundColor attribute
	if node.GetRawAttrDef('transparent', 1):
		return None

	bgcolor = node.GetRawAttrDef('bgcolor', None)
	if bgcolor is None:
		return 'inherit'
	return translatecolor(bgcolor)

def getcmifattr(writer, node, attr, default = None):
	val = node.GetRawAttrDef(attr, default)
	if val is not None:
		if default is not None and val == default:
			return None
		val = str(val)
	return val

def getmimetype(writer, node):
	if node.GetType() not in leaftypes:
		return
	if writer.copydir:
		# MIME type may be changed by copying, so better not to return any
		return
	return node.GetRawAttrDef('mimetype', None)

def getdescr(writer, node, attr):
	if node.GetType() not in leaftypes:
		return
	val = node.GetRawAttrDef(attr, None)
	return val or None

def getregionname(writer, node):
	ch = node.GetChannel()
	if not ch:
		return None
	return writer.ch2name[ch.GetLayoutChannel()]

def getdefaultregion(writer, node):
	chname = node.GetRawAttrDef('project_default_region', None)
	if not chname:
		return None
	ch = node.GetContext().getchannel(chname)
	if ch is None:
		return None
	return writer.ch2name[ch]

def getduration(writer, node, attr = 'duration'):
	duration = node.GetRawAttrDef(attr, None)
	if duration is None:		# no duration
		return None
	elif duration == -1:		# infinite duration...
		return 'indefinite'
	elif duration == -2:
		return 'media'
	else:
		return fmtfloat(duration, 's')

def getmin(writer, node):
	min = node.GetRawAttrDef('min', None)
	if min == -2:
		return 'media'
	elif not min:
		return None		# 0 or None
	return fmtfloat(min, 's')

def getmax(writer, node):
	max = node.GetRawAttrDef('max', None)
	if max is None:
		return None
	elif max == -1:
		return 'indefinite'
	elif max == -2:
		return 'media'
	return fmtfloat(max, 's')

def getspeed(writer, node, attr = 'speed'):
	speed = node.GetRawAttrDef(attr, None)
	if speed is None:
		return None
	else:
		return fmtfloat(speed)

def getproportion(writer, node, attr):
	prop = node.GetRawAttrDef(attr, None)
	if prop is None:
		return None
	else:
		return fmtfloat(prop)

def getpercentage(writer, node, attr):
	prop = node.GetRawAttrDef(attr, None)
	if prop is None:
		return None
	else:
		return fmtfloat(prop * 100, suffix = '%')

def getsensitivity(writer, node):
	if not writer.smilboston:
		return
	sensitivity = node.GetRawAttrDef('sensitivity', None)
	if sensitivity is None:
		return
	if sensitivity >= 100:
		return 'transparent'
	elif sensitivity <= 0:
		return			# 'opaque' is default
	elif 0 < sensitivity < 100:
		return '%d%%' % sensitivity

def escape_name(name, quote_initial = 1):
	name = string.join(string.split(name, '.'), '\\.')
	name = string.join(string.split(name, '-'), '\\-')
	if quote_initial and name in ['prev', 'wallclock', ]:
		name = '\\' + name
	return name

def wallclock2string(wallclock):
	# This code is used also in the EventEditor.
	yr,mt,dy,hr,mn,sc,tzsg,tzhr,tzmn = wallclock
	if yr is not None:
		date = '%04d-%02d-%02dT' % (yr, mt, dy)
	else:
		date = ''
	# time is optional if there is a date
	if date and hr == mn == sc == 0:
		time = ''
		date = date[:-1] # remove T at end
	elif sc == 0:
		# seconds are optional
		time = '%02d:%02d' % (hr, mn)
	elif int(sc) == sc:
		# fraction of seconds is optional
		time = '%02d:%02d:%02d' % (hr, mn, int(sc))
	else:
		time = '%02d:%02d:%05.2f' % (hr, mn, sc)
	if tzhr is not None:
		if tzsg == '+' and tzhr == tzmn == 0:
			# UTC/GMT can be abbreviated to just "Z"
			tz = 'Z'
		else:
			tz = '%s%02d:%02d' % (tzsg, tzhr, tzmn)
	else:
		tz = ''
	return 'wallclock(%s%s%s)' % (date, time, tz)

				
def getsyncarc(writer, node, isend):
	if isend:
		attr = 'endlist'
	else:
		attr = 'beginlist'
	list = []
	nomultiple = 0
	for arc in node.GetRawAttrDef(attr, []):
		if arc.srcnode is None and arc.event is None and arc.marker is None and arc.delay is None and arc.wallclock is None:
			nomultiple = 1
			list.append('indefinite')
		elif arc.srcnode is None and arc.event is None and arc.marker is None and arc.wallclock is None and arc.accesskey is None:
			list.append(fmtfloat(arc.delay, 's'))
		elif arc.wallclock is not None:
			list.append(wallclock2string(arc.wallclock))
		elif arc.accesskey is not None:
			key = 'accesskey(%s)' % arc.accesskey
			if arc.delay:
				key = key + fmtfloat(arc.delay, withsign = 1)
			list.append(key)
		elif arc.marker is None:
			if arc.channel is not None:
				name = writer.ch2name[arc.channel]
			elif arc.srcanchor:
				aid = (arc.srcnode.GetUID(), arc.srcanchor)
				name = escape_name(writer.aid2name[aid])
			elif arc.srcnode == 'syncbase':
				name = ''
			elif arc.srcnode == 'prev':
				name = 'prev'
			elif arc.srcnode is node:
				name = ''
			else:
				name = escape_name(writer.uid2name[arc.srcnode.GetUID()])
			if arc.event is not None:
				if name:
					name = name + '.'
				name = name + escape_name(arc.event, 0)
			if arc.delay or not name:
				if name:
					name = name + fmtfloat(arc.delay, withsign = 1)
				else:
					name = fmtfloat(arc.delay, withsign = 0)
			list.append(name)
		else:
			list.append('%s.marker(%s)' % (escape_name(writer.uid2name[arc.srcnode.GetUID()]), arc.marker))
	if not list:
		return
	return string.join(list, ';')

def getterm(writer, node):
	if node.type in ('seq', 'prio', 'switch'):
		return
	terminator = node.GetTerminator()
	ntype = node.GetType()
	if terminator == 'LAST':
		if ntype in ('par', 'excl'):
			return
		return 'last'
	if terminator == 'FIRST':
		return 'first'
	if terminator == 'ALL':
		return 'all'
	if terminator == 'MEDIA' and ntype in leaftypes:
		return
	for child in node.children:
		if child.GetRawAttrDef('name', '') == terminator:
			id = writer.uid2name[child.GetUID()]
			if writer.smilboston:
				if id in ('all', 'first', 'last', 'media'):
					return '\\' + id
				else:
					return id
			else:
				return 'id(%s)' % id
	print '** Terminator attribute refers to unknown child in', \
	      node.GetRawAttrDef('name', '<unnamed>'),\
	      node.GetUID()

def getrepeat(writer, node):
	value = node.GetAttrDef('loop', None)
	if value is None:
		return
	if value == 0:
		return 'indefinite'
	else:
		return fmtfloat(value)

def getboolean(writer, node, attr):
	value = node.GetRawAttrDef(attr, None)
	if value is not None:
		if value:
			return 'on'
		else:
			return 'off'

def getsysreq(writer, node, attr):
	sysreq = node.GetRawAttrDef('system_required', [])
	if sysreq:
		return string.join(map(lambda i: 'ext%d' % i, range(len(sysreq))), ' + ')
	return None

def getsyscomp(writer, node, attr):
	syscomp = node.GetRawAttrDef('system_component', [])
	if syscomp:
		return string.join(syscomp)
	return None

def getscreensize(writer, node):
	value = node.GetRawAttrDef('system_screen_size', None)
	if value is not None:
		return '%dX%d' % value

def getugroup(writer, node):
	if not node.GetContext().usergroups:
		return
	names = []
	for u_group in node.GetRawAttrDef('u_group', []):
		try:
			names.append(writer.ugr2name[u_group])
		except KeyError:
			print '** Attempt to write unknown usergroup', u_group
	if not names:
		return
	return string.join(names, ' + ')

def getlayout(writer, node):
	if not node.GetContext().layouts:
		return
	layout = node.GetRawAttrDef('layout', 'undefined')
	if layout == 'undefined':
		return
	try:
		return writer.layout2name[layout]
	except KeyError:
		print '** Attempt to write unknown layout', layout
		return

def gettransition(writer, node, which):
	if not node.GetContext().transitions:
		return
	transition = node.GetRawAttrDef(which, None)
	if not transition:
		return
	list = []
	for tr in transition:
		try:
			list.append(writer.transition2name[tr])
		except KeyError:
			print '** Attempt to write unknown transition', tr
			list.append(tr)
	return string.join(list, ';')
		
	
def getautoreverse(writer, node):
	if node.GetRawAttrDef('autoReverse', None):
		return 'true'
	return None

def getattributetype(writer, node):
	atype = node.GetRawAttrDef('attributeType', 'XML')
	if atype == 'XML':
		return None
	return atype

def getaccumulate(writer, node):
	accumulate = node.GetRawAttrDef('accumulate', 'none')
	if accumulate == 'none':
		return None
	return accumulate

def getadditive(writer, node):
	additive = node.GetRawAttrDef('additive', 'replace')
	if additive == 'replace':
		return None
	return additive

def getcalcmode(writer, node):
	mode = node.GetRawAttrDef('calcMode', 'linear')
	tag = node.GetRawAttrDef('atag', 'animate')
	if tag!='animateMotion' and mode == 'linear':
		return None
	elif tag=='animateMotion' and mode == 'paced':
		return None
	return mode

def getpath(writer, node):
	attr = node.GetRawAttrDef('path', None)
	if attr is None:
		return
	# strange but IE manages only spaces
	# grins both spaces and commas
	# so use spaces at least for now
	attr = string.join(string.split(attr,','),' ')
	# collapse multiple spaces to one
	attr = string.join(string.split(attr))
	return attr

def getcollapsed(writer, node):
	if node.GetType() in interiortypes and node.collapsed:
		return 'true'

def getshowtime(writer, node):
	if node.showtime:
		return node.showtime

def getinlinetrmode(writer, node):
	mode = node.GetRawAttrDef('mode', 'in')
	if mode == 'in':
		return None
	return mode

#
# Mapping from SMIL attrs to functions to get them. Strings can be
# used as a shortcut for node.GetAttr
#
smil_attrs=[
	("id", getid),
	("title", lambda writer, node:getcmifattr(writer, node, "title")),
	("region", getregionname),
	("project_default_region", getdefaultregion),
	("project_default_type", lambda writer, node:getcmifattr(writer, node, 'project_default_type')),
	("project_bandwidth_fraction", lambda writer, node:getpercentage(writer, node, 'project_bandwidth_fraction')),
	("type", getmimetype),
	("author", lambda writer, node:getcmifattr(writer, node, "author")),
	("copyright", lambda writer, node:getcmifattr(writer, node, "copyright")),
	("abstract", lambda writer, node:getcmifattr(writer, node, "abstract")),
	("alt", lambda writer, node: getdescr(writer, node, 'alt')),
	("longdesc", lambda writer, node: getdescr(writer, node, 'longdesc')),
	("readIndex", lambda writer, node:getcmifattr(writer, node, "readIndex", 0)),
	("begin", lambda writer, node: getsyncarc(writer, node, 0)),
	("dur", getduration),
	("min", getmin),
	("max", getmax),
	("end", lambda writer, node: getsyncarc(writer, node, 1)),
	("fill", lambda writer, node: getcmifattr(writer, node, 'fill', 'default')),
	("fillDefault", lambda writer, node: getcmifattr(writer, node, 'fillDefault', 'inherit')),
	("erase", lambda writer, node:getcmifattr(writer, node, 'erase', 'whenDone')),
	("syncBehavior", lambda writer, node: getcmifattr(writer, node, 'syncBehavior', 'default')),
	("syncBehaviorDefault", lambda writer, node: getcmifattr(writer, node, 'syncBehaviorDefault', 'inherit')),
	("endsync", getterm),
	("repeat", lambda writer, node:(not writer.smilboston and getrepeat(writer, node)) or None),
	("repeatCount", lambda writer, node:(writer.smilboston and getrepeat(writer, node)) or None),
	("repeatDur", lambda writer, node:getduration(writer, node, "repeatdur")),
	("restart", lambda writer, node: getcmifattr(writer, node, 'restart', 'default')),
	("restartDefault", lambda writer, node: getcmifattr(writer, node, 'restartDefault', 'inherit')),
	("src", lambda writer, node:getsrc(writer, node)),
	("clip-begin", lambda writer, node: (not writer.smilboston and getcmifattr(writer, node, 'clipbegin')) or None),
	("clip-end", lambda writer, node: (not writer.smilboston and getcmifattr(writer, node, 'clipend')) or None),
	("clipBegin", lambda writer, node: (writer.smilboston and getcmifattr(writer, node, 'clipbegin')) or None),
	("clipEnd", lambda writer, node: (writer.smilboston and getcmifattr(writer, node, 'clipend')) or None),
	("sensitivity", getsensitivity),
	("mediaRepeat", lambda writer, node: (writer.smilboston and getcmifattr(writer, node, 'mediaRepeat')) or None),
	("targetElement", lambda writer, node: node.GetRawAttrDef("targetElement", None)),
	("attributeName", lambda writer, node: node.GetRawAttrDef("attributeName", None)),
	("attributeType", getattributetype),
	("speed", lambda writer, node:getspeed(writer, node, "speed")),
	("accelerate", lambda writer, node:getproportion(writer, node, "accelerate")),
	("decelerate", lambda writer, node:getproportion(writer, node, "decelerate")),
	("autoReverse", getautoreverse),
	("system-bitrate", lambda writer, node:(not writer.smilboston and getcmifattr(writer, node, "system_bitrate")) or None),
	("system-captions", lambda writer, node:(not writer.smilboston and getboolean(writer, node, 'system_captions')) or None),
	("system-language", lambda writer, node:(not writer.smilboston and getcmifattr(writer, node, "system_language")) or None),
	("system-overdub-or-caption", lambda writer, node:(not writer.smilboston and {'overdub':'overdub','subtitle':'caption'}.get(getcmifattr(writer, node, "system_overdub_or_caption"))) or None),
	("system-required", lambda writer, node:(not writer.smilboston and getcmifattr(writer, node, "system_required")) or None),
	("system-screen-size", lambda writer, node:(not writer.smilboston and getscreensize(writer, node)) or None),
	("system-screen-depth", lambda writer, node:(not writer.smilboston and getcmifattr(writer, node, "system_screen_depth")) or None),
	("systemAudioDesc", lambda writer, node:(writer.smilboston and getboolean(writer, node, 'system_audiodesc')) or None),
	("systemBitrate", lambda writer, node:(writer.smilboston and getcmifattr(writer, node, "system_bitrate")) or None),
	("systemCaptions", lambda writer, node:(writer.smilboston and getboolean(writer, node, 'system_captions')) or None),
	("systemComponent", lambda writer, node:(writer.smilboston and getsyscomp(writer, node, 'system_component')) or None),
	("systemCPU", lambda writer, node:(writer.smilboston and getcmifattr(writer, node, "system_cpu")) or None),
	("systemLanguage", lambda writer, node:(writer.smilboston and getcmifattr(writer, node, "system_language")) or None),
	("systemOperatingSystem", lambda writer, node:(writer.smilboston and getcmifattr(writer, node, "system_operating_system")) or None),
	("systemOverdubOrSubtitle", lambda writer, node:(writer.smilboston and getcmifattr(writer, node, "system_overdub_or_caption")) or None),
	("systemRequired", lambda writer, node:(writer.smilboston and getsysreq(writer, node, "system_required")) or None),
	("systemScreenSize", lambda writer, node:(writer.smilboston and getscreensize(writer, node)) or None),
	("systemScreenDepth", lambda writer, node:(writer.smilboston and getcmifattr(writer, node, "system_screen_depth")) or None),
	("customTest", getugroup),
	("layout", getlayout),
	("color", getcolor),		# only for brush element
	# subregion positioning
	("left", lambda writer, node:getsubregionatt(writer, node, 'left')),
	("right", lambda writer, node:getsubregionatt(writer, node, 'right')),
	("width", lambda writer, node:getsubregionatt(writer, node, 'width')),
	("top", lambda writer, node:getsubregionatt(writer, node, 'top')),
	("bottom", lambda writer, node:getsubregionatt(writer, node, 'bottom')),
	("height", lambda writer, node:getsubregionatt(writer, node, 'height')),
	("fit", lambda writer, node:getcmifattr(writer, node, 'fit', 'hidden')),
	# registration points
	("regPoint", lambda writer, node:getcmifattr(writer, node, "regPoint", 'topLeft')),
	("regAlign", lambda writer, node:getcmifattr(writer, node, "regAlign", 'topLeft')),
	
	("backgroundColor", lambda writer, node:getbgcoloratt(writer, node, "bgcolor")),	
	("z-index", lambda writer, node:getcmifattr(writer, node, "z")),	
	("from", lambda writer, node: node.GetRawAttrDef("from", None)),
	("to", lambda writer, node: node.GetRawAttrDef("to", None)),
	("by", lambda writer, node: node.GetRawAttrDef("by", None)),
	("values", lambda writer, node: node.GetRawAttrDef("values", None)),
	("path", getpath),
	("origin", lambda writer, node: node.GetRawAttrDef("origin", None)),
	("accumulate", getaccumulate),
	("additive", getadditive),
	("calcMode", getcalcmode),
	("keyTimes", lambda writer, node: node.GetRawAttrDef("keyTimes", None)),
	("keySplines", lambda writer, node: node.GetRawAttrDef("keySplines", None)),
	("transIn", lambda writer, node:gettransition(writer, node, "transIn")),
	("transOut", lambda writer, node:gettransition(writer, node, "transOut")),
	("mode", getinlinetrmode),
	("subtype", lambda writer, node: node.GetRawAttrDef("subtype", None)),

	("mediaSize", lambda writer, node: node.GetRawAttrDef("mediaSize", None)),
	("mediaTime", lambda writer, node: node.GetRawAttrDef("mediaTime", None)),
	("bandwidth", lambda writer, node: node.GetRawAttrDef("bandwidth", None)),

	("collapsed", getcollapsed),
	("showtime", getshowtime),
]
prio_attrs = [
	("id", getid),
	("title", lambda writer, node:getcmifattr(writer, node, "title")),
	("author", lambda writer, node:getcmifattr(writer, node, "author")),
	("copyright", lambda writer, node:getcmifattr(writer, node, "copyright")),
	("abstract", lambda writer, node:getcmifattr(writer, node, "abstract")),
	('lower', lambda writer, node: getcmifattr(writer, node, 'lower', 'defer')),
	('peers', lambda writer, node: getcmifattr(writer, node, 'peers', 'stop')),
	('higher', lambda writer, node: getcmifattr(writer, node, 'higher', 'pause')),
	('pauseDisplay', lambda writer, node: getcmifattr(writer, node, 'pauseDisplay', 'inherit')),
	("collapsed", getcollapsed),
	("showtime", getshowtime),
	]

# attributes that we know about and so don't write into the SMIL file using
# our namespace extension
cmif_node_attrs_ignore = {
	'styledict':0, 'name':0, 'bag_index':0,
	'anchorlist':0, 'channel':0, 'file':0, 'duration':0,
	'min':0, 'max':0, 'erase':0,
	'system_bitrate':0, 'system_captions':0, 'system_language':0,
	'system_overdub_or_caption':0, 'system_overdub_or_subtitle':0,
	'system_required':0, 'system_audiodesc':0, 'system_operating_system':0,
	'system_cpu':0,
	'system_screen_size':0, 'system_screen_depth':0, 'layout':0,
	'clipbegin':0, 'clipend':0, 'u_group':0, 'loop':0,
	'author':0, 'copyright':0, 'abstract':0, 'alt':0, 'longdesc':0,
	'title':0, 'mimetype':0, 'terminator':0, 'begin':0, 'fill':0,
	'fillDefault':0, 'syncBehavior':0, 'syncBehaviorDefault':0,
	'repeatdur':0, 'beginlist':0, 'endlist':0, 'restart':0,
	'restartDefault':0,
	'left':0,'right':0,'top':0,'bottom':0,'fit':0,'units':0,
	'regPoint':0, 'regAlign':0,
	'bgcolor':0, 'transparent':0,
	'transIn':0, 'transOut':0,
	}
cmif_node_realpix_attrs_ignore = {
	'bitrate':0, 'size':0, 'duration':0, 'aspect':0, 'author':0,
	'copyright':0, 'maxfps':0, 'preroll':0, 'title':0, 'href':0,
	}
cmif_node_prio_attrs_ignore = {
	'lower':0, 'peers':0, 'higher':0, 'pauseDisplay':0,
	'name':0, 'title':0, 'abstract':0, 'copyright':0, 'author':0,
	}
cmif_chan_attrs_ignore = {
	'id':0, 'title':0, 'base_window':0, 'base_winoff':0, 'z':0, 'fit':0,
	'transparent':0, 'bgcolor':0, 'winpos':0, 'winsize':0, 'rect':0,
	'units':0,
	# new 03-07-2000
	# we can't save the chan type inside a region since a node may be associate to several nodes
	# the channel type is determinate according to the node type
	'type':0,
	# end new
	'showBackground':0,
	'traceImage':0,
	'soundLevel':0,
	'regAlign':0, 'regPoint':0, 'close':0, 'open':0, 'chsubtype':0,
	'left':0, 'top':0, 'width':0, 'height':0, 'right':0, 'bottom':0,
	'regionName':0
	}
		
qt_node_attrs = {
	'immediateinstantiationmedia':0,'bitratenecessary':0,'systemmimetypesupported':0,
	'attachtimebase':0,'qtchapter':0,'qtcompositemode':0,
	} 

# Mapping from CMIF channel types to smil media types
smil_mediatype={
	'text':'text',
	'sound':'audio',
	'image':'img',
	'video': 'video',
	'html':'text',
	'null':'ref',
	'RealAudio':'audio',
	'RealPix':'animation',
	'RealText':'textstream',
	'RealVideo':'video',
	'unknown': 'ref',
	'animate': 'animate',
	'brush': 'brush',
	'prefetch': 'prefetch',
	'svg': 'img',
}

def mediatype(chtype, error=0):
	if smil_mediatype.has_key(chtype):
		return smil_mediatype[chtype], smil_mediatype[chtype]
	if error and chtype != 'layout':
		print '** Unimplemented channel type', chtype
	return '%s:%s' % (NSGRiNSprefix, chtype), '%s %s' % (GRiNSns, chtype)

class SMILWriter(SMIL):
	def __init__(self, node, fp, filename, cleanSMIL = 0, grinsExt = 1, copyFiles = 0,
		     evallicense = 0, tmpcopy = 0, progress = None,
		     convertURLs = 0, convertfiles = 1, set_char_pos = 0):
		self.set_char_pos = set_char_pos
		ctx = node.GetContext()
		if convertURLs:
			url = MMurl.canonURL(MMurl.pathname2url(filename))
			i = string.rfind(url, '/')
			if i >= 0: url = url[:i+1]
			else: url = ''
			self.convertURLs = url
		else:
			self.convertURLs = None
			
		self.evallicense = evallicense
		self.__generate_number = 0
		if filename == '<string>':
			self.__generate_basename = 'grinstmp'
		else:
			self.__generate_basename = os.path.splitext(os.path.basename(filename))[0]
		self.files_generated = {}
		self.bases_used = {}
		self.progress = progress
		self.convert = convertfiles # we only convert if we have to copy
		if copyFiles:
			dir, base = os.path.split(filename)
			base, ext = os.path.splitext(base)
			base = MMurl.pathname2url(base)
##			if not ext:
##				base = base + '.dir'
##			newdir = self.newfile(base, dir)
			if tmpcopy:
				newdir = base + '.tmpdata'
				self.copydir = os.path.join(dir, newdir)
				self.copydirurl = MMurl.pathname2url(base+'.data') + '/'
				self.copydirname = base + '.data'
			else:
				newdir = base + '.data'
				self.copydir = os.path.join(dir, newdir)
				self.copydirurl = MMurl.pathname2url(newdir) + '/'
				self.copydirname = newdir
			self.copycache = {}
			try:
				os.mkdir(self.copydir)
			except:
				# raise Error, 'Cannot create subdirectory for assets; document not saved'
				pass # Incorrect: may be because of failed permissions
		else:
			self.copydir = self.copydirurl = self.copydirname = None

		self.__isopen = 0
		self.__stack = []

		self.__cleanSMIL = cleanSMIL
		self.uses_grins_namespace = not cleanSMIL and grinsExt
		self.uses_qt_namespace = features.compatibility == features.QT and not cleanSMIL
		self.smilboston = ctx.attributes.get('project_boston', 0)
		self.root = node
		self.fp = IndentedFile(fp)
		self.__title = ctx.gettitle()

		self.ids_used = {}

		self.ugr2name = {}
		self.calcugrnames(node)

		self.layout2name = {}
		self.calclayoutnames(node)
		
		self.transition2name = {}
		self.calctransitionnames(node)

		self.ch2name = {}
		self.calcchnames1(node)

		self.uid2name = {}
		self.calcnames1(node)

		# second pass
		self.calcnames2(node)
		self.calcchnames2(node)

		# must come after second pass
		self.aid2name = {}
		self.anchortype = {}
		self.calcanames(node)

		self.syncidscheck(node)

	def push(self):
		if self.__isopen:
			self.fp.write('>\n')
			self.__isopen = 0
		self.fp.push()

	def pop(self):
		fp = self.fp
		if self.__isopen:
			start, end = fp.write('/>\n')
			x = self.__stack[-1][2]
			if self.set_char_pos and x is not None:
				x.char_positions = x.char_positions[0], end
			self.__isopen = 0
			del self.__stack[-1]
		fp.pop()
		start, end = fp.write('</%s>\n' % self.__stack[-1][0])
		x = self.__stack[-1][2]
		if self.set_char_pos and x is not None:
			x.char_positions = x.char_positions[0], end
		del self.__stack[-1]

	def close(self):
		fp = self.fp
		if self.__isopen:
			start, end = fp.write('/>\n')
			x = self.__stack[-1][2]
			if self.set_char_pos and x is not None:
				x.char_positions = x.char_positions[0], end
			self.__isopen = 0
			del self.__stack[-1]
		while self.__stack:
			self.pop()
		fp.close()

	def writecomment(self, x):
		write = self.fp.write
		if self.__isopen:
			start, end = write('/>\n')
			n = self.__stack[-1][2]
			if self.set_char_pos and n is not None:
				n.char_positions = n.char_positions[0], end
			self.__isopen = 0
			del self.__stack[-1]
		start, end = write('<!--%s-->\n' % string.join(x.values, '\n'))
		if self.set_char_pos and x is not None:
			x.char_positions = start, end

	def writetag(self, tag, attrs = None, x = None):
		compatibility = features.compatibility
		if attrs is None:
			attrs = []
		write = self.fp.write
		if self.__isopen:
			start, end = write('/>\n')
			n = self.__stack[-1][2]
			if self.set_char_pos and n is not None:
				n.char_positions = n.char_positions[0], end
			self.__isopen = 0
			del self.__stack[-1]
		if self.__stack and self.__stack[-1][1]:
			hasprefix = 1
		else:
			hasprefix = 0
		if not hasprefix and not self.__cleanSMIL:
			for attr, val in attrs:
				if (attr == xmlnsGRiNS) or (attr == xmlnsQT):
					hasprefix = 1
					break
				if attr[:len(NSGRiNSprefix)] == NSGRiNSprefix:
					attrs.insert(0, (xmlnsGRiNS, GRiNSns))
					hasprefix = 1
					break
				if attr[:len(NSQTprefix)] == NSQTprefix:
					attrs.insert(0, (xmlnsQT, QTns))
					hasprefix = 1
					break
		if not hasprefix:
			if tag[:len(NSGRiNSprefix)] == NSGRiNSprefix:
				if self.__cleanSMIL:
					# ignore this tag
					# XXX is this correct?
					return
				attrs.insert(0, (xmlnsGRiNS, GRiNSns))
				hasprefix = 1
			elif tag[:len(NSQTprefix)] == NSQTprefix:
				if self.__cleanSMIL:
					# ignore this tag
					# XXX is this correct?
					return
				attrs.insert(0, (xmlnsQT, QTns))
				hasprefix = 1
		start, end = write('<' + tag)
		if self.set_char_pos and x is not None:
			x.char_positions = start, None
		for attr, val in attrs:
			hasGRiNSprefix = attr[:len(NSGRiNSprefix)] == NSGRiNSprefix or \
				        attr == xmlnsGRiNS
			hasQTprefix = attr[:len(NSQTprefix)] == NSQTprefix or \
				    attr == xmlnsQT
			hasanyprefix = hasGRiNSprefix or hasQTprefix
			if (not hasanyprefix) or \
			   ((hasGRiNSprefix and self.uses_grins_namespace) or \
			   (hasQTprefix and self.uses_qt_namespace)):
				write(' %s=%s' % (attr, nameencode(val)))
		self.__isopen = 1
		self.__stack.append((tag, hasprefix, x))
	
	def writeQTAttributeOnSmilElement(self, attrlist):
		attributes = self.root.GetContext().attributes
		for key, val in attributes.items():
			if key == 'qttimeslider':
				defvalue = MMAttrdefs.getdefattr(None, key)
				if attributes[key] != defvalue:
					attrlist.append(('%s:time-slider' % NSQTprefix, intToEnumString(attributes[key],{0:'false',1:'true'})))
			elif key == 'qtchaptermode':
				defvalue = MMAttrdefs.getdefattr(None, key)
				if attributes[key] != defvalue:
					attrlist.append(('%s:chapter-mode' % NSQTprefix, intToEnumString(attributes[key],{0:'all',1:'clip'})))
			elif key == 'autoplay':
				defvalue = MMAttrdefs.getdefattr(None, key)
				if attributes[key] != defvalue:
					attrlist.append(('%s:autoplay' % NSQTprefix, intToEnumString(attributes[key],{0:'false',1:'true'})))
			elif key == 'qtnext':
				attrlist.append(('%s:next' % NSQTprefix, attributes[key]))
			elif key == 'immediateinstantiation':
				defvalue = MMAttrdefs.getdefattr(None, key)
				if attributes[key] != defvalue:
					attrlist.append(('%s:immediate-instantiation' % NSQTprefix, intToEnumString(attributes[key],{0:'false',1:'true'})))
	
	def write(self):
		import version
		ctx = self.root.GetContext()
		fp = self.fp

		# if the document is not valid, just write the raw source code
		# XXX this code should move to another location. I don't know where ?
		parseErrors = ctx.getParseErrors()
		if parseErrors != None:
			source = parseErrors.getSource()
			fp.write(source)
			fp.close()
			return
			
		fp.write(SMILdecl)	# MUST come first
		if self.evallicense:
			fp.write('<!--%s-->\n' % EVALcomment)
		if self.__cleanSMIL:
			if self.smilboston:
				fp.write(doctype2)
			else:
				fp.write(doctype)
		if ctx.comment:
			fp.write('<!--%s-->\n' % ctx.comment)
		attrlist = []
		if self.smilboston:
			attrlist.append(('xmlns', SMIL2ns[0]))
		if self.uses_grins_namespace:
			attrlist.append((xmlnsGRiNS, GRiNSns))
		if self.uses_qt_namespace:
			attrlist.append((xmlnsQT, QTns))
			self.writeQTAttributeOnSmilElement(attrlist)
		# test attributes are not allowed on the body element,
		# but they are allowed on the smil element, so that's
		# where they get moved
		sysreq = self.root.GetRawAttrDef('system_required', [])
		if sysreq:
			for i in range(len(sysreq)):
				attrlist.append(('xmlns:ext%d' % i, sysreq[i]))
		for name, func in smil_attrs:
			if name[:6] != 'system':
				continue
			value = func(self, self.root)
			if value is None:
				continue
			attrlist.append((name, value))
		self.writetag('smil', attrlist)
		self.push()
		self.writetag('head')
		self.push()
		self.writeusergroups()
		if ctx.metadata:
			self.writetag('metadata', [])
			self.push()
			self.fp.write(ctx.metadata)
			self.pop()
			
		if self.__title:
			self.writetag('meta', [('name', 'title'),
					       ('content', self.__title)])
		if not self.convertURLs and ctx.baseurl:
			self.writetag('meta', [('name', 'base'),
					       ('content', ctx.baseurl)])
		self.writetag('meta', [('name', 'generator'),
				       ('content','GRiNS %s'%version.version)])
		for key, val in ctx.attributes.items():
			# for export don't write attributes starting with project_, they are meant
			# for internal information-keeping only
			if self.__cleanSMIL and key[:8] == 'project_':
				continue
			if key == 'qttimeslider':
				continue
			if key == 'autoplay':
				continue
			if key == 'qtnext':
				continue
			if key == 'qtchaptermode':
				continue
			if key == 'immediateinstantiation':
				continue
			if key == 'qtcompositemode':
				continue
			if key == 'project_boston':
				# never save project_boston
				continue
			if self.__cleanSMIL and key[:8] == 'project_':
				continue
			if key == 'project_boston':
				if val:
					val = 'on'
				else:
					val = 'off'
			self.writetag('meta', [('name', key),
					       ('content', val)])
		if not self.__cleanSMIL and ctx.externalanchors:
			links = []
			for link in ctx.externalanchors:
				links.append(string.join(string.split(link, ' '), '%20'))
			self.writetag('meta', [('name', 'project_links'), ('content', string.join(links))])
		self.writelayout()
		self.writetransitions()
		self.writegrinslayout()
		self.pop()
		self.writenode(self.root, root = 1)
		self.close()

	def writebare(self):
		self.writenode(self.root, root = 1)
		self.close()

	def calcugrnames(self, node):
		"""Calculate unique names for usergroups"""
		usergroups = node.GetContext().usergroups
		if not usergroups:
			return
		self.smilboston = 1
		for ugroup in usergroups.keys():
			name = identify(ugroup)
			if self.ids_used.has_key(name):
				i = 0
				nn = '%s-%d' % (name, i)
				while self.ids_used.has_key(nn):
					i = i+1
					nn = '%s-%d' % (name, i)
				name = nn
			self.ids_used[name] = 1
			self.ugr2name[ugroup] = name

	def calctransitionnames(self, node):
		"""Calculate unique names for transitions"""
		transitions = node.GetContext().transitions
		if not transitions:
			return
		self.smilboston = 1
		for transition in transitions.keys():
			name = identify(transition)
			if self.ids_used.has_key(name):
				i = 0
				nn = '%s-%d' % (name, i)
				while self.ids_used.has_key(nn):
					i = i+1
					nn = '%s-%d' % (name, i)
				name = nn
			self.ids_used[name] = 1
			self.transition2name[transition] = name

	def calclayoutnames(self, node):
		"""Calculate unique names for layouts"""
		layouts = node.GetContext().layouts
		if not layouts:
			return
		self.uses_grins_namespaces = 1
		for layout in layouts.keys():
			name = identify(layout)
			if self.ids_used.has_key(name):
				i = 0
				nn = '%s-%d' % (name, i)
				while self.ids_used.has_key(nn):
					i = i+1
					nn = '%s-%d' % (name, i)
				name = nn
			self.ids_used[name] = 1
			self.layout2name[layout] = name

	def calcnames1(self, node):
		"""Calculate unique names for nodes; first pass"""
		uid = node.GetUID()
		name = node.GetRawAttrDef('name', '')
		if name:
			name = identify(name)
			if not self.ids_used.has_key(name):
				self.ids_used[name] = 1
				self.uid2name[uid] = name
		ntype = node.GetType()
		if ntype in interiortypes:
			for child in node.children:
				self.calcnames1(child)
				for c in child.children:
					self.calcnames1(c)

	def calcnames2(self, node):
		"""Calculate unique names for nodes; second pass"""
		uid = node.GetUID()
		name = node.GetRawAttrDef('name', '')
		if not self.uid2name.has_key(uid):
			isused = name != ''
			if isused:
				name = identify(name)
			else:
				name = 'node'
			# find a unique name by adding a number to the name
			i = 0
			nn = '%s-%d' % (name, i)
			while self.ids_used.has_key(nn):
				i = i+1
				nn = '%s-%d' % (name, i)
			name = nn
			self.ids_used[name] = isused
			self.uid2name[uid] = name
		if node.GetType() in interiortypes:
			for child in node.children:
				self.calcnames2(child)
				for c in child.children:
					self.calcnames2(c)

	def calcchnames1(self, node):
		"""Calculate unique names for channels; first pass"""
		context = node.GetContext()
		channels = context.channels
		for ch in channels:
			name = identify(ch.name)
			if not self.ids_used.has_key(name):
				self.ids_used[name] = 0
				self.ch2name[ch] = name
			if ch.GetParent() is None and \
			   ChannelMap.isvisiblechannel(ch['type']):
				# top-level channel with window
				if not self.__title:
					self.__title = ch.name
			# also check if we need to use the CMIF extension
			if not self.uses_grins_namespace and \
			   not smil_mediatype.has_key(ch['type']) and \
			   ch['type'] != 'layout':
				self.uses_namespaces = 1
		if not self.__title and channels:
			# no channels with windows, so take very first channel
			self.__title = channels[0].name

	def calcchnames2(self, node):
		"""Calculate unique names for channels; second pass"""
		context = node.GetContext()
		channels = context.channels
		top0 = None
		for ch in context.getviewports():
			if ChannelMap.isvisiblechannel(ch['type']):
				if top0 is None:
					# first top-level channel
					top0 = ch.name
				else:
					# second top-level, must be SMIL 2.0
					self.smilboston = 1
					break
		for ch in channels:
			if not self.ch2name.has_key(ch):
				name = identify(ch.name)
				i = 0
				nn = '%s-%d' % (name, i)
				while self.ids_used.has_key(nn):
					i = i+1
					nn = '%s-%d' % (name, i)
				name = nn
				self.ids_used[name] = 0
				self.ch2name[ch] = name
			# check for SMIL 2.0 feature: hierarchical regions
			if not self.smilboston and \
			   ch.GetParent() is not None:
				for sch in ch.GetChildren():
					if sch['type'] == 'layout':
						self.smilboston = 1
						break

	def calcanames(self, node):
		"""Calculate unique names for anchors"""
		uid = node.GetUID()
		for a in node.GetRawAttrDef('anchorlist', []):
			aid = (uid, a.aid)
			self.anchortype[aid] = a.atype
			if a.atype in SourceAnchors:
				if isidre.match(a.aid) is None or \
				   self.ids_used.has_key(a.aid):
					aname = '%s-%s' % (self.uid2name[uid], a.aid)
					aname = identify(aname)
				else:
					aname = a.aid
				if self.ids_used.has_key(aname):
					i = 0
					nn = '%s-%d' % (aname, i)
					while self.ids_used.has_key(nn):
						i = i+1
						nn = '%s-%d' % (aname, i)
					aname = nn
				self.aid2name[aid] = aname
				self.ids_used[aname] = 0
		if node.GetType() in interiortypes:
			for child in node.children:
				self.calcanames(child)

	def syncidscheck(self, node):
		# make sure all nodes referred to in sync arcs get their ID written
		for arc in node.GetRawAttrDef('beginlist', []) + node.GetRawAttrDef('endlist', []):
			# see also getsyncarc() for similar code
			if arc.srcnode is None and arc.event is None and arc.marker is None and arc.wallclock is None and arc.accesskey is None:
				pass
			elif arc.wallclock is not None:
				pass
			elif arc.accesskey is not None:
				pass
			elif arc.marker is None:
				if arc.channel is not None:
					pass
				elif arc.srcanchor is not None:
					aid = (arc.srcnode.GetUID(), arc.srcanchor)
					self.ids_used[self.aid2name[aid]] = 1
				elif arc.srcnode in ('syncbase', 'prev'):
					pass
				elif arc.srcnode is not node:
					self.ids_used[self.uid2name[arc.srcnode.GetUID()]] = 1
			else:
				self.ids_used[self.uid2name[arc.srcnode.GetUID()]] = 1
		for child in node.children:
			self.syncidscheck(child)

	def __writeRegPoint(self):
		regpoints = self.root.GetContext().regpoints
		for name, regpoint in regpoints.items():
			if regpoint.isdefault():
				continue
				
			attrlist = []
			attrlist.append(('id', name))
			
			for attr, val in regpoint.items():
				# for instance, we assume that a integer type value is a pixel value,
				# and a float type value is a relative value (%)
				if attr == 'top' or attr == 'bottom' or attr == 'left' or attr == 'right':
					if type(val) == type(0):
						attrlist.append((attr, '%d' % val))
					else:
						attrlist.append((attr, '%d%%' % int(val * 100 + .5)))
				else:
					attrlist.append((attr, val))
				
			self.writetag('regPoint', attrlist)

	def writelayout(self):
		"""Write the layout section"""
		attrlist = []
		self.writetag('layout', attrlist)
		self.push()
		if self.smilboston:
			self.__writeRegPoint()		
		channels = self.root.GetContext().channels
		for ch in self.root.GetContext().getviewports():
			attrlist = []
			if ch['type'] == 'layout':
				attrlist.append(('id', self.ch2name[ch]))
			title = ch.get('title')
			if title:
				attrlist.append(('title', title))
			elif self.ch2name[ch] != ch.name:
				attrlist.append(('title', ch.name))
			if ch.has_key('bgcolor'):
				bgcolor = ch['bgcolor']
			elif features.compatibility == features.G2:
				bgcolor = 0,0,0
			elif self.smilboston:
				bgcolor = 0,0,0
			else:
				bgcolor = 255,255,255
			bgcolor = translatecolor(bgcolor)
			if self.smilboston:
				attrlist.append(('backgroundColor', bgcolor))
			else:
				attrlist.append(('background-color', bgcolor))

			if self.smilboston:
				# write only not default value
				if ch.has_key('open'):
					val = ch['open']
					if val != 'onStart':
						attrlist.append(('open', val))
				if ch.has_key('close'):
					val = ch['close']
					if val != 'onRequest':
						attrlist.append(('close', val))

			for name in ['width', 'height']:
				value = ch.getCssRawAttr(name)
				if type(value) == type(0.0):
					attrlist.append((name, '%d%%' % int(value * 100 + .5)))
				elif type(value) == type(0):
					attrlist.append((name, '%d' % value))

			# special case: collapse information
			if ch.collapsed == 1:
				attrlist.append(('%s:collapsed' % NSGRiNSprefix, 'true'))
			elif ch.collapsed == 0:
				attrlist.append(('%s:collapsed' % NSGRiNSprefix, 'false'))
			else:
				# default behavior. depend of the node
				pass

			# trace image
			traceImage = ch.get('traceImage')
			if traceImage != None:
				attrlist.append(('%s:traceImage' % NSGRiNSprefix, traceImage))
							
			if self.smilboston:
				for key, val in ch.items():
					if not cmif_chan_attrs_ignore.has_key(key):
						attrlist.append(('%s:%s' % (NSGRiNSprefix, key), MMAttrdefs.valuerepr(key, val)))
				self.writetag('topLayout', attrlist, ch)
				self.push()
				self.writeregion(ch)
				self.pop()
			else:
				# not smilboston implies one top-level
				self.writetag('root-layout', attrlist, ch)
				self.writeregion(ch)
												
		self.pop()

	def writeregion(self, ch):
		mtype, xtype = mediatype(ch['type'], error=1)
		if ch['type'] == 'layout' and \
		   ch.GetParent() is None:
			# top-level layout channel has been handled
			for sch in ch.GetChildren():
				self.writeregion(sch)
			return
		attrlist = [('id', self.ch2name[ch])]
		if ch.has_key('regionName'):
			attrlist.append(('regionName', ch['regionName']))
		title = ch.get('title')
		if title:
			attrlist.append(('title', title))
		elif self.ch2name[ch] != ch.name:
			attrlist.append(('title', ch.name))
	
		for name in ['left', 'width', 'right', 'top', 'height', 'bottom']:
			value = ch.getCssRawAttr(name)
			# write only no auto values
			if value != None:
				if type(value) is type(0.0):
					value = '%d%%' % int(value*100+0.5)
				elif type(value) is type(0):
					value = '%d' % value
				attrlist.append((name, value))
		if ChannelMap.isvisiblechannel(ch['type']):
			z = ch.get('z', 0)
			if z > 0:
				attrlist.append(('z-index', "%d" % z))
			fit = ch.getCssRawAttr('fit','hidden')
			if fit not in ('meet','slice','hidden','fill','scroll'):
				fit = None
				print '** Channel uses unsupported fit value', name
			if fit is not None and fit != 'hidden':
				attrlist.append(('fit', fit))

		#
		# Background color for SMIL before version 2:
		#
		
			# SMIL says: either background-color
			# or transparent; if different, set
			# GRiNS attributes
		# We have the following possibilities:
		#		no bgcolor	bgcolor set
		#transp -1	no attr		b-g="bg"
		#transp  0	GR:tr="0"	GR:tr="0" b-g="bg"
		#transp  1	b-g="trans"	b-g="trans" (ignore bg)
		
			if not self.smilboston:
				transparent = ch.get('transparent', 0)
				bgcolor = ch.get('bgcolor')
				if transparent == 0:
					if features.compatibility == features.G2:
						# in G2, setting a
						# background-color implies
						# transparent==never, so set
						# background-color if not
						# transparent
						bgcolor = translatecolor(bgcolor)
						attrlist.append(('background-color',
								 bgcolor))
						bgcolor = None # skip below
					# non-SMIL extension:
					# permanently visible region
					attrlist.append(('%s:transparent' % NSGRiNSprefix,
								 '0'))
				#
				# We write the background color only if it is not None.
				# We also refrain from writing it if we're in G2 compatability mode and
				# the color is the default (g2-compatible) color: white for text channels
				# and black for others.
				if bgcolor is not None and \
				   (features.compatibility != features.G2 or
				    ((ch['type'] not in ('text', 'RealText') or
				      bgcolor != (255,255,255)) and
				     bgcolor != (0,0,0))) and \
				     (not self.__cleanSMIL or ch['type'] != 'RealText'):
					bgcolor = translatecolor(bgcolor)
					attrlist.append(('background-color',
							 bgcolor))
			# Since background-color="transparent" is the
			# default, we don't need to actually write that

		#
		# Background color for SMIL version 2:
		#
			# no transparent or bgcolor attribute : inherit value
			# transparent != 0 : transparent (default value)
			# otherwise : bgcolor
			else:
				transparent = ch.get('transparent', None)
				bgcolor = ch.get('bgcolor', None)
				if transparent == None:
					bgcolor = 'inherit'
				elif transparent != 0:
					# default value
					bgcolor = None
				elif bgcolor != None:
					bgcolor = translatecolor(bgcolor)

				if bgcolor != None:					
					attrlist.append(('backgroundColor', bgcolor))
								
			# we save the showBackground attribute only if it's not the default value
			showBackground = ch.get('showBackground', 'always')
			if showBackground != 'always':
				attrlist.append(('showBackground', showBackground))
			
			if self.smilboston:
				soundLevel = ch.get('soundLevel')
			# we save only the soundLevel attribute if it exists and different of default value
				if soundLevel != None and soundLevel != 1.0:
					value = '%d%%' % int(soundLevel*100)
					attrlist.append(('soundLevel', value))
			
				regPoint = ch.get('regPoint')
				if regPoint != None:
					attrlist.append(('regPoint',regPoint))
				
				regAlign = ch.get('regAlign')
				if regAlign != None and regAlign != 'topLeft':
					attrlist.append(('regAlign',regAlign))
				
		# for layout channel the chsubtype attribute is translated to grins:type attribute
		subtype = ch.get('chsubtype')
		if subtype != None:
			attrlist.append(('%s:type' % NSGRiNSprefix, subtype))

		# special case: collapse information
		if ch.collapsed == 1:
			attrlist.append(('%s:collapsed' % NSGRiNSprefix, 'true'))
		elif ch.collapsed == 0:
			attrlist.append(('%s:collapsed' % NSGRiNSprefix, 'false'))
		else:
			# default behavior. depend of the node
			pass
													
		for key, val in ch.items():
			if not cmif_chan_attrs_ignore.has_key(key):
				attrlist.append(('%s:%s' % (NSGRiNSprefix, key), MMAttrdefs.valuerepr(key, val)))
		self.writetag('region', attrlist, ch)
		subchans = ch.GetChildren()

		# new 03-07-2000
		# cnt sub layoutchannel number --> to allow to close the tag if no element inside
		lcNumber = 0
		if subchans:
			for sch in subchans:
				if sch['type'] == 'layout':
					lcNumber = lcNumber + 1
		# end new
		
		if lcNumber > 0:
			self.push()
			for sch in subchans:
				# new 03-07-2000
				# save only the layout channels
				if sch['type'] == 'layout':
				# end new
					self.writeregion(sch)
			self.pop()

	def writeusergroups(self):
		u_groups = self.root.GetContext().usergroups
		if not u_groups:
			return
		self.writetag('customAttributes')
		self.push()
		for key, val in u_groups.items():
			attrlist = []
			attrlist.append(('id', self.ugr2name[key]))
			title, u_state, override, uid = val
			if title:
				attrlist.append(('title', title))
			if u_state == 'RENDERED':
				attrlist.append(('defaultState', 'true'))
			if override == 'visible':
				attrlist.append(('override', 'visible'))
			if uid:
				attrlist.append(('uid', uid))
			self.writetag('customTest', attrlist)
		self.pop()

	def writetransitions(self):
		transitions = self.root.GetContext().transitions
		if not transitions:
			return
		defaults = {
			'dur':'1',
			'startProgress':'0',
			'endProgress':'1',
			'fadeColor':'black',
			'direction':'forward',
			'vertRepeat':'1',
			'horzRepeat':'1',
			'borderWidth':'0',
			'borderColor':'black',
			'coordinated':'false',
			'clipBoundary':'children',
			}
		for key, val in transitions.items():
			attrlist = []
			attrlist.append(('id', self.transition2name[key]))
			for akey, aval in val.items():
				if akey in ('fadeColor', 'borderColor'):
					aval = translatecolor(aval)
				elif akey[:1] == '_':
					continue
				elif akey == 'coordinated':
					aval = ['false', 'true'][aval]
				elif akey != 'subtype':
					aval = MMAttrdefs.valuerepr(akey, aval)
					if akey == 'trtype':
						akey = 'type'
				if defaults.has_key(akey) and defaults[akey] == aval:
					continue
				attrlist.append((akey, aval))
			self.writetag('transition', attrlist)

	def writegrinslayout(self):
		layouts = self.root.GetContext().layouts
		if not layouts:
			return
		self.writetag('%s:layouts' % NSGRiNSprefix)
		self.push()
		for name, chans in layouts.items():
			channames = []
			for ch in chans:
				channames.append(self.ch2name[ch])
			self.writetag('%s:layout' % NSGRiNSprefix,
				      [('id', self.layout2name[name]),
				       ('regions', string.join(channames))])
		self.pop()

	def writenode(self, x, root = 0):
		"""Write a node (possibly recursively)"""
		type = x.GetType()
		# XXX I don't like this special casing here --sjoerd
		if type=='animate':
			if root:
				self.writetag('body')
				self.push()
			self.writeanimatenode(x)
			return
		elif type=='prefetch':
			if root:
				self.writetag('body')
				self.push()
			self.writeprefetchnode(x)
			return
		elif type == 'comment':
			self.writecomment(x)
			return

		attrlist = []

		interior = (type in interiortypes)
		if interior:
			if type == 'prio':
				xtype = mtype = 'priorityClass'
			elif type == 'seq' and root and self.smilboston:
				xtype = mtype = 'body'
			elif type == 'foreign':
				tag = x.GetRawAttrDef('tag', None)
				if ' ' in tag:
					ns, tag = string.split(tag, ' ', 1)
					xtype = mtype = 'foreign:%s' % tag
					attrlist.append(('xmlns:foreign', ns))
				else:
					ns = ''
					xtype = mtype = tag
			else:
				xtype = mtype = type
		else:
			chtype = x.GetChannelType()
			if not chtype:
				chtype = 'unknown'
			mtype, xtype = mediatype(chtype)

		# if node used as destination, make sure it's id is written
		uid = x.GetUID()
		name = self.uid2name[uid]
		if not self.ids_used[name]:
			alist = x.GetAttrDef('anchorlist', [])
			hlinks = x.GetContext().hyperlinks
			for a in alist:
				if hlinks.finddstlinks((uid, a.aid)):
					self.ids_used[name] = 1
					break

		attributes = self.attributes.get(xtype, {})
		if type == 'prio':
			attrs = prio_attrs
		elif type == 'foreign':
			attrs = []
			extensions = {ns: 'foreign'}
			for attr, val in x.attrdict.items():
				if attr == 'tag':
					continue
				if ' ' in attr:
					ans, attr = string.split(attr, ' ', 1)
					if not extensions.has_key(ans):
						extensions[ans] = 'x%s' % len(extensions)
						attrlist.append(('xmlns:%s' % extensions[ans], ans))
					attr = '%s:%s' % (extensions[ans], attr)
				attrlist.append((attr, val))
		else:
			attrs = smil_attrs
			if xtype != 'body':
				# special case for systemRequired
				sysreq = x.GetRawAttrDef('system_required', [])
				for i in range(len(sysreq)):
					attrlist.append(('xmlns:ext%d' % i, sysreq[i]))
				
		for name, func in attrs:
			value = func(self, x)
			# gname is the attribute name as recorded in attributes
			# name is the attribute name as recorded in SMIL file
			gname1 = '%s %s' % (GRiNSns, name)
			gname2 = '%s %s' % (QTns, name)
			if attributes.has_key(gname1):
				name = '%s:%s' % (NSGRiNSprefix, name)
				gname = gname1
			elif attributes.has_key(gname2):
				name = '%s:%s' % (NSQTprefix, name)
				gname = gname2
			else:
				gname = name
			# only write attributes that have a value and are
			# legal for the type of node
			# other attributes are caught below
			if value and ((attributes.has_key(gname) and
				       value != attributes[gname]) or
				      name[:6] == 'xmlns:'):
				attrlist.append((name, value))
		is_realpix = type == 'ext' and x.GetChannelType() == 'RealPix'
		if not interior and root:
			self.writetag('body')
			self.push()
		if interior:
			if type == 'seq' and self.copydir and not x.GetChildren():
				# Warn the user for a bug in G2
				import windowinterface
				windowinterface.showmessage('Warning: some G2 versions crash on empty sequence nodes')
				x.set_infoicon('error', 'Warning: some G2 versions crash on empty sequence nodes')
			if root:
				if type != 'seq' or (not self.smilboston and attrlist):
					self.writetag('body')
					self.push()
				else:
					mtype = 'body'
			self.writetag(mtype, attrlist, x)
			self.push()
			for child in x.GetChildren():
				self.writenode(child)
			self.pop()
		elif is_realpix and self.copydir:
			# If we are exporting handle RealPix specially: we might want
			# to convert it into a <par> containing a realpix node and a
			# realtext caption node
			self.writerealpixnode(x, attrlist, mtype)
		elif type in ('imm', 'ext', 'brush'):
			self.writemedianode(x, attrlist, mtype)
		else:
			raise CheckError, 'bad node type in writenode'

	def writerealpixnode(self, x, attrlist, mtype):
		# Special case for realpix, so we get a chance to write the RealText captions
		# if needed
		rturl, channel = self.getrealtextcaptions(x)
		if not rturl:
			self.writemedianode(x, attrlist, mtype)
			return
		region = self.ch2name[channel]
		parentattrlist = []
		for attr, val in attrlist:
			if attr in ('id', 'begin'):
				parentattrlist.append((attr, val))
		for item in parentattrlist:
			attrlist.remove(item)
		self.writetag('par', parentattrlist, x)
		self.push()
		self.writemedianode(x, attrlist, mtype)
		self.writetag('textstream', [('src', rturl), ('region', region)])
		self.pop()
		
	def getrealtextcaptions(self, node):
		"""Return None or, only for RealPix nodes with captions, the source
		for the realtext caption file and the channel to play it on"""
		ntype = node.GetType()
		chtype = node.GetChannelType()
		if ntype != 'ext' or chtype != 'RealPix':
			return None, None
		rtchannel = node.GetChannel(attrname='captionchannel')
		if not rtchannel or rtchannel == 'undefined':
			return None, None
		file = self.gen_rtfile()
		self.files_generated[file] = ''
		import realsupport
		realsupport.writeRT(os.path.join(self.copydir, file), node.slideshow.rp, node)
		val = MMurl.basejoin(self.copydirurl, MMurl.pathname2url(file))
		return val, rtchannel
	
	def writeQTAttributeOnMediaElement(self, node, attrlist):
		dict = node.GetAttrDict()
		for key, val in dict.items():
			if key == 'immediateinstantiationmedia':
				attrlist.append(('%s:immediate-instantiation' % NSQTprefix, intToEnumString(val,{0:'false',1:'true'})))
			if key == 'bitratenecessary':
				attrlist.append(('%s:bitrate' % NSQTprefix, '%d' % val))
			if key == 'systemmimetypesupported':
				attrlist.append(('%s:system-mime-type-supported' % NSQTprefix, val))
			if key == 'attachtimebase':
				defvalue = MMAttrdefs.getdefattr(None, 'attachtimebase')
				if val != defvalue:
					attrlist.append(('%s:attach-timebase' % NSQTprefix, intToEnumString(val,{0:'false',1:'true'})))
			if key == 'qtchapter':
				attrlist.append(('%s:chapter' % NSQTprefix, val))
			if key == 'qtcompositemode':
				attrlist.append(('%s:composite-mode' % NSQTprefix, val))

	def writemedianode(self, x, attrlist, mtype):
		# XXXX Not correct for imm
		pushed = 0
		alist = x.GetRawAttrDef('anchorlist', [])

		if self.uses_qt_namespace:
			self.writeQTAttributeOnMediaElement(x,attrlist)

		self.writetag(mtype, attrlist, x)
		fg = x.GetRawAttrDef('fgcolor', None)
		if fg is not None and mtype == 'text':
			if not pushed:
				self.push()
				pushed = 1
			self.writetag('param', [('name','fgcolor'),('value',translatecolor(fg))], x)
		hassrc = 0		# 1 if has source anchors
		for a in alist:
			if a.atype in SourceAnchors:
				hassrc = 1
				break
		if hassrc:
			if not pushed:
				self.push()
				pushed = 1
			for a in alist:
				if a.atype in SourceAnchors:
					self.writelink(x, a)
		children = x.GetChildren()
		if children:
			if not pushed:
				self.push()
				pushed = 1
			for child in x.GetChildren():
				self.writenode(child)
		if pushed:
			self.pop()

	def writeanimatenode(self, node):
		attrlist = []
		tag = node.GetAttrDict().get('atag')
		attributes = self.attributes.get(tag, {})
		for name, func in smil_attrs:
			if attributes.has_key(name):
				if name == 'type':
					value = node.GetRawAttrDef('trtype', None)
				else:
					value = func(self, node)
				if value and value != attributes[name]:
					attrlist.append((name, value))
		self.writetag(tag, attrlist, node)

	def writeprefetchnode(self, node):
		attrlist = []
		attributes = self.attributes.get('prefetch', {})
		for name, func in smil_attrs:
			if attributes.has_key(name):
				value = func(self, node)
				if value and value != attributes[name]:
					attrlist.append((name, value))
		self.writetag('prefetch', attrlist, node)



	def linkattrs(self, a2, ltype, stype, dtype, accesskey):
		attrs = []
		# deprecated
#		if ltype == Hlinks.TYPE_CALL:
#			attrs.append(('show', "pause"))
		if ltype == Hlinks.TYPE_JUMP:
			# default value, so we don't need to write it
			pass
		elif ltype == Hlinks.TYPE_FORK:
			attrs.append(('show', 'new'))
			if stype == Hlinks.A_SRC_PLAY:
				# default sourcePlaystate value
				pass
			elif stype == Hlinks.A_SRC_PAUSE:
				attrs.append(('sourcePlaystate', 'pause'))			
			elif stype == Hlinks.A_SRC_STOP:
				attrs.append(('sourcePlaystate', 'stop'))
		
		if dtype == Hlinks.A_DEST_PLAY:
			# default value, so we don't need to write it
			pass
		elif dtype == Hlinks.A_DEST_PAUSE:
				attrs.append(('destinationPlaystate', 'pause'))
							
		# else show="replace" (default)
		if type(a2) is type(()):
			uid2, aid2 = a2
			if '/' in uid2:
				if aid2:
					href, tag = a2
				else:
					lastslash = string.rfind(uid2, '/')
					href, tag = uid2[:lastslash], uid2[lastslash+1:]
					if tag == '1':
						tag = None
			else:
				href = ''
				if self.anchortype.get(a2) == ATYPE_NORMAL and \
				   self.aid2name.has_key(a2):
					tag = self.aid2name[a2]
				else:
					tag = self.uid2name[uid2]
			if tag:
				href = href + '#' + tag
		else:
			href = a2
		attrs.append(('href', href))

		if accesskey is not None:
			attrs.append(('accesskey', accesskey))

		return attrs

	def writelink(self, x, a):
		attrlist = []
		aid = (x.GetUID(), a.aid)
		attrlist.append(('id', self.aid2name[aid]))

		links = x.GetContext().hyperlinks.findsrclinks(aid)
		if links:
			if len(links) > 1:
				print '** Multiple links on anchor', \
				      x.GetRawAttrDef('name', '<unnamed>'), \
				      x.GetUID()
			a1, a2, dir, ltype, stype, dtype = links[0]
			attrlist[len(attrlist):] = self.linkattrs(a2, ltype, stype, dtype, a.aaccess)
		if a.atype == ATYPE_NORMAL:
			ok = 0
			# WARNING HACK HACK HACK : How know if it's a shape or a fragment ?
			try:
				shapeType = a.aargs[0]
				if shapeType == A_SHAPETYPE_RECT or shapeType == A_SHAPETYPE_POLY or \
						shapeType == A_SHAPETYPE_CIRCLE:
					coords = []
					for c in a.aargs[1:]:
						if type(c) == type(0):
							# pixel coordinates
							coords.append('%d' % c)
						else:
							# relative coordinates
							coords.append(fmtfloat(c*100, '%', prec = 2))
					coords = string.join(coords, ',')
					ok = 1
				elif shapeType == A_SHAPETYPE_ALLREGION:
					ok = 1
			except:
				pass						
			if ok:
				if shapeType == A_SHAPETYPE_POLY:
					attrlist.append(('shape', 'poly'))
				elif shapeType == A_SHAPETYPE_CIRCLE:
					attrlist.append(('shape', 'circle'))
				elif shapeType == A_SHAPETYPE_RECT:
					attrlist.append(('shape', 'rect'))
					
				if shapeType != A_SHAPETYPE_ALLREGION:
					attrlist.append(('coords', coords))
			else:
				attrlist.append(('fragment', a.aid))						
		elif a.atype == ATYPE_AUTO:
			attrlist.append(('actuate', 'onLoad'));
			
		begin, end = a.atimes
		if begin:
			attrlist.append(('begin', fmtfloat(begin, 's')))
		if end:
			attrlist.append(('end', fmtfloat(end, 's')))
		if self.smilboston:
			self.writetag('area', attrlist)
		else:
			self.writetag('anchor', attrlist)

	def newfile(self, srcurl):
		import posixpath, urlparse
		utype, host, path, params, query, fragment = urlparse.urlparse(srcurl)
		if utype == 'data':
			import MMmimetypes
			mtype = MMmimetypes.guess_type(srcurl)[0]
			if mtype is None:
				mtype = 'text/plain'
			ext = MMmimetypes.guess_extension(mtype)
			base = 'data'
		else:
			file = MMurl.url2pathname(posixpath.basename(path))
			base, ext = os.path.splitext(file)
		if self.bases_used.has_key(base):
			i = 1
			while self.bases_used.has_key(base + `i`):
				i = i + 1
			base = base + `i`
		self.bases_used[base] = None
		self.files_generated[base + ext] = None
		return base + ext
	
	def copyfile(self, srcurl, node = None):
		dstdir = self.copydir
		file = self.newfile(srcurl)
		u = MMurl.urlopen(srcurl)
		if not self.convert:
			convert = 0
		elif node is not None:
			if type(node) == type({}):
				convert = node.get('project_convert', 1)
			else:
				convert = node.GetRawAttrDef('project_convert', 1)
		else:
			convert = 1

		if convert and u.headers.maintype == 'audio' and \
		   string.find(u.headers.subtype, 'real') < 0:
			from realconvert import convertaudiofile
			# XXXX This is a hack. convertaudiofile may change the filename (and
			# will, currently, to '.ra').
			if self.progress:
				self.progress("Converting %s"%os.path.split(file)[1], None, None, None, None)
				progress = (self.progress, ("Converting %s"%os.path.split(file)[1], None, None))
			else:
				progress = None
			cfile = convertaudiofile(u, dstdir, file, node,
						progress = progress)
			if cfile:
				self.files_generated[cfile] = 'b'
				return cfile
			msg = "Warning: cannot convert to RealAudio:\n%s\n\nUsing source material unconverted."%srcurl
			if node:
				node.set_infoicon('error', msg)
			import windowinterface
			windowinterface.showmessage(msg)
			u = MMurl.urlopen(srcurl)
		if convert and u.headers.maintype == 'video' and \
		   string.find(u.headers.subtype, 'real') < 0:
			from realconvert import convertvideofile
			# XXXX This is a hack. convertvideofile may change the filename (and
			# will, currently, to '.rm').
			if self.progress:
				self.progress("Converting %s"%os.path.split(file)[1], None, None, None, None)
				progress = (self.progress, ("Converting %s"%os.path.split(file)[1], None, None))
			else:
				progress = None
			cfile = convertvideofile(u, srcurl, dstdir, file, node, progress = progress)
			if cfile:
				self.files_generated[cfile] = 'b'
				return cfile
			msg = "Warning: cannot convert to RealVideo:\n%s\n\nUsing source material unconverted."%srcurl
			if node:
				node.set_infoicon('error', msg)
			import windowinterface
			windowinterface.showmessage(msg)
			u = MMurl.urlopen(srcurl)
		if convert and u.headers.maintype == 'image':
			from realconvert import convertimagefile
			# XXXX This is a hack. convertimagefile may change the filename (and
			# will, currently, to '.jpg').
			if self.progress:
				self.progress("Converting %s"%os.path.split(file)[1], None, None, None, None)
			try:
				cfile = convertimagefile(u, srcurl, dstdir, file, node)
			except:
				# XXXX Too many different errors can occur in convertimagefile:
				# I/O errors, image file errors, etc.
				cfile = None
			if cfile:
				self.files_generated[cfile] = 'b'
				return cfile
			msg = "Warning: cannot convert to Real JPEG:\n%s\n\nUsing source material unconverted."%srcurl
			if node:
				node.set_infoicon('error', msg)
			import windowinterface
			windowinterface.showmessage(msg)
			u = MMurl.urlopen(srcurl)
		if convert and u.headers.maintype == 'text' and \
		   string.find(u.headers.subtype, 'real') < 0:
			from realconvert import converttextfile
			# XXXX This is a hack. convertaudiofile may change the filename (and
			# will, currently, to '.rt').
			if self.progress:
				self.progress("Converting %s"%os.path.split(file)[1], None, None, None, None)
			file = converttextfile(u, dstdir, file, node)
			self.files_generated[file] = ''
			return file
		if u.headers.maintype == 'text':
			binary = ''
		else:
			binary = 'b'
		self.files_generated[file] = binary
		if self.progress:
			self.progress("Copying %s"%os.path.split(file)[1], None, None, None, None)
		dstfile = os.path.join(dstdir, file)
#		print 'DBG verbatim copy', dstfile
		f = open(dstfile, 'w'+binary)
		while 1:
			data = u.read(10240)
			if not data:
				break
			f.write(data)
		f.close()
		u.close()
		if os.name == 'mac':
			import ic, macfs, macostools
			try:
				icinfo = ic.mapfile(dstfile)
			except ic.error:
				if binary:
					tp = '????'
					cr = '????'
				else:
					tp = 'TEXT'
					cr = 'ttxt'
			else:
				tp = icinfo[1]
				cr = icinfo[2]
			fss = macfs.FSSpec(dstfile)
			fss.SetCreatorType(cr, tp)
			macostools.touched(fss)
				
		return file
		
	def getcopyinfo(self):
		return self.copydir, self.copydirname, self.files_generated

	def gen_rpfile(self):
		i = self.__generate_number
		self.__generate_number = self.__generate_number + 1
		return self.__generate_basename + `i` + '.rp'

	def gen_rtfile(self):
		i = self.__generate_number
		self.__generate_number = self.__generate_number + 1
		return self.__generate_basename + `i` + '.rt'

htmlnamechars = string.letters + string.digits + '_.'
namechars = htmlnamechars + '-'

def identify(name, html = 0):
	"""Turn a CMIF name into an identifier"""
	if html:
		minus = '_'
		nmchrs = htmlnamechars
	else:
		minus = '-'
		nmchrs = namechars
	rv = []
	for ch in name:
		if ch in nmchrs:
			rv.append(ch)
		else:
			if rv and rv[-1] != minus:
				rv.append(minus)
	# the first character must not be a digit
	if rv and rv[0] in string.digits:
		rv.insert(0, '_')
	return string.join(rv, '')

def intToEnumString(intValue, dict):
	if dict.has_key(intValue):
		return dict[intValue]
	else:
		return dict[0]
