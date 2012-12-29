#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('hierarchical_label')
        r.fieldcell('tags')
        r.fieldcell('summary')

    def th_order(self):
        return '_h_count'

    def th_query(self):
        return dict(column='parent_id', op='contains', val='%')



    def th_bottom_custom(self,bottom):
        bar = bottom.slotToolbar('importbtn,*')
        bar.importbtn.button('Import from menuxml',fire='.import')
        bar.dataRpc('dummy',self.db.table('adm.menu_dir').createRootHierarchy,_fired='^.import')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('label')
        fb.field('tags')
        fb.field('summary',colspan=2,width='100%')
        bc.contentPane(region='center').inlineTableHandler(relation='@dir_pages',addrow=False,picker='page_id',picker_viewResource='PagePickerView')

    def th_options(self):
        return dict(hierarchical=True)
