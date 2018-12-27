#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('company_code')
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
        return dict(column='name', op='contains', val='')

class ViewFromCustomer(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('user_id')
        r.fieldcell('role')
        r.fieldcell('email')
        r.fieldcell('phone')
        r.fieldcell('skype')
        r.fieldcell('chat')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')

class ViewFromCompany(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('user_id')
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
        top = bc.borderContainer(region='top',datapath='.record',height='150px')
        top.contentPane(region='right',width='250px').linkerBox('user_id',formUrl='/adm/user_page', 
                                                                dialog_height='400px', dialog_width='650px', 
                                                        dialog_title='Login info',margin='2px')
        fb = top.roundedGroup(region='center',title='!!Person info').div(margin_right='30px').formbuilder(cols=2, border_spacing='4px',fld_width='100%',colswidth='auto')
        fb.field('name')
        fb.field('role')
        fb.field('company_code')
        fb.field('customer_id')
        fb.field('email')
        fb.field('phone')
        fb.field('skype')
        fb.field('chat')
        tc = bc.tabContainer(region='center')
        tc.contentPane(title='Tickets').dialogTableHandler(table='uke.ticket',condition='$person_id=:pid OR @ticket_person.person_id=:pid',
                        condition_pid='^#FORM.record.person_id',hider=False,
                        pbl_classes=True,margin='2px',addrow=False,delrow=False)
        tc.contentPane(title='Public Keys').inlineTableHandler(relation='@public_keys',
                                                                viewResource='ViewFromPerson',pbl_classes=True,margin='2px')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class FormFromCustomer(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('user_id')
        fb.field('role')
        fb.field('email')
        fb.field('phone')
        fb.field('skype')
        fb.field('chat')
        bc.contentPane(region='center').inlineTableHandler(relation='@public_keys',viewResource='ViewFromPerson')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')


class FormFromCompany(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('user_id')
        fb.field('role')
        fb.field('email')
        fb.field('phone')
        fb.field('skype')
        fb.field('chat')
        bc.contentPane(region='center').inlineTableHandler(relation='@public_keys',viewResource='ViewFromPerson')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
