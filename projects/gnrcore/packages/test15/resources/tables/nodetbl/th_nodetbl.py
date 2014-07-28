#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.cell('__ins_ts',dtype='DH')

        r.fieldcell('partenza')
        r.fieldcell('arrivo')
        r.fieldcell('reg_part')
        r.fieldcell('@partenza.regione_nome')
        r.fieldcell('@partenza.@regione.nome')

    def th_order(self):
        return 'partenza'

    def th_query(self):
        return dict(column='partenza', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('__ins_ts',format='short',lbl='Ins ts',tag='div')
        fb.field('partenza')
        fb.field('arrivo')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
