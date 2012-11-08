/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_src : Genro clientside Source Bag handler
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

dojo.declare("gnr.GnrSrcHandler", null, {

    constructor: function(application) {
        this.application = application;
        //this.builder = new gnr.GnrDomBuilder(this);
        this._main = new gnr.GnrDomSource();
        this._main.application = this.application;
        this._main.setBackRef();
        this._main.subscribe('sourceTriggers', {'any':dojo.hitch(this, "nodeTrigger")});
        this._subscribedNodes = {};
        this._started=false;
        this._index = {};
        this.pendingBuild = [];
        this.afterBuildCalls = [];
        this.building = false;
        this.datatags = {'data':null,'dataformula':null,'datascript':null,
            'datarpc':null,'dataremote':null,'datacontroller':null};
        this.highlightedNode = null;

    },
    highlightNode:function(sourceNode) {
        if (typeof(sourceNode) == 'string') {
            sourceNode = this.sourceRoot.getValue().getNode(sourceNode);
        }
        ;
        if (this.highlightedNode) {
            domnode = this.highlightedNode.getDomNode();
            if (domnode) {
                genro.dom.removeClass(domnode, 'gnrhighlight');
            }
        }
        this.highlightedNode = sourceNode;
        if (sourceNode) {
            domnode = this.highlightedNode.getDomNode();
            if (domnode) {
                genro.dom.addClass(domnode, 'gnrhighlight');
            }
        }
    },
    onBuiltCall:function(cb,delay){
        this.afterBuildCalls.push(delay? function(){setTimeout(cb,1);}:cb);
    },
    
    nodeTrigger:function(kw) {
        if (kw.node.isFreezed() || kw.node._isBuilding){
            return;
        }
        this.pendingBuild.push(kw);
        if (!this.building) {
            this.building = true;
            while (this.pendingBuild.length > 0) {
                var kw = this.pendingBuild.pop();
                dojo.hitch(this, '_trigger_' + kw.evt)(kw);
            }
            this.building = false;
        }
    },
    _trigger_ins:function(kw) {//da rivedere
        //console.log('trigger_ins',kw);
        if(kw.reason=='autocreate'){
            return;
        }
        var node = kw.node;
        var where = objectPop(node.attr, '_parentDomNode');
        if (!where) {
            var wherenode = kw.where.getParentNode();
            if (wherenode) {
                var where = wherenode.widget || wherenode.domNode;
                if (!where) {
                    alert('_trigger_ins error????');//|| dojo.byId(genro.domRootName);
                }
            } else {
                var where = dojo.byId(genro.domRootName);
                node.domNode = where;
            }
        }

        var ind = kw.ind;
        this.buildNode(node, where, ind);
        if(where.onChangedContent){
            where.onChangedContent(node);
        }
        else if(where._checkIfSingleChild){
            where._checkIfSingleChild();
            where.resize();
        }
    },
    
    _trigger_upd:function(kw) {//da rivedere
        //console.log('trigger_upd',kw);
        var destination = kw.node.getParentBuiltObj();
        if (!destination) {
            console.log('missing destination in rebuild');
        }
        this._onDeletingContent(kw.oldvalue);
        var domNode = kw.node.getDomNode();//get the domnode
        var newNode = document.createElement('div');
        var widget = kw.node.widget;
        var ind = -1;
        var selectedIndex = null;
        if (widget) {
            if (widget.sizeShare) {
                kw.node.attr.sizeShare = widget.sizeShare;
            }
            if (destination.getChildren) {
                var children = destination.getChildren();
                ind = children.indexOf(widget);
                if (destination.getSelectedIndex) {
                    var selectedIndex = destination.getSelectedIndex();
                }
                if ('removeChild' in destination) {
                    destination.removeChild(widget);
                }
                widget.destroyRecursive();
            } else if(destination._singleChild){
                destination.destroyDescendants();
                
            }
            else {
                if (domNode.parentNode) {
                    domNode.parentNode.replaceChild(newNode, domNode);
                }
                widget.destroyRecursive();
            }
        } else {
            if (domNode.parentNode) {
                domNode.parentNode.replaceChild(newNode, domNode);
                ind = newNode;
            }

            var widgets = dojo.query('[widgetId]', domNode);
            while (widgets.length > 0) {
                widgets = widgets.map(dijit.byNode);
                widgets[0].destroyRecursive();
                widgets = dojo.query('[widgetId]', domNode);
            }
            // Array
            //dojo.forEach(widgets, function(widget){ widget.destroyRecursive(); });
            while (domNode.childNodes.length > 0) {
                dojo._destroyElement(domNode.childNodes[0]);
            }
        }
        this.refreshSourceIndexAndSubscribers();
        if(!kw.node._value){
            return;
        }
        this.buildNode(kw.node, destination, ind);
        if(destination._checkIfSingleChild){
            destination._checkIfSingleChild();
        }
        if (selectedIndex) {
            destination.setSelected(selectedIndex);
        }
    },
    
    _onDeletingContent:function(oldvalue){
        if(oldvalue instanceof gnr.GnrBag){
            oldvalue.walk(function(n){
               if(n._onDeleting){
                   n._onDeleting();
               }
            },'static');
        }
    },
    
    _trigger_del:function(kw) {//da rivedere
        //console.log('trigger_del',kw);
        var deletingNode = kw.node;
        deletingNode = deletingNode._isComponentNode?(deletingNode.getWidget()?deletingNode.getWidget().sourceNode:deletingNode):deletingNode;
        deletingNode._onDeleting();
        this._onDeletingContent(deletingNode._value);
        //var domNode = kw.node.getDomNode();
        //if (!domNode) {
        //    return;
        //}

        var widget = deletingNode.widget;
        var domNode = deletingNode.domNode;
        if (widget) {
            var parentWdg = widget.getParent?widget.getParent():null;
            if(parentWdg && parentWdg.onDestroyingChild){
                parentWdg.onDestroyingChild(widget);
            }
            widget.destroyRecursive();
        } else if(domNode) {
            var widgets = dojo.query('[widgetId]', domNode);
            widgets = widgets.map(dijit.byNode);     // Array
            dojo.forEach(widgets, function(widget) {
                widget.destroyRecursive();
            });
            dojo._destroyElement(domNode);
        }
        var parentNode = deletingNode.getParentNode();
        var lastComponentLabel;
        while(parentNode && parentNode._isComponentNode){
            lastComponentLabel = parentNode.label;
            parentNode = parentNode.getParentNode();
         }
         if (parentNode && lastComponentLabel){
             parentNode.getValue().popNode(lastComponentLabel);
         }
        this.refreshSourceIndexAndSubscribers();
    },
    
    
    buildNode: function(sourceNode, where, ind) {
        this.formsToUpdate={};
        this.afterBuildCalls = [];
        sourceNode.build(where, ind);
        var cb;
        while (this.afterBuildCalls.length > 0) {
            cb = this.afterBuildCalls.pop();
            cb.call();
        }
        if(genro._pageStarted){
            for (var formId in this.formsToUpdate){
                var form = this.formsToUpdate[formId];
                form.applyDisabledStatus();
            } 
        }

    },



    getSource:function(path) {
        if (path) {
            return this._main.getItem('main.' + path);
        }
        else {
            return  this._main.getItem('main');
        }


    },

    getNode:function(obj,autocreate) {
        var autocreate = autocreate===false?false:true;
        if (!obj) {
            return this._main.getNode('main');
        }
        if (typeof (obj) == 'string') {
            if (obj.indexOf('main.') != 0) {
                obj = 'main.' + obj;
            }
            return this._main.getNode(obj, false, autocreate);
        }
        if (obj.declaredClass == 'gnr.GnrDomSourceNode') {
            return obj;
        }
        if (obj.sourceNode) {
            return obj.sourceNode;
        }
        if (obj.target) {
            return obj.target.sourceNode || dijit.getEnclosingWidget(obj.target).sourceNode;
        }
    },

    nodeBySourceNodeId:function(identifier) {
        return this._main.findNodeById(identifier);
    },
    newRoot:function() {
        return new gnr.GnrDomSource();
    },
    setSource:function(path, value, attributes, kw) {
        if (!attributes && (value instanceof gnr.GnrDomSource)) {
            value = value.getNodes()[0];
        }
        this._main.setItem('main.' + path, value, attributes, kw);
    },
    delSource:function(path) {
        this._main.delItem('main.' + path);
    },

    startUp:function(source) {//nome troppo generico?
      
        this._main.setItem('main', source);
        this.sourceRoot = source;
        this._started=true;

    },
    setInRootContainer:function(label, item) {
        alert('removed : setInRootContainer in genro_src');
    },
    enclosingSourceNode:function(item) {
        if (item.sourceNode) {
            return item.sourceNode;
        }
        if (item.widget) {
            var widget = item.widget;
        } else {
            var widget = dijit.getEnclosingWidget(item);
        }
        if (widget) {
            if (widget.sourceNode) {
                return widget.sourceNode;
            } else {
                return genro.src.enclosingSourceNode(widget.domNode.parentNode);
            }
        }
    },
    onEventCall:function(e, code, kw) {
        var sourceNode = genro.src.enclosingSourceNode(e.target);
        var func = funcCreate(code, 'kw,e', sourceNode);
        func(kw, e);
    },
    checkSubscribedNodes:function(){
        var subscribedNodes = this._subscribedNodes;
        for (var strid in subscribedNodes){
            var srcnode = genro.src._main.findNodeById(strid.slice(2));
            console.log(strid,srcnode,srcnode.getParentNode())
          //for (var attr in subscribedNodes[strid]) {
          //         dojo.forEach(subscribedNodes[strid][attr],function(n){
          //             console.log(n);
          //         });
          //     }
        }
        return 'finito'
    },
    refreshSourceIndexAndSubscribers:function() {
        var oldSubscribedNodes = this._subscribedNodes;
        var oldIndex = this._index;
        this._index = {};
        this._subscribedNodes = {};
        var refresher = dojo.hitch(this, function(n) {
           //if(n.attr._lazyBuild){
           //    return true;
           //}
            var id = n.getStringId();
            var oldSubscriber = oldSubscribedNodes[id];
            if (oldSubscriber) {
                genro.src._subscribedNodes[id] = oldSubscriber;
                oldSubscribedNodes[id] = null;
            }
            if (n.attr.nodeId) {
                if (!(n.attr.nodeId in oldIndex)){
                    //console.log('ignorato',n.attr.nodeId);
                    return;
                }
                genro.src._index[n.attr.nodeId] = n;
            }
        });
        this._main.walk(refresher, 'static');
        for (var subscriber in oldSubscribedNodes) {
            if (oldSubscribedNodes[subscriber]) {
                for (var attr in oldSubscribedNodes[subscriber]) {
                    dojo.forEach(oldSubscribedNodes[subscriber][attr],function(n){
                        dojo.unsubscribe(n);
                    });
                }

            }
        }
    },
    stripData: function(node) {
        this.stripDataNode(node);
        var content = node.getValue('static');
        if (content instanceof gnr.GnrDomSource) {
            content.forEach(function(node){genro.src.stripDataNode(node);},'static');
        }
    },
    stripDataNode:function(node){
        if (node.attr.tag && !node._alreadyStripped) {
            if (node.attr.tag.toLowerCase() in genro.src.datatags) {
                this.moveData(node);
            }
            else {
                var nodeattr = node.attr;
                var attrvalue;
                var specialattr={}
                for (var attr in nodeattr) {
                    attrvalue = nodeattr[attr];
                    if ((typeof (attrvalue) == 'string') && node.isPointerPath(attrvalue)) {
                        var dflt = (attr == 'value') ? (nodeattr['default'] || nodeattr['default_value'] || '') : nodeattr['default_' + attr];
                        if(dflt && node.attr.dtype){
                            dflt = convertFromText(dflt,node.attr.dtype);
                        }
                        node.getAttributeFromDatasource(attr, true, dflt);
                    }
                    if(attr.indexOf('attr_')==0){
                        specialattr[attr.slice(5)] = attrvalue;
                    }
                }
                if(objectNotEmpty(specialattr) ){
                    var valuepath = nodeattr['value'] || nodeattr['src'] || nodeattr['innerHTML'];
                    if(valuepath){
                        var valueNode = genro.getDataNode(node.absDatapath(valuepath));
                        if(valueNode){
                            valueNode.updAttributes(node.evaluateOnNode(specialattr));
                        }
                    }
                }                
            }
        }
        node._alreadyStripped=true;
    },
    moveData: function(node) {
        node._registerNodeId();
        var attributes = node.registerNodeDynAttr(false);
        var tag = objectPop(attributes, 'tag');
        var path = objectPop(attributes, 'path');
        if (tag == 'data' && attributes.remote) {
            attributes['method'] = objectPop(attributes, 'remote');
            tag = 'dataRemote';
        }
        if (tag == 'data') {
            path = node.absDatapath(path);
            var value = node.getValue('static');
            node._value = null;
            if (value instanceof gnr.GnrBag) {
                value.clearBackRef();
            }
            var serverpath = objectPop(attributes, 'serverpath');
            if (serverpath) {
                genro._serverstore_paths[node.absDatapath(path)] = serverpath;
            }
            if(!genro.getDataNode(path)||(value!==null)){
                genro.setData(path, value, attributes);
            }
        } else if (tag == 'dataRemote') {
            node._dataprovider = tag;
            node.setDataNodeValue();
        } else {         
            var initialize = objectPop(attributes, '_init');
            node._dataprovider = tag;
            if (initialize) {
                node.setDataNodeValue();
            } else {
                path = node.absDatapath(path);
                genro.getDataNode(path, true);
            }
            var timing = objectPop(attributes, '_timing');

            if (timing) {
                node.setTiming(timing);
            }
            var onStart = objectPop(attributes, '_onStart');
            var onBuilt = objectPop(attributes, '_onBuilt');
            var subscriptions = objectExtract(attributes, 'subscribe_*');
            var selfsubscriptions = objectExtract(attributes, 'selfsubscribe_*');
            var formsubscriptions = objectExtract(attributes, 'formsubscribe_*');
            var nid = node.attr.nodeId || node.getStringId();
            for (var selfsubcription in selfsubscriptions){
                subscriptions[nid+'_'+selfsubcription] = selfsubscriptions[selfsubcription];
            }
            if(objectNotEmpty(formsubscriptions) || node.attr.parentForm){
                var cb = function(){
                    var form = node.getFormHandler();
                    if(form){
                        node.form = form;
                        var fid = form.formId;
                        var subscriptions = {};
                        for (var formsubcription in formsubscriptions){
                            subscriptions['form_'+fid+'_'+formsubcription] = formsubscriptions[formsubcription];
                        }
                        node._dataControllerSubscription(subscriptions);
                    }
                };
                genro.src.afterBuildCalls.push(cb);
            }
            
            node._dataControllerSubscription(subscriptions);
            
            if (onStart) {
                node.attr._fired_onStart = '^gnr.onStart';
                node.registerDynAttr('_fired_onStart');
                if (typeof(onStart) == "number" && !node.attr._delay) {
                    node.attr._delay = onStart;
                }
            }
            if(onBuilt){
                this.onBuiltCall(function(){
                    node.setDataNodeValue();
                })
            }
        }
        node._setDynAttributes();
    },
    
    dynamicParameters: function(source, sourceNode) {
        var obj = {};
        var path;
        if ((source != '') & (typeof source == 'string')) {
            source = genro.evaluate(source);
        }
        if (source) {
            sourceNode = sourceNode || objectPop(source,'_sourceNode');
            var formulaProp = [];
            for (var prop in source) {
                var val = source[prop];
                if (typeof(val) == 'string') {
                    var dynval = stringStrip(val);
                    if (dynval.indexOf('==') == 0) {
                        formulaProp.push(prop);
                        //val = funcApply("return "+dynval.slice(2),source,sourceNode);
                    } else if ((dynval.indexOf('^') == 0) || (dynval.indexOf('=') == 0)) {
                        path = dynval.slice(1);
                        if (sourceNode) {
                            path = sourceNode.absDatapath(path);
                        } else {
                            if (path.indexOf('.') == 0) {
                                throw "Unresolved relative path in dynamicParameters: " + path;
                            }
                        }
                        val = genro._data.getItem(path);
                    }
                } else if (typeof(val) == 'function') {
                    val = val();
                }
                obj[prop] = val;
            }
            if(formulaProp.length>0){
                dojo.forEach(formulaProp,function(prop){
                    obj[prop] = funcApply("return "+stringStrip(source[prop]).slice(2),obj,sourceNode);
                });
            }
        }
        return obj;
    },
    create: function(widget,pars,path) {
       //var path = path || '_temp.'+this.getNode()._id;
       //var source = genro.src.getNode(path).getParentBag();
       //source.delItem('#0');
       
       //var root = genro.src.newRoot();
       return genro.src.getNode()._('div', path)._(widget,path,pars);;
       //var node = genro.src.getNode(path).clearValue();
       //return node._(widget,path,pars);        
    }

});