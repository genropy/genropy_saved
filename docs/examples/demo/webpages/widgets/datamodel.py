#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os

import datetime,time
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        split = root.splitContainer(height='100%')
        sp1=split.splitContainer(sizeShare='30',orientation='vertical')
        tree = sp1.contentPane(sizeShare='50',background_color='smoke').tree(storepath='*D',
                                                selected='datatree.selectedLabel',
                                                selected_treecaption='datatree.selectedCaption',
                                                inspect='shift',label="Data")
        
        tree = sp1.contentPane(sizeShare='50',background_color='smoke').tree(storepath='*S',
                                                  selectedLabel='srctree.selectedLabel',
                                                  selectedItem='srctree.selectedItem',
                                                  selectedPath='srctree.selectedPath',
                                                  connect_onClick='genro.src.highlightNode($1)',
                                                  inspect='shift',label="Structure")
                                                  
        tc = split.tabContainer(sizeShare='70',height='100%',margin='5px',value='test',selected='^selectedpage')
        
        self.testFormula(tc,title='Formule',datapath='formule')  
        
        self.testRecord(tc,title='Record',datapath='record')
            
        #self.testSelection(tc)
        
    def testSelection(self,where):
        # --------- model --------
        sp=where.contentPane(title='Test selection').splitContainer(orientation='vertical',height='100%')
        fb=sp.contentPane(sizeShare=30).formbuilder(cols="2",cellspacing='10',datapath='selection')
        
        fb.dataSelection('selection.grid',table='^.table',columns='^.columns',
                                     where="^.where",order_by="^.order_by",structure=True,
                                     distinct="^.distict",group_by="^.group_by",having="^.having",
                                     _if='!stopped',stopped="^.stopped")
                        
        # --------- gui --------
        
        fb.textBox(lbl='Table',width='14em',value='^.table')
        fb.textBox(lbl='Columns',width='20em',value='^.columns')
        fb.textBox(lbl='Where',width='20em',value='^.where')
        fb.textBox(lbl='Order by',width='20em',value='^.order_by')
        fb.textBox(lbl='Group by',width='20em',value='^.group_by')
        fb.checkBox(label='Distinct',value='^.distinct')
        fb.textBox(lbl='Having',width='20em',value='^.having')
        fb.toggleButton(label='Stopped',iconClass="dijitRadioIcon",value='^.stopped',value=True)
        mygrid=sp.contentPane(sizeShare=70).grid(gnrId='mygrid',model='^selection.grid.data',structure="^selection.grid.structure", autoWidth='^grid.autowidth')
        
        
    def testRecord(self,where,**kwargs):
        fb=where.contentPane(**kwargs).formbuilder(cols=2,border_spacing='5px',datapath='.province')
        fb.dataRecord('.record','utils.province',pkey='^.code')
        fb.dbSelect(lbl='Province', value ='^.code',dbtable='utils.province',columns='descrizione')
        fb.div(template='provincia:^.descrizione <br/> <b>(^.@regione.zona)</b> size = ^.codice?size',datasource='^.record')
       #provdata=fb.formbuilder(cols=3,datapath='.record')
       #provdata.div('^.descrizione',lbl='Descrizione:')
       #provdata.div('^.@regione.zona',lbl='Zona:')
       #provdata.div('^.codice?size',lbl='Size:')
        fb.textbox(lbl='Path',value='^srctree.selectedPath',width='40em')
        fb.textbox(lbl='Value',value='^modvalue')
        
        fb.button('Assign',action="var p=genro.getData('srctree.selectedPath');var v=genro.getData('modvalue');genro.src._main.setItem(p,v)")
        fb.br()
       #fb.textbox(lbl='Panetitle',value='^panetitle')
       #
        fb.dbSelect(lbl='Client', value='^clienti.pkey', dbtable='utils.anagrafiche', columns='an_ragione_sociale,an_provincia',
                              auxColumns='$an_localita,@an_provincia.@regione.descrizione as regione')
        clientBox=fb.formbuilder(cols='2',datapath='clienti.record')
        where.dataRecord('clienti.record','utils.anagrafiche',pkey='^clienti.pkey')
        clientBox.div(lbl='Ragione Sociale',value='^.an_ragione_sociale',colspan='2')
        clientBox.div(lbl='Indirizzo',value='^.an_indirizzo',colspan='2')
        clientBox.div(lbl='Localita',value='^.an_localita',colspan='2')
       #clientBox.div(lbl='C.F',value='^.ds_codice_fiscale')
       #clientBox.div(lbl='P.IVA',value='^.ds_partita_iva')
       #clientBox.div(lbl='Tipo Cliente',value='^.@coge_clienti_sy_id_anagrafiche.rows.#0.cg_tipo_cliente')
       #clientBox.div(lbl='importo fattura',value='^.@coge_clienti_sy_id_anagrafiche.rows.#0._.@fatt_fatture_sy_idcliente.rows.#0.totale')
       #clientBox.div(lbl='fatture',value='^.@coge_clienti_sy_id_anagrafiche.rows.#0._.@fatt_fatture_sy_idcliente.rows.#0.totale')
        
    def testFormula(self,where,**kwargs):
        fb=where.contentPane(**kwargs).formbuilder(cols=1,cellspacing='10',datapath='.triangolo')
        # --------- model --------
        fb.dataFormula('.areaclient','base*altezza/2',base='^.base',altezza='^.altezza')
        fb.dataScript('.areaclient2','if (base && altezza) {return base*altezza/2}else{return "Not available"}',base='^.base',altezza='^.altezza')
        fb.dataRpc('.areaserver','areatriangolo',base='^.base',altezza='^.altezza')
        fb.dataFormula('.areaspeciale','as*ac', ac='^.areaclient', as='^.areaserver')
        # --------- gui --------
        fb.NumberTextBox(lbl='Base',value='^.base')
        fb.NumberTextBox(lbl='Altezza',value='^.altezza')
        fb.div(lbl='Area client = ',value='^.areaclient',)
        fb.div(lbl='Area client2 = ',value='^.areaclient2')
        fb.div(lbl='Area server = ',value='^.areaserver')
        fb.div(lbl='Area speciale = ',value='^.areaspeciale')
            
    def rpc_areatriangolo(self,base=0,altezza=0):
        return int(base)*int(altezza)/2.0  
                                  
    





