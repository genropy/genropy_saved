#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Anagrafica """
import time
import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.anagrafica'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    def windowTitle(self):
        return '!!Assopy Gruppi partecipanti'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'superadmin'
        
    def barTitle(self):
        return '!!Gruppi partecipanti'
        
    def columnsBase(self,):
        return """titolo:4,ragione_sociale:14,@utente_id.username:14,indirizzo:10,
                    localita:10,provincia/Pr.:2,nazione/Naz:3,codice_fiscale/C.Fiscale:11,partita_iva/P.Iva:7"""
               
    def formBase(self,pane,datapath='',disabled=False):
        pass
        
    def orderBase(self):
        return 'ragione_sociale'
    
    def conditionBase(self):
        return ("@assopy_ordine_anagrafica_id.fattura_num IS NOT NULL",{})
        
    def queryBase(self):
        return dict(column='ragione_sociale',op='contains', val='')
                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()