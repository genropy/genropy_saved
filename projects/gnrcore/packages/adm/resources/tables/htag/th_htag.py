# -*- coding: UTF-8 -*-

# th_user.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        
        
    def th_order(self):
        return 'code'
        
    def th_query(self):
        return dict(column='code',op='contains', val='%')

class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
                          