#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('title')
        r.fieldcell('imdb_index')
        r.fieldcell('kind_id')
        r.fieldcell('production_year')
        r.fieldcell('episode_of_id')
        r.fieldcell('season_nr')
        r.fieldcell('episode_nr')
        r.fieldcell('series_years')

        
    def th_options(self):
        return dict(tableRecordCount=True)
        
    def th_order(self):
        return 'title'

    def th_sections_kind(self):
        result = []
        f = self.db.table('imdb.kind_type').query().fetch()
        for r in f:
            result.append(dict(code=str(r['id']),caption=r['kind'],condition='$kind_id=:k',condition_k=r['id']))
        return result

    def th_bottom_custom(self,bottom):
        bottom.slotToolbar('3,sections@kind,*')

    def th_query(self):
        return dict(column='title', op='startswith', val='')

class Form(BaseComponent):

    def th_form(self, form):
        bc=form.center.borderContainer()
        top=bc.contentPane(region='top',datapath='.record')

        fb = top.formbuilder(cols=2, border_spacing='4px')
        fb.field('title',colspan=2)
        fb.field('kind_id')
        fb.field('production_year')
        fb.field('episode_of_id')
        fb.field('season_nr')
        fb.field('episode_nr')
        fb.field('series_years')
        self.castMembers( bc.contentPane(region='center'))
        
    def castMembers(self,pane):
        pane.plainTableHandler(relation='@cast_members',viewResource=':ViewFromMovie')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
