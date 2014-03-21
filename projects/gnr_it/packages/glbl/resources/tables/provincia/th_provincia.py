# -*- coding: UTF-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent

class Form(BaseComponent):

    def th_form(self,form,**kwargs):
        pane = form.record
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='5px')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('regione')
        
    def th_dialog(self):
        return dict(height='180px',width='250px')

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


    def th_sections_zone(self):
        return [dict(code='nord_est',caption='!!Nord Est',condition='@regione.zona=:zona',condition_zona='Nord-est'),
                dict(code='nord_ovest',caption='!!Nord Ovest',condition='@regione.zona=:zona',condition_zona='Nord-ovest'),
                dict(code='centro',caption='!!Centro',condition='@regione.zona=:zona',condition_zona='Centro'),
                dict(code='sud',caption='!!Sud',condition='@regione.zona=:zona',condition_zona='Sud'),
                dict(code='isole',caption='!!Isole',condition='@regione.zona=:zona',condition_zona='Isole')
                ]
                
    def th_top_custom(self,top):
        top.bar.replaceSlots('searchOn','searchOn,sections@zone')

    def th_options(self):
        return dict(virtualStore=False)
        

class ViewFromRegione(BaseComponent):    
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('sigla',width='3em',edit=True)
        r.fieldcell('nome', width='20em',edit=True,name='Nome')
        r.fieldcell('codice_istat',width='7em',sortable=False,edit=True)
        
    def th_order(self):
        return 'nome'


        

