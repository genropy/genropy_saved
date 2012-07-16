#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('description')
        r.fieldcell('child_code')
        r.fieldcell('parent_code')
        r.fieldcell('level')
        r.fieldcell('rec_type')
        r.fieldcell('dtype')
        r.fieldcell('name_long')
        r.fieldcell('name_short')
        r.fieldcell('format')
        r.fieldcell('options')
        r.fieldcell('maxvalue')
        r.fieldcell('minvalue')
        r.fieldcell('dflt')
        r.fieldcell('tip')
        r.fieldcell('purpose')
        r.fieldcell('ext_ref')
        r.fieldcell('related_to')
        r.fieldcell('pkg')
        r.fieldcell('pkey_field')
        r.fieldcell('field_size')
        r.fieldcell('tbl')
        r.fieldcell('fld')
        r.fieldcell('comment')
        r.fieldcell('name_full')
        r.fieldcell('datacatalog_path')
        r.fieldcell('dbkey')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('description')
        fb.field('child_code')
        fb.field('parent_code')
        fb.field('level')
        fb.field('rec_type')
        fb.field('dtype')
        fb.field('name_long')
        fb.field('name_short')
        fb.field('format')
        fb.field('options')
        fb.field('maxvalue')
        fb.field('minvalue')
        fb.field('dflt')
        fb.field('tip')
        fb.field('purpose')
        fb.field('ext_ref')
        fb.field('related_to')
        fb.field('pkg')
        fb.field('pkey_field')
        fb.field('field_size')
        fb.field('tbl')
        fb.field('fld')
        fb.field('comment')
        fb.field('name_full')
        fb.field('datacatalog_path')
        fb.field('dbkey')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
