//GNRWDG WIDGET DEFINITION BASE
dojo.declare("gnr.widgets.gnrwdg", null, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    _beforeCreation: function(sourceNode) {
        sourceNode.gnrwdg = {'gnr':this,'sourceNode':sourceNode};
        var attributes = sourceNode.attr;
        sourceNode.attr = {};
        sourceNode.attr.tag=objectPop(attributes,'tag')
        var datapath=objectPop(attributes,'datapath')
        if(datapath){sourceNode.attr.datapath=datapath;}
        var contentKwargs = this.contentKwargs(sourceNode, attributes);
        if (!this.createContent) {
            return false;
        }
        sourceNode.freeze();
        var children = sourceNode.getValue();
        sourceNode.clearValue();
        var content = this.createContent(sourceNode, contentKwargs,children);
        content.concat(children);
        sourceNode._stripData(true);
        sourceNode.unfreeze(true);
        return false;
    },
    onStructChild:function(attributes) {
        if (!attributes.datapath) {
            var defaultDatapath = this.defaultDatapath(attributes);
            if (defaultDatapath) {
                attributes.datapath = defaultDatapath;
            }
        }

    },
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
    defaultDatapath:function(attributes) {
        return null;
    }
});

dojo.declare("gnr.widgets.Palette", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
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
        var dockTo = objectPop(attributes, 'dockTo');
        var floating_kwargs = objectUpdate(attributes, {dockable:true,closable:false,visibility:'hidden'});
        var showOnStart = false;
        if (dockTo === false) {
            floating_kwargs.closable = true;
            floating_kwargs.dockable = false;
            showOnStart = true;
        } else if (dockTo && dockTo.indexOf(':open') >= 0) {
            dockTo = dockTo.split(':')[0];
            objectPop(floating_kwargs, 'visibility');
            showOnStart = true;
        }
        if (showOnStart) {
            floating_kwargs.onCreated = function(widget) {
                setTimeout(function() {
                    widget.show();
                    widget.bringToTop();
                }, 1);
            };
        }
        if (!dockTo && dockTo !== false) {
            dockTo = 'default_dock';
        }
        if (dockTo) {
            floating_kwargs.dockTo = dockTo;
        }
        return objectUpdate({height:'400px',width:'300px',
            top:top,right:right,left:left,bottom:bottom,
            resizable:true}, floating_kwargs);
    },
    createContent:function(sourceNode, kw) {
        if (kw.dockTo == '*') {
            var dockId = sourceNode._id + '_dock';
            sourceNode._('dock', {id:dockId});
            kw.dockTo = dockId;
        }
        if (kw.nodeId) {
            var that=this;
            kw.connect_show = function() {
                genro.publish(kw.nodeId + '_showing');
            };
            kw.connect_hide = function() {
                genro.publish(kw.nodeId + '_hiding');
            };
        }
        return sourceNode._('floatingPane', kw);
    }
});

dojo.declare("gnr.widgets.PalettePane", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var inattr = sourceNode.getInheritedAttributes();
        var groupCode = inattr.groupCode;
        attributes.nodeId = attributes.nodeId || 'palette_' + attributes.paletteCode;
        attributes._class = attributes._class || "basePalette";
        if (groupCode) {
            attributes.groupCode = groupCode;
            attributes.pageName = attributes.paletteCode;
        }
        return attributes;
    },

    defaultDatapath:function(attributes) {
        return  'gnr.palettes.' + attributes.paletteCode;
    },
    createContent:function(sourceNode, kw) {
        var paletteCode = objectPop(kw, 'paletteCode');
        var contentWidget = objectPop(kw,'contentWidget') || 'ContentPane';
        var groupCode = objectPop(kw, 'groupCode');
        if (groupCode) {
            var pane = sourceNode._('ContentPane', objectExtract(kw, 'title,pageName'))._(contentWidget, objectUpdate({'detachable':true}, kw));
            var controller_kw = {'script':"SET gnr.palettes._groups.pagename." + groupCode + " = paletteCode;",
                'paletteCode':paletteCode}
            controller_kw['subscribe_show_palette_' + paletteCode] = true;
            pane._('dataController', controller_kw);
            return pane;
        } else {
            var palette_kwargs = objectExtract(kw, 'title,dockTo,top,left,right,bottom,maxable,height,width');
            palette_kwargs['nodeId'] = paletteCode + '_floating';
            palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + paletteCode;
            objectUpdate(palette_kwargs, objectExtract(kw, 'palette_*'));
            palette_kwargs.selfsubscribe_showing = function() {
                genro.publish('palette_' + paletteCode + '_showing');
            }
            palette_kwargs.selfsubscribe_hiding = function() {
                genro.publish('palette_' + paletteCode + '_hiding');
            }
            var floating = sourceNode._('palette', palette_kwargs);
            return floating._(contentWidget, kw);
        }
    }
});

dojo.declare("gnr.widgets.FramePane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var node;
        var frameCode = kw.frameCode;
        if(frameCode && !kw.nodeId && !kw.formId){
            kw.nodeId = frameCode+'_frame';
        }
        objectPop(kw,'datapath');
        var rounded_corners = genro.dom.normalizedRoundedCorners(kw.rounded,objectExtract(kw,'rounded_*',true))
        var bc = sourceNode._('BorderContainer', kw);
        var slot,v;
        var centerPars = objectExtract(kw,'center_*');
        var sides= kw.design=='sidebar'? ['left','right','top','bottom']:['top','bottom','left','right']
        var corners={'left':['top_left','bottom_left'],'right':['top_right','bottom_right'],'top':['top_left','top_right'],'bottom':['bottom_left','bottom_right']}
        dojo.forEach(sides,function(side){
             slot = children.popNode(side);
             node = slot? slot.getValue().getNode('#0') : children.popNode('#side='+side);
             if(node){                 
                 node.attr['frameCode'] = frameCode;
                 objectPop(node.attr,'side');
                 dojo.forEach(corners[side],function(c){
                     v=objectPop(rounded_corners,c)
                     if(v){
                         node.attr['rounded_'+c] = v;
                     }
                 })             
                 bc._('ContentPane',{'region':side}).setItem('#id',node._value,node.attr);
             }
        });
        slot = children.popNode('center');
        var centerNode = slot? slot.getValue().getNode('#0'):children.popNode('#side=center');
        var center;
        var rounded={};
        var frameChild;
        frameChild = children.popNode('#_frame=true::B');
        while(frameChild){
            objectPop(frameChild.attr,'_frame');
            bc.setItem(frameChild.label,frameChild._value,frameChild.attr);
            frameChild = children.popNode('#_frame=true::B');
        }
        
        for(var k in rounded_corners){
            rounded['rounded_'+k]=rounded_corners[k]
        }
        if(centerNode){
            objectPop(centerNode.attr,'side');
            centerNode.attr['region'] = 'center';
            bc.setItem('#id',centerNode._value,objectUpdate(rounded,centerNode.attr));
            center = centerNode._value;
        }else{
            centerPars['region'] = 'center';
            center = bc._('ContentPane',objectUpdate(rounded,centerPars));
        }
        return center;
    }
});

dojo.declare("gnr.widgets.FrameForm", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var formId = objectPop(kw,'formId');
        var storeNode = children.getNode('formStore');
        if(storeNode){
            storeNode.attr['_frame'] = true;
        }
        var frameCode = kw.frameCode;
        formId = formId || frameCode+'_form';
        var frame = sourceNode._('FramePane',objectUpdate({formDatapath:'.record',controllerPath:'.form',pkeyPath:'.pkey',
                                                          formId:formId},kw));
        frame._('SlotBar',{'side':'bottom',slots:'*,messageBox,*',_class:'fh_bottom_message',messageBox_subscribeTo:'form_'+formId+'_message'});
        var storeId = kw.store+'_store';
        frame._('ContentPane',{side:'center','_class':'fh_content','nodeId':formId+'_content',_lazyBuild:true});
        return frame;
    }
});


dojo.declare("gnr.widgets.PaletteGrid", gnr.widgets.gnrwdg, {
    contentKwargs:function(sourceNode, attributes){
        var gridId = attributes.gridId || attributes.paletteCode+'_grid';
        attributes['frameCode'] = attributes.paletteCode;
        attributes.selfsubscribe_showing = function() {
            var grid = genro.wdgById(gridId);
            if (grid.storebag().len() == 0) {
                grid.reload();
            }
        }
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var frameCode = kw.frameCode;
        var gridId = objectPop(kw, 'gridId') || frameCode+'_grid';
        var storepath = objectPop(kw, 'storepath');
        var structpath = objectPop(kw, 'structpath');
        var store = objectPop(kw, 'store');
        var paletteCode=kw.paletteCode
        storepath = storepath? sourceNode.absDatapath(storepath):'.store';
        structpath = structpath? sourceNode.absDatapath(structpath):'.struct';
        var gridKwargs = {'nodeId':gridId,'datapath':'.grid',
                           'table':objectPop(kw,'table'),
                           'margin':'6px','configurable':true,
                           'storepath': storepath,
                           'structpath': structpath,
                           'frameCode':frameCode,
                           'autoWidth':false,
                           'store':store,
                           'relativeWorkspace':true};   
        gridKwargs.onDrag = function(dragValues, dragInfo) {
            if (dragInfo.dragmode == 'row') {
                dragValues[paletteCode] = dragValues.gridrow.rowset;
            }
        };     
        gridKwargs.draggable_row=true;
        objectUpdate(gridKwargs, objectExtract(kw, 'grid_*'));
        kw['contentWidget'] = 'FramePane';
        var pane = sourceNode._('PalettePane',kw)
        if(kw.searchOn){
            pane._('SlotBar',{'side':'top',slots:'*,searchOn',searchOn:objectPop(kw,'searchOn'),toolbar:true});
        }
        var grid = pane._('includedview', gridKwargs);
        return pane;
    }    
});

dojo.declare("gnr.widgets.PaletteTree", gnr.widgets.gnrwdg, {
    contentKwargs:function(sourceNode, attributes){
        attributes['frameCode'] = attributes.paletteCode;
        attributes.tree_onDrag = function(dragValues, dragInfo, treeItem) {
            if (treeItem.attr.child_count && treeItem.attr.child_count > 0) {
                return false;
            }
            dragValues['text/plain'] = treeItem.attr.caption;
            dragValues[attributes.paletteCode] = treeItem.attr;
        };
        attributes.tree_draggable=true;
        return attributes;
    },

    createContent:function(sourceNode, kw) {
        var frameCode = kw.frameCode;
        var editable = objectPop(kw, 'editable');
        var treeId = objectPop(kw, 'treeId') || frameCode + '_tree';
        var storepath = objectPop(kw, 'storepath') || '.store';
        var tree_kwargs = {_class:'fieldsTree', hideValues:true,
                            margin:'6px',nodeId:treeId,
                            'frameCode':frameCode,
                            storepath:storepath,labelAttribute:'caption'};
        objectUpdate(tree_kwargs, objectExtract(kw, 'tree_*'));
        var searchOn = objectPop(kw, 'searchOn');
        kw['contentWidget'] = 'FramePane';
        var pane = sourceNode._('PalettePane',kw);
        if (searchOn) {
            pane._('SlotBar',{'side':'top',slots:'*,searchOn',searchOn:true,toolbar:true});
        }
        if (editable) {
            var bc = pane._('BorderContainer',{'side':'center'});
            var bottom = bc._('ContentPane', {'region':'bottom',height:'30%',
                splitter:true});
            bottom._('BagNodeEditor', {nodeId:treeId + '_editbagbox',datapath:'.bagNodeEditor',bagpath:pane.getParentNode().absDatapath(storepath)});
            pane = bc._('ContentPane',{'region':'center'});
        }
        pane._('tree', tree_kwargs);
        return pane;
    }
});

dojo.declare("gnr.widgets.PaletteBagNodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var nodeId = objectPop(kw, 'nodeId');
        var pane = sourceNode._('PalettePane', kw);
        pane._('BagNodeEditor', {nodeId:nodeId,datapath:'.bagNodeEditor',bagpath:kw.bagpath});
        return pane;
    }
});

dojo.declare("gnr.widgets.BagNodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var gnrwdg = sourceNode.gnrwdg;
        var nodeId = objectPop(kw, 'nodeId');
        var readOnly = objectPop(kw, 'readOnly', false);
        var valuePath = objectPop(kw, 'valuePath');
        var showBreadcrumb = objectPop(kw, 'showBreadcrumb', true);
        var bc = sourceNode._('BorderContainer', {'nodeId':nodeId,detachable:true,_class:'bagNodeEditor'});
        if (showBreadcrumb) {
            var top = bc._('ContentPane', {'region':'top',background_color:'navy',color:'white'});
            top._('span', {'innerHTML':'Path : '});
            top._('span', {'innerHTML':'^.currentEditPath'});
        }
        var box = bc._('ContentPane', {'region':'center',_class:'formgrid'});
        var gridId = nodeId + '_grid';
        var topic = nodeId + '_editnode';
        var bagpath = objectPop(kw, 'bagpath');
        this.prepareStruct();
        gnrwdg.bagpath = bagpath;
        gnrwdg.valuePath = valuePath;
        gnrwdg.readOnly = readOnly;
        dojo.subscribe(topic, this, function(item) {
            gnrwdg.gnr.setCurrentNode(gnrwdg, item)
        });
        var grid = box._('includedview', {'storepath':'.data','structpath':'gnr._dev.bagNodeEditorStruct',
            'datamode':'bag','relativeWorkspace':true,'nodeId':gridId,
            autoWidth:false,'editorEnabled':true});
        if (!readOnly) {
            var gridEditor = grid._('gridEditor');
            var cellattr = {'gridcell':'attr_value','autoWdg':true};
            cellattr.validate_onAccept = function(value, result, validations, rowIndex, userChange) {
                var dataNode = this.grid.storebag().getParentNode().attr.dataNode;
                var attr_name = this.getRelativeData('.attr_name');
                if (attr_name == '*value') {
                    dataNode.setValue(value);
                } else {
                    var newattr = !('attr_name' in dataNode.attr);
                    dataNode.setAttribute(attr_name, value);
                    if (!value) {
                        objectPop(dataNode.attr, attr_name);
                    }
                    if (newattr || !value)
                        setTimeout(function() {
                            genro.publish(topic, dataNode);
                        }, 300);
                }
            };
            gridEditor._('textbox', {gridcell:'attr_name'});
            gridEditor._('textbox', cellattr);
        }
        return box;
    },
    setCurrentNode:function(gnrwdg, item) {
        var bagpath = gnrwdg.bagpath;
        var sourceNode = gnrwdg.sourceNode;
        if (typeof(item) == 'string') {
            item = sourceNode.getRelativeData(bagpath).getNode(item);
        }
        var itempath = item.getFullpath(null, sourceNode.getRelativeData(bagpath));
        sourceNode.setRelativeData('.currentEditPath', itempath);
        gnrwdg.currentEditPath = itempath;
        var newstore = new gnr.GnrBag();
        for (var k in item.attr) {
            var row = new gnr.GnrBag();
            row.setItem('attr_name', k, {_editable:false});
            row.setItem('attr_value', item.attr[k]);
            newstore.setItem('#id', row);
        }
        var itemvalue = item.getValue('static');

        if (gnrwdg.valuePath) {
            sourceNode.setRelativeData(gnrwdg.valuePath, itemvalue);
        } else {
            var editable = true;
            row = new gnr.GnrBag();
            row.setItem('attr_name', '*value', {_editable:false});
            if (itemvalue instanceof gnr.GnrBag) {
                var editable = false;
                itemvalue = '*bag*';
            }
            row.setItem('attr_value', itemvalue, {_editable:editable});
            newstore.setItem('#id', row);
        }

        newstore.sort('attr_name');
        //newstore.forEach(function(n){if(n.label.indexOf('~~')==0){n.label=n.label.slice(2);}});
        if (!gnrwdg.readOnly) {
            newstore.setItem('#id', new gnr.GnrBag({'attr_name':null,'attr_value':null}));
        }
        sourceNode.setRelativeData('.data', newstore, {'dataNode':item});
    },
    prepareStruct:function() {
        if (genro.getData('gnr._dev.bagNodeEditorStruct')) {
            return;
        }
        var rowstruct = new gnr.GnrBag();
        rowstruct.setItem('cell_0', null, {field:'attr_name',name:'Name',width:'30%',
            cellStyles:'background:gray;color:white;border-bottom:1px solid white;'});
        rowstruct.setItem('cell_1', null, {field:'attr_value',name:'Value',width:'70%',
            cellStyles:'border-bottom:1px solid lightgray;'});
        genro.setData('gnr._dev.bagNodeEditorStruct.view_0.row_0', rowstruct);
    }
});

dojo.declare("gnr.widgets.SearchBox", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        //var topic = attributes.nodeId+'_keyUp';
        var delay = 'delay' in attributes ? objectPop(attributes, 'delay') : 100;
        attributes.onKeyUp = function(e) {
            var sourceNode = e.target.sourceNode;
            if (sourceNode._onKeyUpCb) {
                clearTimeout(sourceNode._onKeyUpCb);
            }
            var v = e.target.value;
            sourceNode._onKeyUpCb = setTimeout(function() {
                sourceNode.setRelativeData('.currentValue', v);
            }, delay);
        };
        return attributes;
    },
    defaultDatapath:function(attributes) {
        return '.searchbox';
    },
    createContent:function(sourceNode, kw) {
        var searchOn = objectPop(kw, 'searchOn') || true;
        var searchDtypes;
        if (searchOn[0] == '*') {
            searchDtypes = searchOn.slice(1);
            searchOn = true;
        }
        var nodeId = objectPop(kw, 'nodeId');
        var menubag;
        var databag = new gnr.GnrBag();
        var defaultLabel = objectPop(kw, 'searchLabel') || 'Search';
        databag.setItem('menu_dtypes', searchDtypes);
        databag.setItem('caption', defaultLabel);
        this._prepareSearchBoxMenu(searchOn, databag);
        sourceNode.setRelativeData(null, databag);
        var searchbox = sourceNode._('table', {nodeId:nodeId,width:'100%'})._('tbody')._('tr');
        sourceNode._('dataController', {'script':'genro.publish(searchBoxId+"_changedValue",currentValue,field)',
            'searchBoxId':nodeId,currentValue:'^.currentValue',field:'^.field'});
        var searchlbl = searchbox._('td');
        searchlbl._('div', {'innerHTML':'^.caption',_class:'buttonIcon'});
        searchlbl._('menu', {'modifiers':'*',_class:'smallmenu',storepath:'.menubag',
            selected_col:'.field',selected_caption:'.caption'});
        
        searchbox._('td')._('div',{_class:'searchInputBox'})._('input', {'value':'^.value',connect_onkeyup:kw.onKeyUp});
        dojo.subscribe(nodeId + '_updmenu', this, function(searchOn) {
            menubag = this._prepareSearchBoxMenu(searchOn, databag);
        });
        return searchbox;
    },
    _prepareSearchBoxMenu: function(searchOn, databag) {
        var menubag = new gnr.GnrBag();
        var i = 0;
        if (searchOn === true) {
            databag.setItem('menu_auto', menubag);
        }
        else {
            dojo.forEach(searchOn.split(','), function(col) {
                col = dojo.trim(col);
                var caption = col;
                if (col.indexOf(':') >= 0) {
                    col = col.split(':');
                    caption = col[0];
                    col = col[1];
                }
                col = col.replace(/[.@]/g, '_');
                menubag.setItem('r_' + i, null, {col:col,caption:caption,child:''});
                i++;
            });
        }
        databag.setItem('field', menubag.getItem('#0?col'));
        var defaultLabel = menubag.getItem('#0?caption');
        if (defaultLabel) {
            databag.setItem('caption', defaultLabel);
        }
        databag.setItem('menubag', menubag);
        databag.setItem('value', '');
    }

});


dojo.declare("gnr.widgets.PaletteGroup", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var groupCode = objectPop(kw, 'groupCode');
        var palette_kwargs = objectExtract(kw, 'title,dockTo,top,left,right,bottom');
        palette_kwargs['nodeId'] = palette_kwargs['nodeId'] || groupCode + '_floating';
        palette_kwargs.selfsubscribe_showing = function() {
            genro.publish('palette_' + this.getRelativeData('gnr.palettes._groups.pagename.' + groupCode) + '_showing'); //gnr.palettes?gruppopiero=palettemario
        }
        palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + groupCode;
        var floating = sourceNode._('palette', palette_kwargs);
        var tab_kwargs = objectUpdate(kw, {selectedPage:'^gnr.palettes._groups.pagename.' + groupCode,groupCode:groupCode,_class:'smallTabs'});
        var tc = floating._('tabContainer', tab_kwargs);
        return tc;
    }
});

dojo.declare("gnr.widgets.SlotButton", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var slotbarCode = sourceNode.getInheritedAttributes().slotbarCode;
        kw['showLabel'] = kw.iconClass? (kw['showLabel'] || false):true;        
        var topic = slotbarCode+'_'+objectPop(kw,'publish');
        var topic = objectPop(kw,'publish');
        if(kw.action===true || 'action' in kw){
            kw.topic = topic;
            kw.command = kw.command || null;
            //kw['action'] = "genro.publish(topic,{'command':command})";
            kw['action'] = "genro.publish(topic,{'command':command})";
        }
        return sourceNode._('button',kw);
    }

});


dojo.declare("gnr.widgets.SlotBar", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var frameNode = sourceNode.getParentNode().getParentNode();
        var side=sourceNode.getParentNode().attr.region;
        var framePars = frameNode.attr;
        var sidePars = objectExtract(framePars,'side_*',true);
        var orientation = attributes.orientation || 'horizontal';
        if (side){
            orientation = ((side=='top')||(side=='bottom'))?'horizontal':'vertical';
        }
        attributes.orientation=orientation
        var buildKw={}
        dojo.forEach(['table','row','cell','lbl'],function(k){
            buildKw[k] = objectExtract(attributes,k+'_*');
            buildKw[k]['_class'] = (buildKw[k]['_class'] || '') + ' slotbar_'+k;
        });
        
        if(orientation=='horizontal'){
            if('height' in attributes){
                buildKw.cell['height']= objectPop(attributes,'height');
            }
        }else{
            if('width' in attributes){
                buildKw.cell['width'] = objectPop(attributes,'width');
            }
        }
        attributes['_class'] = (attributes['_class'] || '')+' slotbar  slotbar_'+orientation+' slotbar_'+side
        if(side){
            attributes['side'] = side;
            attributes['slotbarCode'] = attributes['slotbarCode'] || attributes['frameCode'] +'_'+ side; 
        if(objectPop(attributes,'toolbar')){
            attributes['_class'] += ' slotbar_toolbar';
                attributes['gradient_from'] = attributes['gradient_from'] || sidePars['gradient_from'] || genro.dom.themeAttribute('toolbar','gradient_from','silver');
                attributes['gradient_to'] = attributes['gradient_to'] || sidePars['gradient_to'] || genro.dom.themeAttribute('toolbar','gradient_to','whitesmoke');
                var css3Kw = {'left':[0,'right'],'top':[-90,'bottom'],
                            'right':[180,'left'],'bottom':[90,'top']}
                attributes['gradient_deg'] = css3Kw[side][0];
            }
        }
        buildKw.lbl['_class'] = buildKw.lbl['_class'] || 'slotbar_lbl'
        buildKw.lbl_cell = objectExtract(buildKw.lbl,'cell_*');
        attributes['buildKw'] = buildKw;
        return attributes;
    },
    
    createContent:function(sourceNode, kw,children) {
        var slots = objectPop(kw,'slots');
        return this['createContent_'+objectPop(kw,'orientation')](sourceNode,kw,kw.slotbarCode,slots,children);
    },
    createContent_horizontal:function(sourceNode,kw,slotbarCode,slots,children){
        var buildKw = objectPop(kw,'buildKw');
        var lblPos = objectPop(buildKw.lbl,'position') || 'N';
        var table = sourceNode._('div',kw)._('table',buildKw.table)._('tbody');
        var rlabel;
        if(lblPos=='T'){
            rlabel=  table._('tr');
        }
        var r = table._('tr',buildKw.row);
        if(lblPos=='B'){
            rlabel=  table._('tr');
        }
        var attr,cell,slotNode,slotValue,slotKw,slotValue;
        var children = children || new gnr.GnrBag();
        var that = this;
        var attr,kwLbl,lbl,labelCell,k;
        var slotArray = splitStrip(slots);
        var counterSpacer = dojo.filter(slotArray,function(s){return s=='*'}).length;
        var spacerWidth = counterSpacer? 100/counterSpacer:100;
        var cellKwLbl = buildKw.lbl_cell;
        dojo.forEach(slotArray,function(slot){
            if(rlabel){
                labelCell = rlabel._('td',cellKwLbl);
            }else if(lblPos=='L'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px'
                labelCell = r._('td',cellKwLbl)
            }
            if(slot=='*'){
                r._('td',{'_class':'slotbar_elastic_spacer',width:spacerWidth+'%'});
                return;
            }
            if(slot==parseInt(slot)){
                r._('td')._('div',{width:slot+'px'});
                return;
            }
            if(slot=='|'){
                r._('td')._('div',{_class:'slotbar_spacer'});
                return;
            }
            cell = r._('td',objectUpdate({_slotname:slot},buildKw.cell));
            if(lblPos=='R'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl)
            }
            slotNode = children.popNode(slot);
            if (!that['slot_'+slot] && slotNode){
                slotValue = slotNode.getValue();
                if(slotValue instanceof gnr.GnrBag){
                    k=0;
                    slotValue.forEach(function(n){
                        attr = n.attr;
                        kwLbl = objectExtract(attr,'lbl_*');
                        lbl = objectPop(attr,'lbl');
                        cell.setItem(n.label,n._value,n.attr);
                        if((k==0)&&labelCell){
                            kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                            labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                        }
                        k++;
                    })
                    
                }
            }
            if(cell.len()==0){
                if(that['slot_'+slot]){
                    slotKw = objectExtract(kw,slot+'_*');
                    slotValue = objectPop(kw,slot);
                    lbl = objectPop(slotKw,'lbl');
                    kwLbl = objectExtract(slotKw,'lbl_*');
                    kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                    that['slot_'+slot](cell,slotValue,slotKw,kw.frameCode)
                    if(labelCell){
                        labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                    }
                }else{
                    var textSlot=kw[slot]?kw[slot]:slot;
                    if(textSlot){
                        cell.setItem('div_0',null,objectUpdate({innerHTML:textSlot,tag:'div'},objectExtract(kw,slot+'_*')));
                    }
                }
            }       
        });
        
        return r;
    },
    createContent_vertical:function(sourceNode,kw,slotbarCode,slots,children){
        var buildKw = objectPop(kw,'buildKw');
        var lblPos = objectPop(buildKw.lbl,'position') || 'N';
        var table = sourceNode._('div',kw)._('table',buildKw.table)._('tbody');

        var attr,cell,slotNode,slotValue,slotKw,slotValue;
        var children = children || new gnr.GnrBag();
        var that = this;
        var attr,kwLbl,lbl,labelCell,k;
        var slotArray = splitStrip(slots);
        var cellKwLbl = buildKw.lbl_cell;
        dojo.forEach(slotArray,function(slot){
            /*if(rlabel){
                labelCell = rlabel._('td',cellKwLbl);
            }else if(lblPos=='L'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px'
                labelCell = r._('td',cellKwLbl)
            }*/
            if(slot=='*'){
                table._('tr');
                return;
            }
            if(slot=='|'){
                table._('tr',{'height':'1px'})._('td')._('div',{_class:'slotbar_spacer'});
                return;
            }
            if(slot==parseInt(slot)){
                table._('tr',{height:slot+'px'});
                return;
            }
            
            cell = table._('tr',buildKw.row)._('td',objectUpdate({_slotname:slot},buildKw.cell));
            /*if(lblPos=='R'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl)
            }*/
            slotNode = children.popNode(slot);
            if (slotNode){
                slotValue = slotNode.getValue();
                if(slotValue instanceof gnr.GnrBag){
                    k=0;
                    slotValue.forEach(function(n){
                        attr = n.attr;
                        kwLbl = objectExtract(attr,'lbl_*');
                        lbl = objectPop(attr,'lbl');
                        cell.setItem(n.label,n._value,n.attr);
                        /*if((k==0)&&labelCell){
                            kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                            labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                        }*/
                        k++;
                    });
                }
            }
            if(cell.len()==0 && (that['slot_'+slot])){
                slotKw = objectExtract(kw,slot+'_*');
                slotValue = objectPop(kw,slot);
                lbl = objectPop(slotKw,'lbl');
                kwLbl = objectExtract(slotKw,'lbl_*');
                kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                that['slot_'+slot](cell,slotValue,slotKw,kw.frameCode)
                if(labelCell){
                    labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                }
            }            
        });
        
        return table;
    },
    
    slot_searchOn:function(pane,slotValue,slotKw,frameCode){
        var div = pane._('div',{'width':slotKw.width || '15em'});
        div._('SearchBox', {searchOn:slotValue,nodeId:frameCode+'_searchbox',datapath:'.searchbox'});

    },
    slot_messageBox:function(pane,slotValue,slotKw,frameCode){        
        var mbKw = objectUpdate({duration:1000,delay:2000},slotKw);
        var subscriber = objectPop(mbKw,'subscribeTo');
        mbKw['subscribe_'+subscriber] = function(){
             var kwargs = arguments[0];
             var domNode = this.domNode;
             var sound = objectPop(kwargs,'sound');
             if(sound){
                 genro.playSound(sound);
             }
             var message = objectPop(kwargs,'message');
             var msgnode = document.createElement('span');
             msgnode.innerHTML = message;
             genro.dom.style(msgnode,kwargs);
             domNode.appendChild(msgnode);
             genro.dom.effect(domNode,'fadeout',{duration:objectPop(mbKw,'duration'),delay:objectPop(mbKw,'delay'),onEnd:function(){domNode.innerHTML=null;}});
        }
        pane._('span',mbKw);
    }
});


dojo.declare("gnr.widgets.FormStore", gnr.widgets.gnrwdg, {
    _beforeCreation: function(sourceNode) {
        var storeCode = sourceNode.attr.storeCode;
        var formId = sourceNode.getParentNode().getParentNode().attr.formId;
        if(!sourceNode.attr.storepath){
            if(formId){
                sourceNode.attr.storepath='.record';
            }else{
                console.error('missing storepath')
            }
        }
        if(!storeCode){
            if(formId){
                storeCode = formId+'_store';
            }else{
                console.error("missing storeCode in formStore not attached to a form")
            }
        }
        var handlers = sourceNode.getValue();
        var action;
        sourceNode._value = null;
        sourceNode.attr.handlers = {};
        handlers.forEach(function(n){
            action = objectPop(n.attr,'action');
            if(action){
                sourceNode.attr.handlers[action] = n.attr;
            }
        })
        sourceNode.attr.nodeId = sourceNode.attr.nodeId || storeCode+'_store';
        sourceNode._registerNodeId();
        return false;
    }
});


