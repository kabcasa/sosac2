# -*- coding: utf-8 -*-
# Copyright: (c) 2020, SylvainCecchetto, wwark
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)


import xbmc, xbmcaddon, xbmcvfs, xbmcgui
import os, json, requests, re
from xbmcgui import ListItem

from resources.lib.util import *
from resources.lib.playback_history import *
from resources.lib.advsettings import writeAdvanced
from resources.lib import extract

addon_id = 'plugin.video.sosac-2'
addon_name_ = translate(30402)
addon = xbmcaddon.Addon(addon_id)
addonPath = xbmcvfs.translatePath(addon.getAddonInfo('path'))
addonsPath = xbmcvfs.translatePath('special://home/addons')

languagePathEn = xbmcvfs.translatePath(os.path.join(addonPath, "resources","language","resource.language.en_gb","strings.po"))
languagePathCZ = xbmcvfs.translatePath(os.path.join(addonPath, "resources","language","resource.language.cs_cz","strings.po"))
languagePathCZ2 = xbmcvfs.translatePath(os.path.join(addonPath, "resources","language","resource.language.cs_cz","strings2.po"))


try:
    version = xbmc.getInfoLabel('system.buildversion')
    skinVer = "skin.estuary-sosac-3.0.0.zip"
    '''
    if version[0:2] == '20':
        skinVer = "skin.estuary-sosac-20.zip"
    elif version[0:2] == '19':
        skinVer = "skin.estuary-sosac-19.zip"
    else:
        skinVer = "skin.estuary-sosac-20.zip"
    '''
    endN = skinVer[:18] + ".zip"
    skinVer = os.rename(skinVer,endN)
except:
    xbmc.log("skin install didn't find right version ")
    
skinzipPath = xbmcvfs.translatePath(os.path.join(addonPath, "resources","extras",skinVer))
skinPath = xbmcvfs.translatePath(os.path.join(addonsPath, "skin.estuary-sosac/"))

DOMAIN = ["https://kodi-api.sosac.to/settings","https://tv.sosac.ph/settings.json","https://sosac.eu/settings.json",
    "https://tv.prehraj.net/settings.json","https://tv.pustsi.me/settings.json","https://www.tvserialy.net/settings.json",
        "http://178.17.171.217/settings.json"]

def autorun_addon():
    xbmc.log('Autorun_addon 1%s'%xbmcaddon.Addon().getSetting("start-boot"))
    if int(xbmcaddon.Addon().getSetting("start-boot")) == 0:
        xbmc.executebuiltin('RunAddon(plugin.video.sosac-2)')
        xbmc.log('Autorun_addon 2')
    return

def skin_install() :
    try :
        if not xbmcvfs.exists(skinPath) :
            extract.allNoProgress(skinzipPath,addonsPath)
            xbmc.log("start passe par install ", xbmc.LOGDEBUG)
            count = 0
            while not xbmcvfs.exists(skinPath) :
                xbmc.sleep(100)
                count += 1
                if count > 1000 :
                    break

            xbmc.executebuiltin('EnableAddon("skin.estuary-sosac")')
            diag_YN = xbmcgui.Dialog().yesno(translate(30402), translate(30406), nolabel=translate(30407),yeslabel=translate(30408))
            if diag_YN ==1 : xbmc.executebuiltin('Quit')
            
    except Exception as e :
        xbmc.log("start error %s"%str(e), xbmc.LOGDEBUG)


    try :
        xbmc.log("skin install xbmcvfs.exists(skinPath) %s"%xbmcvfs.exists(skinPath), xbmc.LOGDEBUG)
        if xbmcaddon.Addon().getSetting("skin_enabled") == "false" and xbmcvfs.exists(skinPath) :
            addonData = '{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","params":{"addonid":"skin.estuary-sosac"},"id":1}'
            response = xbmc.executeJSONRPC(addonData)
            response = json.loads(response)
            xbmc.log("skin install enable response %s"%response, xbmc.LOGDEBUG)

            autoEnable = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"skin.estuary-sosac","enabled":true},"id":1}'
            response = xbmc.executeJSONRPC(autoEnable)
            response = json.loads(response)
            xbmc.log("skin_install response %s"%response, xbmc.LOGDEBUG)
            if "error" not in response  :
                xbmcaddon.Addon().setSetting("skin_enabled","true")
                #diag_YN = xbmcgui.Dialog().yesno(translate(30402), translate(30406), nolabel=translate(30407),yeslabel=translate(30408))
                #if diag_YN ==1 : xbmc.executebuiltin('Quit')
        else :
            xbmc.log("skin_install skinPath not exist ", xbmc.LOGDEBUG)
    except Exception as e :
        xbmc.log("skin install  error %s"%str(e), xbmc.LOGDEBUG)


def skin_setting() :
    json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettings","params":{"level":"advanced"}}'))    
    settings = json_response['result']['settings']
    xbmc.log('service settings %s'%settings)
    json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettingValue","params":{"setting":"lookandfeel.skin"}}'))    
    xbmc.log('service settings %s'%json_response)
    xbmcaddon.Addon().setSetting("skin",json_response['result']['value'])
    skindir = xbmc.getSkinDir()
    xbmc.log('service skindir %s'%skindir)

def clear_cache():
        xbmc.log('CLEAR CACHE ACTIVATED')
        xbmc_cache_path = os.path.join(xbmcvfs.translatePath('special://home'), 'userdata','Database')
	
        if os.path.exists(xbmc_cache_path) :
            dirs, files = xbmcvfs.listdir(xbmc_cache_path)
            for fil_item in files :
                if fil_item[:8] == "MyVideos" :
                    ccache = PlaybackHistory(os.path.join(xbmc_cache_path,fil_item))
                    ccache.clear()
                    xbmc.log('CLEAR CACHE clear MyVideos ')

def domain_save() :
    for item in DOMAIN :
        try :
            source = requests.get(item)
            data = json.loads(source.text)
            xbmc.log("domain_save data %s"%data)
            if (data["domain"] != "") and (data["streaming_provider"] != "") :
                xbmcaddon.Addon().setSetting("sosac_domain",data["domain"])
                xbmcaddon.Addon().setSetting("streaming_provider",data["streaming_provider"])
                xbmcaddon.Addon().setSetting("domain_actif",item)
                break
        except Exception as e:
            xbmc.log('domain_save error exception %s'%e)
            pass

    if len(data) > 0 :
        with open(languagePathEn ,"r") as f :
            strinspo = f.read()

        vsteamtv_label = re.findall('(?s)msgctxt "#30200".*?msgid.*?"(.*?) User',strinspo)[0]
        vsosac_label = re.findall('(?s)msgctxt "#30202".*?msgid.*?"(.*?) User',strinspo)[0]
        if vsteamtv_label != data["streaming_provider_label"] :
            strinspo2 = strinspo.replace(vsteamtv_label,data["streaming_provider_label"])
        else : strinspo2 = strinspo
        if vsosac_label != data["domain_label"] :
            strinspo3 = strinspo2.replace(vsosac_label,data["domain_label"])
        else : strinspo3 = strinspo2
        pat1 = 'Account with this username and password does not exist on .*?"'
        rpat1 = 'Account with this username and password does not exist on %s"'%data["domain"]
        vsub1 = re.sub(pat1,rpat1,strinspo3)
        pat1 = 'User account with this username and password does not exist on .*?"'
        rpat1 = 'User account with this username and password does not exist on %s"'%data["streaming_provider"]
        vsub2 = re.sub(pat1,rpat1,vsub1)
        with open(languagePathEn ,"w") as f :
            f.write(vsub2)

        with open(languagePathCZ ,"r",encoding="utf-8") as f :
            strinspo = f.read()
        try :
            vsteamtv_label = re.findall('(?s)msgctxt "#30200".*?msgid.*?"(.*?) User',strinspo)[0]
            vsosac_label = re.findall('(?s)msgctxt "#30202".*?msgid.*?"(.*?) User',strinspo)[0]
            if vsteamtv_label != data["streaming_provider_label"] :
                strinspo2 = strinspo.replace(vsteamtv_label,data["streaming_provider_label"])
            else : strinspo2 = strinspo
            if vsosac_label != data["domain_label"] :
                strinspo3 = strinspo2.replace(vsosac_label,data["domain_label"])
            else : strinspo3 = strinspo2
        except Exception as e:
            xbmc.log('domain_save modif strings.po error exception 1 %s'%e)

        try :
            pat1 = 'Account with this username and password does not exist on .*?"'
            rpat1 = 'Account with this username and password does not exist on %s"'%data["domain"]
            vsub1 = re.sub(pat1,rpat1,strinspo3)
        except Exception as e:
            xbmc.log('domain_save modif strings.po error exception 2 %s'%e)

        try :
            pat1 = 'User account with this username and password does not exist on .*?"'
            rpat1 = 'User account with this username and password does not exist on %s"'%data["streaming_provider"]
            vsub2 = re.sub(pat1,rpat1,vsub1)
        except Exception as e:
            xbmc.log('domain_save modif strings.po error exception 3 %s'%e)

        try :
            pat1 = 'Pro neomezené přehrávání si prosím prodlužte premium na .*?/premium."'
            rpat1 = 'Pro neomezené přehrávání si prosím prodlužte premium na %s/premium."'%data["streaming_provider"]
            vsub3 = re.sub(pat1,rpat1,vsub2)
        except Exception as e:
            xbmc.log('domain_save modif strings.po error exception 4 %s'%e)

        try :
            pat1 = 'Heslo si můžete obnovit na .*?/recoverpassword'
            rpat1 = 'Heslo si můžete obnovit na %s/recoverpassword'%data["streaming_provider"]
            vsub4 = re.sub(pat1,rpat1,vsub3)
        except Exception as e:
            xbmc.log('domain_save modif strings.po error exception 5 %s'%e)

        try :
            pat1 = 'Heslo si můžete obnovit na .*?_'
            rpat1 = 'Heslo si můžete obnovit na %s_'%data["domain"]
            vsub5 = re.sub(pat1,rpat1,vsub4)
        except Exception as e:
            xbmc.log('domain_save modif strings.po error exception 6 %s'%e)

        with open(languagePathCZ ,"w",encoding="utf-8") as f :
            f.write(vsub5)
        

    
        

if __name__ == '__main__':

    domain_save()
    autorun_addon()
    skin_install()

    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        plugin_name = xbmc.getInfoLabel('Container.PluginName')
        skindir = xbmc.getSkinDir()
        if "sosac-2" in plugin_name and skindir != "skin.estuary-sosac":
            xbmcaddon.Addon().setSetting("skin",skindir)
            skin_set = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.SetSettingValue","params":{"setting":"lookandfeel.skin","value":"skin.estuary-sosac"}}'))
            #xbmc.executebuiltin('Reboot')
        elif (plugin_name != "") and ("sosac-2" not in plugin_name):
            last_skin = '"%s"'%(xbmcaddon.Addon().getSetting("skin"))
            if skindir == "skin.estuary-sosac" and last_skin != "skin.estuary-sosac":                
                skin_set = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.SetSettingValue","params":{"setting":"lookandfeel.skin","value":%s}}'%last_skin))
                #xbmc.executebuiltin('Reboot')


        if monitor.waitForAbort(1):
            break
