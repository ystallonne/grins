"""Test windowinterface fixed dialogs, editor specifics"""

__version__ = "$Id$"

import sys
import os

if os.name == 'posix':
	sys.path.append("../lib")
	import X_window
	window = X_window
elif os.name == 'mac':
	sys.path.append("::lib")
	import mac_window
	window = mac_window
# etc...

done="done"
def cb_ok(filename):
	print "Your answer:",filename
	raise done

def cb_cancel():
	print "You selected cancel"
	raise done
	
print "First we will ask you to select a Python source in the current dir"
fd = window.FileDialog("Select Python source", ".", "*.py", "",
		cb_ok, cb_cancel, existing=1)
try:
	window.mainloop()
except done:
	fd.close()
	del fd

print "Next we will ask you to give a name for a new .py file"
fd = window.FileDialog("Select Python output file", ".", "*.py", "",
		cb_ok, cb_cancel, existing=0)
try:
	window.mainloop()
except done:
	fd.close()
	del fd

print "Now we will ask you to select a beer"
sd = window.SelectionDialog("List of beers", "Favourite",
			    ["Heineken", "Amstel", "Brand", "Alfa", "Leeuw",
			     "Henninger", "Bavaria", "Bass", "Miller",
			     "Budwiser", "Budvar"], "none, really")
sd.OkCallback = cb_ok
sd.CancelCallback = cb_cancel
try:
	window.mainloop()
except done:
	sd.close()
	del sd

print "Now you should say something to me"
id = window.InputDialog("Say something", "I have nothing to say", cb_ok)
try:
	window.mainloop()
except done:
	id.close()
	del id
