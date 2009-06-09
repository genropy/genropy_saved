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
        dlg._('div',{'content':msg,'_class':'dlg_ask_msg'});
        var buttonBox = dlg._('div',{'_class':'dlg_ask_btnBox'});
        for (var btn in buttons){
            dlg._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
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
dojo.declare("gnr.GnrViewEditor",null,{
      constructor: function(nodeId, maintable, widgetNodeId){
        this.nodeId = nodeId;
        this.maintable=maintable;
        this.sourceNode=genro.nodeById(widgetNodeId);
        this.width_em = 10;
    },
    getStruct: function(view, subrow){
        var struct = this.sourceNode.getRelativeData(this.sourceNode.attr.structpath);
        if(view){
            struct = struct.getItem(view);
            if(subrow){
                struct = struct.getItem(subrow);
            }
        }
        return struct;
    },
    colsFromBag: function(){
        this.clearCols();
        setTimeout(dojo.hitch(this, 'buildCols'), 100);
    },
    clearCols: function(){
        var startNode = genro.nodeById(this.nodeId);
        var dndBag = startNode.getValue();
        if(dndBag.len()>0){
            dndBag.getNode('#0').dndSource.destroy();
        }
        startNode.clearValue();
    },
    buildCols: function(){
        var startNode = genro.nodeById(this.nodeId);
        startNode.freeze();
        var cols=this.getStruct('#0','#0').getNodes();
        
        var dndOnDrop = function(source, nodes, copy){
            var toPos = 0;
            var torebuild = false;
            var colsBag = genro.viewEditor.getStruct('#0','#0');
            if (this.targetAnchor){
                toPos = this.targetAnchor.sourceNode.attr.pos;
            } else if (colsBag.len()==0){
                toPos = 0;
            } else {
                return;
            }
            if(source.before){
                    toPos = toPos - 1;
            }

            if(source.tree){
                toPos = toPos + 1;
                var colNode = source.tree.getItemById(nodes[0].id);
                if(colNode.attr.tag == 'column' || colNode.attr.tag == 'virtual_column'){
                    colsBag.setItem('cellx_'+genro.getCounter(), null, {'width':'8em','name':colNode.attr.fullcaption, 
                                                    'dtype':colNode.attr.dtype, 'field':colNode.attr.fieldpath,
                                                    'tag':'cell'}, {'_position':toPos});
                }
                torebuild = true;
            } else {
                var fromPos = source.anchor.sourceNode.attr.pos;
                var sourceNode = colsBag.getNode('#'+fromPos);
                colsBag.delItem(sourceNode['label']);
                if(toPos < fromPos){
                    toPos = toPos + 1;
                }
                colsBag.setItem(sourceNode['label'], sourceNode['value'], sourceNode.attr, {'_position':toPos});
                this.parent.removeChild(nodes[0]);
                this.parent.insertBefore(nodes[0], this.parent.childNodes[toPos]);
            }
            this.onDndCancel();
            if(torebuild){
                genro.viewEditor.colsFromBag();
            }
        };
        var head, col, relpath, v, colattrs;
        var pane=startNode._('div',{'dnd_source':true,'dnd_singular':true, 'dnd_onDndDrop': dndOnDrop,
                                    'dnd_horizontal':true,'nodeId':'viewedit', 'dnd_accept':'data',
                                    datapath:'.#0.#0', width:((this.width_em+1) * (cols.length || 5))+ 'em', height:'100%'});
        for (var i=0; i < cols.length; i++) {
             col=cols[i];
             colattrs = col.attr;
             relpath='.'+col['label'];
             v = pane._('div',{'_class':'ve_cols','dnd_itemType':'cols', 'pos':i, 'width':this.width_em + 'em'});
             head = v._('div',{'_class':'ve_cols_label'})._('div',{innerHTML:'^'+relpath+'?name'});
             v._('div',{'_class':'icnBase10_Trash', 'float':'left', 'margin_top':'2px', 'margin_left':'6px', 
                           'connect_onclick':"genro.viewEditor.getStruct('#0','#0').delItem('"+col['label']+"');genro.viewEditor.colsFromBag();"});
     
             v._('div', {'_class':'icnBase10_Lens','float':'right', 'margin_right':'6px', 
                                    connect_onclick:function(evt){
                                        genro.setData('vars.editedColumn', this.absDatapath(this.attr.colpath));
                                        genro.wdgById('ve_colEditor')._openDropDown(evt.target);
                                    },
                                      'colpath':relpath});
        }
        startNode.unfreeze();
     },
     
     buildColEditor_OLD: function(){
         var fb=v._('table',{'border_spacing':'3px', 'font_size':'0.9em'})._('tbody',{});
         this.addDlgCell(fb, 'Name', 'textbox', {'value':'^'+relpath+'?name'});
         this.addDlgCell(fb, 'Width', 'textbox', {'value':'^'+relpath+'?width'});
     },
     addDlgCell_OLD: function(fb, lbl, tag, attrs){
        var dflt = {'width': '6em'};
        attrs = objectUpdate(dflt, attrs);
        r=fb._('tr');
        r._('td')._('div',{'content':lbl});
        r._('td')._(tag, attrs);
     }
});

dojo.declare("gnr.GnrQueryBuilder",null,{
    constructor: function(nodeId, maintable, datapath){
        this.nodeId = nodeId;
        this.maintable=maintable;
        this.datapath = datapath;
        genro.setDataFromRemote('gnr.qb.fieldstree',"app.relationExplorer", {table:maintable, omit:'_'});
        this.treefield = genro.getData('gnr.qb.fieldstree');
        genro.setDataFromRemote('gnr.qb.fieldsmenu',"app.relationExplorer", {table:maintable, omit:'_*'});
        genro.setDataFromRemote('gnr.qb.sqlop',"app.getSqlOperators");  
    },
    createMenues: function(){
        genro.src.getNode()._('div', '_qbmenues');
        var node = genro.src.getNode('_qbmenues');
        node.clearValue();
        node.freeze();
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.jc',id:'qb_jc_menu'});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.not',id:'qb_not_menu'});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.fieldsmenu',id:'qb_fields_menu'});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.op',id:'qb_op_menu'});
        node.unfreeze();
    },
    getCaption: function(optype,val){
        if (val){
            if (optype=='column'){
                return this.treefield.getAttr(val, 'fullcaption') || '&nbsp;';
            }
            else{
                return genro.getDataNode('gnr.qb.sqlop.'+optype+'.'+val).attr.caption;
            }
        }else{
            return '&nbsp;';
        }
    },
    buildQueryPane: function(startNode, datapath){
        var startNode = startNode || genro.nodeById(this.nodeId);
        var datapath = datapath || this.datapath;
        var querydata = genro.getData(datapath);
        startNode.clearValue();
        startNode.freeze();
        this._buildQueryGroup(startNode, querydata,0);
        startNode.unfreeze();
    },
    addDelFunc : function(mode, pos,e){
        var datapath,addblock;
        if (e){
            var target = e.target;
            addblock = e.altKey;
            datapath = target.sourceNode.absDatapath();
        }else{
            addblock=false;
            datapath=this.datapath;
        }
        var querybag = genro.getData(datapath);
        if(mode=='add'){
            if(addblock){
                querybag.setItem('new', null, {jc:'and'}, {_position:pos});
                querybag.setItem('new.c_0', null, {jc:'and'});
            } else {
                querybag.setItem('new', null, {jc:'and'}, {_position:pos});
            }
        }
        else {
            querybag.delItem('#'+pos);
        }
        var nodes = querybag.getNodes();
        for (var i=0; i < nodes.length; i++) {
            nodes[i]['label'] = 'c_'+i;
        };
        this.buildQueryPane();
    },
    createQuery:function(pars){  // Rifare con query more complesse
        var querybag = genro.getData(this.datapath);
        querybag.clear();
        querybag.setItem('c_0',0);
        querybag.setItem('c_0',pars.val,{op:pars.op,
                                 column:pars.column,
                                 op_caption:this.getCaption('op',pars.op),
                                 column_caption:this.getCaption('column',pars.column)});
        this.buildQueryPane();
    },
    _buildQueryRow: function(tr,node,i,level){
        var relpath = '.'+node.label;
        var val = node.getValue();
        var attr = node.getAttr();
        var noValueIndicator= "<span >&nbsp;</span>";
        attr.jc_caption = this.getCaption('jc',attr.jc) ;
        attr.not_caption = this.getCaption('not',attr.not) ;
        cell=tr._('td');
        if (i>0){
            cell._('div',{_class:'qb_div qb_jc floatingPopup',connectedMenu:'qb_jc_menu',selected_fullpath:relpath+'?jc',
                              selected_caption:relpath+'?jc_caption',innerHTML:'^'+relpath+'?jc_caption'});
        } else {
            attr.jc = '';
             //cell._('div',{_class:'qb_jc_noicn'});
        }
        tr._('td')._('div',{_class:'qb_div qb_not floatingPopup', connectedMenu:'qb_not_menu',selected_fullpath:relpath+'?not',
                           selected_caption:relpath+'?not_caption',innerHTML:'^'+relpath+'?not_caption'});
                 
        if(val instanceof gnr.GnrBag){
            cell = tr._('td', {colspan:'3',datapath:relpath});
            this._buildQueryGroup(cell, val,level+1);
        } else {
            attr.column_caption = this.getCaption('column',attr.column) ;
            attr.op_caption = this.getCaption('op',attr.op) ;
            tr._('td')._('div',{_class:'qb_div qb_field floatingPopup',connectedMenu:'qb_fields_menu',selected_fieldpath:relpath+'?column',
                            dnd_onDrop:"SET "+relpath+"?column_caption = item.attr.fullcaption;SET "+relpath+"?column = item.attr.fieldpath;",
                         dnd_allowDrop:"return !(item.attr.one_relation);",
                                selected_fullcaption:relpath+'?column_caption',innerHTML:'^'+relpath+'?column_caption'});
            tr._('td')._('div',{_class:'qb_div qb_op floatingPopup', connectedMenu:'qb_op_menu',selected_fullpath:relpath+'?op',
                                selected_caption: relpath+'?op_caption',innerHTML:'^'+relpath+'?op_caption'});
            tr._('td')._('div',{_class:'qb_div qb_value'})._('textbox',{value:'^'+relpath, width:'10em', _autoselect:true});
        }
        tr._('td')._('div',{connect_onclick:dojo.hitch(this,'addDelFunc','add',i+1), _class:'qb_btn qb_add'});
        if (i>0){
        tr._('td')._('div',{connect_onclick:dojo.hitch(this,'addDelFunc','del',i), _class:'qb_btn qb_del'});
        }             
         //tr._('td',{_class:'querybuilder_rem'})._('inlineeditbox',{value:'^.'+label+'?rem'});
     },

    _buildQueryGroup: function(sourceNode, querydata,level){
        var bagnodes = querydata.getNodes();
        var node;
        if (level%2==0){oddeven='qb_group qb_group_even';}else {oddeven='qb_group qb_group_odd';}
        var container = sourceNode._('div',{_class:oddeven});
        var tbl = container._('table', {_class:'qb_table'})._('tbody');
        for (var i=0; i < bagnodes.length; i++) {
            node = bagnodes[i];
            this._buildQueryRow(tbl._('tr'), bagnodes[i] , i, level);
        }
    },
    saveQueryDialog:function(title, actions, buttons, labels){
        var querypath=this.datapath;
        genro.src.getNode()._('div', '_dlg_savequery');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var labels = labels || {code:'Code', description:'Description', priv:'Private', tags:'Tags'};
        var node = genro.src.getNode('_dlg_savequery').clearValue().freeze();
        var dlg=node._('dialog',{nodeId:'_dlg_savequery',title:title})._('div',{_class:'dlg_ask'});

        var inputs = dlg._('div',{padding:'10px',font_size:'.8'})._('table',{border_spacing:'8px'})._('tbody');
        var tr;
        tr = inputs._('tr');
        tr._('td')._('div',{'innerHTML':labels['code'],_class:'gnrfieldlabel',font_weight:'bold'});
        tr._('td')._('textBox',{'value':'^'+querypath+'?code',width:'25em',_class:'gnrfield'});
        
        tr = inputs._('tr');
        tr._('td')._('div',{'innerHTML':labels['description'],_class:'gnrfieldlabel',font_weight:'bold'});
        tr._('td')._('textarea',{'value':'^'+querypath+'?description',width:'25em',border:'1px solid gray',_class:'gnrfield'});
        
        tr = inputs._('tr');
        tr._('td')._('div',{'innerHTML':labels['priv'],_class:'gnrfieldlabel',font_weight:'bold'});
        tr._('td')._('checkbox',{'value':'^'+querypath+'?private',_class:'gnrfield'});
        tr = inputs._('tr');
        tr._('td')._('div',{'innerHTML':labels['tags'],_class:'gnrfieldlabel',font_weight:'bold'});
        tr._('td')._('textBox',{'value':'^'+querypath+'?auth_tags',width:'25em',_class:'gnrfield'});
        
        var btns = dlg._('div',{'action':"genro.wdgById('_dlg_savequery').hide();if (this.attr.act){this.attr.act.call()}"});
        for (var btn in buttons){
            btns._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'act':actions[btn]});
        }
        node.unfreeze();
        genro.wdgById('_dlg_savequery').show();
    },
    
    deleteQueryDialog:function(title, actions, buttons,confirmMessage, noQueryMessage){
        var qnode = genro.getDataNode(this.datapath);
        var pkey = qnode.getAttr('id');
        if(pkey){
            genro.dlg.ask(title, confirmMessage.replace('$',qnode.getAttr('code')), buttons, actions);
        } else {
            genro.dlg.alert(noQueryMessage);
        }
    },
    doDelete:function(){
        genro.deleteUserObject(this.datapath);
        this.addDelFunc('add', 1);
        this.buildQueryPane();
    },

    _queryParametersDialog: function(kw, resultpath, title, buttons){
        var querypath=this.datapath;
        genro.src.getNode()._('div', '_dlg_loadquery');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var node = genro.src.getNode('_dlg_loadquery').clearValue().freeze();
        var dlg=node._('dialog',{nodeId:'_dlg_loadquery',title:title})._('div',{_class:'dlg_ask'});

        var inputs = dlg._('div',{padding:'10px',font_size:'.8'})._('table',{border_spacing:'8px'})._('tbody');
        
        var tr, path, attrs;
        for (path in kw) {
            attrs = kw[path];
        
            tr = inputs._('tr');
            tr._('td')._('div', {'innerHTML':attrs['column_caption'] + ' ' + attrs['op_caption'],
                                 _class:'gnrfieldlabel', font_weight:'bold'});
            tr._('td')._('textBox',{'value':'^'+querypath+'.'+path, width:'25em', _class:'gnrfield'});
        };
        var btns = dlg._('div',{'action':"genro.wdgById('_dlg_loadquery').hide();genro.setData('"+resultpath+"',this.attr.actCode);"});
        
        for (var btn in buttons){
            btns._('button',{'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_loadquery').show();
    }
});
