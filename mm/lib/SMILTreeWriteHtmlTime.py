__version__ = "$Id$"


#
#	Export interface 
# 
def WriteFileAsHtmlTime(root, filename, cleanSMIL = 0, grinsExt = 1, copyFiles = 0, evallicense = 0, progress = None, convertURLs = 0):
	fp = IndentedFile(open(filename, 'w'))
	try:
		writer = SMILHtmlTimeWriter(root, fp, filename, cleanSMIL, grinsExt, copyFiles, evallicense, progress = progress, convertURLs = convertURLs)
	except Error, msg:
		from windowinterface import showmessage
		showmessage(msg, mtype = 'error')
		return
	writer.writeAsHtmlTime()


#
#	XHTML+TIME DTD 
# 
class XHTML_TIME:
	__basicTiming = {'begin':None,
			 'dur':None,
			 'end':None,
			 'repeatCount':None,
			 'repeatDur':None,
			 }
	__Timing = {'restart':None,
		    'syncBehavior':None,
		    'syncMaster':None,
		    }
	__TimeManipulators = {'speed':None,
		    'accelerate':None,
		    'decelerate':None,
		    'autoReverse':None,
		    }
	attributes = {
		'animate': {},
		'animateColor': {},
		'animateMotion': {},
		'audio': {},
		'excl': {},
		'img': {},
		'media': {},
		'par': {},
		'priorityClass': {},
		'ref': {},
		'seq': {},
		'set': {},
		'video': {},
	}


#
#	SMILHtmlTimeWriter
# 
from SMILTreeWrite import *

class SMILHtmlTimeWriter(SMIL):
	def __init__(self, node, fp, filename, cleanSMIL = 0, grinsExt = 1, copyFiles = 0,
		     evallicense = 0, tmpcopy = 0, progress = None,
		     convertURLs = 0):
		ctx = node.GetContext()
		self.root = node
		self.fp = fp
		self.__title = ctx.gettitle()

		self.smilboston = ctx.attributes.get('project_boston', 0)
		self.copydir = self.copydirurl = self.copydirname = None
		self.convertURLs = None

		self.ids_used = {}

		self.ugr2name = {}
		self.calcugrnames(node)

		self.layout2name = {}
		self.calclayoutnames(node)
		
		self.transition2name = {}
		self.calctransitionnames(node)

		self.ch2name = {}
		self.top_levels = []
		self.__subchans = {}
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

		self.__isopen = 0
		self.__stack = []

		self.__currViewport = None
		self.ch2style = {}
		self.ids_written = {}
		

	def writeAsHtmlTime(self):
		write = self.fp.write
		import version
		write('<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\">\n')
		self.writetag('html', [('xmlns:t','urn:schemas-microsoft-com:time')])
		self.push()

		# head
		self.writetag('head')
		self.push()
		
		# head contents
		if self.__title:
			self.writetag('meta', [('name', 'title'),
					       ('content', self.__title)])
		self.writetag('meta', [('name', 'generator'),
				       ('content','GRiNS %s'%version.version)])
		
		# style
		self.writetag('style', [('type', 'text/css'),])
		self.push()

		# style contents
		# Internet explorer style conventions for HTML+TIME support part 1
		write('.time {behavior: url(#default#time2);}\n')
		self.writelayout()

		self.pop() # style

		# Internet explorer style conventions for HTML+TIME support part 2
		write('<?IMPORT namespace=\"t\" implementation=\"#default#time2\">\n')

		if self.root.GetContext().transitions:
			write(transScript)

		self.pop() # head

		# body
		self.writetag('body')
		self.push()
		self.writetag('t:seq')
		self.push()
		
		# body contents
		# viewports
		if len(self.top_levels)==1:
			self.__currViewport = ch = self.top_levels[0]
			name = self.ch2name[ch]
			self.writetag('div', [('id',name), ('style', self.ch2style[ch]),])
			self.push()
			self.writenode(self.root, root = 1)
			self.pop()
		else:
			self.writenode(self.root, root = 1)
			
		self.close()

	def writefd(self):
		fulldur = self.root.calcfullduration()
		if fulldur is not None:
			if fulldur<0:
				fulldur = 'indefinite'
			else:
				fulldur = '%ds' % fulldur
			self.writetag('div', [('class', 'time'), ('dur', fulldur)])
		else:
			self.writetag('div', [('class', 'time')])

	def push(self):
		if self.__isopen:
			self.fp.write('>\n')
			self.__isopen = 0
		self.fp.push()

	def pop(self):
		fp = self.fp
		if self.__isopen:
			fp.write('/>\n')
			self.__isopen = 0
			del self.__stack[-1]
		fp.pop()
		fp.write('</%s>\n' % self.__stack[-1])
		del self.__stack[-1]

	def close(self):
		fp = self.fp
		if self.__isopen:
			fp.write('/>\n')
			self.__isopen = 0
			del self.__stack[-1]
		while self.__stack:
			self.pop()
		fp.close()

	def writetag(self, tag, attrs = None):
		if attrs is None:
			attrs = []
		write = self.fp.write
		if self.__isopen:
			write('/>\n')
			self.__isopen = 0
			del self.__stack[-1]
		write('<' + tag)
		for attr, val in attrs:
			write(' %s=%s' % (attr, nameencode(val)))
		self.__isopen = 1
		self.__stack.append(tag)

	def writenode(self, x, root = 0):
		type = x.GetType()

		if type=='imm' and x.GetChannelType()=='animate':
			self.writeanimatenode(x, root)
			return

		interior = (type in interiortypes)
		if interior:
			if type == 'alt':
				xtype = mtype = 'switch'
			elif type == 'prio':
				xtype = mtype = 'priorityClass'
			else:
				xtype = mtype = type
		else:
			chtype = x.GetChannelType()
			if not chtype:
				chtype = 'unknown'
			mtype, xtype = mediatype(chtype)
		
		attrlist = []
		regionName = None
		src = None
		nodeid = None
		transIn = None
		transOut = None

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
		else:
			attrs = smil_attrs
			# special case for systemRequired
			sysreq = x.GetRawAttrDef('system_required', [])
			for i in range(len(sysreq)):
				attrlist.append(('ext%d' % i, sysreq[i]))

		for name, func in attrs:
			value = func(self, x)
			if value and attributes.has_key(name) and value != attributes[name]:
				if interior:
					attrlist.append((name, value))
				else:	
					if name == 'region': 
						regionName = value
					elif name == 'src': 
						src = value
					elif name == 'id':
						self.ids_written[value] = 1
						nodeid = value
					elif name == 'transIn':
						transIn = value
					elif name == 'transOut':
						transOut = value
					if name not in ('id', 'top','left','width','height','right','bottom', 'backgroundColor', 'region', 'src', 'transIn', 'transOut'):
						attrlist.append((name, value))
		
		if interior:
			if not root:
				self.writetag('t:'+mtype, attrlist)
				self.push()
			for child in x.GetChildren():
				self.writenode(child)
			if not root:
				self.pop()

		elif type in ('imm', 'ext'):
			children = x.GetChildren()
			if not children:				
				self.writemedianode(x, nodeid, attrlist, mtype, regionName, src, transIn, transOut)
			else:
				self.writetag(mtype, attrlist)
				self.push()
				for child in x.GetChildren():
					self.writenode(child)
				self.pop()
		else:
			raise CheckError, 'bad node type in writenode'


	def writemedianode(self, x, nodeid, attrlist, mtype, regionName, src, transIn, transOut):
		if mtype=='video':
			mtype = 'media'

		if src: 
			attrlist.append(('src', src))
					
		if mtype == 'audio':
			if nodeid:
				attrlist.insert(0,('id', nodeid))
			self.writetag('t:'+mtype, attrlist)
			return	

		parents = []
		viewport = None
		lch = self.root.GetContext().getchannel(regionName)
		while lch:
			if lch.get('type') != 'layout':
				continue
			if lch in self.top_levels:
				viewport = lch
				break
			parents.insert(0, lch)
			lch = lch.__parent
		
		pushed = 0
		if viewport and self.__currViewport!=viewport:
			if self.__currViewport:
				self.pop()
			name = self.ch2name[viewport]
			self.writetag('div', [('id',name), ('style', self.ch2style[viewport]),])
			self.push()
			self.__currViewport = viewport

		for lch in parents:
			divlist = []
			if self.ch2style.has_key(lch):
				name = self.ch2name[lch]
				divlist.append(('id', name))
				divlist.append(('style', self.ch2style[lch]))
				self.writetag('div', divlist)
				self.push()
				self.ids_written[name] = 1
				pushed = pushed + 1

		transitions = self.root.GetContext().transitions
		if transIn or transOut:
			if not nodeid:
				nodeid = 'm' + x.GetUID()
			subregid = nodeid + 'd1'


		subRegGeom, mediaGeom = None, None
		geoms = x.getPxGeomMedia()
		if geoms:
			subRegGeom, mediaGeom = geoms

		if subRegGeom:
			divlist = []
			style = self.rc2style(subRegGeom)

			if transIn or transOut:
				divlist.append(('id', subregid))
				style = style + 'filter:'
				self.writetag('t:par')
				self.push()
				pushed = pushed + 1
			
			if transIn:
				td = transitions[transIn]
				trtype = td.get('trtype')
				transInDur = td.get('dur')
				if not transInDur: transInDur = 1
				if trtype=='fade':
					transInName = 'Fade'
					style = style + transFade(dur=transInDur)
				else:
					transInName = 'Iris'	
					style = style + transIris(dur=transInDur, style='circle', motion='out')

			if transOut:
				td = transitions[transOut]
				trtype = td.get('trtype')
				transOutDur = td.get('dur')
				if not transOutDur: transOutDur = 1
				if trtype=='fade':
					transOutName = 'Fade'
					style = style + transFade(dur=transOutDur)
				else:
					transOutName = 'Iris'	
					style = style + transIris(dur=transOutDur, style='circle', motion='out')
				
			if transIn or transOut:
				style = style + ';'

			if transIn:
				style = style + 'visibility=hidden;'
			

			divlist.append(('style', style))
			self.writetag('div', divlist)
			self.push()
			pushed = pushed + 1

		if mediaGeom:
			if nodeid:
				attrlist.insert(0,('id', nodeid))
			style = 'position=absolute;left=%d;top=%d;width=%d;height=%d;' % mediaGeom
			attrlist.append( ('style',style) )

		if self.writeAnchors(x):
			self.push()
			pushed = pushed + 1

		self.writetag('t:'+mtype, attrlist)

		if transIn or transOut:
			self.pop()
			pushed = pushed - 1
			if transIn:
				trans = 'transIn(%s, \'%s\')' % (subregid, transInName)
				self.writetag('t:set', [ ('begin','%s.begin' % nodeid), ('dur', '%.1f' % transInDur), ('onbegin', trans), ])
			if transOut:	
				trans = 'transOut(%s, \'%s\')' % (subregid, transOutName)
				self.writetag('t:set', [ ('begin','%s.end-%.1f' % (nodeid,transOutDur)), ('dur', '%.1f' % transOutDur), ('onbegin', trans), ])
			self.pop()
			pushed = pushed - 1
		
		for i in range(pushed):
			self.pop()


	def writeAnchors(self, x):
		alist = MMAttrdefs.getattr(x, 'anchorlist')
		hassrc = 0		# 1 if has source anchors
		for a in alist:
			if a.atype in SourceAnchors:
				hassrc = 1
				break
		if hassrc:
			for a in alist:
				if a.atype in SourceAnchors:
					self.writelink(x, a)
					return 1 # XXX: allow one anchor for now
		return 0

				
	def writeEmptyRegion(self, regionName):
		parents = []
		viewport = None
		lch = self.root.GetContext().getchannel(regionName)
		while lch:
			if lch.get('type') != 'layout':
				continue
			if lch in self.top_levels:
				viewport = lch
				break
			parents.insert(0, lch)
			lch = lch.__parent
		
		pushed = 0
		if viewport and self.__currViewport!=viewport:
			if self.__currViewport:
				self.pop()
			name = self.ch2name[viewport]
			self.ids_written[name] = 1
			self.writetag('div', [('id',name), ('style', self.ch2style[viewport]),])
			self.push()
			self.__currViewport = viewport

		for lch in parents:
			divlist = []
			if self.ch2style.has_key(lch):
				name = self.ch2name[lch]
				divlist.append(('id', name))
				divlist.append(('style', self.ch2style[lch]))
				self.writetag('div', divlist)
				self.ids_written[name] = 1
				self.push()
				pushed = pushed + 1

		for i in range(pushed):
			self.pop()

	def writeanimatenode(self, node, root):
		attrlist = []
		targetElement = None
		tag = node.GetAttrDict().get('tag')
		attributes = self.attributes.get(tag, {})
		for name, func in smil_attrs:
			if attributes.has_key(name):
				value = func(self, node)
				if name == 'targetElement':
					targetElement = value
				if value and value != attributes[name]:
					attrlist.append((name, value))

		if not self.ids_written.has_key(targetElement):
			self.writeTargetElement(targetElement)
		self.writetag('t:'+tag, attrlist)

	def writeTargetElement(self, uid):
		lch = self.root.GetContext().getchannel(uid)
		if lch:
			self.writeEmptyRegion(uid)
			

	def writelayout(self):
		x = xmargin = 20
		y = ymargin = 20
		for ch in self.top_levels:
			w, h = ch.getPxGeom()
			name = self.ch2name[ch]
			if ch.has_key('bgcolor'):
				bgcolor = ch['bgcolor']
			else:
				bgcolor = 255,255,255
			if colors.rcolors.has_key(bgcolor):
				bgcolor = colors.rcolors[bgcolor]
			else:
				bgcolor = '#%02x%02x%02x' % bgcolor
			style = 'position:absolute;overflow:hidden;left=%d;top=%d;width=%d;height=%d;background-color=%s;' % (x, y, w, h, bgcolor)
			self.ch2style[ch] = style
			#self.fp.write('.'+name + ' {' + style + '}\n')

			if self.__subchans.has_key(ch.name):
				for sch in self.__subchans[ch.name]:
					self.writeregion(sch)

			x = x + w + xmargin

	def writeregion(self, ch):
		if ch['type'] != 'layout':
			return

		x, y, w, h = ch.getPxGeom()
		style = 'position:absolute;overflow:hidden;left=%d;top=%d;width=%d;height=%d;' % (x, y, w, h)
		
		if ch.has_key('bgcolor'):
			bgcolor = ch['bgcolor']
			if colors.rcolors.has_key(bgcolor):
				bgcolor = colors.rcolors[bgcolor]
			else:
				bgcolor = '#%02x%02x%02x' % bgcolor
			style = style + 'background-color=%s;' % bgcolor
			
		z = ch.get('z', 0)
		if z > 0:
			style = style + 'z-index=%d;' % z

		self.ch2style[ch] = style

		name = self.ch2name[ch]
		#self.fp.write('.'+name + ' {' + style + '}\n')
		
		if self.__subchans.has_key(ch.name):
			for sch in self.__subchans[ch.name]:
				self.writeregion(sch)
		
	def rc2style(self, rc):
		x, y, w, h = rc
		return 'position:absolute;overflow:hidden;left=%d;top=%d;width=%d;height=%d;' % (x, y, w, h)

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
				attrlist.append(('fragment', id))						
		elif a.atype == ATYPE_AUTO:
			attrlist.append(('actuate', 'onLoad'));
			
		begin, end = a.atimes
		if begin:
			attrlist.append(('begin', fmtfloat(begin, 's')))
		if end:
			attrlist.append(('end', fmtfloat(end, 's')))
		self.writetag('a', attrlist)

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

	#
	#
	#
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
		if ntype == 'bag':
			self.uses_grins_namespaces = 1

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
			if ch.has_key('base_window'):
				pch = ch['base_window']
				if not self.__subchans.has_key(pch):
					self.__subchans[pch] = []
				self.__subchans[pch].append(ch)
			if not ch.has_key('base_window') and \
			   ch['type'] not in ('sound', 'shell', 'python',
					      'null', 'vcr', 'socket', 'cmif',
					      'midi', 'external'):
				# top-level channel with window
				self.top_levels.append(ch)
				if not self.__subchans.has_key(ch.name):
					self.__subchans[ch.name] = []
				if not self.__title:
					self.__title = ch.name
			# also check if we need to use the CMIF extension
			#if not self.uses_grins_namespace and \
			#   not smil_mediatype.has_key(ch['type']) and \
			#   ch['type'] != 'layout':
			#	self.uses_namespaces = 1
		if not self.__title and channels:
			# no channels with windows, so take very first channel
			self.__title = channels[0].name

	def calcchnames2(self, node):
		"""Calculate unique names for channels; second pass"""
		context = node.GetContext()
		channels = context.channels
		if self.top_levels:
			top0 = self.top_levels[0].name
		else:
			top0 = None
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
			if not ch.has_key('base_window') and \
			   ch['type'] in ('sound', 'shell', 'python',
					  'null', 'vcr', 'socket', 'cmif',
					  'midi', 'external') and top0:
				self.__subchans[top0].append(ch)
			# check for SMIL 2.0 feature: hierarchical regions
			if not self.smilboston and \
			   not ch in self.top_levels and \
			   self.__subchans.get(ch.name):
				for sch in self.__subchans[ch.name]:
					if sch['type'] == 'layout':
						self.smilboston = 1
						break

		# enable bottom up search
		for ch in channels:
			ch.__parent = None
		for parentName, childs in self.__subchans.items():
			parchan = self.root.GetContext().getchannel(parentName)
			for ch in childs:
				ch.__parent = parchan

	def calcanames(self, node):
		"""Calculate unique names for anchors"""
		uid = node.GetUID()
		alist = MMAttrdefs.getattr(node, 'anchorlist')
		for a in alist:
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
		for srcuid, srcside, delay, dstside in node.GetRawAttrDef('synctolist', []):
			self.ids_used[self.uid2name[srcuid]] = 1
		if node.GetType() in interiortypes:
			for child in node.children:
				self.syncidscheck(child)

#
#	Transitions
# 
transInScript="function transIn(obj, name){\n  var fname=\"DXImageTransform.Microsoft.\" + name;\n  var filter=obj.filters[fname];\n  if(filter!=null) filter.Apply();\n  obj.style.visibility = \"visible\";\n  if(filter!=null) filter.Play();\n}\n"
transOutScript="function transOut(obj, name){\n  var fname=\"DXImageTransform.Microsoft.\" + name;\n  var filter=obj.filters[fname];\n  if(filter!=null) filter.Play();\n}\n"
transScript = "<script language=JavaScript>\n%s%s</script>\n" % (transInScript, transOutScript)

msfilter = 'progid:DXImageTransform.Microsoft'

def trans(trname='Iris', properties='dur=1.0'):
	return "progid:DXImageTransform.Microsoft.%s(%s) " % (trname, properties)
	
def transIris(dur=1, style='circle', motion='out'):
	return "progid:DXImageTransform.Microsoft.Iris(irisStyle=%s, motion=%s, duration=%.1f) " % (style, motion, dur)

def transBarn(dur=1, orientation='vertical', motion='in'):
	return "progid:DXImageTransform.Microsoft.Barn(orientation=%s, motion=%s, duration=%.1f) " % (orientation, motion, dur)

def transSlide(dur=1, direction='up', bands=1):
	return "progid:DXImageTransform.Microsoft.Slide(direction=%s, bands=%d, duration=%.1f) " % (direction, bands, dur)
	
def transStrips(dur=1, motion='leftdown'):
	return "progid:DXImageTransform.Microsoft.Strips(motion=%s, duration=%.1f) " % (motion, dur)

def transBlinds(dur=1, direction='right'):
	return "progid:DXImageTransform.Microsoft.Blinds(direction=%s, duration=%.1f) " % (direction, dur)

def transCheckerBoard(dur=1, direction='down'):
	return "progid:DXImageTransform.Microsoft.CheckerBoard(direction=%s, duration=%.1f) " % (direction, dur)

def transRandomBars(dur=1, orientation='horizontal'):
	return "progid:DXImageTransform.Microsoft.RandomBars(orientation=%s, duration=%.1f) " % (orientation, dur)

def transFade(dur=1):
	return "progid:DXImageTransform.Microsoft.Fade(duration=%.1f)" % dur

def transRandomDissolve(dur=1):
	return "progid:DXImageTransform.Microsoft.RandomDissolve(duration=%.1f) " % dur

def filterAlpha(opacity=100, finishOpacity=0, style=3):
	return "progid:DXImageTransform.Microsoft.Alpha(Opacity=%d, FinishOpacity=%d, Style=%d) " % (opacity, finishOpacity, style)



#
#########################













 
 