genro_plugin_groupth = {
    buildGroupTree:function(pane,structBag){
        pane.getValue().popNode('treeroot');
        var root = pane._('div','treeroot').getParentNode();
        root.freeze();
        var tr = root._('treeGrid',{storepath:'.treestore',headers:true});
        var struct_row = structBag.getItem('#0.#0');
        tr._('treegrid_column',{field:'description',header:''});
        var fld;
        
        struct_row.forEach(function(n){
            if(n.attr.group_aggr){
                fld = n.attr.field.replace(/\W/g, '_')+'_'+n.attr.group_aggr;
                tr._('treegrid_column',{field:fld,dtype:n.attr.dtype,
                                        size:120,header:n.attr.name,format:n.attr.format});
            }
        });
        root.unfreeze();
    },

    groupTreeData:function(gridstore,structBag,rootName){
        var result = new gnr.GnrBag();
        var treeData;
        if(rootName){
            treedata = new gnr.GnrBag();
            result.setItem('_root_',treedata,{'description':rootName});
        }else{
            treedata = result;
        }
        var row,kl,description,treepath;
        var group_by_cols = [];
        structBag.getItem('#0.#0').forEach(function(n){
            if(!n.attr.group_aggr){
                group_by_cols.push(n.attr.field);
            }
        });
        gridstore.forEach(function(n){
            kl = [];
            row = objectUpdate({},n.attr);
            group_by_cols.forEach(function(k){
                description = objectPop(row,k);
                kl.push(flattenString(description,['.']));
                treepath = kl.join('.');
                if(!treedata.getNode(treepath)){
                    treedata.setItem(treepath,null,{'description':description});
                }
            });
            objectUpdate(treedata.getAttr(kl),row);
        });
        this.updateTreeTotals(result);
        return result;
    },

    updateTreeTotals:function(treeData){
        var that = this;
        treeData.forEach(function(n){
            that.updateBranchTotals(n);
        });
    },
    
    updateBranchTotals:function(branchDataNode){
        var currAttr = branchDataNode.attr;
        var k;
        var that = this;
        branchDataNode.getValue().forEach(function(n){
            if(n.getValue()){
                that.updateBranchTotals(n);
            }
            for(k in n.attr){
                if(k.endsWith('_sum')){
                    currAttr[k] = (currAttr[k] || 0)+n.attr[k];
                }
            }
        });
    }
};