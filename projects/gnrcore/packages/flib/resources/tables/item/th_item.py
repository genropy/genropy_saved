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

             
class ThumbsView(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell("title", width='100%', zoom=True)
        r.cell("_thumb", width='5em', name='!!Thumb', calculated=True)  
    
    def th_order(self):
        return 'title'
         
    @public_method
    def th_applymethod(self,selection):
        def apply_thumb(row):
            ext_img = self.getResourceUri('filetype_icons/%s.png' % row['ext'][1:].lower())\
            or self.getResourceUri('filetype_icons/_blank.png')
            return dict(_thumb='<img border=0 draggable="false" src="%s" />' % (row['thumb_url'] or ext_img))
        selection.apply(apply_thumb)

class ImagesView(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.cell('title',width='5em')
        r.cell("image_drag", width='100%', name='!!Thumb', calculated=True)  
        r.cell('description',hidden=True)
        r.cell('url',hidden=True)
        r.cell('path',hidden=True)

    def th_order(self):
        return 'description'
    
    def th_view(self,view):
        view.grid.attributes.update(draggable_row=False)
        
    @public_method
    def th_applymethod(self,selection):
        def apply_thumb(row):
            ext_img = self.getResourceUri('filetype_icons/%s.png' % row['ext'][1:].lower())\
            or self.getResourceUri('filetype_icons/_blank.png')
            return dict(image_drag="""<img border=0 draggable="true" src="%s" height="60px" />""" % (row['url'] or ext_img))
        selection.apply(apply_thumb)
        
    def th_top_custom(self,top):
        top.bar.replaceSlots('#','searchOn',searchOn_width='5em')
        
class LoadedFilesView(ThumbsView):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell("title", width='10em', zoom=True)
        r.fieldcell("description", width='100%', zoom=True)
        r.cell("_thumb", width='5em', name='!!Thumb', calculated=True)
    
    def th_view(self,view):
        view.grid.attributes.update(draggable_row=True,
                                    onDrag="""
                                    var row = dragValues.gridrow.rowdata;
                                    dragValues['flib_element'] = row._pkey;                                
                             """)
    
    def th_order(self):
        return 'description'
        
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