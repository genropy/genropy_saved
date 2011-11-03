#!/usr/bin/env python
# encoding: utf-8
"""
th_product.py

Created by Filippo Astolfi on 2011-07-20.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='20%')
        r.fieldcell('description',width='50%')
        r.fieldcell('price',width='30%')
        
    def th_order(self):
        return 'code'
        
    def th_query(self):
        return dict(column='code',op='contains',val='%',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pass