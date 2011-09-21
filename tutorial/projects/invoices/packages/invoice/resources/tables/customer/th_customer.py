#!/usr/bin/env python
# encoding: utf-8
"""
th_customer.py

Created by Filippo Astolfi on 2011-07-19.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='5em')
        r.fieldcell('name',width='20em')
        r.fieldcell('address',width='100%')
        r.fieldcell('zip',width='5em')
        r.fieldcell('city',width='20em')
        
    def th_order(self):
        return 'name'
        
    def th_query(self):
        return dict(column='name',op='contains',val='%',runOnStart=True)
        
    def th_top_a(self,top):
        top.bar.replaceSlots('#','#,bottone')
        top.bar.bottone.button('!!Print',action='PUBLISH tablehandler_run_script="print","customer_print";')
        
class Form(BaseComponent):
    def th_form(self, form):
        pass