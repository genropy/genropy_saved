#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='warh.razza'
    py_requires='public:Public,standard_tables:TableHandlerLight,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ################ 
    def windowTitle(self):
        return '!!Razze'
        
    def barTitle(self):
        return '!!Razze'
        
    def columnsBase(self):
        return """codice:4,nome:20,descrizione:30,ac_base:4,ab_base:4,f_base/For.Base:4,r_base/Res.Base:4,pf_base/PF.Base:4"""
    
    def printActionBase(self):
        return True

    def exportActionBase(self):
        return True
  
    def orderBase(self):
        return 'nome'

    def formBaseDimension(self):
        return dict(height='300px',width='400px')
############################## FORM METHODS ##################################

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
        fb.field('pf_base',width='100%')