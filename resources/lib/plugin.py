# -*- coding: utf-8 -*-
import routing
import requests, re, json, sys, os, time, threading
import urllib.parse
from datetime import datetime as dt
from datetime import timedelta
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
from xbmcplugin import addDirectoryItem
from xbmcplugin import addDirectoryItems
from xbmcplugin import endOfDirectory
from xbmcplugin import setResolvedUrl
from xbmcgui import ListItem

from resources.lib import util
from resources.lib.util import *
from resources.lib.downThread import *
from . import subs
from resources.lib.player import *
from resources.lib.playerList import cPlayerList2

plugin = routing.Plugin()
dialog = xbmcgui.Dialog()
#################################################################################
hdrs = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
         
letter = ['0-9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


genre1 = ["action","adventure","animation","biography","cartoons","comedy","crime","disaster","documentary","drama","erotic",
  "experimental","fairytales","family","fantasy","history","horror","imax","krimi","music","mystery",
  "psychological","publicistic","realitytv","romance","sci-fi","sport","talkshow","thriller","war","western"]

genre = [translate(30296),translate(30297),translate(30298),translate(30299),translate(30300),translate(30301),translate(30302),translate(30303),translate(30304),translate(30305),translate(30306),\
  translate(30307),translate(30308),translate(30309),translate(30310),translate(30311),translate(30312),translate(30313),translate(30314),translate(30315),translate(30316),\
  translate(30317),translate(30318),translate(30319),translate(30320),translate(30321),translate(30322),translate(30323),translate(30324),translate(30325),translate(30326)]

qual_dic = {"UHD":"2160p","FHD":"1080p","HD":"720p","SD":"480p"}
qual_list = list(qual_dic.keys())

quality_list =["fhd","uhd","hd","sd","kinorip","tvrip"]

country_listt = [translate(30360), translate(30361), translate(30362), translate(30363), translate(30364), translate(30365), translate(30366),
        translate(30367), translate(30368), translate(30369), translate(30370), translate(30371), translate(30372), translate(30373),
        translate(30374), translate(30375), translate(30376), translate(30377), translate(30378), translate(30379), translate(30380),
        translate(30381), translate(30382), translate(30383), translate(30384), translate(30385), translate(30386), translate(30387),
        translate(30388), translate(30389)]

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

dub_list = [translate(30330), translate(30331), translate(30332),translate(30333),translate(30334),translate(30335),translate(30336),translate(30337),translate(30338),translate(30339),\
         translate(30340),translate(30341),translate(30342),translate(30343),translate(30344),translate(30345),translate(30346),translate(30347),translate(30348),translate(30349),translate(30359)]

countries = {
    'USA':"us",
     'Velká Británie':'uk',
     'Nový Zéland':'ve',
     'Kanada':'ca',
     'Německo':'ne',
     'Austrálie':'au',
     'Francie':'fr',
     'Japonsko':'jp',
     'Čína':'cn',
     'Hongkong':'hk'}

SORT_List = [translate(30350),translate(30350)+" "+ translate(30358),translate(30351),translate(30351)+" "+ translate(30358),translate(30352),translate(30352)+" "+ translate(30358),
             translate(30353),translate(30353)+" "+ translate(30358),translate(30354),translate(30354)+" "+ translate(30358),translate(30355),translate(30355)+" "+ translate(30358),
             translate(30356),translate(30356)+" "+ translate(30358),translate(30357)]

SORT_Lists = [translate(30350),translate(30350)+" "+ translate(30358),translate(30351),translate(30351)+" "+ translate(30358),translate(30352),
              translate(30352)+" "+ translate(30358),
             translate(30355),translate(30355)+" "+ translate(30358),translate(30356),translate(30356)+" "+ translate(30358),translate(30357)]


SORT_List1 = ['popularity', 'CSFD rating', 'IMDB rating', 'movie budget', 'movie revenue', 'alphabet', 'date added','best match']
#SORT_Lists = [translate(30350), translate(30351),translate(30352),translate(30355),translate(30356),translate(30357)]
SORT_Lists1 = ['popularity', 'CSFD rating', 'IMDB rating', 'alphabet', 'date added','best match']

SETTINGS = {"adv_sort":"14", "adv_keyword":"", "adv_director":"", "adv_writer":"",
            "adv_actor":"", "adv_from":"1900", "adv_to":"","adv_genre":"0", "adv_origin":"0",
            "adv_quality":translate(30329),"adv_lang":"0"}

SETTINGSs = {"adv_sorts":"10", "adv_keywords":"", "adv_directors":"", "adv_writers":"",
            "adv_actors":"", "adv_froms":"1900", "adv_tos":"","adv_genres":"0", "adv_origins":"0",
            "adv_qualitys":translate(30329),"adv_langs":"0"}

SOSAC_IMAGE = SOSAC_MOVIES
try :
        first_dubbing = DUBBING[first_dubbing]
        second_dubbing = DUBBING[second_dubbing]
        quality = re.findall('\d+p\((.*?)\)',quality)[0]
except :
        pass

stream_man = False
marge = "                                         "

#################################################################################
last_command0 = ""
last_command2 = ""

def get_url(url):
    r = requests.get(url, headers=hdrs).text
    return r

def get_links_mess(data) :
    if data['errormessage'] != 0 and addon.getSetting('get_links') == "true" :
        dialog.ok(translate(30390), data['errormessage'])
        addon.setSetting('get_links',"false")

@plugin.route('/check_streamujtv')
def check_streamujtv() :
    url = set_streamujtv_info("")
    debug("check_streamujtv url %s"%url,2)
    addon.setSetting('get_links',"true")
    if url == None: return
    source = get_url(url)
    data = json.loads(source)

    if data['result'] == 0 :
        dialog.ok(translate(30390), translate(30394))
    elif data['result'] == 1 :
        dialog.ok(translate(30390), translate(30393))
    elif data['result'] == 2 :
        dialog.ok(translate(30390), f"{translate(30392)} \n{data['expiration']}")

@plugin.route('/check_sosac')
def check_sosac() :
    url = sosachash()
    debug("check_sosac url %s"%url,2)
    if url == None : return
    source = get_url(url)
    if "401" in source : dialog.ok(translate(30398), translate(30396))
    else : dialog.ok(translate(30398), translate(30395))

def convert_num(numb) :
    if numb > 999999 :
        res = numb / 1000000
        return str(int(res)) +"mil"
    elif numb > 99999 :
        res = numb / 1000
        return str(int(res))+"tis" #kil"
    else : return str(numb) 

def save_key(fich_data,m_id,key1,key2,key3) :
    with open(fich_data, "r") as fdata :
        f_data = json.load(fdata)
        #f_data = json.loads(fdata.read())
    f_data[m_id] = [key1,key2,key3]
    with open(fich_data, "w") as fdata :
        json.dump(f_data, fdata, indent=4)
        #fdata.write(json.dumps(f_data))

################################################################################
def set_steam_details(item, li):
    li.setProperty('isplayable', 'true')

def set_common_properties(item, li, letype = ""):
    global SOSAC_IMAGE
    try :
        if letype == 'epi_tvguide' : img = item["i"]
        elif "ie" in item and letype != 'download' : img = item["ie"]
        else : img = item["i"] if  ((letype == "sai_prop") or (letype == "epi_prop") or ("i" in item)) else SOSAC_IMAGE + str(item["_id"]) + ".jpg"
        if ("defaultnis.jpg" in img) or (".png" in img) : img = SOSAC_IMAGE + str(item["_id"]) + ".jpg"
        fan_imf = item["b"] if "b" in item else ""
        li.setArt({
            'thumb': img,
            'fanart': fan_imf
        })       
        if letype == 'info' : return
    except Exception as e :
        debug("set_common_properties img error %s"%e, 2)
   
    try :
        info = {}
        info['plot'] = str(item["p"])
        info['dbid'] = item["_id"] if "_id" in item else 0
        info['genre'] = [" / ".join(item["g"])] if (("g" in item) and (len(item["g"]) >= 1)) else ""
        info['year'] = int(item["y"]) if "y" in item else ""
        info['votes'] = int(item["mp"]) if "mp" in item else 0 
        info['userrating'] = int(item["cp"])  if "cp" in item else 0  
        info['rating'] = float(item["c"])  if "c" in item else 0.0
        info['duration'] = item["dl"] 
        info['aired'] = item["r"] if "r" in item else ""
    except Exception as e :
        pass
        debug("set_common_properties info error %s"%e, 2)
    try :
        info['cast'] = [" , ".join(item["f"])] if (("f" in item) and (len(str(item["f"])) >= 1)) else [""]
    except Exception as e :
        debug("set_common_properties info cast ...  error %s"%e, 2)
    try :
        info['director'] = [" , ".join(item["s"])] if (("s" in item) and (len(str(item["s"])) >= 1)) else "" # item["s"] if "s" in item else ""
    except Exception as e :
        debug("set_common_properties info director ...  error %s"%e, 2)
    try :
        info['writer'] = [" , ".join(item["h"])] if (("h" in item) and (len(str(item["h"])) >= 1)) else "" #item["h"] if "h" in item else ""
    except Exception as e :
        debug("set_common_properties info writer ...  error %s"%e, 2)

    try :
        itemk = item["k"] if "k" in item else 0
        budgetv = convert_num(float(itemk))
        li.setProperty('budget',budgetv)
        setid = item["t"] if "t" in item else 0
        revenuev = convert_num(float(setid))
        li.setProperty('revenue',revenuev)
    except Exception as e :
        pass
        debug("set_common_properties info budet revenue error %s"%e, 2)

    li.setInfo('video', info)
    try :
        date_year = f'({item["y"]})' if ("y" in item and item["y"] != "" ) else ""
        li.setProperty('date-year',date_year) 
    except Exception as e :
        debug("set_common_properties year error %s"%e, 2)

    try :
        if not isNexus() :
            li.setProperty('ResumeTime',str(item["w"])) 
    except Exception as e :
        debug("set_common_properties ResumeTime error %s"%e, 2)

    try :
        info['country'] = item["o"] if "o" in item else ""
    except Exception as e :
        debug("set_common_properties country error %s"%e, 2)
    
    try :
        li.setProperty('season', str(item["z"])+translate(30277) if "z" in item else "")
        li.setProperty('episode', str(item["v"])+translate(30278) if "v" in item else "")
    except Exception as e :
        debug("set_common_properties season episode error %s"%e, 2)
    try :
        li.setProperty('dateadded', str(item["r"]) if "r" in item else "")
    except Exception as e :
        debug("set_common_properties dateadded error %s"%e, 2)

    try :
        imdbrating = float(item["m"]) if "m" in item else 0
        imdbv = int(item["mp"]) if "mp" in item else 0
        imdbvotes = convert_num(imdbv)
        li.setProperty('imdbrating', str(int(imdbrating)))
        li.setProperty('imdbvotes', str(imdbvotes))
        csfdrating = float(item["c"]) if "c" in item else 0
        csfdv = int(item["cp"]) if "cp" in item else 0
        csfdvotes = convert_num(csfdv)
        li.setProperty('csfdrating', str(int(csfdrating)))
        li.setProperty('csfdvotes', str(csfdvotes))
        li.setProperty('sounds', str(item["e"]) if "e" in item else "")
        li.setProperty('quality', str(item["q"]).upper() if "q" in item else "")
    except Exception as e :
        debug("set_common_properties info setProperty error %s"%e, 2)

    try :
        if letype == 'download' :
            itemcs = item["n"]["cs"][0] if type(item["n"]["cs"]) == type([]) else item["n"]["cs"]
            li.setProperty('tvshow_cs',itemcs)
            if "ie" in item : 
                itemie = item["ie"][0] if type(item["ie"]) == type([]) else item["ie"]
                #li.setProperty('tvshow_img',item["ie"])
            else : itemie = "http://kodi-api.sosac.to/obrazky/defaultniep.jpg"
            li.setProperty('tvshow_img',itemie)

            z = 0
            for i in item['n'] :
                if i != "cs" :
                    z += 1
                    country = i
                    img = f"special://home/addons/plugin.video.sosac-2/resources/images/languages/{i}.png"
                    li.setProperty('tvshowImg'+str(z), img)
                    itemi = item["n"][i][0] if type(item["n"][i]) == type([]) else item["n"][i]
                    li.setProperty('tvshowTit'+str(z),itemi)        
    except Exception as e :
        debug("set_common_properties download tit & img error %s"%e, 2)

    try :
        z = 0
        for i in item['n'] :
            if i != "cs" :
                z += 1
                title = item['n'][i][0] if type(item['n'][i]) == type([]) else item['n'][i]
                img = f"special://home/addons/plugin.video.sosac-2/resources/images/languages/{i}.png"
                li.setProperty('titre'+str(z), str(title))
                li.setProperty('image'+str(z), img)

        if letype == "download" :
            titlecs = item['ne']["cs"][0] if type(item['ne']["cs"][0]) == type([]) else item['ne']["cs"]
            titleus = item['ne']["en"][0] if type(item['ne']["en"][0]) == type([]) else item['ne']["en"]
            if "ep" in item :
                epi_nb = str(item["ep"]) if len(str(item["ep"])) > 1 else "0" + str(item["ep"])
                sai_nb = str(item["s"]) if len(str(item["ep"])) > 1 else "0" + str(item["s"])
                title = f'{sai_nb}x{epi_nb} - {titlecs}' 
                li.setProperty('titre_cs', str(title))
                title = f'{sai_nb}x{epi_nb} - {titleus}'                 
                li.setProperty('titre_us', str(title))

            else :
                li.setProperty('titre_cs', str(title))
                li.setProperty('titre_us', str(title))
            imgcs = f"special://home/addons/plugin.video.sosac-2/resources/images/languages/cs.png"
            li.setProperty('image_cs', imgcs)
            imgus = f"special://home/addons/plugin.video.sosac-2/resources/images/languages/us.png"
            li.setProperty('image_us', imgus)
    except Exception as e :
        debug("set_common_properties info titles langue error %s"%e, 2)

    try :
        z = 0
        if 'oi' in item : 
            for i in item['oi'] :
                z += 1
                country = i
                #flag = countries[i]
                img = f"special://home/addons/plugin.video.sosac-2/resources/images/countries/{i}.png"
                li.setProperty('flag'+str(z), img)
        else :
            img = ""
            li.setProperty('flag'+str(1), img)
    except Exception as e :
        debug("set_common_properties info flag error %s"%e, 2)

    try :
        lang_list1 = item["d"]
        lang_list = [xtem for xtem in lang_list1]
        langue = ""
        if "cz" in lang_list :
            langue = "CZ, "
            lang_list.remove("cz")
        if "sk" in lang_list :
            langue = langue + "SK, "
            lang_list.remove("sk")

        if len(lang_list) > 0 :
            for i in lang_list :
                if not "tit" in i :
                    langue = langue + i.upper() + ", "
                    lang_list.remove(i)

        if len(lang_list) > 0 :
            for i in lang_list1 :
                if "tit" in i and len(i.split("+")) >=2:
                    langue = langue + (i.split("+")[0]).upper() + " + " + (i.split("+")[1][:2]).upper() + " titulky, "
                    lang_list.remove(i)
                    if len(lang_list) == 0 : break
        langue = langue[:-2 ]if langue[-2] == "," else langue
        langue = f"[B]{langue}[/B]"
    except Exception as e :
        langue = ""
        debug("set_common_properties langue error %s"%e, 2)

    li.setProperty('langue',langue)

    
def show_plug_list(letype, epi_id, items, start=None, stat=None):
    global SOSAC_IMAGE
    if  not start  : start = stat = None
    debug("show_plug_list  sys.argv %s"%sys.argv, 2)
    if letype == "movies" :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        SOSAC_IMAGE = SOSAC_MOVIES
        queueMov = checkMyPlaylist("movies")
        for i, item in enumerate(items):
            try : 
                title = item["n"]["cs"] if epi_id != "ENGLISH" else item["n"]["en"]
                li = ListItem(str(title[0]))
                set_common_properties(item, li)
                set_steam_details(item, li)

                li.setInfo('video', {
                    'title': title,
                    'count': i,
                    'mediatype': 'movie'})
                try :
                    if float(item["w"]) > 0.8 * float(item["dl"]) : iconw = "done"
                    elif float(item["w"]) > 0.5 * float(item["dl"]) : iconw = "3quarters"
                    elif float(item["w"]) > 0.25 * float(item["dl"]) : iconw = "2quarters"
                    elif float(item["w"]) > 0.0  : iconw = "1quarter"
                    elif float(item["w"]) == 0.0 : iconw = "unseen"
                    li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                except Exception as e :
                    debug("set_common_properties country error %s"%e, 2)

                menu_list = []
                action = "RunPlugin(plugin://plugin.video.sosac-2/streammanu/movies/%s/%s)"%(item['_id'],item['l'])
                menu_list.append((translate(30286), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="movies",query1="into-queue",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if item["_id"] not in queueMov : menu_list.append((translate(30287), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="movies",query1="off-queue",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if item["_id"] in queueMov : menu_list.append((translate(30288), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="movies",query1="reset",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                menu_list.append((translate(30289), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="movies",query1=f'watched-{item["dl"]}',query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                menu_list.append((translate(30290), action)) #,replaceItems))
                action = "container.update(\"%s\")" % plugin.url_for(download,"movies",item["_id"],item["l"])
                menu_list.append((translate(30291), action))
                li.addContextMenuItems(menu_list)
                url = plugin.url_for(play, "movies", item["_id"], item["l"], [])
                addDirectoryItem(plugin.handle, url, li, False)

            except Exception as e :
                debug("show_plug_list movies error %s"%e, 2)

        quer, quer1, page = re.findall("query=(.*?)&.*?=(.*?)&.*?=(\d+)",sys.argv[2])[0] #.replace("?","").replace("&",",")
        debug("show_plug_list movies page %s %s %s"%(quer, quer1, page), 2)
        quer2 = int(page) + 1
        if quer == "search" : quer1 = start
        url = set_sosac_info(quer,**{'arg2':quer1,'arg3':quer2})
        source = get_url(url)
        res = json.loads(source)
        if len(res) != 0 :
            fonct_n1 = sys.argv[0].split("/")[-1]            
            url = plugin.url_for(categories, query=quer,query1=quer1,query2=quer2)
            addDirectoryItem(plugin.handle, url,ListItem(translate(30294)), True)

        endOfDirectory(plugin.handle)
        xbmc.sleep(100)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % "507")
        #xbmc.executebuiltin("Container.Refresh")

    elif letype == "serials" :
        SOSAC_IMAGE = SOSAC_SERIES
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        queueSer = checkMyPlaylist("serials")
        for i, item in enumerate(items):
            try :
                title = item["n"]["cs"][0]
                li = ListItem(str(title))
                set_common_properties(item, li)
                li.setInfo('video', {
                    'title': title,
                    'count': i,
                    'mediatype': 'tvshow'})
                menu_list = []
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="into-queue",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if item["_id"] not in queueSer : menu_list.append((translate(30287), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="off-queue",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if item["_id"] in queueSer : menu_list.append((translate(30288), action))
                action = "container.update(\"%s\")" % plugin.url_for(downserial, item["_id"])
                menu_list.append((translate(30291), action))
                li.addContextMenuItems(menu_list)
                url = plugin.url_for(cat_epi, query=item["_id"], query1 ="0", query2=None,query3=None)
                addDirectoryItem(plugin.handle, url, li, True)
            except Exception as e :
                debug("show_plug_list serials error %s"%e, 2)
                pass

        quer, quer1, quer2, quer3, page = re.findall("query=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(\d+)",sys.argv[2])[0] #.replace("?","").replace("&",",")
        debug("show_plug_list movies page %s %s %s"%(quer, quer1, page), 2)
        quer4 = int(page) + 1
        url = set_sosac_ser(quer,**{'arg2':quer1,'arg3':quer2,'arg4':quer3,'arg5':quer4})
        source = get_url(url)
        res = json.loads(source)
        if len(res) != 0 :
            fonct_n1 = sys.argv[0].split("/")[-1]
            
            url = plugin.url_for(cat_ser, query=quer,query1=quer1,query2=quer2,query3=quer3,query4=quer4)
            addDirectoryItem(plugin.handle, url,ListItem(translate(30294)), True)

        endOfDirectory(plugin.handle)
        xbmc.sleep(100)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % "507")
        #xbmc.executebuiltin("Container.Refresh")

    elif letype == "episodes" :
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        SOSAC_IMAGE = SOSAC_SERIES
        saison = list(items.keys())
        if (len(saison) == 2) and ( 'info' in saison ) :
            episodes = list(items[saison[0]].keys())            
            playList = []
            queueSer = checkMyPlaylist("serials")
            for i, item in enumerate(episodes) :
                x  = items[saison[0]][item]
                playList.append(x["_id"])                   
            for i, item in enumerate(episodes) :
                try :
                    x  = items[saison[0]][item]
                    epi_nb = str(item) if len(item) >1 else "0" + str(item)
                    title = f'01x{epi_nb} - {x["n"]["cs"]}'
                    li = ListItem(str(title))
                    set_common_properties(x, li, "epi_prop")
                    set_steam_details(item, li)
                    li.setInfo('video', {
                    'title': title,
                    'count': i,
                    'mediatype': 'movie'})
                    li.setArt({
                    'fanart': items["info"]["b"] if "b" in items["info"] else ""
                        })   
                    if start  :
                        li.setProperty('startime',start)
                        li.setProperty('station',stat)
                    try :
                        if float(x["w"]) > 0.8 * float(x["dl"]) : iconw = "done"
                        elif float(x["w"]) > 0.5 * float(x["dl"]) : iconw = "3quarters"
                        elif float(x["w"]) > 0.25 * float(x["dl"]) : iconw = "2quarters"
                        elif float(x["w"]) > 0.0  : iconw = "1quarter"
                        elif float(x["w"]) == 0.0 : iconw = "unseen"
                        li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                    except Exception as e :
                        debug("set_common_properties country error %s"%e, 2)
                        
                    if x["_id"] in playList : playList.remove(x["_id"])
                    menu_list = []
                    action = "RunPlugin(plugin://plugin.video.sosac-2/streammanu/episodes/%s/%s)"%(x['_id'],x['l']) 
                    menu_list.append((translate(30286), action))
                    action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="into-queue",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                    if x["_id"] not in queueSer : menu_list.append((translate(30287), action))
                    action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="off-queue",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                    if x["_id"] in queueSer : menu_list.append((translate(30288), action))
                    action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1="reset",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                    menu_list.append((translate(30289), action))
                    action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1=f'watched-{x["dl"]}',query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                    menu_list.append((translate(30290), action))
                    action = "container.update(\"%s\")" % plugin.url_for(download,"serials",x["_id"],x["l"])
                    menu_list.append((translate(30291), action))
                    li.addContextMenuItems(menu_list)                    
                    url = plugin.url_for(play, "episodes", x["_id"], x["l"],playList)
                    addDirectoryItem(plugin.handle, url, li, False)
                except Exception as e :
                    debug("show_plug_list 1 saison error %s"%e, 2)

            xbmc.executebuiltin("Container.SetViewMode(%s)" % "505")
            endOfDirectory(plugin.handle)
            #xbmc.executebuiltin("Container.Refresh")

        if (len(saison) > 2) and (int(epi_id) >= 1 ) :
            xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
            SOSAC_IMAGE = SOSAC_SERIES
            #episodes = list(items[saison[int(epi_id)]].keys()) # avant 07/10 int(epi_id)-1
            episodes = list(items[str(epi_id)].keys())
            debug("show_plug_list saison > 2  epi_id %s"%epi_id, 2)
            playList = []
            queueSer = checkMyPlaylist("serials")
            sai_nb = str(epi_id) if len(epi_id) > 1 else "0" + str(epi_id)                    
            for i, item in enumerate(episodes) :
                #x  = items[saison[int(epi_id)]][item] # avant 07/10 int(epi_id)-1
                x  = items[str(epi_id)][item]
                playList.append(x["_id"])                   

            for i, item in enumerate(episodes):
                try :
                    #x  = items[saison[int(epi_id)]][item] # avant 07/10 int(epi_id)-1
                    x  = items[str(epi_id)][item]
                    epi_nb = str(item) if len(item) > 1 else "0" + str(item)
                    title = f'{sai_nb}x{epi_nb} - {x["n"]["cs"]}'
                    li = ListItem(str(title))
                    set_common_properties(x, li, "epi_prop")
                    set_steam_details(item, li)
                    li.setInfo('video', {
                    'title': title,
                    'count': i,
                    'mediatype': 'video'})
                    li.setArt({
                    'fanart': items["info"]["b"] if "b" in items["info"] else ""
                        })   

                    if start  :
                        li.setProperty('startime',start)
                        li.setProperty('station',stat)
                    try :
                        if float(x["w"]) > 0.8 * float(x["dl"]) : iconw = "done"
                        elif float(x["w"]) > 0.5 * float(x["dl"]) : iconw = "3quarters"
                        elif float(x["w"]) > 0.25 * float(x["dl"]) : iconw = "2quarters"
                        elif float(x["w"]) > 0.0  : iconw = "1quarter"
                        elif float(x["w"]) == 0.0 : iconw = "unseen"
                        li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                    except Exception as e :
                        debug("set_common_properties country error %s"%e, 2)

                    if x["_id"] in playList : playList.remove(x["_id"])
                    menu_list = []
                    action = "RunPlugin(plugin://plugin.video.sosac-2/streammanu/episodes/%s/%s)"%(x['_id'],x['l']) 
                    menu_list.append((translate(30286), action))
                    action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="into-queue",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                    if x["_id"] not in queueSer : menu_list.append((translate(30287), action))
                    action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="off-queue",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                    if x["_id"] in queueSer : menu_list.append((translate(30288), action))
                    action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1="reset",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                    menu_list.append((translate(30289), action))
                    action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1=f'watched-{x["dl"]}',query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                    menu_list.append((translate(30290), action))
                    action = "container.update(\"%s\")" % plugin.url_for(download,"serials",x["_id"],x["l"])
                    menu_list.append((translate(30291), action))
                    li.addContextMenuItems(menu_list)
                    url = plugin.url_for(play, "episodes", x["_id"], x["l"], playList)
                    addDirectoryItem(plugin.handle, url, li, False)
                except Exception as e :
                    debug("show_plug_list saison & episodes error %s"%e, 2)

            xbmc.executebuiltin("Container.SetViewMode(%s)" % "CWideList")
            endOfDirectory(plugin.handle)
            #xbmc.executebuiltin("Container.Refresh")
            
        elif len(saison) > 2 :
            SOSAC_IMAGE = SOSAC_SERIES
            xbmcplugin.setContent(int(sys.argv[1]), 'seasons')
            xinfo  = items['info']
            debug("show_plug_list saison >2 ", 2)
            for ind, item in enumerate(items):
                try :
                    #if ind + 1  == len(saison) : continue
                    if item  == "info" : continue
                    title = xinfo["n"]["cs"]
                    debug("set_common_properties season title  %s "%(title), 2)
                    li = ListItem(str(title[0]))
                    saititle = translate(30283)+ " " + item #str(ind+1)
                    saititle1 = "Season " + item #str(ind+1)
                    li.setProperty('saititle',saititle)
                    set_common_properties(items['info'], li, "epi_prop")
                    if start  :
                        li.setProperty('startime',start)
                        li.setProperty('station',stat)
                        debug("show_plug_list saison>2 start %s"%start, 2)
                        debug("show_plug_list saison>2 stat  %s"%stat, 2)
                    done = quarters3 = quarters2 = quarter1 = N0 = 0
                    try :
                        epi_num = 0
                        dl_list = []
                        for y, z  in enumerate(items[item]) :
                            dl_list.append(items[item][z]["_id"])
                            if y == 0 :
                                li.setInfo('video', {
                                    'duration': items[item][z]["dl"]})
                                li.setProperty('dateadded' ,items[item][z]["r"])
                                first_item = items[item][z]["l"]
                                
                            if "w" in items[item][z]:
                                epi_num += 1
                                if float(items[item][z]["w"]) > 0.8 * float(items[item][z]["dl"]) : done += 1
                                elif float(items[item][z]["w"]) > 0.5 * float(items[item][z]["dl"]) : quarters3 += 1
                                elif float(items[item][z]["w"]) > 0.25 * float(items[item][z]["dl"]) : quarters2 += 1
                                elif float(items[item][z]["w"]) > 0.0  : quarter1 += 1
                                elif float(items[item][z]["w"]) == 0.0 : N0 += 1
                        
                        if N0 == epi_num : iconw = "unseen"
                        else :
                            if float(done / epi_num) > 0.8  : iconw = "done"
                            elif float(done / epi_num) > 0.5 : iconw = "3quarters"
                            elif float(done / epi_num) > 0.25 : iconw = "2quarters"
                            elif float(done / epi_num) > 0.0  : iconw = "1quarter"
                            elif (quarter1 > 0) or  (quarters2 > 0) or (quarters3 > 0) : iconw = "1quarter"
                            elif done == 0 : iconw = "unseen"

                        li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                    except Exception as e :
                        debug("set_common_properties season watched error %s"%e, 2)

                    
                    #if ind + 1 != len(saison) :
                    if item  != "info" :
                        try :
                            debug("saison langue item %s"%items[item], 2)
                            lang_list1 = items[item]["1"]["d"]
                            debug("saison langue  %s"%lang_list1, 2)
                            lang_list = [xtem for xtem in lang_list1]
                            langue = ""
                            if "cz" in lang_list :
                                langue = "CZ, "
                                lang_list.remove("cz")
                            if "sk" in lang_list :
                                langue = langue + "SK, "
                                lang_list.remove("sk")

                            if len(lang_list) > 0 :
                                for item_i in lang_list :
                                    if not "tit" in item_i :
                                        langue = langue + item_i.upper() + ", "
                                        lang_list.remove(item_i)

                            if len(lang_list) > 0 :
                               for item_i in lang_list1 :
                                    if "tit" in item_i and len(item_i.split("+")) >=2:
                                        langue = langue + (item_i.split("+")[0]).upper() + " + " + (item_i.split("+")[1][:2]).upper() + " titulky, "
                                        lang_list.remove(item_i)
                                        if len(lang_list) == 0 : break
                            langue = langue[:-2 ]if langue[-2] == "," else langue
                            langue = f"[B]{langue}[/B]"
                        except Exception as e :
                            langue = ""
                            debug("set_common_properties langue error %s"%e, 2)

                        li.setProperty('langue',langue)
                    
                    action = "container.update(\"%s\")" % plugin.url_for(downsais, xinfo["_id"],f"{title[0]} - {saititle1}",dl_list)
                    li.addContextMenuItems([(translate(30291), action)])
                    debug("show_plug_list saison  %s"%item, 2)
                    #url = plugin.url_for(cat_epi, query = xinfo["_id"], query1=str(ind +1),query2=start,query3=stat)
                    url = plugin.url_for(cat_epi, query = xinfo["_id"], query1=item,query2=start,query3=stat)
                    addDirectoryItem(plugin.handle, url, li, True)
                except Exception as e :
                    debug("show_plug_list saison error %s"%e, 2)

            xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)     
            xbmc.executebuiltin("Container.SetViewMode(%s)" % "507")
            endOfDirectory(plugin.handle)
            #xbmc.executebuiltin("Container.Refresh")

    elif letype == "episodes2" :
        SOSAC_IMAGE = SOSAC_SERIES
        '''
        if epi_id == "2" :
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        else  : xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        '''
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        queueSer = checkMyPlaylist("serials")
        for i, item in enumerate(items):
            try :
                if epi_id == "2" :
                    title = item["n"]["cs"]
                else :                        
                    title = item["n"]["cs"] + " -- " + item["ne"]["cs"] if "ne" in item else item["n"]["cs"]

                if "ep" in item :
                    epi_nb = str(item["ep"]) if len(str(item["ep"])) > 1 else "0" + str(item["ep"])
                    sai_nb = str(item["s"]) if len(str(item["s"])) > 1 else "0" + str(item["s"])
                    title1 = f'{sai_nb}x{epi_nb}' 
                    li = ListItem(f"[B]{title}[/B] - {str(title1)}")
                else :
                    li = ListItem(str(title))
                #set_common_properties(item, li)
                if epi_id == "2" : set_common_properties(item, li, letype = "download")
                else : set_common_properties(item, li)
                set_steam_details(item, li)
                li.setInfo('video', {
                    'title': title,
                    'count': i,
                    'mediatype': 'video'})

                if item["l"] == None :
                    li.setProperty("not_yet",translate(30276))
                    
                try :
                    if float(item["w"]) > 0.8 * float(item["dl"]) : iconw = "done"
                    elif float(item["w"]) > 0.5 * float(item["dl"]) : iconw = "3quarters"
                    elif float(item["w"]) > 0.25 * float(item["dl"]) : iconw = "2quarters"
                    elif float(item["w"]) > 0.0  : iconw = "1quarter"
                    elif float(item["w"]) == 0.0 : iconw = "unseen"
                    li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                except Exception as e :
                    debug("show_plug_list episodes2 watched error %s"%e, 2)

                menu_list = []
                action = "RunPlugin(plugin://plugin.video.sosac-2/streammanu/episodes/%s/%s)"%(item['_id'],item['l']) 
                menu_list.append((translate(30286), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="into-queue",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if item["_id"] not in queueSer : menu_list.append((translate(30287), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="off-queue",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if item["_id"] in queueSer : menu_list.append((translate(30288), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1="reset",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                menu_list.append((translate(30289), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1=f'watched-{item["dl"]}',query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                menu_list.append((translate(30290), action))
                action = "container.update(\"%s\")" % plugin.url_for(download,"serials",item["_id"],item["l"])
                menu_list.append((translate(30291), action))
                li.addContextMenuItems(menu_list)                
                url = plugin.url_for(play, "episodes", item["_id"], item["l"] if item["l"] != None else "", [])
                addDirectoryItem(plugin.handle, url, li, False)
            except Exception as e :
                debug("show_plug_list episodes2 error %s"%e, 2)

              
        quer, quer1, quer2, quer3, page = re.findall("query=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(\d+)",sys.argv[2])[0] #.replace("?","").replace("&",",")
        if epi_id == "1" :
            quer1=start
            quer2=stat    
        debug("show_plug_list episodes2 page %s %s %s"%(quer, quer1, page), 2)
        quer4 = int(page) + 1
        url = set_sosac_ser(quer,**{'arg2':quer1,'arg3':quer2,'arg4':quer3,'arg5':quer4})
        source = get_url(url)
        res = json.loads(source)
        if len(res) != 0 :
            url = plugin.url_for(cat_ser, query=quer,query1=quer1,query2=quer2,query3=quer3,query4=quer4)
            addDirectoryItem(plugin.handle, url,ListItem(translate(30294)), True)
        
        #if epi_id == "2" : xbmc.executebuiltin("Container.SetViewMode(%s)" % "506")
        #else : xbmc.executebuiltin("Container.SetViewMode(%s)" % "505")
        #xbmc.executebuiltin("Container.SetViewMode(%s)" % "505")
        endOfDirectory(plugin.handle)
        xbmc.sleep(100)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % "505")
        #xbmc.executebuiltin("Container.Refresh")


    elif letype == "episodes3" :
        SOSAC_IMAGE = SOSAC_SERIES
        '''
        if epi_id == "2" :
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        else  : xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        '''
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        queueSer = checkMyPlaylist("serials")
        for i, item in enumerate(items):
            try :
                if epi_id == "2" :
                    title = item["n"]["cs"]
                else :                        
                    title = item["n"]["cs"] + " -- " + item["ne"]["cs"] if "ne" in item else item["n"]["cs"]

                if "ep" in item :
                    epi_nb = str(item["ep"]) if len(str(item["ep"])) > 1 else "0" + str(item["ep"])
                    sai_nb = str(item["s"]) if len(str(item["s"])) > 1 else "0" + str(item["s"])
                    title1 = f'{sai_nb}x{epi_nb}' 
                    li = ListItem(f"[B]{title}[/B] - {str(title1)}")
                else :
                    li = ListItem(str(title))
                #set_common_properties(item, li)
                if epi_id == "2" : set_common_properties(item, li, letype = "download")
                else : set_common_properties(item, li)
                set_steam_details(item, li)
                li.setInfo('video', {
                    'title': title,
                    'count': i,
                    'mediatype': 'video'})

                if item["l"] == None :
                    li.setProperty("not_yet",translate(30276))
                    
                try :
                    if float(item["w"]) > 0.8 * float(item["dl"]) : iconw = "done"
                    elif float(item["w"]) > 0.5 * float(item["dl"]) : iconw = "3quarters"
                    elif float(item["w"]) > 0.25 * float(item["dl"]) : iconw = "2quarters"
                    elif float(item["w"]) > 0.0  : iconw = "1quarter"
                    elif float(item["w"]) == 0.0 : iconw = "unseen"
                    li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                except Exception as e :
                    debug("show_plug_list episodes2 watched error %s"%e, 2)

                menu_list = []
                action = "RunPlugin(plugin://plugin.video.sosac-2/streammanu/episodes/%s/%s)"%(item['_id'],item['l']) 
                menu_list.append((translate(30286), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="into-queue",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if item["_id"] not in queueSer : menu_list.append((translate(30287), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="off-queue",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if item["_id"] in queueSer : menu_list.append((translate(30288), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1="reset",query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                menu_list.append((translate(30289), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1=f'watched-{item["dl"]}',query2=item["_id"],query3=sys.argv[0],query4=sys.argv[2])
                menu_list.append((translate(30290), action))
                action = "container.update(\"%s\")" % plugin.url_for(download,"serials",item["_id"],item["l"])
                menu_list.append((translate(30291), action))
                li.addContextMenuItems(menu_list)                
                url = plugin.url_for(play, "episodes", item["_id"], item["l"] if item["l"] != None else "", [])
                addDirectoryItem(plugin.handle, url, li, False)
            except Exception as e :
                debug("show_plug_list episodes2 error %s"%e, 2)

              
        quer, quer1, quer2, quer3, page = re.findall("query=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(\d+)",sys.argv[2])[0] #.replace("?","").replace("&",",")
        if epi_id == "1" :
            quer1=start
            quer2=stat    
        debug("show_plug_list episodes2 page %s %s %s"%(quer, quer1, page), 2)
        quer4 = int(page) + 1
        url = set_sosac_ser(quer,**{'arg2':quer1,'arg3':quer2,'arg4':quer3,'arg5':quer4})
        source = get_url(url)
        res = json.loads(source)
        if len(res) != 0 :
            url = plugin.url_for(cat_ser, query=quer,query1=quer1,query2=quer2,query3=quer3,query4=quer4)
            addDirectoryItem(plugin.handle, url,ListItem(translate(30294)), True)
        
        #if epi_id == "2" : xbmc.executebuiltin("Container.SetViewMode(%s)" % "506")
        #else : xbmc.executebuiltin("Container.SetViewMode(%s)" % "505")
        #xbmc.executebuiltin("Container.SetViewMode(%s)" % "506")
        endOfDirectory(plugin.handle)
        xbmc.sleep(100)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % "506")
        #xbmc.executebuiltin("Container.Refresh")

    elif letype == "epi_tvguide" :
        SOSAC_IMAGE = SOSAC_SERIES
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')        
        queueSer = checkMyPlaylist("serials")
        saison = list(items.keys())
        episodes = list(items[str(epi_id)].keys()) #list(items[saison[int(epi_id)-1]].keys())
        debug("show_plug_list epi_tvguide epi_id %s"%epi_id, 2)

        playList = []
        queueSer = checkMyPlaylist("serials")
        for i, item in enumerate(episodes) :
            x  = items[str(epi_id)][item] #items[saison[int(epi_id)-1]][item]
            debug("show_plug_list epi_tvguide x %s"%x, 2)
            playList.append(x["_id"])                   

        for i, item in enumerate(episodes):
            try :
                x  = items[str(epi_id)][item] #items[saison[int(epi_id)-1]][item]
                epi_nb = str(item) if len(item) > 1 else "0" + str(item)
                sai_nb = str(epi_id) if len(epi_id) > 1 else "0" + str(epi_id)                    
                title = f'{sai_nb}x{epi_nb} - {x["n"]["cs"]}'
                li = ListItem(str(title))
                #set_common_properties(item, li)
                
                set_common_properties(x, li, letype = "download")
                li.setProperty("startime",start)
                li.setProperty("station",stat)
                li.setProperty("type","episode")

                set_steam_details(x, li)
                li.setInfo('video', {
                    'title': title,
                    'count': i,
                    'mediatype': 'video'})
                try :
                    if float(x["w"]) > 0.8 * float(x["dl"]) : iconw = "done"
                    elif float(x["w"]) > 0.5 * float(x["dl"]) : iconw = "3quarters"
                    elif float(x["w"]) > 0.25 * float(x["dl"]) : iconw = "2quarters"
                    elif float(x["w"]) > 0.0  : iconw = "1quarter"
                    elif float(x["w"]) == 0.0 : iconw = "unseen"
                    li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                except Exception as e :
                    debug("show_plug_list epi_tvguide watched error %s"%e, 2)

                menu_list = []
                action = "RunPlugin(plugin://plugin.video.sosac-2/streammanu/episodes/%s/%s)"%(x['_id'],x['l']) 
                menu_list.append(("Choose stream manually", action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="into-queue",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if x["_id"] not in queueSer : menu_list.append((translate(30287), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="serials",query1="off-queue",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                if x["_id"] in queueSer : menu_list.append((translate(30288), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1="reset",query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                menu_list.append((translate(30289), action))
                action = "container.update(\"%s\")" % plugin.url_for(playlist,query="episodes",query1=f'watched-{x["dl"]}',query2=x["_id"],query3=sys.argv[0],query4=sys.argv[2])
                menu_list.append((translate(30290), action))
                action = "container.update(\"%s\")" % plugin.url_for(download,"serials",x["_id"],x["l"])
                menu_list.append((translate(30291), action))
                li.addContextMenuItems(menu_list)                
                url = plugin.url_for(play, "episodes", x["_id"], x["l"], playList)
                addDirectoryItem(plugin.handle, url, li, False)
            except Exception as e :
                debug("show_plug_list epi_tvguide error %s"%e, 2)
        '''
        fonct_n1 = sys.argv[0].split("/")[-1]
        if fonct_n1== "tvguidelist" : page = 1  #sys.argv[2])[0] #.replace("?","").replace("&",",")
        else : page = 1
        debug("epi_tvguide  page %s"%(page), 2)
        quer4 = int(page) + 1
        day = addon.getSetting("tvguide")
        url = set_sosac_guide(day,page)
        source = get_url(url)
        res = json.loads(source)
        debug("epi_tvguide  len(res) %s"%len(res), 2) 
        if len(res) != 0 :
            fonct_n1 = sys.argv[0].split("/")[-1]            
            url = plugin.url_for(tvg_list, day,quer4)
            debug("epi_tvguide  url %s"%url, 2)
            addDirectoryItem(plugin.handle, url,ListItem(translate(30294)), True)
        '''
        xbmc.executebuiltin("Container.SetViewMode(%s)" % "506")
        endOfDirectory(plugin.handle)

    elif letype == "download" :
        SOSAC_IMAGE = SOSAC_SERIES
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        if epi_id == "serials" :
            debug("show_plug_list download dir start %s"%start, 2) 
            dir_list , fil_list = xbmcvfs.listdir(start)
            debug("show_plug_list download dir dir_list %s"%dir_list, 2) 
            debug("show_plug_list download dir fil_list %s"%fil_list, 2) 
            for x in dir_list :
                x_id = x.split("_")[-1]
                item = items[x_id]                
                li = ListItem(str(x.split("_")[0]))
                               
                try :
                    if type(item["n"]["cs"]) == type([]) :
                        title = item["n"]["cs"][0] + " -- " + item["ne"]["cs"] if "ne" in item else item["n"]["cs"][0]
                    else  :
                        title = item["n"]["cs"] + " -- " + item["ne"]["cs"] if "ne" in item else item["n"]["cs"]

                    li = ListItem(str(title))
                except Exception as e :
                    debug("show_plug_list download dir listerror %s"%e, 2)                    
                set_common_properties(item, li, letype = "download")
                if ("Season" not in x) and ("1saison" not in x) :
                    debug("show_plug_list download tvshows x %s"%x, 2) 
                    url = plugin.url_for(downloaded,"tvshows",x)
                    addDirectoryItem(plugin.handle, url, li, True)
                else :                    
                    debug("show_plug_list download serials x %s"%x, 2) 
                    url = plugin.url_for(downloaded,"serials",x)
                    addDirectoryItem(plugin.handle, url, li, True)

            for i, x in enumerate(items):
                item = items[x]
                try :
                    title = item["n"]["cs"] + " -- " + item["ne"]["cs"] if "ne" in item else item["n"]["cs"]
                    if "ep" in item :
                        epi_nb = str(item["ep"]) if item["ep"] > 9 else "0" + str(item["ep"])
                        sai_nb = str(item["s"]) if item["s"] > 9 else "0" + str(item["s"])                
                        title1 = f'{sai_nb}x{epi_nb}'
                        title = title + " - "+ title1
                    li = ListItem(str(title))
                    set_common_properties(item, li, letype = "download")
                    set_steam_details(item, li)
                    li.setInfo('video', {
                        'title': title,
                        'count': i,
                        'mediatype': 'video'})
                    try :
                        if float(item["w"]) > 0.8 * float(item["dl"]) : iconw = "done"
                        elif float(item["w"]) > 0.5 * float(item["dl"]) : iconw = "3quarters"
                        elif float(item["w"]) > 0.25 * float(item["dl"]) : iconw = "2quarters"
                        elif float(item["w"]) > 0.0  : iconw = "1quarter"
                        elif float(item["w"]) == 0.0 : iconw = "unseen"
                        li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                    except Exception as e :
                        debug("set_common_properties download watched error %s"%e, 2)

                    menu_list = []
                    action = "container.update(\"%s\")" % plugin.url_for(downloaddel,query="serials",query1=str(item["_id"]),query2=str(item["name2"]))
                    menu_list.append((translate(30293), action))
                    li.addContextMenuItems(menu_list)
                    url = plugin.url_for(downloadPlay, query="serials", query1=str(item["_id"]), query2=str(item["name2"]))
                    addDirectoryItem(plugin.handle, url, li, False)
                except Exception as e :
                    debug("show_plug_list donwload error %s"%e, 2)
                    
            xbmc.executebuiltin("Container.SetViewMode(%s)" % "506")
            endOfDirectory(plugin.handle)

        if epi_id == "tvshows" :
            dir_list , fil_list = xbmcvfs.listdir(start)
            debug("show_plug_list download dir start %s"%start, 2) 
            debug("show_plug_list download dir dir_list %s"%dir_list, 2) 
            debug("show_plug_list download dir fil_list %s"%fil_list, 2) 
            for x in dir_list :
                x_id = x.split("_")[-1]
                item = items[x_id]                
                li = ListItem(str(x.split("_")[0]))
                               
                try :
                    set_common_properties(item, li, letype = "download")
                except Exception as e :
                    debug("show_plug_list download dir listerror %s"%e, 2)
                start_pre = start.split("\\")[-1]
                if "Season" not in x :                   
                    url = plugin.url_for(downloaded,"serials",start_pre+"+"+x)
                    addDirectoryItem(plugin.handle, url, li, True)
                else :                    
                    url = plugin.url_for(downloaded,"serials",start_pre+"+"+x)
                    addDirectoryItem(plugin.handle, url, li, True)                                
            xbmc.executebuiltin("Container.SetViewMode(%s)" % "506")
            endOfDirectory(plugin.handle)
            #xbmc.executebuiltin("Container.Refresh")

        elif epi_id == "movies" :
            for i, x in enumerate(items):
                item = items[x]               
                title = ""
                try :
                    if type(item["n"]["cs"]) == type([]) :
                        for tit_item in item["n"]["cs"] :
                            if  title == "" : title =  title + tit_item #x["movie"]["n"]["cs"][tit_item]
                            else : title = title +  " - " + tit_item
                
                    else : title = item["n"]["cs"]
                    li = ListItem(str(title))
                    set_common_properties(item, li, letype = "download")
                    set_steam_details(item, li)
                    li.setInfo('video', {
                        'title': title,
                        'count': i,
                        'mediatype': 'video'})
                    try :
                        if float(item["w"]) > 0.8 * float(item["dl"]) : iconw = "done"
                        elif float(item["w"]) > 0.5 * float(item["dl"]) : iconw = "3quarters"
                        elif float(item["w"]) > 0.25 * float(item["dl"]) : iconw = "2quarters"
                        elif float(item["w"]) > 0.0  : iconw = "1quarter"
                        elif float(item["w"]) == 0.0 : iconw = "unseen"
                        li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                    except Exception as e :
                        debug("set_common_properties download watched error %s"%e, 2)

                    menu_list = []
                    action = "container.update(\"%s\")" % plugin.url_for(downloaddel,query="movies",query1=str(item["_id"]),query2=str(item["name2"]))
                    menu_list.append((translate(30293), action))
                    li.addContextMenuItems(menu_list)
                    url = plugin.url_for(downloadPlay, query="movies", query1=str(item["_id"]), query2=str(item["name2"]))
                    addDirectoryItem(plugin.handle, url, li, False)
                except Exception as e :
                    debug("show_plug_list donwload error %s"%e, 2)

            xbmc.executebuiltin("Container.SetViewMode(%s)" % "507")
            endOfDirectory(plugin.handle)

    elif letype == "tvguide" :
        SOSAC_IMAGE = SOSAC_SERIES
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        debug("tv-guide items %s"%items, 2)
        for i, x in enumerate(items):
            startime = x["start"]
            a = dt.fromtimestamp(int(startime))
            startime = a.strftime("%H:%M")
            try :
                if x["movie"]  :
                    title = ""
                    debug(" tvguide %s"%x["movie"]["n"]["cs"],2)
                    if type(x["movie"]["n"]["cs"]) == type([]) :
                        for tit_item in x["movie"]["n"]["cs"] :
                            if  title == "" : title =  title + tit_item #x["movie"]["n"]["cs"][tit_item]
                            else : title = title +  " - " + tit_item
                    else : title = x["movie"]["n"]["cs"]
                    li = ListItem(str(title))
                    li.setProperty("startime",startime)
                    li.setProperty("type","movie")
                    li.setProperty("station", x["stanice"])
                    li.setInfo('video', {
                        'title': title,
                        'count': i,
                        'mediatype': 'video'})

                    set_steam_details(x["movie"], li)
                    set_common_properties(x["movie"], li)
                    item = x["movie"]
                    try :
                        if float(item["w"]) > 0.8 * float(item["dl"]) : iconw = "done"
                        elif float(item["w"]) > 0.5 * float(item["dl"]) : iconw = "3quarters"
                        elif float(item["w"]) > 0.25 * float(item["dl"]) : iconw = "2quarters"
                        elif float(item["w"]) > 0.0  : iconw = "1quarter"
                        elif float(item["w"]) == 0.0 : iconw = "unseen"
                        li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                    except Exception as e :
                        debug("set_common_properties tv-guide movie watched error %s"%e, 2)

                    url = plugin.url_for(play, "movies", item["_id"], item["l"], [])
                    addDirectoryItem(plugin.handle, url, li, False)                         

                elif x["serial"] and  x["episode"] :
                    try :
                        epi_nb = str(x["episode"]["ep"]) if len(str(x["episode"]["ep"])) > 1 else "0" + str(x["episode"]["ep"])
                        sai_nb = str(x["episode"]["s"]) if len(str(x["episode"]["s"])) > 1 else "0" + str(x["episode"]["s"])                    
                        title = f'{x["episode"]["n"]["cs"]} {sai_nb}x{epi_nb} - {x["episode"]["ne"]["cs"]}'
                    except Exception as e :
                        debug('show_plug_list tvguide x["serial"] and  x["episode"] error %s'%e, 2)
                        title = f'{x["episode"]["n"]["cs"]} {x["episode"]["ne"]["cs"]}'

                    li = ListItem(str(title))
                    li.setProperty("startime",f"[B]{startime}[/B]")
                    li.setProperty("station",x["stanice"])
                    li.setProperty("type","episode")
                    li.setInfo('video', {
                        'title': title,
                        'count': i,
                        'mediatype': 'episode'})              
                
                    set_common_properties(x["episode"], li, letype="epi_tvguide")
                    item = x["episode"]
                    set_steam_details(item, li)
                    try :
                        if float(item["w"]) > 0.8 * float(item["dl"]) : iconw = "done"
                        elif float(item["w"]) > 0.5 * float(item["dl"]) : iconw = "3quarters"
                        elif float(item["w"]) > 0.25 * float(item["dl"]) : iconw = "2quarters"
                        elif float(item["w"]) > 0.0  : iconw = "1quarter"
                        elif float(item["w"]) == 0.0 : iconw = "unseen"
                        li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                    except Exception as e :
                        debug("show_plug_list tvguide episode watched error %s"%e, 2)

                    url = plugin.url_for(play, "episodes", item["_id"], item["l"], [])
                    addDirectoryItem(plugin.handle, url, li, False)

                elif x["serial"] and not x["episode"] :
                    title = ""
                    if type(x["serial"]["n"]["cs"]) == type([]) :
                        for tit_item in x["serial"]["n"]["cs"] :
                            if  title == "" : title = title + tit_item
                            else : title = title +  " - " + tit_item
                    else : title = x["serial"]["n"]["cs"]
                    li = ListItem(str(title))
                    li.setProperty("startime",startime)
                    li.setProperty("station",x["stanice"])
                    li.setProperty("type","serial")
                    li.setInfo('video', {
                        'title': title,
                        'count': i,
                        'mediatype': 'tvshow'})              
                
                    set_common_properties(x["serial"], li)
                    
                    item = x["serial"]
                    try :
                        if float(item["w"]) > 0.8 * float(item["dl"]) : iconw = "done"
                        elif float(item["w"]) > 0.5 * float(item["dl"]) : iconw = "3quarters"
                        elif float(item["w"]) > 0.25 * float(item["dl"]) : iconw = "2quarters"
                        elif float(item["w"]) > 0.0  : iconw = "1quarter"
                        elif float(item["w"]) == 0.0 : iconw = "unseen"
                        li.setProperty('watched',f"special://home/addons/plugin.video.sosac-2/resources/images/{iconw}.png")
                    except Exception as e :
                        debug("set_common_properties tvguide serial watched error %s"%e, 2)

                    url = plugin.url_for(cat_epi, query=item["_id"], query1="0",query2=startime,query3=x["stanice"])
                    addDirectoryItem(plugin.handle, url, li, True)

            except Exception as e :
                debug("show_plug_list tvguide error %s"%e, 2)

        fonct_n1 = sys.argv[0].split("/")[-3]
        if fonct_n1 == "tvg_list" : page =sys.argv[0].split("/")[-1]  #sys.argv[2])[0] #.replace("?","").replace("&",",")
        else : page = 1
        debug("epi_tvguide  page %s"%(page), 2)
        quer4 = int(page) + 1
        day = addon.getSetting("tvguide")
        url = set_sosac_guide(day,page)
        source = get_url(url)
        res = json.loads(source)
        debug("epi_tvguide  len(res) %s"%len(res), 2) 
        if len(res) != 0 :
            fonct_n1 = sys.argv[0].split("/")[-1]            
            url = plugin.url_for(tvg_list, day,quer4)
            debug("epi_tvguide  url %s"%url, 2)
            addDirectoryItem(plugin.handle, url,ListItem(translate(30294)), True)

        endOfDirectory(plugin.handle)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % "507")

@plugin.route('/')
def index():
    source = get_url(domain_actif)
    data = json.loads(source)
    debug("index  data %s"%data, 2)
    news_data = data["news"] if (data["news"] != "") else ""
    items = []
    listItem = ListItem(translate(30000))
    listItem.setProperty("infomenu",news_data)
    if news_data == ""  : listItem.setProperty("infomenu",translate(30100))
    listItem.setArt({'icon': get_icon("movies.png")}) 
    items.append((plugin.url_for(movies), listItem, True))
    listItem = ListItem(translate(30001))
    listItem.setProperty("infomenu",news_data)
    if news_data == ""  : listItem.setProperty("infomenu",translate(30101))
    listItem.setArt({'icon': 'DefaultTVShows.png'})
    items.append((plugin.url_for(tvshows), listItem, True))
    listItem = ListItem(translate(30002))
    listItem.setProperty("infomenu",news_data)
    if news_data == ""  : listItem.setProperty("infomenu",translate(30102))
    listItem.setArt({'icon': get_icon("tvguide.png")})
    items.append((plugin.url_for(tvguide,query ="1"), listItem, True))
    listItem = ListItem(translate(30003))
    listItem.setProperty("infomenu",news_data)
    if news_data == ""  : listItem.setProperty("infomenu",translate(30103))
    listItem.setArt({'icon': 'DefaultAddonsSearch.png'})
    items.append((plugin.url_for(gensearch), listItem, True))
    listItem = ListItem(translate(30004))
    listItem.setProperty("infomenu",news_data)
    if news_data == ""  : listItem.setProperty("infomenu",translate(30104))
    listItem.setArt({'icon': get_icon("settings.png")})
    items.append((plugin.url_for(settings), listItem, True))    
    addDirectoryItems(plugin.handle, items)
    xbmc.executebuiltin("Container.SetViewMode(%s)" % "508")
    endOfDirectory(plugin.handle)

@plugin.route('/movies')
def movies():
    items = []
    listItem = ListItem(translate(30003))
    listItem.setProperty("infomenu",translate(30103))
    listItem.setArt({'icon': 'DefaultAddonsSearch.png'})   
    items.append((plugin.url_for(searchmenu,"movies"),  listItem, True))
    listItem = ListItem(translate(30005))
    listItem.setProperty("infomenu",translate(30105))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advancedsearch,"movies"), listItem, True))
    listItem = ListItem(translate(30006))
    listItem.setProperty("infomenu",translate(30106))
    listItem.setArt({'icon': get_icon("download.png")})
    items.append((plugin.url_for(downloaded,"movies","m"), listItem, True))
    listItem = ListItem(translate(30007))
    listItem.setProperty("infomenu",translate(30107))
    listItem.setArt({'icon': get_icon("playlist.png")})
    items.append((plugin.url_for(categories,query="queue",query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30008))
    listItem.setProperty("infomenu",translate(30108))
    listItem.setArt({'icon': get_icon("unfinishedmovies.png")})
    items.append((plugin.url_for(categories,query="unfinished",query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30009))
    listItem.setProperty("infomenu",translate(30109))
    listItem.setArt({'icon': get_icon("watchedmovies.png")})
    items.append((plugin.url_for(categories,query="finished",query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30010))
    listItem.setProperty("infomenu",translate(30110))
    listItem.setArt({'icon': get_icon("newdubbedmovies.png")})
    items.append((plugin.url_for(categories, query="news-with-dubbing", query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30011))
    listItem.setProperty("infomenu",translate(30111))
    listItem.setArt({'icon': get_icon("withsubtitles.png")})
    items.append((plugin.url_for(categories, query="news-with-subtitles", query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30012))
    listItem.setProperty("infomenu",translate(30112))
    listItem.setArt({'icon': get_icon("lastaddedmovies.png")})
    items.append((plugin.url_for(categories, query="last-added", query1 = "22",query2 = "1"), listItem, True))
    url = f"https://{sosac_domain}/settings"
    source = get_url(url)
    data = json.loads(source)
    debug("current topic data %s"%data, 2)
    try : 
            if len(data["current_topic"]) != 0 :
                curr_top = data["current_topic"].split("|")
                language = xbmc.getLanguage(xbmc.ENGLISH_NAME)
                item_nam = curr_top[0] if language == "English" else curr_top[-1]
                debug("current topic item_nam %s"%item_nam, 2)
                listItem = ListItem(item_nam)
                listItem.setProperty("infomenu",translate(30113))
                listItem.setArt({'icon': get_icon("movies.png")})
                items.append((plugin.url_for(categories, query="current-topic", query1 = "current_topic",query2 = "1"), listItem, True))
    except Exception as e :
        debug("Movies current-topic error %s"%e, 2)
            
    listItem = ListItem(translate(30014))
    listItem.setProperty("infomenu",translate(30114))
    listItem.setArt({'icon': get_icon("newmostpopular.png")})
    items.append((plugin.url_for(categories,query="news-popular",query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30015))
    listItem.setProperty("infomenu",translate(30115))
    listItem.setArt({'icon': get_icon("mostpopular.png")})
    items.append((plugin.url_for(categories,query ="popular",query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30016))
    listItem.setProperty("infomenu",translate(30116))
    listItem.setArt({'icon': get_icon('bestratednew.png')})
    items.append((plugin.url_for(categories,query="news-top-rated",query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30017))
    listItem.setProperty("infomenu",translate(30117))
    listItem.setArt({'icon': get_icon('bestrated.png')})
    items.append((plugin.url_for(categories,query="top-rated",query1 = "22",query2 = "1"), listItem, True))
    listItem = ListItem(translate(30018))
    listItem.setProperty("infomenu",translate(30118))
    listItem.setArt({'icon': get_icon("movies-tvshows-a-z.png")})
    items.append((plugin.url_for(cat2,"movies","a-z"), listItem, True))
    listItem = ListItem(translate(30019))
    listItem.setProperty("infomenu",translate(30119))
    listItem.setArt({'icon': get_icon("genre.png")})
    items.append((plugin.url_for(cat2,"movies","by-genre"), listItem, True))
    listItem = ListItem(translate(30020))
    listItem.setProperty("infomenu",translate(30120))
    listItem.setArt({'icon': get_icon("byyear.png")})
    items.append((plugin.url_for(cat2,"movies","by-year"), listItem, True))
    listItem = ListItem(translate(30021))
    listItem.setProperty("infomenu",translate(30121))
    listItem.setArt({'icon': get_icon("byquality.png")})
    items.append((plugin.url_for(cat2,"movies","by-quality"), listItem, True))
    
    addDirectoryItems(plugin.handle, items)
    xbmc.executebuiltin("Container.SetViewMode(%s)" % "508")
    endOfDirectory(plugin.handle)


@plugin.route('/tvshows')
def tvshows():
    #debug('tvshows sys arg int(sys.argv[1]) %s'%sys.argv,2)
    items = []
    listItem = ListItem(translate(30003))
    listItem.setProperty("infomenu",translate(30103))
    listItem.setArt({'icon': 'DefaultAddonsSearch.png'})   
    items.append((plugin.url_for(searchmenu,"serials"),  listItem, True))
    listItem = ListItem(translate(30005))
    listItem.setProperty("infomenu",translate(30105))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advancedsearch,"serials"), listItem, True))
    listItem = ListItem(translate(30006))
    listItem.setProperty("infomenu",translate(30106))
    listItem.setArt({'icon': get_icon("download.png")})
    items.append((plugin.url_for(downloaded,"serials","s"), listItem, True))
    listItem = ListItem(translate(30022))
    listItem.setProperty("infomenu",translate(30122))
    listItem.setArt({'icon': get_icon("playlist.png")})
    items.append((plugin.url_for(cat_ser,query="queue",query1 = "22",query2 = "22",query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30023))
    listItem.setProperty("infomenu",translate(30123))
    listItem.setArt({'icon': get_icon("unfinishedtvshows.png")})
    items.append((plugin.url_for(cat_ser,query="unfinished",query1 = "22",query2 = "22",query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30024))
    listItem.setProperty("infomenu",translate(30124))
    listItem.setArt({'icon': get_icon("watchedtvshows.png")})
    items.append((plugin.url_for(cat_ser,query="finished", query1 = "22", query2 = "22",query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30025))
    listItem.setProperty("infomenu",translate(30125))
    listItem.setArt({'icon': get_icon("lastaddedtvshows.png")})
    items.append((plugin.url_for(cat_ser,query="last-added", query1 = "22", query2 = "22", query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30026))
    listItem.setProperty("infomenu",translate(30126))
    listItem.setArt({'icon': get_icon("newmostpopular.png")})
    items.append((plugin.url_for(cat_ser,query="news-with-dubbing",query1 = "22",query2 = "episodes",query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30027))
    listItem.setProperty("infomenu",translate(30127))
    listItem.setArt({'icon': get_icon("withsubtitles.png")})
    items.append((plugin.url_for(cat_ser,query="news-with-subtitles",query1 = "22",query2 = "episodes",query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30028))
    listItem.setProperty("infomenu",translate(30128))
    listItem.setArt({'icon': get_icon("newmostpopular.png")})
    items.append((plugin.url_for(cat_ser,query="last-added", query1 = "22", query2 = "episodes", query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30029))
    listItem.setProperty("infomenu",translate(30129))
    listItem.setArt({'icon': get_icon("tvtracker.png")})
    items.append((plugin.url_for(cat_ser, query="by-date", query1 = "22", query2 = "22", query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30030))
    listItem.setProperty("infomenu",translate(30130))
    listItem.setArt({'icon': get_icon("newmostpopular.png")})
    items.append((plugin.url_for(cat_ser, query="news-popular", query1 = "22", query2 = "22", query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30031))
    listItem.setProperty("infomenu",translate(30131))
    listItem.setArt({'icon': get_icon("mostpopular.png")})
    items.append((plugin.url_for(cat_ser,query ="popular",query1 = "22",query2 = "22",query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30032))
    listItem.setProperty("infomenu",translate(30132))
    listItem.setArt({'icon': get_icon('bestratednew.png')})
    items.append((plugin.url_for(cat_ser,query="news-top-rated",query1 = "22",query2 = "22",query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30033))
    listItem.setProperty("infomenu",translate(30133))
    listItem.setArt({'icon': get_icon("bestrated.png")})
    items.append((plugin.url_for(cat_ser,query="top-rated",query1 = "22",query2 = "22",query3 = "22",query4 = "1"), listItem, True))
    listItem = ListItem(translate(30034))
    listItem.setProperty("infomenu",translate(30134))
    listItem.setArt({'icon': get_icon("movies-tvshows-a-z.png")})
    items.append((plugin.url_for(cat2,"serials","a-z"), listItem, True))
    listItem = ListItem(translate(30035))
    listItem.setProperty("infomenu",translate(30135))
    listItem.setArt({'icon': get_icon("genre.png")})
    items.append((plugin.url_for(cat2,"serials","by-genre"), listItem, True))
    listItem = ListItem(translate(30036))
    listItem.setProperty("infomenu",translate(30136))
    listItem.setArt({'icon': get_icon("byyear.png")})
    items.append((plugin.url_for(cat2,"serials","by-year"), listItem, True))
    
    addDirectoryItems(plugin.handle, items)
    xbmc.executebuiltin("Container.SetViewMode(%s)" % "508")
    endOfDirectory(plugin.handle)

@plugin.route('/advancedsearch/<mov_ser>')
def advancedsearch(mov_ser):
    daten = dt.now()
    year = int(daten.strftime("%Y")) + 1

    items = []
    listItem = ListItem(translate(30041))
    listItem.setProperty("infomenu",translate(30141))
    listItem.setArt({'icon': 'DefaultAddonsSearch.png'})
    if mov_ser == "movies" :
        items.append((plugin.url_for(advanced_sort,"movies","adv_reset"),  listItem, True))
    else : items.append((plugin.url_for(advanced_sort,"serials","adv_resets"),  listItem, True))
    advsv = addon.getSetting('adv_sort') if mov_ser == "movies" else addon.getSetting('adv_sorts')
    advs = SORT_List[int(advsv)] if mov_ser == "movies" else SORT_Lists[int(advsv)]
    listItem = ListItem(f"{translate(30042)} : {advs}") 
    listItem.setProperty("infomenu",translate(30142))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_sort"), listItem, True))
    advk = addon.getSetting('adv_keyword') if mov_ser == "movies" else addon.getSetting('adv_keywords')
    listItem = ListItem(f"{translate(30043)} : {advk}")
    listItem.setProperty("infomenu",translate(30143))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_keyword"), listItem, True))
    advd = addon.getSetting('adv_director') if mov_ser == "movies" else addon.getSetting('adv_directors')
    listItem = ListItem(f"{translate(30052)} : {advd}")
    listItem.setProperty("infomenu",translate(30152))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_director"), listItem, True))
    advw = addon.getSetting('adv_writer') if mov_ser == "movies" else addon.getSetting('adv_writers')
    listItem = ListItem(f"{translate(30044)} : {advw}")
    listItem.setProperty("infomenu",translate(30144))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_writer"), listItem, True))
    adva = addon.getSetting('adv_actor') if mov_ser == "movies" else addon.getSetting('adv_actors')
    listItem = ListItem(f"{translate(30045)} : {adva}")
    listItem.setProperty("infomenu",translate(30145))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_actor"), listItem, True))
    advf = addon.getSetting('adv_from') if mov_ser == "movies" else addon.getSetting('adv_froms')
    word = translate(30046)
    offset = 40 -len(word)
    debug("word1 %s"%offset, 2)
    listItem = ListItem(f"{translate(30046)} : {advf}")         #Release year from   {marge}{addon.getSetting('adv_from')}")
    listItem.setProperty("infomenu",translate(30146))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_from"), listItem, True))
    advt = addon.getSetting('adv_to') if mov_ser == "movies" else addon.getSetting('adv_tos')
    word = translate(30047)
    offset = 40 -len(word)+2
    debug("word2 %s"%offset, 2)
    listItem = ListItem(f"{translate(30047)} : {advt}")
    listItem.setProperty("infomenu",translate(30147))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_to"), listItem, True))
    advgv = addon.getSetting('adv_genre') if mov_ser == "movies" else addon.getSetting('adv_genres')
    advg = genre[int(advgv)-1] if  int(advgv) != 0 else translate(30329)
    word = translate(30048)
    offset = 40 -len(word)+2
    listItem = ListItem(f"{translate(30048)} : {advg}")
    listItem.setProperty("infomenu",translate(30148))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_genre"), listItem, True))
    advov = addon.getSetting('adv_origin') if mov_ser == "movies" else addon.getSetting('adv_origins')
    advo = country_listt[int(advov)-1] if  int(advov) != 0 else translate(30329)
    word = translate(30049)
    offset = 40 -len(word)+2
    listItem = ListItem(f"{translate(30049)} : {advo}")
    listItem.setProperty("infomenu",translate(30149))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_origin"), listItem, True))
    advlv = addon.getSetting('adv_lang') if mov_ser == "movies" else addon.getSetting('adv_langs')
    advl = dub_list[int(advlv)-1] if  int(advlv) != 0 else translate(30329)
    listItem = ListItem(f"{translate(30050)} : {advl}")
    listItem.setProperty("infomenu",translate(30150))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_lang"), listItem, True))
    advq = addon.getSetting('adv_quality') if mov_ser == "movies" else addon.getSetting('adv_qualitys')
    if advq == "All" or advq == "Vše" : advq = translate(30329)
    listItem = ListItem(f"{translate(30051)} : {advq}")
    listItem.setProperty("infomenu",translate(30151))
    listItem.setArt({'icon': get_icon("advancedsearch.png")})
    items.append((plugin.url_for(advanced_sort,mov_ser,"adv_quality"), listItem, True))
    listItem = ListItem(translate(30053))
    if mov_ser == "movies" :
        items.append((plugin.url_for(categories,query="advancedsearch",query1 = "22",query2 = "1"), listItem, True))
    else :
        items.append((plugin.url_for(cat_ser,query="advancedsearch",query1 = "22",query2 = "22",query3 = "22",query4 = "1"), listItem, True))
    xbmc.executebuiltin("Container.SetViewMode(%s)" % "508")
    addDirectoryItems(plugin.handle, items)
    endOfDirectory(plugin.handle)

@plugin.route('/searchmenu/<mov_ser>')
def searchmenu(mov_ser):        
    items = []
    listItem = ListItem(translate(30284))
    listItem.setProperty("infomenu",translate(30285))
    listItem.setArt({'icon': 'DefaultAddonsSearch.png'})
    if mov_ser == "movies" : 
        items.append((plugin.url_for(categories,query="search",query1 = "22",query2 = "1"),  listItem, True))
    else : 
        items.append((plugin.url_for(cat_ser,query="search",query1 = "22", query2 = "22", query3 = "22",query4 = "1"),  listItem, True))

    listItem = ListItem(translate(30040))
    listItem.setProperty("infomenu",translate(30140))
    listItem.setArt({'icon': 'DefaultAddonsSearch.png'})   
    items.append((plugin.url_for(delete_search,query=mov_ser,query1 = "all"),  listItem, True))
    file_search = movie_search if mov_ser == "movies" else serial_search
    if xbmcvfs.exists(file_search) :
        f = open(file_search,"r")
        moviefil = f.readlines()
        f.close()
        for i in moviefil :
            listItem = ListItem(i.strip())
            listItem.setArt({'icon': 'DefaultAddonsSearch.png'})   
            menu_list = []
            action = "container.update(\"%s\")" % plugin.url_for(delete_search, query=mov_ser, query1=str(i))
            menu_list.append((translate(30275), action))
            listItem.addContextMenuItems(menu_list)
            if mov_ser == "movies" : 
                items.append((plugin.url_for(categories,query="search",query1 = i.strip(),query2 = "1"),  listItem, True))
            else : 
                items.append((plugin.url_for(cat_ser,query="search", query1 = i.strip(), query2 = "22", query3 = "22",query4 = "1"),  listItem, True))

    addDirectoryItems(plugin.handle, items)
    xbmc.executebuiltin("Container.SetViewMode(%s)" % "508")
    parentP = xbmc.getInfoLabel('Container.FolderPath')
    debug("searchmenu parentP %s"%parentP, 2)
    endOfDirectory(plugin.handle) #, cacheToDisc=False ) #updateListing=True) #, cacheToDisc=False)

@plugin.route('/delete_search')
def delete_search():
    mov_ser = plugin.args["query"][0]
    m_id = plugin.args["query1"][0]
    file_search = movie_search if mov_ser == "movies" else serial_search
    if m_id == "all" :
        try :
            if not xbmcvfs.exists(file_search) : return
            result = xbmcvfs.delete(file_search)
        except Exception as e:
            debug("Delete search file error %s"%e, 2)
        xbmc.executebuiltin("Action(ParentDir)")
        xbmc.executebuiltin('Container.Refresh')
    else :
        try:
            with open(file_search,"r") as fr:
                lines = fr.readlines()
 
            with open(file_search,"w") as fw:
                for line in lines:               
                    if line.strip('\n') != m_id.strip('\n') :
                        fw.write(line)            
        except Exception as e:
            debug("Delete search file error %s"%e, 2)

        xbmc.sleep(500)
        parentP = xbmc.getInfoLabel('Container.FolderPath')
        debug("Delete search parentP %s"%parentP, 2)
        if "searchmenu" not in parentP :
                url = plugin.url_for(searchmenu,mov_ser)
                xbmc.executebuiltin('Container.Update("%s")' % url)
                return
        else  :
            xbmc.executebuiltin("Action(ParentDir)")
            xbmc.executebuiltin('Container.Refresh')
    #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/searchmenu/mov_ser/)")
    endOfDirectory(plugin.handle)


@plugin.route('/advanced_sort/<mov_ser>/<sort_name>')
def advanced_sort(mov_ser,sort_name):
    adv_dict = {}
    adv_list1 = []
    if sort_name == "adv_reset" :
        for item in SETTINGS :
            try :
                if item == "adv_to" :
                    daten = dt.now()
                    year = daten.strftime("%Y")
                    addon.setSetting(item,year)
                else : addon.setSetting(item,SETTINGS[item])
            except Exception as e :
                debug("Advanced search error %s"%e,2)
        if mov_ser == "movies" :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'movies'/''/)")
        else :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'serials'/''/)")
        return
    elif sort_name == "adv_resets" :
        for item in SETTINGSs :
            try :
                if item == "adv_tos" :
                    daten = dt.now()
                    year = daten.strftime("%Y")
                    addon.setSetting(item,year)
                else : addon.setSetting(item,SETTINGSs[item])
            except Exception as e :
                debug("Advanced search error %s"%e,2)
        if mov_ser == "movies" :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'movies'/''/)")
        else :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'serials'/''/)")
        return
        
    elif sort_name == "adv_sort" :
        message = translate(30054)
        adv_list = []
        adv_list1 = []
        if mov_ser == "movies" :
            for i in SORT_List :
                adv_list.append(i)
        else :
            for i in SORT_Lists :
                adv_list.append(i)
                
    elif sort_name == "adv_keyword" :
        message = translate(30055)
        keyw = search(message)
        if mov_ser != "movies" : sort_name = sort_name + "s"
        addon.setSetting(sort_name,keyw)
        if mov_ser == "movies" :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'movies'/''/)")
        else :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'serials'/''/)")
        return
    elif sort_name == "adv_director" :
        message = translate(30056)
        keyw = search(message)
        if mov_ser != "movies" : sort_name = sort_name + "s"
        addon.setSetting(sort_name,keyw)
        if mov_ser == "movies" :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'movies'/''/)")
        else :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'serials'/''/)")
        return
    elif sort_name == "adv_writer" :
        message = translate(30057)
        keyw = search(message)
        if mov_ser != "movies" : sort_name = sort_name + "s"
        addon.setSetting(sort_name,keyw)
        if mov_ser == "movies" :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'movies'/''/)")
        else :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'serials'/''/)")
        return
    elif sort_name == "adv_actor" :
        message = translate(30058)
        keyw = search(message)
        if mov_ser != "movies" : sort_name = sort_name + "s"
        addon.setSetting(sort_name,keyw)
        if mov_ser == "movies" :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'movies'/''/)")
        else :
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'serials'/''/)")
        return
    elif sort_name == "adv_from" :
        message = translate(30059)
        adv_list = []
        daten = dt.now()
        year = int(daten.strftime("%Y")) + 1
        adv_list = [ str(x) for x in range(1900,year)]
        adv_list.sort(reverse=True)
        adv_dict = {}

    elif sort_name == "adv_to" :
        message = translate(30060)
        adv_list = []
        daten = dt.now()
        year = int(daten.strftime("%Y")) + 2
        adv_list = [ str(x) for x in range(1900,year)]
        adv_list.sort(reverse=True)
        adv_dict = {}
    elif sort_name == "adv_genre" :
        message = translate(30061)
        adv_list = genre
        #adv_list1 = genre1 
        adv_list.insert(0, translate(30329))
        #adv_list1.insert(0, "All")
        adv_dict = {}
    elif sort_name == "adv_origin" :
        message = translate(30062)
        adv_list = country_listt
        adv_list.insert(0, translate(30329))
    elif sort_name == "adv_lang" :
        message = translate(30063)
        adv_list = dub_list #list(DUBBING.keys())
        #adv_list1 = dub_list1 
        adv_list.insert(0, translate(30329))
        #adv_list1.insert(0, "All")
        #adv_dict = COUNTRY_DICT
    elif sort_name == "adv_quality" :
        message = translate(30064)
        adv_list = [x.upper() for x in quality_list]
        adv_list.insert(0, translate(30329))
        adv_dict = {}
    else: adv_list = []

    if len(adv_list) == 0 :
        xbmc.executebuiltin('Container.Refresh')
        return
    adv_select = dialog.select(message, adv_list)
    if adv_select <0 : return
    sel_res = adv_list[adv_select] #if len(adv_list1) == 0 else adv_list1[adv_select]
    list1 = ["adv_sort","adv_genre","adv_origin","adv_lang","adv_sorts","adv_genres","adv_origins","adv_langs"]
    if mov_ser != "movies" : sort_name = sort_name + "s"
    if sort_name in list1 :
        addon.setSetting(sort_name,str(adv_select))
    else :
        addon.setSetting(sort_name,sel_res)

    if mov_ser == "movies" :
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'movies'/''/)")
    else :
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/advanced_sort/'serials'/''/)")
    #xbmc.executebuiltin('Container.Refresh')
    #return

@plugin.route('/cat2/<mov_ser>/<listname>')
def cat2(mov_ser, listname):
    items = []
    if listname == "a-z" : listvalue = letter
    elif listname == "by-genre" : listvalue = genre
    elif listname == "by-quality" : listvalue = qual_list
    elif listname == "by-year" :
        daten = dt.now()
        year = int(daten.strftime("%Y")) + 2
        listvalue = [ x for x in range(1900,year)]
        listvalue.sort(reverse=True)
    for ind , val in enumerate(listvalue) :
        name = val.upper() if listname == "a-z" else val  
        listItem = ListItem(str(name))
        val_r = ind if listname == "by-genre" else val
        if mov_ser == "movies" :
            items.append((plugin.url_for(categories,query =listname, query1 = val_r,query2 = "1"), listItem, True))
        else :
            items.append((plugin.url_for(cat_ser, query =listname, query1 = val_r, query2 = "22", query3 = "22",query4 = "1"), listItem, True))

    xbmc.executebuiltin("Container.SetViewMode(%s)" % "508")          
    xbmcplugin.addDirectoryItems(plugin.handle, items, len(items))
    xbmcplugin.endOfDirectory(plugin.handle)

def select_dat(dat,mess) :
    formatd = "%Y-%m-%d %H:%M:%S.%f"
    day_main = dat 

    day_list = []
    dat_list = []
    for i in range(6) :
        dat = day_main - timedelta(days=6-i)
        d = dat.strftime("%d.%m.%y")
        day_list.append(d)
        dat_list.append(dat)

    d = day_main.strftime("%d.%m.%y")
    day_list.append(f"[B]{d}[/B]")
    dat_list.append(day_main)
    for i in range(7) :
        dat = day_main + timedelta(days=i+1)
        d = dat.strftime("%d.%m.%y")
        day_list.append(d)
        dat_list.append(dat)

    day_list.append(translate(30072))
    day_list.append(translate(30073))

    answ = dialog.select(mess, day_list)
    debug("select_dat answ  %s"%(answ),2)
    if answ == None or answ < 0 :
        #xbmc.executebuiltin("RunScript(plugin://plugin.video.sosac-2/tvshows)")
        return None , None
    if day_list[answ]  == translate(30072) :        
        daynext = dat_list[13] + timedelta(days=7)
        return 14, daynext
    elif day_list[answ]  == translate(30073) :
        dayprev = dat_list[0] - timedelta(days=8)
        return 14, dayprev
    else :
        return answ, dat_list[answ]

def epi_tracker() : #day):
    formatd = "%Y-%m-%d %H:%M:%S.%f"
    day_main = dt.today() 

    mess = translate(30070)
    answ, day_from = select_dat(day_main, mess)
    if answ == None or answ < 0 :
        #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/tvshows)")
        #xbmc.executebuiltin("Action(ParentDir)")
        return None, None #"None" : 
    while answ == 14 :
        day_main = day_from
        answ, day_from = select_dat(day_main, mess)
    if answ == None or answ < 0 :
        #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/tvshows)")
        return None, None
    mess = translate(30071)
    day_main = day_from + timedelta(days=6)
    answ, day_to = select_dat(day_main, mess)
    if  answ == None or answ < 0 :
        #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/tvshows)")
        return None, None
    day_limit = day_main
    while answ == 14 :
        day_main = day_limit if day_to < day_limit else  day_to
        answ, day_to = select_dat(day_main, mess)
    if  answ == None or answ < 0 :
        #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/tvshows)")
        return None, None
    dayf = day_from.strftime("%Y-%m-%d")
    dayt = day_to.strftime("%Y-%m-%d")
    return dayf, dayt #, 

@plugin.route('/tvguide') 
def tvguide() :
    debug('tvguide sys arg int(sys.argv[1]) %s'%sys.argv,2)
    day_main = dt.today()
    mess = translate(30160)
    answ, day_to = select_dat(day_main, mess)
    debug("tvguide1 answ day_to %s %s"%(answ,day_to),2)
    if answ == None or answ < 0   :
        #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/)")
        xbmc.executebuiltin("Action(ParentDir)") 
        #return
    else :
        while answ == 14 :
            day_main = day_to
            answ, day_to = select_dat(day_main, mess)

        debug("tvguide2 answ day_to %s %s"%(answ,day_to),2)
        if answ == None  or answ < 0   :
            #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/)")
            #xbmc.executebuiltin("Container.Refresh")
            xbmc.executebuiltin("Action(ParentDir)")
            #return 
        else :
            debug("tvguide day %s"%day_to,2)
            dayt = day_to.strftime("%Y-%m-%d")     
            debug("tvguide dayt %s"%dayt,2)
            tvg_list(dayt,"1")
    endOfDirectory(plugin.handle)

@plugin.route('/tvg_list/<day>/<page>/')
def tvg_list(day,page):
    day = day.replace(":","-")
    day = day.replace(".","-")
    addon.setSetting("tvguide",day)
    url = set_sosac_guide(day,page)
    source = get_url(url)
    res = json.loads(source)
    show_plug_list("tvguide","0", res)


@plugin.route('/gensearch')
def gensearch():
    items = []
    listItem = ListItem(translate(30037))
    listItem.setProperty("infomenu",translate(30100))
    listItem.setArt({'icon': get_icon("movies.png")}) 
    items.append((plugin.url_for(searchmenu,"movies"), listItem, True))
    listItem = ListItem(translate(30038))
    listItem.setProperty("infomenu",translate(30101))
    listItem.setArt({'icon': 'DefaultTVShows.png'})
    items.append((plugin.url_for(searchmenu,"serials"), listItem, True))
    listItem = ListItem(translate(30039))
    listItem.setProperty("infomenu",translate(30102))
    listItem.setArt({'icon': get_icon("movies.png")})
    items.append((plugin.url_for(advancedsearch,"movies"), listItem, True))
    listItem = ListItem(translate(30068))
    listItem.setProperty("infomenu",translate(30103))
    listItem.setArt({'icon': 'DefaultTVShows.png'})
    items.append((plugin.url_for(advancedsearch,"serials"), listItem, True))
    addDirectoryItems(plugin.handle, items)
    xbmc.executebuiltin("Container.SetViewMode(%s)" % "508")
    endOfDirectory(plugin.handle)


#@plugin.route('/search')
def search(entete=""):
    listing = []
    input = xbmc.Keyboard("", translate(30402)) #_addon.getLocalizedString(30005))
    input.doModal()

    if not input.isConfirmed():
        #xbmc.executebuiltin("Action(ParentDir)")
        #xbmc.executebuiltin('Container.Refresh')
        return None
    query = input.getText()
    if query == "" or query == None:
        #xbmc.executebuiltin("Action(ParentDir)")
        #xbmc.executebuiltin('Container.Refresh')
        return None #xbmc.executebuiltin("Action(ParentDir)")

    return query

    endOfDirectory(plugin.handle)


@plugin.route('/settings')
def settings():
    addon.openSettings("main")

@plugin.route('/downloaddel')
def downloaddel():
    mov_ser = plugin.args["query"][0]
    m_id = plugin.args["query1"][0]
    #name2 = plugin.args["query2"][0]
    name2 = plugin.args["query2"][0].split("+")
    
    filpath = moviesPath if  mov_ser == "movies" else seriesPath
    filename = f"{name2[0]}/{m_id}-{name2[1]}.mp4"
    debug("downloaddel Delete file filename %s"%filename,2)
    try :
        if xbmcvfs.exists(filename) :
            result = xbmcvfs.delete(filename)
            debug("downloaddel Delete file result %s"%result,2)
            if result : notify(translate(30402), translate(30292), time=5000)
    except Exception as e :
        debug("Delete file error %s"%e,2)

    filpath = moviesSub if  mov_ser == "movies" else seriesSub
    try :
        sub_fil = f"{m_id}-{name2[1]}.srt"
        filename = os.path.join(filpath,sub_fil)
        if xbmcvfs.exists(filename) :
            result = xbmcvfs.delete(filename)
            debug("downloaddel Delete sub file result %s"%result,2)
    except Exception as e :
        debug("Delete sub file error %s"%e,2)

    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/downloaded/<mov_ser>/<dir_n>')
def downloaded(mov_ser,dir_n):
    #thread_act = threading.enumerate()
    file_dict = {}
    def sortSecond(val):
        return val[1]
    if mov_ser == "movies" :
        dir_name = moviesPath
    elif mov_ser == "serials" :
        if "+" in dir_n :
            dir_ns = dir_n.split("+")
            dir_n = dir_ns[0]+"/"+dir_ns[1]
        dir_name = xbmcvfs.translatePath(os.path.join(seriesPath, dir_n)) if dir_n != "s" else seriesPath
        debug("downloaded serials dir_name %s"%dir_name,2)
    elif mov_ser == "tvshows" :
        if "+" in dir_n :
            dir_ns = dir_n.split("+")
            dir_n = dir_ns[0]+"/"+dir_ns[1]
        dir_name = xbmcvfs.translatePath(os.path.join(seriesPath, dir_n))
        debug("downloaded tvshows dir_name %s"%dir_name,2)

    dir_list , list_of_files = xbmcvfs.listdir(dir_name)
    debug("downloaded list_of_files %s"%list_of_files,2)
    debug("downloaded dir_list %s"%dir_list,2)
    for item in dir_list :            
        item_id = item.split("_")[-1]
        url = set_sosac_info("id",**{'arg2':item_id}) if mov_ser == "movies" else set_sosac_epi(item_id)
        source = get_url(url)
        data = json.loads(source)
        data["name2"] = ""
        file_dict[item_id] = data["info"]
    if mov_ser != "tvshows" :
        list_of_files = [ x.split(".")[0] for x in list_of_files]
        list_of_files = [ (x.split("-")[0],int(x.split("-")[1])) for x in list_of_files]    
        list_of_files.sort(key=sortSecond, reverse=True)
        debug("downloaded list_of_files apres traitement %s"%list_of_files,2)
        
        for item in list_of_files :
            item_id = item[0]
            url = set_sosac_info("id",**{'arg2':item_id}) if mov_ser == "movies" else set_sosac_ser("",**{'arg2':item_id,'arg3':"episodes",'arg4':""})
            source = get_url(url)
            data = json.loads(source)
            data["name2"] = dir_name + "+" + str(item[1]) if dir_name != "s" else seriespath
            file_dict[item_id] = data

    debug("downloaded list_of_files data %s"%file_dict,2)
    show_plug_list("download",mov_ser, file_dict,dir_name)
        
@plugin.route('/downloadPlay')
def downloadPlay():
    mov_ser = plugin.args["query"][0]
    m_id = plugin.args["query1"][0]
    name2 = plugin.args["query2"][0].split("+")
    #debug("downloadPlay m_id %s"%m_id,2)
    #debug("downloadPlay name2 %s"%name2,2)
    
    filpath = moviesPath if  mov_ser == "movies" else seriesPath
    filename = f"{name2[0]}/{m_id}-{name2[1]}.mp4"
    subpath = moviesSub if  mov_ser == "movies" else seriesSub
    dir_list , fil_list = xbmcvfs.listdir(subpath)
    sub_fil = f"{m_id}-{name2[1]}.srt"
    debug("downloadPlay sub_fil %s"%sub_fil, 2)
    try :
        if xbmcvfs.exists(filename) :
            li = ListItem(path=filename)
            if sub_fil in fil_list :
                sub_path = f"{subpath}/{sub_fil}"
                try:
                    li.setSubtitles([sub_path])
                    SubtitleActive = True
                except Exception as e:
                    debug("downloadPlay Can't load subtitle: %s"%e, 2)
            xbmcplugin.setResolvedUrl(plugin.handle, True, li)
            player = xbmc.Player()
    except Exception as e :
        debug("downloadPlay error %s"%e,2)

def lastCmd(sysargv) :
    lastcommand0 = sysargv[0]
    lastcommand2 = sysargv[2]
    debug("lastCmd last_command0, last_command2 %s %s"%(lastcommand0, lastcommand2),2)
    return lastcommand0, lastcommand2

    
@plugin.route('/categories')
def categories():
    #debug("categories sys.argv  %s"%(sys.argv),2)
    fl_sortie = False
    fl_video = False

    #query = plugin.args["query"][0]
    try :
        query = plugin.args["query"][0]
    except KeyError  :
        return

    query1 = plugin.args["query1"][0]
    query2 = plugin.args["query2"][0]
    if "search" == query and query1 == "22":
        query1 = search()
        if query1 == "" or query1 == None :
            fl_sortie = True
            xbmc.executebuiltin("Action(ParentDir)") #
        else :
            f = open(movie_search,"a")
            f.write(query1+'\n')
            f.close
            #xbmc.executebuiltin('Container.Refresh')
            #fl_sortie = True

    elif "search" == query and query1 == "" :
        fl_sortie = True
        xbmc.executebuiltin("Action(ParentDir)")
    elif "search" == query and query1 == None :
        fl_sortie = True
        xbmc.executebuiltin("Action(ParentDir)")
        
    if not fl_sortie :
        url = set_sosac_info(query,**{'arg2':query1,'arg3':query2})
        source = get_url(url)
        res = json.loads(source)
        addon.setSetting("search-menu",query)
        if "current-topic" == query : 
            show_plug_list("movies", "current_topic", res)
        elif "search" == query :            
            addon.setSetting("search-str",query1)
            show_plug_list("movies", "0", res,start = query1 )
        else : show_plug_list("movies", "0", res)
    elif fl_sortie :
        parentP = xbmc.getInfoLabel('Container.FolderPath')
        debug("categories parentP %s"%parentP, 2)

        url = plugin.url_for(searchmenu,"movies")
        xbmc.executebuiltin('Container.Update("%s")' % url)
        #xbmc.executebuiltin("Action(ParentDir)")
        xbmc.executebuiltin('Container.Refresh')

    endOfDirectory(plugin.handle) #, updateListing=True)

def checkMyPlaylist(mov_ser) :
    query = "queue"
    query1 = "22"
    query2 = "1"
    try :
        url = set_sosac_info(query,**{'arg2':query1,'arg3':query2}) if mov_ser == "movies" else set_sosac_ser("queue",**{'arg2':"22",'arg3':"22",'arg4':"22",'arg5':"1"})
        source = get_url(url)
        data = json.loads(source)
        queueList = [item["_id"] for item in data]
    except Exception as e :
        debug("checkMyPlaylist error %s"%e,2)
        queueList = []
    return queueList
    
@plugin.route('/playlist')
def playlist():
    #global  last_command0, last_command2

    query = plugin.args["query"][0]
    query1 = plugin.args["query1"][0]
    query2 = plugin.args["query2"][0]
    last_command0 = plugin.args["query3"][0] if plugin.args["query3"][0] else "" 
    last_command2 = plugin.args["query4"][0] if plugin.args["query4"][0] else ""

    if "reset" == query1 :
        time_val = 0
        set_sosac_watchTime(query, query2, time_val)
    elif "watched" in query1 :
        time_val = int(query1.split("-")[1])
        set_sosac_watchTime(query, query2, time_val)
    elif query == "movies" :
        set_sosac_info(query1,**{'arg2':query2})
    elif query == "serials" :
        query3 = query4 = ""
        url = set_sosac_ser(query1,**{'arg2':query2,'arg3':query3,'arg4':query4})
    
    #debug("playlist last_command0 %s"%last_command0,2)
    #fonct_n1 = last_command0.split("/")[-1]
    #debug("playlist movies fonct_n1 %s"%fonct_n1, 2)
    parentP = xbmc.getInfoLabel('Container.FolderPath')
    #debug("playlist parentP %s"%parentP, 2)
    if ("categories" in parentP or "cat_epi" in parentP or "cat_ser" in parentP) and not "by-date" in parentP :
        xbmc.executebuiltin("Action(ParentDir)")
        xbmc.executebuiltin('Container.Refresh')
    else :
        xbmc.executebuiltin('Container.Refresh')
        xbmc.sleep(100)
        return
    #endOfDirectory(plugin.handle,succeeded =True , updateListing=True, cacheToDisc=False)
    endOfDirectory(plugin.handle, cacheToDisc=False)
    

@plugin.route('/cat_ser')
def cat_ser():
    fl_date = False
    #query = plugin.args["query"][0]
    try :
        query = plugin.args["query"][0]
    except KeyError  :
        #if "KeyError: 'query'" in e :
        #xbmc.executebuiltin('Container.Refresh')
        return
    query1 = plugin.args["query1"][0]
    #query4 = plugin.args["query4"][0]
    try :
        query2 = "" if not plugin.args["query2"][0] else plugin.args["query2"][0]
        query3 = "" if not plugin.args["query3"][0] else plugin.args["query3"][0]
        query4 = "" if not plugin.args["query4"][0] else plugin.args["query4"][0]
    except Exception as e :
        debug("cat_ser error %s"%e,2)

    if "search" == query and query1 == "22":
        query1 = search()
        if query1 == "" or query1 == None :
            fl_date = True
            xbmc.executebuiltin("Action(ParentDir)") #
        else :
            f = open(serial_search,"a")
            f.write(query1+'\n')
            f.close
    elif "search" == query and query1 == "" :
        fl_date = True
        xbmc.executebuiltin("Action(ParentDir)")
    elif "search" == query and query1 == None :
        fl_date = True
        xbmc.executebuiltin("Action(ParentDir)")

    elif "by-date" == query :
        if query1 == "22":
            dat_from, dat_to = epi_tracker()
            if not dat_from :
                #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sosac-2/tvshows)")
                fl_date = True
                xbmc.executebuiltin("Action(ParentDir)")
                #return
            else :
                query1 = dat_from
                query2 = dat_to
        '''
        else : 
            query1 = query1
            query2 = query2
        '''
    if not fl_date :
        url = set_sosac_ser(query,**{'arg2':query1,'arg3':query2,'arg4':query3,'arg5':query4})
        source = get_url(url)
        res = json.loads(source)
        new_epi = ["last-added","news-with-dubbing", "news-with-subtitles"]
        if (query in  new_epi) and (query2 == "episodes")  :
            show_plug_list("episodes3","2", res)
        elif (query ==  "by-date") :
            show_plug_list("episodes3","2", res, start=query1, stat=query2) #start et stat pour avoir la page 2 et plus
        elif query ==  "search" : show_plug_list("serials","0", res, start=query1)
        else : show_plug_list("serials","0", res)
    elif fl_date and "search" == query :
        url = plugin.url_for(searchmenu,"serials")
        xbmc.executebuiltin('Container.Update("%s")' % url)
        #xbmc.executebuiltin("Action(ParentDir)")
        xbmc.executebuiltin('Container.Refresh')
    

    endOfDirectory(plugin.handle) #, cacheToDisc=False)
    
@plugin.route('/cat_epi') 
def cat_epi() :   
    sais_id = plugin.args["query"][0]
    ep_id = plugin.args["query1"][0]
    #page = plugin.args["query4"][0]
     
    startime = plugin.args["query2"][0] if plugin.args["query2"][0]  else None
    station = plugin.args["query3"][0] if plugin.args["query3"][0]  else None
    url = set_sosac_epi(sais_id)
    source = get_url(url)
    res = json.loads(source)
    debug("cat epi startime ep_id station %s %s %s"%(startime,ep_id,station), 2)
    debug("cat epi data %s"%res, 2)
    if ep_id == "0" : #not station  :
        debug("cat epi startime passe par starttime", 2)
        show_plug_list("episodes", ep_id, res, start=startime, stat=station)
    elif station == "None" : show_plug_list("episodes", ep_id, res, start=startime, stat=station)
    else : show_plug_list("epi_tvguide", ep_id, res, start=startime, stat=station)

@plugin.route('/download/<mov_ser>/<m_id>/<link_id>')
def download(mov_ser,m_id,link_id):
    xbmc.executebuiltin(f"RunPlugin(plugin://plugin.video.sosac-2/downloadPlug/{mov_ser}/{m_id}/{link_id})")

@plugin.route('/downsais/<sais_id>/<title>/<sdsais_list>')
def downsais(sais_id,title,sdsais_list):
    if type(sdsais_list) != type([]) :
        dsais_list = re.findall("(\d+)[,|\]]",sdsais_list.replace("'",""))
    else  : dsais_list = sdsais_list
    title = title.replace(" ","-").replace(":","-")
    title = title + "_" + sais_id 
    try :
        filePath = xbmcvfs.translatePath(os.path.join(seriesPath,title.strip()))
        if not os.path.isdir(filePath) : os.mkdir(filePath)
    except Exception as e :
        debug("downsais filePath error %s"%e, 2)

    m_id = dsais_list[0]
    url = set_sosac_ser("",**{'arg2':m_id,'arg3':"episodes",'arg4':""})
    source = get_url(url)
    data = json.loads(source)
    link_id = data['l']
    select_key = selectQual("serials",m_id,link_id)
    if select_key == None :
        return
    else :
        key1 , key2, key3 = select_key

    try :
        save_key(serial_data,str(sais_id),key1,key2,key3)
    except Exception as e :
        debug("downsais savekey error %s"%e, 2)

    sais_list = []
    addon.setSetting('get_links',"true")
    for item in dsais_list :
        url = set_sosac_ser("",**{'arg2':item,'arg3':"episodes",'arg4':""})
        source = get_url(url)
        data = json.loads(source)
        link_id = data['l']
        url = set_streamujtv_info(link_id)
        source = get_url(url)
        data = json.loads(source)
        get_links_mess(data)

        link = data['URL'][key1][key2]            
        link_url = get_url(link)
        fileId = str(item) + "-" + str(int(time.time()))
        filename = fileId + ".mp4"

        dest =  filePath + "/" + filename
        sais_list.append((link_url,dest))
        try :
            save_key(serial_data,str(item),key1,key2,key3)
        except Exception as e :
            debug("downserial savekey error %s"%e, 2)
        try :
            if ("sub" in key3) and ("subtitles" in data['URL'][key1]) :                     
                subt_url_dict = data['URL'][key1]["subtitles"]
                sub_keys = list(subt_url_dict.keys())
                subt_url = data['URL'][key1]["subtitles"][sub_keys[0]]
                filename = fileId + ".srt"
                dest =  seriesSub + "/" + filename
                subtitle = subs.save_sub(subt_url,dest)
        except Exception as e :
            debug("downserial save subt error %s"%e, 2)

    saveDown(sais_list)
    downloadSais(sais_list)            

@plugin.route('/downserial/<sais_id>')
def downserial(sais_id):
    sais_list = []
    url = set_sosac_epi(sais_id)
    source = get_url(url)
    data = json.loads(source)
    sais_nb = data['info']['z']
    
    fold_name = data['info']['n']['cs'][0] 
    fold_name = fold_name.replace(" ","-").replace(":","-")
    if sais_nb == 1 : fold_name = fold_name + "-1saison"
    fold_name = fold_name + "_" + sais_id 
    try :
        serPath = xbmcvfs.translatePath(os.path.join(seriesPath,fold_name.strip()))
        if not os.path.isdir(serPath) : os.mkdir(serPath)
    except Exception as e :
        debug("downserial filePath error %s"%e, 2)
    
    link_id = data["1"]["1"]['l']
    select_key = selectQual("serials","",link_id)
    if select_key == None :
        return
    else :
        key1 , key2, key3  = select_key

    try :
        save_key(serial_data,str(sais_id),key1,key2,key3)
    except Exception as e :
        debug("downserial savekey error %s"%e, 2)

    addon.setSetting('get_links',"true")
    for x in data :
        if x != 'info' :
            try :
                if int(sais_nb) != 1 : 
                    sais_nm = f"Season-{str(x)}_{sais_id}"
                    filePath = xbmcvfs.translatePath(os.path.join(serPath,sais_nm))
                else : filePath = serPath
                if not os.path.isdir(filePath) : os.mkdir(filePath)
            except Exception as e :
                debug("downserial filePath error %s"%e, 2)
            for item in data[x] :
                try :
                    link_id = data[x][item]['l']
                    selectL = selectQual2("serials",link_id)
                    if selectL :
                        selectB = False
                        for x1, x2, x3 in selectL :
                            if (key1 , key2 ) == (x1,x2) :
                                selectB = True
                                break

                        if not selectB :
                            key1 , key2, key3  = dialSelect(key_list)
                            
                    url = set_streamujtv_info(link_id)
                    source = get_url(url)
                    data1 = json.loads(source)
                    get_links_mess(data1)

                    link = data1['URL'][key1][key2]            
                    link_url = get_url(link)
                    epis_id = data[x][item]['_id']
                    fileId = str(epis_id) + "-" + str(int(time.time()))
                    filename = fileId + ".mp4"
                    dest =  filePath + "/" + filename
                    sais_list.append((link_url,dest))
                    try :
                        save_key(serial_data,epis_id,key1,key2,key3)
                    except Exception as e :
                        debug("downserial savekey error %s"%e, 2)
                    try :
                        if ("sub" in key3) and ("subtitles" in data1['URL'][key1]) :                     
                            subt_url_dict = data1['URL'][key1]["subtitles"]
                            sub_keys = list(subt_url_dict.keys())
                            subt_url = data1['URL'][key1]["subtitles"][sub_keys[0]]
                            filename = fileId + ".srt"
                            dest =  seriesSub + "/" + filename
                            subtitle = subs.save_sub(subt_url,dest)
                    except Exception as e :
                        debug("downserial save subt error %s"%e, 2)


                except Exception as e :
                    debug("downserial item error %s"%e, 2) 

    saveDown(sais_list)
    downloadSais(sais_list)

@plugin.route('/downserialcom/<sais_id>')
def downserialcom(sais_id):
    sais_list = []
    url = set_sosac_epi(sais_id)
    source = get_url(url)
    data = json.loads(source)
    sais_nb = data['info']['z']
    
    fold_name = data['info']['n']['cs'][0] 
    fold_name = fold_name.replace(" ","-").replace(":","-")
    if sais_nb == 1 : fold_name = fold_name + "-1saison"
    fold_name = fold_name + "_" + sais_id 
    try :
        serPath = xbmcvfs.translatePath(os.path.join(seriesPath,fold_name.strip()))
        if not os.path.isdir(serPath) : os.mkdir(serPath)
    except Exception as e :
        debug("downserial filePath error %s"%e, 2)
    
    link_id = data["1"]["1"]['l']
    select_key = selectQual("serials","",link_id)
    if select_key == None :
        pass
    else :
        key1 , key2, key3  = select_key
        
    addon.setSetting('get_links',"true")
    for x in data :
        if x != 'info' :
            try :
                if int(sais_nb) != 1 : 
                    sais_nm = f"Season-{str(x)}_{sais_id}"
                    filePath = xbmcvfs.translatePath(os.path.join(serPath,sais_nm))
                else : filePath = serPath
                if not os.path.isdir(filePath) : os.mkdir(filePath)
            except Exception as e :
                debug("downserial filePath error %s"%e, 2)
            for item in data[x] :
                try :
                    link_id = data[x][item]['l']
                    selectL = selectQual2("serials",link_id)
                    if selectL :
                        selectB = False
                        for x1 ,x2,x3 in selectL :
                            if (key1 , key2 ) == (x1,x2) :
                                selectB = True
                                break

                        if not selectB :
                            key1 , key2, key3  = dialSelect(key_list)
                            
                    url = set_streamujtv_info(link_id)
                    source = get_url(url)
                    data1 = json.loads(source)
                    get_links_mess(data1)

                    link = data1['URL'][key1][key2]            
                    link_url = get_url(link)
                    epis_id = data[x][item]['_id']
                    filename = str(epis_id) + "-" + str(int(time.time())) + ".mp4"

                    dest =  filePath + "/" + filename
                    sais_list.append((link_url,dest))
                    try :
                        save_key(serial_data,epis_id,key1,key2,key3)
                    except Exception as e :
                        debug("downserialcom savekey error %s"%e, 2) 

                except Exception as e :
                    debug("downserialcom item error %s"%e, 2) 

    saveDown(sais_list)
    downloadSais(sais_list)

def prepa_list(s_id, data, sais_n, id_list, dir_name, ex_list) :
    with open(serial_data, "r") as fdata :
        f_data = json.load(fdata)
        #f_data = json.loads(fdata.read())
    if len(ex_list) != 0 : ex_id = ex_list[0]
    if len(ex_list) != 0 and f_data[ex_id] :
        key1,key2,key3 = f_data[ex_id]
        debug("prepa_list if key1,key2,key3 %s %s %s"%(key1,key2,key3), 2)
    elif str(s_id) != "" and f_data[s_id]:
        key1,key2,key3 = f_data[s_id]
        debug("prepa_list elif key1,key2,key3 %s %s %s"%(key1,key2,key3), 2)
    else :
        link_id = data[sais_n]["1"]['l']
        select_key = selectQual("serials","",link_id)
        if select_key == None :
            return
        else :
            key1 , key2, key3  = select_key

    sais_list = []
    addon.setSetting('get_links',"true")
    for item in data[sais_n] :
        if data[sais_n][item]['_id'] not in id_list : continue 
        try :
            link_id = data[sais_n][item]['l']
            selectL = selectQual2("serials",link_id)
            debug("prepalist  selectL %s"%selectL, 2)
            if selectL :                
                selectB = False
                for x1 ,x2,x3 in selectL :
                    if (key1 , key2 ) == (x1,x2) :
                        selectB = True
                        break

                if not selectB :
                    key1 , key2, key3  = dialSelect(key_list)
                    debug("prepalist  not selectL key1 %s %s"%(key1,key2), 2)
            else : continue
                    
            url = set_streamujtv_info(link_id)
            source = get_url(url)
            data1 = json.loads(source)
            get_links_mess(data1)

            link = data1['URL'][key1][key2]            
            link_url = get_url(link)
            epis_id = data[sais_n][item]['_id']
            fileId = str(epis_id) + "-" + str(int(time.time()))
            filename = fileId + ".mp4"
            dest =  dir_name + "/" + filename
            sais_list.append((link_url,dest))
            debug("prepalist  sais_list %s"%sais_list, 2)
            try :
                save_key(serial_data,epis_id,key1,key2,key3)
            except Exception as e :
                debug("prepa_list savekey error %s"%e, 2)

            debug("prepa_list key %s"%key3,2)
            if ("sub" in key3) and ("subtitles" in data1['URL'][key1]) :
                debug("downloadPlug key %s"%key3,2)
                subt_url_dict = data1['URL'][key1]["subtitles"]
                sub_keys = list(subt_url_dict.keys())
                subt_url = data1['URL'][key1]["subtitles"][sub_keys[0]]
                filename = fileId + ".srt"
                dest = seriesSub + "/" + filename
                debug("prepa_list dest %s"%dest,2)
                subtitle = subs.save_sub(subt_url,dest)

        except Exception as e :
            debug("prepa_list item error %s"%e, 2) 

    debug("prepa_list prepa_list sais_list %s"%sais_list, 2)
    

    saveDown(sais_list)
    return 

def saveDown(slist) :
    if xbmcvfs.exists(downListPath) :
        f = open(downListPath, 'r')
        content = f.read()
        f.close()
    else : content = ""
    
    f = open(downListPath, 'a',encoding="utf-8")
    debug("saveDown  ouvre fich ", 2)
    for item_l in slist :
        debug("downserial   item_l %s"%str(item_l), 2)
        if len(str(content)) !=0 and str(item_l) not in str(content) :
            f.write(str(item_l)+"\n")
            debug("saveDown write item_l %s"%str(item_l), 2)
        elif  len(str(content)) ==0 : f.write(str(item_l))
    f.close()     

def verif_tel() :
    fich_id = []
    if xbmcvfs.exists(downListPath) :
        f = open(downListPath, 'r')
        content = f.read()
        f.close()
        ficid_list = re.findall("(?s)'(https.*?)'.*?'(.*?)'",content)
        for i in ficid_list :
            sid = i[1].split("/")[-1]
            sid2 = sid.split("-")[0]
            fich_id.append(sid2)
        debug("verif_tel  fich_id %s"%fich_id, 2) 

    else : content = ""

    dir_list , fil_list = xbmcvfs.listdir(seriesPath)
    debug("verif_tel download dir dir_list %s"%dir_list, 2) 
    
    for x in dir_list :
        sais_list = []
        x_id = x.split("_")[-1]
        url = set_sosac_epi(x_id)
        source = get_url(url)
        data = json.loads(source)
        if ("Season" not in x) :
            epi_tel = 0 
            x_id = x.split("_")[-1]
            url = set_sosac_epi(x_id)
            source = get_url(url)
            data = json.loads(source)
            sais_nb = data['info']['z']
            epi_nb = data['info']['v']
            #debug("verif_tel x_id sais_nb epi_nb %s %s %s"%(x_id,sais_nb,epi_nb), 2)
            dir_name = os.path.join(seriesPath,x)
            debug("verif_tel x_id dir_name %s"%(dir_name), 2)
            dir_listx , fil_listx = xbmcvfs.listdir(dir_name)
            #debug("verif_tel x_id fil_listx %s"%(fil_listx), 2)
            if len(dir_listx) == 0 :
                epi_tel = epi_tel + len(fil_listx)
                if epi_tel != epi_nb and sais_nb == 1:
                    id_list = [data["1"][item]["_id"] for item in data["1"]]
                    debug("verif_tel x_id id_list %s"%(id_list), 2)
                    for fil in fil_listx :
                        fil_item = fil.split("-")[0]
                        debug("verif_tel x_id fil_item %s"%(fil_item), 2)
                        if (int(fil_item) in id_list) or (str(fil_item) in fich_id) :
                            id_list.remove(int(fil_item))
                    debug("verif_tel x_id id_list reste1  %s"%(id_list), 2)
                    if len(id_list) == 0 : continue
                    id_list2 = [id2 for id2 in id_list]
                    ex_list = []
                    for id_item in id_list :
                        if str(id_item) in fich_id :
                            id_list2.remove(int(id_item))
                    debug("verif_tel x_id id_list reste2  %s"%(id_list2), 2)
                    if len(id_list2) == 0 : continue
                    prepa_list("", data, "1", id_list2, dir_name,ex_list)
                    
                    #downloadSais(sais_list)
            
            else :
                if sais_nb > len(dir_listx) :
                    for i_sais in range(sais_nb) :
                        sais_nam = f"Season-{i_sais+1}_{x_id}"
                        if sais_nam in dir_listx : continue
                        dir_sais_nam = os.path.join(dir_name,sais_nam)
                        xbmcvfs.mkdir(dir_sais_nam)
                        dir_listx.append(sais_nam)
                        debug("verif_tel x_id rajout de saison %s"%(dir_sais_nam), 2)
                    debug("verif_tel x_id rajout de saison dir_listx  %s"%(dir_listx), 2)
                for item_dir in dir_listx :
                    if "Season"  in item_dir :
                        dir_namex = os.path.join(dir_name,item_dir)
                        debug("verif_tel x_id dir_namex %s"%(dir_namex), 2)
                        dir_listy , fil_listy = xbmcvfs.listdir(dir_namex)
                        epi_tel = epi_tel + len(fil_listy)
                        ss_nb1 = item_dir.split("_")[0]
                        ss_nb = ss_nb1.split("-")[1]
                        ss_epi = list(data[ss_nb].keys())
                        if len(fil_listy) == len(ss_epi) : continue
                        id_list = [data[ss_nb][item]["_id"] for item in data[ss_nb]]
                        debug("verif_tel x_id id_list %s"%(id_list), 2)
                        for fil in fil_listy :
                            fil_item = fil.split("-")[0]
                            debug("verif_tel x_id fil_item %s"%(fil_item), 2)
                            if (int(fil_item) in id_list) :
                                id_list.remove(int(fil_item))
                        debug("verif_tel x_id id_list reste  %s"%(id_list), 2)
                        if len(id_list) == 0 : continue
                        id_list2 = [id2 for id2 in id_list]
                        ex_list = []
                        for id_item in id_list :
                            if str(id_item) in fich_id :
                                id_list2.remove(int(id_item))
                        debug("verif_tel x_id id_list reste2  %s"%(id_list2), 2)
                        if len(id_list2) == 0 : continue
                        prepa_list("", data, ss_nb, id_list2, dir_namex,ex_list)
                        #debug("downserial saison sais_list %s"%sais_list, 2)
                    else: 
                        epi_tel = epi_tel + len(fil_listx)
        else :
            dir_namex = os.path.join(seriesPath,x)
            debug("verif_tel saison x_id dir_name %s"%(dir_namex), 2)
            dir_listx , fil_listx = xbmcvfs.listdir(dir_namex)
            ss_nb1 = x.split("_")[0]
            ss_nb = ss_nb1.split("-")[-1]
            ss_epi = list(data[ss_nb].keys())
            if len(fil_listy) == len(ss_epi) : continue
            id_list = [data[ss_nb][item]["_id"] for item in data[ss_nb]]
            debug("verif_tel x_id id_list %s"%(id_list), 2)
            for fil in fil_listx :
                fil_item = fil.split("-")[0]
                debug("verif_tel x_id fil_item %s"%(fil_item), 2)
                if (int(fil_item) in id_list) :
                    id_list.remove(int(fil_item))
            debug("verif_tel x_id id_list reste  %s"%(id_list), 2)
            if len(id_list) == 0 : continue
            id_list2 = [id2 for id2 in id_list]
            ex_list = []
            for id_item in id_list :
                if str(id_item) in fich_id :
                    id_list2.remove(int(id_item))
            debug("verif_tel x_id id_list reste2  %s"%(id_list2), 2)
            if len(id_list2) == 0 : continue
            prepa_list("", data, ss_nb, id_list2, dir_namex,ex_list)

        
    sais_list = []
    if xbmcvfs.exists(downListPath) :
        with open(downListPath, 'r') as f :
            content = f.read()
        sais_list = re.findall("(?s)'(https.*?)'.*?'(.*?)'",content)

    debug("downloadSais  sais_list %s"%sais_list, 2)
    #downloadSais(sais_list)
        
def save_downlist(sais_list) :
             
    if xbmcvfs.exists(downListPath) :
        f = open(downListPath, 'r')
        content = f.read()
        f.close()
    else : content = ""
    f = open(downListPath, 'a')                    
    for item_l in sais_list :
        if len(str(content)) !=0 and str(item_l.split("-")[0]) in str(content) :
            f.write(str(item_l))
    f.close()                 
                    

        #debug("verif_tel x_id epi_tel %s %s"%(x_id,epi_tel), 2)
        

def selectQual(mov_ser,m_id,link_id) :
    debug("selectQual selectQual ", 2)
    addon.setSetting('get_links',"true")
    if mov_ser == "serials" or mov_ser == "movies" :
        url = set_streamujtv_info(link_id)
        source = get_url(url)
        data = json.loads(source)
        get_links_mess(data)
        try :
            lang_keys = list(data['URL'].keys()) 
        except Exception as e :
            if len(lang_keys) == 0 :
                raise Exception("could not find any streams")
            return

        info_list = []
        suivi_list = []
        prov = {}
        for i in lang_keys :            
            for x in DUBBING :
                if DUBBING[x] == i.lower() :
                   prov[i] = x
                   continue
        for i in lang_keys :
            qual_keys = list(data['URL'][i].keys())
            
            for j in qual_keys :
                if j != "subtitles" :
                    info_tt = f'[{i}] [{j}] {prov[i].lower()} with sub {list(data["URL"][i]["subtitles"].keys())} v {qual_dic[j]}' if "subtitles" in qual_keys else f'[{i}] [{j}] {prov[i].lower()} v {qual_dic[j]}'
                    info_list.append((i,j,info_tt))


        if len(info_list) == 0 : return None
        for item in DUBBING :
            if len(info_list) == 0 : break
            for i in qual_list :
                for x in info_list :
                    if DUBBING[item].upper() == x[0] and i == x[1] :
                        suivi_list.append((x[0],x[1],x[2]))
                        info_list.remove(x)
                    if len(info_list) == 0 : break

        if len(suivi_list) == 0 : return None                                      
        try :
                answ = dialog.select(translate(30074), [i[2] for i in suivi_list])
        except : return None
        if answ >=0 :
            key1 , key2 , key3 = suivi_list[answ]
            #return (key1 , key2)
            return (key1 , key2, key3)
        else : return None

def selectQual2(mov_ser,link_id) :
    debug("selectQual2  selectQual2 ", 2)
    addon.setSetting('get_links',"true")
    if mov_ser == "serials" or mov_ser == "movies" :
        url = set_streamujtv_info(link_id)
        source = get_url(url)
        data = json.loads(source)
        get_links_mess(data)
        try :
            lang_keys = list(data['URL'].keys())
            debug("selectQual2  lang_keys %s "%lang_keys, 2)
        except Exception as e :
            if len(lang_keys) == 0 :
                raise Exception("could not find any streams")
            return None

        info_list = []
        suivi_list = []
        prov = {}
        for i in lang_keys :            
            for x in DUBBING :
                if DUBBING[x] == i.lower() :
                   prov[i] = x
                   continue
        debug("selectQual2  prov %s "%prov, 2)
        for i in lang_keys :
            qual_keys = list(data['URL'][i].keys())
            
            for j in qual_keys :
                if j != "subtitles" :
                    info_tt = f'[{i}] [{j}] {prov[i].lower()} with sub {list(data["URL"][i]["subtitles"].keys())} v {qual_dic[j]}' if "subtitles" in qual_keys else f'[{i}] [{j}] {prov[i].lower()} v {qual_dic[j]}'
                    info_list.append((i,j,info_tt))
        debug("selectQual2  info_list %s "%info_list, 2)
        if len(info_list) == 0 : return None
        for item in DUBBING :
            if len(info_list) == 0 : break
            for i in qual_list :
                if len(info_list) == 0 : break
                for x in info_list :
                    if DUBBING[item].upper() == x[0] and i == x[1] :
                        suivi_list.append((x[0],x[1],x[2]))
                        info_list.remove(x)
                        debug("selectQual2  suivi_list append %s "%suivi_list, 2)
                    if len(info_list) == 0 : break
                        
        if len(suivi_list) == 0 : return None
        debug("selectQual2  suivi_list fin %s "%suivi_list, 2)
        return suivi_list

def dialSelect(key_list) :                                               
        try :
                answ = dialog.select(translate(30074), [i[2] for i in key_list])
        except : return None
        if answ >=0 :
            key1 , key2 , key3 = suivi_list[answ]
            return (key1 , key2, key3)
        else : return None
            

@plugin.route('/downloadPlug/<mov_ser>/<m_id>/<link_id>')
def downloadPlug(mov_ser,m_id,link_id):
    addon.setSetting('get_links',"true")
    if mov_ser == "serials" or mov_ser == "movies" :
        url = set_streamujtv_info(link_id)
        source = get_url(url)
        data = json.loads(source)
        get_links_mess(data)
        try :
            lang_keys = list(data['URL'].keys()) 
        except Exception as e :
            if len(lang_keys) == 0 :
                raise Exception(translate(30075))
            return

        info_list = []
        suivi_list = []
        prov = {}
        for i in lang_keys :            
            for x in DUBBING :
                if DUBBING[x] == i.lower() :
                   prov[i] = x
                   continue
        for i in lang_keys :
            qual_keys = list(data['URL'][i].keys())            
            for j in qual_keys :
                if j != "subtitles" :
                    info_tt = f'[{i}] [{j}] {prov[i].lower()} with sub {list(data["URL"][i]["subtitles"].keys())} v {qual_dic[j]}' if "subtitles" in qual_keys else f'[{i}] [{j}] {prov[i].lower()} v {qual_dic[j]}'
                    info_list.append((i,j,info_tt))
        if len(info_list) == 0 : return
        for item in DUBBING :
            if len(info_list) == 0 : break
            for i in qual_list :
                if len(info_list) == 0 : break
                for x in info_list :
                    if DUBBING[item].upper() == x[0] and i == x[1] :
                        suivi_list.append((x[0],x[1],x[2]))
                        info_list.remove(x)
                    if len(info_list) == 0 : break

        if len(suivi_list) == 0 : return                                               
        try :
                answ = dialog.select(translate(30074), [i[2] for i in suivi_list])
        except : return
        if answ >=0 :
            key1 , key2 , key3 = suivi_list[answ]
            fich_data = movie_data if mov_ser == "movies" else serial_data
            save_key(fich_data,str(m_id),key1,key2,key3)

            debug("downloadPlug key %s"%key3,2)
            link = data['URL'][key1][key2]
            debug("downloadPlug data %s"%data['URL'],2)
            link_url = get_url(link)
            fileId = str(m_id) + "-" + str(int(time.time()))
            filename = fileId + ".mp4"
            dest =  moviesPath + "/" + filename if mov_ser == "movies" else seriesPath + "/" + filename
            downloadFil(link_url, dest) 
            if ("sub" in key3) and ("subtitles" in data['URL'][key1]) :                     
                subt_url_dict = data['URL'][key1]["subtitles"]
                sub_keys = list(subt_url_dict.keys())
                subt_url = data['URL'][key1]["subtitles"][sub_keys[0]]
                filename = fileId + ".srt"
                dest =  moviesSub + "/" + filename if mov_ser == "movies" else seriesSub + "/" + filename
                subtitle = subs.save_sub(subt_url,dest)
        else : pass
        ##''' le 19-7
        '''
        link = data['URL'][key1][key2]            
        link_url = get_url(link)
        filename = str(m_id) + "-" + str(int(time.time())) + ".mp4"
        dest =  moviesPath + "/" + filename if mov_ser == "movies" else seriesPath + "/" + filename
        downloadFil(link_url, dest)
        '''
    
@plugin.route('/play/<typ_vid>/<stream_id>/<video_id>/<epi_list>')
def play(typ_vid, stream_id, video_id, epi_list):
    global first_dubbing, second_dubbing, stream_man
    addon.setSetting('get_links',"true")
    url = set_streamujtv_info(video_id)
    source = get_url(url)
    data = json.loads(source)
    get_links_mess(data)
    try :
        lang_keys = list(data['URL'].keys()) 
    except Exception as e :
        if len(lang_keys) == 0 :
            raise Exception("could not find any streams")
        return

    qual_keys = list(data['URL'][lang_keys[0]].keys())
    qual_keys_list = []
    for x in range(len(lang_keys)) :
        qual_keys_list.append(list(data['URL'][lang_keys[x]].keys()))                  
    
    link = ""
    quality_index = qual_list.index(quality)
    first_dubbing = first_dubbing.upper()
    second_dubbing = second_dubbing.upper()
    
    if (auto_stream == "true") and (not stream_man) :
        stream_man = False
        if first_dubbing in lang_keys :
            qual_keys = list(data['URL'][first_dubbing].keys())
            if quality in qual_keys :
                link = data['URL'][first_dubbing][quality]
                key1 = first_dubbing
                key2 = quality
            else :
                for i, item in enumerate(qual_list) :
                    if i > quality_index and item in source:
                        link = data['URL'][first_dubbing][item]
                        if link :
                            key1 = first_dubbing
                            key2 = item
                            break

        elif second_dubbing in lang_keys  :
            qual_keys = list(data['URL'][second_dubbing].keys())
            if quality in qual_keys :
                link = data['URL'][second_dubbing][quality]
                key1 = second_dubbing
                key2 = quality
            else :
                for i, item in enumerate(qual_list) :
                    if i > quality_index and item in source :
                        link = data['URL'][second_dubbing][item]
                        if link :
                            key1 = second_dubbing
                            key2 = item
                            break

        else :
            if quality in source :
                for x in range(len(lang_keys)) :
                    qual_keys = list(data['URL'][lang_keys[x]].keys())
                    if quality in qual_keys :
                        link = data['URL'][lang_keys[0]][quality]
                        key1 = lang_keys[0]
                        key2 = quality
                        break
            else :
                for i, item in enumerate(qual_list) :
                    if i > quality_index and item in source:
                        
                        link = data['URL'][lang_keys[0]][item]
                        if link :
                            key1 = lang_keys[0]
                            key2 = item
                           
                            break
                if not link :
                    dialog.ok("info",translate(30075))
                    return

    else :
        stream_man = False
        info_list = []
        suivi_list = []
        prov = {}
        for i in lang_keys :            
            for x in DUBBING :
                if DUBBING[x] == i.lower() :
                   prov[i] = x
                   continue
        for i in lang_keys :
            qual_keys = list(data['URL'][i].keys())
            
            for j in qual_keys :
                if j != "subtitles" :
                    try :
                        info_tt = f'[{i}] [{j}] {prov[i].lower()} with sub {list(data["URL"][i]["subtitles"].keys())} v {qual_dic[j]}' if "subtitles" in qual_keys else f'[{i}] [{j}] {prov[i].lower()} v {qual_dic[j]}'
                        info_list.append((i,j,info_tt))
                    except Exception as e :
                        debug("Play info_list error %s"%str(e), 2)

        if len(info_list) == 0 : return
        for item in DUBBING :
            if len(info_list) == 0 : break
            for i in qual_list :
                if len(info_list) == 0 : break
                for x in info_list :
                    if DUBBING[item].upper() == x[0] and i == x[1] :
                        suivi_list.append((x[0],x[1],x[2]))
                        info_list.remove(x)
                    if len(info_list) == 0 : break

        if len(suivi_list) == 0 : return                                               
        try :
                answ = dialog.select(translate(30074), [i[2] for i in suivi_list])
        except : return
        if answ >=0 :
            key1 , key2 , key3 = suivi_list[answ]
            link = data['URL'][key1][key2]
        else : return

    link_url = get_url(link)
    if ("subtitles" in source) and (auto_subtitles == "true") :                     
        # Wait for stream to start
        if "subtitles" in data['URL'][key1] :
                subt_url_dict = data['URL'][key1]["subtitles"]
                sub_keys = list(subt_url_dict.keys())
                subt_url = data['URL'][key1]["subtitles"][sub_keys[0]]
                subtitle = subs.get_subtitles(subt_url,1)
        else : subtitle = None
    else : subtitle = None

    play_list = []
    url = set_sosac_info("id",**{'arg2':stream_id}) if typ_vid == "movies" else set_sosac_ser("",**{'arg2':stream_id,'arg3':"episodes",'arg4':""})
    source = get_url(url)
    data = json.loads(source)
    start_from = data["w"]
    tot_time = data["dl"]
    title1 = ""
    if typ_vid != "movies" :
        eps = str(data["ep"]) if len(str(data["ep"])) > 1 else "0" + str(data["ep"])
        sas = str(data["s"]) if len(str(data["s"])) > 1 else "0" + str(data["s"])
        title1 = " - " + sas + "x" + eps  

    title = data["n"]["cs"][0] if type(data["n"]["cs"]) == type([]) else data["n"]["cs"]
    title = title + title1
    li = ListItem(title)
    epilist = re.findall("(\d+)[,|\]]",epi_list)
    play_list.append((typ_vid, stream_id, link_url, start_from, tot_time, subtitle, title))
    if next_episode == "true" and len(epilist) !=0 :
        index = 1
        for x in epilist :
            try :
                index +=1
                url = set_sosac_info("id",**{'arg2':x}) if typ_vid == "movies" else set_sosac_ser("",**{'arg2':x,'arg3':"episodes",'arg4':""})
                source = get_url(url)
                data = json.loads(source)
                estart_from = data["w"]
                etot_time = data["dl"]
                title1 = ""
                if typ_vid != "movies" :
                    eps = str(data["ep"]) if len(str(data["ep"])) > 1 else "0" + str(data["ep"])
                    sas = str(data["s"]) if len(str(data["s"])) > 1 else "0" + str(data["s"])
                    title1 = " - " + sas + "x" + eps  
                etitle = data["n"]["cs"][0] if type(data["n"]["cs"]) == type([]) else data["n"]["cs"]
                etitle = etitle + title1
                url = set_streamujtv_info(data["l"])
                source = get_url(url)
                data = json.loads(source)
                get_links_mess(data)
                debug("play play_list  data %s  "%data, 2)
                debug("play play_list  key1 key2 %s %s  "%(key1,key2), 2)
                link = data['URL'][key1][key2]
                elink_url = get_url(link)
                if ("subtitles" in source) and (auto_subtitles == "true") :
                    try :
                        if "subtitles" in data['URL'][key1] :
                            subt_url_dict = data['URL'][key1]["subtitles"]
                            sub_keys = list(subt_url_dict.keys())
                            subt_url = data['URL'][key1]["subtitles"][sub_keys[0]]
                            esubtitle = subs.get_subtitles(subt_url,index)
                        else : esubtitle = None
                    except Exception as e :
                       debug("play play_list  load subtitle %s  "%e, 2)
                       esubtitle = None
                else : esubtitle = None
                play_list.append(("episodes", x, elink_url, estart_from, etot_time, esubtitle, etitle))
            except Exception as e :
                debug("exception playlist append error  %s"%e, 2)

        sv = cPlayerList2(play_list) 
        sv.start()


    elif next_episode == "false" or typ_vid == "movies" or len(epilist) ==0:
        sv = cPlayer(play_list,"auto")
        sv.runs()
        '''
        if addon.getSetting('search-menu') == "search" :
            search_str = addon.getSetting('search-str')
            xbmc.executebuiltin("RunScript(plugin://plugin.video.sosac-2/categories?query=search&query1=%s&query2=1)"%search_str)
        #xbmc.executebuiltin('Container.Refresh')
        #xbmc.executebuiltin("RunScript(plugin://plugin.video.sosac-2/tvshows)")
        '''
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/streammanu/<typ_vid>/<stream_id>/<video_id>') 
def streammanu(typ_vid,stream_id,video_id):
    global first_dubbing, second_dubbing, stream_man
    #debug("streammanu passe ", 2)
    addon.setSetting('get_links',"true")
    url = set_streamujtv_info(video_id)
    source = get_url(url)
    data = json.loads(source)
    get_links_mess(data)
    try :
        lang_keys = list(data['URL'].keys()) 
    except Exception as e :
        if len(lang_keys) == 0 :
            raise Exception(translate(30075))
        return

    qual_keys = list(data['URL'][lang_keys[0]].keys())
    qual_keys_list = []
    for x in range(len(lang_keys)) :
        qual_keys_list.append(list(data['URL'][lang_keys[x]].keys()))                  
    
    link = ""
    quality_index = qual_list.index(quality)
    first_dubbing = first_dubbing.upper()
    second_dubbing = second_dubbing.upper()
    
    try :
        stream_man = False
        info_list = []
        suivi_list = []
        prov = {}
        for i in lang_keys :            
            for x in DUBBING :
                if DUBBING[x] == i.lower() :
                   prov[i] = x
                   continue
        for i in lang_keys :
            qual_keys = list(data['URL'][i].keys())
            
            for j in qual_keys :
                if j != "subtitles" :
                    info_tt = f'[{i}] [{j}] {prov[i].lower()} with sub {list(data["URL"][i]["subtitles"].keys())} v {qual_dic[j]}' if "subtitles" in qual_keys else f'[{i}] [{j}] {prov[i].lower()} v {qual_dic[j]}'
                    info_list.append((i,j,info_tt))

        if len(info_list) == 0 : return
        for item in DUBBING :
            if len(info_list) == 0 : break
            for i in qual_list :
                if len(info_list) == 0 : break
                for x in info_list :
                    if DUBBING[item].upper() == x[0] and i == x[1] :
                        suivi_list.append((x[0],x[1],x[2]))
                        info_list.remove(x)
                    if len(info_list) == 0 : break

        if len(suivi_list) == 0 : return                                       
        try :
                answ = dialog.select(translate(30074), [i[2] for i in suivi_list])
        except : return
        if answ >=0 :
            key1 , key2 , key3 = suivi_list[answ]
            link = data['URL'][key1][key2]            
            link_url = get_url(link)
            if ("subtitles" in source) and (auto_subtitles == "true") :                     
                if "subtitles" in data['URL'][key1] :
                        subt_url_dict = data['URL'][key1]["subtitles"]
                        sub_keys = list(subt_url_dict.keys())
                        subt_url = data['URL'][key1]["subtitles"][sub_keys[0]]
                        subtitle = subs.get_subtitles(subt_url,1)
                else : subtitle = None
            else : subtitle = None

            url = set_sosac_info("id",**{'arg2':stream_id}) if typ_vid == "movies" else set_sosac_ser("",**{'arg2':stream_id,'arg3':"episodes",'arg4':""})
            source = get_url(url)
            data = json.loads(source)
            start_from = data["w"]
            tot_time = data["dl"]
            title1 = ""
            if typ_vid != "movies" :
                eps = str(data["ep"]) if len(str(data["ep"])) > 1 else "0" + str(data["ep"])
                sas = str(data["s"]) if len(str(data["s"])) > 1 else "0" + str(data["s"])
                title1 = " - " + sas + "x" + eps
            title = data["n"]["cs"][0] if type(data["n"]["cs"]) == type([]) else data["n"]["cs"]
            title = title + title1
            li = ListItem(path=str(link_url))
            li = ListItem(title)
            li.setProperty('IsPlayable', 'true')
            li.setInfo(type = "Video", infoLabels = {"Title": "", "Plot": "" } )
            play_list = []
            play_list.append((typ_vid, stream_id, link_url, start_from, tot_time, subtitle, title))
            #sv = cPlayer(play_list,"manu")
            sv = cPlayerMan(play_list,"manu")
            sv.runm() #sv.runs() #
    except Exception as e:
        debug("playvid error %s"%e,2)

    #endOfDirectory(plugin.handle)
    xbmcplugin.endOfDirectory(plugin.handle, succeeded=False, cacheToDisc=False)

def upd_download(del_day) :
    dir_list , fil_list = xbmcvfs.listdir(seriesPath)
    debug("upd_download download dir dir_list %s"%dir_list, 2)
    notify(translate(30402),translate(30161),time=5000)
    for x in dir_list : 
        sais_list = []
        if ("Season" not in x) :
            epi_tel = 0 
            x_id = x.split("_")[-1]
            url = set_sosac_epi(x_id)
            source = get_url(url)
            data = json.loads(source)
            sais_nb = data['info']['z']
            epi_nb = data['info']['v']
            #debug("verif_tel x_id sais_nb epi_nb %s %s %s"%(x_id,sais_nb,epi_nb), 2)
            dir_name = os.path.join(seriesPath,x)
            debug("verif_tel x_id dir_name %s"%(dir_name), 2)
            dir_listx , fil_listx = xbmcvfs.listdir(dir_name)
            debug("upd_download x_id fil_listx %s"%(fil_listx), 2)
            if len(dir_listx) == 0 :
                epi_tel = epi_tel + len(fil_listx)
                if epi_tel != epi_nb and sais_nb == 1:
                    id_list = [data["1"][item]["_id"] for item in data["1"]]
                    debug("upd_download x_id id_list %s"%(id_list), 2)
                    ex_list = []
                    for fil in fil_listx :
                        fil_item = fil.split("-")[0]
                        debug("upd_download x_id fil_item %s"%(fil_item), 2)
                        if int(fil_item) in id_list :
                            id_list.remove(int(fil_item))
                            ex_list.append(fil_item)
                    debug("upd_download x_id id_list reste  %s"%(id_list), 2)
                    if len(id_list) == 0 : continue
                    prepa_list(x_id, data, "1", id_list, dir_name, ex_list)

            else :    
                for item_dir in dir_listx :
                    if "Season"  in item_dir :
                        dir_namex = os.path.join(dir_name,item_dir)
                        debug("upd_download x_id dir_namex %s"%(dir_namex), 2)
                        dir_listy , fil_listy = xbmcvfs.listdir(dir_namex)
                        epi_tel = epi_tel + len(fil_listy)
                        ss_nb1 = item_dir.split("_")[0]
                        ss_nb = ss_nb1.split("-")[1]
                        ss_epi = list(data[ss_nb].keys())
                        if len(fil_listy) == len(ss_epi) : continue
                        id_list = [data[ss_nb][item]["_id"] for item in data[ss_nb]]
                        debug("upd_download x_id id_list %s"%(id_list), 2)
                        ex_list = []
                        for fil in fil_listy :
                            fil_item = fil.split("-")[0]
                            debug("upd_download x_id fil_item %s"%(fil_item), 2)
                            if int(fil_item) in id_list :
                                id_list.remove(int(fil_item))
                                ex_list.append(fil_item)
                        debug("upd_download x_id id_list reste  %s"%(id_list), 2)
                        if len(id_list) == 0 : continue
                        prepa_list(x_id, data, ss_nb, id_list, dir_namex, ex_list)
                        #debug("downserial saison sais_list %s"%sais_list, 2)
                    else: 
                        epi_tel = epi_tel + len(fil_listx)
        elif "Season"  in x :
            #Simpsonovi---Season-1_141
            x_id = x.split("_")[-1]
            url = set_sosac_epi(x_id)
            source = get_url(url)
            data = json.loads(source)
            sais_sp = x.split("_")[0]
            ss_nb = sais_sp.split("-")[-1]
            ss_epi = list(data[ss_nb].keys())
            dir_name = os.path.join(seriesPath,x)
            debug("verif_tel x_id dir_name %s"%(dir_name), 2)
            dir_listx , fil_listx = xbmcvfs.listdir(dir_name)
            epi_tel = len(fil_listx)
            if len(fil_listx) == len(ss_epi) : continue
            id_list = [data[ss_nb][item]["_id"] for item in data[ss_nb]]
            debug("upd_download x_id id_list %s"%(id_list), 2)
            ex_list = []
            for fil in fil_listx :
                fil_item = fil.split("-")[0]
                debug("upd_download x_id fil_item %s"%(fil_item), 2)
                if int(fil_item) in id_list :
                    id_list.remove(int(fil_item))
                    ex_list.append(fil_item)
            debug("upd_download x_id id_list reste  %s"%(id_list), 2)
            if len(id_list) == 0 : continue
            prepa_list(x_id, data, ss_nb, id_list, dir_name, ex_list)            
            
    sais_list = []
    if xbmcvfs.exists(downListPath) :
        with open(downListPath, 'r',encoding="utf-8") as f :
            content = f.read()
        sais_list = re.findall("(?s)'(https.*?)'.*?'(.*?)'",content)
            
    debug("upd_download downloadSais  sais_list %s"%sais_list, 2)
    #notify(translate(200),translate(30279),time=5000)
    if len(sais_list) != 0 : downloadSais(sais_list)

def downloadSais(vid_list):
    thread_act = threading.enumerate()
    debug("Main thread name: {}".format(threading.current_thread().name),2)
    initial = threading.active_count()
    for item in vid_list :
        debug("downloadSais item[1] %s"%(item[1]), 2)
        downloadFil2(item[0], item[1])
        start_ti = time.time()        
        while time.time() - start_ti < 5.0 :
                a = 1
        #debug("nombre de download %s"%(threading.active_count() - initial), 2)

    thread_act = threading.enumerate()
    debug("downloadSais threading.enumerate %s"%thread_act, 2)
    endOfDirectory(plugin.handle)

def run():
    plugin.run()

