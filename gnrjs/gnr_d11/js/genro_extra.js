dojo.declare("gnr.widgets.dummy", null, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    _beforeCreation: function(sourceNode) {
        var attributes = objectUpdate({},sourceNode.attr);
        objectExtract(sourceNode.attr,'nodeId,datapath');
        var contentKwargs = this.contentKwargs(sourceNode,attributes);
        sourceNode.freeze();
        var children = sourceNode.getValue();
        sourceNode.clearValue();
        var content = this.createContent(sourceNode, contentKwargs);
        content.concat(children);
        sourceNode.unfreeze(true);
        return false;
    },
    
    contentKwargs: function(sourceNode,attributes) {
        return attributes;
    }
});

dojo.declare("gnr.widgets.Palette", gnr.widgets.dummy, {
    contentKwargs: function(sourceNode,attributes) {
        var left = objectPop(attributes, 'left');
        var right = objectPop(attributes, 'right');
        var top = objectPop(attributes, 'top');
        var bottom = objectPop(attributes, 'bottom');
        if ((left === null) && (right === null) && (top === null) && (bottom === null)) {
            this._last_floating = this._last_floating || {top:0,right:0};
            this._last_floating['top'] += 10;
            this._last_floating['right'] += 10;
            top = this._last_floating['top'] + 'px';
            right = this._last_floating['right'] + 'px';
        }
        var dockTo = objectPop(attributes,'dockTo') || 'default_dock';
        var floating_kwargs = objectUpdate(attributes,{dockable:true,closable:false,
                                                       dockTo:dockTo,visibility:'hidden'});
        if(dockTo=='*'){
            floating_kwargs.closable = true;
            floating_kwargs.dockable = false;
            floating_kwargs.visibility = 'visible';
        }
        return objectUpdate({height:'400px',width:'300px',
                            top:top,right:right,left:left,bottom:bottom,
                            resizable:true},floating_kwargs);
    },
    createContent:function(sourceNode, kw) {
        return sourceNode._('floatingPane', kw);
    }
});


dojo.declare("gnr.widgets.PalettePane", gnr.widgets.dummy, {
    contentKwargs: function(sourceNode,attributes){
        var inattr = sourceNode.getInheritedAttributes();
        var groupCode = inattr.groupCode;
        attributes.datapath = attributes.datapath || 'gnr.palettes.'+attributes.paletteCode;
        if(groupCode){
            attributes.groupCode = groupCode;
            attributes.pageName = attributes.paletteCode;
        }
        return attributes;
    },
    createContent:function(sourceNode, kw) {
        var paletteCode = objectPop(kw,'paletteCode');
        var groupCode = objectPop(kw,'groupCode');
        if (groupCode){
            
            var pane = sourceNode._('ContentPane',objectExtract(kw,'title,pageName'))._('ContentPane',objectUpdate({'detachable':true},kw));
            var subscription_code = 'subscribe_show_palette_'+paletteCode;
            pane._('dataController',{'script':"SET gnr.palettes?"+groupCode+" = paletteCode;",
                                 'paletteCode':paletteCode,
                                 subscription_code: true});
            return pane;
        }else{
            var palette_kwargs = objectExtract(kw,'title,dockTo,top,left,right,bottom,connect_show');
            palette_kwargs['nodeId'] = paletteCode+'_floating';
            palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + paletteCode;
            var floating = sourceNode._('palette', palette_kwargs);
            return floating._('ContentPane',kw);
        }
    }
});
dojo.declare("gnr.widgets.PaletteTree", gnr.widgets.dummy, {
    createContent:function(sourceNode, kw) {
        var treeId =objectPop(kw,'treeId') || 'palette_'+paletteCode+'_tree';
        var tree_kwargs = {labelAttribute:'caption', _class:'fieldsTree', hideValues:true,
                           margin:'6px', font_size:'.9em', draggable:true,nodeId:treeId,
                           storepath:objectPop(kw,'storepath') || '.store'};
        var paletteCode = kw.paletteCode;
        tree_kwargs.onDrag = function(dragValues,dragInfo,treeItem){
            if(treeItem.attr.child_count && treeItem.attr.child_count>0){
                return false;
            }
            dragValues['text/plain']=treeItem.attr.caption;
            dragValues[paletteCode]=treeItem.attr;
        };
        objectUpdate(tree_kwargs ,objectExtract(kw,'tree_*'));
        var searchOn = objectPop(kw,'searchOn');
        var pane = sourceNode._('PalettePane',kw);
        if (searchOn){
            var bc = pane._('BorderContainer');
            var top = bc._('ContentPane',{region:'top'})._('Toolbar',{height:'20px'});
            pane = bc._('ContentPane',{region:'center'});
            top._('SearchBox',{searchOn:searchOn,nodeId:treeId+'_searchbox',datapath:'.searchbox'});
        }
        var tree = pane._('tree',tree_kwargs);
        return pane;
    }
});

dojo.declare("gnr.widgets.PaletteGrid", gnr.widgets.dummy, {
    createContent:function(sourceNode, kw) {
        var grid_kwargs = {margin:'6px', font_size:'.9em', draggable_row:true,configurable:true,
                            storepath:(objectPop(kw,'storepath') || '.store'),
                            structpath:(objectPop(kw,'structpath') || '.grid.struct'),
                            controllerPath:'.grid',table:kw.table};
        var paletteCode = kw.paletteCode;
        var gridId =objectPop(kw,'gridId') || 'palette_'+paletteCode+'_grid';
        grid_kwargs.nodeId = gridId;
        grid_kwargs.onDrag = function(dragValues,dragInfo){
            if(dragInfo.dragmode=='row'){
                dragValues[paletteCode]=dragValues.gridrow.rowsets;
            }
        };
        kw.connect_show = function(widget){
            var grid = genro.wdgById(gridId);
            if(grid.storebag().len()==0){
                grid.reload();
            }
        };
        objectUpdate(grid_kwargs ,objectExtract(kw,'grid_*'));
        var pane = sourceNode._('PalettePane',kw);
        if (kw.searchOn){
            var bc = pane._('BorderContainer');
            var top = bc._('ContentPane',{region:'top'})._('Toolbar',{height:'20px'});
            pane = bc._('ContentPane',{region:'center'});
            top._('SearchBox',{searchOn:kw.searchOn,nodeId:gridId+'_searchbox',datapath:'.searchbox'});
        }
        var grid = pane._('includedview',grid_kwargs);
        return pane;
    }
});


dojo.declare("gnr.widgets.SearchBox", gnr.widgets.dummy, {
    contentKwargs: function(sourceNode,attributes){
        var topic = attributes.nodeId+'_keyUp';
        var delay = 'delay' in attributes? objectPop(attributes,'delay'): 100;
        attributes.onKeyUp = function(e){
            var sourceNode = e.target.sourceNode;
            if(sourceNode._publisher){
                clearTimeout(sourceNode._publisher);
            }
            var v = e.target.value;
            sourceNode._publisher = setTimeout(function(){
                genro.publish(topic,v,sourceNode.getRelativeData('.field'));
                },delay);
            
        };
        return attributes;
    },
    
    createContent:function(sourceNode, kw) {
        var searchOn = objectPop(kw,'searchOn');
        var searchDtypes;
        if(searchOn[0]=='*'){
            searchDtypes = searchOn.slice(1);
            searchOn=true;
        }
        var datapath = objectPop(kw,'datapath') || '.searchbox';
        var nodeId = objectPop(kw,'nodeId');
        var menubag;
        var databag = new gnr.GnrBag();
        databag.setItem('menu_dtypes',searchDtypes);
        this._prepareSearchBoxMenu(searchOn,databag);
        sourceNode.setRelativeData(datapath,databag);
        var searchbox = sourceNode._('div',{datapath:datapath, nodeId:nodeId});
        var searchlbl = searchbox._('div',{'float':'left', margin_top:'2px'});
        searchlbl._('span',{'innerHTML':'^.caption',_class:'buttonIcon'});
        searchlbl._('menu',{'modifiers':'*',_class:'smallmenu',storepath:'.menubag',
                            selected_col:'.field',selected_caption:'.caption'});
        
        searchbox._('input',{'value':'^.value',_class:'searchInput searchWidth',font_size:'1.0em',
                      connect_onkeyup:kw.onKeyUp});
        dojo.subscribe(nodeId+'_updmenu',this,function(searchOn){
            menubag = this._prepareSearchBoxMenu(searchOn,databag);
        });
        return searchbox;
    },
    _prepareSearchBoxMenu: function(searchOn,databag){
        var menubag = new gnr.GnrBag();
        var i = 0;
        if(searchOn===true){
            databag.setItem('menu_auto',menubag);
        }
        else{
            dojo.forEach(searchOn.split(','),function(col){
                col = dojo.trim(col);
                var caption = col;
                if(col.indexOf(':')>=0){
                    col = col.split(':');
                    caption= col[0];
                    col = col[1];
                }
                col = col.replace(/[.@]/g,'_');
                menubag.setItem('r_'+i,null,{col:col,caption:caption,child:''});
                i++;
            });
        }
        databag.setItem('field',menubag.getItem('#0?col'));
        databag.setItem('caption',menubag.getItem('#0?caption'));
        databag.setItem('menubag',menubag);
        databag.setItem('value','');
    }
    
});


dojo.declare("gnr.widgets.PaletteGroup", gnr.widgets.dummy, {
    createContent:function(sourceNode, kw) {
        var groupCode = objectPop(kw, 'groupCode');
        var palette_kwargs = objectExtract(kw,'title,dockTo,top,left,right,bottom');
        palette_kwargs['nodeId'] = 'paletteGroup_'+groupCode+'_floating';
        palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + groupCode;
        var floating = sourceNode._('palette', palette_kwargs);
        var tc = floating._('tabContainer', objectUpdate(kw,{selectedPage:'^gnr.palettes.?' + groupCode,groupCode:groupCode}));
        return tc;
    }
});



dojo.declare("gnr.widgets.protovis", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    creating: function(attributes, sourceNode) {
        if (sourceNode.attr.storepath) {
            sourceNode.registerDynAttr('storepath');
        }
    },
    created: function(newobj, savedAttrs, sourceNode) {
        dojo.subscribe(sourceNode.attr.nodeId + '_render', this, function() {
            this.render(newobj);
        });
      
    },
    setStorepath:function(obj, value) {
        obj.gnr.update(obj);
    },
    attachToDom:function(domNode, vis) {
        var span = document.createElement('span');
        var fc = domNode.firstElementChild;
        if (fc) {
            domNode.replaceChild(span, fc);
        } else {
            domNode.appendChild(span);
        }
        vis.$dom = span;
        return span;
    },
    update:function(domNode) {
        var sourceNode = domNode.sourceNode;
        if ((sourceNode.vis) && (!sourceNode.visError)){
            sourceNode.vis.render();
        }else{
            this.render(domNode);
        }

    },
    render:function(domNode) {
        var sourceNode = domNode.sourceNode;
        try {
             this._doRender(domNode);
             sourceNode.visError=null;
        } catch(e) {
            console.log('error in rendering protovis '+sourceNode.attr.nodeId+' : '+e);
            sourceNode.visError=e;
        }
        
    },
    _doRender:function(domNode) {
        var sourceNode = domNode.sourceNode;
        if (sourceNode.attr.js) {
            var vis = new pv.Panel();
            var protovis = pv.parse(sourceNode.getAttributeFromDatasource('js'));
            funcApply(protovis, objectUpdate({'vis':vis}, sourceNode.currentAttributes()), sourceNode);
        }
        else if (sourceNode.attr.storepath) {
            var storepath = sourceNode.attr.storepath;
            var visbag = sourceNode.getRelativeData(storepath).getItem('#0');
            var vis;
            _this=this;
            sourceNode.protovisEnv={};
            visbag.forEach(function(n) {
                vis=_this.bnode(sourceNode, n) || vis;
            });
        }
        this.attachToDom(domNode, vis);
        sourceNode.vis = vis;
        vis.render();
    },
    storegetter:function(sourceNode, path) {
        var p = path;
        var s = sourceNode;
        return function() {
            //console.log('getting: ' + p)
            return s.getRelativeData(p);
        };
    },
    bnode:function(sourceNode, node, parent) {
        var env=sourceNode.protovisEnv;
        var storepath = sourceNode.attr.storepath;
        var attr = objectUpdate({}, node.attr);
        var tag = objectPop(attr, 'tag');
        if (tag=='env'){
            console.log(node.getValue())
            env[node.label]=eval(node.getValue())
            return;
        }
        var obj = parent? parent.add(pv[tag]):new pv[tag]();
        this._convertAttr(sourceNode,obj,attr);
        var v = node.getValue();
        _this = this;
        if (v instanceof gnr.GnrBag) {
            v.forEach(function(n) {
                _this.bnode(sourceNode, n, obj);
            });
        }
        return obj;
    },
    _convertAttr:function(sourceNode,obj,attr){
        var env=sourceNode.protovisEnv;
        var storepath = sourceNode.attr.storepath
        for (var k in attr) {
            var v = attr[k];
            if (stringEndsWith(k,'_js')){
                k=k.slice(0,-3);
                v=genro.evaluate(v);
            }
            else if (stringEndsWith(k,'_fn')){
                k=k.slice(0,-3);
                v=genro.evaluate('function(){return '+v+'}');
            }
            else if(k.indexOf('_fn_')>0){
                k=k.split('_fn_');
                var fn='function('+k[1]+'){return ('+v+')}';
                v=genro.evaluate(fn);
                k=k[0];
            }
            
            if ((typeof(v) == 'string') && (v[0] == '=')) {
                path = v.slice(1);
                if (path[0] == '.') {
                    path = storepath + path;
                }
                v = this.storegetter(sourceNode, path);
            }
            if(k.indexOf('_')>0){
                k=k.split('_');
                obj[k[0]](k[1],v);
            }else{
                obj[k](v);
            }
        }
    }
});

dojo.declare("gnr.widgets.CkEditor", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    creating: function(attributes, sourceNode) {
        attributes.id = attributes.id || 'ckedit_' + sourceNode.getStringId();
        var toolbar = objectPop(attributes, 'toolbar');
        var config = objectExtract(attributes, 'config_*');
        if (typeof(toolbar) == 'string') {
            toolbar = genro.evaluate(toolbar);
        }
        ;
        if (toolbar) {
            config.toolbar = 'custom';
            config.toolbar_custom = toolbar;
        }
        ;
        var savedAttrs = {'config':config};
        return savedAttrs;

    },
    created: function(widget, savedAttrs, sourceNode) {
        CKEDITOR.replace(widget, savedAttrs.config);
        var ckeditor_id = 'ckedit_' + sourceNode.getStringId();
        var ckeditor = CKEDITOR.instances[ckeditor_id];
        sourceNode.externalWidget = ckeditor;
        ckeditor.sourceNode = sourceNode;
        for (var prop in this) {
            if (prop.indexOf('mixin_') == 0) {
                ckeditor[prop.replace('mixin_', '')] = this[prop];
            }
        }
        ckeditor.gnr_getFromDatastore();
        var parentWidget = dijit.getEnclosingWidget(widget);
        ckeditor.gnr_readOnly('auto');
        /*dojo.connect(parentWidget,'resize',function(){
         var ckeditor=CKEDITOR.instances[ckeditor_id];
         console.log(ckeditor_id);
         console.log('resize');
         console.log(arguments);
         if (ckeditor){
         console.log(ckeditor);
         ckeditor.resize();}
         else{console.log('undefined');}
         });*/
        // dojo.connect(parentWidget,'onShow',function(){console.log("onshow");console.log(arguments);ckeditor.gnr_readOnly('auto');})
        // setTimeout(function(){;},1000);

    },
    connectChangeEvent:function(obj) {
        var ckeditor = obj.sourceNode.externalWidget;
        dojo.connect(ckeditor.focusManager, 'blur', ckeditor, 'gnr_setInDatastore');
        dojo.connect(ckeditor.editor, 'paste', ckeditor, 'gnr_setInDatastore');
    },

    mixin_gnr_value:function(value, kw, reason) {
        this.setData(value);
    },
    mixin_gnr_getFromDatastore : function() {
        this.setData(this.sourceNode.getAttributeFromDatasource('value'));
    },
    mixin_gnr_setInDatastore : function() {
        this.sourceNode.setAttributeInDatasource('value', this.getData());
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