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
        if(!('autoFocus' in this)){
            this.autoFocus = !genro.isMobile;
        }
        if(this.isRootForm){
            genro._rootForm = this;
        }
        this.formId = formId;
        this.changed = false;
        this.childForms = {};
        this.gridEditors = {};
        this.opStatus = null;
        this.locked = this.locked || false;
        this.parentLock = this.parentLock ==null? 'auto':this.parentLock;
        this.current_field = null;
        this.controllerPath = controllerPath;
        this.formErrors = new gnr.GnrBag();
        if(!this.store){
            this.controllerPath = this.controllerPath || 'gnr.forms.' + this.formId;
        }
        this.formDatapath = formDatapath;
        this.pkeyPath = pkeyPath;
        this.sourceNode = sourceNode;
        var formCenter = this.sourceNode.getValue().getNode('center');
        this.contentSourceNode = this.store? (formCenter?formCenter:sourceNode):sourceNode;
        this.frameCode = sourceNode.attr.frameCode;
        if(this.frameCode){
            this.formParentNode = genro.getFrameNode(this.frameCode,'frame').getParentNode().getParentNode();
        }else{
            this.formParentNode = this.sourceNode.getParentNode();
        }
        this.subscribe('save,reload,load,goToRecord,abort,loaded,setLocked,navigationEvent,newrecord,pendingChangesAnswer,dismiss,deleteItem,deleteConfirmAnswer,message,shortcut_save');
        this._register = {};
        this._status_list = ['ok','error','changed','readOnly','noItem'];
        //this.store=new.....
        this.autoRegisterTags = {
            'textbox':null,
            'simpletextarea':null,
            'checkbox':null,
            'numbertextbox':null,
            'currencytextbox':null,
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
            'geocoderfield':null,
            'ckeditor':null
        };
        
        this.checkLastSavedTags = {
            'textbox':null,
            'numbertextbox':null,
            'currencytextbox':null,
            'timetextbox':null,
            'combobox':null,
            'filteringselect':null,
            'dbselect':null,
            'dbcombobox':null,
            'datetextbox':null,
        };


        var tblname = this.getControllerData('table?name_long');
        var pref = tblname?tblname+' record':'Record';
        this.msg_saved = pref +' saved ';
        this.msg_deleted = pref +' deleted';
        this.table_name = tblname || formId;

        this.msg_unsaved_changes ="Current record has been modified.";
        this.msg_confirm_delete ="You are going to delete the current record.";

    },
    getParentForm:function(){
        return this.sourceNode.getParentNode().getFormHandler();
    },
    
    canBeSaved:function(kw){
        kw = kw || {};
        return !this.opStatus && (this.record_changed || kw.always) && (this.isValid() || this.allowSaveInvalid) && this.status!='noItem';
    },

    saveDisabled:function(){
        if(this.disabledStatus()=='unlocked_readOnly'){
            return this.getChangesLogger().getNodes().some(n => !n.attr.allowed);
        }
        return this.isDisabled();
    },

    doAutoSave:function(){
        var that = this;
        if(this.canBeSaved() && !this.isNewRecord()){
            genro.callAfter(function(){
               that.lazySave();
            },this.autoSave,this.sourceNode,'autoSaveForm_'+this.formId);
        }
    },

    shortcut_save:function(kw){
        if(this.saveDisabled()){
            this.publish('message',{message:_T('Cannot save. Blocked Form'),sound:'$error',messageType:'warning'});
            return;
        }
        kw = kw || {};
        this.save(kw.forced);
    },
    lazySave:function(savedCb,kw,errorCb){
        savedCb = savedCb?funcCreate(savedCb,{},this):false;
        if(this.canBeSaved(kw)){
            var d = this.save(objectUpdate({onSaved:'lazyReload',waitingStatus:false},kw));
            this.getFormData().walk(function(n){
                delete n.attr._loadedValue;
            },'static');
            if(savedCb){
                d.addCallback(savedCb);
            }
            return d;
        }else if(errorCb){
            errorCb.call(this);
        }else if(savedCb){
            savedCb.call(this);
        }
    },

    onStartForm:function(kw){
        kw = kw || {};
        this.formDomNode = this.sourceNode.getDomNode();
        this.formContentDomNode = this.contentSourceNode.getDomNode();
        if(this.store){
            var that = this;
            this.store.init(this);            
            dojo.connect(this.formContentDomNode,'onclick',function(e){
                var wdg = dijit.getEnclosingWidget(e.target);
                if(wdg && wdg.sourceNode && wdg.sourceNode.form && wdg.isFocusable && !wdg.isFocusable() && wdg.sourceNode && (wdg.sourceNode.form != genro.activeForm)){
                   wdg.sourceNode.form.focusCurrentField();
                }
            });
            if(this.store.autoSave){
                this.autoSave = this.store.autoSave===true?2000:this.store.autoSave;
                dojo.connect(this,'updateStatus',this.doAutoSave);
            }
            var startKey = kw.startKey || this.store.startKey || this.getCurrentPkey();
            if(startKey){
                startKey = this.sourceNode.currentFromDatasource(startKey);
            }
            this.sourceNode.getAttributeFromDatasource(startKey);

            if(startKey){
                this.sourceNode.watch('pageStarted',function(){return genro._pageStarted;},function(){
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
                    if(that.parentLock=='auto'){
                        that.setLocked(kw.locked);
                    }
                    that.publish('onParentLockChange',kw);
                },this.sourceNode);
                this.locked = parentStore.locked;
            }else if (parentForm){
                parentForm.subscribe('onLockChange',function(kw){
                    if(that.parentLock=='auto'){
                        that.setLocked(kw.locked);
                    }
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
        this.resetGridEditors();
        this.resetChanges();
        this.resetInvalidFields();
    },
    
    resetGridEditors:function(){
        for(var k in this.gridEditors){
            this.gridEditors[k].resetEditor();
        }
    },

    publish: function(command,kw,topic_kw){
        var topic = {'topic':'form_'+this.formId+'_'+command,parent:this.publishToParent} // re add iframe:'*', (it gives problem with multipage?)
        objectUpdate(topic,topic_kw)
        genro.publish(topic,kw);
    },


    message:function(kw){
        if (!(kw instanceof Array)){
            kw = [kw]
        }
        var msgKw = kw.shift();
        if(typeof(msgKw)=='string'){
            msgKw = {message:msgKw};
        }
        var that = this;
        if(kw.length){
            msgKw.onClosedCb = function(){
                that.message(kw)
            }
        }
        msgKw = objectUpdate({duration_in:3,duration_out:4,yRatio:.8},msgKw);
        genro.dlg.floatingMessage(this.sourceNode,msgKw);
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
        scope = scope || this;
        cb = cb || this[command];
        subscriberNode = subscriberNode || this.sourceNode;
        subscriberNode.registerSubscription(topic,scope,cb);
    },

    applyDisabledStatus:function(){
        var form_disabled = this.isDisabled();
        var disabled_status = this.disabledStatus();
        this.publish('onDisabledChange',{disabled:form_disabled,locked:this.locked});
        genro.dom.setClass(this.sourceNode,'lockedContainer',form_disabled);
        var node,disabled;
        for (var k in this._register){
            node = this._register[k];
            if(disabled_status=='unlocked_readOnly' && node.attr.tag.toLowerCase() in this.autoRegisterTags){
                disabled = this._protectedNode(genro.getDataNode(node.absDatapath(node.attr.value)) || node);
            }else{
                disabled = form_disabled;
            }
            if(disabled===false){
                disabled = 'disabled' in node.attr?node.getAttributeFromDatasource('disabled'):false;
                if(disabled==false && 'unmodifiable' in node.attr){
                    disabled = !this.isNewRecord();
                }
            }
            node.setDisabled(disabled);
        }
    },

    _protectedNode:function(node){
        var recAttr = this.getDataNodeAttributes();
        var protect_write = recAttr._protect_write;
        if(protect_write===true){
            return true;
        }
        if('protected_by' in node.attr){
            return node.attr.protected_by;
        }
        var protect_write_reasons =protect_write?protect_write.split(','):[];
        var protected_by_kwargs = objectExtract(node.attr,'protected_by_*',true);
        return !protect_write_reasons.some(fld => protected_by_kwargs[fld]===false);
    },

    resetKeepable:function(){
        for (var k in this._register){
            var node = this._register[k];
            if (node.attr.keepable){
                node.widget.setKeeper(false);
            }
        }
    },

    isDisabled:function(){
        return this.locked || this.status=='readOnly' || this.status== 'noItem';
    },

    disabledStatus:function(){
        var result = [];
        result.push(this.locked?'locked':'unlocked');
        if(this.status=='readOnly' || this.status=='noItem'){
            result.push(this.status);
        }
        return result.join('_') || false;
    },
    
    setLocked:function(value){
        if(value=='toggle'){
            value = !this.locked;
        }
        this.locked = value;
        this.applyDisabledStatus();
        this.setControllerData('locked',value);
        this.publish('onLockChange',{'locked':this.locked},{iframe:'*'});
    },
    registerChild:function(sourceNode){
        var ltag = sourceNode.attr.tag.toLowerCase();
        if (sourceNode.attr.parentForm || (ltag in this.autoRegisterTags)){
            if(!this._firstField){
                if(ltag in this.autoRegisterTags){
                    this._firstField = sourceNode;
                }
            }
            this._register[sourceNode._id] = sourceNode;
            return;
        }
    },

    setLastSavedValues:function(){
        var k,node,ltag;
        for (k in this._register){
            node = this._register[k];
            if (node.attr.tag.toLowerCase() in this.checkLastSavedTags){
                node._lastSavedValue = node.getRelativeData(node.attr.value);
            }
        }
    },

    registerGridEditor:function(nodeId,gridEditor){
        this.gridEditors[nodeId] = gridEditor;
    },
    
    unregisterChild:function(sourceNode){
        if(this._register[sourceNode._id]){
            delete this._register[sourceNode._id];
        }
        if(sourceNode.widget && sourceNode.widget.gridEditor){
            objectPop(this.gridEditors,sourceNode.attr.nodeId);
        }
    },
    
    getSemaphoreStatus:function(){
        var i;
        if(this.status=='noItem'){
            return '<div class="form_errorslogger">No record loaded</div>';
        }
        if(this.status=='readOnly'){
            var readOnlyMsg = 'Read Only';
            var protectWriteMessage = this.getDataNodeAttributes()._protect_write_message;
            return '<div class="form_errorslogger">'+protectWriteMessage || readOnlyMsg+'</div>';
        }
        if(this.status=='ok'){
            return '<div class="form_okmessage">No changes to save</div>';
        }
        if(this.status=='changed'){
            if (this.isNewRecord()){
                return 'The record can be saved';
            }
            var changes = this.getChangesLogger()
            var content = new gnr.GnrBag();
            i = 0;
            changes.forEach(function(n){
                if(n.attr.from!=n.attr.to){
                    var r = new gnr.GnrBag();
                    r.setItem('fieldname','<div style="font-weight: bold;">'+n.attr._valuelabel+'</div>',{_valuelabel:'Field'});
                    r.setItem('from',n.attr.from,{_valuelabel:'From'});
                    r.setItem('to',n.attr.to,{_valuelabel:'To'});
                    content.setItem('r_'+i,r)
                }
                i++;
            });
            var c = content.asHtmlTable({cells:'fieldname,from,to',headers:true})
            return '<div class="form_changeslogger">Changed fields</div><div class="form_contentlogger">'+c+'</div>';
        } 
        if(this.status=='error'){
            var content = new gnr.GnrBag();
            var invfields = this.getInvalidFields();
            var invdojo = this.getInvalidDojo();
            i = 0;
            if(invfields){
                invfields.forEach(function(n){
                    var sn = genro.src.nodeBySourceNodeId(objectValues(n.getValue())[0]);
                    if(!sn){
                        return;
                    }
                    var r = new gnr.GnrBag();
                    r.setItem('fieldname','<div style="font-weight: bold;">'+sn.getElementLabel()+'</div>',{_valuelabel:'Field'});
                    r.setItem('error',sn._validations.error,{_valuelabel:'Error'});
                    i++;
                    content.setItem('r_'+i,r)
                });

            }
            if(invdojo){
                invdojo.forEach(function(n){
                    var r = new gnr.GnrBag();
                    r.setItem('fieldname','<div style="font-weight: bold;">'+n.attr._valuelabel+'</div>',{_valuelabel:'Field'});
                    r.setItem('error','Invalid data',{_valuelabel:'Error'});
                    content.setItem('r_'+i,r)
                    i++;
                });
            }
            var formErrorsMessages = this.getFormErrors();
            if(formErrorsMessages.length){
                formErrorsMessages.forEach(function(message){
                    content.setItem('r_'+i+'.error',message);
                    i++;
                })
            }
            content = content.asHtmlTable({cells:'fieldname,error',headers:true});
            return '<div class="form_errorslogger">Wrong fields</div><div class="form_contentlogger">'+content+'</div>';
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
            this.addPendingValidation(sourceNode);
            //var result = genro.vld.validateInLoading(sourceNode, value);
        } else if (trigger_reason == 'node') {
            var result = genro.vld.validate(sourceNode, value);
            //console.log("value: " +value+" result: "+ result.toSource());
            if (result['modified']) {
                sourceNode.widget.setValue(result['value']);
            }
            sourceNode.setValidationError(result);
            sourceNode.updateValidationStatus();
        }

        //this.updateInvalidField(sourceNode, sourceNode.attrDatapath('value'));
    },

    forceIgnoreReadOnly:function(evt){
        if(genro.dom.getEventModifiers(evt)=='Shift'){
            this.reload({ignoreReadOnly:true});
        }
    },
    
    reload: function(kw) {
        kw = kw || {};
        var destPkey = this.getCurrentPkey();
        if(destPkey == '*newrecord*'){
            this.newrecord(this.last_default_kw);
            return;
        }
        this.load(objectUpdate({destPkey:destPkey},kw));
    },
    
    goToRecord:function(pkey,ts){
        if(pkey!=this.getCurrentPkey() || (ts && !isEqual(new Date(this.getDataNodeAttributes().lastTS),ts))){
            this.load({destPkey:pkey});
        }
    },

    load: function(kw) {
        if(this.opStatus=='loading'){
            return;
        }

        var that = this;
        if(objectNotEmpty(this.childForms)){
            var onAnswer = function(command){if(command=='cancel'){return;}
                                                that.load(kw);
            };
            for(var k in this.childForms){
                var childForm = this.childForms[k];
                if(childForm.changed){
                    childForm.openPendingChangesDlg({destPkey:'*dismiss*',
                                                    onAnswer:onAnswer
                                                    });
                    return;
                }
            }
        }
        if(this.store && this.changed && this.saveOnChange && this.isValid()){
            var deferred = this.store.save();
            deferred.addCallback(function(){
                that.reset();
                //that.do_load(kw);
            });
            return;
        }
        kw = kw || {};
        if (this.store){

            if(!kw.destPkey && this.store instanceof gnr.formstores.SubForm){
                kw.destPkey="*subform*";
            }
            kw.destPkey = kw.destPkey || this.store.getDefaultDestPkey(); 
            var destPkey = kw.destPkey;
            if(typeof(destPkey)=='string' && destPkey.indexOf('*|')>=0){
                var pkeyChoices = destPkey.split('|');
                var chosedPkey;
                while (!chosedPkey && pkeyChoices.length){
                    chosedPkey = pkeyChoices.shift();
                    if(['*next*','*prev*','*last*','*first*'].indexOf(chosedPkey)>-1){
                        chosedPkey = this.store.getNavigationPkey(chosedPkey.slice(1,-1),this.getCurrentPkey());
                    }
                }
                kw.destPkey = chosedPkey || '*norecord*';
            }
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
        if (!kw.discardChanges && this.changed && kw.destPkey &&(currentPkey=='*newrecord*' || (kw.destPkey != currentPkey))) {
            if(kw.modifiers=='Shift' || this.autoSave){
                this.save(kw);
            }else{
                this.openPendingChangesDlg(kw);
            }
            return;
        }
        var defaultPrompt = 'defaultPrompt' in kw? kw.defaultPrompt:this.defaultPrompt;
        if(kw.destPkey=='*newrecord*' && defaultPrompt){
            var that = this;
            kw.default_kw = kw.default_kw || {};
            genro.dlg.prompt( _T(defaultPrompt.title || 'Fill parameters'),{
                widget:defaultPrompt.fields,
                dflt:new gnr.GnrBag(kw.default_kw),
                cols:defaultPrompt.cols,
                action:function(result){
                    objectUpdate(kw.default_kw,result.asDict());
                    if(defaultPrompt.doSave && that.store.table){
                        genro.serverCall('app.insertRecord',{table:that.store.table,record:new gnr.GnrBag(objectExtract(that.store.prepareDefaults('*newrecord*',kw.default_kw),'default_*'))},function(resultPkey){
                            that.doload_store({destPkey:resultPkey});
                        });
                    }else{
                        that.doload_store(kw);
                    }
                }
            });
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
        kw = kw || {};
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
        kw = kw || {};
        kw.pkey = kw.pkey || this.getCurrentPkey();
        this.setOpStatus('deleting');
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
    
    recordSearchBox:function(kw){
        var datapath = this.sourceNode.absDatapath()+'.temp.jump';
        var that = this;
        var table = this.getControllerData('table');
        var cdata = this.getControllerData();
        var tableattr = this.getControllerData().getAttr('table');
        var searchattr = objectExtract(tableattr,'search_*',true)
        if(that._jumperOpen){
            return;
        }
        that._jumperOpen = true;
        genro.dlg.lightboxDialog(function(dlg,closecb){
            var box = dlg._('div',{padding:'5px',font_size:'1.2em'});
            var onEnter = function(){
                var pkey = genro.getData(datapath+'.pkey');
                if(pkey){
                    that.goToRecord(pkey);
                }
                delete that._jumperOpen;
                closecb();
            }
            fb = genro.dev.formbuilder(box,1,{border_spacing:'1px',
                        onEnter:onEnter,width:'100%',fld_width:'100%'});
            fb.addField('dbselect',objectUpdate({value:'^'+datapath+'.pkey',dbtable:table,padding:'3px',
                        validate_onAccept:function(value,userChange){
                            if(userChange){
                                onEnter();
                            }
                        },
                         padding_left:'5px',padding_right:'5px',rounded:6,
                            width:'30em',lbl:that.table_name+': '},searchattr));
        });
    },
    pendingChangesAnswer:function(kw){
        var command = objectPop(kw,'command');
        var onAnswer = objectPop(kw,'onAnswer');
        var res;
        if(this.store){
            var that = this;
            if(command=='save'){
                res = this.save({destPkey:kw.destPkey});
            }
            else if(command=='discard'){
                res = this.doload_store(kw);
            }else{
                var cancelCb = kw.cancelCb || this.cancelCb;
                if(cancelCb){
                    cancelCb = funcCreate(cancelCb);
                    cancelCb();
                }
                this.publish('onCancel',{formEvent:'loadRecord'});
            }
            if(onAnswer && res instanceof dojo.Deferred){
                res.addCallback(onAnswer);
            }else if(onAnswer){
                onAnswer(command);
            }
        }else{
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

    setFormError:function(errorcode,message){
        if(message===false){
            this.formErrors.popNode(errorcode);
        }else{
            this.formErrors.setItem(errorcode,message);
        }
        this.updateStatus();
    },

    getFormErrors:function(){
        var result = [];
        this.formErrors.walk(function(n){
            var v = n.getValue();
            if(typeof(v)=='string'){
                result.push(v);
            }
        });
        return result;
    },
    
    openPendingChangesDlg:function(kw,saveSlot){
        if(this.avoidPendingChangesDialog){
            kw.command='discard';
            this.publish('pendingChangesAnswer',kw);
            return;
        }
        saveSlot = saveSlot===undefined? true:saveSlot;
        var dlg = genro.dlg.quickDialog('Pending changes in '+this.table_name.toLowerCase(),{_showParent:true,width:'280px'});
        dlg.center._('div',{innerHTML:this.msg_unsaved_changes, text_align:'center',_class:'alertBodyMessage'});
        var form = this;
        var slotbar = dlg.bottom._('slotBar',{slots:saveSlot?'discard,*,cancel,save':'discard,*,cancel',
                                               action:function(){
                                                   dlg.close_action();
                                                   kw.command = this.attr.command;
                                                   form.publish('pendingChangesAnswer',kw);
                                               }});
        slotbar._('button','discard',{label:'Discard changes',command:'discard'});
        slotbar._('button','cancel',{label:'Cancel',command:'cancel'});
        if(saveSlot){
            slotbar._('button','save',{label:'Save',command:'save'});
        }
        dlg.show_action();
     },
     
    setOpStatus:function(opStatus){
        this.opStatus=opStatus;
        this.publish('onSetOpStatus',this.opStatus);
    },
    doload_loader:function(kw){
        kw = kw || {};
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
        kw = kw || {};
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
        }
    },
    setHider:function(show){
        this.sourceNode.setHiderLayer(show);
    },

    deleted:function(result,kw){
        var destPkey = kw.destPkey || this.deleted_destPkey || '*dismiss*';
        this.load({destPkey:destPkey});
        this.publish('message',{message:this.msg_deleted,sound:'$ondeleted'});
        this.publish('onDeleted');
    },



    loaded: function(data) {
        var controllerData = this.getControllerData();
        var that = this;
        controllerData.setItem('temp',null);
        if(data){
            this.setFormData(data);
        }
        this.publish('onLoaded',{pkey:this.getCurrentPkey(),data:data});
        this.setHider(false);
        this.reset(); // reset changes after loading to subscribe the triggers to the current new data bag
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
        setTimeout(function(){
            controllerData.fireItem('loaded',loadedPkey);
            delete that._reloadingAfterSave;
        },1);
        this.updateStatus();
        this.setOpStatus();
        this.currentFocused = null;
        var onLoadingError = this.onLoadingError();
        if(onLoadingError){
            genro.dlg.alert(onLoadingError,'Error',null,null, { confirmCb:function(){
                that.abort();
            } });
            return;
        }else{
            this.handleLoadedMessage();
        }
        if(this.store){
            //if(this.status=='readOnly'){
            //    this.setLocked(true);
            //}
            if(this.store.parentStore){
                this.store.parentStore.onStartEditItem(this);
            }
            this.applyDisabledStatus();
            //this.focus()
            this.handlePendingValidations();
            that = this;
            var parentForm = this.getParentForm();
            if(!parentForm || !parentForm.currentFocused){
                if(this.autoFocus && this.isNewRecord()){
                    setTimeout(function(){ 
                        that.focus();
                    },1);
                }
                
            }

        }
    },
    
    getRecordCaption:function(){
        return this._recordcaption;
    },
    
    focus:function(node){
        if(!this.isDisabled()){
            var formContentDomNode = this.formContentDomNode || this.sourceNode.widget.domNode;
            if(this.sourceNode.widget && this.sourceNode.widget.getSelected){
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
        if(this.autoSave && this.changed){
            this.doAutoSave();
        }
        genro.dom.removeClass(this.sourceNode,'form_activeForm');
    },
    
    
    isRegisteredWidget:function(wdg){
        return (wdg.sourceNode._id in this._register);
    },

    isEmptyForm:function(){
        var has_filled_field = objectValues(this._register).some(function(n){
                                                                var v = n.getAttributeFromDatasource('value');
                                                                if (!isNullOrBlank(v)){
                                                                    return true;
                                                                }
                                                            })
        return !has_filled_field;
    },

    onFocusElement:function(wdg){
        if(this.isRegisteredWidget(wdg) && (typeof(wdg.focus)=='function')){
            this.currentFocused = wdg;
        }else{
            this.currentFocused = null;
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
        record.forEach(function(n){
            if(n.label[0]!='@' && n.label[0]!='$' && !n.attr._sysfield){
                var value = n._value;
                if (isNullOrBlank(value)){
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
        var copybag;
        var controllerdata = this.getControllerData();
        var clipboard = controllerdata.getItem('clipboard')
        var copy = clipboard.getNode(path);
        copybag = copy.getValue().deepCopy();
        this.updateFormData(copybag);
    },

    updateFormData:function(sourceBag){
        var destdata = this.getFormData();
        sourceBag.forEach(function(n){
            var value = n._value;
            if(value instanceof gnr.GnrBag){
                value = value.deepCopy();
            }
            var destnode = destdata.getNode(n.label);
            destnode.setValue(value);
        });
    },

    clearClipboard:function(){
        this.getControllerData().setItem('clipboard',new gnr.GnrBag());
    },
    
    checkPendingGridEditor:function(){
        var pendingEditor;
        for(var k in this.gridEditors){
            if(this.gridEditors[k].grid.gnrediting){
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
        kw = kw || {};
        var always;
        if (typeof(kw)=='object'){
            always=kw.command || kw.always;
            if(kw.modifiers=='Shift'){
                always = true;
            }
        }else{
            always = kw;
            kw = {};
        }
        if (!this.opStatus) {
            always = always || this.getControllerData('is_newrecord');
            var invalid = !this.isValid();
            if (invalid && !this.allowSaveInvalid) {
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
        if(!kw.forced && this.saveDisabled()){
            this.publish('message',{message:_T('Cannot save. Blocked Form'),sound:'$error',messageType:'warning'});
            return;
        }
        var destPkey = kw.destPkey;
        this.setOpStatus('saving');
        this.fireControllerData('saving');
        var saverNode = genro.nodeById(this.formId + '_saver');
        if(saverNode){
            saverNode.fireNode();
            return saverNode._lastDeferred;
        }else if(this.store) {
            var onSaved = objectPop(kw,'onSaved') || this.store.onSaved;
            if(destPkey=='*dismiss*'){
                onSaved = 'dismiss';
            }
            var onReload = objectPop(kw,'onReload');
            this.setLastSavedValues();
            var deferred=this.store.save(kw);
            if(deferred===false){
                //onSaving interuption
                this.setOpStatus();
                return;
            }
            var that,cb;
            that = this;
            if(onSaved=='reload' || (destPkey&&(destPkey!=this.getCurrentPkey())) || (this.isNewRecord() && onSaved=='lazyReload')){
                cb=function(resultDict){
                    resultDict = resultDict || {};
                    if (resultDict.error){
                        //genro.dlg.alert(resultDict.error,'Error');
                        if(resultDict.error!='gnrsilent'){
                            that.publish('message',{message:'Error in save '+resultDict.error,sound:'$onsaved',messageType:'error'});
                        }
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
                        that._reloadingAfterSave = (that.getCurrentPkey()==destPkey);
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
                    result = result || {};
                    if (result.error){
                        //genro.dlg.alert(resultDict.error,'Error');
                        that.publish('message',{message:'Error in save '+result.error,sound:'$onsaved',messageType:'error'});
                        that.setOpStatus();
                        return;
                    }
                    that.reset();
                    if(onSaved in that){
                        that[onSaved](result);
                    }else if(onSaved){
                        funcApply(onSaved,{result:result},this);
                    }
                    return result;
                };
            }
            if(deferred){
                deferred.addCallback(function(result){
                    cb(result);
                    return result;
                });
            }else{
                this.reset();
            }
            return deferred;
        }
    },
    lazyReload:function(result){
        var savedPkey = result.savedPkey;
        this.setCurrentPkey(savedPkey);
        var data = this.getFormData();
        var savedAttr = result.savedAttr;
        if(savedAttr){
            if(savedAttr.lastTS){
                data.getParentNode().attr.lastTS = result.savedAttr.lastTS;
                data.setItem('__mod_ts',convertFromText(result.savedAttr.lastTS),null,{doTrigger:false});
            }
            var relatedLastTs = objectExtract(result.savedAttr,'lastTS_*');
            var rn,t;
            for (var k in relatedLastTs){
                rn = data.getNode('@'+k);
                t = relatedLastTs[k];
                rn.attr.lastTS = t;
                rn.getValue().setItem('__mod_ts',convertFromText(t),null,{doTrigger:false})
            }
        }
        this.reset();
        this.setOpStatus();
        this.__last_save = new Date()
        //if there allowing invalid fields save. this lines force the widget error
        var invalidFields = this.getDataNodeAttributes()['_invalidFields'];
        if(invalidFields && objectNotEmpty(invalidFields)){
            for (var p in invalidFields){
                data.setItem(p,data.getItem(p));
            }
        }
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
        this.fireControllerData('saved');
        this.setOpStatus('saved');
        var savedPkey = result;
        if(this.store && result){
            savedPkey = result.savedPkey;
        }
        this.publish('onSaved',{pkey:savedPkey,saveResult:result});
        if(!this.autoSave){
            var savedAttr = (result?result.savedAttr:null) || {};
            this.publish('message',savedAttr.saved_message || {message:this.msg_saved,sound:'$onsaved'});
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

    externalChange:function(field,value){
        this.sourceNode.setRelativeData(this.formDatapath+'.'+field,value,{_loadedValue:value});
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
        data = data || new gnr.GnrBag();
        this.sourceNode.setRelativeData(this.formDatapath,data);
        this.getDataNodeAttributes().record_root = true;
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

    onLoadingError:function(){
        return this.getDataNodeAttributes()._onLoadingError;
    },

    handleLoadedMessage:function(){
        var loadedMessage = this.getDataNodeAttributes().loaded_message;
        if(loadedMessage){
            this.message(loadedMessage);
        }
    },

    isProtectWrite:function(){
        var parentForm = this.getParentForm();
        var recAttr = this.getDataNodeAttributes();
        var protect_write = recAttr._protect_write;
        if (parentForm && this.inheritProtect!==false){
            protect_write = protect_write || parentForm.isProtectWrite();
        }
        return (protect_write?true:false) || this.readOnly || false;
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
    getFormChanges: function(fullRecord) {
        var data = this._getRecordCluster(this.getFormData(), !fullRecord);
        for(var k in this.gridEditors){
            var ge = this.gridEditors[k];
            if(!ge.storeInForm){
                var changeset = this.gridEditors[k].getChangeset();
                if(this.gridEditors[k].table && changeset.len()>0){
                    data.setItem('grids.'+k,changeset,{table:this.gridEditors[k].table});
                }
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
        var currentPkey = this.getCurrentPkey()
        this.sourceNode.setRelativeData(this.pkeyPath,pkey);
        if(pkey !=currentPkey && this.store){
            this.store.loadedIndex = -1;
        }
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
                    var isRealChange = false;
                    var gridEditorChanged = false;
                    if(objectNotEmpty(this.gridEditors)){
                        for(var k in this.gridEditors){
                            var ge = this.gridEditors[k];
                            if(node._id==ge.grid.storebag().getParentNode()._id){
                                if(ge.status=='changed'){
                                    isRealChange = true;
                                    gridEditorChanged = true;
                                };
                                break;
                            }
                        }
                    }

                    //sendBag = sendBag || (sendback == true) || isNewRecord || value.getNodeByAttr('_loadedValue')!=null;
                    var hasLoadedValue = value.getNodeByAttr('_loadedValue')!=null;
                    if (gridEditorChanged || (sendback == true) || isNewRecord || hasLoadedValue) {
                        value = value.deepCopy();
                        if(hasLoadedValue){
                            isRealChange = true;
                            value.walk(function(n){
                                if('_loadedValue' in n.attr){
                                    var loadedValue = objectPop(n.attr,'_loadedValue');
                                    var rowNode = n.getParentNode();
                                    if(rowNode && !rowNode.attr._newrecord){
                                        n.attr.__old = asTypedTxt(loadedValue, n.attr.dtype);
                                    }
                                }
                            },'static');
                        }
                        if(value.len()>0 || !isNewRecord){
                            data.setItem(node.label, value, objectUpdate({'_gnrbag':true}, node.attr));
                            data.__isRealChange = data.__isRealChange || isRealChange;
                        }
                    }
                }
                else if ((sendback == true) || isNewRecord || ('_loadedValue' in node.attr)) {
                    var attr_dict = {'dtype':node.attr.dtype};
                    if(node.attr.promised){
                        attr_dict.promised = node.attr.promised;
                    }
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
                var resultattr = objectExtract(recordNode.attr, '_pkey,_newrecord,lastTS,mode,one_one,_invalidFields', true);
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
        for (var k in this.gridEditors){
            var ge = this.gridEditors[k];
            if(ge.storeInForm){
                var storebag = ge.grid.storebag();
                if(kw.node.isChildOf(storebag)){
                    return;
                }
            }
        }
        if (kw.reason == 'resolver' || kw.node.getFullpath().indexOf('$') > 0 || kw.node.attr.virtual_column) {
            var invalidFields = this.getInvalidFields();
            var invalidDojo = this.getInvalidDojo();
            var ck = this.getChangeKey(kw.node);
            if(invalidFields && invalidFields.len()){
                invalidFields._nodes.forEach(function(n){
                    if(n.label.indexOf(ck)==0){
                        invalidFields.popNode(n.label);
                    }
                })
            }
            return;
        }
        var allowed = !this.isDisabled();
        if(this.disabledStatus()=='unlocked_readOnly'){
            allowed = !this._protectedNode(kw.node);
        }
        if( kw.value==kw.oldvalue  || (isNullOrBlank(kw.value) && isNullOrBlank(kw.oldvalue))){
            if(kw.updattr && kw.changedAttr){
                var cattr = kw.changedAttr;
                var oldvalue = kw.oldattr[cattr];
                var newvalue = kw.node.attr[cattr];
                var changekey = this.getChangeKey(kw.node) + cattr;
                var changes = this.getChangesLogger();
                var n = changes.getNode(changekey);
                if(n){
                    if(n.attr.from == newvalue){
                        changes.popNode(changekey);
                    }else{
                        n.attr.to = newvalue;
                    }
                }else{
                    changes.setItem(changekey,null,{_valuelabel:kw.reason.getElementLabel?kw.reason.getElementLabel():cattr,from:oldvalue,to:newvalue,allowed:allowed});
                }
                this.updateStatus();
            }
            return;
        }
        if (kw.value instanceof gnr.GnrBag && kw.reason!='_valuebag_') {
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
                if (changed!==false) {
                    changes.setItem(changekey, null,{_valuelabel:kw.reason.getElementLabel?kw.reason.getElementLabel():kw.node.label,
                                                    from:kw.node.attr._loadedValue,to:kw.value,allowed:allowed});
                } else {
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
        if(sourceNode.attr.rejectInvalid){
            return;
        }

        var changekey = this.getChangeKey(changepath);
        if (changekey.indexOf('emptypath') >= 0) {
            return; // PROVVISORIO per includedview con form
        }
        var invalidfields = this.getInvalidFields();
        var invalidnodes = invalidfields.getItem(changekey);
        var sourceNode_id = sourceNode.getStringId();
        var isInvalid;
        if (sourceNode.hasValidationError()) {
            isInvalid = true;
            //console.log("add validation error: "+changekey);
            if (!invalidnodes) {
                invalidnodes = {};
                invalidfields.setItem(changekey, invalidnodes);
            }
            invalidnodes[sourceNode_id] = sourceNode._id;
        } else {
            isInvalid = false;
            //console.log("remove validation error: "+changekey);
            objectPop(invalidnodes, sourceNode_id);
            if (!objectNotEmpty(invalidnodes)) {
                invalidfields.pop(changekey);
            }
        }
        if(this.allowSaveInvalid && this.getCurrentPkey() && !this.opStatus){
            this.setRecordInvalidFields(changeDataNode,isInvalid,sourceNode._validations)
        }
        this.updateStatus();
    },

    recordOwnerNode:function(changeDataNode){
        var rnode = changeDataNode.getParentNode();
        while(rnode && !(rnode.label=='record' || rnode.label[0]=='@' || rnode.attr.record_root)){
            rnode = rnode.getParentNode();
        }
        return rnode;
    },

    setRecordInvalidFields:function(changeDataNode,invalid,validationsDict){
        var recordOwnerNode = this.recordOwnerNode(changeDataNode)
        var _invalidFields = recordOwnerNode.attr['_invalidFields'] || {};
        var fpath = changeDataNode.getFullpath('static',recordOwnerNode.getValue('static'));
        if(invalid){
            _invalidFields[fpath] = {error:validationsDict.error,fieldcaption:changeDataNode.attr.name_long || fpath};
        }else{
            delete _invalidFields[fpath];
        }
        recordOwnerNode.attr['_invalidFields'] = _invalidFields;
    },


    handlePendingValidations:function(){
        if(objectNotEmpty(this._pendingValidations)){
            var that = this;
            var _pendingValidations = this._pendingValidations;
            this._pendingValidations = null;
            var sourceNode;
            for(var k in _pendingValidations){
                sourceNode = genro.src.nodeBySourceNodeId(_pendingValidations[k]);
                if(sourceNode){
                    this.resolvePendingValidation(sourceNode);
                }
            }
        }
    },

    resolvePendingValidation:function(sourceNode){
        var vpath = sourceNode.absDatapath(sourceNode.attr.value);
        var datanode = genro.getDataNode(vpath);
        var recordOwnerNode = this.recordOwnerNode(datanode);
        if(!recordOwnerNode){
            return;
        }
        var _invalidFields = recordOwnerNode.attr['_invalidFields'] || {};
        var fpath = datanode.getFullpath('static',recordOwnerNode.getValue('static'));
        var result = genro.vld.validate(sourceNode,sourceNode.getAttributeFromDatasource('value'),false,
                                true,(fpath in _invalidFields)?null:['notnull']);
        sourceNode.setValidationError(result);
        sourceNode.updateValidationStatus();
    },

    addPendingValidation:function(sourceNode){
        this._pendingValidations = this._pendingValidations || {};
        this._pendingValidations[sourceNode.getStringId()] = sourceNode._id;
    },

    isValid:function(){
        return ((this.formErrors.len()) == 0 && (this.getInvalidFields().len() == 0) && (this.getInvalidDojo().len()==0)) && this.registeredGridsStatus()!='error';
    },

    setProtectWrite:function(set){
        set = set===undefined?true:set;
        var recAttr = this.getDataNodeAttributes();
        recAttr._protect_write = set;
        this.updateStatus();
    },
    registeredGridsStatus:function(storeInForm){
        var status = null;
        for(var k in this.gridEditors){
            if(storeInForm && !this.gridEditors[k].storeInForm){
                continue;
            }
            var gridstatus=objectValues(this.gridEditors[k].status);
            if(gridstatus.indexOf('error')>=0){
                return 'error';
            }else if(gridstatus.indexOf('changed')>=0){
                status = 'changed';
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
        this.record_changed = changes.len() > 0 || this.registeredGridsStatus(true);
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
                    side = formNodeWdg?formNodeWdg['_'+sidename]:null;
                    if(side){
                        genro.dom.setClass(side,'formside_'+st,st==status);
                    }
                }
            });
        }
        this.applyDisabledStatus();
    },

    checkInvalidFields: function() {
        var node, sourceNode,node_identifiers,idx, changekey;
        var invalidfields = this.getInvalidFields();
        var invalidnodes = invalidfields.getNodes();
        for (var i = 0; i < invalidnodes.length; i++) {
            node = invalidnodes[i];
            node_identifiers = node.getValue();
            objectKeys(node_identifiers).forEach(function(idx){
                if(!genro.src.nodeBySourceNodeId(node_identifiers[idx])){
                    objectPop(node_identifiers,idx);
                }
            })
            if(!objectNotEmpty(node_identifiers)){
                invalidfields.popNode(node.label);
                continue;
            }
            objectKeys(node_identifiers).forEach(function(idx){
                sourceNode = genro.src.nodeBySourceNodeId(node_identifiers[idx]);
                result = genro.vld.validate(sourceNode, sourceNode.getAttributeFromDatasource('value'));
                if (result['modified']) {
                    sourceNode.widget.setValue(result['value']);
                }
                sourceNode.setValidationError(result);
            })
        }
        var invalidDojo=this.getInvalidDojo();
        invalidDojo.keys().forEach(function(k){
            if(!genro.src.nodeBySourceNodeId(k)){
                invalidDojo.popNode(k);
            }
        })
        this.updateStatus();
    },


    dojoValidation:function(wdg,isValid){
        var sn = wdg.sourceNode;
        var node_identifier= sn.getStringId();
        var dojoValid=this.getInvalidDojo();
        var changedNode = genro.getDataNode(wdg.sourceNode.absDatapath(wdg.sourceNode.attr.value));
        if(!this.isNodeInFormData(changedNode)){
            return;
        }
        if(changedNode && !changedNode.attr._loadedValue){
            return;
        }
        if(isValid){
            dojoValid.popNode(node_identifier);
        }else{
            if(sn.attr.rejectInvalid){
                return;
            }
            dojoValid.setItem(node_identifier,'Invalid value',{_valuelabel:sn.getElementLabel()});
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
        var sourceNode = genro.src.nodeBySourceNodeId(first[key]);
        if(sourceNode && sourceNode.widget){
            sourceNode.widget.focus();
        }
        
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
        this.formErrors = new gnr.GnrBag();
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
    validationTags: ['select','notnull','empty','case','len','min','max','email','regex','call','gridnodup','nodup','exist','remote'],
    getCurrentValidations: function(sourceNode) {
        return sourceNode.evaluateOnNode(objectExtract(sourceNode.attr, 'validate_*', true));
    },
    validate: function(sourceNode, value, userChange,validateOnly,validationTags) {
        var validations = this.getCurrentValidations(sourceNode);
        var result = this._validate(sourceNode, value, validations, validationTags || this.validationTags, userChange); //userChange added by sporcari
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
            errormessage = validreturn.message;
        } else {
            if (validreturn == false) {
                errorcode = iswarning ? 'warning' : 'error';
            } else if (typeof(validreturn) == 'string') {
                errorcode = validreturn;
            }
            validreturn = {};
        }

        if (errorcode && !errormessage) {
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
            sourceNode._exitValidation = true;
            genro.callAfter(function(){
                func.call(sourceNode,result['value'], result, validations, sourceNode.editedRowIndex, userChange);
                delete sourceNode._exitValidation;
            }, 1);
        }
    },
    validate_notnull: function(param, value) {
        if (isNullOrBlank(value)) {
            return {'errorcode':'notnull', 'required':true};
        }
    },
    validate_select: function(param, value, sourceNode, parameters) {
        if (dojo.isIE > 0) {
            return;
        }
        var result;
        if(sourceNode.widget.item && sourceNode.widget.item.attr._is_invalid_item){
            var invalidItemMsg = sourceNode.attr.invalidItem_message || _T('Invalid item');
            result = {'errorcode':'invalidItem','message':invalidItemMsg,value:null};
            sourceNode.widget._lastValueReported = null;
            return result;
        }
        if(sourceNode.widget._lastQueryError){
            return {'errorcode':'query_error','message':sourceNode.widget._lastQueryError};
        }
        delete sourceNode.widget._lastQueryError;
        var validate_notnull = sourceNode.getAttributeFromDatasource('validate_notnull');//.attr.validate_notnull;
        if ((value == undefined) || (value == '') || (value == null)) {
            if (sourceNode.widget._lastDisplayedValue != "") {
                sourceNode.widget._updateSelect();
                result = validate_notnull?{'errorcode':'missing'}:null;
                if(!validate_notnull){
                    genro.callAfter(function(){
                        if(isNullOrBlank(sourceNode.widget.getValue())){
                            sourceNode.widget.setDisplayedValue('');
                        }
                    },1);
                    if(sourceNode._wrongSearch){
                        result = {'iswarning':'Not existing','errorcode':'missing'}
                    }
                }
                delete sourceNode._wrongSearch;
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
    validate_case: function(param, value,sourceNode) {
        if (value) {
            var original = value;
            param = param.toLowerCase();
            var oldvalue = sourceNode.getAttributeFromDatasource('value') || '';
            if (param == 'upper' || param == 'u') {
                value = value.toUpperCase();
            } else if (param == 'lower' || param == 'l') {
                value = value.toLowerCase();
            }else if(oldvalue.toLowerCase()!=value.toLowerCase()){
                if ((param == 'title' || param == 't'))  {
                    value = stringCapitalize(value.toLowerCase());
                } else if (param == 'capitalize' || param == 'c') {
                    value = value[0].toUpperCase() + value.slice(1);
                }
            }
            if (original != value) {
                return {'value':value};
            }
        }
    },
    
    validate_min: function(param, value) {
        return Math.round10(value,-9)>=Math.round10(param,-9);
    },
    
    validate_max: function(param, value) {
        return Math.round10(value,-9)<=Math.round10(param,-9);
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
        if(value==null){
            return;
        }
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
            if (rpcresult.getNode('value')) {
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
                return {'iswarning':'checkit','errorcode':'Check email format'};
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
                if(kwargs.warning){
                    return {'iswarning':'duplicated_value','errorcode':kwargs.warning===true?'duplicated_value':kwargs.warning};
                }else{
                    return {'errorcode':kwargs.error || 'duplicated_value'};
                }
                
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
    recordCluster_onSaved:'reload',

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
        for (var k in kw){
            this[k] = kw[k];
        }
        if(!this.onSaved){
            var handler_onSaved = this.handlers.save.kw.onSaved;
            this.onSaved = handler_onSaved==null? this[base_handler_type+'_onSaved']:handler_onSaved;
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
    load_dummy:function(loadkw){
        var result = this.form.getFormData().deepCopy();
        this.loaded('*newrecord*',result);
        return result;
    },
    save_dummy:function(loadkw){},

    load_document:function(kw){
        /*
        pkey=discpath; it can use the static shortcut syntax;
        */
        var default_kw = kw.default_kw;
        var form=this.form;
        var that = this;
        var currPkey = this.form.getCurrentPkey();
        var data;
        var loader = this.handlers.load;
        var kw = loader.kw || {};
        var maincb = kw._onResult? funcCreate(kw._onResult,'result',form.sourceNode):function(){};
        kw = form.sourceNode.evaluateOnNode(kw);
        var envelope = new gnr.GnrBag();
        var path = currPkey;
        this.prepareDefaults(null,default_kw,kw);
        this.handlers.load.rpcmethod = loader.rpcmethod  || 'getSiteDocument';
        var deferred = genro.rpc.remoteCall(loader.rpcmethod ,
                                       objectUpdate({'path':path},kw),null,'POST',null,maincb);
        deferred.addCallback(function(result){
                var contentNode = result.popNode('content');
                var content = contentNode.getValue();
                var rec;
                if (content instanceof gnr.GnrBag){
                    rec = contentNode;
                }else{
                    rec = new gnr.GnrBag({'content':content})
                }
                that.loaded(path,rec);
                return result;
            }
        )
        if(loader.callbacks){
            this.handle_deferredCallBacks(deferred,loader.callbacks,kw);
        }
        return deferred;
    },

    save_document:function(kw){
        var data = this.form.getFormData();
        if(this.handlers.save.stripLoadedValue){
            data.walk(function(n){
                delete n.attr._loadedValue;
            });
        }
        this.handlers.save.rpcmethod = this.handlers.save.rpcmethod  || 'saveSiteDocument';
        var saver = this.handlers.save;
        var that = this;
        var path = this.form.getCurrentPkey();
        var rpc_kw = this.form.sourceNode.evaluateOnNode(this.handlers.save.kw);
        rpc_kw.path = path;
        if(path=='*newrecord*' && this.getNewPath){
            path = funcApply(this.getNewPath,{record:formData},form);
        }
        var data = data.deepCopy();
        rpc_kw.data = data;
        var deferred = genro.rpc.remoteCall(saver.rpcmethod ,rpc_kw,null,'POST',null,function(){});
        deferred.addCallback(function(result){
                    result = result || {};
                    var resultDict = {};
                    var pkeyNode=result;
                    resultDict.savedPkey = result.path || path;
                    that.form.setCurrentPkey(resultDict.savedPkey);
                    that.saved(resultDict);
                    var deferred;
                    if(that.parentStore){
                        deferred = that.parentStore.loadData();
                    }
                    that.loaded(resultDict.savedPkey,data);
                    if(deferred instanceof dojo.Deferred){
                        deferred.addCallback(function(){that.setNavigationStatus(resultDict.savedPkey);})
                    }
                    return result;
                }
            )
        if(saver.callbacks){
            this.handle_deferredCallBacks(deferred,saver.callbacks,kw);
        }
        return deferred;
    },
    
    del_document:function(pkey,callkw){
        var deleter = this.handlers.del;
        var form = this.form;
        var that = this;
        var kw =form.sourceNode.evaluateOnNode(this.handlers.del.kw);
        pkey = pkey || form.getCurrentPkey();
        var default_deletemethod = this.parentStore? this.parentStore.deletemethod || 'app.deleteFileRows':'app.deleteFileRows';
        this.handlers.del.rpcmethod = this.handlers.del.rpcmethod || default_deletemethod;
        var that = this;
        var deferred = genro.rpc.remoteCall(this.handlers.del.rpcmethod,
                                            objectUpdate({'files':pkey,'_sourceNode':form.sourceNode},kw),null,'POST',
                                                          null,function(){
                                                            if(that.parentStore){
                                                                that.parentStore.loadData();
                                                            }

                                                          });
        var cb = function(result){
            that.deleted(result,callkw);
            return result;
        };
        deferred.addCallback(cb);
        if(deleter.callbacks){
            this.handle_deferredCallBacks(deferred,deleter.callbacks,kw);
        }
        return deferred;
    },



    prepareDefaults:function(pkey,default_kw,kw){
        var form = this.form;
        var loader = this.handlers.load;
        kw = kw || objectUpdate({},loader.kw);
        var default_kwargs = objectPop(kw,'default_kwargs') || {}; 
        form.last_default_kw = objectUpdate({},default_kw);
        if(default_kwargs){
            default_kwargs = form.sourceNode.evaluateOnNode(default_kwargs);
        }
        if(!pkey || pkey=='*newrecord*'){
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

        return kw;
    },
    duplicateRecord:function(srcPkey, howmany){
        var form=this.form;
        var that = this;
        var srcPkey = srcPkey || this.form.getCurrentPkey();
        var howmany = howmany || 1;
        if (howmany=='?'){
            var that = this;
            genro.dlg.prompt('How many', {msg:_T('How many copies of current record?'),
                                          lbl:_T('How many'),
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
    handle_deferredCallBacks:function(deferred,cblist,kw){
        kw = kw || {};
        var thatnode = this.form.sourceNode;
        cblist.forEach(function(n){
            var defkw = objectUpdate({},kw);
            genro.rpc.addDeferredCb(deferred,n.getValue(),objectUpdate(defkw,n.attr),thatnode);
        });
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
        this.prepareDefaults(currPkey,default_kw,kw);
        loader.rpcmethod = loader.rpcmethod || 'loadRecordCluster';
        kw.sqlContextName = ('sqlContextName' in kw)?kw.sqlContextName:form.formId;
        var virtual_columns = objectPop(kw,'virtual_columns');
        var form_virtual_columns = form.getVirtualColumns();
        virtual_columns = virtual_columns?virtual_columns.split(','):[]
        form_virtual_columns = form_virtual_columns?form_virtual_columns.split(','):[]
        virtual_columns = virtual_columns.concat(form_virtual_columns);
        kw['_sourceNode'] = form.sourceNode;
        kw.ignoreReadOnly = ignoreReadOnly;
        var dbstoreOnDeferred = false;
        if(this.form.dbstoreField){
            objectPop(that.form.sourceNode.attr,'context_dbstore')
            dbstoreOnDeferred = true;
            var row;
            if(this.parentStore){
                let rowNode = this.parentStore.rowBagNodeByIdentifier(currPkey);
                if(rowNode){
                    row = this.parentStore.rowFromItem(rowNode);
                }
            }
            if(row && row[this.form.dbstoreField]){
                this.form.sourceNode.attr.context_dbstore = row[this.form.dbstoreField];
                dbstoreOnDeferred = false;
            }
        }
        var deferred = genro.rpc.remoteCall(loader.rpcmethod ,objectUpdate({'pkey':currPkey,
                                                  'virtual_columns':arrayUniquify(virtual_columns).join(','),
                                                  'table':this.table, timeout:0},kw),null,'POST',null,maincb);
        if(dbstoreOnDeferred){
            deferred.addCallback(function(result){
                var dbstore = result.getValue().getItem(that.form.dbstoreField);
                if(dbstore){
                    that.form.sourceNode.attr.context_dbstore = dbstore;
                }
                return result;
            });
        }
        deferred.addCallback(cb);
        if(loader.callbacks){
            this.handle_deferredCallBacks(deferred,loader.callbacks,kw);
        }
        return deferred;
    },
    save_recordCluster:function(kw){
        var form=this.form;
        var that = this;
        var saver = this.handlers.save;
        var saveKw = objectUpdate({},kw);
        var originalSaveKw = objectUpdate({},kw)
        var destPkey = objectPop(saveKw,'destPkey');
        var kw = form.sourceNode.evaluateOnNode(this.handlers.save.kw);
        objectUpdate(kw,saveKw);
        var fullRecord = objectPop(kw,'fullRecord');
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
        var data = form.getFormChanges(fullRecord);
        var cb = function(result){
            var resultDict={};
            if (result){
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
            form.waitingStatus(false);
            return resultDict;
        };
        this.handlers.save.rpcmethod = this.handlers.save.rpcmethod || 'saveRecordCluster';        
        var rpckw = objectUpdate({'data':data,'table':this.table,save_kw:originalSaveKw},kw);
        if(onSaving){
            var dosave = funcApply(onSaving,rpckw,this);
            if(dosave===false){
                return false;
            }
        }
        var waitingStatus = objectPop(rpckw,'waitingStatus');
        form.waitingStatus(waitingStatus===false?false:true);
        var deferred = genro.rpc.remoteCall(this.handlers.save.rpcmethod,
                                            rpckw,null,'POST', null,function(){});
        deferred.addCallback(cb);
        if(saver.callbacks){
            this.handle_deferredCallBacks(deferred,saver.callbacks,kw);
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
                                                          'table':this.table,'_sourceNode':form.sourceNode},kw),null,'POST',
                                                          null,function(){});
        var cb = function(result){
            that.deleted(result,callkw);
            return result;
        };
        deferred.addCallback(cb);
        if(deleter.callbacks){
            this.handle_deferredCallBacks(deferred,deleter.callbacks,kw);
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
    },
    getDefaultDestPkey:function(){
    }
});



dojo.declare("gnr.formstores.SubForm", gnr.formstores.Base, {
    load_memory:function(){
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
    save_memory:function(kw){
        var saveKw = objectUpdate({},kw);
        var form= this.form;
        var parentForm = form.getParentForm();
        var subRecord = form.getFormData();
        var parentRecord = parentForm.getFormData();
        subRecord.forEach(function(n){
            parentRecord.setItem(n.label,n.getValue());
        });
        this.saved({});
        form.loaded();
        if(kw.destPkey=='*dismiss*'){
            form.dismiss(kw);   
        }
    },
    getDefaultDestPkey:function(){
        return '*subform*';
    }
});

dojo.declare("gnr.formstores.Item", gnr.formstores.Base, {
    setLocationPath:function(locationpath,onchanged){
        if(this.form.changed){
            onchanged = onchanged || 'ignore';
            if(onchanged=='raise'){
                genro.dlg.alert('You cannot change locationpath to this form','Warning');
                return;
            }
            if(onchanged=='save'){
                this.form.save();
            }else{
                this.form.load();
            }
        }
        this.locationpath = locationpath;
    },
    load_memory:function(loadkw){
        //ITEM
        var default_kw = loadkw.default_kw || {};
        var destPkey = loadkw.destPkey;
        var form=this.form;
        var that = this;
        var data;
        var loader = this.handlers.load;
        var kw = loader.kw || {};
        var maincb = kw._onResult? funcCreate(kw._onResult,'result',form.sourceNode):function(){};
        kw = form.sourceNode.evaluateOnNode(kw);
        var envelope = new gnr.GnrBag();
        var recordLoaded = new gnr.GnrBag();
        var sourceBag = form.sourceNode.getRelativeData(this.locationpath);
        kw._newrecord = (destPkey=='*newrecord*' || sourceBag==null || sourceBag.len()===0) ;
        if(kw._newrecord){
            default_kw = objectExtract(this.prepareDefaults(null,default_kw),'default_*');
            for(var k in default_kw){
                recordLoaded.setItem(k,objectPop(default_kw,k));
            }
        }
        else if(sourceBag && this.locationpath){
            var kw = objectExtract(sourceBag.getParentNode().attr,'lastTS,caption,_protect_delete,_protect_write,_pkey',true);
            var d = sourceBag.deepCopy();
            d.walk(function(n){n.attr = {}})
                d.forEach(function(n){
                    recordLoaded.setItem(n.label,n.getValue());
                });
        }

        envelope.setItem('record',recordLoaded,kw);
        var result = envelope.getNode('record');    
        this.loaded('',result);
        return result;        
    },
    

    save_memory:function(kw){
        //ITEM
        var saveKw = objectUpdate({},kw);
        var form = this.form;
        var sourceBag = form.sourceNode.getRelativeData(this.locationpath);
        if(!sourceBag){
            sourceBag = new gnr.GnrBag();
            form.sourceNode.setRelativeData(this.locationpath,sourceBag);
        }
        var formData = form.getFormData();
        var oldsubbag,path;
        formData.walk(function(n){
            var v = n.getValue();
            var kw = {dtype:n.attr.dtype};
            path = n.getFullpath('static',formData);
            if('_displayedValue' in n.attr){
                kw._displayedValue = n.attr._displayedValue;
            }
            if('_formattedValue' in n.attr){
                kw._formattedValue = n.attr._formattedValue;
            }
            if('_valuelabel' in n.attr){
                kw._valuelabel = n.attr._valuelabel;
            }
            if(v instanceof gnr.GnrBag){
                oldsubbag = sourceBag.getItem(path);
                if(oldsubbag){
                    sourceBag.pop(path);
                }
                sourceBag.setItem(path,v);
                return '__continue__';
            }
            sourceBag.setItem(path,n.getValue(),{dtype:n.attr.dtype},{lazySet:true});
        });
        var result = {};//{savedPkey:loadedRecordNode.label,loadedRecordNode:loadedRecordNode};
        this.saved(result);
        this.form.reset();
        this.form.load(kw);
    },
    getDefaultDestPkey:function(){
        return '*loaditem*';
    }
});

dojo.declare("gnr.formstores.Collection", gnr.formstores.Base, {
    getDefaultDestPkey:function(){
        return '*norecord*';
    },
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
    },

    load_memory:function(loadkw){
        //COLLECTION
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
            this.prepareDefaults(currPkey,default_kw,kw);
            data.update(objectExtract(kw,'default_*'));
            envelope.setItem('record',data,{_newrecord:true,lastTS:null,caption:kw.newrecord_caption});
            
        }else{
            var dataNode = this.parentStore.rowBagNodeByIdentifier(currPkey);
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
        //COLLECTION
        var form = this.form;
        var saveKw = form.sourceNode.evaluateOnNode(this.handlers.save.kw);
        saveKw = objectUpdate(saveKw,kw);
        var destPkey = objectPop(saveKw,'destPkey');
        var sourceBag = form.sourceNode.getRelativeData(this.locationpath);
        var formData = form.getFormData();
        var onSaving = objectPop(saveKw,'onSaving');
        if(onSaving){
            var dosave = funcApply(onSaving,{data:formData},this);
            if(dosave===false){
                this.form.setOpStatus(null);
                return;
            }
        }
        var currPkey = form.getCurrentPkey();
        var pkeyField = this.pkeyField || '_pkey';
        var newPkey = pkeyField?formData.getItem(pkeyField):null;
        var data,olddata;
        var newrecord = currPkey=='*newrecord*';
        if(newrecord){
            data = new gnr.GnrBag();
            if (!newPkey){
                if(this.newPkeyCb){
                    newPkey = funcApply(this.newPkeyCb,{record:formData},form);
                }else{
                    newPkey = 'r_'+(sourceBag?sourceBag.len():0);
                }
                data.setItem(pkeyField,newPkey);
                formData.setItem(pkeyField,newPkey);
            }
            sourceBag.setItem(flattenString(newPkey,['.',' ']),data);
        }else{
            data = sourceBag.getItem(currPkey);
            if(currPkey != newPkey){
                data.getParentNode().label = newPkey;
            }
        }
        form.setCurrentPkey(newPkey);
        var path,v,oldsubbag;
        formData.walk(function(n){
            v = n.getValue();
            path = n.getFullpath('static',formData);
            if(v instanceof gnr.GnrBag){
                oldsubbag = data.getItem(path);
                if(oldsubbag){
                    data.pop(path);
                }
                data.setItem(path,v)
                return '__continue__';
            }
            data.setItem(path,n.getValue(),{dtype:n.attr.dtype},{lazySet:true});
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
        //COLLECTION
        var sourceBag = this.form.sourceNode.getRelativeData(this.locationpath);
        var currPkey = this.form.getCurrentPkey();
        sourceBag.popNode(currPkey);
        this.deleted(null,callkw);
    }

    
});

dojo.declare("gnr.formstores.Hierarchical", gnr.formstores.Base, {

});

