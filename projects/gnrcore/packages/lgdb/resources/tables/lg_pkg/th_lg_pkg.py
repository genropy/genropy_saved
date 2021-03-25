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
        legacydb = self.db.application.config['legacy_db']
        if legacydb is not None:
            fb.field('legacy_db',values=','.join(legacydb.keys()),tag='filteringSelect')
            fb.field('legacy_schema')
        fb.field('description')
        fb.button('Fill Pkg description', action='FIRE #FORM.fillPackage;')
        center = bc.contentPane(region='center')
        top.dataRpc('import_result', self.importPackage,
                     legacy_db='=.legacy_db', legacy_schema='=.legacy_schema',
                     pkg_code='=.code',_fired='^#FORM.fillPackage')
        center.dialogTableHandler(relation='@lg_tables', viewResource='ViewFromPackage')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px' )

    @public_method
    def importPackage(self, pkg_code=None,legacy_db=None,legacy_schema=None):
        self.tblobj.importPackage(pkg_code=pkg_code,legacy_db=legacy_db,legacy_schema=legacy_schema)
        self.db.commit()
