#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='warh.razza'
               # sintassi: maintable='nomeCartella_Packages.nomeFile_Model'
    py_requires='public:Public,standard_tables:TableHandlerLight,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ##################
    def windowTitle(self):
        return '!!Razze'
        
    def barTitle(self):
        return '!!Razze'
        
#    def columnsBase(self): # definisce la dimensione della colonna... però è una sintassi sbrigativa
#        return """codice:4,nome:15,descrizione:10,ac_base:4,ab_base:4,f_base/For.Base:4,r_base/					Res.Base:4,agilita:4,intelligenza:4,volonta:4,simpatia:4,attacchi:4,ferite:4,bonus_forza/bonusForza:4,bonus_res/bonus/Res:4,mov:4,magia:4,follia:4,pf_base/PF.Base:4"""

    def lstBase(self,struct): # ci sono alternative alla lstBase?
        """!!Vista base"""
        r = struct.view().rows()
        r.cell('codice', dtype='T', name='!!Codice', width='4em')
               # specifico una riga
        r.fieldcell('nome', width='12em')
               # specifico una riga ma senza dover richiamare il name (cioè la parte visualizzata dell'attributo)
               # ATTENZIONE: per usarlo devo avere creato la cell nella table di riferimento; in questo caso in
               # "razza.py" ci deve essere una column di nome 'nome')
        r.fieldcell('ac_base',width='8em')
        r.fieldcell('ab_base',width='5em')
        r.fieldcell('f_base',width='4em')
        r.fieldcell('r_base',width='6em')
        r.fieldcell('ag_base',width='4em')
        r.fieldcell('int_base',width='6em')
        r.fieldcell('vol_base',width='5em')
        r.fieldcell('simp_base',width='5em')
        r.fieldcell('att_base',width='5em')
        r.fieldcell('mov_base',width='6em')
        r.fieldcell('magia_base',width='4em')
        r.fieldcell('fol_base',width='6em')
        return struct

    def tableWriteTags(self):
        return None
    
    def printActionBase(self):
        return True

    def exportActionBase(self):
        return True
  
    def orderBase(self):
        return 'nome'

    def formBaseDimension(self): 
        return dict(height='350px',width='600px') # specifica la dimensione del dialog (=casella di inserimento dati)

############################## FORM METHODS #################################

    def formBase(self, parentBC, disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
#       pane = parentBC.div('ciao')
        pane = bc.contentPane(region='left',width='60%')
        tc = bc.tabContainer(region='center')
               # la tabContainer genera una struttura con Tab uguale a quella delle tab di internet...
        self.form_razza(pane)
        self.griglia_ferite(tc.borderContainer(title='!!Ferite'))
        self.griglia_fato(tc.borderContainer(title='!!Punti Fato'))
        
    def form_razza(self,pane):
        fb = pane.formbuilder(cols=2, border_spacing='4px',disabled=False,width='300px')
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
        fb.field('mov_base',width='100%')
        fb.field('magia_base',width='100%')
        fb.field('fol_base',width='100%')
                                  
    def griglia_ferite(self,bc):
               # Attenzione! L'includedViewBox e i suoi derivati (es. selectionHandler) accettano solo BorderContainer
               # e non accettano i contentPane; nei contentPane NON posso mettere altri contenitori,
               # posso mettere solo oggetti
        iv = self.includedViewBox(bc,label='!!Punti Ferita',
                                  add_action=True, # tasto "+"
                                  del_action=True, # tasto "-"
                                  nodeId='FeriteGrid',
                				  editorEnabled=True,
                                  storepath='.fer_base', # dove legge e scrive i dati
                                  struct=self.ferite_struct,
               # in "struct" passo il metodo che mi dirà come sono fatte le colonne della griglia
                                  datamode='bag')

        gridEditor = iv.gridEditor()              
        gridEditor.numberTextbox(gridcell='da')
        gridEditor.numberTextbox(gridcell='a')
        gridEditor.numberTextbox(gridcell='valore')
        
    def ferite_struct(self, struct):
        r = struct.view().rows()
        r.cell('da',name='Tiro da',dtype='L',width='3em')
               # se non dichiarato si ha una cella standard di tipo testo (dtype='T')
        r.cell('a',name='Tiro a',dtype='L',width='3em')
        r.cell('valore',name='Valore',dtype='L',width='7em')

    def griglia_fato(self,bc):
        iv = self.includedViewBox(bc,label='!!Punti Fato',
                                  add_action=True,
                                  del_action=True,
                                  nodeId='FatoGrid',
                                  editorEnabled=True,
                                  storepath='.pf_base',
                                  struct=self.fato_struct,
                                  datamode='bag'
                                  )        

        gridEditor = iv.gridEditor()              
        gridEditor.numberTextbox(gridcell='da')
        gridEditor.numberTextbox(gridcell='a')
        gridEditor.numberTextbox(gridcell='valore')

    def fato_struct(self, struct):
        r = struct.view().rows()
        r.cell('da',name='Tiro da',dtype='L',width='3em')
        r.cell('a',name='Tiro a',dtype='L',width='3em')
        r.cell('valore',name='Valore',dtype='L',width='7em')

