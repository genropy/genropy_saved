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
        var dlg=node._('dialog',{nodeId:'_dlg_alert', title:title, toggle:"fade", toggleDuration:250})._('div',{_class:'dlg_ask',
                                    'action':"genro.wdgById('_dlg_alert').hide();genro.fireEvent('"+resultPath+"',this.attr.actCode);"});
        dlg._('div',{'innerHTML':msg,'_class':'dlg_ask_msg'});
        var buttonBox = dlg._('div',{'_class':'dlg_ask_btnBox'});
        for (var btn in buttons){
            dlg._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_alert').show();
    },
    
    serverMessage: function(msg){
        genro.dlg.alert(msg,'Warning');
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
        var dlg=node._('dialog',{nodeId:'_dlg_ask',title:title})._('div',{_class:'dlg_ask','action':action});
        dlg._('div',{'content':msg,'_class':'dlg_ask_msg'});
        var buttonBox = dlg._('div',{'_class':'dlg_ask_btnBox'});

        for (var btn in buttons){
            dlg._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn,'act':actions[btn]});
        }
        node.unfreeze();
        genro.wdgById('_dlg_ask').show();
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
        /* first 4 params are mandatory */
        label=label || 'Browse...';
        cancel=cancel || 'Cancel';
        send=send || 'Send';
        var title = title;
        genro.src.getNode()._('div', '_dlg_ask');
        var node = genro.src.getNode('_dlg_ask').clearValue().freeze();
        var dlgRoot = node._('div');
        var baseId = node.getValue().getNodes()[0].getStringId();
        var kw = {width:'28em',height:'1.8em',margin:'15px','float':'left',
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
        dlg._('fileInput',kw);   
                          
        var cb = function(){
            var dlgid=baseId+'_dlg';
            var uploaderid=baseId+'_uploader';
            dijit.byId(dlgid).onCancel(); 
            if (fireOnSend){
                genro.fireEvent(fireOnSend);
            }
            dijit.byId(uploaderid).uploadFile();
        };
        
        dlg._('button',{label:send,margin_top:'15px',margin_top:'18px',
                        onClick:cb});
        node.unfreeze();
        dijit.byId(baseId+'_dlg').show();
    }
});

