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
    maintable='assopy.socio'
    py_requires='basecomponent:Public,standard_tables:TableHandler'

    def windowTitle(self):
        return '!!Assopy Valutazioni espresse dai Soci'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def barTitle(self):
        return '!!Valutazioni espresse dai Soci'
        
    def columnsBase(self):
        return """@anagrafica_id.ragione_sociale/Socio:14,@anagrafica_id[localita:20,provincia/Pr.:2],
                                  @anagrafica_id.@utente_id[username/Username:12,email:12]"""
        

    def formBase(self,pane,disabled=False,datapath=''):
        lc=pane.layoutContainer(height='100%',datapath=datapath)
        lc.contentPane(layoutAlign='top',height='1.5em').div('^.nome_cognome',width='100%',text_align='center',font_size='1.3em',border_bottom='1px solid silver')
        tab = lc.tabContainer(layoutAlign='client')
        p2 = tab.contentPane(title='Valutazioni',connect_onLoad='genro.wdgById("votiGrid").render()')
        self.visualizzaVoti(p2)

    def TEST_visualizzaVoti(self,pane, struct, **kwargs):
        self.visualizzaVoti(pane, struct=self._structVotiGrid(), sorted='#a.voto:d',
                           storepath='.@anagrafica_id.@utente_id.@assopy_valutazione_utente_id', 
                           gridpath='form.votiGrid', selectedIndex='form.votiGrid.selectedIndex',**kwargs)
        
    def visualizzaVoti(self,pane):
        """docstring for visualizzaVoti"""
        #pane.div(value='^.@anagrafica_id.@utente_id.@assopy_valutazione_utente_id.#0.id')
        pane.data('form.votiGrid.struct', self._structVotiGrid())
        pane.data('form.votiGrid.sorted', '#a.voto:d')
        pane.VirtualStaticGrid(nodeId='votiGrid', selectedIndex='form.votiGrid.selectedIndex', sortedBy='^form.votiGrid.sorted',
                        storepath='.@anagrafica_id.@utente_id.@assopy_valutazione_utente_id', structpath='form.votiGrid.struct',
                        elasticView=0, autoWidth=True, autoHeight=False,updateContent='^recordLoaded')
        

    def _structVotiGrid(self):
        struct = self.newGridStruct('assopy.valutazione')
        r = struct.view().rows(classes='df_grid', cellClasses='df_cells', headerClasses='df_headers')
        r.fieldcell('@talk_id.@oratore_id.@anagrafica_id.@utente_id.nome_cognome',name='Speaker',width='12em')
        r.fieldcell('@talk_id.titolo',name='Titolo',width='18em')
        
        r.fieldcell('voto',width='4em')
        r.fieldcell('note',width='30em')
        return struct

    def sqlContextRecord(self):
        result = Bag()
        result['relatedcolumns.assopy.valutazione.utente_id'] = self._structVotiGrid().getFieldNames()
        return result
            
    def orderBase(self):
        return '@anagrafica_id.ragione_sociale'
    
    def queryBase(self):
        return dict(column='@valutazione.voto',op='not null', val='',runOnStart=True)


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
