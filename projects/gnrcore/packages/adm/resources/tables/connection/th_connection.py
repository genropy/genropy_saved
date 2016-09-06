#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('userid',caption_field=False)
        r.fieldcell('username')
        r.fieldcell('ip')
        r.fieldcell('start_ts')
        r.fieldcell('end_ts')
        r.fieldcell('end_reason')
        r.fieldcell('user_agent')

    def th_order(self):
        return 'userid'

    def th_query(self):
        return dict(column='username', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('userid')
        fb.field('username')
        fb.field('ip')
        fb.field('start_ts')
        fb.field('end_ts')
        fb.field('end_reason')
        fb.field('user_agent')
        
        bc.contentPane(region='center').plainTableHandler(relation='@pages',viewResource='ViewFromConnection')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
