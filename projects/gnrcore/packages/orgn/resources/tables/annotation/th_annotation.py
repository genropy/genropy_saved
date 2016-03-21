#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

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

class ActionPluginForm(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        fb = bc.contentPane(region='top').formbuilder(cols=2,border_spacing='3px')

        #fb.field('action_type_id',condition=action_type_condition,
        #            selected_default_priority='.priority',hasDownArrow=True,
        #            colspan=2,
        #            selected_default_notice_days='.notice_days',
        #            validate_notnull='^.rec_type?=#v=="AC"',**action_type_kwargs)
        #fb.field('assigned_user_id',#disabled='^.assigned_tag',
        #                            validate_onAccept="""if(userChange){
        #                                        SET .assigned_tag=null;
        #                            }""",hasDownArrow=True,**user_kwargs)
        ##condition='==allowed_users?allowed_users:"TRUE"',condition_allowed_users='=#FORM.condition_allowed_users'
        #fb.field('assigned_tag',condition='$child_count = 0 AND $isreserved IS NOT TRUE',tag='dbselect',
        #        dbtable='adm.htag',alternatePkey='code',
        #        validate_onAccept="""if(userChange){
        #                            SET .assigned_user_id=null;
        #                        }""",hasDownArrow=True)
        fb.field('date_due')
        fb.field('time_due')
        fb.field('description',tag='simpleTextArea',colspan=2,width='100%')
        fb.field('priority')
        fb.field('notice_days')
        bc.contentPane(region='center').dynamicFieldsPane('action_fields',margin='2px')

    def th_options(self):
        return dict(dialog_height='300px',dialog_width='600px',form_add=False,form_delete=False)


