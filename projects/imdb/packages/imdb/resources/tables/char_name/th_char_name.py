#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('imdb_index')
        r.fieldcell('imdb_id')
        r.fieldcell('name_pcode_nf')
        r.fieldcell('surname_pcode')
        r.fieldcell('md5sum')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('imdb_index')
        fb.field('imdb_id')
        fb.field('name_pcode_nf')
        fb.field('surname_pcode')
        fb.field('md5sum')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
