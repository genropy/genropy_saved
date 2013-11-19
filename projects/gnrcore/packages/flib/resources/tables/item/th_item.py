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
        r.fieldcell('url', name='!!Url',template='<a href="#?download=True">download</a>')
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
        r.cell('title',width='5em',hidden=True)
        r.cell('description',width='5em',hidden=True)

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
            url = row['url'] or ext_img


            url = self.externalUrl(url)
            title = row['title']
            description = row['description']
            if row['ext'] not in ('jpg','png','jpeg'):
                image_drag="""<div draggable="true"><div>%s</div><img border=0 draggable="false" title="%s" src="%s" height="60px"/>%s</div>""" %(title,description,ext_img,row['path'])
            else:
                image_drag="""<div><div>%s</div><img border=0 draggable="true" title="%s" src="%s" height="60px"/></div>""" %(title,description,url)

            return dict(image_drag=image_drag)
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
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',
                              margin_top='1em')
        width='60em'
        fb.field('title', lbl='!!Title', width=width)
        fb.field('description', lbl='!!Description', width=width)
        fb.field('url', lbl='!!Url', width=width)
        fb.field('path', lbl='!!Path', width=width)
        fb.field('thumb_url', lbl='!!Url', width=width)
        fb.field('thumb_path', lbl='!!Path', width=width)
        fb.field('file_type', lbl='!!File type', width=width)
        fb.field('ext', lbl='!!Extension', width=width)
        fb.field('username', lbl='!!User', width=width)