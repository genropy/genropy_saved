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


dojo.declare("gnr.GnrDevHandler",null,{
    
    constructor: function(application){
        this.application=application;
    },
    editSourceNode: function (treenode){
        var sourceNode = this.application.getDataNode(treenode);
        var dest=genro.inspector_struct_pane.sourceNode;
        var form = dest.getValue();
        var r,c;
        var nodeAttr=sourceNode.getAttr();
        dest.setValue(null,false);
        form.clear();
        var tbody=form._('table')._('tbody');
        var tagParameters=this.application.wdg.tagParameters[nodeAttr.tag.toLowerCase()];
        var currBag = new gnr.GnrBag();

         if (tagParameters){
              for (var par in tagParameters){
                  var r = tbody._('tr');
                  r._('td',{'content':par});
                  var v = tagParameters[par].split(':');
                  var c=r._('td');
                  if(v[0]=='input'){
                      c._('input',{datasource:':'+par});
                  }
                  currBag.setItem(par,null);
              }
         }
         for(var i=0; i<this.application.dom.styleAttrNames.length; i++){
             var stl = this.application.dom.styleAttrNames[i];
             var r = tbody._('tr');
             r._('td',{'content':stl});
             var c=r._('td');
             c._('input',{datasource:':'+stl});
             currBag.setItem(stl,null);
         }


         for (attr in nodeAttr){
             if(attr!='tag'){
                 if(currBag.index(attr)<0){
                     var r = tbody._('tr');
                     r._('td',{'content':attr});
                     var c=r._('td');
                     c._('input',{datasource:':'+attr});
                 }
                 currBag.setItem(attr,nodeAttr[attr]);
             }
         }
         currBag['editedNode']= sourceNode;
         currBag.subscribe('sourceTriggers',{'any':{obj:this,func:'editSourceNode_trigger'}
                                               });
         dest.setValue(form);
         genro.setData('currentnode',currBag);
         
     },
     
    editSourceNode_trigger: function(kw){
        var currBagNode = kw.node;
        var sourceNode = currBagNode.getParentBag().editedNode;
        var newValue=currBagNode.getValue() || null;
        var nodeAttrs=objectUpdate({},sourceNode.getAttr());
        var attrname=currBagNode.label;
        if(kw.evt=='upd_del' || newValue==null){
            delete(nodeAttrs[attrname]);
        }else{
            nodeAttrs[attrname]=newValue;
        }
        sourceNode.setAttr(nodeAttrs);
    },
    srcInspector:function(node){
        var showInspector=function(domnode){
            var sourceNode=domnode.sourceNode;
            if (!sourceNode){
                var wdg=dijit.getEnclosingWidget(domnode);
                    if (wdg){sourceNode=wdg.sourceNode;}
            }
            if(sourceNode){
                var showDict = objectUpdate({}, sourceNode.attr);
                showDict.absDatapath = sourceNode.absDatapath();
                return genro.dev.dictToHtml(showDict, 'bagAttributesTable');
            }else{
                return 'No sourceNode';
            }
        };
        genro.wdg.create('tooltip',null,{label:showInspector,
                                         modifiers:'alt'
                                        }).connectOneNode(node);   
    },
    
    debugMessage: function(msg, level, duration){
        
        var level = level|| 'MESSAGE';
        var duration = duration|| 50 ;
        dojo.publish("standardDebugger",{message: msg, type:level.toUpperCase(), duration:duration});
    },
    handleRpcHttpError:function(response, ioArgs){
        var xhr=ioArgs.xhr;
        var status = xhr.status;
        var statusText = xhr.statusText;
        var readyState = xhr.readyState;
        var responseText = xhr.responseText;
        if (status==400) {
            genro.dlg.alert('Client HTTP error');
            genro.pageReload();
            return;
        }
        else if (status==412) {
            genro.dlg.alert('No longer existing page');
            genro.pageReload();
            return;
        }else if(status==0){
            //genro.dlg.alert('Site temporary un available. Retry later');
             
             var msg='status: '+ xhr.status+' - statusText:'+xhr.statusText+' - readyState:'+xhr.readyState+' - responseText:'+responseText;
             console.log(ioArgs.url);
             console.log(msg);
             console.log (ioArgs);
            
        }
        else
        {
            console.log('handleRpcHttpError');
            debug_url = ioArgs.xhr.getResponseHeader('X-Debug-Url');
            if (!debug_url){
                genro.dlg.message("An HTTP error occurred: " + response.message, null,'error' );
            }
            else
            {
            genro.openWindow(debug_url,'Internal Server Error',{scrollbars:'yes'});
            }
        }
    },
    handleRpcError:function(error, envNode){
        if (error=='expired'){
            genro.dlg.message('expired session');
            genro.pageReload();
        }
        else if (error=='clientError'){
            genro.dlg.alert('clientError');
                //throw result;
        } else if (error=='serverError'){
            var root = genro.src.newRoot();
            var fpane = root._('dialog','traceback', {title:'Trace',nodeId:'traceback_main',_class:'tracebackDialog'});
            fpane.setItem('',envNode.getValue()); 
                                            
            genro.src.setSource('traceback',root);
            genro.wdgById('traceback_main').show();
        }
    },
        
    formbuilder:function(node,col,tblattr){
        var tbl = node._('table',tblattr||{})._('tbody');
        tbl.col_max = col || 1;
        tbl.col_count = tbl.col_max +1;
        tbl.addField = function(tag,kw){
            if(this.col_count>this.col_max){
                this.curr_tr = this._('tr');
                this.col_count = 1;
            }
            var lblpars = {innerHTML:objectPop(kw,'lbl')};
            objectUpdate(lblpars,objectExtract(kw,'lbl_*'));
            var tr = this.curr_tr;
            tr._('td',lblpars);
            tr._('td')._(tag,kw);
            this.col_count = this.col_count+1;
        };
        return tbl;
    },
    
    relationExplorer:function(table,title,rect){
        var rect=rect || {'top':'10px','right':'10px','height':'300px','width':'200px'};
        var code = table.replace('.','_');
        genro.src.getNode()._('div', '_relationExplorer_'+code);
        var node = genro.src.getNode('_relationExplorer_'+code).clearValue();
        node.freeze();
        var path = 'gnr.relation_explorers.'+table;
        genro.setData(path,
                     genro.rpc.remoteResolver('relationExplorer',{'table':table}));
        var fpane = node._('floatingPane',{title:title,top:rect.top,bottom:rect.bottom,
                                                          left:rect.left,right:rect.right,
                                                          height:rect.height,width:rect.width,
                                                      resizable:true,dockable:false,_class:'shadow_4',
                                                      closable:true});
       var treeattr = {storepath:path,margin:'4px'};
       treeattr.labelAttribute='caption';
       treeattr._class='fieldsTree';
       treeattr.hideValues=true;
       treeattr.onDrag = function(dragValues,dragInfo,treeItem){
                                if(!(treeItem.attr.dtype && treeItem.attr.dtype!='RM' && treeItem.attr.dtype!='RO')){
                                    return false;
                                }
                               var fldinfo=objectUpdate({},treeItem.attr);
                               fldinfo['maintable']=table;
                               dragValues['text/plain']=treeItem.attr.fieldpath;
                               dragValues['gnrdbfld_'+code]=fldinfo; 
        };
        treeattr.draggable=true;
        treeattr.getIconClass='if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}';                                       
        fpane._('tree',treeattr);
        node.unfreeze();
        fpane.getParentNode().widget.bringToTop();
    },
        
    openInspector:function(){
        var root=genro.src.newRoot();
        this.application.setData('_dev.dbstruct',null,{remote:"app.dbStructure"});
        var fpane = root._('floatingPane','inspector',{title:'Debug',top:'100px',left:'100px',height:'300px',width:'400px',
                                                      resizable:true,maxable:true,dockable:false,
                                                      closable:true,gnrId:'inspector_main'});
                          
       var accordion=fpane._('accordionContainer',{height:'100%'});
       accordion._('accordionPane',{title:'Data'})._('tree',{ gnrId:'inspector_data',datasource:'*D'});
       var structInsp=fpane._('accordionPane',{title:'Structure'});
       var splitter=structInsp._('SplitContainer', {height:'100%'});
       splitter._('ContentPane',{sizeShare:30})._('tree',{gnrId:'inspector_struct',datasource:'*S'});
       splitter._('ContentPane',{sizeShare:70, gnrId:'inspector_struct_pane',background_color:'silver', datasource: 'currentnode'})._('div');
       accordion._('accordionPane',{title:'Widgets'})._('tree',{gnrId:'inspector_widgets', datasource:'_dev.widgets'});
       accordion._('accordionPane',{title:'Db Structure'})._('tree',{gnrId:'inspector_db', datasource:'_dev.dbstruct'});
       dojo.connect(genro.inspector_struct,'onSelect', function(treenode){genro.dev.editSourceNode(treenode);});
       genro.src.setInRootContainer('inspector',root.getNode('inspector'));
    },
    openLocalizer:function(){
        noValueIndicator = "<span >&nbsp;</span>";
        genro.src.getNode()._('div', '_localizer');
        var node = genro.src.getNode('_localizer').clearValue().freeze();
        genro.setData('gnr.pageLocalization',genro.rpc.remoteCall('localizer.pageLocalizationLoad'));
        var dlg=node._('dialog',{nodeId:'_localizer',title:'Localizer',width:'40em','padding':'2px'});
        var xx=dlg._('div',{height:'400px',overflow:'auto',background_color:'#eee',border:'1px inset'});
        var saveData=function(){
            var data=genro.getData('gnr.pageLocalization');
            var cb=function(){
                genro.pageReload();
            };
            genro.rpc.remoteCall('localizer.pageLocalizationSave',{data:data},'bag','POST',null,cb);
        };
        dlg._('button',{label:'Save',margin:'4px','float':'right',onClick:saveData});
        var nodes=genro.getData('gnr.pageLocalization').getNodes();
        var tbl=xx._('table',{_class:'localizationTable',width:'100%'});
        var thead=tbl._('thead');
        var r=thead._('tr');
        r._('th',{content:'Key'});
        r._('th',{content:'Value'});
        var tbody=tbl._('tbody');
        for(var i=0; i<nodes.length; i++){
            var r=tbody._('tr',{datapath:'gnr.pageLocalization.r_'+i});
            r._('td',{width:'15em'})._('div',{innerHTML:'^.key'});
            r._('td')._('inlineeditbox',{value:'^.txt',noValueIndicator:noValueIndicator});
        }
        node.unfreeze();
        genro.wdgById('_localizer').show();
    },
    printUrl: function(url){
        genro.dev.deprecation("genro.dev.printUrl(url)","genro.download(url,'print')");
        genro.download(url,null,'print');
        /*genro.src.getNode()._('div', '_printframe');
        var node = genro.src.getNode('_printframe').clearValue().freeze();
        frm = node._('iframe', {'src':url, connect_onload:"genro.dom.iFramePrint(this.domNode);", 
                                          display:'hidden', width:'0px', height:'0px'});
        node.unfreeze();*/
    },
    exportUrl: function(url){
        genro.dev.deprecation('genro.dev.exportUrl','genro.download');
        genro.download(url);
        // USELESS, USE download(url) instead of this
/*        genro.src.getNode()._('div', '_printframe');
        var node = genro.src.getNode('_printframe').clearValue().freeze();
        frm = node._('iframe', {'src':url, display:'hidden', width:'0px', height:'0px'});
        node.unfreeze();*/
    },
    deprecation:function(oldval,newval){
        console.warn('Deprecation warning: '+oldval+' was replaced with '+newval,'WARNING');
        //this.debugMessage('Deprecation warning: '+oldval+' was replaced with '+newval,'WARNING');
    },
    dataDebugTrigger : function(kw){
        var path=kw.pathlist.join('.');
        var msg= "A bag trigger : "+ kw.evt;
        if (kw.evt=='upd_value'){
           var msg= "The value of node '"+path+"' was changed from "+kw.oldvalue+" to "+ kw.node.getValue();
        }
        else if(kw.evt=='ins'){
            var msg= "A node was inserted at path '"+path+"' position="+kw.ind+" value="+ kw.node.getValue();
        }
        else if(kw.evt=='del'){
            var msg= "A node was deleted at path '"+path+"' position="+kw.ind+" oldvalue="+ kw.node.getValue();
        }
        dojo.publish("triggerBag",{message: msg});
    },
    getSourceBlock: function(path){
        var node = this.application.source.getNode(path, false, true, new gnr.GnrDomSource());
        if (node){
            var block = node.getValue();
            if (!block){
                block = new gnr.GnrDomSource();
                node.setValue(block,false);
            }
            return block;
        }
    },
    dictToHtml:function(obj,tblclass){
        var result=["<table class='"+tblclass+"'><thead><tr><th>Name</th><th>Value</th></tr></thead><tbody>"];
        for (key in obj){
            result.push("<tr><td>"+key+"</td><td>"+obj[key]+"</td></tr>");
        }
        result.push("</tbody></table>");
        return result.join('\n');
    },
    bagAttributesTable : function(node){
        var item=dijit.getEnclosingWidget(node).item;
        if (item){
            return genro.dev.dictToHtml(item.attr,'bagAttributesTable');
        }
    },
    showDebugger: function(){
        var open = genro._data.getItem('_clientCtx.mainBC.right?show');
        genro._data.setItem('_clientCtx.mainBC.right?show', !open);
    },
    showBottomHelper: function(){
        var open = genro._data.getItem('_clientCtx.mainBC.bottom?show');
        genro._data.setItem('_clientCtx.mainBC.bottom?show', !open);
    },
    shortcut: function(shortcut,callback,opt){
        var default_options = {
            'type':'keydown',
            'propagate':false,
            'target':document
        };
        if(!opt) opt = default_options;
        else {
            for(var dfo in default_options) {
                if(typeof opt[dfo] == 'undefined') opt[dfo] = default_options[dfo];
            }
        }

        var ele = opt.target;
        if(typeof opt.target == 'string') ele = document.getElementById(opt.target);
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

            
            for(var i=0; i<keys.length; i++) {
                //Modifiers
                var k=keys[i];
                if(k == 'ctrl' || k == 'control') {
                    if(e.ctrlKey) kp++;

                } else if(k ==  'shift') {
                    if(e.shiftKey) kp++;

                } else if(k == 'alt') {
                        if(e.altKey) kp++;

                } else if(k.length > 1) { //If it is a special key
                    if(special_keys[k] == code) kp++;

                } else { //The special keys did not match
                    if(character == k) kp++;
                    else {
                        if(shift_nums[character] && e.shiftKey) { //Stupid Shift key bug created by using lowercase
                            character = shift_nums[character]; 
                            if(character == k) kp++;
                        }
                    }
                }
            }

            if(kp == keys.length) {
                callback(e);

                if(!opt['propagate']) { //Stop the event
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
        if(ele.addEventListener) ele.addEventListener(opt['type'], func, false);
        else if(ele.attachEvent) ele.attachEvent('on'+opt['type'], func);
        else ele['on'+opt['type']] = func;
    }
});
//dojo.declare("gnr.GnrViewEditor",null,{
//      constructor: function(widget){
//        this.widget = widget;
//      }
//});
