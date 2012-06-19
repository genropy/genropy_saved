#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('movie_id')
        r.fieldcell('title')
        r.fieldcell('imdb_index')
        r.fieldcell('kind_id')
        r.fieldcell('production_year')
        r.fieldcell('phonetic_code')
        r.fieldcell('episode_of_id')
        r.fieldcell('season_nr')
        r.fieldcell('episode_nr')
        r.fieldcell('note')
        r.fieldcell('md5sum')

    def th_order(self):
        return 'movie_id'

    def th_query(self):
        return dict(column='movie_id', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('movie_id')
        fb.field('title')
        fb.field('imdb_index')
        fb.field('kind_id')
        fb.field('production_year')
        fb.field('phonetic_code')
        fb.field('episode_of_id')
        fb.field('season_nr')
        fb.field('episode_nr')
        fb.field('note')
        fb.field('md5sum')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
