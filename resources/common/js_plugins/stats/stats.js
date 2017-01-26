dojo.declare("gnr.widgets.StatsPane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw, children){
        var gnrwdg = sourceNode.gnrwdg;
        var rootKw = objectExtract(kw,'height,width,region,side');
        gnrwdg.connectedWidgetId = this.getConnectedWidgetId(sourceNode,objectPop(kw,'connectedTo'));
        var statsNodeId = objectPop(kw,'nodeId') || this.autoStatsNodeId(gnrwdg.connectedWidgetId);
        gnrwdg.statsNodeId = statsNodeId;
        sourceNode.attr.nodeId = statsNodeId;
        if(objectPop(kw,'_workspace')!==false){
            sourceNode.attr._workspace = true;
        }
        gnrwdg.defaultGroupByFields = objectPop(kw,'groupByFields');
        if(gnrwdg.connectedWidgetId){
            var sn = genro.nodeById(gnrwdg.connectedWidgetId);
            gnrwdg.table = sn.attr.table;
            if(sn.attr.tag.toLowerCase()=='tree'){
                sn.subscribe('onSelected',function(kw){
                    console.log('tree selected',kw);
                });
            }else{
                sn.subscribe('onSelectedRow',function(kw){
                    sourceNode.setRelativeData('#WORKSPACE.filter',kw.selectedPkeys);
                });
            }
            gnrwdg.storepath = sn.absDatapath(sn.attr.storepath);
            gnrwdg.datamode = sn.attr.datamode;
        }else{
            var value = objectPop(kw,'value');
            if(typeof(value)=='string'){
                gnrwdg.storepath = sourceNode.absDatapath(value);
            }else{
                gnrwdg.storepath = '#WORKSPACE.store';
                sourceNode.setRelativeData('#WORKSPACE.store',value);
            }
        }
        sourceNode.attr.storepath = gnrwdg.storepath;
        sourceNode.registerDynAttr('storepath');
        sourceNode.attr.groupBy = '#WORKSPACE.groupBy';
        sourceNode.registerDynAttr('groupBy');

        var rootbc = sourceNode._('borderContainer',rootKw);
        if(kw.configurator){
            gnrwdg.configuratorFrame(rootbc,kw);
        }
        gnrwdg.datamode = objectPop(kw,'datamode') || gnrwdg.datamode;
        var userObjectId = objectPop(kw,'userObjectId');            
        gnrwdg.setDefaults();
        gnrwdg.statsCenter(rootbc,kw);
        if(userObjectId){
            sourceNode.watch('waitingBuild',function(){
                return genro.nodeById(gnrwdg.statsNodeId).externalWidget;
            },function(){
                gnrwdg.loadStats(userObjectId);
            });
        }
        return rootbc;
    },

    autoStatsNodeId:function(connectedWidgetId){
        return  'stats_'+ (connectedWidgetId || '') +'_'+genro.getCounter();
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

    gnrwdg_setLoadMenuData:function(){
        var kw = {'objtype':'stats',
                  'flags':genro.getData('gnr.pagename')+'_'+(this.connectedWidgetId || this.statsNodeId),
                    'table':this.table};
        var result = genro.serverCall('_table.adm.userobject.userObjectMenu',kw) || new gnr.GnrBag();
        if(result.len()){
            result.setItem('r_'+result.len(),null,{caption:'-'});
        }
        result.setItem('__newstats__',null,{caption:'New Stats'});
        this.sourceNode.setRelativeData('#WORKSPACE.loadMenu',result);
    },

    gnrwdg_setDefaults:function(){
        //this.sourceNode.setRelativeData('#WORKSPACE.groupByFields',this.defaultGroupByFields,{_displayedValue:this.defaultGroupByFields});
    },

    gnrwdg_setStorepath:function(){
        if(!this.datamode){
            var d = this.getData();
            if(d && d.len()){
                var n = d.getNode('#0');
                if('pageIdx' in n.attr){
                    this.datamode = 'attr';
                }
                else if(d.getItem('#0') instanceof gnr.GnrBag){
                    this.datamode = 'bag';
                }else{
                    this.datamode = 'attr';
                }
                //genro.nodeById(this.statsNodeId).attr.datamode = this.datamode;
            }
        }
    },

    gnrwdg_getData:function(){
        return this.sourceNode.getRelativeData(this.sourceNode.attr.storepath);
    },

    gnrwdg_groupByMenu:function(){
        var types = {'I':true,'L':true,'N':true,'R':true,'T':true,'A':true,'C':true,'D':true,'B':true};
        var result = new gnr.GnrBag();
        var s = {};
        if(this.connectedWidgetId){
            var widgetNode = genro.nodeById(this.connectedWidgetId);
            if(widgetNode.attr.structpath){
                var structbag = widgetNode.getRelativeData(widgetNode.attr.structpath);
                if(structbag){
                    structbag.getItem('#0.#0').forEach(function(n){
                        var c = objectUpdate({},n.attr);
                        objectExtract(c,'tag');
                        if((c.dtype || 'T') in types && !(c.field in s)){
                            var f = c.field_getter || c.field;
                            f = f.replace(/\W/g, '_');
                            c.code = f;
                            c.label = c.name;
                            s[f] = true;
                            result.setItem(c.code,null,c);
                        }
                    });
                }
            }
        }else{
            var storebag = this.getData();
            var dtype;
            var datamode = this.datamode || 'attr';
            var items;
            if(storebag){
                storebag.walk(function(n){
                    if('pageIdx' in n.attr){
                        return;
                    }
                    if(datamode=='bag'){
                        items = n.getValue().items();
                    }else{
                        items = objectItems(n.attr);
                    }
                    items.forEach(function(n){
                        if(!isNullOrBlank(n.value)){
                            dtype = guessDtype(n.value);
                            if(dtype in types && !(n.key in s)){
                                s[n.key] = true;
                                result.setItem(n.key,null,{'code':n.key,'label':n.key});
                            }
                        }
                    });
                },'static');
            }
        }
        return result;

    },

    gnrwdg_setGroupBy:function(){
        return;
    },

    gnrwdg_statsCenter:function(bc,kw){
        
    },

    gnrwdg_configuratorFrame:function(parentBc,kw){
        var confkw = objectPop(kw,'configurator');
        var that = this;

        confkw = confkw===true?{region:'right',drawer:(kw.userObjectId || this.defaultGroupByFields)?'close':true,splitter:true,border_left:'1px solid #ccc',width:'320px'}:configurator;        
        this.setLoadMenuData();
        this.sourceNode.setRelativeData('#WORKSPACE.groupByFieldsMenu',new gnr.GnrBagCbResolver({method:function(){
            return that.groupByMenu();
        }},true));

        var confframe = parentBc._('FramePane',objectUpdate(confkw,{frameCode:this.statsNodeId+'_options'}));
        var bar = confframe._('slotBar',{toolbar:true,side:'top',slots:'5,refresh,saveBtn,loadMenu,2,statsTitle,*,delgroup,addgroup,10,runstats'});
        bar._('div','statsTitle',{innerHTML:'^#WORKSPACE.metadata.description?=(#v || "New Stats")',font_weight:'bold',font_size:'.9em',color:'#666'});
        bar._('slotButton','refresh',{label:'Refresh',iconClass:'iconbox reload',action:function(){
            genro.nodeById(that.statsNodeId).publish('refresh');
        }});
        bar._('slotButton','loadMenu',{iconClass:'iconbox folder',label:'Load',
            menupath:'#WORKSPACE.loadMenu',action:function(item){
                if(item.pkey){
                    that.loadStats(item.pkey);
                }else if(item.fullpath == '__newstats__'){
                    that.loadStats('__newstats__');
                }
            }});
        bar._('slotButton','saveBtn',{iconClass:'iconbox save',label:'Save',
                                        action:function(){
                                            that.saveStats();
                                        }});

        bar._('slotButton','delgroup',{iconClass:'iconbox delete_row',label:'Delete',action:function(){
                                                genro.nodeById(that.sourceNode.attr.nodeId+'_groupby_grid').publish('delrow');
                                            }});
        bar._('slotButton','addgroup',{iconClass:'iconbox add_row',label:'Add',

                                        menupath:'#WORKSPACE.groupByFieldsMenu',
                                            hiddenItemCb:function(item){
                                                var groupBy = that.sourceNode.getRelativeData('#WORKSPACE.groupBy') || new gnr.GnrBag();
                                                return groupBy.getNode(item.code);
                                            },
                                            action:function(item){
                                                var groupBy = that.sourceNode.getRelativeData('#WORKSPACE.groupBy') || new gnr.GnrBag();
                                                groupBy.setItem(item.code,new gnr.GnrBag(item));
                                                
                                            }});
        bar._('slotButton','runstats',{iconClass:'iconbox run',action:function(){
            
        }});

        this.groupByGrid(confframe._('ContentPane',{title:'GroupBy',region:'center'}));
    },

    gnrwdg_groupByGrid:function(pane){
        var grid = pane._('quickGrid',{value:'^'+this.sourceNode.absDatapath('#WORKSPACE.groupBy'),
                                    selfDragRows:true,canSort:false,
                                    nodeId:this.sourceNode.attr.nodeId +'_groupby_grid'});
        var that = this;
        grid._('column',{'field':'label',name:'Label',width:'22em',edit:true});
        grid._('column',{'field':'format',name:'Format',width:'7em',edit:true});

    },

    gnrwdg_saveStats:function() {
        var connectedWidgetId = this.connectedWidgetId || this.statsNodeId;
        var statsNode =genro.nodeById(this.statsNodeId);
        var that = this;
        var instanceCode = statsNode.getRelativeData('#WORKSPACE.metadata.code');
        var statsPars = statsNode.getRelativeData('#WORKSPACE').deepCopy();
        var datapath = statsNode.absDatapath('#WORKSPACE.metadata');
        statsPars.popNode('metadata');
        statsPars.popNode('filter');
        statsPars.popNode('options');
        statsPars.popNode('loadMenu');

        var options = statsNode.getRelativeData(statsNode.attr.optionsBag);
        var savedOptions = new gnr.GnrBag();
        options.walk(function(n){
            if(n.attr._userChanged){
                var fullpath = n.getFullpath(null,options);
                savedOptions.setItem(fullpath.replace(/\./g, '_'),null,{path:fullpath,value:n.getValue()});
            }
        });
        statsPars.setItem('savedOptions',savedOptions);
        saveCb = function(dlg) {
            var metadata = genro.getData(datapath);
            var pagename = genro.getData('gnr.pagename');
            var flags = metadata.getItem('flags');
            metadata.setItem('flags',pagename+'_'+connectedWidgetId);
            genro.serverCall('_table.adm.userobject.saveUserObject',
                            {'objtype':'stats','metadata':metadata,
                            'data':statsPars,

                            table:that.table},
                            function(result) {
                                dlg.close_action();
                                that.setLoadMenuData();
                            });
        };
        genro.dev.userObjectDialog(instanceCode ? 'Save Stats ' + instanceCode : 'Save New Stats',datapath,saveCb);
    },

    gnrwdg_loadStats:function(userObjectId,fistLoad){
        var statsNode = genro.nodeById(this.statsNodeId);
        if(userObjectId=='__newstats__'){
            statsNode.freeze();
            statsNode.setRelativeData('#WORKSPACE.metadata',new gnr.GnrBag());
            statsNode.setRelativeData('#WORKSPACE.scales',new gnr.GnrBag());
            statsNode.setRelativeData('#WORKSPACE.options',new gnr.GnrBag());
            statsNode.setRelativeData('#WORKSPACE.statsType','bar');
            setTimeout(function(){
                statsNode.unfreeze();
            },1);
        }else{
            genro.serverCall('_table.adm.userobject.loadUserObject', {pkey:userObjectId}, 
            function(result){
                
            });
        }
    },
});

