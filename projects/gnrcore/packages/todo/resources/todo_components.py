# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs

class FormActionComponent(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'
    def th_form(self, form):
        action_types = form._current_options['action_types']
        user_kwargs = form._current_options['user_kwargs'] or dict()
        if isinstance(action_types,basestring):
            action_types = action_types.split(',')
        action_type_condition = '$child_count = 0'
        action_type_kwargs = dict()
        if action_types:
            action_type_condition_list = []
            tbl_action_type = self.db.table('todo.action_type')
            for t in action_types:
                action_type_condition_list.append(" ( $hierarchical_pkey LIKE :type_%s)" %t)
                action_type_kwargs['condition_type_%s' %t] = '%s%%'  %tbl_action_type.sysRecord(t)['id']
                action_type_condition = '%s AND ( %s )' %(action_type_condition,' OR '.join(action_type_condition_list))

        bc = form.center.borderContainer(datapath='.record')
        fb = bc.contentPane(region='top').div(margin_right='20px',margin='10px').formbuilder(cols=2, border_spacing='4px',colswidth='auto',width='100%')
        fb.field('action_type_id',condition=action_type_condition,
                    selected_default_priority='.priority',hasDownArrow=True,
                    selected_default_days_before='.days_before',colspan=2,**action_type_kwargs)
        fb.field('assigned_user_id',validate_notnull='^.assigned_tag?=!#v',#disabled='^.assigned_tag',
                        validate_onAccept="""if(userChange){
                                                SET .assigned_tag=null;
                                        }""",hasDownArrow=True,**user_kwargs)
        #condition='==allowed_users?allowed_users:"TRUE"',condition_allowed_users='=#FORM.condition_allowed_users'
        fb.field('assigned_tag',tag='hdbselect',dbtable='adm.htag',alternatePkey='code',
            validate_notnull='^.assigned_user_id?=!#v',#disabled='^.assigned_user_id',
            validate_onAccept="""if(userChange){
                                    SET .assigned_user_id=null;
                                }""")

        fb.field('priority')
        fb.field('days_before')
        fb.field('description',tag='simpleTextArea',colspan=2,width='450px')
        bc.contentPane(region='center').dynamicFieldsPane('action_fields',margin='2px')

    def th_options(self):
        return dict(dialog_height='300px', dialog_width='550px')


class todoActionsTableHandler(BaseComponent):
    py_requires='th/th:TableHandler'
    @extract_kwargs(user=True)
    @struct_method
    def td_todoActionsTableHandler(self,pane,action_types=None,user_kwargs=None,**kwargs):
        pid = id(pane)
        pane.dialogTableHandler(relation='@todoactions',nodeId='todoactions_%s' %pid,datapath='#FORM.todoactions_%s' %pid,
                                            formResource='todo_components:FormActionComponent',
                                            form_action_types=action_types,
                                            form_user_kwargs=user_kwargs,
                                            **kwargs)


