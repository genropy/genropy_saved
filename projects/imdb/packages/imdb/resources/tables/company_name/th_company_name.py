#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('country_code')
        r.fieldcell('imdb_id')
        r.fieldcell('name_pcode_nf')
        r.fieldcell('name_pcode_sf')
        r.fieldcell('md5sum')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('country_code')
        fb.field('imdb_id')
        fb.field('name_pcode_nf')
        fb.field('name_pcode_sf')
        fb.field('md5sum')
        bc.contentPane(region='center').plainTableHandler(relation='@movies',viewResource='ViewFromCompany')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
