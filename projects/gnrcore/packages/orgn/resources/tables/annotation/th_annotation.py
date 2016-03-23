#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from datetime import datetime
from gnr.core.gnrbag import Bag

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('annotation_caption')
        r.fieldcell('description')
        #r.fieldcell('log_id')

    def th_order(self):
        return 'annotation_caption'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')

class ViewAction(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('annotation_caption')
        r.fieldcell('assigned_to')
        r.fieldcell('priority',width='6em')
        r.fieldcell('notice_days')
        #r.fieldcell('log_id')

    def th_order(self):
        return 'annotation_caption'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')

class ViewPlugin(View):
    def th_hiddencolumns(self):
        return '$linked_fkey'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('template_cell',width='100%', name='-')
        #r.fieldcell('__ins_ts',name='Ins')
        #r.fieldcell('annotation_caption')
        #r.fieldcell('priority')
        #r.fieldcell('connected_description',name='Connected to')

    def th_top_custom(self,top):
        top.bar.replaceSlots('#','*,sections@priority,*')

    def th_options(self):
        return dict(liveUpdate=True)
        
    def th_order(self):
        return '$__ins_ts'

class Form(BaseComponent):
    def th_form(self, form):
        form.record

class ActionOutcomeForm(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        bc = form.center.borderContainer()
        bc.contentPane(region='top').templateChunk(template='action_tpl',
                                                    record_id='^#FORM.record.id',table='orgn.annotation',_class='orgn_form_tpl',
                                                    margin='5px',height='80px')

        centerframe = bc.framePane(region='center')
        centerframe.top.slotToolbar('*,stackButtons,*')
        sc = centerframe.center.stackContainer(selectedPage='^#FORM.record.exit_status')
        sc.contentPane(title='!!More info',pageName='more_info').dynamicFieldsPane('action_fields',margin='2px')
        self.orgnActionConfirmed(sc.contentPane(title='!!Action confirmed',pageName='action_confirmed'))
        self.orgnActionCancelled(sc.contentPane(title='!!Action cancelled',pageName='action_cancelled'))
        self.orgnActionDelay(sc.contentPane(title='!!Action Delay',pageName='action_delay'))
        self.orgnActionRescheduled(sc.contentPane(title='!!Action rescheduled',pageName='action_rescheduled'))


    def orgnActionConfirmed(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=1,border_spacing='3px',width='100%',colswidth='auto')
        fb.simpleTextArea(value='^#FORM.record.description',lbl='!!Action description',width='100%')
        fb.button('!!Confirm Action',action='this.form.publish("save",{destPkey:"*dismiss*"})')

    def orgnActionCancelled(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=1,border_spacing='3px',width='100%',colswidth='auto')
        fb.simpleTextArea(value='^#FORM.record.description',lbl='!!Cancelling reason',width='100%')
        fb.button('!!Cancel Action',action='this.form.publish("save",{destPkey:"*dismiss*"})')

    def orgnActionDelay(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=2,border_spacing='3px',colswidth='auto')
        fb.simpleTextArea(value='^#FORM.record.action_description',lbl='!!Delay details',width='400px',colspan=2)
        fb.dateTextBox(value='^#FORM.record.date_due',lbl='!!Date due',validate_notnull='^#FORM.record.exit_status?=#v=="action_delay"',width='7em')
        fb.timeTextBox(value='^#FORM.record.time_due',lbl='!!Time due',width='6em')
        fb.button('!!Delay Action',action='this.form.publish("save",{destPkey:"*dismiss*"})')

    def orgnActionRescheduled(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=2,border_spacing='3px',colswidth='auto')
        fb.simpleTextArea(value='^#FORM.record.description',lbl='!!Rescheduling reason',colspan=2,width='400px')
        fb.dateTextBox(value='^#FORM.record.rescheduling.date_due',lbl='!!Date due',
                      validate_notnull='^#FORM.record.exit_status?=#v=="action_rescheduled"',
                      width='7em')
        fb.timeTextBox(value='^#FORM.record.rescheduling.time_due',lbl='!!Time due',width='6em')
        fb.dbSelect(value='^#FORM.record.rescheduling.assigned_user_id',lbl='!!Rescheduling user',
                    dbtable='adm.user',width='7em') #setting condition
        fb.dbSelect(value='^#FORM.record.rescheduling.assigned_tag',lbl='!!Rescheduling Tag',
                condition='$child_count = 0 AND $isreserved IS NOT TRUE',
                dbtable='adm.htag',alternatePkey='code',validate_onAccept="""if(userChange){
                        SET #FORM.record.rescheduling.assigned_user_id=null;}""",width='7em')
        fb.button('!!Reschedule Action',action='this.form.publish("save",{destPkey:"*dismiss*"})')

    def th_options(self):
        return dict(dialog_height='300px',dialog_width='600px',
                    titleTemplate='!!Action $@action_type_id.description',
                    showtoolbar=False)

    @public_method
    def th_onSaving(self, recordCluster,recordClusterAttr, resultAttr=None):
        exit_status = recordCluster.pop('exit_status')
        tblannotation_type = self.db.table('orgn.annotation_type')
        if exit_status == 'action_confirmed':
            recordCluster['rec_type'] = 'AN'
            recordCluster['annotation_type_id'] = tblannotation_type.sysRecord('ACT_CONFIRMED')['id']
        elif exit_status == 'action_cancelled':
            recordCluster['rec_type'] = 'AN'
            recordCluster['annotation_type_id'] = tblannotation_type.sysRecord('ACT_CANCELLED')['id']
        elif exit_status == 'action_rescheduled':
            recordCluster['rec_type'] = 'AN'
            recordCluster['annotation_type_id'] = tblannotation_type.sysRecord('ACT_RESCHEDULED')['id']
        elif exit_status == 'action_delay':
            n_date_due = recordCluster.getNode('date_due')
            n_time_due = recordCluster.getNode('time_due')
            delay_history = recordCluster['delay_history'] or Bag()
            r = Bag(dict(user=self.user))
            if n_date_due and n_date_due.value != n_date_due.attr.get('oldValue'):
                r['new_date_due'] = n_date_due.value 
                r['old_date_due'] = n_date_due.attr.get('oldValue')
            if n_time_due and n_time_due.value != n_time_due.attr.get('oldValue'):
                r['new_time_due'] = n_date_due.value 
                r['old_time_due'] = n_date_due.attr.get('oldValue')
            delay_history['r_%s' %(len(delay_history)+1)] = r
            recordCluster['delay_history'] = delay_history



