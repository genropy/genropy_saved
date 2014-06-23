# -*- coding: UTF-8 -*-

# th_localita.py
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent

class Form(BaseComponent):

    def th_form(self,form,**kwargs):
        pane = form.record
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('regione',width='15em')
        
    def th_dialog(self):
        return dict(height='300px',width='500px')

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome', width='20em')
        r.fieldcell('sigla',width='3em')
        r.fieldcell('codice_istat',width='7em')
        r.fieldcell('regione',width='15em')
        r.cell('pippo',calculated=True,formula='regione+"-"+sigla')
    

    def th_order(self):
        return 'nome'

    def th_query(self):
        return dict(column='nome',op='contains', val='')
        