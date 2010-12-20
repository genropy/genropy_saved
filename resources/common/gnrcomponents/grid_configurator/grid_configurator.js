var genro_plugin_grid_configurator = {
    deleteGridView:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        genro.serverCall('deleteViewGrid',{pkey:gridSourceNode.selectedView['id']},function(){
            genro.grid_configurator.loadGridBaseView(gridId);
        });
    },
    
    saveGridView:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        var gridControllerPath = gridSourceNode.gridControllerPath;
        var selectedView = gridSourceNode.selectedView;
        var datapath = gridControllerPath+'.confMenu.save_dlg';
        var dlg = genro.dlg.quickDialog(selectedView?'Save View '+selectedView.description:'Save New View');
        genro.setData(datapath,new gnr.GnrBag(selectedView));
        var center = dlg.center;
        var box = center._('div',{datapath:datapath,padding:'20px'});
        var fb = genro.dev.formbuilder(box,1,{border_spacing:'6px'});
        fb.addField('textbox',{lbl:"Name",value:'^.description',width:'10em'});
        fb.addField('checkbox',{label:"Private",value:'^.private'});
        var bottom = dlg.bottom._('div');
        var saveattr = {'float':'right',label:'Save'};
        var data = new gnr.GnrBag();

        saveattr.action = function(){
            genro.serverCall('saveGridCustomView',
                            {'gridId':gridId,'save_info':genro.getData(datapath),'data':gridSourceNode.widget.structBag},
                            function(result){
                                dlg.close_action();
                                gridSourceNode.setRelativeData(gridSourceNode.gridControllerPath+'.confMenu.selectedViewPkey',result.attr.id);
                                genro.setInStorage("local",result.attr.objtype,result.attr.id);
                                gridSourceNode.selectedView = result.attr;
                                var node = genro.getDataNode(gridSourceNode.gridControllerPath+'.confMenu.data');
                                node.getResolver().reset();
                            });
        };
        bottom._('button',saveattr);
        bottom._('button',{'float':'right',label:'Cancel',action:dlg.close_action});
        dlg.show_action();
    },
    
    
    gridConfiguratorMenu:function(gridId){
        var menuId = 'confMenu_'+gridId;
        var menu_wdg=dijit.byId(menuId);
        var gridSourceNode = genro.nodeById(gridId);
        if(!menu_wdg){
            genro.src.getNode()._('div', '_confMenuBox_'+gridId);
            var node = genro.src.getNode('_confMenuBox_'+gridId).clearValue();
            node.freeze();
            var menu_datapath = gridSourceNode.gridControllerPath+'.confMenu'; 
            genro.setData(menu_datapath+'.data',
                     genro.rpc.remoteResolver('gridConfigurationMenu',
                                            {'gridId':gridId,'table':gridSourceNode.attr.table,
                                              'selectedViewPkey':'='+menu_datapath+'.selectedViewPkey',
                                              '_sourceNode':gridSourceNode},
                                            {'cacheTime':'5'}));
            var menu = node._('menu',{storepath:'.data',id:menuId,
                    action:function(){
                        genro.grid_configurator.loadCustomView(gridId,this.attr.pkey);
                    },
                    _class:'smallmenu',datapath:menu_datapath});
            node.unfreeze();
            menu_wdg=dijit.byId(menuId);
        }

        var grid = gridSourceNode.widget;
        dojo.connect(grid, 'postrender', function(){
            menu_wdg.bindDomNode(grid.views.views[0].headerNode);
        });
    },
    
    onGridCreated:function(sourceNode){
        if(sourceNode.attr.configurable && sourceNode.attr.nodeId){
            var gridId = sourceNode.attr.nodeId;
            var cb = function(){
                genro.grid_configurator.gridConfiguratorMenu(gridId);
            };
            setTimeout(cb,1);
        }
    },
    onStructCreating:function(sourceNode){
        var gridId = sourceNode.attr.nodeId;
        var loadedCustomViewId = genro.getFromStorage("local",'iv_'+genro.getData('gnr.pagename')+'_'+gridId);
        if(loadedCustomViewId){
            var result = genro.serverCall('loadGridCustomView',{pkey:loadedCustomViewId,sync:true});
            structBag = result.getValue();
            sourceNode.setRelativeData(sourceNode.attr.structpath,structBag);
            sourceNode.selectedView = result.attr;
            sourceNode.setRelativeData(sourceNode.gridControllerPath+'.confMenu.selectedViewPkey',sourceNode.selectedView?sourceNode.selectedView.id:null);
        }
    },
    
    loadGridBaseView:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        gridSourceNode.setRelativeData(gridSourceNode.attr.structpath,gridSourceNode.baseStructBag.deepCopy());
        gridSourceNode.setRelativeData(gridSourceNode.gridControllerPath+'.confMenu.selectedViewPkey',null);
        var node = genro.getDataNode(gridSourceNode.gridControllerPath+'.confMenu.data');
        genro.setInStorage("local",'iv_'+genro.getData('gnr.pagename')+'_'+gridId,null);
        node.getResolver().reset();
        gridSourceNode.selectedView = null;
        gridSourceNode.widget.reload();
    },
    
    loadCustomView:function(gridId,pkey){
        var gridSourceNode = genro.nodeById(gridId);
        genro.serverCall('loadGridCustomView',{pkey:pkey},function(result){
            gridSourceNode.selectedView = result.attr;
            gridSourceNode.setRelativeData(gridSourceNode.attr.structpath,result.getValue());
            gridSourceNode.widget.reload();
            gridSourceNode.setRelativeData(gridSourceNode.gridControllerPath+'.confMenu.selectedViewPkey',result.attr.id);
            genro.setInStorage("local",result.attr.objtype,result.attr.id);
            var node = genro.getDataNode(gridSourceNode.gridControllerPath+'.confMenu.data');
            node.getResolver().reset();
        });
    }
};
    
    
    