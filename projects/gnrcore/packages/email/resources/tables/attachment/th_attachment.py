#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('filename',width='7em')
        r.fieldcell('mime_type',width='7em')
        r.fieldcell('size',width='7em')
        r.fieldcell('path',width='7em')
        r.fieldcell('message_id',width='35em')
        return struct

    def th_order(self):
        return 'filename'

    def th_query(self):
        return dict(column='filename',op='contains', val='',runOnStart=False)

    def th_dialog(self):
        return dict(height='400px',width='600px')


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=1,border_spacing='4px')
        fb.field('filename')
        fb.field('mime_type')
        fb.field('size')
        fb.field('path')
        fb.field('message_id')


