# -*- coding: UTF-8 -*-

# base.py
# Created by Francesco Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name',width='100%')

    def th_order(self):
        return 'name'
        
    def th_query(self):
        return dict(column='name',op='contains', val='%',runOnStart=True)
    def th_options(self):
        return dict()
        
class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2)
        fb.field('name')
        fb.field('parent_id',readOnly=True)

        #bc.contentPane(region='center').remote(self.childrenTH,parent_id='=.pkey')
        
    @public_method
    def childrenTH(self,pane,parent_id=None,**kwargs):
        th = pane.dialogTableHandler(relation='@_children',nodeId='%s_children' %id(pane),maintable='base.element')
        th.view.store.attributes.update(_onBuilt=True)
        
    def th_options(self):
        return dict(dialog_height='300px',dialog_width='600px',dialog_stacked=True)