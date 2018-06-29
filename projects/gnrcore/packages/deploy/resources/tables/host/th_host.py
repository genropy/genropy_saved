#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('provider')
        r.fieldcell('code')
        r.fieldcell('name')
        r.fieldcell('description')
        r.fieldcell('wsgi_server')
        r.fieldcell('address')
        r.fieldcell('admin_user')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')


class Form(BaseComponent):
    
    def th_form(self, form):
        bc = form.center.borderContainer()
        top_pane =bc.contentPane(region='top', datapath='.record')
        fb = top_pane.formbuilder(cols=1, border_spacing='4px')
        fb.field('provider')
        fb.field('code')
        fb.field('name')
        fb.field('description')
        fb.field('wsgi_server')
        fb.field('address')
        fb.field('ssh_command')
        fb.field('admin_user')
        center_pane=bc.contentPane(region='center')
        center_pane.dialogTableHandler(relation='@instances')
    
    def th_options(self):
        return dict(dialog_windowRatio=.9)