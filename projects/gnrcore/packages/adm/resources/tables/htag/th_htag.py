# -*- coding: UTF-8 -*-

# th_user.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('hierarchical_description')
        
    def th_order(self):
        return 'code'
        
    def th_query(self):
        return dict(column='code',op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.div(margin='5px').formbuilder(cols=2, border_spacing='2px',colswidth='20em')
        fb.field('code')
        fb.field('description')
        fb.field('isreserved', lbl='',label='Is reserved')
        fb.field('note')
        self.usersPane(bc.contentPane(region='center',datapath='#FORM'))

    def usersPane(self,pane):
        pane.plainTableHandler(relation='@users',viewResource=':ViewFromTag',picker='user_id',picker_viewResource=True,
                                delrow=True,pbl_classes=True,margin='2px')
 

    def th_options(self):
        return dict(hierarchical=True)