#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('pkgid')
        r.fieldcell('prj')

    def th_order(self):
        return 'pkgid'

    def th_query(self):
        return dict(column='pkgid', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('pkgid')
        fb.field('prj')
        tc = bc.tabContainer(region='center',margin='2px')
        tc.contentPane(title='Tables').dialogTableHandler(relation='@tables',viewResource='ViewFromPackage',
                                                            nodeId='tblinfo_frompkg')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
