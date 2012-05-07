# -*- coding: UTF-8 -*-

"""
th_person.py
Created by Jeff Edwards on 2011-03-13.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        """!!Main view"""
        r = struct.view().rows()
        r.fieldcell('name_first', width='10em')
        r.fieldcell('name_last', width='12em')
        r.fieldcell('birth_year', width='7em')
        r.fieldcell('death_year', width='7em')
        r.fieldcell('nationality', width='12em')
        r.fieldcell('number', width='7em')
        return struct

    def th_order(self):
        return '$name_last,$name_first'

    def th_query(self):
        return dict(column='name_full',op='contains', val='%', runrunOnStart=True)


class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        pane.attributes.update(tag='borderContainer',_class='pbl_roundedGroup',margin='3px')
        pane.div('!!Person or Artist',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, margin='1em',border_spacing='3px',fld_width='20em')
        fb.field('name_first')
        fb.field('name_last')
        fb.field('nationality')
        fb.field('birth_year',width='5em')
        fb.field('death_year',width='5em')
        fb.field('number',width='5em')