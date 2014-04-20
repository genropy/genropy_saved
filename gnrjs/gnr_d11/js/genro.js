/*
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro  : Genro client application
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
var dojo_version = dojo.version.major + '.' + dojo.version.minor;
dojo.require("dojo.date");
dojo.require('dijit.Tooltip');
dojo.require('dojo.date.locale');
dojo.require("dojo.currency");
dojo.require("dojox.validate.web");
dojo.require("dojo.number");
dojo.require("dojo.cookie");
dojo.require("dojo.fx");
dijit.showTooltip = function(/*String*/ innerHTML, /*DomNode*/ aroundNode) {
    // summary:
    //  Display tooltip w/specified contents to right specified node
    //  (To left if there's no space on the right, or if LTR==right)
    if (!dijit._masterTT) {
        dijit._masterTT = new dijit._MasterTooltip();
    }
    var tooltip_text = innerHTML;
    if (tooltip_text instanceof Function) {
        tooltip_text = tooltip_text(aroundNode);
    }
    return dijit._masterTT.show(tooltip_text, aroundNode);
};

/* ----------- Class gnr.GenroClient ----------------*/
dojo.declare('gnr.GenroClient', null, {

    constructor: function(kwargs) {
        //this.patchConsole();
        this.domRootName = kwargs.domRootName || 'mainWindow';
        this.page_id = kwargs.page_id;
        this.startArgs = kwargs.startArgs || {};
        this.debuglevel = kwargs.startArgs.debug || null;
        this.debug_sql = kwargs.startArgs.debug_sql;
        this.debug_py = kwargs.startArgs.debug_py;

        this.pageMode = kwargs.pageMode;
        this.baseUrl = kwargs.baseUrl;
        this.serverTime = convertFromText(objectPop(kwargs.startArgs,'servertime'));
        var start_ts = new Date();
        this.serverTimeDelta = this.serverTime - start_ts;
        this.lockingElements = {};
        this.debugRpc = false;
        this.polling_enabled = false;
        this.auto_polling = -1;
        this.user_polling = -1;
        this.isDeveloper = objectPop(this.startArgs,'isDeveloper');
        this.theme = {};
        this.dojo = dojo;
        this.ext={};
        this.userInfoCb = [];
        this.formatter = gnrformatter;
        this.timeProfilers = [];
        this.currProfilers = {nc:0,st:0,sqlt:0,sqlc:0};
        this.rpcHeaderInfo = {};
        this.profile_count = 4;
        this.lastPing = start_ts;
        this._lastUserEventTs = start_ts;
        this._lastChildUserEventTs = start_ts;
        this._lastGlobalUserEventTs = start_ts;
        this._lastRpc = start_ts;

        for (var i = 0; i < this.profile_count; i++) {
            this.timeProfilers.push({nc:0,st:0,sqlt:0,sqlc:0});  
        };
        
        setTimeout(dojo.hitch(this, 'genroInit'), 1);
    },

    patchConsole:function(){
        console.zlog = console.log;
        console.log = function(){
            if(!arguments[0]){
                genro.bp(true)
            }
            console.zlog(arguments);
        };
    },

    genroInit:function() {
        this.startTime = new Date();
        this.lastTime = this.startTime;
        this.dialogStack = [];
        this.sounds = {};
        this._serverstore_paths = {};
        this._serverstore_changes = null;
        this.pendingCallAfter = {};
        var plugins = objectExtract(window, 'genro_plugin_*');
        objectUpdate(genro, plugins);
        this.compareDict = { '==' : function(a, b) {return (a == b);},
                             '>'  : function(a, b) {return (a > b);},
                             '>=' : function(a, b) {return (a >= b);},
                             '<'  : function(a, b) {return (a < b);},
                             '<=' : function(a, b) {return (a <= b);},
                             '!=' : function(a, b) {return (a != b);},
                             '%'  : function(a, b) {return (a.indexOf(b) >= 0);},
                             '!%' : function(a, b) {return (a.indexOf(b) < 0);}
                             };
        window.onbeforeunload = function(e) {
            var exit;
            if (genro.checkBeforeUnload) {
                exit = genro.checkBeforeUnload();
            }
            if (exit) {
                return exit;
            }
            //if(!genro.root_page_id){
            //    var rootenv = genro.getData('gnr.rootenv');
            //    if(rootenv){
            //        var b = new gnr.GnrBag();
            //        b.setItem('rootenv',rootenv,{page_id:genro.page_id});
            //        dojo.cookie(genro.getData('gnr.siteName')+'_dying_'+genro.getData('gnr.package')+'_'+genro.getData('gnr.pagename'),b.toXml(),{'expires':new Date((new Date().getTime()+2000))});
            //    }
            //}            
        };
        window.onunload = function(e) {
            genro.onWindowUnload(e);
        };
        this.rpc = new gnr.GnrRpcHandler(this);
        this.src = new gnr.GnrSrcHandler(this);
        this.wdg = new gnr.GnrWdgHandler(this);
        this.dev = new gnr.GnrDevHandler(this);
        this.dlg = new gnr.GnrDlgHandler(this); //da implementare

        this.dom = new gnr.GnrDomHandler(this);
        this.vld = new gnr.GnrValidator(this);
        var onerrorcb = function(errorMsg,url,linenumber){
            genro.onError(errorMsg,url,linenumber);
        };
        window.onerror = onerrorcb;

        dojo.connect(console.err,onerrorcb);

        if (dojo_version == '1.1') {
            if (dojo.isSafari) {
                dojo.keys.DOWN_ARROW = 40;
                dojo.keys.UP_ARROW = 38;
            }
            genropatches.getDocumentWindow();
            genropatches.forEachError();
            genropatches.borderContainer();
            genropatches.setStateClass();
            genropatches.menu();
            genropatches.comboBox();
            genropatches.tree();
            //genropatches.grid();
            genropatches.parseNumbers();
            genropatches.dojoToJson();
            genropatches.sendAsBinary();
        }
        this.clsdict = {domsource:gnr.GnrDomSource, bag:gnr.GnrBag};
        this.eventPath = '_sys.events';
        this.prefs = {'recordpath':'tables.$dbtable.record',
            'selectionpath':'tables.$dbtable.selection',
            'limit':'50'};
        var mainWindow = dojo.byId('mainWindow');
        dojo.locale = dojo.i18n.normalizeLocale(dojo.locale);
        if (mainWindow && mainWindow.clientHeight===0){
            genro._startDelayer = setInterval(function(){
                if(dojo.byId('mainWindow').clientHeight>0){
                    clearInterval(genro._startDelayer);
                    genro.start();
                }
            },200);
        }else{
            dojo.addOnLoad(genro, 'start');
        }

    },

    compare: function(op, a, b) {
        if((a instanceof Date) && (b instanceof Date)){
            a = a.valueOf();
            b = b.valueOf();          
        }
        return genro.compareDict[op](a, b);
    },
    timeIt:function(msg) {
        var t = this.lastTime;
        this.lastTime = new Date();
        console.log('----timeIt:' + msg + ':' + (this.lastTime - t) + ' - totalTime:' + (this.lastTime - this.startTime));
    },
    ping:function() {
        genro.rpc.ping();
    },
    assert:function(condition,msg,level){
        if(!condition){
            console[level || 'error'](msg);
        }
    },

    safetry:function(cb){
        try{
            return cb();
        }catch(e){
            console.error(e.message);
            console.log(e.stack);
        }

    },

    bp:function(aux) {
        console.log('bp ',arguments);
        if (aux===true){
            debugger;
        }
    },
    
    debugEvent:function(e,sourceNode,evt_type) {
        if(!evt_type||(evt_type==e.type)){
            console.log('debugEvent ',e.keyCode,keyName(e.keyCode),e.type);
        }
    },

    onError:function(errorMsg,url,linenumber){
        var msg = "<div style='white-space:nowrap;'>"+url+' line:'+linenumber+'</div>'+errorMsg;
        genro.dev.addError(msg,'js',true);
    },

    onWindowUnload:function(e) {
        this.rpc.remoteCall('onClosePage', {sync:true});
        genro.publish('onClosePage');
        if (genro._data) {
            genro.saveContextCookie();
        }
    },
    saveContextCookie:function() {
        var clientCtx = genro.getData('_clientCtx');
        //genro.publish('onCookieSaving');
        if (clientCtx) {
            dojo.cookie("genroContext", clientCtx.toXml(), { expires: 5,path:genro.getData('gnr.homeUrl')});
        }
    },
    clientCtx:function(path) {
        var path = path ? '.' + path : '';
        return genro._('_clientCtx' + path);
    },
    warning: function(msg) {
        console.warn(msg);
        genro.dlg.message(msg);
    },

    commandLink:function(href,content){
        return "<a onclick='if((genro.isMac&&!event.metaKey)||(!genro.isMac&&!event.ctrlKey)){dojo.stopEvent(event);}' class='gnrzoomcell' href='"+href+"'>" + content + "</a>";
    },

    childUserEvent:function(childgenro){
        genro._lastChildUserEventTs = new Date();
        genro._lastGlobalUserEventTs = genro._lastChildUserEventTs > genro._lastUserEventTs? genro._lastChildUserEventTs:genro._lastUserEventTs;
        genro.onUserEvent();
    },

    _registerUserEvents:function(){
        var cb = function(){
            genro._lastUserEventTs = new Date();
            genro._lastGlobalUserEventTs = new Date();
            if(genro.root_page_id){
                genro.mainGenroWindow.genro.childUserEvent();
            }else{
                genro.onUserEvent();
            }
            genro.execUserInfoCb();
        };
        dojo.connect(window, 'onclick', cb);
        dojo.connect(window, 'onmousemove', cb);
        dojo.connect(window, 'onkeypress', cb);
        setInterval(function(){
            genro.timeProfilers.push(genro.currProfilers);
            if(genro.timeProfilers.length>genro.profile_count){
                genro.timeProfilers = genro.timeProfilers.slice(-genro.profile_count);
            }
            genro.currProfilers = {nc:0,st:0,sqlt:0,sqlc:0};
        },15000);
    },
    
    execUserInfoCb:function(){
        if(genro.userInfoCb.length>0){
            var userInfoCb = genro.userInfoCb;
            genro.userInfoCb = [];
            dojo.forEach(userInfoCb,function(cb){cb()});
        }
    },
    getScreenLockTimeout:function(){
        if(!genro._screenlock_timeout){
            genro._screenlock_timeout = genro.userPreference('adm.general.screenlock_timeout') || genro.appPreference('adm.general.screenlock_timeout') || -1;
        }
        return genro._screenlock_timeout;
    },

    onUserEvent:function() {
        if (genro.user_polling > 0) {
            if ((genro._lastGlobalUserEventTs - genro.lastPing) / 1000 > genro.user_polling) {
                genro.rpc.ping({'reason':'user'});
            }
        }
        var st = genro.getScreenLockTimeout();
        if(st>0){
            genro.callAfter(function(){
                 genro.publish('screenlock');
            },st*1000*60,this,
            'screenlock');
        }
        if(genro.fast_polling){
            if(!genro.fast_polling_limiter){
                genro.setAutoPolling(true);
            }
        }
        var now = new Date();
        for (var k in genro.rpc.rpc_register){
            var kw = genro.rpc.rpc_register[k];
            var age = now-kw.__rpc_started;
            if (age>5000){
                console.warn('slow rpc pending',kw,age);
                objectPop(genro.rpc.rpc_register,k);
            }
        }
    },
    
    loginDialog:function(loginUrl){
        genro.src.getNode()._('div', '_loginDialog_');
        var node = genro.src.getNode('_loginDialog_').clearValue();
        
        var dlg = node._('dialog',{'_class':'lightboxDialog'});
        dlg._('iframe',{'height':'500px',width:'600px',border:0,src:loginUrl,background:'transparent'});
        dlg.getParentNode().widget.show();
    },
    
    login: function(data,kw) {
        genro.serverCall('doLogin',objectUpdate({'login':data},kw),function(result){
            result=result.getValue()
            var message=result.getItem('message')
            if (message){
                genro.publish('invalid_login',{'message':message})
            }else{
                genro.mainGenroWindow.location.reload();
            }
        })
    },
    start: function() {
                /*
         Here starts the application on page loading.
         It calls the remoteCall to receive the page contained in the bag called 'main'.
         */
        //genro.timeIt('** dostart **');
        this._dataroot = new gnr.GnrBag();
        this._dataroot.setBackRef();
        this._data = new gnr.GnrBag();
        this._dataroot.setItem('main', this._data);
        this.widget = {};
        this._counter = 0;
        this.dlg.createStandardMsg(document.body);
        this.contextIndex = {};
        this.isMac = dojo.isMac != undefined ? dojo.isMac : navigator.appVersion.indexOf('Macintosh') >= 0;
        this.isTouchDevice = ( (navigator.appVersion.indexOf('iPad') >= 0 ) || (navigator.appVersion.indexOf('iPhone') >= 0));
        this.isChrome = ( (navigator.appVersion.indexOf('Chrome') >= 0 ));
        //genro.timeIt('** getting main **');
        this.mainGenroWindow = window;
        this.root_page_id = null;
        if(this.startArgs['_parent_page_id']){
            this.parent_page_id = this.startArgs['_parent_page_id'];
        }
        if (window.frameElement && window.parent.genro){
            this.mainGenroWindow = window.parent.genro.mainGenroWindow;
            this.root_page_id = this.mainGenroWindow.genro.page_id;
            this.parent_page_id = this.parent_page_id || window.parent.genro.page_id;
            this.startArgs['_root_page_id'] = this.root_page_id;
            this.startArgs['_parent_page_id'] = this.parent_page_id;
        }
        var mainBagPage = this.rpc.remoteCall('main',this.startArgs, 'bag');
        if (mainBagPage  &&  mainBagPage.attr && mainBagPage.attr.redirect) {
            var pageUrl = this.absoluteUrl()
            if (pageUrl.slice(0,genro.baseUrl.length-1)==genro.baseUrl.slice(0,genro.baseUrl.length-1))
            {
                pageUrl = pageUrl.slice(genro.baseUrl.length-1) || '/';
            }
            var url = this.addParamsToUrl(mainBagPage.attr.redirect, {'fromPage':pageUrl});
            console.log('not logged',mainBagPage.attr.redirect, {'fromPage':pageUrl},url)
           // genro.currentUrl=mainBagPage.attr.redirect
            //var mainBagPage = this.rpc.remoteCall('main',this.startArgs, 'bag');
            //this.dostart(mainBagPage)
           this.gotoURL(url);
        }else{
            this.dostart(mainBagPage)
        }
    },
        
    dostart: function(mainBagPage) {
        //this.loadPersistentData()
        this.loadContext();
        //genro.timeIt('** starting builder **');
        this.src.startUp(mainBagPage);
        //genro.timeIt('** end builder **');
        genro.dom.removeClass('mainWindow', 'waiting');
        genro.dom.removeClass('_gnrRoot', 'notvisible');
        genro.dom.effect('_gnrRoot', 'fadein', {duration:400});
        dojo.connect(dojo.doc, 'onkeydown', function(event) {
              if ((event.keyCode == dojo.keys.BACKSPACE ) &&(event.target.size === undefined ) && (event.target.rows === undefined )){
                 event.preventDefault();
              }
        })
        genro.dragDropConnect();
        genro.standardEventConnection();
        if(genro.isDeveloper){
            genro.dom.addClass(dojo.body(),'isDeveloper');
            genro.dev.inspectConnect();
        }
        if(this.startArgs.workInProgress){
            genro.dom.addClass(dojo.body(),'workInProgress');
        }
        var _this = this;
        this._dataroot.subscribe('dataTriggers', {'any':dojo.hitch(this, "dataTrigger")});
        dojo.subscribe('ping',genro.ping);
        
        genro.dev.shortcut("Ctrl+Shift+D", function() {
            genro.dev.showDebugger();
        });

        genro.dev.shortcut("Shift+space", function(e) {
            var sn = dijit.getEnclosingWidget(e.target).sourceNode;
            if('_lastSavedValue' in sn){
                if(sn.form && sn.form.isNewRecord() && isNullOrBlank(sn.widget.getValue())){
                    sn.widget.setValue(sn._lastSavedValue,false);
                }
            }
        });
        genro.setDefaultShortcut();
        dojo.subscribe("setWindowTitle",function(title){genro.dom.windowTitle(title);});
        genro.setData('gnr.debugger.debug_sql',this.debug_sql);
        genro.setData('gnr.debugger.debug_py',this.debug_py);
        this._registerUserEvents();
        if(!this.root_page_id){
            this.setAutoPolling();
        }
        dojo.subscribe('/dnd/move/start',function(mover){
            mover.page_id = genro.page_id;
            genro.mainGenroWindow.genro.currentDnDMover=mover;
        });
        dojo.connect(window, 'onmouseup', function(e){
            var currentDnDMover = genro.mainGenroWindow.genro.currentDnDMover;
            if(currentDnDMover && (currentDnDMover.page_id != genro.page_id)){
                genro.mainGenroWindow.genro.currentDnDMover = null;
                currentDnDMover.events = currentDnDMover.events || [];
                currentDnDMover.destroy();
            }
            var currentResizeHandle = genro.mainGenroWindow.genro.currentResizeHandle;
            if(currentResizeHandle && (currentResizeHandle.page_id!=genro.page_id)){
                currentResizeHandle._endSizing(e);
            }
        });
        dojo.connect(window,'onmousemove',function(e){
            var currentResizeHandle = genro.mainGenroWindow.genro.currentResizeHandle;
            if(currentResizeHandle && (currentResizeHandle.page_id!=genro.page_id)){
                var screeStartPoint = currentResizeHandle.screenStartPoint;
                var startPoint = currentResizeHandle.startPoint;
                e.clientX = startPoint.x + e.screenX -screeStartPoint.x;
                e.clientY = startPoint.y + e.screenY -screeStartPoint.y;
                currentResizeHandle._updateSizing(e);
            }
        });
        this.windowStartHeight = window.outerHeight;
        this.windowStartWidth = window.outerWidth;

        //dojo.connect(window,'onresize',function(e){
        //    dojo.body().style.zoom = (window.outerHeight/genro.windowStartHeight + window.outerWidth/genro.windowStartWidth)/2;
        //    console.log('window resize',e,window.outerHeight,window.outerWidth);
        //});



        //genro.dom.preventGestureBackForward();
        if (this.isTouchDevice) {
            genro.dom.startTouchDevice();
        }
        genro.callAfter(function() {
            if(genro.root_page_id){
                genro._connectToParentIframe(window.frameElement);
            }
            genro.windowMessageListener();
            genro.fireEvent('gnr.onStart');
            genro.publish('onPageStart');
            genro._pageStarted = true;
        }, 100);
    },
    
    parentFrameNode:function(){
        return window.frameElement?window.frameElement.sourceNode:null;
    },

    setFastPolling:function(fast){
        this.fast_polling = fast;
        this.setAutoPolling(fast);
    },

    setAutoPolling:function(fast){
        var delay = fast? 2 : genro.auto_polling;
        if(genro.auto_polling_handler){
            clearInterval(genro.auto_polling_handler)
        }
        genro.dom.removeClass('mainWindow','fast_polling');
        genro.auto_polling_handler = setInterval(function(){
                if ((new Date() - genro.lastPing) / 1000 > genro.user_polling) {
                    genro.rpc.ping({'reason':'auto'});
                }
            },delay*1000);

        if(delay<genro.auto_polling){
            genro.dom.addClass('mainWindow','fast_polling');
            var limiter = function(){
                genro.fast_polling_limiter = setTimeout(function(){
                    var ts = new Date();
                    genro.fast_polling_limiter = null;
                    var evtage =(ts-genro._lastGlobalUserEventTs)/1000;
                    if(evtage>genro.user_polling){
                        genro.setAutoPolling();
                    }else{
                        limiter();
                    }
                },genro.user_polling*10000);
            }
            limiter();
        }
    },


    windowMessageListener:function(){
        window.addEventListener("message", function(e){
                if(e.data){
                    var kw = objectUpdate({},e.data);
                    var topic = objectPop(kw,'topic') || 'windowMessage';
                    genro.publish(topic,kw);
                }
            }, false);
        window._windowMessageReady = true;
    },

    setDefaultShortcut:function(){
        genro.dev.shortcut('f1', function(e) {
            if(genro.activeForm){
                genro.activeForm.save();
            }
        });
        genro.dev.shortcut('f3', function(e) {
            genro.publish('PRINTRECORD', e);
        });
    },


    tooltipHelpModifier:function(value){
        if(value){
            this.setInStorage('local','tooltipHelpModifier',value);
        }else{
            return this.getFromStorage('local','tooltipHelpModifier');
        }
    },
    
    _connectToParentIframe:function(parentIframe){
        var parentGenroData = window.parent.genro._data;
        genro._data.setCallBackItem('_frames._parent',
            function(){
                return parentGenroData;
            },null,{isGetter:true});
        var parentIframeSourceNode = parentIframe.sourceNode;
        var frameName = parentIframeSourceNode.attr.frameName;
        if(frameName){
            var currentData = genro._data;
            parentGenroData.setCallBackItem('_frames.'+frameName,function(){
                return currentData;
            });
        }            
        parentIframeSourceNode._genro = this;
        parentIframeSourceNode.publish('pageStarted');
    },
    
    getChildFramePage:function(page_id){
        var result;
        var cb = function(f,r){
            if (f.genro){
                if(f.genro.page_id==page_id){
                    return f;
                }
                return f.genro.getChildFramePage(page_id);
            }
        };
        for (var i=0;i<window.frames.length; i++){
            result = cb(window.frames[i]);
            if(result){
                break;
            }
        }
        return result;
    },
    getValueFromFrame: function(object_name, attribute_name, dtype){
        return asTypedTxt(window[object_name][attribute_name],dtype);
    },

    getServerLastTs:function(){
        return asTypedTxt(new Date(genro._lastUserEventTs.getTime()+(genro.serverTimeDelta || 0)),'DH')
    },

    getServerLastRpc:function(){
        return asTypedTxt(new Date(genro._lastRpc.getTime()+(genro.serverTimeDelta || 0)),'DH')
    },

    getTimeProfilers:function(){
        return dojo.toJson(this.timeProfilers);
    },

    getChildrenInfo:function(result){
        var result = result ||  {};
        var cb = function(f,r){
            if (f.genro){
                var kw = {_lastUserEventTs:f.genro.getServerLastTs(),_pageProfilers:f.genro.getTimeProfilers(),_lastRpc:f.genro.getServerLastRpc()};
                r[f.genro.page_id] = objectUpdate(kw,f.genro._serverstore_changes);
                f.genro._serverstore_changes = null;
                f.genro.getChildrenInfo(r);
            }
        };
        dojo.forEach(window.frames,function(f){
            try{
                cb(f,result);
            }catch(e){
                //console.log('external iframe detected: error ',e);
            }
        });
        return objectUpdate({},result);
    },
    
    dragDropConnect:function(pane) {
        var pane = pane || dojo.body();
        dojo.connect(pane, 'dragstart', genro.dom, 'onDragStart');
        dojo.connect(pane, 'dragend', genro.dom, 'onDragEnd');
        dojo.connect(pane, 'dragover', genro.dom, 'onDragOver');
        dojo.connect(pane, 'drop', genro.dom, 'onDrop');
    },
    setLastSelection:function(focusNode){

        try{
            if (focusNode.selection || focusNode.selectionStart || focusNode.selectionEnd){
                genro._lastSelection = {domNode:focusNode,start:focusNode.selectionStart,end:focusNode.selectionEnd};
            }else{
                genro._lastSelection = {};
            }
        }catch(e){
            genro._lastSelection = {};
        }

    },
    
    setCurrentFocused:function(wdg){
        var sourceNode = wdg.sourceNode;
        var destform = sourceNode.form;
        var changedForm = destform!=genro.activeForm;
         if(changedForm){
            if(genro.activeForm){
                genro.activeForm.onBlurForm();
            }
            genro.activeForm = destform;
        }
        if(genro.activeForm){
            genro.activeForm.onFocusElement(wdg);
            if(changedForm){
                destform.onFocusForm();
            }
        }
    },

    standardEventConnection:function(pane){
        var pane = pane || genro.domById('mainWindow');
        if(this.isDeveloper){
            dojo.connect(dojo.body(),'onmouseover',function(e){
                if(e.shiftKey && e.altKey){
                    var sn = genro.getSourceNode(e);
                    if(sn){
                        console.log(sn.absDatapath());
                    }
                }
            });
        }
    },
    playUrl:function(url,onEnd){
        var sound = new Audio(url);
        if(onEnd){
            sound.addEventListener('ended', function() {
                onEnd.call();
            }, false);
        }
        sound.play();
    },
    
    playSound:function(name, path, ext) {
        if(name.indexOf('$')==0){
            var name = genro.userPreference('sys.sounds.'+name.slice(1));
            if(!name){
                return;
            }
        }
        if (!(name in genro.sounds)) {
            var path = path || '/_gnr/11/sounds/';
            var ext = ext || 'wav';
            genro.sounds[name] = new Audio(path + name + '.' + ext);
        }
        genro.sounds[name].play();
    },
    setInServer: function(path, value, pageId) {
        genro.rpc.remoteCall('setInServer', {path:path, value:value,pageId:pageId});
    },
    loadContext:function() {
        var contextBag = new gnr.GnrBag();
        var cookie = dojo.cookie("genroContext");
        if (cookie) {
            var cookiestring = genro.dom.parseXmlString(cookie);
            contextBag.fromXmlDoc(cookiestring);
        }
        genro.setData('_clientCtx', contextBag);
        genro.publish('onCookieLoaded');
    },
    fireEvent: function(path, msg) {
        msg = (msg != null) ? msg : true;
        var path = genro.src.getNode().absDatapath(path);
        genro._data.setItem(path, msg);
        genro._data.setItem(path, null, null, {'doTrigger':false});
    },
    test:function(v) {
        console.log(v);
    },
    resizeAll: function() {
        genro.wdgById('_gnrRoot').resize();
        //window.resizeBy(1,1);
        //window.resizeBy(-1,-1);

        //setTimeout(dojo.hitch(genro.wdgById('pbl_root'), 'resize'), 100);
    },
    callAfter: function(cb, timeout, scope,reason) {
        scope = scope || genro;
        cb = funcCreate(cb);
        if (reason){
            if (this.pendingCallAfter[reason]){
                clearTimeout(this.pendingCallAfter[reason]);
            }
             this.pendingCallAfter[reason] = setTimeout(dojo.hitch(scope, cb), timeout);
        }
        else{
            setTimeout(dojo.hitch(scope, cb), timeout);
        }
    },
    
    fireAfter: function(path, msg, timeout) {
        var timeout = timeout || 1;
        var _path = path;
        var _msg = msg;
        if (this.pendingCallAfter[path]) {
            clearTimeout(this.pendingCallAfter[path]);
        }
        this.pendingCallAfter[path] = setTimeout(function() {
            genro.fireEvent(_path, _msg);
        }, timeout);
    },
    setDataAfter: function(path, value, timeout) {
        setTimeout(function() {
            genro.setData(path, value);
        }, timeout || 1);
    },

    sendMouseEvent:function(target, evtstr, delay) {
        var delay = delay || 100;
        var evtstr = evtstr || 'click';
        var cb = dojo.hitch(target, function() {
            var newevt = document.createEvent("MouseEvents");
            newevt.initMouseEvent(evtstr, true, true, window,
                    0, 0, 0, 0, 0, false, false, false, false, 0, null);
            this.dispatchEvent(newevt);
        });
        setTimeout(cb, 100);
    },

    getPref: function(prefname, pars) {
        if (pars) {
            return templateReplace(genro.prefs[prefname], pars);
        } else {
            return genro.prefs[prefname];
        }
    },

    userPreference:function(pref){
        return genro._('gnr.user_preference.'+pref);
    },

    appPreference:function(pref){
        return genro._('gnr.app_preference.'+pref);
    },

    setUserPreference:function(path,data,pkg){
        genro.serverCall('setUserPreference',{path:path,data:data,pkg:pkg});
    },

    setAppPreference:function(path,data){
        genro.serverCall('setPreference',{path:path,data:data,pkg:pkg});
    },

    chat:function(){
        return this.mainGenroWindow.ct_chat_utils;
    },
    format: function (v, f, m) {
        if( f.dtype=='P'){
            return genro.formatter.asText(v,{dtype:'P',format:f.format.format,mask:f.mask});
        }
        if (v instanceof Date) {
            var opt = objectUpdate({}, f);
            if (opt['time']) {
                opt.selector = 'time';
                opt.formatLength = opt['time'];
            }
            else if (opt['datetime']) {
                opt.selector = 'datetime';
                opt.formatLength = opt['datetime'];
            } else {
                opt.selector = 'date';
                opt.formatLength = opt['date'];

            }
            v = dojo.date.locale.format(v, opt);
        }
        else if (typeof(v) == 'number') {
            f.locale = f.locale || dojo.locale;
            if(f.format && f.format.format!=null){
                return genro.formatter.asText(v,{format:f.format.format,format_max:f.max,format_min:f.min,format_high:f.high,format_low:f.low,format_optimal:f.optimal});
            }
            if (!f.places && f.dtype == 'L') {
                f.places = 0;
            }
            if (!f.pattern && f.places == 0) {
                f.pattern = '##########';
            }
            if (!f.currency){
                v = stringStrip(dojo.number.format(v, f));
            }
            else
            {
                v = stringStrip(dojo.currency.format(v, f));
            }
        }else if(v instanceof Array){
            if(f['joiner']){
                v = v.join(f['joiner']);
            }
        }else if (v && f.dtype=='X'){
            var b = new gnr.GnrBag();
            try{
                var parser = new DOMParser();
                var xmlDoc = parser.parseFromString(v,"text/xml");
                b.fromXmlDoc(xmlDoc,genro.clsdict);
                if(b.keys().length>0){
                    v = genro.formatter.asText(b,objectUpdate({format:objectExtract(f,'bag_*',true)}) );
                }else{
                    v='';
                }
            }catch(e){
                v = '';
            }
        }
        else if (typeof(v) == 'boolean' || f.dtype == 'B') {
            var divcontent,divclass;
            var falsecontent = f['false'] || (f['falseclass'] ? '' : 'false');
            var truecontent =(f['true'] || (f['trueclass'] ? '' : 'true'));
            var trueclass = (f['trueclass'] ? f['trueclass'] : '');
            var falseclass = (f['falseclass'] ? f['falseclass'] : '');
            if (f['nullclass'] || f['null']){
                var nullclass = (f['nullclass'] ? f['nullclass'] : '');
                var nullcontent =(f['null'] || (f['nullclass'] ? '' : 'null'));
                divcontent = (v===true)?truecontent:(v===false)?falsecontent:nullcontent;
                divclass = (v===true)?trueclass:(v===false)?falseclass:nullclass;
            }else{
                divcontent = v ? truecontent : falsecontent;
                divclass = v ? trueclass:falseclass;
            }
            
            divclass = (divclass&&!divcontent) ? 'class="' + divclass + '"' : '';
            var event_attrs = '';
            var events = objectExtract(f, 'on*', true);
            if (events) {
                for (var event_type in events) {
                    var cellPars = f['cellPars'] || {};
                    var jsCode = "genro.src.onEventCall(event,'" + escapeLiterals(events[event_type]) + "'," + serialize(cellPars) + ");";
                    event_attrs += " on" + event_type + '="' + cleanJsCode(jsCode) + '"';
                }
            }
            v = "<div " + event_attrs + " style='margin:auto;' " + divclass + ">" + divcontent + "</div>";
        }
        // area passibile di modifiche
        if (f['apply']) {
            var cb = funcCreate(f['apply'], 'value');
            v = cb.apply(window, [v]);
        }
        else if (!v) {
            if (f['isbutton']) {
                var divclass = f['buttonclass'];
                divclass = divclass ? 'class="' + divclass + '"' : '';
                var event_attrs = '';
                var events = objectExtract(f, 'on*', true);
                var title = f['tip'] || '';
                var label = typeof(f['isbutton'])=='string'?f['isbutton']:'&nbsp;';
                if (events) {
                    for (var event_type in events) {
                        var cellPars = f['cellPars'] || {};
                        var jsCode = "genro.src.onEventCall(event,'" + escapeLiterals(events[event_type]) + "'," + serialize(cellPars) + ");";
                        event_attrs += " on" + event_type + '="' + cleanJsCode(jsCode) + '"';
                    }
                }
                v = "<div title='"+title+"'" + event_attrs + " style='margin:auto;' " + divclass + ">" + label + "</div>";
            }
            else if (f['inlineedit'] == true) {
                v = "<span style='font-family: wingdings; text-decoration: underline;'>&nbsp;&nbsp;&nbsp;&nbsp;&#x270d;&nbsp;&nbsp;&nbsp;&nbsp;</span>";
            }

        }
        // fine area passibile di modifiche
        if(f['showlinks'] && v){
            if (v instanceof Array){
                v=v.join(f['joiner'] || ',')
            }
            v = highlightLinks(v);
        }
        if(f.format){
            v = genro.formatter.asText(v,{format:f.format.format,mask:f.mask});
        }
        return v;
    },
    setdebug:function(topic, level) {
        if (!topic && this.debugtopics) {
            delete this.debugtopics;
        } else {
            if (!this.debugtopics) {
                this.debugtopics = {};
            }
            this.debugtopics[topic] = level || 'console';
        }
    },

    debug: function(msg, debuglevel, topic) {
        if (this.debugtopics) {
            var debuglevel = this.debugtopics[topic];
        } else {
            var debuglevel = debuglevel || this.debuglevel;
        }
        if (debuglevel == 'console') {
            console.debug((new Date()) + msg);
        }
        else if (debuglevel == 'alert') {
            alert(msg);
        }
    },
    log: function(source,reason){
        var logpath = 'gnr._dev.logger';
        reason = reason?'\n-----------------\n'+reason+'\n-----------------':'';
        var log = genro.getData(logpath)+reason+'\n'+source;
        genro.setData(logpath,log);
    },
    
    clearlog:function(){
        genro.setData('gnr._dev.logger','');
    },

    isLocalPageId:function(page_id){
        if(page_id==genro.page_id){
            return true;
        }
        return dojo.some(window.frames,function(f){return f.genro?f.genro.page_id==page_id:false});
    },



    getCounter: function(what,reset) {
        what = what?'_counter_'+what:'_counter';
        if(reset==true){
            this[what] = 0;
        }else{
            this[what] = (this[what] || 0)+1;
        }
        return this[what];
    },

    
    bagToTable:function(kwargs/*path,columns,key*/) {
        /*
         Transforms a bag in a table bag with headers, columns and rows.
         Each table's row is composed by a bag node, and columns are filled with its attributes.
         @param path: the source bag path in the datasource
         @param columns: a an array of couple like 'name:label'
         @param key: the name of the primary key column
         */
        var bag = genro.getData(kwargs.path);
        var result = new gnr.GnrBag();
        var columns = [];
        for (var i = 0; i < kwargs.columns.length; i++) {
            var col = kwargs.columns[i].split(':');
            result.setItem('headers.' + col[0], null, {label:col[1]});
            columns.push(col[0]);
        }
        var node;
        var tblId;
        for (var i = 0; i < bag.len(); i++) {
            node = bag.getNodes()[i];
            for (var j = 0; j < columns.length; j++) {
                if (columns[j] == kwargs.key) {
                    result.setItem('rows.' + node.label + '.' + columns[j], node.label);
                }
                else {
                    result.setItem('rows.' + node.label + '.' + columns[j], node.getAttr(columns[j]));
                }
            }
        }
        return result;
    },
    recordToPDF: function(table, pkey, template) {
        //var url = genro.rpc.rpcUrl("app.recordToPDF", {table:table, pkey:pkey, template:template});
        genro.download("", {table:table, pkey:pkey, template:template, method:"app.recordToPDF",mode:'text'});
    },
    rpcDownload: function(method, kwargs, onload_cb) {
        genro.download('', genro.rpc.getRpcUrlArgs(method, kwargs), onload_cb);

    },
    download: function(url, args, onload_cb) {
        var args = args || {};
        if (onload_cb == 'print') {
            onload_cb = "genro.dom.iFramePrint(this.domNode);";
        }
        else {
            args.download = true;
        }
        url = genro.makeUrl(url, args);
        genro.src.getNode()._('div', '_dlframe');
        var node = genro.src.getNode('_dlframe').clearValue().freeze();
        var params = {'src':url, display:'none', width:'0px', height:'0px'};
        if (onload_cb) {
            params['connect_onload'] = onload_cb;
        }
        ;
        frm = node._('htmliframe', params);
        node.unfreeze();


    },
    makeUrl: function(url, kwargs) {
        if (url.indexOf('://') == -1) {
            if (url.slice(0, 1) != '/') {
                var base = document.location.pathname;
                if (base==null || base=='/'){
                    base = '/index';
                }
                url = base + '/' + url;
            }
            ;
            url = document.location.protocol + '//' + document.location.host + url;
        }
        ;
        return genro.addKwargs(url, kwargs);
    },
    addKwargs: function(url, kwargs) {
        if (kwargs) {
            var currParams = {};
            var parameters = [];
            currParams['page_id'] = genro.page_id;
            currParams['_no_cache_'] = genro.getCounter();
            objectUpdate(currParams, kwargs);
            for (var key in currParams) {
                parameters.push(key + '=' + escape(currParams[key]));
            }
            url = url + '?' + parameters.join('&');
        } else {
            url = url + document.location.search;
        }
        return url;
    },
    _invalidNodes: function(databag, sourceNode) {
        if (typeof(databag) == 'string') {
            if (sourceNode) {
                databag = sourceNode.absDatapath(databag);
            }
            databag = genro.getData(databag);
        }
        return databag.invalidNodes('@');
    },
    dataValidate: function(databag, sourceNode) {
        var r = this._invalidNodes(databag, sourceNode);
        return (r.length == 0);
    },
    focusOnError: function(databag, sourceNode) {
        var invalidNodes = this._invalidNodes(databag, sourceNode);
        if (invalidNodes.length > 0) {
            var node = invalidNodes[0];
            var kw = {'evt':'invalid', 'node':node, 'pathlist':node.getFullpath().split('.')};
            dojo.publish('_trigger_data', [kw]);
        }
        return (invalidNodes.length == 0);
    },
    
    dataTrigger:function(kw) {
        if (kw.evt == 'upd' && kw.reason != 'serverChange') {
            var dpath = kw.pathlist.slice(1).join('.');
            for (var registered_path in genro._serverstore_paths){
                if(dpath.indexOf(registered_path)==0){
                    var inner=dpath.slice(registered_path.length);
                    if(!inner || inner[0]=='.'){
                        genro._serverstore_changes = genro._serverstore_changes || {};
                        genro._serverstore_changes[genro._serverstore_paths[registered_path]+inner] = asTypedTxt(kw.value);
                        break;
                    }
                }
            }
        }
        dojo.publish('_trigger_data', [kw]);
    },
    
    fireDataTrigger: function(path) {
        var node = genro.getDataNode(path);
        //var v=node.getValue();
        var kw = {'evt':'fired', 'node':node, 'pathlist':('main.' + path).split('.')};
        dojo.publish('_trigger_data', [kw]);
    },
    getSourceNode: function(obj) {
        return genro.src.getNode(obj);
    },

    pathResolve: function(obj) {
        if (!obj) {
            debugger;
        }
        if (typeof (obj) == 'string') {
            // return (obj.indexOf('@') ==0) ? obj.slice(1) : obj;
            if (!genro.src.getNode()) {
                return obj;
            }
            return genro.src.getNode().absDatapath(obj);
        }
        if (obj instanceof gnr.GnrDomSourceNode) {
            return obj.absDatapath();
        }
        if (obj.sourceNode) {// widget or domnode
            return obj.sourceNode.absDatapath();
        }

    },
    getDataNode: function(path, autocreate, dflt) {
        /*
         This method returns the databag node at passed path.
         If path is equal or starts with "*S" it takes the srcbag.
         */
        var path;
        if (path) {
            path = this.pathResolve(path);
            if (path) {
                if (stringStartsWith(path, '*S')) {
                    return genro.src.getNode(path.slice(3));
                }
                if (stringStartsWith(path, '*D')) {
                    path = path.slice(2);
                }
                if (path) {
                    return this._data.getNode(path, false, autocreate, dflt);
                } else {
                    return this._dataroot.getNode('main');
                }

            }
        }
    },
    getDataAttr:function(path, attr, dflt) {
        /*
         This method returns an attribute at given path from the databag
         */
        var node = this.getDataNode(path);
        if (node) {
            return node.getAttr(attr, dflt);
        }
    },

    getData:function(path, dflt, cb) {
        /*
         This method returns an the bag at given path from the databag
         */
        var dflt = (dflt != undefined) ? dflt : null;
        if (path) {
            var node = this.getDataNode(path);
            if (node) {
                var value = node.getValue();
                if (value == null) {
                    value = dflt;
                }
                return value;
            } else {
                return dflt;
            }
        } else {
            return this._data;
        }
    },
    _: function(path, dflt) {
        return genro.src.getNode().getRelativeData(path);
    },

    resetData: function(path) {
        var node = genro.getDataNode(path);
        if ('_loadedValue' in node.attr) {
            node.setValue(node.attr._loadedValue);
        }
    },
    copyData: function(path, sourcepath, changebackref) {
        /*
         Copy a datanode from a path to another one
         */
        var node = genro.getDataNode(sourcepath);
        var value = node.getValue();
        if (changebackref) {
            value.clearBackRef();
        }
        genro.setData(path, value, node.getAttr());

    },

    doCallback: function(cb, _this) {
        var obj;
        if (cb instanceof Function) {
            return cb;
        }
        else if ((typeof(cb) == 'string')) {
            cb = cb.split('.');
            if (cb[0] == 'this') {
                obj = _this;
                cb.pop(0);
            } else {
                var obj = window;
            }
            for (var i = 0; i < cb.length; i++) {
                obj = obj[cb[i]];
            }
            return obj;
        }
        else {// {obj:objectToCall, func:functionName}
            return cb.obj[cb.func];
        }
    },
    setData: function(path, value, attributes, doTrigger) {
        var path = genro.pathResolve(path);
        genro._data.setItem(path, value, attributes, {'_doTrigger': doTrigger});
    },

    setDataFromRemote:function(path, method, params, attributes) {
        /*Uguale a setData con l'attributo remote*/
        genro.setData(path, genro.rpc.remoteCall(method, params));
    },

    dataSubscribe:function(path, subscriberId, kwargs) {
        /*Set a trigger on databag at the given path with given subscriberId*/
        //perchè non usare direttamente genro.getData?
        var bag = genro.getData(path);
        if (bag instanceof dojo.Deferred) {
            return bag.addCallback(function(result) {
                return result.subscribe(subscriberId, kwargs);
            });
        } else {
            return genro.getData(path).subscribe(subscriberId, kwargs);
        }
    },
    dataNodeSubscribe:function(path, subscriberId, kwargs) {
        /*Set a trigger on databag at the given path with given subscriberId*/
        //perchè non usare direttamente genro.getDataNode?
        return genro.getDataNode(path).subscribe(subscriberId, kwargs);
    },

    subscribeEvent: function(object, eventname, obj, func) {
        //MISTERO
        /*add an event subscription
         @param object: objectId
         @param eventname*/
        var objId = object.widgetId;
        dojo.subscribe(objId + '/' + eventname, obj, func);
    },
    publish:function(topic,kw) {
        var args = [];  
        if(typeof(topic)=='string'){
            //console.log('publishing:'+topic,args);
            //console.log(args)
            for (var i = 1; i < arguments.length; i++) {
                args.push(arguments[i]);
            }
            dojo.publish(topic, args);
            return ;
        }
        var parent=topic['parent'];
        var iframe=topic['iframe'];
        var kw=topic['kw'] || kw;
        if('nodeId' in topic){
            var node= genro.nodeById(topic['nodeId']);
            if (node){
                node.publish(topic['topic'],kw);
            }
        }else if('form' in topic){
            var form=genro.getForm(topic['form']);
            if (form){
                form.publish(topic['topic'],kw);
            }
        }
        else{
            genro.publish(topic['topic'], kw);
        }

        if (iframe){
            var t=objectUpdate({},topic);
            objectPop(t,'parent');
            if (iframe=='*'){
                dojo.forEach(window.frames,function(f){
                    try{
                        if (f.genro){
                            f.genro.publish(t,kw);
                        }
                    }catch(e){

                    }
                });
            }else{
                var iframeNode=genro.domById(iframe);
                if(iframeNode){
                    var f =iframeNode.contentWindow;
                    if(f && f.genro){
                        f.genro.publish(t,kw);
                    }
                }
            }     
        }
        
        if(parent && (window.parent!=window) && window.parent.genro ){
            var t=objectUpdate({},topic);
            objectPop(t,'iframe');
            objectPop(t,'parent');
            window.parent.genro.publish(t,kw);
        }
    },

    absoluteUrl: function(url, kwargs, avoidCache) {
        var base = document.location.pathname;
        var avoidCache = avoidCache === false ? false : true;
        if (url) {
            var sep = url.slice(0, 1) == '?' ? '' : '/';
            url = base + sep + url;
        }
        else {
            url = base;
        }
        if (kwargs) {
            var currParams = {};
            currParams['page_id'] = genro.page_id;
            if (avoidCache != false) {
                currParams['_no_cache_'] = genro.getCounter();
            }
            objectUpdate(currParams, kwargs);
            var parameters = [];
            for (var key in currParams) {
                parameters.push(key + '=' + escape(currParams[key]));
            }


            url = url + '?' + parameters.join('&');
        } else {
            url = url + document.location.search;
        }
        return url;
    },


    setInStorage:function(sessionType, key, value) {
        var sessionType = sessionType || 'session';
        var storage = (sessionType == 'local') ? localStorage : sessionStorage;
        storage.setItem(key, asTypedTxt(value));
        //console.log('Stored in ' + sessionType + 'Storage at key:' + key + '  value:' + value);
    },
    getFromStorage:function(sessionType, key) {
        var sessionType = sessionType || 'session';
        var storage = (sessionType == 'local') ? localStorage : sessionStorage;
        var value = storage.getItem(key);
        /*if (value) {
            //console.log('Loaded from '+sessionType+'Storage at key:'+key+'  value:'+value);
        } else {
            //console.log('Not existing in '+sessionType+'Storage key:'+key);
        }*/
        return convertFromText(value);
    },


    addParamsToUrl: function(url, params) {
        if(!objectNotEmpty(params)){
            return url;
        }
        var parameters = [];
        for (var key in params) {
            if(params[key]!==null){
                parameters.push(key + '=' + encodeURIComponent(params[key]));
            }
        }
        var sep = (url.indexOf('?') != -1) ? '&' : '?';
        return url + sep + parameters.join('&');
    },
    getFormChanges: function(formId) {
        var fh = genro.formById(formId);
        if (fh) {
            return fh.getFormChanges();
        }
    },
    getFormData: function(formId) {
        var fh = genro.formById(formId);
        if (fh) {
            return fh.getFormData();
        }
    },
    getFormCluster: function(formId) {
        var fh = genro.formById(formId);
        if (fh) {
            return fh.getFormCluster();
        }
    },
    getForm:function(frameCode){
        var frameNode = genro.getFrameNode(frameCode);
        return frameNode?frameNode.form:genro.formById(frameCode);
    },
    
    getStore:function(storeCode){
        return genro.nodeById(storeCode+'_store').store;
    },
    
    getFrameNode:function(frameCode,side){
        var frameNode = genro.nodeById(frameCode+'_frame');
        if(!frameNode){
            return;
        }
        if(side=='frame'){
            return frameNode;
        }
        var containerNode =  frameNode.getValue().getNodes()[0];
        if(!side){
            return containerNode;
        }

        return containerNode.getValue().getNodeByAttr('region',side);
    },
    formById:function(formId) {
        var node = genro.nodeById(formId);
        if (node) {
            return node.form;
        }
    },
    nodeById:function(nodeId,scope) {
        var childpath,node;
        if(nodeId[0]=='/'){
            childpath = nodeId.slice(1);
            if(scope.attr.nodeId){
                node=scope;
            }else{
                if(scope.attr._childname){
                    childpath = scope.attr._childname+'/'+childpath;
                }
                node = scope.getParentNode();
                while(node && !node.attr.nodeId){
                    if(node.attr._childname){
                        childpath = node.attr._childname+'/'+childpath;
                    }                    
                    node = node.getParentNode();            
                }
            }
        }
        else{
            if(nodeId.indexOf('/')>=0){
                childpath=nodeId.split('/');
                nodeId=childpath[0];
                childpath = childpath.slice(1).join('/');
            }
            if(nodeId.indexOf('FORM')==0){
                node=scope.attributeOwnerNode('formId,_fakeform') || scope.getParentNode();
            }else if(nodeId.indexOf('ANCHOR')==0){
                node=scope.attributeOwnerNode('_anchor') || scope.getParentNode();
            }
        }
        var node =node || genro.src._index[nodeId];
        if (!node && genro.src.building) {
            node = genro.src._main.getNodeByAttr('nodeId', nodeId);
        }
        
        return childpath?node.getChild(childpath):node;
    },
    
    domById:function(nodeId,scope) {
        var node = this.nodeById(nodeId,scope);
        if (node) {
            return node.getDomNode();
        } else {
            return dojo.byId(nodeId);
        }
    },
    wdgById:function(nodeId,scope) {
        var node = this.nodeById(nodeId,scope);
        if (node) {
            return node.getWidget();
        }
    },
    byId: function(id) {
        var obj = dojo.widget.byId(id);
        if (obj == null) {
            obj = dojo.byId(id);
        }
        return obj;
    },
    remoteUrl: function(method, args, sourceNode, avoidCache) {
        return genro.rpc.rpcUrl(method, args, sourceNode, avoidCache);
    },
    setUrlRemote: function(widget, method, args) {
        var url = genro.rpc.rpcUrl(method, args);
        widget.setHref(url);
    },
    setLocStatus:function(status) {
        if ((status == 'missingLoc') || (! genro.getData('gnr.localizerStatus'))) {
            genro.setData('gnr.localizerStatus', status);
        }
    },
    setUrl: function(widget, url) {
        widget.setUrl(url);
    },
    gotoURL:function(url, relative) {
        if (relative) {
            url = genro.constructUrl(url);
        } else {
            url = genro.joinPath(genro.getData('gnr.homeUrl') || '', url);
        }
        window.location.assign(url);
    },
    joinPath:function() {
        var result = arguments[0];
        var i;
        for (i = 1; i < arguments.length; i++) {
            var p = arguments[i];
            if (result.substr(-1) != "/") {
                result += "/";
            }
            if (p.substr(0, 1) == "/") {
                p = p.substr(1);
            }
            result += p;
        }
        return result;
    },
    /*joinPath: function() {
     return arguments.join('/').replace(/\/+/g,'/');
     },*/ //arguments.join is not a function!
    gotoHome:function() {
        window.location.assign(genro.getData('gnr.homepage'));
    },
    webcalUrl:function(path, params) {
        console.log(path);
    },

    constructUrl:function(path, params) {
        var url = genro.getData('gnr.homeFolder') + path;
        if (params) {
            var parameters = [];
            for (var key in params) {
                parameters.push(key + '=' + encodeURIComponent(params[key]));
            }
            url = url + '?' + parameters.join('&');
        }
        ;
        return url;

    },
    logout:function() {
        genro.lockScreen(true,'logout');
        this.serverCall('connection.logout', null, 'genro.gotoHome();');
    },
    remoteJson:function(method, params) {
        return genro.rpc.remoteCall(method, params, 'json');
    },
    serverCall:function(method, params, async_cb, mode,httpMethod) {
        var cb = funcCreate(async_cb);
        var httpMethod = httpMethod || 'POST';
        return genro.rpc.remoteCall(method, params, mode, httpMethod, null, cb);
    },
    
    makeDeferred:function(cb){
        var deferred = new dojo.Deferred();
        setTimeout(function(){deferred.callback(cb());},1);
        return deferred;
    },
    
    setSelectedVal:function(obj, value) {
        /*Set the attr selectedValue*/
        var dataNode = genro.getDataNode(obj.sourceNode);
        dataNode.setAttr({'selectedValue':value});
    },
    evaluate:function(expr,showError) {
        try {
            var toEval = 'genro.auxresult=(' + expr + ')';
            dojo.eval(toEval);
            return genro.auxresult;
        } catch(e) {
            var showError = showError===false?false:true;
            if ((console != undefined) && showError) {
                console.log('genro.evaluate() failed:');
                console.log(expr);
                console.log(e);
            }
            throw e;
        }
    },
    isEqual:function(a, b) {
        var a = a instanceof Date ? a.valueOf() : a;
        var b = b instanceof Date ? b.valueOf() : b;
        return a == b;
    },
    connect: function(target, funcName, objToConnect) {
        if (typeof objToConnect == 'function') {
            dojo.connect(target, funcName, objToConnect);
        } else {
            dojo.connect(target, funcName, objToConnect['obj'], objToConnect['func']);
        }
    },

    call: function(objToCall) {
        if (typeof objToCall == 'function') {
            objToCall.apply(null, arguments);
        } else {
            objToCall['obj'][objToConnect['func']].apply(objToCall['obj'], arguments);
        }
    },

    pageReload:function(params,replaceParams) {
        if (params) {
            if (!replaceParams){
                var oldparams = parseURL(window.location)['params'] || {};
                params = objectUpdate(params || {},oldparams);
            }
            if (objectNotEmpty(params)) {
                params['_no_cache_'] = genro.getCounter();
                var plist = [];
                for (k in params) {
                    plist.push(k + '=' + encodeURIComponent(params[k]));
                }
                window.location.search = plist.join('&');
            } else {
                window.location.search = '';
            }
        } else {
            window.location.reload();
        }
    },

    pageBack:function() {
        window.history.back();
    },
    goBack:function() {
        var pathlist = window.location.pathname.split('/');
        if (pathlist.slice(-1) != '') {
            window.location.pathname = pathlist.slice(0, -1).join('/');
        } else {
            window.location.pathname = pathlist.slice(0, -2).join('/');
        }

    },
    getSource:function(item) {
        return item.sourceNode.getValue();
    },
    viewPDF: function(filename, forcedownload) {
        var url = genro.rpc.rpcUrl("app.downloadPDF", {filename:filename, forcedownload:forcedownload});
        if (forcedownload) {
            genro.dev.exportUrl(url);
        } else {
            genro.openWindow(url, filename);

        }
    },
    openWindow:function(url, name, params) {
        params = params || {height:'700',width:'800'};
        if (params) {
            if (typeof(params) != 'string') {
                parlist = [];
                for (var par in params) {
                    parlist.push(par + '=' + params[par]);
                }
                params = parlist.join(',');
            }
        }
        var newwindow = window.open(url, name, params);
        if (window.focus) {
            newwindow.focus();
        }
    },
    openBrowserTab:function(url){
        window.open(url)
    },
    
    childBrowserTab:function(url,parent_page_id){
        window.open(genro.addParamsToUrl(url,{_parent_page_id:(parent_page_id || genro.page_id)}))
    },
    

    dynamicDataProvider:function(table, columns, where, params) {
        var method = 'app.getSelection';
        var cacheTime = -1;
        var isGetter = true;
        var attributes = {'sync':true,
            'table':table,
            'columns':columns,
            'where':where,
            'recordResolver':false,
            'selectionName':'grid_' + table.replace(/\./g, '_')};
        attributes = objectUpdate(attributes, params);
        return genro.rpc.remoteResolver(method, attributes, {'cacheTime':cacheTime,'isGetter':isGetter});
    },
    getRelationResolver: function(params, resolverName, parentbag) {
        params = objectUpdate({}, params);
        var resolverName = resolverName || objectPop(params, '_resolver_name');
        var resolver = genro.rpc['remote_' + resolverName];
        if (resolver){
            return resolver.call(genro.rpc, params, parentbag);
        }
            
    },
    loadUserObject: function(path, params) {
        var result = genro.rpc.remoteCall('app.loadUserObject', {'id': params['id'],
            'code': params['code'],
            'objtype': params.objtype,
            'userid': params.userid,
            'table': params.table
        },
                null, 'GET').getValue();
        genro.setData(path, result.getItem('userobject'), result.getAttr('userobject'));
    },
    saveUserObject: function(path) {
        var userobjectnode = genro.getDataNode(path);
        var userobjectbag = new gnr.GnrBag();
        userobjectbag.setItem('userobject', userobjectnode.getValue(), userobjectnode.getAttr());
        genro.rpc.remoteCall('app.saveUserObject', {'userobject': userobjectbag},
                null, 'POST');
    },
    deleteUserObject: function(path) {
        var qnode = genro.getDataNode(path);
        var pkey = qnode.getAttr('id');
        if (pkey) {
            genro.rpc.remoteCall('app.deleteUserObject', {'pkey': pkey}, null, 'GET');
        }
        objectPopAll(qnode.attr);
        qnode.setValue(new gnr.GnrBag());
    },
    PATCHED_KEYS: {
        LEFT_ARROW: 37,
        UP_ARROW: 38,
        RIGHT_ARROW: 39,
        DOWN_ARROW: 40,
        TAB: 9,
        SHIFT: 16,
        CTRL: 17,
        ALT: 18,
        ESCAPE: 27,
        ENTER: 13
    },
    //forms functions
    formInfo: function(name) {
        var name = name || 'formPane';
        var controllerPath = genro.formById(name).controllerPath;
        return genro._(controllerPath);
    },

    invalidFields: function(name) {
        return genro.formInfo(name).getItem('invalidFields');
    },
    google:function(){
        if(! this._googleHandler){
            this._googleHandler=this.wdg.getHandler('GoogleLoader')
        } 
        return this._googleHandler;  
    },

    lockScreen:function(locking, reason, options) {
        if (reason) {
            genro.lockingElements[reason] = reason;
        }
        if (locking) {
            if (!reason) {
                return;
            }
            genro.nodeById('_gnrRoot').setHiderLayer(true,{message:'<div class="form_waiting"></div>',z_index:999998});
        } else {
            if (reason) {
                objectPop(genro.lockingElements, reason);
            } else {
                genro.lockingElements = {};
            }
            if (!objectNotEmpty(genro.lockingElements)) {
                genro.nodeById('_gnrRoot').setHiderLayer(false);
            }
        }
    }
});

dojo.declare("gnr.GnrClientCaller", gnr.GnrBagResolver, {
    constructor: function(kwargs/*callback, params*/) {
        if (typeof kwargs.callback == 'string') {
            this.callback = genro.evaluate(kwargs.callback);
        } else {
            this.callback = kwargs.callback;
        }


        if (typeof kwargs.params == 'string') {
            this.evaluate = 'this.params = ' + kwargs.params;
            this.params = {};
        } else {
            this.evaluate = null;
            this.params = kwargs.params;
        }
    },

    load: function (kwargs) {
        if (this.evaluate) {
            genro.evaluate(this.evaluate);
        }
        if (kwargs) {
            objectUpdate(this.params, kwargs);
        }
        if (this.callback instanceof Function) {
            return this.callback(this.params);
        }
        else {
            return this.callback.obj[this.callback.func](this.params);
        }
    }
});

