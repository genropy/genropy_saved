#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
class GnrCustomWebPage(object):
    maintable = 'invc.invoice'
    py_requires = 'public:Public,standard_tables:TableHandler,public:IncludedView'

    ######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Invoice'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def tableWriteTags(self):
        return 'user'

    def tableDeleteTags(self):
        return 'admin'

    def barTitle(self):
        return '!!Invoice'

    def columnsBase(self, ):
        return """number,date,customer,city,net,vat,total"""

    def orderBase(self):
        return 'number'

    def conditionBase(self):
        pass

    def queryBase(self):
        return dict(column='customer', op='contains', val='%')

    ############################## FORM METHODS ##################################

    def formBase(self, parentBC, disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        self.invoice_head(bc.contentPane(region='top', height='20ex'), disabled=disabled)
        self.invoice_bottom(bc.contentPane(region='bottom', height='10ex'), disabled=disabled)
        self.invoice_body(bc.borderContainer(region='center'), disabled=disabled)

    def invoice_head (self, pane, disabled=False):
        fb = pane.formbuilder(cols=2, width='600px', border_spacing='4px', disabled=disabled)
        fb.field('number', readOnly=True, width='100%')
        fb.field('date', readOnly=True, width='100%')
        fb.field('customer_id', width='100%', colspan='2')

    def invoice_body_old(self, bc, disabled=False):
        iv = self.includedViewBox(bc, label='!!Rows',
                                  storepath='.@invc_invoice_row_invoice_id', struct=self.rowstruct(),
                                  autoWidth=True, add_action=True, del_action=True)
        gridEditor = iv.gridEditor()
        gridEditor.dbSelect(dbtable='invc.product', value='^.product_id', gridcell='@product_id.description')
        gridEditor.numbertextbox(gridcell='quantity')
        gridEditor.currencytextbox(gridcell='price')

    def invoice_body(self, bc, disabled=False):
        self.includedViewBox(bc, label='!!Rows', nodeId='invoice_rows_grid',
                             storepath='.@invc_invoice_row_invoice_id', struct=self.rowstruct(),
                             autoWidth=True,
                             add_action=True, del_action=True,
                             formPars=dict(height='300px', width='400px',
                                           add_action=True, del_action=True,
                                           title='!!Invoice Row', formCb=self.invoicerow))

    def invoicerow(self, parentBC, disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=1, dbtable='invc.invoice_row', border_spacing='4px', disabled=disabled)
        fb.field('product_id', selected_price='.price')
        fb.field('quantity', validate_onAccept='FIRE calculateTotal')
        fb.field('price', tag='currencytextbox', validate_onAccept='FIRE calculateTotal')
        fb.field('total', readOnly=True)
        pane.dataFormula('.total', 'p*q', p='^.price', q='^.quantity')

    def rowstruct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('@product_id.description', name='Product', width='25em')
        r.cell('quantity', name='Quantity', width='6em')
        r.cell('price', name='Price', width='10em')
        r.cell('total', name='Total', width='10em')
        return struct

    def invoice_bottom(self, pane, disabled=False):
        fb = pane.formbuilder(cols=3, width='600px', border_spacing='4px', disabled=disabled)
        fb.field('net', tag='currencytextbox', readOnly=True, width='100%')
        fb.field('vat', tag='currencytextbox', readOnly=True, width='100%')
        fb.field('total', tag='currencytextbox', readOnly=True, width='100%')
        pane.dataFormula('.net', "rows.sum('total')", rows='=.@invc_invoice_row_invoice_id', _fired='^calculateTotal')
        pane.dataFormula('.vat', 'dojo.number.round(net*vat_rate/100.0,2)', net='^.net',
                         vat_rate=int(self.site.config['defaults?vat_rate'] or 0))
        pane.dataFormula('.total', 'net+vat', net='^.net', vat='^.vat')
        pane.dataController('FIRE calculateTotal;', _fired='^grids.invoice_rows_grid.onDeletedRow')

    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['date'] = self.workdate