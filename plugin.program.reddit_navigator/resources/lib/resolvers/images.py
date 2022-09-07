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

import re
from tulip import client


class Generic(object):

    name = 'generic'
    domain = 'example.com'
    tag = 'meta'
    attrs = {'property': 'og:image'}
    ret = 'content'

    def __init__(self, url):

        self.url = url
        self.ext_boolean = any([e in url for e in ['.png', '.jpg', '.jpeg', '.gif', '.gifv']])

    @property
    def web_url(self):

        return self.url

    @property
    def resolve(self):

        try:

            mime = str(client.request(self.web_url, output='headers'))
            mime = [l for l in mime.splitlines() if 'Content-Type' in l][0]
            mime = re.sub(r'.+?(\w*/\w*).+', r'\1', mime)

            if mime is None:

                raise Exception

            if mime == 'text/html':

                res = client.request(self.web_url)

                if not res:
                    raise Exception

                image = client.parseDOM(res, self.tag, attrs=self.attrs, ret=self.ret)

                if 'instagram.com' in self.web_url and 'og:video' in res:

                    image = client.parseDOM(res, Instagram.tag, attrs=Instagram.attrs, ret=Instagram.ret)

                return image[0]

            elif self.ext_boolean:

                return self.web_url

            else:

                raise Exception

        except Exception:

            return self.url


class Imgur(Generic, object):

    name = 'imgur'
    domain = 'imgur.com'
    tag = 'link'
    attrs = {'rel': 'image_src'}
    ret = 'href'


class Pixhost(Generic, object):

    name = 'pixhost'
    domain = 'pixhost.to'
    tag = 'img'
    attrs = {'id': 'image', 'data-zoom': 'out', 'class': 'image-img'}
    ret = 'src'


class Gfycat(Generic, object):

    name = 'gfycat'
    domain = 'gfycat.com'
    tag = 'source'
    attrs = {'type': 'video/mp4'}
    ret = 'src'


class Tinypic(Generic, object):

    name = 'tinypic'
    domain = 'tinypic.com'
    tag = 'source'
    attrs = {'title': 'Click for a larger view', 'id': 'imgElement'}
    ret = 'src'


class Instagram(Generic, object):

    # video resolver only, generic handles images

    name = 'instagram'
    domain = 'instagram.com'
    tag = 'meta'
    attrs = {'property': 'og:video'}
    ret = 'content'


def router(link):

    resolvers = [Gfycat, Pixhost, Imgur, Tinypic]

    boolean = False
    resolver = None

    for r in resolvers:
        boolean = r.domain in link
        if boolean:
            resolver = r
            break

    if boolean:

        image = resolver(link).resolve

        return image

    elif link:

        image = Generic(link).resolve

        if image == link:
            return link
        else:
            return image

    else:

        return link
