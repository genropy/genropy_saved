var genro_plugin_chartjs =  {
    openGridChart:function(kw){
        var grid = objectPop(kw,'grid');
        var sn = grid.sourceNode;
        var code = sn.attr.nodeId+'_chart_'+(kw.pkey || '_newchart') +'_'+ genro.getCounter();
        var chartNode = this.openChart({
                                code:code,
                                storepath:sn.absDatapath(sn.attr.storepath),
                                title:kw.caption || 'New Chart',
                                pkeys:grid.getSelectedPkeys(),
                                struct:grid.structbag().deepCopy(),
                                datamode:grid.datamode});
        sn.subscribe('onSelectedRow',function(kw){
            chartNode.setRelativeData('.filter',kw.selectedPkeys);
        });
    },
    openChart:function(kw){
        genro.setAliasDatapath('CHARTJS_DFLT','gnr.chartjs.defaults');
        genro.setAliasDatapath('CHARTJS_GLOB','gnr.chartjs.defaults.global');
        var code = objectPop(kw,'code');
        var title = objectPop(kw,'title');
        var datastruct = objectPop(kw,'struct');
        var storepath = objectPop(kw,'storepath');
        var pkeys = objectPop(kw,'pkeys');

        var wdg = genro.wdgById(code+'_floating');

        if(wdg){
            //this.updateChartParameters(wdg.sourceNode,datastruct,pkeys,data);
            wdg.show();
            wdg.bringToTop();
            return genro.nodeById(code+'_cjs');
        }
        genro.src.getNode()._('div',code);
        var node = genro.src.getNode(code).clearValue();
        node.freeze();
        var paletteAttr = {'paletteCode':code,title:title,dockTo:false,width:'600px',height:'500px'};
        var palette = node._('palettePane',code,paletteAttr);
        var bc = palette._('BorderContainer',{_anchor:true});
        
        var confbc = bc._('BorderContainer',{region:'right',width:'320px',drawer:true,splitter:true});
        this._chartParametersPane(confbc,code);
        var chartNode = bc._('ContentPane',{region:'center'})._('chartjs',{
            nodeId:code+'_cjs',
            value:'^'+storepath,
            filter:'^.filter',
            columnCaption:'^.columnCaption',
            datasets:'^.datasets',            
            options:'^.options',
            chartType:'^.chartType',
            datamode:kw.datamode,
            selfsubscribe_chartReady:function(){
                var currentOptbag = this.getRelativeData('.options');
                this.setRelativeData('.options',new gnr.GnrBag(this.externalWidget.options));
            }
        }).getParentNode();
        this.updateChartParameters(palette.getParentNode(),datastruct,pkeys);
        node.unfreeze();
        return chartNode;
    },

    updateChartParameters:function(sourceNode,datastruct,pkeys){
        var columnCaption_all = [];
        var numeric_types = {'I':true,'L':true,'N':true,'R':true};
        var text_types = {'T':true,'A':true,'C':true};
        var backgrounds = ['red','green','blue','yellow'];
        var ds_all = [];
        var datasets = new gnr.GnrBag();
        var cr = new gnr.GnrBag();   
        var common_attrs = ['backgroundColor','borderColor','borderWidth'];
        var defkw = {backgroundColor:null,borderColor:null,borderWidth:null,enabled:false};
        datastruct.walk(function(n){
            if(!n.attr.field){
                return;
            }
            if(n.attr.dtype in numeric_types){ 
                datasets.setItem(n.label,null,objectUpdate({field:n.attr.field,name:n.attr.name},defkw));
            }else if(!n.attr.dtype || n.attr.dtype in text_types){
                columnCaption_all.push(n.attr.field);
            }
        });
        sourceNode.setRelativeData('.columnCaption_all',columnCaption_all.join(','));
        sourceNode.setRelativeData('.columnCaption',columnCaption_all[0]);
        sourceNode.setRelativeData('.datasets',datasets);
        sourceNode.setRelativeData('.ds_checked',null);
        sourceNode.setRelativeData('.chartType','bar');
        sourceNode.setRelativeData('.filter',pkeys);
    },

    _chartParametersPane:function(bc,code){
        var fb = genro.dev.formbuilder(bc._('ContentPane',{region:'top'}),1,{border_spacing:'1px'});
        var modes = 'bar:Bar,line:Line,radar:Radar,polar:Polar,pie:Pie & Doughnut,bubble:Bubble,scales:Scales';
        fb.addField('filteringSelect',{value:'^.chartType',values:modes,lbl:'Type'});
        fb.addField('comboBox',{value:'^.columnCaption',width:'15em',
                                        lbl_text_align:'right',
                                        lbl_class:'gnrfieldlabel',
                                        lbl:_T('Caption'),
                                        values:'^.columnCaption_all',
                                        parentForm:false});
        fb.addField('Button',{label:'Full Options',action:function(){
            genro.dev.openBagInspector(this.absDatapath('.options'),{title:'Full Options'});
        }});
        var tc = bc._('TabContainer',{margin:'2px',region:'center'});
        tc._('FlatBagEditor',{path:'.datasets',box_title:'Datasets',exclude:'field,enabled',grid_region:'top',grid_addCheckBoxColumn:{field:'enabled'}});
        this._optionsFormPane(tc._('ContentPane',{title:'Options',datapath:'.options'}));
        tc._('ContentPane',{title:'Options JS'})._('codemirror','optionEditor',{value:'^.options_js',config_mode:'javascript',config_lineNumbers:true,
                                                    height:'100%'});
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