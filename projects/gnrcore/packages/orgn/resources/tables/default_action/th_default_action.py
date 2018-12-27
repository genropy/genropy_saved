#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class ViewFromAnnotationType(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('action_type_id',width='100%')
        r.fieldcell('@action_type_id.default_tag',width='10em')
        r.fieldcell('@action_type_id.default_priority',width='10em')
        r.fieldcell('@action_type_id.color',name='Color',width='7em',
                    _customGetter="""function(row){
                        return dataTemplate("<div style='background:$_action_type_id_background_color;color:$_action_type_id_color;border:1px solid $color;text-align:center;border-radius:10px;'>Sample</div>",row)
                    }""")
        r.fieldcell('@action_type_id.background_color',hidden=True)

    def th_order(self):
        return 'annotation_type_id'

    def th_query(self):
        return dict(column='annotation_type_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('annotation_type_id')
        fb.field('action_type_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
