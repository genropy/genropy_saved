#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('company_id')
        r.fieldcell('user_id')
        r.fieldcell('customer_id')
        r.fieldcell('role')
        r.fieldcell('email')
        r.fieldcell('phone')
        r.fieldcell('skype')
        r.fieldcell('chat')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        top = bc.borderContainer(region='top',height='110px')
        top.contentPane(region='right',width='200px').linkerBox('user_id',formUrl='/adm/user_page',dialog_height='400px',
                                                                 dialog_width='650px',
                                                                 default_firstname='=#FORM.record.name',
                                                                 default_lastname='=#FORM.record.name',
                                                                 default_email='=#FORM.record.email',
                                                                 default_status='C',template='default',
                                                                 openIfEmpty=True)
        fb = top.contentPane(region='center').formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('company_id')
        fb.field('customer_id')
        fb.field('role')
        fb.field('email')
        fb.field('phone')
        fb.field('skype')
        fb.field('chat')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
