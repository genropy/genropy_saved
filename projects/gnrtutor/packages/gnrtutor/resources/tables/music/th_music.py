# -*- coding: UTF-8 -*-

"""
th_music.py
Created by Jeff Edwards on 2011-03-13.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        """!!Main view"""
        r = struct.view().rows()
        r.fieldcell('title', width='30em')
        r.fieldcell('genre', width='12em')
        r.fieldcell('year', width='7em')
        r.fieldcell('rating', width='7em')
        return struct

    def th_order(self):
        return '$title'

    def th_query(self):
        return dict(column='title',op='contains', val='%', runOnStart=True)


class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        pane.attributes.update(tag='borderContainer',_class='pbl_roundedGroup',margin='3px')
        pane.div('!!Music',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, margin='1em',border_spacing='3px',fld_width='20em')
        fb.field('title')
        fb.field('genre')
        fb.field('year')
        fb.field('rating',width='5em')
