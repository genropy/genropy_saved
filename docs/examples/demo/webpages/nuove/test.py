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

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        root.data('',self.mydata())
        root.dataRemote('remote.test','getProvincia',prov='^mydata.prov')
        #root.numberSpinner(lbl='page',value='^selectedpage')
        split = root.splitContainer(height='100%')
        
        tree = split.contentPane(sizeShare='30',background_color='smoke').tree(storepath='*D',
                                                selected='xyz.selectedLabel',
                                                selected_treecaption='xyz.celectedCaption',
                                                inspect='shift',label="Data")
        tc = split.tabContainer(sizeShare='70',height='100%',margin='5px',datapath='test',selected='^selectedpage')
        self.testDbSelect(tc)
        self.testFormula(tc)      
        self.testPane(tc)
        
    def testDbSelect(self,where):
        fb=where.contentPane(title='^dbrecords.cliente.an_ragione_sociale',default_title='Client pane').formbuilder(cols=2,cellspacing='10',datapath='buttons')
        fb.textbox(lbl='Name',value='^.name')
        fb.textbox(lbl='Label button',default='A nice button',value='^.btnLabel')
        fb.textbox(lbl='Pane name',value='^pane.name')
        
        fb.button(label="@:btnLabel", action="alert('No way...')",gnrId='mybtn')
        fb.dbSelect(lbl='Province', datasource = 'mydata.prov',ignoreCase=True,
                               dbtable='utils.province',columns='descrizione',
                               searchDelay=200,
                               method='dbSelect',
                               recordpath='dbrecords.provincia'
                               )
        
        fb.dbSelect(lbl='Client', value='^mydata.cliente', ignoreCase=True,
                                dbtable='utils.anagrafiche', columns='an_ragione_sociale',
                                searchDelay=200,
                                method='dbSelect',
                                tooltip='Select a client for this operation',
                                auxColumns='$an_localita,$an_provincia,@an_provincia.@regione.descrizione as regione',
                                recordpath='dbrecords.cliente'
                                
                                )
        
        fb.dbSelect(lbl='City', datasource = 'mydata.localita',ignoreCase=True,
                                dbtable='utils.localita',columns='localita',
                                searchDelay=200,
                                method='dbSelect',
                                recordpath='dbrecords.localita'
                                )
        fb.toggleButton('Toggle',iconClass="dijitRadioIcon",value='^.toggle1')
        fb.Button('Publish',action="genro.publish('mytopic',23,56)")
        
        fb.checkBoxGroup("Rugby,Soccer,Baseball,Tennis",cols=1,border='1px solid silver',padding='5px',value='^.cb')
        fb.radioGroup('Jazz,Rock,Punk,Metal','genre',cols=4,border='1px solid red',padding='5px',
                               subscribe_mytopic='alert($1+$2)',value='^.rb')
        
        
    def testFormula(self,where):
         fb=where.contentPane(title='Formule').formbuilder(cols=5,cellspacing='10',datapath='triangolo')
         fb.dataFormula(':areaclient','base*altezza/2',base='^.base',altezza='^.altezza')
         fb.dataScript(':areaclient2','if (base && altezza) {return base*altezza/2}else{return "Not available"}',base='^.base',altezza='^.altezza')
         fb.dataRpc(':areaserver','areatriangolo',base='^.base',altezza='^.altezza')
         fb.dataFormula(':areaspeciale','as*ac', ac='^.areaclient', as='^.areaserver')
         fb.NumberTextBox(lbl='Base',value='^.base')
         fb.NumberTextBox(lbl='Altezza',value='^.altezza')
         fb.div(lbl='Area client = ',value='^.areaclient',pos='+')
         fb.div(lbl='Area client2 = ',value='^.areaclient2')
         fb.div(lbl='Area server = ',value='^.areaserver')
         fb.div(lbl='Area speciale = ',value='^.areaspeciale')
            
    def testPane(self,where):
        where=where.contentPane(title='Test Tree')
        where.dbSelect(lbl='Province', datasource = 'test.prov',ignoreCase=True,
                            dbtable='utils.province',columns='descrizione',
                            searchDelay=200,
                            method='dbSelect')
        where.tree(storepath='test.record',inspect='shift',
                    selected='^test.selected.label',
                    selected_name_long='^test.selected.name_long'
                    )
        where.dataRpc('test.record','getProvincia',prov='^test.prov')
        
                                
    def rpc_getProvincia(self,prov=None):
        try:
            return self.db.table('utils.province').record(prov).output('bag')
        except:
            return Bag()
            
    def mydata(self):
        b=Bag()
        b['xyz.selected']=None
        b['xxx.btnLabel']='I am a button'
        b['xxx.name']='John'
        b['pane.name']='A tab pane'
        b['selectedpage']=2
        b['test.buttons.btnLabel']='You can change this label...'
        return b
    
    def rpc_areatriangolo(self,base=0,altezza=0):
        return int(base)*int(altezza)/2.0
    
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()





