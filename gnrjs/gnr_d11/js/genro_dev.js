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
        pane = pane || genro.domById('mainWindow');
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
                var sourceNode = genro.src.enclosingSourceNode(e.target);
                genro.dev.openBagNodeEditorPalette(sourceNode.getFullpath(),{name:'_devSrcInspector_',title:'Sourcenode Inspector',origin:'*S'});
                console.log('------current edit node:-------');
                genro.publish('srcInspector_editnode',sourceNode);
                console.log(sourceNode);
                window._sourceNode_ = sourceNode;
            }
            
            
        });
  
    },


    openBagNodeEditorPalette:function(nodePath,kw){
        var root = genro.src.newRoot();
        var name = kw.name || '_currentBagNodeEditor_';
        genro.src.getNode()._('div', name);

        var node = genro.src.getNode(name).clearValue();
        node.freeze();
        node._('PaletteBagNodeEditor','currentEditor',objectUpdate({'paletteCode':name,'dockTo':false,
                                        title:kw.title || 'BagNode editor',
                                        'nodePath':nodePath},kw));
        node.unfreeze();
        
    },


    openBagInspector:function(path,kw){
        kw = kw || {};
        var code = objectPop(kw,'code') || path.replace(/\./g, '_').replace(/@/g, '_');
        var wdg = genro.wdgById(code+'_floating');
        if(wdg){
            wdg.show();
            wdg.bringToTop();
            return;
        }
        var root = genro.src.newRoot();
        var name = kw.name || '_currentBagEditor_'+code;
        genro.src.getNode()._('div', name);
        var node = genro.src.getNode(name).clearValue();
        node.freeze();
        node._('paletteTree',{'paletteCode':code,title:objectPop(kw,'title') || 'Edit Bag '+path,
                           storepath:path,searchOn:true,tree_inspect:'shift',tree_searchMode:'static',
                           'tree_selectedLabelClass':'selectedTreeNode',
                           editable:true,tree_labelAttribute:null,
                           tree_hideValues:false,dockTo:'dummyDock:open'});
        node.unfreeze();
    },

    openBagEditorPalette:function(path,kw){
        kw = kw || {};
        var root = genro.src.newRoot();
        var name = kw.name || '_currentPaletteBagEditor_';
        genro.src.getNode()._('div', name);

        var node = genro.src.getNode(name).clearValue();
        node.freeze();
        node._('PaletteBagEditor','currentBagEditor',objectUpdate({'paletteCode':name,'dockTo':false,
                                        title:kw.title || 'Bag editor',
                                        'path':path},kw));
        node.unfreeze();
        return;
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
        level = level || 'MESSAGE';
        duration = duration || 50;
        dojo.publish("standardDebugger", {message: msg, type:level.toUpperCase(), duration:duration});
    },
    handleRpcHttpError:function(response, ioArgs) {
        if(response.dojoType=='cancel'){
            return;
        }
        var xhr = ioArgs.xhr;
        if(response.dojoType=='cancel'){
            return;
        }
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
        } else if (status === 0) {
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
        if(error=='gnrsilent'){
            var v = envNode.getValue();
            if (v instanceof gnr.GnrBag){
                if(v.getItem('topic')){
                    genro.publish(v.getItem('topic'),v.getItem('parameters').asDict());
                }
            }
            return;
        }
        if (error=='gnrexception'){
            if(genro.src.getNode()){
                genro.dlg.alert('<h2 align="center">'+envNode.getValue()+'</h2> <br/>','Warning');
            }else{
                dojo.byId('mainWindow').innerHTML = '<h2 class="selectable" style="color:red;" align="center">'+envNode.getValue()+'</h2> <br/>';
            }
            return;
        }else if (error=='server_exception'){
            if(genro.src.getNode()){
                genro.dlg.alert('<h3 align="center">'+envNode.getValue()+'</h3> <br/>','Error');
            }else{
                dojo.byId('mainWindow').innerHTML = '<h2 class="selectable" style="color:red;" align="center">'+envNode.getValue()+'</h2> <br/>';
            }
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
        var defautlLblAttr = objectExtract(tblattr,'lbl_*');
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
            var lbl = objectPop(kw, 'lbl');
            var lblpars = {innerHTML:lbl?_T(lbl,true):null,_class:'gnrfieldlabel',
                        hidden:kw.hidden,text_align:'right'};
            lblpars = objectUpdate(defautlLblAttr,lblpars);
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
        rect = rect || {'top':'10px','right':'10px','height':'300px','width':'200px'};
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


    tableUserConfiguration:function(table){
        var onSavedCb=null;
        genro.dlg.zoomPalette({height:'600px',width:'700px',table:'adm.tblinfo',pkey:table,
                                      formResource:'FormFromTH',main_call:'main_form',
                                      onSavedCb:onSavedCb,top:'30px',right:'40px'});
    },
    
    fieldsTree:function(pane,table,kw){
        kw = kw || {};
        var path = kw.explorerPath || 'gnr.relation_explorers.' + table;
        var checkPermissions = objectPop(kw,'checkPermissions');
        var dragCode = objectPop(kw,'dragCode') || 'gnrdbfld_'+table.replace('.', '_');
        genro.setData(path,genro.rpc.remoteResolver('relationExplorer', {'table':table,'currRecordPath':objectPop(kw,'currRecordPath'),omit:'_',item_type:'FTREE',checkPermissions:checkPermissions}));
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
    startDebug:function(callcounter){
        if(this._debuggerWindow){
            console.log('callcounter',callcounter)
            this._debuggerWindow.focus();
        }else{
            this.openGnrIde();
        }
    },

    openGnrIde :function(){
        var url = window.location.host+'/sys/gnride/'+genro.page_id;
        url = window.location.protocol+'//'+url;
        var w = genro.openWindow(url,'debugger',{location:'no',menubar:'no'});
        console.log('w,h',window.clientWidth,window.clientHeight)
        w.resizeTo(window.screen.width,window.screen.height);
        var debuggedModule = genro.pageModule;
        var mainGenro = genro;
        this._debuggerWindow = w;
        genro.wsk.addhandler('do_focus_debugger',function(callcounter){
            setTimeout(function(){
                genro.dev.startDebug(callcounter);
            },100)
        });
        w.addEventListener('load',function(){
            var dbg_genro = this.genro;     
            dbg_genro.ext.mainGenro = mainGenro;
            dbg_genro.ext['startingModule'] = debuggedModule;
        });

    },
    onDebugstep:function(data){
        var callcounter = data.callcounter;
        if (!('r_'+callcounter in genro.debugged_rpc)){
            this.addToDebugged(callcounter,data)
            this.updateDebuggerStepBox(callcounter,data);
            
        }
    },

    updateDebuggerStepBox:function(callcounter,data){
        var debugger_box = dojo.byId('pdb_root');
        var debuggerStepBox = dojo.byId('_debugger_step_'+callcounter);
        if(!debuggerStepBox){
            debuggerStepBox = document.createElement('div');
            debuggerStepBox.setAttribute('id','_debugger_step_'+callcounter);
            debuggerStepBox.setAttribute('class','pdb_debugger_step');
            debugger_box.appendChild(debuggerStepBox);
        }else{
            dojo.removeClass(debuggerStepBox,'pdb_running');
            debuggerStepBox.removeChild(debuggerStepBox.firstChild);
        }
        var container = document.createElement('div');
        var message = document.createElement('div');
        var footer = document.createElement('div');
        footer.setAttribute('class','pdb_debugger_step_footer');
        container.appendChild(message);
        container.appendChild(footer);
        debuggerStepBox.appendChild(container);
        message.innerHTML = dataTemplate('<table><tbody><tr><td class="pdb_label">Rpc:</td><td>$methodname</td></tr><tr><td class="pdb_label">Module:</td><td>$filename</td><tr><td class="pdb_label">Function:</td><td>$functionName</td></tr><td class="pdb_label">Line:</td><td>$lineno</td></tr></tbody></table>',data);
        var link = document.createElement('div');
        link.setAttribute('class','pdb_footer_button pdb_footer_button_right');
        link.innerHTML = 'Debug';
        link.setAttribute('onclick',dataTemplate("genro.dev.openDebugInIde('$pdb_id','$debugger_page_id');",data));
        footer.appendChild(link);
        link = document.createElement('div');
        link.setAttribute('class','pdb_footer_button pdb_footer_button_left');
        link.innerHTML = 'Continue';
        link.setAttribute('onclick',dataTemplate("dojo.addClass(dojo.byId('_debugger_step_"+callcounter+"'),'pdb_running'); genro.dev.continueDebugInIde('$pdb_id','$debugger_page_id',"+callcounter+");",data));
        footer.appendChild(link);
    },

    continueDebugInIde:function(pdb_id,debugger_page_id,callcounter){
        genro.wsk.publishToClient(debugger_page_id,"debugCommand",{cmd:'c',pdb_id:pdb_id});
        setTimeout(function(){
            genro.dev.removeFromDebugged(callcounter);
        },1000)
    },

    openDebugInIde:function(pdb_id,debugger_page_id){
        if(genro.mainGenroWindow){
            genro.mainGenroWindow.genro.framedIndexManager.openGnrIDE();
        }else{
            genro.wsk.publishToClient(debugger_page_id,'bringToTop')
        }
    },


    addToDebugged:function(callcounter,data){
        var dbgpars = {debugger_page_id:data.debugger_page_id,pdb_id:data.pdb_id};
        genro.debugged_rpc['r_'+callcounter] = dbgpars;
        genro.rpc.suspend_call(callcounter);
    },

    removeFromDebugged:function(callcounter){
        var dbgpars = objectPop(genro.debugged_rpc,'r_'+callcounter);
        var debuggerStepBox = dojo.byId('_debugger_step_'+callcounter);
        if(debuggerStepBox){
            dojo.byId('pdb_root').removeChild(debuggerStepBox);
        }
    },

    handleDebugPath:function(dataNode){
        if(dataNode.getFullpath){
            var path = dataNode.getFullpath(null,true);
            var existing = genro._debugPaths[path];
            genro.dlg.prompt('Set breakpoint',{
                    widget:[{lbl:'Mode',tag:'filteringSelect',values:'D:Debugger,C:Console',value:'^.mode'},
                            {lbl:'Condition',value:'^.condition',width:'20em',margin_right:'5px'}],
                    action:function(result){
                        genro.setDebugPath(path,result.asDict());
                    },
                    dflt:existing?new gnr.GnrBag(existing):null
                });
        }
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
                           storepath:'*D',searchOn:true,tree_inspect:'shift',tree_searchMode:'static',
                           'tree_connect_onclick':cbLog,
                           'tree_selectedLabelClass':'selectedTreeNode',
                           tree_connect_ondblclick:function(e){
                                var wdg = dijit.getEnclosingWidget(e.target);
                                var item = wdg.item;
                                genro.dev.handleDebugPath(item);
                           },
                           editable:true,tree_labelAttribute:null,tree_hideValues:false});
        var sourcePane = pg._('paletteTree',{'paletteCode':'cliSourceStore',title:'Source',
                           storepath:'*S',searchOn:true,tree_inspect:'shift',tree_searchMode:'static',
                           editable:true,
                           'tree_connect_onclick':cbLog,

                           tree_getLabel:function(n){
                               return n.label+'['+n.attr.tag+':'+(n.attr.nodeId || n._id)+']';
                           },
                           tree_selectedPath:'.tree.selectedPath'});
        sourcePane._('dataController',{'script':'genro.src.highlightNode(fpath)', 
                                       'fpath':'^gnr.palettes.cliSourceStore.tree.selectedPath'});
        pg._('paletteTree',{'paletteCode':'dbmodel',title:'Model',tree_searchMode:'static',
                            searchOn:true,tree_inspect:'shift',tree_labelAttribute:null,editable:true});
        genro.setDataFromRemote('gnr.palettes.dbmodel.store', "app.dbStructure",{checkPermission:true});
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
        //bc._('dataController',{'script':"SET gnr.debugger.pydebug = pydebug_methods?true:false; genro.debug_py=pydebug_methods;",'pydebug_methods':'^gnr.debugger.pydebug_methods',_delay:1});

        var top = bc._('framePane',{frameCode:'debugger_rpcgrid',region:'top',height:'200px',splitter:true,_class:'pbl_roundedGroup',margin:'2px',center_overflow:'hidden'});
        var topbar = top._('SlotBar',{_class:'pbl_roundedGroupLabel',slots:'5,vtitle,*,activator_sql,5,clearConsole,5',side:'top'})
        topbar._('div','vtitle',{innerHTML:'RPC grid'})
        var sn = bc.getParentNode();
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
    showInspector:function(){
        if(!dijit.byId("gnr_devTools")){
             genro.dev.openInspector();
        }
    },

    shortcut: function(shortcut, callback, opt,sourceNode) {
        if(shortcut[0]=='@'){
            shortcut = shortcut.slice(1).split(':');
            shortcut = genro.getData('gnr.user_preference.sys.shortcuts.'+shortcut[0]) || shortcut[1];
            if(!shortcut){
                return;
            }
        }
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

                } else if(k=='cmd' || k=='command'){
                    if(e.metaKey) kp++;
                }
                else if (k == 'shift') {
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
        if (ele.addEventListener){
            ele.addEventListener(opt['type'], func, false);
            if(sourceNode){
                if(!sourceNode._shortcuts){
                    sourceNode._shortcuts = [];
                }
                sourceNode._shortcuts.push({args:[opt['type'], func, false],element:ele});
            }
        }
        else if (ele.attachEvent) ele.attachEvent('on' + opt['type'], func);
        else ele['on' + opt['type']] = func;
    },

    userObjectSave:function(sourceNode,kw,onSaved){
        var datapath = sourceNode.absDatapath(kw.metadataPath);
        var saveAs = objectPop(kw,'saveAs');
        var currentMetadata = genro.getData(datapath);
        var userObjectIsLoaded = currentMetadata && currentMetadata.getItem('code');
        var preview = objectPop(kw,'preview');
        var saveCb = function(dlg,evt,counter,modifiers){
            var data = new gnr.GnrBag();
            if(kw.dataIndex){
                for(var key in kw.dataIndex){
                    data.setItem(key,sourceNode.getRelativeData(kw.dataIndex[key]));
                }
                data.setItem('__index__',new gnr.GnrBag(kw.dataIndex));
            }else if(kw.dataSetter){
                funcApply(kw.dataSetter,{data:data},sourceNode);
            }
            var metadata = new gnr.GnrBag(kw.defaultMetadata);
            metadata.update(genro.getData(datapath));
            if (!metadata.getItem('code')){
                genro.publish('floating_message',{message:_T('Missing code'),messageType:'error'});
                return;
            }
            return genro.serverCall('_table.adm.userobject.saveUserObject',
                {'objtype':kw.objtype,'table':kw.table,flags:kw.flags,
                'data':data,metadata:metadata},
                function(result) {
                    if(dlg){
                        dlg.close_action();
                    }else{
                        var objname = result.attr.description || result.attr.code;
                        genro.publish('floating_message',{message:_T('Saved object '+objname)});
                    }
                    if(kw.loadPath){
                        sourceNode.setRelativeData(kw.loadPath, result.attr.code);
                    }
                    if(onSaved){
                        funcApply(onSaved,{result:result},sourceNode);
                    }
                    genro.setData(datapath,new gnr.GnrBag(result.attr));
                    return result;
                });
        };
        if(userObjectIsLoaded && !saveAs){
            return saveCb();
        }
        this.userObjectDialog(objectPop(kw,'title'),datapath,saveCb,preview);
    },

    userObjectLoad:function(sourceNode,kw){
        var metadataPath = objectPop(kw,'metadataPath');
        var onLoaded = objectPop(kw,'onLoaded');
        var onLoading = objectPop(kw,'onLoading');
        var resback = function(result){
            var resultValue,resultAttr,dataIndex;
            if(!result){
                resultValue = new gnr.GnrBag();
                resultAttr = objectUpdate({},kw.defaultMetadata);
                dataIndex = kw.dataIndex;
            }else{
                resultValue = result._value.deepCopy();
                resultAttr = objectUpdate({},result.attr);
                dataIndex = resultValue.pop('__index__');
            }
            if(onLoading){
                funcApply(onLoading,null,sourceNode,
                        ['dataIndex','resoultValue','resoultAttr'],
                        [dataIndex,resultValue,resultAttr]);
            }
            sourceNode.setRelativeData(metadataPath,new gnr.GnrBag(resultAttr));
            if(dataIndex){
                dataIndex.forEach(function(n){
                    sourceNode.setRelativeData(n.getValue(),resultValue.getItem(n.label));
                });
            }
            if(onLoaded){
                funcApply(onLoaded,null,
                        sourceNode,['dataIndex','resoultValue','resoultAttr'],
                        [dataIndex,resultValue,resultAttr]);
            }
        }; 
        if(kw.userObjectIdOrCode==='__newobj__'){
            return resback();
        }

        genro.serverCall('_table.adm.userobject.loadUserObject',kw,resback);
    },

    userObjectDialog:function(title,datapath,saveCb,preview){
        var dlg = genro.dlg.quickDialog(title);
        var center = dlg.center;
        var box = center._('div', {datapath:datapath,padding:'20px'});
        var fb = genro.dev.formbuilder(box, 2, {border_spacing:'6px'});
        fb.addField('textbox', {lbl:_T("Code"),value:'^.code',width:'10em'});
        fb.addField('checkbox', {label:_T("Private"),value:'^.private'});
        fb.addField('textbox', {lbl:_T("Name"),value:'^.description',width:'100%',colspan:2});
        fb.addField('textbox', {lbl:_T("Authorization"),value:'^.authtags',width:'100%',colspan:2});
        fb.addField('simpleTextArea', {lbl:_T("Notes"),value:'^.notes',width:'100%',height:'5ex',colspan:2,lbl_vertical_align:'top'});
        if(preview){
            fb.addField('button',{action:function(){
                var that = this;
                dlg.getParentNode().widget.hide(); 
                genro.dev.takePicture(function(data){
                    dlg.getParentNode().widget.show(); 
                    that.setRelativeData('.preview',data);
                });
            },label:_T('Screenshot')});
            fb.addField('br',{});
            fb.addField('img',{src:'^.preview',height:'50px',width:'200px',boder:'1px solid silver'});
        }
        var bottom = dlg.bottom._('div');
        var saveattr = {'float':'right',label:_T('Save')};        
        saveattr.action = function(evt,counter,modifiers){
            saveCb(dlg,evt,counter,modifiers);
        };
        bottom._('button', saveattr);

        var meta = genro.getData(datapath) || new gnr.GnrBag();
        if(meta.getItem('id') || meta.getItem('pkey')){
            var savecopy = {'float':'right',label:_T('Duplicate as')};        
            savecopy.action = function(evt,counter,modifiers){
                genro.getData(datapath).setItem('id',null);
                genro.getData(datapath).setItem('pkey',null);
                saveCb(dlg,evt,counter,modifiers);
            };
            bottom._('button', savecopy);
        }

        bottom._('button', {'float':'right',label:_T('Cancel'),action:dlg.close_action});
        dlg.show_action();
    },

    userObjectMenuData:function(kw,extraRows){
        if(extraRows){
            kw._onResult = function(result){
                var offset = result.len();
                if(offset){
                    result.setItem('r_'+offset,null,{caption:'-'});
                }
                offset+=1;
                extraRows.forEach(function(n,i){
                    result.setItem('r_'+(i+offset),null,n);
                });
            };
        }
        var resolver = genro.rpc.remoteResolver('_table.adm.userobject.userObjectMenu', kw);
        return resolver;
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
    },

    errorPalette:function(parent){
        if(!parent){
            var root = genro.src.newRoot();
            genro.src.getNode()._('div', '_helpdesk_');
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
                errors.push(errorNode.getValue());
            })
        })
        return errors.join('<br/><hr/>');
    },

    openHelpDesk:function(){
        var root = genro.src.newRoot();
        genro.src.getNode()._('div', '_helpdesk_');
        var parent = genro.src.getNode('_helpdesk_').clearValue();
        parent.freeze();
        genro.setData('gnr.helpdesk',new gnr.GnrBag());
        var pane = parent._('palettePane',{'paletteCode':'helpdesk','dockTo':false,
                                        title:_T('Helpdesk'),height:'550px',width:'400px',
                                        'z_index':100000});
        var sc = pane._('stackContainer',{selectedPage:'^.page',datapath:'gnr.helpdesk'});
        var pages = [['index',_T('Index'),true],['documentation',_T('Documentation')],
                    ['help',_T('Help')],['bug_report',_T('Report a bug')],
                    ['new_ticket',_T('New ticket'),true]];
        
        pages.forEach(function(page,idx){
            var bc = sc._('borderContainer',{'pageName':page[0]});
            var bottom;
            if(idx>0){
                bottom = bc._('contentPane',{region:'bottom',height:'40px'});
                if(!page[2]){ //nobutton
                    bottom._('lightbutton',{innerHTML:_T('Back'),action:"SET .page=pageName;",pageName:pages[0][0],
                                        _class:'helpdesk_btn helpdesk_footer',
                                        position:'absolute',left:'3px',top:'2px'});
                }
            }
            genro.dev['openHelpDesk_'+page[0]](bc._('contentPane',{region:'center'}),bottom,pages);
        });
        parent.unfreeze();
    },

    openHelpDesk_index:function(pane,bottom,pages){
        pages.forEach(function(p){
            var nobutton = p[2];
            if(nobutton){
                return;
            }
            pane._('lightbutton',{innerHTML:p[1],action:"SET .page=pageName;",pageName:p[0],
                                  _class:'helpdesk_btn helpdesk_'+p[0]});
        });
    },

    openHelpDesk_documentation:function(pane){

    },

    _helpDeskTicketTemplate : function(){
        var t = '';
            t += '<div class="helpdesk_ticket_top">';
                t += '<div class="helpdesk_ticket_subject">$subject</div>';
                t += '<div class="helpdesk_ticket_date">$date</div>';
            t += '</div>';
            t += '<div class"helpdesk_ticket_body">';
                t += '<div class"helpdesk_ticket_summary">$summary</div>';
            t += '</div>';
            t += '<div class"helpdesk_ticket_bottom">';
                t += '&nbsp;';
            t += '</div>';
        return t;
    },

    openHelpDesk_bug_report:function(pane,bottom){
        var template = this._helpDeskTicketTemplate();
        genro.serverCall('dev.getCurrentTickets',{},function(reported_tickets){
            if(reported_tickets){
                reported_tickets.forEach(function(n){
                    pane._('div',{innerHTML:dataTemplate(template,n.attr),_class:'helpdesk_ticket_box'});
                });
            }
            bottom._('lightbutton',{innerHTML:_T('New ticket'),'float':'right',_class:'helpdesk_btn helpdesk_footer',
                                    position:'absolute',right:'3px',top:'2px',action:'SET .page=pageName',pageName:'new_ticket'});
        });
    },
    openHelpDesk_new_ticket:function(pane,bottom){
        var fb = genro.dev.formbuilder(pane._('div',{margin:'5px'}), 1, {border_spacing:'6px',datapath:'.record'});
        fb.addField('textbox',{value:'^.title',lbl:_T('Subject'),width:'30em'});
        var sn = pane.getParentNode();

        genro.serverCall('dev.getNewTicketInfo',{},function(result){
            var priorities = result.getItem('priorities');
            var questions = result.getItem('questions');
            var locale = genro.locale();
            var lang = (locale=='it-IT')? 'it':'en';
            if(questions){
                questions = questions.getItem(lang);
                if (questions){
                    fb.addField('checkboxText',{value:'^.ticket_answers',values:questions,cols:1});
                }
            }
            if(result.getItem('tasks')){
                fb.addField('filteringSelect',{value:'^.task_id',values:result.getItem('tasks'),lbl:_T('Topic'),
                                placeholder:_T('Current page')});
            }
            fb.addField('filteringSelect',{value:'^.priority',values:priorities,lbl:_T('Priority')});
            fb.addField('simpleTextArea',{value:'^.notes',lbl:'Notes',
                                        lbl_vertical_align:'top',height:'80px',width:'300px'});
            fb.addField('button',{action:function(){
                var that = this;
                genro.wdgById('helpdesk_floating').hide();
                genro.dev.takePicture(function(data){
                    genro.wdgById('helpdesk_floating').show(); 
                    sn.setRelativeData('.record.screenshot',data);
                });
            },label:_T('Screenshot')});
            fb.addField('br',{});
            fb.addField('img',{src:'^.screenshot',height:'100px',width:'300px',boder:'1px solid silver'});

        });

        var savekw = {innerHTML:_T('Save ticket'),
                    _class:'helpdesk_btn helpdesk_footer',
                    position:'absolute',right:'3px',top:'2px'};
        savekw.action = function(){
            var record = sn.getRelativeData('.record');
            var extra_info = new gnr.GnrBag();
            /*ACTIVE FORM VIENE MESSA QUELLA DEL TICKET...
            if(genro.activeForm){
                var formInfo = new gnr.GnrBag();
                try {
                    formInfo.setItem('formId',genro.activeForm.formId);
                    formInfo.setItem('controller',genro.activeForm.getControllerData().deepCopy());
                    formInfo.setItem('record',genro.activeForm.getControllerData().deepCopy());
                    extra_info.setRelativeData('activeForm',formInfo.getFormData().deepCopy());
                } catch (error) {
                    console.log('error',error);
                    //
                }
            }
            */
            if(genro.getData('gnr.errors')){
                extra_info.setItem('js_errors',genro.getData('gnr.errors').deepCopy());
            }
            record.setItem('extra_info',extra_info);
            genro.serverCall('dev.saveNewTicket',{
                record:record
            },function(result){
                if(result && result.getItem('error')){
                    genro.dlg.floatingMessage(pane.getParentNode(),{message:result.getItem('error'),messageType:'error'});
                }else{
                    pane.getParentNode().setRelativeData('.record',new gnr.GnrBag());
                    genro.wdgById('helpdesk_floating').hide();
                }
            });
        }
        bottom._('lightbutton',savekw);
        bottom._('lightbutton',{innerHTML:_T('Back'),_class:'helpdesk_btn helpdesk_footer',
                                    action:'SET .page=pageName',pageName:'bug_report',
                                    left:'3px',top:'2px'});

    },



    openHelpDesk_help:function(pane){

    },

    takePicture:function(sendPars,onResult){
        genro.publish('onPageSnapshot',{setting:true});
        const divOffset = 1;
        var overlay = document.createElement('div');
        dojo.style(overlay,{position:'fixed',top:'0',bottom:'0',left:'0',right:'0',opacity:'.3',background:'white',zIndex:1000,cursor:'crosshair'});
        dojo.body().appendChild(overlay);
        var sel = document.createElement('div');
        dojo.style(sel,{position:'absolute',top:'0',width:'0',height:'0',display:'none',border:'2px solid black'});
        overlay.appendChild(sel);

        sendPars = sendPars || {uploadPath:'site:screenshots/'+genro.getData('gnr.pagename')};
        if(typeof(sendPars)=='string'){
             sendPars = {uploadPath:sendPars};
        }
        var pos = [0, 0];
        var x1,x2,y1,y2, xDif, yDif = 0;
        var isSelection, 
            isBottomRight, 
            isTopRight, 
            isTopLeft, 
            isBottomLeft = false

        dojo.connect(overlay,'mousedown',function(event){
            isSelection = true
            x1 = event.pageX - pos[0]
            y1 = event.pageY - pos[1]
            sel.style.setProperty('display', 'block')
            sel.style.setProperty('left', event.pageX + "px")
            sel.style.setProperty('top', event.pageY + "px")
            sel.style.setProperty('width', '0px')
            sel.style.setProperty('height', '0px')
        });

        dojo.connect(overlay,'mouseup',function(event){
           isSelection = false;
           if(isBottomRight){
             x2 = event.pageX - pos[0]
             y2 = event.pageY - pos[1]
             xDif = x2-x1
             yDif = y2-y1 
           } else if (isBottomLeft){
             y2 = event.pageY - pos[1]
             yDif = y2 - y1 

             xDif = x1 - x2
             x1 = x1 - xDif

           } else if(isTopRight){
             x2 = event.pageX - pos[0]
             xDif = x2 - x1 
             yDif = y1 - y2
             y1 = y1 - yDif         
           } else if (isTopLeft){
             xDif = x1 - x2
             x1 = x1 - xDif
             yDif = y1 - y2
             y1 = y1 - yDif         
           }
           sel.style.setProperty('display', 'none');
           dojo.body().removeChild(overlay);
           var onResultSnapshot = function(){
                if(onResult){
                    onResult();
                }
                genro.publish('onPageSnapshot',{setting:false});
           }
           var kw = {sendPars:sendPars,onResult:onResultSnapshot,crop:{x:x1,y:y1,deltaX:xDif,deltaY:yDif}};
           genro.dom.htmlToCanvas(dojo.body(),kw)
        });

        dojo.connect(overlay,'mousemove',function(event){
            if(isSelection){
                x2 = event.pageX - pos[0]
                y2 = event.pageY - pos[1]
                if(x2>x1 && y2>y1){ //moving right bottom selection
                  isBottomRight = true
                  isBottomLeft = false
                  isTopLeft = false
                  isTopRight = false
                  
                  xDif = x2 - x1
                  yDif = y2 - y1 

                  sel.style.setProperty('width', xDif + 'px')
                  sel.style.setProperty('height', yDif + 'px')
                } else if(x2<x1 && y2>y1){ //moving left bottom selection
                  isBottomLeft = true
                  isTopLeft = false
                  isTopRight = false
                  isBottomRight = false
                  
                  xDif = x1 - x2
                  yDif = y2 - y1 

                  sel.style.setProperty('left', x2 + 'px')
                  sel.style.setProperty('width', xDif + 'px')
                  sel.style.setProperty('height', yDif + 'px')
                  
                } else if(x2>x1 && y2<y1){
                  isTopRight = true
                  isTopLeft = false
                  isBottomLeft = false
                  isBottomRight = false

                  xDif = y1 - y2
                  yDif = x2 - x1 

                  sel.style.setProperty('top', y2 + 'px')
                  sel.style.setProperty('width', yDif + 'px')
                  sel.style.setProperty('height', xDif + 'px')
                } else if (x2<x1 && y2<y1){
                  isTopLeft = true
                  isTopRight = false
                  isBottomLeft = false
                  isBottomRight = false

                  yDif = y1 - y2 
                  xDif = x1 - x2

                  sel.style.setProperty('left', x2 + pos[0] + divOffset + 'px')
                  sel.style.setProperty('top', y2 + pos[1] + divOffset + 'px')
                  sel.style.setProperty('width', xDif  + 'px')
                  sel.style.setProperty('height', yDif  + 'px')
                }
        }})}

});
//dojo.declare("gnr.GnrViewEditor",null,{
//      constructor: function(widget){
//        this.widget = widget;
//      }
//});
