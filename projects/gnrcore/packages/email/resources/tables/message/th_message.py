#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('subject',width='30em')

        r.fieldcell('to_address',width='18em')
        r.fieldcell('from_address',width='18em')
        r.fieldcell('cc_address',width='18em')
        r.fieldcell('bcc_address',width='18em')
        r.fieldcell('uid',width='7em')
        r.fieldcell('send_date',width='7em')
        r.fieldcell('sent',width='7em')
        #r.fieldcell('user_id',width='35em')
        r.fieldcell('account_id',width='12em')


    def th_queryBySample(self):
        return dict(fields=[dict(field='send_date',lbl='!!Send date',width='7em'),
                            dict(field='subject', lbl='!!Subject'),
                            dict(field='body_plain',lbl='!!Content'),
                            dict(field='to_address', lbl='To address'),
                            dict(field='from_address', lbl='From address')],cols=5,isDefault=True)

    def th_order(self):
        return '__ins_ts'

    def th_query(self):
        return dict(column='subject',op='contains', val='',runOnStart=False)
    
    def th_options(self):
        return dict(partitioned=True)

    def th_top_message_type(self,top):
        top.slotToolbar('5,sections@in_out,*',childname='upper',_position='<bar')


class ViewFromMailbox(View):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('to_address',width='7em')
        r.fieldcell('from_address',width='7em')
        r.fieldcell('cc_address',width='7em')
        r.fieldcell('bcc_address',width='7em')
        r.fieldcell('uid',width='7em')
        r.fieldcell('body',width='7em')
        r.fieldcell('body_plain',width='7em')
        r.fieldcell('html',width='7em')
        r.fieldcell('subject',width='7em')
        r.fieldcell('send_date',width='7em')
        r.fieldcell('sent',width='7em')
        r.fieldcell('user_id',width='35em')
        r.fieldcell('account_id',width='35em')

class ViewFromDashboard(View):
    
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('send_date',width='7em',dtype='DH')
        r.fieldcell('to_address',width='12em')
        r.fieldcell('from_address',width='12em')
        r.fieldcell('subject',width='100%')
        r.fieldcell('account_id',hidden=True)
        r.fieldcell('mailbox_id',hidden=True)

    def th_order(self):
        return 'send_date:d'

class Form(BaseComponent):
    def th_form(self, form):
        fb = form.record.formbuilder(cols=1,border_spacing='3px',fld_width='100%',width='100%',tdl_width='5em')
        fb.field('to_address')
        fb.field('from_address')
        fb.field('cc_address')
        fb.field('bcc_address')
        fb.field('uid')
        fb.field('body')
        fb.field('body_plain')
        fb.field('html')
        fb.field('subject')
        fb.field('send_date')
        fb.field('sent')
        fb.field('user_id')
        fb.field('account_id')

class FormFromDashboard(Form):

    def th_form(self, form):
        pane = form.record
        pane.div('^.body')
    
    def th_options(self):
        return dict(showtoolbar=False)



