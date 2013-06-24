# -*- coding: UTF-8 -*-

# contextname.py
# Created by Francesco Porcari on 2011-03-05.
# Copyright (c) 2011 Softwell. All rights reserved.

"webRTC test"
class GnrCustomWebPage(object):

    py_requires="gnrcomponents/testhandler:TestHandlerFull"


    def test_0_video(self,pane):
        """Video"""
        v = pane.div(height='310px').video(autoplay=True,height='300px',width='400px')
        fb = pane.formbuilder(cols=3,border_spacing='3px')
        fb.checkbox(value='^.video',label='Video',default_value=True)
        fb.checkbox(value='^.audio',label='Audio')
        fb.button('Start',action='v.startCapture({video:video,audio:audio})',v=v,video='=.video',audio='=.audio')



    def test_1_video_canvas(self,pane):
        """Video and Canvas"""
        v = pane.div(height='310px',display='inline-block').video(autoplay=True,height='300px',width='400px')
        c = pane.div(height='310px',display='inline-block',margin_left='10px').canvas(height='300px',width='400px',border='1px solid silver')
        pane.br()
        fb = pane.formbuilder(cols=5,border_spacing='3px')
        fb.checkbox(value='^.video',label='Video',default_value=True)
        fb.checkbox(value='^.audio',label='Audio')
        fb.button('Start',action='v.startCapture({video:video,audio:audio})',v=v,video='=.video',audio='=.audio')
        fb.button('Snapshot',action='v.takePhoto(c)',v=v,c=c)
        fb.button('Save',action='c.savePhoto()',c=c)

