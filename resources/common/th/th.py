# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from past.builtins import basestring
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrdict import dictExtract

from gnr.core.gnrbag import Bag

class TableHandler(BaseComponent):
    js_requires = 'th/th'
    css_requires= 'th/th'

    py_requires="""th/th_view:TableHandlerView,th/th_tree:TableHandlerHierarchicalView,
                    th/th_stats:TableHandlerStats,th/th_groupth:TableHandlerGroupBy,
                  th/th_form:TableHandlerForm,th/th_lib:TableHandlerCommon,th/th:ThLinker,
                  th/th:MultiButtonForm,th/th:THBusinessIntelligence,
                  gnrcomponents/userobject/userobject_editor:PrintGridEditor
                  """
    
    @extract_kwargs(condition=True,grid=True,view=True,picker=True,export=True,addrowmenu=True,hider=True,preview=True,relation=True)
    def __commonTableHandler(self,pane,nodeId=None,th_pkey=None,table=None,relation=None,datapath=None,viewResource=None,
                            formInIframe=False,virtualStore=False,extendedQuery=None,condition=None,condition_kwargs=None,
                            default_kwargs=None,grid_kwargs=None,pageName=None,readOnly=False,tag=None,
                            lockable=False,pbl_classes=False,configurable=True,groupable=None,hider=True,searchOn=True,count=None,
                            parentFormSave=None,
                            rowStatusColumn=None,
                            picker=None,addrow=True,addrowmenu=None,
                            delrow=True,
                            archive=False,
                            export=False,printRows=False,title=None,
                            addrowmenu_kwargs=None,
                            export_kwargs=None,
                            liveUpdate=None,
                            picker_kwargs=True,subtable=None,
                            dbstore=None,hider_kwargs=None,view_kwargs=None,preview_kwargs=None,parentForm=None,
                            form_kwargs=None,relation_kwargs=None,**kwargs):
        fkeyfield=None
        if relation:
            table,condition,fkeyfield = self._th_relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    relation_kwargs=relation_kwargs,
                                                    default_kwargs=default_kwargs,original_kwargs=kwargs)

        if 'inheritLock' in kwargs:
            view_kwargs['store_inheritLock'] = kwargs['inheritLock']
            form_kwargs['form_inheritLock'] = kwargs.pop('inheritLock')
        if 'inheritProtect' in kwargs:
            view_kwargs['store_inheritProtect'] = kwargs['inheritProtect']
            form_kwargs['form_inheritProtect'] = kwargs.pop('inheritProtect')
        if subtable:
            view_kwargs['store_subtable'] = subtable
        tblobj = self.db.table(table)
        tblattr = tblobj.attributes

        readOnly = readOnly or tblattr.get('readOnly')
        if not self.checkTablePermission(table,'readonly'):
            readOnly = True
        delrow = tblattr.get('deletable',delrow)
        if isinstance(delrow,basestring):
            delrow = self.application.checkResourcePermission(delrow, self.userTags)
        if isinstance(addrow,basestring):
            addrow = self.application.checkResourcePermission(addrow, self.userTags)
        if isinstance(archive,basestring):
            archive = self.application.checkResourcePermission(archive, self.userTags)
        tableCode = table.replace('.','_')
        th_root = self._th_mangler(pane,table,nodeId=nodeId)
        if nodeId is None and th_root in pane.register_nodeId:
            th_root = '{}_{}'.format(th_root,id(pane))
            datapath = datapath or '.{}'.format(th_root)
        viewCode='V_{}'.format(th_root)
        formCode='F_{}'.format(th_root)
        defaultModule = 'th_{}'.format(table.split('.')[1])
        unlinkdict = kwargs.pop('store_unlinkdict',None)
        store_excludeDraft = kwargs.pop('store_excludeDraft',None)
        store_excludeLogicalDeleted = kwargs.pop('store_excludeLogicalDeleted',None)

        if pane.attributes.get('tag') == 'ContentPane':
            pane.attributes['overflow'] = 'hidden'
        wdg = pane.child(tag=tag,datapath=datapath or '.{}'.format(tableCode),
                        thlist_root=viewCode,
                        thform_root=formCode,
                        th_viewResource=self._th_getResourceName(viewResource,defaultClass='View',defaultModule=defaultModule),
                        th_formResource=self._th_getResourceName(kwargs.get('formResource'),defaultClass='Form',defaultModule=defaultModule),
                        table=table,
                        nodeId=th_root,
                        context_dbstore=dbstore,
                        overflow='hidden',
                        **kwargs) 
        top_slots = ['#']   
        addrow_defaults = None  
        if readOnly:
            delrow = False
            addrow =False
            lockable = False  
            picker = False
        if export:
            top_slots.append('export')
        if printRows:
            top_slots.append('printRows')
        if archive:
            top_slots.append('archive')
            
        if delrow:
            top_slots.append('delrow')
        if addrow:
            top_slots.append('addrow')
            if addrow is not True:
                addrow_defaults = addrow

        if picker:
            top_slots.append('thpicker')
            if picker is True:
                picker = tblobj.pkey
                picker_kwargs['table'] = table
                if picker_kwargs.pop('exclude_assigned',None):
                    picker_base_condition = '$%(_fkey_name)s IS NULL' %condition_kwargs 
                else:
                    picker_base_condition = '$%(_fkey_name)s IS NULL OR $%(_fkey_name)s!=:fkey' %condition_kwargs 
                picker_custom_condition = picker_kwargs.get('condition')
                picker_kwargs['condition'] = picker_base_condition if not picker_custom_condition else '(%s) AND (%s)' %(picker_base_condition,picker_custom_condition)
                for k,v in list(condition_kwargs.items()):
                    picker_kwargs['condition_%s' %k] = v
                if delrow:
                    tblname = tblattr.get('name_plural') or tblattr.get('name_one') or tblobj.name
                    unlinkdict = dict(one_name=tblname.lower(),
                                    field=condition_kwargs['_fkey_name'])
            picker_kwargs['relation_field'] = picker

        if addrowmenu:
            top_slots.append('addrowmenu')
            addrowmenu_kwargs['relation_field'] = addrowmenu

        if lockable:
            top_slots.append('viewlocker')

        top_slots = ','.join(top_slots)

        if form_kwargs is not None:
            form_kwargs['dfltoption_readOnly'] = readOnly
            form_kwargs.setdefault('dfltoption_form_add',addrow) 
            form_kwargs.setdefault('dfltoption_form_delete',delrow) 
            form_kwargs.setdefault('dfltoption_form_archive',archive)
            form_kwargs.setdefault('fkeyfield',fkeyfield)
            if fkeyfield:
                form_kwargs.setdefault('excludeCols',fkeyfield)

        if parentFormSave:
            grid_kwargs['_saveNewRecordOnAdd'] = True
            if isinstance(parentFormSave,basestring):
                hider_kwargs.setdefault('message',parentFormSave)
        preview_kwargs.setdefault('tpl',True)
        hasProtectionColumns = self.db.table(table).hasProtectionColumns()
        hasInvalidCheck = self.db.table(table).hasInvalidCheck()

        rowStatusColumn = hasInvalidCheck or hasProtectionColumns if rowStatusColumn is None else rowStatusColumn
        grid_kwargs.setdefault('rowStatusColumn',rowStatusColumn)
        if fkeyfield:
            grid_kwargs.setdefault('excludeCols',fkeyfield)
            
        wdg.tableViewer(frameCode=viewCode,th_pkey=th_pkey,table=table,pageName=pageName,viewResource=viewResource,
                                virtualStore=virtualStore,extendedQuery=extendedQuery,top_slots=top_slots,
                                top_thpicker_picker_kwargs=picker_kwargs,top_export_parameters=export_kwargs,
                                top_addrowmenu_parameters=addrowmenu_kwargs,
                                top_addrow_defaults=addrow_defaults,
                                lockable=lockable,
                                configurable=configurable,groupable=groupable,
                                condition=condition,condition_kwargs=condition_kwargs,
                                count=count,
                                grid_kwargs=grid_kwargs,unlinkdict=unlinkdict,searchOn=searchOn,title=title,
                                preview_kwargs=preview_kwargs,
                                parentForm=parentForm,liveUpdate=liveUpdate,
                                excludeDraft = store_excludeDraft,
                                excludeLogicalDeleted = store_excludeLogicalDeleted,
                                **view_kwargs) 
        hiderRoot = wdg if kwargs.get('tag') == 'BorderContainer' else wdg.view
        if hider:
            wdg.dataController("""
                            var currform = this.getFormHandler();
                            message = message || msg_prefix+' '+ (currform?currform.getRecordCaption():"main record") +' '+ msg_suffix;
                            if(pkey=='*newrecord*'){
                                sourceNode.setHiderLayer(true,{message:message,button:function(){grid.publish('onClickHider');}});
                            }else{
                                sourceNode.setHiderLayer(false);
                            }
                            """,sourceNode=hiderRoot,
                                message=hider_kwargs.get('message') or False,
                                    msg_prefix='!!Save',msg_suffix='',
                                pkey='^#FORM.controller.loaded',grid=wdg.view.grid)   

            wdg.view.grid.attributes.update(selfsubscribe_onClickHider="""
                    if(this.attr._saveNewRecordOnAdd){
                        this.publish('addrow');
                    }else{
                        this.form.save()
                    }
                """)
            if hider_kwargs.get('onChanged'):
                wdg.dataController("""
                            var currform = this.getFormHandler();
                            message = message==true?msg_prefix+' '+ (currform?currform.getRecordCaption():"main record") +' '+ msg_suffix:message;
                            if(changed){
                                sourceNode.setHiderLayer(true,{message:message,button:function(){currform.save();}});
                            }else{
                                sourceNode.setHiderLayer(false);
                            }
                            """,sourceNode=hiderRoot,
                                message=hider_kwargs.get('onChanged'),
                                    msg_prefix='!!Save',msg_suffix='',
                                changed='^#FORM.controller.changed',grid=wdg.view.grid)  

        if pbl_classes:
            wdg.view.attributes.update(_class='pbl_roundedGroup')
            if pbl_classes=='*':
                wdg.view.attributes.update(_class='pbl_roundedGroup noheader')
            wdg.view.top.bar.attributes.update(toolbar=False,_class='slotbar_toolbar pbl_roundedGroupLabel')
            if count is None:
                wdg.view.top.bar.replaceSlots('count','')
        if not self.th_checkPermission(wdg.view) or not self.application.allowedByPreference(**tblattr):
            wdg.attributes['_notallowed'] = True
        return wdg


    def th_checkPermission(self,pane,table=None):
        inattr = pane.getInheritedAttributes()
        table = table or inattr['table']
        if not self.checkTablePermission(table,'hidden'):
            return False
        dflt = self.pageAuthTags(method='main')
        tags = self._th_hook('tags',mangler=pane,dflt=dflt)()
        if tags:
            if not self.application.checkResourcePermission(tags, self.userTags):
                return False
        return True

    @extract_kwargs(dialog=True,default=True,form=True)
    @struct_method
    def th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,dialog_kwargs=None,default_kwargs=None,readOnly=False,form_kwargs=None,**kwargs):
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,handlerType='dialog',
                                        tag='ContentPane',default_kwargs=default_kwargs,readOnly=readOnly,
                                        form_kwargs=form_kwargs,**kwargs)
        form_kwargs.setdefault('form_locked',True)
        pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,loadEvent='onRowDblClick',
                        dialog_kwargs=dialog_kwargs,attachTo=pane,formInIframe=formInIframe,
                        formResource=formResource,default_kwargs=default_kwargs,**form_kwargs)     
        return pane
    
    @extract_kwargs(palette=True,default=True,form=True)
    @struct_method
    def th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,palette_kwargs=None,default_kwargs=None,readOnly=False,form_kwargs=None,**kwargs):
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,
                                        formInIframe=formInIframe,
                                        default_kwargs=default_kwargs,handlerType='palette',
                                        tag='ContentPane',readOnly=readOnly,
                                        form_kwargs=form_kwargs,**kwargs)    
        palette_kwargs = palette_kwargs 
        form_kwargs.setdefault('form_locked',True)
        pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,
                                formResource=formResource,
                                loadEvent='onRowDblClick',
                                palette_kwargs=palette_kwargs,attachTo=pane,default_kwargs=default_kwargs,
                                **form_kwargs)     
        return pane

    @extract_kwargs(widget=True,vpane=True,fpane=True,default=True,form=True)
    @struct_method
    def th_borderTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,widget_kwargs=None,default_kwargs=None,loadEvent='onSelected',
                            readOnly=False,viewRegion=None,formRegion=None,vpane_kwargs=None,fpane_kwargs=None,
                            saveOnChange=False,form_kwargs=None,**kwargs):
        kwargs['tag'] = 'BorderContainer'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,handlerType='border',
                                        default_kwargs=default_kwargs,readOnly=readOnly,
                                        form_kwargs=form_kwargs,**kwargs)
        form_kwargs.setdefault('form_locked',True)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent=loadEvent,
                        default_kwargs=default_kwargs,formInIframe=formInIframe,navigation=False,linker=True,
                        saveOnChange=saveOnChange,**form_kwargs)
        formtop = wdg.form.top  
        if formtop and formtop.bar:
            formtop.bar.replaceSlots('|,dismiss','') 
            formtop.bar.replaceSlots('navigation,|','') 

        def regionAdapter(kw,**defaults):
            defaults.update(kw)
            if (defaults['region'] in ('bottom' ,'top')) and not defaults.get('height'):
                defaults['height'] = '50%'
            if (defaults['region'] in ('left' ,'right')) and not defaults.get('width'):
                defaults['width'] = '50%'
            return defaults
        wdg.view.attributes.update(**regionAdapter(vpane_kwargs,region='top',splitter=True))
        wdg.form.attributes.update(**regionAdapter(fpane_kwargs,region='center'))
        return wdg
        
    @extract_kwargs(widget=True,default=True,form=True)
    @struct_method
    def th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,widget_kwargs=None,default_kwargs=None,
                            readOnly=False,form_kwargs=None,toggleParentToolbar=False,**kwargs):
        kwargs['tag'] = 'StackContainer'
        kwargs['selectedPage'] = '^.selectedPage'
        form_kwargs.setdefault('form_locked',True)
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,default_kwargs=default_kwargs,
                                        pageName='view',readOnly=readOnly,handlerType='stack',
                                        form_kwargs=form_kwargs,**kwargs)
        form = wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,pageName='form',formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent='onRowDblClick',default_kwargs=default_kwargs,
                        formInIframe=formInIframe,**form_kwargs)    
        if toggleParentToolbar:
            form.dataController("""
            var parentForm = this.form.getParentForm();
            if(parentForm && parentForm.sourceNode.widget._top){
                parentForm.sourceNode.widget.setRegionVisible('top',false);
            }
            """, formsubscribe_onLoading=True)
            form.dataController("""
            var parentForm = this.form.getParentForm();
            if(parentForm && parentForm.sourceNode.widget._top){
                parentForm.sourceNode.widget.setRegionVisible('top',true);
            }
            """, formsubscribe_onDismissed=True)
        return wdg
        
    @extract_kwargs(default=True,page=True,form=True)
    @struct_method
    def th_pageTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,formUrl=None,viewResource=None,
                            default_kwargs=None,dbname=None,recyclablePages=None,public=True,main_call=None,form_kwargs=None,**kwargs):
        kwargs['tag'] = 'ContentPane'
        th = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,handlerType='page',
                                        viewResource=viewResource,default_kwargs=default_kwargs,
                                        form_kwargs=form_kwargs,**kwargs)
        grid = th.view.grid
        table = table or th.attributes['table']
        formUrl = formUrl or '/sys/thpage/%s' %table.replace('.','/')
        grid.attributes.update(connect_onRowDblClick="""FIRE .editrow = this.widget.rowIdByIndex($1.rowIndex);""",
                                selfsubscribe_addrow="FIRE .editrow = '*newrecord*';")
        grid.dataController("""
            if(pkey=='*newrecord*' && this.form && this.form.changed && this.form.isNewRecord()){
                var that = this;
                this.form.save({onReload:function(){
                        that.fireEvent('.editrow','*newrecord*');
                    }})
                return;
            }
            var mainpkey = this.form?this.form.getCurrentPkey():null;
            if(!this._pageHandler){
                var th = {formResource:formResource,public:public}
                var kw = {formUrl:formUrl,default_kwargs:default_kwargs,
                          th:th,viewStore:viewStore,recyclablePages:recyclablePages};
                if (main_call){
                    kw['url_main_call'] = main_call;
                }
                
                this._pageHandler = new gnr.pageTableHandlerJS(this,mainpkey,kw);
            }
            this._pageHandler.checkMainPkey(mainpkey);
            if(pkey){
                this._pageHandler.openPage(pkey,dbname);
            }
        """,formUrl=formUrl,formResource=formResource or ':Form',
             pkey='^.editrow',
             formsubscribe_onLoaded=True,
            formsubscribe_onDismissed=True,
           default_kwargs=default_kwargs,_fakeform=True,
           dbname=dbname or False,viewStore=th.view.store,
           recyclablePages=recyclablePages or False,public=public,main_call=main_call or False
           )
        return th
        
    @struct_method
    def th_plainTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,viewResource=None,
                            hider=False,picker=None,addrow=None,delrow=None,height=None,width=None,rowStatusColumn=None,**kwargs):
        kwargs['tag'] = 'ContentPane'
        if picker:
            hider=True
            delrow = True if delrow is None else delrow
            addrow = False if addrow is None else addrow
        if not delrow and rowStatusColumn is None:
            rowStatusColumn = False
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,handlerType='plain',
                                        viewResource=viewResource,hider=hider,rowStatusColumn=rowStatusColumn,
                                        picker=picker,addrow=addrow,delrow=delrow,**kwargs)
        wdg.view.attributes.update(height=height,width=width)
        return wdg

    @extract_kwargs(default=True,page=True)     
    @struct_method
    def th_inlineTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,viewResource=None,
                            readOnly=False,hider=False,saveMethod=None,autoSave=False,statusColumn=None,
                            default_kwargs=None,defaultPrompt=None,semaphore=None,saveButton=None,
                            configurable=False,height=None,width=None,**kwargs):
        """ JBE We must document the parameters here please  """
        kwargs['tag'] = 'ContentPane'
        saveMethod = saveMethod or 'app.saveEditedRows'
        if autoSave:
            semaphore = False if semaphore is None else semaphore
            saveButton = False if saveButton is None else saveButton
            statusColumn = True if statusColumn is None else statusColumn
        else:
            semaphore = False if semaphore is None else semaphore
            saveButton = False if saveButton is None else saveButton
            statusColumn = False if statusColumn is None else statusColumn
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,readOnly=readOnly,hider=hider,handlerType='inline',
                                        default_kwargs=default_kwargs,configurable=configurable,
                                        _foreignKeyFormPath='=#FORM',**kwargs)
        remoteRowController = self._th_hook('remoteRowController',dflt=None,mangler=wdg.view) or None
        options = self._th_hook('options',mangler=wdg.view)() or dict()
        wdg.view.store.attributes.update(recordResolver=False)
        wdg.view.grid.attributes.update(remoteRowController=remoteRowController,
                                        defaultPrompt = defaultPrompt or options.get('defaultPrompt'),
                                        gridEditorPars=dict(saveMethod=saveMethod,
                                                        default_kwargs=default_kwargs,
                                                        autoSave=autoSave or options.get('autoSave'),
                                                        statusColumn=statusColumn or options.get('statusColumn')))

        wdg.view.attributes.update(height=height,width=width)

        if saveButton:
            wdg.view.top.bar.replaceSlots('#','#,gridsave')
        if semaphore:
            wdg.view.top.bar.replaceSlots('#','#,gridsemaphore')
        return wdg
        
        
    @struct_method
    def th_thIframe(self,pane,method=None,src=None,**kwargs):
        pane.attributes.update(dict(overflow='hidden',_lazyBuild=True))
        #pane = pane.contentPane(detachable=True,height='100%',_class='detachablePane')
        #box = pane.div(_class='detacher',z_index=30)
        kwargs = dict([('main_%s' %k,v) for k,v in kwargs.items()])
        iframe = pane.iframe(main='th_iframedispatcher',main_methodname=method,
                            main_table=pane.getInheritedAttributes().get('table'),
                            main_pkey='=#FORM.pkey',
                            src=src,**kwargs)
        pane.dataController('genro.publish({iframe:"*",topic:"frame_onChangedPkey"},{pkey:pkey})',pkey='^#FORM.pkey')
        return iframe

    @struct_method
    def th_externalThForm(self,pane,src=None,aux_instance=None,table=None,pkeyField=None,formResource='Form',**kwargs):
        pane.attributes.update(dict(overflow='hidden',_lazyBuild=True))
        if src:
            src = '%s/sys/thpage/%s?main_call=main_form&th_formResource=%s' %(src,table.replace('.','/'),formResource)
        else:
            src = '/sys/thpage/%s?aux_instance=%s&main_call=main_form&th_formResource=%s' %(table.replace('.','/'),aux_instance,formResource)
        iframe = pane.htmliframe(src=src,height='100%',width='100%',border=0)
        pane.dataController("""
                            if(myiframe.domNode && myiframe.domNode.contentWindow){
                                myiframe.domNode.contentWindow.postMessage({topic:'main_form_open',pkey:pkey},'*')
                            }
                           """,myiframe=iframe,_virtual_column=pkeyField,pkey='^#FORM.record.%s' %pkeyField,
                           _delay=100,**{'subscribe_iframeform_%s_ready' %table.replace('.','_'):True})


    @struct_method
    def th_relatedIframeForm(self,pane,related_field=None,related_table=None,src=None,formResource=None,**kwargs):
        pane.attributes.update(dict(overflow='hidden',_lazyBuild=True))
        pane = pane.contentPane(detachable=True,height='100%',_class='detachablePane')
        box = pane.div(_class='detacher',z_index=30)
        kwargs.setdefault('readOnly',True)
        kwargs.setdefault('showfooter',False)
        kwargs.setdefault('showtoolbar',False)
        kwargs = dict([('main_%s' %k,v) for k,v in list(kwargs.items())])
        table = pane.getInheritedAttributes()['table']
        if not related_table:
            tblobj = self.db.table(table)
            related_tblobj = tblobj.column(related_field).relatedColumn().table    
            related_table = related_tblobj.fullname            
        src = src or '/sys/thpage/%s' %related_table.replace('.','/')
        iframe = box.iframe(main='main_form',main_th_pkey='=#FORM.record.%s' %related_field,
                            src=src,main_th_formResource=formResource,**kwargs)
        pane.dataController('iframe._genro._rootForm.load({destPkey:pkey});',
                            pkey='^#FORM.record.%s' %related_field,iframe=iframe)
        return iframe
        
    @public_method
    def th_iframedispatcher(self,root,methodname=None,pkey=None,table=None,**kwargs):
        rootattr = root.attributes
        rootattr['datapath'] = 'main'
        rootattr['overflow'] = 'hidden'
        rootattr['_fakeform'] = True
        rootattr['table'] = table
        rootattr['subscribe_frame_onChangedPkey'] = 'SET .pkey=$1.pkey; FIRE .controller.loaded = $1.pkey;'
        if pkey:
            root.dataController('SET .pkey = pkey; FIRE .controller.loaded=pkey;',pkey=pkey,_onStart=True)
            root.dataRecord('.record',table,pkey='^#FORM.pkey',_if='pkey')
        handler = self.getPublicMethod('rpc',methodname)
        if handler:
            return handler(root,**kwargs)
        return getattr(self,'iframe_%s' %methodname)(root,**kwargs)

    #USER SETTINGS 
    def th_mainUserSettings(self,kwargs=None):
        table = self.maintable
        defaultModule = 'th_%s' %table.replace('.','_')
        #th_viewResource=self._th_getResourceName(kwargs.get('viewResource'),defaultClass='View',defaultModule=defaultModule)
        th_formResource=self._th_getResourceName(kwargs.get('formResource'),defaultClass='Form',defaultModule=defaultModule)
        settingKey = '%s/%s' %(table,th_formResource)
        settingKey = 'thpref.%s' %settingKey.replace('.','_').replace(':','_')
        currset = self.getUserPreference(path=settingKey,pkg='sys') or Bag()
        widget = currset.getItem('widget') or kwargs.get('widget')
        kwargs['widget'] = widget
        h = '%spx' %(currset['form.height'] or 400)
        w = '%spx' %(currset['form.width'] or 500)
        if widget in ('dialog','palette'):
            kwargs['%s_height' %widget] = h 
            kwargs['%s_width' %widget] = w

    @public_method
    def th_userSetting(self,pane,thkey=None):
        path = 'thpref.%s' %thkey
        datapath = 'gnr.%s' %path
        currpref = self.getUserPreference(path=path,pkg='sys') or Bag()
        currpref['widget'] = currpref['widget'] or 'stack'
        currpref['form.height'] = currpref['form.height'] or 400
        currpref['form.width'] = currpref['form.width'] or 600
        pane.data(datapath,currpref)
        fb = pane.formbuilder(cols=2,border_spacing='3px',datapath=datapath)
        fb.filteringSelect(value='^.widget',lbl='Widget',
                            values='stack:Stack,palette:Palette,dialog:Dialog,border:Border',colspan='2')
        fb.numbertextbox(value='^.form.height',lbl='!!F. height',width='5em',
                        row_hidden='^.widget?=(#v=="stack" || #v=="border")')
        fb.numbertextbox(value='^.form.width',lbl='!!F. width',width='5em')

    @public_method
    def th_saveUserSetting(self,data=None,thkey=None):
        self.db.table('adm.user').setPreference(data=data,path='thpref.%s' %thkey,pkg='sys',username=self.user)


    @public_method
    def th_remoteTableHandler(self,pane,thkwargs=None,**kwargs):
        thkwargs.update(kwargs)
        thwidget=thkwargs.pop('thwidget','plain')
        if thwidget == 'form':
            thkwargs.setdefault('startKey','*newrecord*')
            thkwargs.setdefault('modal',True)
            #fix lock 
            pane.thFormHandler(**thkwargs)
        else:
            thkwargs.setdefault('view_store__onBuilt',True)
            getattr(pane,'%sTableHandler' %thwidget)(**thkwargs)

class MultiButtonForm(BaseComponent):
    @extract_kwargs(condition=True,store=True,multibutton=True,default=True,formhandler=True,form=True)
    @struct_method
    def th_multiButtonForm(self,pane,relation=None,table=None,condition=None,condition_kwargs=None,store_kwargs=None,
                            storepath=None,caption=None,switch=None,
                            multibutton_kwargs=None,formhandler_kwargs=None,form_kwargs=None,
                            frameCode=None,formId=None,formResource=None,
                            default_kwargs=None,modal=True,datapath=None,
                            emptyPageMessage=None,darkToolbar=False,pendingChangesMessage=None,pendingChangesTitle=None,
                            **kwargs):
        if relation:
            table,condition,fkeyfield = self._th_relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    default_kwargs=default_kwargs,original_kwargs=kwargs)
        pane.attributes.update(overflow='hidden')
        frameCode = frameCode or 'fhmb_%s' %table.replace('.','_')
        frame = pane.framePane(frameCode=frameCode,datapath=datapath,**kwargs)
        frameCode = frame.attributes['frameCode'] # frameCode dynamic value
        storepath  = storepath or '.store' 
        store_kwargs['storepath'] = storepath
        store_kwargs.update(condition_kwargs)
        columns = store_kwargs.pop('columns','*')
        tbkw = dict()
        if darkToolbar:
            tbkw = dict(_class='darktoolbar')
        bar = frame.top.slotToolbar('5,mbslot,*',height='20px',**tbkw)
        caption_field = caption or self.db.table(table).attributes['caption_field']
        multibutton_kwargs.setdefault('caption',caption_field)
        self.subscribeTable(table,True)
        mb = bar.mbslot.multibutton(value='^.value',**multibutton_kwargs)
        columnslist = [columns,'$%(caption)s' %multibutton_kwargs]

        if formhandler_kwargs:
            frame.attributes.update(onCreated="""
                    var that = this;
                    this.loadForm = function(kw){
                        var switchValue = objectPop(kw,'switchValue');
                        var destPkey = objectPop(kw,'destPkey') || '*newrecord*';
                        var formpars = that.getRelativeData('.connected_forms').getItem(switchValue);
                        var formId = formpars.getItem('formId');
                        var form = genro.formById(formId)
                        form.load({destPkey:destPkey,default_kw:kw});
                    }
                """)
            sc = frame.center.stackContainer(selectedPage='^.selectedForm')
            emptyPageMessage = emptyPageMessage or '!!No Record Selected'
            sc.contentPane(pageName='emptypage').div(emptyPageMessage,_class='hiderMessage',height='50px',position='absolute',top='25%',left=0,right=0,text_align='center')
            columnslist.append('$%s' %switch)
            switchdict = dict()
            for formId,pars in list(formhandler_kwargs.items()):
                self._th_appendExternalForm(sc,formId=formId,pars=pars,columnslist=columnslist,
                                            switchdict=switchdict,storetable=table,
                                            caption_field=caption_field,frameCode=frameCode,
                                            switch=switch)
            formIdlist = list(formhandler_kwargs.keys())
            bar.dataController("""if(!storebag || storebag.len()==0){
                    SET .pkey = null;
                }
                """,storebag='^%s' %storepath,_delay=1)
            bar.dataController("""
                if(currentFormId && currentFormId!='emptypage'){
                    var currentLoadedForm = genro.formById(currentFormId);
                    if(currentLoadedForm.changed){
                        PUT .value = _triggerpars.kw.oldvalue;
                        genro.dlg.alert(pendingChangesMessage,pendingChangesTitle)
                        return;
                    }else if(currentLoadedForm.parentFormPkey=='*newrecord*'){
                        if(!multiButtonValue){
                            SET .formPkey = '*norecord*';
                        }
                        return;
                    }else if(!multiButtonValue){
                        currentLoadedForm.abort();
                    }
                }else if(!multiButtonValue){
                    SET .formPkey = null;
                }
                if(multiButtonValue!='_newrecord_'){
                    SET .formPkey = multiButtonValue?multiButtonValue:'*norecord*';
                }
                """,
                multiButtonValue='^.value',formIdlist=formIdlist,currentFormId='=.selectedForm',
                pendingChangesTitle=pendingChangesTitle or '!!Operation forbidden',
                pendingChangesMessage=pendingChangesMessage or '!!You cannot change record. The record is not saved')
            bar.dataController("""
                var selectedNode = storebag.getNodeByAttr('_pkey',pkey);
                if(!selectedNode){
                    SET .row = new gnr.GnrBag();
                    return; 
                }
                var record = selectedNode.attr;
                SET .row = new gnr.GnrBag(record);
                """,pkey='^.formPkey',storebag='=%s' %storepath)
            bar.data('.connected_forms',Bag(switchdict))
            bar.dataController("""
                var switchValue = row.getItem(sw);
                var pars = switchdict[switchValue];
                var formId = pars['formId'];
                var pkeyColumn = pars['pkeyColumn'];
                SET .selectedForm = formId;
                var loadPkeyValue = row.getItem(pkeyColumn);
                var relatedForm = genro.formById(formId);
                relatedForm.goToRecord(loadPkeyValue,row.getItem('__mod_ts'));
                """,row='^.row',switchdict=switchdict,
                sw=switch,_if='row && row.getItem("_pkey")')
            frame.dataController("SET .store = new gnr.GnrBag();",formsubscribe_onLoading=True) #it should be done by store itself check better solution
        else:
            formId= formId or '%s_frm' %frameCode
            form = frame.center.contentPane(overflow='hidden').thFormHandler(formResource=formResource,table=table,
                                    default_kwargs=default_kwargs,formId=formId,**form_kwargs)
            frame.form = form
            bar.dataController("""
                if(pkey=='*newrecord*' || pkey=='_newrecord_'){
                    if(!store){
                        store = new gnr.GnrBag();
                        SET .store = store;
                    }
                    kw = {};
                    kw[caption_field] = frm.form.getRecordCaption();
                    kw['_pkey'] = '_newrecord_';
                    store.setItem('_newrecord_',null,kw)
                    pkey = '*newrecord*';
                }else if(store && store.len()>0){
                    store.popNode('_newrecord_');
                }
                frm.form.goToRecord(pkey)
                """,
                pkey='^.value',
                frm=form,_if='pkey',caption_field=caption_field,store='=.store')
            bar.dataController("""
            if(_node.label=='store' && !(store && store.len()>0)){
                SET .value = '*norecord*';
            }
            """,store='^.store',frm=form.js_form)
            form.dataController("""
                if(mb.form){
                    mb.form.childForms[this.form.formId] = this.form;
                }
                mb.setRelativeData('.value',pkey=='*newrecord*'?'_newrecord_':pkey);
                """,pkey='^#FORM.controller.loaded',mb=mb)
            form.dataController("""
                mb.setRelativeData('.value',pkey=='*newrecord*'?'_newrecord_':pkey);
                """,formsubscribe_onCancel=True,mb=mb,pkey='=.pkey')
        store_kwargs['_if'] = store_kwargs.pop('if',None) or store_kwargs.pop('_if',None)
        store_kwargs['_else'] = "this.store.clear(); SET .value = '*norecord*'"
        tblobj = self.db.table(table)
        table_order_by = tblobj.attributes.get('order_by')
        if not table_order_by:
            if tblobj.column('__ins_ts') is not None:
                table_order_by = '$__ins_ts'
            else:
                table_order_by = '$%s' %(tblobj.attributes.get('caption_field') or tblobj.pkey)
        store_kwargs.setdefault('order_by',table_order_by)
        if store_kwargs['order_by']:
            columnslist.append([c.strip() for c in store_kwargs['order_by'].split(' ')][0])
        store_kwargs['columns'] = ','.join(columnslist)
        rpc = mb.store(table=table,condition=condition,**store_kwargs)
        frame.multiButtonView = mb
        return frame


    def _th_appendExternalForm(self,sc,formId=None,pars=None,columnslist=None,switchdict=None,storetable=None,
                                caption_field=None,frameCode=None,switch=None):
        form_kwargs = dictExtract(pars,'form_',pop=True)
        default_kwargs = dictExtract(pars,'default_',pop=True)
        datapath = pars.pop('datapath','.forms.%s' %formId)
        switchValues = pars.pop('switchValues')
        table = pars.pop('table',None) or storetable
        pkeyColumn = pars.pop('pkeyColumn',None) or self.db.table(table).pkey
        if table!=storetable:
            columnslist.append('$%s' %pkeyColumn)
            joiner = self.db.table(table).model.getJoiner(storetable)
            fkey = joiner['many_relation'].split('.')[-1]
        else:
            fkey = pkeyColumn
        for c in switchValues.split(','):
            switchdict[c] = dict(formId=formId,pkeyColumn=pkeyColumn,fkey=fkey,default_kwargs=default_kwargs)
        form = sc.contentPane(pageName=formId,overflow='hidden').thFormHandler(table=table,
                                                                        formResource=pars.pop('formResource','Form'),
                                                                        formId=formId,datapath=datapath,
                                                                        **form_kwargs) 
        form.dataController("""
                            if (pkey=='*newrecord*'){
                                var store = mainstack.getRelativeData('.store');
                                if(!store){
                                    store = new gnr.GnrBag();
                                    mainstack.setRelativeData('.store',store);
                                }
                                kw = {newrecord:true};
                                kw[caption_field] = data.attr.caption;
                                fkey = fkey || '_newrecord_';
                                kw['_pkey'] = fkey;
                                kw[switch_field] = data.getValue().getItem(switch_field);
                                store.setItem(fkey,null,kw)
                            }
                            if(mainstack.form){
                                mainstack.form.childForms[code] = this.form;
                            }
                            mainstack.setRelativeData('.value',fkey);
                            mainstack.setRelativeData('.selectedForm',fid);
                            """,
                            mainstack=sc,fid=formId,caption_field=caption_field,
                            fkey='=#FORM.record.%s' %fkey,code=frameCode,switch_field=switch,
                            formsubscribe_onLoaded=True)     
        form.dataController("""
                mainstack.setRelativeData('.value',fkey);
                mainstack.setRelativeData('.selectedForm',fid);
                """,formsubscribe_onCancel=True,mainstack=sc,fid=formId,
                fkey='=#FORM.record.%s' %fkey)   

class ThLinker(BaseComponent):
    py_requires='gnrcomponents/tpleditor:ChunkEditor'
    @extract_kwargs(dialog=True,default=True)
    @struct_method 
    def th_linker(self,pane,field=None,formResource=None,formUrl=None,newRecordOnly=None,table=None,
                    openIfEmpty=None,embedded=True,excludeLinked=False,dialog_kwargs=None,
                    default_kwargs=None,auxColumns=None,hiddenColumns=None,addEnabled=None,**kwargs):
        fkeyfield = None
        if not table:
            if '.' in field:
                fldlst = field.split('.')
                table = '.'.join(fldlst[0:2])
                field = fldlst[2]
            else:
                inattr = pane.getInheritedAttributes()
                table = inattr.get('table') or self.maintable
                fkeyfield = inattr.get('fkeyfield')
        tblobj = self.db.table(table)
        related_tblobj = tblobj.column(field).relatedColumn().table    
        related_table = related_tblobj.fullname
        joiner = tblobj.model.relations.getAttr('@'+field, 'joiner')
        if 'one_one' in joiner:
            manyrelfld = joiner['relation_name']
            if excludeLinked:    
                noduplinkcondition = '@%s.%s IS NULL OR @%s.%s=:_rec_curr_pkey' %(manyrelfld,tblobj.pkey,manyrelfld,tblobj.pkey)
                condition =  kwargs.get('condition')
                kwargs['condition__rec_curr_pkey'] = '=#FORM.pkey'
                kwargs['condition'] = '%s AND (%s)' %(condition,noduplinkcondition) if condition else noduplinkcondition 
            else:
                pane.dataController("""if(_reason!='container' && this.form.isNewRecord()){
                    var linked_id  = GET #FORM.record.@%s.@%s.%s;
                    if(linked_id && linked_id!=curr_pkey){
                        this.form.reset();
                        this.form.load({destPkey:linked_id});
                    }
                }""" %(field,manyrelfld,tblobj.pkey)
                ,fkey='^#FORM.record.%s' %field,
                    curr_pkey='=#FORM.pkey')
                _customclasscol = """(CASE WHEN @%s.%s IS NOT NUll THEN 'linked_row' ELSE '' END) AS _customclasses_existing""" %(manyrelfld,tblobj.pkey)
                hiddenColumns = _customclasscol if not hiddenColumns else '%s,%s' %hiddenColumns
        linkerpath = '#FORM.linker_%s' %field
        forbudden_dbstore = self.dbstore and (related_tblobj.attributes.get('multidb') or related_tblobj.dbtable.use_dbstores() is False)
        linker = pane.div(_class='th_linker',childname='linker',datapath=linkerpath,
                         rounded=8,tip='!!Select %s' %self._(related_tblobj.name_long),
                         onCreated='this.linkerManager = new gnr.LinkerManager(this);',
                         connect_onclick='this.linkerManager.openLinker();',
                         selfsubscribe_disable='this.linkerManager.closeLinker();',
                         selfsubscribe_newrecord='this.linkerManager.newrecord();',
                         selfsubscribe_loadrecord='this.linkerManager.loadrecord();',
                         _forbudden_dbstore = forbudden_dbstore,
                         table=related_table,_field=field,_embedded=embedded,
                         _formUrl=formUrl,_formResource=formResource,
                         _dialog_kwargs=dialog_kwargs,_default_kwargs=default_kwargs)
        if kwargs.get('validate_notnull'):
            openIfEmpty = True
        if (formResource or formUrl) and addEnabled is not False:
            add = linker.div(_class='th_linkerAdd',tip=related_tblobj.dbtable.newRecordCaption(),childname='addbutton',
                        connect_onclick="this.getParentNode().publish('newrecord')",hidden=forbudden_dbstore)
            if addEnabled and not forbudden_dbstore:
                pane.dataController("genro.dom.toggleVisible(add,addEnabled);",addEnabled=addEnabled,add=add)
            linker.attributes.update(_embedded=False)
            embedded = False
            openIfEmpty = True if openIfEmpty is None else openIfEmpty
        if openIfEmpty:
            pane.dataController("""
                                   linker.linkerManager.openLinker(false);""",linker=linker,
                                currvalue='^#FORM.record.%s' %field,_if='!currvalue',
                                _else='linker.linkerManager.closeLinker()')          
        selectvisible = None
        if newRecordOnly:
            selectvisible = '^#FORM.record?_newrecord'
        if fkeyfield==field:
            selectvisible = False
        if selectvisible is not None:
            linker.attributes.update(visible=selectvisible)
        linker.field('%s.%s' %(table,field),childname='selector',datapath='#FORM.record',
                    connect_onBlur='this.getParentNode().publish("disable");',
                    _class='th_linkerField',background='white',auxColumns=auxColumns,hiddenColumns=hiddenColumns,
                    lbl=False,**kwargs)
        return linker
        
    @extract_kwargs(template=True)
    @struct_method 
    def th_linkerBox(self,pane,field=None,template='default',frameCode=None,formResource=None,
                    formUrl=None,newRecordOnly=None,openIfEmpty=None,
                    _class='pbl_roundedGroup',label=None,template_kwargs=None,
                    margin=None, editEnabled=True, addEnabled=True, 
                    clientTemplate=False,center_class=None, **kwargs):
        frameCode= frameCode or 'linker_%s' %field.replace('.','_')
        if pane.attributes.get('tag') == 'ContentPane':
            pane.attributes['overflow'] = 'hidden'
        frame = pane.framePane(frameCode=frameCode,_class=_class,margin=margin)
        linkerBar = frame.top.linkerBar(field=field,
                                        formResource=formResource,
                                        formUrl=formUrl,
                                        newRecordOnly=newRecordOnly,
                                        openIfEmpty=openIfEmpty,
                                        addEnabled=addEnabled,
                                        label=label,
                                        **kwargs)
        linker = linkerBar.linker
        currpkey = '^#FORM.record.%s' %field
        center_class = center_class or 'linkerCenter'
        table = linker.attributes['table']
        related_tblobj = self.db.table(table)
        if clientTemplate:
            template = frame.center.contentPane(_class=center_class).templateChunk(template=template,table=table,
                                      datasource='^.@%s' %field,
                                      visible=currpkey,margin='4px',
                                      **template_kwargs)
        else:
            template = frame.center.contentPane(_class=center_class).templateChunk(template=template,table=table,
                                      record_id='^.%s' %field,
                                      visible=currpkey,margin='4px',
                                      **template_kwargs)
        
        forbudden_dbstore = self.dbstore and (related_tblobj.attributes.get('multidb') or related_tblobj.use_dbstores() is False)
        if editEnabled and formResource or formUrl:
            footer = frame.bottom.slotBar('*,linker_edit',height='20px')
            footer.linker_edit.slotButton('Edit',baseClass='no_background',iconClass='iconbox pencil',
                                            action='linker.publish("loadrecord");',linker=linker,
                                            forbudden_dbstore=forbudden_dbstore,hidden=forbudden_dbstore,
                                            visible=currpkey,parentForm=True)
        return frame

    @struct_method          
    def th_linkerBar(self,pane,field=None, label=None, _class='pbl_roundedGroupLabel',newRecordOnly=True, addEnabled=None, **kwargs):
        bar = pane.slotBar('lbl,*,linkerslot,5',height='20px',_class=_class)
        linker = bar.linkerslot.linker(field=field,newRecordOnly=newRecordOnly, addEnabled=addEnabled, **kwargs)
        bar.linker = linker
        label = label or self.db.table(linker.attributes['table']).name_long
        bar.lbl.div(label)
        return bar

    @struct_method          
    def th_thIframeDialog(self,pane,**kwargs):
        return pane.child('ThIframeDialog',**kwargs)

    @struct_method          
    def th_thIframePalette(self,pane,**kwargs):
        return pane.child('ThIframePalette',**kwargs)

class THBusinessIntelligence(BaseComponent):
    
    @struct_method
    def th_viewLinkedDashboard(self,view,nodeId=None,**kwargs):
        if not self.db.package('biz'):
            return
        self.mixinComponent('dashboard_component/dashboard_component:DashboardGallery')
        linkedTo=view.attributes.get('frameCode')
        table = view.grid.attributes.get('table')
        #frameCode = '%s_biz_analyzer' %linkedTo
        kwargs.setdefault('region','bottom')
        kwargs.setdefault('height','40%')
        kwargs.setdefault('closable','close')
        kwargs.setdefault('margin','2px')
        kwargs.setdefault('splitter',True)
        kwargs.setdefault('border_top','1px solid #efefef')
        parent = view.grid_envelope
        pkg,tbl = table.split('.')
        dashboardGalleryId = nodeId or '%s_dashboardGallery' %linkedTo
        parent.dataController("""var kw = {};
                            kw[table.replace('.','_')+'_pkey'] = selectedPkeys;
                            genro.nodeById(dashboardGalleryId).publish('updatedChannels',kw)""",
                            selectedPkeys='^.grid.currentSelectedPkeys',
                            dashboardGalleryId=dashboardGalleryId,table=table,tablepkey=self.db.table(table).pkey)
        parent.dashboardGallery(pkg=pkg,code=linkedTo,nodeId=dashboardGalleryId,from_table=table,**kwargs)

    @struct_method
    def th_formLinkedDashboard(self,parent,code=None,nodeId=None,**kwargs):
        if not self.db.package('biz'):
            return
        self.mixinComponent('dashboard_component/dashboard_component:DashboardGallery')
        inattr = parent.getInheritedAttributes()
        formId = inattr['formId']
        table = inattr['table']
        pkg,tbl = table.split('.')
        dashboardGalleryId = nodeId or  '%s_dashboardGallery' %formId
        parent.dataController("""var kw = {};
                            kw[table.replace('.','_')+'_pkey'] = pkey;
                            genro.nodeById(dashboardGalleryId).publish('updatedChannels',kw)
                            """,
                            pkey='^#FORM.controller.loaded',
                            dashboardGalleryId=dashboardGalleryId,table=table,tablepkey=self.db.table(table).pkey)
        parent.dashboardGallery(pkg=pkg,code=code or formId,nodeId=dashboardGalleryId,from_table=inattr['table'],
                                from_pkey='=#FORM.pkey',**kwargs)
