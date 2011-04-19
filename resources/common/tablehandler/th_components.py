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
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrlang import extract_kwargs

class TableHandlerBase(BaseComponent):
    py_requires='tablehandler/th_list:TableHandlerListBase,tablehandler/th_form:TableHandlerFormBase'
    
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
                        dialog_kwargs=None,palette_kwargs=None,default_kwargs=None,**kwargs):
        table = table or pane.attributes.get('table')
        self.__mixinResource(frameCode,table=table,resourceName=formResource,defaultClass='Form')   
        form = pane.thLinkedForm(frameCode=frameCode,table=table,
                                    dialog_kwargs=dialog_kwargs,
                                    palette_kwargs=palette_kwargs,**kwargs)    
        rpc = form.store.handler('load',**default_kwargs)
        return form 
            
    @extract_kwargs(condition=True)
    def __commonTableHandler(self,pane,nodeId=None,th_pkey=None,table=None,relation=None,datapath=None,viewResource=None,
                            th_iframe=False,reloader=None,virtualStore=False,condition=None,condition_kwargs=None,
                            default_kwargs=None,**kwargs):
        if relation:
            table,condition = self.__relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    default_kwargs=default_kwargs,**kwargs)
        tableCode = table.replace('.','_')
        th_root = nodeId or '%s_%i' %(tableCode,id(pane.parentNode))
        listCode='L_%s' %th_root
        formCode='F_%s' %th_root
        wdg = pane.child(datapath=datapath or '#FORM.%s'%tableCode,
                        thlist_root=listCode,
                        thform_root=formCode,
                        nodeId=nodeId,
                        table=table,
                        **kwargs)
        viewpage = wdg.tableViewer(frameCode=listCode,th_pkey=th_pkey,table=table,pageName='view',viewResource=viewResource,
                                reloader=reloader,virtualStore=virtualStore,top_slots='#,addrow,delrow,list_locker',
                                condition=condition,condition_kwargs=condition_kwargs)    
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
                            th_iframe=False,dialog_kwargs=None,reloader=None,default_kwargs=None,**kwargs):      
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,th_iframe=th_iframe,reloader=reloader,
                                        tag='ContentPane',default_kwargs=default_kwargs,**kwargs)        
        form = pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,loadEvent='onRowDblClick',
                               form_locked=True,dialog_kwargs=dialog_kwargs,attachTo=pane,
                               formResource=formResource,default_kwargs=default_kwargs)     
        return pane
    
    @extract_kwargs(palette=True,default=True)
    @struct_method
    def th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            th_iframe=False,palette_kwargs=None,default_kwargs=None,reloader=None,**kwargs):
        pane = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,
                                        th_iframe=th_iframe,reloader=reloader,
                                        default_kwargs=default_kwargs,
                                        tag='ContentPane',**kwargs)        
        palette_kwargs = palette_kwargs
        form = pane.tableEditor(frameCode=pane.attributes['thform_root'],table=table,
                                formResource=formResource,
                                loadEvent='onRowDblClick',form_locked=True,
                                palette_kwargs=palette_kwargs,attachTo=pane,default_kwargs=default_kwargs)     
        return pane

    @extract_kwargs(widget=True,default=True)
    @struct_method
    def th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            th_iframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,**kwargs):
        kwargs['tag'] = 'StackContainer'
        kwargs['selectedPage'] = '^.selectedPage'
        wdg = self.__commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,
                                        viewResource=viewResource,th_iframe=th_iframe,reloader=reloader,default_kwargs=default_kwargs,**kwargs)
        wdg.tableEditor(frameCode=wdg.attributes['thform_root'],formRoot=wdg,pageName='form',formResource=formResource,
                        store_startKey=th_pkey,table=table,loadEvent='onRowDblClick',form_locked=True,default_kwargs=default_kwargs)    
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
    
                
    def th_stackIframe(self,sc,pkg,tablename):
        formRunnerUrl='/adm/th/formrunner'
        viewRunnerUrl='/adm/th/viewrunner'
        sc.contentPane(detachable=True,pageName='view').contentPane(margin='5px',overflow='hidden'
                            ).iframe(src='%s/%s/%s' %(viewRunnerUrl,pkg,tablename),border=0,height='100%',width='100%')
        sc.contentPane(detachable=True,pageName='form').contentPane(margin='5px',overflow='hidden',_lazyBuild=True,
                            ).iframe(src='%s/%s/%s' %(formRunnerUrl,pkg,tablename),border=0,height='100%',width='100%')
    

                            
class StackTableHandlerRunner(BaseComponent):
    py_requires = """public:Public,tablehandler/th_components:TableHandlerBase"""
    plugin_list=''
    formResource = None
    viewResource = None
    
    def onMain_pbl(self):
        pass

    def main(self,root,th_formResource=None,th_viewResource=None,**kwargs):
        formResource = th_formResource or self.formResource
        viewResource = th_viewResource or self.viewResource
        root = root.rootContentPane(title=self.tblobj.name_long,bottom=False)
        sc = root.stackTableHandler(table=self.maintable,datapath=self.maintable.replace('.','_'),
                                formResource=formResource,viewResource=viewResource,virtualStore=True,**kwargs)
        sc.view.bottom.slotBar('*,messageBox,*',childname='footer',_class='pbl_root_bottom',messageBox_subscribedTo='%s_message' %sc.attributes['thlist_root'])
        sc.form.attributes['hasBottomMessage'] = False
        sc.form.bottom.slotBar('*,messageBox,*',childname='footer',_class='pbl_root_bottom',
                            messageBox_subscribeTo='form_%s_form_message' %sc.attributes['thform_root'])

        
    
     