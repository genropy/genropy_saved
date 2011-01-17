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
        form.contentPane(region='center',datapath='.record',_attachname='content')
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
        pane = pane.div(width='120px')
        pane.button('!!First', fire_first='.navbutton', iconClass="tb_button icnNavFirst",
                  disabled='^.atBegin', showLabel=False)
        pane.button('!!Previous', fire_prev='.navbutton', iconClass="tb_button icnNavPrev",
                  disabled='^.atBegin', showLabel=False)
        pane.button('!!Next', fire_next='.navbutton', iconClass="tb_button icnNavNext",
                  disabled='^.atEnd', showLabel=False)
        pane.button('!!Last', fire_last='.navbutton', iconClass="tb_button icnNavLast",
                  disabled='^.atEnd', showLabel=False)
    
    @struct_method               
    def fh_sltb_semaphore(self,pane):
        pane.div(width='20px',_class='greenLight',
                 formsubscribe_onStatusChange="""
                                    var status = $1.status;
                                    genro.dom.setClass(this.domNode,"redLight",status=='error');
                                    genro.dom.setClass(this.domNode,"yellowLight",status=='changed');
                                    genro.dom.setClass(this.domNode,"greenLight",status=='ok');
                                    genro.dom.setClass(this.domNode,"icnBaseReadOnly",status=='readOnly');
                                    """)
    
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
        pane.button('!!Locker',width='20px',iconClass='icnBaseLocked',showLabel=False,
                    action='this.form.publish("setLocked","toggle");',
                    formsubscribe_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'icnBaseLocked':'icnBaseUnlocked');""")
        
        