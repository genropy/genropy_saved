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
        var statsRoot = objectPop(kw,'statsRoot');
        if(!statsRoot){
            return this.openPaletteStats(kw);
        }
        if(kw.configurator!==false){
            kw.configurator = true;
        }
        statsRoot._('StatsPane','statsPane',kw);
    },

    queryParsFromGrid:function(connectedWidgetId){
        if(!connectedWidgetId){
            return;
        }
        var result = new gnr.GnrBag();
        var widgetSourceNode = genro.nodeById(connectedWidgetId);
        var w = widgetSourceNode.widget;
        if(w.collectionStore){
            var s = w.collectionStore();
            var sn = s.storeNode;
            var selattr = sn.currentAttributes();
            if(selattr._sections){
                th_sections_manager.onCalling(selattr._sections,selattr);
            }
            result.setItem('where',objectPop(selattr,'where'));
            result.setItem('condition' ,objectPop(selattr,'condition'));
            objectExtract(selattr,'_*');
            objectExtract(selattr,'hardQueryLimit,checkPermissions');
            var columns = objectPop(selattr,'columns');
            if(widgetSourceNode.attr.structpath){
                var struct = widgetSourceNode.getRelativeData(widgetSourceNode.attr.structpath);
                var row_head = struct.getItem('#0.#0');
                var colInfo = {};
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
                    colInfo[f.replace(/\./g, '_').replace(/@/g, '_')] = {dtype:n.attr.dtype,name:n.attr.name,format:n.attr.format};
                    if(f[0]!='@' && f[0]!='$'){
                        f = '$'+f;
                    }
                    arrayPushNoDup(columns,f);
                });
                columns = columns.join(',');
                result.setItem('colInfo',colInfo);
            }
            result.setItem('columns',columns);
            result.setItem('selectionKwargs', selattr);
        }
        return result;
        
    },
    
    commandMenu:function(dataframes,basecommands,dfcommands,baseParsDefaults){
        var result = basecommands.deepCopy();
        result.forEach(function(n){
            n.attr.default_kw.pars = new gnr.GnrBag(baseParsDefaults);
        });
        if(!dataframes || dataframes.len()===0){
            return result;
        }
        result.setItem('sep',null,{caption:'-'});
        dataframes.keys().forEach(function(dfname){
            var r = new gnr.GnrBag();
            dfcommands._nodes.forEach(function(n){
                var kw = objectUpdate({},n.attr);
                kw.default_kw = objectUpdate({dfname:dfname},n.attr.default_kw);
                r.setItem(n.label,null,kw);
            });
            result.setItem('r_'+result.len(),r,{caption:dfname});
        });
        return result;
    },
    parentDataFrame:function(sourceNode){
        var dfname = sourceNode.getRelativeData('.record.dfname');
        var dataframes = sourceNode.getRelativeData('#ANCHOR.dataframes.info');
        if(!dataframes){
            return new gnr.GnrBag();
        }
        var df = dataframes.getItem(dfname);
        if (df){
            return df.getItem('store').deepCopy();
        }else{
            return new gnr.GnrBag();
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
        if(genro.nodeById(code)){
            code = code+'_'+genro.getCounter();
        }
        attributes.nodeId = code;
        sourceNode.attr.nodeId = code;
        sourceNode.attr._anchor = true;
        sourceNode._registerNodeId();
        sourceNode.setRelativeData('.statcode',code);
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
        var tc = frame._('TabContainer',{side:'center',margin:'2px'});
        var sckw = {selectedPage:'^#ANCHOR.selectedStep',datapath:'.viewer',title:_T('Commands outputs')};
        var topic = 'subscribe_'+this.sourceNode.attr.nodeId+'_stepDone';
        sckw['subscribe_'+this.sourceNode.attr.nodeId+'_stepRemoved'] = function(kw){
            this.setRelativeData('.rows.'+kw.step+'.store',null);
            this.setRelativeData('#ANCHOR.selectedStep','emptyStep');
            var that = this;
            setTimeout(function(){
                var v = that.getValue();
                if(v.getNode(kw.step)){
                    that.getValue().popNode(kw.step+'.center.grid');
                    that.getValue().popNode(kw.step);
                }
            },1);
        };
        sckw[topic] = function(kw){
            var result = kw.result;
            var data = result.getItem('store');
            var dataframe_info = result.getItem('dataframe_info');
            this.setRelativeData('.rows.'+kw.step,new gnr.GnrBag(),{dataframe_info:dataframe_info});
            if(!(kw.step in this.widget.gnrPageDict)){
                var f = this._('borderContainer',kw.step,{datapath:'.rows.'+kw.step,
                                    pageName:kw.step,_class:'pbl_roundedGroup',margin:'5px'});
                f._('ContentPane',{region:'top',height:'20px',_class:'pbl_roundedGroupLabel'})._('div',{template:'$counter)$command $comment',datasource:'^#ANCHOR.stored_data.commands.'+kw.step});
                var qg =f._('ContentPane','center',{region:'center'})._('quickGrid','grid',{value:'^.store',infoInCellAttributes:true});
            }
            this.setRelativeData('.rows.'+kw.step+'.store',data.deepCopy());
            this.setRelativeData('#ANCHOR.selectedStep',kw.step);
        };
        sc = tc._('StackContainer',sckw);
        sc._('ContentPane',{pageName:'emptyStep'})._('div',{innerHTML:'Empty Step',font_size:'20px',margin_top:'20px',text_align:'center',color:'#ccc'});      
        var rs = tc._('ContentPane',{title:_T('Report site'),hidden:'^#ANCHOR.report_site_active?=!#v',overflow:'hidden'});
        var ifkw = {src:'^#ANCHOR.report_url',height:'100%',width:'100%',border:0};
        rs._('iframe',ifkw);
    },

    gnrwdg_configuratorFrame:function(frame,kw){
        var cpkw = {side:'center',overflow:'hidden',remote:'pdstats_remoteCommandGrid',
                              remote_table:this.table,
                              remote_code:this.sourceNode.attr.nodeId,
                              remote_connectedWidgetId:this.connectedWidgetId,   
                              remote_py_requires:'js_plugins/statspane/statspane:StatsPane'};

        cpkw.remote_query_pars = normalizeKwargs(kw,'condition');
        frame._('ContentPane',cpkw);
    },

    gnrwdg_userObjectData:function(){
        //override
        return this.sourceNode.getRelativeData('.stored_data').deepCopy();
    },

    gnrwdg_onLoadingObject:function(userObjectId,fistLoad){
        //override
    },

    gnrwdg_onLoadedObject:function(result,userObjectId,fistLoad){
        //override
        this.sourceNode.setRelativeData('.stored_data',result || new gnr.GnrBag());
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
        palettePars.height = palettePars.height || '600px';
        palettePars.width = palettePars.width || '800px';
        palettePars.maxable = true;
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
