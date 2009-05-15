#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag
from datetime import datetime

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='invc.product'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView,public:RecordHandler'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Products'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Products'
        
    def columnsBase(self,):
        return """code/Code:6,description,price"""
                  
            
    def orderBase(self):
        return 'code'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='code',op='contains', val='%', runOnStart=True)

############################## FORM METHODS ##################################
 
    def formBase(self, parentBC,disabled=False, **kwargs):
        tc=parentBC.tabContainer(margin='5px', **kwargs)
        self.productPage(tc.contentPane(title='!!Product'),disabled=disabled)
        self.invoicesPage(tc.borderContainer(title='!!Invoices'),disabled=disabled)
        self.rowsPage(tc.borderContainer(title='!!Invoices Rows'),disabled=disabled)
        
    def productPage(self,pane,disabled=False):
        fb=pane.formbuilder(cols=2, border_spacing='6px',disabled=disabled)
        fb.field('code',readOnly=True)
        fb.field('description')
        fb.field('product_type')
        fb.field('price', tag='currencyTextbox')
        pane.dataFormula("form.title", "code+'-'+description",code="^.code",description="^.description")

    def invoicesPage(self,bc,disabled=False):
        topbc=bc.borderContainer(region='top', height='50%',splitter= True)
        centerbc=bc.borderContainer(region='center')
        self.recordDialog('invc.invoice',firedPkey='^fired.invoice_id',height='400px',width='700px',title='Invoice',
                            formCb=self.invoiceForm, onSaved='FIRE reloadinvoice')
        bc.dataSelection('selections.invoices','invc.invoice',where='@invc_invoice_row_invoice_id.product_id=:prid',
                            prid='^.id',columnsFromView='invoices_grid', _fired='^reloadinvoice')
        bc.dataSelection('selections.invoice_rows','invc.invoice_row',where='invoice_id=:invid', invid='^aux.invoice_id',columnsFromView='rows_from_invoice')
        
        self.includedViewBox(topbc,nodeId='invoices_grid', label='!!Invoices',
                             storepath='selections.invoices',
                             columns="""number,date,customer,city,net,vat,total""",
                             selectedId='aux.invoice_id',
                             connect_onRowDblClick='FIRE fired.invoice_id=GET aux.invoice_id',
                             table='invc.invoice', autoWidth=True)
        iv = self.includedViewBox(centerbc, nodeId='rows_from_invoice', label='!!Invoice Rows',
                            storepath='selections.invoice_rows',
                            columns="""@product_id.code,@product_id.description,quantity,price,total""",
                            table='invc.invoice_row', autoWidth=True)
   
    def invoiceForm(self,parentContainer,disabled,table):
        pane=parentContainer.contentPane()
        self.invoice_head(pane,disabled,table)
        
    def invoice_head (self,pane,disabled,table):
        fb=pane.formbuilder(dbtable=table,cols=2, width='600px', border_spacing='4px',disabled=disabled)
        fb.field('number',readOnly= True, width='100%')
        fb.field('date',readOnly= True, width='100%')
        fb.field('customer_id',width='100%',colspan='2')        
                             
    def rowsPage(self,bc,disabled=False):
        self.includedViewBox(bc,label='!!Invoices Rows', filterOn='Customer:@invoice_id.customer,City:@invoice_id.city,Price:price',
                             storepath='.@invc_invoice_row_product_id',
                             columns="""@invoice_id.number,@invoice_id.date,@invoice_id.customer,@invoice_id.city,
                                        quantity,price,total""",
                             table='invc.invoice_row', autoWidth=True)                                     
  
############################## RPC_METHODS ###################################       

