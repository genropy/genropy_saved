genro.setAliasDatapath('CHARTJS_DFLT','gnr.chartjs.defaults');
genro.setAliasDatapath('CHARTJS_GLOB','gnr.chartjs.defaults.global');
genro.chartjs =  {
    chartTypes:'bar,line,bubble,pie,doughnut,polarArea,radar,scatter',

    openPaletteChart:function(kw){
        //kw.chartCode
        if(!('chroma' in window)){
            genro.dom.loadJs('/_rsrc/js_libs/chroma.min.js',function(){});
            genro.dom.loadJs('/_rsrc/js_libs/distinct-colors.min.js');
        }
        var chartCode = objectPop(kw,'chartCode');
        if(chartCode){
            var wdg = genro.wdgById(chartCode+'_floating');
            if(wdg){
                wdg.show();
                wdg.bringToTop();
                return;
            }
            kw.nodeId = chartCode;
        }
        chartCode = chartCode || '_chart_'+genro.getCounter();
        genro.src.getNode()._('div',chartCode);
        var node = genro.src.getNode(chartCode).clearValue();
        node.freeze();
        kw.dockTo = kw.dockTo || 'dummyDock:open';
        if(kw.configurator!==false){
            kw.configurator = true;
        }
        var palette = node._('PaletteChart',kw);
        node.unfreeze();
        return palette;
    },

    openGridChart:function(kw){
        kw.connectedTo = objectPop(kw,'grid').sourceNode;
        kw.userObjectId = objectPop(kw,'pkey');
        return this.openPaletteChart(kw);
    },

    _defaultDict:{
        backgroundColor:function(kw){
            return chroma(kw._baseColor).alpha(0.6).css();
        },
        borderColor:function(kw){
            return chroma(kw._baseColor).css();
        },
        borderWidth:3,
    },


//CHART OPTIONS
    
    option_list:'title:Title,legend:Legend,tooltip:Tooltip,hover:Hover,xAxes:X-Axes,yAxes:Y-Axes',    

    
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

    z_option_legend:function(parent,kw){
        /*
            display Boolean true    Is the legend displayed
            position    String  'top'   Position of the legend. Possible values are 'top', 'left', 'bottom' and 'right'.
            fullWidth   Boolean true    Marks that this box should take the full width of the canvas (pushing down other boxes)
            onClick Function    function(event, legendItem) {}  A callback that is called when a 'click' event is registered on top of a label item
            onHover Function    function(event, legendItem) {}  A callback that is called when a 'mousemove' event is registered on top of a label item
            labels  Object  -   See the Legend Label Configuration section below.
            reverse Boolean false   Legend will show datasets in reverse order

        */
        kw.margin = '2px';
        var tc = parent._('tabContainer',kw);
        var main = parent._('ContentPane',{title:'Main'});
        var fb = genro.dev.formbuilder(main,1,{border_spacing:'3px',margin:'3px',margin_top:'10px',
                                    font_size:'.9em',lbl_text_align:'right'});
        fb.addField('checkbox',{value:'^.display',label:'Display'});
        fb.addField('filteringSelect',{value:'^.position',lbl:'Position',values:'top,left,bottom,right'});
        fb.addField('checkbox',{value:'^.fullWidth',label:'FullWidth'});
        fb.addField('checkbox',{value:'^.reverse',label:'reverse'});


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



    datasetDefaults:function(chartType){
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
                        edit:{tag:'colorTextBox',mode:'rgba',placeholder:'Color or "*"'}},
                {field:'borderColor',dtype:'T',lbl:'borderColor',multiple:true,edit:{tag:'colorTextBox',mode:'rgba',placeholder:'Color or "*"'}},
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
    },
//Scales grids

    scalesTab:function(bc,chartNodeId){
        var tc = bc._('tabContainer',{tabPosition:"left-h",region:'center',margin:'2px'});
        this.axesGrid(tc,{title:'X-Axes',mode:'xAxes',chartNodeId:chartNodeId //,hidden:'^.chartType?=(#v=="radar" || #v=="polarArea")'
        });
        this.axesGrid(tc,{title:'Y-Axes',mode:'yAxes',chartNodeId:chartNodeId //,hidden:'^.chartType?=(#v=="radar" || #v=="polarArea")'
        });
        this.axesGrid(tc,{title:'Radiant',mode:'radiant',chartNodeId:chartNodeId //,hidden:'^.chartType?=!(#v=="radar" || #v=="polarArea")'
        });

    },

    scales_xAxes:function(pane,chartType){
        /*
            type    String  "Category"  As defined in Scales.
            display Boolean true    If true, show the scale.
            id  String  "x-axis-0"  Id of the axis so that data can bind to it
            stacked Boolean false   If true, bars are stacked on the x-axis
            barThickness    Number      Manually set width of each bar in pixels. If not set, the bars are sized automatically.
            categoryPercentage  Number  0.8 Percent (0-1) of the available width (the space between the gridlines for small datasets) for each data-point to use for the bars. Read More
            barPercentage   Number  0.9 Percent (0-1) of the available width each bar should be within the category percentage. 1.0 will take the whole category width and put the bars right next to each other. Read More
            gridLines   Object  See Scales  
            gridLines.offsetGridLines   Boolean true    If true, the bars for a particular data point fall between the grid lines. If false, the grid line will go right down the middle of the bars.
        */
        var fb = genro.dev.formbuilder(pane,1,{border_spacing:'3px',margin:'3px',margin_top:'10px',font_size:'.9em',lbl_text_align:'right'});

        fb.addField('filteringSelect',{value:'^.type',lbl:'type',
                        values:"linear,logarithmic,time", placeholder:'linear'}); //time to be implemented
        fb.addField('checkbox',{value:'^.display',label:'display'});
        fb.addField('filteringSelect',{value:'^.position',lbl:'Position',values:'bottom,top'});

        fb.addField('checkbox',{value:'^.stacked',label:'stacked'});
        fb.addField('numberTextBox',{value:'^.barThickness',lbl:'barThickness'});
        fb.addField('numberTextBox',{value:'^.barPercentage',lbl:'barPercentage'});
    },

    scales_yAxes:function(pane,chartType){
        var fb = genro.dev.formbuilder(pane,1,{border_spacing:'3px',margin:'3px',margin_top:'10px',font_size:'.9em',lbl_text_align:'right'});
        fb.addField('filteringSelect',{value:'^.type',lbl:'type',
                        values:"linear,logarithmic", placeholder:'linear'});
        fb.addField('checkbox',{value:'^.display',label:'display'});
        fb.addField('filteringSelect',{value:'^.position',lbl:'Position',values:'left,right'});
        fb.addField('checkbox',{value:'^.stacked',label:'stacked'});
        fb.addField('numberTextBox',{value:'^.barThickness',lbl:'barThickness'});
        /*
           type    String  "linear"    As defined in Scales.
           display Boolean true    If true, show the scale.
           id  String  "y-axis-0"  Id of the axis so that data can bind to it.
           stacked Boolean false   If true, bars are stacked on the y-axis
           barThickness    Number      Manually set height of each bar in pixels. If not set, the bars are sized automatically.
        */
    },

    scales_radiant:function(pane,chartType){
        var fb = genro.dev.formbuilder(pane,1,{border_spacing:'3px',margin:'3px',margin_top:'10px',font_size:'.9em',lbl_text_align:'right'});
        fb.addField('checkbox',{value:'^.display',label:'Display'});

        /*
            ********SCALES MODE radialLinear****
            lineArc Boolean false   If true, circular arcs are used else straight lines are used. The former is used by the polar area chart and the latter by the radar chart
            angleLines  Object  -   See the Angle Line Options section below for details.
            pointLabels Object  -   See the Point Label Options section below for details.
            ticks   Object  -   See the Ticks table below for options.
        */
    },

    scales_mode_linear:function(parent){
        var pane = parent._('ContentPane',{title:'Linear',hidden:'^.type?=#v!="linear"'});
        var fb = genro.dev.formbuilder(pane,1,{border_spacing:'3px',margin:'3px',margin_top:'10px',
                        font_size:'.9em',datapath:'.linear'});
        this._scalesTitle(fb);
        fb.addField('checkbox',{value:'^.beginAtZero',label:'beginAtZero'});
        fb.addField('numberTextBox',{value:'^.min',lbl:'min'});
        fb.addField('numberTextBox',{value:'^.max',lbl:'max'});
        fb.addField('numberTextBox',{value:'^.maxTicksLimit',lbl:'maxTicksLimit'});
        fb.addField('numberTextBox',{value:'^.fixedStepSize',lbl:'fixedStepSize'});
        fb.addField('numberTextBox',{value:'^.stepSize',lbl:'stepSize'});
        fb.addField('numberTextBox',{value:'^.suggestedMax',lbl:'suggestedMax'});
        fb.addField('numberTextBox',{value:'^.suggestedMin',lbl:'suggestedMin'});

        /*
            beginAtZero Boolean -   if true, scale will include 0 if it is not already included.
            min Number  -   User defined minimum number for the scale, overrides minimum value from data.
            max Number  -   User defined maximum number for the scale, overrides maximum value from data.
            maxTicksLimit   Number  11  Maximum number of ticks and gridlines to show. If not defined, it will limit to 11 ticks but will show all gridlines.
            fixedStepSize   Number  -   User defined fixed step size for the scale. If set, the scale ticks will be enumerated by multiple of stepSize, having one tick per increment. If not set, the ticks are labeled automatically using the nice numbers algorithm.
            stepSize    Number  -   if defined, it can be used along with the min and the max to give a custom number of steps. See the example below.
            suggestedMax    Number  -   User defined maximum number for the scale, overrides maximum value except for if it is lower than the maximum value.
            suggestedMin    Number  -   User defined minimum number for the scale, overrides minimum value except for if it is higher than the minimum value.
        */
    },

    scales_mode_logarithmic:function(parent){
        /*
            min Number  -   User defined minimum number for the scale, overrides minimum value from data.
            max Number  -   User defined maximum number for the scale, overrides maximum value from data
        */
        var pane = parent._('ContentPane',{title:'Logarithmic',hidden:'^.type?=#v!="logarithmic"'});
        var fb = genro.dev.formbuilder(pane,1,{border_spacing:'3px',margin:'3px',margin_top:'10px',
                        font_size:'.9em',datapath:'.logarithmic'});
        this._scalesTitle(fb);
        fb.addField('numberTextBox',{value:'^.min',lbl:'min'});
        fb.addField('numberTextBox',{value:'^.max',lbl:'max'});
    },

    scales_mode_time:function(parent){
        var pane = parent._('ContentPane',{title:'Time',hidden:'^.type?=#v!="time"'});
        pane._('div',{innerHTML:'TO DO...'});
        /*
            displayFormats  Object  -   See Display Formats section below.
            isoWeekday  Boolean false   If true and the unit is set to 'week', iso weekdays will be used.
            max Time    -   If defined, this will override the data maximum
            min Time    -   If defined, this will override the data minimum
            parser  String or Function  -   If defined as a string, it is interpreted as a custom format to be used by moment to parse the date. If this is a function, it must return a moment.js object given the appropriate data value.
            round   String  -   If defined, dates will be rounded to the start of this unit. See Time Units below for the allowed units.
            tooltipFormat   String  ''  The moment js format string to use for the tooltip.
            unit    String  -   If defined, will force the unit to be a certain type. See Time Units section below for details.
            unitStepSize    Number  1   The number of units between grid lines.
            minUnit String  'millisecond'   The minimum display format to be used for a time unit
        */
    },
    scalesGridlines:function(pane){
        /*
            display Boolean true    
            color   Color or Array[Color]   "rgba(0, 0, 0, 0.1)"    Color of the grid lines.
            borderDash  Array[Number]   []  Length and spacing of dashes. See MDN
            borderDashOffset    Number  0.0 Offset for line dashes. See MDN
            lineWidth   Number or Array[Number] 1   Stroke width of grid lines
            drawBorder  Boolean true    If true draw border on the edge of the chart
            drawOnChartArea Boolean true    If true, draw lines on the chart area inside the axis lines. This is useful when there are multiple axes and you need to control which grid lines are drawn
            drawTicks   Boolean true    If true, draw lines beside the ticks in the axis area beside the chart.
            tickMarkLength  Number  10  Length in pixels that the grid lines will draw into the axis area.
            zeroLineWidth   Number  1   Stroke width of the grid line for the first index (index 0).
            zeroLineColor   Color   "rgba(0, 0, 0, 0.25)"   Stroke color of the grid line for the first index (index 0).
            offsetGridLines Boolean false   If true, labels are shifted to be between grid lines. This is used in the bar chart.

        */
    },

    _scalesTitle:function(fb){
        fb.addField('checkbox',{value:'^.title.display',label:'Display'});
        fb.addField('textbox',{value:'^.title.labelString',lbl:'labelString'});
        fb.addField('colorTextBox',{value:'^.title.fontColor',lbl:'fontColor'});
        fb.addField('numberTextBox',{value:'^.title.fontSize',lbl:'fontSize'});
        fb.addField('filteringSelect',{value:'^.title.fontFamily',lbl:'fontFamily',
                        values:"Helvetica Neue,Helvetica,Arial,sans-serif",
                    });
        fb.addField('filteringSelect',{value:'^.title.fontStyle',lbl:'fontStyle',
                        values:"bold,italic,normal"});
        
        /*
            display Boolean false   
            labelString String  ""  The text for the title. (i.e. "# of People", "Response Choices")
            fontColor   Color   "#666"  Font color for the scale title.
            fontFamily  String  "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"    Font family for the scale title, follows CSS font-family options.
            fontSize    Number  12  Font size for the scale title.
            fontStyle   String  "normal"    Font style for the scale title, follows CSS font-style options (i.e. normal, italic, oblique, initial, inherit).
        */
    },

    scalesTick:function(pane){
        var fb = genro.dev.formbuilder(pane,1,{border_spacing:'3px',margin:'3px',margin_top:'10px',
                        font_size:'.9em',datapath:'.ticks'});
        fb.addField('checkbox',{value:'^.beginAtZero',label:'beginAtZero'});
        /*
            autoSkip    Boolean true    If true, automatically calculates how many labels that can be shown and hides labels accordingly. Turn it off to show all labels no matter what
            autoSkipPadding Number  0   Padding between the ticks on the horizontal axis when autoSkip is enabled. Note: Only applicable to horizontal scales.
            callback    Function    function(value) { return helpers.isArray(value) ? value : '' + value; } Returns the string representation of the tick value as it should be displayed on the chart. See callback section below.
            display Boolean true    If true, show the ticks.
            fontColor   Color   "#666"  Font color for the tick labels.
            fontFamily  String  "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"    Font family for the tick labels, follows CSS font-family options.
            fontSize    Number  12  Font size for the tick labels.
            fontStyle   String  "normal"    Font style for the tick labels, follows CSS font-style options (i.e. normal, italic, oblique, initial, inherit).
            labelOffset Number  0   Distance in pixels to offset the label from the centre point of the tick (in the y direction for the x axis, and the x direction for the y axis). Note: this can cause labels at the edges to be cropped by the edge of the canvas
            maxRotation Number  90  Maximum rotation for tick labels when rotating to condense labels. Note: Rotation doesn't occur until necessary. Note: Only applicable to horizontal scales.
            minRotation Number  0   Minimum rotation for tick labels. Note: Only applicable to horizontal scales.
            mirror  Boolean false   Flips tick labels around axis, displaying the labels inside the chart instead of outside. Note: Only applicable to vertical scales.
            padding Number  10  Padding between the tick label and the axis. Note: Only applicable to horizontal scales.
            reverse Boolean false   Reverses order of tick labels.
        */
    }
};




dojo.declare("gnr.widgets.ChartPane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw, children){
        var gnrwdg = sourceNode.gnrwdg;
        var rootKw = objectExtract(kw,'height,width,region,side');
        gnrwdg.connectedWidgetId = this.getConnectedWidgetId(sourceNode,objectPop(kw,'connectedTo'));
        var chartNodeId = objectPop(kw,'nodeId') || this.autoChartNodeId(gnrwdg.connectedWidgetId);
        gnrwdg.chartNodeId = chartNodeId;
        sourceNode.attr.nodeId = 'cp_' +chartNodeId;
        sourceNode._registerNodeId();
        if(objectPop(kw,'_workspace')!==false){
            sourceNode.attr._workspace = true;
            sourceNode.attr._workspace_path = objectPop(kw,'_workspace_path');
        }
        gnrwdg.defaultDatasetFields = objectPop(kw,'datasetFields');
        gnrwdg.defaultChartType = objectPop(kw,'chartType','bar');
        gnrwdg.defaultCaptionField = objectPop(kw,'captionField');
        gnrwdg.filterpath = objectPop(kw,'filterpath') || '#WORKSPACE.filter';
        sourceNode.attr.datasetFields = '^#WORKSPACE.datasetFields';
        if(gnrwdg.connectedWidgetId){
            var sn = genro.nodeById(gnrwdg.connectedWidgetId);
            gnrwdg.table = sn.attr.table;
            if(sn.attr.tag.toLowerCase()=='tree'){
                sn.subscribe('onSelected',function(kw){
                    console.log('tree selected',kw);
                });
            }else{
                sn.subscribe('onSelectedRow',function(kw){
                    console.log('gnrwdg.filterpath',gnrwdg.filterpath);
                    sourceNode.setRelativeData(gnrwdg.filterpath,kw.selectedPkeys);
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
        sourceNode.registerDynAttr('datasetFields');

        var rootbc = sourceNode._('borderContainer',rootKw);
        //var useUserObject = kw.configurator && kw.configurator.userObject!==false;
        if(kw.configurator){
            gnrwdg.configuratorFrame(rootbc,kw);
        }
        gnrwdg.datamode = objectPop(kw,'datamode') || gnrwdg.datamode;
        var userObjectId = objectPop(kw,'userObjectId');            
        gnrwdg.setDefaults();
        gnrwdg.setDatasetFields();
        gnrwdg.chartCenter(rootbc,kw);
        if(userObjectId){
            sourceNode.watch('waitingBuild',function(){
                return genro.nodeById(gnrwdg.chartNodeId).externalWidget;
            },function(){
                gnrwdg.loadChart(userObjectId);
            });
        }
        return rootbc;
    },

    autoChartNodeId:function(connectedWidgetId){
        return  'chart_'+ (connectedWidgetId || '') +'_'+genro.getCounter();
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
    gnrwdg_resetMenuData:function(){
        var m = this.sourceNode.getRelativeData('#WORKSPACE.loadMenu');
        m.getParentNode().getResolver().reset();
    },


    gnrwdg_setLoadMenuData:function(){
        var kw = {'objtype':'chartjs',
                  'flags':genro.getData('gnr.pagename')+'_'+(this.connectedWidgetId || this.chartNodeId),
                    'table':this.table};
        this.sourceNode.setRelativeData('#WORKSPACE.loadMenu',
                                        genro.dev.userObjectMenuData(kw,[{pkey:'__newchart__',caption:_T('New chart')}]));
    },

    gnrwdg_setDefaults:function(){
        if(!this.sourceNode.getRelativeData('#WORKSPACE.chartType')){
            this.sourceNode.setRelativeData('#WORKSPACE.chartType',this.defaultChartType);
        }
        if(!this.sourceNode.getRelativeData('#WORKSPACE.captionField')){
            this.sourceNode.setRelativeData('#WORKSPACE.captionField',this.defaultCaptionField);
        }
        if(!this.sourceNode.getRelativeData('#WORKSPACE.datasetFields')){
            this.sourceNode.setRelativeData('#WORKSPACE.datasetFields',this.defaultDatasetFields,{_displayedValue:this.defaultDatasetFields});
        }
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
                genro.nodeById(this.chartNodeId).attr.datamode = this.datamode;
            }
        }
    },

    gnrwdg_getData:function(){
        return this.sourceNode.getRelativeData(this.sourceNode.attr.storepath);
    },

    gnrwdg__fgetter:function(types,captions){
        var result = [];
        var s = {};
        if(this.connectedWidgetId){
            var widgetNode = genro.nodeById(this.connectedWidgetId);
            if(widgetNode.attr.structpath){
                var structbag = widgetNode.getRelativeData(widgetNode.attr.structpath);
                
                if(structbag){
                    var colsets =  structbag.getItem('info.columnsets') || new gnr.GnrBag();
                    let gridrow = structbag.getItem('view_0.rows_0');
                    if (!gridrow){
                        return;
                    }
                    gridrow.forEach(function(n){
                        var c = objectUpdate({},n.attr);
                        if(c.name){
                            c.name = c.name.replace(/<br\/>/g,' ');
                        }
                        if(c.columnset && colsets.getNode(c.columnset)){
                            c.name = colsets.getNode(c.columnset).attr.name+' '+c.name;
                        }
                        if(captions && c.group_aggr && 'LNRIF'.indexOf(c.dtype)>=0){
                            return;
                        }
                        if((c.dtype || 'T') in types && !(c.field in s)){
                            var f = c.field_getter || c.field;
                            f = f.replace(/\W/g, '_');
                            if(c.group_aggr){
                                f+='_'+c.group_aggr.toLowerCase().replace(/\W/g, '_');
                            }
                            c.code = f;
                            s[f] = true;
                            
                            result.push(c);
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
                                result.push({'code':n.key,'name':n.key});
                            }
                        }
                    }
                    );
                    return '__continue__';
                },'static');
            }
            
        }
        return result;

    },
    gnrwdg_datasetsGetter:function(){
        return this._fgetter({'I':true,'L':true,'N':true,'R':true});
    },

    gnrwdg_captionGetter:function(kw){
        kw = kw || {};
        var g = this._fgetter({'D':true,'T':true,'A':true,'C':true,'L':true,'I':true},true);
        if(!g){
            return;
        }
        var data = [];
        if(this.defaultCaptionField && !g.length){
            data.push({_pkey:this.defaultCaptionField,caption:this.defaultCaptionField});
        }
        var _id = kw._id;
        var _querystring = kw._querystring;
        g.forEach(function(n){
            if(_id && n.code == _id){
                data.push({_pkey:n.code,caption:n.name});
            }else if (_querystring && n.name.toLowerCase().indexOf(_querystring.slice(0,-1).toLowerCase())>=0){
                data.push({_pkey:n.code,caption:n.name});
            }
        });
        return {data:data};
    },
    gnrwdg_addDataset:function(kw){
        var sourceNode = this.sourceNode;
        var fields = sourceNode.getAttributeFromDatasource('datasetFields');
        var fieldsCaption = sourceNode.getRelativeData('#WORKSPACE.datasetFields?_displayedValue');
        fields = fields?fields.split(','):[];
        if(fields.indexOf(kw.field)<0){
            fields.push(kw.field);
            fieldsCaption = fieldsCaption?fieldsCaption.split(','):[];
            fieldsCaption.push(kw.caption);
            fieldsCaption = fieldsCaption.join(',');
            fields = fields.join(',');
            console.log('fieldsCaption',fieldsCaption,kw);

        }
        sourceNode.setRelativeData('#WORKSPACE.datasetFields',fields,{_displayedValue:fieldsCaption});
    },

    gnrwdg_setDatasetFields:function(){
        var sourceNode = this.sourceNode;
        var fields = sourceNode.getAttributeFromDatasource('datasetFields');
        var fieldsCaption = sourceNode.getRelativeData('#WORKSPACE.datasetFields?_displayedValue');
        var currentDatasets = sourceNode.getRelativeData('#WORKSPACE.datasets') || new gnr.GnrBag();
        var defaultChartType = sourceNode.getRelativeData('#WORKSPACE.chartType');
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
        var that = this;
        fields.forEach(function(n,idx){
            if(!currentDatasets.getNode(n)){
                var dflt = genro.chartjs.datasetDefaults(defaultChartType);
                var parameters = new gnr.GnrBag(objectUpdate(dflt,{label:fieldsCaption[idx]}));
                currentDatasets.setItem(n,new gnr.GnrBag({field:n,enabled:true,chartType:null,
                                                             parameters:parameters}));
            }
        });
        sourceNode.setRelativeData('#WORKSPACE.datasets',currentDatasets);
    },

    gnrwdg_chartCenter:function(bc,kw){
        bc._('ContentPane',{region:'center'})._('chartjs',{
            nodeId:this.chartNodeId,
            storepath:this.storepath,
            filter:kw.filter || '^'+this.filterpath,
            onClick:kw.onClick,
            captionField:'^#WORKSPACE.captionField',
            datasets:'^#WORKSPACE.datasets',            
            optionsBag:'^#WORKSPACE.options',
            scalesBag:'^#WORKSPACE.scales',
            chartType:'^#WORKSPACE.chartType',
            datamode:this.datamode,
            selfsubscribe_refresh:function(){
                this.rebuild();
            },
            selfsubscribe_addAxis:function(kw){
                var scalesBag = this.getAttributeFromDatasource('scalesBag');
                var axebag = scalesBag.getItem(kw.axes);
                if(!axebag){
                    axebag = new gnr.GnrBag();
                    scalesBag.setItem(kw.axes,axebag);
                }
                var position = kw.axes=='xAxes'?'top':'right';
                var dkw = {id:kw.id,type:'linear',position:position,scaleLabel:{
                          labelString:kw.id,
                          display:true},
                          gridLines:{drawOnChartArea:false}};
                axebag.setItem('r_'+axebag.len(),new gnr.GnrBag(dkw),{_autolist:true});
                this.publish('refresh');        
            }
        });
    },
    gnrwdg_configuratorFrame:function(parentBc,kw){
        var confkw = objectPop(kw,'configurator');
        confkw = confkw===true?{region:'right',drawer:(kw.userObjectId || this.defaultDatasetFields)?'close':true,splitter:true,border_left:'1px solid #ccc',width:'320px'}:confkw;       
        var userObject = objectPop(confkw,'userObject');
        var parent = parentBc;
        if(confkw.palette){
            var paletteCode = confkw.palette;
            var paletteKw = {paletteCode:paletteCode,dockTo:'dummyDock'};
            paletteKw['subscribe_'+paletteCode+'_open'] = function(){
                genro.wdgById(paletteCode+'_floating').show();
            };
            parent = parentBc._('palettePane',paletteKw);
        }
        var confframe = parent._('FramePane',objectUpdate(confkw,{frameCode:this.chartNodeId+'_options'}));
        var that = this;
        var bar;
        if(userObject!==false){
            this.setLoadMenuData();
            bar = confframe._('slotBar',{toolbar:true,side:'top',slots:'5,loadMenu,2,chartTitle,*,fulloptions,refresh,saveBtn,5'});
    
            bar._('div','chartTitle',{innerHTML:'^#WORKSPACE.metadata.description?=(#v || "New Chart")',font_weight:'bold',font_size:'.9em',color:'#666'});
            bar._('slotButton','fulloptions',{label:'Full Options',iconClass:'iconbox gear',action:function(){
                genro.dev.openBagInspector(this.absDatapath('#WORKSPACE.options'),{title:'Full Options'});
            }});
            bar._('slotButton','refresh',{label:'Refresh',iconClass:'iconbox reload',action:function(){
                genro.nodeById(that.chartNodeId).publish('refresh');
            }});
            bar._('slotButton','loadMenu',{iconClass:'iconbox folder',label:'Load',
                menupath:'#WORKSPACE.loadMenu',action:function(item){
                    that.loadChart(item.pkey);
                }});
            bar._('slotButton','saveBtn',{iconClass:'iconbox save',label:'Save',
                                            action:function(){
                                                that.saveChart();
                                            }});
                                            
        }else{
            bar = confframe._('slotBar',{toolbar:true,side:'top',slots:',2,*,fulloptions,refresh,5'});    
            bar._('slotButton','fulloptions',{label:'Full Options',iconClass:'iconbox gear',action:function(){
                genro.dev.openBagInspector(this.absDatapath('#WORKSPACE.options'),{title:'Full Options'});
            }});
            bar._('slotButton','refresh',{label:'Refresh',iconClass:'iconbox reload',action:function(){
                genro.nodeById(that.chartNodeId).publish('refresh');
            }});
        }
        var bc = confframe._('BorderContainer',{side:'center'});

        var fb = genro.dev.formbuilder(bc._('ContentPane',{region:'top'})._('div',{margin_right:'10px'}),1,{border_spacing:'3px',margin_top:'10px',width:'100%'});
        fb.addField('filteringSelect',{value:'^#WORKSPACE.chartType',colspan:1,width:'10em',values:genro.chartjs.chartTypes,lbl:'Type'});
        let captions = this.captionGetter({_querystring:'*'});
        if(!captions){
            return;
        }
        var fistCap = captions.data[0] || {};
        fb.addField('callbackSelect',{value:'^#WORKSPACE.captionField',width:'10em',
                                        lbl_text_align:'right',
                                        lbl_class:'gnrfieldlabel',
                                        lbl:_T('Caption'),
                                        callback:function(kw){
                                            return that.captionGetter(kw);
                                        },
                                        parentForm:false,hasDownArrow:true,
                                        default_value:fistCap.code});
        fb.addField('checkBoxText',{lbl:'Datasets',width:'100%',colspan:1,
                                    value:'^#WORKSPACE.datasetFields',
                                    cols:1,valuesCb:function(){
                                        var index = {};
                                        var result = [];
                                        that.datasetsGetter().forEach(function(c){
                                            if(!(c.code in index)){
                                                result.push(c.code+':'+(c.name || c.code));
                                                index[c.code] = true;
                                            }
                                    });
                                    return result.join(',');
                                }});
        var tc = bc._('TabContainer',{margin:'2px',region:'center'});
        this.datasetsTab(tc._('ContentPane',{title:'Datasets'}));
        this.scalesTab(tc._('BorderContainer',{title:'Scales'}));
        this.optionsTab(tc._('BorderContainer',{title:'Options'}));
    },

    gnrwdg_datasetForm:function(pane,kw){
        var sn = pane.getParentNode();
        var chartType = sn.getRelativeData('.chartType') || this.sourceNode.getRelativeData('#WORKSPACE.chartType');
        var pagesCb = genro.chartjs['_dataset_'+chartType];
        var pages;
        if(pagesCb){
            pages = pagesCb();
        }else{
            pages = genro.chartjs._dataset__base();
        }
        var dtypeWidgets = {'T':'TextBox','B':'Checkbox','L':'NumberTextBox','N':'NumberTextBox'};
        var bc = pane._('BorderContainer',{height:'300px',width:'330px',_class:'datasetParsContainer'});
        var top = bc._('ContentPane',{region:'top',_class:'dojoxFloatingPaneTitle'})._('div',{innerHTML:'Dataset '+sn.getRelativeData('.field')});
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
    },

    gnrwdg_datasetsTab:function(pane){
        var grid = pane._('quickGrid',{value:'^'+this.sourceNode.absDatapath('#WORKSPACE.datasets'),
                                    selfDragRows:true,canSort:false,
                                    addCheckBoxColumn:{field:'enabled'}});
        var that = this;
        
        grid._('column',{'field':'parameters',name:'Parameters',width:'100%',
                        _customGetter:function(row){
                            return row.parameters?row.parameters.getFormattedValue():'No Parameters';
                        },
                        edit:{modal:true,contentCb:function(pane,kw){
                            that.datasetForm(pane,kw);
                        }}});
        grid._('column',{field:'chartType',name:'Type',edit:{tag:'filteringSelect',values:'bar,line,bubble'}});
    },

    gnrwdg_scalesTab:function(bc,chartNodeId){
        var tc = bc._('tabContainer',{tabPosition:"left-h",region:'center',margin:'2px'});
        this.axesGrid(tc,{title:'X-Axes',mode:'xAxes'//,hidden:'^.chartType?=(#v=="radar" || #v=="polarArea")'
        });
        this.axesGrid(tc,{title:'Y-Axes',mode:'yAxes'//,hidden:'^.chartType?=(#v=="radar" || #v=="polarArea")'
        });
        this.axesGrid(tc,{title:'Radiant',mode:'radiant'//,hidden:'^.chartType?=!(#v=="radar" || #v=="polarArea")'
        });
    },

    gnrwdg_axesGrid:function(parent,kw){
        var bc = parent._('BorderContainer',{title:kw.title,hidden:kw.hidden});
        var top = bc._('ContentPane',{region:'top',font_size:'.9em',_class:'commonTitleBar'});
        top._('div',{innerHTML:kw.title,text_align:'center'});
        var center = bc._('ContentPane',{region:'center'});
        var grid = center._('quickGrid',{value:'^'+this.sourceNode.absDatapath('#WORKSPACE.scales.'+kw.mode),canSort:false});
        var that = this;
        grid._('column',{'field':'parameters',name:'Parameters',width:'100%',
                        _customGetter:function(row,rowIndex){
                            var b = new gnr.GnrBag(row);
                            return b.getFormattedValue();
                        },
                        edit:{modal:true,contentCb:function(pane,editkw){
                            var chartType = editkw.rowDataNode.getValue().getItem('chartType') || that.sourceNode.getRelativeData('#WORKSPACE.chartType');
                            var bc = pane._('BorderContainer',{height:'300px',width:'330px',_class:'datasetParsContainer'});
                            var top = bc._('ContentPane',{region:'top',_class:'dojoxFloatingPaneTitle'})._('div',{innerHTML:kw.title+' '+editkw.rowDataNode.getValue().getItem('id')});
                            var center = bc._('TabContainer',{region:'center',margin:'2px'});
                            genro.chartjs['scales_'+kw.mode](center._('ContentPane',{title:'Main'}),chartType);
                            if(kw.mode!='radiant'){
                                genro.chartjs.scales_mode_linear(center);
                                genro.chartjs.scales_mode_logarithmic(center);
                                if(kw.mode=='xAxes'){
                                    genro.chartjs.scales_mode_time(center);
                                }
                            }
                            genro.chartjs.scalesGridlines(center._('ContentPane',{title:'Gridlines Conf.',datapath:'.gridLines'}),chartType);
                            genro.chartjs.scalesTick(center._('ContentPane',{title:'Tick Conf.',datapath:'.ticks'}),chartType);
                        }
        }});
    },

    gnrwdg_optionsTab:function(bc){
        var tc = bc._('tabContainer',{tabPosition:"left-h",region:'center',margin:'2px'});
        var opcode,optitle,innerBc;
        genro.chartjs.option_list.split(',').forEach(function(op){
            op = op.split(':');
            opcode = op[0];
            optitle = op[1];
            innerBc = tc._('BorderContainer',{title:optitle});
            var top = innerBc._('ContentPane',{region:'top',font_size:'.9em',_class:'commonTitleBar'});
            top._('div',{innerHTML:optitle,text_align:'center'});
            if(genro.chartjs['_option_'+opcode]){
                genro.chartjs['_option_'+opcode](innerBc,{datapath:'#WORKSPACE.options.'+opcode,region:'center'});
            }else{
                innerBc._('ContentPane',{region:'center'})._('div',{innerHTML:'TO DO...'});
            }
        });
    },

    gnrwdg_saveChart:function() {
        var connectedWidgetId = this.connectedWidgetId || this.chartNodeId;
        var chartNode =genro.nodeById(this.chartNodeId);
        var that = this;
        var instanceCode = chartNode.getRelativeData('#WORKSPACE.metadata.code');
        var chartPars = chartNode.getRelativeData('#WORKSPACE').deepCopy();
        var datapath = chartNode.absDatapath('#WORKSPACE.metadata');
        chartPars.popNode('metadata');
        chartPars.popNode('filter');
        chartPars.popNode('options');
        chartPars.popNode('loadMenu');

        var options = chartNode.getRelativeData(chartNode.attr.optionsBag);
        var savedOptions = new gnr.GnrBag();
        options.walk(function(n){
            if(n.attr._userChanged){
                var fullpath = n.getFullpath(null,options);
                savedOptions.setItem(fullpath.replace(/\./g, '_'),null,{path:fullpath,value:n.getValue()});
            }
        });
        chartPars.setItem('savedOptions',savedOptions);
        saveCb = function(dlg) {
            var metadata = genro.getData(datapath);
            var pagename = genro.getData('gnr.pagename');
            var flags = metadata.getItem('flags');
            metadata.setItem('flags',pagename+'_'+connectedWidgetId);
            genro.serverCall('_table.adm.userobject.saveUserObject',
                            {'objtype':'chartjs','metadata':metadata,
                            'data':chartPars,
                            table:that.table},
                            function(result) {
                                dlg.close_action();

                                that.resetMenuData();
                            });
        };
        genro.dev.userObjectDialog(instanceCode ? 'Save Chart ' + instanceCode : 'Save New Chart',datapath,saveCb);
    },

    gnrwdg_loadChart:function(userObjectId,fistLoad){
        var chartNode = genro.nodeById(this.chartNodeId);
        if(userObjectId=='__newchart__'){
            chartNode.freeze();
            chartNode.setRelativeData('#WORKSPACE.metadata',new gnr.GnrBag());
            chartNode.setRelativeData('#WORKSPACE.datasetFields',null);
            chartNode.setRelativeData('#WORKSPACE.captionField',null);
            chartNode.setRelativeData('#WORKSPACE.scales',new gnr.GnrBag());
            chartNode.setRelativeData('#WORKSPACE.options',new gnr.GnrBag());
            chartNode.setRelativeData('#WORKSPACE.chartType','bar');
            setTimeout(function(){
                chartNode.unfreeze();
            },1);
        }else{
            genro.serverCall('_table.adm.userobject.loadUserObject', {pkey:userObjectId}, 
            function(result){
                chartNode.freeze();
                chartNode.setRelativeData('#WORKSPACE.metadata',new gnr.GnrBag(result.attr));
                var data = result.getValue();
                var savedOptions = data.pop('savedOptions');
                var scales = data.pop('scales');
                if(scales && scales.len() && (scales.getItem('xAxes').len()>1 || scales.getItem('yAxes').len()>1)){
                    chartNode.setRelativeData('#WORKSPACE.scales',scales);
                }
                data.forEach(function(n){
                    chartNode.setRelativeData('#WORKSPACE.'+n.label,n.getValue(),n.attr);
                });
                savedOptions.forEach(function(n){
                    chartNode.setRelativeData('#WORKSPACE.options.'+n.attr.path,n.attr.value);
                });
                setTimeout(function(){
                    chartNode.unfreeze();
                },1);
            });
        }
    }
});



dojo.declare("gnr.widgets.PaletteChart", gnr.widgets.ChartPane, {
    createContent:function(sourceNode, kw, children){
        var palettePars = objectExtract(kw,'paletteCode,title,height,width,top,right,dockButton,dockTo');
        if(palettePars.dockButton===true){
            palettePars.dockButton = {iconClass:'iconbox chart_bar'};
        }
        palettePars._lazyBuild = true;
        palettePars._workspace = true;
        palettePars.title = palettePars.title || 'Chart';
        palettePars.top = palettePars.top || '20px';
        palettePars.right = palettePars.right || '20px';
        palettePars.height = palettePars.height || '400px';
        palettePars.width = palettePars.width || '700px';
        var connectedWidgetId = this.getConnectedWidgetId(sourceNode,kw.connectedTo);
        kw.nodeId = kw.nodeId || this.autoChartNodeId(connectedWidgetId);
        palettePars.paletteCode = palettePars.paletteCode || kw.nodeId;
        kw._workspace = false;
        var palette = sourceNode._('palettePane',palettePars);
        var chartPane = palette._('ChartPane','chartPane',kw);
        return chartPane;
    }
});
