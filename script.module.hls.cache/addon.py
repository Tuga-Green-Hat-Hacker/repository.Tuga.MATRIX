#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys,xbmcgui,xbmcaddon,xbmcvfs,shutil

def fix_encoding(path):
	if sys.version_info.major == 2:

		if sys.platform.startswith('win'):return path
		else:return path # .encode('ISO-8859-1')

	elif sys.version_info.major == 3:return path

__addon__ =  xbmcaddon.Addon(id='script.module.hls.cache')
__addon_path__ = fix_encoding(__addon__.getAddonInfo('path'))
__kodi_log_file__ = fix_encoding(xbmcvfs.translatePath('special://logpath/kodi.log'))
__kodi_error_log_file_ = os.path.abspath(os.path.join(__addon_path__,'kodi.log'))


ip = xbmc.getIPAddress()
__addon__.setSetting('ip',ip)
port = __addon__.getSetting('port')

if __addon__.getSetting('import_kodi_log') == 'true':
	try:
		shutil.copyfile(__kodi_log_file__,__kodi_error_log_file_)
		xbmcgui.Dialog().notification(heading='[COLOR blue]Kodi log created ![/COLOR]',message='http://'+ ip +':'+ port +'/kodi.log',icon=xbmcgui.NOTIFICATION_INFO,time=10000,sound=False)
	except:pass
else:
	if os.path.exists(__kodi_error_log_file_):
		try:os.unlink(__kodi_error_log_file_)
		except:pass

__addon__.openSettings()