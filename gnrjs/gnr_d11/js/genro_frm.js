/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_dlg : todo
 * Copyright (c) : 2004 - 2007 Softwell sas - Milano
 * Written by    : Giovanni Porcari, Francesco Cavazzana
 *                 Saverio Porcari, Francesco Porcari
 *--------------------------------------------------------------------------
 *This library is free software; you can redistribute it and/or
 *modify it under the terms of the GNU Lesser General Public
 *License as published by the Free Software Foundation; either
 *version 2.1 of the License, or (at your option) any later version.

 *This library is distributed in the hope that it will be useful,
 *but WITHOUT ANY WARRANTY; without even the implied warranty of
 *MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 *Lesser General Public License for more details.

 *You should have received a copy of the GNU Lesser General Public
 *License along with this library; if not, write to the Free Software
 *Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */


//######################## genro  #########################

dojo.declare("gnr.GnrFrmHandler", null, {
    constructor: function(sourceNode, formId, formDatapath, controllerPath, pkeyPath,formAttr) {
        var that = this;
        genro.src.onBuiltCall(function(){that.onStartForm();});
        for(var k in formAttr){
            this[k] = formAttr[k];
        }
        if(this.isRootForm){
            genro._rootForm = this;
        }
        if(this.subforms){
            this.subforms = this.subforms.split(',');
        }
        this.formId = formId;
        this.changed = false;
        this.gridEditors = {};
        this.opStatus = null;
        this.locked = this.locked || false;
        this.current_field = null;
        this.controllerPath = controllerPath;
        if(!this.store){
            this.controllerPath = this.controllerPath || 'gnr.forms.' + this.formId;
        }
        this.formDatapath = formDatapath;
        this.pkeyPath = pkeyPath;
        this.sourceNode = sourceNode;
        this.contentSourceNode = this.store? this.sourceNode.getValue().getNode('center'):sourceNode;
        
        this.frameCode = sourceNode.attr.frameCode;
        if(this.frameCode){
            this.formParentNode = genro.getFrameNode(this.frameCode,'frame').getParentNode().getParentNode();
        }else{
            this.formParentNode = this.sourceNode.getParentNode();
        }
        this.subscribe('save,reload,load,abort,loaded,setLocked,navigationEvent,newrecord,pendingChangesAnswer,dismiss,deleteItem,deleteConfirmAnswer,message');
        this._register = {};
        this._status_list = ['ok','error','changed','readOnly','noItem'];
        //this.store=new.....
        this.autoRegisterTags = {
            'textbox':null,
            'simpletextarea':null,
            'checkbox':null,
            'numbertextbox':null,
            'timetextbox':null,
            'horizzontalslider':null,
            'radiobutton':null,
            'verticalslider':null,
            'combobox':null,
            'filteringselect':null,
            'dbselect':null,
            'dbcombobox':null,
            'input':null,
            'textarea':null,
            'datetextbox':null,
            'geocoderfield':null
        };
        var tblname = this.getControllerData('table?name_long');
        var pref = tblname?tblname+' record':'Record'
        this.msg_saved = pref +' saved ';
        this.msg_deleted = pref +' deleted';

        this.msg_unsaved_changes ="Current record has been modified.";
        this.msg_confirm_delete ="You are going to delete the current record.";

    },
    getParentForm:function(){
        return this.sourceNode.getParentNode().getFormHandler();
    },

    onStartForm:function(kw){
        var kw = kw || {};
        this.formDomNode = this.sourceNode.getDomNode();
        this.formContentDomNode = this.contentSourceNode.getDomNode();
        if(this.store){
            var that = this;
            this.store.init(this);            
            var that = this;
            dojo.connect(this.formContentDomNode,'onclick',function(e){
                var wdg = dijit.getEnclosingWidget(e.target);
                if(wdg && wdg.isFocusable && !wdg.isFocusable() && wdg.sourceNode && (wdg.sourceNode.form != genro.activeForm)){
                   wdg.sourceNode.form.focusCurrentField();
                }
            });
            if(this.store.autoSave){
                this.autoSave = this.store.autoSave===true?1000:this.store.autoSave;
                this.sourceNode.watch('autoSave',
                        function(){
                                    if(that.record_changed && that.isValid() && !that.isNewRecord()){
                                        that.save({onSaved:'lazyReload'});
                                   };
                                   return false;},
                        function(){},that.autoSave);
            }
            var startKey = kw.startKey || this.store.startKey || this.getCurrentPkey();
            if(startKey){
                startKey = this.sourceNode.currentFromDatasource(startKey);
            }
            this.sourceNode.getAttributeFromDatasource(startKey);

            if(startKey){
                var that = this;
                this.sourceNode.watch('pageStarted',function(){return genro._pageStarted},function(){
                    console.log('inizio form')
                    that.load({destPkey:startKey});
                });
            }
            var parentForm = this.getParentForm();
            if(parentForm){
                //dojo.connect(parentForm,'load',this,'abort');
                parentForm.subscribe('onLoaded',function(kw){
                    if(kw.pkey!=that.parentFormPkey){
                        that.parentFormPkey = kw.pkey;
                        if(that.status!='noItem'){
                            that.abort();
                        }
                        that.publish('changedParent');
                    }
                });
            }
            
            var parentStore = this.store.parentStore;
            if(parentStore){
                parentStore.storeNode.subscribe('onLockChange',function(kw){
                    that.setLocked(kw.locked);
                },this.sourceNode);
                this.locked = parentStore.locked;
            }else if (parentForm){
                parentForm.subscribe('onLockChange',function(kw){
                    that.setLocked(kw.locked);
                },null,this.sourceNode);
                this.locked = parentForm.locked;
            }
            dojo.subscribe('onPageStart',function(){
                that.setLocked(that.locked);
                that.updateStatus();
            });
        }
    },

    reset: function() {
        this.resetChanges();
        this.resetInvalidFields();
    },
    publish: function(command,kw,topic_kw){
        var topic = {'topic':'form_'+this.formId+'_'+command,parent:this.publishToParent}; //iframe:'*' removed (useless?) it gives problem with multipage
        genro.publish(topic,kw);
    },

    message:function(kw){
        kw['duration_in'] = 3;
        kw['duration_out'] = 4;
        kw['yRatio'] = .8;
        genro.dlg.floatingMessage(this.sourceNode,kw);
    },

    subscribe: function(command,cb,scope,subscriberNode){
        if(command.indexOf(',')>=0){
            var that = this;
            dojo.forEach(command.split(','),function(command){
                that.subscribe(command);
            });
            return;
        }
        var topic = 'form_'+this.formId+'_'+command;
        var scope = scope || this;
        var cb = cb || this[command];
        subscriberNode = subscriberNode || this.sourceNode;
        subscriberNode.registerSubscription(topic,scope,cb);
    },

    applyDisabledStatus:function(){
        var disabled = this.isDisabled();
        this.publish('onDisabledChange',{disabled:disabled})
        genro.dom.setClass(this.sourceNode,'lockedContainer',disabled)
        var node,localdisabled;
        for (var k in this._register){
            node = this._register[k];
            localdisabled = 'disabled' in node.attr?node.getAttributeFromDatasource('disabled'):false;
            this._register[k].setDisabled(disabled || localdisabled);
        }
    },
    isDisabled:function(){
        return this.locked || this.status=='readOnly' || this.status=='noItem';
    },
    
    setLocked:function(value){
        if(value=='toggle'){
            value = !this.locked;
        }
        this.locked = value;
        this.applyDisabledStatus();
        this.setControllerData('locked',value);
        this.publish('onLockChange',{'locked':this.locked});
    },
    registerChild:function(sourceNode){
        if (sourceNode.attr.parentForm || (sourceNode.attr.tag.toLowerCase() in this.autoRegisterTags)){
            if(!this._firstField){
                if(sourceNode.attr.tag.toLowerCase() in this.autoRegisterTags){
                    this._firstField = sourceNode;
                }
            }
            this._register[sourceNode._id] = sourceNode;
            return;
        }
    },
    registerGridEditor:function(nodeId,gridEditor){
        this.gridEditors[nodeId] = gridEditor;
    },
    
    unregisterChild:function(sourceNode){
        if(this._register[sourceNode._id]){
            delete this._register[sourceNode._id];
        }
    },
    

    dismiss:function(modifiers){
        this.publish('navigationEvent',{'command':'dismiss',modifiers:modifiers});
    },
    resetChanges: function() {
        var formData = this.getFormData();
        if(formData){
            formData.subscribe('dataLogger',{'upd':dojo.hitch(this, "triggerUPD"),
                                                   'ins':dojo.hitch(this, "triggerINS"),
                                                   'del':dojo.hitch(this, "triggerDEL")
                                                  });
        }
        this.resetChangesLogger();
    },

    validateFromDatasource: function(sourceNode, value, trigger_reason) {
        // called when a widget changes its value because of a databag change, not an user action
        if (trigger_reason == 'container') {
            var result = genro.vld.validateInLoading(sourceNode, value);
        } else if (trigger_reason == 'node') {
            var result = genro.vld.validate(sourceNode, value);
            //console.log("value: " +value+" result: "+ result.toSource());
            if (result['modified']) {
                sourceNode.widget.setValue(result['value']);
            }
        }
        sourceNode.setValidationError(result);
        sourceNode.updateValidationStatus();
        //this.updateInvalidField(sourceNode, sourceNode.attrDatapath('value'));
    },
    reload: function(kw) {
        var kw = kw || {};
        this.load(objectUpdate({destPkey:this.getCurrentPkey()},kw));
    },
    load: function(kw) {
        if(this.opStatus=='loading'){
            return;
        }
        if(this.store && this.changed && this.saveOnChange && this.isValid()){
            var deferred = this.store.save();
            var that = this;
            deferred.addCallback(function(){
                that.reset();
                //that.do_load(kw);
            })
            return;
        }
        var kw = kw || {};
        if (this.store){
            if(!kw.destPkey && this.store.base_handler_type=='subform'){
                kw.destPkey="*subform*";
            }
            kw.destPkey = kw.destPkey || '*norecord*';
            if(kw['destPkey']=='*norecord*'){
                kw['destPkey'] = null;
                this.store.setNavigationStatus('*norecord*');
                this.setFormData();
                this.setCurrentPkey();
                this.loaded();
            }
            this.load_store(kw);
        }else{
            if ('destPkey' in kw) {
                var currentPkey = this.getCurrentPkey();
                if (this.changed && (kw.destPkey != currentPkey)) {
                    this.openPendingChangesDlg(kw);
                    return;
                }
            }
            this.doload_loader(kw);
        }
    },
    
    load_store:function(kw){
        var currentPkey = this.getCurrentPkey();
        if (this.changed && kw.destPkey &&(currentPkey=='*newrecord*' || (kw.destPkey != currentPkey))) {
            if(kw.modifiers=='Shift' || this.autoSave){
                this.save(kw);
            }else{
                this.openPendingChangesDlg(kw);
            }
            return;
        }
        this.doload_store(kw);
    },
    
    abort:function(){
        this.doload_store({destPkey:'*dismiss*'});
    },
    
    norecord:function(){
        this.load({destPkey:'*norecord*'});
    },

    newrecord:function(default_kw){
        this.load({destPkey:'*newrecord*', default_kw:default_kw});
    },
    
    deleteItem:function(kw){
        this.deleteConfirmDlg(kw);
    },
    
    deleteConfirmDlg:function(kw){
         var dlg = genro.dlg.quickDialog('Alert',{_showParent:true,width:'280px'});
         dlg.center._('div',{innerHTML:this.msg_confirm_delete, text_align:'center',_class:'alertBodyMessage'});
         var form = this;
         var slotbar = dlg.bottom._('slotBar',{slots:'*,cancel,delete',
                                                action:function(){
                                                    dlg.close_action();
                                                    kw.command = this.attr.command;
                                                    form.publish('deleteConfirmAnswer',kw);
                                                }});
         slotbar._('button','cancel',{label:'Cancel',command:'cancel'});
         slotbar._('button','delete',{label:'Delete',command:'deleteItem'});
         dlg.show_action();
     },
     
    
    deleteConfirmAnswer:function(kw){
        var command = objectPop(kw,'command');
        if(this.store){
            var that = this;
            if(command=='deleteItem'){
                this.do_deleteItem(kw);
            }else{
                if(kw.cancelCb){
                    kw.cancelCb();
                }
                this.publish('onCancel',{formEvent:'deleteRecord'});
            }
        }
    },
    
    do_deleteItem:function(kw){
        kw = {}
        kw.pkey = kw.pkey || this.getCurrentPkey();
        var r = this.store.deleteItem(kw.pkey,kw);
        if(kw.onDeleted){
            var onDeleted = funcCreate(kw.onDeleted,'result',this);
            if(r instanceof dojo.Deferred){
                r.addCallback(onDeleted);
            }else{
                onDeleted(r);
            }
        }
    },
    
    pendingChangesAnswer:function(kw){
        var command = objectPop(kw,'command');
        if(this.store){
            var that = this;
            if(command=='save'){
                this.save({destPkey:kw.destPkey});
            }
            else if(command=='discard'){
                this.doload_store(kw);
            }else{
                var cancelCb = kw.cancelCb || this.cancelCb;
                if(cancelCb){
                    cancelCb = funcCreate(cancelCb);
                    cancelCb();
                }
                this.publish('onCancel',{formEvent:'loadRecord'});
            }
            
            
        }else{
            var that = this;
            if(command=='save'){
                this.setCurrentPkey(kw.destPkey);
                this.save();
            }
            else if(command=='discard'){
                this.doload_loader(kw);
            }else{
                if(kw.cancelCb){
                    kw.cancelCb();
                }
            }
        }
    },
    waitingStatus:function(waiting){
        this.sourceNode.setHiderLayer(waiting,{message:'<div class="form_waiting"></div>',z_index:999999});
    },
    
    openPendingChangesDlg:function(kw){
         var dlg = genro.dlg.quickDialog('Pending changes',{_showParent:true,width:'280px'});
         dlg.center._('div',{innerHTML:this.msg_unsaved_changes, text_align:'center',_class:'alertBodyMessage'});
         var form = this;
         var slotbar = dlg.bottom._('slotBar',{slots:'discard,*,cancel,save',
                                                action:function(){
                                                    dlg.close_action();
                                                    kw.command = this.attr.command;
                                                    form.publish('pendingChangesAnswer',kw);
                                                }});
         slotbar._('button','discard',{label:'Discard changes',command:'discard'});
         slotbar._('button','cancel',{label:'Cancel',command:'cancel'});
         slotbar._('button','save',{label:'Save',command:'save'});
         dlg.show_action();
     },
     
    setOpStatus:function(opStatus){
        this.opStatus=opStatus;
        this.publish('onSetOpStatus',this.opStatus);
    },
    doload_loader:function(kw){
        var kw = kw || {};
        var sync = kw.sync;
        this.setControllerData('loading',true);
        this.setOpStatus('loading');
        if ('destPkey' in kw) {
            var destPkey = kw.destPkey || '*newrecord*';
            this.setCurrentPkey(destPkey);
        }
        if (!sync) {
            this.setHider(true);
        }
        this.resetInvalidFields(); // reset invalid fields before loading to intercept required fields during loading process
        genro.setData('_temp.grids', null);
        var loaderNode = genro.nodeById(this.formId + '_loader');
        if (loaderNode) {
            loaderNode.fireNode();
            if (sync) {
                this.loaded();
            }
        } else  {
          console.log('missing loader');
          this.loaded();
        }
    },
    doload_store: function(kw) {
        if(kw.destPkey=='*dismiss*'){
            for(var k in this.gridEditors){
                this.gridEditors[k].resetEditor();
            }
            this.reset();
            this.setCurrentPkey(null);
            if(this.store.parentStore){
                this.store.parentStore.onEndEditItem(this);
            };
            genro.callAfter(function(){
                genro.dlg.removeFloatingMessage(this.sourceNode);
                this.publish('onDismissed');
            },('onReload' in kw)?1000:1,this);
            
            return;
        }else if(kw['destPkey'] == '*duplicate*'){
            this.store.duplicateRecord(null, kw.howmany);
            return;
        }
        var kw = kw || {};
        var sync = kw.sync;
        this.setControllerData('loading',true);
        var pkey= ('destPkey' in kw)? kw.destPkey : this.store.getStartPkey();
        this.setCurrentPkey(pkey);
        this.publish('onLoading',{destPkey:pkey});
        if(pkey){
            if (!sync && !this.autoSave) {
                this.setHider(true);
            }
            this.resetInvalidFields(); // reset invalid fields before loading to intercept required fields during loading process
            this.setOpStatus('loading',pkey);
            var deferredOrResult = this.store.load(kw);
            if(kw.onReload){
                if(deferredOrResult instanceof dojo.Deferred){
                    deferredOrResult.addCallback(kw.onReload);
                }else{
                    kw.onReload(deferredOrResult);
                }
            }
        }else{
            this.updateStatus();
            this.applyDisabledStatus();
        }
    },
    setHider:function(show){
        this.sourceNode.setHiderLayer(show);
    },

    deleted:function(result,kw){
        var destPkey = kw.destPkey || '*dismiss*';
        this.load({destPkey:destPkey});
        this.publish('message',{message:this.msg_deleted,sound:'$ondeleted'});
        this.publish('onDeleted');
    },

    loaded: function(data) {
        var controllerData = this.getControllerData();
        controllerData.setItem('temp',null);
        if(data){
            this.setFormData(data);
        }
        this.publish('onLoaded',{pkey:this.getCurrentPkey(),data:data});
        this.setHider(false);
        this.resetChanges(); // reset changes after loading to subscribe the triggers to the current new data bag
        this.protect_write = this.isProtectWrite();
        genro.dom.setClass(this.sourceNode,'form_logical_deleted',this.isLogicalDeleted());
        genro.dom.setClass(this.sourceNode,'form_protect_write',this.protect_write);
        genro.dom.setClass(this.sourceNode,'form_draft',this.isDraft());

        this.protect_delete = this.isProtectDelete();
        genro.dom.setClass(this.sourceNode,'form_protect_delete',this.protect_delete);

        this.newRecord = this.isNewRecord();
        genro.dom.setClass(this.sourceNode,'form_new_record',this.newRecord);
        this._recordcaption = data instanceof gnr.GnrBagNode?data.attr.caption:'';
        controllerData.setItem('protect_write',this.protect_write,null,{lazySet:true});
        controllerData.setItem('protect_delete',this.protect_delete,null,{lazySet:true});
        controllerData.setItem('is_newrecord',this.newRecord,null,{lazySet:true});
        controllerData.setItem('loading',false,null,{lazySet:true});
        var loadedPkey = (this.getCurrentPkey() || '*norecord*');
        var that = this;
        setTimeout(function(){controllerData.fireItem('loaded',loadedPkey);},1);
        this.updateStatus();
        this.setOpStatus();
        this.currentFocused = null;
        if(this.store){
            //if(this.status=='readOnly'){
            //    this.setLocked(true);
            //}
            if(this.store.parentStore){
                this.store.parentStore.onStartEditItem(this);
            };
            this.applyDisabledStatus();
            //this.focus()
            var that = this;
            setTimeout(function(){    
                that.focus();
            },1);
        }
    },
    
    getRecordCaption:function(){
        return this._recordcaption;
    },
    
    focus:function(node){
        if(!this.isDisabled()){
            var formContentDomNode = this.formContentDomNode || this.sourceNode.widget.domNode;
            if(this.sourceNode.widget.getSelected){
                formContentDomNode = this.sourceNode.widget.getSelected().domNode;
            }
            if(!node && this._firstField){
                node = this._firstField.widget?this._firstField.widget.focusNode:this._firstField.domNode;
            }
            if(node){
                node.focus();
            }
        }
    },
    onFocusForm:function(){
        genro.dom.addClass(this.sourceNode,'form_activeForm');
        this.focusCurrentField();
    },
    
    onBlurForm:function(){
        genro.dom.removeClass(this.sourceNode,'form_activeForm');
    },
    
    isRegisteredWidget:function(wdg){
        return (wdg.sourceNode._id in this._register);
    },
    onFocusElement:function(wdg){
        if(this.isRegisteredWidget(wdg) && (typeof(wdg.focus)=='function')){
            this.currentFocused=wdg;
        }
    },
    focusCurrentField:function(e){
        if(!this.isDisabled()){
            if(this.currentFocused){
                this.currentFocused.focus();
            }
        }
    },

    copyPasteMenu:function(){
        var result = new gnr.GnrBag();
        var currentPkey = this.getCurrentPkey();
        var that = this;
        var clipboard = this.getControllerData('clipboard');
        var disabled = this.isDisabled();
        var copyDisabled = currentPkey==null || currentPkey=='*newrecord*' || this.changed;
        result.setItem('r_0',null,{caption:_T('Copy current record'),
                                   disabled:copyDisabled,
                                   action:function(){that.copyCurrentRecord();}}
                                   );
        if(clipboard){
            result.setItem('r_1',null,{caption:'-'});
            clipboard.forEach(function(n){
                result.setItem(n.label,null,{caption:n.attr.caption,action:function(item){that.pasteClipboard(item.fullpath)},disabled:disabled});
            });
        }
            
        result.setItem('r_2',null,{caption:'-'});
        result.setItem('r_3',null,{caption:_T('Clear clipboard')});

        return result;
    },
    copyCurrentRecord:function(){
        var controller = this.getControllerData();
        var clipboard = controller.getItem('clipboard') || new gnr.GnrBag();
        var copy = new gnr.GnrBag();
        var record = this.getFormData();
        var pkeyField =
        record.forEach(function(n){
            if(n.label[0]!='@' && n.label[0]!='$' && !n.attr._sysfield){
                var value = n._value;
                if (value==null || value==undefined || value==''){
                    return;
                }
                if(value instanceof gnr.GnrBag){
                    value = value.deepCopy();
                }
                copy.setItem(n.label,value,n.attr);
            }
        },'static');
        clipboard.setItem(this.getCurrentPkey(),copy,{caption:this.getRecordCaption()})
        controller.setItem('clipboard',clipboard);
    },

    pasteClipboard:function(path){
        var controllerdata = this.getControllerData();
        var clipboard = controllerdata.getItem('clipboard')
        var copy = clipboard.getNode(path);
        var copybag = copy.getValue().deepCopy();
        var currdata = this.getFormData();
        copybag.forEach(function(n){
            var value = n._value;
            var currnode = currdata.getNode(n.label);
            var currvalue = currnode._value;
            if(currvalue && currvalue instanceof gnr.GnrBag){
                currvalue.update(value.deepCopy());
            }else{
                currnode.setValue(value);
            }
        });
    },
    clearClipboard:function(){
        this.getControllerData().setItem('clipboard',new gnr.GnrBag());
    },
    checkPendingGridEditor:function(){
        var pendingEditor;
        for(var k in this.gridEditors){
            if(this.gridEditors[k]._exitCellTimeout){
                pendingEditor = this.gridEditors[k];
                break;
            }
        }
        return pendingEditor;
        
    },
    save: function(kw,modifiers) {
        var pendingEditor = this.checkPendingGridEditor(kw,modifiers);
        if(pendingEditor){
            var that = this;
            this.sourceNode.watch('pendingEditor',function(){return pendingEditor._exitCellTimeout==null;},
                                    function(){
                                        that.save(kw,modifiers);
                                    });
            return;
        }
        var kw = kw || {};
        var always;
        if (typeof(kw)=='object'){
            always=kw.command;
        }else{
            always = kw;
            kw = {};
        }
        if (!this.opStatus) {
            var always = always || this.getControllerData('is_newrecord');
            var invalid = !this.isValid();
            if (invalid) {
                this.fireControllerData('save_failed','invalid');
                return 'invalid:'+invalid;
            }
            if (this.changed || always || this.isNewRecord()) {
                return this.do_save(kw);
            } else {
                this.fireControllerData('save_failed','nochange');
                if(kw.destPkey){
                    this.load({destPkey:kw.destPkey});
                }
            }
        }
        else if(!this.autoSave){
            genro.playSound('Basso');
            return false;
        }
    },

    do_save:function(kw){
        var destPkey = kw.destPkey;
        this.setOpStatus('saving');
        this.fireControllerData('saving');
        var saverNode = genro.nodeById(this.formId + '_saver');
        if(saverNode){
            saverNode.fireNode();
            return saverNode._lastDeferred;
        }else if(this.store) {
            var waitingStatus = objectPop(kw,'waitingStatus') || this.store.handlers.save.kw.waitingStatus;
            this.waitingStatus(waitingStatus);
            var onSaved = objectPop(kw,'onSaved') || this.store.onSaved;
            if(destPkey=='*dismiss*'){
                onSaved = 'dismiss';
            }
            var onReload = objectPop(kw,'onReload');
            var deferred=this.store.save(kw);
            var that,cb;
            that = this;
            if(onSaved=='reload' ||(destPkey&&(destPkey!=this.getCurrentPkey()))|| this.isNewRecord()){
                cb=function(resultDict){
                    resultDict = resultDict || {};
                    if (resultDict.error){
                        genro.dlg.alert(resultDict.error,'Error');
                        that.setOpStatus();
                        return;
                    }
                    destPkey = destPkey || resultDict.savedPkey;
                    if(resultDict.loadedRecordNode){
                        that.setCurrentPkey(destPkey);
                        that.store.loaded(destPkey,resultDict.loadedRecordNode);
                    }else if(destPkey=='*duplicate*'){
                        that.store.duplicateRecord(resultDict.savedPkey, kw.howmany);
                    }else{
                        that.setCurrentPkey(destPkey);
                        if(that.store){
                            that.doload_store({'destPkey':destPkey,'onReload':onReload});
                        }else{
                            that.doload_loader({'destPkey':destPkey});
                        }
                    }
                };
            }else{
                cb=function(result){
                    that.reset();
                    if(onSaved in that){
                        that[onSaved](result);
                    }else if(onSaved){
                        funcApply(onSaved,{result:result},this);
                    }
                };
            }
            if(deferred){
                deferred.addCallback(function(result){
                    cb(result);
                    return result;
                });
            }
            return deferred;

        }
    },
    lazyReload:function(result){
        var savedPkey = result.savedPkey;
        this.setCurrentPkey(savedPkey);
        var data = this.getFormData();
        data.walk(function(n){ delete n.attr._loadedValue},'static');
        if(result.savedAttr.lastTS){
            data.getParentNode().attr.lastTS = result.savedAttr.lastTS;
            data.setItem('__mod_ts',convertFromText(result.savedAttr.lastTS),null,{doTrigger:false});
        }
        this.setOpStatus();
    },

    setKeptData:function(valuepath,value,set){
        var keptData = this.keptData || {};
        if(set){
            keptData[valuepath] = value;
        }else{
            objectPop(keptData,valuepath); 
        }
        this.keptData = objectNotEmpty(keptData)?keptData:null;
    },

    saved: function(result) {
        this.waitingStatus(false);
        this.fireControllerData('saved');
        this.setOpStatus('saved');
        var savedPkey = result;
        if(this.store && result){
            savedPkey = result.savedPkey;
        }
        this.publish('onSaved',{pkey:savedPkey,saveResult:result});
        if(!this.autoSave){
            this.publish('message',{message:this.msg_saved,sound:'$onsaved'});
        }
        return result;

    },

    openForm:function(idx, pkey) {
        if(this.store && false){
            //console.log('idx',idx,'pkey',pkey);
            this.load({destPkey:pkey});
        }else{
            this.fireControllerData('openFormPkey',pkey);
            this.fireControllerData('openFormIdx',idx);
        }
    },
    getFormData: function() {
        return this.sourceNode.getRelativeData(this.formDatapath, true, new gnr.GnrBag());
    },
    getControllerData: function(path) {
        var cd = this.sourceNode.getRelativeData(this.controllerPath, true, new gnr.GnrBag());
        return path?cd.getItem(path):cd;
    },
    setControllerData: function(path,value) {
        this.getControllerData().setItem(path,value,null,{lazySet:true});
    },
    fireControllerData: function(path,value,reason) {
        this.getControllerData().fireItem(path,value,reason);
    },
    setFormData:function(data){
        if(data && this.keptData){
            var newrecord = data.attr._newrecord;
            var n;
            var record = data._value;
            for(var k in this.keptData){
                n = record.getNode(k);
                if(newrecord){
                    n.setValue(this.keptData[k]);
                }
                n.attr._keep = true;
            }
        }
        var data = data || new gnr.GnrBag();
        this.sourceNode.setRelativeData(this.formDatapath,data);
    },
    getDataNodeAttributes:function(){
        var data = this.sourceNode.getRelativeData(this.formDatapath);
        if(data){
            return data.getParentNode().attr;
        }
        return {};
        
    },
    isNewRecord:function(){
        return this.getDataNodeAttributes()._newrecord;
    },
    isProtectWrite:function(){
        var parentForm = this.getParentForm();
        var protect_write = this.getDataNodeAttributes()._protect_write;
        if (parentForm){
            protect_write = protect_write || parentForm.isProtectWrite();
        }
        return protect_write || this.readOnly || false;
    },
    
    isLogicalDeleted:function(){
        var logical_deleted = this.getDataNodeAttributes()._logical_deleted;
        return logical_deleted;
    },

    isDraft:function(){
        return this.getDataNodeAttributes()._draft;
    },

    setDraft:function(set){
        this.sourceNode.setRelativeData('.record.__is_draft',set);
        this.getDataNodeAttributes()._draft = set;
        genro.dom.setClass(this.sourceNode,'form_draft',set);
    },


    
    isProtectDelete:function(){
        return this.getDataNodeAttributes()._protect_delete;
    },
    
    hasChanges: function() {
        return this.getControllerData('changed'); 
    },
    getFormChanges: function() {
        var data = this._getRecordCluster(this.getFormData(), true);
        for(var k in this.gridEditors){
            var changeset = this.gridEditors[k].getChangeset();
            if(this.gridEditors[k].table && changeset.len()>0){
                data.setItem('grids.'+k,changeset,{table:this.gridEditors[k].table});
            }
        }
        return data;
    },
    getFormCluster: function() {
        return this._getRecordCluster(this.getFormData(), false);
    },
    getCurrentPkey:function(){
        return this.pkeyPath ? this.sourceNode.getRelativeData(this.pkeyPath) : null;
    },
    setCurrentPkey:function(pkey){
        this.sourceNode.setRelativeData(this.pkeyPath,pkey);
    },
    getVirtualColumns:function() {
        var virtual_columns = [];
        this.sourceNode._value.walk(function(n) {
            if (n.attr._virtual_column) {
                virtual_columns.push(n.attr._virtual_column);
            }
        },'static');
        return virtual_columns.join(',');
    },


    _getRecordCluster: function(record, changesOnly, result, removed, parentpath) {
        if (record) {
            var parentpath = parentpath || this.sourceNode.absDatapath(this.formDatapath);
            var data = new gnr.GnrBag();
            data.__isRealChange = false;
            var node, sendBag, value, currpath, sendback;
            var recInfo = record.attributes();
            var isNewRecord = recInfo._newrecord;
            var bagnodes = record.getNodes();
            for (var i = 0; i < bagnodes.length; i++) {
                node = bagnodes[i];
                sendback = changesOnly ? node.attr._sendback: true;
                if (sendback == false || node.label.slice(0, 1) == '$' || node.attr.virtual_column) {
                    continue;
                }
                currpath = parentpath ? parentpath + '.' + node.label : node.label;
                value = node.getValue('static');
                if (removed) {
                    data.setItem(node.label, null, objectUpdate(node.attr, {'_deleterecord':true}));
                    data.__isRealChange = true;
                }
                else if (stringEndsWith(node.label, '_removed')) {
                    this._getRecordCluster(value, changesOnly, data, true, currpath);
                }
                else if ((node.attr.mode == 'O') || (node.attr.mode == 'M') || ('_pkey' in node.attr)) {
                    this._getRecordCluster(value, changesOnly, data, false, currpath);
                }
                else if (value instanceof gnr.GnrBag) {
                    sendBag = (sendback == true) || isNewRecord || this.hasChangesAtPath(currpath);
                    if (sendBag) {
                        value.walk(function(n){
                            if('_loadedValue' in n.attr){
                                var loadedValue = objectPop(n.attr,'_loadedValue');
                                n.attr.__old = asTypedTxt(loadedValue, n.attr.dtype);
                            }
                        },'static');
                        if(value.len()>0 || !isNewRecord){
                            data.setItem(node.label, value, objectUpdate({'_gnrbag':true}, node.attr));
                            data.__isRealChange = true;
                        }
                    }
                }
                else if ((sendback == true) || (isNewRecord && value != null) || ('_loadedValue' in node.attr)) {
                    var attr_dict = {'dtype':node.attr.dtype};
                    if ('_loadedValue' in node.attr) {
                        attr_dict.oldValue = asTypedTxt(node.attr._loadedValue, attr_dict['dtype']);
                        data.__isRealChange = true;
                    }
                    if (recInfo._alwaysSaveRecord) {
                        data.__isRealChange = true;
                    }
                    data.setItem(node.label, value, attr_dict);
                }
            }
            if (((data.len() > 0) && (data.__isRealChange)) || (!result)) {
                var result = result || new gnr.GnrBag();
                var recordNode = record.getParentNode();
                var resultattr = objectExtract(recordNode.attr, '_pkey,_newrecord,lastTS,mode,one_one', true);
                result.setItem(recordNode.label, data, resultattr);
                result.__isRealChange = data.__isRealChange;
            }
            return result;
        }
    },

    triggerUPD: function(kw) {
        //var path = this._dataLogger.path;

        /*
         if ( kw.reason=='selected_' && kw.pathlist[0][0]=='@'){// avoid to change related records from dbselect
         return;
         }*/
        if (kw.reason == 'resolver' || kw.node.getFullpath().indexOf('$') > 0) {
            return;
        }
        if( kw.value==kw.oldvalue || (isNullOrBlank(kw.value) && isNullOrBlank(kw.oldvalue))){
            return;
        }
        ;
        if (kw.value instanceof gnr.GnrBag) {
            //console.log('dataChangeLogger event: ' + kw.evt + ' is Bag ' + path)
        } else if (kw.evt == 'upd') {
            if (kw.updvalue) {
                var changed = null;
                var changes = this.getChangesLogger();
                var changekey = this.getChangeKey(kw.node);

                if (!('_loadedValue' in kw.node.attr)) {//has never been changed before
                    kw.node.attr._loadedValue = kw.oldvalue;
                    changed = true;
                    //console.log('dataChangeLogger NEWCHANGE: ' + path);
                } else if (kw.node.attr._loadedValue == kw.value || ( isNullOrBlank(kw.value) && isNullOrBlank(kw.node.attr._loadedValue) )) {//value = _loadedValue
                    delete kw.node.attr._loadedValue;
                    changed = false;
                    //console.log('dataChangeLogger UNCHANGED: ' + path);
                }

                if (changed) {
                    changes.setItem(changekey, null);
                } else if (changed === false) {
                    changes.pop(changekey);
                }
                // if changed == null is a modification of a yet modified value, do nothing

                this.updateStatus();
                //this.updateInvalidField(kw.reason, changekey);
            } else {
                //changed attributes
            }
        } else {
            //console.log('dataChangeLogger event: ' + kw.evt + ' updattr:' + kw.updattr +' - ' + path)
        }
    },
    triggerINS: function(kw) {
        if (kw.node.getFullpath().indexOf('$') > 0) {
            return;
        }
        ;
        if (kw.reason == 'autocreate' || kw.reason == '_removedRow') { // || kw.reason==true){
            return;
        }
        var changes = this.getChangesLogger();
        if(!('_loadedValue' in kw.node.attr)){
            kw.node.attr._loadedValue = null;
        }
        var changekey = this.getChangeKey(kw.node);
        changes.setItem(changekey, null, {isNewNode: true});
        this.updateStatus();
        //this.updateInvalidField(kw.reason, changekey);
    },
    triggerDEL: function(kw) {
        var changes = this.getChangesLogger();
        var changekey = this.getChangeKey(kw.node);
        if (changes.getAttr(changekey, 'isNewNode')) {
            changes.pop(changekey);
        } else {
            changes.setItem(changekey, null);
        }
        dojo.forEach(changes.getNodes(),function(n){
            if((changekey!=n.label) && (n.label.indexOf(changekey)==0)){
                changes.popNode(n.label);
            }
        });
        this.updateStatus();
    },
    getChangeKey:function(changekey) {
        if (typeof(changekey) != 'string') {//changekey is a data node
            changekey = changekey.getFullpath(null, true);
        }
        return changekey.replace(/[\.\?]/g, '_');
    },
    isNodeInFormData:function(datanode){
        if(!datanode){
            return false;
        }
        var res =  datanode.isChildOf(this.getFormData());
        return res;
    },
    updateInvalidField:function(sourceNode, changepath) {
        var changeDataNode = genro.getDataNode(changepath);
        if(!this.isNodeInFormData(changeDataNode)){
            return;
        }
        if (sourceNode == true) {
            return;
        }
        var changekey = this.getChangeKey(changepath);
        if (changekey.indexOf('emptypath') >= 0) {
            return; // PROVVISORIO per includedview con form
        }
        var invalidfields = this.getInvalidFields();
        var invalidnodes = invalidfields.getItem(changekey);

        var sourceNode_id = sourceNode.getStringId();
        if (sourceNode.hasValidationError()) {
            //console.log("add validation error: "+changekey);
            if (!invalidnodes) {
                invalidnodes = {};
                invalidfields.setItem(changekey, invalidnodes);
            }
            invalidnodes[sourceNode_id] = sourceNode;
        } else {
            //console.log("remove validation error: "+changekey);
            objectPop(invalidnodes, sourceNode_id);
            if (!objectNotEmpty(invalidnodes)) {
                invalidfields.pop(changekey);
            }
        }
        this.updateStatus();
    },
    isValid:function(){
        return ((this.getInvalidFields().len() == 0) && (this.getInvalidDojo().len()==0)) && this.registeredGridsStatus()!='error';
    },
    registeredGridsStatus:function(){
        var status = null;
        for(var k in this.gridEditors){
            var gridstatus=this.gridEditors[k].status;
            if(gridstatus=='error'){
                return 'error';
            }else if(gridstatus=='changed'){
                status = gridstatus;
            }
        }
        return status;
    },
    updateStatus:function(){
        var isValid = this.isValid();
        this.setControllerData('valid',isValid);
        var status;
        //this.contentSourceNode.setHiderLayer(false,{});
        var changes = this.getChangesLogger();
        var changed = (changes.len() > 0 || this.registeredGridsStatus()=='changed');
        this.record_changed = changes.len() > 0;
        this.changed = changed;
        this.setControllerData('record_changed',this.record_changed);
        this.setControllerData('changed',changed);
        if(this.pkeyPath && !this.getCurrentPkey()){
            status = 'noItem';
            //this.contentSourceNode.setHiderLayer(true,{z_index:10});
        }
        else if(this.isProtectWrite()){
            status = 'readOnly';
        }
        else if(!isValid){
            status = 'error';
        }
        else{
            status = this.changed ? 'changed':'ok';
        }
        if(this.status!=status){
            this.status=status;
            this.publish('onStatusChange',{'status':this.status});
            var formDomNode = this.formDomNode;
            var side;
            var formNodeWdg = this.sourceNode.widget;
            dojo.forEach(this._status_list,function(st){
                genro.dom.setClass(formDomNode,'form_'+st,st==status);
                for(var sidename in {'top':true,'bottom':true,'left':true,'right':true}){
                    side = formNodeWdg['_'+sidename];
                    if(side){
                        genro.dom.setClass(side,'formside_'+st,st==status);
                    }
                }
            });
        }
    },
    checkInvalidFields: function() {
        var node, sourceNode, changekey;
        var invalidfields = this.getInvalidFields();
        var invalidnodes = invalidfields.getNodes();
        for (var i = 0; i < invalidnodes.length; i++) {
            node = invalidnodes[i];
            sourceNode = node.getValue();
            changekey = node.label;
            result = genro.vld.validate(sourceNode, sourceNode);
            if (result['modified']) {
                sourceNode.widget.setValue(result['value']);
            }
            sourceNode.setValidationError(result);
            return result['value'];
        }
    },
    dojoValidation:function(wdg,isValid){
        var node_identifier=wdg.sourceNode.getStringId();
        var dojoValid=this.getInvalidDojo();
        var changedNode = genro.getDataNode(wdg.sourceNode.absDatapath(wdg.sourceNode.attr.value));
        if(!this.isNodeInFormData(changedNode)){
            return;
        }
        if(isValid){
            dojoValid.popNode(node_identifier);
        }else{
            dojoValid.setItem(node_identifier,null);
        }
        this.updateStatus();
    },
    
    focusFirstInvalidField: function() {
        if (dojo.isIE > 0) {
            return;
        }
        var invalidFields = this.getInvalidFields();
        var first = invalidFields.getItem("#0");
        var key = objectKeyByIdx(first, 0);
        first[key].widget.focus();
    },
    getInvalidFields: function() {
        return this.getControllerData().getItem('invalidFields') || new gnr.GnrBag();
    },
    getInvalidDojo: function() {
        return this.getControllerData().getItem('invalidDojo') || new gnr.GnrBag();
    },
    
    resetInvalidFields:function(){
        this.getControllerData().setItem('invalidFields',new gnr.GnrBag());
        this.getControllerData().setItem('invalidDojo',new gnr.GnrBag());
        this.updateStatus();
    },
    getChangesLogger: function() {
        return this.getControllerData().getItem('changesLogger') || new gnr.GnrBag();
    },
    resetChangesLogger:function(){
        this.getControllerData().setItem('changesLogger',new gnr.GnrBag());
        this.updateStatus();
    },

    hasChangesAtPath:function(path) {
        var changesLogger = this.getChangesLogger();
        var chpath = path.replace(/\./g, '_');
        var labels = changesLogger.keys();
        for (var i = 0; i < labels.length; i++) {
            if (stringStartsWith(labels[i], chpath)) {
                return true;
            }   
        }
    },
    
    navigationEvent:function(kw){
        var loadkw={modifiers:kw.modifiers,cancelCb:kw.cancelCb}
        var command = kw.command;
        if(command=='add'){
            loadkw.destPkey = '*newrecord*';
        }else if (command=='dismiss'){
            loadkw.destPkey = '*dismiss*';
        }else if(command=='duplicate'){
            loadkw.destPkey = '*duplicate*';
            loadkw.howmany = kw.howmany
        }
        else{
            loadkw.destPkey = this.store.navigationEvent(kw);
        }
         this.load(loadkw);
        
    }  
});

dojo.declare("gnr.GnrValidator", null, {
    validationTags: ['dbselect','notnull','empty','case','len','min','max','email','regex','call','gridnodup','nodup','exist','remote'],
    getCurrentValidations: function(sourceNode) {
        return sourceNode.evaluateOnNode(objectExtract(sourceNode.attr, 'validate_*', true));
    },
    validateInLoading: function(sourceNode, value) {
        var validations = this.getCurrentValidations(sourceNode);
        return this._validate(sourceNode, value, validations, ['notnull']);
    },
    validate: function(sourceNode, value, userChange,validateOnly) {
        var validations = this.getCurrentValidations(sourceNode);
        var result = this._validate(sourceNode, value, validations, this.validationTags, userChange); //userChange added by sporcari
        if(!validateOnly){
            this.exitValidation(result, sourceNode, validations, userChange);
        }
        return result;
    },
    _validate: function(sourceNode, value, validations, validationTags, userChange) {
        var validation, validreturn;
        var result = {'warnings':[]};
        result['value'] = value;
        var parameters = objectUpdate({}, validations);
        parameters.userChange = userChange; //added by sporcari userChange was not in _validate params
        objectExtract(parameters, this.validationTags.join(','));
        for (var i = 0; i < validationTags.length; i++) {
            validation = validationTags[i];
            if ((validation in validations) && ((validations[validation]) || (validations[validation] === 0))) {
                validreturn = this.callValidation(validation, result['value'], sourceNode, validations, parameters);
                if (validreturn != true) {
                    if (validreturn['required']) {
                        result['required'] = validreturn['required'];
                    }
                    if (validreturn['modified']) {
                        result['value'] = validreturn['value'];
                        result['modified'] = true;
                    }
                    if (validreturn['errorcode']) {
                        if (validreturn['iswarning']) {
                            result['warnings'].push(validreturn['message']);
                        } else {
                            result['error'] = validreturn['message'];
                            break;
                        }
                    }
                }
            }
        }
        ;
        return result;
    },
    
    callValidation: function(validation, value, sourceNode, validations, parameters) {
        var errorcode, modified, iswarning, errormessage;

        var val_condition = objectPop(validations, validation + '_if');
        if (val_condition) {
            var satisfy_cond = funcApply('return ' + val_condition, objectUpdate({'value':value}, parameters), sourceNode);
            if (!satisfy_cond) {
                return true;
            }
        }
        if (validation + '_iswarning' in validations) {
            iswarning = validations[validation + '_iswarning'];
        } else {
            iswarning = ((validations[validation + '_warning']) && (!validations[validation + '_error']));
        }

        var validHandler = this['validate_' + validation];
        var validreturn = validHandler.call(this, validations[validation], value, sourceNode, parameters);
        if ((validreturn == null) || (validreturn == true)) {
            return true;
        } else if (typeof(validreturn) == 'object') {
            iswarning = validreturn['iswarning'] || iswarning;
            if (('value' in validreturn) && !(validreturn['value'] === value)) {
                modified = true;
                value = validreturn['value'];
            }
            errorcode = validreturn['errorcode'];
        } else {
            if (validreturn == false) {
                errorcode = iswarning ? 'warning' : 'error';
            } else if (typeof(validreturn) == 'string') {
                errorcode = validreturn;
            }
            validreturn = {};
        }

        if (errorcode) {
            var msgorder = [validation + '_' + errorcode];
            if (iswarning) {
                msgorder.push(validation + '_warning');
                msgorder.push(validation + '_error');
            } else {
                msgorder.push(validation + '_error');
                msgorder.push(validation + '_warning');
            }

            for (var i = 0; i < msgorder.length; i++) {
                errormessage = validations[msgorder[i]];
                if (errormessage) break;
            }
            ;
            errormessage = errormessage ? errormessage : errorcode;
        }

        validreturn['value'] = value;
        validreturn['modified'] = modified;
        validreturn['errorcode'] = errorcode;
        validreturn['iswarning'] = iswarning;
        if (errormessage) {
            errormessage = dataTemplate(errormessage, validreturn);
        }
        validreturn['message'] = errormessage;
        return validreturn;
    },
    exitValidation: function(result, sourceNode, validations, userChange) {
        var func;
        if (result['error']) {
            if (validations['onReject']) {
                func = funcCreate(validations['onReject'], 'value,result,validations,rowIndex,userChange');
            }
        } else {
            if (validations['onAccept']) {
                func = funcCreate(validations['onAccept'], 'value,result,validations,rowIndex,userChange');
            }
        }
        if (func) {
            genro.callAfter(dojo.hitch(sourceNode, func, result['value'], result, validations, sourceNode.editedRowIndex, userChange), 1);
        }
    },
    validate_notnull: function(param, value) {
        if ((value === '') || (value == null)) {
            return {'errorcode':'notnull', 'required':true};
        }
    },
    validate_dbselect: function(param, value, sourceNode, parameters) {
        if (dojo.isIE > 0) {
            return;
        }
        var validate_notnull = sourceNode.attr.validate_notnull;
        var result;
        if ((value == undefined) || (value == '') || (value == null)) {
            if (sourceNode.widget._lastDisplayedValue != "") {
                sourceNode.widget._updateSelect();
                result = {'errorcode':'missing'};
            }
            sourceNode.widget._lastValueReported = null;
            return result;
        }
    },
    validate_empty: function(param, value) {
        if (value == null || value === '') {
            return {'value':param};
        }
    },
    validate_case: function(param, value) {
        if (value) {
            var original = value;
            param = param.toLowerCase();
            if (param == 'upper' || param == 'u') {
                value = value.toUpperCase();
            } else if (param == 'lower' || param == 'l') {
                value = value.toLowerCase();
            } else if (param == 'capitalize' || param == 'c') {
                value = stringCapitalize(value.toLowerCase());
            } else if (param == 'title' || param == 't') {
                value = value[0].toUpperCase() + value.slice(1);
            }
            if (original != value) {
                return {'value':value};
            }
        }
    },
    
    validate_min: function(param, value) {
        return value>=param;
    },
    
    validate_max: function(param, value) {
        return value<=param;
    },
    
    validate_len: function(param, value) {
        if (value) {
            if (param.indexOf(':') >= 0) {
                var sl = param.split(':');
                if (sl[1]) {
                    if (value.length > parseInt(sl[1])) {
                        return 'too long';
                    }
                }
                if (sl[0]) {
                    if (value.length < parseInt(sl[0])) {
                        return 'too short';
                    }
                }
            } else {
                if (value.length != parseInt(param)) {
                    return 'wrong lenght';
                }
            }
        }
    },
    validate_regex: function(param, value) {
        if (value) {
            var not = false;
            param = param.trim()
            if (param[0] == '!') {
                not = true;
                param = param.slice(1);

            }
            var r = new RegExp(param);
            var result = r.test(value);
            return not ? !result : result;
        }
    },
    validate_call: function(param, value, sourceNode, parameters) {
        return funcApply(param, objectUpdate({'value':value}, parameters), sourceNode);
    },
    
    validate_remote: function(param, value, sourceNode, parameters) {
        var rpcresult = genro.rpc.remoteCall(param, objectUpdate({'value':value}, parameters), null, 'POST');
        if(parameters['_onResult']){
            var kw = objectUpdate({},parameters);
            kw['result'] = rpcresult;
            funcApply(parameters['_onResult'],null,sourceNode,['result','kwargs'],[rpcresult,parameters]);
        }
        if (rpcresult instanceof gnr.GnrBag) {
            var result = {};
            result['errorcode'] = rpcresult.getItem('errorcode');
            result['iswarning'] = rpcresult.getItem('iswarning');
            if (rpcresult.getItem('value')) {
                result['value'] = rpcresult.getItem('value');
            }
            var datachanges = rpcresult.getItem('data');
            if(datachanges){
                var sdata = sourceNode.getRelativeData();
                sdata.update(datachanges);
            }
            return result;
        } else {
            return rpcresult;
        }
    },
    
    validate_email: function(param, value) {
        if (value) {
            var r = new RegExp("^" + dojox.regexp.emailAddress() + "$", "i");
            if (!r.test(value)) {
                return false;
            }
        }
    },
    validate_gridnodup: function(param, value, sourceNode) {
        var col = ((typeof(param) == 'string') && param) ? param : sourceNode.attr.field;
        if (value && sourceNode.grid) {
            var colvalues = sourceNode.grid.getColumnValues(col);
            var n = dojo.indexOf(colvalues, value);
            if ((n != -1) && (n != sourceNode.editedRowIndex)) {
                return false;
            }
        }
    },
    validate_nodup: function(param, value, sourceNode,kwargs) {
        var nodupkwargs = objectExtract(kwargs,'nodup_*');
        var relative = objectPop(nodupkwargs,'relative');
        if(relative){
            var _parent = sourceNode.getRelativeData('#FORM.record.'+relative);
            nodupkwargs['condition'] = "$"+relative+"=:_parent";
            nodupkwargs['_parent'] = _parent;
        }
        var dbfield = ((typeof(param) == 'string') && param) ? param : sourceNode.getAttributeFromDatasource('dbfield');
        if (value) {
            var n = genro.rpc.getRecordCount(dbfield, value,null,nodupkwargs);
            if (n != 0) {
                return false;
            }
        }
    },
    validate_exist: function(param, value, sourceNode) {
        var dbfield = ((typeof(param) == 'string') && param) ? param : sourceNode.getAttributeFromDatasource('dbfield');
        if (value) {
            var n = genro.rpc.getRecordCount(dbfield, value);
            if (n == 0) {
                return false;
            }
        }
    }
});

///formstores
dojo.declare("gnr.formstores.Base", null, {
    constructor:function(kw,handlers){
        objectPop(kw, 'tag');
        this.handlers = handlers;
        this.storepath = '.record';
        this.parentStoreCode = objectPop(kw,'parentStore')
        //this.startKey = objectPop(kw,'startKey');
        //this.table = kw.table;
        //this.onSaved = kw.onSaved;
        ;
        var base_handler_type = objectPop(kw,'handler');
        this.base_handler_type = base_handler_type;
        var handlerKw = objectExtract(kw,'handler_*');
        var handler,handler_type,method,actionKw,callbacks,defaultCb;
        var that = this;
        var rpcmethod;
        dojo.forEach(['save','load','del'],function(action){
            actionKw = objectExtract(handlerKw,action+'_*');
            handler = objectUpdate({},that.handlers[action]);
            handler_type = objectPop(handler,'handler_type') || objectPop(handlerKw,action)||base_handler_type;
            if(typeof(handler_type)=='function'){
                method = handler_type;
            }else if(that[action+'_'+handler_type]){
                method = that[action+'_'+handler_type];
            }else{
                method = funcCreate(handler_type);
            }
            callbacks = objectPop(handler,'callbacks');
            rpcmethod = objectPop(handler,'rpcmethod');
            defaultCb = funcCreate(objectPop(handler,'defaultCb'),'kw');
            that.handlers[action]= {'kw':objectUpdate(actionKw,handler),'method':method,'callbacks':callbacks,'rpcmethod':rpcmethod,defaultCb:defaultCb};
        });
        for (k in kw){
            this[k] = kw[k];
        }
        if(!this.onSaved){
            var handler_onSaved = this.handlers.save.kw.onSaved;
            this.onSaved = handler_onSaved==null? 'reload':handler_onSaved;
        }        
    },
    
    init:function(form){
        this.form = form;
        if(this.parentStoreCode){
            this.parentStore = genro.getStore(this.parentStoreCode);
            if(this.base_handler_type=='memory'){
                this.locationpath = this.parentStore.storeNode.absDatapath(this.parentStore.storepath)
            }
        }
    },
    
    getStartPkey:function(){
        return;
    },
    getParentStoreData:function(){
        return this.parentStore.getData();
    },
    
    load_document:function(pkey,dflt){
        /*
        pkey=discpath; it can use the static shortcut syntax;
        */
        var form=this.form;
        var that = this;
        var loader = this.handlers.load;
        var kw = loader.kw;
        kw =form.sourceNode.evaluateOnNode(kw);
        if(loader.defaultCb){
            var dflt = loader.defaultCb.call(form.sourceNode,kw);
        };
 
        this.handlers.load.rpcmethod = this.handlers.load.rpcmethod  || 'getSiteDocument';
        var deferred = genro.rpc.remoteCall(this.handlers.load.rpcmethod ,
                                            objectUpdate({'path':pkey,defaultContent:dflt},kw),null,'POST',null,function(){});
        deferred.addCallback(function(result){
            that.loaded(pkey,result.popNode('content'));
            return result;
        });
 
        
    },

    save_document:function(kw){
        
    },
    
    delete_document:function(){
        
    },


    load_memory:function(loadkw){
        var default_kw = loadkw.default_kw;
        var form=this.form;
        var that = this;
        var currPkey = this.form.getCurrentPkey();
        var data;
        var loader = this.handlers.load;
        var kw = loader.kw || {};
        var maincb = kw._onResult? funcCreate(kw._onResult,'result',form.sourceNode):function(){};
        kw = form.sourceNode.evaluateOnNode(kw);
        
        var envelope = new gnr.GnrBag();
        if(currPkey=='*newrecord*'){
            data = new gnr.GnrBag();
            this._load_prepareDefaults(currPkey,default_kw,kw);
            data.update(objectExtract(kw,'default_*'));
            envelope.setItem('record',data,{_newrecord:true,lastTS:null,caption:kw.newrecord_caption});
            
        }else{
            var sourceBag = form.sourceNode.getRelativeData(this.locationpath);
            var dataNode = sourceBag.getNode(currPkey);
            genro.assert(dataNode,'Missing data for currentPath',currPkey);
            var kw = objectExtract(dataNode.attr,'lastTS,caption,_protect_delete,_protect_write,_pkey',true);
            var recordLoaded = new gnr.GnrBag();
            var d = dataNode.getValue().deepCopy();
            d.walk(function(n){n.attr = {}})
            d.forEach(function(n){
                recordLoaded.setItem(n.label,n.getValue());
            });
            envelope.setItem('record',recordLoaded,kw);
        }
        var result = envelope.getNode('record');    
        this.loaded(currPkey,result);
        return result;        
    },
    
    
    save_memory:function(kw){
        var saveKw = objectUpdate({},kw);
        var destPkey = objectPop(saveKw,'destPkey');
        var form = this.form;
        var sourceBag = form.sourceNode.getRelativeData(this.locationpath);
        var formData = form.getFormData();
        var currPkey = form.getCurrentPkey();
        var pkeyField = this.pkeyField;
        var newPkey = formData.getItem(pkeyField);
        var data;
        var newrecord = currPkey=='*newrecord*';
        if(newrecord){
            data = new gnr.GnrBag();
            if (!newPkey){
                if(this.newPkeyCb){
                    newPkey = funcApply(this.newPkeyCb,{record:formData},form);
                }else{
                    newPkey = 'r_'+genro.getCounter();
                }
                data.setItem(pkeyField,newPkey);
            }
            sourceBag.setItem(newPkey,data);
        }else{
            data = sourceBag.getItem(currPkey);
            if(currPkey != newPkey){
                data.getParentNode().label = newPkey;
            }
        }
        form.setCurrentPkey(newPkey);
        var path,v;
        formData.walk(function(n){
            v = n.getValue();
            if(v instanceof gnr.GnrBag){
                return;
            }
            if(newrecord || '_loadedValue' in n.attr){
                path = n.getFullpath('static',formData);
                data.setItem(path,n.getValue(),{dtype:n.attr.dtype});
            }
        });
        var result = {};//{savedPkey:loadedRecordNode.label,loadedRecordNode:loadedRecordNode};
        this.saved(result);
        if(destPkey){
            this.form.reset();
            this.form.load({destPkey:destPkey});
        }else{
            this.form.load({destPkey:newPkey}); 
        }

    },
    del_memory:function(pkey,callkw){
        var sourceBag = this.form.sourceNode.getRelativeData(this.locationpath);
        var currPkey = this.form.getCurrentPkey();
        sourceBag.popNode(currPkey);
        this.deleted(null,callkw);
    },
    _load_prepareDefaults:function(pkey,default_kw,kw){
        var form = this.form;
        var loader = this.handlers.load;
        var default_kwargs = objectPop(kw,'default_kwargs') || {}; 
        if(default_kwargs){
            default_kwargs = form.sourceNode.evaluateOnNode(default_kwargs);
        }
        if(pkey=='*newrecord*'){
            default_kw = default_kw || {}       
            if(loader.defaultCb){
                default_kw = objectUpdate(default_kw,(loader.defaultCb.call(form,kw)||{}));
            }
            objectUpdate(default_kwargs,form.sourceNode.evaluateOnNode(default_kw));
        }
        if(objectNotEmpty(default_kwargs)){
            for(var k in default_kwargs){
                kw['default_'+k] = default_kwargs[k]
            }
        }
    },
    duplicateRecord:function(srcPkey, howmany){
        var form=this.form;
        var that = this;
        var srcPkey = srcPkey || this.form.getCurrentPkey();
        var howmany = howmany || 1;
        if (howmany=='?'){
            var that = this;
            genro.dlg.prompt('How many', {msg:_T('How many copies of current record?'),
                                          lbl:'How many',
                                          widget:'numberTextBox',
                                          action:function(value){that.duplicateRecord(srcPkey,value);}
                                          });
            return
        }
        genro.assert(this.table,'only form with table allow duplicate');
        genro.serverCall('app.duplicateRecord',{table:this.table,pkey:srcPkey,howmany:howmany},function(resultPkey){
            form.doload_store({destPkey:resultPkey});
            
        })
    },

    load_recordCluster:function(loadkw){
        var default_kw = loadkw.default_kw;
        var ignoreReadOnly = loadkw?objectPop(loadkw,'ignoreReadOnly'):null;
        var form=this.form;
        var that = this;
        var currPkey = this.form.getCurrentPkey();
        var loader = this.handlers.load;
        var cb = function(result){
            that.loaded(currPkey,result);
            return result;
        };
        var kw = loader.kw || {};
        var maincb = kw._onResult? funcCreate(kw._onResult,'result',form.sourceNode):function(){};
        kw = form.sourceNode.evaluateOnNode(kw);
        this._load_prepareDefaults(currPkey,default_kw,kw);
        
        
        loader.rpcmethod = loader.rpcmethod || 'loadRecordCluster';
        kw.sqlContextName = ('sqlContextName' in kw)?kw.sqlContextName:form.formId;
        var virtual_columns = objectPop(kw,'virtual_columns');
        var form_virtual_columns = form.getVirtualColumns();
        virtual_columns = virtual_columns?virtual_columns.split(','):[]
        form_virtual_columns = form_virtual_columns?form_virtual_columns.split(','):[]
        virtual_columns = virtual_columns.concat(form_virtual_columns);
        kw['_sourceNode'] = form.sourceNode;
        kw.ignoreReadOnly = ignoreReadOnly;
        var deferred = genro.rpc.remoteCall(loader.rpcmethod ,objectUpdate({'pkey':currPkey,
                                                  'virtual_columns':arrayUniquify(virtual_columns).join(','),
                                                  'table':this.table, timeout:0},kw),null,'POST',null,maincb);
        deferred.addCallback(cb);
        if(loader.callbacks){
            var thatnode = form.sourceNode;
            loader.callbacks.forEach(function(n){
                var defkw = objectUpdate({},kw);
                genro.rpc.addDeferredCb(deferred,n.getValue(),objectUpdate(defkw,n.attr),thatnode);
            });
        }
        return deferred;
    },
    save_recordCluster:function(kw){
        var form=this.form;
        var that = this;
        var saver = this.handlers.save;
        var saveKw = objectUpdate({},kw);
        var destPkey = objectPop(saveKw,'destPkey');
        var kw = form.sourceNode.evaluateOnNode(this.handlers.save.kw);
        objectUpdate(kw,saveKw);
        var onSaving = objectPop(kw,'onSaving');
        kw['_sourceNode'] = form.sourceNode;
        kw['_autoreload'] = kw['_autoreload'] || false;
        if(kw._autoreload){
            if (destPkey){
                kw._autoreload=destPkey;
            }else if(this.onSaved=='reload' || this.form.isNewRecord()){
                kw._autoreload=true;
            }
        }

        //kw._autoreload = null;
        var autoreload =kw._autoreload;
        
        var cb = function(result){
            if (result){
                var resultDict={};
                if (result.error){
                    resultDict['error'] = result.error;
                }
                else if(autoreload){
                    var loadedRecordNode = result.getNode('loadedRecord');
                    var pkeyNode = result.getNode('pkey'); 
                    resultDict.savedPkey=pkeyNode.getValue();
                    resultDict.savedAttr=pkeyNode.attr;
                    resultDict.loadedRecordNode=loadedRecordNode;
                    //resultDict.loadedAttr=loadedRecordNode.attr;
                }else{
                    var pkeyNode=result;
                    resultDict.savedPkey=pkeyNode.getValue();
                    resultDict.savedAttr=pkeyNode.attr;
                    
                }
            }
            that.saved(resultDict);
            return resultDict;
        };
        this.handlers.save.rpcmethod = this.handlers.save.rpcmethod || 'saveRecordCluster';
        var data = form.getFormChanges();
        var rpckw = objectUpdate({'data':data,'table':this.table},kw);
        if(onSaving){
            var dosave = funcApply(onSaving,rpckw,this);
            if(dosave===false){
                this.form.setOpStatus(null);
                return;
            }
        }
        var deferred = genro.rpc.remoteCall(this.handlers.save.rpcmethod,
                                            rpckw,null,'POST', null,function(){});
        deferred.addCallback(cb);
        if(saver.callbacks){
            var thatnode = form.sourceNode;
            saver.callbacks.forEach(function(n){
                var defkw = objectUpdate({},kw);
                genro.rpc.addDeferredCb(deferred,n.getValue(),objectUpdate(defkw,n.attr),thatnode);
            });
        }
        return deferred;
    },
    del_recordCluster:function(pkey,callkw){
        var deleter = this.handlers.del;
        var form = this.form;
        var that = this;
        var kw =form.sourceNode.evaluateOnNode(this.handlers.del.kw);
        pkey = pkey || form.getCurrentPkey();
        this.handlers.del.rpcmethod = this.handlers.del.rpcmethod || 'deleteDbRow';
        var deferred = genro.rpc.remoteCall(this.handlers.del.rpcmethod,
                                            objectUpdate({'pkey':pkey,
                                                          'table':this.table},kw),null,'POST',
                                                          null,function(){});
        var cb = function(result){
            that.deleted(result,callkw);
            return result;
        };
        deferred.addCallback(cb);
        if(deleter.callbacks){
            var thatnode = form.sourceNode;
            deleter.callbacks.forEach(function(n){
                var defkw = objectUpdate({},kw);
                genro.rpc.addDeferredCb(deferred,n.getValue(),objectUpdate(defkw,n.attr),thatnode);
            });
        }
        return deferred;
    },
    loaded:function(pkey,result){
        this.setNavigationStatus(pkey);
        this.form.loaded(result);
    },
    deleted:function(result,kw){
        this.form.deleted(result,kw);
    },
    saved:function(result){
        return this.form.saved(result);
    },
    save:function(kw){
        return this.handlers.save.method.call(this,kw);
    },
    load:function(loadkw){
        return this.handlers.load.method.call(this,loadkw);
    },
    deleteItem:function(pkey,kw){
        return this.handlers.del.method.call(this,pkey,kw);
    },
    setNavigationStatus:function(){
        return;
    },
    navigationEvent:function(kw){
    }
});

dojo.declare("gnr.formstores.Item", gnr.formstores.Base, {
    load_subform:function(){
        var form= this.form;
        var parentForm = form.getParentForm();
        var subRecordKeys = form.getFormData().keys();
        var r = new gnr.GnrBag();
        var parentRecord = parentForm.getFormData();
        dojo.forEach(subRecordKeys,function(field){
            var n = parentRecord.getNode(field);
            if(n){
                r.setItem(field,n.getValue());
            }
        });
        this.loaded('*subform*',r);
    },
    save_subform:function(kw){
        var saveKw = objectUpdate({},kw);
        var destPkey = saveKw.destPkey; 
        var form= this.form;
        var parentForm = form.getParentForm();
        var subRecord = form.getFormData();
        var parentRecord = parentForm.getFormData();
        subRecord.forEach(function(n){
            parentRecord.setItem(n.label,n.getValue());
        });
        this.saved({});
        this.load_subform();
        if(destPkey){
            form.load({destPkey:destPkey});
        }
    }
});

dojo.declare("gnr.formstores.Collection", gnr.formstores.Base, {
    getStartPkey:function(){
        return this.getNavigationPkey(0);
    },    
    setNavigationStatus:function(pkey){
        var currIdx=-1;
        if(pkey!='*norecord*' && pkey!='*newrecord*'){
            var currIdx = this.parentStore.getIdxFromPkey(pkey,true);
            if(this.loadedIndex!=null && this.loadedIndex>=0 && currIdx<0){
                return;
            }
        }
        var kw = {};
        if(currIdx<0){
            kw.first = true;
            kw.last = true;
        }
        else{
            if(currIdx==0){
                kw.first = true;
            }
            if(currIdx>=this.parentStore.len(true)-1){
                kw.last = true;
            }
        }
        this.loadedIndex = currIdx;
        this.form.publish('navigationStatus',kw);
        return;
    },

    navigationEvent:function(kw){
        var command = kw.command;
        return this.getNavigationPkey(command,this.form.getCurrentPkey());
    },

    getNavigationPkey:function(nav,currentPkey){
        var idx = nav == parseInt(nav) && nav;
        if(!idx){
            if(nav=='first'){
                idx = 0;
            }else if(nav=='last'){
                idx = this.parentStore.len(true)-1;
            }else{
                idx = this.parentStore.getIdxFromPkey(currentPkey,true);
                if(idx<0){
                    if(this.loadedIndex>=0){
                        idx = nav=='next'?this.loadedIndex:this.loadedIndex-1;
                    }else{
                        console.log('out of selection');
                    }
                }else{
                    idx = nav=='next'? idx+1:idx-1;
                }
            }
        }

        return this.parentStore.getKeyFromIdx(idx,true);
    }
    
});

dojo.declare("gnr.formstores.Hierarchical", gnr.formstores.Base, {

});

