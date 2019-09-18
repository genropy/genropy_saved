# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,metadata
from datetime import datetime,timedelta
from gnr.core.gnrbag import Bag

class View(BaseComponent):
    def th_hiddencolumns(self):
        return """$annotation_ts,$sort_ts,$priority,$rec_type,$annotation_background,
                  $annotation_color,$description,$action_description,
                  $done_ts,$action_type_description,$following_actions"""

    def th_struct(self,struct):
        r = struct.view().rows()
        r.cell('priority',width='2em',
            name='P.',rowTemplate="""
            <div class="priority_annotation_cell priority_$priority">&nbsp;</div>
            """)
        r.fieldcell('sort_ts',name='!!Datetime',width='6em')
        r.fieldcell('author_user_id',name='!!Autor',width='9em')
        r.cell('annotation_template',name='!!Type',width='9em',
                rowTemplate="""<div style='background:$annotation_background;color:$annotation_color;border:1px solid $color;text-align:center;border-radius:10px;'>$annotation_caption</div>""")
        r.fieldcell('annotation_caption',hidden=True)
        r.fieldcell('calc_description',width='25em',name='Description')
        r.fieldcell('date_due',width='7em',name='!!Date due')

    def th_order(self):
        return 'sort_ts'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')

    def th_bottom_custom(self,bottom):
        bottom.slotToolbar('2,sections@entities,*,sections@rec_type,2')

    
    def th_sections_entities(self):
        entities = self.db.table('orgn.annotation').getLinkedEntities()
        result = [dict(code='_all_',caption='!!All')]
        for ent in entities.split(','):
            code,caption = ent.split(':')
            result.append(dict(code=code,caption=caption,condition='$linked_entity=:le',condition_le=code))
        return result

    @public_method
    def th_applymethod(self,selection):
        def cb(row):
            _customClasses=['orgn_%s' %row['rec_type']]
            return dict(_customClasses=' '.join(_customClasses))
        selection.apply(cb)


class ViewMixedComponent(View):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.cell('priority',width='2em',
            name='P.',rowTemplate="""
            <div class="priority_annotation_cell priority_$priority">&nbsp;</div>
            """)
        r.fieldcell('sort_ts',name='!!Datetime',width='6em')
        r.fieldcell('author_user_id',name='!!Autor',width='9em')
        r.fieldcell('__mod_ts',name='!!Last upd.',width='6em')
        r.fieldcell('__mod_user',name='!!Upd.User',width='9em')
        r.cell('annotation_template',name='!!Type',width='9em',
                rowTemplate="""<div style='background:$annotation_background;color:$annotation_color;border:1px solid $annotation_color;text-align:center;border-radius:10px;'>$annotation_caption</div>""")
        r.fieldcell('annotation_caption',hidden=True)
        r.fieldcell('calc_description',width='25em',name='Description')
        r.cell('action_do',name=" ",calculated=True,width='3em',
                    cellClasses='cellbutton',
                    format_buttonclass='icnBaseLens auction',
                    format_isbutton=True,format_onclick="""var row = this.widget.rowByIndex($1.rowIndex);
                                                           this.publish('do_action',{pkey:row['_pkey']});""",
                    cellClassCB="""var row = cell.grid.rowByIndex(inRowIndex);
                                    if(row.rec_type=='AN'){
                                        return 'hidden';
                                    }""")       
        #r.fieldcell('log_id')

    def th_struct_ann(self,struct):
        r = struct.view().rows()
        r.fieldcell('sort_ts',name='!!Datetime',width='6em')
        r.fieldcell('__mod_ts',name='!!Last upd.',width='6em')
        r.fieldcell('__mod_user',name='!!Upd.User',width='9em')
        r.cell('annotation_template',name='!!Type',width='30em',
                rowTemplate="""<div style='background:$annotation_background;color:$annotation_color;border:1px solid $annotation_color;text-align:center;border-radius:10px;'><b>$annotation_caption</b><br/>$action_description</div>""")
        r.fieldcell('annotation_caption',hidden=True)
        r.fieldcell('calc_description',width='30em',name='Description')

    @metadata(variable_struct=True,isMain=True)
    def th_sections_modesec(self):
        return [dict(code='all',caption='!!Actions and annotations'),
                dict(code='annotation',caption='!!Annotations',condition='$rec_type=:rt',condition_rt='AN',struct='ann'),
                dict(code='action',caption='!!Actions',condition='$rec_type=:rt',condition_rt='AC',struct='')]

    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@modesec')

    def th_bottom_custom(self,bottom):
        pass

class ViewZoomAnnotationAndAction(object):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.cell('priority',width='2em',
            name='P.',rowTemplate="""
            <div class="priority_annotation_cell priority_$priority">&nbsp;</div>
            """)
        r.fieldcell('sort_ts',name='!!Datetime',width='6em')
        r.fieldcell('author_user_id',name='!!Autor',width='9em')
        r.fieldcell('__mod_ts',name='!!Last upd.',width='6em')
        r.fieldcell('__mod_user',name='!!Upd.User',width='9em')
        r.cell('annotation_template',name='!!Type',width='9em',
                rowTemplate="""<div style='background:$annotation_background;color:$annotation_color;border:1px solid $annotation_color;text-align:center;border-radius:10px;'>$annotation_caption</div>""")
        r.fieldcell('annotation_caption',hidden=True)
        r.fieldcell('calc_description',width='25em',name='Description')
        r.cell('action_do',name=" ",calculated=True,width='3em',
                    cellClasses='cellbutton',
                    format_buttonclass='icnBaseLens auction',
                    format_isbutton=True,format_onclick="""var row = this.widget.rowByIndex($1.rowIndex);
                                                           this.publish('do_action',{pkey:row['_pkey']});""",
                    cellClassCB="""var row = cell.grid.rowByIndex(inRowIndex);
                                    if(row.rec_type=='AN'){
                                        return 'hidden';
                                    }""")  

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
        return '$calculated_due_ts,$linked_fkey'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('template_cell',width='100%', name='-')
        #r.fieldcell('__ins_ts',name='Ins')
        #r.fieldcell('annotation_caption')
        #r.fieldcell('priority')
        #r.fieldcell('connected_description',name='Connected to')

    def th_top_custom(self,top):
        top.bar.replaceSlots('#','2,sections@action_type_id,5,searchOn,count,*',
                                sections_action_type_id_multiButton=False,
                                sections_action_type_id_multivalue=True,
                                sections_action_type_id_lbl='!!Actions')
        
        top.slotToolbar('*,sections@priority,*',
                        childname='lower',
                        _position='>bar')

    def th_options(self):
        return dict(liveUpdate=True,limit=1000)
        
    def th_order(self):
        return '$calculated_due_ts'


    def th_bottom_custom(self,bottom):
        bottom.slotToolbar('2,sections@entities,*,2')


class ViewDashboard(ViewPlugin):
    def th_bottom_custom(self,bottom):
        bottom.slotToolbar('2,sections@priority,*,sections@action_type_id,2',
                                sections_action_type_id_multiButton=False,
                                sections_action_type_id_multivalue=False,
                                sections_action_type_id_lbl='!!Actions')


    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@entities')
    


class ActionOutcomeForm(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        form.attributes.update(form_avoidPendingChangesDialog=True)
        bc = form.center.borderContainer()
        self.action_outcome_form(bc)

    def action_outcome_form(self,bc):
        bc.contentPane(region='top',height='95px').templateChunk(template='action_tpl',
                                                    record_id='^#FORM.record.id',table='orgn.annotation',_class='orgn_form_tpl')

        centerframe = bc.framePane(region='center')
        centerframe.top.slotToolbar('*,stackButtons,*')
        sc = centerframe.center.stackContainer(selectedPage='^#FORM.record.exit_status')
        sc.contentPane(title='!!More info',pageName='more_info').dynamicFieldsPane('action_fields',margin='2px')
        self.orgnActionConfirmed(sc.contentPane(title='!!Confirm',pageName='action_confirmed'))
        self.orgnActionCancelled(sc.contentPane(title='!!Cancel',pageName='action_cancelled'))
        self.orgnActionDelay(sc.contentPane(title='!!Delay',pageName='action_delay'))
        self.orgnActionRescheduled(sc.contentPane(title='!!Reschedule',pageName='action_rescheduled'))

    def orgnActionConfirmed(self,pane):
        fb = pane.div(margin='10px').formbuilder(cols=2,border_spacing='3px',width='100%',colswidth='auto',datapath='.record',fld_width='100%')
        fb.field('description',lbl='!!Action result',width='100%',tag='simpleTextArea',colspan=2)

        fb.dbSelect(value='^.outcome_id',hidden='^.@action_type_id.@outcomes?=(!#v || #v.len()===0)',
                    dbtable='orgn.action_outcome',hasDownArrow=True,condition='$action_type_id=:aid',
                    condition_aid='=.action_type_id',
                    selected_deadline_days='.$outcome_deadline_days',
                    selected_description='.next_action.action_description',
                    selected_default_tag='.next_action.assigned_tag',
                    selected_default_priority='.next_action.priority',
                    selected_outcome_action_type_id='.next_action.action_type_id',
                    lbl='!!Outcome action',colspan=2)
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
                                validate_notnull='^.outcome_id',
                                lbl='!!Priority',values='L:[!!Low],M:[!!Medium],H:[!!High]',width='8em')
        fb.dbSelect(value='^.next_action.assigned_tag',lbl='!!Assigned tag',
                condition='$child_count = 0 AND $isreserved IS NOT TRUE',
                validate_notnull='^.outcome_id',
                dbtable='adm.htag',alternatePkey='hierarchical_code',hidden='^.outcome_id?=!#v',
                colspan=2,hasDownArrow=True)
        fb.dbSelect(value='^.next_action.assigned_user_id',lbl='!!Assigned to',
                    condition="$id IN :allowed_user_pkeys AND @tags.@tag_id.hierarchical_code=:atag",
                    condition_atag='=.next_action.assigned_tag',
                    condition_allowed_user_pkeys='=#FORM.record.$allowed_user_pkeys',
                    dbtable='adm.user',hidden='^.outcome_id?=!#v',hasDownArrow=True) #setting condition
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
        
        fb.dbSelect(value='^.rescheduling.assigned_tag',lbl='!!Rescheduling Tag',
                condition='$child_count = 0 AND $isreserved IS NOT TRUE',
                validate_notnull='^.exit_status?=#v=="action_rescheduled"',
                dbtable='adm.htag',alternatePkey='hierarchical_code',width='7em')

        fb.dbSelect(value='^.rescheduling.assigned_user_id',lbl='!!Rescheduling user',
                    condition="$id IN :allowed_user_pkeys AND @tags.@tag_id.hierarchical_code=:atag",
                    condition_atag='=.rescheduling.assigned_tag',
                    condition_allowed_user_pkeys='=#FORM.record.$allowed_user_pkeys',
                    dbtable='adm.user',width='7em') #setting condition
        pane.button('!!Reschedule Action',action='this.form.publish("save",{destPkey:"*dismiss*"})',position='absolute',bottom='5px',right='5px')

    def th_options(self):
        return dict(dialog_height='350px',dialog_width='600px',
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
        recInfo.pop('_protect_write',None)
        record['$allowed_user_pkeys'] = self.db.table('orgn.annotation').getAllowedActionUsers(record)
        record.setItem('.exit_status','more_info',_sendback=True)

class Form(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'
    def th_form(self, form):
        linked_entity = '=#FORM.record.linked_entity'
        default_kwargs = form.store.handler('load').attributes.get('default_kwargs')
        sc = form.center.stackContainer(selectedPage='^.record.rec_type')
        self.orgn_annotationForm(sc.borderContainer(pageName='AN'),linked_entity=linked_entity,sub_action_default_kwargs=default_kwargs)
        self.orgn_actionForm(sc.borderContainer(pageName='AC'),linked_entity=linked_entity,default_kwargs=default_kwargs)

    def orgn_annotationForm(self,bc,linked_entity=None,sub_action_default_kwargs=None):
        annotation_type_condition=None
        annotation_type_kwargs = dict()
        action_type_condition = None
        action_type_kwargs = dict()
        if linked_entity:
            annotation_type_condition = """(CASE WHEN :is_newrecord THEN  ($__syscode IS NULL OR $__syscode NOT IN :system_annotations) ELSE TRUE END) AND
                                        (CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"""
            annotation_type_kwargs = dict(condition_restriction=linked_entity,condition_is_newrecord='=#FORM.controller.is_newrecord',
                                            condition_system_annotations=self.db.table('orgn.annotation_type').systemAnnotations())
            action_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            action_type_kwargs = dict(condition_restriction=linked_entity)
        topbc = bc.borderContainer(region='top',datapath='.record',height='55%')
        fb = topbc.contentPane(region='center').div(margin_right='20px',margin='10px').formbuilder(cols=2, border_spacing='4px',
                                                                                            fld_width='100%',
                                                                                            colswidth='auto',width='100%')
        fb.field('annotation_type_id',condition=annotation_type_condition,
                    hasDownArrow=True,width='15em',validate_notnull='^.rec_type?=#v=="AN"',
                    colspan=2,**annotation_type_kwargs)

        fb.field('description',tag='simpleTextArea',colspan=2)
        fb.field('annotation_date',width='7em')
        fb.field('annotation_time',width='7em')
        fb.appendDynamicFields('annotation_fields')
        #topbc.contentPane(region='center').dynamicFieldsPane('annotation_fields',margin='2px')
        def following_actions_struct(struct):
            r = struct.view().rows()
            r.cell('_date_due_from_pivot',calculated=True,hidden=True)
            r.fieldcell('action_type_id',edit=dict(condition=action_type_condition,
                    selected_default_priority='.priority',
                    selected_default_tag='.assigned_tag',
                    hasDownArrow=True,editDisabled='=#FORM.controller.is_newrecord?=!#v',**action_type_kwargs))
            r.fieldcell('assigned_tag',edit=dict(condition='$child_count = 0 AND $isreserved IS NOT TRUE',tag='dbselect',
                         dbtable='adm.htag',alternatePkey='hierarchical_code',validate_notnull=True,
                         hasDownArrow=True),editLazy='=#ROW.assigned_tag',width='7em')
            r.fieldcell('assigned_user_id',
                         edit=dict(hasDownArrow=True,
                                  condition="$id IN :allowed_user_pkeys AND @tags.@tag_id.hierarchical_code=:atag",
                                  condition_atag='=#ROW.assigned_tag',
                                  condition_allowed_user_pkeys='=#FORM.record.$allowed_user_pkeys'),width='9em')
            r.fieldcell('priority',edit=dict(validate_notnull=True),width='6em')
            r.fieldcell('date_due',edit=dict(validate_notnull='=#ROW._date_due_from_pivot?=!#v'),width='7em',
                        _customGetter="""function(row){
                                            return row['date_due'] || '<div class="dimmed">'+row['_date_due_from_pivot']+'</div>'
                                         }""")
            r.fieldcell('time_due',edit=True,width='7em')
            r.fieldcell('notice_days',edit=True,width='4em')
        th = bc.contentPane(region='center').inlineTableHandler(title='!!Actions',relation='@orgn_related_actions',
                        viewResource='orgn_components:ViewActionComponent',
                        view_structCb=following_actions_struct,searchOn=False,
                        nodeId='orgn_action_#',default_rec_type='AC',default_priority='L',
                        **dict([('default_%s' %k,v) for k,v in sub_action_default_kwargs.items()]))
        rpc = bc.dataRpc('dummy',self.orgn_getDefaultActionsRows,annotation_type_id='^#FORM.record.annotation_type_id',
                        _if='annotation_type_id&&_is_newrecord',_is_newrecord='=#FORM.controller.is_newrecord',**sub_action_default_kwargs)
        rpc.addCallback("""if(result){
                                grid.gridEditor.addNewRows(result)
                            }""",grid = th.view.grid.js_widget)          

    def orgn_actionForm(self,bc,linked_entity=None,default_kwargs=None):
        action_type_condition = None
        action_type_kwargs = dict()
        if linked_entity:
            action_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            action_type_kwargs = dict(condition_restriction=linked_entity)
        fb = bc.contentPane(region='center',datapath='.record').div(margin_right='20px',margin='10px').formbuilder(cols=2, border_spacing='4px',
                                                                                            fld_width='100%',
                                                                                            colswidth='auto',width='100%')
        fb.field('action_type_id',condition=action_type_condition,
                    selected_default_priority='.priority',
                    selected_default_tag='.assigned_tag',
                    hasDownArrow=True,
                    colspan=2,
                    validate_notnull='^.rec_type?=#v=="AC"',
                    unmodifiable=True,**action_type_kwargs)
        fb.field('assigned_tag',condition='$child_count = 0 AND $isreserved IS NOT TRUE',tag='dbselect',
                validate_notnull='^.rec_type?=#v=="AC"',
                dbtable='adm.htag',alternatePkey='hierarchical_code',
                hasDownArrow=True)
        fb.field('assigned_user_id',
                    condition="$id IN :allowed_user_pkeys AND @tags.@tag_id.hierarchical_code=:atag",
                    condition_atag='=.assigned_tag',
                    condition_allowed_user_pkeys='=#FORM.record.$allowed_user_pkeys',
                    hasDownArrow=True)
        fb.field('priority')
        fb.field('notice_days')
        fb.dataRpc('dummy',self.db.table('orgn.annotation').getDueDateFromDeadline,
                    deadline_days='^.@action_type_id.deadline_days',
                    date_due='=.date_due',_if='deadline_days && !date_due',
                    _onResult="""
                    if(result){
                        SET .$date_due_ghost = _F(result);
                    }else{
                        SET .$date_due_ghost = '';
                    }""",
                    **default_kwargs)
        fb.field('date_due',placeholder='^.$date_due_ghost')
        fb.field('time_due')
        fb.field('action_description',tag='simpleTextArea',colspan=2,width='420px',lbl='!!Description')
        fb.appendDynamicFields('action_fields')


    @public_method
    def orgn_getDefaultActionsRows(self,annotation_type_id=None,**action_defaults):
        pivot_date = self.db.table('orgn.annotation').getPivotDateFromDefaults(action_defaults)
        action_types = self.db.table('orgn.action_type').query(where='@annotation_default_actions.annotation_type_id=:annotation_type_id',
                                                               annotation_type_id=annotation_type_id).fetch()
        result = []
        for i,ac in enumerate(action_types):
            _date_due_from_pivot = None
            if ac['deadline_days'] and pivot_date:
                _date_due_from_pivot = datetime(pivot_date.year,pivot_date.month,pivot_date.day)
                _date_due_from_pivot = (_date_due_from_pivot+timedelta(days=ac['deadline_days'])).date()
            result.append(dict(action_type_id=ac['id'],assigned_tag=ac['default_tag'],priority=ac['default_priority'] or 'L',
                                _date_due_from_pivot=self.toText(_date_due_from_pivot)))
        return result

    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        record['$allowed_user_pkeys'] = self.db.table('orgn.annotation').getAllowedActionUsers(record)

    def th_options(self):
        return dict(dialog_height='350px', dialog_width='550px',readOnly=True)


class FormMixedComponent(Form):
    def th_options(self):
        return dict(dialog_height='350px', dialog_width='550px',modal=True)

    def th_form(self, form):
        linked_entity = form._current_options['linked_entity']
        default_kwargs = form.store.handler('load').attributes.get('default_kwargs')
        sc = form.center.stackContainer(selectedPage='^.record.rec_type')
        self.orgn_annotationForm(sc.borderContainer(pageName='AN'),linked_entity=linked_entity,sub_action_default_kwargs=default_kwargs)
        self.orgn_actionForm(sc.borderContainer(pageName='AC'),linked_entity=linked_entity,default_kwargs=default_kwargs)


class FormAction(Form):
    #def th_options(self):
       # anno
       # entities =.getLinkedEntityDict()
#
       # print x
       # return dict(dialog_height='350px', dialog_width='550px',modal=True,
       #                     defaultPrompt=dict(title='!!New Action',
       #                             fields=[dict(value='^.linked_entity',lbl='Entity',tag='filteringSelect',values=entities)]))
#
    def th_form(self, form):
        linked_entity = '=#FORM.record.linked_entity'
        default_kwargs = form.store.handler('load').attributes.get('default_kwargs')
        self.orgn_actionForm(form.center.borderContainer(),linked_entity=linked_entity,default_kwargs=default_kwargs)



class ViewActionComponent(BaseComponent):
    def th_hiddencolumns(self):
        return '$annotation_ts'
    def th_order(self):
        return 'annotation_ts'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')




