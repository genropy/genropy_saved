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
# 


from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method



class TableHandlerFormBase(BaseComponent):
    py_requires='gnrcomponents/formhandler:FormHandler,tablehandler/th_core:TableHandlerCommon'
    css_requires='public'
    @struct_method
    def th_linkedFormPage(self,th,frameCode=None,table=None,**kwargs):
        form = th.list.iv.linkedForm(frameCode=frameCode,th_root=frameCode,datapath='.form',childname='form',**kwargs)  
        toolbar = form.top.slotToolbar('navigation,|,5,*,|,semaphore,|,formcommands,|,dismiss,5,locker,5',
                                        dismiss_iconClass='tb_button tb_listview',namespace='form')
        if table == self.maintable and hasattr(self,'th_main'):
            self.th_main(th)
        else:
            center = form.center.contentPane(datapath='.record')
            self._th_hook('form',mangler=frameCode)(center)
        return form
    
    @struct_method
    def th_formPage(self, th,frameCode=None,table=None,parentStore=None,startKey=None,**kwargs):
        th_root=th.attributes['thform_root']
        form = th.frameForm(frameCode=th_root,th_root=th_root,datapath='.form',childname='form',
                            table=table,form_locked=True,**kwargs)
        if parentStore:
            self.th_formPageCollection(form,parentStore=parentStore)
        elif startKey:
            self.th_formPageItem(form, startKey=startKey)
        if table == self.maintable and hasattr(self,'th_main'):
            self.th_main(th)
        else:
            center = form.center.contentPane(datapath='.record')
            self._th_hook('form',mangler=frameCode)(center)
        return form
        
    def th_formPageCollection(self,form,parentStore=None):
        store = form.formStore(storepath='.record',hander='recordCluster',storeType='Collection',onSaved='reload',parentStore=parentStore)                 
        toolbar = form.top.slotToolbar('navigation,|,5,*,|,semaphore,|,formcommands,|,dismiss,5,locker,5',
                                        dismiss_iconClass='tb_button tb_listview',namespace='form')
    
    def th_formPageItem(self,form,startKey=None):
        store = form.formStore(storepath='.record',hander='recordCluster',onSaved='reload',startKey=startKey)                 
        toolbar = form.top.slotToolbar('*,|,semaphore,|,formcommands,|,5,locker,5',
                                        dismiss_iconClass='tb_button tb_listview',namespace='form')
    
    

class TableHandlerFormLegacy(BaseComponent):
    py_requires='gnrcomponents/formhandler:FormHandler'
    @struct_method
    def th_formPage(self, sc,frameCode=None):
        sc.attributes['center_selfsubscribe_dismiss']='SET list.selectedIndex=-2;',
        form = sc.frameForm(frameCode=frameCode,formId='formPane',datapath='form',controllerPath='gnr.forms.formPane',
                            table=self.maintable,center_widget='BorderContainer',
                            pkeyPath='.pkey',hasBottomMessage=False,
                            form_locked=True,th_root=frameCode,
                            formsubscribe_onDismissed='SET list.selectedIndex=-2;')
        form.dataController("this.form.load({destPkey:pkey});",pkey="=list.selectedId",_fired='^form.doLoad')
        store = form.formStore(storepath='.record',hander='recordCluster',storeType='Collection',onSaved='reload',
                        parentStore='maingrid')
        store.handler('load',sqlContextName='sql_record')
        form.dataController("""
                                SET form.locked=locked;
                                """,formsubscribe_onLockChange=True)
        form.data('form.locked',True)
        form.dataController("genro.dom.setClass(dojo.body(),'form_locked',locked)", locked="^form.locked")
        form.dataFormula('form.canWrite', '(!locked ) && writePermission', locked='^form.locked',
                         writePermission='=usr.writePermission', _init=True)
        form.dataFormula('form.canDelete', '(!locked) && deletePermission', locked='^form.locked',
                         deletePermission='=usr.deletePermission', _init=True)
        
        self.formTitleBase(form)
        toolbarKw = dict()
        tagSlot = ''
        if self.hasTags():
            tagSlot = '15,|,tagsbtn,|,'
            toolbarKw['tagsbtn_mode'] = 'form'                  
        toolbar = form.top.slotToolbar('navigation,|,5,hiddenrecord,%s*,|,semaphore,|,formcommands,|,dismiss,5,locker,5' %tagSlot,
                                        dismiss_iconClass='tb_button tb_listview',**toolbarKw)

        self.setLogicalDeletionCheckBox(toolbar.hiddenrecord)
        center = form.center.contentPane(datapath='.record')
        self._th_hook('form')(center)
        
    def setLogicalDeletionCheckBox(self, elem):
        box = elem.div(_class='hidden_record_checkbox')
        box.checkbox(label='!! Hidden',
                     value='^form.logical_deleted',
                     disabled='^form.locked')
        #elem.dataFormula('aux.listpage', '!selectedpage', selectedpage='^selectedPage', _onStart=True)
        elem.dataController("""if(logical_deleted){
                                   genro.dom.addClass("formPane", "logicalDeleted");
                               }else{
                                   genro.dom.removeClass("formPane", "logicalDeleted");
                               }
                               if($2.kw.reason!=true){
                                   if (delete_ts && !logical_deleted){
                                        SET form.record.__del_ts = null;
                                    }else if(logical_deleted && !delete_ts){
                                        SET form.record.__del_ts =new Date();
                                    }
                               }
                               """,
                            logical_deleted='^form.logical_deleted', delete_ts='=form.record.__del_ts')