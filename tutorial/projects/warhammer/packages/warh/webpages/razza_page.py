#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2010-05-15.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable = 'warh.razza'
    py_requires = """public:TableHandlerMain,
                     public:IncludedView"""
                     
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Warhammer'
        
    def barTitle(self):
        return '!!Warhammer'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def th_form(self, form, **kwargs):
        bc = form.record.borderContainer(margin='3px')
        pane = bc.contentPane(region='top', height='50%')
        tc = bc.tabContainer(region='center')
        self.form_razza(pane)
        self.griglia_ferite(tc.borderContainer(title='!!Ferite'))
        self.griglia_fato(tc.borderContainer(title='!!Punti Fato'))
        
    def form_razza(self, pane):
        fb = pane.formbuilder(cols=2, fld_width='7em', border_spacing='4px', disabled=False, width='300px')
        fb.field('codice', width='2em', colspan=2)
        fb.field('nome', width='245px', colspan=2)
        fb.field('descrizione', width='245px', colspan=2)
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
                                  nodeId='FeriteGrid',
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
        r.cell('da', name='Tiro da', dtype='L', width='6em')
        r.cell('a', name='Tiro a', dtype='L', width='6em')
        r.cell('valore', name='Valore', dtype='L', width='6em')
        
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
        r.cell('da', name='Tiro da', dtype='L', width='6em')
        r.cell('a', name='Tiro a', dtype='L', width='6em')
        r.cell('valore', name='Valore', dtype='L', width='6em')
        