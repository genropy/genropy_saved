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
    
    @extract_kwargs(widget=True,dialog=True)
    @struct_method
    def th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            th_iframe=False,widget_kwargs=None,dialog_kwargs=None,reloader=None,**kwargs):
        pane = self._commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,formResource=formResource,viewResource=viewResource,
                                        th_iframe=th_iframe,reloader=reloader,
                                        widget_kwargs=dict(tag='ContentPane'),**kwargs)        
        dialog_kwargs = dialog_kwargs #or self._th_hook('dialog',mangler=pane.attributes['thform_root'])()
        form = pane.linkedFormPage(pageName='form',table=table,loadEvent='onRowDblClick',
                            form_locked=True,dialog_kwargs=dialog_kwargs)     
        pane.form = form        
        return pane

    @extract_kwargs(widget=True)
    @struct_method
    def th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,
                            th_iframe=False,widget_kwargs=None,reloader=None,**kwargs):
        widget_kwargs['tag'] = 'StackContainer'
        widget_kwargs['selectedPage'] = '^.selectedPage'
        wdg = self._commonTableHandler(pane,nodeId=nodeId,table=table,th_pkey=th_pkey,datapath=datapath,formResource=formResource,
                                        viewResource=viewResource,th_iframe=th_iframe,reloader=reloader,
                                        widget_kwargs=widget_kwargs,**kwargs)
        
        wdg.linkedFormPage(formRoot=wdg,pageName='form',store_startKey=th_pkey,table=table,loadEvent='onRowDblClick',
                            form_locked=True,**kwargs)                    
        return wdg
    
   
    def _commonTableHandler(self,pane,nodeId=None,th_pkey=None,table=None,datapath=None,formResource=None,viewResource=None,
                            th_iframe=False,widget_kwargs=None,reloader=None,virtualStore=False,**kwargs):
        pkg,tablename = table.split('.')
        tableCode = table.replace('.','_')
        th_root = nodeId or tableCode
        defaultModule = 'th_%s' %tablename
        def getResourceName(name=None,defaultModule=None,defaultClass=None):
            if not name:
                return '%s:%s' %(defaultModule,defaultClass)
            if not ':' in name:
                return '%s:%s' %(name,defaultClass)
            if name.startswith(':'):
                return '%s%s' %(defaultModule,name)
            return name
        
        formResource = getResourceName(formResource,defaultModule,'Form')
        viewResource = getResourceName(viewResource,defaultModule,'View')
        thlist_root='L_%s' %th_root
        thform_root='F_%s' %th_root
        wdg = pane.child(datapath=datapath or '.%s'%tableCode,thlist_root=thlist_root,
                        thform_root=thform_root,nodeId=nodeId,
                        selfsubscribe_load='genro.getForm(this.attr.thform_root).load({destPkey:$1})',
                        **widget_kwargs)
        if th_iframe:
            self.th_stackIframe(wdg,pkg,tablename)            
        else:
            self.mixinComponent(pkg,'tables',tablename,viewResource,defaultModule=defaultModule,defaultClass='View',mangling_th=thlist_root)
            self.mixinComponent(pkg,'tables',tablename,formResource,defaultModule=defaultModule,defaultClass='Form',mangling_th=thform_root)
            viewpage = wdg.listPage(frameCode=thlist_root,th_root=thlist_root,th_pkey=th_pkey,table=table,pageName='view',reloader=reloader,virtualStore=virtualStore)
            
            viewpage.iv.attributes['selfsubscribe_add'] = 'genro.getForm(this.attr.linkedForm).load({destPkey:"*newrecord*"});'
            viewpage.iv.attributes['selfsubscribe_del'] = 'var pkeyToDel = this.widget.getSelectedPkeys(); console.log(pkeyToDel);' #'genro.getForm(this.attr.linkedForm).deleteItem({});'
        return wdg
                
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
        root = root.rootContentPane(title=self.tblobj.name_long)
        root.stackTableHandler(table=self.maintable,datapath=self.maintable.replace('.','_'),formResource=formResource,viewResource=viewResource,virtualStore=True,**kwargs)
        
    
     