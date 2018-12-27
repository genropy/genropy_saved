#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('batch_title')
        r.fieldcell('page_id')
        r.fieldcell('start_ts')
        r.fieldcell('end_ts')
        r.fieldcell('logfile_url',format='download')
        r.fieldcell('notes')

    def th_order(self):
        return 'batch_title'

    def th_query(self):
        return dict(column='batch_title', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        pane = bc.contentPane(region='top')
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('batch_title')
        fb.field('page_id')
        fb.field('start_ts')
        fb.field('end_ts')
        fb.field('notes')
        bc.contentPane(region='center',overflow='auto'
                ).tree(storepath='.logbag',labelAttribute='caption',searchOn=True)


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
