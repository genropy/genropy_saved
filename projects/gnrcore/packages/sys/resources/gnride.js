var gnride = {
    start:function(){
        genro.wsk.addHandler('do_pdb_out_bag',this.onPdbAnswer_bag);
        genro.wsk.addHandler('do_pdb_out_line',this.onPdbAnswer_line);
    },

    getStackEditor:function(ide_page){
        ide_page = ide_page || this.getCurrentIdePage();
        return genro.nodeById(ide_page+'_sc');
    },
    getIdeStack:function(){
        return genro.nodeById('ideStack');
    },

    newIde:function(kw){
        var mainstack = this.getIdeStack();
        var ide_page = kw.ide_page;
        var ide_name = kw.ide_name || ide_page;
        if(ide_page in mainstack.widget.gnrPageDict){
            return;
        }
        mainstack._('ContentPane',ide_page,{title:ide_name,
                                    overflow:'hidden',pageName:ide_page,closable:true,
                                    datapath:'.'+ide_name
                        })._('ContentPane',{remote:'makeEditorStack',remote_frameCode:ide_page,
                                            remote_isDebugger:kw.isDebugger,overflow:'hidden'})
    },

    openModuleToEditorStack:function(kw){
        var module = kw.module;
        var ide_page = kw.ide_page || this.getCurrentIdePage();
        var scNode = gnride.getStackEditor(ide_page);
        var module = kw.module;
        if(!(module in scNode.widget.gnrPageDict)){
            this.addModuleToEditorStack(ide_page,module);
        }
        scNode.setRelativeData('.selectedModule',module)
    },

    addModuleToEditorStack:function(ide_page,module){
        ide_page = ide_page || this.getCurrentIdePage();
        var scNode = gnride.getStackEditor(ide_page);
        var label = this.getModuleKey(module);
        var l = module.split('/');
        var title = l[l.length-1];
        scNode._('ContentPane',label,{title:title,datapath:'.page_'+scNode._value.len(),
                                    overflow:'hidden',
                                    pageName:module,closable:true
                                    })._('ContentPane',{remote:'buildEditorTab',remote_ide_page:ide_page,
                                                        remote_module:module,overflow:'hidden'})
    },

    onPdbAnswer_line:function(line){
        genro.setData('_dev.pdb.debugger.output_line',line)
        window.focus();
    },
    onPdbAnswer_bag:function(data){
        var status = data.getItem('status');
        var module=status.getItem('module')
        var lineno=status.getItem('lineno')
        var functionName=status.getItem('functionName')
        console.log('onPdbAnswer: module=',module,'  lineno=',lineno,' functionName=',functionName)
        this.onDebugStep(data)
        window.focus();
    },

    onDebugStep:function(data){
        genro.setData('main.stack',data.getItem('stack'),{caption:'Stack'})
        var result=new gnr.GnrBag();
        result.setItem('locals',data.getItem('current.locals'),{caption:'Locals'})
        var returnValue = data.getItem('current.returnValue');
        var watches = data.getItem('watches');
        if (returnValue!==undefined){
            result.setItem('returnValue',returnValue,{caption:'Return Value'})       
        }
        if (watches){
            result.setItem('watches',watches,{caption:'Watches'})
        }
        genro.setData('main.result',result)
        genro.setData('main.status',data.getItem('status'));
    },
 
    onCreatedEditor:function(sourceNode){
        var that = this;
        sourceNode.watch('externalWidgetReady',function(){
            return sourceNode.externalWidget;
        },function(){
            that.onCreatedEditorDo(sourceNode);
            sourceNode.fireEvent('.editorCompleted')
        })
    },
    onCreatedEditorDo:function(sourceNode){
        var selectedLine = genro.getData('_dev.pdb.status.lineno'); 
        var cm = sourceNode.externalWidget;
        cm.gnrMakeMarker = function(conditional) {
            var marker = document.createElement("div");
            var _class = conditional?"pdb_conditional_breakpoint":"pdb_breakpoint";
            genro.dom.addClass(marker,_class);
            marker.innerHTML = "●";
            return marker;
        }
        cm.gnrSetCurrentLine = function(line) {
            var cm_line = line-1;
            if(cm.currentLine){
                cm.removeLineClass(cm.currentLine,'wrap','pdb_currentLine_wrap');
                cm.removeLineClass(cm.currentLine,'background','pdb_currentLine_background');  
                cm.removeLineClass(cm.currentLine,'text','pdb_currentLine_text');
                cm.removeLineClass(cm.currentLine,'gutter','pdb_currentLine_gutter');   
            }
            cm.currentLine = cm_line;
            cm.addLineClass(cm.currentLine,'wrap','pdb_currentLine_wrap');
            cm.addLineClass(cm.currentLine,'background','pdb_currentLine_background');
            cm.addLineClass(cm.currentLine,'text','pdb_currentLine_text');
            cm.addLineClass(cm.currentLine,'gutter','pdb_currentLine_gutter'); 
        }

        cm.on("gutterClick", function(cm, n,gutter,evt) {
            var info = cm.lineInfo(n);
            var evt = info.gutterMarkers?'del':'ins';
            var code_line = n+1;
            var modifier = genro.dom.getEventModifiers(evt)
            var module = sourceNode.attr.modulePath;

            var cb = function(condition){
                cm.setGutterMarker(n, "pdb_breakpoints", evt=='del' ? null : cm.gnrMakeMarker(condition));
                genro.publish('setBreakpoint',{line:code_line,module:module,condition:condition,evt:evt});
                
            };
            if(modifier=='Shift'){
                genro.dlg.prompt(_T("Breakpoint condition"),{lbl:_T('Condition'),action:cb})
            }else{
                cb();
            }
        });
        if(selectedLine){
            this.selectLine(selectedLine);
            
        }
    },


    getCurrentModule:function(ide_page){
        ide_page = ide_page || this.getCurrentIdePage();
        return genro.getData('main.instances.'+ide_page+'.selectedModule');
    },
    getCurrentIdePage:function(){
        return genro.getData('main.ide_page');
    },

    getEditorNode:function(module,ide_page){
        ide_page = ide_page || this.getCurrentIdePage();
        module = module || this.getCurrentModule(ide_page);
        return genro.nodeById(ide_page+'_'+this.getModuleKey(module)+'_cm');
    },

    getModuleKey:function(module){
        return module.replace(/[\.|\/]/g,'_');
    },

    selectLine:function(lineno){
        var cm = this.getEditorNode().externalWidget;
        cm.gnrSetCurrentLine(lineno)
        cm.scrollIntoView({line:lineno});
    },


}