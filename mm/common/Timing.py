# Interface to calculate the timing of a (sub)tree

import sched

import MMAttrdefs
from MMExc import *
from MMNode import alltypes, leaftypes, interiortypes

from ChannelMap import channelmap

HD, TL = 0, 1	# Same as in Player!


# Calculate the nominal times for each node in the given subtree.
# When the function is done, each node has two instance variables
# 't0' and 't1' that give the begin and end time of the node.
# By definition, 't0' for the given root is zero; its 't1' value
# gives the total duration.
#
# This takes sync arcs within the subtree into account, but ignores
# sync arcs with one end outside the given subtree.
#
# Any circularities in the sync arcs are detected and "reported"
# as exceptions.
#
def calctimes(root):
	prepare(root)
	pt = pseudotime().init(0.0)
	q = sched.scheduler().init(pt.timefunc, pt.delayfunc)
	root.counter[HD] = 1
	decrement(q, (0, root, HD))
	q.run()


# Interface to the prep1() and prep2() functions; these are also used
# by the player (which uses a different version of decrement()).
# This adds instance variables 'counter' and 'deps' to each node,
# with meanings that can be deduced from the code below. :-) :-) :-)
#
def prepare(root):
	prep1(root)
	prep2(root, root)
	if root.counter[HD] <> 0:
		raise CheckError, 'head of root has dependencies!?!'


# Interface to clean up the mess left behind by prepare().
#
# Calling this can never really hurt,
# ***however***, if you repeatedly call calctimes(),
# it is faster not to call cleanup() in between!
#
# It does *not* remove t0 and t1, by the way...
#
def cleanup(node):
	node.counter = node.deps = None
	del node.counter
	del node.deps
	type = node.GetType()
	if type in interiortypes:
		for c in node.GetChildren():
			cleanup(c)


# Return a node's nominal duration, in seconds, as a floating point value.
# Should only be applied to leaf nodes.
#
def getduration(node):
	if node.GetType() in interiortypes:
		raise CheckError, 'Timing.getduration() on non-leaf'
	try:
		cname = MMAttrdefs.getattr(node, 'channel')
		cattrs = node.context.channeldict[cname]
		ctype = cattrs['type']
		cclass = channelmap[ctype]
	except:
		# Fallback if the channel doesn't exists, etc.
		return MMAttrdefs.getattr(node, 'duration')
	# Get here only if the 'try' succeeded
	instance = cclass()		# XXX Not initialized!
					# Walking on thin ice here...
	return instance.getduration(node)


###########################################################
# The rest of the routines here are for internal use only #
###########################################################


def prep1(node):
	node.counter = [0, 0]
	node.deps = [], []
	type = node.GetType()
	if type = 'seq':
		xnode, xside = node, HD
		for c in node.GetChildren():
			prep1(c)
			adddep(xnode, xside, 0, c, HD)
			xnode, xside = c, TL
		adddep(xnode, xside, 0, node, TL)
	elif type = 'par':
		for c in node.GetChildren():
			prep1(c)
			adddep(node, HD, 0, c, HD)
			adddep(c, TL, 0, node, TL)
	else:
		# Special case -- delay -1 means execute leaf node
		# of leaf node when playing
		adddep(node, HD, -1, node, TL)


def prep2(node, root):
	if not node.GetSummary('synctolist'): return
	arcs = MMAttrdefs.getattr(node, 'synctolist')
	for arc in arcs:
		xuid, xside, delay, yside = arc
		xnode = node.MapUID(xuid)
		if root.IsAncestorOf(xnode):
			adddep(xnode, xside, delay, node, yside)
	#
	if node.GetType() in interiortypes:
		for c in node.GetChildren(): prep2(c, root)


def adddep(xnode, xside, delay, ynode, yside):
	ynode.counter[yside] = ynode.counter[yside] + 1
	if delay >= 0:
		xnode.deps[xside].append(delay, ynode, yside)


def decrement(q, (delay, node, side)):
	if delay > 0:
		id = q.enter(delay, 0, decrement, (q, (0, node, side)))
		return
	x = node.counter[side] - 1
	node.counter[side] = x
	if x > 0:
		return
	if x < 0:
		raise CheckError, 'counter below zero!?!?'
	if side = HD:
		node.t0 = q.timefunc()
	elif side = TL:
		node.t1 = q.timefunc()
	if node.GetType() not in interiortypes:
		if side = HD:
			dt = getduration(node)
			id = q.enter(dt, 0, decrement, (q, (0, node, TL)))
	for arg in node.deps[side]:
		decrement(q, arg)


class pseudotime():
	def init(self, t):
		self.t = t
		return self
	def timefunc(self):
		return self.t
	def delayfunc(self, delay):
		self.t = self.t + delay
