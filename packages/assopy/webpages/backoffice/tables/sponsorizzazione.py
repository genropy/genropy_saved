#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.sponsorizzazione'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    def windowTitle(self):
        return '!!Assopy Sponsorizzazioni'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
    
    def tableWriteTags(self):
        return 'admin'
    
    def tableDeleteTags(self):
        return 'superadmin'
    
    def barTitle(self):
        return '!!Gestione Sponsorizzazioni'
        
    def columnsBase(self):
        return """sponsor:15,descrizione:30,settore:10,www/Sito:20,ordine_riga_id:20"""


    def formBase(self,pane,datapath='',disabled=False):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.sponsorizzazione.sponsor')
        fb.field('assopy.sponsorizzazione.descrizione',width='20em')
        fb.field('assopy.sponsorizzazione.www')
        fb.field('assopy.sponsorizzazione.attivita')
        fb.field('assopy.sponsorizzazione.settore')
        fb.field('assopy.sponsorizzazione.logo')
        fb.field('assopy.sponsorizzazione.evento_id')
        fb.field('assopy.sponsorizzazione.ordine_riga_id')
        fb.field('assopy.sponsorizzazione.anagrafica_id')


        
    def orderBase(self):
        return 'sponsor'
    
    def queryBase(self):
        return dict(column='sponsor',op='contains', val=None)
    


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
