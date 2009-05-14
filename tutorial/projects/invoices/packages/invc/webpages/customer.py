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
        pane=parentBC.contentPane(padding='4em', **kwargs)
        fb=pane.formbuilder(cols=2, border_spacing='6px',disabled=disabled)
        fb.field('code')
        fb.field('name')
        fb.field('country', rowcaption='$name')
        fb.field('address')
        fb.field('zip')
        fb.field('city')
        fb.button('Che Ore Sono?',fire='abu.ora')
        
        fb.dataRpc('abu.oraRitornata','dammilora', nome='=form.record.name', _fired='^abu.ora')
        fb.div('^abu.oraRitornata')
############################## RPC_METHODS ###################################       
    def rpc_dammilora(self,nome=None,**kwargs):
        return "caro %s sono le %s" %(nome,str(datetime.now()))
