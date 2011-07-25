#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2011-07-20.
Copyright (c) 2008 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    maintable = 'invoice.product'
    py_requires = 'public:TableHandlerMain'
    
    def th_form(self, form, **kwargs):
        tc = form.center.tabContainer(margin='5px', **kwargs)
        self.productPage(tc.contentPane(title='!!Product',datapath='.record'))
        #self.invoicesPage(tc.borderContainer(title='!!Invoices'))
        #self.rowsPage(tc.borderContainer(title='!!Invoices Rows'))

    def productPage(self, pane):
        fb = pane.formbuilder(cols=2,lbl_width='7em',fld_width='20em')
        fb.field('code',readOnly=True,width='7em')
        fb.field('description')
        fb.field('price',tag='currencyTextbox',width='7em')
        fb.field('product_type',hasDownArrow=True)
        fb.field('full_description',tag='simpleTextArea',width='100%',height='8ex',colspan=2,lbl_vertical_align='top')
        pane.dataFormula("form.title", "code+'-'+description", code="^.code", description="^.description")
        pane.dataFormula(".full_description", "description", description='^.description',
                         full_description='=.full_description', _if='!full_description')
                         
    #def invoicesPage(self, bc):
    #    topbc = bc.borderContainer(region='top', height='50%', splitter=True)
    #    centerbc = bc.borderContainer(region='center')
    #    self.recordDialog('invoice.invoice', firedPkey='^fired.invoice_id', height='400px', width='700px', title='Invoice',
    #                      formCb=self.invoiceForm, onSaved='FIRE reloadinvoice')
    #    bc.dataSelection('selections.invoices', 'invoice.invoice', where='@invoice_invoice_row_invoice_id.product_id=:prid',
    #                     prid='^.id', columnsFromView='invoices_grid', _fired='^reloadinvoice')
    #    bc.dataSelection('selections.invoice_rows','invoice.invoice_row', where='invoice_id=:invid',
    #                     invid='^aux.invoice_id', columnsFromView='rows_from_invoice')
    #
    #    self.includedViewBox(topbc, nodeId='invoices_grid', label='!!Invoices',
    #                         storepath='selections.invoices',
    #                         columns="""number,date,customer,city,net,vat,total""",
    #                         selectedId='aux.invoice_id',
    #                         connect_onRowDblClick='FIRE fired.invoice_id=GET aux.invoice_id',
    #                         table='invoice.invoice', autoWidth=True)
    #    iv = self.includedViewBox(centerbc, nodeId='rows_from_invoice', label='!!Invoice Rows',
    #                              storepath='selections.invoice_rows',
    #                              columns="""@product_id.code,@product_id.description,quantity,price,total""",
    #                              table='invoice.invoice_row', autoWidth=True)
    #
    #def invoiceForm(self, parentContainer, disabled, table):
    #    pane = parentContainer.contentPane()
    #    self.invoice_head(pane, disabled, table)
    #
    #def invoice_head (self, pane, disabled, table):
    #    fb = pane.formbuilder(dbtable=table, cols=2, width='600px', border_spacing='4px', disabled=disabled)
    #    fb.field('number', readOnly=True, width='100%')
    #    fb.field('date', readOnly=True, width='100%')
    #    fb.field('customer_id', width='100%', colspan='2')

    #def rowsPage(self, bc):
        #self.includedViewBox(bc, label='!!Invoices Rows',
        #                     filterOn='Customer:@invoice_id.customer,City:@invoice_id.city,Price:price',
        #                     storepath='.@invoice_invoice_row_product_id',
        #                     columns="""@invoice_id.number,@invoice_id.date,@invoice_id.customer,@invoice_id.city,
        #                                quantity,price,total""",
        #                     table='invoice.invoice_row', autoWidth=True)