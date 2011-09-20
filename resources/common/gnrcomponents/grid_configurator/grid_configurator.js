var genro_plugin_grid_configurator = {
    deleteGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var that = this;
        var currViewAttr = gridSourceNode.getRelativeData('.currViewAttrs');
        genro.serverCall('deleteViewGrid', {pkey:currViewAttr.getItem('pkey')}, function() {
            genro.grid_configurator.loadView(gridId);
            that.refreshMenu(gridId);
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
        gridSourceNode.setRelativeData('.currViewPath',favoritePath);
        this.setCurrentAsDefault(gridId);
    },
    
    saveGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var selectedViewCode = gridSourceNode.getRelativeData('.currViewAttrs.code');
        var datapath =  gridSourceNode.absDatapath('.currViewAttrs');
        var that = this;
        saveCb = function(dlg) {
            genro.serverCall('saveGridCustomView',
            {'gridId':gridId,'save_info':genro.getData(datapath),'data':gridSourceNode.widget.structBag},
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
            sourceNode.attr['onDrop_gnrdbfld_' + tablecode] = function(dropInfo, data) {
                var grid = this.widget;
                grid.addColumn(data, dropInfo.column);
                if (grid.rowCount > 0) {
                    setTimeout(function() {
                        grid.reload();
                    }, 1);
                }
            };
            sourceNode.attr.dropTarget_column = sourceNode.attr.dropTarget_column ? sourceNode.attr.dropTarget_column + ',' + 'gnrdbfld_' + tablecode : 'gnrdbfld_' + tablecode;
            sourceNode.dropModes.column = sourceNode.attr.dropTarget_column;
        }
        sourceNode._gridConfiguratorBuilt=true;
    },
    
    loadView:function(gridId,currPath,frameCode){
        currPath = currPath || '__baseview__';
        var gridSourceNode = genro.nodeById(gridId);
        var menubag = gridSourceNode.getRelativeData('.structMenuBag')
        if(!menubag.getNode(currPath)){
            gridSourceNode.setRelativeData('.currViewPath','__baseview__');
            return;
        }
        var viewAttr = menubag.getNode(currPath).attr;
        
        gridSourceNode.setRelativeData('.currViewAttrs',new gnr.GnrBag(viewAttr));
        this.checkFavorite(gridId);
        var finalize = function(struct){
             gridSourceNode.setRelativeData(gridSourceNode.attr.structpath,struct);
             if(gridSourceNode.widget && gridSourceNode.widget.storeRowCount()>0){
                 gridSourceNode.widget.reload();
             }
        }
        if(viewAttr.pkey){
            var pkey = viewAttr.pkey;
            genro.serverCall('loadGridCustomView', {pkey:pkey}, function(result){finalize(result.getValue())});
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
        this.refreshMenu(gridId);
        genro.dom.setClass(frame,'th_isFavoriteView',currfavorite==currPath);
    }
};
    
    
    