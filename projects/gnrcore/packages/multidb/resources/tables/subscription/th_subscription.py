# -*- coding: UTF-8 -*-

# subscription.py

from gnr.web.gnrwebpage import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tablename',name_long='!!Tablename') #table fullname 
        r.fieldcell('rec_pkey',name_long='!!Pkey') # if rec_pkey == * means all records
        r.fieldcell('dbstore',name_long='!!Store')
        



class Form(BaseComponent):
    def th_form(self,form):
        pass