#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('request')
        r.fieldcell('execution_start')
        r.fieldcell('execution_end')
        r.fieldcell('mode')
        r.fieldcell('action')
        r.fieldcell('implementor')
        r.fieldcell('maintable')
       # r.fieldcell('data')
        r.fieldcell('error_id')
        r.fieldcell('request_id')
        r.fieldcell('request_ts')
        r.fieldcell('user_id')
        r.fieldcell('session_id')
        r.fieldcell('user_ip')
        r.fieldcell('file_name',width='60em')
        r.fieldcell('queue_id')

    def th_order(self):
        return 'request'


    def th_query(self):
        return dict(column='execution_start', op='isnull', val='')

    def th_options(self):
        return dict(widget='border')



class Form(BaseComponent):

    def th_form(self, form):
        tc = form.center.tabContainer()
        bc = tc.borderContainer(datapath='.record',title='Main')
        bc.contentPane(region='left',width='300px').tree(storepath='.data',_fired='^#FORM.controller.loaded')
        fb = bc.contentPane(region='center').formbuilder(cols=2, border_spacing='4px')
        fb.field('request')
        fb.field('execution_start')
        fb.field('execution_end')
        fb.field('mode')
        fb.field('action')
        fb.field('implementor')
        fb.field('maintable')
        fb.field('data')
        fb.field('error_id')
        fb.field('request_id')
        fb.field('request_ts')
        fb.field('user_id')
        fb.field('session_id')
        fb.field('user_ip')
        fb.field('file_name')
        fb.field('queue_id')
        tc.contentPane(title='Error').simpleTextArea(value='^.record.@error_id.data',height='400px',width='100%')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
