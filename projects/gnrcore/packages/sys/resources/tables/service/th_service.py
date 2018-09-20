#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('service_name')
        r.fieldcell('service_type')
        r.fieldcell('resource')
        r.fieldcell('parameters')

    def th_order(self):
        return 'service_name'

    def th_query(self):
        return dict(column='service_name', op='contains', val='')

    def th_options(self):
        #addrow=[(service_type,dict(service_type=service_type)) for service_type in service_types]
        return dict(addrow=self.db.table('sys.service').getAvailableServiceTree())



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('service_name')
        fb.field('service_type')
        fb.field('resource')
        fb.field('parameters')


    #def th_options(self):
    #    return dict(dialog_height='400px', dialog_width='600px',addrow=[(service_type,dict(service_type=service_type)) for service_type in service_types])
