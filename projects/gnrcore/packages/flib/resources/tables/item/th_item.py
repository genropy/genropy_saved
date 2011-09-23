# -*- coding: UTF-8 -*-
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('title', name='!!Title')
        r.fieldcell('description', name='!!Description')
        r.fieldcell('url', name='!!Url')
        r.fieldcell('path', name='!!Path')
        r.fieldcell('thumb_url', name='!!Url')
        r.fieldcell('thumb_path', name='!!Path')
        r.fieldcell('file_type', name='!!File type')
        r.fieldcell('ext', name='!!Extension')
        r.fieldcell('username', name='!!User')
        
    def th_order(self):
        return 'description'
        
    def th_query(self):
        return dict(column='description',op='contains',val='',runOnStart=True)
    
class LoadedFilesView(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell("title", width='10em', zoom=True)
        r.fieldcell("description", width='100%', zoom=True)
        r.cell("_thumb", width='5em', name='!!Thumb', calculated=True)
                
        
class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        return
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',
                              margin_top='1em')
        fb.field('title', lbl='!!Title')
        fb.field('description', lbl='!!Description')
        fb.field('url', lbl='!!Url')
        fb.field('path', lbl='!!Path')
        fb.field('thumb_url', lbl='!!Url')
        fb.field('thumb_path', lbl='!!Path')
        fb.field('file_type', lbl='!!File type')
        fb.field('ext', lbl='!!Extension')
        fb.field('username', lbl='!!User')