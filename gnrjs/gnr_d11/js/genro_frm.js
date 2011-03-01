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
       //dojo.subscribe('onPageStart',this,'onStartForm');
       //sourceNode.subscribe('built',function(){
       //    this.form.onStartForm();
       //});
        var that = this;
        genro.src.afterBuildCalls.push(function(){
            that.onStartForm();
        });
        
        for(var k in formAttr){
            this[k] = formAttr[k];
        }
        if(this.subforms){
            this.subforms = this.subforms.split(',');
        }
        this.formId = formId;
        this.changed = false;
        this.opStatus = null;
        this.locked = false;
        this.current_field = null;
        this.controllerPath = controllerPath;
        if(!this.store){
            this.controllerPath = this.controllerPath || 'gnr.forms.' + this.formId;
        }
        this.formDatapath = formDatapath;
        this.pkeyPath = pkeyPath;
        this.sourceNode = sourceNode;
        this.frameCode = sourceNode.attr.frameCode;
        if(this.frameCode){
            this.formParentNode = genro.getFrameNode(this.frameCode,'frame').getParentNode().getParentNode()
        }else{
            this.formParentNode = this.sourceNode.getParentNode();
        }
        this.subscribe('save,load,loaded,setLocked,navigationEvent,newrecord,deleteItem,pendingChangesAnswer,dismiss');
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
            'datetextbox':null
        };
        this.msg_saved = 'Saved';
        this.msg_unsaved_changes ="Current record has been modified.";
    },
    onStartForm:function(kw){
        var kw = kw || {};
        this.formDomNode =  genro.domById(this.formId);
        if(this.store){
            var contentSourceNode = genro.nodeById(this.formId+'_content');

            this.formContentDomNode = contentSourceNode.widget.domNode;
            this.store.init(this);            
            var that = this;
            dojo.connect(this.formContentDomNode,'onclick',function(e){
                if(genro.activeForm!=that){
                    that.focusCurrentField();
                }
            });
            var startKey = kw.startKey || this.store.startKey || this.getCurrentPkey();
            if(startKey){
                this.load({destPkey:startKey});
            }
        }
        
    },
    reset: function() {
        this.resetChanges();
        this.resetInvalidFields();
    },
    publish: function(command,kw){
        dojo.publish('form_'+this.formId+'_'+command,[kw]);
    },
    subscribe: function(command,cb,scope){
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
        dojo.subscribe(topic,scope,cb);
    },
    setDisabled:function(disable){
        disable = disable || this.isProtected();
        for (var k in this._register){
            this._register[k].setDisabled(disable);
        }
    },
    isProtected:function(){
        return this.locked || this.status=='readOnly' || this.status=='noItem'
    },
    
    setLocked:function(value){
        if(value=='toggle'){
            value = !this.locked;
        }
        this.locked = value;
        this.setDisabled(this.locked);
        this.publish('onLockChange',{'locked':this.locked});
    },
    registerChild:function(sourceNode){
        if (sourceNode.attr.parentForm || (sourceNode.attr.tag.toLowerCase() in this.autoRegisterTags)){
            this._register[sourceNode._id] = sourceNode;
            return;
        }
    },

    dismiss:function(modifiers){
        this.publish('navigationEvent',{'command':'dismiss',modifiers:modifiers});
    },
    resetChanges: function() {
        var sourceNode = genro.nodeById(this.formId);
        this.getFormData().subscribe('dataLogger',{'upd':dojo.hitch(this, "triggerUPD"),
                                                   'ins':dojo.hitch(this, "triggerINS"),
                                                   'del':dojo.hitch(this, "triggerDEL")
                                                  });
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
        this.updateInvalidField(sourceNode, sourceNode.attrDatapath('value'));
    },
    
    load: function(kw) {
        var kw = kw || {};
        if(kw['destPkey']=='*norecord*'){
            kw['destPkey'] = null;
            this.store.setNavigationStatus('*norecord*');
            this.setFormData();
        }
        if (this.store){
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
        if (this.changed && kw.destPkey &&(kw.destPkey != currentPkey)) {
            if(kw.modifiers=='Shift'){
                this.do_save(kw.destPkey);
            }else{
                this.openPendingChangesDlg(kw);
            }
            return;
        }
        this.doload_store(kw);
    },
    newrecord:function(){
        this.load({destPkey:'*newrecord*'});
    },
    
    deleteItem:function(){
        this.store.deleteItem();
    },
    
    pendingChangesAnswer:function(kw){
        var command = objectPop(kw,'command');
        if(this.store){
            var that = this;
            if(command=='save'){
                this.do_save(kw.destPkey);
            }
            else if(command=='discard'){
                this.doload_store(kw);
            }else{
                if(kw.cancelCb){
                    kw.cancelCb();
                }
            }
            
            
        }else{
            var that = this;
            if(command=='save'){
                this.setCurrentPkey(kw.destPkey);
                this.do_save()
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
    
    openPendingChangesDlg:function(kw){
         var dlg = genro.dlg.quickDialog('Pending changes',{_showParent:true,width:'250px'});
         dlg.center._('div',{innerHTML:this.msg_unsaved_changes, text_align:'center',height:'50px'})
         var form = this;
         var slotbar = dlg.bottom._('slotBar',{slots:'discard,*,cancel,save',
                                                action:function(){
                                                    dlg.close_action();
                                                    kw.command = this.attr.command;
                                                    form.publish('pendingChangesAnswer',kw);
                                                }});
         slotbar._('button','discard',{label:'Discard',command:'discard'});
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
            this._showHider();
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
            this.publish('onDismissed');
            return;
        }
        var kw = kw || {};
        var sync = kw.sync;
        this.setControllerData('loading',true);
        var pkey= ('destPkey' in kw)? kw.destPkey : this.store.getStartPkey();
        this.setCurrentPkey(pkey);
        this.publish('onLoading',pkey);
        if(pkey){
            if (!sync) {
                this._showHider();
            }
            this.resetInvalidFields(); // reset invalid fields before loading to intercept required fields during loading process
            this.setOpStatus('loading',pkey);
            this.store.load(pkey);
        }else{
            this.setDisabled(true);
            this.updateStatus();
        }
        
    },
    _showHider: function(){
        var formDomNode = genro.domById(this.formId);
        genro.dom.addClass(formDomNode, 'loadingForm');
        var formHider = document.createElement("div");
        formHider.id = this.formId + "_hider";
        dojo.addClass(formHider, 'formHider');
        formDomNode.appendChild(formHider);
    },
    _hideHider:function(){
        genro.dom.removeClass(this.formId, 'loadingForm');
        var hider = dojo.byId(this.formId + "_hider");
        if (hider) {
            genro.domById(this.formId).removeChild(hider);
        }
    },
    loaded: function(data) {
        if(data){
            this.setFormData(data);
        }
        this.publish('onLoaded',{pkey:this.getCurrentPkey()});
        this._hideHider()
        this.resetChanges(); // reset changes after loading to subscribe the triggers to the current new data bag
        var controllerData = this.getControllerData();
        this.readOnly = this.isReadOnly();
        this.newRecord = this.isNewRecord();
        controllerData.setItem('is_newrecord',this.newRecord,null,{lazySet:true});
        controllerData.setItem('loading',false,null,{lazySet:true});
        controllerData.fireItem('loaded');
        this.updateStatus();
        this.setOpStatus();
        if(this.store){
            //modalita nuova
            this.setDisabled(false)
            this.focus();
        }
        
    },
    
    focus:function(node){
        if(!this.isProtected()){
            var formContentDomNode = this.formContentDomNode || this.sourceNode.widget.domNode;
            var node = node || dijit.getFirstInTabbingOrder(formContentDomNode);
            node.focus();
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
        return (wdg.sourceNode._id in this._register)
    },
    onFocusElement:function(wdg){
        if(this.isRegisteredWidget(wdg) && (typeof(wdg.focus)=='function')){
            this.currentFocused=wdg;
        }
    },
    focusCurrentField:function(e){
        if(!this.isProtected()){
            if(this.currentFocused){
                this.currentFocused.focus();
            }
        }
    },
    save: function(always) {
        if (!this.opStatus) {
            var always = always || this.getControllerData('is_newrecord');
            if (this.changed || always) {
                var invalidfields = this.getInvalidFields();
                var invalid = (invalidfields.len() > 0);
                if (invalid) {
                    this.fireControllerData('save_failed','invalid');
                    return 'invalid:' + invalid;
                }
                return this.do_save();
            } else {
                this.fireControllerData('save_failed','nochange');
            }
        }
        else {
            genro.playSound('Basso');
        }
    },
    do_save:function(destPkey){        
        this.setOpStatus('saving');
        this.fireControllerData('saving');
        var saverNode = genro.nodeById(this.formId + '_saver');
        if(saverNode){
            saverNode.fireNode();
            return saverNode._lastDeferred;
        }else if(this.store) {
            var onSaved = this.store.onSaved;
            if(destPkey=='*dismiss*'){
                onSaved = 'dismiss';
            }
            var deferred=this.store.save(destPkey);
            var that,cb;
            that = this;
            if(onSaved=='reload' ||(destPkey&&(destPkey!=this.getCurrentPkey()))|| this.isNewRecord()){
                cb=function(resultDict){
                    destPkey = destPkey || resultDict.savedPkey;
                    if(resultDict.loadedRecord){
                        that.setCurrentPkey(destPkey);
                        that.store.loaded(destPkey,resultDict.loadedRecordNode);
                    }else{
                        that.setCurrentPkey(destPkey);
                        that.load({'destPkey':destPkey});
                    }
                }
            }else{
                cb=function(result){
                    that.reset();
                    if(onSaved=='dismiss'){
                        that.publish('onDismissed');
                    }
                };
            }
            if(deferred){
                deferred.addCallback(function(result){
                    cb(result);
                    return result
                });
            }
            return deferred;

        }
    },
    
    
    saved: function(result) {
        this.fireControllerData('saved');
        this.setOpStatus('saved');
        var savedPkey = result;
        if(this.store){
            savedPkey = result.savedPkey;
        }
        this.publish('onSaved',{pkey:savedPkey});
        this.publish('message',{message:this.msg_saved,sound:'$onsaved'});
        return result;

    },

    openForm:function(idx, pkey) {
        if(this.store && false){
            console.log('idx',idx,'pkey',pkey);
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
        return path?cd.getItem('path'):cd;
    },
    setControllerData: function(path,value) {
        this.getControllerData().setItem(path,value,null,{lazySet:true});
    },
    fireControllerData: function(path,value,reason) {
        this.getControllerData().fireItem(path,value,reason);
    },
    setFormData:function(data){
        this.sourceNode.setRelativeData(this.formDatapath,data || new gnr.GnrBag());
    },
    getDataNodeAttributes:function(){
        return this.sourceNode.getRelativeData(this.formDatapath).getParentNode().attr;
    },
    isNewRecord:function(){
        return this.getDataNodeAttributes()._newrecord;
    },
    isReadOnly:function(){
        return this.getDataNodeAttributes()._readonly;
    },
    
    hasChanges: function() {
        return this.getControllerData('changed'); 
    },
    getFormChanges: function() {
        return this._getRecordCluster(this.getFormData(), true);
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
        this.sourceNode.getValue().walk(function(n) {
            if (n.attr._virtual_column) {
                virtual_columns.push(n.attr._virtual_column)
            }
        });
        return virtual_columns.join(',');
    },


    _getRecordCluster: function(record, changesOnly, result, removed, parentpath) {
        if (record) {
            var parentpath = parentpath || genro.nodeById(this.formId).absDatapath('');
            var data = new gnr.GnrBag();
            data.__isRealChange = false;
            var node, sendBag, value, currpath, sendback;
            var recInfo = record.attributes();
            var isNewRecord = recInfo._newrecord;
            var bagnodes = record.getNodes();
            for (var i = 0; i < bagnodes.length; i++) {
                node = bagnodes[i];
                sendback = changesOnly ? node.attr._sendback : true;
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
                    sendBag = (sendback == true) || this.hasChangesAtPath(currpath);
                    if (sendBag) {
                        value.walk(function(n){
                            if('_loadedValue' in n.attr){
                                var loadedValue = objectPop(n.attr,'_loadedValue');
                                n.attr.__old = asTypedTxt(loadedValue, n.attr.dtype);
                            }
                        },'static')
                        data.setItem(node.label, value, objectUpdate({'_gnrbag':true}, node.attr));
                        data.__isRealChange = true;
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
                } else if (kw.node.attr._loadedValue == kw.value) {//value = _loadedValue
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
        this.updateStatus();
    },
    getChangeKey:function(changekey) {
        if (typeof(changekey) != 'string') {//changekey is a data node
            changekey = changekey.getFullpath(null, true);
        }
        return changekey.replace(/[\.\?]/g, '_');
    },
    updateInvalidField:function(sourceNode, changekey) {
        if (sourceNode == true) {
            return;
        }
        changekey = this.getChangeKey(changekey);
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
            if (!objectNotEmpty()) {
                invalidfields.pop(changekey);
            }
        }
        this.updateStatus();
    },
    updateStatus:function(){
        var invalidfields = this.getInvalidFields();
        var invalid = (invalidfields.len() > 0);
        this.setControllerData('valid',!invalid);
        var status;
        if(this.pkeyPath && !this.getCurrentPkey()){
            status = 'noItem';
        }
        else if(this.isReadOnly()){
            status = 'readOnly';
        }
        else if(invalid){
            status = 'error'
        }
        else{
            var changes = this.getChangesLogger();
            var changed = (changes.len() > 0)
            this.changed = changed;
            this.setControllerData('changed',changed);
            status = this.changed ? 'changed':'ok';
        }
        if(this.status!=status){
            this.status=status;
            this.publish('onStatusChange',{'status':this.status});
            var formDomNode = this.formDomNode
            dojo.forEach(this._status_list,function(st){
                genro.dom.setClass(formDomNode,'form_'+st,st==status);
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

            //console.log("value: " +value+" result: "+ result.toSource());
            if (result['modified']) {
                sourceNode.widget.setValue(result['value']);
            }
            sourceNode.setValidationError(result);
            return result['value'];

        }
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
    resetInvalidFields:function(){
        this.getControllerData().setItem('invalidFields',new gnr.GnrBag());
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
        var command = kw.command;
        var pkey;
        if(command=='add'){
            pkey = '*newrecord*';
        }else if (command=='dismiss'){
            pkey = '*dismiss*';
        }
        else{
            pkey = this.store.navigationEvent(kw);
        }
         this.load({destPkey:pkey,modifiers:kw.modifiers,cancelCb:kw.cancelCb});
        
    }  
});

dojo.declare("gnr.GnrValidator", null, {
    validationTags: ['dbselect','notnull','empty','case','len','email','regex','call','nodup','exist','remote'],
    getCurrentValidations: function(sourceNode) {
        return sourceNode.evaluateOnNode(objectExtract(sourceNode.attr, 'validate_*', true));
    },
    validateInLoading: function(sourceNode, value) {
        var validations = this.getCurrentValidations(sourceNode);
        return this._validate(sourceNode, value, validations, ['notnull']);
    },
    validate: function(sourceNode, value, userChange) {
        var validations = this.getCurrentValidations(sourceNode);
        var result = this._validate(sourceNode, value, validations, this.validationTags, userChange); //userChange added by sporcari
        this.exitValidation(result, sourceNode, validations, userChange);
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
    validate_len: function(param, value) {
        if (value) {
            if (param.indexOf(':') >= 0) {
                var sl = param.split(':');
                if (sl[1]) {
                    if (value.length > parseInt(sl[1])) {
                        return 'max';
                    }
                }
                if (sl[0]) {
                    if (value.length < parseInt(sl[0])) {
                        return 'min';
                    }
                }
            } else {
                if (value.length != parseInt(param)) {
                    return 'fixed';
                }
            }
        }
    },
    validate_regex: function(param, value) {
        if (value) {
            var not = false;
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
        var rpcresult = genro.rpc.remoteCall(param, objectUpdate({'value':value}, parameters), null, 'GET');
        if (rpcresult instanceof gnr.GnrBag) {
            var result = {};
            result['errorcode'] = rpcresult.getItem('errorcode');
            result['iswarning'] = rpcresult.getItem('iswarning');
            if (rpcresult.getItem('value')) {
                result['value'] = rpcresult.getItem('value');
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
        var col = ((typeof(param) == 'string') && param) ? param : sourceNode.getAttributeFromDatasource('value');
        if (value) {
            var colvalues = genro.wdgById(sourceNode.gridId).getColumnValues(col);
            var n = dojo.indexOf(colvalues, value);
            if ((n != -1) && (n != sourceNode.editedRowIndex)) {
                return false;
            }
        }
    },
    validate_nodup: function(param, value, sourceNode) {
        var dbfield = ((typeof(param) == 'string') && param) ? param : sourceNode.getAttributeFromDatasource('dbfield');
        if (value) {
            var n = genro.rpc.getRecordCount(dbfield, value);
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

//formstores
dojo.declare("gnr.formstores.Base", null, {
    constructor:function(kw,handlers){
        objectPop(kw, 'tag');
        this.handlers = handlers;
        this.storepath = objectPop(kw,'storepath');
        this.parentStoreCode = objectPop(kw,'parentStore')
        //this.startKey = objectPop(kw,'startKey');
        //this.table = kw.table;
        //this.onSaved = kw.onSaved;
        ;
        var base_handler_type = objectPop(kw,'handler');
        var handlerKw = objectExtract(kw,'handler_*');
        var handler,handler_type,method,actionKw,callbacks;
        var that = this;
        var rpcmethod;
        dojo.forEach(['save','load','delete'],function(action){
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
            that.handlers[action]= {'kw':objectUpdate(actionKw,handler),'method':method,'callbacks':callbacks,rpcmethod:rpcmethod};
        });
        for (k in kw){
            this[k] = kw[k];
        }
    },
    
    init:function(form){
        this.form = form;
        if(this.parentStoreCode){
            this.parentStore = genro.getStore(this.parentStoreCode);
        }
    },
    
    getStartPkey:function(){
        return;
    },
    getParentStoreData:function(){
        return this.parentStore.getData();
    },
    load_memory:function(){
        var sourcebag = this.form.sourceNode.getRelativeData(this.sourcepath);
        var fields = this.fields.split(',');
        var result = new gnr.GnrBag();
        dojo.forEach(fields,function(n){
            result.setItem(n,sourcebag.getItem(n));
        });
        this.loaded(null,result);
    },
    
    
    save_memory:function(){
        var fields = this.fields.split(',');
        var sourcebag = this.form.sourceNode.getRelativeData(this.sourcepath);
        var form = this.form;
        dojo.forEach(fields,function(n){
            sourcebag.setItem(n,form.getFormData(n));
        });
        this.saved();
    },
    delete_memory:function(){
        
    },

    load_recordCluster:function(){
        var form=this.form;
        var that = this;
        var currPkey = this.form.getCurrentPkey();
        var cb = function(result){
            that.loaded(currPkey,result);
        };
        var kw =form.sourceNode.evaluateOnNode(this.handlers.load.kw);
        this.handlers.load.rpcmethod = this.handlers.load.rpcmethod || 'loadRecordCluster';
        genro.rpc.remoteCall(this.handlers.load.rpcmethod ,objectUpdate({'pkey':currPkey,
                                                  'virtual_columns':form.getVirtualColumns(),
                                                  'table':this.table},kw),null,'POST',null,cb);
    },
    save_recordCluster:function(destPkey){
        var form=this.form;
        var that = this;
        var saver = this.handlers.save;
        var kw =form.sourceNode.evaluateOnNode(this.handlers.save.kw);
        if (destPkey){
            kw._autoreload=destPkey
        }else if(this.onSaved=='reload' || this.form.isNewRecord()){
            kw._autoreload=true
        }
        //kw._autoreload = null;
        var autoreload =kw._autoreload;
        
        var cb = function(result){
            if (result){
                var resultDict={}
                if(autoreload){
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
        var deferred = genro.rpc.remoteCall(this.handlers.save.rpcmethod,
                                            objectUpdate({'data':form.getFormChanges(),
                                                          'table':this.table},kw),null,'POST',
                                                          null,function(){});
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
    delete_recordCluster:function(){
        
    },
    loaded:function(pkey,result){
        this.setNavigationStatus(pkey)
        if(this.subforms){
            
        }
        this.form.loaded(result);
    },
    saved:function(result){
        return this.form.saved(result);
    },
    save:function(destPkey){
        return this.handlers.save.method.call(this,destPkey);
    },
    load:function(){
        return this.handlers.load.method.call(this);
    },
    setNavigationStatus:function(){
        return;
    },
    navigationEvent:function(kw){
    }
});

dojo.declare("gnr.formstores.Item", gnr.formstores.Base, {

});

dojo.declare("gnr.formstores.Collection", gnr.formstores.Base, {
    getStartPkey:function(){
        return this.getNavigationPkey(0);
    },    
    setNavigationStatus:function(pkey){
        var currIdx = this.parentStore.getIdxFromPkey(pkey);
        var kw = {}
        if(currIdx<0){
            kw.first = true;
            kw.last = true;
        }
        else if(currIdx==0){
            kw.first = true;
        }else if(currIdx>=this.parentStore.len()-1){
            kw.last = true;
        }
        this.form.publish('navigationStatus',kw);
        return;
    },

    navigationEvent:function(kw){
        var command = kw.command;
        return this.parentStore.getNavigationPkey(command,this.form.getCurrentPkey());
    }
    
});

dojo.declare("gnr.formstores.Hierarchical", gnr.formstores.Base, {

});


