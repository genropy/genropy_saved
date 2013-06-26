# -*- coding: UTF-8 -*-

# contextname.py
# Created by Francesco Porcari on 2011-03-05.
# Copyright (c) 2011 Softwell. All rights reserved.

"webRTC test"
class GnrCustomWebPage(object):

    py_requires="gnrcomponents/testhandler:TestHandlerFull"


    def test_0_video(self,pane):
        """Video"""
        video = pane.div(height='310px').video(autoplay=True,height='300px',width='400px')
        fb = pane.formbuilder(cols=3,border_spacing='3px')
        fb.checkbox(value='^.video',label='Video',default_value=True)
        fb.checkbox(value='^.audio',label='Audio')
        fb.button('Start',action='video.startCapture({video:videoCapture,audio:audioCapture})',video=video,videoCapture='=.video',audioCapture='=.audio')



    def test_1_video_canvas(self,pane):
        """Video and Canvas"""
        video = pane.div(height='310px',display='inline-block').video(autoplay=True,height='300px',width='400px')
        canvas = pane.div(height='310px',display='inline-block',margin_left='10px').canvas(height='300px',width='400px',border='1px solid silver')
        pane.br()
        fb = pane.formbuilder(cols=5,border_spacing='3px')
        fb.checkbox(value='^.video',label='Video',default_value=True)
        fb.checkbox(value='^.audio',label='Audio')
        fb.button('Start',action='video.startCapture({video:videoCapture,audio:audioCapture})',video=video,videoCapture='=.video',audioCapture='=.audio')

        fb.button('Snapshot',action='canvas.takePhoto(video)',video=video,canvas=canvas)
        fb.button('Save',action='canvas.savePhoto()',canvas=canvas)

    def test_2_video_copytocanvas(self,pane):
        """Video and Canvas"""
        video = pane.div(height='310px',display='inline-block').video(autoplay=True,height='300px',width='400px')
        canvas = pane.div(height='310px',display='inline-block',margin_left='10px').canvas(height='300px',width='400px',
                            border='1px solid silver',effect='^.effect')
        pane.br()
        fb = pane.formbuilder(cols=6,border_spacing='3px')
       # fb.checkbox(value='^.video',label='Video',default_value=True)
        fb.checkbox(value='^.mirror',label='Mirror')
        fb.dataController('SET .effects = canvas.pixasticEffects.join(",")',_onStart=True,canvas=canvas)
        fb.filteringSelect(value='^.effect',values='^.effects')
        fb.button('Start',action='video.startCapture({video:videoCapture,audio:audioCapture})',video=video,videoCapture=True,audioCapture=False)
        fb.button('Copy',action='canvas.takePhoto(video,{"sync":sync,"mirror":mirror})',video=video,canvas=canvas,sync=True,mirror='=.mirror')
        fb.button('Save',action='canvas.savePhoto()',canvas=canvas)
        fb.button('Save server',action='canvas.savePhoto({uploadPath:path,filename:"supertest})',canvas=canvas,path='site:test/myimage')

    def test_3_video_capture(self,pane):
        frame = pane.framePane(height='340px',width='420px',border='1px solid silver')
        top = frame.top.slotToolbar('*,pickerImage,5',height='20px')
        top.pickerImage.videoPickerPalette()
        frame.center.contentPane(overflow='hidden').img(src='^.currUrl',crop_width='400px',crop_height='300px',
                        placeholder=self.getResourceUri('images/missing_photo.png'),
                        upload_folder='site:test/photo',edit=True,
                        upload_filename='foto_test_grabber',crop_border='1px solid #ddd',crop_rounded=8,crop_margin='9px',
                       zoomWindow=True)


