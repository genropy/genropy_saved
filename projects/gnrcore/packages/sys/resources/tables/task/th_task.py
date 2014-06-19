# -*- coding: UTF-8 -*-

# base.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('task_name',width='10em') # char(4)
        r.fieldcell('table_name',width='10em')
        r.fieldcell('stopped',semaphore=True)
        r.fieldcell('command',width='15em')
        r.fieldcell('month',width='20em')
        r.fieldcell('day',width='15em')
        r.fieldcell('weekday',width='20em')
        r.fieldcell('hour',width='12em')
        r.fieldcell('minute',width='12em')
        r.fieldcell('last_execution',width='14em')
    def th_order(self):
        return 'task_name'
        
    def th_query(self):
        return dict(column='task_name',op='contains', val='',runOnStart=True)

    def th_options(self):
        return dict(widget='dialog')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        top = bc.contentPane(region='top')
        fb = top.div(margin_right='10px').formbuilder(cols=2,border_spacing='4px',margin_top='3px',fld_width='100%',width='100%',lbl_width='5em',fld_html_label=True)
        fb.field('task_name')
        fb.field('table_name')
        fb.field('command',colspan='2')
        fb.field('date_start')
        fb.field('date_end')
        fb.field('stopped',colspan=2)
        rpane = fb.div(lbl='!!Rules',colspan=2,_class='pbl_roundedGroup',padding='3px',padding_top='0')
        self.task_params(rpane)
    
    def task_params(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px',lblpos='T',lblalign='left',
                            fldalign='left',lbl_font_size='.9em',lbl_font_weight='bold')
        fb.div(rounded=4,background='white',padding='3px',
            shadow='1px 1px 2px #666 inset',lbl='!!Month').field('month',tag='checkboxtext',cols=6,border_spacing='2px')
        fb.div(rounded=4,background='white',padding='3px',
            shadow='1px 1px 2px #666 inset',lbl='!!Day').field('day',tag='checkboxtext',cols=10,border_spacing='2px')
        fb.div(rounded=4,background='white',padding='3px',
            shadow='1px 1px 2px #666 inset',lbl='!!Weekday').field('weekday',tag='checkboxtext',cols=7,border_spacing='2px')
        fb.div(rounded=4,background='white',padding='3px',
            shadow='1px 1px 2px #666 inset',lbl='!!Hour').field('hour',tag='checkboxtext',cols=12,border_spacing='2px')
        fb.div(rounded=4,background='white',padding='3px',
            shadow='1px 1px 2px #666 inset',lbl='!!Minute').field('minute',tag='checkboxtext',cols=10,border_spacing='2px')
        
    def th_options(self):
        return dict(dialog_height='530px',dialog_width='600px',modal=True)
        
        
class FormFromTableScript(Form):
    def th_form(self,form):
        pass

        