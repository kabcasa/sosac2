import sys, json, os, shutil
from datetime import datetime as dt
from datetime import timedelta
import threading
import xbmc, xbmcvfs
from resources.lib import plugin
from resources.lib.util import *
addon_id = 'plugin.video.sosac-2'
addon_name_ = 'Sosac.TV'
addon = xbmcaddon.Addon(addon_id)
__set__ = addon.getSetting
addonPath = xbmcvfs.translatePath(addon.getAddonInfo('path'))
HOME = xbmcvfs.translatePath("special://home")
addonsPath = xbmcvfs.translatePath('special://home/addons')


plugin.run()
