#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('usage_scope')
        r.fieldcell('__ins_user', name='User Ins')
        r.fieldcell('user_id')
        r.fieldcell('use_ts')
        r.fieldcell('used_by')
        r.fieldcell('note')
        r.fieldcell('remaining_usages')
        r.fieldcell('expiry_date')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')


class Form(BaseComponent):
            
    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.field('code')
        fb.field('usage_scope', lbl='Scope',values=self.db.table('adm.authorization').getUsageScopes(),
                    tag='filteringSelect',validate_notnull=True)
        fb.simpleTextArea(value='^.note', lbl='!!Note',
                          height='10ex', width='100%', speech=True, editor=True)
        fb.field('remaining_usages', lbl='Max usages')
        fb.field('expiry_date', lbl='Exp date')



    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
