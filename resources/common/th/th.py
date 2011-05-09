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
    py_requires='th/th_view:TableHandlerView,th/th_form:TableHandlerForm,th/th_lib:TableHandlerCommon'

    @extract_kwargs(condition=True,grid=True)
    def __commonTableHandler(self,pane,nodeId=None,th_pkey=None,table=None,relation=None,datapath=None,viewResource=None,
                            formInIframe=False,reloader=None,virtualStore=False,condition=None,condition_kwargs=None,
                            default_kwargs=None,grid_kwargs=None,hiderMessage=None,pageName=None,readOnly=False,tag=None,**kwargs):
        if relation:
            table,condition = self._th_relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    default_kwargs=default_kwargs,**kwargs)
        tableCode = table.replace('.','_')
        th_root = nodeId or '%s_%i' %(tableCode,id(pane.parentNode))
        listCode='L_%s' %th_root
        formCode='F_%s' %th_root   
        wdg = pane.child(tag=tag,datapath=datapath or '.%s'%tableCode,
                        thlist_root=listCode,
                        thform_root=formCode,
                        nodeId=nodeId,
                        table=table,
                        **kwargs)
        message= hiderMessage or '!!Save the main record to use this pane.'
        wdg.dataController("""
                            genro.bp(pkey);
                            if(pkey=='*newrecord*'){
                                hider = sourceNode.setHiderLayer({message:message});
                            }else{
                                sourceNode.setHiderLayer(null,true);
                            }
                            """,pkey='^#FORM.pkey',sourceNode=wdg,message=message)                
        top_slots = '#,delrow,addrow'
        if readOnly:
            top_slots = '#'
        wdg.tableViewer(frameCode=listCode,th_pkey=th_pkey,table=table,pageName=pageName,viewResource=viewResource,
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
        
    @extract_kwargs(widget=True,default=True)
    @struct_method
    def th_plainTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=True,**kwargs):
        kwargs['tag'] = 'ContentPane'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,reloader=reloader,
                                        default_kwargs=default_kwargs,readOnly=readOnly,**kwargs)
        return wdg


    @extract_kwargs(default=True,condition=True)
    @struct_method   
    def th_linker(self,pane,field=None,label=None,resource=None,formResource=None,pageUrl=None,
                        frameCode=None,condition=None,default_kwargs=None,condition_kwargs=None,**kwargs):
        maintable = pane.getInheritedAttributes().get('table') or self.maintable
        maintableobj = self.db.table(maintable)
        column = maintableobj.column(field)
        label = label or column.name_long
        table = column.relatedColumn().table.fullname
        tableCode = table.replace('.','_')
        frameCode = frameCode or '%s_%i' %(tableCode,id(pane.parentNode))
        self._th_mixinResource(frameCode,table=table,resourceName=resource,defaultClass='Linker')  
        formResource = formResource or self._th_hook('formResource',mangler=frameCode)()
        frame = pane.framePane(frameCode=frameCode,_class='pbl_roundedGroup', **kwargs)
        top = frame.top
        top.attributes.update(_class='pbl_roundedGroupLabel')
        linkerpath = '#FORM.linkers.%s' %frameCode
        top = top.stackContainer(datapath=linkerpath)
        top.dataController('console.log(pkey);sc.widget.switchPage(pkey?0:1);',
                        pkey='^#FORM.record.%s' %field,sc=top)
        readBar = top.contentPane(childname='read').slotBar('label,*,write',label=label)
        readBar.write.slotButton('!!Write',iconClass='icnBaseWrite',showLabel=False,baseClass='no_background',
                                    action='sc.widget.switchPage(1)',sc=top)
    
        writeBar = top.contentPane(childname='write').slotBar('label,selector,add,edit,*,back',label=label)
        writeBar.selector.field(column.fullname,datapath='#FORM.record',lbl=None,**self._th_hook('fieldOptions',mangler=frameCode,dflt=dict())())
        
        palette = pane.palette(dockTo='dummyDock',title='^.title',
                               datapath=linkerpath,**self._th_hook('dialog',mangler=frameCode)())
                               
        pageUrl = pageUrl or self._th_hook('pageUrl',mangler=frameCode,dflt='/sys/thpage/%s' %table.replace('.','/'))() 
        iframe = palette.div(height='100%',width='100%',_lazyBuild=True,overflow='hidden').iframe(src=pageUrl,main='form',main_th_linker=True,main_th_pkey='=#FORM.record.%s' %field)
        writeBar.add.slotButton('!!Add',action="FIRE .pkey='*newrecord*';",iconClass='icnBaseAdd',
                                showLabel=False,baseClass='no_background')
        writeBar.edit.slotButton('!!Edit',action='if(currPkey){FIRE .pkey=currPkey;}',
                                iconClass='icnBaseEdit',showLabel=False,baseClass='no_background',
                                currPkey='=#FORM.record.%s' %field,visible='^#FORM.record.%s' %field)
        writeBar.dataController(""" palette = palette.widget; 
                                    palette.show(); palette.bringToTop();
                                    if(!iframeNode.domNode){
                                        return;
                                    }
                                    iframeNode = iframeNode.domNode;
                                    var loadKw= {default_kw:default_kwargs,destPkey:pkey};
                                    iframeNode.contentWindow.genro.publish('external_load',loadKw);
                                   """,
                                    pkey="^.pkey",palette=palette,iframeNode=iframe,default_kwargs=default_kwargs)
                                    
        writeBar.back.slotButton('!!Cancel',iconClass='icnTabClose',showLabel=False,baseClass='no_background',
                                action='sc.widget.switchPage(0)',sc=top)        
                                
                                
        frame.div(innerHTML='==dataTemplate(_tpl,_data)',_data='^#FORM.record.@%s' %field,
                  _tpl=self._th_hook('template',mangler=frameCode)())

        
    @struct_method
    def th_thIframe(self,pane,method=None,**kwargs):
        pane.attributes.update(dict(overflow='hidden',_lazyBuild=True))
        pane = pane.contentPane(detachable=True,height='100%',_class='detachablePane')
        box = pane.div(_class='detacher',z_index=30)
        kwargs = dict([('main_%s' %k,v) for k,v in kwargs.items()])
        iframe = box.iframe(main='th_iframedispatcher',main_methodname=method,main_pkey='=#FORM.pkey',**kwargs)
        pane.dataController('genro.publish({iframe:"*",topic:"frame_onChangedPkey"},{pkey:pkey})',pkey='^#FORM.pkey')
        return iframe
         
    def rpc_th_iframedispatcher(self,root,methodname=None,pkey=None,**kwargs):
        rootattr = root.attributes
        rootattr['datapath'] = 'main'
        rootattr['overflow'] = 'hidden'
        rootattr['_fakeform'] = True
        rootattr['subscribe_frame_onChangedPkey'] = 'SET .pkey=$1.pkey;'
        root.dataFormula('.pkey','pkey',pkey=pkey,_onStart=True)
        getattr(self,'iframe_%s' %methodname)(root,**kwargs)