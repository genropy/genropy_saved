#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    maintable = 'invoice.customer'
    py_requires = 'public:TableHandlerMain'
        
    def th_form(self,form,**kwargs):
        bc = form.center.borderContainer()
        tc = bc.tabContainer(margin='5px',**kwargs)
        self.page1(tc.borderContainer(title='!!Profiles',datapath='.record'))
        self.page2(tc.borderContainer(title='!!Invoices'))

    def page1(self,bc):
        fb = bc.formbuilder(cols=2,dbtable='invoice.customer')
        fb.field('code',readOnly = not self.isDeveloper())
        fb.field('name',autoFocus=True)
        fb.field('country',rowcaption='$name')
        fb.field('address')
        fb.field('zip')
        fb.field('city')

    def page2(self, bc):
        bc.div('hello!')
        #self.includedViewBox(bc, label='!!Invoices',
        #                     storepath='.@invoice_invoice_customer_id',
        #                     columns="""number,date,net,vat,total""",
        #                     table='invoice.invoice', autoWidth=True)
                             
    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            country = self.site.config('defaults?country')
            record['country'] = country