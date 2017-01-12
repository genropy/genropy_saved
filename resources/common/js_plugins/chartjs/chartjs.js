var genro_plugin_chartjs =  {
    chartTypes:'bar,line,bubble,doughnut,polarArea,radar,scatter',
    openGridChart:function(kw){
        var grid = objectPop(kw,'grid');
        var sn = grid.sourceNode;
        var chartNode = this.openChart({
                                    widgetNodeId:sn.attr.nodeId,
                                    userObjectId:kw.pkey,
                                    storepath:sn.absDatapath(sn.attr.storepath),
                                    title:kw.caption || 'New Chart',
                                    datamode:grid.datamode,
                                    chartMenuPath:sn.absDatapath('.chartsMenu'),
                                    captionGetter:function(kw){
                                        return genro.chartjs.gridCaptionGetter(grid,kw);
                                    },
                                    datasetGetter:function(kw){
                                        return genro.chartjs.gridDatasetGetter(grid,kw);
                                    },
                                });
        chartNode.setRelativeData('.filter',grid.getSelectedPkeys());
        var chartNodeId = chartNode.attr.nodeId;
        sn.subscribe('onSelectedRow',function(kw){
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
        console.log('datasetFields',chartPars.getNode('datasetFields'));
        chartPars.popNode('metadata');
        chartPars.popNode('filter');
        chartPars.popNode('options');
        var options = chartNode.getRelativeData('.options');
        var savedOptions = new gnr.GnrBag();
        options.walk(function(n){
            if(n.attr._userChanged){
                var fullpath = n.getFullpath(null,options);
                savedOptions.setItem(fullpath.replace(/\./g, '_'),null,{path:fullpath,value:n.getValue()});
            }
        });
        chartPars.setItem('savedOptions',savedOptions);
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

    loadChart:function(sourceNode,userObjectId){
        genro.serverCall('_table.adm.userobject.loadUserObject', {pkey:userObjectId}, 
            function(result){
                sourceNode.setRelativeData('.metadata',new gnr.GnrBag(result.attr));
                var data = result.getValue();
                var savedOptions = data.pop('savedOptions');
                data.forEach(function(n){
                    sourceNode.setRelativeData('.'+n.label,n.getValue(),n.attr);
                });
                savedOptions.forEach(function(n){
                    sourceNode.setRelativeData('.options.'+n.attr.path,n.attr.value);
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
        var code =widgetNodeId+'_chart_'+(kw.userObjectId || '_newchart_')+genro.getCounter();
        var title = objectPop(kw,'title');
        var storepath = objectPop(kw,'storepath');
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
        var paletteAttr = {'paletteCode':code,'frameCode':code,'title':title,'dockTo':false,'width':'600px','height':'500px'};
        var palette = node._('palettePane',code,paletteAttr);
        
        var bc = palette._('BorderContainer',{_anchor:true,side:'center',design:'sidebar'});
        
        var confframe = bc._('FramePane',{frameCode:code+'_options',region:'right',width:'320px',border_left:'1px solid #ccc',
                            drawer:kw.userObjectId?'close':true,splitter:true});
        var bar = confframe._('slotBar',{toolbar:true,side:'top',slots:'5,fulloptions,refresh,*,saveBtn,5'});
        
        bar._('slotButton','fulloptions',{label:'Full Options',iconClass:'iconbox gear',action:function(){
            genro.dev.openBagInspector(this.absDatapath('.options'),{title:'Full Options'});
        }});
        bar._('slotButton','refresh',{label:'Refresh',iconClass:'iconbox reload',action:function(){
            genro.nodeById(chartNodeId).publish('refresh');
        }});
        bar._('slotButton','saveBtn',{iconClass:'iconbox save',
                                        action:function(){
                                            genro.chartjs.saveChart(widgetNodeId,genro.nodeById(chartNodeId));
                                        }});
        var confbc = confframe._('BorderContainer',{side:'center'});
        this._chartParametersPane(confbc,code,kw);
        var sn = confbc.getParentNode();
        this.initChartParameters(sn);
        var chartNode = bc._('ContentPane',{region:'center'})._('chartjs',{
            nodeId:chartNodeId,
            value:'^'+storepath,
            filter:'^.filter',
            columnCaption:'^.columnCaption',
            datasets:'^.datasets',            
            optionsBag:'^.options',
            chartType:'^.chartType',
            datamode:kw.datamode,
            selfsubscribe_refresh:function(){
                this.rebuild();
            }
        }).getParentNode();
        node.unfreeze();
        if(kw.userObjectId){
            genro.chartjs.loadChart(chartNode,kw.userObjectId);
        }
        return chartNode;
    },

    initChartParameters:function(sourceNode,pkeys){
        var columnCaption_all = [];
        sourceNode.setRelativeData('.datasets',new gnr.GnrBag());
        sourceNode.setRelativeData('.chartType','bar');
    },

    updateDatasetsBag:function(chartNodeId){
        var chartNode = genro.nodeById(chartNodeId);
        var fields = chartNode.getRelativeData('.datasetFields');
        var fieldsCaption = chartNode.getRelativeData('.datasetFields?_displayedValue');
        var currentDatasets = chartNode.getRelativeData('.datasets') || new gnr.GnrBag();
        var defaultChartType = chartNode.getRelativeData('.chartType');
        fields = fields? fields.split(','):[];
        fieldsCaption = fieldsCaption?fieldsCaption.split(','):copyArray(fields);
        var ridx;
        currentDatasets.getNodes().forEach(function(n){
            ridx = fields.indexOf(n.label);
            if(ridx<0){
                currentDatasets.popNode(n.label);
            }else{
                fields.splice(ridx,1);
                fieldsCaption.splice(ridx,1);
            }
        }); 
        fields.forEach(function(n,idx){
            if(!currentDatasets.getNode(n)){
                var dflt = genro.chartjs._defaultValues(defaultChartType);
                var parameters = new gnr.GnrBag(objectUpdate(dflt,{label:fieldsCaption[idx]}));
                currentDatasets.setItem(n,new gnr.GnrBag({field:n,enabled:true,chartType:null,
                                                             parameters:parameters}));
            }
        });
        chartNode.setRelativeData('.datasets',currentDatasets);
    },

    _chartParametersPane:function(bc,code,pars){
        var fb = genro.dev.formbuilder(bc._('ContentPane',{region:'top'}),1,{border_spacing:'3px',margin_top:'10px'});
        fb.addField('filteringSelect',{value:'^.chartType',colspan:1,width:'10em',values:this.chartTypes,lbl:'Type'});
        fb.addField('callbackSelect',{value:'^.columnCaption',width:'10em',
                                        lbl_text_align:'right',
                                        lbl_class:'gnrfieldlabel',
                                        lbl:_T('Caption'),
                                        callback:function(kw){
                                            return pars.captionGetter(kw);},
                                        parentForm:false,hasDownArrow:true,
                                        default_value:pars.captionGetter({_querystring:'*'}).data[0]._pkey});
        fb.addField('checkBoxText',{lbl:'Datasets',width:'20em',colspan:1,value:'^.datasetFields',cols:1,valuesCb:function(){
            var index = {};
            var result = [];
            pars.datasetGetter().forEach(function(c){
                if(!(c.field in index)){
                    result.push(c.field+':'+(c.name || c.field));
                    index[c.field] = true;
                }
            });
            return result.join(',');
        }});
        bc._('dataController',{script:"genro.chartjs.updateDatasetsBag(chartNodeId);",datasetFields:'^.datasetFields',chartNodeId:pars.chartNodeId});
        var tc = bc._('TabContainer',{margin:'2px',region:'center'});
        this.datasetsGrid(tc._('ContentPane',{title:'Datasets'}),pars.chartNodeId);
        this._optionsFormPane(tc._('BorderContainer',{title:'Options'}));
        tc._('ContentPane',{title:'Options JS'})._('codemirror','optionEditor',{value:'^.options_js',config_mode:'javascript',config_lineNumbers:true,
                                                    height:'100%'});
    },

    datasetsGrid:function(pane,chartNodeId){
        var grid = pane._('quickGrid',{value:'^.datasets',addCheckBoxColumn:{field:'enabled'}});
        var that = this;
        var dtypeWidgets = {'T':'TextBox','B':'Checkbox','L':'NumberTextBox','N':'NumberTextBox'};
        grid._('column',{'field':'parameters',name:'Parameters',width:'100%',
                        _customGetter:function(row){
                            return row.parameters?row.parameters.getFormattedValue():'No Parameters';
                        },
                        edit:{modal:true,contentCb:function(pane,kw){
                            var chartNode = genro.nodeById(chartNodeId);
                            var chartType = kw.rowDataNode.getValue().getItem('chartType') || chartNode.getRelativeData('.chartType');
                            var pagesCb = genro.chartjs['_dataset_'+chartType];
                            var pages;
                            if(pagesCb){
                                pages = pagesCb();
                            }else{
                                pages = genro.chartjs._dataset__base();
                            }
                            var bc = pane._('BorderContainer',{height:'300px',width:'330px',_class:'datasetParsContainer'});
                            var top = bc._('ContentPane',{region:'top',_class:'dojoxFloatingPaneTitle'})._('div',{innerHTML:'Dataset '+kw.rowDataNode.label});
                            var tc = bc._('tabContainer',{region:'center',margin:'2px'});
                            var field,dtype,lbl,editkw;
                            pages.forEach(function(pageKw){
                                var pane = tc._('ContentPane',{title:pageKw.title});
                                var fb = genro.dev.formbuilder(pane,1,{border_spacing:'3px',datapath:'.parameters',margin:'3px',margin_top:'10px'});
                                pageKw.fields.forEach(function(fkw){
                                    dtype = fkw.dtype;
                                    editkw = objectUpdate({},fkw.edit || {});
                                    editkw.width = editkw.width || (dtype=='N' || dtype=='L') ?'7em':'12em';
                                    editkw.value = '^.'+fkw.field;
                                    if(fkw.values){
                                        editkw.tag =editkw.tag || 'filteringSelect';
                                        editkw.values = fkw.values;
                                    }
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
        grid._('column',{field:'chartType',name:'Type',edit:{tag:'filteringSelect',values:'bar,line,bubble'}});

    },

//CHART OPTIONS
    
    _op_list:'title:Title,legend:Legend,tooltip:Tooltip,hover:Hover,xAxes:X-Axes,yAxes:Y-Axes',

    _optionsFormPane:function(bc){
        var tc = bc._('tabContainer',{tabPosition:"left-h",region:'center',margin:'2px'});
        var opcode,optitle,innerBc;
        this._op_list.split(',').forEach(function(op){
            op = op.split(':');
            opcode = op[0];
            optitle = op[1];
            innerBc = tc._('BorderContainer',{title:optitle});
            var top = innerBc._('ContentPane',{region:'top',font_size:'.9em',_class:'commonTitleBar'});
            top._('div',{innerHTML:optitle,text_align:'center'});
            if(genro.chartjs['_option_'+opcode]){
                genro.chartjs['_option_'+opcode](innerBc,{datapath:'.options.'+opcode,region:'center'});
            }else{
                innerBc._('ContentPane',{region:'center'})._('div',{innerHTML:'TO DO...'});
            }
        });
    },
    

    
    _option_title:function(parent,kw){
        var pane = parent._('ContentPane',kw);
        var fb = genro.dev.formbuilder(pane,1,{border_spacing:'3px',margin:'3px',margin_top:'10px',
                                    font_size:'.9em',lbl_text_align:'right'});
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
    },

//DATASETS PARAMETERS

    _defaultDict:{
        backgroundColor:function(kw){
            return chroma(kw._baseColor).alpha(0.6).css();
        },
        borderColor:function(kw){
            return chroma(kw._baseColor).css();
        },
        borderWidth:3,
    },


    _defaultValues:function(chartType){
        var dsCallback = this['_dataset_'+chartType] || this._dataset__base;
        var result = {};
        var cbkw = {};
        cbkw._baseColor = chroma.random().hex();
        var _defaultDict = this._defaultDict;
        dsCallback().forEach(function(g){
            g.fields.forEach(function(c){
                var v = _defaultDict[c.field]
                ;
                if(isNullOrBlank(v)){
                    return;
                }
                if(typeof(v)=='function'){
                    v = v(cbkw);
                }
                result[c.field] = v;
            });
        });
        return result;
    },

    _dataset_bar:function(){
        var b1 = [{field:'label',dtype:'T',lbl:'Label'},
                {field:'xAxisID',dtype:'T',lbl:'xAxisID'},
                {field:'yAxisID',dtype:'T',lbl:'yAxisID'},
                {field:'backgroundColor',dtype:'T',lbl:'backgroundColor',multiple:true,
                        edit:{tag:'colorTextBox',mode:'rgba'}},
                {field:'borderColor',dtype:'T',lbl:'borderColor',multiple:true,edit:{tag:'colorTextBox',mode:'rgba'}},
                {field:'borderWidth',dtype:'L',lbl:'borderWidth',multiple:true,edit:{tag:'numberSpinner',minimum:0,maximum:8,width:'5em'}}];
        var b2  = [{field:'borderSkipped',dtype:'T',lbl:'borderSkipped',values:'top,left,right,bottom',multiple:true},
                {field:'hoverBackgroundColor',dtype:'T',edit:{tag:'colorTextBox',mode:'rgba'},lbl:'backgroundColor',multiple:true},
                {field:'hoverBorderColor',dtype:'T',edit:{tag:'colorTextBox',mode:'rgba'},lbl:'borderColor',multiple:true},
                {field:'hoverBorderWidth',dtype:'L',lbl:'borderWidth',multiple:true}];
        return [{title:'Bar',fields:b1},{title:'Advanced',fields:b2}];
    },


    _dataset_line:function(){
        var b1 = [  {field:'label',dtype:'T',lbl:'Label'},
                    {field:'xAxisID',dtype:'T',lbl:'xAxisID'},
                    {field:'yAxisID',dtype:'T',lbl:'yAxisID'},
                   //{field:'_xAxes_number',dtype:'T',lbl:'xAxes',values:'0,1,2,3,4'},
                   //{field:'_yAxes_number',dtype:'T',lbl:'yAxes',values:'0,1,2,3,4'},
                    {field:'fill',dtype:'T',lbl:'fill',values:'zero,top,bottom'},
                    {field:'backgroundColor',dtype:'T',edit:{tag:'colorTextBox',mode:'rgba'},lbl:'backgroundColor'},
                    {field:'borderColor',dtype:'T',edit:{tag:'colorTextBox',mode:'rgba'},lbl:'borderColor'},
                    {field:'borderWidth',dtype:'L',lbl:'borderWidth'},
                    {field:'lineTension',dtype:'N',lbl:'lineTension'},
                    {field:'borderDash',dtype:'L',lbl:'borderDash'},
                    {field:'borderDashOffset',dtype:'L',lbl:'borderDashOffset'},
                    {field:'borderJoinStyle',dtype:'T',lbl:'borderJoinStyle'},
                    {field:'showLine',dtype:'B',lbl:'showLine'},
                    {field:'spanGaps',dtype:'B',lbl:'spanGaps'},
                    {field:'steppedLine',dtype:'B',lbl:'steppedLine'}
                ];
        var point = [{field:'pointStyle',dtype:'T',lbl:'pointStyle',multiple:true,values:'circle,triangle,rect,rectRot,cross,crossRot,star,line,dash'},
                    {field:'pointBorderColor',dtype:'T',lbl:'pointBorderColor',multiple:true,edit:{tag:'colorTextBox',mode:'rgba'}},
                    {field:'pointBackgroundColor',dtype:'T',lbl:'pointBackgroundColor',multiple:true,edit:{tag:'colorTextBox',mode:'rgba'}},
                    {field:'pointBorderWidth',dtype:'L',lbl:'pointBorderWidth',multiple:true,edit:{tag:'numberSpinner',minimum:0,maximum:8,width:'5em'}},
                    {field:'pointRadius',dtype:'L',lbl:'pointRadius',multiple:true,edit:{tag:'numberSpinner',minimum:0,maximum:8,width:'5em'}},
                    {field:'pointHoverRadius',dtype:'L',lbl:'pointHoverRadius',multiple:true,edit:{tag:'numberSpinner',minimum:0,maximum:8,width:'5em'}},
                    {field:'pointHitRadius',dtype:'L',lbl:'pointHitRadius',multiple:true,edit:{tag:'numberSpinner',minimum:0,maximum:8,width:'5em'}},
                    {field:'pointHoverBorderColor',dtype:'T',lbl:'pointHoverBorderColor',multiple:true,edit:{tag:'colorTextBox',mode:'rgba'}},
                    {field:'pointHoverBackgroundColor',dtype:'T',lbl:'pointHoverBackgroundColor',multiple:true,edit:{tag:'colorTextBox',mode:'rgba'}},
                    {field:'pointHoverBorderWidth',dtype:'L',lbl:'pointBorderWidth',multiple:true,edit:{tag:'numberSpinner',minimum:0,maximum:8,width:'5em'}},
                    ];

        var b2  = [ {field:'cubicInterpolationMode',dtype:'T',lbl:'cubicInterpolationMode'},
                    {field:'borderCapStyle',dtype:'T',lbl:'borderCapStyle'}];
        return [{title:'Line',fields:b1},{title:'Point',fields:point},{title:'Advanced',fields:b2}];
    },
    _dataset_pie:function(){
        var b1 = [{field:'label',dtype:'T',lbl:'Label'},
                {field:'backgroundColor',dtype:'T',edit:{tag:'colorTextBox',mode:'rgba'},lbl:'backgroundColor',multiple:true},
                {field:'borderColor',dtype:'T',edit:{tag:'colorTextBox',mode:'rgba'},lbl:'borderColor',multiple:true},
                {field:'borderWidth',dtype:'L',lbl:'borderWidth',multiple:true}];
        return [{title:'Pie',fields:b1}];
    },
    _dataset__base:function(){
        var b1 = [{field:'label',dtype:'T',lbl:'Label'},
                {field:'backgroundColor',dtype:'T',edit:{tag:'colorTextBox',mode:'rgba'},lbl:'backgroundColor',multiple:true},
                {field:'borderColor',dtype:'T',edit:{tag:'colorTextBox',mode:'rgba'},lbl:'borderColor',multiple:true},
                {field:'borderWidth',dtype:'L',lbl:'borderWidth',multiple:true}];
        return [{title:'Parameters',fields:b1}];
    }

};