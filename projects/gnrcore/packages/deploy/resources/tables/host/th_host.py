#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('name')
        r.fieldcell('description')
        r.fieldcell('webserver')
        r.fieldcell('genro_branch')
        r.fieldcell('address')
        r.fieldcell('ssh_command')
        r.fieldcell('admin_user')
        r.fieldcell('admin_pwd')
      

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')


class Form(BaseComponent):
    
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        fb = bc.contentPane(region='top').formbuilder(cols=1, border_spacing='4px')
        fb.field('code')
        fb.field('name')
        fb.field('description')
        fb.field('webserver')
        fb.field('genro_branch')
        fb.field('address')
        fb.field('ssh_command')
        fb.field('admin_user')
        fb.field('admin_pwd')
  