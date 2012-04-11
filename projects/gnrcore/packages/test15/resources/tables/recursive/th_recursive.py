# -*- coding: UTF-8 -*-

# th_recursive.py
# Created by Francesco Porcari on 2011-09-18.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebpage import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description',name='Description',width='15em')
        r.cell('_parent_h_description',width='30%')
        r.cell('hierarchical_description',width='100%')

    def th_query(self):
        return dict(column='description',op='contains',val='',runOnStart=True)
    
    def th_order(self):
        return 'hierarchical_description'
        
class Form(BaseComponent):
    def th_form(self,form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2)
        fb.field('description')
        bc.contentPane(region='center').remote(self.childrenTH,parent_id='=.pkey',_onRemote='FIRE #FORM.controller.loaded;')
        
    @public_method
    def childrenTH(self,pane,parent_id=None,**kwargs):
        pane.dialogTableHandler(relation='@_children',nodeId='%s_children' %id(pane),condition_built='^#FORM.controller.loaded')
        
    def th_options(self):
        return dict(dialog_height='300px',dialog_width='600px',dialog_stacked=True)