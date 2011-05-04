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


class FormHandler(BaseComponent):
    css_requires='public'
    py_requires='foundation/macrowidgets:SlotBar'

    @extract_kwargs(palette=True,dialog=True,default=True)
    @struct_method
    def lf_linkedForm(self,pane,frameCode=None,loadEvent=None,formRoot=None,store=True,table=None,
                        formId=None,dialog_kwargs=None,palette_kwargs=None,attachTo=None,
                        iframe=False,default_kwargs=None,**kwargs):
        formId = formId or '%s_form' %frameCode
        attachTo = attachTo or pane.parent
        table = table or pane.attributes.get('table')
        formRoot = self.__formRoot(pane,formId,formRoot=formRoot,dialog_kwargs=dialog_kwargs,
                                    palette_kwargs=palette_kwargs,attachTo=attachTo,form_kwargs=kwargs)
        parentTag = pane.attributes['tag'].lower()
        if iframe:
            iframe = self.__formInIframe(formRoot.contentPane(**kwargs),frameCode=frameCode,
                                          table=table,formId=formId,
                                         default_kwargs=default_kwargs)
            if parentTag=='includedview' or parentTag=='newincludedview':
                gridattr = pane.attributes
                gridattr['iframeform'] = iframe.js_domNode
                gridattr['formrootwidget'] = formRoot.js_widget
                gridattr['connect_%s' %loadEvent] = """
                                                var iframeform = this.inheritedAttribute('iframeform');
                                                var formrootwidget = this.inheritedAttribute('formrootwidget');
                                                formrootwidget.switchPage(1);
                                                console.log(iframeform);
                                                """                
                return iframe
        else:
            form = formRoot.frameForm(frameCode=frameCode,formId=formId,table=table,
                                     store=store,**kwargs)
            attachTo.form = form
            form.store.handler('load',**default_kwargs)
            
        if parentTag=='includedview' or parentTag=='newincludedview':
            gridattr = pane.attributes
            storeattr = form.store.attributes
            storeattr['storeType'] = 'Collection'
            storeattr['parentStore'] = gridattr['store']
            gridattr['currform'] = form.js_form
            gridattr['connect_%s' %loadEvent] = """
                                                var rowIndex= typeof($1)=="number"?$1:$1.rowIndex;
                                                if(rowIndex>-1){
                                                    var currform = this.inheritedAttribute('currform');
                                                    currform.load({destPkey:this.widget.rowIdByIndex(rowIndex),destIdx:rowIndex});
                                                }
                                                """
            gridattr['selfsubscribe_addrow'] = 'currform.newrecord();'
            gridattr['selfsubscribe_delrow'] = "alert('should delete')"
            gridattr['subscribe_form_%s_onLoaded' %formId] ="""
                                                                if($1.pkey!='*newrecord*' || $1.pkey!='*norecord*'){
                                                                    this.widget.selectByRowAttr('_pkey',$1.pkey);
                                                                }
                                                                  """
            form = self.linkedFormBody(form,**kwargs)
        return form
    
    def linkedFormBody(self,form,**kwargs):
        return form
        
    def __formRoot(self,pane,formId,formRoot=None,dialog_kwargs=None,palette_kwargs=None,
                    attachTo=None,form_kwargs=None):
        loadSubscriber = 'subscribe_form_%s_onLoading' %formId
        closeSubscriber = 'subscribe_form_%s_onDismissed' %formId
        if formRoot:
            if form_kwargs.get('pageName'):
                formRoot.attributes[loadSubscriber] = 'this.widget.switchPage(1);'
                formRoot.attributes[closeSubscriber] = 'this.widget.switchPage(0);'
        elif dialog_kwargs:
            if 'height' in dialog_kwargs:
                form_kwargs['height'] = dialog_kwargs.pop('height')
            if 'width' in dialog_kwargs:
                form_kwargs['width'] = dialog_kwargs.pop('width')
                dialog_kwargs['closable'] = dialog_kwargs.get('closable','publish')
                dialog_kwargs[loadSubscriber] = "this.widget.show();"
                dialog_kwargs[closeSubscriber] = "this.widget.hide();"
                dialog_kwargs['selfsubscribe_close'] = """genro.formById('%s').dismiss($1.modifiers);
                                                            """ %formId
            formRoot = attachTo.dialog(**dialog_kwargs)
        elif palette_kwargs:
            palette_kwargs[loadSubscriber] = "this.widget.show();"
            palette_kwargs[closeSubscriber] = "this.widget.hide();"
            palette_kwargs['dockTo'] = palette_kwargs.get('dockTo','dummyDock')
            formRoot = attachTo.palette(**palette_kwargs)
        return formRoot
        
    def __formInIframe(self,pane,default_kwargs=None,**kwargs):     
        pane.attributes.update(dict(overflow='hidden',_lazyBuild=True))
        pane = pane.contentPane(detachable=True,height='100%',_class='detachablePane')
        box = pane.div(_class='detacher',z_index=30)
        kwargs = dict([('main_%s' %k,v) for k,v in kwargs.items()])
        kwargs.update(dict([('main_default_%s' %k,v) for k,v in default_kwargs.items()]))
        dispatcher = 'lf_iframeFormDispatcher'
        iframe = box.iframe(main=dispatcher,**kwargs)
        #pane.dataController('genro.publish({iframe:"*",topic:"frame_onChangedPkey"},{pkey:pkey})',pkey='^#FORM.pkey')
        return iframe

    @extract_kwargs(default=True)
    def rpc_lf_iframeFormDispatcher(self,root,pkey=None,default_kwargs=None,**kwargs):        
        rootattr = root.attributes
        rootattr['datapath'] = 'main'
        rootattr['overflow'] = 'hidden'
        root.dataFormula('.pkey','pkey',pkey=pkey,_onStart=True)
        form = root.frameForm(store=True,store_startKey=pkey,**kwargs)
        #form.formStore(storeType='recordCluster',startKey=pkey)
        form.store.handler('load',default_kwargs=default_kwargs)
        self.linkedFormBody(form,**kwargs)

    @struct_method
    def fh_slotbar_form_navigation(self,pane,**kwargs):
        pane = pane.div(lbl='!!Navigation',_class='slotbar_group')
        pane.slotbar_form_first()
        pane.slotbar_form_prev()
        pane.slotbar_form_next()
        pane.slotbar_form_last()
        
    @struct_method               
    def fh_slotbar_form_semaphore(self,pane,**kwargs):
        pane.div(_class='fh_semaphore')
    
    @struct_method          
    def fh_slotbar_form_formcommands(self,pane,**kwargs):
        pane = pane.div(lbl='!!Form Commands',_class='slotbar_group')
        pane.slotbar_form_save()
        pane.slotbar_form_revert()
        pane.slotbar_form_delete()
        pane.slotbar_form_add()
        
    @struct_method          
    def fh_slotbar_form_dismiss(self,pane,caption=None,iconClass=None,**kwargs):
        pane.formButton('!!Dismiss',iconClass="tb_button tb_listview",
                    topic='navigationEvent',command='dismiss')
    
    @struct_method          
    def fh_slotbar_form_save(self,pane,**kwargs):
        pane.formButton('!!Save',topic='save',iconClass="tb_button db_save", parentForm=True)

    @struct_method          
    def fh_slotbar_form_revert(self,pane,**kwargs):
        pane.formButton('!!Revert',topic='load',iconClass="tb_button db_revert", parentForm=True)
    
    @struct_method          
    def fh_slotbar_form_delete(self,pane,parentForm=True,**kwargs):
        pane.formButton('!!Delete',topic='deleteItem',
                        iconClass="tb_button db_del",parentForm=parentForm,**kwargs)
    
    @struct_method          
    def fh_slotbar_form_add(self,pane,parentForm=True,**kwargs):
        pane.formButton('!!Add',topic='navigationEvent',command='add',
                        iconClass="tb_button db_add",parentForm=parentForm,**kwargs)

    @struct_method          
    def fh_slotbar_form_first(self,pane,**kwargs):
        pane.formButton('!!First',iconClass="tb_button icnNavFirst",
                    topic='navigationEvent',command='first',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.first || false);")
    
    @struct_method          
    def fh_slotbar_form_prev(self,pane,**kwargs):
        pane.formButton('!!Prev',iconClass="tb_button icnNavPrev",
                    topic='navigationEvent',command='prev',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.first || false);")
    
    @struct_method          
    def fh_slotbar_form_next(self,pane,**kwargs):
        pane.formButton('!!Next',iconClass="tb_button icnNavNext",
                    topic='navigationEvent',command='next',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.last || false);")
    
    @struct_method          
    def fh_slotbar_form_last(self,pane,**kwargs):
        pane.formButton('!!Last',iconClass="tb_button icnNavLast",
                    topic='navigationEvent',command='last',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.last || false);")

    @struct_method           
    def fh_formButton(self,pane,label=None,iconClass=None,topic=None,command=True,**kwargs):
        pane.slotButton(label, lbl=label,iconClass=iconClass,topic=topic,
                    action='this.form.publish(topic,{command:command,modifiers:genro.dom.getEventModifiers(event)});',command=command,
                    **kwargs)
    
    @struct_method 
    def fh_slotbar_form_locker(self,pane,**kwargs):
        pane.button('!!Locker',width='20px',iconClass='icnBaseUnlocked',showLabel=False,
                    action='this.form.publish("setLocked","toggle");',
                    formsubscribe_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'icnBaseLocked':'icnBaseUnlocked');""",
                    **kwargs)
