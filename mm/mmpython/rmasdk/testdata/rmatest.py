

# An example of a RM listener class.
# An instance can be set to receive RM status notifications
# RMListener classes may have some or all of the methods
class PrintRMListener:
	def __init__(self):
		pass
	def __del__(self):
		print 'PrinterAdviceSink dying'
	def OnPresentationOpened(self):
		print 'OnPresentationOpened'
	def OnPresentationClosed(self):
		print 'OnPresentationClosed'
	def OnStop(self):
		print 'OnStop'
	def OnPause(self,timenow):
		print 'OnPause',timenow
	def OnBegin(self,timenow):
		print 'OnBegin',timenow
	def OnPosLength(self,pos,len):
		#print 'pos:',pos,'/',len
		pass
	def OnPreSeek(self,oldtime,newtime):
		pass
	def OnPostSeek(self,oldtime,newtime):
		pass
	def OnBuffering(self,flags,percentcomplete):
		pass
	def OnContacting(self,hostname):
		print hostname

url="file://D|/ufs/mm/cmif/mmpython/rmasdk/testdata/thanks3.ra"

import rma
player=rma.CreatePlayer()
player.SetStatusListener(PrintRMListener())
player.OpenURL(url)
player.Begin()

# for console apps, enter message loop
#import sys
#if sys.platform=='win32':
#	import win32ui
#	win32ui.GetApp().RunLoop(win32ui.GetWin32Sdk().GetDesktopWindow())

