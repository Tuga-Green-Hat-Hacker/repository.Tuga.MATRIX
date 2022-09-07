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

from ..modules.tools import *

from ..modules.reddit import url_generator, base_link, dotjson, request_headers, reddit_url, account_info
from tulip import directory, client, bookmarks, cache, control, init
from tulip.compat import iteritems, urlparse, urlunparse, urlencode, parse_qsl

cache_method = cache.FunctionCache().cache_method

# noinspection PyProtectedMember
class Main:

    formatting = '[CR]' if control.setting('label.formatting') == '0' else ' | '

    def __init__(self):

        self.list = []; self.menu = []; self.data = []; self.nested = []; self.directory = []

    def executable(self):

        modes = [control.lang(30033), control.lang(30034), control.lang(30035), control.lang(30028)]

        if control.setting('window.action') == '0':

            choice = control.selectDialog(modes)

            if choice == 0:

                window_activate(query='video')

            elif choice == 1:

                window_activate(query='audio')

            elif choice == 2:

                window_activate(query='image')

            elif choice == 3:

                control.openSettings()

            else:

                control.execute('Dialog.Close(all)')

        else:

            self.list = [
                {
                    'title': modes[0],
                    'action': 'window_activate',
                    'query': 'video',
                    'isFolder': 'False',
                    'isPlayable': 'False'
                }
                ,
                {
                    'title': modes[1],
                    'action': 'window_activate',
                    'query': 'audio',
                    'isFolder': 'False',
                    'isPlayable': 'False'
                }
                ,
                {
                    'title': modes[2],
                    'action': 'window_activate',
                    'query': 'image',
                    'isFolder': 'False',
                    'isPlayable': 'False'
                }
                ,
                {
                    'title': modes[3],
                    'action': 'tools',
                    'icon': 'settings_tools.png',
                    'isFolder': 'False',
                    'isPlayable': 'False'
                }
            ]

            directory.add(self.list)

    def root(self):

        self.menu = [
            {
                'title': control.lang(30029) + ' ' + active_mode()[0],
                'action': 'mode_change',
                'boolean': control.setting('show.mode') == 'true'
            }
            ,
            {
                'title': 'Reddit: ' + control.lang(30120),
                'action': 'listing',
                'url': base_link() + '/hot/',
                'icon': 'hot.png',
                'boolean': control.setting('show.hot') == 'true'
            }
            ,
            {
                'title': 'Reddit: ' + control.lang(30121),
                'action': 'listing',
                'url': base_link() + '/new/',
                'icon': 'new.png',
                'boolean': control.setting('show.new') == 'true'
            }
            ,
            {
                'title': control.lang(30001),
                'action': 'search',
                'url': 'media',
                'icon': 'search_media_files.png',
                'boolean': control.setting('show.media') == 'true'
            }
            ,
            {
                'title': control.lang(30012),
                'action': 'search',
                'url': 'subreddits',
                'icon': 'search_reddit.png',
                'boolean': control.setting('show.subreddits') == 'true'
            }
            ,
            {
                'title': control.lang(30002),
                'action': 'saved_subreddits',
                'icon': 'saved_subreddits.png',
                'boolean': control.setting('show.saved') == 'true'
            }
            ,
            {
                'title': control.lang(30027),
                'action': 'bookmarks',
                'icon': 'bookmarks.png',
                'boolean': control.setting('show.bookmarks') == 'true'
            }
            ,
            {
                'title': control.lang(30028),
                'action': 'tools',
                'icon': 'settings_tools.png',
                'boolean': control.setting('show.tools') == 'true'
            }
        ]

        my_account = {
            'title': control.lang(30090),
            'action': 'my_account',
            'icon': 'my_account.png',
            'boolean': control.setting('show.account') == 'true'
        }

        if control.setting('window.action') == '0':

            for i in self.menu:
                if i['action'] in ['mode_change', 'search', 'my_account']:
                    i.update({'isFolder': 'False', 'isPlayable': 'False'})

        if len(control.setting('access.token')) > 0:
            self.menu.insert(-2, my_account)

        self.list = [i for i in self.menu if i['boolean']]

        directory.add(self.list, content='addons')

    def my_account(self):

        choices = [control.lang(30091), control.lang(30092), control.lang(30093)]

        username = control.setting('username.string')
        icon_img = control.setting('avatar.url')

        if not username or not icon_img:

            ai = account_info()

            username, icon_img = (ai['name'], ai['icon_img'])
            control.setSetting('username.string', username)
            control.setSetting('avatar.url', icon_img)

        if control.setting('window.action') == '0':

            choice = control.selectDialog(choices)

            if choice == 0:

                self.listing(reddit_url('/user/{0}/saved/'.format(username)))

            elif choice == 1:

                self.bookmarks(table='reddit')

            elif choice == 2:

                self.listing(reddit_url('/api/multi/mine/'))

            else:
                control.execute('Dialog.Close(all)')
                return

        else:

            self.list = [
                {
                    'title': choices[0],
                    'action': 'listing',
                    'url': reddit_url('/user/{0}/saved/'.format(username)),
                    'image': icon_img
                }
                ,
                {
                    'title': choices[1],
                    'action': 'subscribed_subreddits',
                    'image': icon_img
                }
                ,
                {
                    'title': choices[2],
                    'action': 'listing',
                    'url': reddit_url('/api/multi/mine/'),
                    'image': icon_img
                }
            ]

            if control.setting('user.icon') == 'false':

                for i in self.list:
                    del i['image']

            directory.add(self.list)

    def search(self, media=True, override=False, query=None):

        if media:
            choices = [control.lang(30003), control.lang(30005), control.lang(30155), control.lang(30010)]
        else:
            choices = [control.lang(30003), control.lang(30005), control.lang(30010)]

        if control.setting('history.bool') == 'false':
            del choices[-1]

        if control.setting('window.action') == '0' or override:

            if media:

                if not override:
                    choice = control.selectDialog(choices)
                else:
                    choice = None

                if choice == 0 or query == 'quick':

                    search_link = url_generator()

                elif choice == 1 or query == 'advanced':

                    search_link = url_generator(advanced=True)

                elif choice == 2 or query == 'domain':

                    q = control.dialog.input(control.name())

                    search_link = url_generator(query=q)

                elif choice == 3 or query == 'history':

                    if not read_from_history(history_media):
                        return

                    queries = read_from_history(history_media)

                    if control.setting('window.action') == '0':

                        choice = control.selectDialog(queries)

                        if choice <= len(read_from_history(history_media)) and not choice == -1:
                            search_link = url_generator(read_from_history(history_media)[choice], history=True)
                        else:
                            control.execute('Dialog.Close(all)')
                            return

                    else:

                        self.list = [
                            {
                                'title': q, 'url': url_generator(q, history=True), 'action': 'search', 'query': q,
                                'isFolder': 'False', 'isPlayable': 'False'
                            } for q in queries
                        ]

                        for i in self.list:

                            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
                            bm_object = json.dumps(bookmark)
                            add_bm_cm = {'title': 30023, 'query': {'action': 'addBookmark', 'url': bm_object}}
                            i.update({'cm': [add_bm_cm]})

                        directory.add(self.list)
                        return

                elif query:

                    # Can convert a query directly to listing for display

                    search_link = url_generator(query, history=True)

                else:

                    control.execute('Dialog.Close(all)')
                    return

                directory.run_builtin(action='listing', url=search_link)

            else:

                if not override:
                    del choices[1]
                    choice = control.selectDialog(choices)
                else:
                    choice = None

                if choice == 0 or query == 'quick':

                    search_link = url_generator(media=False)

                elif choice == 1 or query == 'history':

                    if not read_from_history(history_subrs):
                        return

                    queries = read_from_history(history_subrs)

                    if control.setting('window.action') == '0':

                        choice = control.selectDialog(queries)

                        if choice <= len(read_from_history(history_media)) and not choice == -1:
                            search_link = url_generator(read_from_history(history_subrs)[choice], media=False, history=True)
                        else:
                            control.execute('Dialog.Close(all)')
                            return

                    else:

                        self.list = [
                            {
                                'title': q, 'url': url_generator(q, media=False, history=True), 'action': 'search',
                                'query': q, 'isFolder': 'False', 'isPlayable': 'False'
                            } for q in queries
                        ]

                        directory.add(self.list)
                        return

                elif query:

                    # Can convert a query directly to listing for display

                    search_link = url_generator(query=query, media=False, history=True)

                else:

                    control.execute('Dialog.Close(all)')
                    return

                directory.run_builtin(action='listing', url=search_link)

        else:

            self.list = [
                {
                    'title': control.lang(30003),
                    'action': 'search',
                    'query': 'quick',
                    'url': 'media' if media else 'subreddits'
                }
            ]

            if media:

                self.list.append(
                    {
                        'title': control.lang(30005),
                        'action': 'search',
                        'query': 'advanced',
                        'url': 'media'
                    }
                )

                self.list.append(
                    {
                        'title': control.lang(30155),
                        'action': 'search',
                        'query': 'domain',
                        'url': 'media'
                    }
                )

            for i in self.list:
                i.update({'isFolder': 'False', 'isPlayable': 'False'})

            if control.setting('history.bool') == 'true':

                self.list.append(
                    {
                        'title': control.lang(30010), 'action': 'search', 'query': 'history',
                        'url': 'media' if media else 'subreddits'
                    }
                )

        directory.add(self.list)

    @cache_method(int(control.setting('cache.size')) * 60)
    def items_list(self, link):

        if not link.startswith('http'):

            link = base_link() + link

        link = client.quote_paths(link)

        link = link.replace('old.', 'oauth.' if access_boolean() else 'www.')
        link = link.replace('www.', 'oauth.' if access_boolean() else 'www.')

        #### Start of nested helper functions ####

        # Pulls images and thumbnails
        def image_generator(children_data):

            print(children_data)

            image = control.addonInfo('icon')
            fanart = control.fanart()

            try:

                try:
                    m_thumb = children_data.get('media').get('oembed').get('thumbnail_url')
                except AttributeError:
                    m_thumb = None

                try:
                    s_thumb = children_data.get('secure_media').get('oembed').get('thumbnail_url')
                except AttributeError:
                    s_thumb = None

                try:
                    p_thumb = children_data.get('preview').get('oembed').get('thumbnail_url')
                except AttributeError:
                    p_thumb = None

                try:
                    u_thumb = children_data.get('preview').get('images')[0].get('source').get('url')
                except AttributeError:
                    u_thumb = None

                images = [
                    children_data.get('community_icon'),
                    children_data.get('icon_img'),
                    children_data.get('header_img'),
                    children_data.get('thumbnail'),
                    children_data.get('icon_img'),
                    children_data.get('header_img'),
                    children_data.get('banner_img'),
                    children_data.get('url')
                ]

                if m_thumb:
                    images.insert(-2, m_thumb)
                if s_thumb:
                    images.insert(-2, s_thumb)
                if p_thumb:
                    images.insert(-2, p_thumb)
                if u_thumb:
                    images.insert(-2, u_thumb)

                for i in images:

                    if i in ['default', 'spoiler', 'image', 'self'] or not i:
                        continue
                    elif '.jpg' in i or '.png' in i:
                        image = i
                        break

                if '?' in image:
                    image = image.partition('?')[0]

            except (KeyError, IndexError, TypeError):

                pass

            if 'embed.ly' in image:

                image = dict(parse_qsl(urlparse(image).query))['url']

            try:

                try:
                    p_fanart = children_data.get('preview').get('images')[0].get('source').get('url')
                except AttributeError:
                    p_fanart = None

                try:
                    s_fanart = children_data.get('secure_media').get('oembed').get('thumbnail_url')
                except AttributeError:
                    s_fanart = None

                fanarts = [children_data.get('banner_background_image')]

                if p_fanart:
                    fanarts.insert(0, p_fanart)

                if s_fanart:
                    fanarts.insert(-1, s_fanart)

                for f in fanarts:
                    if not f:
                        continue
                    elif f:
                        fanart = f
                        break

                if '?' in fanart:
                    fanart = fanart.partition('?')[0]

            except (KeyError, IndexError):

                pass

            return image, fanart

        # Comment
        def t1_kind(children_data, next_url):

            author = children_data['author']
            body = legacy_replace(children_data['body'])
            short = legacy_replace(body[:50] + '...')

            image = control.addonInfo('icon')

            subreddit = children_data['subreddit']
            subreddit_id = children_data['subreddit_id']
            name = children_data['name']

            if children_data['replies']:

                reply_json = children_data['replies']
                replies_children = reply_json['data']['children']
                replies = len(replies_children)
                try:
                    comprehension = [base_link() + client.quote_paths(r['data']['permalink']) for r in replies_children]
                    replies_urls = json.dumps(comprehension)
                except KeyError:
                    replies_urls = None

            else:

                replies_urls = None
                replies = 0

            replies_num = ' | ' + control.lang(30102) + str(replies) if replies > 0 else ''
            title = short.replace('\n', '') + self.formatting + '[I]' + author + '[/I]' + replies_num

            url = permalink = base_link() + children_data['permalink']

            link_id = children_data['link_id']

            pairs = {
                'title': title, 'url': url, 'permalink': permalink, 'image': image, 'subreddit': subreddit,
                'kind': 't1', 'subreddit_url': base_link() + '/r/' + subreddit, 'next': next_url,
                'subreddit_id': subreddit_id, 'name': name, 'body': body, 'plot': body, 'query': replies_urls,
                'replies_urls': replies_urls, 'link_id': link_id
            }

            return pairs

        # Link/Thread
        def t3_kind(children_data, next_url):

            title = client.replaceHTMLCodes(children_data['title'])
            name = children_data['name']
            author = children_data['author']

            domain = children_data['domain']
            num_comments = str(children_data['num_comments'])

            try:

                if domain.startswith('self.'):

                    selftext = legacy_replace(children_data['selftext'])

                    if selftext == '':

                        selftext = title

                else:

                    selftext = None

            except KeyError:

                selftext = None

            subreddit = children_data['subreddit']
            subreddit_id = children_data['subreddit_id']

            url = children_data['url']
            permalink = base_link() + children_data['permalink']

            image, fanart = image_generator(children_data)

            if access_boolean() and 'reddit' in url and not 'video' in url:

                url = url.replace('www.reddit', 'oauth.reddit')

            label = title + ' | ' + subreddit + ' | ' + '[B]' + author + '[/B]' + self.formatting + '[I]' + domain + '[/I]' + ' | ' + '[B]' + control.lang(30103) + num_comments + '[/B]'

            pairs = {
                'label': label, 'title': title, 'url': url, 'image': image, 'fanart': fanart, 'next': next_url,
                'subreddit_id': subreddit_id, 'subreddit': subreddit, 'subreddit_url': base_link() + '/r/' + subreddit,
                'kind': 't3', 'permalink': permalink, 'domain': domain, 'name': name, 'selftext': selftext,
                'author': author, 'plot': selftext, 'query': client.quote_paths(permalink)
            }

            return pairs

        # Subreddit
        def t5_kind(children_data, next_url):

            display_name = client.replaceHTMLCodes(children_data['display_name'])
            title = client.replaceHTMLCodes(children_data['title'])
            public_description = legacy_replace(children_data['public_description'])
            description = legacy_replace(children_data['description'])
            plot = json.dumps({'title': title, 'public_description': public_description, 'description': description})
            subscribers = str(children_data['subscribers'])
            url = base_link() + children_data['url']
            name = children_data['name']

            image, fanart = image_generator(children_data)

            pairs = {
                'title': title + ' | ' + subscribers + self.formatting + '[I]' + display_name + '[/I]', 'url': url,
                'image': image, 'next': next_url, 'fanart': fanart, 'display_name': display_name, 'name': name,
                'kind': 't5', 'plot': plot
            }

            return pairs

        # Multi
        def lm_kind(children_data):

            display_name = children_data['display_name']
            name = children_data['name']

            # description = html_processor(children_data['description_html'])

            try:

                image = children_data['icon_url']
                if not image:
                    raise KeyError

            except KeyError:

                image = control.addonInfo('icon')

            path = base_link() + children_data['path']

            subreddits = json.dumps(children_data['subreddits'])

            pairs = {
                'title': display_name, 'url': path, 'image': image, 'subreddits': subreddits,
                'kind': 'LabeledMulti', 'name': name
            }

            return pairs

        def more_kind(children_data):

            # title = '' if children_data['depth'] == 0 else '>' * children_data['depth'] + ' ' + control.lang(30117)
            title = control.lang(30144)
            name, id = (children_data['name'], children_data['id'])
            if len(name) < 10:
                name = children_data['parent_id']
            if len(id) < 7:
                id = children_data['parent_id'][3:]

            parsed = urlparse(link)
            permalink = urlunparse(parsed._replace(path=parsed.path + id))

            if children_data['children']:
                replies_urls = json.dumps([urlunparse(parsed._replace(path=parsed.path + u)) for u in children_data['children']])
            else:
                replies_urls = None

            image = control.addonInfo('icon')

            pairs = {
                'title': title, 'name': name, 'id': id, 'image': image, 'kind': 'more', 'permalink': permalink,
                'replies_urls': replies_urls
            }

            return pairs

        def next_appender(json_data):

            try:

                next_id = json_data['after']
                if not next_id:
                    raise KeyError
                elif '&after=' in parsed.query:
                    _next_url = urlunparse(parsed._replace(query=re.sub(r'&after=\w{8,9}', r'&after=' + next_id, parsed.query)))
                else:
                    _next_url = urlunparse(parsed._replace(query=parsed.query + '&after=' + next_id))

            except KeyError:

                _next_url = ''

            return _next_url

        def processor(_json):

            if isinstance(_json, list):

                for j in _json:

                    data = j['data']
                    kind = j['kind']

                    if kind == 'LabeledMulti':

                        pairs = lm_kind(data)

                        self.data.append(pairs)

                    else:

                        children = data['children']

                        nu = next_appender(data)

                        for c in children:

                            kind = c['kind']

                            data = c['data']

                            if kind == 't3':

                                pairs = t3_kind(data, nu)

                            elif kind == 't1':

                                pairs = t1_kind(data, nu)

                            elif kind == 'more':

                                pairs = more_kind(data)

                            else:

                                pairs = None

                            self.data.append(pairs)

                return self.data

            else:

                data = _json['data']

                children = data['children']

                nu = next_appender(data)

                for d in children:

                    item_data = d['data']
                    kind = d['kind']

                    # Link:
                    if kind == 't3':

                        pairs = t3_kind(item_data, nu)

                    # Subreddit:
                    elif kind == 't5':

                        pairs = t5_kind(item_data, nu)

                    # Comment:
                    elif kind == 't1':

                        pairs = t1_kind(item_data, nu)

                    elif kind == 'more':

                        pairs = more_kind(data)

                    else:

                        pairs = {
                            'title': 'Null',
                            'action': None
                        }

                    self.data.append(pairs)

                return self.data

        #### End of nested helper functions ####

        parsed = urlparse(link)
        query = dict(parse_qsl(parsed.query))
        path = parsed.path

        if 'limit' not in query:

            query.update({'limit': control.setting('items.limit')})

        query = urlencode(query)

        if not access_boolean() and not path.endswith('.json'):

            path += dotjson

        link = urlunparse(parsed._replace(path=path, query=query))

        json_object = client.request(link, headers=request_headers())

        loaded = json.loads(json_object)

        self.list = processor(loaded)

        return self.list

    @cache_method(int(control.setting('cache.size')) * 60)
    def replies_viewer(self, query):

        reply_urls = json.loads(query)

        self.data = [self.items_list(ru) for ru in reply_urls][0]

        self.list = [i for i in self.data if i['kind'] == 't1' or i['kind'] == 'more']

        self.list.insert(0, self.data[0])

        return self.list

    def listing(self, url=None, return_list=False, query=None):

        if url:
            self.data = self.items_list(url)
        else:
            self.data = self.replies_viewer(query)

        if self.data is None:

            return

        self.list = action_updater(self.data)

        self.menu = cm_updater(self.list, url)

        if return_list:

            return self.menu

        else:

            if active_mode()[1] == 'pictures':

                for i in self.menu:
                    li = control.item(label=i['title'])
                    li.setArt(
                        {
                            'icon': i['image'], 'poster': i['image'], 'thumb': i['image'],
                            'fanart': control.addonInfo('fanart')
                        }
                    )
                    li.setInfo('image', {'title': i['title'], 'picturepath': i['url']})
                    url = i['url']
                    self.directory.append((url, li, False))

                control.addItems(init.syshandle, self.directory)
                control.directory(init.syshandle)

            else:

                directory.add(self.menu, content='movies')

    def bookmarks(self, table=None):

        if not table:
            self.data = bookmarks.get()
            action = 'deleteBookmark'
        elif table == 'reddit':
            self.data = self.listing(reddit_url('/subreddits/mine/subscriber'), return_list=True)
            action = 'unsubscribeSubreddit'
        else:
            self.data = bookmarks.get(file_=saved_subrs)
            action = 'deleteSubreddit'

        if not self.data:

            directory.add(
                [
                    {
                        'title': control.lang(30025 if not table else 30026), 'action': None,
                        'icon': 'no_bookmarks.png' if not table else 'no_subreddits_found.png'
                    }
                ]
            )

        else:

            self.list = cm_updater(self.data)

            try:

                urls = '+'.join([i.get('display_name') for i in self.list])
                ms_cm = {'title': 30101, 'query': {'action': 'multi', 'url': urls}}

            except TypeError:

                ms_cm = None

            if table != 'reddit':

                for i in self.list:

                    bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
                    bookmark['delbookmark'] = i['url']

                    del_bm_cm = {
                        'title': control.lang(30024 if not table else 30039),
                        'query': {'action': action, 'url': json.dumps(bookmark)}
                    }

                    i['cm'][0] = del_bm_cm

            else:

                for i in self.list:

                    unsub_cm = {'title': 30088, 'query': {'action': action, 'query': i['display_name']}}
                    sync_cm = {'title': 30089, 'query': {'action': 'sync'}}

                    i['cm'][2] = unsub_cm
                    i['cm'] += [sync_cm, ms_cm]

            self.list = sorted(self.list, key=lambda k: k['title'].lower())

            if not table:
                directory.add(self.list, content='videos')
            else:
                directory.add(self.list)

    def tools(self):

        self.list = [
            {
                'title': control.lang(30057 if not access_boolean() else 30058),
                'action': 'authorize' if not access_boolean() else 'revoke',
                'icon': 'authorize.png' if not access_boolean() else 'revoke.png',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': control.lang(30050),
                'action': 'settings',
                'icon': 'settings_tools.png',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': control.lang(30004),
                'action': 'readme',
                'icon': 'read_me.png',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': control.lang(30042),
                'action': 'clear_cache',
                'icon': 'settings_tools.png',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': control.lang(30040),
                'action': 'delete_history',
                'icon': 'settings_tools.png',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': control.lang(30045),
                'action': 'purge_bookmarks',
                'icon': 'settings_tools.png',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': control.lang(30115),
                'action': 'quit',
                'icon': 'quit.png',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
        ]

        directory.add(self.list)
