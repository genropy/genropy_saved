# -*- coding: UTF-8 -*-
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        
        r.fieldcell('code', name='!!Code')
        r.fieldcell('description', name='!!Description')
        
    def th_order(self):
        return 'description'
        
    def th_query(self):
        return dict(column='description',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record

        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',
                              margin_top='1em')
        r.field('code', lbl='!!Code')
        r.field('description', lbl='!!Description')