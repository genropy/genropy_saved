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
        fb = bc.formbuilder(cols=2)
        fb.field('code',tooltip='!!Automatically added',readOnly = not self.isDeveloper())
        fb.field('name',validate_case='c')
        fb.field('address')
        fb.field('zip')
        fb.field('city',validate_case='t')
        
        #NISO: non va la dbSelect...
        #fb.field('country',name='!!Country',tag='dbSelect',dbtable='glbl.nazione',value='.country',
        #          columns='$code,$name',hasDownArrow=True)        
                  
    def page2(self, pane):
        th = pane.plainTableHandler(relation='@invoices',
                                    viewResource=':ViewFromCustomer')
                                    
    #def onLoading(self, record, newrecord, loadingParameters, recInfo):
    #    if newrecord:
    #        country = self.site.config('defaults?country')
    #        record['country'] = country