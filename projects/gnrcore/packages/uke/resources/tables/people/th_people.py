#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('company')
        r.fieldcell('user_id')
        r.fieldcell('customer')
        r.fieldcell('role')
        r.fieldcell('email')
        r.fieldcell('phone')
        r.fieldcell('skype')
        r.fieldcell('chat')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('company')
        fb.field('user_id')
        fb.field('customer')
        fb.field('role')
        fb.field('email')
        fb.field('phone')
        fb.field('skype')
        fb.field('chat')
        bc.contentPane(region='center').inlineTableHandler(relation='@public_keys',viewResource='ViewFromPerson')




    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
