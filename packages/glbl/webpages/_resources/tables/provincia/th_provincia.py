# -*- coding: UTF-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrbaseclasses import component_hook

class Form(BaseComponent):
    @component_hook
    def form(self,pane,**kwargs):
        pane.div(u'!!Provincia',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('regione',width='15em')

class View(BaseComponent):
    @component_hook
    def struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome', width='20em')
        r.fieldcell('sigla',width='3em')
        r.fieldcell('codice_istat',width='7em')
        r.fieldcell('regione',width='15em')

    @component_hook
    def order(self):
        return 'nome'

    @component_hook 
    def query(self):
        return dict(column='nome',op='contains', val=None)
        