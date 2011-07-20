#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    maintable = 'invoice.customer'
    py_requires = 'public:TableHandlerMain'
    
    def th_form(self, form, **kwargs):
        tc = form.center.tabContainer(margin='5px',**kwargs)
        self.page1(tc.borderContainer(title='!!Profiles',_class='pbl_roundedGroup',datapath='.record'))
        self.page2(tc.contentPane(title='!!Invoices',_class='pbl_roundedGroup'))

    def page1(self, bc):
        fb = bc.formbuilder(cols=2,dbtable='invoice.customer')
        fb.field('code',readOnly = not self.isDeveloper())
        fb.field('name',autoFocus=True)
        fb.field('country',rowcaption='$name')
        fb.field('address')
        fb.field('zip')
        fb.field('city')

    def page2(self, pane):
        th = pane.plainTableHandler(relation='@invoices',pbl_classes=True,
                                    viewResource=':ViewFromCustomer')
        #self.includedViewBox(bc,table='invoice.invoice',label='!!Invoices',
        #                     storepath='.@invoice_invoice_customer_id',
        #                     columns="""number,date,net,vat,total""",
        #                     autoWidth=True)
                             
    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            country = self.site.config('defaults?country')
            record['country'] = country