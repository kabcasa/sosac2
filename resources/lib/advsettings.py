import os, re, shutil
import xbmcvfs
from resources.lib.util import *

advFile = xbmcvfs.translatePath(os.path.join(libPath,"advancedsettings.xml"))


settings_sub = "<video> \n\
    <playcountminimumpercent>101</playcountminimumpercent> \n\
    <ignoresecondsatstart>10800</ignoresecondsatstart>"

settings_sub2 = "<advancedsettings> \n\
    <video> \n\
    <playcountminimumpercent>101</playcountminimumpercent> \n\
    <ignoresecondsatstart>10800</ignoresecondsatstart> \n\
    </video>"


def writeAdvanced():
        if not xbmcvfs.exists(ADVANCEDSETTINGS):
                #with open(ADVANCEDSETTINGS, "w") as f :
                #        f.write("")
                try :
                        shutil.copy(advFile, ADVANCEDSETTINGS)
                except Exception as e :
                    debug("adv error  %s"%e, 2)    
                return
        else  :
            with open(ADVANCEDSETTINGS, 'r') as f:
                    content = f.read()

            if "<video>" in content : 
                try : 
                    match = re.findall('(?s)<video>(.*?)</video>',content)[0]
                except IndexError:
                    match = None
                    debug("adv match error ", 2)                
                

                if ("playcountminimumpercent" in match ) or ("ignoresecondsatstart" in match) :
                    return    
                else :
                    content = content.replace('<video>',settings_sub)
                    with open(ADVANCEDSETTINGS, 'w') as f:
                        f.write(content)
                    return
            else :                
                content = content.replace('<advancedsettings>',settings_sub2)
                with open(ADVANCEDSETTINGS, 'w') as f:
                    f.write(content)
                return

if __name__ == '__main__':
    writeAdvanced()
