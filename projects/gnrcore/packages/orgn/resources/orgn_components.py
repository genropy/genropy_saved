# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method

class FormMixedComponent(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'
    def th_form(self, form):
        type_restriction = form._current_options['type_restriction']
        user_kwargs = form._current_options['user_kwargs'] or dict()
        default_kwargs = form.store.handler('load').attributes.get('default_kwargs')

        sc = form.center.stackContainer(selectedPage='^.record.rec_type')
        self.orgn_annotationForm(sc.borderContainer(pageName='AN'),type_restriction=type_restriction,user_kwargs=user_kwargs,
                                sub_action_default_kwargs=default_kwargs)
        self.orgn_actionForm(sc.borderContainer(pageName='AC'),type_restriction=type_restriction,user_kwargs=user_kwargs)

    def orgn_annotationForm(self,bc,type_restriction=None,user_kwargs=None,sub_action_default_kwargs=None):
        annotation_type_condition=None
        annotation_type_kwargs = dict()
        action_type_condition = None
        action_type_kwargs = dict()
        if type_restriction:
            annotation_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            annotation_type_kwargs = dict(condition_restriction=type_restriction)
            action_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            action_type_kwargs = dict(condition_restriction=type_restriction)
        topbc = bc.borderContainer(region='top',datapath='.record',height='50%')
        fb = topbc.contentPane(region='top').div(margin_right='20px',margin='10px').formbuilder(cols=1, border_spacing='4px',
                                                                                            fld_width='100%',
                                                                                            colswidth='auto',width='100%')
        fb.field('annotation_type_id',condition=annotation_type_condition,
                    hasDownArrow=True,width='15em',validate_notnull='^.rec_type?=#v=="AN"',**annotation_type_kwargs)
        fb.field('description',tag='simpleTextArea')
        topbc.contentPane(region='center').dynamicFieldsPane('annotation_fields',margin='2px')
    
        def following_actions_struct(struct):
            r = struct.view().rows()
            r.fieldcell('action_type_id',edit=dict(condition=action_type_condition,
                    selected_default_priority='.priority',hasDownArrow=True,
                    selected_default_days_before='.days_before',**action_type_kwargs))
            r.fieldcell('assigned_tag',edit=dict(condition='$child_count = 0 AND $isreserved IS NOT TRUE',tag='dbselect',
                dbtable='adm.htag',alternatePkey='code',
                hasDownArrow=True),editDisabled='=#ROW.assigned_user_id',width='7em')
            r.fieldcell('assigned_user_id',
                         edit=dict(hasDownArrow=True,**user_kwargs),
                         editDisabled='=#ROW.assigned_tag')
            r.fieldcell('priority',edit=True,width='8em')
            r.fieldcell('days_before',edit=True,width='7em')
        th = bc.contentPane(region='center').inlineTableHandler(relation='@orgn_related_actions',
                        viewResource='orgn_components:ViewActionComponent',
                        view_structCb=following_actions_struct,
                        nodeId='orgn_action_#',
                        form_user_kwargs=user_kwargs,default_rec_type='AC',
                        **dict([('default_%s' %k,v) for k,v in sub_action_default_kwargs.items()]))
        rpc = bc.dataRpc('dummy',self.orgn_getDefaultActionsRows,annotation_type_id='^#FORM.record.annotation_type_id',
                        _if='annotation_type_id&&_is_newrecord',_is_newrecord='=#FORM.controller.is_newrecord')
        rpc.addCallback("""if(result){
                                grid.gridEditor.addNewRows(result)
                            }""",grid = th.view.grid.js_widget)

    @public_method
    def orgn_getDefaultActionsRows(self,annotation_type_id=None,**kwargs):
        action_types = self.db.table('orgn.action_type').query(where='@annotation_default_actions.annotation_type_id=:annotation_type_id',
                                                               annotation_type_id=annotation_type_id).fetch()
        result = []
        for i,ac in enumerate(action_types):
            result.append(dict(action_type_id=ac['id'],assigned_tag=ac['default_tag'],days_before=ac['default_days_before'],
                    priority=ac['default_priority']))
        return result
            

    def orgn_actionForm(self,bc,type_restriction=None,user_kwargs=None):
        action_type_condition = None
        action_type_kwargs = dict()
        if type_restriction:
            action_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            action_type_kwargs = dict(condition_restriction=type_restriction)
        fb = bc.contentPane(region='top',datapath='.record').div(margin_right='20px',margin='10px').formbuilder(cols=2, border_spacing='4px',
                                                                                            fld_width='100%',
                                                                                            colswidth='auto',width='100%')
        fb.field('action_type_id',condition=action_type_condition,
                    selected_default_priority='.priority',hasDownArrow=True,
                    colspan=2,
                    selected_default_days_before='.days_before',
                    validate_notnull='^.rec_type?=#v=="AC"',**action_type_kwargs)
        fb.field('assigned_user_id',#disabled='^.assigned_tag',
                                    validate_onAccept="""if(userChange){
                                                SET .assigned_tag=null;
                                    }""",hasDownArrow=True,**user_kwargs)
        #condition='==allowed_users?allowed_users:"TRUE"',condition_allowed_users='=#FORM.condition_allowed_users'
        fb.field('assigned_tag',condition='$child_count = 0 AND $isreserved IS NOT TRUE',tag='dbselect',
                dbtable='adm.htag',alternatePkey='code',
                validate_onAccept="""if(userChange){
                                    SET .assigned_user_id=null;
                                }""",hasDownArrow=True)
        fb.field('priority')
        fb.field('days_before')
        fb.field('date_due')
        fb.field('time_due')
        fb.field('description',tag='simpleTextArea',colspan=2,width='420px')
        bc.contentPane(region='center').dynamicFieldsPane('action_fields',margin='2px')

    def th_options(self):
        return dict(dialog_height='300px', dialog_width='550px',modal=True)

class ViewActionComponent(BaseComponent):
    def th_hiddencolumns(self):
        return '$__ins_ts'
    def th_order(self):
        return '__ins_ts'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')


class FormActionComponent(FormMixedComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'
    def th_form(self, form):
        type_restriction = form._current_options['type_restriction']
        user_kwargs = form._current_options['user_kwargs'] or dict()
        self.orgn_actionForm(form.center.borderContainer(),type_restriction=type_restriction,user_kwargs=user_kwargs)

class ViewMixedComponent(BaseComponent):
    def th_hiddencolumns(self):
        return '$__ins_ts,$rec_type'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts',name='TS')
        r.fieldcell('annotation_caption',width='20em')
        r.fieldcell('description',width='20em')
        r.fieldcell('priority',width='10em')
        r.fieldcell('days_before',width='5em',name='D.B.')
        #r.fieldcell('log_id')

    def th_order(self):
        return '__ins_ts'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')

    def th_sections_orgn(self):
        return [dict(code='all',caption='!!All'),
                dict(code='orgn',caption='!!To do',condition='$done_ts IS NULL'),
                dict(code='done',caption='!!Done',condition='$done_ts IS NOT NULL')]

    @public_method
    def th_applymethod(self,selection):
        def cb(row):
            _customClasses=['orgn_%s' %row['rec_type']]
            return dict(_customClasses=' '.join(_customClasses))
        selection.apply(cb)

class annotationTableHandler(BaseComponent):
    py_requires='th/th:TableHandler'
    @extract_kwargs(user=True)
    @struct_method
    def td_annotationTableHandler(self,pane,type_restriction=None,user_kwargs=None,configurable=False,**kwargs):
        pid = id(pane)
        pane.dialogTableHandler(relation='@annotations',nodeId='orgn_annotation_%s' %pid,
                                datapath='#FORM.orgn_annotations_%s' %pid,
                                viewResource='orgn_components:ViewMixedComponent',
                                formResource='orgn_components:FormMixedComponent',
                                form_type_restriction=type_restriction,
                                form_user_kwargs=user_kwargs,configurable=configurable,
                                addrow=[('Annotation',dict(rec_type='AN')),('Action',dict(rec_type='AC'))],
                                **kwargs)


