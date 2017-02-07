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

        genro.src.getNode()._('div',statsCode);
        var node = genro.src.getNode(statsCode).clearValue();
        node.freeze();
        kw.dockTo = kw.dockTo || 'dummyDock:open';
        kw.paletteCode = statsCode;
        console.log('openPaletteStats',kw);
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
        kw.statsCode = 'stats_palette_'+kw.connectedTo.attr.nodeId;
        return this.openPaletteStats(kw);
    },
    queryParsFromGrid:function(kw){
        if(!kw._connectedWidgetId){
            return;
        }
        var widgetSourceNode = genro.nodeById(kw._connectedWidgetId);
        var w = widgetSourceNode.widget;
        if(w.collectionStore){
            var s = w.collectionStore();
            var sn = s.storeNode;
            var selattr = sn.currentAttributes();
            if(selattr._sections){
                th_sections_manager.onCalling(selattr._sections,selattr);
            }
            kw.where = objectPop(selattr,'where');
            kw.condition = objectPop(selattr,'condition');
            objectExtract(selattr,'_*');
            objectExtract(selattr,'hardQueryLimit,checkPermissions');
            var columns = objectPop(selattr,'columns');
            if(widgetSourceNode.attr.structpath){
                var struct = widgetSourceNode.getRelativeData(widgetSourceNode.attr.structpath);
                var row_head = struct.getItem('#0.#0');
                var headers = {};
                columns = [];
                row_head.forEach(function(n){
                    if(n.attr.calculated){
                        return;
                    }
                    if('hidden' in n.attr){
                        if(widgetSourceNode.currentFromDatasource(n.attr.hidden)){
                            return;
                        }
                    }
                    var f = n.attr.caption_field || n.attr.field;
                    headers[f.replace(/\./g, '_').replace(/@/g, '_')] = {dataType:n.attr.dtype,label:n.attr.name};
                    if(f[0]!='@' && f[0]!='$'){
                        f = '$'+f;
                    }
                    arrayPushNoDup(columns,f);
                });
                columns = columns.join(',');
                kw.headers = headers;
            }
            kw.columns = columns;
            kw.selectionKwargs = selattr;
        }
        
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
        if(!palettePars.paletteCode){
            palettePars.paletteCode =  kw.nodeId || (connectedWidgetId?'palette_'+connectedWidgetId:'palette_stats_' %genro.getCounter());
        }
        kw._workspace = false;
        var palette = sourceNode._('palettePane',palettePars);
        return palette._('StatsPane','statsPane',kw);
    },



    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
});
