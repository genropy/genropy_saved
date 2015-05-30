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
        var current = new gnr.GnrBag();
        genro.setData('_dev.pdb.current',current)
        current.subscribe('changedCurrent',{'upd':dojo.hitch(this, "onChangedCurrent"),
                                                        'ins':dojo.hitch(this, "onChangedCurrent"),
                                                        'del':dojo.hitch(this, "onChangedCurrent")});
        
    },

    showDebugger:function(module){
        var palette = genro.nodeById('pdbDebugger_floating');
        if(palette){
            palette.widget.show();
            palette.widget.bringToTop();
            if(module && this.getEditorNode(module)){
                palette.setRelativeData('.editor.selectedModule',module);
            }
            return
        }
        var root = genro.src.newRoot();
        genro.src.getNode()._('div', '_pdbDebugger_');
        var node = genro.src.getNode('_pdbDebugger_').clearValue();
        node.freeze();
        var bc = node._('palettePane',{'paletteCode':'pdbDebugger',title:'Server debugger ['+genro._('gnr.pagename')+']',
                        contentWidget:'borderContainer',frameCode:'codeDebugger',width:'800px',height:'700px',dockTo:false,
                        maxable:true});
        bc._('contentPane',{region:'center',remote:'pdb.debuggerPane',remote_mainModule:module,overflow:'hidden',datapath:'_dev.pdb',
                            remote_cm_config_gutters:["CodeMirror-linenumbers", "pdb_breakpoints"],
                            remote_cm_onCreated:'genro.pdb.onCreatedEditor(this);'})
        node.unfreeze();
    },
    getModuleKey:function(module){
        return module.replace(/[\.|\/]/g,'_');
    },

    getEditorNode:function(module){
        module = module || this.getCurrentModule();
        return genro.nodeById('pdbEditor_'+this.getModuleKey(module)+'_cm');
    },

    getBreakpoints:function(){
        return  genro.getData(this.breakpoint_path);
    },
    onChangedCurrent:function(kw){
        console.log('onChangedCurrent',kw)
        //sthis.showDebugger();
    },
    onPdbAnswer:function(data){
        genro.setData('_dev.pdb.current',data)
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