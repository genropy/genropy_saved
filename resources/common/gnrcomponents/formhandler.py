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
from gnr.core.gnrdict import dictExtract


class FormHandler(BaseComponent):
    css_requires='public'
    py_requires='foundation/macrowidgets:SlotBar'

    @struct_method
    def fh_sltb_navigation(self,pane,**kwargs):
        pane = pane.div(width='120px',action='this.form.publish("navigationEvent",command);')
        pane.button('!!First', command='first', iconClass="tb_button icnNavFirst",
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.first || false);",
                    showLabel=False)
        pane.button('!!Previous', command='prev', iconClass="tb_button icnNavPrev",
                    showLabel=False,formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.first || false);")
        pane.button('!!Next', command='next', iconClass="tb_button icnNavNext",showLabel=False,
                  formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.last || false);")
        pane.button('!!Last', command='last', iconClass="tb_button icnNavLast",
                   formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.last || false);",showLabel=False)
    
    @struct_method               
    def fh_sltb_semaphore(self,pane,**kwargs):
        pane.div(_class='fh_semaphore')
    
    @struct_method          
    def fh_sltb_formcommands(self,pane,**kwargs):
        buttons = pane.div(width='100px')
        buttons.button('!!Save', action='this.form.publish("save");', float='right',
                       iconClass="tb_button db_save", showLabel=False,parentForm=True)
        buttons.button('!!Revert', action='this.form.publish("load");',
                        iconClass="tb_button db_revert",
                       float='right',
                       showLabel=False,parentForm=True)
        buttons.button('!!Delete', action='this.form.publish("delete");', iconClass='db_del tb_button',
                       showLabel=False,float='right',parentForm=True)
    @struct_method 
    def fh_sltb_locker(self,pane,**kwargs):
        pane.button('!!Locker',width='20px',iconClass='icnBaseUnlocked',showLabel=False,
                    action='this.form.publish("setLocked","toggle");',
                    formsubscribe_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'icnBaseLocked':'icnBaseUnlocked');""")
        
    @struct_method
    def recordClusterStore(self,pane,table=None,storeType=None,**kwargs):
        form_table = table or self.maintable
        pane.attributes['form_table'] = form_table
        pane.formStore('recordCluster',storeType=storeType,loadMethod='loader_recordCluster',
                        saveMethod='saver_recordCluster',deleteMethod='deleter_recordCluster',
                        **kwargs)
               