#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('account_name',width='35em')
        r.fieldcell('address',width='35em')
        r.fieldcell('full_name',width='80em')
        r.fieldcell('host',width='80em')
        r.fieldcell('port',width='7em')
        r.fieldcell('protocol_code',width='35em')
        r.fieldcell('tls',width='7em')
        r.fieldcell('ssl',width='7em')
        r.fieldcell('username',width='80em')
        r.fieldcell('password',width='80em')
        r.fieldcell('last_uid',width='7em')
        return struct

    def th_order(self):
        return 'account_name'

    def th_query(self):
        return dict(column='account_name',op='contains', val='%',runOnStart=False)

    def th_dialog(self):
        return dict(height='400px',width='600px')


class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',height='50%', datapath='.record')
        bottom = bc.contentPane(region='center')
        fb = top.formbuilder(cols=1,border_spacing='4px')
        fb.field('account_name')
        fb.field('address')
        fb.field('full_name')
        fb.field('host')
        fb.field('port')
        fb.field('protocol_code')
        fb.field('tls')
        fb.field('ssl')
        fb.field('username')
        fb.field('password')
        fb.field('last_uid')
        fb.button('check email', action='PUBLISH check_email')
        fb.dataRpc('dummy', self.check_imap, subscribe_check_email=True, account_id='=.id')
        th = bottom.dialogTableHandler(relation='@messages',
                                   dialog_height='600px',
                                   dialog_width='800px',
                                   dialog_title='Message')

    @public_method
    def check_imap(self, account_id=None):
        self.db.table('email.account').check_imap(self, account=account_id)
