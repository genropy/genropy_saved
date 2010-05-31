#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrbag import Bag
from random import randint
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='warh.personaggio'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ################ 
    def windowTitle(self):
        return '!!Scheda Personaggio'
        
    def barTitle(self):
        return '!!Scheda Personaggio'
        
    def columnsBase(self):
        return """sigla:4,nome:20,razza_codice/RC:3,@razza_codice.nome/Razza:10"""
    
    def printActionBase(self):
        return True

    def exportActionBase(self):
        return True
  
    def orderBase(self):
        return 'nome'
    
    def queryBase(self):
        return dict(column='nome',op='contains', val='')

    def userCanWrite(self):
        return True
    
    def userCanDelete(self):
        return True
        
############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2, border_spacing='4px',disabled=disabled,width='500px',background='^.@razza_codice.colore')
        fb.field('sigla',width='2em')
        fb.field('nome',width='100%')
        fb.field('razza_codice',width='100%')
        fb.button('Genera valori',fire='call_generavalori')
        #RPC CALLER
        fb.dataRpc('valori',"generaValori",_fired="^call_generavalori",razza='=.razza_codice')
        fb.dataFormula(".ac", "x",x="^valori.ac")
        fb.dataFormula(".ab", "x",x="^valori.ab")
        fb.dataFormula(".forza", "valore",valore="^valori.f")
        fb.dataFormula(".resistenza", "valore",valore="^valori.r")
        
        #fine rpc_caller
        fb.br()
        fb.field('ac',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.ac',minimum='^.@razza_codice.ac_base',maximum=100,width='100%',
                            discreteValues='==101-minimum',intermediateChanges=True)
                                                
        fb.field('ab',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.ab',minimum='^.@razza_codice.ab_base',maximum=100,width='100%',
                            discreteValues='==101-minimum', intermediateChanges=True)
                            
        fb.field('forza',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.forza',minimum='^.@razza_codice.f_base',maximum=100,width='100%',
                            discreteValues='==101-minimum', intermediateChanges=True)
        
        fb.field('resistenza',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.resistenza',minimum='^.@razza_codice.r_base',maximum=100,width='100%',
                            discreteValues='==101-minimum', intermediateChanges=True)
        
        fb.field('fato',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.fato',minimum='^.@razza_codice.pf_base',maximum=100,width='100%',
                            discreteValues='==101-minimum', intermediateChanges=True)
                            
    def rpc_generaValori(self,razza=None):
        tblrazza = self.db.table('warh.razza')
        record = tblrazza.record(pkey=razza).output('dict')
        risultato = Bag()
        for x in ('ac','ab','f','r'):
            risultato[x] = record['%s_base' % x]+randint(1,10)+randint(1,10)+randint(1,10)
        return risultato