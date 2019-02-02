# -*- coding: utf-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from builtins import object
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/tpleditor:TemplateEditor"
    
    def test_0_videotrack_static(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='500px')
        pane = bc.contentPane(overflow='hidden',region='center')
        pane.video(src='/_site/screencasts/screencast_package_editor.mp4?#t=30,40',height='100%',width='100%',
                    border=0,controls=True,nodeId='preview_video',
                    tracks=[dict(src='/_site/screencasts/pippo.vtt?zzz',
                                kind='subtitles',srclang='it')])

    def test_1_videotrack_dinamic(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='500px')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.dbSelect(value='^.video_id',lbl='Video',selected_url='.video_url',dbtable='video.video')
        fb.filteringSelect(value='^.language',lbl='Lang',values='it,en,fr',
                        default_value='it',validate_onAccept="""
                        var video_url = GET .video_url;
                        PUT .video_url = null
                        SET .video_url = video_url;
                        """)

        pane = bc.contentPane(overflow='hidden',region='center')
        pane.video(src='^.video_url',height='100%',width='100%',
                    border=0,controls=True,nodeId='preview_video',
                    tracks=[dict(src='/video/index/vtt/$_video_id/$kind/$srclang.vtt',
                                kind='subtitles',srclang='^.language',_video_id='^.video_id',
                                label='Subtitle'),
                            dict(src='/video/index/vtt/$_video_id/$kind/$srclang.vtt',
                                kind='chapters',srclang='^.language',_video_id='^.video_id',
                                label='Chapter')])

    def test_2_videotrack_semistatic(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='500px')
        top = bc.contentPane(region='top',height='50px',background='red',splitter=True)
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.data('.myvideo.range','12,30')
        fb.data('.myvideo.playerTime',0)

        fb.textbox('^.myvideo.range',lbl='Range')

        bc.contentPane(region='left',width='50px',splitter=True,background='lime')
        bc.contentPane(region='right',width='50px',splitter=True,background='navy')
        bc.contentPane(region='bottom',height='50px',splitter=True,background='silver')

        pane = bc.VideoPlayer(url='https://player.vimeo.com/external/131523423.hd.mp4?s=0793387c74bb8a52ac266b4b67fe7dc623f1b447&profile_id=113&',
                    datapath='.myvideo',
                    region='center',
                    manageCue=True,
                    timerange='^.range',
                    selfsubscribe_addCue='console.log("fffff",$1);',
                   border=0,nodeId='preview_videoplayer',
                   subtitlePane=True,
                   tracks=[dict(src='/video/index/vtt/KMq3Rzs6MMW3so_vWdYFXg/subtitles/it.vtt',
                               kind='subtitles',srclang='it',label='Subtitle',
                               cue_path='.mainsub',hidden=True)
                   ])
        