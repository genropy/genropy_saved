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

dojo.declare("gnr.GnrDlgHandler", null, {

    constructor: function(application) {
        this.application = application;
    },
    recordChange: function(record_path, selected_pkey) {
        var pkey_now = genro.getDataNode(record_path).attr.pkey;
        if (pkey_now == selected_pkey) {
            return true;
        } else {
            if (genro.getData(record_path).get_modified()) {
                var todo = request('vuoi salvare?');
                if (todo == 'salva') {
                    salva();
                    return true;
                } else if (todo == 'non salvare') {
                    return true;
                } else {
                    return false;
                }
            }
        }
    },
    dialog:function(msg, cb, buttons) {
        var root = genro.getNode()._('div', '_dlg');
        dlg = root._('dialog', 'dialogbox', {gnrId:'dialogbox', toggle:"fade", toggleDuration:250});
        dlg._('layoutcontainer', {height:'100%'});
        dlg._('contentpane', {'_class':'dojoDialogInner',layoutAling:'client'})._('span', {content:msg});
        var bottom = dlg._('contentpane', {layoutAling:'bottom'})._('div', {'align':'right'});
        var buttons = buttons || [
            {'caption':'OK', result:'OK'},
            {'caption':'cancel', result:'cancel'}
        ];
        for (btn in buttons) {
            btn.action = function() {
                genro.dialogbox.hide();
                cb(btn.result);
            };
            bottom._('button', btn);
        }
        dlg.show();
    },

    showMenuPane:function(nodeId) {
        //alert(nodeId);
        var root = genro.nodeById(nodeId);
        root.freeze();
        var mc = root._('contentPane', {'_class':'menucontainer','background_color':'red',
            'height':'3em',margin_left:'1em',margin_right:'1em',layoutAlign:'top'});
        /*var menunodes = genro.getData('gnr.pagemenu').getNodes();
         for (var i=0; i < menunodes.length; i++) {
         var title = menunodes[i].attr.title;
         var url = menunodes[i].attr.url;
         mc._('a',{content:title,href:url,margin:'1em'});
         };*/
        dojo.fx.wipeIn({node:root.getDomNode(),duration:1000}).play();

    },
    connectTooltipDialog:function(wdg, btnId) {
        dojo.connect(wdg, 'onclick', function(e) {
            genro.wdgById(btnId)._openDropDown(e.target);
        });
    },
    /*experimental*/
    genericWipePane:function(nodeId, msgpth, over) {
        var nodeId = nodeId || 'standardmsgpane';
        var msgpth = msgpth || 'gnr.message';
        var msg = genro.getData(msgpth);
        var root = genro.nodeById(nodeId);

        root.clearValue().freeze();
        if (over == true) {
            root.attr['z_index'] = 999;
            root.attr['position'] = 'absolute';

        }
        ;
        var mc = root._('div', {'background_color':'silver',
            'height':'3em',width:'400px'
        });
        mc._('span', {content:msg});
        var cb = function  (argument) {
            dojo.fx.wipeOut({node:root.getDomNode(),duration:1000}).play();
        };
        mc._('button', {label:'close',onClick:cb});
        root.unfreeze();
        dojo.fx.wipeIn({node:root.getDomNode(),duration:1000}).play();

    },

    createStandardMsg: function(domnode) {
        dojo.require("dojox.widget.Toaster");
        var toaster = new dojox.widget.Toaster({positionDirection:"tl-down",
            duration:1000,
            separator:'<hr>',
            messageTopic:'standardMsg'
        });
        dojo.connect(toaster, 'setContent', this, 'onMsgShow');
        domnode.appendChild(toaster.domNode);
        this.messanger = toaster;
    },

    onMsgShow: function() {
        if (this.messanger.forcedPos) {
            dijit.placeOnScreenAroundElement(genro.dlg.messanger.domNode, this.messanger.forcedPos, {'TL': 'BL', 'BL': 'TL'});
        }
    },


    alert:function(msg, title, buttons, resultPath, kw) {
        genro.src.getNode()._('div', '_dlg_alert');
        var title = title || '';
        var buttons = buttons || {confirm:'OK'};
        //var kw = objectUpdate({'width':'20em'}, kw);
        var kw = kw || {};
        var resultPath = resultPath || 'dummy';
        var node = genro.src.getNode('_dlg_alert').clearValue().freeze();
        var dlg = node._('dialog', objectUpdate({nodeId:'_dlg_alert', title:title, toggle:"fade", toggleDuration:250,centerOn:'_pageRoot'},kw))._('div', {_class:'dlg_ask',
            'action':"genro.wdgById('_dlg_alert').hide();genro.fireEvent('" + resultPath + "',this.attr.actCode);"});
        dlg._('div', {'innerHTML':msg,'_class':'dlg_ask_msg'});
        for (var btn in buttons) {
            dlg._('button', {'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_alert').show();
    },

    serverMessage: function(msgpath) {
        var msgnode = genro.getDataNode(msgpath);
        var msgtext = msgnode.getValue();
        var msgattr = msgnode.attr;
        //genro._data.setItem(msgpath, null, null, {'doTrigger':false});
        genro.src.getNode()._('div', '_dlg_alert');
        var node = genro.src.getNode('_dlg_alert').clearValue().freeze();
        var title = msgattr['title'] || 'Message from ' + msgattr['from_user'];
        var dlg = node._('dialog', {nodeId:'_dlg_alert', title:'', toggle:"fade", toggleDuration:250,centerOn:'_pageRoot'})._('div');
        var tbl = dlg._('table', {});
        tbl = tbl._('tbody', {});
        var r = tbl._('tr');
        r._('td', {content:'From'});
        r._('td', {})._('div', {innerHTML:msgattr['from_user']});
        r = tbl._('tr');
        r._('td', {content:'Message'});
        r._('td', {})._('div', {innerHTML:msgtext});
        node.unfreeze();
        genro.wdgById('_dlg_alert').show();
    },

    ask: function(title, msg, buttons, resultPathOrActions) {
        genro.src.getNode()._('div', '_dlg_ask');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var action;
        var node = genro.src.getNode('_dlg_ask').clearValue().freeze();
        if (typeof(resultPathOrActions) == 'string') {
            var resultPath = resultPathOrActions;
            var actions = {};
            action = "genro.wdgById('_dlg_ask').hide();genro.fireEvent('" + resultPath + "',this.attr.actCode);";
        }
        else {
            var actions = resultPathOrActions || {};
            action = "genro.wdgById('_dlg_ask').hide();if (this.attr.act){funcCreate(this.attr.act).call();};";
        }
        var dlg = node._('dialog', {nodeId:'_dlg_ask',title:title,centerOn:'_pageRoot'})._('div', {_class:'dlg_ask','action':action});
        dlg._('div', {'content':msg,'_class':'dlg_ask_msg'});
        //var buttonBox = dlg._('div', {'_class':'dlg_ask_btnBox'});

        for (var btn in buttons) {
            dlg._('button', {'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn,'act':actions[btn]});
        }
        node.unfreeze();
        genro.wdgById('_dlg_ask').show();
    },

    batchMonitor:function(thermopath) {
        var thermopath = thermopath || '_thermo';
        genro.src.getNode()._('div', '_thermo_floating');
        var node = genro.src.getNode('_thermo_floating').clearValue().freeze();
        var floatingPars = {};
        floatingPars.title = 'public floating';
        floatingPars._class = 'shadow_4';
        floatingPars.nodeId = 'batchMonitor';
        floatingPars.datapath = thermopath;
        floatingPars.top = '80px';
        floatingPars.left = '20px';
        floatingPars.width = '400px';
        floatingPars.closable = true;
        floatingPars.resizable = true;
        floatingPars.dockable = false;
        floatingPars.resizeAxis = 'y';
        floatingPars.maxable = false;
        floatingPars.duration = 400;
        var floating = node._('floatingPane', floatingPars);
        var container = floating._('div', {datapath:'.data','margin_bottom':'12px'});
        var create_thermoline = function(node, kw, i) {
            var innerpane = kw.pane._('div', {datapath:'.' + node.label});
            innerpane._('div', {innerHTML:'^.?message',font_size:'8px',text_align:'center',color:'black'});
            innerpane._('progressBar', {progress:'^.?progress',maximum:'^.?maximum',indeterminate:'^.?indeterminate',
                places:'^.?places',width:'100%',height:'10px',font_size:'9px'});

        };
        var create_thermopane = function(node, kw, i) {
            var innerpane = kw.pane._('div', {_class:'thermopane',border:'1px solid gray',
                margin:'2px',datapath:'.' + node.label});
            var titlediv = innerpane._('div', {background:'gray',color:'white',font_size:'9px',padding:'2px',height:'8px'});
            titlediv._('div', {innerHTML:'^.?thermotitle','float':'left'});
            titlediv._('a', {innerHTML:'Stop','float':'right'});
            var pane = innerpane._('div', {datapath:'.lines',padding:'3px'});
            var lines = node.getValue().getItem('lines');
            if (lines) {
                lines.forEach(create_thermoline, null, {'pane':pane});
            }
        };
        var thermobag = genro._(thermopath + '.data');
        thermobag.forEach(create_thermopane, null, {'pane':container});
        node.unfreeze();
        var bm = genro.wdgById('batchMonitor');
        dojo.connect(bm, 'close', function() {
            genro.setData('_thermo.monitor', false);
        });
        genro.setData('_thermo.monitor', true);
    },

    message: function(msg, position, level, duration) {
        this.messanger.forcedPos = position;
        var level = level || 'message';
        var duration = duration || 4000;
        dojo.publish("standardMsg", [
            {message: msg, type: level, duration: duration}
        ]);
    },
    
    
    prompt: function(title, kw,sourceNode) {
        var kw = kw || {};
        var msg = kw.msg;
        var confirmCb = kw.action || '';
        var wdg = kw['widget'] || 'textbox';
        var remote = kw['remote'];

        var dflt = kw['dflt'];
        var dlg = genro.dlg.quickDialog(title,{_showParent:true,width:'280px',datapath:'gnr.promptDlg',background:'white'});
        var bar = dlg.bottom._('slotBar',{slots:'*,cancel,confirm',action:function(){
                                                    dlg.close_action();
                                                    if(this.attr.command=='confirm'){
                                                        funcApply(confirmCb,{value:genro.getData('gnr.promptDlg.promptvalue')},(sourceNode||this));
                                                        genro.setData('gnr.promptDlg.promptvalue',null);
                                                    }
                                                }});
        bar._('button','cancel',{'label':'Cancel',command:'cancel'});
        bar._('button','confirm',{'label':'Confirm',command:'confirm'});
        var kwbox = {padding:'10px'};
        if(remote){
            kwbox['remote'] = remote;
            kwbox['remote_valuepath'] = '.promptvalue';
        }
        var box = dlg.center._('div',kwbox);
        if(!remote){
            if(msg){
                box._('div',{innerHTML:msg,color:'#666',margin_bottom:'10px'});
            }
            var fb = genro.dev.formbuilder(box,1,{border_spacing:'1px',width:'100%',fld_width:'100%'});
            fb.addField(wdg,objectUpdate({value:'^.promptvalue',lbl:kw.lbl,lbl_color:'#666'},objectExtract(kw,'wdg_*')));
        }
        dlg.show_action();
        if (dflt){
            genro.setData('gnr.promptDlg.promptvalue',dflt);
        }


    },
    paletteMap:function(kw) {
        var kw = kw || {};
        kw.paletteCode = kw.paletteCode || 'mapViewer';
        var paletteWdg = genro.wdgById(kw.paletteCode+'_floating');
        if(!paletteWdg){
            var node = objectPop(kw,'sourceNode');
            if(!node){
                genro.src.getNode()._('div', '_map_palette');
                var node = genro.src.getNode('_map_palette').clearValue();     
            }
            node.freeze();
            kw.dockTo = kw.dockTo || 'dummyDock:open';
            var paletteNode = node._('PaletteMap',kw).getParentNode();
            node.unfreeze();
            paletteWdg = paletteNode.getWidget();
        }else{
            paletteWdg.show();
        }
    },
    
    request: function(title, msg, buttons, resultPath, valuePath) {
        genro.src.getNode()._('div', '_dlg_request');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var node = genro.src.getNode('_dlg_request').clearValue().freeze();
        var dlg = node._('dialog', {nodeId:'_dlg_request',title:title})._('div', {_class:'dlg_ask',
            'action':"genro.wdgById('_dlg_request').hide();genro.setData('" + resultPath + "',this.attr.actCode);"});
        dlg._('div', {'content':msg,'_class':'dlg_ask_msg'});
        dlg._('textBox', {'value':'^' + valuePath});
        for (var btn in buttons) {
            dlg._('button', {'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_request').show();
    },
    floating: function(kw) {
        var float_id = kw.nodeId;
        genro.src.getNode()._('div', '_gnr_float_' + float_id);
        var node = genro.src.getNode('_gnr_float_' + float_id).clearValue();
        return node._('floatingPane', kw);
    },

    quickDialog: function(title,kw) {
        var kw = kw || {};
        genro.src.getNode()._('div', '_dlg_quick');
        var node = genro.src.getNode('_dlg_quick').clearValue();
        node.freeze();
        var kwdimension = objectExtract(kw,'height,width,background,padding');
        var dlg = node._('dialog', objectUpdate({title:title},kw));
        var box = dlg._('div',kwdimension)
        var center = box._('div', {_class:'pbl_dialog_center'});
        var bottom = box._('div', {_class:'dialog_bottom'});
        dlg.center = center;
        dlg.bottom = bottom;
        dlg.close_action = function() {
            dlg.getParentNode().widget.hide();
        };
        dlg.show_action = function() {
            node.unfreeze();
            var wdg = dlg.getParentNode().widget;
            genro.callAfter(function(){
                wdg.show();
            },1);
        };
        return dlg;
    },
    
    zoomPaletteFromSourceNode:function(sourceNode,evt,paletteKw){
        var paletteKw = paletteKw || {};
        var pkey = sourceNode.getRelativeData(sourceNode.attr.pkey);
        var paletteCode='external_'+sourceNode.getStringId();
        var wdg = genro.wdgById(paletteCode+'_floating');
        if(wdg){
            wdg.show();
            wdg.bringToTop();
            return;
        }
        var zoomUrl = '/'+sourceNode.attr.zoomUrl+'/'+pkey+'?th_public=false&&th_iframeContainerId='+paletteCode+'_floating';
        genro.src.getNode()._('div',paletteCode,{_class:'hiddenDock'});
        var node = genro.src.getNode(paletteCode).clearValue();
        node.freeze();
        var paletteAttr = {'paletteCode':paletteCode,title:'Palette:'+pkey,overflow:'hidden',
                                                      dockTo:false,//'*:open',
                                                      width:'1px',height:'1px'
                                                     // palette_transition:'all .7s'
                                                      };
        if(evt){
            paletteAttr.top=_px(evt.clientY);
            paletteAttr.left=_px(evt.clientX);
        }
        paletteAttr.palette_selfsubscribe_resize = "$1.top='100px';this.widget.setBoxAttributes($1);";
        objectUpdate(paletteAttr,paletteKw);
        var palette = node._('palettePane',paletteCode,paletteAttr);
        palette._('iframe',{'src':zoomUrl,height:'100%',width:'100%',border:0}); 
        node.unfreeze(); 
    },
    
    zoomFromCell:function(evt){
        var view = dijit.getEnclosingWidget(evt.target);
        view.content.decorateEvent(evt);
        var cellIndex = evt.cellIndex;
        var rowIndex = evt.rowIndex;
        var grid = view.grid;
        var structbag = grid.structbag();
        var cellattr = structbag.getNode('view_0.rows_0.#'+cellIndex).attr;
        var zoomAttr = objectExtract(cellattr,'zoom_*',true);
        zoomAttr['pkey'] = grid.currRenderedRow[zoomAttr['pkey'] ? zoomAttr['pkey'] : grid._identifier];
        zoomAttr['formOnly'] = true;
        zoomAttr['evt'] = evt;
        zoomAttr['title'] = grid.currRenderedRow[cellattr['field'].replace(/\W/g, '_')]
        var mode = objectPop(zoomAttr,'mode') || 'palette';
        if(mode=='palette'){
            this.zoomPalette(zoomAttr);
        }else if(mode=='page' && genro.root_page_id){
            var pageKw = {};
            pageKw['file'] = this._prepareZoomUrl(zoomAttr,true);
            pageKw['label'] = zoomAttr.title;
            pageKw['subtab'] = true;
            genro.mainGenroWindow.genro.publish('selectIframePage',pageKw)
        }
    },
    
    _prepareZoomUrl:function(kw,usepublic){
        var formOnly = 'formOnly' in kw? kw.formOnly:true;
        var zoomUrl = kw.zoomUrl || '/sys/thpage/'+kw.table.replace('.','/');
        var urlKw = objectUpdate({th_public:usepublic},objectExtract(kw,'url_*'));
        if(!formOnly){
            zoomUrl+'/'+kw.pkey;
        }else{
            urlKw['th_pkey'] = kw.pkey;
            urlKw['main_call'] = 'main_form';
            if(kw.formResource){
                urlKw['th_formResource'] = kw.formResource;
            }
        }
        return genro.addParamsToUrl(zoomUrl,urlKw); 
    },



    floatingEditor:function(sourceNode,kw){
        var paletteCode = 'floatingEditor_'+sourceNode.getStringId();
        var wdg = genro.wdgById(paletteCode+'_floating');
        if (wdg){
            wdg.show();
            wdg.bringToTop();
            return;
        }
        genro.src.getNode()._('div',paletteCode,{_class:'hiddenDock'});
        var node = genro.src.getNode(paletteCode).clearValue();
        node.freeze();
        var kw = kw || {};
        var paletteAttr = {'paletteCode':paletteCode,title:'Editor',
                            overflow:'hidden',
                            dockTo:'dummyDock:open',
                            width:'600px',height:'400px',
                            maxable:true};
        var palette = node._('palettePane',paletteCode,paletteAttr);
        var tc = palette._('tabcontainer');
        var editorpane = tc._('contentpane',{title:'Editor'});
        var previewpane = tc._('contentpane',{title:'Preview'});
        var valuepath = sourceNode.attr.innerHTML || sourceNode.attr.value;
        valuepath = '^'+sourceNode.absDatapath(valuepath);
        editorpane._('ckeditor',{value:valuepath});
        previewpane._('div',{innerHTML:valuepath,position:'absolute',top:'2px',left:'2px',right:'2px',bottom:'2px',background:'white',border:'1px solid silver'});
        node.unfreeze(); 
    },

    zoomPalette:function(kw){
        if(objectPop(kw,'rootZoom')){
            genro.mainGenroWindow.genro.dlg.zoomPalette(kw);
            return;
        }
        var pkey = kw.pkey;
        var table = kw.table;
        var evt = kw.evt;
        var paletteCode= kw.paletteCode || 'zoom_'+table.replace('.','_')+pkey;
        var wdg = genro.wdgById(paletteCode+'_floating');
        if(wdg){
            wdg.show();
            wdg.bringToTop();
            return;
        }
        var zoomUrl = this._prepareZoomUrl(kw,false); 
        genro.src.getNode()._('div',paletteCode,{_class:'hiddenDock'});
        var node = genro.src.getNode(paletteCode).clearValue();
        node.freeze();
        var paletteAttr = {'paletteCode':paletteCode,title:kw.title || 'Palette:'+pkey,
                                                    overflow:'hidden',
                                                      dockTo:'dummyDock:open',
                                                      width:'1px',height:'1px',
                                                      fixedPosition:true
                                                     // palette_transition:'all .7s'
                                                      };
        if(evt){
            paletteAttr.top=_px(evt.clientY);
            paletteAttr.left=_px(evt.clientX);
        }
        //paletteAttr.palette_selfsubscribe_resize = "$1.top='100px';this.widget.setBoxAttributes($1);";
        var palette = node._('palettePane',paletteCode,paletteAttr);
        var onSavedCb = objectPop(kw,'onSavedCb');
        palette._('iframe',{'src':zoomUrl,height:'100%',width:'100%',border:0,onStarted:function(){
            var palette_height = this._genro.getData('gnr.rootform.size.height');
            var palette_width = this._genro.getData('gnr.rootform.size.width');
            var wdg = palette.getParentNode().getWidget();
            wdg.setBoxAttributes({height:palette_height,width:palette_width});
            this._genro._rootForm.subscribe('onDismissed',function(){wdg.hide();})
            this._genro._rootForm.subscribe('onChangedTitle',function(kw){wdg.setTitle(kw.title)});
            if(onSavedCb){
                this._genro._rootForm.subscribe('onSaved',function(kw){
                    onSavedCb(kw);
                });
            }
        }}); 
        node.unfreeze(); 
    },

    quickPalette:function(paletteCode,kw,contentNode){
        var kw = kw || {};
        kw = objectUpdate({paletteCode:paletteCode,dockTo:'dummyDock:open'},kw);
        var wdg = genro.wdgById(paletteCode+'_floating');
        var evt = kw.evt;
        if(wdg){
            wdg.show();
            wdg.bringToTop();
            return;
        }
        genro.src.getNode()._('div',paletteCode,{_class:'hiddenDock'});
        var node = genro.src.getNode(paletteCode).clearValue();
        node.freeze();
        if(evt){
            kw.top=_px(evt.clientY);
            kw.left=_px(evt.clientX);
        }
        var palette = node._('palettePane',paletteCode,kw);
        if(contentNode){
            palette.setItem(contentNode.label,contentNode._value,contentNode.attr);
        }
        node.unfreeze();
        return palette.getParentNode();
    },
    

    listChoice: function(title, msg, buttons, resultPath, valuePath, storePath) {
        genro.src.getNode()._('div', '_dlg_listChoice');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var node = genro.src.getNode('_dlg_listChoice').clearValue().freeze();
        var dlg = node._('dialog', {nodeId:'_dlg_listChoice',title:title})._('div', {_class:'dlg_ask',
            'action':"genro.wdgById('_dlg_listChoice').hide();genro.setData('" + resultPath + "',this.attr.actCode);"});
        dlg._('div', {'content':msg,'_class':'dlg_ask_msg'});
        dlg._('filteringSelect', {'value':'^' + valuePath, 'storepath':storePath, 'ignoreCase':true});

        for (var btn in buttons) {
            dlg._('button', {'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_listChoice').show();
    },

    upload: function(title, method, resultPath, remotekw, label, cancel, send, fireOnSend) {
        /* first 3 params are mandatory */
        label = label || 'Browse...';
        cancel = cancel || 'Cancel';
        send = send || 'Send';
        var title = title;
        genro.src.getNode()._('div', '_dlg_ask');
        var node = genro.src.getNode('_dlg_ask').clearValue().freeze();
        var dlgRoot = node._('div');
        var baseId = node.getValue().getNodes()[0].getStringId();
        var kw = {width:'340px',height:'25px',margin:'15px',
            label:label,
            cancel:cancel,
            id:baseId + '_uploader',
            method:method,
            onUpload:'genro.setData("' + resultPath + '", $1);'};
        if (remotekw) {
            for (var par in remotekw) {
                kw['remote_' + par] = remotekw[par];
            }
        }

        var dlg = dlgRoot._('dialog', {id:baseId + '_dlg',title:title})._('div', {_class:'dlg_ask'});
        dlg._('div')._('fileInput', kw);

        var cb = function() {
            var dlgid = baseId + '_dlg';
            var uploaderid = baseId + '_uploader';
            dijit.byId(dlgid).onCancel();
            if (fireOnSend) {
                genro.fireEvent(fireOnSend);
            }
            dijit.byId(uploaderid).uploadFile();
        };

        dlg._('div')._('button', {label:send,margin_right:'15px',margin_bottom:'1px',
            onClick:cb});
        node.unfreeze();
        dijit.byId(baseId + '_dlg').show();
    }
});

