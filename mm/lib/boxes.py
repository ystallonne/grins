import dialogs, windowinterface, EVENTS

message = 'Use left mouse button to draw a box.\n' + \
	  'Click `Done\' when ready or `Cancel\' to cancel.'

def create_box(window, msg, *box):
	if len(box) == 1 and type(box) == type(()):
		box = box[0]
	if len(box) not in (0, 4):
		raise TypeError, 'bad arguments'
	if len(box) == 0:
		box = None
	windowinterface.startmonitormode()
	display = window._active_display_list
	window.pop()
	window._close_subwins()
	try:
		oldfuncarg1 = windowinterface.getregister(window,
							 EVENTS.Mouse0Press)
	except windowinterface.error:
		oldfuncarg1 = None
	else:
		windowinterface.unregister(window, EVENTS.Mouse0Press)
	try:
		oldfuncarg2 = windowinterface.getregister(window,
							  EVENTS.Mouse0Release)
	except windowinterface.error:
		oldfuncarg2 = None
	else:
		windowinterface.unregister(window, EVENTS.Mouse0Release)
	try:
		if msg:
			msg = msg + '\n\n' + message
		else:
			msg = message
		dialog = dialogs.Dialog((msg, '!Done', 'Cancel'))
		while not box:
			win, ev, val = windowinterface.readevent()
			if win == window and ev == EVENTS.Mouse0Press:
				box = window.sizebox((val[0], val[1], 0, 0), 0, 0)
				break
			else:
				r = dialog.checkevent(win, ev, val)
				if r:
					dialog.close()
					return None
		if display and not display.is_closed():
			d = display.clone()
		else:
			d = window.newdisplaylist()
		for win in window._subwindows:
			d.drawbox(win._sizes)
		d.fgcolor(255, 0, 0)
		d.drawbox(box)
		d.render()
		while 1:
			win, ev, val = windowinterface.readevent()
			if win == window and ev == EVENTS.Mouse0Press:
				x, y = val[0:2]
				if box[0] + box[2]/4 < x < box[0] + box[2]*3/4:
					constrainx = 1
				else:
					constrainx = 0
				if box[1] + box[3]/4 < y < box[1] + box[3]*3/4:
					constrainy = 1
				else:
					constrainy = 0
				if display and not display.is_closed():
					display.render()
				d.close()
				if constrainx and constrainy:
					box = window.movebox(box, 0, 0)
				else:
					if x < box[0] + box[2] / 2:
						x0 = box[0] + box[2]
						w = - box[2]
					else:
						x0 = box[0]
						w = box[2]
					if y < box[1] + box[3] / 2:
						y0 = box[1] + box[3]
						h = -box[3]
					else:
						y0 = box[1]
						h = box[3]
					box = window.sizebox((x0, y0, w, h), \
						  constrainx, constrainy)
				if display and not display.is_closed():
					d = display.clone()
				else:
					d = window.newdisplaylist()
				for win in window._subwindows:
					d.drawbox(win._sizes)
				d.fgcolor(255, 0, 0)
				d.drawbox(box)
				d.render()
			else:
				r = dialog.checkevent(win, ev, val)
				if r:
					dialog.close()
					if display and not display.is_closed():
						display.render()
					d.close()
					if r == '!Done':
						return box
					return None
	finally:
		window._open_subwins()
		windowinterface.endmonitormode()
		if oldfuncarg1:
			windowinterface.register(window, EVENTS.Mouse0Press,
						 oldfuncarg1[0],
						 oldfuncarg1[1])
		if oldfuncarg2:
			windowinterface.register(window, EVENTS.Mouse0Release,
						 oldfuncarg2[0],
						 oldfuncarg2[1])
