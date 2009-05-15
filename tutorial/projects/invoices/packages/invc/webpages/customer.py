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
    maintable='invc.customer'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Customers'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Customers'
        
    def columnsBase(self,):
        return """code/codice:4,name,country"""
                  
            
    def orderBase(self):
        return ''
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='name',op='contains', val='%', runOnStart=True)

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        tc=parentBC.tabContainer(margin='5px', **kwargs)
        self.page1(tc.contentPane(title='!!Profile'),disabled=disabled)
        self.page2(tc.borderContainer(title='!!Invoices'),disabled=disabled)
        
    def page1(self,pane,disabled=False):
        fb=pane.formbuilder(cols=2, border_spacing='6px',disabled=disabled)
        #fb.field('code',readOnly='^aux_code.readOnly')
        fb.field('code',readOnly=not self.isDeveloper())
        fb.field('name',autoFocus=True)
        fb.field('country', rowcaption='$name')
        fb.field('address')
        fb.field('zip')
        fb.field('city')
        
    def page2(self,bc,disabled=False):
        self.includedViewBox(bc,label='!!Invoices',
                            storepath='.@invc_invoice_customer_id',
                            columns="""number,date,net,vat,total""",
                            table='invc.invoice', autoWidth=True)
        
    def pagetest(self,pane,disabled=False):
        fb=pane.formbuilder(cols=1,border_spacing='4px')
        fb.button('Che Ore Sono?',fire='abu.ora')
        fb.dataRpc('abu.oraRitornata','dammilora', nome='=form.record.name', _fired='^abu.ora')
        fb.div('^abu.oraRitornata')
        
    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            country = self.site.config('defaults?country')
            record['country'] = country
############################## RPC_METHODS ###################################       
    def rpc_dammilora(self,nome=None,**kwargs):
        return "caro %s sono le %s" %(nome,str(datetime.now()))
