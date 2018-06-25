genro_plugin_dashboards = {
  
};


dojo.declare("gnr.DashboardManager", null, {
    regions : {headline:['top', 'bottom', 'center'], sidebar:['left', 'right', 'center']},
    subregions : {sidebar:['top', 'bottom', 'center'], headline:['left', 'right', 'center']},
    
    constructor:function(sourceNode,storepath){
        this.sourceNode = sourceNode;
        this.identifier = sourceNode.attr.nodeId;
        this.edit = sourceNode.attr._editMode;
        this.storepath = sourceNode.absDatapath(sourceNode.attr._storepath);
        this.dashboardspath = this.storepath+'.dashboards';
        this.itemspath = this.storepath+'.items';
        this.channelspath = this.storepath+'.channels';
        this.channelsdata = this.storepath+'.channels_data';
        this.externalChannels = sourceNode.attr._externalChannels || [];
        this.workspaces = sourceNode.absDatapath('.dashboards');
    },

    pageTrigger:function(kw,reason){
        try {
            if(kw.evt=='ins'){
                //this.rebuild();
            }else if(kw.evt=='del'){
                this.sourceNode.getValue().popNode(kw.node.label);
            }else if(reason=='container'){
                this.rebuild();
            }else if (reason=='child'){
            }else{
                this.rebuild();
            }
        } catch (error) {
            console.error('error in dashboard store controller',error);
        }
    },


    dashboardItemsMenu:function(){
        if(this.edit){
            genro.src.getNode()._('div', '_dhmenues');
            var node = genro.src.getNode('_dhmenues');
            node.clearValue();
            node.freeze();
            var menupath = this.sourceNode.absDatapath('.dashboardItemsMenu');
            node._('menu', {modifiers:'*',_class:'smallmenu',dashboardspath:menupath,
                                            id:'dashboardItemsMenu',
                                           action:'$2.setRelativeData(".table",$1.fullpath.split(".").slice(0,2).join("."));$2.setRelativeData(".itemName",$1.resource)'});
            node.unfreeze();

        }
        
    },

    addPage:function(){
        var that = this;
        var saveCb = function(label){
            that.sourceNode.form.save({
                onReload:function(){
                    that.sourceNode.setRelativeData('#ANCHOR.selectedDashboard',label);
                }
            });
        }; 
        genro.dlg.prompt("New dashboard",
                        {dflt:new gnr.GnrBag({design:'headline',title:'new dashboard'}),
                                    widget:[{value:'^.title',lbl:_T('Title')},
                                            {value:'^.design',lbl:_T('Design'),tag:'filteringSelect',values:'headline,sidebar'}],
                                    action:function(res){
                                        res.setItem('layout',that.defaultLayout(res.getItem('design')));
                                        var pages = genro.getData(that.dashboardspath); 
                                        var label = 'r_'+pages.len();
                                        pages.setItem(label,res);
                                        saveCb(label);
                                    }});
    },

    delPage:function(){
        var selectedDashboard = this.sourceNode.getRelativeData('.selectedDashboard');
        var pages = genro.getData(this.dashboardspath); 
        pages.popNode(selectedDashboard);
    },

    dupPage:function(){

    },

    galleryChannelsDataUpdated:function(){
        var channelsData = this.sourceNode.getRelativeData(this.channelsdata);
        this.sourceNode.publish('updatedChannels',channelsData.asDict());
    },

    updatedChannels:function(channelskw){
        var subscriptions,config;
        var items = genro.getData(this.itemspath);
        var workspaces = this.workspaces;
        var storepath = this.storepath;
        var sn = this.sourceNode;
        var itemRun,item;
        items.forEach(function(itemNode){
            item = itemNode.getValue();
            config = item.getItem('conf');
            subscriptions = item.getItem('conf_subscriber');
            itemRun=false;
            if(!subscriptions){
                return;
            }
            subscriptions.values().forEach(function(sub){
                var topic = sub.getItem('topic');
                var aliasTopic =  sub.getItem('aliasTopic');
                var newval;
                var updating = false;
                var confpath = (sub.getItem('autoTopic')?workspaces:storepath)+'.'+itemNode.label+'.conf.'+sub.getItem('varpath');
                if (topic in channelskw){
                    newval = channelskw[topic];
                    updating = true;
                }else if(aliasTopic && (aliasTopic in channelskw)){
                    newval = channelskw[aliasTopic];
                    updating = true;
                }
                if(updating){
                    var oldval = genro.getData(confpath);
                    if(!isEqual(oldval,newval)){
                        genro.setData(confpath,newval);
                        itemRun = true;
                    }
                }
            }); 
            if(itemRun){
                sn.fireEvent(workspaces+'.'+itemNode.label+'.runItem',true);
            }  
        });
    },

    channelsEdit:function(){
        var channelspath = this.channelsdata;
        var channelsData = this.sourceNode.getRelativeData(this.channelsdata) || new gnr.GnrBag();
        var currentChannels = this.sourceNode.getRelativeData(this.channelspath);
        channelsData.getNodes().forEach(function(n){
            if(!currentChannels.getNode(n.label)){
                channelsData.popNode(n.label,false);
            }
        });
        var kw = {};
        var that = this;
        kw.widget = function(parent){
            that.channelsPane(parent,currentChannels);
        };
        kw.dflt = channelsData.deepCopy();
        kw.action = function(result){
            genro.setData(channelspath,result);
            that.galleryChannelsDataUpdated();
        };
        genro.dlg.prompt(_T('Dashboard channels'),kw);
    },

    channelsPane:function(parent){
        var currentChannels = this.sourceNode.getRelativeData(this.channelspath);
        var root = parent._('div','root',{margin_top:'4px'});
        var fb = genro.dev.formbuilder(root._('div',{margin:'8px'}),1,{border_spacing:'4px'});
        var kw,defaultWdg;
        var externalChannels = this.externalChannels;
        currentChannels.forEach(function(n){
            if(externalChannels.indexOf(n.label)>=0){
                return;
            }
            kw = n.getValue().asDict();
            if(kw.wdg===false){
                return;
            }
            defaultWdg = 'textbox';
            if(kw.dbtable){
                defaultWdg = 'dbselect';
            }else if(kw.dtype=='N' || kw.dtype=='L'){
                defaultWdg = 'numberTextBox';
            }else if(kw.dtype=='D'){
                defaultWdg = 'dateTextBox';
            }
            fb.addField(objectPop(kw,'wdg') || defaultWdg,{value:'^.'+kw.topic,lbl:kw.topic,dbtable:kw.dbtable});
        });
    },
    configurationPane:function(parent){
        var src = parent.getValue();
        src.popNode('root');
        var selectedDashboard = this.sourceNode.getRelativeData('.selectedDashboard');
        if(!selectedDashboard){
            selectedDashboard = this.sourceNode.getValue().getNode('#0').label;
        }
        var currentDatapath = this.dashboardspath+'.'+selectedDashboard;
        var root = src._('div','root',{datapath:currentDatapath,margin_top:'4px'});
        var fb = genro.dev.formbuilder(root._('div',{margin:'8px'}),1,{border_spacing:'4px'});
        fb.addField('textbox',{value:'^.title',lbl:_T('Title')});
        var that = this;
        fb.addField('filteringSelect',{value:'^.design',lbl:_T('Region'),
                        validate_onAccept:function(){
                            //that.rebuild();
                        },
                        values:'headline,sidebar',disabled:true});
        var kw = {_class:'dhthumb'};
        var center = root._('div',kw);
        center._('div',{innerHTML:_T('Region visibility'),text_align:'center',color:'silver',
                        font_weight:'bold'});
        root._('dataController',{script:"genro.dashboards[dashboardIdentifier]['thumbEditor_'+design](center)",
                                center:center,design:'^.design',dashboardIdentifier:this.identifier,_onBuilt:true});
    },

    thumbEditor_sidebar:function(box){
        box.popNode('thumbroot');
        var root  = box._('div','thumbroot',{_class:'dhthumb_sidebar'}).getParentNode();
        root.freeze();
        var regions = ['left','center','right'];
        var subregions = ['top','center','bottom'];
        var r,closernode,cc,cell,regionshow;
        regions.forEach(function(region){
            regionshow = '^.layout.regions.'+region+'?show';
            r = root._('div',{_class:'dhthumb_col dhthumb_'+region});
            closernode = r._('div',{_class:'dhthumb_closer'});
            if(region!='center'){
                root._('dataController',{script:'genro.dom.setClass(r,"dhthumb_hiddenregion",!regionshow)',
                                    regionshow:regionshow,_onBuilt:true,r:r.getParentNode()});
                closernode._('div',{_class:'dhthumb_checkbox_closer'})._('checkbox',{
                    value:regionshow});
            }
            cc = r._('div',{_class:'dhthumb_cellcontainer',datapath:'.layout.'+region});
            subregions.forEach(function(subregion){
                cell = cc._('div',{_class:'dhthumb_cell dhthumb_'+subregion});
                if(subregion!='center'){
                    cell._('checkbox',{_class:'dhthumb_checkbox_closer',
                                            position:'absolute',left:'20px',top:'-4px',
                                            value:'^.regions.'+subregion+'?show'});
                }
            });
        });
        root.unfreeze(true);
    },
    thumbEditor_headline:function(box){
        box.popNode('thumbroot');
        var root  = box._('div','thumbroot',{_class:'dhthumb_headline'}).getParentNode();
        root.freeze();
        var regions = ['top','center','bottom'];
        var subregions = ['left','center','right'];
        var r,closernode,cc,cell,regionshow;
        regions.forEach(function(region){
            regionshow = '^.layout.regions.'+region+'?show';
            r = root._('div',{_class:'dhthumb_row dhthumb_'+region});
            closernode = r._('div',{_class:'dhthumb_closer'});
            if(region!='center'){
                root._('dataController',{script:'genro.dom.setClass(r,"dhthumb_hiddenregion",!regionshow)',
                                    regionshow:regionshow,_onBuilt:true,r:r.getParentNode()});
                closernode._('div',{_class:'dhthumb_checkbox_closer'})._('checkbox',{
                    value:regionshow
                });
            }
            cc = r._('div',{_class:'dhthumb_cellcontainer',datapath:'.layout.'+region});
            subregions.forEach(function(subregion){
                cell = cc._('div',{_class:'dhthumb_cell dhthumb_'+subregion});
                if(subregion!='center'){
                    cell._('checkbox',{_class:'dhthumb_checkbox_closer',
                                            position:'absolute',left:'20px',top:'-4px',
                                            value:'^.regions.'+subregion+'?show'});
                }
            });
        });
        root.unfreeze(true);
    },


    defaultLayout:function(design){
        design = design || 'headline';
        var result = new gnr.GnrBag();
        var extregions = new gnr.GnrBag();
        var rgdict = design=='headline'? {top:'250px',bottom:'250px'}:{left:'250px',right:'250px'};
        var key;
        for(key in rgdict){
            extregions.setItem(key,rgdict[key],key=='center'?null:{show:true});
        }
        var regiondict = design=='sidebar'? {top:'250px',bottom:'250px'}:{left:'250px',right:'250px'};
        var extside = design=='headline'?['top', 'bottom','center']:['left','right','center'];
        var inside = design=='sidebar'?['top', 'bottom','center']:['left','right','center'];
        result.setItem('regions',extregions);
        extside.forEach(function(region){
            var innerbag = new gnr.GnrBag();
            var rgbag = new gnr.GnrBag();
            innerbag.setItem('regions',rgbag);
            for(key in regiondict){
                rgbag.setItem(key,regiondict[key],key=='center'?null:{show:true});
            }
            inside.forEach(function(subregion){
                innerbag.setItem(subregion,null);
            });
            result.setItem(region,innerbag);
        });
        return result;
    },

    rebuild:function(){
        var pages = genro.getData(this.dashboardspath); 
        var that = this;
        this.clearRoot();
        this.sourceNode.setRelativeData('.selectedDashboard',null);
        if(pages){
            pages.forEach(function(n){
                that.buildDashboard(n);
            });
        }
    },

    registerFormSubscriptions:function(){
        var that = this;
        var tbl = this.sourceNode.form.getControllerData('table');
        if(!tbl){
            return;
        }
        this.sourceNode.registerSubscription('form_'+this.sourceNode.form.formId+'_onLoaded',function(subkw){
            var topickw = {};
            topickw[tbl.replace('.','_')+'_pkey'] = subkw.pkey;
            that.sourceNode.publish('updatedChannels',topickw);
        });
    },

    cleanUnusedItems:function(){
        var items = genro.getData(this.itemspath);
        if(!items){
            return;
        }
        var itemsMap = this.itemsMap();
        items.getNodes().forEach(function(n){
            if(!(n.label in itemsMap)){
                items.popNode(n.label);
            }
        });
    },

    itemsMap:function(){
        var itemsMap = {};
        var pages = genro.getData(this.dashboardspath); 
        var identifier;
        pages.walk(function(n){
            if (n.getValue() instanceof gnr.GnrBag && n.getValue().getItem('itemIdentifier')){
                identifier = n.getValue().getItem('itemIdentifier');
                itemsMap[identifier] = itemsMap[identifier] || [];
                itemsMap[identifier].push(n.getFullpath(null,pages));
            }
        });
        return itemsMap;

    },
    
    emptyTile:function(sourceNode){
        sourceNode.setRelativeData('.itemIdentifier',null);
        this.cleanUnusedItems();
    },

    clearRoot:function(){
        var container = this.sourceNode.getValue();
        container.getNodes().forEach(function(n){
            container.popNode(n.label);
        });
        this.sourceNode.setRelativeData(this.workspaces,null);
    },

    buildDashboard:function(pageNode){
        this.sourceNode.freeze();
        this.sourceNode.getValue().popNode(pageNode.label);
        var that = this;
        var pageData = pageNode.getValue();
        var design = pageData.getItem('design') || 'headline';
        var bc = this.sourceNode._('BorderContainer',pageNode.label,{regions:'^.layout.regions',_class:'hideSplitter',
                                                            datapath:this.dashboardspath+'.'+pageNode.label,
                                                            pageName:pageNode.label,
                                                            design:design,title:'^.title'
                                                        });
        this.regions[design].forEach(function(region){
            var subbc = bc._('BorderContainer',region,{region:region, splitter:(region != 'center')  && that.edit,
            _class:'hideSplitter',
            regions:'^.regions',datapath:'.layout.'+region});
            that.dashboard_subRegions(subbc, design,region);
        });

        this.sourceNode.unfreeze();

    },
    dashboard_subRegions:function(bc,design,region){
        var that = this;
        var itemRecordGetter = '==this.getRelativeData("'+this.itemspath+'"+"."+remote_itemIdentifier)';
        this.subregions[design].forEach(function(subregion){
            var pane = bc._('contentPane',subregion,{region:subregion, _class:'itemRegion', 
                                        datapath:'.'+subregion,
                                        splitter:(subregion != 'center') && that.edit,
                                        overflow:'hidden',
                                        dropTarget:true,
                                        dropCodes:'dashboardItems,itemIdentifier',
                                        onDrop_itemIdentifier:function(p1,p2,kw){
                                            if(kw.dropInfo.event.shiftKey){
                                                this.setRelativeData('.itemIdentifier',that.duplicateItem(kw.data));
                                            }else{
                                                this.setRelativeData('.itemIdentifier',kw.data);
                                                var draggedSn = genro.dom._lastDragInfo.sourceNode;
                                                setTimeout(function(){
                                                    draggedSn.setRelativeData('.itemIdentifier',null);
                                                },1);
                                            }
                                            
                                        },
                                        onDrop_dashboardItems:function(p1,p2,kw){
                                            var sourceNode = this;
                                            var item_parameters = [{value:'^._item_title',lbl:_T('Title'),default_value:kw.data.caption}];
                                            var fixedParameters = objectPop(kw.data,'fixedParameters');
                                            if(!fixedParameters){
                                                if(kw.data.item_parameters && kw.data.item_parameters.length){
                                                    item_parameters = item_parameters.concat(kw.data.item_parameters);
                                                }
                                                genro.dlg.prompt(_T('Parameters ')+kw.data.caption,
                                                        {widget:item_parameters,
                                                        action:function(result){
                                                            if(fixedParameters){
                                                                result.update(fixedParameters);
                                                            }
                                                            var itemIdentifier = that.registerDashboardItem(sourceNode,kw,result);
                                                            that.assignDashboardItem(sourceNode,itemIdentifier);
                                                        }
                                                });
                                            }else{
                                                var itemIdentifier = that.registerDashboardItem(sourceNode,kw,new gnr.GnrBag(fixedParameters));
                                                that.assignDashboardItem(sourceNode,itemIdentifier);
                                            }
                                            
                                        },
                                        remote:'di_buildRemoteItem',
                                        remote_py_requires:'dashboard_component/dashboard_component:DashboardItem',
                                        remote_itemIdentifier:'^.itemIdentifier',
                                        remote_dashboardIdentifier:that.identifier,
                                        remote_itemRecord:itemRecordGetter,
                                        remote__if:'itemIdentifier',
                                        remote__else:"this.getValue().popNode('remoteItem');",
                                        remote_editMode:that.edit,
                                        remote_workspaces:that.workspaces,
                                        remote_itemspath:that.itemspath, //'dashboards.'+region+'.'+subregion,
                                        remote_channelspath:that.channelspath,
                                        remote__waitingMessage:'Loading...',
                                        remote__onRemote:function(){
                                            //console.log('bbb',region,subregion,this);
                                        }});
           //pane._('div',{position:'absolute',border:'2px dotted silver',rounded:6,
           //                top:'2px',bottom:'2px',left:'2px',right:'2px',
           //                hidden:'^.itemName'});
        });
    },
    registerDashboardItem:function(sourceNode,kw,itemParameters){
        var itemRecord = new gnr.GnrBag();
        var itemPars = itemParameters.deepCopy();
        itemRecord.setItem('id',genro.time36Id());
        if(kw.data.objtype){
            table = kw.data.tbl;
            itemRecord.setItem('resource',kw.data.objtype);
            itemPars.setItem('userobject_id',kw.data.pkey);
            itemPars.setItem('table',kw.data.tbl);
        }else{
            itemRecord.setItem('table',kw.data.table);
            itemRecord.setItem('resource',kw.data.resource);
        }
        var title = itemPars.getItem('title') || itemPars.pop('_item_title');
        itemRecord.setItem('title',title);
        itemRecord.setItem('parameters',itemPars);
        var items = genro.getData(this.itemspath);
        return items.setItem(itemRecord.getItem('id'),itemRecord).label;
    },

    duplicateItem:function(identifier){
        var items = genro.getData(this.itemspath);    
        var itemRecord = items.getItem(identifier).deepCopy();
        itemRecord.setItem('id',genro.time36Id());
        itemRecord.setItem('title',itemRecord.getItem('title')+'[copy]');
        return items.setItem(itemRecord.getItem('id'),itemRecord).label;

    },

    assignDashboardItem:function(sourceNode,identifier){
        sourceNode.setRelativeData('.itemIdentifier',identifier);
    },

    availableChartGrid:function(kw){
        var _id = kw._id;
        var _querystring = kw._querystring;
        var data = this.sourceNode.getRelativeData(this.workspaces).getNodes().map(function(n){
            var v = n.getValue();
            if(v.getItem('chart_gridId')){
                return {caption:v.getItem('current_title'),_pkey:v.getItem('chart_gridId')};
            }else{
                return false;
            }
        }).filter(n => n);
        var cbfilter = function(n){return true;};
        if(_querystring){
            _querystring = _querystring.slice(0,-1).toLowerCase();
            cbfilter = function(n){return n.caption.toLowerCase().indexOf(_querystring)>=0;};
        }else if(_id){
            cbfilter = function(n){return n._pkey==_id;};
        }
        data = data.filter(cbfilter);
        return {headers:'title:Title',data:data};
    }
});