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

    removeFloatingMessage:function(sourceNode){
        sourceNode._value.popNode('_floatingmess');
    },

    makeFloatingMessage:function(sourceNode,kw){
        console.warn('Use floatingMessage instead of makeFloatingMessage');
        this.floatingMessage(sourceNode,kw);
    },

    floatingMessage:function(sourceNode,kw){
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
        var onClosedCb = objectPop(kw,'onClosedCb');
        if (onClosedCb){
            onClosedCb = funcCreate(onClosedCb,null,sourceNode)
        }
        var messageBox = sourceNode._('div','_floatingmess',{_class:'invisible fm_box fm_'+msgType,transition:transition}).getParentNode()
        kw.innerHTML = message;
        messageBox._('div',kw);
        var deleteCb = function(){
                                    that._value.popNode('_floatingmess');
                                    if(onClosedCb){
                                        onClosedCb();
                                    }
                                 };
        messageBox._('div',{_class:'dlg_closebtn',connect_onclick:deleteCb});
        genro.dom.centerOn(messageBox,sourceNode,xRatio,yRatio);
        var that = sourceNode;
        if(sound){
            genro.playSound(sound);
        }
        var t1 = setTimeout(function(){
                              genro.dom.removeClass(messageBox,'invisible');
                              setTimeout(function(){
                                    if(duration_out>0){
                                        var dt = duration_out/2;
                                        setTimeout(function(){
                                            genro.dom.addClass(messageBox,'invisible');
                                            setTimeout(function(){
                                                deleteCb();
                                            },dt*1000)
                                        },(dt*1000)+1)
                                    }
                                    
                              },(duration_in*1000)+1);
                            },1)

    },
    iframeDialog:function(iframeId,kw){
        var dialogId = iframeId+'_dlg';
        var dlgNode = genro.nodeById(dialogId)
        if(!dlgNode){
            var root = genro.src.getNode()._('div', '_dlg_iframe');
            var dlg = root._('dialog',{title:kw.title,closable:kw.closable,nodeId:dialogId});
            var iframekw = {src:kw.src,border:0,height:'100%',width:'100%',nodeId:iframeId};
            iframekw['selfsubscribe_close'] = "this.dialog.hide();"
            objectUpdate(iframekw,objectExtract(kw,'selfsubscribe_*',true,true));
            var iframe = dlg._('div',{height:kw.height,width:kw.width,overflow:'hidden'})._('iframe','iframe',iframekw);
            var dlgNode = dlg.getParentNode()
            dlgNode._iframeNode = iframe.getParentNode();
            dlgNode._iframeNode.dialog = dlgNode.widget;
            //create dlg and iframe
        }
        dlgNode.widget.show()
        if(kw.openKw){
            dlgNode._iframeNode.domNode.gnr.postMessage(dlgNode._iframeNode,kw.openKw);
        }
    },

    lightboxDialog:function(kwOrCb,onClosedCb){        
        genro.src.getNode()._('div', '_dlg_lightbox');
        var node = genro.src.getNode('_dlg_lightbox').clearValue().freeze();
        var onClosedCb = onClosedCb?funcCreate(onClosedCb):null;
        var dlg = node._('dialog',{_class:'lightboxDialog',nodeId:'_dlg_lightbox',connect_hide:function(){
            if(onClosedCb){
                onClosedCb.call(this);
            }
            genro.src.getNode('_dlg_lightbox').clearValue();
        }});
        dlg._('div',{_class:'dlg_closebtn',connect_onclick:'genro.wdgById("_dlg_lightbox").hide()',top:'-20px',right:'-20px'});
        if(typeof(kwOrCb)=='function'){
            kwOrCb(dlg);
        }else{
            dlg._(objectPop(kwOrCb,'tag'),kwOrCb);
        }
        node.unfreeze();
        genro.wdgById('_dlg_lightbox').show();
    },

    lightboxVideo:function(url,kw){
        this.lightboxDialog(function(dlg){
            kw = kw || {};
            var caption = objectPop(kw,'caption');
            
            var box = dlg._('div',{padding:'10px',background:'white',rounded:6});
            if(caption){
                dlg._('div',{innerHTML:caption,text_align:'center',color:'#999',font_weight:'bold'});
            }
            box._('htmliframe',objectUpdate({src:url,height:'500px',width:'600px',border:'0',nodeId:'_videoiframe_'},kw))
        },function(){
            genro.domById('_videoiframe_').setAttribute('src','');
        });
    },     


    alert:function(msg, title, buttons, resultPath, kw) {
        genro.src.getNode()._('div', '_dlg_alert');
        var title = title || '';
        var buttons = buttons || {confirm:'OK'};
        //var kw = objectUpdate({'width':'20em'}, kw);
        var kw = kw || {};
        var confirmCb = objectPop(kw,'confirmCb')
        var resultPath = resultPath;
        var node = genro.src.getNode('_dlg_alert').clearValue().freeze();
        var dlg = node._('dialog', objectUpdate({nodeId:'_dlg_alert', title:title, toggle:"fade", toggleDuration:250},kw))._('div', {_class:'dlg_ask',
            action:function(){
                genro.wdgById('_dlg_alert').hide();
                if(resultPath){
                    genro.fireEvent(resultPath,this.attr.actCode);
                }
                if(confirmCb){
                    funcApply(confirmCb);
                }
            }

        });
        dlg._('div', {'innerHTML':msg,'_class':'selectable dlg_ask_msg'});
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
        genro.dlg.alert(msgtext,title)
    },

    ask: function(title, msg, buttons, resultPathOrActions,kw) {
        genro.src.getNode()._('div', '_dlg_ask');
        var kw = kw || {};
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
        dlg._('div', {'content':msg,'_class':'selectable dlg_ask_msg',width:kw.width});
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
        if(level=='error'){
            if(!dojo.query('.countBoxErrors').length){
                return;
            }
        }
        dojo.publish("standardMsg", [
            {message: msg, type: level, duration: duration}
        ]);
    },

    remoteDialog:function(name,remote,remoteKw,dlgKw){
        var remoteKw = remoteKw || {};
        var dlgKw = dlgKw || {};
        dlgKw.nodeId = 'remote_dlg_'+name;
        var dlgNode = genro.nodeById(dlgKw.nodeId);
        if(!dlgNode){
            var dlg = genro.src.create('dialog',dlgKw,'_rmt_dlg');
            var kw = {};
            for (var k in remoteKw){
                kw['remote_'+k] = remoteKw[kw];
            }
            kw.min_height = '1px';
            kw.min_width = '1px';
            kw.remote = remote;
            console.log('remote pars',kw);
            dlg._('div',kw);
            dlgNode = dlg.getParentNode();
        }
        dlgNode.widget.show()
    },
    
    prompt: function(title, kw,sourceNode) {
        var kw = kw || {};
        var dlg_kw = objectExtract(kw,'dlg_*');
        var msg = kw.msg;
        var confirmCb = kw.action || '';
        var cancelCb = kw.cancelCb;
        var wdg = kw['widget'] || 'textbox';
        var remote = kw['remote'];
        var dflt = kw['dflt'];
        genro.setData('gnr.promptDlg.promptvalue',dflt || null);
        dlg_kw = objectUpdate({_showParent:true,width:'280px',datapath:'gnr.promptDlg',background:'white',autoSize:true},dlg_kw);
        var dlg = genro.dlg.quickDialog(title,dlg_kw);
        var mandatory = objectPop(kw,'mandatory');
        var bar = dlg.bottom._('slotBar',{slots:'*,cancel,confirm',action:function(){
                                                    dlg.close_action();
                                                    if(this.attr.command=='confirm'){
                                                        var v = genro.getData('gnr.promptDlg.promptvalue');
                                                        if(mandatory && isNullOrBlank(v)){
                                                            return;
                                                        }
                                                        funcApply(confirmCb,{value:genro.getData('gnr.promptDlg.promptvalue')},(sourceNode||this));
                                                        genro.setData('gnr.promptDlg.promptvalue',null);
                                                    }else if(this.attr.command == 'cancel' && cancelCb){
                                                        funcApply(cancelCb,{},(sourceNode||this));
                                                    }
                                                }});
        bar._('button','cancel',{'label':'Cancel',command:'cancel'});
        var confirmbtnKW = {'label':'Confirm',command:'confirm'};
        if(mandatory){
            confirmbtnKW.disabled = '^.promptvalue?=(#v==null) || (#v=="")';
        }
        bar._('button','confirm',confirmbtnKW);
        var kwbox = {padding:'10px'};
        if(remote){
            kwbox['remote'] = remote;
            objectUpdate(kwbox,objectExtract(kw,'remote_*',false,true));
            kwbox['remote_valuepath'] = '.promptvalue';
            dlg.center._('div',kwbox);
        }
        else{
            kwbox.width=dlg_kw.width;
            var box = dlg.center._('div',kwbox);
            if(msg){
                box._('div',{innerHTML:msg,color:'#666',margin_bottom:'10px',_class:'selectable'});
            }
            if(typeof(wdg)=='string'){
                var fb = genro.dev.formbuilder(box,1,{border_spacing:'1px',width:'100%',fld_width:'100%'});
                fb.addField(wdg,objectUpdate({value:'^.promptvalue',lbl:kw.lbl,lbl_color:'#666',lbl_text_align:'right'},objectExtract(kw,'wdg_*')));
            }else{
                var fb = genro.dev.formbuilder(box,1,{border_spacing:'4px',width:'100%',fld_width:'100%',datapath:'.promptvalue'});
                wdg.forEach(function(n){
                    var w = objectPop(n,'wdg','textbox');
                    fb.addField(w,objectUpdate({lbl_color:'#666',lbl_text_align:'right'},n));
                })
            }
        }
        dlg.show_action();

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
        dlg._('div', {'content':msg,'_class':'selectable dlg_ask_msg'});
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
        var kw = objectUpdate({},kw);
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
            setTimeout(function(){
                var ndlg =dlg.getParentNode();
                if(ndlg){
                    ndlg.getParentNode()._value.popNode(ndlg.label);
                }
            },500);
            
        };
        dlg.show_action = function() {
            var node = this.getParentNode().getParentNode();
            node.unfreeze();
            var wdg = this.getParentNode().widget;
            genro.callAfter(function(){
                wdg.show();
            },1);
        };
        return dlg;
    },
    
    zoomPaletteFromSourceNode:function(sourceNode,evt){
        var zoomAttr =sourceNode.evaluateOnNode(sourceNode.attr._zoomKw);
        var attr = sourceNode.currentAttributes();
        objectUpdate(zoomAttr,objectExtract(attr,'_zoomKw_*'));
        zoomAttr.evt = evt;
        var mode = objectPop(zoomAttr,'mode') || 'palette';

        if(mode=='palette'){
            this.zoomPalette(zoomAttr);
        }else if(mode=='page' && genro.root_page_id){
            var pageKw = {};
            zoomAttr['main_call'] = 'main_form';
            pageKw['file'] = this._prepareThIframeUrl(zoomAttr);
            pageKw['label'] = zoomAttr.title;
            pageKw['subtab'] = true;
            genro.mainGenroWindow.genro.publish('selectIframePage',pageKw);
        }
    },
    
    iframePalette:function(kw){
        var paletteCode=kw.paletteCode || 'external_'+genro.getCounter();
        var wdg = genro.wdgById(paletteCode+'_floating');
        if(wdg){
            wdg.show();
            wdg.bringToTop();
            return;
        }
        var zoomUrl = objectPop(kw,'url');
        genro.src.getNode()._('div',paletteCode,{_class:'hiddenDock'});
        var node = genro.src.getNode(paletteCode).clearValue();
        node.freeze();
        var paletteAttr = {'paletteCode':paletteCode,title:kw.title,overflow:'hidden',
                                                      dockTo:false,//'*:open',
                                                      width:'1px',height:'1px'
                                                     // palette_transition:'all .7s'
                                                      };
        if(kw.evt){
            paletteAttr.top=_px(evt.clientY);
            paletteAttr.left=_px(evt.clientX);
        }
        paletteAttr.palette_selfsubscribe_resize = "$1.top='100px';this.widget.setBoxAttributes($1);";
        objectUpdate(paletteAttr,kw);
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
        zoomAttr['pkey'] = grid.currRenderedRow[(zoomAttr['pkey'] ? zoomAttr['pkey'] : grid._identifier).replace(/\./g, '_').replace(/@/g, '_')];
        zoomAttr['main_call'] = 'main_form';
        zoomAttr['evt'] = evt;
        zoomAttr['title'] = grid.currRenderedRow[(cellattr['caption_field'] || cellattr['field']).replace(/\W/g, '_')]
        zoomAttr['url_th_linker'] =zoomAttr.linker || true;
        zoomAttr['paletteCode']  = zoomAttr['pkey']+(zoomAttr['formResource'] || '');
        var mode = objectPop(zoomAttr,'mode') || 'palette';

        if(mode=='palette'){
            this.zoomPalette(zoomAttr);
        }else if(mode=='page' && genro.root_page_id){
            var pageKw = {};
            pageKw['file'] = this._prepareThIframeUrl(zoomAttr);
            pageKw['label'] = zoomAttr.title;
            pageKw['subtab'] = true;
            genro.mainGenroWindow.genro.publish('selectIframePage',pageKw);
        }
    },

    zoomPage:function(kw){
        kw = kw || {};
        kw.main_call = kw.main_call || 'main_form';
        kw['file'] = this._prepareThIframeUrl(kw);
        kw['label'] = kw.title;
        kw['subtab'] = true;
        genro.mainGenroWindow.genro.publish('selectIframePage',kw)
    },

    floatingEditor:function(sourceNode,kw){
        kw = kw || {};
        var paletteCode = kw.paletteCode || 'floatingEditor_'+sourceNode.getStringId();
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
                            width:'800px',height:'400px',
                            maxable:true};
        var palette = node._('palettePane',paletteCode,paletteAttr);
        var valuepath = kw.valuepath || sourceNode.attr.innerHTML || sourceNode.attr.value;
        valuepath = '^'+sourceNode.absDatapath(valuepath);
        palette._('ckeditor',objectUpdate(kw,{value:valuepath}));
        node.unfreeze(); 
    },

    thIframePalette:function(kw,openKw){
        if(objectPop(kw,'rootPalette')){
            genro.mainGenroWindow.genro.dlg.thIframePalette(kw);
            return;
        }
        var table = kw.table;
        var evt = kw.evt;
        var paletteCode= kw.paletteCode || 'th_'+table.replace('.','_')+(kw.formResource || '')+(kw.main_call  || '');
        var paletteNode = genro.nodeById(paletteCode+'_floating');
        openKw = openKw || {};

        var openKw = objectUpdate(openKw,objectExtract(kw,'default_*',false,true));
        if(kw.pkey){
            openKw.pkey = objectPop(kw,'pkey');
        }
        if(paletteNode){
            paletteNode.widget.show();
            paletteNode.widget.bringToTop();
        }else{
            var zoomUrl = this._prepareThIframeUrl(kw); 
            genro.src.getNode()._('div',paletteCode,{_class:'hiddenDock'});
            var node = genro.src.getNode(paletteCode).clearValue();
            node.freeze();
            var dockTo = kw.dockTo || 'dummyDock:open';
            var paletteAttr = {'paletteCode':paletteCode,title:kw.title || 'Palette:'+table,
                                                        overflow:'hidden',
                                                          dockTo: dockTo,
                                                          width:'1px',height:'1px',
                                                          fixedPosition:true
                                                         // palette_transition:'all .7s'
                                                          };
            var paletteKwargs = objectExtract(kw,'palette_*');
            objectUpdate(paletteAttr,paletteKwargs);
            var palette = node._('palettePane',paletteCode,paletteAttr);
            var onSavedCb = objectPop(kw,'onSavedCb');
            var iframeNode = palette._('iframe',{'src':zoomUrl,height:'100%',width:'100%',border:0,onStarted:function(){
                var palette_height = '300px';
                var palette_width =  '500px';
                var paletteNode = palette.getParentNode();
                var wdg = paletteNode.getWidget();
                if(this._genro._rootForm){
                    palette_height = this._genro.getData('gnr.rootform.size.height') || palette_height;
                    palette_width = this._genro.getData('gnr.rootform.size.width') || palette_width;
                    if(kw.main_call=='main_form'){
                        this._genro._rootForm.subscribe('onDismissed',function(){if(!dockTo){wdg.close();}else{wdg.hide();}})
                    }
                    this._genro._rootForm.subscribe('onChangedTitle',function(kw){wdg.setTitle(kw.title)});
                }else if(kw.lookup){
                    this._genro.nodeById('lookup_root').subscribe('lookup_cancel',function(){wdg.close();});
                }
                if(onSavedCb){
                    this._genro._rootForm.subscribe('onSaved',function(kw){
                        onSavedCb(kw);
                    });
                }
                wdg.setBoxAttributes({height:palette_height,width:palette_width});
            }}).getParentNode();         
            node.unfreeze(); 
            var paletteNode = genro.nodeById(paletteCode+'_floating');
            paletteNode._iframeNode = iframeNode;
        }
        if(objectNotEmpty(openKw)){
            openKw.topic = openKw.topic || 'main_form_open';
            paletteNode._iframeNode.domNode.gnr.postMessage(paletteNode._iframeNode,openKw);
        }
    },

    _prepareThIframeUrl:function(kw){
        var prefix = kw.lookup? '/sys/lookuptables/':'/sys/thpage/';
        var zoomUrl = kw.zoomUrl || prefix+kw.table.replace('.','/');
        var urlKw = objectExtract(kw,'url_*');
        urlKw.th_public = objectPop(kw,'public') || false;
        if(kw.pkey){
            urlKw.th_pkey = kw.pkey; 
        }
        if(kw.formResource){
            urlKw.th_formResource = kw.formResource;
        }
        if(kw.viewResource){
            urlKw.th_viewResource = kw.viewResource;
        }
        if(kw.main_call){
            urlKw['main_call'] = kw.main_call;
        }
        if (kw.readOnly){
            urlKw['readOnly'] = kw.readOnly;
        }
        objectUpdate(urlKw,objectExtract(kw,'current_*',false,true));
        urlKw['th_from_package'] = genro.getData("gnr.package");
        urlKw['_parent_page_id'] = genro.page_id;
        return genro.addParamsToUrl(zoomUrl,urlKw); 
    },

    zoomPalette:function(kw){
        var evt = objectPop(kw,'evt');
        if(evt){
            kw['palette_top'] = _px(evt.clientY);
            kw['palette_left'] = _px(evt.clientX);
        }
        this.thIframePalette(kw);
    },

    quickPalette:function(paletteCode,kw,content){
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
        if(content){
            if(typeof(content)=='string'){
                palette._('div',{innerHTML:content});
            }else if(content instanceof gnr.GnrDomSourceNode){
                palette.setItem(content.label,content._value,content.attr);
            }else if(typeof(content)=='function'){
                content(palette);
            }else{
                var tag = objectPop(content,'tag') || 'div';
                palette._(tag,content);
            }
            
        }
        node.unfreeze();
        return palette.getParentNode();
    },

    lazyTip:function(domNode,rpcmethod){
        var kw = {};
        var k = 0;
        for (var i=2; i<arguments.length;i++){
            kw['p_'+k] = arguments[i];
            k++;
        }


        var to = setTimeout(function(){
            var result = genro.serverCall(rpcmethod,kw);
            domNode.setAttribute('title',result);
            domNode.setAttribute('onmouseover','');
        },1000);
        domNode.onmouseout = function(){
            clearTimeout(to);
        };
    },
    

    listChoice: function(title, msg, buttons, resultPath, valuePath, storePath) {
        genro.src.getNode()._('div', '_dlg_listChoice');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var node = genro.src.getNode('_dlg_listChoice').clearValue().freeze();
        var dlg = node._('dialog', {nodeId:'_dlg_listChoice',title:title})._('div', {_class:'dlg_ask',
            'action':"genro.wdgById('_dlg_listChoice').hide();genro.setData('" + resultPath + "',this.attr.actCode);"});
        dlg._('div', {'content':msg,'_class':'selectable dlg_ask_msg'});
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

