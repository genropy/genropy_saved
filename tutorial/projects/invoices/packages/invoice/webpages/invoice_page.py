#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    maintable = 'invoice.invoice'
    py_requires = 'public:TableHandlerMain'
    #css_icons = 'retina/violet'
    
    def th_form(self, form):
        bc = form.center.borderContainer()
        self.invoice_head(bc.contentPane(region='top',height='5ex',datapath='.record'))
        self.invoice_body(bc.contentPane(region='center'))
        self.invoice_bottom(bc.contentPane(region='bottom',height='5ex',datapath='.record'))
        
    def invoice_head(self, pane):
        fb = pane.formbuilder(cols=3,fld_width='6em',lbl_width='3em')
        fb.field('number',readOnly=True,lbl_width='4em')
        fb.field('date',readOnly=True)
        fb.field('customer_id',width='15em',hasDownArrow=True)
        
    def invoice_body(self, pane):
        pane.dialogTableHandler(relation='@invoice_rows',
                                viewResource=':ViewFromInvoice',
                                formResource=':FormFromInvoice',
                                pbl_classes=True,
                                dialog_height='300px',
                                dialog_width='400px')
                                
    def invoice_bottom(self, pane):
        fb = pane.formbuilder(cols=3,fld_width='6em',lbl_width='3em')
        fb.field('net', tag='currencytextbox', readOnly=True)
        fb.field('vat', tag='currencytextbox', readOnly=True, lbl_width='2em')
        fb.field('total', tag='currencytextbox', readOnly=True)
        #pane.dataFormula('.net', "rows.sum('total')",
        #                  rows='=.@invoice_rows',
        #                  _fired='^.calculateTotal')
        #pane.dataFormula('.vat', 'net*vat_rate/100',
        #                 net='^.net',
        #                 vat_rate=int(self.site.config['defaults?vat_rate'] or 0))
        #pane.dataFormula('.total', 'net+vat', net='^.net', vat='^.vat')
        #pane.dataController("""FIRE .calculateTotal;
        #                       alert('It works!');""",_fired='^#FORM.invoice_invoice_row.view.count.total')
        #                                          #_fired='^grids.invoice_rows_grid.onDeletedRow'
                                                  
    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['date'] = self.workdate