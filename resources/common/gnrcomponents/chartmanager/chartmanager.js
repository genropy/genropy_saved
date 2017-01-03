var genro_plugin_charts =  {
    openChart:function(kw){
        var code = objectPop(kw,'code');
        var title = objectPop(kw,'title');
        
        var datastruct = objectPop(kw,'struct');
        var data = objectPop(kw,'data');
        var pkeys = objectPop(kw,'pkeys');

        var wdg = genro.wdgById(code+'_floating');

        if(wdg){
            //this.updateChartParameters(wdg.sourceNode,datastruct,pkeys,data);
            wdg.show();
            wdg.bringToTop();
            return;
        }
        genro.src.getNode()._('div',code);
        var node = genro.src.getNode(code).clearValue();
        node.freeze();
        var paletteAttr = {'paletteCode':code,title:title,dockTo:false,width:'600px',height:'500px'};
        var palette = node._('palettePane',code,paletteAttr);
        var bc = palette._('BorderContainer',{_anchor:true});
        
        var confbc = bc._('BorderContainer',{region:'right',width:'320px',drawer:true,splitter:true});
        this._chartParametersPane(confbc,code);
        console.log('n',code+'_cjs');
        bc._('ContentPane',{region:'center'})._('chartjs',{height:'100%',
            nodeId:code+'_cjs',
            value:data,
            filter:pkeys && pkeys.length?pkeys:null,
            columnCaption:'^.columnCaption',
            datasets:'^.datasets',            
            options:'^.options',
            chartType:'^.chartType',
            datamode:kw.datamode
        });
        this.updateChartParameters(palette.getParentNode(),datastruct,pkeys,data);
        node.unfreeze();
        return palette;
    },

    updateChartParameters:function(sourceNode,datastruct,pkeys,data){
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
        var defaultOptions = new gnr.GnrBag();
        defaultOptions.setItem('scales/yAxes/ticks/beginAtZero',true);
        sourceNode.setRelativeData('.columnCaption_all',columnCaption_all.join(','));
        sourceNode.setRelativeData('.columnCaption',columnCaption_all[0]);
        sourceNode.setRelativeData('.datasets',datasets);
        sourceNode.setRelativeData('.ds_checked',null);
        sourceNode.setRelativeData('.chartType','bar');
        sourceNode.setRelativeData('.options',defaultOptions);

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
        var tc = bc._('TabContainer',{margin:'2px',region:'center'});
        tc._('FlatBagEditor',{path:'.datasets',box_title:'Datasets',exclude:'field,enabled',grid_region:'top',grid_addCheckBoxColumn:{field:'enabled'}});
        tc._('ContentPane',{title:'Options'})._('multiValueEditor',{value:'^.options'});

    }
};//