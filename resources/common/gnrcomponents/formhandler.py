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

class FormHandler(BaseComponent):
    css_requires='public'
    py_requires='foundation/macrowidgets:SlotToolbar'
    
    @struct_method
    def fh_paletteFormPane(self,pane,paletteCode=None,table=None,title=None,
                        formId=None,nodeId=None,datapath=None,height=None,width=None,saveKwargs=None,
                        loadKwargs=None,disabled=None,**kwargs):
        nodeId = nodeId or '%s_palette' %paletteCode
        formId = formId or '%s_form' %paletteCode
        title = title or '^.record?caption'
        palette = pane.palettePane(paletteCode,datapath=datapath,
                                        height=height,width=width,title=title)
        return palette.formPane(formId=formId,table=table,datapath=datapath,
                                     disabled=disabled)
        
    @struct_method
    def fh_formPane(self,pane,formId=None,datapath=None,**kwargs):
        sqlContextName = 'sqlcontext_%s' % formId
        sqlContextRoot = '#%s.record' % formId    
        height= kwargs.get('height') or '100%'
        form = pane.borderContainer(datapath=datapath,formDatapath='.record',controllerPath='.form',pkeyPath='.pkey',
                                    formId=formId,sqlContextName=sqlContextName,sqlContextRoot=sqlContextRoot,
                                    height=height,**kwargs)
        form.contentPane(region='top',overflow='hidden',_attachname='top')
        bottom = form.contentPane(region='bottom',overflow='hidden',_attachname='bottom')
        form.contentPane(region='center',datapath='.record',_attachname='content',_class='fh_content',nodeId='%s_content' %formId)
        bottom.div(_class='fh_bottom_message').span(formsubscribe_message="""var domNode = this.domNode;
                                                 var sound = objectPop($1,'sound');
                                                 if(sound){
                                                    genro.playSound(sound);
                                                 }
                                                 var message = objectPop($1,'message');
                                                 var msgnode = document.createElement('span');
                                                 msgnode.innerHTML = message;
                                                 genro.dom.style(msgnode,$1);
                                                 domNode.appendChild(msgnode);
                                                 genro.dom.effect(domNode,'fadeout',{duration:1000,delay:2000,
                                                                                     onEnd:function(){domNode.innerHTML=null;}});
                                                """)
        return form

        
    @struct_method
    def fh_sltb_navigation(self,pane):
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
    def fh_sltb_semaphore(self,pane):
        pane.div(_class='fh_semaphore')
    
    @struct_method          
    def fh_sltb_formcommands(self,pane):
        buttons = pane.div(width='100px')
        buttons.button('!!Save', action='this.form.publish("save");', float='right',
                       iconClass="tb_button db_save", showLabel=False)
        buttons.button('!!Revert', action='this.form.publish("load");',
                        iconClass="tb_button db_revert",
                       float='right',
                       showLabel=False)
        buttons.button('!!Delete', action='this.form.publish("delete");', iconClass='db_del tb_button',
                       showLabel=False,float='right')
    @struct_method 
    def fh_sltb_locker(self,pane):
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
               