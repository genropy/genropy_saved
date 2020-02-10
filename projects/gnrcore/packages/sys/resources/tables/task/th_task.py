# -*- coding: utf-8 -*-

# base.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('stopped',inv_semaphore=True,name='!!Active')
        r.fieldcell('task_name',width='10em') # char(4)
        r.fieldcell('table_name',width='10em')
        r.fieldcell('command',width='15em')
        r.fieldcell('frequency',width='7em')
        r.fieldcell('run_asap',width='5em',name='ASAP')
        r.fieldcell('last_execution_ts',width='14em')
        r.fieldcell('last_result_ts',width='14em')
        r.fieldcell('last_error_ts',width='14em')

        #r.fieldcell('month',width='20em')
       # r.fieldcell('day',width='15em')
       # r.fieldcell('weekday',width='20em')
       # r.fieldcell('hour',width='12em')
       # r.fieldcell('minute',width='12em')
       # r.fieldcell('last_execution_ts',width='14em')

    def th_order(self):
        return 'task_name'
        
    def th_query(self):
        return dict(column='task_name',op='contains', val='',runOnStart=True)

    def th_options(self):
        return dict(widget='dialog')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.div(margin_right='10px').formbuilder(cols=3,border_spacing='4px',margin_top='3px',
                                                    fld_html_label=True)
        fb.field('task_name',width='12em')
        fb.field('table_name',colspan=2,width='20em')
        fb.field('command',colspan=3,width='40em')
        fb.field('max_workers',width='4em')
        fb.field('run_asap')
        fb.field('stopped')
        fb.field('worker_code',width='7em')


        fb.field('date_start',width='7em')
        fb.field('date_end',width='7em')
        fb.field('frequency',width='4em')

        center = bc.tabContainer(region='center',margin='2px')

        fb = center.contentPane(title='!!Config').div(margin_right='10px').formbuilder(cols=3,border_spacing='4px',margin_top='3px',
                                                    fld_html_label=True,datapath='.record')
        

        rpane = fb.div(lbl='!!Rules',colspan=3,_class='pbl_roundedGroup',position='relative',padding='3px',padding_top='0')
        fb.dataController("""rpane.setHiderLayer(freq,{message:'Using frequency'});""",rpane=rpane,freq='^.frequency')
        
        self.task_timeRules(rpane)

        #center.contentPane(title='!!Logs',hidden='^#FORM.record.log_result?=!#v').plainTableHandler(relation='@logs',pbl_classes=True,margin='2px')
        center.contentPane(title='Executions').plainTableHandler(relation='@executions',viewResource='ViewFromTask')
    
    def task_timeRules(self,pane):
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
        return dict(dialog_parentRatio=.9)
        
        
class FormFromTableScript(Form):
    def th_form(self,form):
        pass

    def th_options(self):
        return dict(dialog_parentRatio=.9,modal=True)
        
        