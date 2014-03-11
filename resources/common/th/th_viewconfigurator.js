var genro_plugin_grid_configurator = {
    deleteGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var that = this;
        var currViewAttr = gridSourceNode.getRelativeData('.currViewAttrs');
        genro.serverCall('_table.adm.userobject.deleteUserObject', {pkey:currViewAttr.getItem('pkey')}, function() {
            genro.grid_configurator.loadView(gridId);
            that.refreshMenu(gridId);
        });
    },
    configureStructure:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        var structpath = gridSourceNode.absDatapath(gridSourceNode.attr.structpath);
        var palette = genro.dlg.quickPalette(gridId+'_viewconf',{height:'500',width:'600px',title:'View Configurator'},
                                            function(pane){
                                                pane._('bagEditor',{storepath:structpath,labelAttribute:'name',addrow:true,delrow:false,addcol:true});
                                            });
    },

    setCurrentAsDefault:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        genro.setInStorage("local", this.storeKey(gridId), gridSourceNode.getRelativeData('.currViewPath'));
        this.checkFavorite(gridId);
    },
    storeKey:function(gridId){
        return 'view_' + genro.getData('gnr.pagename') + '_' + gridId +'_struct';
    },
    setFavoriteView:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        var favoritePath = genro.getFromStorage("local", this.storeKey(gridId)) || '__baseview__';        
        gridSourceNode.setRelativeData('.favoriteViewPath',favoritePath);
        //this.setCurrentAsDefault(gridId);
    },
    
    saveGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var selectedViewCode = gridSourceNode.getRelativeData('.currViewAttrs.code');
        var datapath =  gridSourceNode.absDatapath('.currViewAttrs');
        var that = this;
        saveCb = function(dlg) {
            var pagename = genro.getData('gnr.pagename');
            var flag =  pagename+'_'+gridId;
            var metadata = genro.getData(datapath);
            var flags = metadata.getItem('flags');
            if(flags){
                if(flags.indexOf(flag)<0){
                    flags = flags.split(',');
                    flags.push(flag)
                }
            }else{
                flags = flag;
            }
            metadata.setItem('flags',flags)
            genro.serverCall('_table.adm.userobject.saveUserObject',
                            {'objtype':'view','metadata':metadata,'data':gridSourceNode.widget.structBag,
                            table:gridSourceNode.attr.table},
                            function(result) {
                                dlg.close_action();
                                gridSourceNode.setRelativeData('.currViewPath', result.attr.code);
                                that.refreshMenu(gridId);
                            });
        };
        genro.dev.userObjectDialog(selectedViewCode ? 'Save View ' + selectedViewCode : 'Save New View',datapath,saveCb);
    },
    

    addGridConfigurator:function(sourceNode){
        sourceNode.attr.selfDragColumns = 'trashable';
        var table = sourceNode.attr.table;
        if(!table && sourceNode.attr.storepath){
            table = genro.getDataNode(sourceNode.widget.absStorepath()).attr.dbtable;
            sourceNode.attr.table = table; 
        }
        if(table){
            var tablecode = table.replace('.', '_');
            var fieldcellattr;
            sourceNode.attr['onDrop_gnrdbfld_' + tablecode] = function(dropInfo, data) {
                var grid = this.widget;
                if(dropInfo.event.shiftKey){
                    fieldcellattr = genro.serverCall('app.getFieldcellPars',{field:data.fieldpath,table:data.maintable});
                    if(fieldcellattr){
                        fieldcellattr = fieldcellattr.asDict();
                    }
                }
                grid.addColumn(data, dropInfo.column,fieldcellattr);
            };
            sourceNode.attr.dropTarget_column = sourceNode.attr.dropTarget_column ? sourceNode.attr.dropTarget_column + ',' + 'gnrdbfld_' + tablecode : 'gnrdbfld_' + tablecode;
            sourceNode.dropModes.column = sourceNode.attr.dropTarget_column;
        }
        sourceNode._gridConfiguratorBuilt=true;
    },
    
    loadView:function(gridId,currPath,frameCode){
        var gridSourceNode = genro.nodeById(gridId);
        currPath = currPath || gridSourceNode.getRelativeData('.favoriteViewPath') || '__baseview__';
        var resource_structs = gridSourceNode.getRelativeData('.resource_structs');
        var structbag,structnode,viewAttr;
        var finalize = function(struct){
             gridSourceNode.setRelativeData(gridSourceNode.attr.structpath,struct);
             //if(gridSourceNode.widget && gridSourceNode.widget.storeRowCount()>0){
             //    gridSourceNode.widget.reload(true);
             //}
        }
        
        if(resource_structs){
            structnode = resource_structs.getNode(currPath);
            if(structnode){
                viewAttr = structnode.attr;
                structbag = structnode._value;
            }
        }
        if(!structbag){
            var menubag = gridSourceNode.getRelativeData('.structMenuBag')
            if(!menubag.getNode(currPath)){
                gridSourceNode.setRelativeData('.currViewPath','__baseview__');
                return;
            }
            viewAttr = menubag.getNode(currPath).attr;
        }        
        viewAttr['id'] = viewAttr['pkey']
        gridSourceNode.setRelativeData('.currViewAttrs',new gnr.GnrBag(viewAttr));
        this.checkFavorite(gridId);
        if(viewAttr.pkey){
            var pkey = viewAttr.pkey;
            genro.serverCall('_table.adm.userobject.loadUserObject', {pkey:pkey}, function(result){finalize(result.getValue())});
        }else{
            finalize(gridSourceNode.getRelativeData('.resource_structs.'+currPath).deepCopy())
        }
    },
    refreshMenu:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        var menubag = gridSourceNode.getRelativeData('.structMenuBag');
        if(!menubag){
            return;
        }
        menubag.getParentNode().getResolver().reset();
    },
    checkFavorite:function(gridId){
        var frame = genro.getFrameNode(gridId.replace('_grid',''));
        var gridSourceNode = genro.nodeById(gridId);
        if(!frame){
            return;
        }
        var currPath = gridSourceNode.getRelativeData('.currViewPath');
        var currfavorite = genro.getFromStorage("local", this.storeKey(gridId));
        gridSourceNode.setRelativeData('.favoriteViewPath',currfavorite);
        //this.refreshMenu(gridId);
        genro.dom.setClass(frame,'th_isFavoriteView',currfavorite==currPath);
    }
};
    
    
    