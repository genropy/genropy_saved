#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class View(BaseComponent):

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
        return struct

    def th_order(self):
        return 'to_address'

    def th_query(self):
        return dict(column='to_address',op='contains', val='%',runOnStart=False)

    def th_dialog(self):
        return dict(height='400px',width='600px')


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=1,border_spacing='4px')
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


