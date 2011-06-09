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
from gnr.core.gnrlang import extract_kwargs

class TableHandler(BaseComponent):
    """Main class of th"""
    js_requires = 'th/th'
    css_requires= 'th/th'
    py_requires='th/th_view:TableHandlerView,th/th_form:TableHandlerForm,th/th_lib:TableHandlerCommon,th/th:ThLinker'

    
    def _th_mangler(self,pane,table,nodeId=None):
        tableCode = table.replace('.','_')
        th_root = nodeId or '%s_%i' %(tableCode,id(pane.parentNode))
        return th_root
    
    @extract_kwargs(condition=True,grid=True)
    def __commonTableHandler(self,pane,nodeId=None,th_pkey=None,table=None,relation=None,datapath=None,viewResource=None,
                            formInIframe=False,reloader=None,virtualStore=False,condition=None,condition_kwargs=None,
                            default_kwargs=None,grid_kwargs=None,hiderMessage=None,pageName=None,readOnly=False,tag=None,**kwargs):
        if relation:
            table,condition = self._th_relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    default_kwargs=default_kwargs,**kwargs)
        tableCode = table.replace('.','_')
        th_root = self._th_mangler(pane,table,nodeId=nodeId)
        viewCode='V_%s' %th_root
        formCode='F_%s' %th_root   
        wdg = pane.child(tag=tag,datapath=datapath or '.%s'%tableCode,
                        thlist_root=viewCode,
                        thform_root=formCode,
                        nodeId=nodeId,
                        table=table,
                        **kwargs)
        message= hiderMessage or '!!Save the main record to use this pane.'
        wdg.dataController("""
                            if(pkey=='*newrecord*'){
                                sourceNode.setHiderLayer({message:message});
                            }else{
                                sourceNode.setHiderLayer(null,true);
                            }
                            """,pkey='=#FORM.pkey',sourceNode=wdg,message=message,_fired='^#FORM.controller.loaded')                
        top_slots = '#,delrow,addrow'
        if readOnly:
            top_slots = '#'
        wdg.tableViewer(frameCode=viewCode,th_pkey=th_pkey,table=table,pageName=pageName,viewResource=viewResource,
                                reloader=reloader,virtualStore=virtualStore,top_slots=top_slots,
                                condition=condition,condition_kwargs=condition_kwargs,grid_kwargs=grid_kwargs)    
        return wdg
    
    @extract_kwargs(dialog=True,default=True)
    @struct_method
    def th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,dialog_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs):
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,reloader=reloader,
                                        tag='ContentPane',default_kwargs=default_kwargs,readOnly=readOnly,**kwargs)        
        form = pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,loadEvent='onRowDblClick',
                               form_locked=True,dialog_kwargs=dialog_kwargs,attachTo=pane,formInIframe=formInIframe,
                               formResource=formResource,default_kwargs=default_kwargs,readOnly=readOnly)     
        return pane
    
    @extract_kwargs(palette=True,default=True)
    @struct_method
    def th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,palette_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs):
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,
                                        formInIframe=formInIframe,reloader=reloader,
                                        default_kwargs=default_kwargs,
                                        tag='ContentPane',readOnly=readOnly,**kwargs)        
        palette_kwargs = palette_kwargs
        form = pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,
                                formResource=formResource,
                                loadEvent='onRowDblClick',form_locked=True,
                                palette_kwargs=palette_kwargs,attachTo=pane,default_kwargs=default_kwargs,
                                readOnly=readOnly)     
        return pane

    @extract_kwargs(widget=True,vpane=True,fpane=True,default=True)
    @struct_method
    def th_borderTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,loadEvent='onSelected',
                            readOnly=False,viewRegion=None,formRegion=None,vpane_kwargs=None,fpane_kwargs=None,**kwargs):
        kwargs['tag'] = 'BorderContainer'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,reloader=reloader,
                                        default_kwargs=default_kwargs,readOnly=readOnly,**kwargs)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent=loadEvent,form_locked=True,
                        default_kwargs=default_kwargs,formInIframe=formInIframe,readOnly=readOnly)   
        wdg.form.top.bar.replaceSlots('|,dismiss','') 
        wdg.form.top.bar.replaceSlots('navigation,|','') 

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
                            formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs):
        kwargs['tag'] = 'StackContainer'
        kwargs['selectedPage'] = '^.selectedPage'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,reloader=reloader,default_kwargs=default_kwargs,
                                        pageName='view',readOnly=readOnly,**kwargs)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,pageName='form',formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent='onRowDblClick',form_locked=True,default_kwargs=default_kwargs,
                        formInIframe=formInIframe,readOnly=readOnly)    
        return wdg
        
    @extract_kwargs(default=True)
    @struct_method
    def th_pageTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,formUrl=None,viewResource=None,
                            formInIframe=False,reloader=None,default_kwargs=None,**kwargs):
        kwargs['tag'] = 'ContentPane'
        th = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,reloader=reloader,
                                        default_kwargs=default_kwargs,
                                        **kwargs)
        grid = th.view.grid
        table = table or th.attributes['table']
        formUrl = formUrl or '/sys/thpage/%s' %table.replace('.','/')
        fakeFormId ='%s_form' %th.attributes['thform_root']
        grid.attributes.update(connect_onRowDblClick="""FIRE .editrow = this.widget.rowIdByIndex($1.rowIndex);""",
                                selfsubscribe_addrow="FIRE .editrow = '*newrecord*';")
        grid.dataController("""
            if(!this._pageHandler){
                this._pageHandler = new gnr.pageTableHandlerJS(this,_formId,mainpkey,formUrl,default_kwargs,formResource);
            }
            this._pageHandler.checkMainPkey(mainpkey);
            if(pkey){
                this._pageHandler.openPage(pkey);
            }
        """,formUrl=formUrl,formResource=formResource,pkey='^.editrow',_formId=fakeFormId,
           default_kwargs=default_kwargs,_fakeform=True,mainpkey='^#FORM.pkey')
        return th    
        
    @struct_method
    def th_plainTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,reloader=None,readOnly=True,**kwargs):
        kwargs['tag'] = 'ContentPane'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,reloader=reloader,
                                        readOnly=readOnly,**kwargs)
        return wdg    
        
    @struct_method
    def th_thIframe(self,pane,method=None,src=None,**kwargs):
        pane.attributes.update(dict(overflow='hidden',_lazyBuild=True))
        pane = pane.contentPane(detachable=True,height='100%',_class='detachablePane')
        box = pane.div(_class='detacher',z_index=30)
        kwargs = dict([('main_%s' %k,v) for k,v in kwargs.items()])
        iframe = box.iframe(main='th_iframedispatcher',main_methodname=method,main_pkey='=#FORM.pkey',src=src,**kwargs)
        pane.dataController('genro.publish({iframe:"*",topic:"frame_onChangedPkey"},{pkey:pkey})',pkey='^#FORM.pkey')
        return iframe
         
    def rpc_th_iframedispatcher(self,root,methodname=None,pkey=None,**kwargs):
        rootattr = root.attributes
        rootattr['datapath'] = 'main'
        rootattr['overflow'] = 'hidden'
        rootattr['_fakeform'] = True
        rootattr['subscribe_frame_onChangedPkey'] = 'SET .pkey=$1.pkey; FIRE .controller.loaded;'
        root.dataController('SET .pkey = pkey; FIRE .controller.loaded;',pkey=pkey,_onStart=True)
        getattr(self,'iframe_%s' %methodname)(root,**kwargs)

class ThLinker(BaseComponent):
    @extract_kwargs(dialog=True,default=True)
    @struct_method 
    def th_linker(self,pane,field=None,formResource=None,formUrl=None,newRecordOnly=None,table=None,
                    openIfNew=None,embedded=True,dialog_kwargs=None,default_kwargs=None,**kwargs):
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
        joiner = tblobj.model.relations.getAttr('@'+field, 'joiner')[0]
        if 'one_one' in joiner:
            one_one = joiner['one_one']
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
            linker.div(_class='th_linkerAdd',tip='^.tip_add' ,childname='addbutton',
                        connect_onclick="this.getParentNode().publish('newrecord')")
            linker.attributes.update(_embedded=False)
            embedded = False
            openIfNew = True if openIfNew is None else openIfNew
        if openIfNew:
            linker.attributes.update(_class='==newrecord?"th_enableLinker th_linker": "th_linker"',
                                      newrecord='^#FORM.record?_newrecord')
        if newRecordOnly:
            linker.attributes.update(visible='^#FORM.record?_newrecord')
        linker.field('%s.%s' %(table,field),childname='selector',datapath='#FORM.record',
                    connect_onBlur='this.getParentNode().publish("disable");',
                    _class='th_linkerField',background='white',**kwargs)
        return linker
    
    @struct_method 
    def th_linkerBox(self,pane,field=None,template='default',frameCode=None,formResource=None,newRecordOnly=None,openIfNew=None,_class='pbl_roundedGroup',label=None,**kwargs):
        frameCode= frameCode or 'linker_%s' %field.replace('.','_')
        frame = pane.framePane(frameCode=frameCode,_class=_class)
        linkerBar = frame.top.linkerBar(field=field,formResource=formResource,newRecordOnly=newRecordOnly,openIfNew=openIfNew,label=label,**kwargs)
        linker = linkerBar.linker
        currpkey = '^#FORM.record.%s' %field
        frame.div(template=self.tableTemplate(linker.attributes['table'],template),
                    datasource='^.@%s' %field,visible=currpkey,margin='4px')
        footer = frame.bottom.slotBar('*,linker_edit')
        footer.linker_edit.slotButton('Edit current record',baseClass='no_background',iconClass='icnBaseWrite',
                                       action='linker.publish("loadrecord");',linker=linker,showLabel=False,
                                       visible=currpkey,margin='2px',parentForm=True)
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


