# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrbag import Bag


class OrganizerComponent(BaseComponent):
    py_requires='th/th:TableHandler'
    css_requires='orgn_components'
    js_requires='orgn_components'

    def onMain_orgn_quickAnnotationDialog(self):
        if not hasattr(self,'_orgn_quick_annotation_dlg'):
            page = self.pageSource()
            self._orgn_quick_annotation_dlg =  page.thFormHandler(table='orgn.annotation',
                        formResource='QuickAnnotationForm',
                        dialog_height='350px',dialog_width='600px',
                        formId='orgn_quick_annotation',
                        datapath='gnr.orgn.quick_annotation')


    @extract_kwargs(user=True)
    @struct_method
    def td_annotationTableHandler(self,pane,linked_entity=None,user_kwargs=None,configurable=True,
                                parentForm=False,nodeId=None,viewResource=None,formResource=None,
                                thwidget=None,**kwargs):
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
            thwidget = thwidget or 'stack'
            th = getattr(pane,'%sTableHandler' %thwidget)(formResource=formResource or 'FormMixedComponent',addrow=[('Annotation',dict(rec_type='AN')),('Action',dict(rec_type='AC'))],**pars)
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

    @struct_method
    def td_gridAnnotationTool(self,pane,linked_entity=None,table=None,height=None,width=None,**kwargs):
        pid = id(pane)
        paletteCode='annotation_%s' %pid
        parentTable = table or pane.getInheritedAttributes()['table']
        tblobj = self.db.table(parentTable)
        joiner = tblobj.relations.getNode('@annotations').attr['joiner']
        pkg,tbl,fkey = joiner['many_relation'].split('.')
        if not linked_entity:
            linked_entity = self.db.table('orgn.annotation').linkedEntityName(tblobj)
        palette = pane.palettePane(paletteCode=paletteCode,title='!!Row annotations',
                                    dockTo='dummyDock',width=width or '730px',height=height or '500px')

        kwargs = dict([('main_%s' %k,v) for k,v in kwargs.items()])
        iframe = palette.iframe(main=self.orgn_remoteAnnotationTool,
                            main_linked_entity=linked_entity,
                            main_table=parentTable,
                            main_pkey='=.grid.selectedId',
                            **kwargs)
        pane.dataController("""
            iframe.domNode.gnr.postMessage(iframe,{topic:'changedMainRecord',pkey:pkey});
            """,iframe=iframe,pkey='^.grid.selectedId')
        
        pane.slotButton('!!See annotations',action="""genro.nodeById("%s_floating").widget.show();""" %paletteCode,
                        hidden='^.grid.selectedId?=!#v',iconClass='iconbox comment')

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
        bc.annotationTableHandler(nodeId='annotationTH',linked_entity=linked_entity,
                                        region='center',lockable=True,**kwargs)

    @struct_method
    def td_quickAnnotationTool(self,pane,linked_entity=None,table=None,height=None,width=None,**kwargs):
        parentTable = table or pane.getInheritedAttributes()['table']
        tblobj = self.db.table(parentTable)
        joiner = tblobj.relations.getNode('@annotations').attr['joiner']
        pkg,tbl,fkey = joiner['many_relation'].split('.')
        if not linked_entity:
            linked_entity = self.db.table('orgn.annotation').linkedEntityName(tblobj)
        pane.dataRemote('.annotation_type_menu',self.orgn_getAnnotationTypes,
                        cacheTime=120,entity=linked_entity)
        pane.menudiv(storepath='.annotation_type_menu',iconClass='comment',tip='!!Add annotation',
                        action='FIRE .new_annotation = $1.pkey;', disabled='^.grid.selectedId?=!#v')
        pane.dataController(""" var kw = {annotation_type_id:annotation_type_id,entity:entity};
                                kw[fkey] = entity_id;
                                genro.orgn.newQuickAnnotation(kw);""",
                                annotation_type_id='^.new_annotation',
                                entity_id='=.grid.selectedId',entity=linked_entity,fkey=fkey)

    @public_method
    def orgn_getAnnotationTypes(self,entity=None):
        result = Bag()
        tblobj = self.db.table('orgn.annotation_type')
        caption_field = tblobj.attributes['caption_field']
        fetch = tblobj.query(columns='*,$%s' %(caption_field),where="""
            ($__syscode IS NULL OR $__syscode NOT IN :system_annotations) AND
            (CASE WHEN $restrictions IS NOT NULL THEN :entity = ANY(string_to_array($restrictions,','))  ELSE TRUE END)
            """,entity=entity,system_annotations=tblobj.systemAnnotations()).fetch()
        for i,r in enumerate(fetch):
            result.setItem('r_%i' %i,None,caption=r[caption_field],pkey=r['pkey'])
        return result