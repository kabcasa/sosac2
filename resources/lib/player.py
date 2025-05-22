# -*- coding: utf-8 -*-
import sys, time, json
import xbmcplugin
import xbmc
from xbmcgui import ListItem
import routing
from resources.lib.util import *
from os.path import splitext

# pour les sous titres
# https://github.com/amet/service.subtitles.demo/blob/master/service.subtitles.demo/service.py
# player API
# http://mirrors.xbmc.org/docs/python-docs/stable/xbmc.html#Player

plugin = routing.Plugin()
class cPlayer(xbmc.Player):

    def __init__(self, playlist,mode):

        xbmc.Player.__init__(self)
        typ_vid, stream_id, URL, start_from, tot_time, subtitle, title = playlist[0]
        self.count = 0
        self.typ_vid = typ_vid
        self.stream_id = stream_id
        self.Subtitles_file = subtitle
        self.sURL = URL
        self.tot_time = tot_time
        self.timeresumepoint = start_from
        self.title = title
        self.SubtitleActive = False
        self.mode = mode

        self.playBackEventReceived = False
        self.playBackStoppedEventReceived = False
        self.forcestop = False
        self.multi = False  # Plusieurs vidéos se sont enchainées
        self.totalTime = 0
        debug("player init start_from %s"%start_from, 2)

    def __getPlayList(self):
        return xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

    def runs(self):
        if self.isPlaying():
            self._setWatcheds()
        self.currentTime = 0
        item = ListItem(self.title)
        item.setPath(self.sURL)
        item.setProperty('isFolder', 'false')
        item.setProperty('IsPlayable', 'true')
        item.setInfo(type='Video', infoLabels={'title': self.title})
        #item.setProperty('ResumeTime', str(self.resumePoint))
        debug("player runs self.timeresumepoint %s"%self.timeresumepoint, 2)
        # Sous titres
        if self.Subtitles_file:
            try:
                item.setSubtitles([self.Subtitles_file])
                self.SubtitleActive = True
            except:
                debug("Can't load subtitle:" + str(self.Subtitles_file), 2)

        xbmcplugin.setResolvedUrl(plugin.handle, True, item)
        self.player = xbmc.Player()

        self.sektime = mess_resTime(self.timeresumepoint, self.tot_time)
        if self.sektime == None :
            self.player.stop()
            return
        '''
        if isNexus() :
            info = '{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "params": { "filter": { "id": "Player.Seek", "type": "method" } }, "id": 1 }'
            setResume = '{"jsonrpc": "2.0", "method": "Player.Seek", "params":{"playerid":1,"value":{"seconds":800}},"id": 1}'
            response = xbmc.executeJSONRPC(setResume)
            response = json.loads(response)
            xbmc.log("player seek response %s"%response, xbmc.LOGDEBUG)
        '''
        #if self.isPlaying():
        #    self.tag = self.player.getVideoInfoTag()

        debug('Player start playing', 2)

        for _ in range(20):
            if self.playBackEventReceived:
                break
            xbmc.sleep(1000)

        while self.isPlaying() and not self.forcestop:
            try:
                self.currentTime = self.getTime()
            except Exception as e:
                debug("player run isPlaying error %s"%str(e), 2)

            xbmc.sleep(1000)

        if not self.playBackStoppedEventReceived:
            self.onPlayBackStopped()

        debug('Closing player', 2)
        return True

    def onPlayBackStarted(self):
        self.old_id = self.stream_id
        
        try :
            count = 0 
            while not self.isPlayingVideo() :
                count +=1
                if count > 1000 : break
                xbmc.sleep(100)
            
            if isNexus() :                
                h = int(float(self.sektime)//3600)
                ms = float(self.sektime)-h*3600
                m = int(ms//60) 
                s = int(ms-m*60)
                setResume = '{"jsonrpc": "2.0", "method": "Player.Seek", "params":{"playerid":1,"value":{"time":{"hours": %s ,"minutes": %s,"seconds":%s}}},"id": 1}'%(h,m,s)
                response = xbmc.executeJSONRPC(setResume)
                response = json.loads(response)
                xbmc.log("player seek response2 %s"%response, xbmc.LOGDEBUG)
            
            else :
                debug('player 3 onPlayBackStarted isNexus else ', 2)
                self.seekTime(float(self.sektime))
        except Exception as e :
           debug('player onPlayBackStarted seektime error %s'%str(e), 2)
           self.seekTime(0.0)

    def onPlayBackEnded(self):
        self.onPlayBackStopped()

    # Attention pas de stop, si on lance une seconde video sans fermer la premiere
    def onPlayBackStopped(self):
        # reçu deux fois, on n'en prend pas compte
        if self.playBackStoppedEventReceived:
            debug('player onPlayBackStopped playBackStoppedEventReceived', 2)
            return
        self.playBackStoppedEventReceived = True
        self._setWatcheds()

    def _setWatcheds(self):
        try:            
            if self.isPlaying():
                self.totalTime = int(self.getTotalTime())
                self.currentTime = int(self.getTime())
                
            if int(self.currentTime) >= int(self.totalTime)- 60 : self.currentTime = int(self.totalTime)
            if "movies" == self.typ_vid  : set_sosac_watchTime("movies", self.stream_id, self.currentTime)
            else  : set_sosac_watchTime("episodes", self.stream_id, self.currentTime)

        except Exception as e:
            debug("Player_setWatched error: {0}".format(e), 2)

    # def onPlayBackStarted(self):
    def onAVStarted(self):
        self.tag = self.player.getVideoInfoTag()
        self.totalTime = int(self.getTotalTime())

        # Si on recoit une nouvelle fois l'event, c'est que ca buggue, on stope tout
        if self.playBackEventReceived:
            self.forcestop = True
            return

        self.playBackEventReceived = True

class cPlayerMan(xbmc.Player):

    def __init__(self, playlist,mode):

        xbmc.Player.__init__(self)
        typ_vid, stream_id, URL, start_from, tot_time, subtitle, title = playlist[0]
        self.count = 0
        self.typ_vid = typ_vid
        self.stream_id = stream_id
        self.Subtitles_file = subtitle
        self.sURL = URL
        self.tot_time = tot_time
        self.timeresumepoint = start_from
        self.title = title
        self.SubtitleActive = False
        self.mode = mode

        self.playBackEventReceived = False
        self.playBackStoppedEventReceived = False
        self.forcestop = False
        self.multi = False  # Plusieurs vidéos se sont enchainées
        self.totalTime = 0

    def __getPlayList(self):
        return xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

    def runm(self):
        if self.isPlaying():
            self._setWatcheds()
        self.currentTime = 0
        item = ListItem(self.title)
        item.setPath(self.sURL)
        item.setProperty('isFolder', 'false')
        item.setProperty('IsPlayable', 'true')
        item.setInfo(type='Video', infoLabels={'title': self.title})
        #item.setProperty('ResumeTime', str(self.resumePoint))
        debug("player2 runs self.timeresumepoint %s"%self.timeresumepoint, 2)
        # Sous titres
        if self.Subtitles_file:
            try:
                item.setSubtitles([self.Subtitles_file])
                self.SubtitleActive = True
            except:
                debug("Can't load subtitle:" + str(self.Subtitles_file), 2)
        
        self.player_man = xbmc.Player()#.play(self.sURL,item)
        if  self.Subtitles_file :
            self.player_man.setSubtitles(self.Subtitles_file)
            self.player_man.showSubtitles(True)
        self.player_man.play(self.sURL,item)
                        
        self.sektime = mess_resTime(self.timeresumepoint, self.tot_time)
        if self.sektime == None :
            self.player_man.stop()
            return

        debug('Player start playing', 2)

        for _ in range(20):
            if self.playBackEventReceived:
                break
            xbmc.sleep(1000)

        while self.isPlaying() and not self.forcestop:
            try:
                self.currentTime = self.getTime()
            except Exception as e:
                debug("player run isPlaying error %s"%str(e), 2)

            xbmc.sleep(1000)

        if not self.playBackStoppedEventReceived:
            self.onPlayBackStopped()

        debug('Closing player2', 2)
        return True

    def onPlayBackStarted(self):
        self.old_id = self.stream_id
        try :
            count = 0 
            while not self.isPlayingVideo() :
                count +=1
                if count > 1000 : break
                xbmc.sleep(100)
            if isNexus() :                
                h = int(float(self.sektime)//3600)
                ms = float(self.sektime)-h*3600
                m = int(ms//60) 
                s = int(ms-m*60)
                setResume = '{"jsonrpc": "2.0", "method": "Player.Seek", "params":{"playerid":1,"value":{"time":{"hours": %s ,"minutes": %s,"seconds":%s}}},"id": 1}'%(h,m,s)
                response = xbmc.executeJSONRPC(setResume)
                response = json.loads(response)
                xbmc.log("player seek response2 %s"%response, xbmc.LOGDEBUG)
            
            else :
                debug('player 3 onPlayBackStarted isNexus else ', 2)
                self.seekTime(float(self.sektime))
        except Exception as e :
           debug('player onPlayBackStarted seektime error %s'%str(e), 2)
           self.seekTime(0.0)

    def onPlayBackEnded(self):
        self.onPlayBackStopped()

    def onPlayBackError() :
        debug("player2 onPlayBackError ",2)
        return
        
    # Attention pas de stop, si on lance une seconde video sans fermer la premiere
    def onPlayBackStopped(self):
        # reçu deux fois, on n'en prend pas compte
        if self.playBackStoppedEventReceived:
            debug('player2 onPlayBackStopped playBackStoppedEventReceived', 2)
            return
        self.playBackStoppedEventReceived = True
        self._setWatcheds()

    def _setWatcheds(self):
        try:            
            if self.isPlaying():
                self.totalTime = int(self.getTotalTime())
                self.currentTime = int(self.getTime())
            debug('player2 _setWatcheds self.currentTime %s'%self.currentTime, 2)
            debug('player2 _setWatcheds self.typ_vid %s'%self.typ_vid, 2)
            debug('player2 _setWatcheds self.stream_id %s'%self.stream_id, 2)
                
            if int(self.currentTime) >= int(self.totalTime)- 60 : self.currentTime = int(self.totalTime)
            if "movies" == self.typ_vid  : set_sosac_watchTime("movies", self.stream_id, self.currentTime)
            else  : set_sosac_watchTime("episodes", self.stream_id, self.currentTime)

        except Exception as e:
            debug("Player2 _setWatched error: {0}".format(e), 2)

    # def onPlayBackStarted(self):
    def onAVStarted(self):
        self.infotag = self.getVideoInfoTag()
        self.totalTime = int(self.getTotalTime())

        # Si on recoit une nouvelle fois l'event, c'est que ca buggue, on stope tout
        if self.playBackEventReceived:
            self.forcestop = True
            return

        self.playBackEventReceived = True

def mess_resTime(vtimeresumepoint, vtot_time) :
        if vtimeresumepoint and (vtimeresumepoint < vtot_time ):
                debug("player  2onPlayBackStarted self.timeresumepoint %s"%vtimeresumepoint, 2)
                h = vtimeresumepoint//3600
                ms = vtimeresumepoint-h*3600
                m = ms//60
                s = ms-m*60
                try :
                    if vtimeresumepoint > 5 :
                        ret = dialog.select(translate(30280), ['%s %02d:%02d:%02d' %(translate(30281),h, m, s), translate(30282)])
                        if ret == 0:
                            sektime = vtimeresumepoint
                        elif ret == 1:
                            sektime = 0.0
                        else : return None
                    else : sektime = 0.0

                except Exception as e :
                    debug("mess_resTime  error: %s"%e, 2)
                    return None
                    
                    

        else : sektime = 0.0

        return sektime
