#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.valutazione'
    py_requires='basecomponent:Public,basecomponent:Tables'
    def windowTitle(self):
        return '!!Assopy Valutazioni'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'

    def barTitle(self):
        return '!!Gestione Valutazioni'
        
    def lstBase(self):
        struct = self.newGridStruct()
        r=struct.view().rows(classes='lst_grid',cellClasses='lst_grid_cells',headerClasses='lst_grid_headers')
        r.fields("""@socio_id.nome_cognome/Socio:12,@talk_id.codice/Talk:9,voto:3""")
        return struct   
    

 

    def formBase(self,pane,datapath=''):

        fb = pane.formbuilder(cols=1)
        fb.field('assopy.valutazione.socio_id')
        fb.field('talk_id')
        fb.field('voto')

        
    def orderBase(self):
        return 'nome'
        
    
    def queryBase(self):
        return dict(column='nome',op='contains', val=None)
    


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
