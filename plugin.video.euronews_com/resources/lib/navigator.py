# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import time
from datetime import datetime, timedelta
from collections import OrderedDict
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode  # Python 2.X
	from urllib2 import urlopen  # Python 2.X
else: 
	from urllib.parse import urlencode  # Python 3.X
	from urllib.request import urlopen  # Python 3.X

from .common import *


if not xbmcvfs.exists(os.path.join(dataPath, 'settings.xml')):
	addon.openSettings()


def mainMenu():
	debug_MS("(navigator.mainMenu) -------------------------------------------------- START = mainMenu --------------------------------------------------")
	debug_MS("(navigator.mainMenu) ### BASE_URL = {0} ###".format(BASE_URL))
	un_WANTED = ['Video', 'Living It', 'Partner']
	ISOLATED = set()
	content = getUrl(BASE_URL)
	results = re.findall('<div class="js-programs-menu c-programs-menu c-header-sub-menu(.+?)<div class="c-programs-menu__footer">', content, re.S)
	for chtml in results:
		debug_MS("(navigator.mainMenu) xxxxx RESULT : {0} xxxxx".format(str(chtml)))
		part = chtml.split('<div class="list-item')
		for i in range(1,len(part),1):
			entry = part[i]
			if '<li class="list-item' in entry:
				name = re.compile(r'class=["\']title.*?>([^<]+?)(?:</a>|</span>)', re.DOTALL).findall(entry)[0]
				main_THEME = cleaning(name)
				match_URL = re.search(r'<a href=["\'](.+?)["\'] class=["\']title["\']', entry)
				if match_URL:
					main_URL = match_URL.group(1)
					show_plus = "OKAY"
				else:
					main_URL = main_THEME
					show_plus = "NOTHING"
				if not any(x in main_THEME for x in un_WANTED):
					new_NAME = main_THEME.lower()
					if new_NAME in ISOLATED:
						continue
					ISOLATED.add(new_NAME)
					addDir(main_THEME, icon, {'mode': 'SubTopics', 'url': main_URL, 'extras': show_plus})
					debug_MS("(navigator.mainMenu) ##### TITLE : {0} || URL : {1} || EXTRA : {2} #####".format(main_THEME, str(main_URL), show_plus))
	addDir(translation(30608), artpic+'livestream.png', {'mode': 'playLIVE', 'url': BASE_URL+'/api/watchlive.json'}, folder=False)
	if enableADJUSTMENT:
		addDir(translation(30609), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SubTopics(first_URL, plus_CONTENT):
	debug_MS("(navigator.SubTopics) -------------------------------------------------- START = SubTopics --------------------------------------------------")
	debug_MS("(navigator.SubTopics) ### startURL = {0} ### XTRA = {1} ###".format(str(first_URL), str(plus_CONTENT)))
	ISOLATED = set()
	content = getUrl(BASE_URL)
	if plus_CONTENT == "OKAY":
		addDir('NEWS', icon, {'mode': 'listVideos', 'url': first_URL})
	results = re.findall('<div class="js-programs-menu c-programs-menu c-header-sub-menu(.+?)<div class="c-programs-menu__footer">', content, re.S)
	for chtml in results:
		part = chtml.split('<div class="list-item')
		for i in range(1,len(part),1):
			entry = part[i]
			if '<li class="list-item' in entry:
				debug_MS("(navigator.SubTopics) ### ENTRY : {0} ###".format(str(entry)))
				main_URL = '00'
				match_URL = re.search(r'<a href=["\'](.+?)["\'] class=["\']title["\']', entry)
				if match_URL:
					main_URL = match_URL.group(1)
				name = re.compile(r'class=["\']title.*?>([^<]+?)(?:</a>|</span>)', re.DOTALL).findall(entry)[0]
				sub_THEME = cleaning(name)
				debug_MS("(navigator.SubTopics) no.01 ##### sub_THEME : {0} || first_URL : {1} || main_URL : {2} #####".format(sub_THEME, str(first_URL), str(main_URL)))
				if first_URL == main_URL or first_URL == sub_THEME:
					match = re.compile('<li class="list-item"><a href="([^"]+?)".*?list-item__link.*?>(.+?)</a></li>', re.DOTALL).findall(entry)
					for link, title in match:
						if link in ISOLATED:
							continue
						ISOLATED.add(link)
						title = cleaning(title).replace('"', '').replace('>', '').strip()
						addDir(title, icon, {'mode': 'listVideos', 'url': link, 'extras': title})
						debug_MS("(navigator.SubTopics) no.02 ##### SHOW : {0} || LINK : {1} #####".format(str(cleaning(name)), link))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listVideos(url, category):
	debug_MS("(navigator.listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	debug_MS("(navigator.listVideos) ### startURL = {0} ### CATEGORY = {1} ###".format(url, str(category)))
	api_FOUND = False
	vid_FOUND = False
	finalURL = False
	ISOLATED = set()
	new_URL = url if url.startswith('http') else 'https:'+url if url.startswith('//') else BASE_URL+url
	content = getUrl(new_URL) # https://de.euronews.com/api/program/state-of-the-union?before=1519998565&extra=1&offset=13
	match = re.findall('data-api-url="([^"]+)"', content, re.S)
	if match:
		API_URL = match[0]
		api_FOUND = True
	else:
		if url.count('/') == 1:
			API_URL = BASE_URL+'/api/program'+url
			api_FOUND = True
	if api_FOUND:
		url2 = 'https:'+API_URL+'?extra=1&offset=0&limit=50' if API_URL.startswith('//') else API_URL+'?extra=1'
		debug_MS("(navigator.listVideos) ### URL-2 : {0} ###".format(url2))
		result = getUrl(url2)
		JS = json.loads(result, object_pairs_hook=OrderedDict)
		DATA = JS['articles'] if 'articles' in JS else JS
		for article in DATA:
			debug_MS("(navigator.listVideos) xxxxx ARTICLE : {0} xxxxx".format(str(article)))
			thumb, Note_1, Note_2 = ("" for _ in range(3))
			duration = '0'
			aired, youtubeID = (None for _ in range(2))
			name = cleaning(article['title'])
			if article.get('images', None) and 'url' in str(article.get('images', None)):
				thumb = article['images'][0]['url'].replace('{{w}}x{{h}}', '861x485')
			if str(article.get('publishedAt', '')).isdigit():
				aired = datetime.fromtimestamp(article['publishedAt']).strftime('%d{0}%m{0}%Y').format('.')
				Note_1 = datetime.fromtimestamp(article['publishedAt']).strftime('%d{0}%m{0}%Y {1} %H{2}%M').format('-', '•', ':')
			if Note_1 != "": Note_1 = "[COLOR chartreuse]"+str(Note_1)+"[/COLOR][CR][CR]"
			Note_2 = (cleaning(article.get('leadin', '')) or "")
			plot = Note_1+Note_2
			debug_MS("(navigator.listVideos) no.01 ##### TITLE : {0} || THUMB : {1} #####".format(str(name), thumb))
			if 'videos' in article and len(article['videos']) > 0:
				if 'youtubeId' in str(article['videos']):
					youtubeID = [vid.get('youtubeId', []) for vid in article.get('videos', {})][-1]
				if 'duration' in str(article['videos']):
					duration = [int(vid.get('duration', []))/1000 for vid in article.get('videos', {})][-1]
				if 'url' in str(article['videos']):
					finalURL = [vid.get('url', []) for vid in article.get('videos', {})][-1]
					vid_FOUND = True
			if not finalURL or finalURL in ISOLATED:
				continue
			ISOLATED.add(finalURL)
			addLink(name, thumb, {'mode': 'playVideo', 'url': finalURL, 'extras': str(youtubeID)}, plot, duration, aired)
			debug_MS("(navigator.listVideos) no.02 ##### YoutubeID : {0} || VIDEO : {1} || DURATION : {2} #####".format(str(youtubeID), finalURL, str(duration)))
	if not vid_FOUND:
		return dialog.notification(translation(30522).format('Videos'), translation(30524).format(category), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playLIVE(url):
	debug_MS("(navigator.playLIVE) ------------------------------------------------ START = playLIVE -----------------------------------------------")
	live_url = False
	youtubeID = False
	try:
		content1 = getUrl(url)
		DATA_1 = json.loads(content1)
		firstURL = DATA_1['url']
		youtubeID = DATA_1['videoId']
		if firstURL is not None:
			forward_url = 'https://'+firstURL.split('//')[1]
			debug_MS("(navigator.playLIVE) no.01 ### URL-1 : {0} ###".format(forward_url))
			content2 = getUrl(forward_url)
			DATA_2 = json.loads(content2)
			secondURL = DATA_2['primary']
			if secondURL is not None:
				live_url = 'https://'+secondURL.split('//')[1]
				debug_MS("(navigator.playLIVE) no.02 ### URL-2 : {0} ###".format(live_url))
	except: pass
	if not live_url:
		if youtubeID:
			testing = youtubeID
		elif not youtubeID and channelLIVE != '00':
			testing = channelLIVE
		log("(navigator.playLIVE) ##### TRY -  TO - PLAY - VIA - YOUTUBE = YES #####")
		try:
			code = urlopen('https://www.youtube.com/oembed?format=json&url=http://www.youtube.com/watch?v='+testing).getcode()
			if str(code) == '200': live_url = 'plugin://plugin.video.youtube/play/?video_id='+testing
		except: pass
	if live_url:
		debug_MS("(navigator.playLIVE) ### LIVEurl : {0} ###".format(live_url))
		listitem = xbmcgui.ListItem(label=translation(30610))
		listitem.setPath(live_url)
		listitem.setMimeType('application/vnd.apple.mpegurl')
		xbmc.Player().play(item=live_url, listitem=listitem)
	else:
		failing("(navigator.playLIVE) ##### Abspielen des Live-Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Live-Stream-Eintrag auf der Webseite von *euronews.com* gefunden !!! ##########".format(url))
		return dialog.notification(translation(30521).format('LIVE'), translation(30525), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playVideo(url, YTID):
	debug_MS("(navigator.playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	log("(navigator.playVideo) ### YoutubeID = {0} ### Standard-VIDEO = {1} ###".format(str(YTID), url))
	stream = url
	if PlayToYT and YTID != 'None':
		log("(navigator.playVideo) ##### TRY -  TO - PLAY - VIA - YOUTUBE = YES #####")
		try:
			code = urlopen('https://www.youtube.com/oembed?format=json&url=http://www.youtube.com/watch?v='+YTID).getcode()
			if str(code) == '200': stream = 'plugin://plugin.video.youtube/play/?video_id='+YTID
		except: pass
	listitem = xbmcgui.ListItem(path=stream)
	xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem)

def addDir(name, image, params={}, plot=None, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot=None, duration=None, aired=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	info = {}
	info['Tvshowtitle'] = None
	info['Title'] = name
	info['Tagline'] = None
	if aired is not None:
		info['Date'] = aired
	info['Plot'] = plot
	info['Duration'] = duration
	info['Year'] = None
	info['Genre'] = 'News'
	info['Studio'] = 'euronews'
	info['Mediatype'] = 'movie'
	liz.setInfo(type='Video', infoLabels=info)
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)
