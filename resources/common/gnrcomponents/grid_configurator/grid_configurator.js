var genro_plugin_grid_configurator = {
    deleteGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        genro.serverCall('deleteViewGrid', {pkey:gridSourceNode.selectedView['id']}, function() {
            genro.grid_configurator.loadGridBaseView(gridId);
        });
    },

    saveGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var gridControllerPath = gridSourceNode.gridControllerPath;
        var selectedView = gridSourceNode.selectedView;
        var datapath = gridControllerPath + '.confMenu.save_dlg';
        var dlg = genro.dlg.quickDialog(selectedView ? 'Save View ' + selectedView.description : 'Save New View');
        genro.setData(datapath, new gnr.GnrBag(selectedView));
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
                                gridSourceNode.setRelativeData(gridSourceNode.gridControllerPath + '.confMenu.selectedViewPkey', result.attr.id);
                                genro.setInStorage("local", result.attr.objtype, result.attr.id);
                                gridSourceNode.selectedView = result.attr;
                                var node = genro.getDataNode(gridSourceNode.gridControllerPath + '.confMenu.data');
                                node.getResolver().reset();
                            });
        };
        bottom._('button', saveattr);
        bottom._('button', {'float':'right',label:'Cancel',action:dlg.close_action});
        dlg.show_action();
    },

   //gridConfiguratorMenu:function(gridId) {
   //    var menuId = 'confMenu_' + gridId;
   //    var menu_wdg = dijit.byId(menuId);
   //    var gridSourceNode = genro.nodeById(gridId);
   //    if (!menu_wdg) {
   //        genro.src.getNode()._('div', '_confMenuBox_' + gridId);
   //        var node = genro.src.getNode('_confMenuBox_' + gridId).clearValue();
   //        node.freeze();
   //        var menu_datapath = gridSourceNode.gridControllerPath + '.confMenu';
   //        genro.setData(menu_datapath + '.data',
   //                genro.rpc.remoteResolver('gridConfigurationMenu',
   //                {'gridId':gridId,'table':gridSourceNode.attr.table,
   //                    'selectedViewPkey':'=' + menu_datapath + '.selectedViewPkey',
   //                    '_sourceNode':gridSourceNode},
   //                {'cacheTime':'5'}));
   //        var menu = node._('menu', {storepath:'.data',id:menuId,
   //            action:function() {
   //                genro.grid_configurator.loadCustomView(gridId, this.attr.pkey);
   //            },
   //            _class:'smallmenu',datapath:menu_datapath,modifiers:'*'});
   //        node.unfreeze();
   //        menu_wdg = dijit.byId(menuId);
   //    }
   //
   //    var grid = gridSourceNode.widget;
   //    var frameNode = genro.getFrameNode(gridSourceNode.attr.frameCode);
   //    var confnode = frameNode.getValue().getNodeByAttr('_gridConfigurator',true);
   //    if (confnode){
   //        dijit.byId(menuId).bindDomNode(confnode.getDomNode());
   //    }
   //},

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
    
    
    