#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('video_id')
        r.fieldcell('name')
        r.fieldcell('kind')
        r.fieldcell('start_time')
        r.fieldcell('end_time')
        r.fieldcell('subtitles')
        r.fieldcell('options')


    def th_query(self):
        return dict(column='video_id', op='contains', val='')

class ViewFromVideo(View):
    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@kind',sections_kind_all_end=True)

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('kind',hidden='^.#parent.sections.kind.current?=#v!="c_all_end"')
        r.fieldcell('start_time')
        r.fieldcell('end_time')
        r.fieldcell('subtitles')
        r.fieldcell('options')

    def th_order(self):
        return 'start_time:a'

class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('video_id',colspan=2)
        fb.field('kind',colspan=2)
        fb.field('start_time')
        fb.field('end_time')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class FormFromVideo(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        fb = bc.contentPane(region='top').formbuilder(cols=3, border_spacing='4px')
        fb.field('name',width='20em')
        fb.field('start_time',format='###.00',width='7em')
        fb.field('end_time',format='###.00',width='7em')
        tc = bc.tabContainer(margin='2px',region='center')
        for lang in self.db.table('docu.language').query().fetch():
            tc.contentPane(title='Subs: %(code)s' %lang,datapath='.subtitles').simpleTextArea(value='^.%(code)s' %lang)
        tc.contentPane(title='Options')

        #fb.field('subtitles')
        #fb.field('options')
