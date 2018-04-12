genro_plugin_dashboards = {

    regions : {headline:['top', 'bottom', 'center'], sidebar:['left', 'right', 'center']},

    subregions : {sidebar:['top', 'bottom', 'center'], headline:['left', 'right', 'center']},

    dashboardItemsMenu:function(){
        if(this.edit){
            genro.src.getNode()._('div', '_dhmenues');
            var node = genro.src.getNode('_dhmenues');
            node.clearValue();
            node.freeze();
            var menupath = this.root.absDatapath('.dashboardItemsMenu');
            node._('menu', {modifiers:'*',_class:'smallmenu',storepath:menupath,
                                            id:'dashboardItemsMenu',
                                           action:'$2.setRelativeData(".table",$1.fullpath.split(".").slice(0,2).join("."));$2.setRelativeData(".itemName",$1.resource)'});
            node.unfreeze();

        }
        
    },

    addPage:function(){
        var that = this;
        genro.dlg.prompt("New dashboard",
                        {dflt:new gnr.GnrBag({design:'headline',title:'new dashboard'}),
                                    widget:[{value:'^.title',lbl:_T('Title')},
                                            {value:'^.design',lbl:_T('Design'),tag:'filteringSelect',values:'headline,sidebar'}],
                                    action:function(res){
                                        res.setItem('layout',that.defaultLayout(res.getItem('design')));
                                        var pages = genro.getData(that.storepath); 
                                        var label = 'r_'+pages.len();
                                        pages.setItem(label,res);
                                        that.root.setRelativeData('.selectedDashboard',label);
                                    }});
    },

    delPage:function(){
        var selectedDashboard = this.root.getRelativeData('.selectedDashboard');
        var pages = genro.getData(this.storepath); 
        pages.popNode(selectedDashboard);
    },

    dupPage:function(){

    },
    configurationPane:function(parent){
        var src = parent.getValue();
        src.popNode('root');
        var selectedDashboard = this.root.getRelativeData('.selectedDashboard');
        if(!selectedDashboard){
            selectedDashboard = this.root.getValue().getNode('#0').label;
        }
        var currentDatapath = this.storepath+'.'+selectedDashboard;
        var root = src._('div','root',{datapath:currentDatapath,margin_top:'4px'});
        var fb = genro.dev.formbuilder(root._('div',{margin:'8px'}),1,{border_spacing:'4px'});
        fb.addField('textbox',{value:'^.title',lbl:_T('Title')});
        var that = this;
        fb.addField('filteringSelect',{value:'^.design',lbl:_T('Region'),
                        validate_onAccept:function(){
                            //that.rebuild();
                            //that.root.setRelativeData('.selectedDashboard',selectedDashboard);
                        },
                        values:'headline,sidebar'});
        var kw = {_class:'dhthumb'};
        var center = root._('div',kw);
        center._('div',{innerHTML:_T('Region visibility'),text_align:'center',color:'silver',
                        font_weight:'bold'});
        root._('dataController',{script:"genro.dashboards['thumbEditor_'+design](center)",
                                center:center,design:'^.design',_onBuilt:true});
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
        var pages = genro.getData(this.storepath); 
        var that = this;
        this.clearRoot();
        this.root.setRelativeData('.selectedDashboard',null);
        pages.forEach(function(n){
            that.buildDashboard(n);
        });
    },
    clearRoot:function(){
        var container = this.root.getValue();
        container.getNodes().forEach(function(n){
            container.popNode(n.label);
        });
    },

    buildDashboard:function(pageNode){
        this.root.freeze();
        this.root.getValue().popNode(pageNode.label);
        var that = this;
        var pageData = pageNode.getValue();
        var design = pageData.getItem('design') || 'headline';
        var bc = this.root._('BorderContainer',pageNode.label,{regions:'^.layout.regions',_class:'hideSplitter',
                                                            datapath:this.storepath+'.'+pageNode.label,
                                                            pageName:pageNode.label,
                                                            design:design,title:'^.title'
                                                        });
        this.regions[design].forEach(function(region){
            var subbc = bc._('BorderContainer',region,{region:region, splitter:(region != 'center')  && that.edit,
            _class:'hideSplitter',
            regions:'^.regions',datapath:'.layout.'+region});
            that.dashboard_subRegions(subbc, design,region);
        });

        this.root.unfreeze();

    },
    dashboard_subRegions:function(bc,design,region){
        var that = this;
        this.subregions[design].forEach(function(subregion){
            var pane = bc._('contentPane',subregion,{region:subregion, _class:'itemRegion', 
                                        datapath:'.'+subregion,
                                        splitter:(subregion != 'center') && that.edit,
                                        overflow:'hidden',
                                        dropTarget:true,
                                        dropCodes:'dashboardItems',
                                        onDrop_dashboardItems:function(p1,p2,kw){
                                            var sourceNode = this;
                                            var item_parameters = [{value:'^._item_title',lbl:_T('Title')}];
                                            if(kw.data.item_parameters){
                                                item_parameters = item_parameters.concat(kw.data.item_parameters);
                                                
                                            }
                                            genro.dlg.prompt(_T('Parameters ')+kw.data.caption,
                                                        {widget:item_parameters,
                                                        action:function(result){
                                                            that.assignDashboardItem(sourceNode,kw,result);}
                                            });
                                        },
                                        remote:'di_buildRemoteItem',
                                        remote_py_requires:'gnrcomponents/dashboard_component/dashboard_component:DashboardItem',
                                        remote_table:'^.table',
                                        remote_itemName:'^.itemName',
                                        remote__if:'table&&itemName',
                                        remote_editMode:that.edit,
                                        remote_itemPars:'=.itemPars',
                                        remote_workpath:'dashboards.'+region+'.'+subregion,
                                        remote__waitingMessage:'Loading...',
                                        remote__onRemote:function(){
                                            //console.log('bbb',region,subregion,this);
                                        }});
           //pane._('div',{position:'absolute',border:'2px dotted silver',rounded:6,
           //                top:'2px',bottom:'2px',left:'2px',right:'2px',
           //                hidden:'^.itemName'});
        });
    },
    assignDashboardItem:function(sourceNode,kw,itemParameters){
        if(itemParameters){
            sourceNode.setRelativeData('.itemPars',itemParameters.deepCopy());
        }
        sourceNode.setRelativeData('.table',kw.data.table);
        sourceNode.setRelativeData('.itemName',kw.data.resource);
    }
};