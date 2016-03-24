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
        top.bar.replaceSlots('#','2,sections@priority,*,searchOn,2')

    def th_options(self):
        return dict(liveUpdate=True)
        
    def th_order(self):
        return '$annotation_ts'

class Form(BaseComponent):
    def th_form(self, form):
        form.record

class ActionOutcomeForm(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        bc = form.center.borderContainer()
        bc.contentPane(region='top').templateChunk(template='action_tpl',
                                                    record_id='^#FORM.record.id',table='orgn.annotation',_class='orgn_form_tpl',
                                                    margin='10px',height='80px')

        centerframe = bc.framePane(region='center')
        centerframe.top.slotToolbar('*,stackButtons,*')
        sc = centerframe.center.stackContainer(selectedPage='^#FORM.record.exit_status')
        sc.contentPane(title='!!More info',pageName='more_info').dynamicFieldsPane('action_fields',margin='2px')
        self.orgnActionConfirmed(sc.contentPane(title='!!Confirm',pageName='action_confirmed'))
        self.orgnActionCancelled(sc.contentPane(title='!!Cancel',pageName='action_cancelled'))
        self.orgnActionDelay(sc.contentPane(title='!!Delay',pageName='action_delay'))
        self.orgnActionRescheduled(sc.contentPane(title='!!Reschedule',pageName='action_rescheduled'))
        bc.dataController("""
            if(exit_status=='action_rescheduled' || exit_status=='action_confirmed' && outcome_id){
                SET .$assiged_user_id_mandatory = !assigned_tag;
                SET .$assigned_tag_mandatory = !assigned_user_id;
            }""",rec_type='^.rec_type',_delay=1,
                        assigned_tag='^.assigned_tag',
                        assigned_user_id='^.assigned_user_id',
                        exit_status='^#FORM.record.exit_status',
                        outcome_id='^#FORM.record.$outcome_id')

    def orgnActionConfirmed(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=2,border_spacing='3px',width='100%',colswidth='auto',datapath='.record',fld_width='100%')
        fb.field('description',lbl='!!Action result',width='100%',tag='simpleTextArea',colspan=2)

        fb.dbSelect(value='^.outcome_id',hidden='^.@action_type_id.@outcomes?=(!#v || #v.len()===0)',
                    dbtable='orgn.action_outcome',hasDownArrow=True,condition='$action_type_id=:aid',
                    condition_aid='=.action_type_id',
                    selected_deadline_days='.$outcome_deadline_days',
                    selected_description='.next_action.action_description',
                    selected_default_tag='.next_action.assigned_tag',
                    selected_outcome_action_type_id='.next_action.action_type_id',
                    lbl='!!Outcome action')
        fb.br()
        fb.dataRpc('dummy',self.db.table('orgn.annotation').getDueDateFromDeadline,
                    deadline_days='^.$outcome_deadline_days',
                    pivot_date='==new Date()',
                    _if='deadline_days',
                    _onResult="""
                    SET .next_action.date_due = result;""",
                    hidden='^.outcome_id?=!#v')
        fb.textbox(value='^.next_action.action_description',lbl='!!Outcome description',hidden='^.outcome_id?=!#v',colspan=3) 
        fb.dateTextBox(value='^.next_action.date_due',lbl='!!Outcome date due',hidden='^.outcome_id?=!#v',width='7em') 
        fb.timeTextBox(value='^.next_action.time_due',lbl='!!Time due',hidden='^.outcome_id?=!#v',width='7em') 
        fb.filteringSelect(value='^.next_action.priority',hidden='^.outcome_id?=!#v',
                                lbl='!!Priority',values='L:[!!Low],M:[!!Medium],H:[!!High]')
        fb.dbSelect(value='^.next_action.assigned_tag',lbl='!!Assigned tag',
                condition='$child_count = 0 AND $isreserved IS NOT TRUE',
                validate_notnull='^.$assigned_tag_mandatory',
                dbtable='adm.htag',alternatePkey='code',validate_onAccept="""if(userChange && value){
                        SET .next_action.assigned_user_id=null;}""",
                        hidden='^.outcome_id?=!#v',colspan=2)
        fb.dbSelect(value='^.next_action.assigned_user_id',lbl='!!Assigned to',
                    validate_notnull='^.$assiged_user_id_mandatory',
                    dbtable='adm.user',hidden='^.outcome_id?=!#v') #setting condition
        pane.button('!!Confirm Action',action='this.form.publish("save",{destPkey:"*dismiss*"})',position='absolute',bottom='5px',right='5px')

    def orgnActionCancelled(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=1,border_spacing='3px',width='100%',colswidth='auto')
        fb.simpleTextArea(value='^#FORM.record.description',lbl='!!Cancelling reason',width='100%')
        pane.button('!!Cancel Action',action='this.form.publish("save",{destPkey:"*dismiss*"})',position='absolute',bottom='5px',right='5px')

    def orgnActionDelay(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=2,border_spacing='3px',colswidth='auto',datapath='.record')
        fb.field('action_description',lbl='!!Details',width='400px',colspan=2)
        fb.field('date_due',lbl='!!Date due',validate_notnull='^#FORM.record.exit_status?=#v=="action_delay"',width='7em')
        fb.field('time_due',lbl='!!Time due',width='6em')
        pane.button('!!Delay Action',action='this.form.publish("save",{destPkey:"*dismiss*"})',position='absolute',bottom='5px',right='5px')

    def orgnActionRescheduled(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=2,border_spacing='3px',colswidth='auto',datapath='.record')
        fb.field('description',lbl='!!Rescheduling reason',colspan=2,width='400px',tag='simpleTextArea')
        fb.dateTextBox(value='^.rescheduling.date_due',lbl='!!Date due',
                      validate_notnull='^.exit_status?=#v=="action_rescheduled"',
                      width='7em')
        fb.timeTextBox(value='^.rescheduling.time_due',lbl='!!Time due',width='6em')
        fb.dbSelect(value='^.rescheduling.assigned_user_id',lbl='!!Rescheduling user',
                    validate_notnull='^.$assiged_user_id_mandatory',validate_onAccept="""if(userChange && value){
                        SET .rescheduling.assigned_tag=null;}""",
                    dbtable='adm.user',width='7em') #setting condition
        fb.dbSelect(value='^.rescheduling.assigned_tag',lbl='!!Rescheduling Tag',
                condition='$child_count = 0 AND $isreserved IS NOT TRUE',
                validate_notnull='^.$assigned_tag_mandatory',
                dbtable='adm.htag',alternatePkey='code',validate_onAccept="""if(userChange && value){
                        SET .rescheduling.assigned_user_id=null;}""",width='7em')
        pane.button('!!Reschedule Action',action='this.form.publish("save",{destPkey:"*dismiss*"})',position='absolute',bottom='5px',right='5px')

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

    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        record.setItem('.exit_status','more_info',_sendback=True)


