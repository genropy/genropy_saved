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
dojo.declare("gnr.GnrDomSourceNode",gnr.GnrBagNode,{
    application:function(){
        return this.getParentBag().getRoot().application; 
    },
    freeze:function(){
        this._savedparentbag=this._parentbag;
        this._parentbag=null;
        if (this._value instanceof gnr.GnrDomSource){
            this._value.clearBackRef();
        }
        return this;
    },
    unfreeze:function(){
        this._parentbag=this._savedparentbag;
        if (this._value instanceof gnr.GnrDomSource){
            this._value.setBackRef(this,this._parentbag);
            this.rebuild();
        }
    },
    getBuiltObj:function(){
        return this.widget || this.domNode;
    },
    getParentBuiltObj:function(){
        var parentNode=this.getParentNode();
        if (parentNode){
            return parentNode.getBuiltObj();
        }
    },
    getDomNode:function(){
        if(this.domNode){
            return  this.domNode;
        }
        if(this.widget){
            return  this.widget.domNode;
        }
        
    },
    getParentDomNode:function(){
        var parentNode=this.getParentNode();
        if (parentNode){
            return parentNode.getDomNode();
        }
     },
    getWidget:function(){
        return  this.widget || dijit.getEnclosingWidget(this.domNode);
    },
    getParentWidget:function(){
        var parentNode=this.getParentNode();
        if (parentNode){
                return parentNode.getWidget();
        }
    },
    destroy:function(){
        if(this.widget){ /* this is a widget*/
            this.widget.destroyRecursive();
        }
        else if (this.domNode){
            var widgets = dojo.query('[widgetId]', this.domNode);
            widgets= widgets.map(dijit.byNode);     // Array
            dojo.forEach(widgets, function(widget){ widget.destroy(); });
            while (this.domNode.childNodes.length > 0){
                dojo._destroyElement(node.childNodes[0]);
            }
        }
    },
    
    trigger_data:function(prop, kw){
        var dpath=kw.pathlist.slice(1).join('.');
        var mydpath = this.attrDatapath(prop);
        if(mydpath==null){
            return;
        }
        if(mydpath.indexOf('#parent') >0){
            mydpath = gnr.bagRealPath(mydpath);
        }
        if (mydpath.indexOf('?')>=0){
            if( (kw.updattr)||(mydpath.indexOf('?=')>=0)){
               mydpath = mydpath.split('?')[0];
           }
       }
        
        var trigger_reason=null;
        var eqpath=(mydpath==dpath);
        if (eqpath){
            trigger_reason ='node';
        }
        var changed_container=(mydpath.indexOf(dpath+'.')==0);
        if (changed_container){
            trigger_reason = 'container';
        }
        var changed_child=(dpath.indexOf(mydpath+'.')==0);
        if (changed_child){
            trigger_reason = 'child';
        }
        if(trigger_reason){
        //if((mydpath==dpath)|| (mydpath.indexOf(dpath+'.')==0)  ||(dpath.indexOf(mydpath+'.')==0)){
            //genro.debug(kw.evt+' data node at path:'+dpath+' ('+prop+') - updating sourceNode:'+mydpath,null,'trigger_data');
            if((kw.evt == 'fired') && (trigger_reason == 'child')){
                // pass fired event on child datapath: get only parent changes for variable datapaths
            } else if (kw.evt=='invalid'){
                if(this.widget){
                    this.widget.focus();
                }
            } else if (this._dataprovider && (kw.evt!='del')){ //VERIFICARE perché escusi gli eventi DEL
                if (this.attr._delay>0){
                    setTimeout(dojo.hitch(this,'setDataNodeValue',kw.node,kw,trigger_reason),this.attr._delay);
                   
                }else{
                    //console.log('136 '+mydpath+'   -   '+dpath);
                    this.setDataNodeValue(kw.node,kw,trigger_reason);
                }
                
            }
            else{
                if (kw.reason != this){
                    //console.log('143 '+mydpath+'   -   '+dpath);
                    this.updateAttrBuiltObj(prop,kw, trigger_reason);
                }
            }
        }
    },
    fireNode: function(){
        this.setDataNodeValue();
    },
    setDataNodeValue:function(node, kw, trigger_reason){
        var attributes=objectUpdate({}, this.attr);
        var _userChanges=objectPop(attributes,'_userChanges');
        if ((kw && kw.reason == 'autocreate' )||( _userChanges && trigger_reason!='node')){
            return;
        }
        var tag=objectPop(attributes,'tag');
        var path=objectPop(attributes,'path');
        objectPop(attributes,'_onStart');
        objectPop(attributes,'_fired_onStart');

        var destinationPath, dataNode;
        if (path){ // if it has a result path set it to the returned value
            destinationPath = this.absDatapath(path);
            dataNode=genro.getDataNode(destinationPath,true);
        }
        objectPop(attributes,'_init');
        objectPop(attributes,'_delay');
        var _if=objectPop(attributes,'_if');
        var _else=objectPop(attributes,'_else');
        var expr;
        if(tag=='dataFormula'){
            expr=objectPop(attributes,'formula');
        }else if ((tag=='dataController') || (tag=='dataScript')){
            expr=objectPop(attributes,'script');
        }else {
            expr=objectPop(attributes,'method');
        }
        var argValues=[node, {'kw':kw, 'trigger_reason':trigger_reason}];
        var argNames=['_node', '_triggerpars']; //_node is also in _triggerpars.kw.node: todo remove (could be used as $1)
        var kwargs={};
        var val;
        for (var attrname in attributes){
            argNames.push(attrname);
            val= this.getAttributeFromDatasource(attrname);
            argValues.push(val);
            kwargs[attrname]=val;
        }
        var if_result=true;
        if(_if){
            if_result = funcCreate('return (' + _if +')', argNames.join(',')).apply(this,argValues);
        }
        if(tag=='dataFormula' || tag=='dataScript' || tag=='dataController' || tag=='dataRpc'){
            var val;
            if(! if_result){
                if(!_else){
                    return;
                }
                expr=_else;
            }
            if(tag=='dataRpc' && (expr != _else)){
                 var doCall = true;
                 var method=expr;
                 var httpMethod = objectPop(kwargs,'_POST')? 'POST' :'GET';
                 var _onResult = objectPop(kwargs,'_onResult');
                 objectPop(kwargs,'nodeId');
                 var _onCalling = objectPop(kwargs,'_onCalling');
                 var origKwargs = objectUpdate({},kwargs);
                 objectExtract(kwargs,'_*');
                 if (_onResult){
                    //_onResult = dojo.hitch(this, funcCreate(_onResult));
                    _onResult = funcCreate(_onResult,'result,kwargs',this);

                 }
                 var cb = function(result){   dataNode.setValue(result);
                                              if(_onResult){
                                                    _onResult(result,origKwargs);
                                              }
                                        };
                
                 if (_onCalling){
                     doCall = funcCreate(_onCalling, (['kwargs'].concat(argNames)).join(',')).apply(this, ([kwargs].concat(argValues)));
                 }
                if(doCall != false){
                    genro.rpc.remoteCall(method, kwargs, null, httpMethod, null, cb);
                }
            }
            else{
                var result;
                if(!expr){
                    result = new gnr.GnrBag(kwargs);
                } else {
                    expr = (tag=='dataFormula') ? 'return '+ expr : expr;
                    result = funcCreate(expr,argNames.join(',')).apply(this,argValues);
                }
                if (dataNode){ // if it has a dataNode set it to the returned value
                    dataNode.setValue(result);
                }
            } 
        }
        else{
            if( if_result){
                var method=expr;
                var cacheTime=objectPop(attributes,'cacheTime', -1);
                var isGetter=objectPop(attributes,'isGetter', false);
                attributes.sync = ('sync' in attributes) ? attributes.sync: true;
                attributes['_sourceNode']=this;
                var resolver = genro.rpc.remoteResolver(method, attributes, {'cacheTime':cacheTime,
                                                        'isGetter':isGetter});
                dataNode.setValue(resolver,true,attributes);
            }
        }
    },
    setAttributeInDatasource: function(attrname,value,doTrigger,attributes,forceChanges){
        var doTrigger=(doTrigger==false) ? doTrigger : this; 
        var path=this.attrDatapath(attrname);
        /*if (forceChanges){
               genro._data.setItem(path,null,null,{'doTrigger':false});
        }*/
        if (forceChanges || (genro._data.getItem(path)!=value)){
            genro._data.setItem(path,value,attributes,{'doTrigger':doTrigger});
        }
    },
    defineForm: function(form_id,formDatapath,controllerNodeId){
        this.formHandler = new gnr.GnrFrmHandler(form_id,formDatapath,controllerNodeId);
    },
    hasDynamicAttr: function(attr){
        return (this._dynattr && (attr in this._dynattr));
    },
    getRelativeData: function(path,autocreate,dflt){
         var path=this.absDatapath(path);
         var value;
         if (path!=null){
             if(autocreate){
                 var node=genro._data.getNode(path,false,autocreate,dflt);
                 if(path.indexOf('?')>=0){
                     value=genro._data.getItem(path);
                 }else if(node){
                     value=node.getValue(null, {'_sourceNode':this});
                 }
             }else{
                 if(path.indexOf('?')>=0){
                     value=genro._data.getItem(path);
                 }else{
                     var node=genro._data.getNode(path);
                      if(node){
                          value=node.getValue(null, {'_sourceNode':this});
                      }
                 }
             
             }
        }
        return value;
    },
    setRelativeData: function(path, value, attributes, fired, reason,delay){
       // var reason=reason || this
        if (delay){
            setTimeout(dojo.hitch(this,'setRelativeData',path,value, attributes, fired, reason),delay);
        }else{
            var reason = reason==null ? true : reason;
            var oldpath=path;
            var path=this.absDatapath(path);
            if (fired){
                genro._firingNode = this;
                genro._data.setItem(path, value, attributes, {'doTrigger':reason});
                genro._data.setItem(path, null, attributes, {'doTrigger':false});
                genro._firingNode = null;
            } else {
                if(genro._data.getItem(path)!=value){
                    genro._data.setItem(path,value,attributes,{'doTrigger':reason});
                }
            }
        }
    },
    getAttributeFromDatasource: function(attrname,autocreate,dflt){
        var attrname = attrname || 'value';
        var value = this.attr[attrname];
        value = this.currentFromDatasource(value, autocreate, dflt);
        if (((attrname=='value') || (attrname=='innerHTML'))  && (this.attr.mask || this.attr.format)){
            value = asText(value, this.attr);
        }
        return value;
    },
    currentFromDatasource: function(value, autocreate, dflt){
        var path;
        if(typeof(value)=='string'){
            if (this.isPointerPath(value)){
                if (value.indexOf('==')==0){
                    var argNames = [];
                    var argValues = [];
                    for (var attr in this.attr){
                        var attrval = this.attr[attr];
                        if ((typeof(attrval)!='string') || (attrval.indexOf('==')!=0)){ // if it is not a formula: for avoid infinite loop
                            argNames.push(attr);
                            argValues.push(this.getAttributeFromDatasource(attr));
                        }
                    }
                    value = funcCreate('return ' + value.slice(2), argNames.join(',')).apply(this, argValues);
                } else {
                    value=this.getRelativeData(value,autocreate,dflt);
                }
            }
            //else if (value.indexOf('=')==0){    rimosso in favore di dataScript
            //    value = (new Function ('',value.slice(1))).call(this);
            //}
        }
        return value;
    },
    attrDatapath: function(attrname){
        if (!attrname){
            return this.absDatapath();
        }
        var attrvalue=this.attr[attrname];
        var path=null;
        if (typeof(attrvalue)=='string') {
            if(this.isPointerPath(attrvalue)){
                attrvalue=attrvalue.slice(1);
            }
            path=this.absDatapath(attrvalue);
        }
        return path;
    },
    isPointerPath: function(path){
        if (path && (path.indexOf('^')==0) || (path.indexOf('=')==0)){
            return true;
        }
    },
    symbolicDatapath:function(path){
        var pathlist=path.split('.');
        var nodeId = pathlist[0].slice(1);
        currNode=nodeId?genro.nodeById(nodeId):this;
        if (!currNode){
            alert('not existing nodeId:'+nodeId);
        }
        var relpath=pathlist.slice(1).join('.');
        path= currNode.absDatapath(relpath?'.'+relpath:'');
        return path;
    },
    absDatapath: function(path){
        var path=path || '';
        if(this.isPointerPath(path)){
            path=path.slice(1);
        }
        if (path.indexOf('#')==0){
            return this.symbolicDatapath(path);
        }
        var currNode=this;
        var datapath;
        while(currNode && ((!path) || path.indexOf('.')==0)){
            datapath = currNode.attr.datapath;
            if(datapath){
                if(this.isPointerPath(datapath)){
                    datapath = currNode.getAttributeFromDatasource('datapath');
                    if(!datapath){
                        return null;
                    }
                } 
                if (datapath.indexOf('#')==0){
                    datapath = this.symbolicDatapath(datapath);
                }
                path =datapath + path;
            }
            currNode = currNode.getParentNode();
        }
        if (path.indexOf('.')==0){
            console.error('unresolved relativepath '+path);
        }
        path = path.replace('.?','?');
        if(path.indexOf('#parent') >0){
            path = gnr.bagRealPath(path);
        }
        return path;
    },
    
    connect: function(target,eventname,handler,parameters) {
        var eventname=((!eventname) || eventname=='action')? target.gnr._defaultEvent : eventname;
        var handler=dojo.hitch(this,funcCreate(handler,parameters));
        if (target.domNode){/* connect to a widget*/
            if (eventname in target){
                dojo.connect(target, eventname, handler);
            }else{
                dojo.connect(target.domNode, eventname,  handler);
            }
        }
        else{/* connect to a domnode*/
            dojo.connect(target, eventname,  handler);
        }  
    },
    updateContent: function(kw) {
        if(this._resolver){
            var mode= kw ? 'reload' : null;
            this.getValue(mode,kw);
            this.widget.resize();
        }
    },
     setRemoteContent:function(kwargs) {
         kwargs.sync =('sync' in kwargs) ? kwargs.sync : true;
         var cacheTime=objectPop(kwargs,'cacheTime');
         var resolver = new gnr.GnrRemoteResolver(kwargs, false, cacheTime);
         resolver.updateAttr=true;
         this.setResolver(resolver);
     },
    
    _bld_data: function() {},
    _bld_dataremote: function() {},
    _bld_dataformula: function() {},
    _bld_datascript: function() {},
    _bld_datacontroller: function() {},
    _bld_datarpc: function() {},
    _bld_script: function() {
        dojo.eval(this.getValue());
    },
    _bld_css:function() {
        genro.dom.addCssRule(this.getValue());
    },
    _bld_remote:function() {
        var kwargs = objectUpdate({},this.attr);
        objectPop(kwargs,'tag');
        this.getParentNode().setRemoteContent(kwargs);
    },
    registerDynAttr: function(attr){
        this._dynattr=this._dynattr||{};
        this._dynattr[attr]=null;
    },
    registerNodeDynAttr: function(returnCurrentValues){
        this._resetDynAttributes();
        var attributes = {};
        var attrvalue;
        for (var attr in this.attr){
            attrvalue = this.attr[attr];
            attributes[attr] = attrvalue;
            if((typeof(attrvalue)=='string') && this.isPointerPath(attrvalue)){
                if((attrvalue.indexOf('^')==0)){
                     this.registerDynAttr(attr);
                }
                if(returnCurrentValues){
                    attributes[attr] = this.getAttributeFromDatasource(attr);
                }
            } 
        }
        return attributes;
    },
    evaluateOnNode: function(pardict){
        // given an object representing dynamic parameters
        // get current values relative to this node
        // eg. values starting with ^. are datapath relative to the current node
        for (var attr in pardict){
            pardict[attr] = this.currentFromDatasource(pardict[attr]);
        }
        return pardict;
    },
    currentAttributes: function(){
        var attributes = {};
        for (var attr in this.attr){
            attributes[attr] = this.getAttributeFromDatasource(attr);
        }
        return attributes;
    },
    rebuild: function(){
        this.setValue(this._value);
    },
    build: function(destination, ind){
        this._isBuilding = true;
        var attributes = this.registerNodeDynAttr(true);
        //var attributes = this.currentAttributes();
        var tag =objectPop(attributes,'tag');
        if (!tag){
            this._buildChildren(destination);
        }else{
            this._doBuildNode(tag, attributes, destination, ind);
            this._setDynAttributes();
        }
        this._isBuilding=false;
    },
    _buildChildren: function(destination){
        if(this.attr.remote){
            dojo.connect(this.widget,'onShow',this,'updateRemoteContent');
        }
        var content = this.getValue('static');
        if (content instanceof gnr.GnrDomSource){
            var sourceNodes = content.getNodes();
            var node;
            var newobj;
            for (var i=0; i< sourceNodes.length;i++){
                node=sourceNodes[i];
                if(node.attr.tag){ // ignore nodes without tag: eg. grid structure
                    var aux='_bld_'+node.attr.tag.toLowerCase();
                    if (aux in node){
                        node[aux].call(node);
                    }else{
                        node.build(destination,-1); // append to parent
                    }
                }
            }
        }
    },
    _registerNodeId: function(nodeId){
        var nodeId = this.attr.nodeId || nodeId;
        if (nodeId){
            genro.src._index[nodeId]=this;
        }
    },
    _doBuildNode: function(tag, attributes, destination, ind){
        var bld_attrs = objectExtract(attributes,'onCreating,onCreated,gnrId,tooltip,nodeId');
        var connections = objectExtract(attributes,'connect_*');
        if (objectPop(attributes,'autofocus')){
            attributes.subscribe_onPageStart="this.focus()";
        }
        var subscriptions = objectExtract(attributes,'subscribe_*');
            
        var attrname;
        var ind=ind || 0;
        if (bld_attrs.onCreating){
            funcCreate(bld_attrs.onCreating).call(this, attributes) ;
        }
        var newobj = genro.wdg.create(tag, destination, attributes, ind, this);
        
        this._registerNodeId(bld_attrs.nodeId);
        
        if (bld_attrs.gnrId){
            this.setGnrId(bld_attrs.gnrId, newobj);
        }
        
        //dojo.hitch(this,'_buildChildren',newobj)
        this._buildChildren(newobj);
        if('startup' in newobj){
             newobj.startup();
        }
        if((typeof(this.attr.value) == 'string') && (this.isPointerPath(this.attr.value))){
            newobj.gnr.connectChangeEvent(newobj);
        }
        for(var eventname in connections){
            this.connect(newobj, eventname,connections[eventname]);
        }
        for(var subscription in subscriptions){
            var handler=funcCreate(subscriptions[subscription]);
                dojo.subscribe(subscription, newobj, handler);
        }
        if (bld_attrs.onCreated){
            funcCreate(bld_attrs.onCreated,'widget,attributes').call(this, newobj, attributes);
        }

        if(bld_attrs.tooltip){
            genro.wdg.create ('tooltip',null, {label:bld_attrs.tooltip}).connectOneNode(newobj.domNode || newobj);
        }

        return newobj;
    },
    _resetDynAttributes : function(){
        if (this._dynattr){
            delete this._dynattr;
        }
        var stringId=this.getStringId();
        var nodeSubscribers = genro.src._subscribedNodes[stringId];
        if(nodeSubscribers){
            for (var attr in nodeSubscribers){
                dojo.unsubscribe(nodeSubscribers[attr]);
            }
            delete genro.src._subscribedNodes[stringId];
        }
    },
    _setDynAttributes : function(){
        var stringId=this.getStringId();
        if (this._dynattr){
            var nodeSubscribers={};
            var path,fn,prop;
            for (var attr in this._dynattr){
                nodeSubscribers[attr]=this._subscriptionHandle(attr);
            }
            genro.src._subscribedNodes[stringId] = nodeSubscribers;
        }
    },
    _subscriptionHandle:function(attr){
        var prop = attr;
        return dojo.subscribe('_trigger_data',this,function(kw){this.trigger_data(prop,kw);});
    },
    setGnrId:function(gnrId, obj){
        var idLst=gnrId.split('.');
        var curr=genro;
        for (var i=0;i<idLst.length-1;i++){
            var id=idLst[i];
            if (!curr[id]){ curr[id]={};};
            curr=curr[id];
        }
        curr[idLst[idLst.length-1]] = obj;
    },
    getFormHandler:function(){
        if (this.formHandler != null){
            return this.formHandler;
        } else {
            var parent = this.getParentNode();
            if(parent){
                return parent.getFormHandler();
            }
        }
    },
    //updateBuiltObj:function(){
    //    for(var attr in this._dynattr){
    //        this.updateAttrBuiltObj(attr);
    //    }
    //},
    updateAttrBuiltObj:function(attr, kw, trigger_reason){
       var attr = attr || 'value';
       var attr_lower = attr.toLowerCase();
       var path;
       var value = null;
       if (!(kw.evt=='ins' || kw.evt=='del')) {
           value=this.getAttributeFromDatasource(attr,true);
       }
       value = (value!=null) ? value : '';
       if (attr=='datapath'){           
           var absDatapath = this.absDatapath();
           if (absDatapath){
               genro.fireDataTrigger(absDatapath);
           }
       }
       else if(this.externalWidget){
           if ('gnr_'+attr in this.externalWidget){
               this.externalWidget['gnr_'+attr](value,kw,trigger_reason);
           }
           return;
       }
       else if (attr=='_class'){
           var oldvalue = ('oldvalue' in kw)? kw.oldvalue :  kw.changedAttr? kw.oldattr[kw.changedAttr]:null;
           
           var domnode;
           if (this.widget){
               domnode=this.widget.domNode;
           }
           else{
               domnode=this.domNode;
           }
           if (oldvalue){
               if (oldvalue instanceof gnr.GnrBag){
                   var q = kw.pathlist.length;
                   var p=this.absDatapath(this.attr._class).split('.').slice(q-1);
                   var old_class=oldvalue.getItem(p.join('.'));
               }else{
                   var old_class=oldvalue;
               }
               genro.dom.removeClass(domnode, old_class);
              }
           genro.dom.addClass(domnode, value);
       }
       else if (this.widget){
           if(attr.indexOf('remote_')==0){
               this.updateRemoteContent(this);
           }
           else if(attr.indexOf('__')==0){
               return;
           }
           else if ((attr_lower=='disabled') || (attr_lower=='readonly'))  {
               this.widget.setAttribute(attr_lower,value? true:false);
           }
           else if ((attr=='storepath') && (this.attr.storepath.indexOf('^') == 0)){
               this.rebuild();
           }
           else if(attr.indexOf('validate_')==0){
               //this.validationsOnChange(this, this.getAttributeFromDatasource('value'));
               if(trigger_reason=='node'){
                   this.resetValidationError();
                   var currval =  this.getAttributeFromDatasource('value');
                   var newval = this.validationsOnChange(this, currval)['value'];
                   this.updateValidationStatus();
                   this.setAttributeInDatasource('value', newval);
               }
           }
           else{
                var setter='set'+stringCapitalize(attr);
                if (setter in this.widget){
                    if (attr=='value'){
                        this.resetValidationError();                // reset validationError when data from bag is set in widget
                        if('_lastValueReported' in this.widget){    // VERIFICARE DOJO 1.2
                            this.widget._lastValueReported = value; // see dijit.form._formWidget setValue
                        }                                           // force _lastValueReported to get onChange event
                        kw = false;
                    }
                    dojo.hitch(this.widget,setter)(value, kw);
                    if ((attr=='value') && (this.hasValidations())){
                        var formHandler = this.getFormHandler();
                        if(formHandler){
                            formHandler.validateFromDatasource(this, value, trigger_reason);
                        }
                    }
                }else{
                    this.rebuild();
                }
            }
        }
        else if(this.domNode){
            var domnode=this.domNode;
            var setter='set'+stringCapitalize(attr);
            if(attr=='disabled'){domnode.disabled = value ? true : false; return;}
            else if(attr=='visible'){dojo.style(domnode,'visibility',(value ? 'visible':'hidden'));return;}
            else if(attr=='hidden'){dojo.style(domnode,'display',(value ? 'none':''));return;}
            else if(attr=='value'){
                if ('value' in domnode){
                    domnode.value=value;
                }
                else{
                    //genro.debug('unable to use datasource for node:'+this.getFullpath());
                }
            }
            else if(attr=='datasource'){
                domnode.innerHTML = dataTemplate(this.attr.template,this,this.attr.datasource);
            }
            else if(attr=='innerHTML'){
                domnode.innerHTML = value;
            }
           else if(genro.dom.isStyleAttr(attr)){
                var attr=attr.replace('_','-');
                dojo.style(domnode,attr,value);
           }
           else if(setter in domnode.gnr){
               dojo.hitch(domnode.gnr, setter)(domnode, value, kw);
           }
           else{
               var attrdict = {};
               this.setAttr(attrdict, this, true);
               //this.setAttr({attr:value}, this, true);
               
               //domnode.setAttribute(attr,value);
           }
        }
    },
    _stripData: function(){
        var content=this.getValue('static');
        var dflt;
        if (content instanceof gnr.GnrBag){
            var bagnodes=content.getNodes();
            var node,v;
            for(var i=0;i<bagnodes.length;i++){
                node=bagnodes[i];
                if (node.attr.tag){
                    if(node.attr.tag.toLowerCase() in genro.src.datatags){
                        node._moveData(node);
                    }
                    else {
                        var nodeattr=node.attr;
                        for (var attr in nodeattr){
                            if ((typeof (nodeattr[attr]) =='string') && node.isPointerPath(nodeattr[attr])){
                                dflt = (attr=='value') ? (nodeattr['default'] || nodeattr['default_value']||'') : nodeattr['default_'+attr];
                                node.getAttributeFromDatasource(attr, true, dflt);
                            }
                        }
                    }
                    node._stripData();
                }
            }
        } 
    },
    _moveData: function() {
        this._registerNodeId();
        var attributes = this.registerNodeDynAttr(false);
        //var attributes=this.currentAttributes();
        var tag= objectPop(attributes,'tag');
        var path = this.absDatapath( objectPop(attributes,'path'));
        if(tag=='data' && attributes.remote ){
            attributes['method']=objectPop(attributes,'remote');
            tag='dataRemote';
        }
        if(tag=='data'){
            var value = this.getValue();
            this._value=null;
            if (value instanceof gnr.GnrBag){
                value.clearBackRef();
            }
            var context = objectPop(attributes, 'context');
            genro.setData(path,value,attributes);
            if(context){
                if (!(value instanceof gnr.GnrBag)){
                    value = new gnr.GnrBag();
                    genro.setData(path, value, attributes);
                }
                if (!genro.contextIndex[context]){
                    
                    genro.contextIndex[context] = this;
                    value.subscribe('context',{'any':dojo.hitch(this, "contextChange")});
                } else {
                    alert("Context name conflict: "+context);
                }
            }
        }else if (tag=='dataRemote'){
            this._dataprovider=tag;
            this.setDataNodeValue();
        }else{
            //var functions=objectExtract(attributes,'function_*');
            //for (func in functions){
            //    this[func] = funcCreate(functions[func],null,this);
            //}            
            var initialize = objectPop(attributes,'_init');
            this._dataprovider=tag;
            if(initialize){
                this.setDataNodeValue();
            }else{
                genro.getDataNode(path, true);
                //genro.setData(path,null);
            }
            var timing = objectPop(attributes,'_timing');
            
            if(timing){
                var timerFunc = dojo.hitch(this, 'setDataNodeValue');
                setInterval(timerFunc, timing*1000);
            }
            var onStart = objectPop(attributes,'_onStart');
            if (onStart){
                this.attr._fired_onStart='^gnr.onStart';
                this.registerDynAttr('_fired_onStart');
                if (typeof(onStart) == "number" && !this.attr._delay) {
                    this.attr._delay = onStart;
                };
            }
        }     
        this._setDynAttributes();
    },
    updateRemoteContent:function(forceUpdate){
        var currentValue = this.getValue('static');
        if (currentValue && currentValue.len()>0 && !forceUpdate){
            return;
        }
        var kwargs={};
        for (var attrname in this.attr){
            if(attrname.indexOf('remote_')==0){
                kwargs[attrname.slice(7)]=this.getAttributeFromDatasource(attrname);
            }
        }
        var method=this.attr.remote;
        var _sourceNode=this;
        kwargs.sync=true;
        genro.rpc.remoteCall(method, kwargs, null, null, null, function(result){
                                             _sourceNode.setValue(result);
                                             });
    },
    getValidationError: function(){
        if (this._validations){
            return this._validations.error;
        }
    },
    getValidationWarnings: function(){
        if (this._validations){
            return this._validations.warnings;
        }
    },
    isValidationRequired: function(){
        if ((this._validations) && (this._validations.required)){
            return true;
        }
    },
    hasValidationWarnings: function(){
        if ((this._validations) && (objectNotEmpty(this._validations.warnings))){
            return true;
        }
    },
    hasValidationError: function(){
        if ((this._validations) && (this._validations.error)){
            return true;
        }
    },
    resetValidationError: function(){
        if(this._validations){
            this._validations.error = null;
            this._validations.warnings = [];
            this._validations.required = null;
            this.updateValidationClasses();
        }
    },
    setValidationError: function(validation_result){
        this._validations.error = validation_result.error;
        this._validations.warnings = validation_result.warnings;
        this._validations.required = validation_result.required;
        this.updateValidationClasses();
    },
    setValidations: function(){
        this._validations = {};
    },
    hasValidations: function(){
        if(this._validations){
            return true;
        }
    },
    updateValidationStatus: function(kw){
        if(this.widget){
            this.updateValidationClasses();
            this.widget.state = this.hasValidationError() ? 'Error' : null;
            this.widget._setStateClass();
        }
    },
    updateValidationClasses: function(){
        if (this.widget.cellNode){
            var domnode = this.widget.cellNode;
        }else{
            var domnode = this.widget.focusNode; //(this.widget.stateNode||this.widget.domNode);
  
        }
        if(this.isValidationRequired()){
            genro.dom.addClass(domnode, 'gnrrequired');
        } else {
            genro.dom.removeClass(domnode, 'gnrrequired');
        }        
    },
    contextChange: function(kw){
        if(kw.reason != 'autocreate'){
            genro.rpc.remoteCall('updateSessionContext', {'context': this.attr.context,
                                                 'value': kw.node._value,
                                                  'attr': kw.node.attr,
                                                   'evt': kw.evt,
                                                  'path': kw.pathlist.join('.')
                                                },
                                null, 'GET');
        }
    },
    setSource: function(path, /*gnr.GnrDomSource*/ source){
       var content=this.getValue();
       var child;
       if (!content){
           content=new gnr.GnrDomSource();
           this.setValue(content,false);
       }else{
           if (!(content instanceof gnr.GnrDomSource)){
                 this.setValue(content,false);
           }
       }
       child = content.setItem(path, source.getNodes()[0]);
       return child;
   },     
   _ : function(tag,name,attributes){
           var content=this.getValue();
           var child;
           if (!content){
               content=new gnr.GnrDomSource();
               this.setValue(content,false);
           }else{
               if (!(content instanceof gnr.GnrDomSource)){
                     this.setValue(content,false);
               }
           }
           child = content._(tag,name,attributes);
           return child;
       }
});

dojo.declare("gnr.GnrStructData",gnr.GnrBag,{    
   // constructor: function(source){
   //     this._validationPrefix = 'structvalidate_';
   // }
});

dojo.declare("gnr.GnrDomSource",gnr.GnrStructData,{
    _validationPrefix: 'structvalidate_',
    _nodeFactory:gnr.GnrDomSourceNode,
    
    _ : function(tag, name/*optional*/, attributes/*Object*/){
            var tag_UpperLower = null;
            var name, content;
            tag=tag.toLowerCase();
            if(tag){
                if (name instanceof Object){
                    var attributes =  name;
                    var name='';
                }
                var attributes=attributes || {};
                name = name || '*_?';
                name = name.replace('*', tag).replace('?', this.len());
                if (attributes.content){
                    content = attributes.content;
                    delete attributes.content;
                }
                if (content == null){ 
                        content = new gnr.GnrDomSource();
                }
                attributes.tag = tag;
                this.setItem(name, content, attributes);
                return content;
            }
            
    },

    component: function(){
        if (this.component != null){
            return this._component;
        }else if (this.parent!=null){
            return this.parent.component();
        }
    }

});



