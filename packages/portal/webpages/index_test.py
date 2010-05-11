#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Registrazione nuovo utente
#
#  Created by Francesco Cavazzana on 2008-01-23.
#

""" Registrazione nuovo utente """

from gnr.core.gnrbag import Bag
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='publicsite:SiteLayout'
    css_requires='fonts/Nadia/stylesheet'
    def main(self, root,**kwargs):
        self.margin_default='7px'
        layout = root.borderContainer(_class='site_body',font_family='NadiaSerifNormal')
        layout.dataRemote('pippo','pippo')
        self.site_header(layout.contentPane(region='top',_class='site_header'))
        self.site_footer(layout.contentPane(region='bottom',_class='site_footer',height='15px'))
        left=self.site_left(layout.borderContainer(region='left',width='25%'))
        right=self.site_right(layout.borderContainer(region='right',width='25%'))
        self.site_center(layout.borderContainer(region='center'))
    def rpc_pippo(self):
        return Bag(dict(pippo='pluto',paperino=12))

    def site_center(self,bc):
        bc = bc.borderContainer(region='center',_class='site_pane',margin=self.margin_default)
        tc = bc.tabContainer(region='center',margin='10px')
        self.page_0(tc.contentPane(title='Page 0',nodeId='tab0'))
        tc.contentPane(title='Page 1',nodeId='tab1').remote('page_1',lazy=False)
        tc.contentPane(title='Page 2').remote('page_2')
        self.page_3(tc.contentPane(title='Page 3'))

    def page_0(self,pane):
        """docstring for page_0"""
       # self.videoScript(pane)
        pane.div('page 0')
        pane.button('Hero',action='genro.playSound("Hero")')
        pane.button('Frog',action='genro.playSound("Frog")')
        pane.button('Glass',action='genro.playSound("Glass")')
        pane.button('Submarine',action='genro.playSound("Submarine")')
        #pane.button('initvideo',action='initVideo()')
        #pane.video(src="http://movies.apple.com/movies/us/apple/ipoditunes/2007/touch/ads/apple_ipodtouch_touch_r640-9cie.mov", autoplay=True)
       #videocontainer= pane.div(id='videocontainer')
       #videocontainer.video(id='videoelem', poster="/blog-files/touch-poster.png")
       #videocontainer.div(_class="videobutton videoplay", id="videoplaybutton")
       #videocontainer.div(id='videozoombutton', _class="videobutton videozoombutton videofadeout")

    def remote_page_1(self,pane):
        """docstring for page_1"""
        pane.data('angle','30::L')
        pane.dataController(""" var st='-webkit-transform: rotate('+angle+'deg);'+
                                   '-moz-transform: rotate('+angle+'deg);'+
                                   'border:6px dotted red;width:4em;'+
                                   'padding:10px;text-align:center;'+
                                   '-webkit-border-radius:8px;'+
                                    '-moz-border-radius:8px;'+
                                    'color:red;cursor:pointer;'+
                                    'background-color:yellow;'+
                                    'font-size:3em;'+
                                    'margin-top:50px;'+
                                    'margin-left:20px;'+
                                    '-mox-box-shadow:15px 15px 35px #888;'+
                                    '-webkit-box-shadow:15px 15px 35px #888;'+
                                    'text-shadow:6px 6px 14px #333;'
                                    SET divstyle=st;
                                   """,angle='^angle',_onStart=True)
        pane.div('page 1',style="^divstyle",connect_onclick='SET angle=GET angle+2;')
    def videoScript(self,pane): 
        pane.script("""var videoElem;
                       var playButton;
                       var showProgress = true;
                       var videoLargeSize = false;
                       function startedPlaying() {
                            showProgress = false;
                            playButton.innerHTML = "||"
                            playButton.className = "videobutton videoplay videofadeout";
                       }
                       function stoppedPlaying() {
                           playButton.innerHTML = ">"
                           playButton.className = "videobutton videoplay";
                       }
                       function waiting (ev) {
                            if (!showProgress) {
                                showProgress = true;
                                playButton.innerHTML = "Loading...";
                                playButton.className = "videobutton videoloading";
                            }
                       }
                       function loadRequired() {
                           if ("DATA_UNAVAILABLE" in HTMLMediaElement)
                               return videoElem.readyState == HTMLMediaElement.DATA_UNAVAILABLE;
                           if ("HAVE_NOTHING" in HTMLMediaElement)
                               return videoElem.readyState == HTMLMediaElement.HAVE_NOTHING;
                           return false
                       }
                       function canPlayThrough() {
                           if ("CAN_PLAY_THROUGH" in HTMLMediaElement)
                               return videoElem.readyState == HTMLMediaElement.CAN_PLAY_THROUGH;
                           if ("HAVE_ENOUGH_DATA" in HTMLMediaElement)
                               return videoElem.readyState == HTMLMediaElement.HAVE_ENOUGH_DATA;
                           return false
                       }
                       function updateProgress(ev) {
                           if (!showProgress)
                              return;
                           if (ev.total)
                               playButton.innerHTML = "Loading " + (100*ev.loaded/ev.total).toFixed(0) + "%";
                           else
                               playButton.innerHTML = "Loading...";
                           playButton.className = "videobutton videoloading";
                       }
                       function initVideo() {
                           videoElem = document.getElementById("videoelem");
                           playButton = document.getElementById("videoplaybutton");
                           videoZoomButton = document.getElementById("videozoombutton");
                           if (!videoElem.play) {
                              playButton.style.display = "none";
                              videoZoomButton.style.display = "none";
                              return;
                           }
                           videoElem.addEventListener("play", startedPlaying);
                           videoElem.addEventListener("pause", stoppedPlaying);
                           videoElem.addEventListener("ended", function () {
                               if (!videoElem.paused)
                                   videoElem.pause();
                               stoppedPlaying();
                           });
                           videoElem.addEventListener("progress", updateProgress);
                           videoElem.addEventListener("begin", updateProgress);
                           videoElem.addEventListener("canplaythrough", function () {
                                videoElem.play();
                           });
                           videoElem.addEventListener("error", function() {
                               playButton.innerHTML = "Load failed";
                           });
                           videoElem.addEventListener("waiting", waiting);
                           videoElem.addEventListener("dataunavailable", waiting);
                           videoZoomButton.addEventListener("click", function () {
                               var container = document.getElementById("videocontainer");
                               videoLargeSize = !videoLargeSize;
                               if (videoLargeSize) {
                                   container.style.width = "640px";
                                   container.style.height = "360px";
                                   videoZoomButton.innerHTML = "-";
                               } else {
                                   container.style.width = "400px";
                                   container.style.height = "225px";
                                   videoZoomButton.innerHTML = "+";
                               }
                           });
                           playButton.addEventListener("click", function () {
                               if (videoElem.paused) {
                                   if (!videoElem.src)
                                       //videoElem.src = "sample.mov";
                                       videoElem.src = "http://movies.apple.com/movies/us/apple/ipoditunes/2007/touch/ads/apple_ipodtouch_touch_r640-9cie.mov";
                                   if (loadRequired())
                                       videoElem.load();
                                   if (canPlayThrough())
                                       videoElem.play();
                               } else
                                   videoElem.pause();
                           } );
}
        """)

                                
    def remote_page_2(self,pane):
        """docstring for page_2"""
        pane.div('page 2')


    def page_3(self,pane):
        """docstring for page_3"""
        pane.div('page 3')
        
    def site_footer(self,bc):
        pass
        
    def site_left(self,bc):
        
        bc.borderContainer(region='top',_class='site_pane',margin=self.margin_default,height='60px')
        bc.borderContainer(region='center',_class='site_pane',margin=self.margin_default)
        
    def site_right(self,bc):
        pane=bc.contentPane(region='top',_class='site_pane',margin=self.margin_default,height='60px')
        bc.contentPane(region='bottom',_class='site_pane',margin=self.margin_default,height='60px')
        center=bc.borderContainer(region='center',_class='site_pane',margin=self.margin_default)
        fb = pane.formbuilder(cols=1,border_spacing='4px',margin=self.margin_default)
        fb.textbox(value='^tabs',lbl='Tabs',width='16em') 
        center.tabContainer(region='center',margin='8px').remote('tabContent',tabs='^tabs',lazy=False)       

    def remote_tabContent(self,tc,tabs='pippo,pluto'):
        tabs=tabs.split(',')
        for t in tabs:
            p=tc.contentPane(title=t,height='100%')
            p.button(t)            
                        
