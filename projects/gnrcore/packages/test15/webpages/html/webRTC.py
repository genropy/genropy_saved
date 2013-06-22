# -*- coding: UTF-8 -*-

# contextname.py
# Created by Francesco Porcari on 2011-03-05.
# Copyright (c) 2011 Softwell. All rights reserved.

"webRTC test"
class GnrCustomWebPage(object):
    #auto_polling=0
    #user_polling=0
    py_requires="gnrcomponents/testhandler:TestHandlerFull"


    def test_0_video(self,pane):
        """First test description"""
        pane = pane.contentPane(height='300px')
        
        pane.script("""var webrtc={};
                       webrtc.onErr=function(e){
                            console.log('error',e)
                       };
                     webrtc.onOk=function(stream){
                         var videoSourceNode=genro.nodeById('myvideo');
                         videoSourceNode.domNode.src=window.webkitURL.createObjectURL(stream);
                     };
                      webrtc.start=function(){
                          navigator.webkitGetUserMedia({'video':true},webrtc.onOk,webrtc.onErr);
                      }
                       """)
        pane.video(autoplay="",nodeId='myvideo',controls=True)
        pane.button('start',action="""webrtc.start()""")
        

