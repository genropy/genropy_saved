#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,metadata


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

    def th_top_upperbar(self,top):
        top.slotToolbar('5,sections@in_out,*,sections@sendingstatus',
                        childname='upper',_position='<bar')


    @metadata(isMain=True,_if='inout=="o"',_if_inout='^.in_out.current')
    def th_sections_sendingstatus(self):
        return [dict(code='drafts',caption='!!Drafts',condition="$__is_draft IS TRUE",includeDraft=True),
                dict(code='to_send',caption='!!Ready to send',isDefault=True,condition='$send_date IS NULL AND $sending_attempt IS NULL'),
                dict(code='sending_error',caption='!!Sending error',condition='$send_date IS NULL AND $sending_attempt IS NOT NULL'),
                dict(code='sent',caption='!!Sent',includeDraft=False,condition='$send_date IS NOT NULL'),
                dict(code='all',caption='All',includeDraft=True)]


class ViewOutOnly(View):
        
    def th_top_upperbar(self,top):
        top.slotToolbar('5,sections@sendingstatus',
                        childname='upper',_position='<bar')

    @metadata(isMain=True)
    def th_sections_sendingstatus(self):
        return [dict(code='drafts',caption='!!Drafts',condition="$__is_draft IS TRUE",includeDraft=True),
                dict(code='to_send',caption='!!Ready to send',isDefault=True,condition='$send_date IS NULL AND $sending_attempt IS NULL'),
                dict(code='sending_error',caption='!!Sending error',condition='$send_date IS NULL AND $sending_attempt IS NOT NULL'),
                dict(code='sent',caption='!!Sent',includeDraft=False,condition='$send_date IS NOT NULL'),
                dict(code='all',caption='All',includeDraft=True)]



    def th_options(self):
        return dict()

    def th_condition(self):
        return dict(condition='$in_out=:io',condition_io='O')



class ViewInOnly(View):
    def th_top_upperbar(self,top):
        pass

    def th_condition(self):
        return dict(condition='$in_out=:io',condition_io='I')

    

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
    py_requires = "gnrcomponents/attachmanager/attachmanager:AttachManager"
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.div(margin_right='20px').formbuilder(cols=4,border_spacing='3px',
                                                    fld_width='100%',
                                                    width='100%',colswidth='auto')
        fb.field('to_address',colspan=4)
        fb.field('from_address',colspan=4)
        fb.field('cc_address',colspan=4)
        fb.field('bcc_address',colspan=4)
        fb.field('subject',colspan=4)

        fb.field('uid')
        fb.field('send_date')
        fb.field('sent',html_label=True)
        fb.field('html',html_label=True)
        fb.field('user_id')
        fb.field('account_id')

        fb.field('__is_draft', lbl='Draft')

        

        tc = bc.tabContainer(region='center',margin='2px')
        tc.contentPane(title='Body').simpleTextArea(value='^.record.body',editor=True)
        sc = tc.stackContainer(title='Attachments')
        sc.plainTableHandler(relation='@attachments',pbl_classes=True)
        sc.attachmentGrid(pbl_classes=True)
        tc.dataController("sc.switchPage(in_out=='O'?1:0)",sc=sc.js_widget,in_out='^#FORM.record.in_out')
        tc.contentPane(title='Body plain').simpleTextArea(value='^.record.body_plain',height='100%')
        tc.contentPane(title='Errors', region='center',overflow='hidden').quickGrid('^#FORM.record.sending_attempt')

class FormFromDashboard(Form):

    def th_form(self, form):
        pane = form.record
        pane.div('^.body')
    
    def th_options(self):
        return dict(showtoolbar=False)



