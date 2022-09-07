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

from tulip.compat import parse_qsl
from sys import argv
from resources.lib.modules.tools import refresh_access, first_time_prompt

params = dict(parse_qsl(argv[2].replace('?', '')))

content = params.get('content_type')
action = params.get('action')
url = params.get('url')
image = params.get('image')
title = params.get('title')
name = params.get('name')
query = params.get('query')
plot = params.get('plot')
genre = params.get('genre')

refresh_access()
first_time_prompt()


if content in ['video', 'audio', 'image'] or action == 'root':

    from resources.lib.indexers import navigator
    navigator.Main().root()

elif action == 'mode_change' or action is None:

    from resources.lib.indexers import navigator
    navigator.Main().executable()

elif action == 'window_activate':

    from resources.lib.modules.tools import window_activate
    if query in ['video', 'audio', 'image']:
        window_activate(query=query, jump=False)
    else:
        window_activate(url=url, jump=True)

elif action == 'multi':

    from resources.lib.modules.reddit import multisel
    from resources.lib.modules.tools import window_activate
    output = multisel(url, simple=True)
    window_activate(url=output, jump=True)

elif action == 'multisel':

    from resources.lib.modules.reddit import multisel
    from resources.lib.modules.tools import window_activate
    output = multisel(url)
    window_activate(url=output, jump=True)

elif action == 'search':

    from resources.lib.indexers import navigator

    media = url == 'media'

    if query in ['quick', 'advanced', 'history', 'domain']:

        navigator.Main().search(media=media, override=True, query=query)

    elif query:

        navigator.Main().search(media='subreddits/search' not in url, override=True, query=query)

    else:

        navigator.Main().search(media=media)

elif action == 'listing':

    from resources.lib.indexers import navigator
    if query:
        navigator.Main().listing(query=query)
    else:
        navigator.Main().listing(url=url)

elif action == 'replies_viewer':

    from resources.lib.modules.tools import window_activate
    window_activate(query=query, jump=True)

elif action == 'my_account':

    from resources.lib.indexers import navigator
    navigator.Main().my_account()

elif action == 'readme':

    from resources.lib.modules.tools import readme
    readme()

elif action == 'text_viewer':

    from resources.lib.modules.player import text_viewer
    text_viewer(plot, title, permalink=query)

elif action == 'comment_scraper':

    from resources.lib.modules.player import comment_scraper
    comment_scraper(plot, title)

elif action == 'play':

    from resources.lib.modules.player import play
    play(url, permalink=query)

elif action == 'show_picture':

    from resources.lib.modules.player import show_picture
    show_picture(title, url, permalink=query)

elif action == 'addBookmark':

    from tulip import bookmarks
    bookmarks.add(url)

elif action == 'deleteBookmark':

    from tulip import bookmarks
    bookmarks.delete(url)

elif action == 'bookmarks':

    from resources.lib.indexers import navigator
    navigator.Main().bookmarks()

elif action == 'addSubreddit':

    from tulip import bookmarks
    from resources.lib.modules.tools import saved_subrs
    bookmarks.add(url, file_=saved_subrs)

elif action == 'subscribeSubreddit':

    from resources.lib.modules.reddit import reddit_subs
    reddit_subs(action='sub', sr_name=query)

elif action == 'save_thing':

    action = 'save'

    from resources.lib.modules.reddit import reddit_save
    reddit_save(action, url)

elif action == 'unsave_thing':

    action = 'unsave'

    from resources.lib.modules.reddit import reddit_save
    reddit_save(action, url)

elif action == 'deleteSubreddit':

    from tulip import bookmarks
    from resources.lib.modules.tools import saved_subrs
    bookmarks.delete(url, file_=saved_subrs)

elif action == 'unsubscribeSubreddit':

    from resources.lib.modules.reddit import reddit_subs
    reddit_subs(action='unsub', sr_name=query)

elif action == 'saved_subreddits':

    from resources.lib.indexers import navigator
    from resources.lib.modules.tools import saved_subrs
    navigator.Main().bookmarks(table=saved_subrs)

elif action == 'subscribed_subreddits':

    from resources.lib.indexers import navigator
    navigator.Main().bookmarks(table='reddit')

elif action == 'sync':

    from resources.lib.modules.reddit import reddit_subs

    reddit_subs(action=None, sr_name=None)

elif action == 'purge_bookmarks':

    from resources.lib.modules.tools import deletion
    deletion(history=False)

elif action == 'settings':

    from tulip import control
    control.openSettings()

elif action == 'tools':

    from resources.lib.indexers import navigator
    navigator.Main().tools()

elif action == 'delete_history':

    from resources.lib.modules.tools import deletion
    deletion()

elif action == 'authorize':

    from resources.lib.modules.reddit import authorize
    authorize()

elif action == 'revoke':

    from resources.lib.modules.reddit import revoke
    revoke()

elif action == 'get_tokens':

    from resources.lib.modules.reddit import get_tokens
    get_tokens()

elif action == 'access_renewal':

    from resources.lib.modules.reddit import get_tokens
    get_tokens(refresh=True)

elif action == 'ip_address_set':

    from resources.lib.modules.reddit import ip_address_set
    ip_address_set()

elif action == 'clear_cache':

    from tulip import cache
    cache.FunctionCache().reset_cache(notify=True)

elif action == 'debugging_toggle':

    from resources.lib.modules.tools import debugging_toggle
    debugging_toggle()

elif action == 'refresh':

    from resources.lib.modules.tools import refresh
    refresh()

elif action == 'quit':

    from tulip.control import quit_kodi
    quit_kodi()


# TODO: Add ability to open /r/* links (needs testing)
# TODO: Add /domain/* navigation ability (needs testing)
