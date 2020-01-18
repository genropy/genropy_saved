#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('date_from')
        r.fieldcell('date_to')

    def th_order(self):
        return 'date_from'

    def th_query(self):
        return dict(column='name', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('date_from')
        fb.field('date_to')
        fb.bagField('^.values',colspan=2,
                    table='dform.dform_data',
                    resource='^#FORM.record.@dform_type_version_id.@dform_type_id.hierarchical_code',
                    version='=#FORM.record.@dform_type_version_id.version_code'
                    )
        fb.bagField('^.options',colspan=2,
                    table='dform.dform_data',
                    resource='^#FORM.record.@dform_type_version_id.@dform_type_id.hierarchical_code',
                    version='=#FORM.record.@dform_type_version_id.version_code'
                    )

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
