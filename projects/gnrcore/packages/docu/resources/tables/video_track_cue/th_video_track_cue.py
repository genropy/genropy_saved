#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('video_id')
        r.fieldcell('kind')
        r.fieldcell('start_time')
        r.fieldcell('end_time')
        r.fieldcell('subtitles')
        r.fieldcell('options')


    def th_query(self):
        return dict(column='video_id', op='contains', val='')

class ViewFromVideo(View):
    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@kind')


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('video_id',colspan=2)
        fb.field('kind',colspan=2)
        fb.field('start_time')
        fb.field('end_time')
        fb.field('subtitles')
        fb.field('options')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class FormFromVideo(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('kind',colspan=2)
        fb.field('start_time',format='###.00')
        fb.button('GET',action='SET .start_time = currTime',currTime='=#preview_video.currentTime')
        fb.field('end_time',format='###.00')
        fb.button('GET',action='SET .end_time = currTime; genro.nodeById("preview_video").domNode.pause();',
                    currTime='=#preview_video.currentTime')
        tc = bc.tabContainer(margin='2px',region='center')
        tc.contentPane(title='Subtitles')
        tc.contentPane(title='Options')

        #fb.field('subtitles')
        #fb.field('options')
