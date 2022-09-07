### Description

Reddit Navigator is a free and open source Kodi addon for the popular social sharing platform known as [Reddit](https://www.reddit.com).

Since it is designed to work with the Kodi media center, certain limitations do apply. This Kodi addon has been developed from scratch.

Reddit Navigator for Kodi is designed to scrape all forms of content: video, live streams, audio, images, and text.

**Features:**

* Fully featured navigation of the Reddit platform via json for both guests and registered users.
* Video, Pictures, Audio and Executable modes. Mode changer provided for convenience.
* Caching improving performance with adjustable setting, while reducing the number of requests to Reddit.
* Quick, Advanced, History modes of searching for both media links and text posts. By default only link/media searches are performed.
* Ability to set default domains on search query.
* Separate local bookmarking for both media/text posts and subreddits.
* Multi-Reddit navigation and composition/filtering of them.
* Login function via oauth2, (semi-)automatic access/refresh tokens retrieval (or manual).
* My account menu allowing access to remotely saved items and subscriptions and ability to sync locally saved items.
* QRcode generation for obtaining tokens from a mobile device.
* Tokens revocation function acting as logout.
* VOD playback with the help of [resolveurl](https://github.com/jsergio123/script.module.resolveurl).
* P2P acestream/sopcast playback with the help of plexus (optional).
* Textviewer for comments.
* Full-screen and windowed image modes display.
* Resolver for images on the following sites: imgur, instagram, imagebam, gfycat, tinypic, pixhost and possibly others as well (through a generic resolver)
* Comprehensive addon settings to adjust various aspects.
* Comprehensive context menu with various actions such as subscribing to subreddits, opening nested threads, refresh current directories etc.
* Debugging for errors/operations retrieval.
* Preliminary support for Python 3 (Kodi 18+).

**Reddit permissions requested for login/authorization:**

* **Subscribe**: Manage my subreddit subscriptions. Manage "friends" - users whose content I follow.
* **Identity**: Access my reddit username and signup date. (Reddit Browser will not have access do your Reddit password)
* **Read**: Access posts and comments through my account.
* **Mysubreddits**: Access the list of subreddits I moderate, contribute to, and subscribe to.
* **Save**: Save and unsave comments and submissions.
* **History**: Access my voting history and comments or submissions I've saved or hidden.

**Dependencies:**

* Tulip libraries kindly provided by Twilight0: [https://github.com/Twilight0/script.module.tulip](https://github.com/Twilight0/script.module.tulip)
* ResolveURL for video resolving from various cyberlockers
* Youtube addon (provides resolving and dash playback of youtube streams)
* **Pyxbmct** for windowed display of images and authentication window

Icons sourced from **Flaticon.com** ([Licence](https://file000.flaticon.com/downloads/license/license.pdf "Licence"))
