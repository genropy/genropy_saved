#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts',name='Datetime')
        r.fieldcell('error_type')

        r.fieldcell('description')
        r.fieldcell('username')
        r.fieldcell('user_ip')
        r.fieldcell('user_agent')
        r.fieldcell('fixed')
        r.fieldcell('notes')

    def th_order(self):
        return 'description'

    def th_query(self):
        return dict(column='description', op='contains', val='')

    def th_bottom_custom(self,bar):
        bar.slotToolbar('sections@error_type,*')

    def th_sections_error_type(self):
        return [dict(code='exc',caption='!!Exceptions',condition="$error_type=:c",condition_c='EXC'),
                dict(code='err',caption='!!Errors',condition="$error_type=:c",condition_c='ERR')]


class Form(BaseComponent):
    def th_form(self, form):
        # pane = form.record
        bc = form.center.borderContainer(datapath='#FORM.record')
        self.left(bc.contentPane(region='left',margin='2px',_class='pbl_roundedGroup'))
        self.right(bc.contentPane(region='center',margin='2px',_class='pbl_roundedGroup',overflow='auto'))

    def left(self,pane):
        width='35em'
        pane.div('Error Data',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('error_type',colspan=2,width=width)
        fb.field('description',colspan=2,width=width)
        fb.field('username',width='15em')
        fb.field('user_ip',width='15em')
        fb.field('fixed',colspan=2,width=width)
        fb.field('user_agent',colspan=2,width=width,tag='simpleTextArea',height='2.5em')

    def right(self,pane):
        width='35em'
        pane.div('TraceBack Tree',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.field('error_data',width=width)



    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
