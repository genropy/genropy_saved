# -*- coding: UTF-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrwebpage import BaseComponent

class Form(BaseComponent):
    def th_form(self,form,**kwargs):
        pane = form.record
        #pane=parent.contentPane(padding='5px',**kwargs).div(_class='pbl_roundedGroup', height='100%')
        pane.div(u'!!Località',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('provincia',width='15em')
        fb.field('prefisso_tel',width='3em')
        fb.field('cap',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('codice_comune',width='4em')

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome',width='50%')
        r.fieldcell('provincia',width='20%')
        r.fieldcell('codice_istat',width='10%') 
        r.fieldcell('codice_comune',width='10%')
        r.fieldcell('prefisso_tel',width='5%')
        r.fieldcell('cap',width='5%')
        
    def th_order(self):
        return 'nome'
        
    def th_options_(self):
        return dict(widget='border',vpane_region='left', vpane_width='40%',dialog_height='200px',dialog_width='400px')
    
    def th_query(self):
        return dict(column='nome',op='contains', val='')
        