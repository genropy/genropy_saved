/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_dev : Genro clientside developement module
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


dojo.declare("gnr.GnrDevHandler", null, {

    constructor: function(application) {
        this.application = application;
    },
    
        
    inspectConnect:function(pane){
        var pane = pane || genro.domById('mainWindow');
        dojo.connect(pane,'onmousemove',function(e){
            if(e.altKey && e.shiftKey){
                var sourceNode = genro.src.enclosingSourceNode(e.target);
                genro.src.highlightNode(sourceNode);
                genro.publish('srcInspector_editnode',sourceNode);
            }else{
                genro.src.highlightNode();
            }
        });
        dojo.connect(pane,'onmouseout',function(e){
            genro.src.highlightNode();
        });
        
        dojo.connect(pane,'onclick',function(e){
            if(e.altKey && e.shiftKey){
                if(!dijit.byId("gnr_srcInspector")){
                    genro.dev.openSrcInspector();
                }
                var sourceNode = genro.src.enclosingSourceNode(e.target);
                console.log('------current edit node:-------');
                console.log(sourceNode);
                genro.publish('srcInspector_editnode',sourceNode);
                window._sourceNode_ = sourceNode;
            }
            
            
        });
  
    },
    openSrcInspector:function(){
        var root = genro.src.newRoot();
        genro.src.getNode()._('div', '_devSrcInspector_');
        var node = genro.src.getNode('_devSrcInspector_').clearValue();
        node.freeze();
        node._('PaletteBagNodeEditor',{'paletteCode':'srcInspector',nodeId:'srcInspector',id:'gnr_srcInspector','dockTo':false,
                                        title:'Source Node Inspector',style:"font-family:monaco;",
                                        'bagpath':'*S'});
        
        node.unfreeze();
        

    },
    debugMessage: function(msg, level, duration) {

        var level = level || 'MESSAGE';
        var duration = duration || 50;
        dojo.publish("standardDebugger", {message: msg, type:level.toUpperCase(), duration:duration});
    },
    handleRpcHttpError:function(response, ioArgs) {
        var xhr = ioArgs.xhr;
        var status = xhr.status;
        var statusText = xhr.statusText;
        var readyState = xhr.readyState;
        var responseText = xhr.responseText;
        if (status == 400) {
            genro.dlg.alert('Client HTTP error','Error',null,null,{confirmCb:genro.pageReload});
            return;
        }
        else if (status == 412) {
            genro.dlg.alert('No longer existing page','Error',null,null,{confirmCb:genro.pageReload});
            return;
        } else if (status == 0) {
            //genro.dlg.alert('Site temporary un available. Retry later');

            var msg = 'status: ' + xhr.status + ' - statusText:' + xhr.statusText + ' - readyState:' + xhr.readyState + ' - responseText:' + responseText;
            console.log(ioArgs.url);
            console.log(msg);
            console.log(ioArgs);

        }
        else {
            console.log('handleRpcHttpError');
            debug_url = ioArgs.xhr.getResponseHeader('X-Debug-Url');
            if (!debug_url) {
                console.log('RESPONSE',response,'ioArgs',ioArgs,responseText)
                if (genro.isDeveloper){
                    var title = 'Server error ' +ioArgs.content.method || '';
                    genro.dlg.quickPalette('error_palette_'+genro.getCounter(),{height:'500px',width:'700px',maxable:true,title:title},
                        {innerHTML:responseText,position:'absolute',top:0,left:0,right:0,bottom:0,overflow:'auto'});
                }else{
                    genro.dev.addError("An HTTP error occurred: " + response.message,'SERVER',true);
                }
            }
            else {
                if(genro.isDeveloper){
                    genro.openWindow(debug_url, 'Internal Server Error', {scrollbars:'yes'});
                }else{
                    genro.dlg.ask('Server error',
                        '<h2 align="">Sorry. There was a server error</h2>. <br/> <i>For more details see</i> <br/>'+_F(debug_url,'autolink'),
                        {confirm:'Reload',cancel:'Ignore'},{confirm:function(){genro.pageReload();}});
                }
            }
        }
    },
    handleRpcError:function(error, envNode) {
        if (error=='gnrexception'){
            genro.dlg.alert('<h2 align="center">'+envNode.getValue()+'</h2> <br/>','Warning');
        }
        if (error == 'expired') {
            genro.dlg.message('expired session');

            genro.dlg.ask('Expired session',
                        '<h2 align="">Sorry. The session is expired</h2>.<br/>',
                        {confirm:'Reload'},{confirm:function(){
                            genro.mainGenroWindow.genro.pageReload();
                        }});
            //genro.pageReload();
        }
        else if (error == 'clientError') {
            genro.dlg.alert('clientError');
            //throw result;
        } else if (error == 'serverError') {
            var root = genro.src.newRoot();
            var fpane = root._('dialog', 'traceback', {title:'Trace',nodeId:'traceback_main',_class:'tracebackDialog'});
            fpane.setItem('', envNode.getValue());

            genro.src.setSource('traceback', root);
            genro.wdgById('traceback_main').show();
        }
    },

    formbuilder:function(node, col, tblattr) {
        var tbl = node._('table', tblattr || {})._('tbody');
        tbl.col_max = col || 1;
        tbl.col_count = tbl.col_max + 1;
        tbl.addField = function(tag, kw) {
            if (this.col_count > this.col_max) {
                this.curr_tr = this._('tr');
                this.col_count = 1;
            }
            var colspan = objectPop(kw,'colspan') || 1;
            colspan = colspan==1?colspan:colspan*2;
            var lblpars = {innerHTML:objectPop(kw, 'lbl')};
            objectUpdate(lblpars, objectExtract(kw, 'lbl_*'));
            var tr = this.curr_tr;
            tr._('td', lblpars);
            var res = tr._('td',objectUpdate({colspan:colspan},objectExtract(kw,'td_*')))._(tag, kw);
            this.col_count = this.col_count + colspan;
            return res;
        };
        return tbl;
    },

    relationExplorer:function(table, title, rect) {
        var rect = rect || {'top':'10px','right':'10px','height':'300px','width':'200px'};
        var code = table.replace('.', '_');
        genro.src.getNode()._('div', '_relationExplorer_' + code);
        var node = genro.src.getNode('_relationExplorer_' + code).clearValue();
        node.freeze();
        var fpane = node._('floatingPane', {title:title,top:rect.top,bottom:rect.bottom,
            left:rect.left,right:rect.right,
            height:rect.height,width:rect.width,
            resizable:true,dockable:false,_class:'shadow_4',
            closable:true});
        this.fieldsTree(fpane,table);
        node.unfreeze();
        fpane.getParentNode().widget.bringToTop();
    },
    
    fieldsTree:function(pane,table,kw){
        var path = kw.explorerPath || 'gnr.relation_explorers.' + table;
        var dragCode = objectPop(kw,'dragCode') || 'gnrdbfld_'+table.replace('.', '_');
        genro.setData(path,genro.rpc.remoteResolver('relationExplorer', {'table':table,'currRecordPath':objectPop(kw,'currRecordPath'),omit:'_'}));
        var treeattr = objectUpdate({storepath:path,margin:'4px'},kw || {});
        treeattr.labelAttribute = 'caption';
        treeattr._class = 'fieldsTree noIcon noExpando';
        treeattr.hideValues = true;
        treeattr.autoCollapse=true;
        treeattr.openOnClick = true;
        treeattr.getLabelClass=function(item){
            var dtype = item.attr.dtype;
            var _class = [];
            if(!dtype || dtype=='RM' || dtype=='RO' || item.attr.subfields){
                _class.push('fieldsTree_folder');
            }
            dtype = dtype || (item.attr.isRoot?'root':'group');
            _class.push('fieldsTree_' +dtype);
            return _class.join(' ');
        };
        treeattr.onDrag = function(dragValues, dragInfo, treeItem) {
            if (!(treeItem.attr.dtype && treeItem.attr.dtype != 'RM' && treeItem.attr.dtype != 'RO')) {
                return false;
            }
            var fldinfo = objectUpdate({}, treeItem.attr);
            fldinfo['maintable'] = table;
            dragValues['text/plain'] = treeItem.attr.fieldpath;
            dragValues[dragCode] = fldinfo;
        };
        treeattr.draggable = true;
        //treeattr.getIconClass = 'if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}';
        treeattr.getIconClass = 'return "treeNoIcon";';
        pane._('tree', treeattr);
    },
    
    openInspector:function(){
        var root = genro.src.newRoot();
        genro.src.getNode()._('div', '_devInspector_');
        var node = genro.src.getNode('_devInspector_').clearValue();
        node.freeze();
        var cbLog = function(e){
            if(e.altKey){
                var wdg = dijit.getEnclosingWidget(e.target);
                console.log(wdg.item);
            }
        };
        var pg = node._('paletteGroup',{'groupCode':'devTools','dockTo':false,id:'gnr_devTools',
                                        title:'Developer tools ['+genro._('gnr.pagename')+']',style:"font-family:monaco;",
                                        width:'500px'});
        pg._('paletteTree',{'paletteCode':'cliDatastore',title:'Data',
                           storepath:'*D',searchOn:true,tree_inspect:'shift',
                           'tree_connect_onclick':cbLog,
                           editable:true,tree_labelAttribute:null,tree_hideValues:false});
        var sourcePane = pg._('paletteTree',{'paletteCode':'cliSourceStore',title:'Source',
                           storepath:'*S',searchOn:true,tree_inspect:'shift',
                           editable:true,
                           'tree_connect_onclick':cbLog,
                           tree_getLabel:function(n){
                               return n.attr.tag+':'+(n.attr.nodeId || n._id);
                           },
                           tree_selectedPath:'.tree.selectedPath'});
        sourcePane._('dataController',{'script':'genro.src.highlightNode(fpath)', 
                                       'fpath':'^gnr.palettes.cliSourceStore.tree.selectedPath'});
        pg._('paletteTree',{'paletteCode':'dbmodel',title:'Model',
                            searchOn:true,tree_inspect:'shift',editable:true});
        genro.setDataFromRemote('gnr.palettes.dbmodel.store', "app.dbStructure");
        this.sqlDebugPalette(pg);
        this.devUtilsPalette(pg);
        node.unfreeze();
    },
    
    moverSavingDlg:function(sourceNode,saveaction){
        var dlg = genro.dlg.quickDialog('Save Mover');
        var center = dlg.center;
        var box = center._('div', {datapath:sourceNode.absDatapath(),padding:'20px'});
        var fb = genro.dev.formbuilder(box, 1, {border_spacing:'6px'});
        fb.addField('textbox', {lbl:_T("Mover"),value:'^.dlg.movername',width:'10em'});
        var bottom = dlg.bottom._('div');
        var saveattr = {'float':'right',label:_T('Save')};
        var data = new gnr.GnrBag();
        saveattr.action = function(){
            saveaction(dlg);
        }
        bottom._('button', saveattr);
        bottom._('button', {'float':'right',label:_T('Cancel'),action:dlg.close_action}); 
        return dlg;       
    },

    sqlDebugPalette:function(parent){
        var frame = parent._('palettePane',{'paletteCode':'devSqlDebug',title:'Sql',contentWidget:'framePane',frameCode:'devSqlDebug'});
        var top = frame._('toolbar',{side:'top'});
        top._('checkbox',{'value':'^gnr.debugger.sqldebug','label':'Debug SQL'});
        top._('button',{'label':'Clear',action:'genro.setData("gnr.debugger.main",null)'});
        var treeId='sql_debugger_tree';
        var storepath='gnr.debugger.main';
        var bc = frame._('borderContainer',{side:'center'});
        var right = bc._('contentPane',{'region':'right','splitter':true,width:'50%'});
        var bottom = bc._('contentPane',{'region':'bottom','splitter':true,height:'50%','overflow':'hidden',_class:'selectable'});
        var center = bc._('contentPane',{'region':'center'});

        bottom._('div',{'innerHTML':'^.grid.bottomData',height:'100%',
                                    style:'white-space: pre;background:white;',overflow:'auto'});
      
        

        center._('tree',{'storepath':storepath,fired:'^gnr.debugger.tree_redraw','margin':'6px','nodeId':treeId,
                        'getIconClass':"return 'treeNoIcon'",'_class':'fieldsTree', 'hideValues':true});
                        
        right._('BagNodeEditor',{'nodeId':treeId+'_editbagbox','datapath':'.grid','bagpath':storepath,
                            'readOnly':true,'valuePath':'.bottomData','showBreadcrumb':false});
                
        center._('dataController',{'script':"genro.debugopt=sqldebug?'sql':null",'sqldebug':'^gnr.debugger.sqldebug'});
        center._('dataController',{'script':"FIRE gnr.debugger.tree_redraw;", 'sqldebug':'^gnr.debugger.main', '_delay':1});

    },
    devUtilsPalette:function(parent){
        var pane = parent._('palettePane',{'paletteCode':'devUtils',title:'Utils',contentWidget:'FramePane',
                                            frameCode:'devUtils',center_overflow:'hidden'});
        var dbchangelog = function(result,kwargs){
                               var txt = '';
                               result.walk(function(n){
                                   if(n.attr.changes){
                                       txt= txt +'\n'+n.attr.changes;
                                   }else{
                                       txt = txt +'\n----- pkg:' +n.label;
                                   }
                               });
                               genro.log(txt,'Check db');
                           };
         sb=pane._('SlotBar',{'side':'top',slots:'pollingSwitch,*,actionMenu,5',toolbar:true,font_size:'.8'});
         pane._('dataRpc',{'path':'.checkDb',method:'checkDb',subscribe_devUtils_checkDb:true,
                           _onResult:dbchangelog});
         pane._('dataRpc',{'path':'.applyChangesToDb',method:'applyChangesToDb',
                            subscribe_devUtils_dbsetup:true,
                            _onResult:'genro.log("DB Change applied","applyChangesToDb")'});
        sb._('checkbox','pollingSwitch',{'label':'Polling',value:'^gnr.polling.polling_enabled'});

        var m = sb._('DropDownButton','actionMenu',{label:'Commands'})._('menu',{_class:'smallMenu'})
        m._('menuline',{'label':'Clear LS',action:function(){localStorage.clear()}});
        m._('menuline',{'label':'Clear SS',action:function(){sessionStorage.clear()}});
        m._('menuline',{'label':'CheckDb',publish:'devUtils_checkDb'});
        m._('menuline',{'label':'DbSetup',publish:'devUtils_dbsetup'});
        m._('menuline',{'label':'Clear log',action:'genro.clearlog()'});
        pane._('simpleTextArea',{'value':'^gnr._dev.logger',readOnly:true,height:'100%',
                                    style:'white-space: pre;'});
    },

    openLocalizer:function() {
        noValueIndicator = "<span >&nbsp;</span>";
        genro.src.getNode()._('div', '_localizer');
        var node = genro.src.getNode('_localizer').clearValue().freeze();
        genro.setData('gnr.pageLocalization', genro.rpc.remoteCall('localizer.pageLocalizationLoad'));
        var dlg = node._('dialog', {nodeId:'_localizer',title:'Localizer',width:'40em','padding':'2px'});
        var xx = dlg._('div', {height:'400px',overflow:'auto',background_color:'#eee',border:'1px inset'});
        var saveData = function() {
            var data = genro.getData('gnr.pageLocalization');
            var cb = function() {
                genro.pageReload();
            };
            genro.rpc.remoteCall('localizer.pageLocalizationSave', {data:data}, 'bag', 'POST', null, cb);
        };
        dlg._('button', {label:'Save',margin:'4px','float':'right',onClick:saveData});
        var nodes = genro.getData('gnr.pageLocalization').getNodes();
        var tbl = xx._('table', {_class:'localizationTable',width:'100%'});
        var thead = tbl._('thead');
        var r = thead._('tr');
        r._('th', {content:'Key'});
        r._('th', {content:'Value'});
        var tbody = tbl._('tbody');
        for (var i = 0; i < nodes.length; i++) {
            var r = tbody._('tr', {datapath:'gnr.pageLocalization.r_' + i});
            r._('td', {width:'15em'})._('div', {innerHTML:'^.key'});
            r._('td')._('inlineeditbox', {value:'^.txt',noValueIndicator:noValueIndicator});
        }
        node.unfreeze();
        genro.wdgById('_localizer').show();
    },
    printUrl: function(url) {
        genro.dev.deprecation("genro.dev.printUrl(url)", "genro.download(url,'print')");
        genro.download(url, null, 'print');
        /*genro.src.getNode()._('div', '_printframe');
         var node = genro.src.getNode('_printframe').clearValue().freeze();
         frm = node._('iframe', {'src':url, connect_onload:"genro.dom.iFramePrint(this.domNode);",
         display:'hidden', width:'0px', height:'0px'});
         node.unfreeze();*/
    },
    exportUrl: function(url) {
        genro.dev.deprecation('genro.dev.exportUrl', 'genro.download');
        genro.download(url);
        // USELESS, USE download(url) instead of this
        /*        genro.src.getNode()._('div', '_printframe');
         var node = genro.src.getNode('_printframe').clearValue().freeze();
         frm = node._('iframe', {'src':url, display:'hidden', width:'0px', height:'0px'});
         node.unfreeze();*/
    },
    deprecation:function(oldval, newval) {
        console.warn('Deprecation warning: ' + oldval + ' was replaced with ' + newval, 'WARNING');
        //this.debugMessage('Deprecation warning: '+oldval+' was replaced with '+newval,'WARNING');
    },
    dataDebugTrigger : function(kw) {
        var path = kw.pathlist.join('.');
        var msg = "A bag trigger : " + kw.evt;
        if (kw.evt == 'upd_value') {
            var msg = "The value of node '" + path + "' was changed from " + kw.oldvalue + " to " + kw.node.getValue();
        }
        else if (kw.evt == 'ins') {
            var msg = "A node was inserted at path '" + path + "' position=" + kw.ind + " value=" + kw.node.getValue();
        }
        else if (kw.evt == 'del') {
            var msg = "A node was deleted at path '" + path + "' position=" + kw.ind + " oldvalue=" + kw.node.getValue();
        }
        dojo.publish("triggerBag", {message: msg});
    },
    getSourceBlock: function(path) {
        var node = this.application.source.getNode(path, false, true, new gnr.GnrDomSource());
        if (node) {
            var block = node.getValue();
            if (!block) {
                block = new gnr.GnrDomSource();
                node.setValue(block, false);
            }
            return block;
        }
    },
    dictToHtml:function(obj, tblclass) {
        var result = ["<table class='" + tblclass + "'><thead><tr><th>Name</th><th>Value</th></tr></thead><tbody>"];
        for (key in obj) {
            result.push("<tr><td>" + key + "</td><td>" + obj[key] + "</td></tr>");
        }
        result.push("</tbody></table>");
        return result.join('\n');
    },
    bagAttributesTable : function(node) {
        var item = dijit.getEnclosingWidget(node).item;
        if (item) {
            return genro.dev.dictToHtml(item.attr, 'bagAttributesTable');
        }
    },
    showDebugger:function(){
        if(!dijit.byId("gnr_devTools")){
             genro.dev.openInspector();
        }
    },
    shortcut: function(shortcut, callback, opt) {
        var default_options = {
            'type':'keydown',
            'propagate':false,
            'target':document
        };
        if (!opt) opt = default_options;
        else {
            for (var dfo in default_options) {
                if (typeof opt[dfo] == 'undefined') opt[dfo] = default_options[dfo];
            }
        }

        var ele = opt.target;
        if (typeof opt.target == 'string') ele = document.getElementById(opt.target);
        var ths = this;

        //The function to be called at keypress
        var func = function(e) {
            e = e || window.event;

            //Find Which key is pressed
            var code;
            if (e.keyCode) code = e.keyCode;
            else if (e.which) code = e.which;

            var character = String.fromCharCode(code).toLowerCase();

            var keys = shortcut.toLowerCase().split("+");
            //Key Pressed - counts the number of valid keypresses - if it is same as the number of keys, the shortcut function is invoked
            var kp = 0;

            //Work around for stupid Shift key bug created by using lowercase - as a result the shift+num combination was broken
            var shift_nums = {
                "`":"~",
                "1":"!",
                "2":"@",
                "3":"#",
                "4":"$",
                "5":"%",
                "6":"^",
                "7":"&",
                "8":"*",
                "9":"(",
                "0":")",
                "-":"_",
                "=":"+",
                ";":":",
                "'":"\"",
                ",":"<",
                ".":">",
                "/":"?",
                "\\":"|"
            };
            //Special Keys - and their codes
            var special_keys = {
                'esc':27,
                'escape':27,
                'tab':9,
                'space':32,
                'return':13,
                'enter':13,
                'backspace':8,

                'scrolllock':145,
                'scroll_lock':145,
                'scroll':145,
                'capslock':20,
                'caps_lock':20,
                'caps':20,
                'numlock':144,
                'num_lock':144,
                'num':144,

                'pause':19,
                'break':19,

                'insert':45,
                'home':36,
                'delete':46,
                'end':35,

                'pageup':33,
                'page_up':33,
                'pu':33,

                'pagedown':34,
                'page_down':34,
                'pd':34,

                'left':37,
                'up':38,
                'right':39,
                'down':40,

                'f1':112,
                'f2':113,
                'f3':114,
                'f4':115,
                'f5':116,
                'f6':117,
                'f7':118,
                'f8':119,
                'f9':120,
                'f10':121,
                'f11':122,
                'f12':123
            };


            for (var i = 0; i < keys.length; i++) {
                //Modifiers
                var k = keys[i];
                if (k == 'ctrl' || k == 'control') {
                    if (e.ctrlKey) kp++;

                } else if (k == 'shift') {
                    if (e.shiftKey) kp++;

                } else if (k == 'alt') {
                    if (e.altKey) kp++;

                } else if (k.length > 1) { //If it is a special key
                    if (special_keys[k] == code) kp++;

                } else { //The special keys did not match
                    if (character == k) kp++;
                    else {
                        if (shift_nums[character] && e.shiftKey) { //Stupid Shift key bug created by using lowercase
                            character = shift_nums[character];
                            if (character == k) kp++;
                        }
                    }
                }
            }

            if (kp == keys.length) {
                callback(e);

                if (!opt['propagate']) { //Stop the event
                    //e.cancelBubble is supported by IE - this will kill the bubbling process.
                    e.cancelBubble = true;
                    e.returnValue = false;

                    //e.stopPropagation works only in Firefox.
                    if (e.stopPropagation) {
                        e.stopPropagation();
                        e.preventDefault();
                    }
                    return false;
                }
            }
        };

        //Attach the function with the event    
        if (ele.addEventListener) ele.addEventListener(opt['type'], func, false);
        else if (ele.attachEvent) ele.attachEvent('on' + opt['type'], func);
        else ele['on' + opt['type']] = func;
    },
    userObjectDialog:function(title,datapath,saveCb){
        var dlg = genro.dlg.quickDialog(title);
        var center = dlg.center;
        var box = center._('div', {datapath:datapath,padding:'20px'});
        var fb = genro.dev.formbuilder(box, 2, {border_spacing:'6px'});
        fb.addField('textbox', {lbl:_T("Code"),value:'^.code',width:'10em'});
        fb.addField('checkbox', {label:_T("Private"),value:'^.private'});
        fb.addField('textbox', {lbl:_T("Name"),value:'^.description',width:'100%',colspan:2});
        fb.addField('textbox', {lbl:_T("Authorization"),value:'^.authtags',width:'100%',colspan:2});
        fb.addField('simpleTextArea', {lbl:_T("Notes"),value:'^.notes',width:'100%',height:'5ex',colspan:2,lbl_vertical_align:'top'});
        var bottom = dlg.bottom._('div');
        var saveattr = {'float':'right',label:_T('Save')};
        var data = new gnr.GnrBag();
        saveattr.action = function(){
            saveCb(dlg);
        }
        bottom._('button', saveattr);
        bottom._('button', {'float':'right',label:_T('Cancel'),action:dlg.close_action});
        dlg.show_action();
    },

    addError:function(error,error_type,show){
        var msg = "<div style='text-align:center;font-size:1em;font-weight:bold;'>"+error_type.toUpperCase()+" Error "+_F(new Date(),'short')+"</div>"+error;
        if(show){
            genro.dlg.message(msg,null,'error',3000);
        }
        var errorbag = genro.getData('gnr.errors');
        if(!errorbag){
            errorbag = new gnr.GnrBag();
            genro.setData('gnr.errors',errorbag);
        }
        errorbag.setItem(error_type+'.#id',msg,{ts:new Date()});
        var toterr = 0;
        errorbag.forEach(function(n){
            toterr+=n.getValue().len();
        });
        errorbag.getParentNode().setAttribute('counter',toterr,true);
        if(genro.isDeveloper){
            debugger;
        }
    },

    errorPalette:function(parent){
        if(!parent){
            var root = genro.src.newRoot();
            genro.src.getNode()._('div', '_devErrors_');
            var parent = genro.src.getNode('_devErrors_').clearValue();
        }
        parent.freeze();
        var pane = parent._('palettePane',{'paletteCode':'gnrerrors','dockTo':false,
                                        title:'Current errors'});
        pane._('div',{innerHTML:'==genro.dev.formatErrors(_errors)',_errors:'^gnr.errors',padding:'5px',
                    border:'1px solid silver',background:'whitesmoke',rounded:6,margin:'5px'});
        parent.unfreeze();
    },
    formatErrors:function(errorbag){
        var errors = [];
        errorbag.forEach(function(n){
            n.getValue().forEach(function(errorNode){
                errors.push(errorNode.getValue())
            })
        })
        return errors.join('<br/><hr/>');
    }
});
//dojo.declare("gnr.GnrViewEditor",null,{
//      constructor: function(widget){
//        this.widget = widget;
//      }
//});
