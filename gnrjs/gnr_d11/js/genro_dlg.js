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

dojo.declare("gnr.GnrDlgHandler",null,{
    
    constructor: function(application){
        this.application = application;
    },
    recordChange: function(record_path, selected_pkey){
        var pkey_now = genro.getDataNode(record_path).attr.pkey;
        if(pkey_now == selected_pkey){
            return true;
        } else {
            if (genro.getData(record_path).get_modified()){
                var todo = request('vuoi salvare?');
                if(todo=='salva'){
                    salva();
                    return true;
                } else if(todo=='non salvare'){
                    return true;
                } else {
                    return false;
                }
            }
        }
    },
    dialog:function(msg, cb, buttons){
        var root = genro.getNode()._('div', '_dlg');
        dlg = root._('dialog','dialogbox', {gnrId:'dialogbox', toggle:"fade", toggleDuration:250});
        dlg._('layoutcontainer',{height:'100%'});
        dlg._('contentpane', {'_class':'dojoDialogInner',layoutAling:'client'})._('span',{content:msg});
        var bottom = dlg._('contentpane',{layoutAling:'bottom'})._('div',{'align':'right'});
        var buttons = buttons || [{'caption':'OK', result:'OK'}, {'caption':'cancel', result:'cancel'}];
        for (btn in buttons){
            btn.action = function(){
                             genro.dialogbox.hide();
                             cb(btn.result);
                             };
            bottom._('button', btn);
        }
        dlg.show();
    },
   
    showMenuPane:function(nodeId){
        //alert(nodeId);
        var root = genro.nodeById(nodeId);
        root.freeze();
        var mc = root._('contentPane',{'_class':'menucontainer','background_color':'red',
                              'height':'3em',margin_left:'1em',margin_right:'1em',layoutAlign:'top'});
        /*var menunodes = genro.getData('gnr.pagemenu').getNodes();
        for (var i=0; i < menunodes.length; i++) {
            var title = menunodes[i].attr.title;
            var url = menunodes[i].attr.url;
            mc._('a',{content:title,href:url,margin:'1em'});
        };*/
        dojo.fx.wipeIn({node:root.getDomNode(),duration:1000}).play();
        
    },
    connectTooltipDialog:function(wdg,btnId){
        dojo.connect(wdg,'onclick',function(e){genro.wdgById(btnId)._openDropDown(e.target);});
    },
    /*experimental*/
    genericWipePane:function(nodeId,msgpth,over){
        var nodeId = nodeId || 'standardmsgpane';
        var msgpth = msgpth || 'gnr.message';
        var msg = genro.getData(msgpth);
        var root = genro.nodeById(nodeId);
    
        root.clearValue().freeze();
        if (over==true) {
            root.attr['z_index']=999;
            root.attr['position']='absolute';
            
        };
        var mc = root._('div',{'background_color':'silver',
                              'height':'3em',width:'400px'
                              });
        mc._('span',{content:msg});
        var cb = function  (argument) {
            dojo.fx.wipeOut({node:root.getDomNode(),duration:1000}).play();
        };
        mc._('button',{label:'close',onClick:cb});
        root.unfreeze();
        dojo.fx.wipeIn({node:root.getDomNode(),duration:1000}).play();
        
    },
        
    createStandardMsg: function(domnode){
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
    
    onMsgShow: function(){
        if(this.messanger.forcedPos){
           dijit.placeOnScreenAroundElement(genro.dlg.messanger.domNode, this.messanger.forcedPos,{'TL': 'BL', 'BL': 'TL'});
        }
    }, 
    
    alert:function(msg, title, buttons, resultPath, kw){
        genro.src.getNode()._('div', '_dlg_alert');
        var title = title || '';
        var buttons = buttons || {confirm:'OK'};
        var kw = objectUpdate({'width':'20em'},kw);
        var resultPath = resultPath || 'dummy';
        var node = genro.src.getNode('_dlg_alert').clearValue().freeze();
        var dlg=node._('dialog',{nodeId:'_dlg_alert', title:title, toggle:"fade", toggleDuration:250,centerOn:'_pageRoot'})._('div',{_class:'dlg_ask',
                                    'action':"genro.wdgById('_dlg_alert').hide();genro.fireEvent('"+resultPath+"',this.attr.actCode);"});
        dlg._('div',{'innerHTML':msg,'_class':'dlg_ask_msg'});
        var buttonBox = dlg._('div',{'_class':'dlg_ask_btnBox'});
        for (var btn in buttons){
            dlg._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_alert').show();
    },
    
    serverMessage: function(msgpath){
        var msgnode = genro.getDataNode(msgpath);
        var msgtext = msgnode.getValue();
        var msgattr = msgnode.attr;
        //genro._data.setItem(msgpath, null, null, {'doTrigger':false});
        genro.src.getNode()._('div', '_dlg_alert');
        var node = genro.src.getNode('_dlg_alert').clearValue().freeze();
        var title = msgattr['title'] || 'Message from '+msgattr['from_user'];
        var dlg=node._('dialog',{nodeId:'_dlg_alert', title:'', toggle:"fade", toggleDuration:250,centerOn:'_pageRoot'})._('div');
        var tbl = dlg._('table',{});
        tbl = tbl._('tbody',{});
        var r = tbl._('tr');
        r._('td',{content:'From'});
        r._('td',{})._('div',{innerHTML:msgattr['from_user']});
        r = tbl._('tr');
        r._('td',{content:'Message'});
        r._('td',{})._('div',{innerHTML:msgtext});   
        node.unfreeze();
        genro.wdgById('_dlg_alert').show();
    },
    
    ask: function(title, msg, buttons, resultPathOrActions){
        genro.src.getNode()._('div', '_dlg_ask');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var action;
        var node = genro.src.getNode('_dlg_ask').clearValue().freeze();
        if (typeof(resultPathOrActions)=='string'){
            var resultPath=resultPathOrActions;
            actions={};
            action="genro.wdgById('_dlg_ask').hide();genro.fireEvent('"+resultPath+"',this.attr.actCode);";
         }
         else{
             var actions=resultPathOrActions || {};
             action="genro.wdgById('_dlg_ask').hide();if (this.attr.act){funcCreate(this.attr.act).call();};";
         }
        var dlg=node._('dialog',{nodeId:'_dlg_ask',title:title,centerOn:'_pageRoot'})._('div',{_class:'dlg_ask','action':action});
        dlg._('div',{'content':msg,'_class':'dlg_ask_msg'});
        var buttonBox = dlg._('div',{'_class':'dlg_ask_btnBox'});

        for (var btn in buttons){
            dlg._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn,'act':actions[btn]});
        }
        node.unfreeze();
        genro.wdgById('_dlg_ask').show();
    },
    thermoFloating:function(thermopath){
        
    },
    batchMonitor:function(thermopath){
        var thermopath = thermopath || '_thermo';
        genro.src.getNode()._('div', '_thermo_floating');
        var node = genro.src.getNode('_thermo_floating').clearValue().freeze();
        var floatingPars = {};
        floatingPars.title='public floating';
        floatingPars._class='shadow_4';
        floatingPars.nodeId='batchMonitor';
        floatingPars.datapath=thermopath;
        floatingPars.top='80px';
        floatingPars.left='20px';
        floatingPars.width='400px';
        floatingPars.closable = true;
        floatingPars.resizable=true;
        floatingPars.dockable=false;
        floatingPars.resizeAxis='y';
        floatingPars.maxable=false;
        floatingPars.duration=400;
        var floating = node._('floatingPane',floatingPars)
        var container = floating._('div',{datapath:'.data','margin_bottom':'12px'})
        var create_thermoline = function(node,kw,i){
            var innerpane = kw.pane._('div',{datapath:'.'+node.label})
            innerpane._('div',{innerHTML:'^.?message',font_size:'8px',text_align:'center',color:'black'});
            innerpane._('progressBar',{progress:'^.?progress',maximum:'^.?maximum',indeterminate:'^.?indeterminate',
                                places:'^.?places',width:'100%',height:'10px',font_size:'9px'});
            
        };
        var create_thermopane = function(node,kw,i){
            var innerpane = kw.pane._('div',{_class:'thermopane',border:'1px solid gray',
                                margin:'2px',datapath:'.'+node.label});
            var titlediv = innerpane._('div',{background:'gray',color:'white',font_size:'9px',padding:'2px',height:'8px'});
            titlediv._('div',{innerHTML:'^.?thermotitle','float':'left'});
            titlediv._('a',{innerHTML:'Stop','float':'right'});
            var pane = innerpane._('div',{datapath:'.lines',padding:'3px'});
            var lines = node.getValue().getItem('lines');
            if(lines){
                lines.forEach(create_thermoline,null,{'pane':pane});
            }
        };
        var thermobag = genro._(thermopath+'.data');
        thermobag.forEach(create_thermopane,null,{'pane':container});
        node.unfreeze();
        var bm=genro.wdgById('batchMonitor')
        dojo.connect(bm,'close',function(){genro.setData('_thermo.monitor',false)})
        genro.setData('_thermo.monitor',true)
    },
    
    message: function(msg, position,level, duration ){
        this.messanger.forcedPos = position;
        var level = level|| 'message';
        var duration = duration || 4000;
        dojo.publish("standardMsg",[ {message: msg, type: level, duration: duration}]);
    },
    
    
    request: function(title, msg, buttons, resultPath, valuePath){
        genro.src.getNode()._('div', '_dlg_request');
        var buttons=buttons || {confirm:'Confirm',cancel:'Cancel'};
        var node = genro.src.getNode('_dlg_request').clearValue().freeze();
        var dlg=node._('dialog',{nodeId:'_dlg_request',title:title})._('div',{_class:'dlg_ask',
                                    'action':"genro.wdgById('_dlg_request').hide();genro.setData('"+resultPath+"',this.attr.actCode);"});
        dlg._('div',{'content':msg,'_class':'dlg_ask_msg'});
        dlg._('textBox',{'value':'^'+valuePath});
        for (var btn in buttons){
            dlg._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_request').show();
    },
    
    listChoice: function(title, msg, buttons, resultPath, valuePath, storePath){
        genro.src.getNode()._('div', '_dlg_listChoice');
        var buttons=buttons || {confirm:'Confirm',cancel:'Cancel'};
        var node = genro.src.getNode('_dlg_listChoice').clearValue().freeze();
        var dlg=node._('dialog',{nodeId:'_dlg_listChoice',title:title})._('div',{_class:'dlg_ask',
                                    'action':"genro.wdgById('_dlg_listChoice').hide();genro.setData('"+resultPath+"',this.attr.actCode);"});
        dlg._('div',{'content':msg,'_class':'dlg_ask_msg'});
        dlg._('filteringSelect',{'value':'^'+valuePath, 'storepath':storePath, 'ignoreCase':true});
                                      
        for (var btn in buttons){
            dlg._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_listChoice').show();
    },
    
    upload: function(title,method,resultPath,remotekw,label,cancel,send,fireOnSend){
        /* first 3 params are mandatory */
        label=label || 'Browse...';
        cancel=cancel || 'Cancel';
        send=send || 'Send';
        var title = title;
        genro.src.getNode()._('div', '_dlg_ask');
        var node = genro.src.getNode('_dlg_ask').clearValue().freeze();
        var dlgRoot = node._('div');
        var baseId = node.getValue().getNodes()[0].getStringId();
        var kw = {width:'340px',height:'25px',margin:'15px',
                           label:label,
                           cancel:cancel,
                           id:baseId+'_uploader',
                           method:method,
                           onUpload:'genro.setData("'+resultPath+'", $1);'};
        if(remotekw){
            for (var par in remotekw){
                kw['remote_'+par] = remotekw[par];
            }
        }
                           
        var dlg = dlgRoot._('dialog',{id:baseId+'_dlg',title:title})._('div',{_class:'dlg_ask'});
        dlg._('div')._('fileInput',kw);   
                          
        var cb = function(){
            var dlgid=baseId+'_dlg';
            var uploaderid=baseId+'_uploader';
            dijit.byId(dlgid).onCancel(); 
            if (fireOnSend){
                genro.fireEvent(fireOnSend);
            }
            dijit.byId(uploaderid).uploadFile();
        };
        
        dlg._('div')._('button',{label:send,margin_right:'15px',margin_bottom:'1px',
                        onClick:cb});
        node.unfreeze();
        dijit.byId(baseId+'_dlg').show();
    }
});

