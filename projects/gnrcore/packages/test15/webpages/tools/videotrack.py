# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/tpleditor:TemplateEditor"
    
    def test_0_videotrack_static(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='500px')
        pane = bc.contentPane(overflow='hidden',region='center')
        pane.video(src='/_site/screencasts/screencast_package_editor.mp4',height='100%',width='100%',
                    border=0,controls=True,nodeId='preview_video',
                    tracks=[dict(src='/_site/screencasts/pippo.vtt?zzz',
                                kind='subtitles',srclang='it')])

    def test_1_videotrack_dinamic(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='500px')
        pane = bc.contentPane(overflow='hidden',region='center')
        pane.video(src='/_site/screencasts/screencast_package_editor.mp4',height='100%',width='100%',
                    border=0,controls=True,nodeId='preview_video',
                    tracks=[dict(src='/docu/index/vtt/KMq3Rzs6MMW3so_vWdYFXg/subtitles/it.vtt',
                                kind='subtitles',srclang='it')])

  #ef test_2_videotrack_semistatic(self,pane):
  #   """First test description"""
  #   bc = pane.borderContainer(height='500px')
  #   pane = bc.contentPane(overflow='hidden',region='center')
  #   pane.video(src='/_site/screencasts/screencast_package_editor.mp4',height='100%',width='100%',
  #               border=0,controls=True,nodeId='preview_video',
  #               tracks=[dict(src='/_site/screencasts/sub_it.vtt',
  #                           kind='subtitles',srclang='it')])
        