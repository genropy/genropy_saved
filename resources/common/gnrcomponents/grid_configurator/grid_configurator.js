var genro_plugin_grid_configurator = {
    deleteGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var currViewAttr = gridSourceNode.getRelativeData('.currViewAttrs');
        genro.serverCall('deleteViewGrid', {pkey:currViewAttr.getItem('id')}, function() {
            genro.grid_configurator.loadView(gridId);
        });
    },

    saveGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var selectedView = gridSourceNode.getRelativeData('.currViewAttrs');
        var datapath =  gridSourceNode.absDatapath('.currViewAttrs');
        var dlg = genro.dlg.quickDialog(selectedView ? 'Save View ' + selectedView.getItem('description') : 'Save New View');
        var center = dlg.center;
        var box = center._('div', {datapath:datapath,padding:'20px'});
        var fb = genro.dev.formbuilder(box, 1, {border_spacing:'6px'});
        fb.addField('textbox', {lbl:"Name",value:'^.description',width:'10em'});
        fb.addField('checkbox', {label:"Private",value:'^.private'});
        var bottom = dlg.bottom._('div');
        var saveattr = {'float':'right',label:'Save'};
        var data = new gnr.GnrBag();

        saveattr.action = function() {
            genro.serverCall('saveGridCustomView',
            {'gridId':gridId,'save_info':genro.getData(datapath),'data':gridSourceNode.widget.structBag},
                            function(result) {
                                dlg.close_action();
                                gridSourceNode.setRelativeData('.currViewPath', result.attr.code);
                            });
        };
        bottom._('button', saveattr);
        bottom._('button', {'float':'right',label:'Cancel',action:dlg.close_action});
        dlg.show_action();
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
    
    loadView:function(gridId,currPath){
        currPath = currPath || '__baseview__';
        var gridSourceNode = genro.nodeById(gridId);
        var menubag = gridSourceNode.getRelativeData('.structMenuBag')
        if(!menubag.getNode(currPath)){
            gridSourceNode.setRelativeData('.currViewPath','__baseview__');
            return;
        }
        var viewAttr = menubag.getNode(currPath).attr;
        var storeKey = 'iv_' + genro.getData('gnr.pagename') + '_' + gridId
        gridSourceNode.setRelativeData('.currViewAttrs',new gnr.GnrBag(viewAttr));
        var finalize = function(struct){
             gridSourceNode.setRelativeData(gridSourceNode.attr.structpath,struct);
             if(gridSourceNode.widget.storeRowCount()>0){
                 gridSourceNode.widget.reload();
             }
             genro.setInStorage("local", storeKey, currPath);
        }
        if(viewAttr.pkey){
            var pkey = viewAttr.pkey;
            genro.serverCall('loadGridCustomView', {pkey:pkey}, function(result){finalize(result.getValue())});
        }else{
            finalize(gridSourceNode.getRelativeData('.resource_structs.'+currPath).deepCopy())
        }
    }
};
    
    
    