# Help window

# Interface:
# (1) optionally call sethelpdir(dirname) with a directory name argument;
# (2) if the user presses a Help button, call showhelpwindow();
# (3) or call givehelp(topic) to show help on a particular subject.
# When the help window is already open, it is popped up.


import fl
import os
import string
import flp
from Dialog import BasicDialog
import sys
sys.path.append('/ufs/guido/src/www') # XXX
import helplib


helpdir = None # Directory where the help files live

def sethelpdir(dirname):
	global helpdir
	helpdir = dirname


helpwindow = None # Help window instance, once opened

def givehelp(topic):
	global helpwindow, helpdir
	if helpwindow == None:
		if helpdir == None:
			import cmif
			helpdir = cmif.findfile('help')
		helpwindow = 'CMIF_help'
		print 'Initializing help server... be patient...'
	helplib.init(helpwindow)
	helplib.show('file:' + helpdir + '/' + topic + '.html')

def showhelpwindow():
	givehelp('Help')
