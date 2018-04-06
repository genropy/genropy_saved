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
    },

    getPivotGrid:function(sourceStore,sourceStruct){
        if(!(sourceStore && sourceStruct)){
            return {};
        }
        var resultStore = new gnr.GnrBag();
        var resultStruct = new gnr.GnrBag();
        var resultStructRow = new gnr.GnrBag();
        resultStruct.setItem('views_0.rows_0',resultStructRow);

        var struct_row = sourceStruct.getItem('#0.#0');
        var grpcol = [];
        var valuecols = [];
        var nobreak = [];
        var fld;
        var attr;
        struct_row.forEach(function(n){
            attr = objectUpdate({},n.attr);
            attr.col_getter = attr.field.replace(/\W/g, '_');
            if (attr.group_aggr){
                attr.col_getter+='_'+attr.group_aggr.replace(/\W/g, '_').toLowerCase();
            }
            if(attr.group_aggr && 'NLIRF'.indexOf(attr.dtype)>=0 ){                
                valuecols.push(attr);
            }else if (attr.group_nobreak){
                nobreak.push(attr);
            }else{
                grpcol.push(attr);
            }
        });
        var lastGrpcol = grpcol.pop();
        var lastGrpcolField = lastGrpcol.col_getter;
        var colset = Array.from(new Set(sourceStore.columns('#a.'+lastGrpcolField)[0])).sort();
        var colsetDict = {};
        
        grpcol.concat(nobreak).forEach(function(attr,idx){
            resultStructRow.setItem('cell_'+resultStructRow.len(),null,objectUpdate({},attr));
        });
        colset.forEach(function(f,colsetidx){
            colsetDict[f]=colsetidx;
            valuecols.forEach(function(attr){
                attr = objectUpdate({},attr);
                attr.field = attr.field+'_'+colsetidx;
                attr.name = f+'<br/>'+attr.name;
                attr.columnset = 'grp_'+colsetidx;
                resultStructRow.setItem('cell_'+resultStructRow.len(),null,attr);
            });
        });
        var colname,row,keylist,cskey,key,nodeToUpdate;
        sourceStore.getNodes().forEach(function(n,idx){
            row = {};
            keylist = [];
            attr = n.attr;
            cskey = colsetDict[attr[lastGrpcolField]];
            grpcol.forEach(function(f){
                colname = f.col_getter;
                keylist.push(attr[colname]);
                row[colname] = attr[colname];
            });
            nobreak.forEach(function(f){
                colname = f.col_getter;
                row[colname] = attr[colname];
            });
            valuecols.forEach(function(f){
                colname = f.field.replace(/\W/g, '_');
                row[colname+'_'+cskey+'_'+f.group_aggr.replace(/\W/g, '_').toLowerCase()] = attr[f.col_getter];
            });
            key = keylist.join('_');
            nodeToUpdate = resultStore.getNode(key);
            if(!nodeToUpdate){
                resultStore.setItem(key,null,row);
            }else{
                nodeToUpdate.updAttributes(row);
            }
        });
        return {'struct':resultStruct,'store':resultStore};
    }

};