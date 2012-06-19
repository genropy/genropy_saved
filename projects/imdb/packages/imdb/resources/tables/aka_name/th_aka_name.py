#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('person_id')
        r.fieldcell('name')
        r.fieldcell('imdb_index')
        r.fieldcell('name_pcode_cf')
        r.fieldcell('name_pcode_nf')
        r.fieldcell('surname_pcode')
        r.fieldcell('md5sum')

    def th_order(self):
        return 'person_id'

    def th_query(self):
        return dict(column='person_id', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('person_id')
        fb.field('name')
        fb.field('imdb_index')
        fb.field('name_pcode_cf')
        fb.field('name_pcode_nf')
        fb.field('surname_pcode')
        fb.field('md5sum')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
