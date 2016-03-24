# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method,metadata
from datetime import datetime,timedelta

class FormMixedComponent(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'
    def th_form(self, form):
        linked_entity = form._current_options['linked_entity']
        user_kwargs = form._current_options['user_kwargs'] or dict()
        default_kwargs = form.store.handler('load').attributes.get('default_kwargs')

        sc = form.center.stackContainer(selectedPage='^.record.rec_type')
        self.orgn_annotationForm(sc.borderContainer(pageName='AN'),linked_entity=linked_entity,user_kwargs=user_kwargs,
                                sub_action_default_kwargs=default_kwargs)
        self.orgn_actionForm(sc.borderContainer(pageName='AC'),linked_entity=linked_entity,user_kwargs=user_kwargs,
                                                                default_kwargs=default_kwargs)

    def orgn_annotationForm(self,bc,linked_entity=None,user_kwargs=None,sub_action_default_kwargs=None):
        annotation_type_condition=None
        annotation_type_kwargs = dict()
        action_type_condition = None
        action_type_kwargs = dict()
        if linked_entity:
            annotation_type_condition = "$reserved IS NOT TRUE AND (CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            annotation_type_kwargs = dict(condition_restriction=linked_entity)
            action_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            action_type_kwargs = dict(condition_restriction=linked_entity)
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
            r.cell('_date_due_from_pivot',calculated=True,hidden=True)
            r.fieldcell('action_type_id',edit=dict(condition=action_type_condition,
                    selected_default_priority='.priority',hasDownArrow=True,**action_type_kwargs))
            r.fieldcell('assigned_tag',edit=dict(condition='$child_count = 0 AND $isreserved IS NOT TRUE',tag='dbselect',
                dbtable='adm.htag',alternatePkey='code',validate_notnull='=#ROW.assigned_user_id?=!#v',
                validate_onAccept="""if(value){this.setCellValue("assigned_user_id",null)}""",
                hasDownArrow=True),editLazy='=#ROW.assigned_user_id',width='7em')
            r.fieldcell('assigned_user_id',
                         edit=dict(hasDownArrow=True,
                                  validate_notnull='=#ROW.assigned_tag?=!#v',
                                  validate_onAccept="""if(value){this.setCellValue("assigned_tag",null)}""",
                                  **user_kwargs),
                         editLazy='=#ROW.assigned_tag',width='9em')
            r.fieldcell('priority',edit=True,width='6em')
            r.fieldcell('date_due',edit=True,width='7em',
                        _customGetter="""function(row){
                                            return row['date_due'] || '<div class="dimmed">'+_F(row['_date_due_from_pivot'])+'</div>'
                                         }""")
            r.fieldcell('notice_days',edit=True,width='4em')
        th = bc.contentPane(region='center').inlineTableHandler(title='!!Actions',relation='@orgn_related_actions',
                        viewResource='orgn_components:ViewActionComponent',
                        view_structCb=following_actions_struct,searchOn=False,
                        nodeId='orgn_action_#',
                        form_user_kwargs=user_kwargs,default_rec_type='AC',
                        **dict([('default_%s' %k,v) for k,v in sub_action_default_kwargs.items()]))
        rpc = bc.dataRpc('dummy',self.orgn_getDefaultActionsRows,annotation_type_id='^#FORM.record.annotation_type_id',
                        _if='annotation_type_id&&_is_newrecord',_is_newrecord='=#FORM.controller.is_newrecord',**sub_action_default_kwargs)
        rpc.addCallback("""if(result){
                                grid.gridEditor.addNewRows(result)
                            }""",grid = th.view.grid.js_widget)          

    def orgn_actionForm(self,bc,linked_entity=None,user_kwargs=None,default_kwargs=None):
        action_type_condition = None
        action_type_kwargs = dict()
        if linked_entity:
            action_type_condition = "(CASE WHEN $restrictions IS NOT NULL THEN :restriction = ANY(string_to_array($restrictions,',')) ELSE TRUE END)"
            action_type_kwargs = dict(condition_restriction=linked_entity)
        fb = bc.contentPane(region='top',datapath='.record').div(margin_right='20px',margin='10px').formbuilder(cols=2, border_spacing='4px',
                                                                                            fld_width='100%',
                                                                                            colswidth='auto',width='100%')
        fb.field('action_type_id',condition=action_type_condition,
                    selected_default_priority='.priority',
                    hasDownArrow=True,
                    colspan=2,
                    validate_notnull='^.rec_type?=#v=="AC"',**action_type_kwargs)
        fb.field('assigned_user_id',#disabled='^.assigned_tag',
                    validate_notnull='^.$assiged_user_id_mandatory',
                    validate_onAccept="""if(userChange && value){
                                                SET .assigned_tag=null;
                                    }""",hasDownArrow=True,**user_kwargs)

        #condition='==allowed_users?allowed_users:"TRUE"',condition_allowed_users='=#FORM.condition_allowed_users'
        fb.field('assigned_tag',condition='$child_count = 0 AND $isreserved IS NOT TRUE',tag='dbselect',
                validate_notnull='^.$assigned_tag_mandatory',
                dbtable='adm.htag',alternatePkey='code',
                validate_onAccept="""if(userChange && value){
                                    SET .assigned_user_id=null;
                                }""",hasDownArrow=True)
        fb.dataController("""if(rec_type=='AN'){
                SET .$assiged_user_id_mandatory = false;
                SET .$assigned_tag_mandatory = false;
            }else{
                SET .$assiged_user_id_mandatory = !assigned_tag;
                SET .$assigned_tag_mandatory = !assigned_user_id;
            }""",rec_type='^.rec_type',_delay=1,
                        assigned_tag='^.assigned_tag',
                        assigned_user_id='^.assigned_user_id')
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
        bc.contentPane(region='center').dynamicFieldsPane('action_fields',margin='2px')

    def th_options(self):
        return dict(dialog_height='300px', dialog_width='550px',modal=True)

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
            result.append(dict(action_type_id=ac['id'],assigned_tag=ac['default_tag'],priority=ac['default_priority'],
                                _date_due_from_pivot=_date_due_from_pivot))
        return result

class ViewActionComponent(BaseComponent):
    def th_hiddencolumns(self):
        return '$__ins_ts'
    def th_order(self):
        return '__ins_ts'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')


class ViewMixedComponent(BaseComponent):
    def th_hiddencolumns(self):
        return '$__ins_ts,$rec_type,$annotation_background,$annotation_color,$description,$action_description,$rec_type,$done_ts,$action_type_description'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts',name='TS',width='12em')
        r.cell('annotation_template',name='!!About',width='18em',
                rowTemplate="""<div style='background:$annotation_background;color:$annotation_color;border:1px solid $color;text-align:center;border-radius:10px;'>$annotation_caption</div>""")
        r.fieldcell('annotation_caption',hidden=True)
        r.fieldcell('calc_description',width='20em',name='Description')
        r.fieldcell('priority',width='6em')
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

    def th_order(self):
        return '__ins_ts'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')

    def th_bottom_custom(self,bottom):
        bottom.slotToolbar('2,sections@rec_type,*,2')

    @public_method
    def th_applymethod(self,selection):
        def cb(row):
            _customClasses=['orgn_%s' %row['rec_type']]
            return dict(_customClasses=' '.join(_customClasses))
        selection.apply(cb)

class OrganizerComponent(BaseComponent):
    py_requires='th/th:TableHandler'
    css_requires='orgn_components'

    @extract_kwargs(user=True)
    @struct_method
    def td_annotationTableHandler(self,pane,linked_entity=None,user_kwargs=None,configurable=False,nodeId=None,**kwargs):
        pid = id(pane)
        if not linked_entity:
            parentTable = pane.getInheritedAttributes()['table']
            tblobj = self.db.table(parentTable)
            linked_entity = self.db.table('orgn.annotation').linkedEntityName(tblobj)
        formOutcomeId = 'outcomeAction_%s' %pid
        self.actionOutcomeDialog(pane,formId=formOutcomeId)
        th = pane.dialogTableHandler(relation='@annotations',nodeId=nodeId or 'orgn_annotation_%s' %pid,
                                datapath='#FORM.orgn_annotations_%s' %pid,
                                viewResource='orgn_components:ViewMixedComponent',
                                formResource='orgn_components:FormMixedComponent',
                                form_type_restriction=linked_entity,
                                form_user_kwargs=user_kwargs,configurable=configurable,
                                default_linked_entity=linked_entity,
                                form_linked_entity=linked_entity,
                                liveUpdate=True,
                                view_grid_selfsubscribe_do_action="genro.formById('%s').goToRecord($1.pkey);" %formOutcomeId,
                                addrow=[('Annotation',dict(rec_type='AN')),('Action',dict(rec_type='AC'))],
                                **kwargs)
        return th

    def actionOutcomeDialog(self,pane,formId=None):
        pane.thFormHandler(table='orgn.annotation',formResource='ActionOutcomeForm',
                        dialog_height='300px',dialog_width='600px',
                        formId=formId,datapath='#FORM.actionOutcome')

    @struct_method
    def td_annotationTool(self,pane,linked_entity=None,**kwargs):
        pid = id(pane)
        paletteCode='annotation_%s' %pid
        parentTable = pane.getInheritedAttributes()['table']
        tblobj = self.db.table(parentTable)
        joiner = tblobj.relations.getNode('@annotations').attr['joiner']
        pkg,tbl,fkey = joiner['many_relation'].split('.')
        if not linked_entity:
            linked_entity = self.db.table('orgn.annotation').linkedEntityName(tblobj)
        palette = pane.palettePane(paletteCode=paletteCode,title='!!Record annotations',
                                    dockTo='dummyDock',width='730px',height='500px')

        kwargs = dict([('main_%s' %k,v) for k,v in kwargs.items()])
        iframe = palette.iframe(main=self.orgn_remoteAnnotationTool,
                            main_linked_entity=linked_entity,
                            main_table=parentTable,
                            main_pkey='=#FORM.pkey',**kwargs)
        pane.dataController("""
            iframe.domNode.gnr.postMessage(iframe,{topic:'changedMainRecord',pkey:pkey});
            """,iframe=iframe,pkey='^#FORM.controller.loaded')
  
        pane.slotButton('!!See annotations',action="""genro.nodeById("%s_floating").widget.show();""" %paletteCode,
                        hidden='^#FORM.pkey?=#v=="*newrecord*"',iconClass='iconbox comment')

    @public_method
    def orgn_remoteAnnotationTool(self,root,table=None,pkey=None,linked_entity=None,**kwargs):
        rootattr = dict()
        rootattr['datapath'] = 'main'
        rootattr['_fakeform'] = True
        rootattr['table'] = table
        bc = root.borderContainer(**rootattr)
        bc.dataController("SET .pkey=pkey; FIRE .controller.loaded = pkey;",subscribe_changedMainRecord=True)
        if pkey:
            bc.dataController('SET .pkey = pkey; FIRE .controller.loaded=pkey;',pkey=pkey,_onStart=True)
            bc.dataRecord('.record',table,pkey='^#FORM.pkey',_if='pkey')
        th = bc.annotationTableHandler(nodeId='annotationTH',linked_entity=linked_entity,region='center',lockable=True,**kwargs)
        bc.dataController("form.newrecord(default_kw)",form=th.form.js_form,subscribe_newAnnotation=True)

