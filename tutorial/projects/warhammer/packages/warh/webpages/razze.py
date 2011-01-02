#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2010-05-15.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable = 'warh.razza'
    py_requires = 'public:Public,standard_tables:TableHandlerLight,public:IncludedView'

    ######################## STANDARD TABLE OVERRIDDEN METHODS ##################
    def windowTitle(self):
        return '!!Razze'

    def barTitle(self):
        return '!!Razze'

    def lstBase(self, struct):
        r = struct.view().rows()
        r.cell('codice', dtype='T', name='!!Codice', width='4em')
        r.fieldcell('nome', width='12em')
        r.fieldcell('ac_base', width='8em')
        r.fieldcell('ab_base', width='5em')
        r.fieldcell('f_base', width='4em')
        r.fieldcell('r_base', width='6em')
        r.fieldcell('ag_base', width='4em')
        r.fieldcell('int_base', width='6em')
        r.fieldcell('vol_base', width='5em')
        r.fieldcell('simp_base', width='5em')
        r.fieldcell('att_base', width='5em')
        r.fieldcell('mov_base', width='6em')
        r.fieldcell('magia_base', width='4em')
        r.fieldcell('fol_base', width='6em')
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
        return dict(height='350px', width='600px')

    ############################## FORM METHODS #################################

    def formBase(self, parentBC, disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        pane = bc.contentPane(region='left', width='65%')
        tc = bc.tabContainer(region='center')
        self.form_razza(pane)
        self.griglia_ferite(tc.borderContainer(title='!!Ferite'))
        self.griglia_fato(tc.borderContainer(title='!!Punti Fato'))

    def form_razza(self, pane):
        fb = pane.formbuilder(cols=2, fld_width='7em', border_spacing='4px', disabled=False, width='300px')
        fb.field('codice', width='2em', colspan=2)
        fb.field('nome', width='245px', colspan=2)
        fb.field('descrizione', width='245px', colspan=2)
        #fb.div(width='20px',height='20px',lbl='!!Colore',background='^.colore').menu(modifiers='*',_class='colorPaletteMenu').menuItem().colorPalette(value='^.colore')
        fb.field('ac_base')
        fb.field('ab_base')
        fb.field('f_base')
        fb.field('r_base')
        fb.field('ag_base')
        fb.field('int_base')
        fb.field('vol_base')
        fb.field('simp_base')
        fb.field('att_base')
        fb.field('mov_base')
        fb.field('magia_base')
        fb.field('fol_base')

    def griglia_ferite(self, bc):
        iv = self.includedViewBox(bc,
                                  add_action=True,
                                  del_action=True,
                                  storepath='.fer_base', # path of data
                                  struct=self.ferite_struct,
                                  datamode='bag',
                                  label='!!Punti Ferita')

        gridEditor = iv.gridEditor()
        gridEditor.numberTextbox(gridcell='da')
        gridEditor.numberTextbox(gridcell='a')
        gridEditor.numberTextbox(gridcell='valore')

    def ferite_struct(self, struct):
        r = struct.view().rows()
        r.cell('da', name='Tiro da', dtype='L', width='3em')
        r.cell('a', name='Tiro a', dtype='L', width='3em')
        r.cell('valore', name='Valore', dtype='L', width='7em')

    def griglia_fato(self, bc):
        iv = self.includedViewBox(bc,
                                  add_action=True,
                                  del_action=True,
                                  nodeId='FatoGrid',
                                  editorEnabled=True,
                                  storepath='.pf_base',
                                  struct=self.fato_struct,
                                  datamode='bag', label='!!Punti Fato')

        gridEditor = iv.gridEditor()
        gridEditor.numberTextbox(gridcell='da')
        gridEditor.numberTextbox(gridcell='a')
        gridEditor.numberTextbox(gridcell='valore')

    def fato_struct(self, struct):
        r = struct.view().rows()
        r.cell('da', name='Tiro da', dtype='L', width='3em')
        r.cell('a', name='Tiro a', dtype='L', width='3em')
        r.cell('valore', name='Valore', dtype='L', width='7em')
        