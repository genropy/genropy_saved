# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs

class FormMixedComponent(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'
    def th_form(self, form):
        type_restriction = form._current_options['type_restriction']
        user_kwargs = form._current_options['user_kwargs'] or dict()
        sc = form.center.stackContainer(selectedPage='^.record.rec_type')
        self.orgn_annotationForm(sc.borderContainer(pageName='AN'),type_restriction=type_restriction,user_kwargs=user_kwargs)
        self.orgn_actionForm(sc.borderContainer(pageName='AC'),type_restriction=type_restriction,user_kwargs=user_kwargs)

    def orgn_annotationForm(self,bc,type_restriction=None,user_kwargs=None):
        if type_restriction:
            annotation_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            annotation_type_kwargs = dict(condition_restriction=type_restriction)
        topbc = bc.borderContainer(region='top',datapath='.record',height='50%')
        fb = topbc.contentPane(region='top').div(margin_right='20px',margin='10px').formbuilder(cols=1, border_spacing='4px',
                                                                                            fld_width='100%',
                                                                                            colswidth='auto',width='100%')
        fb.field('annotation_type_id',condition=annotation_type_condition,
                    hasDownArrow=True,width='15em',**annotation_type_kwargs)
        fb.field('description',tag='simpleTextArea')
        topbc.contentPane(region='center').dynamicFieldsPane('annotation_fields',margin='2px')

        bc.contentPane(region='center').dialogTableHandler(relation='@orgn_related_actions',
                        formResource='orgn_components:FormActionComponent',
                        viewResource='orgn_components:ViewActionComponent',
                        nodeId='orgn_action_#',
                        form_user_kwargs=user_kwargs,form_type_restriction=type_restriction)

    def orgn_actionForm(self,bc,type_restriction=None,user_kwargs=None):
        action_type_condition = None
        action_type_kwargs = dict()
        if type_restriction:
            action_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            action_type_kwargs = dict(condition_restriction=type_restriction)
        fb = bc.contentPane(region='top').div(margin_right='20px',margin='10px').formbuilder(cols=2, border_spacing='4px',
                                                                                            fld_width='100%',
                                                                                            colswidth='auto',width='100%')
        fb.field('action_type_id',condition=action_type_condition,
                    selected_default_priority='.priority',hasDownArrow=True,
                    colspan=2,
                    selected_default_days_before='.days_before',**action_type_kwargs)
        fb.field('assigned_user_id',validate_notnull='^.assigned_tag?=!#v',#disabled='^.assigned_tag',
                                    validate_onAccept="""if(userChange){
                                                SET .assigned_tag=null;
                                    }""",hasDownArrow=True,**user_kwargs)
        #condition='==allowed_users?allowed_users:"TRUE"',condition_allowed_users='=#FORM.condition_allowed_users'
        fb.field('assigned_tag',condition='$child_count = 0 AND $isreserved IS NOT TRUE',tag='dbselect',
                dbtable='adm.htag',alternatePkey='code',validate_notnull='^.assigned_user_id?=!#v',
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


class FormActionComponent(FormMixedComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'
    def th_form(self, form):
        type_restriction = form._current_options['type_restriction']
        user_kwargs = form._current_options['user_kwargs'] or dict()
        self.orgn_actionForm(form.center.borderContainer(),type_restriction=type_restriction,user_kwargs=user_kwargs)

class ViewMixedComponent(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('typename')
        r.fieldcell('assigned_to')
        r.fieldcell('priority')
        r.fieldcell('days_before')
        #r.fieldcell('log_id')

    def th_order(self):
        return 'typename'

    def th_query(self):
        return dict(column='typename', op='contains', val='')

    def th_sections_orgn(self):
        return [dict(code='all',caption='!!All'),
                dict(code='orgn',caption='!!To do',condition='$done_ts IS NULL'),
                dict(code='done',caption='!!Done',condition='$done_ts IS NOT NULL')]


class ViewActionComponent(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('typename')
        r.fieldcell('assigned_to')
        r.fieldcell('priority')
        r.fieldcell('days_before')
        #r.fieldcell('log_id')

    def th_order(self):
        return 'typename'

    def th_query(self):
        return dict(column='typename', op='contains', val='')

    def th_sections_orgn(self):
        return [dict(code='all',caption='!!All'),
                dict(code='orgn',caption='!!To do',condition='$done_ts IS NULL'),
                dict(code='done',caption='!!Done',condition='$done_ts IS NOT NULL')]

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


