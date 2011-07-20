#!/usr/bin/env python
# encoding: utf-8
"""
th_invoice.py

Created by Filippo Astolfi on 2011-07-20.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('number',width='5em')
        r.fieldcell('date',width='5em')
        r.fieldcell('customer',width='5em')
        r.fieldcell('city',width='5em')
        r.fieldcell('net',width='5em')
        r.fieldcell('vat',width='5em')
        r.fieldcell('total',width='5em')
        
    def th_order(self):
        return 'number'
        
    def th_query(self):
        return dict(column='customer',op='contains',val='%',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pass

class ViewFromInvoice(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('number',width='5em')
        r.fieldcell('date',width='5em')
        r.fieldcell('net',width='5em')
        r.fieldcell('vat',width='5em')
        r.fieldcell('total',width='5em')
        
    def th_order(self):
        return 'number'