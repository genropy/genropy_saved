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
                                        title:'Source Node Inspector',
                                        'bagpath':'*S'});
        
        node.unfreeze();
        

    },


    siteLockedStatus:function(set){
        var maingenro = genro.mainGenroWindow.genro;
        var sn = maingenro.nodeById('_gnrRoot');
        if(!sn){
            return;
        }
        if(set){
            if(!maingenro.site_locked){
                maingenro.site_locked = true;
                sn.setHiderLayer(true,{message:'Site temporary unavailable',z_index:999998,message_color:'white',message_font_size:'30pt',
                                    message_background:'red',message_padding:'20px',message_margin:'20%'});
            }
        }else if (maingenro.site_locked){
            maingenro.site_locked = false;
            sn.setHiderLayer(false);
        }
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
            var mainGenroWindow = genro.mainGenroWindow.genro;
            mainGenroWindow.polling_enabled = false;
            mainGenroWindow.dlg.alert('No longer existing page','Error',null,null,{confirmCb:genro.pageReload});
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
                console.error('RESPONSE',response,'ioArgs',ioArgs,responseText)
                genro.dev.addError("An HTTP error occurred: " + response.message,'SERVER',true);
                if (genro.isDeveloper){
                    //var title = 'Server error ' +ioArgs.args.content.method || '';
                    //var qp = genro.dlg.quickPalette('error_palette_'+genro.getCounter(),{height:'500px',width:'700px',maxable:true,title:title,dockTo:false},responseText);
                        //{innerHTML:responseText,position:'absolute',top:0,left:0,right:0,bottom:0,overflow:'auto'});
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
            return;
        }else if (error=='server_exception'){
            genro.dlg.alert('<h3 align="center">'+envNode.getValue()+'</h3> <br/>','Error');
            return;
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
    serverWriteError:function(error_description, error_type,kw){
        var kw =kw || {};
        objectUpdate(kw,{description:error_description,error_type:error_type});
        genro.serverCall('site.writeError', kw, function(){console.warn(error_type,error_description)});
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
            var lblpars = {innerHTML:objectPop(kw, 'lbl'),_class:'gnrfieldlabel'};
            objectUpdate(lblpars, objectExtract(kw, 'lbl_*'));
            var tr = this.curr_tr;
            tr._('td', lblpars);
            var res = tr._('td',objectUpdate({colspan:colspan},objectExtract(kw,'td_*')))._(tag, kw);
            var default_value = objectPop(kw,'default_value');
            var resNode = res.getParentNode();
            if(default_value && resNode.attr.value){
                resNode.setRelativeData(resNode.attr.value,default_value);
            }
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


    fieldsTreeConfigurator:function(table){
        var kw = {height:'550px', width:'840px', title:'Fields tree configurator',src:'/sys/tableconf/'+table.replace('.','/'),closable:true};
        kw.selfsubscribe_exit = function(kw){
            console.log('refresh remoteResolver albero')
        };
        genro.dlg.iframeDialog('fieldsTreeConfigurator_'+table.replace('.','_'), kw)

    },
    
    fieldsTree:function(pane,table,kw){
        var kw = kw || {};
        var path = kw.explorerPath || 'gnr.relation_explorers.' + table;
        var dragCode = objectPop(kw,'dragCode') || 'gnrdbfld_'+table.replace('.', '_');
        genro.setData(path,genro.rpc.remoteResolver('relationExplorer', {'table':table,'currRecordPath':objectPop(kw,'currRecordPath'),omit:'_'}));
        var treeattr = objectUpdate({storepath:path,margin:'4px'},kw);
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
            fldinfo._nodelabel = treeItem.label;
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
                                        title:'Developer tools ['+genro._('gnr.pagename')+']',
                                        width:'500px',maxable:true});
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
                            searchOn:true,tree_inspect:'shift',tree_labelAttribute:null,editable:true});
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


    _getHeaderInfo_getcell:function(row,field){
        var h = genro.rpcHeaderInfo[row['r_count']];
        return h?h[field]:'';
    },

    sqlDebugPalette:function(parent){
        var bc = parent._('palettePane',{'paletteCode':'devSqlDebug',title:'Sql',contentWidget:'borderContainer',frameCode:'devSqlDebug',margin:'2px',rounded:4});
        bc._('dataController',{'script':"genro.debug_sql=sqldebug",'sqldebug':'^gnr.debugger.sqldebug'});
        bc._('dataController',{'script':"SET gnr.debugger.pydebug = pydebug_methods?true:false; genro.debug_py=pydebug_methods;",'pydebug_methods':'^gnr.debugger.pydebug_methods',_delay:1});

        var top = bc._('framePane',{frameCode:'debugger_rpcgrid',region:'top',height:'200px',splitter:true,_class:'pbl_roundedGroup',margin:'2px',center_overflow:'hidden'});
        var topbar = top._('SlotBar',{_class:'pbl_roundedGroupLabel',slots:'5,vtitle,*,activator_py,activator_sql,5,clearConsole,5',side:'top'})
        topbar._('div','vtitle',{innerHTML:'RPC grid'})
        var sn = bc.getParentNode();
        topbar._('checkbox','activator_py',{'value':'^gnr.debugger.pydebug','label':'Debug py',
            validate_onAccept:function(value,userChange){
                if(userChange){
                    var currval = genro.getData('gnr.debugger.pydebug_methods') || '';
                    genro.setData('gnr.debugger.pydebug_methods',currval);
                    genro.dlg.prompt('Methods',{dflt:currval,widget:'simpleTextArea',action:function(value){
                        sn.setRelativeData('gnr.debugger.pydebug_methods',value);
                    }});
                }
            }
        });

        topbar._('checkbox','activator_sql',{'value':'^gnr.debugger.sqldebug','label':'Debug sql'});
        topbar._('slotButton','clearConsole',{'label':'Clear',action:'genro.setData("gnr.debugger.main",null);genro.rpcHeaderInfo = {};genro.getCounter("debug",true);'});
        if(!genro.getData('gnr.debugger.main')){
            genro.setData('gnr.debugger.main', new gnr.GnrBag());
        }
        var rowstruct = new gnr.GnrBag();
        rowstruct.setItem('cell_0', null, {field:'r_count',name:'N',width:'2em',dtype:'L'});

        rowstruct.setItem('cell_1', null, {field:'methodname',name:'Method',width:'18em'});
        rowstruct.setItem('cell_5', null, {field:'debug_info',name:'Debug info',width:'15em'});

        rowstruct.setItem('cell_2', null, {field:'server_time',name:'Server',width:'4em',dtype:'N'});
        rowstruct.setItem('cell_8', null, {field:'xml_size',name:'Size(kb)',width:'4em',dtype:'N',_customGetter:function(row){
            return Math.floor((genro.dev._getHeaderInfo_getcell(row,'xml_size')/1024));
        }});
        rowstruct.setItem('cell_7', null, {field:'xml_time',name:'XMLTime',width:'4em',dtype:'N',_customGetter:function(row){
            return genro.dev._getHeaderInfo_getcell(row,'xml_time')
        }});

        rowstruct.setItem('cell_3', null, {field:'sql_count',name:'N.Sql',width:'4em',dtype:'N'});
        rowstruct.setItem('cell_4', null, {field:'sql_total_time',name:'Sql time',width:'4em',dtype:'N'});
        rowstruct.setItem('cell_6', null, {field:'not_sql_time',name:'Py time',width:'4em',dtype:'N'});




        genro.setData('gnr.debugger.rpccall_grid.struct.view_0.row_0', rowstruct);
        var rpcgrid = top._('includedView',{nodeId:'sql_debugger_grid_rpccall',storepath:'gnr.debugger.main',
                                    structpath:'gnr.debugger.rpccall_grid.struct',datapath:'gnr.debugger.rpccall_grid',
                                    selectedIndex:'gnr.debugger.rpccall_grid.currentRowIndex',relativeWorkspace:true});

        rpcgrid._('dataController',{script:'SET gnr.debugger.sqlquery_grid.store = (sind&&sind)!=-1?mainbag.getItem("#"+sind).deepCopy():null;',
                                    sind:'^gnr.debugger.rpccall_grid.currentRowIndex',mainbag:'=gnr.debugger.main',_if:'mainbag && mainbag.len()'})
        rpcgrid._('dataController',{script:'SET gnr.debugger.sqlquery_grid.store = null;',mainbag:'^gnr.debugger.main',_delay:1})

        
        var center = bc._('framePane',{frameCode:'debugger_sqlgrid',region:'center',_class:'pbl_roundedGroup',margin:'2px',center_widget:'borderContainer'});
        center._('contentPane','top',{_class:'pbl_roundedGroupLabel'})._('div',{'innerHTML':'Sql query grid'})


        var rowstruct = new gnr.GnrBag();
        rowstruct.setItem('cell_0', null, {field:'_type',name:'T',width:'2em'});
        rowstruct.setItem('cell_1', null, {field:'_description',name:'Description',width:'9em'});
        //rowstruct.setItem('cell_1', null, {field:'sqltext',name:'Server time',width:'20em'});
        rowstruct.setItem('cell_2', null, {field:'_execution_time',name:'Time',width:'8em',dtype:'N'});

        genro.setData('gnr.debugger.sqlquery_grid.struct.view_0.row_0', rowstruct);
        center._('contentPane',{region:'left',width:'220px',overflow:'hidden',splitter:true})._('includedView',{nodeId:'sql_debugger_grid_sqlquery',storepath:'gnr.debugger.sqlquery_grid.store',
                                structpath:'gnr.debugger.sqlquery_grid.struct',datapath:'gnr.debugger.sqlquery_grid',relativeWorkspace:true,selectedIndex:'.currentRowIndex'});
        var tc = center._('tabContainer',{region:'center',margin:'2px'});
        tc._('dataController',{script:'var n=store.getNode("#"+currentRowIndex); if(n){this.setRelativeData(".output.sqltext",n._value);this.setRelativeData(".output.params",objectAsHTMLTable(n.attr))}',currentRowIndex:'^.currentRowIndex',store:'=.store',_if:'store',_else:'SET .output=null;',datapath:'gnr.debugger.sqlquery_grid'})
        tc._('contentPane',{title:'Sql'})._('div',{innerHTML:'^gnr.debugger.sqlquery_grid.output.sqltext',height:'100%',
                                    style:'white-space: pre;background:white;',overflow:'auto',padding:'5px',_class:'selectable'});
        tc._('contentPane',{title:'Arguments'})._('div',{innerHTML:'^gnr.debugger.sqlquery_grid.output.params',height:'100%',overflow:'auto',_class:'debug_params'});

        
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
         sb=pane._('SlotBar',{'side':'top',slots:'pollingSwitch,5,rpcAnalyzer,*,actionMenu,5',toolbar:true,font_size:'.8'});
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
