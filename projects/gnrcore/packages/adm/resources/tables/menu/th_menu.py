#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_h_count',hidden=True)
        r.fieldcell('hierarchical_label')
        r.fieldcell('tags')
        r.fieldcell('summary')

    def th_order(self):
        return '_h_count'

    def th_query(self):
        return dict(column='hierarchical_label', op='contains', val='%')



    def th_bottom_custom(self,bottom):
        bar = bottom.slotToolbar('importbtn,*')
        bar.importbtn.button('Import from menuxml',fire='.import_all')
        bar.dataRpc('dummy',self.db.table('adm.menu').createRootHierarchy,_fired='^.import_all')

        bar.importbtn.button('Update pages',fire='.import_all')
        bar.dataRpc('dummy',self.db.table('adm.menu').createRootHierarchy,pagesOnly=True,_fired='^.import_all')


class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('label')
        fb.field('tags')
        fb.field('summary',colspan=2,width='100%')
        #bc.contentPane(region='center').inlineTableHandler(relation='@dir_pages',addrow=False,picker='page_id',picker_viewResource='PagePickerView')

    def th_options(self):
        return dict(hierarchical=True,tree_picker='page_id',tree_picker_viewResource='PagePickerView')
