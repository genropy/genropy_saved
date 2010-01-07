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

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        
        sp=root.splitContainer(height='99%',border='1px solid gray',margin='5px')
        left=sp.contentPane(sizeShare=20)
        left.tree(storepath='*D',inspect=True,label='datastore',selected='tree.selected.item',
                                                                 selected_one='tree.selected.one',
                                                                 selected_many='tree.selected.many')
        tc=sp.tabContainer(sizeShare=80,datapath='tabs',margin='5px')
        self.pane1(tc,title='Tab1',datapath='.tab1')
        #self.formulePane(tc,title='Formule',datapath='.formule')
        self.recordsPane(tc,title='Records',datapath='.records')
        
        #self.browserPane(tc,title='Selections',datapath='.browse')
        

    def pane1(self,where,**kwargs):
        pane=where.contentPane(**kwargs)
        pane.data('',dict(name='John',city='New York',age=21))
        fb=pane.formbuilder(cols='2')
        fb.textbox(lbl='Name',value='^.name')
        fb.textbox(lbl='Name2',value='^.name')
        fb.input(lbl='Name in input',value='^.name')
        fb.div(value='^.name',lbl='Name in div')
        fb.span('^.name',lbl='Name in span',mask='My name is %s')
        fb.textbox(lbl='City',value='^.city')
        fb.textbox(lbl='City2',value='^.city')
        fb.numbertextbox(lbl='Age',value='^.age')
        fb.numbertextbox(lbl='Age2',value='^.age')
        fb.checkbox(lbl='Partner',cecked='^.partner')
        fb.checkbox(lbl='Partner2',cecked='^.partner')
    
    def recordsPane(self,where,**kwargs):
        pane=where.contentPane(**kwargs)
        pane.dataRecord('.provincia.data','utils.province',pkey='^.provincia.key')
        
        fb=pane.formbuilder(cols='1',cellspacing='5')
        block=fb.formbuilder(lbl='Province',datapath='.provincia',cols=2)
        block.dataRecord('.data','utils.province',pkey='^.key')
        block.dbSelect( value = '^.key', dbtable='utils.province',columns='descrizione')
        block.div('^.data.regione')
        
        block=fb.formbuilder(lbl='Client', datapath='.client',cols=2)
        block.dataRecord('.data',  'utils.anagrafiche', pkey='^.key')
        block.dbSelect(value='^.key', 
                                dbtable='utils.anagrafiche', columns='an_ragione_sociale',
                                auxColumns='$an_localita,$an_provincia,@an_provincia.@regione.descrizione as regione',                                
                                )

        block = fb.formbuilder(cols=1, dbtable='utils.anagrafiche', datapath='.client.data')
        #block.placeFields('utils.anagrafiche.an_ragione_sociale,an_indirizzo,an_cap,an_provincia,an_localita,sy_modificato_il')
       #block.field('utils.anagrafiche.an_ragione_sociale')
       #block.field('an_indirizzo')
       #block.field('an_cap')
       #block.field('an_provincia')
        
    def browserPane(self,where,**kwargs):
        pane = where.contentPane(**kwargs)
        pane.dataSelection('.anag.sel','utils.anagrafiche',
                columns='an_ragione_sociale,an_indirizzo,an_cap,an_localita,an_provincia,ds_codice_fiscale,ds_partita_iva',
                where='an_provincia = :prv', prv='^.prv.key', structure=True)
        pane.dataSelection('.fatt.sel.data','fatt.fatture',
                columns='protocollo,data,imponibile,iva,totale',
                where='@sy_idcliente.@sy_id_anagrafiche.sy_id = :idanag', idanag='^.anag.selected.record.sy_id')
                
        pane=pane.layoutContainer(height='100%')
        top=pane.contentPane(layoutAlign='top',height='3em')
        split=pane.splitContainer(layoutAlign='client',orientation='vertical')
        s1=split.contentPane(sizeShare=50)
        top.dbSelect(margin='5px',lbl='Provincia',value = '^.prv.key',
                               dbtable='utils.province',columns='descrizione')
        
        s1.grid(margin='5px',model='^.anag.sel.data',structure='^.anag.sel.structure',
                                  clientSort=True, selected_idx='.anag.selected.idx', selected_record='.anag.selected.record')
        sps = split.splitContainer(sizeShare=50)
        fb = sps.contentPane(sizeShare=30,background_color='pink').formbuilder(cols=1,datapath='.anag.selected.record')
        
        fb.div('^.an_ragione_sociale')
        fb.div('^.an_indirizzo')
        fb.div('^.an_localita')
        fatture=sps.contentPane(sizeShare=70)
        fatture.grid(margin='5px',width='100&',model='^.fatt.sel.data',structure='^.fatt.sel.structure',
                        clientSort=True,selected_idx='.anag.selected.idx',selected_record='.fatt.selected.record')
        fatstruct=Bag()
        r=fatstruct.child('view').child('rows')
        r.child('cell',field='protocollo',width='9em',name='Protocollo' )
        r.child('cell',field='data',width='10em',name='Data', format_date='long')
        r.child('cell',field='imponibile',width='8em',name='Imponibile',text_align='right')
        r.child('cell',field='iva',width='8em',name='Iva',text_align='right',color='red')
        r.child('cell',field='totale',width='8em',name='Totale',format_currency='EUR',
                                         background_color='yellow',text_align='right')
        fatture.data('.fatt.sel.structure',fatstruct)
    
    def formulePane(self,where,**kwargs):
        pane=where.contentPane(**kwargs)
        fbext=pane.formbuilder(cols=1,datapath='.geometria',margin='2em')
        fb=fbext.div(lbl='Triangolo',lbl_font_size='medium',border='1px solid green').formbuilder(cols=6,datapath='.triangolo',lblpos='T')
        fb.dataFormula('.area','base*altezza/2',base='^.base',altezza='^.altezza' )
        fb.dataFormula('.tipo','"basso e largo"',base='^.base',altezza='^.altezza' , _if='base>altezza', _else='"alto e stretto"')
        fb.dataRpc('.areaserver','areatriangolo',base='^.base',altezza='^.altezza', _if='base && altezza', _else='return "inutile chiedere"')
        fb.dataScript('.areacommento','if (base && altezza) {return base*altezza/2}else{return "Not available"}',base='^.base',altezza='^.altezza')
        fb.NumberTextBox(lbl='Base',value='^.base',width='5em')
        fb.NumberTextBox(lbl='Altezza',value='^.altezza',width='5em')
        fb.NumberTextBox(lbl='Area',value='^.area',disabled=True,width='5em')
        fb.textBox(lbl='Area da server',value='^.areaserver',disabled=True,width='10em')
        fb.TextBox(lbl='Area da script',value='^.areacommento',disabled=True,width='10em')
        fb.TextBox(lbl='Tipologia',value='^.tipo',disabled=True,width='12em')
        fb=fbext.div(lbl='Rettangolo',lbl_font_size='medium',border='1px solid green').formbuilder(cols=3,datapath='.rettangolo',lblpos='T')
        fb.dataFormula('.area','base*altezza',base='^.base',altezza='^.altezza')
        fb.NumberTextBox(lbl='Base',value='^.base',width='5em')
        fb.NumberTextBox(lbl='Altezza',value='^.altezza',width='5em')
        fb.NumberTextBox(lbl='Area',value='^.area',disabled=True,width='5em')
        
        fb=fbext.div(lbl='Confronto',lbl_font_size='medium',border='1px solid red').formbuilder(cols=3,lblpos='T')
        fb.dataScript('.risultato',u'if(rettangolo>triangolo){return "Il rettangolo è maggore del triangolo"}else{ return "Il triangolo è maggore del rettangolo"}'
                                   ,rettangolo='^.rettangolo.area', triangolo='^.triangolo.area')
        fb.TextBox(lbl='Risultato',value='^.risultato',disabled=True,width='24em')

    def rpc_areatriangolo(self,base=0,altezza=0):
        return int(base)*int(altezza)/2.0
