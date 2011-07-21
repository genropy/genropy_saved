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
        r.cell('quantity',name='!!Quantity',width='6em')
        r.cell('price',name='!!Price',width='10em')
        r.cell('total',name='!!Total',width='10em')
        
    def th_order(self):
        return '@product_id.description'
        
class FormFromInvoice(BaseComponent):
    def th_form(self, form):
        pane = form.record.contentPane()
        pane.dataFormula('.net', "rows.sum('total')", rows='=.@invoice_rows', _fired='^calculateTotal')
        fb = pane.formbuilder()
        fb.field('product_id',selected_price='.price')
        fb.field('quantity',validate_onAccept='FIRE calculateTotal')
        fb.field('price',tag='currencytextbox',validate_onAccept='FIRE calculateTotal')
        fb.field('total',readOnly=True)
        pane.dataFormula('.total','p*q',p='^.price',q='^.quantity')