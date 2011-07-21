#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    maintable = 'invoice.invoice'
    py_requires = 'public:TableHandlerMain'
    
    def th_form(self, form):
        bc = form.center.borderContainer()
        self.invoice_head(bc.contentPane(region='top',height='15ex',datapath='.record'))
        self.invoice_bottom(bc.contentPane(region='bottom',height='10ex',datapath='.record'))
        self.invoice_body(bc.contentPane(region='center',datapath='.record'))
        
    def invoice_head(self, pane):
        fb = pane.formbuilder(cols=3,fld_width='7em',margin_left='2em')
        fb.field('number',readOnly=True)
        fb.field('date',readOnly=True)
        fb.field('customer_id',width='15em')
        
    def invoice_body(self, pane):
        pane.dialogTableHandler(relation='@invoice_rows',
                                viewResource=':ViewFromInvoice',
                                formResource=':FormFromInvoice',
                                dialog_height='300px',
                                dialog_width='400px')
                                
    def invoice_bottom(self, pane):
        tag = 'currencytextbox'
        fb = pane.formbuilder(cols=3,fld_width='6em',lbl_width='3em',margin_left='2em')
        fb.field('net',tag=tag,readOnly=True)
        fb.field('vat',tag=tag,readOnly=True)
        fb.field('total',tag=tag,readOnly=True)
        pane.dataFormula('.net', "rows.sum('total')", rows='=.@invoice_rows', _fired='^calculateTotal')
        pane.dataFormula('.vat', 'dojo.number.round(net*vat_rate/100.0,2)', net='^.net',
                         vat_rate=int(self.site.config['defaults?vat_rate'] or 0))
        pane.dataFormula('.total', 'net+vat', net='^.net', vat='^.vat')
        #NISO: correggere l'indirizzo del "_fired"
        pane.dataController('FIRE calculateTotal;', _fired='^grids.invoice_rows_grid.onDeletedRow')

    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['date'] = self.workdate