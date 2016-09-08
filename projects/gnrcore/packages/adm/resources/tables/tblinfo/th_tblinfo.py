#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tbl')
        r.fieldcell('pkg')
        r.fieldcell('description')

    def th_order(self):
        return 'tbl'

    def th_query(self):
        return dict(column='tbl', op='contains', val='')


    def th_top_custom(self,top):
        top.bar.replaceSlots('searchOn','searchOn,sections@pkg')

    def th_options(self):
        return dict(virtualStore=False)



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('tbl')
        fb.field('pkg')
        fb.field('description')
        tc = bc.tabContainer(region='center',margin='2px')
        self.authorizationsItems(tc.contentPane(title='Authorization'))

    def authorizationsItems(self,pane):
        pane.dialogTableHandler(relation='@items',condition='$item_type=:t',
                                condition_t='AUTH',default_item_type='AUTH',
                                viewResource='AuthItemView',formResource='AuthItemForm')

    def th_options(self):
        return dict(dialog_parentRatio=0.9)
