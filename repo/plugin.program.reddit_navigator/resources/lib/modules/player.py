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

import pyxbmct, re, json, youtube_resolver, resolveurl
from sys import argv
from tulip import control, directory
from tulip.init import sysaddon
from tulip.compat import parse_qsl
from .tools import close_all, window_activate, images_boolean, get_skin_resolution, TextDisplay
from ..resolvers.images import router as pic_router
from .reddit import base_link


def router(link):

    if 'youtu' in link:

        yt_mpd_enabled = control.addon(id='plugin.video.youtube').getSetting('kodion.video.quality.mpd') == 'true'

        streams = youtube_resolver.resolve(link)

        if yt_mpd_enabled:
            urls = streams
        else:
            urls = [s for s in streams if 'dash' not in s['title'].lower()]

        resolved = urls[0]['url']

        return resolved

    elif 'v.redd.it' in link or 'reddit.com/video' in link:

        if 'reddit.com/video' in link:
            link = 'https://v.redd.it/' + link.partition('/')[2]

        try:

            dash_on = control.addon_details('inputstream.adaptive').get('enabled')

        except KeyError:

            dash_on = False

        if dash_on:
            stream = link + '/DASHPlaylist.mpd'
        else:
            stream = link + '/HLSPlaylist.m3u8'

        return stream

    elif resolveurl.HostedMediaFile(link).valid_url():

        stream = resolveurl.resolve(link)

        return stream

    else:

        return link


def play(link, permalink=None, title=None, image=None, skip_question=False):

    def playback(resolved_mode=True):

        stream = router(link)

        if stream == link and not skip_question:

            yesno = control.yesnoDialog(control.lang(30125), yeslabel=control.lang(30126), nolabel=control.lang(30127))

            if not yesno:

                control.open_web_browser(stream)
                return close_all()

        dash = '.mpd' in stream or 'dash' in stream

        if title and image:
            directory.resolve(stream, dash=dash, icon=image, meta={'title': title}, resolved_mode=resolved_mode)
        else:
            directory.resolve(stream, dash=dash, resolved_mode=resolved_mode)

    ##############################################

    if control.setting('single.button') == 'true':

        choice = control.selectDialog([control.lang(30157), control.lang(30100), control.lang(30159)])

        if choice == 0:

            playback(resolved_mode=False)

        elif choice == 1:

            window_activate(url=permalink, jump=True)

        elif choice == 2:

            control.execute('Action(ContextMenu)')

    else:

        playback()


class ImageDisplay(pyxbmct.AddonDialogWindow):

    pyxbmct.skin.estuary = control.setting('pyxbmct.estuary') == 'true'

    def __init__(self, title, image):

        super(ImageDisplay, self).__init__(title)

        self.xval, self.yval = get_skin_resolution()

        self.setGeometry(int(float(self.xval) / 1.5), int(float(self.yval) / 1.5), 1, 1)
        self.image = image
        self.set_controls(self.image)
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self, image):

        image = pyxbmct.Image(image, aspectRatio=2)

        self.placeControl(image, 0, 0)


def show_picture(title, link, permalink=None):

    def image_display():

        image = pic_router(link)

        if 'mp4' in image:

            play(
                link=image, title=title, image=dict(parse_qsl(argv[2].replace('?', ''))).get('image'), skip_question=True
            )

        else:

            if control.setting('image.fullscreen') == 'true':

                control.execute('ShowPicture("{0}")'.format(image))

            else:

                window = ImageDisplay(title, image)
                window.doModal()
                del window
                close_all()

    if control.setting('single.button') == 'true':

        choice = control.selectDialog([control.lang(30157), control.lang(30100), control.lang(30159)])

        if choice == 0:

            image_display()

        elif choice == 1:

            window_activate(url=permalink, jump=True)

        elif choice == 2:

            control.execute('Action(ContextMenu)')

    else:

        image_display()


def view_text(text, title=None):

    try:

        data = json.loads(text)

    except (TypeError, ValueError):

        data = None

    if isinstance(data, dict):

        public = data['public_description']
        full = data['description']
        title = data['title']

        text = public + '\n' * 4 + full

    if not title:

        title = control.name()

    if control.setting('text.box') == 'true':

        window = TextDisplay(title, text=text)
        window.doModal()
        del window

    else:

        control.dialog.textviewer(title, text=text)


def text_viewer(text, title=None, permalink=None):

    if control.setting('single.button') == 'true':

        choice = control.selectDialog([control.lang(30158), control.lang(30100), control.lang(30159)])

        if choice == 0:

            view_text(text, title)

        elif choice == 1:

            if permalink.startswith('http'):
                window_activate(url=permalink, jump=True)
            else:
                window_activate(query=permalink, jump=True)

        elif choice == 2:

            control.execute('Action(ContextMenu)')

    else:

        view_text(text, title)


def comment_scraper(text, title):

    link = None

    links = re.findall(r'(\w*(?:://|/r/|/domain/)[^\r\n\t\f\v()\[\] ]*)', text)

    if links:

        choice = control.selectDialog(links)

        if choice == -1:
            close_all()
            return
        elif choice <= len(links):
            link = links[choice]

        if 'reddit.com/r/' in link:

            window_activate(url=link, jump=True)

        elif link.startswith('/r/') or link.startswith('/domain/'):

            link = base_link() + link
            window_activate(url=link, jump=True)

        else:

            if images_boolean(link):

                show_picture(title, link)

            else:

                control.execute(
                    'PlayMedia("{0}?action=play&url={1}&title={2}&image={3}")'.format(
                        sysaddon[:-1], link, title, control.addonInfo('icon')
                    )
                )

    else:

        control.infoDialog(control.lang(30130))
