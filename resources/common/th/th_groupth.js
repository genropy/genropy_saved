genro_plugin_groupth = {
    buildGroupTree:function(pane,structBag){
        pane.getValue().popNode('treeroot');
        var root = pane._('div','treeroot').getParentNode();
        if(!(structBag && structBag.getItem('#0.#0'))){
            return;
        }
        root.freeze();
        var tr = root._('treeGrid',{storepath:'.treestore',autoCollapse:false,headers:true,_class:'groupby_tree'});
        var struct_row = structBag.getItem('#0.#0');
        tr._('treegrid_column',{field:'description',header:''});
        var fld;
        
        struct_row.forEach(function(n){
            if(n.attr.group_aggr && 'NLIRF'.indexOf(n.attr.dtype)>=0  || n.attr.group_nobreak){
                fld = n.attr.field.replace(/\W/g, '_')+(n.attr.group_aggr?'_'+n.attr.group_aggr:'');
                tr._('treegrid_column',{field:fld,dtype:n.attr.dtype,
                                        size:120,header:n.attr.name,format:n.attr.format});
            }
        });
        root.unfreeze();
    },

    groupTreeData:function(gridstore,structBag,rootName){
        if(!(structBag && structBag.getItem('#0.#0'))){
            return;
        }
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
        var f;
        structBag.getItem('#0.#0').forEach(function(n){
            if(!(n.attr.group_aggr && 'NLIRF'.indexOf(n.attr.dtype)>=0 || n.attr.group_nobreak)){
                f = n.attr.field.replace(/\W/g, '_');
                if(n.attr.group_aggr){
                    f += '_'+n.attr.group_aggr.replace(/\W/g, '_').toLowerCase();
                }
                group_by_cols.push(f);
            }
        });
        gridstore.forEach(function(n){
            kl = [];
            row = objectUpdate({},n.attr);
            group_by_cols.forEach(function(k){
                description = objectPop(row,k) || '-';
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
        var branchdata = branchDataNode.getValue();
        if(!branchdata){
            return;
        }
        branchdata.forEach(function(n){
            if(n.getValue()){
                that.updateBranchTotals(n);
            }
            for(k in n.attr){
                if(k.endsWith('_sum')){
                    currAttr[k] = (currAttr[k] || 0)+n.attr[k];
                }else if(k.endsWith('_avg')){
                    currAttr[k+'_avg_cnt'] = (currAttr[k+'_avg_cnt'] || 0)+n.attr._grp_count_sum;
                    currAttr[k+'_avg_s'] = (currAttr[k+'_avg_s'] || 0)+n.attr[k]*n.attr._grp_count_sum;
                    currAttr[k] = currAttr[k+'_avg_s']/currAttr[k+'_avg_cnt'];
                }else if(k.endsWith('_min')){
                    currAttr[k] = Math.min(k in currAttr? currAttr[k]:n.attr[k],n.attr[k]);
                }else if(k.endsWith('_max')){
                    currAttr[k] = Math.max(k in currAttr? currAttr[k]:n.attr[k],n.attr[k]);
                }
            }
        });
    }
};