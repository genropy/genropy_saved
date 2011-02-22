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

class TableHandlerForm(BaseComponent):
    def pageForm(self, sc):
        sc.attributes['center_selfsubscribe_dismiss']='SET list.selectedIndex=-2;',
        form = sc.frameForm(frameCode='formPane',formId='formPane',datapath='form',controllerPath='gnr.forms.formPane',
                            table=self.maintable,center_widget='BorderContainer',
                            pkeyPath='.pkey',hasBottomMessage=False,
                            formsubscribe_onDismissed='SET list.selectedIndex=-2;',
                            sqlContextName='sql_record',
                            sqlContextRoot='form.record',
                            sqlContextTable=self.maintable)
        form.dataController("this.form.load({destPkey:pkey});",pkey="=list.selectedId",_fired='^form.doLoad')
        store = form.formStore(storepath='.record',hander='recordCluster',storeType='Collection',onSaved='reload',
                        parentStore='maingrid')
        self.formTitleBase(form)
        toolbarKw = dict()
        tagSlot = ''
        if self.hasTags():
            tagSlot = '15,|,tagsbtn,|,'
            toolbarKw['tagsbtn_mode'] = 'form'                  
        toolbar = form.top.slotToolbar('navigation,|,5,hiddenrecord,%s*,|,semaphore,|,formcommands,|,dismiss,5,locker,5' %tagSlot,
                                        dismiss_iconClass='tb_button tb_listview',**toolbarKw)

        self.setLogicalDeletionCheckBox(toolbar.hiddenrecord)
        self.formBase(form,region='center')
        
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