__version__ = "$Id$"

# Event handling.

# Window system events
KeyboardInput = 1
Mouse0Press = 2
Mouse0Release = 3
Mouse1Press = 4
Mouse1Release = 5
Mouse2Press = 6
Mouse2Release = 7
ResizeWindow = 8
WindowExit = 9
WindowActivate = 11 # Mac-only
WindowDeactivate = 12 # Mac-only


# File descriptor ready events
FileEvent = 10

# Timer events
TimerEvent = 20

# Drag and drop, copy and paste file events
DropFile  = 30
PasteFile = 31
DropURL = 32
DragFile = 33
DragURL = 34

# Underlying OS window/bitmap has changed (onscreen<->offscreen bitmap, etc)
OSWindowChanged = 40
