#!/usr/bin/env python
# encoding: utf-8
"""
th_invoice_row.py

Created by Filippo Astolfi on 2011-07-20.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent

class ViewFromInvoice(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.cell('@product_id.description',name='!!Product',width='25em')
        r.cell('quantity',name='!!Quantity',width='8em')
        r.cell('price',name='!!Price',width='8em')
        r.cell('total',name='!!Total',width='8em')
        
    def th_order(self):
        return '@product_id.description'
        
class FormFromInvoice(BaseComponent):
    def th_form(self, form):
        pane = form.record.contentPane()
        fb = pane.formbuilder(fld_width='18em')
        fb.field('product_id',selected_price='.price')
        fb.field('quantity')
        fb.field('price',readOnly=True)
        fb.field('total',readOnly=True)
        pane.dataFormula('.total','p*q',p='^.price',q='^.quantity')