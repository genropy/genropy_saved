# -*- coding: UTF-8 -*-

# th_user.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class ViewFromCatalog(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@tag_id.code',name='!!Tag',threestate=True)
        r.checkboxcell('view_read',name='VRead',threestate=True)
        r.checkboxcell('view_add',name='VAdd',threestate=True)
        r.checkboxcell('view_del',name='VDel',threestate=True)
        r.checkboxcell('form_read',name='FRead',threestate=True)
        r.checkboxcell('form_add',name='FAdd',threestate=True)
        r.checkboxcell('form_del',name='FDel',threestate=True)
        r.checkboxcell('form_upd',name='FUpd',threestate=True)
        r.checkboxcell('column_read',name='CRead',threestate=True)
        r.checkboxcell('column_upd',name='CUpd',threestate=True)
        
    def th_order(self):
        return '@tag_id.code'
        
    def th_query(self):
        return dict(column='@tag_id.code',op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        

                          
