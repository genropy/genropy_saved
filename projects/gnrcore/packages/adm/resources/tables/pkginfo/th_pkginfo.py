#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('pkg')
        r.fieldcell('prj')

    def th_order(self):
        return 'pkg'

    def th_query(self):
        return dict(column='pkg', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('pkg')
        fb.field('prj')
        tc = bc.tabContainer(region='center',margin='2px')
        tc.contentPane(title='Tables').dialogTableHandler(relation='@tables')
        tc.contentPane(title='Permissons').plainTableHandler(relation='@permissions',viewResource='ViewEditable')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
