dojo.declare("gnr.widgets.GoogleLoader", null, {
    geocoder:{module_name:'maps',other_params: "sensor=false",version:'3.26',language:navigator.language
    },
              
    constructor: function(application) {
        this.pending_commands=[];
        this.ready = true;
        var that=this;
        if (!window.google){
            this.ready = false;
            genro.dom.loadJs("https://www.google.com/jsapi",
                          function(){
                              that.ready=true;
                              dojo.forEach(that.pending_commands, function(cb){
                                  cb.call(that);
                              });
                              that.pending_commands=[];
                          });
        }
    },
    
    runCommand:function(module,cb){
        var that=this;
        if (!this.ready){
            this.pending_commands.push(function(){
                that.runCommand(module,cb);
            });
            return;
        }
        var handler=google[module.module_name];
        if(handler && handler._loaded){
            cb.call(this);
        }
        else if('pending_calls' in module){
            module.pending_calls.push(cb);
        }
        else {
            var kw=objectUpdate({},module);
            var pending_calls=[cb];
            module.pending_calls=pending_calls;
            var module_name=objectPop(kw,'module_name');
            var version=objectPop(kw,'version');
            kw.callback=function(){
                handler=google[module_name];
                handler._loaded=true;
                 dojo.forEach(pending_calls, function(cb){
                     cb.call(that);
                 });
            };
            google.load(module_name,version,kw);
        }
    },
    setGeocoder:function(widget,cb){
        var obj=widget;
        if(this._mapkey){
            this.geocoder.other_params+=('&key='+this._mapkey);
        }
        this.runCommand(this.geocoder,function(){
            obj.geocoder = new google.maps.Geocoder();
            if (cb){
                cb();
            }
        });
    }

});
dojo.declare("gnr.widgets.fullcalendar", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    getAddOnDict:function(key){
        return {}[key];
    },
    creating: function(attributes, sourceNode) {
        var boxAttrs = objectExtract(attributes,'box_*');
        var calAttrs = objectUpdate({},attributes);
        var storepath = objectPop(calAttrs,storepath);
        
        objectPopAll(attributes);
        objectUpdate(attributes,boxAttrs);
        //var readOnly = objectPop(attributes,'readOnly');

        return {calAttrs:calAttrs,storepath:storepath};
    },

    created:function(widget, savedAttrs, sourceNode){
        var that = this;
        if(sourceNode.attr.storepath){
            sourceNode.attr.storepath = sourceNode.absDatapath(sourceNode.attr.storepath);
            sourceNode.registerDynAttr('storepath');
        }
        var cb = function(){
            setTimeout(function(){
                that.initialize(widget,savedAttrs.calAttrs);
            },000);
        }
        if(!window.FullCalendar){
            this.loadFullCalendar(cb);
        }else{
            cb();
        }
    },

    loadFullCalendar:function(cb){
        var urlist = ['/_rsrc/js_libs/fullcalendar/premium/main.min.css'];
        genro.dom.addHeaders(urlist,function(){
            genro.dom.loadJs('/_rsrc/js_libs/fullcalendar/premium/main.js',cb);
        });
    },

    initialize:function(domroot,calAttrs){
        //dojo.style(domroot,{position:'relative'})
        calAttrs.schedulerLicenseKey = genro._('gnr.api_keys.fullcalendar?schedulerLicenseKey');
        var that = this;
        calAttrs.eventSources = [function(info,successCallback,failureCallback){
            return that.readEventStore(domroot.sourceNode,info,successCallback,failureCallback);
        }]
        var calendar = new FullCalendar.Calendar(domroot,calAttrs);
        //dojo.style(domroot.firstChild,{height:'inherit',top:0,left:0,right:0,bottom:0,position:'absolute'})
       
        calendar.render();
        calendar.sourceNode = domroot.sourceNode;
        calendar.gnr = this;
        calendar.sourceNode.externalWidget = calendar;
        for (var prop in this) {
            if (prop.indexOf('mixin_') == 0) {
                calendar[prop.replace('mixin_', '')] = this[prop];
            }
        }
    },

    mixin_gnr_storepath:function(value,kw, trigger_reason){        
        var calendar = this;
        this.sourceNode.delayedCall(function(){
            console.log('update')
            calendar.refetchEvents();
        }, 500,'updatingContent')    
    },
    
    readEventStore:function(sourceNode,info,successCallback,failureCallback){
        var store = sourceNode.getRelativeData(sourceNode.attr.storepath);
        var events= []
        if(!store){
            return
        }
        store.getNodes().forEach(function(n){
            let row = objectUpdate({},n.attr);
            let v = n.getValue();
            if(v){
                objectUpdate(row,v.asDict());
            }
            if(row.start && row.end){
                events.push(row);
            }
        });
        if(!events.length){
            events = [{title:'Prova',start:new Date()}]
        }
        console.log('successCallback',events);
        successCallback(events);
        
    }
});
dojo.declare("gnr.widgets.codemirror", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    getAddOnDict:function(key){
        return {
            search:{
                command:'find',
                js:['addon/search/search.js','addon/search/searchcursor.js','addon/dialog/dialog.js'],
                css:['addon/dialog/dialog.css'],
            },lint:{
                command:'lint',
                js:['//ajax.aspnetcdn.com/ajax/jshint/r07/jshint.js','addon/lint/lint.js','addon/lint/javascript-lint.js'],
                css:['addon/lint/lint.css'],
            }
        }[key];
    },
    creating: function(attributes, sourceNode) {
        //if (sourceNode.attr.storepath) {
        //    sourceNode.registerDynAttr('storepath');
        //}
        var cmAttrs = objectExtract(attributes,'config_*');
        var readOnly = objectPop(attributes,'readOnly');
        var lineWrapping = objectPop(attributes,'lineWrapping');

        if(readOnly){
            cmAttrs.readOnly = readOnly;
        }
        if(lineWrapping){
            cmAttrs.lineWrapping = lineWrapping;
        }
        cmAttrs.value = objectPop(attributes,'value') || '';
        return {cmAttrs:cmAttrs}
    },

    created:function(widget, savedAttrs, sourceNode){
        var that = this;
        var cmAttrs = objectPop(savedAttrs,'cmAttrs');
        var mode = cmAttrs.mode;
        var theme = cmAttrs.theme;
        var addon = cmAttrs.addon;
        if(addon){
            addon = addon.split(',');
        }

        var cb = function(){
            that.load_mode(mode,function(){
                if(theme){
                    that.load_theme(theme,function(){that.initialize(widget,cmAttrs,sourceNode)})
                }
                else{
                    that.initialize(widget,cmAttrs,sourceNode);
                }
             });
            if(addon){
                addon.forEach(function(addon){
                    that.load_addon(addon)
                })
            }
        }
        if(!window.CodeMirror){
            this.loadCodeMirror(cb);
        }else{
            cb();
        }
    },

    loadCodeMirror:function(cb){
        var urlist = ['/_rsrc/js_libs/codemirror/lib/codemirror.js',
                    '/_rsrc/js_libs/codemirror/lib/codemirror.css'];
        genro.dom.addHeaders(urlist,function(){
            genro.dom.loadJs('/_rsrc/js_libs/codemirror/addon/mode/overlay.js',cb);
        });
        
    },
    defineKeyMap:function(name,keyMap){
        CodeMirror.keyMap[name] = objectUpdate(keyMap,CodeMirror.keyMap['default']);
    },


    initialize:function(widget,cmAttrs,sourceNode){
        this.defineKeyMap('softTab',{'Tab':function(cm){
                                          var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
                                          cm.replaceSelection(spaces);
                                      }
                                });
        dojo.style(widget,{position:'relative'})
        var cm = CodeMirror(widget,cmAttrs);
        dojo.style(widget.firstChild,{height:'inherit',top:0,left:0,right:0,bottom:0,position:'absolute'})
        cm.refresh();
        cm.sourceNode = sourceNode;
        cm.gnr = this;
        sourceNode.externalWidget = cm;
        for (var prop in this) {
            if (prop.indexOf('mixin_') == 0) {
                cm[prop.replace('mixin_', '')] = this[prop];
            }
        }
        cm.on('update',function(){
            sourceNode.delayedCall(function(){
                var v = sourceNode.externalWidget.getValue();
                sourceNode.setRelativeData(sourceNode.attr.value,v,null,null,sourceNode);
            },sourceNode.attr._delay || 500,'updatingContent')
        })
    },


    load_theme:function(theme,cb){
        genro.dom.loadCss('/_rsrc/js_libs/codemirror/theme/'+theme+'.css','codemirror_'+theme,cb);
    },

    load_addon:function(addon,cb){
        var that = this;
        var addondict = this.getAddOnDict(addon);
        if (!CodeMirror.commands[addondict.command]){
            addondict.js.forEach(function(path){
                if(path[0]=='/'){
                    genro.dom.loadJs(path);
                }else{
                    genro.dom.loadJs('/_rsrc/js_libs/codemirror/'+path);
                }
                 
            })
            addondict.css.forEach(function(path){
                 genro.dom.loadCss('/_rsrc/js_libs/codemirror/'+path);
            })
        }
    },

    load_mode:function(mode,cb){
        var that = this;
        if (!(mode in CodeMirror.modes)){
            genro.dom.loadJs('/_rsrc/js_libs/codemirror/mode/'+mode+'/'+mode+'.js',function(){
                if(CodeMirror.modes[mode].dependencies){
                    var i =0;
                    CodeMirror.modes[mode].dependencies.forEach(function(dep){
                        i++;
                        if(CodeMirror.modes[mode].dependencies.length==i){
                            that.load_mode(dep,function(){
                                setTimeout(function(){cb()},10);
                            });
                        }else{
                            that.load_mode(dep);
                        }
                    });
                }
                else if(cb){
                    cb()
                }
            });
        }
        else if(cb){
            cb();
        }
    },

    mixin_gnr_value:function(value,kw, trigger_reason){        
        this.setValue(value || '');
        var that = this;
        var sourceNode = this.sourceNode;

        sourceNode.watch('isVisible',function(){
            return genro.dom.isVisible(sourceNode);
        },function(){
            that.refresh();
        });
    },


    mixin_gnr_setDisabled:function(disabled){
        genro.dom.setDomNodeDisabled(this.sourceNode.domNode,disabled);
        this.gnr_readOnly(disabled);
    },

    mixin_gnr_readOnly:function(value,kw,trigger_reason){
        this.setOption('readOnly',value?'nocursor':false);
    },

    mixin_gnr_lineWrapping:function(value,kw,trigger_reason){
        this.setOption('lineWrapping',value);
    },


    mixin_gnr_quoteSelection:function(startchunk,endchunk){
        endchunk = endchunk || startchunk;
        var oldtxt = this.doc.getSelection();
        var newtxt = startchunk+oldtxt+endchunk;
        this.doc.replaceSelection(newtxt);
    }
});


dojo.declare("gnr.widgets.chartjs", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'canvas';
    },


    creating: function(attributes, sourceNode) {
        sourceNode.registerDynAttr('storepath');
        var savedAttrs = objectExtract(attributes,'chartType,filter,datasets,captionField,options,data,scalesBag,onClick');
        return savedAttrs;
    },
    

    created:function(domNode, savedAttrs, sourceNode){
        //var chartjs_root = document.createElement('canvas');
        //domNode.appendChild(chartjs_root);
        var data = savedAttrs.data;
        var dataset = savedAttrs.dataset;
        var filter = savedAttrs.filter;
        var captionField = savedAttrs.captionField;
        var options = savedAttrs.options || {maintainAspectRatio:false};
        if(savedAttrs.onClick){
            options.onClick = funcCreate(savedAttrs.onClick,'event,elements',sourceNode);
        }
        var chartType = savedAttrs.chartType;
        var scalesBag = savedAttrs.scalesBag;
        var scalesOpt;
        var that = this;
        dojo.connect(sourceNode,'_onDeleting',function(){
            //Chart.helpers.removeResizeListener(sourceNode.domNode);
            //sourceNode.externalWidget.destroy();
        });
        if(scalesBag){
            if(scalesBag){
                scalesOpt = scalesBag.asDict(true,true);
                objectPop(scalesOpt,'radiant'); //to implement
                if(objectNotEmpty(scalesOpt)){
                    options.scales = scalesOpt;
                }else{
                    scalesOpt = false;
                }
                
            }
        }
        sourceNode.freeze();
        var cb = function(){
            sourceNode.unfreeze(true);
            var chartjs = new Chart(domNode,{'type':chartType,options:options});
            sourceNode.externalWidget = chartjs;
            chartjs.sourceNode = sourceNode;
            chartjs.gnr = that;
            for (var prop in that) {
                if (prop.indexOf('mixin_') === 0) {
                    chartjs[prop.replace('mixin_', '')] = that[prop];
                }
            }
            sourceNode.publish('chartReady');
            if(sourceNode.attr.optionsBag){
                var optionsBag = sourceNode.getAttributeFromDatasource('optionsBag');
                if(optionsBag && optionsBag.getNodeByAttr('_userChanged')){
                    optionsBag.walk(function(n){
                        if(n.attr._userChanged){
                            n.setValue(n._value);
                        }
                    });
                }else{
                    sourceNode.setAttributeInDatasource('optionsBag',new gnr.GnrBag(chartjs.options));
                }
                if(!scalesOpt){
                    sourceNode.setAttributeInDatasource('scalesBag',new gnr.GnrBag(chartjs.options.scales));
                }
            }
            chartjs.gnr_updateChart();
        };
        if(!window.Chart){
            //var url = '/_rsrc/js_libs/Chart.min.js'; 
            var url ='/_rsrc/js_libs/Chart.js';
            genro.dom.loadJs(url,function(){
                genro.setData('gnr.chartjs.defaults',new gnr.GnrBag(Chart.defaults));
                cb();
            });
        }else{
            setTimeout(cb,1);
        }
    },
    autoColors:function(dataset){
        var colorParNames = ['backgroundColor:0.7','borderColor:1',
                            'pointBackgroundColor:1','pointBorderColor:1'];
        var result = {};
        colorParNames.forEach(function(n){
            n = n.split(':'); 
            if(dataset[n[0]]=='*'){
                dataset[n[0]] = [];
                result[n[0]] = n[1];
            }
        });
        return result;
    },

    makeDataset:function(kw){
        var field = objectPop(kw,'field');

        var dataset = objectUpdate({data:[]},kw.pars);
        var autoColorsDict = this.autoColors(dataset);
        objectPop(dataset,'enabled');
        var idx = 0;
        var k;
        var caption;
        var isBagMode = kw.datamode=='bag';
        kw.rows.walk(function(n){
            if('pageIdx' in n.attr){return;}
            var row = isBagMode?n.getValue('static').asDict() : n.attr;
            var pkey = row._pkey || n.label;
            if(kw.filterCb(pkey,row)){
                var chart_row_pars = objectExtract(row,'chart_*');
                caption = row[kw.captionField] || (dataset.label || field)+' '+idx;
                if('labels' in kw){
                    kw.labels.push(caption);
                }
                dataset.data.push(row[field]);
                var autocol = chroma(stringToColour(caption));
                for(k in autoColorsDict){
                    dataset[k].push(chroma(autocol).alpha(autoColorsDict[k]).css());
                }
                for(k in chart_row_pars){
                    if(isNullOrBlank(dataset[k])){
                        dataset[k] = [];
                    }
                    if(dataset[k] instanceof Array){
                        dataset[k].push(chart_row_pars[k]);
                    }
                    
                }
                idx++;
            }
            return '__continue__';
        },'static',null,isBagMode);
        return dataset;
    },

    mixin_gnr_updateChart:function(){
        if(this.sourceNode.isFreezed()){
            return;
        }
        var that = this;
        this.sourceNode.delayedCall(function(){
            var data = that.sourceNode.getAttributeFromDatasource('data'); 
            if(!data){
                var rows = that.sourceNode.getRelativeData(that.sourceNode.attr.storepath); 
                var filter = that.sourceNode.getAttributeFromDatasource('filter'); 
                var datasets = that.sourceNode.getAttributeFromDatasource('datasets'); 
                var captionField = that.sourceNode.getAttributeFromDatasource('captionField');
                var filterCb;
                if(typeof(filter)=='string'){
                    filter = filter.split(',');
                }
                if(typeof(filter)!='function'){
                    filterCb = filter?function(pkey,row){return filter.length===0 ||filter.indexOf(pkey)>=0;}:function(){return true;};
                }else{
                    filterCb = filter;
                }
                var attrs,dslabel,dsfield;
                var datamode = that.sourceNode.attr.datamode || 'attr';
                data = {labels:[],datasets:[]};
                var dskw = {'rows':rows,'datamode':datamode,
                            'filterCb':filterCb,'labels':data.labels,
                            'captionField':captionField};
                if(datasets){
                    datasets._nodes.forEach(function(n){
                        var v = n.getValue();
                        if(!(v.getNode('enabled')) || v.getItem('enabled')){
                            dskw.pars = v.getItem('parameters').asDict(true,true);
                            dskw.pars.type = v.getItem('chartType');
                            dskw.field = v.getItem('field');
                            data.datasets.push(that.gnr.makeDataset(dskw));
                            objectPop(dskw,'labels');
                        }
                    });
                }
            }         
            objectUpdate(that.data,data);
            that.update();
            that.resize();
        },1,'updateChart');
        
    },
    
    mixin_gnr_storepath:function(value,kw, trigger_reason){  
        this.gnr_updateChart();
    },
    
    mixin_gnr_chartType:function(value,kw, trigger_reason){  
        //this.config.type = this.sourceNode.getAttributeFromDatasource('chartType');
        //this.gnr_updateChart();
        if(this.sourceNode.isFreezed()){
            return;
        }
        this.sourceNode.rebuild();
        
    },

    mixin_gnr_datasets:function(value,kw, trigger_reason){ 
        if(kw.node.label == 'xAxisID' || kw.node.label=='yAxisID'){
            var axes = kw.node.label=='xAxisID'?'xAxes':'yAxes';
            var axeslist = this.options.scales[axes];
            if(!axeslist.some(function(n){return n.id==value;})){
                this.sourceNode.publish('addAxis',{axes:axes,id:kw.value});
                return;
            }
        }
        this.gnr_updateChart();
    },

    mixin_gnr_filter:function(value,kw, trigger_reason){  
        this.gnr_updateChart();
    },

    mixin_gnr_captionField:function(value,kw, trigger_reason){  
        this.gnr_updateChart();
    },
    mixin_gnr_scalesBag:function(value,kw, trigger_reason){ 
        var scalesBag = this.sourceNode.getAttributeFromDatasource('scalesBag');
        if(kw.node._id == scalesBag.getParentNode()._id){
            return;
        }
        this.gnr_updateOptionsObject(kw.node,this.options.scales,scalesBag);
    },
    mixin_gnr_optionsBag:function(value,kw, trigger_reason){ 
        var optionsBag = this.sourceNode.getAttributeFromDatasource('optionsBag');
        if(kw.node._id == optionsBag.getParentNode()._id){
            return;
        }
        this.gnr_updateOptionsObject(kw.node,this.options,optionsBag);
    },

    mixin_gnr_updateOptionsObject:function(triggerNode,curr,optionsBagChunk){
        var optpath = triggerNode.getFullpath(null,optionsBagChunk);
        var currOptionBag = optionsBagChunk;
        var node,val;
        var optlist = optpath.split('.');
        var lastLabel = optlist.pop();
        var k;
        optlist.forEach(function(chunk){
            node = currOptionBag.getNode(chunk);
            if(node.attr._autolist){
                k = currOptionBag.index(chunk);
                if(isNullOrBlank(curr[k])){
                    curr[k] = {};
                }
                curr = curr[k];
            }else{
                if(!(chunk in curr)){
                    curr[chunk] = {};
                }
                curr = curr[chunk];
            }
            currOptionBag = node.getValue();
        });
        var lastValue = currOptionBag.getItem(lastLabel);
        lastValue = lastValue instanceof gnr.GnrBag?lastValue.asDict(true,true):lastValue;
        if(curr instanceof Array){
            var lastIdx = currOptionBag.index(lastLabel);
            if(curr.length>lastIdx){
                curr[lastIdx] = lastValue;
            }else{
                curr.push(lastValue);
            }
        }
        if(curr[lastLabel]!=lastValue){
            triggerNode.attr._userChanged = true;
            curr[lastLabel] = lastValue;
        }
        if(this.sourceNode.isFreezed()){
            return;
        }
        this.update();
        this.resize();
    }
});

dojo.declare("gnr.widgets.dygraph", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'div';
    },

    creating: function(attributes, sourceNode) {
        var savedAttrs = objectExtract(attributes,'data,options,columns');
        return savedAttrs;
    },

    created:function(domNode, savedAttrs, sourceNode){
        var dygraph_root = document.createElement('div');
        domNode.appendChild(dygraph_root);
        var data = savedAttrs.data;
        var options = savedAttrs.options;
        if(options instanceof gnr.GnrBag){
            options =  options.asDict(true);
        }
        if(sourceNode.attr.title){
            options.title = options.title || sourceNode.attr.title; 
        }
        if(sourceNode.attr.detachable){
            options.title = options.title || 'Untiled Graph';
        }
        if(data instanceof gnr.GnrBag){
            sourceNode.labelKeys = sourceNode.labelKeys || savedAttrs.columns.split(','); //during rebuilding
            data = this.getDataFromBag(sourceNode,data);
        }
        var that = this;

        var cb = function(){
            sourceNode._current_height = domNode.clientHeight;
            sourceNode._current_width = domNode.clientWidth;
            options.height = sourceNode._current_height;
            options.width = sourceNode._current_width;
            var dygraph = new Dygraph(dygraph_root,data,options);
            sourceNode.externalWidget = dygraph;
            dygraph.sourceNode = sourceNode;
            dygraph.gnr = that;
            for (var prop in that) {
                if (prop.indexOf('mixin_') === 0) {
                    dygraph[prop.replace('mixin_', '')] = that[prop];
                }
            }
            genro.dom.setAutoSizer(sourceNode,domNode,function(w,h){
                 dygraph.resize(w,h);
            });
        };
        if(!window.Dygraph){
            genro.dom.loadJs('/_rsrc/js_libs/dygraph-combined.js',cb);
        }else{
            setTimeout(cb,1);
        }
    },

    getDataFromBag:function(sourceNode,data){
        var result = [];
        var labelKeys = sourceNode.labelKeys;
        var datagetter = function(n,l){
            return n.attr[l];
        };
        if(data.getItem('#0')){
            datagetter = function(n,l){
                return n._value.getItem(l);
            };
        }
        data.forEach(function(n){
            var row = [];
            labelKeys.forEach(function(l){
                row.push(datagetter(n,l));
            });
            result.push(row);
        });
        return result;
    },

    mixin_gnr_columns:function(value,kw, trigger_reason){  
        this.sourceNode.labelKeys = value.split(',');
        this.sourceNode.rebuild();
    },
    
    mixin_gnr_data:function(value,kw, trigger_reason){  
        var data = this.sourceNode.getAttributeFromDatasource('data');      
        if(data instanceof gnr.GnrBag){
            data = this.gnr.getDataFromBag(this.sourceNode,data);
        }
        this.updateOptions({ 'file': data });
    },

    mixin_gnr_options:function(options,kw, trigger_reason){   
        options = this.sourceNode.getAttributeFromDatasource('options');      
        if(options instanceof gnr.GnrBag){
            options = options.asDict(true);
        }    
        this.updateOptions(options);
    }
});

dojo.declare("gnr.widgets.CkEditor", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'div';
    },

    toolbar_dict:{
        'simple':[['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-','Image','Table','HorizontalRule','PageBreak'],
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize','TextColor','BGColor']],
        'standard':[
                   ['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink','-','Templates'],
                   ['Image','Table','HorizontalRule','PageBreak'],
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize'],
                   ['TextColor','BGColor'],['Maximize', 'ShowBlocks']
                   ]

    },
    creating: function(attributes, sourceNode) {

        attributes.id = attributes.id || 'ckedit_' + sourceNode.getStringId();
        var toolbar = objectPop(attributes, 'toolbar');
        var config = objectExtract(attributes, 'config_*');
        var stylesheet = objectPop(attributes,'stylesheet');
        var customStyles = objectPop(attributes,'customStyles');
        var contentsCss = objectPop(attributes,'contentsCss');
        if(stylesheet){
            config.extraPlugins = 'stylesheetparser';
            config.contentsCss = stylesheet;
        }
        if(customStyles){
            var l = [];
            customStyles.forEach(function(n){
                l.push({name:n.name,element:n.element,styles:objectFromStyle(n.styles),attributes:objectFromStyle(n.attributes)});
            })
            customStyles = l;
        }
        var showtoolbar = true;
        if (toolbar===false){
            toolbar=[];
            showtoolbar = false;
        }
        if (typeof(toolbar) == 'string') {
            if(toolbar in this.toolbar_dict){
                toolbar = this.toolbar_dict[toolbar];
            }else{
                toolbar = genro.evaluate(toolbar);
            }
        }
        ;
        if (toolbar) {
            config.toolbar = 'custom';
            config.toolbar_custom = toolbar;
        }
        ;
        var savedAttrs = {'config':config,showtoolbar:showtoolbar,enterMode:objectPop(attributes,'enterMode'),bodyStyle:objectPop(attributes,'bodyStyle',{margin:'2px'})};
        savedAttrs.customStyles = customStyles;
        savedAttrs.contentsCss = contentsCss;
        savedAttrs.constrainAttr = objectExtract(attributes,'constrain_*')
        return savedAttrs;

    },
    dialog_tableProperties:function(definition,ckeditor){
        this.dialog_table(definition,ckeditor);
    },
    dialog_table:function(definition,ckeditor){
        definition.getContents('info').get('txtBorder')['default']=null;
        definition.getContents('advanced').get('advStyles')['default']='border-collapse:collapse;';
        definition.addContents({
            id : 'gnr_tableProperties',
            label : 'Genropy',
            accessKey : 'G',
            elements : [
                    {id : 'row_datasource',type : 'text',label : 'Row Datasource',
                        setup: function(i) {
                            this.setValue(i.getAttribute('row_datasource') || '');
                        },
                        commit: function(i, j) {
                            if (this.getValue()) j.setAttribute('row_datasource', this.getValue());
                            else j.removeAttribute('row_datasource');
                        }
                    },

                    {id : 'row_condition',type : 'text',label : 'Row Condition',
                        setup: function(i) {
                            this.setValue(i.getAttribute('row_condition') || '');
                        },
                        commit: function(i, j) {
                            if (this.getValue()) j.setAttribute('row_condition', this.getValue());
                            else j.removeAttribute('row_condition');
                        }
                    },
                    {id : 'row_sort',type : 'text',label : 'Row Sort',
                        setup: function(i) {
                            this.setValue(i.getAttribute('row_sort') || '');
                        },
                        commit: function(i, j) {
                            if (this.getValue()) j.setAttribute('row_sort', this.getValue());
                            else j.removeAttribute('row_sort');
                        }
                    }
                    ]
            });
    },
    mixin_gnr_constrain_height:function(height,kw, trigger_reason){
         this.document.getBody()['$'].style.height = height;
    }, 

    mixin_gnr_constrain_width:function(width,kw, trigger_reason){
         this.document.getBody()['$'].style.width = width;
    }, 
    mixin_gnr_assignConstrain:function(){
        var that = this;
        this.sourceNode.watch('hasDocument',function(){
            return that.document;
        },function(){
            var constrainAttr = objectExtract(that.sourceNode.attr,'constrain_*',true);
            constrainAttr = that.sourceNode.evaluateOnNode(constrainAttr);
            var b = that.document.getBody()['$'];
            b.style.cssText = objectAsStyle(objectUpdate(objectFromStyle(b.style.cssText),
                                                genro.dom.getStyleDict(constrainAttr)));  
        });
            

    },

    makeEditor:function(widget, savedAttrs, sourceNode){
        var showtoolbar = objectPop(savedAttrs,'showtoolbar');
        var enterMode = objectPop(savedAttrs,'enterMode') || 'div';
        var bodyStyle = objectPop(savedAttrs,'bodyStyle');
        //var constrainAttr = objectPop(savedAttrs,'constrainAttr');
        var enterModeDict = {'div':CKEDITOR.ENTER_DIV,'p':CKEDITOR.ENTER_P,'br':CKEDITOR.ENTER_BR};
        if(showtoolbar===false){
        objectUpdate(savedAttrs.config, {
            toolbar: 'Custom', //makes all editors use this toolbar
            toolbarStartupExpanded : false,
            toolbarCanCollapse  : false,
            toolbar_Custom: '' //define an empty array or whatever buttons you want.
            });
        }

        if(savedAttrs.customStyles){
            var csname = 'customStyles_'+sourceNode.getStringId();
            CKEDITOR.stylesSet.add(csname,savedAttrs.customStyles);
            savedAttrs.config.stylesSet = csname
        } 
        savedAttrs.config.enterMode = enterModeDict[enterMode];
        //savedAttrs.config.enterMode = CKEDITOR.ENTER_BR;
        //savedAttrs.config.enterMode = CKEDITOR.ENTER_P;

        if(savedAttrs.contentsCss){
            var currlst = CKEDITOR.config.contentsCss;
            if(typeof(currlst)=='string'){
                currlst = currlst.split(',')
            }
            savedAttrs.config.contentsCss = currlst.concat(savedAttrs.contentsCss.split(','));
        }
        CKEDITOR.replace(widget, savedAttrs.config);


        var ckeditor_id = 'ckedit_' + sourceNode.getStringId();
        var ckeditor = CKEDITOR.instances[ckeditor_id];
        sourceNode.externalWidget = ckeditor;
        ckeditor.sourceNode = sourceNode;
        ckeditor.gnr = this;
        for (var prop in this) {
            if (prop.indexOf('mixin_') == 0) {
                ckeditor[prop.replace('mixin_', '')] = this[prop];
            }
        }
        ckeditor.gnr_getFromDatastore();
        var parentWidget = dijit.getEnclosingWidget(widget);
        ckeditor.gnr_readOnly('auto');
        var parentDomNode=sourceNode.getParentNode().getDomNode();
        ckeditor.on('currentInstance', function(ev){
            console.log('currentInstance',constrainAttr);
        });
        
        var cbResize=function(){
                sourceNode._rsz=null;
                try{
                    ckeditor.gnr_assignConstrain();
                    ckeditor.resize(parentDomNode.clientWidth,parentDomNode.clientHeight);
                }catch(e){
                    
                }
                
        };
        ckeditor.on('instanceReady', function(ev){
            var editor = ev.editor;
            editor.gnr_assignConstrain();
            var dropHandler = function( evt ) {
                setTimeout(function(){ckeditor.gnr_setInDatastore();},1);
            };
            if (editor.document.$.addEventListener) {
                editor.document.$.addEventListener( 'drop', dropHandler, true ) ; 
            } else if (editor.document.$.attachEvent) {
                editor.document.$.attachEvent( 'ondrop', dropHandler, true ) ; 
            }
            editor.document.$.addEventListener('keydown',function(evt){
                ckeditor.lastKey = evt.keyCode;
            });

            if(sourceNode.attr.onStarted){
                funcApply(sourceNode.attr.onStarted,{editor:editor},sourceNode);
            }
            cbResize();
            if(sourceNode.attr._inGridEditor){
                var that = this;
                setTimeout(function(){that.focus()},100);
            }
        });


        dojo.connect(parentWidget,'resize',function(){
            if(sourceNode._rsz){
                clearTimeout(sourceNode._rsz);
            }
            sourceNode._rsz=setTimeout(cbResize,100);
        });
        var that=this;
        if(!CKEDITOR._dialog_patched){
            CKEDITOR.on( 'dialogDefinition', function( ev ){
                if (that['dialog_'+ev.data.name]){
                    that['dialog_'+ev.data.name].call(that,ev.data.definition);
                }
            });
            CKEDITOR._dialog_patched = true;
        }

        var ckeditor =  sourceNode.externalWidget;
        dojo.connect(ckeditor.focusManager, 'blur', function(evt){
            ckeditor.gnr_setInDatastore();            
            if(sourceNode.attr.connect_onBlur){
                if(ckeditor._blurTimeOut){
                    clearTimeout(ckeditor._blurTimeOut)
                    ckeditor._blurTimeOut = null
                }
                ckeditor._blurTimeOut = setTimeout(function(){
                    if(sourceNode.attr._inGridEditor && sourceNode.externalWidget.lastKey==9){
                        sourceNode.externalWidget.cellNext = 'RIGHT';  
                    }
                    funcApply(sourceNode.attr.connect_onBlur,{evt:evt},sourceNode);
                    clearTimeout(ckeditor._blurTimeOut)
                    ckeditor._blurTimeOut = null
                },200)
                
            }
        });
        dojo.connect(ckeditor.focusManager, 'focus', function(evt){
            if(ckeditor._blurTimeOut){
                clearTimeout(ckeditor._blurTimeOut)
                    ckeditor._blurTimeOut = null
                }
        });


        dojo.connect(ckeditor.editor, 'paste', ckeditor, 'gnr_onPaste');
        ckeditor['on']('paste',function(e){
            var lastSelection = sourceNode.externalWidget.getSelection().getNative();
            var data = e.data.html || '';
            if(data[0]=='<'){
                var anchorNode = lastSelection.anchorNode;
                if(anchorNode.innerHTML=='<br>'){
                    anchorNode.innerHTML = '&nbsp;';
                    var an = anchorNode.firstChild;
                    lastSelection.anchorNode.parentNode.replaceChild(an,anchorNode);
                    lastSelection.anchorNode = an;
                }
            }
            genro.callAfter(function(){
                this.gnr_onTyped();
                this.gnr_setInDatastore();
            },1,this,'typing');
        })
        ckeditor['on']('key',function(kw){
            if(!sourceNode.attr._inGridEditor){
                genro.callAfter(function(){
                    this.gnr_onTyped();
                    this.gnr_setInDatastore();
                },1000,this,'typing');
            }
        });
    
        return ckeditor;
        
    },

    onSpeechEnd:function(sourceNode,v){
        var lastSelection = sourceNode.externalWidget.getSelection().getNative();
        if(lastSelection){
            var oldValue = sourceNode.getAttributeFromDatasource('value') || '';
            var fistchunk = oldValue.slice(0,lastSelection.start);
            var secondchunk =  oldValue.slice(lastSelection.end);
            v = fistchunk+v+secondchunk;
        }
        setTimeout(function(){
            sourceNode.setAttributeInDatasource('value',v,true);
            //sourceNode.widget.domNode.focus();
        },1);
    },

    created: function(widget, savedAttrs, sourceNode) {
        var that = this;
        var cb = function(){
            that.makeEditor(widget, savedAttrs, sourceNode);
            sourceNode.publish('editorCreated');
        };
        if(!window.CKEDITOR){
            var suff = genro.newCkeditor? '_new':'';
            genro.dom.loadJs('/_rsrc/js_libs/ckeditor'+suff+'/ckeditor.js',function(){
                cb();
            });
            return;
        }
        cb();
         
        // dojo.connect(parentWidget,'onShow',function(){console.log("onshow");console.log(arguments);ckeditor.gnr_readOnly('auto');})
        // setTimeout(function(){;},1000);

    },

    mixin_gnr_value:function(value, kw, reason) {
        if(!this.focusManager.hasFocus){
            this.setData(value);
        }
    },
    
    mixin_gnr_getFromDatastore : function() {
        this.setData(this.sourceNode.getAttributeFromDatasource('value') || '');
    },

    mixin_gnr_setInDatastore : function() {
        var value=this.getData();
        if(this.sourceNode.getAttributeFromDatasource('value')!=value){
            this.sourceNode.setAttributeInDatasource('value',value );
        }
    },
    mixin_gnr_onPaste:function(){
        this.gnr_setInDatastore();
    },
    mixin_gnr_onTyped:function(){

    },

    mixin_gnr_setDisabled:function(disabled){
        this.gnr_setReadOnly(disabled);
    },

    mixin_gnr_highlightChild:function(idx){
        var cs = this.sourceNode.externalWidget.document.$.getElementById('customstyles');
        if(!cs){
            var cs = this.sourceNode.externalWidget.document.$.createElement('style');
            cs.setAttribute('id','customstyles');
            this.sourceNode.externalWidget.document.getHead().$.appendChild(cs)
        }
        cs.textContent =idx>=0? "body>*:nth-child("+(idx+1)+"){background:yellow;}":"";
        if(idx>=0){
            var b = this.sourceNode.externalWidget.document.getBody().$;
            var higlightedNode = b.children[idx];
            var ht = higlightedNode.offsetTop;
            //if(b.parentNode.clientHeight+b.scrollTop-ht<0){
               b.scrollTop = ht-100;
            //}
        }
    },

    mixin_gnr_cancelEvent : function(evt) {
        evt.cancel();
    },

    mixin_gnr_readOnly:function(value, kw, reason) {
        var value = (value != 'auto') ? value : this.sourceNode.getAttributeFromDatasource('readOnly');
        this.gnr_setReadOnly(value);
    },
    mixin_gnr_setReadOnly:function(isReadOnly) {
        if (!this.document) {
            return;
        }
        //this.document.$.body.disabled = isReadOnly;
        CKEDITOR.env.ie ? this.document.$.body.contentEditable = !isReadOnly
                : this.document.$.designMode = isReadOnly ? "off" : "on";
        this[ isReadOnly ? 'on' : 'removeListener' ]('key', this.gnr_cancelEvent, null, null, 0);
        this[ isReadOnly ? 'on' : 'removeListener' ]('selectionChange', this.gnr_cancelEvent, null, null, 0);
        var command,
                commands = this._.commands,
                mode = this.mode;
        for (var name in commands) {
            command = commands[ name ];
            isReadOnly ? command.disable() : command[ command.modes[ mode ] ? 'enable' : 'disable' ]();
            this[ isReadOnly ? 'on' : 'removeListener' ]('state', this.gnr_cancelEvent, null, null, 0);
        }
    }

});