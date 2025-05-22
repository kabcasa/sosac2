# -*- coding: UTF-8 -*-

import sys, os, requests, json
from hashlib import md5
import urllib.parse
import xbmcaddon
import xbmcgui
import xbmcvfs
import xbmc

addon_id = 'plugin.video.sosac-2'
#addon_name_ = translate(30402) #'Sosac.TV'
addon = xbmcaddon.Addon(addon_id)
addonPath = xbmcvfs.translatePath(addon.getAddonInfo('path'))
artPath = xbmcvfs.translatePath(os.path.join(addonPath,"resources","icons"))
imgPath = xbmcvfs.translatePath(os.path.join(addonPath,"resources","images"))
libPath = xbmcvfs.translatePath(os.path.join(addonPath,"resources","lib"))
profilepath = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
addon_lang = addon.getLocalizedString
__set__ = addon.getSetting
dialog = xbmcgui.Dialog()

settings = {'downloads': __set__('downloads'), 'quality': __set__(
    'quality'), 'subs': __set__('subs') == 'true', 'lang': __set__('language')}

qual_orig = ["2160p(UHD)","1080p(FHD)","720p(HD)","480p(SD)"]
dubb_orig = ["CZECH","SLOVAK","ENGLISH"]
topic_orig = ["NO","CZECH","SLOVAK"]
yesno = ["YES","NO"]

sosac_domain = __set__("sosac_domain")
streaming_provider = __set__("streaming_provider")
domain_actif = __set__("domain_actif")
print("domain_actif ",domain_actif)
#STREAMUJ_API = "https://www.streamuj.tv/json_api_player.php?"
#SOSAC_API = "https://kodi-api.sosac.to/"
STREAMUJ_API = f"https://{streaming_provider}/json_api_player.php?"
SOSAC_API = f"https://{sosac_domain}/"
SOSAC_MOVIES = "https://movies.sosac.tv/images/75x109/movie-"
SOSAC_SERIES = "http://movies.sosac.tv/images/558x313/serial-"
streamujtv_user = __set__('streamujtv_user')
streamujtv_pass = __set__('streamujtv_pass')
streamujtv_location = __set__('streamujtv_location')
streamujtv_location = str(int(streamujtv_location) + 1)
sosac_user = __set__('sosac_user')
sosac_pass = __set__('sosac_pass')

try : 
    auto_stream = __set__('auto-stream')
    quality = qual_orig[int(__set__('quality'))]
    first_dubbing = dubb_orig[int(__set__('first-dubbing'))]
    second_dubbing = dubb_orig[int(__set__('second-dubbing'))]
    auto_subtitles = __set__('auto-subtitles')
    first_subtitles = dubb_orig[int(__set__('first-subtitles'))]
    second_subtitles = dubb_orig[int(__set__('second-subtitles'))]
    next_episode = __set__('next-episode')
    current_topic = topic_orig[int(__set__('current-topic'))]
except :
    pass
down_int = [10, 20, 30, 40, 50]

    
COUNTRY_DICT = {
    "Czech Republic":1, "USA":2, "Slovakia":3, "Great Britain":4, "Germany":5,"Spain":6, "America":7,
    "France":8, "Italia":9, "Canada":10, "Romania":11, "Japan":12, "HongKong":13, "Turkey":14,
    "Austria":15, "Denmark":16, "Netherlands":17, "Belgium":18, "Ireland":19,
    "Egypt":20, "Switzerland":21, "Peru":22,"Luxembourg":23, "JAR":24,
    "New Zealand":25, "China":26, "Ukraine":27, "Finland":28,"Sweden":29,"Russia":30}

COUNTRY_DICT_old = {
    "Czech Republic":"cs","USA":"us","Slovakia":"sk","Great Britain":"uk","Germany":"de","Spain":"es","America":"en",
    "France":"fr","Italia":"it","Canada":"ca","Romania":"ro","Japan":"ja","HongKong":"cn","Turkey":"tr",
    "Austria":"de","Denmark":"dk","Netherlands":"nl","Belgium":"be","Ireland":"ie",
    "Egypt":"eg","Switzerland":"ch","Peru":"pe","Luxembourg":"lu","JAR":"za",
    "New Zealand":"nz","China":"cn","Ukraine":"ua","Finland":"fi","Sweden":"se","Russia":"ru"}
country_list = ["cs","us","sk","uk","de","es","en","fr","it","ca","ro","ja","cn","tr",
    "de","dk","nl","be","ie","eg","ch","pe","lu","za","nz","cn","ua","fi","se","ru"]

sort_list ={
"popularity":"v1","CSFD rating":"v2","IMDB rating":"v3","movie budget":"v4",
"movie revenue":"v5","alphabet":"v6","date added":"v7","best match":""}
SORT_Listv = ["v1","-v1","v2","-v2","v3","-v3","v4","-v4","v5","-v5","v6","-v6","v7","-v7",""]
SORT_Listsv = ["v1","-v1","v2","-v2","v3","-v3","v4","-v6","v5","-v7",""]

dub_list1 = ['CZECH', 'SLOVAK', 'ENGLISH', 'CHINESE', 'GERMAN', 'GREEK', 'SPANISH', 'FINNISH', 'FRENCH', 'CROATIAN', 'INDU', 'ITALIAN',\
             'JAPANESE', 'KOREAN', 'DUTCH', 'NORWEGIAN','POLISH', 'PORTUGUESE', 'RUSSIAN', 'TURKISH', 'VIETNAMESE']

DUBBING = {
    'CZECH': 'cz',
     'SLOVAK': 'sk',
     'ENGLISH': 'en',
     'CHINESE': 'cn',
     'GERMAN': 'de',
     'GREEK': 'el',
     'SPANISH': 'es',
     'FINNISH': 'fi',
     'FRENCH': 'fr',
     'CROATIAN': 'hr',
     'INDU': 'id',
     'ITALIAN': 'it',
     'JAPANESE': 'ja',
     'KOREAN': 'ko',
     'DUTCH': 'nl',
     'NORWEGIAN': 'no',
     'POLISH': 'pl',
     'PORTUGUESE': 'pt',
     'RUSSIAN': 'ru',
     'TURKISH': 'tr',
     'VIETNAMESE': 'vi'}

sort_dict ={
"popularity":"v1","CSFD rating":"v2","IMDB rating":"v3","movie budget":"v4","movie revenue":"v5","alphabet":"v6","date added":"v7","best match":""}
sort_dicts ={
"popularity":"v1","popularity descending":"-v1","CSFD rating":"v2","CSFD rating descending":"-v2","IMDB rating":"v3","IMDB rating descending":"-v3",
"alphabet":"v4","alphabet descending":"-v6","date added":"v5","date added descending":"-v7","best match":""}

genre1 = ["action","adventure","animation","biography","cartoons","comedy","crime","disaster","documentary","drama","erotic",
  "experimental","fairytales","family","fantasy","history","horror","imax","krimi","music","mystery",
  "psychological","publicistic","realitytv","romance","sci-fi","sport","talkshow","thriller","war","western"]

country_list0 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]

############################################
def get_icon(icon) :
    return os.path.join(artPath,icon)

def debug(text,level):
    if level == 0 : xbmc.log(str([text]))
    elif level == 1 : xbmc.log(str([text]), xbmc.LOGDEBUG)
    elif level == 2 : xbmc.log(str([text]), xbmc.LOGERROR)

def notify(title, message, time=5000):
    try:
        xbmcgui.Dialog().notification(title, message, time=time)
    except exception as e:
        debug(" error notify %s"%e,2)

def translate(text):
      return addon.getLocalizedString(text)

def isMatrix():
    try:
        version = xbmc.getInfoLabel('system.buildversion')
        if version[0:2] >= '19':
            return True
        else:
            return False
    except:
        return False


def isNexus():
    try:
        version = xbmc.getInfoLabel('system.buildversion')
        if version[0:2] >= '20':
            return True
        else:
            return False
    except:
        return False

try :
    down_folder = addon.getSetting("downloads")
    moviesPath = xbmcvfs.translatePath(os.path.join(down_folder,"movies"))
    seriesPath = xbmcvfs.translatePath(os.path.join(down_folder,"series"))
    moviesSub= xbmcvfs.translatePath(os.path.join(down_folder,"moviessub"))
    seriesSub = xbmcvfs.translatePath(os.path.join(down_folder,"seriessub"))
    movie_data = xbmcvfs.translatePath(os.path.join(profilepath,"movie_data.json"))
    if not xbmcvfs.exists(movie_data) :
        f_data = {}
        f_data["test"] = "test"
        with open(movie_data, "w") as fdata :
            json.dump(f_data, fdata, indent=4)
            #fdata.write(json.dumps(f_data))
    serial_data = xbmcvfs.translatePath(os.path.join(profilepath,"serial_data.json"))
    if not xbmcvfs.exists(serial_data) :
        f_data = {}
        f_data["test"] = "test"
        with open(serial_data, "w") as fdata :
            json.dump(f_data, fdata, indent=4)
            #fdata.write(json.dumps(f_data))

    movie_search = xbmcvfs.translatePath(os.path.join(profilepath,"movie_search.txt"))
    serial_search = xbmcvfs.translatePath(os.path.join(profilepath,"serial_search.txt"))
    if not os.path.isdir(moviesPath) : os.mkdir(moviesPath)
    if not os.path.isdir(seriesPath) : os.mkdir(seriesPath)
    if not os.path.isdir(moviesSub) : os.mkdir(moviesSub)
    if not os.path.isdir(seriesSub) : os.mkdir(seriesSub)
except Exception as e :
    debug("downfolder error %s"%e, 2)

xbmcpath = xbmcvfs.translatePath(os.path.join("special://xbmc","skin.estuary"))
skinpath = xbmcvfs.translatePath("special://skin")

ADVANCEDSETTINGS = xbmcvfs.translatePath(os.path.join("special://userdata","advancedsettings.xml"))
downListPath = xbmcvfs.translatePath(os.path.join(profilepath,"downList"))

addon_name_ = translate(30402) #'Sosac.TV'

#########################################
def sosachash() :
    if len(sosac_user) == 0 or len(sosac_pass) == 0:
        repse = dialog.yesno(addon_name_,translate(30404))
        if repse  :
            addon.openSettings()
            return None
        else : return None
        
    # set streamujtv credentials
    
    passwordForApi = md5(f"{sosac_user}:{sosac_pass}".encode('utf-8')).hexdigest()
    passwordForApi2 = md5((passwordForApi + 'EWs5yVD4QF2sshGm22EWVa').encode('utf-8'))
    sosac_passwordhash = passwordForApi2.hexdigest()
    if sosac_passwordhash : 
        stream_url = f"{SOSAC_API}movies/lists/queue?pocet=1&stranka=1&username={sosac_user}&password={sosac_passwordhash}"
        return stream_url
    else : exit()

def passhash() :
    if len(sosac_user) == 0 or len(sosac_pass) == 0:
        repse = dialog.yesno(addon_name_,translate(30404))
        if repse  : addon.openSettings()
        else : exit()
        
    # set streamujtv credentials
    passwordForApi = md5(f"{sosac_user}:{sosac_pass}".encode('utf-8')).hexdigest()
    passwordForApi2 = md5((passwordForApi + 'EWs5yVD4QF2sshGm22EWVa').encode('utf-8'))
    sosac_passwordhash = passwordForApi2.hexdigest()
    stream_url = f"{SOSAC_API}movies/lists/popular?pocet=100&stranka=1&username={sosac_user}&password={sosac_passwordhash}"
    source = requests.get(stream_url)
    data = json.loads(source.text)
    debug("passhash %s "%source.status_code, 2)
    debug("passhash data %s "%data[0], 2)
    try :
        if data[0]["w"] == None :
            debug('data["w"] %s'%data[0]["w"],2)
            repse = dialog.yesno(addon_name_,translate(30405))
            if repse  :
                addon.openSettings()
            exit()
    except Exception as e:
        debug('data["w"] error %s'%e,2)
        pass
    
    if source.status_code == "403" :
        repse = dialog.yesno(addon_name_,translate(30404))
        if repse  :
            addon.openSettings()
        exit()
    elif source.status_code == "401" :
        repse = dialog.yesno(addon_name_,translate(30405))
        if repse  :
            addon.openSettings()
        exit()
    return sosac_passwordhash

def set_streamujtv_info(stream):
    if len(streamujtv_user) == 0 or len(streamujtv_pass) == 0:
        repse = dialog.yesno(addon_name_,translate(30404))
        if repse  : addon.openSettings()
        else : exit()

    if len(streamujtv_user) > 0 and len(streamujtv_pass) > 0:
        # set streamujtv credentials
        m = md5()
        m.update(streamujtv_pass.encode('utf-8'))
        h = m.hexdigest()
    else : h = ""
    
    if stream :
        if streamujtv_location in ['1', '2']:
            location = streamujtv_location
        else : location = 1
        stream_url = f"{STREAMUJ_API}action=get-video-links&link={stream}&login={streamujtv_user}&password={h}&location={location}"
    elif h  :
        stream_url = f"{STREAMUJ_API}action=check-user&password={h}&login={streamujtv_user}&passwordinmd5=1"
    else : exit()
    print("check stream_url", stream_url)
    return stream_url

def set_sosac_info(stream,**kwargs):
    print("util kwargs ",kwargs)
    sosac_passwordhash = passhash()
    page = kwargs['arg3'] if 'arg3' in kwargs else "1"
    
    
    if  "a-z" == stream:
        letter = kwargs['arg2'].lower()
        stream_url = f"{SOSAC_API}movies/lists/a-z?l={letter}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "by-year" == stream :
        year = kwargs['arg2']
        stream_url = f"{SOSAC_API}movies/lists/by-year?y={year}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "by-quality" == stream :
        quality = kwargs['arg2']
        stream_url = f"{SOSAC_API}movies/lists/by-quality?q={quality}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "by-genre" == stream :
        genrev = kwargs['arg2']
        genre = genre1[int(genrev)]
        stream_url = f"{SOSAC_API}movies/lists/by-genre?g={genre}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "search" == stream :
        keyword = kwargs['arg2']
        stream_url = f"{SOSAC_API}movies/simple-search?q={keyword}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "advancedsearch" == stream :
        search = urllib.parse.quote_plus(__set__('adv_keyword'))
        debug(" params %s"%search,2)
        yearfrom = __set__('adv_from')
        yearto = __set__('adv_to')
        debug(" params %s"%yearto,2)
        year = f"{int(yearfrom)},{int(yearto)}" if yearto != "" else yearfrom
        genre = genre1[int(__set__('adv_genre'))-1] if  int(__set__('adv_genre')) != 0 else ""
        debug("__set__('adv_quality') %s"%__set__('adv_quality'), 2)
        quality = "" if  __set__('adv_quality') == "All" or __set__('adv_quality') == "Vše" else __set__('adv_quality').lower()
        debug("__set__('adv_origin') %s"%__set__('adv_origin'), 2)
        country = country_list[int(__set__('adv_origin'))-1 ] if  int(__set__('adv_origin')) != 0 else "" 
        #country = COUNTRY_DICT[__set__('adv_origin')] if  __set__('adv_origin') != "All" else ""
        dubv = dub_list1[int(__set__('adv_lang'))-1 ] if  int(__set__('adv_lang')) != 0 else "" 
        language = DUBBING[dubv] if  dubv != "" else ""
        debug(" params %s"%language,2)
        director = urllib.parse.quote_plus(__set__('adv_director'))
        scriptwriter = urllib.parse.quote_plus(__set__('adv_writer'))
        actor = urllib.parse.quote_plus(__set__('adv_actor'))
        sort_set = int(__set__('adv_sort'))
        sort_v = SORT_Listv[sort_set] 
        stream_url = f"{SOSAC_API}movies/advanced-search?k={search}&y={year}&g={genre}&q={quality}&c={country}&l={language}&d={director}&s={scriptwriter}&a={actor}&pocet=10&stranka={page}&o={sort_v}&username={sosac_user}&password={sosac_passwordhash}"
        #stream_url = stream_url.replace("&","&amp;")
    elif "watching-time" == stream :
        _id = kwargs['arg2']
        stream_url = f"{SOSAC_API}movies/{_id}/watching-time?username={sosac_user}&password={sosac_passwordhash}"
    elif stream == "into-queue" :
        _id = kwargs['arg2']
        stream_url = f"{SOSAC_API}movies/{_id}/into-queue?username={sosac_user}&password={sosac_passwordhash}"
        respse = requests.post(stream_url,data={})
        return
    elif stream == "off-queue" :
        _id = kwargs['arg2']
        stream_url = f"{SOSAC_API}movies/{_id}/off-queue?username={sosac_user}&password={sosac_passwordhash}"
        respse = requests.post(stream_url,data={})
        return
    elif stream == "id":
        _id = kwargs['arg2']
        stream_url = f"{SOSAC_API}movies/{_id}?username={sosac_user}&password={sosac_passwordhash}"

    else : 
        stream_url = f"{SOSAC_API}movies/lists/{stream}?pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"

    debug("stream_url %s"%stream_url,2)
    return stream_url


def set_sosac_ser(stream,**kwargs):
    sosac_passwordhash = passhash()
    episodes = kwargs['arg3']
    page = kwargs['arg5'] if 'arg5' in kwargs else "1"
    
    if  "a-z" == stream:
        letter = kwargs['arg2'].lower()
        stream_url = f"{SOSAC_API}serials/lists/a-z?l={letter}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "by-year" == stream :
        year = kwargs['arg2']
        stream_url = f"{SOSAC_API}serials/lists/by-year?y={year}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "by-quality" == stream :
        quality = kwargs['arg2']
        stream_url = f"{SOSAC_API}serials/lists/by-quality?q={quality}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "by-genre" == stream :
        genrev = kwargs['arg2']
        genre = genre1[int(genrev)]
        stream_url = f"{SOSAC_API}serials/lists/by-genre?g={genre}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "search" == stream :
        keyword = kwargs['arg2']
        stream_url = f"{SOSAC_API}serials/simple-search?q={keyword}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    elif "advancedsearch" == stream : 
        search = urllib.parse.quote_plus(__set__('adv_keywords'))
        #debug(" params %s"%search,2)
        yearfrom = __set__('adv_froms')
        yearto = __set__('adv_tos')
        #debug(" params %s"%yearto,2)
        year = f"{int(yearfrom)},{int(yearto)}" if yearto != "" else yearfrom
        genre = genre1[int(__set__('adv_genres'))-1] if  int(__set__('adv_genres')) != 0 else ""
        quality = "" if  __set__('adv_qualitys') == "All" or __set__('adv_quality') == "Vše" else __set__('adv_qualitys').lower()
        country = country_list[int(__set__('adv_origins'))-1 ] if  int(__set__('adv_origins')) != 0 else "" 
        dubv = dub_list1[int(__set__('adv_langs'))-1 ] if  int(__set__('adv_langs')) != 0 else "" 
        language = DUBBING[dubv] if  dubv != "" else ""
        debug(" params %s"%language,2)
        director = urllib.parse.quote_plus(__set__('adv_directors'))
        scriptwriter = urllib.parse.quote_plus(__set__('adv_writers'))
        actor = urllib.parse.quote_plus(__set__('adv_actors'))
        sort_set = int(__set__('adv_sorts'))
        sort_v = SORT_Listsv[sort_set] 
        stream_url = f"{SOSAC_API}serials/advanced-search?k={search}&y={year}&g={genre}&q={quality}&c={country}&l={language}&d={director}&s={scriptwriter}&a={actor}&pocet=10&stranka={page}&o={sort_v}&username={sosac_user}&password={sosac_passwordhash}"
        #stream_url = stream_url.replace("&","&amp;")
        #stream_url = f"{SOSAC_API}serials/advanced-search?k={search}&y={year}&g={genre}&q={quality}&c={country}&l={language}&d={director}&s={scriptwriter}&a={actor}&pocet=10&stranka=1&o={sorted}&username={sosac_user}&password={sosac_passwordhash}"
    elif "by-date" == stream :
        date_from = kwargs['arg2']
        debug("by-date date_from %s"%date_from,2)
        date_to = kwargs['arg3']
        debug("by-date date_to %s"%date_to,2)
        stream_url = f"{SOSAC_API}episodes/lists/by-date?f={date_from}&t={date_to}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"         
    elif (stream == "watching-time") and ("episodes" == episodes) :
        _id = kwargs['arg2']
        stream_url = f"{SOSAC_API}episodes/{_id}/watching-time?username={sosac_user}&password={sosac_passwordhash}"
    elif stream == "watching-time" :
        _id = kwargs['arg2']
        stream_url = f"{SOSAC_API}serials/{_id}/watching-time?username={sosac_user}&password={sosac_passwordhash}"
    elif stream == "into-queue" :
        _id = kwargs['arg2']
        stream_url = f"{SOSAC_API}serials/{_id}/into-queue?username={sosac_user}&password={sosac_passwordhash}"
        respse = requests.post(stream_url,data={})
        debug("stream_url %s"%stream_url,2)
        return
    elif stream == "off-queue" :
        _id = kwargs['arg2']
        stream_url = f"{SOSAC_API}serials/{_id}/off-queue?username={sosac_user}&password={sosac_passwordhash}"
        respse = requests.post(stream_url,data={})
        debug("stream_url %s"%stream_url,2)
        return

    elif "episodes" == episodes :
        _id = kwargs['arg2'] 
        if _id != "22" :
            stream_url = f"{SOSAC_API}episodes/{_id}?username={sosac_user}&password={sosac_passwordhash}"
        else :
            stream_url = f"{SOSAC_API}episodes/lists/{stream}?pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"


    else : 
        stream_url = f"{SOSAC_API}serials/lists/{stream}?pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"

    debug("stream_url %s"%stream_url,2)    
    return stream_url

def set_sosac_epi(sais_id) :
    sosac_passwordhash = passhash()
    sais_id = int(sais_id)
    stream_url = f"{SOSAC_API}serials/{sais_id}?username={sosac_user}&password={sosac_passwordhash}"
    debug("set_sosac_epi stream_url %s"%stream_url,2)
    return stream_url

def set_sosac_guide(day,page) :
    sosac_passwordhash = passhash()
    stream_url = f"{SOSAC_API}tv/program?d={day}&pocet=100&stranka={page}&username={sosac_user}&password={sosac_passwordhash}"
    debug("set_sosac_guide stream_url %s"%stream_url,2)
    return stream_url

def set_sosac_watchTime(type_id, stream_id, time_val) :
    sosac_passwordhash = passhash()
    time_val = int(time_val)
    data = {"time":int(time_val)}
    stream_url = f"{SOSAC_API}{type_id}/{stream_id}/watching-time?username={sosac_user}&password={sosac_passwordhash}"
    hdrs = {'Content-Type': 'application/json'}
    respse = requests.post(stream_url, json=data, headers=hdrs)
    debug("mark as watched time_val %s %s"%(time_val,stream_url),2)
    #debug("mark as watched repse %s"%respse.status_code,2)
    return

def get_title(dest) :
    not_name = dest.split("/")[-1]
    item_id = not_name.split("-")[0]
    link = set_sosac_info("id",**{'arg2':item_id}) if "movies" in dest else set_sosac_ser("",**{'arg2':item_id,'arg3':"episodes",'arg4':""})
    debug("downloadFil link %s"%link,2)
    source = requests.get(link).text
    data = json.loads(source)
    vid_title = data["n"]["cs"][0] if type(data["n"]["cs"]) == type([]) else data["n"]["cs"]
    if "movies" not in dest :
        epi_nb = str(data["ep"]) if len(str(data["ep"])) > 1 else "0" + str(data["ep"])
        sai_nb = str(data["s"]) if len(str(data["s"])) > 1 else "0" + str(data["s"])                    
        vid_title = f'{vid_title} {sai_nb}x{epi_nb}'
    return vid_title
    
