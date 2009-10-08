/*
*-*- coding: UTF-8 -*-
*--------------------------------------------------------------------------
* package       : Genro js - see LICENSE for details
* module genro_rpc : Genro clientside module for remote calling remote methods
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
dojo.declare("gnr.GnrRemoteResolver",gnr.GnrBagResolver,{
    constructor: function(kwargs, isGetter, cacheTime){
        this.xhrKwargs = {'handleAs': 'xml',
                            'timeout': 50000,
                            'load': 'resultHandler',
                            'error': 'errorHandler',
                            'sync': false,
                            'preventCache': false
                        };
        var k;
        for (k in this.xhrKwargs){
            if (k in kwargs){
                this.xhrKwargs[k] = objectPop(kwargs, k);
            }
        }
        this.xhrKwargs.load = dojo.hitch(this, this.xhrKwargs.load);
        this.xhrKwargs.error = dojo.hitch(this, this.xhrKwargs.error);
        this.httpMethod = objectPop(kwargs, 'httpMethod');
        this.onloading = null;
    },
    load: function (kwargs){
        if (this.onloading){
            this.onloading(kwargs);
        }
        var sync = this.xhrKwargs.sync;
        var sourceNode = objectPop(kwargs, '_sourceNode');
        var result = genro.rpc._serverCall(kwargs, this.xhrKwargs, this.httpMethod, sourceNode);
        if (sync){
            result.addCallback(function(value){
                result= value;
            });
        }
        return result;
    },
    errorHandler: function(response, ioArgs){
        return genro.rpc.errorHandler(response, ioArgs);
    },
    resultHandler: function(response, ioArgs){
        return genro.rpc.resultHandler(response, ioArgs, (this.updateAttr ? this._parentNode.attr: null));
    }
});

dojo.declare("gnr.GnrServerCaller",gnr.GnrBagResolver,{
    constructor: function(kwargs /*url, page_id, methodname, params*/){
        alert("GnrServerCaller");
        if (typeof kwargs.params == 'string'){
            this.evaluate = 'this.params = ' + kwargs.params;
            this.params = {};
        } else {
            this.evaluate = null;
            this.params = kwargs.params;
        }
        this.methodname = kwargs.methodname;
        this.respars = kwargs.respars || {};
        },

    load: function (kwargs, cb){
        if(this.evaluate){
            eval(this.evaluate);
        }
        if (kwargs){
            objectUpdate(this.params, kwargs);
        }
        return genro.rpc.remoteCall(this.methodname,this.params, this.respars.mode || 'bag',null,null, cb);
    }
    
});


dojo.declare("gnr.GnrRpcHandler",null,{
    
    constructor: function(application){
        this.application=application;
        this.counter=0;
    },
    /* callbackArgs 
              args: Object 
                  the original object argument to the IO call.
              xhr: XMLHttpRequest
                  For XMLHttpRequest calls only, the
                  XMLHttpRequest object that was used for the
                  request.
              url: String
                  The final URL used for the call. Many times it
                  will be different than the original args.url
                  value.
              query: String
                  For non-GET requests, the
                  name1=value1&name2=value2 parameters sent up in
                  the request.
              handleAs: String
                  The final indicator on how the response will be
                  handled.
              id: String
                  For dojo.io.script calls only, the internal
                  script ID used for the request.
              canDelete: Boolean
                  For dojo.io.script calls only, indicates
                  whether the script tag that represents the
                  request can be deleted after callbacks have
                  been called. Used internally to know when
                  cleanup can happen on JSONP-type requests.
              json: Object
                  For dojo.io.script calls only: holds the JSON
                  response for JSONP-type requests. Used
                  internally to hold on to the JSON responses.
                  You should not need to access it directly --
                  the same object should be passed to the success
                  callbacks directly.

    */
    serverCall:function(callKwargs, xhrKwargs, httpMethod){
        
    },
    _serverCall:function(callKwargs, xhrKwargs, httpMethod,sourceNode){
        // s=serverCall({method:'moltiplica', op1:3, op2:7},{timeout:300,handleAs'xml',load=function(){}}
        /* 
        callKwargs :       The parameters for the server call. For genropy webpage
                           it should include also the method to call.
                           Remaining parameters should be jsonable so, for example, a bag should
                           be converted to xml before this call.

        xhrKwargs  :       Object with original dojo parameters
                     url - URL to server endpoint.
                 content - Object : Contains properties with string values. These
                           properties will be serialized as name1=value2 and
                           passed in the request.
                 timeout - Integer : Milliseconds to wait for the response. If this time
                           passes, the then error callbacks are called.
            preventCache - Boolean : Default is false. If true, then a
                           "dojo.preventCache" parameter is sent in the request
                           with a value that changes with each request
                           (timestamp). Useful only with GET-type requests.
                handleAs - String : Acceptable values depend on the type of IO
                           transport (see specific IO calls for more information).
                    load - Function : function(response, ioArgs){}. response is an Object, ioArgs
                           is of type callbackArgs. The load function will be
                           called on a successful response.
                   error - Function : function(response, ioArgs){}. response is an Object, ioArgs
                           is of type callbackArgs. The error function will
                           be called in an error case. 
                  handle - Function : function(response, ioArgs){}. response is an Object, ioArgs
                           is of type callbackArgs. The handle function will
                           be called in either the successful or error case.  
                    sync - Boolean. false is default. Indicates whether the request should
                           be a synchronous (blocking) request.
                 headers - Object. Additional HTTP headers to send in the request.
        */
        var httpMethod = httpMethod || 'GET';
        callKwargs = this.serializeParameters(this.dynamicParameters(callKwargs, sourceNode));
        var content = objectUpdate({},callKwargs);
        content.page_id = this.application.page_id;
        var kw = objectUpdate({},xhrKwargs);
        kw.url = kw.url || this.pageIndexUrl();
        kw.content=content;
         //kw.preventCache = kw.preventCache - just to remember that we can have it
        kw.handleAs = kw.handleAs || 'xml';
        var xhrResult;
        if(httpMethod=='GET'){
            xhrResult=dojo.xhrGet(kw);
        }
        else if(httpMethod=='POST'){
            if ('postData' in callKwargs){
                xhrResult=dojo.rawXhrPost(kw);
            }else{
                xhrResult=dojo.xhrPost(kw);
            }
         }
         else if(httpMethod=='DELETE'){
             xhrResult=dojo.xhrDelete(kw);
         }
         else if('PUT'){
             if ('putData' in callKwargs){
                 xhrResult=dojo.rawXhrPut(kw);
             }else{
                 xhrResult=dojo.xhrPut(kw);
             }
         }     
         return xhrResult;
    },
    
    errorCallback:function(type,errObj){
        alert("errorCallback");
        
        var status=errObj.xhr.status;
        if(status=200){// it was a server error that created a traceback
            alert('there was a server error');
        }
        else if (status=401){
            genro.pageReload();
        }
        else {
            genro.iobindError = status;
        }
    },
    remoteCallAsync:function(method, params, async_cb){
        alert("remoteCallAsync");
        return this.remoteCall(method, params, null, null, null, async_cb);
    },
    remoteUpload_old: function(formElement, method, params, cb){
        alert("remoteUpload");
        dojo.require('dojo.io.IframeIO');
        var serverUrl=genro.rpc.rpcUrl(method, params);
        var cb = cb || function(type, data){alert(data.toString());};
        dojo.io.bind({
            url:serverUrl,
            handler:cb,
            mimetype: 'text/plain',
            formNode: formElement,
            sync:false
        });
    },
    downloadCall: function(method, kwargs){
        var cb = function(result){genro.download(result);};
        genro.rpc.remoteCall(method, objectUpdate(kwargs,{'mode':'text'}), null, 'POST', null, cb)
    },
    remoteCall:function(method, params, mode, httpMethod, preventCache, async_cb){
        var callKwargs = objectUpdate({}, params);
        callKwargs.method = method;
        var mode = mode || 'bag';
        var preprocessor, handleAs, result;
        if (mode == 'bag'){
            handleAs = 'xml';
            preprocessor = dojo.hitch(this, 'resultHandler');
        } 
        else{
            handleAs = mode;
            preprocessor = function(response, ioArgs){return response;};
        }
        var cb;
        var sync = objectPop(callKwargs, 'sync', false);
        if (async_cb) {
            cb = dojo.hitch(this,function(response, ioArgs){
                var result = preprocessor(response, ioArgs);
                //var innercb = dojo.hitch(this,function(){async_cb(result);});
                //setTimeout(innercb,1);
                async_cb(result);
            });
            //sync = false;
        } else {
            cb =dojo.hitch(this, function(response, ioArgs){
                result = preprocessor(response, ioArgs);
            });
            sync = true;
        }
        var timeout = objectPop(params, 'timeout', 50000);
        var xhrKwargs = {'handleAs': handleAs,
                            'timeout': timeout,
                            'load': cb,
                            'error': dojo.hitch(this,'errorHandler'),
                            'sync': sync,
                            'preventCache': preventCache
                        };
        this._serverCall(callKwargs, xhrKwargs, httpMethod);
        return result;
    },
    errorHandler: function(response, ioArgs){
        genro.dev.handleRpcHttpError(response, ioArgs);
    },
    resultHandler: function(response, ioArgs, currentAttr){
        var envelope = new gnr.GnrBag();
        envelope.fromXmlDoc(response, genro.clsdict);
        var envNode = envelope.getNode('result');
        var resultAsNode=(envelope.getItem('resultType')=='node') || currentAttr;
        
        genro.lastRpc = new Date();
        var changenode, _client_path, fired;
        var dataChanges = envelope.getItem('dataChanges');
        if(dataChanges){
            var changenodes = dataChanges.getNodes();
            for (var i=0;i<changenodes.length;i++){
                changenode = changenodes[i];
                _client_path = objectPop(changenode.attr, '_client_path');
                fired = objectPop(changenode.attr, 'fired');
                if(changenode.attr._error){
                    setTimeout(dojo.hitch(genro.dev, 'handleRpcError', changenode.attr._error, changenode));
                } else {
                    genro.setData(_client_path, changenode.getValue(), changenode.attr);
                    if (fired){
                        genro._data.setItem(_client_path, null, null, {'doTrigger':false});
                    }
                }
            };
        }
        var error = envelope.getItem('error'); 
        if(!error){
            var locStatus = envelope.getItem('_localizerStatus');
            if (locStatus){
                genro.setLocStatus(locStatus);
            }
            if(currentAttr){
                var attr = objectUpdate({}, currentAttr);
                envNode.attr = objectUpdate(attr, envNode.attr);
            }
        }else{
            setTimeout(dojo.hitch(genro.dev, 'handleRpcError', error, envNode));
            return null;
        }
        if(resultAsNode){
            return envNode;
        } else {

            return envNode.getValue();

        }
        
    },
    
    getRecordCount:function(field, value, cb){
        var result = genro.rpc.remoteCall('app.getRecordCount', {'field':field, 'value':value}, null, 'GET', null, cb);
        return result;
    },
    pageIndexUrl:function(){
        var url;
        var curloc=document.location.pathname;
        if (stringEndsWith(curloc,'/')){
            curloc = curloc.slice(0, curloc.length-1);
        }
        if (stringEndsWith(curloc,'.py')||this.application.pageMode!='legacy'){
            url= curloc;
        }else{
            
            url=curloc+'/index.py';
        }
        return url;
    },
    

    
    remoteResolver: function(methodname, params, kw /*readOnly, cacheTime*/){
        var kw = kw || {};
        var cacheTime = kw.cacheTime || -1;
        var isGetter = kw.isGetter || null;
        
        var kwargs = objectUpdate({'sync':true}, params);
        kwargs.method = methodname;
        
        var resolver = new gnr.GnrRemoteResolver(kwargs, isGetter, cacheTime);
        return resolver;
    },

    
    getURLParams: function(source){
        if (source==null){
            source = window.location.search;
        }
        var result = {};
        source.replace(/(?:[\?&])?([^=]+)=([^&]+)/g, function(str, key, value){result[key]=unescape(value);});
        return result;
    },
    
    updateUrlParams: function(params, source){
        return dojo.io.argsFromMap(objectUpdate(genro.rpc.getURLParams(source), params, true));
    },
    getRpcUrlArgs:function(method, kwargs, sourceNode, avoidCache){
        var avoidCache= avoidCache===false?false:true;
        var currParams = {};
        currParams['page_id']=this.application.page_id;
        currParams['method']=method;
        currParams['mode']='text';
        if(avoidCache!=false){
            currParams['xxcnt'] = genro.getCounter();
        }
        return objectUpdate(currParams, this.serializeParameters(this.dynamicParameters(kwargs, sourceNode)));
    }
    ,
    rpcUrl:function(method, kwargs, sourceNode, avoidCache){
        return genro.absoluteUrl(null,  genro.rpc.getRpcUrlArgs(method, kwargs, sourceNode,avoidCache), avoidCache);
    },
    
    makoUrl:function(template, kwargs){
        this.counter = this.counter + 1;
        var currParams = {};
        currParams['page_id']=this.application.page_id;
        currParams['mako']=template;
        currParams['xxcnt']=this.counter;
        objectUpdate(currParams, kwargs);
        var parameters = [];
        for (var key in currParams){
            parameters.push(key+'='+escape(currParams[key]));
        }
        return this.application.absoluteUrl('?'+parameters.join('&'));
    },
    dynamicParameters: function(source, sourceNode){
        var obj = {};
        var path;
        if ((source != '') & (typeof source == 'string')){
            source = genro.evaluate(source);
        } 
        if (source){
            for (var prop in source){
                var val = source[prop];
                if (typeof(val)=='string'){
                    var dynval = stringStrip(val);
                    if (dynval.indexOf('==')==0){
                        val = genro.evaluate(dynval.slice(2));
                    } else if((dynval.indexOf('^')==0)||(dynval.indexOf('=')==0)) {
                        path = dynval.slice(1);
                        if (sourceNode){
                            path = sourceNode.absDatapath(path);
                        } else {
                            if (path.indexOf('.') == 0){
                                throw "Unresolved relative path in dynamicParameters: " + path;
                            }
                        }
                        val = genro._data.getItem(path,'');
                    }
                } else if(typeof(val)=='function'){
                    val = val();
                }
                obj[prop]=val;
            }
        }
        return obj;
    },
    serializeParameters: function(kwargs){
        var cntrlstr=[];
        var currarg, nodeattrs;
        for (var attr in kwargs){
            currarg = kwargs[attr];
            if((currarg instanceof gnr.GnrBag) && (currarg.getParentNode() != null)){
                nodeattrs = currarg.getParentNode().getAttr();
                if(objectNotEmpty(nodeattrs)){
                    kwargs[attr+'_attr'] = asTypedTxt(nodeattrs);
                }
            }
            kwargs[attr] = asTypedTxt(currarg);
            cntrlstr.push(attr+'_'+kwargs[attr]);
        }
        return kwargs;
    },
    managePolling: function(freq){
        if(freq==null){
            freq = genro.getData('gnr.polling');
        }
        if(genro.polling){
            clearInterval(genro.polling);
            genro.polling = null;
        }        
        if(freq>0){
            genro.lastRpc = new Date();
            genro.polling = setInterval(function(){ var now = new Date();
                                if ((!genro.pollingRunning) && ((now - genro.lastRpc) > (freq*1000) )){
                                    genro.rpc.ping();
                                }
                        }, 1000);
        }
    },
    ping:function(){
        genro.pollingRunning=true;
        genro.rpc.remoteCall('ping', null, null, null, null, function(){genro.pollingRunning=false;});
    },
    
    
    remote_relOneResolver: function(params, parentbag){
        var kw = {};
        var cacheTime = -1;
        var isGetter = false;
        var sync=('sync' in params)? objectPop(params,'sync'):true;
        var kwargs = { 'sync':sync,'from_fld':params._from_fld, 
                                 'target_fld':params._target_fld, 
                             'sqlContextName':params._sqlContextName};
        kwargs.method = 'app.getRelatedRecord';
        
        var resolver = new gnr.GnrRemoteResolver(kwargs, isGetter, cacheTime);
        resolver.updateAttr=true;
        resolver.onloading = function(kwargs){
            var target = kwargs.target_fld.split('.');
            var table = target[0] + '_' + target[1];
            var loadingParameters = genro.getData('gnr.tables.'+table+'.loadingParameters');
            var rowLoadingParameters = objectPop(kwargs, 'rowLoadingParameters');
            if(rowLoadingParameters){
                loadingParameters = loadingParameters || new gnr.GnrBag();
                var nodes = rowLoadingParameters.getNodes();
                for (var i=0; i < nodes.length; i++) {
                    if(nodes[i].label[0]!='@'){
                        loadingParameters.setItem(nodes[i].label, nodes[i].getValue(), nodes[i].attr);
                    }
                };
            }
            kwargs['loadingParameters'] = loadingParameters;
        };
        var _related_field = params._target_fld.split('.')[2];
        
        if(params._auto_relation_value){
            resolver.relation_fld = params._auto_relation_value; //params._from_fld.split('.')[2];
            var dataprovider = function(){
                return this.getParentNode().getParentBag().getItem(this.relation_fld);
            };
            kwargs[_related_field] = dojo.hitch(resolver, dataprovider);

            //TODO: move that feature to BagNode.setResolver
            var valNode = parentbag.getNode(resolver.relation_fld);
            var reloader = function(){
                this.getParentNode().getValue('reload');
            };
            valNode._onChangedValue = dojo.hitch(resolver, reloader);

        } else {
        	kwargs[_related_field] = params._relation_value;
        }
        return resolver;
    },
    remote_relManyResolver: function(params){
        var kw = {};
        var cacheTime = -1;
        var isGetter = false;

        var kwargs = {'sync':true, 
                      'from_fld':params._from_fld, 'target_fld':params._target_fld, 'relation_value':params._relation_value,
                      'sqlContextName':params._sqlContextName};
        kwargs.method = 'app.getRelatedSelection';
                
        var resolver = new gnr.GnrRemoteResolver(kwargs, isGetter, cacheTime);
        resolver.updateAttr=true;
        resolver.onSetResolver = function(node){
            node.newBagRow = function(defaultArgs){
                var childResolverParams=this.attr.childResolverParams
                var table = childResolverParams._target_fld.split('.').slice(0,2).join('_');
                var loadingParameters = genro.getData('gnr.tables.'+table+'.loadingParameters');
                if (defaultArgs instanceof Array){
                    
                } else {
                    //var defaultArgs = defaultArgs || {};
                    var resolver = genro.getRelationResolver(objectUpdate(childResolverParams,{'sync':true}));
                    if (!defaultArgs){
                        
                    }
                    resolver.kwargs.rowLoadingParameters = new gnr.GnrBag(defaultArgs);
                    
                    var attr = objectUpdate({}, childResolverParams);
                    for (var label in defaultArgs) {
                        attr[label.replace(/\W/g,'_')] = defaultArgs[label];
                    };
                    if (loadingParameters){
                        var nodes= loadingParameters.getNodes();
                        for (var i=0; i < nodes.length; i++) {
                            var n = nodes[i];
                            attr[n.label] = n.getValue();
                        };
                    }
                    var result = new gnr.GnrBagNode(null,'label',null , attr, resolver);
                    //result.getValue();
                    return result;
                }
            };
        };
        resolver.updateAttr=true;
        return resolver;
    }
    
});