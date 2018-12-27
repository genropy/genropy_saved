#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('hierarchical_name')

    def th_order(self):
        return 'hierarchical_name'

    def th_query(self):
        return dict(column='hierarchical_name', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.button('Parse Module',action='FIRE #FORM.parsemodule',hidden='^.rtype?=#v!="M"')
        fb.dataRpc('dummy',self.parseModule,
                    _fired='^#FORM.parsemodule',hierarchical_name='=.hierarchical_name')

    @public_method
    def parseModule(self,hierarchical_name=None):
        self.db.table('dev.pysource').parseModule(hierarchical_name)


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px',hierarchical=True)
