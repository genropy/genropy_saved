# -*- coding: UTF-8 -*-
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

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method

from gnr.core.gnrbag import Bag

class TableHandler(BaseComponent):
    js_requires = 'th/th'
    css_requires= 'th/th'

    py_requires='th/th_view:TableHandlerView,th/th_tree:TableHandlerHierarchicalView,th/th_form:TableHandlerForm,th/th_lib:TableHandlerCommon,th/th:ThLinker'
    
    @extract_kwargs(condition=True,grid=True,view=True,picker=True,export=True,addrowmenu=True,hider=True,preview=True)
    def __commonTableHandler(self,pane,nodeId=None,th_pkey=None,table=None,relation=None,datapath=None,viewResource=None,
                            formInIframe=False,virtualStore=False,extendedQuery=None,condition=None,condition_kwargs=None,
                            default_kwargs=None,grid_kwargs=None,pageName=None,readOnly=False,tag=None,
                            lockable=False,pbl_classes=False,configurable=True,hider=True,searchOn=True,count=None,
                            parentFormSave=None,
                            rowStatusColumn=None,
                            picker=None,addrow=True,addrowmenu=None,delrow=True,export=False,title=None,
                            addrowmenu_kwargs=None,
                            export_kwargs=None,
                            liveUpdate=None,
                            picker_kwargs=True,
                            dbstore=None,hider_kwargs=None,view_kwargs=None,preview_kwargs=None,parentForm=None,
                            form_kwargs=None,**kwargs):
        if relation:
            table,condition = self._th_relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    default_kwargs=default_kwargs,original_kwargs=kwargs)
        readOnly = readOnly or self.db.table(table).attributes.get('readOnly')
        if form_kwargs:
            form_kwargs['readOnly'] = readOnly
        tableCode = table.replace('.','_')
        th_root = self._th_mangler(pane,table,nodeId=nodeId)
        viewCode='V_%s' %th_root
        formCode='F_%s' %th_root

        defaultModule = 'th_%s' %tableCode
        
        unlinkdict = kwargs.pop('store_unlinkdict',None)

        if pane.attributes.get('tag') == 'ContentPane':
            pane.attributes['overflow'] = 'hidden'
        wdg = pane.child(tag=tag,datapath=datapath or '.%s'%tableCode,
                        thlist_root=viewCode,
                        thform_root=formCode,
                        th_viewResource=self._th_getResourceName(viewResource,defaultClass='View',defaultModule=defaultModule),
                        th_formResource=self._th_getResourceName(kwargs.get('formResource'),defaultClass='Form',defaultModule=defaultModule),
                        nodeId=th_root,
                        table=table,
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
        if delrow:
            top_slots.append('delrow')
        if addrow:
            top_slots.append('addrow')
            if addrow is not True:
                addrow_defaults = addrow

        if picker:
            top_slots.append('thpicker')
            picker_kwargs['relation_field'] = picker
        if addrowmenu:
            top_slots.append('addrowmenu')
            addrowmenu_kwargs['relation_field'] = addrowmenu

        if lockable:
            top_slots.append('viewlocker')

        top_slots = ','.join(top_slots)
        if parentFormSave:
            grid_kwargs['_saveNewRecordOnAdd'] = True
            if isinstance(parentFormSave,basestring):
                hider_kwargs.setdefault('message',parentFormSave)
        preview_kwargs.setdefault('tpl',True)
        rowStatusColumn = self.db.table(table).attributes.get('protectionColumn') if rowStatusColumn is None else rowStatusColumn
        grid_kwargs.setdefault('rowStatusColumn',rowStatusColumn)
        wdg.tableViewer(frameCode=viewCode,th_pkey=th_pkey,table=table,pageName=pageName,viewResource=viewResource,
                                virtualStore=virtualStore,extendedQuery=extendedQuery,top_slots=top_slots,
                                top_thpicker_picker_kwargs=picker_kwargs,top_export_parameters=export_kwargs,
                                top_addrowmenu_parameters=addrowmenu_kwargs,
                                top_addrow_defaults=addrow_defaults,
                                lockable=lockable,
                                configurable=configurable,
                                condition=condition,condition_kwargs=condition_kwargs,
                                grid_kwargs=grid_kwargs,unlinkdict=unlinkdict,searchOn=searchOn,title=title,
                                preview_kwargs=preview_kwargs,
                                parentForm=parentForm,liveUpdate=liveUpdate,
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
        if not self.th_checkPermission(wdg.view):
            wdg.attributes['_notallowed'] = True
        return wdg


    def th_checkPermission(self,pane):
        tags = self._th_hook('tags',mangler=pane,dflt='user')()
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
                            formInIframe=False,widget_kwargs=None,default_kwargs=None,readOnly=False,form_kwargs=None,**kwargs):
        kwargs['tag'] = 'StackContainer'
        kwargs['selectedPage'] = '^.selectedPage'
        form_kwargs.setdefault('form_locked',True)
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,default_kwargs=default_kwargs,
                                        pageName='view',readOnly=readOnly,handlerType='stack',
                                        form_kwargs=form_kwargs,**kwargs)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,pageName='form',formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent='onRowDblClick',default_kwargs=default_kwargs,
                        formInIframe=formInIframe,**form_kwargs)    
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
        if rowStatusColumn is None:
            rowStatusColumn = delrow is True
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,handlerType='plain',
                                        viewResource=viewResource,hider=hider,rowStatusColumn=rowStatusColumn,
                                        picker=picker,addrow=addrow,delrow=delrow,**kwargs)
        wdg.view.attributes.update(height=height,width=width)
        return wdg

    @extract_kwargs(default=True,page=True)     
    @struct_method
    def th_inlineTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,viewResource=None,
                            readOnly=False,hider=False,saveMethod=None,autoSave=False,statusColumn=None,
                            default_kwargs=None,semaphore=None,saveButton=None,configurable=False,height=None,width=None,**kwargs):
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
                                        foreignKeyGetter='=#FORM.pkey',**kwargs)
        remoteRowController = self._th_hook('remoteRowController',dflt=None,mangler=wdg.view) or None
        options = self._th_hook('options',mangler=wdg.view)() or dict()
        wdg.view.store.attributes.update(recordResolver=False)
        wdg.view.grid.attributes.update(remoteRowController=remoteRowController,
                                        gridEditor=dict(saveMethod=saveMethod,
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
        iframe = pane.iframe(main=self.th_iframedispatcher,main_methodname=method,
                            main_table=pane.getInheritedAttributes().get('table'),
                            main_pkey='=#FORM.pkey',src=src,**kwargs)
        pane.dataController('genro.publish({iframe:"*",topic:"frame_onChangedPkey"},{pkey:pkey})',pkey='^#FORM.pkey')
        return iframe
    

    @struct_method
    def th_relatedIframeForm(self,pane,related_field=None,related_table=None,src=None,formResource=None,**kwargs):
        pane.attributes.update(dict(overflow='hidden',_lazyBuild=True))
        pane = pane.contentPane(detachable=True,height='100%',_class='detachablePane')
        box = pane.div(_class='detacher',z_index=30)
        kwargs.setdefault('readOnly',True)
        kwargs.setdefault('showfooter',False)
        kwargs.setdefault('showtoolbar',False)
        kwargs = dict([('main_%s' %k,v) for k,v in kwargs.items()])
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
        rootattr['subscribe_frame_onChangedPkey'] = 'SET .pkey=$1.pkey; FIRE .controller.loaded;'
        if pkey:
            root.dataController('SET .pkey = pkey; FIRE .controller.loaded=pkey;',pkey=pkey,_onStart=True)
            root.dataRecord('.record',table,pkey='^#FORM.pkey',_if='pkey')
        getattr(self,'iframe_%s' %methodname)(root,**kwargs)

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

class ThLinker(BaseComponent):
    py_requires='gnrcomponents/tpleditor:ChunkEditor'
    @extract_kwargs(dialog=True,default=True)
    @struct_method 
    def th_linker(self,pane,field=None,formResource=None,formUrl=None,newRecordOnly=None,table=None,
                    openIfEmpty=None,embedded=True,excludeLinked=False,dialog_kwargs=None,
                    default_kwargs=None,auxColumns=None,hiddenColumns=None,addEnabled=None,**kwargs):
        if not table:
            if '.' in field:
                fldlst = field.split('.')
                table = '.'.join(fldlst[0:2])
                field = fldlst[2]
            else:
                table = pane.getInheritedAttributes().get('table') or self.maintable
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
        linker = pane.div(_class='th_linker',childname='linker',datapath=linkerpath,
                         rounded=8,tip='^.tip_link',
                         onCreated='this.linkerManager = new gnr.LinkerManager(this);',
                         connect_onclick='this.linkerManager.openLinker();',
                         selfsubscribe_disable='this.linkerManager.closeLinker();',
                         selfsubscribe_newrecord='this.linkerManager.newrecord();',
                         selfsubscribe_loadrecord='this.linkerManager.loadrecord();',
                         table=related_table,_field=field,_embedded=embedded,
                         _formUrl=formUrl,_formResource=formResource,
                         _dialog_kwargs=dialog_kwargs,_default_kwargs=default_kwargs)
        linker.dataController("""SET .tip_link =linktpl.replace('$table1',t1).replace('$table2',t2);
                                 SET .tip_add = addtpl.replace('$table2',t2);""",
                            _init=True,linktpl='!!Link current $table1 record to an existing record of $table2',
                            addtpl='!!Add a new $table2',
                            t1=tblobj.name_long, t2=related_tblobj.name_long)        
        if (formResource or formUrl) and addEnabled is not False:
            add = linker.div(_class='th_linkerAdd',tip='^.tip_add',childname='addbutton',
                        connect_onclick="this.getParentNode().publish('newrecord')")
            if addEnabled:
                pane.dataController("genro.dom.toggleVisible(add,addEnabled);",addEnabled=addEnabled,add=add)
            linker.attributes.update(_embedded=False)
            embedded = False
            openIfEmpty = True if openIfEmpty is None else openIfEmpty
        if openIfEmpty:
            pane.dataController("linker.linkerManager.openLinker(false);",linker=linker,
                                currvalue='^#FORM.record.%s' %field,_if='!currvalue',_else='linker.linkerManager.closeLinker()')          
        if newRecordOnly:
            linker.attributes.update(visible='^#FORM.record?_newrecord')
        linker.field('%s.%s' %(table,field),childname='selector',datapath='#FORM.record',
                    connect_onBlur='this.getParentNode().publish("disable");',
                    _class='th_linkerField',background='white',auxColumns=auxColumns,hiddenColumns=hiddenColumns,**kwargs)
        return linker
        
    @extract_kwargs(template=True)
    @struct_method 
    def th_linkerBox(self,pane,field=None,template='default',frameCode=None,formResource=None,formUrl=None,newRecordOnly=None,openIfEmpty=None,
                    _class='pbl_roundedGroup',label=None,template_kwargs=None,margin=None,editEnabled=True,clientTemplate=False,**kwargs):
        frameCode= frameCode or 'linker_%s' %field.replace('.','_')
        if pane.attributes.get('tag') == 'ContentPane':
            pane.attributes['overflow'] = 'hidden'
        frame = pane.framePane(frameCode=frameCode,_class=_class,margin=margin)
        linkerBar = frame.top.linkerBar(field=field,formResource=formResource,formUrl=formUrl,newRecordOnly=newRecordOnly,openIfEmpty=openIfEmpty,label=label,**kwargs)
        linker = linkerBar.linker
        currpkey = '^#FORM.record.%s' %field
        if clientTemplate:
            template = frame.templateChunk(template=template,table=linker.attributes['table'],
                                      datasource='^.@%s' %field,
                                      visible=currpkey,margin='4px',
                                      **template_kwargs)
        else:
            template = frame.templateChunk(template=template,table=linker.attributes['table'],
                                      record_id='^.%s' %field,
                                      visible=currpkey,margin='4px',
                                      **template_kwargs)
        if editEnabled and formResource or formUrl:
            footer = frame.bottom.slotBar('*,linker_edit')
            footer.linker_edit.slotButton('Edit',baseClass='no_background',iconClass='iconbox pencil',
                                            action='linker.publish("loadrecord");',linker=linker,
                                            visible=currpkey,parentForm=True)
        return frame

    @struct_method          
    def th_linkerBar(self,pane,field=None,label=None,table=None,_class='pbl_roundedGroupLabel',newRecordOnly=True,**kwargs):
        bar = pane.slotBar('lbl,*,linkerslot,5',height='20px',_class=_class)
        linker = bar.linkerslot.linker(field=field,newRecordOnly=newRecordOnly,**kwargs)
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


