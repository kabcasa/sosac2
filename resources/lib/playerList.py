# -*- coding: utf-8 -*-
import sys, json, threading
import xbmcplugin
import xbmc
from xbmcgui import ListItem
import routing
from resources.lib.util import *

# pour les sous titres
# https://github.com/amet/service.subtitles.demo/blob/master/service.subtitles.demo/service.py
# player API
# http://mirrors.xbmc.org/docs/python-docs/stable/xbmc.html#Player

plugin = routing.Plugin()

class cPlayerList2(xbmc.Player):

    def __init__(self, play_list):

        xbmc.Player.__init__(self)
        self.playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        self.playlist.clear()
        self.last_cur = 0
        self.play_list = play_list
        self.old_id = 0
        self.fl_id = False
        self.posL = 0
        #self.playBackEnd = False
        self.totalTime = 0
        self.played = []
        if len(self.playlist) == 0 :
            self.sURL, self.item, self.tot_time, self.timeresumepoint = self.addItem(play_list,0)
            self.playlist.add(self.sURL,self.item)
        else : return

    def start(self) :
        self.run_st = False
        self.fl_plstarted = False # flag pour ne pas repeter commande pl back started
        self.fl_watched = False
        self.playBackEventReceived = False
        self.playBackStoppedEventReceived = False
        self.forcestop = False
        debug('player initialized', 2)
        self.run()

    def __getPlayList(self):
        return xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

    def run(self):        
        if self.isPlaying():
            pass #self.setWatched()
        self.playBackEventReceived = False
        self.playBackStoppedEventReceived = False
        self.currentTime = 0
        #debug('Player sys arg int(sys.argv[1]) %s'%sys.argv,2)
        self.posn = self.playlist.getposition()
        #debug('Player playlist posn %s'%self.posn,2)
        xbmcplugin.setResolvedUrl(plugin.handle, True, self.item) 
        self.player = xbmc.Player()
        
        if self.posn == -1 :
            self.fl_watched = True
            self.player.stop()
            return

        # Attend que le lecteur démarre, avec un max de 20s
        for _ in range(20):
            if self.isPlaying() : #self.playBackEventReceived:
                break
            xbmc.sleep(1000)

        while self.isPlaying() and not self.forcestop:
            try:
                self.currentTime = self.getTime()
                #self.last_cur = self.currentTime
            except Exception as e:
                debug("player run isPlaying error %s"%str(e), 2)            

            self.last_cur = self.currentTime
            xbmc.sleep(1000)
       
        if not self.playBackStoppedEventReceived:
            self.onPlayBackStopped()            
        debug('player run Closing player', 2)
        return self.run_st

    def onPlayBackError() :
        debug("player2 onPlayBackError ",2)
        self.setWatched()
        return

    def onPlayBackStarted(self):
        if self.old_id != self.stream_id  :  #not self.fl_plstarted :
            self.old_id = self.stream_id
            #self.fl_plstarted = True                      
            debug('player onPlayBackStarted  %s'%self.old_id, 2)
        else :
            debug('player onPlayBackStarted passage else ',2) #%s'%self.fl_plstarted, 2)

        
        if self.timeresumepoint and (self.timeresumepoint < self.tot_time ):
                h = self.timeresumepoint//3600
                ms = self.timeresumepoint-h*3600
                m = ms//60
                s = ms-m*60
                if self.timeresumepoint > 5 :
                    ret = dialog.select(translate(30280), ['%s %02d:%02d:%02d' %(translate(30281),h, m, s), translate(30282)])
                    if ret == 0:
                        sekTime = float(self.timeresumepoint)
                        count = 0 
                        while not self.isPlayingVideo() :
                            count +=1
                            if count > 1000 : break
                            xbmc.sleep(100)
                        threading.Thread(target = self.setResumePointTh, name="resumepoint", args =[h, m, s, sekTime]).start()
                    elif ret == 1:
                        h = m = s = 0
                        sekTime = 0.0
                    else :
                        self.player.stop()
                        return
                else :
                    h = m = s = 0
                    sekTime = 0.0

                
        else :
            h = m = s = 0
            sekTime = 0.0

        
        
        '''        
        if isNexus() :
                debug('player 3 onPlayBackStarted isNexus %s'%isNexus(), 2)
                try : 
                    setResume = '{"jsonrpc": "2.0", "method": "Player.Seek", "params":{"playerid":1,"value":{"time":{"hours": %s ,"minutes": %s,"seconds":%s}}},"id": 1}'%(h,m,s)
                    response = xbmc.executeJSONRPC(setResume)
                    response = json.loads(response)
                    xbmc.log("player seek response2 %s"%response, xbmc.LOGDEBUG)                
                except Exception as e :
                    debug('player onPlayBackStarted self.tag error1 %s'%e, 2)                            
                    self.seekTime(sekTime)
        else :
                debug('player 3 onPlayBackStarted isNexus else ', 2)
                self.seekTime(sekTime)
        '''
        
    def onPlayBackEnded(self):
        #self.playBackEnd = True
        self.onPlayBackStopped()
        debug('player onPlayBackEnded self.playBackEnd %s'%self.playBackEnd, 2)

    def onPlayBackStopped(self):
        if self.old_id in self.played : return
        self.played.append(self.old_id)
        self.setWatched()
        if int(self.last_cur) >= int(self.totalTime)- 10 : #self.playBackEnd :
            try :
                if int(self.posL) < len(self.playlist) and (self.fl_watched) :
                    self.start()
                else :
                    self.player.stop()
                    xbmc.sleep(500)
                    return
            except Exception as e :
                debug('player onPlayBackStopped error %s'%e, 2)
                return #player.stop()
        else :
            self.player.stop()
            xbmc.sleep(500)
            return
        
    def setWatched(self):        
        try:
            if not self.fl_watched  :
                #debug("Player setWatched not self.fl_watched", 2)                
                try :
                    self.fl_watched = True     
                    if int(self.last_cur) >= int(self.totalTime)- 30 : self.last_cur = int(self.totalTime) 
                    threading.Thread(target = setWatchedTH, name=str(self.old_id), args =[self.old_id,int(self.last_cur)]).start()
                                                    
                except Exception as e:
                    debug("Player_setWatched last_curr error: {0}".format(e), 2)

        except Exception as e:
            debug("Player_setWatched error: {0}".format(e), 2)

    def onAVStarted(self):
        #self.infotag = self.getVideoInfoTag()
        #self.totalTime = int(self.getTotalTime())
        debug("Player onAVStarted ", 2)
        self.totalTime = int(self.getTotalTime())
        if self.playBackEventReceived:
            self.forcestop = True
            debug("Player onAVStarted playBackEventReceived forcestop %s %s"%(self.playBackEventReceived,self.forcestop), 2)
            #return

        # Reprendre la lecture
        if self.isPlayingVideo() :
            #debug("Player onAVStarted self.isPlayingVideo ", 2)
            if self.fl_id :
                self.posL = int(self.playlist.getposition()) + 1
                self.fl_id = False
                debug("Player onAVStarted self.posL : %s"%self.posL, 2)
            
            if (self.posL < len(self.play_list)) and (self.posL >= len(self.playlist)) :
                #self.old_id = self.stream_id
                self.sURL, self.item, self.tot_time, self.timeresumepoint = self.addItem(self.play_list,self.posL)
                if not self.sURL : return
                self.playlist.add(self.sURL,self.item)

    def addItem(self, mplaylist, n) :        
        try :
                if n > len(mplaylist) :
                    return None, None
                x = mplaylist[n] 
                self.typ_vid, self.stream_id, self.sURL, self.timeresumepoint, self.tot_time, self.Subtitles_file, self.title =  x
                self.SubtitleActive = False
                self.item = ListItem(self.title)
                self.item.setPath(self.sURL)
                self.item.setProperty('isFolder', 'false')
                self.item.setProperty('IsPlayable', 'true')
                self.item.setInfo(type='Video', infoLabels={'title': self.title})
                # Sous titres
                if self.Subtitles_file:
                    self.item.setSubtitles([self.Subtitles_file])
                    #self.SubtitleActive = True
                self.fl_id = True
                return self.sURL, self.item, self.tot_time, self.timeresumepoint
                
        except Exception as e :
            debug('player addItem error %s'%e, 2)

    def setResumePointTh(self,h, m, s, sekTime) :
                
        if isNexus() :
                debug('player 3 onPlayBackStarted isNexus %s'%isNexus(), 2)
                try : 
                    setResume = '{"jsonrpc": "2.0", "method": "Player.Seek", "params":{"playerid":1,"value":{"time":{"hours": %s ,"minutes": %s,"seconds":%s}}},"id": 1}'%(h,m,s)
                    response = xbmc.executeJSONRPC(setResume)
                    response = json.loads(response)
                    xbmc.log("player seek response2 %s"%response, xbmc.LOGDEBUG)                
                except Exception as e :
                    debug('player onPlayBackStarted self.tag error1 %s'%e, 2)                            
                    self.seekTime(sekTime)
        else :
                debug('player 3 onPlayBackStarted isNexus else ', 2)
                self.seekTime(sekTime)                    
def setWatchedTH(old_id,totalTime)  :
    try :
        set_sosac_watchTime("episodes", old_id, totalTime)
    except Exception as e:
        debug("Player_setWatched last_curr error: {0}".format(e), 2)


