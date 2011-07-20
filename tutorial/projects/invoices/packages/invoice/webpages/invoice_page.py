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
        self.invoice_head(bc.contentPane(region='top',height='15ex'))
        self.invoice_bottom(bc.contentPane(region='bottom',height='10ex'))
        self.invoice_body(bc.borderContainer(region='center'))
        
    def invoice_head(self, pane):
        fb = pane.formbuilder(cols=3,fld_width='7em',margin_left='2em')
        fb.field('number',readOnly=True)
        fb.field('date',readOnly=True)
        fb.field('customer_id',width='15em')
        
    def invoice_body(self, bc):
        bc.div('"includedViewBox" ancora da convertire...',margin='10px')
        
    #NISO: devo tradurre uno dei due invoice_body...
    #def invoice_body_old(self, bc):
    #    iv = self.includedViewBox(bc, label='!!Rows',
    #                              storepath='.@invoice_invoice_row_invoice_id', struct=self.rowstruct(),
    #                              autoWidth=True, add_action=True, del_action=True)
    #    gridEditor = iv.gridEditor()
    #    gridEditor.dbSelect(dbtable='invoice.product', value='^.product_id', gridcell='@product_id.description')
    #    gridEditor.numbertextbox(gridcell='quantity')
    #    gridEditor.currencytextbox(gridcell='price')
    #
    #def invoice_body(self, bc):
    #    self.includedViewBox(bc, label='!!Rows', nodeId='invoice_rows_grid',
    #                         storepath='.@invoice_invoice_row_invoice_id', struct=self.rowstruct(),
    #                         autoWidth=True,
    #                         add_action=True, del_action=True,
    #                         formPars=dict(height='300px', width='400px',
    #                                       add_action=True, del_action=True,
    #                                       title='!!Invoice Row', formCb=self.invoicerow))
    #
    #def invoicerow(self, parentBC, **kwargs):
    #    pane = parentBC.contentPane(**kwargs)
    #    fb = pane.formbuilder(dbtable='invoice.invoice_row')
    #    fb.field('product_id', selected_price='.price')
    #    fb.field('quantity', validate_onAccept='FIRE calculateTotal')
    #    fb.field('price', tag='currencytextbox', validate_onAccept='FIRE calculateTotal')
    #    fb.field('total', readOnly=True)
    #    pane.dataFormula('.total', 'p*q', p='^.price', q='^.quantity')
    #
    #def rowstruct(self,struct):
    #    r = struct.view().rows()
    #    r.cell('@product_id.description', name='Product', width='25em')
    #    r.cell('quantity', name='Quantity', width='6em')
    #    r.cell('price', name='Price', width='10em')
    #    r.cell('total', name='Total', width='10em')

    def invoice_bottom(self, pane):
        tag = 'currencytextbox'
        fb = pane.formbuilder(cols=3,fld_width='6em',lbl_width='3em',margin_left='2em')
        fb.field('net',tag=tag,readOnly=True)
        fb.field('vat',tag=tag,readOnly=True)
        fb.field('total',tag=tag,readOnly=True)
        pane.dataFormula('.net', "rows.sum('total')", rows='=.@invoice_invoice_row_invoice_id', _fired='^calculateTotal')
        pane.dataFormula('.vat', 'dojo.number.round(net*vat_rate/100.0,2)', net='^.net',
                         vat_rate=int(self.site.config['defaults?vat_rate'] or 0))
        pane.dataFormula('.total', 'net+vat', net='^.net', vat='^.vat')
        pane.dataController('FIRE calculateTotal;', _fired='^grids.invoice_rows_grid.onDeletedRow')

    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['date'] = self.workdate