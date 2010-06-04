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
    
#    def columnsBase(self):
#        return """sigla:4,nome:20,razza_codice/RC:3,@razza_codice.nome/Razza:10"""
    
    def lstBase(self,struct):
        """!!Vista base"""
        r = struct.view().rows()
        r.fieldcell('sigla',width='4em')
        r.fieldcell('nome',width='20em')
        r.fieldcell('razza_codice',width='6em')
        r.fieldcell('@razza_codice.nome',width='10em')
        return struct
    
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

    def formBase(self, parentBC, disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2, border_spacing='4px', disabled=disabled, width='500px', background='^.@razza_codice.colore')
        fb.field('sigla', width='2em')
        fb.field('nome', width='100%')
        fb.field('razza_codice', width='100%')
        fb.button('Genera valori', fire='call_generavalori')
        #rpc_caller
        fb.dataRpc('valori',"generaValori",_fired="^call_generavalori",razza='=.razza_codice')
        fb.dataFormula(".ac", "x", x="^valori.ac")
        fb.dataFormula(".ab", "x", x="^valori.ab")
        fb.dataFormula(".forza", "x", x="^valori.f")
        fb.dataFormula(".resistenza", "x", x="^valori.r")
        fb.dataFormula(".agilita", "x", x="^valori.ag")
#        fb.dataFormula(".intelligenza", "x", x="^valori.int")
#        fb.dataFormula(".volonta", "x", x="^valori.vol")
#        fb.dataFormula(".simpatia", "x", x="^valori.simp")
#        fb.dataFormula(".attacchi", "x", x="^valori.att")
#        fb.dataFormula(".ferite", "x", x="^valori.fer")
#        fb.dataFormula(".bonus_forza", "x", x="^valori.b_forza")
#        fb.dataFormula(".bonus_res", "x", x="^valori.b_res")
#        fb.dataFormula(".mov", "x", x="^valori.mov")
#        fb.dataFormula(".magia", "x", x="^valori.magia")
#        fb.dataFormula(".follia", "x", x="^valori.fol")
#        fb.dataFormula(".fato", "x", x="^valori.pf_base")
        
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

        fb.field('agilita',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.agilita',minimum='^.@razza_codice.agilita',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('intelligenza',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.intelligenza',minimum='^.@razza_codice.intelligenza',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('volonta',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.volonta',minimum='^.@razza_codice.volonta',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('simpatia',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.simpatia',minimum='^.@razza_codice.simpatia',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('attacchi',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.attacchi',minimum='^.@razza_codice.attacchi',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('ferite',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.ferite',minimum='^.@razza_codice.ferite',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('bonus_forza',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.bonus_forza',minimum='^.@razza_codice.bonus_forza',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('bonus_res',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.bonus_res',minimum='^.@razza_codice.bonus_res',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('mov',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.mov',minimum='^.@razza_codice.mov',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)
    
        fb.field('magia',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.magia',minimum='^.@razza_codice.magia',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('follia',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.follia',minimum='^.@razza_codice.follia',maximum=100,width='100%',
        discreteValues='==101-minimum',intermediateChanges=True)

        fb.field('fato',width='2em',readOnly=True)
        fb.horizontalSlider(value='^.fato',minimum='^.@razza_codice.pf_base',maximum=100,width='100%',
                            discreteValues='==101-minimum', intermediateChanges=True)
                            
    def rpc_generaValori(self,razza=None):
        tblrazza = self.db.table('warh.razza')
        record = tblrazza.record(pkey=razza).output('dict')
        risultato = Bag()
        for x in ('ac','ab','f','r','ag'): # 'int','vol','simp','att','fer','b_forza','b_res','mov','magia','fol','pf_base'):
            risultato[x] = record['%s_base' % x]+randint(1,10)+randint(1,10)
        return risultato
