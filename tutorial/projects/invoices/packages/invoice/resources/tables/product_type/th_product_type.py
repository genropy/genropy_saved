#!/usr/bin/env python
# encoding: utf-8
"""
th_product_type.py

Created by Softwell on 2011-07-20.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='7em')
        r.fieldcell('description',width='20em')
        
    def th_order(self):
        return 'code'
        
    def th_query(self):
        return dict(column='description',op='contains',val='%',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pass