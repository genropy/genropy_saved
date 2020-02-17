#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('name')
        r.fieldcell('description')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('name')
        fb.field('description')
        fb.button('Fill Pkg description', action='FIRE fillPackage')
        center = bc.contentPane(region='center')
        top.dataRpc('import_result', self.importPackage,
                     _fired='^fillPackage', 
                     pkg_code='=.code')
       
        
        center.dialogTableHandler(relation='@lg_tables', viewResource='ViewFromPackage')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px' )

    @public_method
    def importPackage(self, pkg_code):
        self.tblobj.importPackage(pkg_code=pkg_code)
        self.db.commit()
