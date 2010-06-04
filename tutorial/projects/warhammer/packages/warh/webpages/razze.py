#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='warh.razza' # sintassi: maintable='nomeCartella_Packages.nomeFile_Model'
    py_requires='public:Public,standard_tables:TableHandlerLight,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ##################
    def windowTitle(self):
        return '!!Razze'
        
    def barTitle(self):
        return '!!Razze'
        
#    def columnsBase(self): # definisce la dimensione della colonna... però è una sintassi sbrigativa
#        return """codice:4,nome:15,descrizione:10,ac_base:4,ab_base:4,f_base/For.Base:4,r_base/#Res.Base:4,agilita:4,intelligenza:4,volonta:4,simpatia:4,attacchi:4,ferite:4,bonus_forza/bonusForza:4,bonus_res/bonus/#Res:4,mov:4,magia:4,follia:4,pf_base/PF.Base:4"""

    def lstBase(self,struct):
        """!!Vista base"""
        r = struct.view().rows()
        r.cell('codice', dtype='T', name='!!Codice', width='4em') # specifico una riga
        r.fieldcell('nome', width='12em') # specifico una riga ma senza dover richiamare il name (cioè la parte visualizzata dell'attributo)
        r.fieldcell('descrizione', width='6em')
        r.fieldcell('ac_base',width='3em')
        r.fieldcell('ab_base',width='3em')
        r.fieldcell('f_base',width='3em')
        r.fieldcell('r_base',width='5em')
        r.fieldcell('ag_base',width='4em')
        r.fieldcell('int_base',width='5em')
        r.fieldcell('vol_base',width='4em')
        r.fieldcell('simp_base',width='4em')
        r.fieldcell('att_base',width='4em')
        r.fieldcell('fer_base',width='4em')
        r.fieldcell('b_forza_base',width='4em')
        r.fieldcell('b_res_base',width='5em')
        r.fieldcell('mov_base',width='5em')
        r.fieldcell('magia_base',width='4em')
        r.fieldcell('fol_base',width='4em')
        r.fieldcell('pf_base',width='5em')
        return struct
    
    def printActionBase(self):
        return True

    def exportActionBase(self):
        return True
  
    def orderBase(self):
        return 'nome'

    def formBaseDimension(self): 
        return dict(height='350px',width='400px') # specifica la dimensione del dialog (=casella di inserimento dati)

############################## FORM METHODS #################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2, border_spacing='4px',disabled=disabled,width='290px')
        fb.field('codice',width='100%')
        fb.field('nome',width='100%')
        fb.field('descrizione',width='100%')
        fb.div(width='20px',height='20px',lbl='!!Colore',background='^.colore').menu(modifiers='*',_class='colorPaletteMenu').menuItem().colorPalette(value='^.colore')
        fb.field('ac_base',width='100%')
        fb.field('ab_base',width='100%')
        fb.field('f_base',width='100%')
        fb.field('r_base',width='100%')
        fb.field('ag_base',width='100%')
        fb.field('int_base',width='100%')
        fb.field('vol_base',width='100%')
        fb.field('simp_base',width='100%')
        fb.field('att_base',width='100%')
        fb.field('fer_base',width='100%')
        fb.field('b_forza_base',width='100%')
        fb.field('b_res_base',width='100%')
        fb.field('mov_base',width='100%')
        fb.field('magia_base',width='100%')
        fb.field('fol_base',width='100%')
        fb.field('pf_base',width='100%')
