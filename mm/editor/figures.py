# draw miscellaneous figures for channel view
from math import *
from GL import *
from gl import *

BG_BOX = 0
FG_BOX = 1
FOCUS_BOX = 2
LOCK_BOX = 3

# play with these for arrows
ARR_WIDTH = 5
ARR_HEAD = 18
ARR_SLANT = float(ARR_WIDTH) / float(ARR_HEAD)

def clear_window():
	color(WHITE)
	clear()

# define a rectangular box with vertex at (x,y); width w and heigth h.
class box():

	def new(self,(kind,x,y,w,h,name)):
		self.boxtype = kind
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.label = name
		self.hidden = 0
		return self

	def draw(self):
		if self.hidden <> 0 or self.boxtype = BG_BOX:
			return
		color(YELLOW)
		x = self.x
		y = self.y
		w = self.w
		h = self.h
		pushmatrix()
		translate(x, y, 0)
		bgnpolygon()
		v2f(0, 0)
		v2f(w, 0)
		v2f(w, h)
		v2f(0, h)
		endpolygon()
		l = getlwidth()
		linewidth(l * 2)
		if self.boxtype = FOCUS_BOX:
			color(RED)
		elif self.boxtype = LOCK_BOX:
			color(GREEN)
		else:
			color(WHITE)
		bgnclosedline()
		v2f(0, 0)
		v2f(w, 0)
		v2f(w, h)
		v2f(0, h)
		endclosedline()
		translate(w/2, h/2, 0)
		putlabel(self.label)
		popmatrix()
		linewidth(l)

# define a diamond with vertices on the midpoints on the sides of a
# rectangle.  the rectangle has one vertex at (x,y), width w and height h
# moreover, this pattern contains a line from the bottom of the diamond
# extending for l units.  the line is not part of the hotspot.
class diamond():

	def new(self,(x,y,w,h,l,name)):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.l = l
		self.hidden = 0
		self.label = name
		return self

	def draw(self):
		if self.hidden <> 0:
			return
		x = self.x
		y = self.y
		w = self.w
		h = self.h
		l = self.l
		color(GREEN)
		pushmatrix()
		translate(x+w/2, y, 0)
		bgnpolygon()
		v2f(0, 0)
		v2f(w/2, h/2)
		v2f(0, h)
		v2f(-w/2, h/2)
		endpolygon()
		bgnline()
		v2f(0, 0)
		v2f(0, -l)
		endline()
		translate(0, h/2, 0)
		putlabel(self.label)
		popmatrix()

	def hotspot(self, (mx, my)):
		if self.hidden <> 0:
			return 0
		if mx < self.x or mx > self.x + self.w:
			return 0
		if my < self.y or my > self.y + self.h:
			return 0
		w = self.w * 2
		h = self.h * 2
		wh = self.w * self.h
		# translate to left low corner
		nx = mx - self.x
		ny = my - self.y
		if nx * h + ny * w - wh < 0:
			return 0
		# translate to right low corner
		nx = nx - self.w
		if -nx * h + ny * w - wh < 0:
			return 0
		# translate to right upp corner
		ny = ny - self.h
		if -nx * h - ny * w - wh < 0:
			return 0
		# translate to left upp corner
		nx = nx + self.w
		if nx * h - ny * w - wh < 0:
			return 0
		return 1

# define an arrow from (fx,fy) to (tx,ty).
# the hotspot is the arrowhead
class arrow():

	def new(self, (fx, fy, tx, ty, arc)):
		self.fx = fx
		self.fy = fy
		self.lx = tx - fx
		self.ly = ty - fy
		self.arc = arc
		self.length = int(sqrt(self.lx*self.lx+self.ly*self.ly))
		self.angle = atan2(self.lx, self.ly)
		self.cos = cos(self.angle)
		self.sin = sin(self.angle)
		self.hidden = 0
		return self

	def draw(self):
		if self.hidden <> 0:
			return
		pushmatrix()
		l = getlwidth()
		linewidth(l*2)
		color(RED)
		translate(self.fx, self.fy, 0)
		rot(- self.angle * 180 / pi, 'z')
		bgnline()
		v2f(0, 0)
		v2f(0, self.length)
		endline()
		bgnpolygon()
		v2f(0, self.length)
		v2f(ARR_WIDTH, self.length - ARR_HEAD)
		v2f(-ARR_WIDTH, self.length - ARR_HEAD)
		endpolygon()
		linewidth(l)
		popmatrix()

	def hotspot(self, (mx, my)):
		if self.hidden <> 0:
			return 0
		# translate
		x, y = mx - self.fx, my - self.fy
		# rotate (sine reversal?)
		nx = x * self.cos - y * self.sin
		ny = y * self.cos + x * self.sin
		# translate over length
		ny = ny - self.length
		if ny > 0 or ny < -ARR_HEAD:
			return 0
		if nx > -ARR_SLANT * ny or nx < ARR_SLANT * ny:
			return 0
		return 1

def putlabel(label):
	h = getheight()
	w = strwidth(label)
	cmov2(-w/2, -h/2)
	color(BLACK)
	charstr(label)

