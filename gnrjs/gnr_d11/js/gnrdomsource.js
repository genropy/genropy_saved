/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module GnrDomSource : Genro clientside structure implementation for web elements
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



//######################## class BagNode##########################
dojo.declare("gnr.GnrDomSourceNode", gnr.GnrBagNode, {
    application:function() {
        return this.getParentBag().getRoot().application;
    },
    freeze:function() {
        this._isFreezed = true;
        return this;
    },
    unfreeze:function(noRebuild) {
        this._isFreezed = false;
        if (!noRebuild) {
            this.rebuild();
        }
    },
    isFreezed:function(){
        var parentNode = this.getParentNode();
        return this._isFreezed?true:parentNode?parentNode.isFreezed():false;
    },
    
    getBuiltObj:function() {
        return this.getWidget(true) || this.getDomNode();
    },
    
    getParentBuiltObj:function() {
        var parentNode = this.getParentNode();
        if (parentNode) {
            return parentNode.getBuiltObj();
        }
    },

    getDomNode:function() {
        if (this.domNode) {
            return  this.domNode;
        }
        if (this.widget) {
            return  this.widget.containerNode || this.widget.domNode;
        }

    },
    
    getWidget:function(notEnclosed) {
        if(this.domNode && !notEnclosed){
            return dijit.getEnclosingWidget(this.domNode);
        }
        var curr = this;
        var currvalue;
        while(curr && !curr.widget && !curr.domNode){
            currvalue = curr.getValue();
            if(currvalue instanceof gnr.GnrBag){
                curr = currvalue.getNode('#0');
            }else{
                return;
            }
        }
        return curr?curr.widget:null;
    },
    
    
    _relativeGetter:function(prefix){
        var that = this;
        return function(path){
            return that.getRelativeData(prefix? prefix+path:path);
        };
    },
    
    getParentWidget:function() {
        var parentNode = this.getParentNode();
        if (parentNode) {
            return parentNode.widget?parentNode.widget : parentNode.getParentWidget();
        }
    },
    destroy:function() {
        if (this.widget) { /* this is a widget*/
            this.widget.destroyRecursive();
        }
        else if (this.domNode) {
            var widgets = dojo.query('[widgetId]', this.domNode);
            widgets = widgets.map(dijit.byNode);     // Array
            dojo.forEach(widgets, function(widget) {
                widget.destroy();
            });
            while (this.domNode.childNodes.length > 0) {
                dojo._destroyElement(this.domNode.childNodes[0]);
            }
            dojo._destroyElement(this.domNode);
        }
    },

    trigger_data:function(prop, kw) {
        var dpath = kw.pathlist.slice(1).join('.');
        var mydpath = this.attrDatapath(prop);
        if (mydpath == null) {
            return;
        }
        if (mydpath.indexOf('#parent') > 0) {
            mydpath = gnr.bagRealPath(mydpath);
        }
        if (mydpath.indexOf('?') >= 0) {
            if ((kw.updattr) || (kw.evt=='fired') ||(mydpath.indexOf('?=') >= 0)) {
                mydpath = mydpath.split('?')[0];
            }
        }

        var trigger_reason = null;
        var eqpath = (mydpath == dpath);
        if (eqpath) {
            trigger_reason = 'node';
        }
        var changed_container = (mydpath.indexOf(dpath + '.') == 0);
        if (changed_container) { 
            trigger_reason = 'container';
        }
        var changed_child = (dpath.indexOf(mydpath + '.') == 0);
        if (changed_child) {
            trigger_reason = 'child';
        }
        if (trigger_reason) {
            //if((mydpath==dpath)|| (mydpath.indexOf(dpath+'.')==0)  ||(dpath.indexOf(mydpath+'.')==0)){
            //genro.debug(kw.evt+' data node at path:'+dpath+' ('+prop+') - updating sourceNode:'+mydpath,null,'trigger_data');
            if ((kw.evt == 'fired') && (trigger_reason == 'child')) {
                // pass fired event on child datapath: get only parent changes for variable datapaths
            } else if (kw.evt == 'invalid') {
                if (this.widget) {
                    this.widget.focus();
                }
            } else if (this._dataprovider /*&& (kw.evt!='del')*/) { //VERIFICARE perché erano escusi gli eventi DEL
                if(prop=='_timing'){
                    this.setTiming(kw.value);
                }else{
                    this.setDataNodeValue(kw.node, kw, trigger_reason);
                }
                
            }
            else {
                if (kw.reason != this) {
                    this.updateAttrBuiltObj(prop, kw, trigger_reason);
                }
            }
        }
    },
    fireNode: function(runKwargs) {
        return this.setDataNodeValue(runKwargs);
    },
    setDataNodeValue:function(nodeOrRunKwargs, kw, trigger_reason, subscription_args) {

        var delay = this.attr._delay;
        if(delay == 'auto'){
            delay = null;//genro.rpc.rpc_level>2? genro.rpc.rpc_level * 100 : null;
        }
        if (delay) {
            if (this.pendingFire) {
                clearTimeout(this.pendingFire);
            }
            this.pendingFire = setTimeout(dojo.hitch(this, 'setDataNodeValueDo', nodeOrRunKwargs, kw, trigger_reason,subscription_args),delay);
        } else if(this.attr._ask){
            if((kw && kw.reason == 'autocreate' ) || (trigger_reason != 'node')){
                return; //askmode
            }
            var currentAttributes = this.currentAttributes();
            if(!this.attr._ask_if ||  funcApply('return ('+this.attr._ask_if+');',currentAttributes,this) ){
                var that = this;
                var _ask_onCancel= this.attr._ask_onCancel || function(){};
                _ask_onCancel = funcCreate(_ask_onCancel,'kwargs',this);
                genro.dlg.ask(currentAttributes._ask_title || 'Warning',currentAttributes._ask,null,
                            {confirm:function(){that.setDataNodeValueDo(nodeOrRunKwargs, kw, trigger_reason, subscription_args);},
                            cancel:function(){_ask_onCancel(currentAttributes)}});
            }
        }
        else{
            return this.setDataNodeValueDo(nodeOrRunKwargs, kw, trigger_reason, subscription_args);
        }
    },

    setDataNodeValueDo:function(nodeOrRunKwargs, kw, trigger_reason, subscription_args) {
        var node;
        var runKwargs={};
        var isFiredNode=!(nodeOrRunKwargs instanceof gnr.GnrBagNode)
        if(isFiredNode){
            runKwargs = nodeOrRunKwargs;
        }else{
            node = nodeOrRunKwargs;
        }
        var attributes = objectUpdate({}, this.attr);
        var _userChanges = objectPop(attributes, '_userChanges');
        var _trace = objectPop(attributes, '_trace');
        var _trace_level = objectPop(attributes, '_trace_level') || 0;
        if ((kw && kw.reason == 'autocreate' ) || ( _userChanges && trigger_reason != 'node')) {
            return;
        }
        objectExtract(attributes, 'subscribe_*');
        var tag = objectPop(attributes, 'tag').toLowerCase();
        var path = objectPop(attributes, 'path');
        objectPop(attributes, '_onStart');
        objectPop(attributes, '_onBuilt');
        objectPop(attributes, '_fired_onStart');
        objectPop(attributes, 'datapath');
        var destinationPath, dataNode;
        if (path) { // if it has a result path set it to the returned value
            destinationPath = this.absDatapath(path);
            dataNode = genro.getDataNode(destinationPath, true);
        }
        objectPop(attributes, '_init');
        objectPop(attributes, '_delay');
        var _if = objectPop(attributes, '_if');
        var _else = objectPop(attributes, '_else');
        var expr;
        if (tag == 'dataformula') {
            expr = objectPop(attributes, 'formula');
        } else if ((tag == 'datacontroller') || (tag == 'datascript')) {
            expr = objectPop(attributes, 'script');
        } else {
            expr = objectPop(attributes, 'method');
            expr = this.getAttributeFromDatasource('method');
        }
        if (_trace) {
            console.log("TRACE " + tag + "(" + _trace + ")");
            if (_trace_level >= 2) {
                console.log("trigger_reason=" + trigger_reason);
                console.log("kw=");
                console.log(kw);
            }
            if (_trace_level >= 3) {
                console.log("expr=");
                console.log(expr);
            }
        }
        var argValues = [node, {'kw':kw, 'trigger_reason':trigger_reason},trigger_reason];
        var argNames = ['_node', '_triggerpars','_reason']; //_node is also in _triggerpars.kw.node: todo remove (could be used as $1)
        var kwargs = {};
        if (subscription_args) {
            argNames.push(trigger_reason);
            argValues.push(subscription_args);
            if ((subscription_args.length == 1) && (typeof(subscription_args[0]) == 'object')) {
                for (var k in subscription_args[0]) {
                    argNames.push(k);
                    argValues.push(subscription_args[0][k]);
                    kwargs[k] = subscription_args[0][k];
                }
                argNames.push('_subscription_kwargs');
                argValues.push(subscription_args[0]);
                kwargs['_subscription_kwargs'] = subscription_args[0];
            }
        }
        var val;
        if (_trace && (_trace_level > 0)) {
            console.log('Arguments:');
        }
        for (var attrname in attributes) {
            argNames.push(attrname);
            val = this.getAttributeFromDatasource(attrname);
            argValues.push(val);
            kwargs[attrname] = val;
            if (_trace && (_trace_level > 0)) {
                console.log("--- " + attrname + " ---");
                console.log(val);
            }
        }
        objectUpdate(kwargs,runKwargs);
        var if_result = true;
        if (_if) {
            if_result = funcCreate('return (' + _if + ')', argNames.join(',')).apply(this, argValues);
            if (_trace && (_trace_level > 0)) {
                console.log("_if=" + if_result);
            }
        }
        if (tag == 'dataformula' || tag == 'datascript' || tag == 'datacontroller' || tag == 'datarpc') {
            var val;
            if (! if_result) {
                if (!_else) {
                    return;
                }
                expr = _else;
            }

            if (tag == 'datarpc' && (expr != _else)) {
                var doCall = true;
                var domsource_id = this.getStringId();
                var method = expr;
                // var httpMethod = objectPop(kwargs, '_POST') ? 'POST' : 'GET';

                var httpMethod = objectPop(kwargs, '_POST') === false? 'GET' : 'POST';
                var _onResult = objectPop(kwargs, '_onResult');
                var _onError = objectPop(kwargs, '_onError');
                var _lockScreen = objectPop(kwargs, '_lockScreen');
                var _execClass = objectPop(kwargs, '_execClass');
                objectPop(kwargs, 'nodeId');
                var _onCalling = objectPop(kwargs, '_onCalling');
                var origKwargs = objectUpdate({}, kwargs);
                if (_onResult) {
                    _onResult = funcCreate(_onResult, 'result,kwargs,old', this);
                }
                if (_onError) {
                    _onError = funcCreate(_onError, 'error,kwargs', this);
                }
                var cb = function(result, error) {
                    if (_lockScreen) {
                        genro.lockScreen(false, domsource_id);
                    }
                    if(_execClass){
                        genro.dom.removeClass(dojo.body(),_execClass);
                    }
                    if (error) {
                        if (_onError) {
                            _onError(error, origKwargs);
                        }
                        //else {
                        //    genro.dlg.alert(error, 'Server error');
                        //}
                    }
                    else {
                        var oldValue;
                        if (dataNode) {
                            oldValue = dataNode.getValue();
                            dataNode.setValue(result);
                            dataNode._rpcNode_id = this._id;
                        }
                        if (_onResult) {
                            _onResult(result, origKwargs, oldValue);
                        }
                    }
                };
                if(_execClass){
                    genro.dom.addClass(dojo.body(),_execClass);
                }
                if (_onCalling) {
                    doCall = funcCreate(_onCalling, (['kwargs'].concat(argNames)).join(',')).apply(this, ([kwargs].concat(argValues)));
                }
                objectExtract(kwargs, '_*');
                if (doCall != false) {
                    if (_lockScreen) {
                        genro.lockScreen(true, domsource_id);
                    }   
                    if (!this._deferredRegister){
                        this._deferredRegister ={};
                    }   
                    kwargs['_sourceNode'] = this;
                    var deferred = genro.rpc.remoteCall(method, kwargs, null, httpMethod, null, cb);
                    if(deferred){
                        this._deferredRegister[deferred.id]= deferred;
                        this._lastDeferred = deferred;
                        var that = this;
                        deferred.addCallback(function(result){
                            delete that._deferredRegister[deferred.id];
                            return result;
                        });
                        if(this._callbacks){
                            this._callbacks.forEach(function(n){
                                var kw = objectUpdate({},kwargs);
                                kw['_isFiredNode'] = isFiredNode;
                                genro.rpc.addDeferredCb(deferred,n.getValue(),objectUpdate(kw,n.attr),that);
                            });
                        }
                    }
                    return deferred;
                }
            }
            else {
                var result;
                if (!expr) {
                    result = new gnr.GnrBag(kwargs);
                } else {
                    expr = (tag == 'dataformula') ? 'return ' + expr : expr;
                    result = funcCreate(expr, (['_kwargs'].concat(argNames)).join(',')).apply(this, ([kwargs].concat(argValues)));
                }
                if (dataNode) { // if it has a dataNode set it to the returned value
                    dataNode.setValue(result);
                }
            }
        }
        else {
            if (if_result) {
                var method = expr;
                var cacheTime = objectPop(attributes, 'cacheTime', -1);
                var isGetter = objectPop(attributes, 'isGetter', false);
                attributes.sync = ('sync' in attributes) ? attributes.sync : true;
                attributes['_sourceNode'] = this;
                var resolver = genro.rpc.remoteResolver(method, attributes, {'cacheTime':cacheTime,
                    'isGetter':isGetter});
                dataNode.setValue(resolver, true, attributes);
            }
        }
        
    },
    setAttributeInDatasource: function(attrname, value, doTrigger, attributes, forceChanges) {
        var doTrigger = (doTrigger == null) ? this:doTrigger;
        var path = this.attrDatapath(attrname);
        var old_value = genro._data.getItem(path);
        //if (forceChanges){
        //    genro._data.setItem(path,v,null,{'doTrigger':false});
        //}
        if (old_value != value || (forceChanges && value != null)) {
            genro._data.setItem(path, value, attributes, {'doTrigger':doTrigger});
        }
    },
    defineForm: function(formId, formDatapath, controllerPath, pkeyPath,kw) {
        this.form = new gnr.GnrFrmHandler(this, formId, formDatapath, controllerPath, pkeyPath,kw);
    },
    hasDynamicAttr: function(attr) {
        return (this._dynattr && (attr in this._dynattr));
    },

    getRelativeData: function(path, autocreate, dflt) {
        var path = this.absDatapath(path);
        var value;
        if (path != null) {
            if (autocreate) {
                var node = genro._data.getNode(path, false, autocreate, dflt);
                if (path.indexOf('?') >= 0) {
                    value = genro._data.getItem(path);
                } else if (node) {
                    value = node.getValue(null, {'_sourceNode':this});
                }
            } else {
                if (path.indexOf('?') >= 0) {
                    value = genro._data.getItem(path);
                } else {
                    var node = genro._data.getNode(path);
                    if (node) {
                        value = node.getValue(null, {'_sourceNode':this});
                    }
                }

            }
        }
        return value;
    },
    fireEvent:function(path, value, attributes, reason, delay) {
        this.setRelativeData(path, value || true, attributes, true, reason, delay);
    },
    setRelativeData: function(path, value, attributes, fired, reason, delay,_kwargs) {
        // var reason=reason || this
        if (delay) {
            setTimeout(dojo.hitch(this, 'setRelativeData', path, value, attributes, fired, reason,null,_kwargs), delay);
        } else {
            var reason = reason == null ? true : reason;
            var oldpath = path;
            var path = this.absDatapath(path);
            if (fired) {
                genro._firingNode = this;
                genro._data.fireItem(path, value, attributes, {'doTrigger':reason});
                genro._firingNode = null;
            } else {
                genro._data.setItem(path, value, attributes, objectUpdate({'doTrigger':reason,lazySet:true},_kwargs));
            }
        }
    },
    getAttributeFromDatasource: function(attrname, autocreate, dflt) {
        var attrname = attrname || 'value';
        var value = this.attr[attrname];
        value = this.currentFromDatasource(value, autocreate, dflt);
        if (((attrname == 'innerHTML')) && (this.attr.mask || this.attr.format || (value instanceof gnr.GnrBag)) ) {
            var kw = objectUpdate({},this.attr);
            objectPop(kw,attrname)
            value = genro.formatter.asText(value, this.evaluateOnNode(kw));
        }
        return value;
    },
    
    currentFromDatasource: function(value, autocreate, dflt) {
        var path;
        if (typeof(value) == 'string') {
            if (this.isPointerPath(value)) {
                if (value.indexOf('==') == 0) {
                    var argNames = [];
                    var argValues = [];
                    for (var attr in this.attr) {
                        var attrval = this.attr[attr];
                        if ((typeof(attrval) != 'string') || (attrval.indexOf('==') != 0)) { // if it is not a formula: for avoid infinite loop
                            argNames.push(attr);
                            argValues.push(this.getAttributeFromDatasource(attr));
                        }
                    }
                    try {
                        value = funcCreate('return ' + value.slice(2), argNames.join(',')).apply(this, argValues);
                    } catch(e) {
                        if (console != undefined) {
                            console.log('ERROR in ' + value);
                            console.log(e);
                            console.log('arguments: ');
                            for (var i = 0; i < argNames.length; i++) {
                                console.log(argNames[i] + " = " + argValues[i]);
                            }
                        }
                        throw e;
                    }
                } else {
                    value = this.getRelativeData(value, autocreate, dflt);
                }
            }
        }
        return value;
    },
    attrDatapath: function(attrname,targetNode) {
        targetNode = targetNode || this;
        if (!attrname) {
            return targetNode.absDatapath();
        }
        var attrvalue = this.attr[attrname];
        var path = null;
        if (typeof(attrvalue) == 'string') {
            if (this.isPointerPath(attrvalue)) {
                attrvalue = attrvalue.slice(1);
            }
            path = targetNode.absDatapath(attrvalue);
        }
        return path;
    },
    isPointerPath: function(path) {
        return path? ((path.indexOf('^') == 0) || (path.indexOf('=') == 0)):false;
    },
    nodeById:function(nodeId){
        return genro.nodeById(nodeId,this); 
    },
    
    wdgById:function(nodeId){
        return genro.wdgById(nodeId,this); 
    },
    
    domById:function(nodeId){
        return genro.domById(nodeId,this); 
    },
    
    symbolicDatapath:function(path) {
        var attachpath;
        var pathlist = path.split('.');
        var nodeId = pathlist[0].slice(1);
        var relpath = pathlist.slice(1).join('.');
        if(nodeId=='WORKSPACE'){
            node=this.attributeOwnerNode('_workspace');
            genro.assert(node,'with WORKSPACE path you need an ancestor node with attribute _workspace');
            return 'gnr.workspace.'+(node.attr.nodeId || node.getStringId())+'.'+relpath;
        }
        if(nodeId=='DATA'){
            return relpath;
        }
        var currNode = this.nodeById(nodeId); 
        if (!currNode) {
            console.error('not existing nodeId:' + nodeId);
        }
       
        if(relpath=='*S'){
            return currNode.getFullpath().replace('main.','*S.');
        }
        path = currNode.absDatapath(relpath ? '.' + relpath : '');
        return path;
    },
    absDatapath: function(path) {
        var path = path || '';
        if (this.isPointerPath(path)) {
            path = path.slice(1);
        }
        if (path.indexOf('#') == 0) {
            return this.symbolicDatapath(path);
        }
        if(path=='.'){
            return this.absDatapath();
        }
        var currNode = this;
        var datapath;
        while (currNode && ((!path) || path.indexOf('.') == 0)) {
            datapath = currNode.attr.datapath;
            if(typeof(datapath)=='function'){
                datapath = datapath.call(currNode,datapath);
            }
            if (datapath) {
                if (this.isPointerPath(datapath)) {
                    datapath = currNode.getAttributeFromDatasource('datapath');
                    if (!datapath) {
                        return null;
                    }
                }
                if (datapath.indexOf('#') == 0) {
                    datapath = currNode.symbolicDatapath(datapath);
                }
                path = datapath + path;
            }
            currNode = currNode.getParentNode();
        }
        if (path.indexOf('.') == 0) {
            console.error('unresolved relativepath ' + path);
        }
        path = path.replace('.?', '?');
        if (path.indexOf('#parent') > 0) {
            path = gnr.bagRealPath(path);
        }
        return path;
    },

    connect: function(target, eventname, handler) {
        var eventname = ((!eventname) || eventname == 'action') ? target.gnr._defaultEvent : eventname;
        var handler = dojo.hitch(this, funcCreate(handler));
        //var that=this;
       //var h = handler;
       //var handler = function(evt){
       //    funcApply(h, objectUpdate({evt:evt},that.currentAttributes()),that,['evt'],[evt]);
       //}        
        if (target.domNode) {/* connect to a widget*/
            if (eventname in target) {
                dojo.connect(target, eventname, handler);
            } else {
                dojo.connect(target.domNode, eventname, handler);
            }
        }
        else {/* connect to a domnode*/
            dojo.connect(target, eventname, handler);
        }
    },
    updateContent: function(kw) {
        if (this._resolver) {
            var mode = kw ? 'reload' : null;
            this.getValue(mode, kw);
            this.widget.resize();
        }
    },
    setRemoteContent:function(kwargs) {
        kwargs.sync = ('sync' in kwargs) ? kwargs.sync : true;
        var cacheTime = objectPop(kwargs, 'cacheTime');
        var resolver = new gnr.GnrRemoteResolver(kwargs, false, cacheTime);
        resolver.updateAttr = true;
        this.setResolver(resolver);
    },
    _bld_data: function() {
    },
    _bld_dataremote: function() {
    },
    _bld_dataformula: function() {
    },
    _bld_datascript: function() {
    },
    _bld_datacontroller: function() {
    },
    _bld_datarpc: function() {
        this._callbacks = this.getValue();
        this._value = null;
    },
    _bld_script: function() {
        if (this.attr.src) {
            genro.dom.loadJs(this.attr.src);
        } else {
            dojo.eval(this.getValue());
        }

    },
    _bld_stylesheet:function() {
        if (this.attr.href) {
            genro.dom.loadCss(this.attr.href, this.attr.cssTitle);
        } else {
            genro.dom.addStyleSheet(this.getValue(), this.attr.cssTitle);
        }
    },

    _bld_css:function() {
        genro.dom.addCssRule(this.getValue());
    },
    _bld_remote:function() {
        var kwargs = objectUpdate({}, this.attr);
        objectPop(kwargs, 'tag');
        this.getParentNode().setRemoteContent(kwargs);
    },
    registerDynAttr: function(attr) {
        this._dynattr = this._dynattr || {};
        this._dynattr[attr] = null;
    },
    registerNodeDynAttr: function(returnCurrentValues) {
        this._resetDynAttributes();
        var attributes = {};
        var attrvalue;
        for (var attr in this.attr) {
            attrvalue = this.attr[attr];
            attributes[attr] = attrvalue;
            if ((typeof(attrvalue) == 'string') && this.isPointerPath(attrvalue)) {
                if ((attrvalue.indexOf('^') == 0)) {
                    this.registerDynAttr(attr);
                }
                if (returnCurrentValues) {
                    attributes[attr] = this.getAttributeFromDatasource(attr);
                }
                if(attrvalue.indexOf('==')==0){
                    this._formulaAttributes = this._formulaAttributes || {};
                    this._formulaAttributes[attr] = attrvalue.slice(2);
                }
            }
        }
        return attributes;
    },
    onNodeCall:function(func,kw){
        var kw = objectUpdate(objectUpdate({},this.attr),kw); 
        return funcApply(func,this.evaluateOnNode(kw),this);
    },
    
    evaluateOnNode: function(pardict) {
        // given an object representing dynamic parameters
        // get current values relative to this node
        // eg. values starting with ^. are datapath relative to the current node
        var result = {};
        for (var attr in pardict) {
            result[attr] = this.currentFromDatasource(pardict[attr]);
        }
        return result;
    },
    currentAttributes: function() {
        var attributes = {};
        for (var attr in this.attr) {
            attributes[attr] = this.getAttributeFromDatasource(attr);
        }
        return attributes;
    },
    rebuild: function() {
        this.setValue(this._value);
    },
    build: function(destination, ind) {
        genro.src.stripData(this);
        if(this.attr._attachPoint){
            var _attachPoint = this.attr._attachPoint.split('.');
            while (_attachPoint.length>0){
                destination = destination[_attachPoint.shift()];
            }
        }
        if (!this.attr.tag) {
            //console.warn('notag in build domsource',arguments.callee);
            this._buildChildren(destination);
            return;
        }
        var handler=genro.wdg.getHandler(this.attr.tag);
        if(handler && handler.onBuilding){
           handler.onBuilding(this);
        }
        if(this.attr.parentForm===false){
            this.form = null;
        }else{
            this._registerInForm();
        }
        this._isBuilding = true;
        var aux = '_bld_' + this.attr.tag.toLowerCase();
        if (aux in this) {
            this[aux].call(this);
        }else{
            var attributes = this.registerNodeDynAttr(true);
            var tag=objectPop(attributes,'tag')
            this._doBuildNode(tag, attributes, destination, ind);
            this._setDynAttributes();
        }
        this._isBuilding = false;
    },
    _buildChildren: function(destination) {
        if (this.attr.remote) {
            var that = this;
            this.watch('isVisibile',function(){return genro.dom.isVisible(that);},function(){that.updateRemoteContent();});
        }
        var content = this.getValue('static');
        if (content instanceof gnr.GnrDomSource) {
            content.forEach(function(node){
                node.build(destination, -1);
            },'static');
        }
    },
    _registerInForm:function(){
        var formHandler = this.getFormHandler();
        if(formHandler){
            this.form = formHandler;
            if(this.attr.parentForm!==false){
                formHandler.registerChild(this);
                genro.src.formsToUpdate[this.form.formId]=this.form;
            }
        }
    },
    _registerNodeId: function(nodeId) {
        var nodeId = this.attr.nodeId || nodeId;
        if (nodeId) {
            var reg_node = genro.src._index[nodeId];
            if(reg_node){
                genro.assert(reg_node===this,'duplicate nodeId:'+nodeId);

            }
            genro.src._index[nodeId] = this;
        }
    },
    _onDeleting:function(){
        if(this.form){
            this.form.unregisterChild(this);
        }
        if(this.watches){
            for(var w in this.watches){
                var interval = this.watches[w];
                if(interval){
                    clearInterval(interval);
                }
            }
        }
    
    },
    
    _doBuildNode: function(tag, attributes, destination, ind) {
        var bld_attrs = objectExtract(attributes, 'onCreating,onCreated,gnrId,tooltip,nodeId');
        var connections = objectExtract(attributes, 'connect_*');
        if (objectPop(attributes, 'autofocus')) {
            attributes.subscribe_onPageStart = "this.widget.focus()";
        }
        var subscriptions = objectExtract(attributes, 'subscribe_*');
        var selfsubscription = objectExtract(attributes, 'selfsubscribe_*');
        var formsubscription = objectExtract(attributes, 'formsubscribe_*');
        
        var attrname;
        var ind = ind || 0;
        if (bld_attrs.onCreating) {
            funcCreate(bld_attrs.onCreating).call(this, attributes);
        }
        var newobj = genro.wdg.create(tag, destination, attributes, ind, this);
        for (var selfsubscribe in selfsubscription){
            this.subscribe(selfsubscribe,selfsubscription[selfsubscribe]);
        }
        if(this.form){
            var topic_pref = 'form_'+this.form.formId+'_';
            for (var formsubscribe in formsubscription){
                subscriptions[topic_pref+formsubscribe] = formsubscription[formsubscribe];
            }
        }

        if (newobj === false) {
            this._buildChildren(destination);
            return;
        }
        if (bld_attrs.onCreated) {
            funcCreate(bld_attrs.onCreated, 'widget,attributes').call(this, newobj, attributes);
        }
        this._registerNodeId(bld_attrs.nodeId);
        if (bld_attrs.gnrId) {
            this.setGnrId(bld_attrs.gnrId, newobj);
        }

        for (var eventname in connections) {
            this.connect(newobj, eventname, connections[eventname]);
        }
        for (var subscription in subscriptions) {
            var handler = funcCreate(subscriptions[subscription]);
            this.registerSubscription(subscription, this, handler);
        }
        if (this.attr._lazyBuild){
            var that = this;
            var cbtest;
            cbtest= function(){
                return genro.dom.isVisible(that) || that._buildNow;
            }
            this.watch('lazyBuildWait',cbtest,
                    function(){
                        that.lazyBuildFinalize(newobj);
                    });
        }else{
            this._buildChildren(newobj);
        }
        if ('startup' in newobj) {
            newobj.startup();
        }
        if ((typeof(this.attr.value) == 'string') && (this.isPointerPath(this.attr.value))) {
            newobj.gnr.connectChangeEvent(newobj);
        }

        if (bld_attrs.tooltip) {
            genro.wdg.create('tooltip', null, {label:bld_attrs.tooltip,tooltip_type:'help'}).connectOneNode(newobj.domNode || newobj);
        }
        if (genro.src._started && this.widget && (this.widget instanceof dijit.form.ValidationTextBox)){
            var validations = objectExtract(this.attr, 'validate_*',true);
            if (this.validationsOnChange && objectNotEmpty(validations)){
                this.resetValidationError();
                var newval = this.validationsOnChange(this, attributes.value,true)['value'];
                this.updateValidationStatus();
            }
        }
        this._built = true;
        this.onNodeBuilt(newobj);
        return newobj;
    },

    buildNow:function(){
        this._buildNow=true;
    },
    
    onNodeBuilt:function(newobj){
        return;
    },
    
    delayedCall:function(cb,delay,code){
        var code = code || 'delayedCall';
        var handlerName = '_dc_'+code;
        var delay = delay || 1;
        if(this[handlerName]){
            clearTimeout(this[handlerName]);
        }
        this[handlerName] = setTimeout(cb,delay);
    },
    
    _resetDynAttributes : function() {
        if (this._dynattr) {
            delete this._dynattr;
        }
        var stringId = this.getStringId();
        var nodeSubscribers = genro.src._subscribedNodes[stringId];
        if (nodeSubscribers) {
            for (var attr in nodeSubscribers) {
                dojo.forEach(nodeSubscribers[attr],function(n){
                    dojo.unsubscribe(n);
                });
            }
            delete genro.src._subscribedNodes[stringId];
        }
    },
    registerSubscription:function(topic,scope,handler,reason){
        var stringId = this.getStringId();
        var reason = reason || topic;
        var subDict=genro.src._subscribedNodes[stringId];
        if(!subDict){
            subDict = {};
            genro.src._subscribedNodes[stringId] = subDict;
        }
        if(!(topic in subDict)){
            subDict[reason] = [];
        }
        subDict[reason].push(dojo.subscribe(topic, scope, handler));
    },
    unregisterSubscription:function(reason){
        var stringId = this.getStringId();
        var subDict=genro.src._subscribedNodes[stringId];
        if(reason in subDict){
            var l = objectPop(subDict,reason);
            if(l){
                dojo.forEach(l,function(s){dojo.unsubscribe(s)});
            }
        }
    },
    
    _setDynAttributes : function() {
        var stringId = this.getStringId();
        if (this._dynattr) {
            var nodeSubscribers = genro.src._subscribedNodes[stringId] || {};
            var path,fn,prop;
            for (var attr in this._dynattr) {
                nodeSubscribers[attr] = [this._subscriptionHandle(attr)];
            }
            genro.src._subscribedNodes[stringId] = nodeSubscribers;
        }
    },
    _subscriptionHandle:function(attr) {
        var prop = attr;
        return dojo.subscribe('_trigger_data', this, function(kw) {
            this.trigger_data(prop, kw);
        });
    },
    setGnrId:function(gnrId, obj) {
        var idLst = gnrId.split('.');
        var curr = genro;
        for (var i = 0; i < idLst.length - 1; i++) {
            var id = idLst[i];
            if (!curr[id]) {
                curr[id] = {};
            }
            ;
            curr = curr[id];
        }
        curr[idLst[idLst.length - 1]] = obj;
    },
    
    publish:function(msg,kw,recursive){
        var topic = (this.attr.nodeId || this.getStringId()) +'_'+msg;
        dojo.publish(topic,[kw]);
        if (recursive){
            var children =this.getValue('static');
            if (children instanceof gnr.GnrDomSource){
                children.walk(function(n){
                    if(!n._built){
                       return true;
                    }
                    n.publish(msg,kw);
                });
            }
        }
    },
    subscribe:function(command,handler,subscriberNode){
        var that=this;
        var h = handler;
        var handler = function(){
            var argNames = [];
            var argValues = [];
            for (var i=0; i < arguments.length; i++) {
                argValues.push(arguments[i]);
                argNames.push('p_'+i);
            };
            var currAttr = that.currentAttributes();
            funcApply(h, that.currentAttributes(),that,argNames,argValues);
        };
        var topic = (this.attr.nodeId || this.getStringId()) +'_'+command;
        subscriberNode = subscriberNode || this;
        subscriberNode.registerSubscription(topic,this,handler);
    },
    lazyBuildFinalize:function(widget){
        var lazyBuild = objectPop(this.attr,'_lazyBuild');
        var content = this.getValue();
        if (content instanceof gnr.GnrBag){
            var nodes = content._nodes;
            content._nodes = [];
            dojo.forEach(nodes,function(n){
                content.setItem(n.label,n);
            });
        }
        
        //if ('onLazyContentCreated' in widget) {
        //    widget.onLazyContentCreated();
        //}
        if(this.attr._onLazyBuilt){
            funcApply(this.attr._onLazyBuilt,null,this);
        }
    },

    getFrameNode:function(){
        if(this.attr.tag.toLowerCase()=='framepane'){
            return this;
        }
        var parent = this.getParentNode();
        if(parent){
            return parent.getFrameNode();
        }
    },
    
    getFormHandler:function(){
        if ('form' in this){
            return this.form;
        }        
        else if (this.attr.parentForm){
            if(typeof(this.attr.parentForm)=='string'){
                return genro.formById(this.attr.parentForm);
            }
        }
        
        var parent = this.getParentNode();
        if (parent) {
            return parent.getFormHandler();
        }else if (window.frameElement){
            var parentIframe = window.frameElement.sourceNode;
            if(parentIframe){
                return parentIframe.getFormHandler();
            }
        }
    },
    
   /* getParentForm:function(){
        var parentForm = this.sourceNode.getParentNode().form;
        if(!parentForm && window.frameElement){
            var parentIframe = window.frameElement.sourceNode;
            if(parentIframe){
                return parentIframe.form;
            }
        }
        return parentForm;
    },*/
    
    inheritedAttribute:function(attr){
        var node = this.attributeOwnerNode(attr);
        if(node){
            return node.getAttributeFromDatasource(attr);
        }
    },
    
    setHiderLayer:function(set,kw){
        if(!set){
            this.unwatch('isVisibile');
            this.getValue().popNode('hiderNode');
        }else if (!this.getValue().getNode('hiderNode')){
            var that = this;
            this.watch('isVisibile',
                        function(){return genro.dom.isVisible(that);},
                        function(){genro.dom.makeHiderLayer(that,kw);});
        }        
    },

    makeFloatingMessage:function(kw){
        kw = objectUpdate({},kw)
        var yRatio = objectPop(kw,'yRatio')
        var xRatio = objectPop(kw,'xRatio')
        var duration = objectPop(kw,'duration') || 2;
        var duration_in = objectPop(kw,'duration_in') || duration;
        var duration_out = objectPop(kw,'duration_out') || duration;

        var sound = objectPop(kw,'sound');
        var message = objectPop(kw,'message');

        var msgType = objectPop(kw,'messageType') || 'message';
        var transition = 'opacity '+duration_in+'s';
        var messageBox = this._('div','_floatingmess',{_class:'invisible fm_box fm_'+msgType,transition:transition}).getParentNode()
        kw.innerHTML = message;
        messageBox._('div',kw);
        var deleteCb = function(){that._value.popNode('_floatingmess')};
        messageBox._('div',{_class:'fm_closebtn',connect_onclick:deleteCb});
        genro.dom.centerOn(messageBox,this,xRatio,yRatio);
        var that = this;
        if(sound){
            genro.playSound(sound);
        }
        var t1 = setTimeout(function(){
                              genro.dom.removeClass(messageBox,'invisible');
                              setTimeout(function(){genro.dom.addClass(messageBox,'invisible')
                                    setTimeout(deleteCb,(duration_out*1000)+1)
                              },(duration_in*1000)+1);
                            },1)

    },
    
    updateAttrBuiltObj:function(attr, kw, trigger_reason) {
        var re= new RegExp('\\b'+attr+'\\b');
        var isInFormula = false;
        if(this._formulaAttributes){
            for(var formulaAttribute in this._formulaAttributes){
                if(this._formulaAttributes[formulaAttribute].match(re)){
                    this.doUpdateAttrBuiltObj(formulaAttribute,kw,trigger_reason);
                    isInFormula = true;
                }
            }
        }
        if (!isInFormula){
            this.doUpdateAttrBuiltObj(attr,kw,trigger_reason);
        }

    },
    doUpdateAttrBuiltObj:function(attr, kw, trigger_reason) {
        if(stringStartsWith(attr,'attr_')){
            var valuepath = this.attr.value || this.attr.src ||this.attr.innerHTML
            if(valuepath){
                var updattr = {};
                updattr[attr.slice(5)] = kw.value;
                genro.getDataNode(this.absDatapath(valuepath)).updAttributes(updattr);
            }
        }
        if(this._original_attributes){
            this.setAttr(this._original_attributes,true);
            this._original_attributes=null;
        }
        var autocreate = kw.reason =='autocreate';
        var attr = attr || 'value';
        var path;
        var value = null;
        var attr_lower = attr.toLowerCase();
        var valueNode = kw.node;
        if(trigger_reason=='container' && attr=='value' && kw.evt=='upd'){
            var vpath = this.attr['value'];
            if (this.isPointerPath(vpath)){
                var valueNode = genro._data.getNode(this.absDatapath(vpath),null,true);
                if (valueNode){
                    var wdg_prefix = vpath.indexOf('?')<0?'wdg_*':'wdg_'+vpath.split('?')[1]+'_*';
                    var wdg_modifiers = objectExtract(valueNode.attr,wdg_prefix);
                    if(objectNotEmpty(wdg_modifiers)){
                        this._original_attributes = objectUpdate({},this.attr);
                        this.updAttributes(wdg_modifiers,true);
                    }
                }
            }
        }
        if (!(kw.evt == 'ins' || kw.evt == 'del')) {
            value = this.getAttributeFromDatasource(attr, true);
        }
        //value = (value != null) ? value : '';
        if(attr_lower=='disabled'){
            return this.setDisabled(value);
        }
        if (attr == 'datapath') {
            var absDatapath = this.absDatapath();
            if (absDatapath) {
                genro.fireDataTrigger(absDatapath);
            }
        }
        else if (attr == 'zoomFactor') {
            if (this.setZoomFactor) {
                this.setZoomFactor(value);
            }
        }
        else if (this.externalWidget) {
            if ('gnr_' + attr in this.externalWidget) {
                this.externalWidget['gnr_' + attr](value, kw, trigger_reason);
            }
            return;
        }
        else if (attr == '_class') {
            var oldvalue = ('oldvalue' in kw) ? kw.oldvalue : kw.changedAttr ? kw.oldattr[kw.changedAttr] : null;

            var domnode;
            if (this.widget) {
                domnode = this.widget.domNode;
            }
            else {
                domnode = this.domNode;
            }
            if (oldvalue) {
                if (oldvalue instanceof gnr.GnrBag) {
                    var q = kw.pathlist.length;
                    var p = this.absDatapath(this.attr._class).split('.').slice(q - 1);
                    var old_class = oldvalue.getItem(p.join('.'));
                } else {
                    var old_class = oldvalue;
                }
                genro.dom.removeClass(domnode, old_class);
            }
            genro.dom.addClass(domnode, value);
        }
        else if (attr=='style'){
            genro.dom.style(this,value);
        }
        else if (attr=='placeholder'){
            (this.widget? this.widget.focusNode:this.domNode).setAttribute('placeholder',value || '');
        }
        else if (attr.indexOf('remote_') == 0) {
            this.updateRemoteContent(this);
        }
        else if (this.widget) {
            /* if(attr.indexOf('remote_')==0){
             this.updateRemoteContent(this);
             }*/
            if (attr.indexOf('__') == 0) {
                return;
            }
            else if (attr_lower == 'readonly') {
                this.widget.setAttribute(attr, value ? true : false);
            }
            else if ((attr == 'storepath') && (this.attr.storepath.indexOf('^') == 0)) {
                this.rebuild();
            }
            else if (attr.indexOf('validate_') == 0) {
                //this.validationsOnChange(this, this.getAttributeFromDatasource('value'));
                if ((trigger_reason == 'node') || (kw.reason=='resolver')){
                    this.resetValidationError();
                    var currval = this.getAttributeFromDatasource('value');
                    var newval = this.validationsOnChange(this, currval,true)['value'];
                    this.updateValidationStatus();
                    this.setAttributeInDatasource('value', newval);
                }
            }else if (attr.indexOf('condition_')==0){
                if('setCondition' in this.widget){
                    if ((trigger_reason == 'node') || (kw.reason=='resolver')){
                        this.widget.setCondition(value,kw);
                    }
                }
            }
            else {
                var setter = 'set' + stringCapitalize(attr);
                if (setter in this.widget) {
                    var trgevt = kw.evt;
                    if (attr != 'value') {
                        dojo.hitch(this.widget, setter)(value, kw);
                        return
                    }
                    var formHandler = this.getFormHandler();

                    this.resetValidationError();     // reset validationError when data from bag is set in widget
                    if(formHandler && trigger_reason=='container' && this.attr.default_value && formHandler.isNewRecord() && (value==null) ){
                        value = this.attr.default_value;
                    }
                    if ('_lastValueReported' in this.widget) {    // VERIFICARE DOJO 1.2
                        this.widget._lastValueReported = value; // see dijit.form._formWidget setValue
                    }                                           // force _lastValueReported to get onChange event
                    kw = false;
                    if (this.attr.unmodifiable) {
                        var parentAttr = this.getRelativeData('.?');
                        if ('_newrecord' in parentAttr) {
                            this.widget.setAttribute('readOnly', !parentAttr['_newrecord']);
                        }
                    }
                    if (this.attr['protected']) {
                        var parentAttr = this.getRelativeData('.?');
                        if ('_newrecord' in parentAttr) {
                            if(!parentAttr['_newrecord']){
                                this.widget.setAttribute('readOnly', true);
                                var wdg = this.widget;
                                dojo.connect(wdg.domNode,'ondblclick',function(e){
                                    wdg.setAttribute('readOnly',false);
                                });
                                dojo.connect(wdg,'onBlur',function(){
                                    wdg.setAttribute('readOnly',true);
                                });
                            }
                        }
                    }
                    this.widget.setValue(value,kw);
                    if (trgevt != 'del') {
                        if(this.hasValidations()){
                            var formHandler = this.getFormHandler();
                            if (formHandler && !autocreate) {
                                formHandler.validateFromDatasource(this, value, trigger_reason);
                            }
                        }
                        var valueAttr = valueNode?valueNode.attr:null;
                        var sourceNodeValueAttr = objectExtract(this.attr,'attr_*',true);
                        if(objectNotEmpty(sourceNodeValueAttr)){
                            objectUpdate(valueAttr,this.evaluateOnNode(sourceNodeValueAttr));
                        }
                        if(this.attr.format || this.attr.mask){
                            var valueToFormat = value;
                            if(this.widget.getDisplayedValue){
                                valueToFormat = this.widget.getDisplayedValue();
                                if(valueToFormat!=value){
                                    if(isNullOrBlank(valueToFormat) && isNullOrBlank(value)){
                                        delete valueAttr._displayedValue;
                                    }else{
                                        valueAttr['_displayedValue'] = valueToFormat;
                                    }
                                }
                            }
                            valueNode.updAttributes({_formattedValue:genro.formatter.asText(valueToFormat, this.currentAttributes())},this);
                        }

                    }
                } 
                else if (genro.dom.isStyleAttr(attr)) {
                    this.widget.domNode.setAttribute('style',objectAsStyle(genro.dom.getStyleDict(this.currentAttributes())));
                }
                
                
                else {
                    this.rebuild();
                }
            }
        }
        else if (this.domNode) {
            var domnode = this.domNode;
            var setter = 'set' + stringCapitalize(attr);
            if (setter in domnode.gnr) {
                dojo.hitch(domnode.gnr, setter)(domnode, value, kw);
            }
            else if (attr == 'visible') {
                dojo.style(domnode, 'visibility', (value ? 'visible' : 'hidden'));
                return;
            }
            else if (attr == 'hidden') {
                dojo.style(domnode, 'display', (value ? 'none' : ''));
                return;
            }
            else if (attr == 'value') {
                if ('value' in domnode) {
                    domnode.value = value;
                }
                else {
                    //genro.debug('unable to use datasource for node:'+this.getFullpath());
                }
            }
            else if (attr == 'innerHTML') {
                domnode.innerHTML = value;
            }
            else if ( ('template' in this.attr) && ( (attr == 'datasource') || attr.indexOf('tpl_')==0 )) {
                var ih = dataTemplate(this.getAttributeFromDatasource('template'), this, this.attr.datasource);
                if(this.isPointerPath(this.attr.innerHTML)){
                    this.setRelativeData(this.attr.innerHTML,ih);
                }else{
                    this.domNode.innerHTML = ih;
                }
            }
            else if (genro.dom.isStyleAttr(attr)) {
                domnode.setAttribute('style',objectAsStyle(genro.dom.getStyleDict(this.currentAttributes())));
            }
            else if (attr in domnode){
                domnode[attr] = value;
            }
            else {
                var attrdict = {};
                this.setAttr(attrdict, this, true);
                //this.setAttr({attr:value}, this, true);

                //domnode.setAttribute(attr,value);
            }
        }else if(this.gnrwdg){
            var setter = 'set' + stringCapitalize(attr);
            if(setter in this.gnrwdg){
                this.gnrwdg[setter].call(this.gnrwdg,value,kw,trigger_reason);
            }
        }
    },
    
    _dataControllerSubscription:function(subscriptions){
        for (var subscription in subscriptions) {
            var cb = function(node, trigger_reason) {
                    var reason = trigger_reason;
                    node.registerSubscription(subscription, node, function() {
                        node.setDataNodeValue(null, {}, reason, arguments);
                    });
                };
            cb(this, subscription);
        }
    },
    setTiming:function(timing) {
        if (this._timing) {
            clearInterval(this._timing);
        }
        if (timing > 0) {
            var timerFunc = dojo.hitch(this, 'setDataNodeValue');
            this._timing = setInterval(timerFunc, timing * 1000);
        }

    },
    updateRemoteContent:function(forceUpdate) {
        var _onRemote = false;
        var currentValue = this.getValue('static');
        if (currentValue && currentValue.len() > 0 && !forceUpdate) {
            return;
        }
        var remoteAttr = this.evaluateOnNode(objectExtract(this.attr,'remote_*',true));
        if(this._lastRemoteAttr && this.attr._cachedRemote && objectIsEqual(this._lastRemoteAttr,remoteAttr)){
            return;
        }
        this._lastRemoteAttr = remoteAttr;
        if(remoteAttr._if){
            var condition = funcApply('return (' + remoteAttr._if + ')',remoteAttr,this);
            if(!condition){
                if ('_else' in remoteAttr){
                    var elseval=remoteAttr._else;
                    if (elseval && typeof(elseval)=='string'){
                        elseval=funcCreate(elseval).call(this)
                    }
                    this.replaceContent(elseval)
                }
                return;
            }
        }
        var kwargs = {};
        for (var attrname in remoteAttr) {
            var value = remoteAttr[attrname];
            if (value instanceof Date) {
                var abspath = this.absDatapath(this.attr['remote_'+attrname]);
                var node = genro._data.getNode(abspath);
                value = asTypedTxt(value, node.attr.dtype);
            }
            ;
            if (attrname.indexOf('_') != 0) {
                kwargs[attrname] = value;
            } else if (attrname == '_onRemote') {
                _onRemote = funcCreate(value, attrname._onRemote, this);
            }
        }
        var method = this.attr.remote;
        var that = this;
        kwargs.sync = true;
        var currval;
        genro.rpc.remoteCall(method, kwargs, null, 'POST', null,
                            function(result) {
                                //that.setValue(result);
                                if(result.error){
                                    genro.dlg.alert('Error in remote '+result.error,'Error')
                                }else{
                                    that.replaceContent(result);
                                }
                                
                                if (_onRemote) {
                                    _onRemote();
                                }
                            });
    },
    getValidationError: function() {
        if (this._validations) {
            return this._validations.error;
        }
    },
    getValidationWarnings: function() {
        if (this._validations) {
            return this._validations.warnings;
        }
    },
    isValidationRequired: function() {
        if ((this._validations) && (this._validations.required)) {
            return true;
        }
    },
    hasValidationWarnings: function() {
        if ((this._validations) && (objectNotEmpty(this._validations.warnings))) {
            return true;
        }
    },
    hasValidationError: function() {
        if ((this._validations) && (this._validations.error)) {
            return true;
        }
    },
    resetValidationError: function() {
        if (this._validations) {
            this._validations.error = null;
            this._validations.warnings = [];
            this._validations.required = null;
            this.updateValidationClasses();
        }
    },
    setValidationError: function(validation_result) {
        this._validations.error = validation_result.error;
        this._validations.warnings = validation_result.warnings;
        this._validations.required = validation_result.required;
        this.updateValidationClasses();
    },

    setValidations: function() {
        this._validations = {};
    },

    hasValidations: function() {
        if (this._validations) {
            return true;
        }
    },
    getElementLabel:function(){
        return this.attr._valuelabel || this.attr.field_name_long || this.attr.name_long || stringCapitalize(this.label);
    },

    unwatch:function(watchId){
        if (this.watches && this.watches[watchId]){
            clearInterval(this.watches[watchId]);
            delete this.watches[watchId];
        }
    },
    
    watch: function(watchId,conditionCb,action,delay){
        var delay=delay || 200;
        if(this.watches && (watchId in this.watches)){
            this.unwatch(watchId);
        }
        if (conditionCb()){
            action();
        }else{
            this.watches=this.watches || {};
            var that = this;
            this.watches[watchId] = setInterval(
                function(){
                    if (conditionCb()){
                        that.unwatch(watchId);
                        action();
                    }
            },delay);
        }
    },
    
    updateValidationStatus: function(kw) {
        if (this.widget) {
            this.updateValidationClasses();
            this.widget.state = this.hasValidationError() ? 'Error' : null;
            this.widget._setStateClass();
            if(this.form){
                this.form.updateInvalidField(this, this.attrDatapath('value'));
            }
        }
    },

    updateValidationClasses: function() {
        if (this.widget.cellNode) {
            var domnode = this.widget.cellNode;
        } else {
            var domnode = this.widget.focusNode; //(this.widget.stateNode||this.widget.domNode);
        }
        if (this.isValidationRequired()) {
            genro.dom.addClass(domnode, 'gnrrequired');
        } else {
            genro.dom.removeClass(domnode, 'gnrrequired');
        }
    },

    setDisabled:function(value){
        var value = value ? true : false;
        if(this.widget){
            if (dijit.form._FormWidget.prototype.setDisabled == this.widget.setDisabled) {
                this.widget.setAttribute('disabled', value);
            } else if (this.widget.setDisabled) {
                this.widget.setDisabled(value);
            }
        }else if(this.externalWidget){
            this.externalWidget.gnr_setDisabled(value);
        }
        else if(this.domNode){
            this.domNode.disabled = value;
            if(value){
                this.domNode.setAttribute('disabled',value);
            }else{
                this.domNode.removeAttribute('disabled');
            }
            
        }
    },

    setSource: function(path, /*gnr.GnrDomSource*/ source) {
        var content = this.getValue();
        var child;
        if (!content) {
            content = new gnr.GnrDomSource();
            this.setValue(content, false);
        } else {
            if (!(content instanceof gnr.GnrDomSource)) {
                this.setValue(content, false);
            }
        }
        child = content.setItem(path, source.getNodes()[0]);
        return child;
    },
    replaceContent:function(value){
        var currval = this._value;
        if(currval instanceof gnr.GnrDomSource){
            dojo.forEach(currval._nodes,function(n){
                currval.popNode(n.label);
            });
        }else{
            currval = new gnr.GnrDomSource();
            this._value = currval;
            currval.setBackRef(this, this._parentbag);
        }
        if(value){
                dojo.forEach(value._nodes,function(n){
                var node = value.popNode(n.label);
                currval.setItem(node.label,node);
            });
        }
        
    },
    
    _ : function(tag, name, attributes, extrakw) {
        var content = this.getValue();
        var child;
        if (!(content instanceof gnr.GnrDomSource)) {
            content = new gnr.GnrDomSource();
            this.setValue(content, false);
        }
        child = content._(tag, name, attributes, extrakw);
        return child;
    },
    _destroy: function() {
        return this.getParentBag().popNode(this.label);
    },
    getChild:function(childpath){
        var v = this._value;
        if(!v || !(v.getChild)){
             var clist = childpath.split('/')
             if(clist[0]=='parent'){
                 var node = this.getParentNode().getParentNode();
                 v = node.getValue();
             }
        }
        return v.getChild(childpath);
    }

});

dojo.declare("gnr.GnrStructData", gnr.GnrBag, {
    // constructor: function(source){
    //     this._validationPrefix = 'structvalidate_';
    // }
});

dojo.declare("gnr.GnrDomSource", gnr.GnrStructData, {
    _validationPrefix: 'structvalidate_',
    _nodeFactory:gnr.GnrDomSourceNode,

    _ : function(tag, name/*optional*/, attributes/*Object*/, extrakw) {
        var tag_UpperLower = null;
        var content;
        tag = tag.toLowerCase();
        if (tag) {
            if (name instanceof Object) {
                var extrakw = attributes || {};
                var attributes = name || {};
                var name = '';
                if('childname' in attributes){
                    name = name || objectPop(attributes,'childname');
                }
            }
            var attributes = attributes || {};
            tag = objectPop(attributes,'tag')|| tag;
            if (attributes && ('remote' in attributes) && (attributes.remote!='remoteBuilder')) {
                if (typeof(attributes.remote)=="string"){
                attributes['remote_handler'] = attributes.remote;
                }
                else if (attributes.remote instanceof Object){
                    attributes['remote_handler'] = objectPop(attributes.remote, 'method');
                    for (var prop in attributes.remote){
                        attributes['remote_'+prop]=attributes.remote[prop];
                    };
                }
                attributes.remote = 'remoteBuilder';
            }
            name = name || '*_?';
            name = name.replace('*', tag).replace('?', this.len());
            if (attributes.content) {
                content = attributes.content;
                delete attributes.content;
            }
            if (content == null) {
                content = new gnr.GnrDomSource();
            }
            attributes.tag = tag;
            var handler=genro.wdg.getHandler(tag);
            if(handler && handler.onStructChild){
                handler.onStructChild(attributes,this);
            }
            this.setItem(name, content, attributes, extrakw);
            return content;
        }

    },

    component: function() {
        if (this.component != null) {
            return this._component;
        } else if (this.parent != null) {
            return this.parent.component();
        }
    },
    getChild:function(childpath){
        childpath = childpath.split('/');
        var curr = this;
        var node;
        dojo.forEach(childpath,function(childname){
            if (childname=='parent'){
                node=curr.getParentNode().getParentNode();
                curr=node.getValue();
            }else if(childname.indexOf('#')==0){
                node=curr.getParentNode();
                node=node.nodeById(childname.slice(1));
                curr=node.getValue();
            }
            else{

                curr.forEach(function(n){
                    if(n.attr._childname==childname){
                        node = n;
                    }
                },'static');
                
                if(node){
                    return 
                }
                node=curr.walk(function(n){
                       if('_childname' in n.attr){
                           return n.attr._childname==childname?n:true;
                         }
                      },'static');

                if (node==true){
                    return;
                }else{
                    curr=node.getValue();
                    if(!(curr instanceof gnr.GnrBag)){
                        return;
                    }
                }
            }
            
        });
        return node===true?null:node;
    }
});



