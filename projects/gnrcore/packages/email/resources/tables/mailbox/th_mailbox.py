# -*- coding: UTF-8 -*-

# th_office.py
# Created by Francesco Porcari on 2011-04-10.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('account_id',width='12em')
        r.fieldcell('name',width='12em')
        r.fieldcell('user_id',width='12em')

    def th_order(self):
        return 'code'
        
    def th_query(self):
        return dict(column='name',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self,form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=1,border_spacing='4px')
        fb.field('name')
        fb.field('account_id')
        fb.field('user_id')
        bc.contentPane(region='center').remote(self.childrenTH,parent_id='=.pkey',_onRemote='FIRE #FORM.controller.loaded;')
        
    @public_method
    def childrenTH(self,pane,parent_id=None,**kwargs):
        pane.dialogTableHandler(relation='@_children',nodeId='%s_children' %id(pane),condition_built='^#FORM.controller.loaded')
        
    def th_options(self):
        return dict(dialog_height='300px',dialog_width='600px',dialog_stacked=True)
    
    @public_method
    def th_onLoading(self,record,newrecord,loadingParameters,recInfo):
        if newrecord:
            if record['parent_code']:
                record['account_id'] = record['@parent_code.account_id']
        