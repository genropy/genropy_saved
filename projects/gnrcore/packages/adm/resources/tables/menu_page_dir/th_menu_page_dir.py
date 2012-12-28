#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_count',hidden=True,counter=True)
        r.fieldcell('page_id',hidden=True)
        r.fieldcell('label',edit=True,width='20em')
        r.fieldcell('tags',edit=True,width='30em')

    def th_order(self):
        return '_row_count'

    def th_query(self):
        return dict(column='label', op='contains', val='%')


