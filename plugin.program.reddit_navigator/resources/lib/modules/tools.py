# -*- coding: utf-8 -*-

'''
    License summary below, for more details please read license.txt file

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import socket, json, re, pyxbmct, time
from tulip import control, client
from tulip.init import sysaddon
from tulip.compat import quote, range, iteritems
from tulip.log import log_debug

history_media = control.join(control.dataPath, 'history_media')
history_subrs = control.join(control.dataPath, 'history_subreddits')
saved_subrs = control.join(control.dataPath, 'subreddits.db')


def trim_history(file_):

    """
    Trims history to what is set in settings
    :return:
    """

    history_size = int(control.setting('history.size'))

    f = open(file_, 'r')
    text = [i.rstrip('\n') for i in f.readlines()]
    f.close()

    if len(text) > history_size:
        f = open(file_, 'w')
        dif = history_size - len(text)
        result = text[:dif]
        f.write('\n'.join(result) + '\n')
        f.close()


def add_to_history(txt, file_):

    if not txt:
        return

    try:
        with open(file_) as f:
            if txt in f.read():
                return
            else: pass
    except IOError:
        pass

    with open(file_, 'a') as f:
        f.writelines(txt + '\n')

    trim_history(file_)


def read_from_history(file_):

    """
    Reads from history file which is stored in plain text, line by line
    :return: List
    """

    if control.exists(file_):

        with open(file_, 'r') as f:
            text = [i.rstrip('\n') for i in f.readlines()][::-1]

        return text

    else:

        return


def deletion(history=True):

    if history:
        control.deleteFile(history_media)
        control.deleteFile(history_subrs)
    else:
        control.deleteFile(control.bookmarksFile)
        control.deleteFile(saved_subrs)

    control.infoDialog(control.lang(30402))


class TextDisplay(pyxbmct.AddonDialogWindow):

    pyxbmct.skin.estuary = control.setting('pyxbmct.estuary') == 'true'

    def __init__(self, title, text):

        super(TextDisplay, self).__init__(title)

        self.xval, self.yval = get_skin_resolution()

        self.setGeometry(int(float(self.xval) / 1.5), int(float(self.yval) / 1.5), 1, 1)
        self.text = text
        self.text_box = None
        self.set_controls()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self):

        self.text_box = pyxbmct.TextBox()
        self.placeControl(self.text_box, 0, 0)
        self.text_box.setText(self.text)
        self.text_box.autoScroll(5000, 1000, 1000)


def text_box(text):

    if control.setting('text.box') == 'true':

        window = TextDisplay(control.name(), text=text)
        window.doModal()
        del window

    else:

        control.dialog.textviewer(control.name(), text=text)


def readme():

    with open(control.join(control.addonPath, 'README.md')) as f:
        text = f.read()

    text_box(text)


def welcome_message():

    text = u''.join([control.lang(s) for s in list(range(30131, 30143))])

    text_box(text)


def window_activate(url=None, query=None, jump=False, action='listing'):

    control.execute('Dialog.Close(all)')

    if not jump:

        if query == 'video':
            window = 'videos'
        elif query == 'audio':
            window = 'music'
        elif query == 'image':
            window = 'pictures'
        else:
            window = 'programs'

        executable = 'ActivateWindow({0},"{1}?content_type={2}&action=root",return)'.format(window, sysaddon[:-1], query)

        control.execute(executable)

    elif url == 'home':

        control.execute('Container.Update({0}?action=root)'.format(sysaddon[:-1]))

    else:

        if query:
            param = 'query'
        else:
            param = 'url'

        try:
            obj = quote(query if param == 'query' else url)
        except KeyError:
            obj = quote(query if param == 'query' else url.encode('latin1'))

        executable = 'Container.Update({0}?action={1}&{2}={3},return)'.format(sysaddon[:-1], action, param, obj)

        control.execute(executable)


def active_mode():

    def visible_window(window_id):

        boolean = control.condVisibility('Window.IsVisible({0})'.format(window_id))

        return boolean

    if visible_window('videos'):
        mode = control.lang(30030)
        window = 'videos'
    elif visible_window('music'):
        mode = control.lang(30031)
        window = 'music'
    elif visible_window('pictures'):
        mode = control.lang(30032)
        window = 'pictures'
    else:
        mode = control.lang(30036)
        window = 'programs'

    return mode, window


def addon_version(addon_id):

    version = int(control.infoLabel('System.AddonVersion({0})'.format(addon_id)).replace('.', ''))

    return version


def install_plexus():

    if addon_version('xbmc.python') >= 2250:
        control.execute('InstallAddon(program.plexus)')
    else:
        control.execute('RunPlugin(plugin://program.plexus/)')


def available_domains(add_operator=True):

    reduced_list = [
        'dailymotion.com', 'docs.google.com', 'drive.google.com', 'estream.nu', 'thevideobee.to', 'streamable.com'
        'vk.com', 'flashx.tv', 'vidoza.net', 'clipwatching.com', 'vidzi.tv', 'tune.pk', 'vshare.io', 'vshare.eu'
    ]

    if add_operator:
        return '(' + ' OR '.join(reduced_list) + ')'
    else:
        return reduced_list

    # Reserved:
    # import resolveurl

    # rr = resolveurl.relevant_resolvers()
    # domains = [r.domains for r in rr][1:]
    # domain_list = [d for dm in domains for d in dm]

    # if add_operator:
    #     return '(' + ' OR '.join(domain_list) + ')'
    # else:
    #     return domain_list


def stream_picker(names, urls):

    choice = control.selectDialog(heading=control.lang(30061), list=names)

    if choice <= len(names) and not choice == -1:
        popped = urls[choice]
        return popped
    else:
        return control.execute('Dialog.Close(all)')


def convert_date(stamp):

    DATEFORMAT = control.getregion('dateshort')
    TIMEFORMAT = control.getregion('meridiem')

    date_time = time.localtime(stamp)

    if DATEFORMAT[1] == 'd':
        localdate = time.strftime('%d-%m-%Y', date_time)
    elif DATEFORMAT[1] == 'm':
        localdate = time.strftime('%m-%d-%Y', date_time)
    else:
        localdate = time.strftime('%Y-%m-%d', date_time)
    if TIMEFORMAT != '/':
        localtime = time.strftime('%I:%M%p', date_time)
    else:
        localtime = time.strftime('%H:%M', date_time)

    return localtime + ' ' + localdate


def legacy_replace(txt):

    try:

        txt = txt.replace('&lt;', '<')
        txt = txt.replace('&gt;', '>')
        txt = txt.replace('&amp;', '&')

    except AttributeError:

        pass

    return txt


def cm_updater(the_list, url=''):

    for i in the_list:

        bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')

        try:
            bookmark['bookmark'] = i['url']
        except KeyError:
            bookmark['bookmark'] = i['permalink']

        bm_object = json.dumps(bookmark)
        add_bm_cm = {'title': 30023, 'query': {'action': 'addBookmark', 'url': bm_object}}
        go_to_home_cm = {'title': 30104, 'query': {'action': 'window_activate', 'url': 'home'}}
        refresh_cm = {'title': 30107, 'query': {'action': 'refresh'}}

        try:

            go_to_sr_cm = {
                'title': control.lang(30044) + ' ' + i['subreddit'], 'query': {
                    'action': 'window_activate', 'url': i['subreddit_url']
                }
            }

        except KeyError:

            go_to_sr_cm = None

        try:
            if not access_boolean():
                raise KeyError
            if url is not None and '/saved/' in url:
                thing_cm = {'title': 30106, 'query': {'action': 'unsave_thing', 'url': i['name']}}
            else:
                thing_cm = {'title': 30105, 'query': {'action': 'save_thing', 'url': i['name']}}
        except KeyError:
            thing_cm = None

        if i['kind'] == 't3':

            list_thread_cm = {'title': 30100, 'query': {'action': 'window_activate', 'url': i['permalink']}}

            comment_scraper_cm = {
                'title': 30118, 'query': {'action': 'comment_scraper', 'title': i['title'], 'plot': i['selftext']}
            }

            try:
                del bookmark['isFolder']
            except KeyError:
                pass

            bookmark['url'] = i['subreddit_url']
            bookmark['bookmark'] = i['subreddit_url']
            bookmark['action'] = 'listing'
            bm_object = json.dumps(bookmark)

            add_sr_cm = {
                'title': control.lang(30038) + ' ' + i['subreddit'], 'query': {
                    'action': 'addSubreddit', 'url': bm_object
                }
            }

            if access_boolean():

                sub_sr_cm = {
                    'title': control.lang(30055), 'query': {
                        'action': 'subscribeSubreddit', 'query': i['subreddit']
                    }
                }

                i.update(
                    {
                        'cm': [
                            add_bm_cm, go_to_sr_cm, sub_sr_cm, add_sr_cm, list_thread_cm, thing_cm, comment_scraper_cm,
                            go_to_home_cm, refresh_cm
                        ]
                    }
                )

            else:

                i.update(
                    {
                        'cm': [
                            add_bm_cm, go_to_sr_cm, add_sr_cm, list_thread_cm, comment_scraper_cm, go_to_home_cm,
                            refresh_cm
                        ]
                    }
                )

        elif i['kind'] == 't5':

            add_sr_cm = {
                'title': control.lang(30038) + ' ' + i['display_name'], 'query': {
                    'action': 'addSubreddit', 'url': bm_object
                }
            }

            sub_plot_cm = {
                'title': control.lang(30113),
                'query': {'action': 'text_viewer', 'plot': i['plot'], 'title': i['display_name']}
            }

            if access_boolean():
                sub_sr_cm = {
                    'title': control.lang(30055), 'query': {
                        'action': 'subscribeSubreddit', 'query': i['display_name']
                    }
                }

                i.update({'cm': [add_bm_cm, add_sr_cm, sub_sr_cm, go_to_home_cm, sub_plot_cm, refresh_cm]})

            else:

                i.update({'cm': [add_bm_cm, add_sr_cm, go_to_home_cm, sub_plot_cm, refresh_cm]})

        elif i['kind'] == 't1':

            comment_scraper_cm = {
                'title': 30118, 'query': {'action': 'comment_scraper', 'title': i['title'], 'plot': i['plot']}
            }

            if i['replies_urls']:
                list_thread_cm = {'title': 30100, 'query': {'action': 'replies_viewer', 'query': i['replies_urls']}}
            else:
                list_thread_cm = {'title': 30100, 'query': {'action': 'window_activate', 'url': i['permalink']}}

            i.update(
                {
                    'cm': [
                        add_bm_cm, list_thread_cm, comment_scraper_cm, go_to_sr_cm, thing_cm, go_to_home_cm, refresh_cm
                    ]
                }
            )

        elif i['kind'] == 'LabeledMulti':

            ms_cm = {'title': 30101, 'query': {'action': 'multisel', 'url': i['subreddits']}}

            i.update({'cm': [add_bm_cm, ms_cm, go_to_home_cm, refresh_cm]})

        elif i['kind'] == 'more':

            list_thread_cm = {'title': 30100, 'query': {'action': 'window_activate', 'url': i['permalink']}}

            i.update({'cm': [add_bm_cm, list_thread_cm, go_to_home_cm, refresh_cm]})

        else:

            i.update({'cm': [add_bm_cm, go_to_home_cm, refresh_cm]})

    # if active_mode()[1] == 'pictures':
    #
    #     for i in the_list:
    #
    #         if i['action'] == 'show_picture' and ('gfycat.com' in i['url'] or 'instagram.com' in i['url']):
    #
    #             show_pic_cm = [{'title': 30143, 'query': {'action': 'show_picture', 'url': i['url']}}]
    #             i['cm'] += show_pic_cm

    return the_list


def action_updater(the_list):

    for i in the_list:

        if i['kind'] == 't3':

            if images_boolean(i['url']):
                i.update({'action': 'show_picture', 'isFolder': 'False', 'isPlayable': 'False'})
                if 'gfycat.com' in i['url'] or 'instagram.com' in i['url'] and control.setting('single.button') == 'false':
                    i.update({'isPlayable': 'True'})
            elif i['selftext']:
                i.update({'action': 'text_viewer', 'isFolder': 'False', 'isPlayable': 'False'})
            else:
                i.update({'action': 'play', 'isFolder': 'False'})
                if control.setting('single.button') == 'true':
                    i.update({'isPlayable': 'False'})

        elif i['kind'] == 't1':

            i.update({'action': 'text_viewer', 'isFolder': 'False', 'isPlayable': 'False'})

        elif i['kind'] == 'more':

            i.update({'action': 'listing', 'query': i['replies_urls']})

        else:

            i.update({'action': 'listing'})

    for i in the_list:

        i.update({'nextlabel': 30043, 'nextaction': 'listing'})

    return the_list


def images_boolean(url):

    hosts = ['gfycat.com', 'imgur.com', 'tinypic.com', 'media.tumblr.com', 'instagram.com']

    extensions = ['.png', '.jpg', '.jpeg', '.gif', '.gifv']

    return any([e in url for e in extensions]) or any([h in url for h in hosts])


def access_boolean():

    return True if control.setting('access.token') else False


def get_skin_resolution():

    aspect_ratio = control.infoLabel('Skin.AspectRatio')

    xml = control.join(control.transPath('special://skin/'), 'addon.xml')
    with open(xml) as f:
        xml_file = f.read()
    res_extension_point = client.parseDOM(xml_file, 'extension', attrs={'point': 'xbmc.gui.skin'})[0]

    res_lines = res_extension_point.splitlines()

    try:
        skin_resolution = [res for res in res_lines if aspect_ratio in res][0]
    except IndexError:
        skin_resolution = res_lines[0]

    xval = int(re.findall(r'width="(\d{3,4})"', skin_resolution)[0])
    yval = int(re.findall(r'height="(\d{3,4})"', skin_resolution)[0])

    return xval, yval


def close_all():

    return control.execute('Dialog.Close(all)')


def debugging_toggle():

    if not control.get_a_setting('debug.showloginfo')['result']['value']:

        control.execute('ToggleDebug')

        if control.setting('debugging.toggle') == 'false':

            yes = control.yesnoDialog(control.lang(30016))

            if yes:

                control.setSetting('debugging.toggle', 'true')
                log_debug('Debugging activated')

    else:

        control.setSetting('debugging.toggle', 'false')
        control.execute('ToggleDebug')


def refresh():

    from tulip import cache
    cache.FunctionCache().reset_cache()
    control.refresh()


def refresh_access():

    if control.setting('refresh.token') and control.setting('auto.refresh') == 'true':

        if float(control.setting('expiration.stamp')) < time.time():

            from .reddit import get_tokens
            get_tokens(refresh=True)


def first_time_prompt():

    if control.setting('first.time') == 'true':

        welcome_message()
        control.setSetting('first.time', 'false')
