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
/*String.prototype.startswith=function(start_string){
 len=start_string.length;
 if (this.slice(0,len)==start_string){
 return true
 }
 else
 {
 return false;
 }
 };*/

/* ----------- Class gnr.GenroClient ----------------*/
dojo.declare('gnr.GenroClient', null, {

    constructor: function(kwargs) {
        this.domRootName = kwargs.domRootName || 'mainWindow';
        this.page_id = kwargs.page_id;
        this.startArgs = kwargs.startArgs || {};
        this.debuglevel = kwargs.startArgs.debug || null;
        this.debugopt = kwargs.startArgs.debugopt || null;
        this.pageMode = kwargs.pageMode;
        this.baseUrl = kwargs.baseUrl;
        this.lockingElements = {};
        this.debugRpc = false;
        this.isDeveloper = this.startArgs.isDeveloper;
        setTimeout(dojo.hitch(this, 'genroInit'), 1);
    },
    genroInit:function() {
        this.startTime = new Date();
        this.lastTime = this.startTime;
        this.dialogStack = [];
        this.sounds = {};

        this._serverstore_paths = {};
        this._serverstore_changes = null;
        this.pendingFireAfter = {};
        var plugins = objectExtract(window, 'genro_plugin_*');
        objectUpdate(genro, plugins);
        this.compareDict = {'==':function(a, b) {
            return (a == b);
        },
            '>':function(a, b) {
                return (a > b);
            },
            '>=':function(a, b) {
                return (a >= b);
            },
            '<':function(a, b) {
                return (a < b);
            },
            '<=':function(a, b) {
                return (a <= b);
            },
            '!=':function(a, b) {
                return (a != b);
            },
            '%':function(a, b) {
                return (a.indexOf(b) >= 0);
            },
            '!%':function(a, b) {
                return (a.indexOf(b) < 0);
            }
        };
        window.onbeforeunload = function(e) {
            var exit;
            if (genro.checkBeforeUnload) {
                exit = genro.checkBeforeUnload();
            }
            if (exit) {
                return exit;
            }
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


        if (dojo_version == '1.1') {
            if (dojo.isSafari) {
                dojo.keys.DOWN_ARROW = 40;
                dojo.keys.UP_ARROW = 38;
            }
            genropatches.borderContainer();
            genropatches.comboBox();
            genropatches.tree();
            //genropatches.grid();
            genropatches.parseNumbers();
        }
        this.clsdict = {domsource:gnr.GnrDomSource, bag:gnr.GnrBag};
        this.eventPath = '_sys.events';
        this.prefs = {'recordpath':'tables.$dbtable.record',
            'selectionpath':'tables.$dbtable.selection',
            'limit':'50'};

        dojo.addOnLoad(this, 'start');
    },
    start:function() {
        setTimeout(dojo.hitch(this, 'dostart'), 1);
    },
    compare: function(op, a, b) {
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
    bp:function(aux) {
        console.log('bp ' + aux);
        if (aux===true){
            debugger;
        }
    },
    onWindowUnload:function(e) {
        this.rpc.remoteCall('onClosePage', {sync:true});
        if (genro._data) {
            genro.saveContextCookie();
        }
    },
    saveContextCookie:function() {
        var clientCtx = genro.getData('_clientCtx');
        genro.publish('onCookieSaving');
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
    _registerUserEvents:function() {
        this.auto_polling = -1;
        this.user_polling = -1;
        genro._lastUserEventTs = new Date();
        var cb = function(e) {
            if (genro.user_polling > 0) {
                genro._lastUserEventTs = new Date();
                if ((genro._lastUserEventTs - genro.lastRpc) / 1000 > genro.user_polling) {
                    genro.rpc.ping({'reason':'user'});
                }
            }
        };
        dojo.connect(window, 'onmousemove', cb);
        dojo.connect(window, 'onkeypress', cb);
    },
    dostart: function() {
        /*
         Here starts the application on page loading.
         It calls the remoteCall to receive the page contained in the bag called 'main'.
         */
        //genro.timeIt('** dostart **');
        this._dataroot = new gnr.GnrBag();
        this._dataroot.setBackRef();
        this._data = new gnr.GnrBag();
        //this.setData('_dev.widgets',this.catalog);
        this._dataroot.setItem('main', this._data);

        this.widget = {};
        this._counter = 0;

        this.dlg.createStandardMsg(document.body);
        //this.dev.srcInspector(document.body);
        this.contextIndex = {};


        //genro.timeIt('** getting main **');
        var mainBagPage = this.rpc.remoteCall('main', this.startArgs, 'bag');
        //genro.timeIt('**  main received  **');
        if (mainBagPage && mainBagPage.attr.redirect) {
            var url = this.addParamsToUrl(mainBagPage.attr.redirect, {'fromPage':this.absoluteUrl()});
            this.gotoURL(url);
        }
        //this.loadPersistentData()
        this.loadContext();
        //genro.timeIt('** starting builder **');
        this.src.startUp(mainBagPage);
        //genro.timeIt('** end builder **');
        genro.dom.removeClass('mainWindow', 'waiting');
        genro.dom.removeClass('_gnrRoot', 'notvisible');
        genro.dom.effect('_gnrRoot', 'fadein', {duration:400});
        genro.dragDropConnect();
        if(genro.isDeveloper){
            genro.dev.inspectConnect();
        }
        
        var _this = this;
        this._dataroot.subscribe('dataTriggers', {'any':dojo.hitch(this, "dataTrigger")});
        genro.dev.shortcut("Ctrl+Shift+D", function() {
            genro.dev.showDebugger();
        });

        genro.callAfter(function() {
            genro.fireEvent('gnr.onStart');
        }, 100);
        genro.dev.shortcut('f1', function(e) {
            genro.publish('SAVERECORD', e)
        })
        genro.dev.shortcut('f3', function(e) {
            genro.publish('PRINTRECORD', e)
        })
        /* if (dojo.isSafari && genro.wdgById('pbl_root')){
         setTimeout(genro.forceResize,1);
         }*/
        dojo.publish('onPageStart', []);
        var windowTitle = this.getData('gnr.windowTitle');
        if (windowTitle) {
            genro.dom.windowTitle(windowTitle);
        }
        if (this.debugopt) {
            genro.setData('gnr.debugger.sqldebug', this.debugopt.indexOf('sql') >= 0);
        }
        this.isMac = dojo.isMac != undefined ? dojo.isMac : navigator.appVersion.indexOf('Macintosh') >= 0;
        this.isTouchDevice = ( (navigator.appVersion.indexOf('iPad') >= 0 ) || (navigator.appVersion.indexOf('iPhone') >= 0));
        this.isChrome = ( (navigator.appVersion.indexOf('Chrome') >= 0 ));
        this._registerUserEvents();

        if (this.isTouchDevice) {
            genro.dom.startTouchDevice();
        }

    },
    

    dragDropConnect:function(pane) {
        var pane = pane || genro.domById('mainWindow');
        dojo.connect(pane, 'dragstart', genro.dom, 'onDragStart');
        dojo.connect(pane, 'dragend', genro.dom, 'onDragEnd');
        dojo.connect(pane, 'dragover', genro.dom, 'onDragOver');
        dojo.connect(pane, 'drop', genro.dom, 'onDrop');
    },

    
    playSound:function(name, path, ext) {
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
        //window.resizeBy(1,1);
        //window.resizeBy(-1,-1);

        //setTimeout(dojo.hitch(genro.wdgById('pbl_root'), 'resize'), 100);
    },
    callAfter: function(cb, timeout, scope) {
        scope = scope || genro;
        cb = funcCreate(cb);
        setTimeout(dojo.hitch(scope, cb), timeout);
    },
    fireAfter: function(path, msg, timeout) {
        var timeout = timeout || 1;
        var _path = path;
        var _msg = msg;
        if (this.pendingFireAfter[path]) {
            clearTimeout(this.pendingFireAfter[path]);
        }
        this.pendingFireAfter[path] = setTimeout(function() {
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
    format: function (v, f, m) {
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
            if (!f.places && f.dtype == 'L') {
                f.places = 0;
            }
            if (!f.pattern && f.places == 0) {
                f.pattern = '##########';
            }
            v = stringStrip(dojo.currency.format(v, f));
        }
        else if (typeof(v) == 'boolean' || f.dtype == 'B') {
            var divcontent = v ? (f['true'] || (f['trueclass'] ? '' : 'true')) : (f['false'] || (f['falseclass'] ? '' : 'false'));
            var divclass = v ? (f['trueclass'] ? f['trueclass'] : '') : (f['falseclass'] ? f['falseclass'] : '');
            divclass = divclass ? 'class="' + divclass + '"' : '';
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
            if (f['isbutton'] === true) {
                var divclass = f['buttonclass'];
                divclass = divclass ? 'class="' + divclass + '"' : '';
                var event_attrs = '';
                var events = objectExtract(f, 'on*', true);
                if (events) {
                    for (var event_type in events) {
                        var cellPars = f['cellPars'] || {};
                        var jsCode = "genro.src.onEventCall(event,'" + escapeLiterals(events[event_type]) + "'," + serialize(cellPars) + ");";
                        event_attrs += " on" + event_type + '="' + cleanJsCode(jsCode) + '"';
                    }
                }
                v = "<div " + event_attrs + " style='margin:auto;' " + divclass + ">" + '&nbsp;' + "</div>";
            }
            else if (f['inlineedit'] == true) {
                v = "<span style='font-family: wingdings; text-decoration: underline;'>&nbsp;&nbsp;&nbsp;&nbsp;&#x270d;&nbsp;&nbsp;&nbsp;&nbsp;</span>";
            }

        }
        // fine area passibile di modifiche

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
    }
    ,
    getCounter: function() {
        this._counter = this._counter + 1;
        return this._counter;
    },
    blurCurrent:function(a, b, c) {
        if (genro.currentFocusedElement) {
            genro.currentFocusedElement.blur();
        }
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
        frm = node._('iframe', params);
        node.unfreeze();


    },
    makeUrl: function(url, kwargs) {
        if (url.indexOf('://') == -1) {
            if (url.slice(0, 1) != '/') {
                var base = document.location.pathname;
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
        if (kw.evt == 'upd') {
            var dpath = kw.pathlist.slice(1).join('.');
            if (dpath in genro._serverstore_paths && kw.reason != 'serverChange') {
                genro._serverstore_changes = genro._serverstore_changes || {};
                genro._serverstore_changes[genro._serverstore_paths[dpath]] = kw.value;
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
    publish:function(topic) {
        var args = [];
        for (var i = 1; i < arguments.length; i++) {
            args.push(arguments[i]);
        }
        //console.log('publishing:'+topic);
        //  console.log(args)
        dojo.publish(topic, args);
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
        storage.setItem(key, value);
        console.log('Stored in ' + sessionType + 'Storage at key:' + key + '  value:' + value);
    },
    getFromStorage:function(sessionType, key) {
        var sessionType = sessionType || 'session';
        var storage = (sessionType == 'local') ? localStorage : sessionStorage;
        var value = storage.getItem(key);
        if (value) {
            //console.log('Loaded from '+sessionType+'Storage at key:'+key+'  value:'+value);
        } else {
            //console.log('Not existing in '+sessionType+'Storage key:'+key);
        }
        return value;
    },


    addParamsToUrl: function(url, params) {
        var parameters = [];
        for (var key in params) {
            parameters.push(key + '=' + encodeURIComponent(params[key]));
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
    formById:function(formId) {
        var node = genro.nodeById(formId);
        if (node) {
            return node.formHandler;
        }
    },
    nodeById:function(nodeId) {
        var node = genro.src._index[nodeId];
        if (!node && genro.src.building) {
            node = genro.src._main.getNodeByAttr('nodeId', nodeId);
        }
        return node;
    },
    domById:function(nodeId) {
        var node = this.nodeById(nodeId);
        if (node) {
            return node.getDomNode();
        } else {
            return dojo.byId(nodeId);
        }
    },
    wdgById:function(nodeId) {
        var node = this.nodeById(nodeId);
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
    remoteUrl: function(method, arguments, sourceNode, avoidCache) {
        return genro.rpc.rpcUrl(method, arguments, sourceNode, avoidCache);
    },
    setUrlRemote: function(widget, method, arguments) {
        var url = genro.rpc.rpcUrl(method, arguments);
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
        this.serverCall('connection.logout', null, 'genro.gotoHome();');
        //this.gotoHome();
    },
    remoteJson:function(method, params) {
        //UTILE?
        /* remoteCall mode json*/
        return genro.rpc.remoteCall(method, params, 'json');
    },
    //UTILE?
    //rimappa la rpc.remoteCall
    serverCall:function(method, params, async_cb, mode) {
        var cb = funcCreate(async_cb);
        return genro.rpc.remoteCall(method, params, mode, null, null, cb);
    },

    setSelectedVal:function(obj, value) {
        /*Set the attr selectedValue*/
        var dataNode = genro.getDataNode(obj.sourceNode);
        dataNode.setAttr({'selectedValue':value});
    },
    evaluate:function(expr) {
        try {
            var toEval = 'genro.auxresult=(' + expr + ')';
            dojo.eval(toEval);
            return genro.auxresult;
        } catch(e) {
            if (console != undefined) {
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
    pageReload:function(params) {
        if (params) {
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
        return genro.rpc['remote_' + resolverName].call(genro.rpc, params, parentbag);
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
    lockScreen:function(locking, reason, options) {
        if (reason) {
            genro.lockingElements[reason] = reason;
        }
        if (locking) {
            if (!reason) {
                return;
            }
            document.createElement("div");
            var hider = document.createElement("div");
            hider.id = "mainWindow_hider";
            dojo.addClass(hider, 'formHider');
            if (options) {
                var waiting = document.createElement("div");
                dojo.addClass(waiting, 'waiting');
                hider.appendChild(waiting);
            }
            if (!genro.domById('mainWindow_hider')) {
                genro.domById('mainWindow').appendChild(hider);
            }
        } else {
            if (reason) {
                objectPop(genro.lockingElements, reason);
            } else {
                genro.lockingElements = {};
            }
            if (!objectNotEmpty(genro.lockingElements)) {
                genro.domById('mainWindow').removeChild(genro.domById('mainWindow_hider'));
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

