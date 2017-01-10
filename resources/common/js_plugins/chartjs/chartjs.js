var genro_plugin_chartjs =  {
    openGridChart:function(kw){
        var grid = objectPop(kw,'grid');
        var sn = grid.sourceNode;
        var chartNode = this.openChart({
                                    widgetNodeId:sn.attr.nodeId,
                                    userObjectId:kw.pkey,
                                    storepath:sn.absDatapath(sn.attr.storepath),
                                    title:kw.caption || 'New Chart',
                                    pkeys:grid.getSelectedPkeys(),
                                    struct:grid.structbag().deepCopy(),
                                    datamode:grid.datamode,
                                    chartMenuPath:sn.absDatapath('.chartsMenu'),
                                    captionGetter:function(kw){
                                        return genro.chartjs.gridCaptionGetter(grid,kw);
                                    },
                                    datasetGetter:function(kw){
                                        return genro.chartjs.gridDatasetGetter(grid,kw);
                                    },
                                });
        var chartNodeId = chartNode.attr.nodeId;
        chartNode.registerSubscription(sn.attr.nodeId+'_onSelectedRow',function(kw){
            genro.nodeById(chartNodeId).setRelativeData('.filter',kw.selectedPkeys);
        });
    },

    gridCaptionGetter:function(grid,kw){
        var r = grid.structbag().getItem('#0.#0');
        var text_types = {'T':true,'A':true,'C':true};
        var _id = kw._id;
        var _querystring = kw._querystring;
        var data = [];
        r.forEach(function(n){
            var dtype = n.attr.dtype || 'T';
            if(!(dtype in text_types)){
                return;
            }
            var caption = n.attr.name || n.attr.field;
            if(_id && n.attr.field==_id || _querystring && caption.toLowerCase().indexOf(_querystring.slice(0,-1).toLowerCase())>=0){
                data.push({_pkey:n.attr.field,caption:caption});
            }
        });
        return {headers:'name:Customer,addr:Address,state:State',data:data};
    },

    gridDatasetGetter:function(grid,kw){
        var result = [];
        var numeric_types = {'I':true,'L':true,'N':true,'R':true};
        var s = {};
        grid.structbag().getItem('#0.#0').forEach(function(n){
            var c = n.attr;
            if(c.dtype in numeric_types && !(c.field in s)){
                s[c.field] = true;
                result.push(c);
            }
        });
        return result;
    },

    saveChart:function(widgetNodeId,chartNode) {
        var widgetSourceNode = genro.nodeById(widgetNodeId);
        var that = this;
        var chartCode = chartNode.getRelativeData('.metadata.code');
        var datapath = chartNode.absDatapath('.metadata');
        var chartPars = chartNode.getRelativeData().deepCopy();
        chartPars.popNode('metadata');
        chartPars.popNode('filter');
        saveCb = function(dlg) {
            var datapath = chartNode.absDatapath('.metadata');
            var metadata = genro.getData(datapath);
            var pagename = genro.getData('gnr.pagename');
            var flags = metadata.getItem('flags');
            metadata.setItem('flags',pagename+'_'+widgetNodeId);
            genro.serverCall('_table.adm.userobject.saveUserObject',
                            {'objtype':'chartjs','metadata':metadata,
                            'data':chartPars,
                            table:widgetSourceNode.attr.table},
                            function(result) {
                                dlg.close_action();
                                var menuData = widgetSourceNode.getRelativeData('.chartsMenu');
                                if(menuData){
                                    menuData.getParentNode().getResolver().reset();
                                }
                            });
        };
        genro.dev.userObjectDialog(chartCode ? 'Save Chart ' + chartCode : 'Save New Chart',datapath,saveCb);
    },

    loadChart:function(chartNode,userObjectId){
        genro.serverCall('_table.adm.userobject.loadUserObject', {pkey:userObjectId}, 
            function(result){
                chartNode.setRelativeData('.metadata',new gnr.GnrBag(result.attr));
                result.getValue().forEach(function(n){
                    chartNode.setRelativeData('.'+n.label,n.getValue());
                });
            });
    },

    openChart:function(kw){
        if(!('chroma' in window)){
            genro.dom.loadJs('/_rsrc/js_libs/chroma.min.js',function(){});
            genro.dom.loadJs('/_rsrc/js_libs/distinct-colors.min.js');
        }
        genro.setAliasDatapath('CHARTJS_DFLT','gnr.chartjs.defaults');
        genro.setAliasDatapath('CHARTJS_GLOB','gnr.chartjs.defaults.global');
        var widgetNodeId = objectPop(kw,'widgetNodeId');
        var code =widgetNodeId+'_chart_'+(kw.userObjectId || ('_newchart_'+genro.getCounter()));
        var title = objectPop(kw,'title');
        var datastruct = objectPop(kw,'struct');
        var storepath = objectPop(kw,'storepath');
        var pkeys = objectPop(kw,'pkeys');
        var wdg = genro.wdgById(code+'_floating');
        var chartNodeId = code+'_cjs';
        kw.chartNodeId = chartNodeId;
        if(wdg){
            wdg.show();
            wdg.bringToTop();
            return genro.nodeById(chartNodeId);
        }
        genro.src.getNode()._('div',code);
        var node = genro.src.getNode(code).clearValue();
        node.freeze();
        var paletteAttr = {'paletteCode':code,'frameCode':code,'title':title,'dockTo':false,'width':'600px','height':'500px','contentWidget':'FramePane'};
        var palette = node._('palettePane',code,paletteAttr);
        var bar = palette._('slotBar',{toolbar:true,side:'top',slots:'*,saveBtn,5'});
        bar._('slotButton','saveBtn',{iconClass:'iconbox save',
                                        action:function(){
                                            genro.chartjs.saveChart(widgetNodeId,genro.nodeById(chartNodeId));
                                        }});
        var bc = palette._('BorderContainer',{_anchor:true,side:'center'});
        
        var confbc = bc._('BorderContainer',{region:'right',width:'320px',border_left:'1px solid #efefef',
                            drawer:kw.userObjectId?'close':true,splitter:true});
        this._chartParametersPane(confbc,code,kw);
        var chartNode = bc._('ContentPane',{region:'center'})._('chartjs',{
            nodeId:chartNodeId,
            value:'^'+storepath,
            filter:'^.filter',
            columnCaption:'^.columnCaption',
            datasets:'^.datasets',            
            options:'^.options',
            chartType:'^.chartType',
            datamode:kw.datamode,
            selfsubscribe_chartReady:function(){
                if(!kw.userObjectId){
                    this.setRelativeData('.options',new gnr.GnrBag(this.externalWidget.options));
                }
            }
        }).getParentNode();
        this.initChartParameters(palette.getParentNode(),datastruct,pkeys);
        node.unfreeze();
        if(kw.userObjectId){
            this.loadChart(chartNode,kw.userObjectId);
        }
        return chartNode;
    },

    initChartParameters:function(sourceNode,datastruct,pkeys){
        var columnCaption_all = [];
        sourceNode.setRelativeData('.datasets',new gnr.GnrBag());
        sourceNode.setRelativeData('.chartType','bar');
        sourceNode.setRelativeData('.filter',pkeys);
    },

    _chartParametersPane:function(bc,code,pars){
        var fb = genro.dev.formbuilder(bc._('ContentPane',{region:'top'}),1,{border_spacing:'1px'});
        var modes = 'bar:Bar,line:Line,radar:Radar,polar:Polar,pie:Pie & Doughnut,bubble:Bubble,scales:Scales';
        fb.addField('filteringSelect',{value:'^.chartType',values:modes,lbl:'Type'});
        fb.addField('callbackSelect',{value:'^.columnCaption',width:'15em',
                                        lbl_text_align:'right',
                                        lbl_class:'gnrfieldlabel',
                                        lbl:_T('Caption'),
                                        callback:function(kw){
                                            return pars.captionGetter(kw);},
                                        parentForm:false,hasDownArrow:true});
        fb.addField('Button',{label:'Datasets',action:function(){
            var allDatasets = pars.datasetGetter();
            var currentDatasets = this.getRelativeData('.datasets');
            currentDatasets = currentDatasets? currentDatasets.deepCopy():new gnr.GnrBag();
            var that = this;
            var dataSetsValues = [];
            var pickerValue = [];
            var dsIndex = {};
            allDatasets.forEach(function(ds){
                dataSetsValues.push(ds.field+':'+(ds.name || ds.field));
                if(currentDatasets.getNode(ds.field)){
                    pickerValue.push(ds.field);
                }
                dsIndex[ds.field] = ds;
            });
            genro.dlg.prompt('Manage datasets',{dflt:pickerValue.join(','),
                widget:'checkBoxText',wdg_values:dataSetsValues.join(','),
                wdg_cols:1,
                action:function(result){
                    result = result? result.split(','):[];
                    var ridx;
                    currentDatasets.getNodes().forEach(function(n){
                        ridx = result.indexOf(n.label);
                        if(ridx<0){
                            currentDatasets.popNode(n.label);
                        }else{
                            result.splice(ridx,1);
                        }
                    }); 
                    result.forEach(function(n,idx){
                        var c = dsIndex[n];
                        var nlab = n.replace(/\./g, '_').replace(/@/g, '_');
                        if(!currentDatasets.getNode(nlab)){
                            currentDatasets.setItem(nlab,new gnr.GnrBag({field:n,enabled:true,parameters:new gnr.GnrBag({label:c.name || c.field})}));
                        }
                    });
                    that.setRelativeData('.datasets',currentDatasets);
            }});
        }});

        fb.addField('Button',{label:'Full Options',action:function(){
            genro.dev.openBagInspector(this.absDatapath('.options'),{title:'Full Options'});
        }});
        var tc = bc._('TabContainer',{margin:'2px',region:'center'});
        this.datasetsGrid(tc._('ContentPane',{title:'Datasets'}),pars.chartNodeId);
        this._optionsFormPane(tc._('ContentPane',{title:'Options',datapath:'.options'}));
        tc._('ContentPane',{title:'Options JS'})._('codemirror','optionEditor',{value:'^.options_js',config_mode:'javascript',config_lineNumbers:true,
                                                    height:'100%'});
    },

    datasetsGrid:function(pane,chartNodeId){
        var grid = pane._('quickGrid',{value:'^.datasets',addCheckBoxColumn:{field:'enabled'}});
        var that = this;
        var dtypeWidgets = {'T':'TextBox','B':'Checkbox','L':'NumberTextBox'};
        grid._('column',{'field':'parameters',name:'Parameters',width:'100%',
                        _customGetter:function(row){
                            return row.parameters?row.parameters.getFormattedValue():'No Parameters';
                        },
        edit:{modal:true,contentCb:function(pane,kw){
            var chartNode = genro.nodeById(chartNodeId);
            var chartType = chartNode.getRelativeData('.chartType');
            var pagesCb = chartNode.externalWidget.gnr['_dataset_'+chartType];
            var pages;
            if(pagesCb){
                pages = pagesCb();
            }else{
                pages = chartNode.externalWidget.gnr._dataset__base();
            }
            var bc = pane._('BorderContainer',{height:'250px',width:'300px',_class:'datasetParsContainer'});
            var top = bc._('ContentPane',{region:'top',_class:'dojoxFloatingPaneTitle'})._('div',{innerHTML:'Dataset '+kw.rowDataNode.label});
            var tc = bc._('tabContainer',{region:'center',margin:'2px'});
            var field,dtype,lbl,editkw;
            pages.forEach(function(pageKw){
                var pane = tc._('ContentPane',{title:pageKw.title});
                var fb = genro.dev.formbuilder(pane,1,{border_spacing:'1px',datapath:'.parameters',margin:'3px'});
                pageKw.fields.forEach(function(fkw){
                    dtype = fkw.dtype;
                    editkw = objectUpdate({},fkw.edit || {});
                    editkw.value = '^.'+fkw.field;
                    editkw.lbl = fkw.lbl;
                    if(dtype=='B'){
                        editkw.label = objectPop(editkw,'lbl');
                    }else{
                        editkw.lbl_text_align = 'right';
                    }
                    fb.addField(objectPop(editkw,'tag') || dtypeWidgets[dtype], editkw);
                });
            });
        }}});
    },

    _optionsFormPane:function(pane){
        var op_list = 'title';
        var that = this;
        op_list.split(',').forEach(function(op){
            that._optioncb(pane,op);
        });
    },
    
    _optioncb:function(pane,name){
        //datasource:'^.'+name,template:this['_template_'+name]
        var box = pane._('div',{_class:'chart_option_panel'});
        box._('div',{innerHTML:stringCapitalize(name),_class:'chart_option_panel_title'});
        box._('div',{_class:'chart_option_panel_content'})._('div',{innerHTML:"==_v?_v.getFormattedValue():'No Option'",_v:'^.'+name});
        var tp = box._('tooltipPane',{datapath:'.'+name})._('div',{padding:'10px'});
        this['_option_'+name](tp);
    },
    
    _option_title:function(pane){
        var fb = genro.dev.formbuilder(pane,1,{border_spacing:'1px'});
        fb.addField('textbox',{value:'^.text',lbl:'Text'});
        fb.addField('checkbox',{value:'^.display',label:'Display'});
        fb.addField('filteringSelect',{value:'^.position',lbl:'Position',values:'top,left,bottom,right'});
        fb.addField('checkbox',{value:'^.fullWidth',label:'FullWidth'});
        this._optionFonts(fb);
        fb.addField('numberTextBox',{value:'^.padding',lbl:'Padding'});
    },

    _optionFonts:function(fb){
        fb.addField('numberTextBox',{value:'^.fontSize',lbl:'fontSize',placeholder:'^#CHARTJS_GLOB.defaultFontSize'});
        fb.addField('filteringSelect',{value:'^.fontFamily',lbl:'fontFamily',
                        values:"Helvetica Neue,Helvetica,Arial,sans-serif",
                        placeholder:'^#CHARTJS_GLOB.defaultFontFamily'
                    });
        fb.addField('filteringSelect',{value:'^.fontStyle',lbl:'fontStyle',
                        values:"bold,italic,normal", placeholder:'^#CHARTJS_GLOB.defaultFontStyle'});
        fb.addField('textbox',{value:'^.fontColor',lbl:'Color',
                        placeholder:'^#CHARTJS_GLOB.defaultFontColor'});
    }

};