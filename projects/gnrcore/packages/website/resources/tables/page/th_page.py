# -*- coding: UTF-8 -*-
# th_page.py

from gnr.web.gnrwebpage import BaseComponent


    
class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('permalink', width='15%')
        r.fieldcell('title', width='35%',name='Title')
        r.fieldcell('@folder.title', width='50%',name='Folder')
        r.fieldcell('path')
        return struct
        
    def th_order(self):
        return 'permalink'
        
    def th_query(self):
        return dict(column='permalink',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self,form):
        pass