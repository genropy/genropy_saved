#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  provincia.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    maintable='glbl.provincia'
    py_requires='public:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return u'!!Provincia'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return None
        
    def barTitle(self):
        return '!!Provincia'
        
    def columnsBase(self,):
        return """nome/Nome:17,
                  sigla/Sigla:3,
                  codice_istat/Istat:6,
                  regione/Regione:3"""
               
    def formBase(self, parentBC, disabled=False, **kwargs):
        pane=parentBC.contentPane(padding='5px',**kwargs).div(_class='pbl_roundedGroup', height='100%')
        pane.div(u'!!Provincia',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('regione',width='15em')
        
    def orderBase(self):
        return 'nome'
        
    def queryBase(self):
        return dict(column='nome',op='contains', val=None)
        