/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_dlg : todo
 * Copyright (c) : 2004 - 2007 Softwell sas - Milano
 * Written by    : Giovanni Porcari, Michele Bertoldi
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

dojo.declare("gnr.GnrPdbHandler", null, {
    constructor: function(application) {
        this.application = application;
        this.breakpoint_path ='_dev.pdb.breakpoints';
    },
    start:function(){
        var breakpoints = new gnr.GnrBag();
        genro.setData(this.breakpoint_path,breakpoints);
        breakpoints.subscribe('breakpoint_subscriber',{'upd':dojo.hitch(this, "breakpointTrigger"),
                                                        'ins':dojo.hitch(this, "breakpointTrigger"),
                                                        'del':dojo.hitch(this, "breakpointTrigger")});
        genro.setData('_dev.pdb.current',new gnr.GnrBag())
    },

    paletteNode:function(){
        return genro.nodeById('pdbDebugger_floating');
    },

    selectModule:function(module){
        genro.setData('_dev.pdb.editor.selectedModule',module);
    },

    showDebugger:function(module,lineno){
        var palette = this.paletteNode();
        if(palette){
            palette.widget.show();
            palette.widget.bringToTop();
        }else{
            var root = genro.src.newRoot();
            genro.src.getNode()._('div', '_pdbDebugger_');
            var node = genro.src.getNode('_pdbDebugger_').clearValue();
            node.freeze();
            var bc = node._('palettePane',{'paletteCode':'pdbDebugger',title:'Server debugger ['+genro._('gnr.pagename')+']',
                            contentWidget:'borderContainer',frameCode:'codeDebugger',width:'800px',height:'700px',dockTo:false,
                            maxable:true});
            bc._('contentPane',{region:'center',remote:'pdb.debuggerPane',overflow:'hidden',datapath:'_dev.pdb',
                                remote_cm_config_gutters:["CodeMirror-linenumbers", "pdb_breakpoints"],
                                remote_cm_onCreated:'genro.pdb.onCreatedEditor(this);',
                                remote_mainModule:module})
            node.unfreeze();
        }
        if(module){
            this.selectModule(module);
            if(lineno){
                var that = this;
                this.paletteNode().watch('codemirrorReady',function(){
                    var editorNode = that.getEditorNode();
                    return editorNode?editorNode.externalWidget:false;
                },function(){
                    that.selectLine(lineno-1)
                })
            }
        }
    },

    getModuleKey:function(module){
        return module.replace(/[\.|\/]/g,'_');
    },

    getEditorNode:function(module){
        module = module || this.getCurrentModule();
        return genro.nodeById('pdbEditor_'+this.getModuleKey(module)+'_cm');
    },
    selectLine:function(lineno){
        var cm = this.getEditorNode().externalWidget;
        cm.gnrSetCurrentLine(lineno)
        cm.scrollIntoView({line:lineno});
    },

    getBreakpoints:function(){
        return  genro.getData(this.breakpoint_path);
    },

    onPdbAnswer:function(data){
        console.log('onPdbAnswer',data)
        genro.setData('_dev.pdb.lastAnswer',data.deepCopy())
        var current = data.getItem('current');
        genro.setData('_dev.pdb.current',current)
        genro.setData('_dev.pdb.stackMenu',data.getItem('stackMenu'))
        this.showDebugger(current.getItem('filename'),current.getItem('lineno'));
    },

    onSelectedEditorPage:function(module){

    },

    onSelectStackMenu:function(kw){
        var paletteNode = this.paletteNode();
        var stackData = paletteNode.getRelativeData('_dev.pdb.current.stack.content.'+kw.fullpath);
        this.selectModule(stackData.getItem('filename'));
        //paletteNode.setRelativeData('_dev.pdb.editor.selectedModule',stackData.getItem('filename'));
    },

    breakpointTrigger:function(triggerKw){
        var cm = this.getEditorNode().externalWidget;
        if(triggerKw.reason==true){
            var kw = triggerKw.node.attr;
            if(triggerKw.evt=='ins'){
                cm.setGutterMarker(kw.line, "pdb_breakpoints", cm.gnrMakeMarker(kw.condition));
            }else if(triggerKw.evt=='del'){
                cm.setGutterMarker(kw.line, "pdb_breakpoints",null);
            }
        }
    },

    getCurrentModule:function(){
        return genro.getData('_dev.pdb.editor.selectedModule');
    },

    setBreakpoint:function(kw){
        kw.module = kw.module || this.getCurrentModule();
        var breakpoints = this.getBreakpoints()
        var bpkey = this.getModuleKey(kw.module)+'.ln_'+kw.line;
        if(breakpoints.getNode(bpkey)){
            breakpoints.popNode(bpkey);
        }else{
            breakpoints.setItem(bpkey,null,kw);
        }
    },

    onCreatedEditor:function(sourceNode){
        console.log('onCreatedEditor',sourceNode)
        var cm = sourceNode.externalWidget;
        cm.gnrMakeMarker = function(conditional) {
            var marker = document.createElement("div");
            var _class = conditional?"pdb_conditional_breakpoint":"pdb_breakpoint";
            genro.dom.addClass(marker,_class);
            marker.innerHTML = "●";
            return marker;
        }
        cm.gnrSetCurrentLine = function(line) {
            if(cm.currentLine){
                cm.removeLineClass(cm.currentLine,'wrap','pdb_currentLine_wrap');
                cm.removeLineClass(cm.currentLine,'background','pdb_currentLine_background');  
                cm.removeLineClass(cm.currentLine,'text','pdb_currentLine_text');
                cm.removeLineClass(cm.currentLine,'gutter','pdb_currentLine_gutter');   
            }
            cm.currentLine = line;
            cm.addLineClass(cm.currentLine,'wrap','pdb_currentLine_wrap');
            cm.addLineClass(cm.currentLine,'background','pdb_currentLine_background');
            cm.addLineClass(cm.currentLine,'text','pdb_currentLine_text');
            cm.addLineClass(cm.currentLine,'gutter','pdb_currentLine_gutter'); 
        }

        cm.on("gutterClick", function(cm, n,gutter,evt) {
            var info = cm.lineInfo(n);
            genro.pdb.setBreakpoint({line:n,modifier:genro.dom.getEventModifiers(evt)});
        });

       //var lineno = error.lineno-1;
       //var offset = error.offset-1;
       //var ch_start = error.offset>1?error.offset-1:error.offset;
       //var ch_end = error.offset;
       //cm.scrollIntoView({line:lineno,ch:ch_start});
       //var tm = cm.doc.markText({line:lineno,ch:ch_start},{line:lineno, ch:ch_end},
       //                {clearOnEnter:true,className:'source_viewer_error'});
       //genro.dlg.floatingMessage(cmNode.getParentNode(),{messageType:'error',
       //            message:error.msg,onClosedCb:function(){
       //        tm.clear();
       //    }})

    }
});