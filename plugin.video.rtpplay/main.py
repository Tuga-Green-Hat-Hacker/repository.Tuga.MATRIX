from resources.lib import kodilogging
from resources.lib import plugin

import xbmcaddon

# Keep this file to a minimum, as Kodi
# doesn't keep a compiled copy of this
ADDON = xbmcaddon.Addon()
kodilogging.config()
plugin.run()
