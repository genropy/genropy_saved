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
from gnr.core.gnrdecorator import extract_kwargs
from gnr.core.gnrbag import Bag


class FormHandler(BaseComponent):
    css_requires='public'

    @extract_kwargs(palette=True,dialog=True,default=True,tree=True)
    @struct_method
    def formhandler_linkedForm(self,pane,frameCode=None,loadEvent=None,formRoot=None,store=True,table=None,
                        formId=None,dialog_kwargs=None,palette_kwargs=None,attachTo=None,
                        iframe=False,default_kwargs=None,tree_kwargs=None,**kwargs):
        formId = formId or '%s_form' %frameCode
        attachTo = attachTo or pane.parent
        table = table or pane.attributes.get('table')
        formRoot = pane._makeFormRoot(formId,formRoot=formRoot,dialog_kwargs=dialog_kwargs,
                                    palette_kwargs=palette_kwargs,attachTo=attachTo,form_kwargs=kwargs)
        parentTag = pane.attributes['tag'].lower()
        if parentTag=='includedview' or parentTag=='newincludedview':
            self.__linkToParentGrid(pane,formId=formId,iframe=iframe,loadEvent=loadEvent)
            kwargs['store_storeType'] = 'Collection'
            kwargs['store_parentStore'] = pane.attributes['store']
        if iframe:
            src=None if iframe is True else iframe
            return formRoot.formInIframe(table=table,formId=formId,default_kwargs=default_kwargs,src=src,**kwargs)
        form = formRoot.frameForm(frameCode=frameCode,formId=formId,table=table,store=store,**kwargs)
        attachTo.form = form
        form.store.handler('load',default_kwargs=default_kwargs)
        return form
    
    
    @extract_kwargs(palette=True,dialog=True)
    @struct_method
    def formhandler__makeFormRoot(self,pane,formId,formRoot=None,dialog_kwargs=None,palette_kwargs=None,
                    attachTo=None,form_kwargs=None,datapath=None,handlerType=None):
        attachTo = attachTo or pane
        loadSubscriber = 'subscribe_form_%s_onLoading' %formId
        closeSubscriber = 'subscribe_form_%s_onDismissed' %formId
        onChangedTitle = 'subscribe_form_%s_onChangedTitle' %formId

        handlerType = handlerType or form_kwargs.get('handlerType') or pane.getInheritedAttributes().get('handlerType')
        if not handlerType:
            if dialog_kwargs:
                handlerType = 'dialog'
            elif palette_kwargs:
                handlerType = 'palette'
        form_kwargs['form_handlerType'] = handlerType
        if formRoot:
            if form_kwargs.get('pageName'):
                formRoot.attributes[loadSubscriber] = 'this.widget.switchPage(1);'
                formRoot.attributes[closeSubscriber] = 'this.widget.switchPage(0);'
        elif handlerType=='dialog':
            if datapath:
                dialog_kwargs['datapath'] = datapath
            dialog_kwargs['noModal'] = dialog_kwargs.get('noModal',True)
            if 'height' in dialog_kwargs:
                form_kwargs['height'] = dialog_kwargs.pop('height','400px')
            if 'width' in dialog_kwargs:
                form_kwargs['width'] = dialog_kwargs.pop('width','600px')
            dialog_kwargs['closable'] = dialog_kwargs.get('closable','publish')
            #dialog_kwargs['title'] = dialog_kwargs.get('title','^.form.controller.title')
            dialog_kwargs[onChangedTitle] = "this.widget.setTitle($1.title);"
            dialog_kwargs[loadSubscriber] = "this.widget.show();"
            dialog_kwargs[closeSubscriber] = "this.widget.hide();"
            dialog_kwargs['selfsubscribe_close'] = """genro.publish('form_%s_dismiss',$1.modifiers);""" %formId
            formRoot = attachTo.dialog(**dialog_kwargs)
        elif handlerType=='palette':
            if datapath:
                palette_kwargs['datapath'] = datapath
            palette_kwargs[loadSubscriber] = "this.widget.show();"
            palette_kwargs[closeSubscriber] = "this.widget.hide();"
            palette_kwargs[onChangedTitle] = "this.widget.setTitle($1.title);"
            palette_kwargs['dockTo'] = palette_kwargs.get('dockTo','dummyDock')
            dialog_kwargs['selfsubscribe_close'] = """genro.formById('%s').dismiss($1.modifiers);
                                                            """ %formId
            formRoot = attachTo.palette(**palette_kwargs)
        return formRoot

    def __linkToParentGrid(self,grid,formId=None,iframe=None,loadEvent=None):
        gridattr = grid.attributes
        gridattr['_linkedFormId']=formId
        gridsubscribers = dict()
        gridattr['connect_%s' %loadEvent] = """
                                            var rowIndex= typeof($1)=="number"?$1:$1.rowIndex;
                                            genro.callAfter(function(){
                                                var selectedRows = this.widget.getSelectedRowidx() || [];
                                                if(rowIndex>-1 && selectedRows.length==1){
                                                    this.publish('editrow',{pkey:this.widget.rowIdByIndex(rowIndex)});
                                                }else{
                                                    this.publish('editrow',{pkey:'*norecord*'});
                                                }
                                            },100,this,'editselectedrow');
                                            """
        gridattr['selfsubscribe_addrow'] = """ var newrecord_kw = {pkey:"*newrecord*"};
                                                if($1.opt){
                                                    objectUpdate(newrecord_kw,objectPop($1,'opt'));
                                                    objectUpdate(newrecord_kw,$1);
                                                }
                                                if(this.attr.table && this.form && this.form.isNewRecord()){
                                                    if(this.attr._saveNewRecordOnAdd){
                                                        var that = this;
                                                        this.form.save({onReload:function(result){
                                                                that.publish('editrow',newrecord_kw);
                                                            }});
                                                    }else{
                                                        return;
                                                    }
                                                }else{
                                                    this.publish('editrow',newrecord_kw);
                                                }"""
        gridattr['selfsubscribe_editrow'] = """
                                    var pref = 'form_'+this.attr._linkedFormId;
                                    if($1.pkey=='*newrecord*'){
                                        var kw = {destPkey:$1.pkey};
                                        if($1.default_kw){
                                            kw.default_kw = $1.default_kw;
                                        }
                                        genro.publish(pref+'_load',kw);
                                    }else{

                                        genro.publish(pref+'_goToRecord',$1.pkey || '*norecord*');
                                    }
                                    """
        gridattr['selfsubscribe_viewlocker'] = 'this.widget.collectionStore().setLocked("toggle");'
        gridsubscribers['onExternalChanged']= """
            var selectionStore = this.widget.collectionStore();
            var frm = selectionStore._editingForm;
            if(!frm){
                return;
            }
            var currentPkey =  frm.getCurrentPkey();
            if(currentPkey && currentPkey!='*newrecord*' && currentPkey!='*norecord*'){
                var selectedRows = this.widget.getSelectedRowidx() || [];
                if(!(selectedRows.length>1)){
                    this.widget.selectByRowAttr('_pkey',currentPkey,null,frm.store.loadedIndex==-1);
                }
                frm.store.setNavigationStatus(currentPkey);
            }
        """
        gridattr['subscribe_form_%s_onLoaded' %formId] ="""if(!(($1.pkey=='*newrecord*') || ($1.pkey=='*norecord*'))){
                                                                var selectedRows = this.widget.getSelectedRowidx() || [];
                                                                if(!(selectedRows.length>1)){
                                                                    this.widget.selectByRowAttr('_pkey',$1.pkey);
                                                                }
                                                            }
                                                              """
        subpref = 'subscribe_%(nodeId)s' %gridattr
        for k,v in gridsubscribers.items():
            gridattr['%s_%s' %(subpref,k)] = v

    @extract_kwargs(store=True,dialog=True,palette=True,main=dict(slice_prefix=False),default=True)
    @struct_method
    def fh_formInIframe(self,pane,table=None,
                       formId=None,default_kwargs=None,src=None,
                       formResource=None,store_kwargs=True,
                       dialog_kwargs=None,palette_kwargs=None,main_kwargs=True,main='main_form',**kwargs):
        if dialog_kwargs or palette_kwargs:
            formRoot = pane._makeFormRoot(formId,attachTo=pane,dialog_kwargs=dialog_kwargs,palette_kwargs=palette_kwargs,form_kwargs=kwargs)
        else:
            formRoot = pane
        default_kwargs = default_kwargs or dict()
        kwargs['subscribe_form_%s_goToRecord' %formId] = 'this.iframeFormManager.openrecord($1);'
        kwargs['subscribe_form_%s_load' %formId] = 'this.iframeFormManager.openrecord($1);'
        kwargs['subscribe_form_%s_dismiss' %formId] = 'this.iframeFormManager.closerecord($1);'
        kwargs['_iframeAttr'] = dict(main_th_formResource=formResource,src=src,main=main,**main_kwargs)
        kwargs['_fakeFormId'] = formId
        kwargs['_table'] = table
        kwargs['_formStoreKwargs'] = store_kwargs
        kwargs['_default_kwargs'] = default_kwargs
        return formRoot.contentPane(overflow='hidden',onCreated='this.iframeFormManager = new gnr.IframeFormManager(this);',**kwargs)


    @struct_method
    def fh_slotbar_form_navigation(self,pane,**kwargs):
        pane = pane.div(lbl='!!Navigation',_class='slotbar_group')
        pane.slotbar_form_dismiss()
        pane.slotbar_form_first()
        pane.slotbar_form_prev()
        pane.slotbar_form_next()
        pane.slotbar_form_last()
        
    @struct_method               
    def fh_slotbar_form_semaphore(self,pane,**kwargs):
        s = pane.div(_class='fh_semaphore',connect_onclick="""
            if(genro.dom.getEventModifiers($1)=='Shift'){
                if(this.form.status=='readOnly'){
                    this.form.reload({ignoreReadOnly:true})
                }
            }
            """)
        s.tooltip(callback="return this.form.getSemaphoreStatus()")

    
    @struct_method          
    def fh_slotbar_form_formcommands(self,pane,**kwargs):
        pane = pane.div(lbl='!!Form Commands',_class='slotbar_group')
        pane.slotbar_form_delete()
        pane.slotbar_form_add()
        pane.slotbar_form_revert()
        pane.slotbar_form_save()
        
        
    @struct_method          
    def fh_slotbar_form_dismiss(self,pane,caption=None,iconClass="iconbox dismiss" ,**kwargs):
        pane.formButton('!!Dismiss',iconClass=iconClass,
                    topic='navigationEvent',command='dismiss',**kwargs)
    
    @struct_method          
    def fh_slotbar_form_save(self,pane,always=False,**kwargs):
        pane.formButton('!!Save',topic='save',iconClass="iconbox save",parentForm=True,command=always)

    @struct_method          
    def fh_slotbar_form_revert(self,pane,**kwargs):
        pane.formButton('!!Revert',topic='reload',iconClass="iconbox revert", parentForm=True,
                       disabled='^.controller.changed?=!#v')
    
    @struct_method          
    def fh_slotbar_form_delete(self,pane,parentForm=True,**kwargs):
        pane.formButton(topic='deleteItem',
                        iconClass="iconbox delete_record",parentForm=parentForm,
                        disabled='==_newrecord||_protected',
                        _newrecord='^.controller.is_newrecord',
                        _protected='^.controller.protect_delete',tip='==_protected?_msg_protect_delete:_msg_delete',
                        _msg_protect_delete='!!This record cannot be deleted',_msg_delete='!!Delete current record',
                        **kwargs)
    @struct_method          
    def fh_slotbar_form_selectrecord(self,pane,table=None,**kwargs):
        fb = pane.formbuilder(cols=1, border_spacing='1px')
        table = table or pane.getInheritedAttributes()['table']
        tblobj = self.db.table(table)
        fb.dbselect(value="^.pkey",dbtable=table,
                    parentForm=False,condition=':pkeys IS NULL OR ($pkey IN :pkeys)',
                    #condition_pkeys='==this.form?this.form.store.parentStore? this.form.store.parentStore.currentPkeys():null:null;',
                    #validate_onAccept="if(userChange){this.form.publish('load',{destPkey:value})};",
                    hasDownArrow=True,
                    lbl=tblobj.name_long)
    
    @struct_method          
    def fh_slotbar_form_add(self,pane,parentForm=True,defaults=None,**kwargs):
        menupath = None
        if defaults:
            menubag = Bag()
            for i,(caption,default_kw) in enumerate(defaults):
                menubag.setItem('r_%i' %i,None,caption=caption,default_kw=default_kw)
            pane.data('.addrow_menu_store',menubag)
            menupath = '.addrow_menu_store'
            pane.slotButton('!!Add',action='this.form.newrecord($1.default_kw);',menupath=menupath,
                        iconClass="iconbox add_record",parentForm=parentForm,**kwargs)
        else:
            pane.formButton('!!Add',topic='navigationEvent',command='add',
                        iconClass="iconbox add_record",parentForm=parentForm,**kwargs)


    @struct_method          
    def fh_slotbar_form_duplicate(self,pane,parentForm=True,**kwargs):
        pane.formButton('!!Duplicate',iconClass='iconbox copy',
                       topic='navigationEvent',command='duplicate',parentForm=parentForm)

    @struct_method          
    def fh_slotbar_form_first(self,pane,**kwargs):
        pane.formButton('!!First',iconClass="iconbox first",
                    topic='navigationEvent',command='first',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.first || false);")
    
    @struct_method          
    def fh_slotbar_form_prev(self,pane,**kwargs):
        pane.formButton('!!Prev',iconClass="iconbox previous",
                    topic='navigationEvent',command='prev',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.first || false);")
    
    @struct_method          
    def fh_slotbar_form_next(self,pane,**kwargs):
        pane.formButton('!!Next',iconClass="iconbox next",
                    topic='navigationEvent',command='next',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.last || false);")

    @struct_method          
    def fh_slotbar_form_logicalDeleter(self,pane,**kwargs):
        table = pane.getInheritedAttributes()['table']
        logicalDeletionField = self.db.table(table).logicalDeletionField
        box = pane.div(_class='form_deleter',padding_right='5px')
        box.checkbox(value='^#FORM.controller.do_logical_delete',label='!!Hidden',
                    validate_onAccept="""
                    if(userChange){
                        var logical_deleted = this.form.isLogicalDeleted();
                        this.setRelativeData('#FORM.record.%s',value?new Date():null);  
                        this.form.save();
                    }
                    """ %logicalDeletionField,disabled=False)
        box.dataController("""SET #FORM.controller.do_logical_delete = logical_del_ts!=null;""",
                        logical_del_ts='^#FORM.record.%s' %logicalDeletionField)

            
    @struct_method          
    def fh_slotbar_form_last(self,pane,**kwargs):
        pane.formButton('!!Last',iconClass="iconbox last",
                    topic='navigationEvent',command='last',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.last || false);")

    @struct_method           
    def fh_formButton(self,pane,label=None,iconClass=None,topic=None,command=True,**kwargs):
        pane.slotButton(label, lbl=label,iconClass=iconClass,topic=topic,
                    action='this.form.publish(topic,{command:command,modifiers:genro.dom.getEventModifiers(event)});',command=command,
                    **kwargs)
    
    @struct_method 
    def fh_slotbar_form_locker(self,pane,**kwargs):
        pane.slotButton('!!Locker',iconClass='iconbox lock',showLabel=False,
                    action='this.form.publish("setLocked","toggle");',
                    disabled='==_pw||(_changed && !this.form.isDisabled())',
                    _pw='^#FORM.record?_protect_write',
                    _changed='^#FORM.controller.changed',
                    formsubscribe_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'iconbox lock':'iconbox unlock');""",
                    **kwargs)
        