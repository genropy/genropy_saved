# -*- coding: utf-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method


class OrganizerComponent(BaseComponent):
    py_requires='th/th:TableHandler'
    css_requires='orgn_components'

    @extract_kwargs(user=True)
    @struct_method
    def td_annotationTableHandler(self,pane,linked_entity=None,user_kwargs=None,configurable=True,
                                parentForm=False,nodeId=None,viewResource=None,formResource=None,**kwargs):
        pid = id(pane)
        if not linked_entity:
            parentTable = pane.getInheritedAttributes()['table']
            tblobj = self.db.table(parentTable)
            linked_entity = self.db.table('orgn.annotation').linkedEntityName(tblobj)
        formOutcomeId = 'outcomeAction_%s' %pid
        self.actionOutcomeDialog(pane,formId=formOutcomeId)
        pars = dict(relation='@annotations',nodeId=nodeId or 'orgn_annotation_%s' %pid,
                                datapath='#FORM.orgn_annotations_%s' %pid,
                                viewResource=viewResource or 'ViewMixedComponent',
                                form_type_restriction=linked_entity,
                                form_user_kwargs=user_kwargs,configurable=configurable,
                                default_linked_entity=linked_entity,
                                form_linked_entity=linked_entity,
                                liveUpdate=True,parentForm=parentForm,
                                form_form_parentLock=False if parentForm is False else None,
                                view_grid_canSort=False,
                                view_grid_selfsubscribe_do_action="genro.formById('%s').goToRecord($1.pkey);" %formOutcomeId,
                                )
        pars.update(kwargs)
        if formResource is False:
            th = pane.plainTableHandler(**pars)
        else:
            th = pane.dialogTableHandler(formResource=formResource or 'FormMixedComponent',addrow=[('Annotation',dict(rec_type='AN')),('Action',dict(rec_type='AC'))],**pars)
        return th

    def actionOutcomeDialog(self,pane,formId=None):
        pane.thFormHandler(table='orgn.annotation',formResource='ActionOutcomeForm',
                        dialog_height='350px',dialog_width='600px',
                        formId=formId,datapath='#FORM.actionOutcome')

    @struct_method
    def td_annotationTool(self,pane,linked_entity=None,table=None,height=None,width=None,**kwargs):
        pid = id(pane)
        paletteCode='annotation_%s' %pid
        parentTable = table or pane.getInheritedAttributes()['table']
        tblobj = self.db.table(parentTable)
        joiner = tblobj.relations.getNode('@annotations').attr['joiner']
        pkg,tbl,fkey = joiner['many_relation'].split('.')
        if not linked_entity:
            linked_entity = self.db.table('orgn.annotation').linkedEntityName(tblobj)
        palette = pane.palettePane(paletteCode=paletteCode,title='!!Record annotations',
                                    dockTo='dummyDock',width=width or '730px',height=height or '500px')

        kwargs = dict([('main_%s' %k,v) for k,v in list(kwargs.items())])
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
        th = bc.annotationTableHandler(nodeId='annotationTH',linked_entity=linked_entity,
                                        region='center',lockable=True,**kwargs)
        bc.dataController("form.newrecord(default_kw)",form=th.form.js_form,subscribe_newAnnotation=True)


