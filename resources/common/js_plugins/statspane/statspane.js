genro.statspane =  {

    openPaletteStats:function(kw){
        var statsCode = objectPop(kw,'statsCode');
        if(statsCode){
            var wdg = genro.wdgById(statsCode+'_floating');
            if(wdg){
                wdg.show();
                wdg.bringToTop();
                return;
            }
            kw.nodeId = statsCode;
        }
        statsCode = statsCode || '_stats_'+genro.getCounter();
        genro.src.getNode()._('div',statsCode);
        var node = genro.src.getNode(statsCode).clearValue();
        node.freeze();
        kw.dockTo = kw.dockTo || 'dummyDock:open';
        if(kw.configurator!==false){
            kw.configurator = true;
        }
        var palette = node._('PaletteStats',kw);
        node.unfreeze();
        return palette;
    },

    openGridStats:function(kw){
        kw.connectedTo = objectPop(kw,'grid').sourceNode;
        kw.userObjectId = objectPop(kw,'pkey');
        return this.openPaletteStats(kw);
    }
};

dojo.declare("gnr.widgets.StatsPane", gnr.widgets.UserObjectLayout, {
    objtype:'stats',

    contentKwargs: function(sourceNode, attributes) {
        sourceNode.gnrwdg.table = attributes.table;
        var connectedWidgetId = this.getConnectedWidgetId(sourceNode,objectPop(attributes,'connectedTo'));
        sourceNode.gnrwdg.connectedWidgetId = connectedWidgetId;
        var code = objectPop(attributes,'code');
        if(!code){
            if(connectedWidgetId){
                code = 'stats_'+connectedWidgetId;
            }else{
                code = attributes.table?'stats_'+attributes.table.replace('.','_'):'stats_'+genro.getCounter();
            }
        }
        if(!attributes.table && connectedWidgetId){
            attributes.table = genro.nodeById(connectedWidgetId).attr.table;
        }
        attributes.nodeId = code;
        return attributes;
    },

    getConnectedWidgetId:function(sourceNode,connectedTo){
        var connectedWidgetId;
        if(typeof(connectedTo)=='string'){
            if(sourceNode.isPointerPath(connectedTo)){
                connectedTo = sourceNode.currentFromDatasource(connectedTo);
            }else{
                connectedTo = genro.nodeById(connectedTo);
            }
        }
        if(connectedTo){
            connectedWidgetId = connectedTo.attr.nodeId;
            genro.assert(connectedWidgetId,'connectedTo must have a nodeId');
        }
        return connectedWidgetId;
    },

    gnrwdg_viewerFrame:function(frame,kw){
        //override
        var center = frame._('ContentPane',{region:'center'});
        var gridId = this.sourceNode.attr.nodeId+'_pivot_grid';
        center._('BagStore',{storepath:'#WORKSPACE.pivot.result.store',
                        nodeId:gridId+'_store',
                        storeType:'AttributesBagRows',
                        datapath:'#WORKSPACE.pivot'});
        center._('newIncludedView',{structpath:'#WORKSPACE.pivot.result.struct',
                                    controllerPath:'#WORKSPACE.pivot',
                                    datamode:'attr',datapath:'#WORKSPACE.pivot',
                                    nodeId:gridId,store:gridId});


    },

    gnrwdg_configuratorFrame:function(frame,kw){
        var cpkw = {side:'center',overflow:'hidden',remote:'pdstats_configuratorTabs',
                              remote_table:this.table,
                              remote_connectedWidgetId:this.connectedWidgetId,   
                              remote_dfname:this.sourceNode.attr.nodeId,
                              remote_py_requires:'js_plugins/statspane/statspane:StatsPane',
                              _anchor:true};

        cpkw.remote_query_pars = normalizeKwargs(kw,'condition');
        frame._('ContentPane',cpkw);
    },

    gnrwdg_userObjectData:function(){
        //override
        return new gnr.GnrBag();
    },

    gnrwdg_onLoadingObject:function(userObjectId,fistLoad){
        //override
    },

    gnrwdg_onLoadedObject:function(result,userObjectId,fistLoad){
        //override
    }
});

dojo.declare("gnr.widgets.PaletteStats", gnr.widgets.StatsPane, {
    createContent:function(sourceNode, kw, children){
        var palettePars = objectExtract(kw,'paletteCode,title,height,width,top,right,dockButton,dockTo');
        if(palettePars.dockButton===true){
            palettePars.dockButton = {iconClass:'iconbox sum'};
        }
        palettePars._lazyBuild = true;
        palettePars._workspace = true;
        palettePars.title = palettePars.title || 'Stats';
        palettePars.top = palettePars.top || '20px';
        palettePars.right = palettePars.right || '20px';
        palettePars.height = palettePars.height || '400px';
        palettePars.width = palettePars.width || '700px';
        var connectedWidgetId = this.getConnectedWidgetId(sourceNode,kw.connectedTo);
        palettePars.paletteCode = palettePars.paletteCode || kw.nodeId || connectedWidgetId?'palette_'+connectedWidgetId:'palette_stats_' %genro.getCounter();
        kw._workspace = false;
        var palette = sourceNode._('palettePane',palettePars);
        return palette._('StatsPane','statsPane',kw);
    },



    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
});
