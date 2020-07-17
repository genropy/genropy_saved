var THPicker = {

    onDropElement:function(sourceNode,data,mainpkey,rpcmethod,treepicker,tbl,one,many,grid,defaults,nodup){
        if(data.structure_many){
            //dragging from structure tree
            many = data.structure_many;
            treepicker = true;
        }
        var kw = {dropPkey:mainpkey,tbl:tbl,one:one,many:many};
        var cbdef = function(destrow,sourcerow,d){
            var l = d.split(':');
            var sfield = l[0];
            var dfield = l.length==1?l[0]:l[1];
            destrow[dfield] = sourcerow[sfield];
        };
        var drow;
        if(treepicker){
            kw.dragPkeys = [data.pkey];
            if(defaults){
                drow = {};
                kw.dragDefaults = {};
                defaults.split(',').forEach(function(d){cbdef(drow,data['_record'],d);});
                kw.dragDefaults[data['pkey']] = drow;
            }
        }else{
            var pkeys = [];
            var dragDefaults = {};
            dojo.forEach(data,function(n){
                pkeys.push(n['_pkey'])
                if(defaults){
                    drow = {};
                    defaults.split(',').forEach(function(d){cbdef(drow,n,d);});
                    dragDefaults[n['_pkey']] = drow;
                }
                
            });
            kw.dragPkeys = pkeys;
            kw.dragDefaults = dragDefaults;
        }
        if(grid && nodup){
            var exclude_values = grid.getColumnValues(many);
            kw.dragPkeys = kw.dragPkeys.filter(function(fkey){
                return exclude_values.indexOf(fkey)<0;
            });
        }

        kw._sourceNode = sourceNode;
        if(grid.gridEditor && grid.gridEditor.editorPars && !(grid.gridEditor.autoSave && mainpkey)){
            var rows = [];
            dojo.forEach(kw.dragPkeys,function(fkey){
                var r = {};
                r[many] = fkey;
                if(kw.dragDefaults){
                    objectUpdate(r,kw.dragDefaults[fkey]);
                }
                rows.push(r);
            });
            grid.gridEditor.addNewRows(rows);
        }else if(mainpkey){
            if(grid.gridEditor && objectNotEmpty(grid.gridEditor.editorPars.default_kwargs)){
                var editorDefaults = grid.sourceNode.evaluateOnNode(grid.gridEditor.editorPars.default_kwargs);
                kw.dragDefaults = kw.dragDefaults || {};
                kw.dragPkeys.forEach(function(pkey){
                    kw.dragDefaults[pkey] = kw.dragDefaults[pkey] || {};
                    objectUpdate(kw.dragDefaults[pkey],editorDefaults);
                });
            }
            genro.serverCall(rpcmethod,kw,function(){},null,'POST');
        }

    }
};