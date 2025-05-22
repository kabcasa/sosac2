# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 Thomas Amland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import xbmc
import xbmcvfs    # 4.8.0  https://github.com/xbmc/xbmc/pull/19301
import requests
from resources.lib.util import *
from io import StringIO


def get_subtitles(video_id,index):
    
    subs = requests.get(video_id)
    debug("subs requests get subtitle status %s"%subs,2)
    
    if not subs:
        debug("subs requests get subtitle status %s"%subs.status_code,2)
        return None

    content = _vtt_to_srt(subs.text)
    debug("subs requests get subtitle status subs %s"%content,2)
    nor = f"nor{index}.srt"
    try:
        filename1 = xbmcvfs.translatePath(os.path.join(profilepath, nor))
        filename = xbmcvfs.validatePath(filename1)
        debug("subs filename passe par 1 ",2)# deprecated already in Kodi v19
    except Exception as e :
        debug("subs filename %s"%str(e),2)
        debug("subs filename passe par 2 ",2)
        filename = os.path.join(profilepath, nor)  # 4.8.0 https://github.com/xbmc/xbmc/pull/19301
    with xbmcvfs.File(filename, 'w') as f:
        result = f.write(content)
    return filename

def save_sub(video_id,video_path):
    
    subs = requests.get(video_id)
    debug("subs requests get subtitle status %s"%subs,2)
    
    if not subs:
        debug("subs requests get subtitle status %s"%subs.status_code,2)
        return None

    content = _vtt_to_srt(subs.text)
    debug("subs requests get subtitle status subs %s"%content,2)
    nor = f"{video_path}.srt"
    try:
        #filename1 = xbmcvfs.translatePath(os.path.join(profilepath, nor))
        filename = xbmcvfs.validatePath(video_path)
        debug("subs filename passe par 1 ",2)# deprecated already in Kodi v19
    except Exception as e :
        debug("subs filename %s"%str(e),2)
        debug("subs filename passe par 2 ",2)
        filename = os.path.join(profilepath, nor)  # 4.8.0 https://github.com/xbmc/xbmc/pull/19301
    with xbmcvfs.File(filename, 'w') as f:
        result = f.write(content)
    return filename

def _vtt_to_srt(content):
    return content

def _str_to_time(txt):
    p = txt.split(':')
    try:
        ms = float(p[2])
    except ValueError:
        ms = 0
    return int(p[0]) * 3600 + int(p[1]) * 60 + ms


def _time_to_str(time):
    return '%02d:%02d:%02d,%03d' % (time / 3600, (time % 3600) / 60, time % 60, (time % 1) * 1000)
