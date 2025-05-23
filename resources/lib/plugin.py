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
from . import subs
from resources.lib.player import *

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
        z = 0
        for i in item['n'] :
            if i != "cs" :
                z += 1
                title = item['n'][i][0] if type(item['n'][i]) == type([]) else item['n'][i]
                img = f"special://home/addons/plugin.video.sosac-2/resources/images/languages/{i}.png"
                li.setProperty('titre'+str(z), str(title))
                li.setProperty('image'+str(z), img)

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
    
    # generate the list of movies 
    if letype == "movies" :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        SOSAC_IMAGE = SOSAC_MOVIES
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

                url = plugin.url_for(play, "movies", item["_id"], item["l"], [])
                addDirectoryItem(plugin.handle, url, li, False)

            except Exception as e :
                debug("show_plug_list movies error %s"%e, 2)

        # add item for next page list
        quer, quer1, page = re.findall("query=(.*?)&.*?=(.*?)&.*?=(\d+)",sys.argv[2])[0] 
        debug("show_plug_list movies page %s %s %s"%(quer, quer1, page), 2)
        quer2 = int(page) + 1
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

    # generate the list of  tvshows 
    elif letype == "serials" :
        SOSAC_IMAGE = SOSAC_SERIES
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        for i, item in enumerate(items):
            try :
                title = item["n"]["cs"][0]
                li = ListItem(str(title))
                set_common_properties(item, li)
                li.setInfo('video', {
                    'title': title,
                    'count': i,
                    'mediatype': 'tvshow'})
                url = plugin.url_for(cat_epi, query=item["_id"], query1 ="0", query2=None,query3=None)
                addDirectoryItem(plugin.handle, url, li, True)
            except Exception as e :
                debug("show_plug_list serials error %s"%e, 2)
                pass

        # add item for next page list
        quer, quer1, quer2, quer3, page = re.findall("query=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(\d+)",sys.argv[2])[0] #.replace("?","").replace("&",",")
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

    # generate list of saisons and episodes for a tvshow 
    elif letype == "episodes" :
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        SOSAC_IMAGE = SOSAC_SERIES
        saison = list(items.keys())
        # case just 1 saison prepare list of episodes to be played
        if (len(saison) == 2) and ( 'info' in saison ) :
            episodes = list(items[saison[0]].keys())            
            playList = []
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
                    url = plugin.url_for(play, "episodes", x["_id"], x["l"],playList)
                    addDirectoryItem(plugin.handle, url, li, False)
                except Exception as e :
                    debug("show_plug_list 1 saison error %s"%e, 2)

            xbmc.executebuiltin("Container.SetViewMode(%s)" % "505")
            endOfDirectory(plugin.handle)

        # case more than 1 saison prepare list of episodes for a saison to be played 
        if (len(saison) > 2) and (int(epi_id) >= 1 ) :
            xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
            SOSAC_IMAGE = SOSAC_SERIES
            episodes = list(items[str(epi_id)].keys())
            playList = []
            sai_nb = str(epi_id) if len(epi_id) > 1 else "0" + str(epi_id)                    
            for i, item in enumerate(episodes) :
                x  = items[str(epi_id)][item]
                playList.append(x["_id"])                   

            for i, item in enumerate(episodes):
                try :
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

                    if x["_id"] in playList : playList.remove(x["_id"])
                    url = plugin.url_for(play, "episodes", x["_id"], x["l"], playList)
                    addDirectoryItem(plugin.handle, url, li, False)
                except Exception as e :
                    debug("show_plug_list saison & episodes error %s"%e, 2)

            xbmc.executebuiltin("Container.SetViewMode(%s)" % "CWideList")
            endOfDirectory(plugin.handle)
            
        # case a tvshow have more than 1 saison , will list the saisons
        elif len(saison) > 2 :
            SOSAC_IMAGE = SOSAC_SERIES
            xbmcplugin.setContent(int(sys.argv[1]), 'seasons')
            xinfo  = items['info']
            for ind, item in enumerate(items):
                try :
                    if item  == "info" : continue
                    title = xinfo["n"]["cs"]
                    li = ListItem(str(title[0]))
                    saititle = translate(30283)+ " " + item #str(ind+1)
                    saititle1 = "Season " + item #str(ind+1)
                    li.setProperty('saititle',saititle)
                    set_common_properties(items['info'], li, "epi_prop")
                    if start  :
                        li.setProperty('startime',start)
                        li.setProperty('station',stat)
                                

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
                    
                    url = plugin.url_for(cat_epi, query = xinfo["_id"], query1=item,query2=start,query3=stat)
                    addDirectoryItem(plugin.handle, url, li, True)
                except Exception as e :
                    debug("show_plug_list saison error %s"%e, 2)

            xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)     
            xbmc.executebuiltin("Container.SetViewMode(%s)" % "507")
            endOfDirectory(plugin.handle)

    # case a tvshow is one of this "last-added","news-with-dubbing", "news-with-subtitles" 
    elif letype == "episodes3" :
        SOSAC_IMAGE = SOSAC_SERIES
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
                    
                url = plugin.url_for(play, "episodes", item["_id"], item["l"] if item["l"] != None else "", [])
                addDirectoryItem(plugin.handle, url, li, False)
            except Exception as e :
                debug("show_plug_list episodes2 error %s"%e, 2)

              
        quer, quer1, quer2, quer3, page = re.findall("query=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(.*?)&.*?=(\d+)",sys.argv[2])[0] #.replace("?","").replace("&",",")
        if epi_id == "1" :
            quer1=start
            quer2=stat    
        quer4 = int(page) + 1
        url = set_sosac_ser(quer,**{'arg2':quer1,'arg3':quer2,'arg4':quer3,'arg5':quer4})
        source = get_url(url)
        res = json.loads(source)
        if len(res) != 0 :
            url = plugin.url_for(cat_ser, query=quer,query1=quer1,query2=quer2,query3=quer3,query4=quer4)
            addDirectoryItem(plugin.handle, url,ListItem(translate(30294)), True)
        
        endOfDirectory(plugin.handle)
        xbmc.sleep(100)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % "506")
        #xbmc.executebuiltin("Container.Refresh")



@plugin.route('/')
def index():
    source = get_url(domain_actif)
    data = json.loads(source)
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
    addDirectoryItems(plugin.handle, items)
    xbmc.executebuiltin("Container.SetViewMode(%s)" % "508")
    endOfDirectory(plugin.handle)

@plugin.route('/movies')
def movies():
    items = []
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

@plugin.route('/settings')
def settings():
    addon.openSettings("main")
            
@plugin.route('/categories')
def categories():
    fl_sortie = False
    fl_video = False

    try :
        query = plugin.args["query"][0]
    except KeyError  :
        return

    query1 = plugin.args["query1"][0]
    query2 = plugin.args["query2"][0]
    url = set_sosac_info(query,**{'arg2':query1,'arg3':query2})
    source = get_url(url)
    res = json.loads(source)
    if "current-topic" == query : 
        show_plug_list("movies", "current_topic", res)
    else : show_plug_list("movies", "0", res)

    endOfDirectory(plugin.handle) 

@plugin.route('/cat_ser')
def cat_ser():
    fl_date = False
    try :
        query = plugin.args["query"][0]
    except KeyError  :
        return
    query1 = plugin.args["query1"][0]
    try :
        query2 = "" if not plugin.args["query2"][0] else plugin.args["query2"][0]
        query3 = "" if not plugin.args["query3"][0] else plugin.args["query3"][0]
        query4 = "" if not plugin.args["query4"][0] else plugin.args["query4"][0]
    except Exception as e :
        debug("cat_ser error %s"%e,2)


    if True:
        url = set_sosac_ser(query,**{'arg2':query1,'arg3':query2,'arg4':query3,'arg5':query4})
        source = get_url(url)
        res = json.loads(source)
        new_epi = ["last-added","news-with-dubbing", "news-with-subtitles"]
        if (query in  new_epi) and (query2 == "episodes")  :
            show_plug_list("episodes3","2", res)
        elif (query ==  "by-date") :
            show_plug_list("episodes3","2", res, start=query1, stat=query2) #start et stat pour avoir la page 2 et plus
        else : show_plug_list("serials","0", res)

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
    if ep_id == "0" : #not station  :
        show_plug_list("episodes", ep_id, res, start=startime, stat=station)
    elif station == "None" : show_plug_list("episodes", ep_id, res, start=startime, stat=station)
    else : show_plug_list("epi_tvguide", ep_id, res, start=startime, stat=station)




    
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

    if next_episode == "false" or typ_vid == "movies" or len(epilist) ==0:
        sv = cPlayer(play_list,"auto")
        sv.runs()
    xbmcplugin.endOfDirectory(plugin.handle)


def run():
    plugin.run()

