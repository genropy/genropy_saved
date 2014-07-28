# -*- coding: UTF-8 -*-

# subscription.py

from gnr.web.gnrwebpage import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tablename',name_long='!!Tablename') #table fullname 
        r.fieldcell('dbstore',name_long='!!Store')
        
    def th_query(self):
        return dict(column='tablename',op='contains', val='')



class Form(BaseComponent):
    def th_form(self,form):
        form.record