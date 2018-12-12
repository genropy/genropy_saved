# -*- coding: utf-8 -*-
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_hiddencolumns(self):
        return '_h_count'
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('hierarchical_child_code', name='!!Code')
        r.fieldcell('hierarchical_description', name='!!Description')
        
    def th_order(self):
        return '_h_count'
        
    def th_query(self):
        return dict(column='description',op='contains',val='')
        
class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder()
        fb.field('child_code')
        fb.field('description')
        bc.contentPane(region='center').plainTableHandler(relation='@items',pbl_classes=True,margin='2px')


    def th_options(self):
        return dict(hierarchical=True)