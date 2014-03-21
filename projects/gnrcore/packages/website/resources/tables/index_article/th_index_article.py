# -*- coding: UTF-8 -*-
# th_index_article.py

from gnr.web.gnrwebpage import BaseComponent


    
class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_counter', width='5%')
        r.fieldcell('@page_id.permalink', width='15%')
        r.fieldcell('@page_id.@folder.title', width='85%',name='Folder')
        return struct
        
    def th_order(self):
        return '@page_id.permalink'
        
    def th_query(self):
        return dict(column='@page_id.permalink',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self,form):
        bc=form.center.borderContainer()