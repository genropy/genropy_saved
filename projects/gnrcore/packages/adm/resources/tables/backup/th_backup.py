#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('start_ts')
        r.fieldcell('dl_link')

    def th_order(self):
        return 'start_ts'

    def th_query(self):
        return dict(column='start_ts', op='contains', val='%')

    @public_method
    def th_applymethod(self,selection):
        def fileFinder(row):
            if not row['filename']: return dict()
            link='<a href="%s?download=True">%s</a>'%(row['dl_link'],'Download')
            return dict(linkdl=link)
        selection.apply(fileFinder)




class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('start_ts')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
