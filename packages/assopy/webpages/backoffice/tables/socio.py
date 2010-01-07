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
    maintable='assopy.socio'
    py_requires='basecomponent:Public,standard_tables:TableHandler'

    def windowTitle(self):
        return '!!Assopy Soci'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def barTitle(self):
        return '!!Gestione Socio'
        
    def columnsBase(self):
        return """nome_cognome:12,@anagrafica_id[codice_fiscale/C.F.:12,localita:11,provincia/Pr.:2,cellulare:7],
                                  @anagrafica_id.@utente_id[username/Username:12,email:10]"""
        

    def formBase(self,pane,disabled=False,datapath=''):
        lc=pane.layoutContainer(height='100%',datapath=datapath)
        lc.contentPane(layoutAlign='top',height='1.5em').div('^.nome_cognome',width='100%',text_align='center',font_size='1.3em',border_bottom='1px solid silver')
        tab = lc.tabContainer(layoutAlign='client')
        
        p1 = tab.contentPane(title='Dati Anagrafici')
        fb = p1.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.socio.nome_cognome', lbl='Nome')
        fb.field('assopy.socio.anagrafica_id', lbl='Anagrafica', width='25em')
        fb.field('assopy.socio.data_inizio')
        fb.field('assopy.socio.data_fine')
        fb.field('assopy.socio.attivita')
        fb.field('assopy.socio.settore')
        fb.textarea(lbl_vertical_align='top', lbl='Descrizione',width='30em'
                    ,colspan=2,_class='form_textarea',value='^.descrizione')       
        fb.field('assopy.socio.www')
        
        p2 = tab.contentPane(title='Valutazioni',connect_onLoad='genro.wdgById("votiGrid").render()')

                    
    def orderBase(self):
        return 'nome_cognome'
    
    def queryBase(self):
        return dict(column='nome_cognome',op='contains', val=None)


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
