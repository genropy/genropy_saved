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

class TableHandlerBase(BaseComponent):
    py_requires='tablehandler/th_list:TableHandlerListBase,tablehandler/th_components:LinkedForm,gnrcomponents/formhandler:FormHandler'
    @extract_kwargs(condition=True)
    @struct_method
    def th_tableViewer(self,pane,frameCode=None,table=None,relation=None,th_pkey=None,viewResource=None,
                       reloader=None,virtualStore=None,condition=None,condition_kwargs=None,**kwargs):
        if relation:
            table,condition = self.__relationExpand(pane,relation=relation,condition=condition,condition_kwargs=condition_kwargs,**kwargs)             
        self.__mixinResource(frameCode,table=table,resourceName=viewResource,defaultClass='View')
        viewer = pane.thFrameGrid(frameCode=frameCode,th_root=frameCode,th_pkey=th_pkey,table=table,
                                 reloader=reloader,virtualStore=virtualStore,
                                 condition=condition,condition_kwargs=condition_kwargs,**kwargs)
        return viewer

    @extract_kwargs(dialog=True,palette=True,default=True)
    @struct_method
    def th_tableEditor(self,pane,frameCode=None,table=None,th_pkey=None,datapath=None,formResource=None,
                        dialog_kwargs=None,palette_kwargs=None,default_kwargs=None,formInIframe=False,**kwargs):
        table = table or pane.attributes.get('table')
        self.__mixinResource(frameCode,table=table,resourceName=formResource,defaultClass='Form')   
        
        if formInIframe:
            iframe = pane.view.grid.linkedForm(frameCode=frameCode,
                                                dialog_kwargs=dialog_kwargs,
                                                palette_kwargs=palette_kwargs,
                                               iframe=True,**kwargs)  
        else:
            form = pane.thLinkedForm(frameCode=frameCode,table=table,
                                    dialog_kwargs=dialog_kwargs,
                                    palette_kwargs=palette_kwargs,**kwargs)    
            rpc = form.store.handler('load',**default_kwargs)
            return form 
    
    @struct_method
    def th_thLinkedForm(self,th,frameCode=None,table=None,relation=None,readOnly=False,**kwargs):
        form = th.view.grid.linkedForm(frameCode=frameCode,th_root=frameCode,datapath='.form',childname='form',**kwargs) 
        slots = 'navigation,|,5,*,|,semaphore,|,formcommands,|,dismiss,5,locker,5'
        if readOnly:
            slots = 'navigation,|,5,*,|,dismiss,5'             
        toolbar = form.top.slotToolbar(slots,dismiss_iconClass='tb_button tb_listview',namespace='form')
        if table == self.maintable and hasattr(self,'th_form'):
            self.th_form(form)
        else:
            self._th_hook('form',mangler=frameCode)(form)
        return form
            
    
    @extract_kwargs(condition=True,grid=True)
    def __commonTableHandler(self,pane,nodeId=None,th_pkey=None,table=None,relation=None,datapath=None,viewResource=None,
                            formInIframe=False,reloader=None,virtualStore=False,condition=None,condition_kwargs=None,
                            default_kwargs=None,grid_kwargs=None,hiderMessage=None,pageName=None,readOnly=False,**kwargs):
        if relation:
            table,condition = self.__relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    default_kwargs=default_kwargs,**kwargs)
        tableCode = table.replace('.','_')
        th_root = nodeId or '%s_%i' %(tableCode,id(pane.parentNode))
        listCode='L_%s' %th_root
        formCode='F_%s' %th_root
        wdg = pane.child(datapath=datapath or '.%s'%tableCode,
                        thlist_root=listCode,
                        thform_root=formCode,
                        nodeId=nodeId,
                        table=table,
                        **kwargs)
        message= hiderMessage or '!!Save the main record to use this pane.'
        wdg.dataController("""
                            if(pkey=='*newrecord*'){
                                hider = sourceNode.setHiderLayer({message:message});
                            }else{
                                sourceNode.setHiderLayer(null,true);
                            }
                            """,pkey='^#FORM.pkey',sourceNode=wdg,message=message)
        top_slots = '#,addrow,delrow'
        if readOnly:
            top_slots = '#'
        wdg.tableViewer(frameCode=listCode,th_pkey=th_pkey,table=table,pageName=pageName,viewResource=viewResource,
                                reloader=reloader,virtualStore=virtualStore,top_slots=top_slots,
                                condition=condition,condition_kwargs=condition_kwargs,grid_kwargs=grid_kwargs)    
        return wdg
            
    def __relationExpand(self,pane,relation=None,condition=None,condition_kwargs=None,default_kwargs=None,**kwargs):
        maintable=kwargs.get('maintable') or pane.getInheritedAttributes().get('table') or self.maintable
        relation_attr = self.db.table(maintable).model.getRelation(relation)
        many = relation_attr['many'].split('.')
        fkey = many.pop()
        table = str('.'.join(many))
        fkey = str(fkey)
        condition_kwargs['fkey'] = '^#FORM.pkey'
        basecondition = '$%s=:fkey' %fkey       
        condition = basecondition if not condition else '(%s) AND (%s)' %(basecondition,condition)  
        default_kwargs['default_%s' %fkey] = '=#FORM/parent/#FORM.pkey'
        return table,condition 
    
    @extract_kwargs(dialog=True,default=True)
    @struct_method
    def th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,dialog_kwargs=None,reloader=None,default_kwargs=None,readOnly=None,**kwargs):      
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
                            formInIframe=False,palette_kwargs=None,default_kwargs=None,reloader=None,readOnly=None,**kwargs):
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,
                                        formInIframe=formInIframe,reloader=reloader,
                                        default_kwargs=default_kwargs,
                                        tag='ContentPane',readOnly=readOnly,**kwargs)        
        palette_kwargs = palette_kwargs
        form = pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,
                                formResource=formResource,
                                loadEvent='onRowDblClick',form_locked=True,
                                palette_kwargs=palette_kwargs,attachTo=pane,default_kwargs=default_kwargs,readOnly=readOnly)     
        return pane

    @extract_kwargs(widget=True,default=True)
    @struct_method
    def th_borderTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,loadEvent='onSelected',readOnly=None,**kwargs):
        kwargs['tag'] = 'BorderContainer'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,reloader=reloader,
                                        default_kwargs=default_kwargs,readOnly=readOnly,**kwargs)
        wdg.view.attributes.update(region='top',height='50%',splitter=True)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent=loadEvent,form_locked=True,default_kwargs=default_kwargs,readOnly=readOnly)    
        wdg.form.attributes.update(region='center')
        wdg.form.top.bar.replaceSlots('|,dismiss','')
        return wdg
        
    @extract_kwargs(widget=True,default=True)
    @struct_method
    def th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=None,**kwargs):
        kwargs['tag'] = 'StackContainer'
        kwargs['selectedPage'] = '^.selectedPage'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,formInIframe=formInIframe,reloader=reloader,default_kwargs=default_kwargs,
                                        pageName='view',readOnly=readOnly,**kwargs)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,pageName='form',formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent='onRowDblClick',form_locked=True,default_kwargs=default_kwargs,formInIframe=formInIframe,readOnly=readOnly)    
        return wdg
    
    def __getResourceName(self,name=None,defaultModule=None,defaultClass=None):
        if not name:
            return '%s:%s' %(defaultModule,defaultClass)
        if not ':' in name:
            return '%s:%s' %(name,defaultClass)
        if name.startswith(':'):
            return '%s%s' %(defaultModule,name)
        return name
        
    def __mixinResource(self,rootCode=None,table=None,resourceName=None,defaultClass=None):
        pkg,tablename = table.split('.')
        defaultModule = 'th_%s' %tablename
        resourceName = self.__getResourceName(resourceName,defaultModule,defaultClass)
        self.mixinComponent(pkg,'tables',tablename,resourceName,mangling_th=rootCode)
    
    @struct_method
    def th_thIframe(self,pane,method=None,**kwargs):     
        pane.attributes.update(dict(overflow='hidden',_lazyBuild=True))
        pane = pane.contentPane(detachable=True,height='100%',_class='detachablePane')
        box = pane.div(_class='detacher',z_index=30)
        kwargs = dict([('main_%s' %k,v) for k,v in kwargs.items()])
        dispatcher = 'th_iframedispatcher'
        iframe = box.iframe(main=dispatcher,main_methodname=method,main_pkey='=#FORM.pkey',**kwargs)
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
        
            
    def rpc_th_iframedispatcher_form(self,root,frameCode=None,formResource=None,table=None,pkey=None,**kwargs):
        self.__mixinResource(frameCode,table=table,resourceName=formResource,defaultClass='Form')   

        rootattr = root.attributes
        rootattr['datapath'] = 'main'
        rootattr['overflow'] = 'hidden'
        rootattr['subscribe_frame_onChangedPkey'] = 'SET .pkey=$1.pkey;'
        #root.dataFormula('.pkey','pkey',pkey=pkey,_onStart=True)
        form = root.frameForm(frameCode=frameCode,th_root=frameCode,datapath='.form',childname='form',
                            table=table,form_locked=True,startKey=pkey)
        if table == self.maintable and hasattr(self,'th_form'):
            self.th_form(form)
        else:
            self._th_hook('form',mangler=frameCode)(form)        
            
                                    
class StackTableHandlerRunner(BaseComponent):
    py_requires = """public:Public,tablehandler/th_components:TableHandlerBase"""
    plugin_list=''
    formResource = None
    viewResource = None
    formInIframe = False
    th_widget = 'stack'
    th_readOnly = False
    
    def onMain_pbl(self):
        pass

    def main(self,root,th_formResource=None,th_viewResource=None,**kwargs):
        formResource = th_formResource or self.formResource
        viewResource = th_viewResource or self.viewResource
        root = root.rootContentPane(title=self.tblobj.name_long)
        th_attr = dict(table=self.maintable,datapath=self.maintable.replace('.','_'),
                                formResource=formResource,viewResource=viewResource,virtualStore=True,
                                formInIframe=self.formInIframe,readOnly=self.th_readOnly,**kwargs)
                
        sc = getattr(root,'%sTableHandler' %self.th_widget)(**th_attr)
        sc.attributes.update(dict(border_left='1px solid gray'))
        sc.view.attributes.update(dict(border='0',margin='0', rounded=0))
        if not self.formInIframe:
            sc.form.attributes['hasBottomMessage'] = False
            sc.form.dataController('PUBLISH pbl_bottomMsg ={message:message,sound:sound};',formsubscribe_message=True)