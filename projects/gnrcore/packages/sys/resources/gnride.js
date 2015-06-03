var gnride = {
    
    
    
    
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
    }

}