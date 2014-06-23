#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class ViewFromUser(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts',width='10em',name='Datetime')
        r.fieldcell('@notification_id.title',width='15em',name='!!Username')
        r.fieldcell('confirmed',semaphore=True)

    def th_order(self):
        return '__ins_ts:d'

    def th_condition(self):
        return dict(condition='$user_id=:env_user_id')

    def th_options(self):
        return dict(extendedQuery=False,virtualStore=False,readOnly=True,widget='border')

class FormFromUser(BaseComponent):
    def th_form(self, form):
        form.top.popNode('bar')
        pane = form.record.div(position='absolute',top='10px',bottom='10px',left='10px',right='10px',background='white',padding='20px',overflow='auto')
        pane.div('^._message')

    @public_method
    def th_onLoading(self,record, newrecord, loadingParameters, recInfo):
        if not newrecord:
            record['_message'] = self.db.table('adm.user_notification').getNotification(pkey=record['id'])['notification']

class ViewFromNotification(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@user_id.username',width='15em',name='!!Username')

        r.fieldcell('user_id',width='25em')
        r.fieldcell('confirmed',semaphore=True)

    def th_order(self):
        return 'user_id'

    def th_query(self):
        return dict(column='user_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('user_id')
        fb.field('notification_id')
        fb.field('confirmed')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
