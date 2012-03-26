# -*- coding: UTF-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent

class Form(BaseComponent):

    def th_form(self,form,**kwargs):
        pane = form.record
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('regione')
        
    def th_dialog(self):
        return dict(height='300px',width='500px')

class View(BaseComponent):
    
    
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome', width='20em')
        r.fieldcell('sigla',width='3em')
        r.fieldcell('codice_istat',width='7em',sortable=False)
        r.fieldcell('regione',width='100%')

    def th_order(self):
        return 'nome'

    def th_query(self):
        return dict(column='nome',op='contains', val='')
        

class EditableView(View):    
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome', width='20em',edit=True)
        r.fieldcell('sigla',width='3em',edit=True)
        r.fieldcell('codice_istat',width='7em',sortable=False,edit=True)
       # r.cell('pippo',calculated=True,formula='nome+"-"+sigla')
        r.fieldcell('regione',width='8em',name='Regione',edit=True)
        r.fieldcell('@regione.zona',width='5em',name='Zona')
        #r.fieldcell('regione_nome',width='8em')
        

