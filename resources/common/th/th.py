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

class TableHandler(BaseComponent):
    js_requires = 'th/th'
    css_requires= 'th/th'
    py_requires='th/th_view:TableHandlerView,th/th_form:TableHandlerForm,th/th_lib:TableHandlerCommon,th/th:ThLinker'
    
    
    @extract_kwargs(condition=True,grid=True)
    def __commonTableHandler(self,pane,nodeId=None,th_pkey=None,table=None,relation=None,datapath=None,viewResource=None,
                            formInIframe=False,virtualStore=False,extendedQuery=None,condition=None,condition_kwargs=None,
                            default_kwargs=None,grid_kwargs=None,hiderMessage=None,pageName=None,readOnly=False,tag=None,
                            lockable=False,pbl_classes=False,configurable=True,hider=True,**kwargs):
        if relation:
            table,condition = self._th_relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    default_kwargs=default_kwargs,original_kwargs=kwargs)
        tableCode = table.replace('.','_')
        th_root = self._th_mangler(pane,table,nodeId=nodeId)
        viewCode='V_%s' %th_root
        formCode='F_%s' %th_root
        
        unlinkdict = kwargs.pop('store_unlinkdict',None)
        wdg = pane.child(tag=tag,datapath=datapath or '.%s'%tableCode,
                        thlist_root=viewCode,
                        thform_root=formCode,
                        nodeId=th_root,
                        table=table,
                        **kwargs)               
        top_slots = '#,delrow,addrow'
        if lockable:
            top_slots = '#,delrow,addrow,10,viewlocker'
        if readOnly:
            top_slots = '#'
        wdg.tableViewer(frameCode=viewCode,th_pkey=th_pkey,table=table,pageName=pageName,viewResource=viewResource,
                                virtualStore=virtualStore,extendedQuery=extendedQuery,top_slots=top_slots,lockable=lockable,
                                configurable=configurable,
                                condition=condition,condition_kwargs=condition_kwargs,grid_kwargs=grid_kwargs,unlinkdict=unlinkdict) 
        hiderRoot = wdg if kwargs.get('tag') == 'BorderContainer' else wdg.view
        if hider:
            wdg.dataController("""
                            var currform = this.getFormHandler();
                            message = message || msg_prefix+' '+ (currform?currform.getRecordCaption():"main record") +' '+ msg_suffix;
                            if(pkey=='*newrecord*'){
                                sourceNode.setHiderLayer(true,{message:message,button:'this.getFormHandler().save();'});
                            }else{
                                sourceNode.setHiderLayer(false);
                            }
                            """,sourceNode=hiderRoot,message=hiderMessage or False,msg_prefix='!!Save',msg_suffix='',
                                pkey='^#FORM.controller.loaded')    
        if pbl_classes:
            wdg.view.attributes.update(_class='pbl_roundedGroup')
            wdg.view.top.bar.attributes.update(toolbar=False,_class='slotbar_toolbar pbl_roundedGroupLabel')
            wdg.view.top.bar.replaceSlots('vtitle','vtitle')
            wdg.view.top.bar.replaceSlots('count','')

        return wdg
    
    @extract_kwargs(dialog=True,default=True)
    @struct_method
    def th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,dialog_kwargs=None,default_kwargs=None,readOnly=False,**kwargs):
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,
                                        tag='ContentPane',default_kwargs=default_kwargs,readOnly=readOnly,**kwargs)     
        dialog_kwargs.setdefault('height','400px')   
        dialog_kwargs.setdefault('width','600px')   
        pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,loadEvent='onRowDblClick',
                               form_locked=True,dialog_kwargs=dialog_kwargs,attachTo=pane,formInIframe=formInIframe,
                               formResource=formResource,default_kwargs=default_kwargs,readOnly=readOnly)     
        return pane
    
    @extract_kwargs(palette=True,default=True)
    @struct_method
    def th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,palette_kwargs=None,default_kwargs=None,readOnly=False,**kwargs):
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,
                                        formInIframe=formInIframe,
                                        default_kwargs=default_kwargs,
                                        tag='ContentPane',readOnly=readOnly,**kwargs)        
        palette_kwargs = palette_kwargs
        palette_kwargs.setdefault('height','400px')   
        palette_kwargs.setdefault('width','600px')  
        pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,
                                formResource=formResource,
                                loadEvent='onRowDblClick',form_locked=True,
                                palette_kwargs=palette_kwargs,attachTo=pane,default_kwargs=default_kwargs,
                                readOnly=readOnly)     
        return pane

    @extract_kwargs(widget=True,vpane=True,fpane=True,default=True)
    @struct_method
    def th_borderTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,widget_kwargs=None,default_kwargs=None,loadEvent='onSelected',
                            readOnly=False,viewRegion=None,formRegion=None,vpane_kwargs=None,fpane_kwargs=None,**kwargs):
        kwargs['tag'] = 'BorderContainer'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,
                                        default_kwargs=default_kwargs,readOnly=readOnly,**kwargs)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent=loadEvent,form_locked=True,
                        default_kwargs=default_kwargs,formInIframe=formInIframe,readOnly=readOnly,navigation=False,linker=True)
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
        
    @extract_kwargs(widget=True,default=True)
    @struct_method
    def th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,widget_kwargs=None,default_kwargs=None,readOnly=False,**kwargs):
        kwargs['tag'] = 'StackContainer'
        kwargs['selectedPage'] = '^.selectedPage'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,default_kwargs=default_kwargs,
                                        pageName='view',readOnly=readOnly,**kwargs)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,pageName='form',formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent='onRowDblClick',form_locked=True,default_kwargs=default_kwargs,
                        formInIframe=formInIframe,readOnly=readOnly)    
        return wdg
        
    @extract_kwargs(default=True,page=True)
    @struct_method
    def th_pageTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,formUrl=None,viewResource=None,
                            default_kwargs=None,dbname=None,recyclablePages=None,public=True,main_call=None,**kwargs):
        kwargs['tag'] = 'ContentPane'
        th = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,default_kwargs=default_kwargs,**kwargs)
        grid = th.view.grid
        table = table or th.attributes['table']
        formUrl = formUrl or '/sys/thpage/%s' %table.replace('.','/')
        grid.attributes.update(connect_onRowDblClick="""FIRE .editrow = this.widget.rowIdByIndex($1.rowIndex);""",
                                selfsubscribe_addrow="FIRE .editrow = '*newrecord*';")
        grid.dataController("""
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
             mainpkey='^#FORM.pkey',
           default_kwargs=default_kwargs,_fakeform=True,
           dbname=dbname or False,viewStore=th.view.store,
           recyclablePages=recyclablePages or False,public=public,main_call=main_call or False
           )
        return th    
        
    @struct_method
    def th_plainTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,viewResource=None,
                            readOnly=True,hider=False,**kwargs):
        kwargs['tag'] = 'ContentPane'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,readOnly=readOnly,hider=hider,**kwargs)
        return wdg

    @extract_kwargs(default=True,page=True)     
    @struct_method
    def th_inlineTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,viewResource=None,
                            readOnly=False,hider=False,saveMethod=None,autoSave=True,statusColumn=None,
                            default_kwargs=None,semaphore=None,saveButton=None,**kwargs):
        kwargs['tag'] = 'ContentPane'
        saveMethod = saveMethod or 'app.saveEditedRows'
        if autoSave:
            semaphore = False if semaphore is None else semaphore
            saveButton = False if saveButton is None else saveButton
            statusColumn = True if statusColumn is None else statusColumn
        else:
            semaphore = True if semaphore is None else semaphore
            saveButton = False if saveButton is None else saveButton
            statusColumn = False if statusColumn is None else statusColumn
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,readOnly=readOnly,hider=hider,
                                        default_kwargs=default_kwargs,**kwargs)
        wdg.view.store.attributes.update(recordResolver=False)
        wdg.view.grid.attributes.update(gridEditor=dict(saveMethod=saveMethod,default_kwargs=default_kwargs,autoSave=autoSave,statusColumn=statusColumn))
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

class ThLinker(BaseComponent):
    py_requires='gnrcomponents/tpleditor:ChunkEditor'
    @extract_kwargs(dialog=True,default=True)
    @struct_method 
    def th_linker(self,pane,field=None,formResource=None,formUrl=None,newRecordOnly=None,table=None,
                    openIfEmpty=None,embedded=True,dialog_kwargs=None,default_kwargs=None,**kwargs):
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
            noduplinkcondition = '@%s.%s IS NULL' %(manyrelfld,tblobj.pkey)
            condition =  kwargs.get('condition')
            kwargs['condition'] = '%s AND (%s)' %(condition,noduplinkcondition) if condition else noduplinkcondition                  
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
        if formResource or formUrl:
            linker.div(_class='th_linkerAdd',tip='^.tip_add',childname='addbutton',
                        connect_onclick="this.getParentNode().publish('newrecord')")
            linker.attributes.update(_embedded=False)
            embedded = False
            openIfEmpty = True if openIfEmpty is None else openIfEmpty
        if openIfEmpty:
            pane.dataController("genro.dom.setClass(linker,'th_enableLinker',!currvalue)",linker=linker.js_domNode,currvalue='^#FORM.record.%s' %field)          
        if newRecordOnly:
            linker.attributes.update(visible='^#FORM.record?_newrecord')
        linker.field('%s.%s' %(table,field),childname='selector',datapath='#FORM.record',
                    connect_onBlur='this.getParentNode().publish("disable");',
                    _class='th_linkerField',background='white',**kwargs)
        return linker
        
    @extract_kwargs(template=True)
    @struct_method 
    def th_linkerBox(self,pane,field=None,template='default',frameCode=None,formResource=None,formUrl=None,newRecordOnly=None,openIfEmpty=None,
                    _class='pbl_roundedGroup',label=None,template_kwargs=None,**kwargs):
        frameCode= frameCode or 'linker_%s' %field.replace('.','_')
        frame = pane.framePane(frameCode=frameCode,_class=_class)
        linkerBar = frame.top.linkerBar(field=field,formResource=formResource,formUrl=formUrl,newRecordOnly=newRecordOnly,openIfEmpty=openIfEmpty,label=label,**kwargs)
        linker = linkerBar.linker
        currpkey = '^#FORM.record.%s' %field
        template = frame.templateChunk(template=template,table=linker.attributes['table'],
                                      datasource='^.@%s' %field,visible=currpkey,margin='4px',
                                      **template_kwargs)
        if formResource or formUrl:
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


