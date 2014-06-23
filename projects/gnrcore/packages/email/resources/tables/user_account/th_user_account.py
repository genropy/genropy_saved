#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_id',width='35em')
        r.fieldcell('account_id',width='35em')
        r.fieldcell('can_send',width='7em')


    def th_order(self):
        return 'user_id'

    def th_query(self):
        return dict(column='user_id',op='contains', val='',runOnStart=False)

    def th_dialog(self):
        return dict(height='400px',width='600px')

class ViewFromAccount(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_id',width='20em',name='!!User')
        r.fieldcell('can_send',edit=True)
        
    
class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=1,border_spacing='4px')
        fb.field('user_id')
        fb.field('account_id')
        fb.field('can_send')



