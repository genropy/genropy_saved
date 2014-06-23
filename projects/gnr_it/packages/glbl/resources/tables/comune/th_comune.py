#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('denominazione')
        r.fieldcell('sigla_provincia',width='3em',name='Pr.',caption_field='sigla')
        r.fieldcell('@sigla_provincia.regione',width='3em',name='Reg.')
        r.fieldcell('capoluogo')
        r.fieldcell('zona_altimetrica')
        r.fieldcell('altitudine')
        r.fieldcell('litoraneo')
        r.fieldcell('comune_montano')
        r.fieldcell('csl')
        r.fieldcell('superficie')
        r.fieldcell('popolazione_residente')

    def th_order(self):
        return 'denominazione'

    def th_query(self):
        return dict(column='codice_regione', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('codice_regione')
        fb.field('codice_provincia')
        fb.field('sigla_provincia')
        fb.field('codice_comune')
        fb.field('denominazione')
        fb.field('denominazione_tedesca')
        fb.field('capoluogo')
        fb.field('zona_altimetrica')
        fb.field('altitudine')
        fb.field('litoraneo')
        fb.field('comune_montano')
        fb.field('csl')
        fb.field('superficie')
        fb.field('popolazione_residente')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
