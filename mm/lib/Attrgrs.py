__version__ = "$Id$"

# Each group is a dictionary with entries:
# unique name 'name'
# display title 'title'
# attributes 'attrs'
# optional match method 'match'

# The order of groups in the attrgrs list is important (first is visited first for match)
# All attributes not in complete groups will be displayed on their own page
# unless we specify a different match condition ('part', 'first' default is: 'all')

attrgrs=(
	{'name':'infogroup',
	'title': 'Info',
	'match': 'first',
	'attrs':[
		'title',
		'abstract',
		'alt',
		'longdesc',
		'author',
		'copyright',
		'comment'
		]},


	{'name':'subregion',
	'title':'Destination region',
	'attrs':[
		'subregionxy',
		'subregionwh',
		'displayfull',
		'subregionanchor',
		]},

	{'name':'base_winoff_and_units',
	'title':'Position and size',
	'attrs':[
		'base_winoff',
		'units',
		]},

	{'name':'base_winoff',
	'title':'Position and size',
	'attrs':[
		'base_winoff',
		]},

	{'name':'system',
	'title': 'System properties',
	'attrs':[
		'system_bitrate',
		'system_captions',
		'system_language',
		'system_overdub_or_caption',
		'system_required',
		'system_screen_depth',
		'system_screen_size',
		]},

	{'name':'name',
	'title':'Node name',
	'attrs':[
		'name',
		'channel',
		]},

	{'name':'.cname',
	'title':'Channel name',
	'attrs':[
		'.cname',
		'type',
		]},

	{'name':'duration_and_loop',
	'title':'Duration and loop',
	'attrs':[
		'duration',
		'loop',
		]},
	)


