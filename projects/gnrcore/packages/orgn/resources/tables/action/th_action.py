#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('typename')
        r.fieldcell('assigned_to')
        r.fieldcell('priority')
        r.fieldcell('days_before')
        #r.fieldcell('done_ts')

    def th_order(self):
        return 'typename'

    def th_query(self):
        return dict(column='typename', op='contains', val='')



    def th_sections_orgn(self):
        return [dict(code='orgn',caption='!!To do',condition='$done_ts IS NULL'),
                dict(code='done',caption='!!Done',condition='$done_ts IS NOT NULL')]


    def th_top_custom(self,top):
        bar = top.bar.replaceSlots('#','5,actiontitle,5,sections@orgn,10,sections@priority,*,delrow,addrow,5')
        bar.actiontitle.div('!!Actions',_class='frameGridTitle')

class ViewPlugin(View):
    def th_hiddencolumns(self):
        return '$connected_fkey'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('typename')
        r.fieldcell('priority')
        r.fieldcell('connected_description',name='Connected to')

    def th_top_custom(self,top):
        top.bar.replaceSlots('#','*,sections@priority,*')


class Form(BaseComponent):
    def th_form(self, form):
        form.record


