//GNRWDG WIDGET DEFINITION BASE
dojo.declare("gnr.widgets.gnrwdg", null, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    _beforeCreation: function(attributes, sourceNode) {
        sourceNode.gnrwdg = {'gnr':this,'sourceNode':sourceNode};
        var attributes = sourceNode.attr;
        sourceNode.attr = {};
        sourceNode.attr.tag=objectPop(attributes,'tag');
        var datapath=objectPop(attributes,'datapath');
        if(datapath){sourceNode.attr.datapath=datapath;}
        else if(datapath===false){
            sourceNode.attr.datapath = '';
        }
        var contentKwargs = this.contentKwargs(sourceNode, attributes);
        if (!this.createContent) {
            return false;
        }
        sourceNode.freeze();
        var children = sourceNode.getValue();
        sourceNode.clearValue();
        var content = this.createContent(sourceNode, contentKwargs,children);
        genro.assert(content,'create content must return');
        content.concat(children);
        sourceNode._isComponentNode=true;
        genro.src.stripData(sourceNode);
        sourceNode.unfreeze(true);
        return false;
    },
    onStructChild:function(attributes,source) {
        if (source.getParentNode().attr.datapath==null && attributes.datapath==null) {
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

dojo.declare("gnr.widgets.TooltipPane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw, children) {
        
        var ddbId = sourceNode.getStringId();
        var modifiers = objectPop(kw,'modifiers') || '*';
        var onOpening = objectPop(kw,'onOpening');
        if (onOpening){
            onOpening = funcCreate(onOpening,'e,sourceNode',sourceNode);
        }
        var evt = objectPop(kw,'evt') || 'onclick';
        
        var parentDomNode = sourceNode.getParentNode().getDomNode();
        dojo.connect(parentDomNode,evt,function(e){
            if(genro.wdg.filterEvent(e,modifiers)){
                if(!onOpening || onOpening(e,e.target.sourceNode)){
                    genro.publish(ddbId+'_open',{'evt':e,'domNode':e.target});
                }
            } 
        });
        
        var ddb = sourceNode._('dropDownButton',{hidden:true,nodeId:ddbId,modifiers:modifiers,evt:evt,
                                selfsubscribe_open:"this.widget.dropDown._lastEvent=$1.evt;this.widget._openDropDown($1.domNode);"});

        kw['connect_onOpen'] = function(){
            this.widget.resize();
        };
        return  ddb._('TooltipDialog',kw);
    }
});

dojo.declare("gnr.widgets.Palette", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var left = objectPop(attributes, 'left');
        var right = objectPop(attributes, 'right');
        var top = objectPop(attributes, 'top');
        var bottom = objectPop(attributes, 'bottom');
        var lazyContent = objectPop(attributes,'lazyContent');
        var paletteCode = objectPop(attributes,'paletteCode');
        if(paletteCode){
            attributes['datapath'] = attributes['datapath'] || 'gnr.palettes.'+paletteCode;
        }
        if ((left === null) && (right === null) && (top === null) && (bottom === null)) {
            this._last_floating = this._last_floating || {top:0,right:0};
            this._last_floating['top'] += 10;
            this._last_floating['right'] += 10;
            top = this._last_floating['top'] + 'px';
            right = this._last_floating['right'] + 'px';
        }
        var dockTo = objectPop(attributes, 'dockTo');
        var dockButton = objectPop(attributes,'dockButton') || objectExtract(attributes, 'dockButton_*');
        if(dockButton===true){
            dockButton = {iconClass:'iconbox app'};
        }
        if (objectNotEmpty(dockButton)){
            dockTo = 'dummyDock';
            dockButton._class = 'slotButtonIconOnly';
            attributes.dockButton = dockButton;
        }
        var floating_kwargs = objectUpdate(attributes, {dockable:true,closable:false,visibility:'hidden'});
        floating_kwargs['templateString'] ="<div class=\"dojoxFloatingPane\" id=\"${id}\"><div tabindex=\"0\" waiRole=\"button\" class=\"dojoxFloatingPaneTitle\" dojoAttachPoint=\"focusNode\"><span dojoAttachPoint=\"closeNode\" dojoAttachEvent=\"onclick: close\" class=\"dojoxFloatingCloseIcon\"></span><span dojoAttachPoint=\"maxNode\" dojoAttachEvent=\"onclick: maximize\" class=\"dojoxFloatingMaximizeIcon\"></span><span dojoAttachPoint=\"restoreNode\" dojoAttachEvent=\"onclick: _restore\" class=\"dojoxFloatingRestoreIcon\"></span><span dojoAttachPoint=\"dockNode\" dojoAttachEvent=\"onclick: minimize\" class=\"dojoxFloatingMinimizeIcon\"></span><span dojoAttachPoint=\"titleNode\" class=\"dijitInline dijitTitleNode\"></span></div><div dojoAttachPoint=\"canvas\" class=\"dojoxFloatingPaneCanvas\"><div dojoAttachPoint=\"containerNode\" waiRole=\"region\" tabindex=\"-1\" class=\"${contentClass}\"></div><span dojoAttachPoint=\"resizeHandle\" class=\"dojoxFloatingResizeHandle\"></span></div></div>";
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
        floating_kwargs.subscribe_onClosePage=function(){
            this.widget.saveRect();
        };
        floating_kwargs.onCreated = function(widget) {
            setTimeout(function() {
                if(showOnStart){
                    widget.show();
                    widget.bringToTop();
                }
            }, 1);
        };
        if (!dockTo && dockTo !== false) {
            dockTo = 'default_dock';
        }
        if (dockTo) {
            floating_kwargs.dockTo = dockTo;
        }
        return objectUpdate({height:'350px',width:'300px',
            top:top,right:right,left:left,bottom:bottom,
            resizable:true}, floating_kwargs);
    },
    createContent:function(sourceNode, kw) {
        if (kw.dockTo == '*') {
            var dockId = sourceNode._id + '_dock';
            sourceNode._('dock', {id:dockId});
            kw.dockTo = dockId;
        }
        if (kw.dockButton){
            kw.dockButton['action'] = function(){
                var widget = genro.wdgById(kw.nodeId);
                widget.show();
                widget.bringToTop();
            };
            kw.dockButton['label'] = kw.dockButton['label'] || kw.title;
            kw.dockButton['showLabel'] = kw.dockButton['showLabel'] || !kw.dockButton.iconClass;
            sourceNode._('button', kw.dockButton);
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
                'paletteCode':paletteCode};
            controller_kw['subscribe_show_palette_' + paletteCode] = true;
            pane._('dataController', controller_kw);
            return pane;
        } else {
            var palette_kwargs = objectExtract(kw, 'title,dockTo,top,left,right,bottom,maxable,height,width,maxable,resizable');
            palette_kwargs.dockButton = objectPop(kw,'dockButton') || objectExtract(kw,'dockButton_*');
            palette_kwargs['nodeId'] = paletteCode + '_floating';
            palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + paletteCode;
            objectUpdate(palette_kwargs, objectExtract(kw, 'palette_*'));
            palette_kwargs.selfsubscribe_showing = function() {
                genro.publish('palette_' + paletteCode + '_showing');
            };
            palette_kwargs.selfsubscribe_hiding = function() {
                genro.publish('palette_' + paletteCode + '_hiding');
            };
            var floating = sourceNode._('palette', palette_kwargs);
            return floating._(contentWidget, kw);
        }
    }
});

dojo.declare("gnr.widgets.FramePane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var node;
        var frameCode = objectPop(kw,'frameCode');
        genro.assert(frameCode,'Missing frameCode');
        if(frameCode.indexOf('#')>=0){
            kw.frameCode = frameCode = frameCode.replace('#',sourceNode.getStringId());
        }
        var frameId = frameCode+'_frame';
        genro.assert(!genro.nodeById(frameId),'existing frame');
        sourceNode.attr.nodeId = frameId;
        sourceNode._registerNodeId();
        objectPop(kw,'datapath');
        var rounded_corners = genro.dom.normalizedRoundedCorners(kw.rounded,objectExtract(kw,'rounded_*',true));
        var centerPars = objectExtract(kw,'center_*');
        var bc = sourceNode._('BorderContainer', kw);
        var slot,v,sideKw;
        var sides= kw.design=='sidebar'? ['left','right','top','bottom']:['top','bottom','left','right'];
        var corners={'left':['top_left','bottom_left'],'right':['top_right','bottom_right'],'top':['top_left','top_right'],'bottom':['bottom_left','bottom_right']};
        dojo.forEach(sides,function(side){
             slot = children.popNode(side);
             if(slot){
                 node = slot.getValue().getNode('#0');
                 if(slot.attr.tag=='autoslot'){
                     objectPop(slot.attr,'tag');
                 }
             }else{
                 node = children.popNode('#side='+side);
             }
             if(node){                 
                 node.attr['frameCode'] = frameCode;
                 sideKw = slot?objectUpdate(slot.attr,{'region':side}):{'region':side};
                 sideKw.splitter = sideKw.splitter || objectPop(node.attr,'splitter');
                 objectPop(node.attr,'side');
                 dojo.forEach(corners[side],function(c){
                     v=objectPop(rounded_corners,c);
                     if(v){
                         node.attr['rounded_'+c] = v;
                     }
                 });
                 node.attr['_childname'] = node.attr['_childname'] || side;
                 bc._('ContentPane',sideKw).setItem('#id',node._value,node.attr);
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
            rounded['rounded_'+k]=rounded_corners[k];
        }
        if(centerNode){
            objectPop(centerNode.attr,'side');
            centerNode.attr['region'] = 'center';
            centerNode.attr['_childname'] = centerNode.attr['_childname'] || 'center';
            bc.setItem('center',centerNode._value,objectUpdate(rounded,centerNode.attr));
            center = centerNode._value;
        }else{
            centerPars['region'] = 'center';
            centerPars['_childname'] = centerPars['_childname'] || 'center';
            centerPars['widget'] = centerPars['widget'] || 'ContentPane';
            center = bc._(centerPars['widget'],'center',objectUpdate(rounded,centerPars));
        }
        return center;
    }
});

dojo.declare("gnr.widgets.FrameForm", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var formId = objectPop(kw,'formId');
        var storeNode = children.popNode('store');
        var contentNode = children.getNode('center.#0');
        genro.assert(contentNode,'missing contentNode:  attach to form.center a layout widget');
        contentNode.attr['_class'] =  contentNode.attr['_class'] + ' fh_content';
        var store = this.createStore(storeNode);
        var frameCode = kw.frameCode;
        formId = formId || frameCode+'_form';
        var frame = sourceNode._('FramePane',objectUpdate({controllerPath:'.controller',formDatapath:'.record',
                                                            pkeyPath:'.pkey',formId:formId,form_store:store},kw));
        if(kw.hasBottomMessage!==false){
            frame._('SlotBar',{'side':'bottom',slots:'*,messageBox,*',_class:'fh_bottom_message',messageBox_subscribeTo:'form_'+formId+'_message'});
        }
        var storeId = kw.store+'_store';
        return frame;
    },
    createStore:function(storeNode){
        var storeCode = storeNode.attr.storeCode;
        var storeContent = storeNode.getValue();
        var action,callbacks;
        storeNode._value = null;
        var handlers = {};
        if(storeContent){
            storeContent.forEach(function(n){
                action = objectPop(n.attr,'action');
                if(action){
                    objectPop(n.attr,'tag');
                    handlers[action] = n.attr;
                    callbacks = n.getValue();
                    if(callbacks){
                        handlers[action]['callbacks'] = callbacks;
                    }
                }
            });
        }        
        var kw = storeNode.attr;
        var storeType = objectPop(kw,'storeType');
        storeType = storeType ||(kw.parentStore?'Collection':'Item');
        return new gnr.formstores[storeType](kw,handlers);
    }
});
dojo.declare("gnr.widgets.PaletteMap", gnr.widgets.gnrwdg, {
    contentKwargs:function(sourceNode, attributes){
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var paletteCode=kw.paletteCode;
        kw.frameCode = paletteCode;
        kw['contentWidget'] = 'FramePane';
        var mapKw = objectExtract(kw,'map_*',false,true)
        var pane = sourceNode._('PalettePane',kw);
        var centerMarker = objectPop(kw,'centerMarker',true);
        if(centerMarker){
            mapKw.centerMarker = true;
        }
       //if(kw.searchOn){
       //    //var bar = pane._('SlotBar',{'side':'top',slots:'fbpars,*',searchOn:objectPop(kw,'searchOn'),toolbar:true});
       //    //var fb = genro.dev.formbuilder(bar._('div','fbpars',{}),{border_spacing:'1px',width:'100%',margin_bottom:'12px'});
       //   // _('horizontalSlider',{'value':'^.zoom'});
       //   // 
       //   //         fb.horizontalSlider(value='^.zoom',lbl='Zoom',minimum=4,maximum=21,width='150px',discreteValues=18)
       //
       //}
        
        var mapNode = pane._('GoogleMap',objectUpdate({'height':'100%',map_type:'roadmap'},mapKw)).getParentNode();
        
        var paletteNode = pane.getParentNode();
    
        paletteNode.addMapMarker = function(marker_name,marker){
            var kw={title:marker_name,draggable:true}
            mapNode.gnr.setMarker(mapNode,marker_name,marker,kw)
        };
        paletteNode.removeMapMarker = this.removeMapMarker;
        return pane;
    }
});

dojo.declare("gnr.widgets.PaletteGrid", gnr.widgets.gnrwdg, {
    contentKwargs:function(sourceNode, attributes){
        var gridId = attributes.gridId || attributes.paletteCode+'_grid';
        attributes['frameCode'] = attributes.paletteCode;
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var frameCode = kw.frameCode;
        var reloadOnShow = objectPop(kw,'reloadOnShow');
        var gridId = objectPop(kw, 'gridId') || frameCode+'_grid';
        var storepath = objectPop(kw, 'storepath');
        var structpath = objectPop(kw, 'structpath');
        var store = objectPop(kw, 'store');
        var _newGrid = objectPop(kw,'_newGrid');
        var paletteCode=kw.paletteCode;
        structpath = structpath? sourceNode.absDatapath(structpath):'.struct';
        var gridKwargs = {'nodeId':gridId,'datapath':'.grid',
                           'table':objectPop(kw,'table'),
                           'margin':'6px','configurable':true,
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
        var pane = sourceNode._('PalettePane',kw);
        if(kw.searchOn){
            pane._('SlotBar',{'side':'top',slots:'*,searchOn',searchOn:objectPop(kw,'searchOn'),toolbar:true});
        }
        pane._(_newGrid?'NewIncludedView':'includedview', 'grid',gridKwargs);
        var gridnode = pane.getNode('grid');
        gridnode.watch('isVisibile',function(){return genro.dom.isVisible(gridnode);},
                        function(){
                            if(gridnode.widget.storebag().len()==0 && reloadOnShow!==false){
                                gridnode.widget.reload(true)
                            }
                        });
        return pane;
    }    
});

dojo.declare("gnr.widgets.PaletteTree", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        
        var frameCode = kw.frameCode = kw.paletteCode;
        var editable = objectPop(kw, 'editable');
        var treeId = objectPop(kw, 'treeId') || frameCode + '_tree';
        var storepath = objectPop(kw, 'storepath') || '.store';
        var draggableFolders = objectPop(kw,'draggableFolders');
        var default_onDrag =  function(dragValues, dragInfo, treeItem) {
            if (treeItem.attr.child_count && treeItem.attr.child_count > 0 && !draggableFolders) {
                return false;
            }
            dragValues['text/plain'] = treeItem.attr.caption;
            dragValues[frameCode] = treeItem.attr;
        };
        var tree_kwargs = {_class:'fieldsTree', hideValues:true,
                            margin:'6px',nodeId:treeId,draggable:true,
                            'frameCode':frameCode,onDrag:default_onDrag,
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
        var bc = sourceNode._('BorderContainer', {'nodeId':nodeId+'_bc',detachable:true,_class:'bagNodeEditor'});
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
        sourceNode.registerSubscription(topic, this, function(item) {
            gnrwdg.gnr.setCurrentNode(gnrwdg, item);
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
        var searchbox = sourceNode._('table', {nodeId:nodeId})._('tbody')._('tr');
        sourceNode._('dataController', {'script':'genro.publish(searchBoxId+"_changedValue",currentValue,field)',
            'searchBoxId':nodeId,currentValue:'^.currentValue',field:'^.field',_userChanges:true});
        var searchlbl = searchbox._('td');
        searchlbl._('div', {'innerHTML':'^.caption',_class:'buttonIcon'});
        searchlbl._('menu', {'modifiers':'*',_class:'smallmenu',storepath:'.menubag',
            selected_col:'.field',selected_caption:'.caption'});
        
        searchbox._('td')._('div',{_class:'searchInputBox'})._('input', {'value':'^.value',connect_onkeyup:kw.onKeyUp,parentForm:false,width:objectPop(kw,'width') || '6em'});
        sourceNode.registerSubscription(nodeId + '_updmenu', this, function(searchOn) {
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
        var palette_kwargs = objectExtract(kw, 'title,dockTo,top,left,right,bottom,height,width,maxable,resizable');
        palette_kwargs.dockButton = objectPop(kw,'dockButton') || objectExtract(kw,'dockButton_*');
        palette_kwargs['nodeId'] = palette_kwargs['nodeId'] || groupCode + '_floating';
        palette_kwargs.selfsubscribe_showing = function() {
            genro.publish('palette_' + this.getRelativeData('gnr.palettes._groups.pagename.' + groupCode) + '_showing'); //gnr.palettes?gruppopiero=palettemario
        };
        palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + groupCode;
        var floating = sourceNode._('palette', palette_kwargs);
        var tab_kwargs = objectUpdate(kw, {selectedPage:'^gnr.palettes._groups.pagename.' + groupCode,groupCode:groupCode,_class:'smallTabs'});
        var tc = floating._('tabContainer', tab_kwargs);
        return tc;
    }
});

dojo.declare("gnr.widgets.TemplateChunk", gnr.widgets.gnrwdg, {
    getVirtualColumns:function(tpl_vc,curr_vc){
        curr_vc = curr_vc?curr_vc.split(','):[]
        tpl_vc = tpl_vc? tpl_vc.split(','):[];
        if(!curr_vc){
            curr_vc = tpl_vc;
        }else{
            dojo.forEach(tpl_vc,function(c){
                if(dojo.indexOf(curr_vc,c)<0){
                    curr_vc.push(c)
                }
            });
        }
        return curr_vc;
    },
    
    openTemplatePalette:function(sourceNode,editorConstrain,showLetterhead){
        var paletteCode = 'template_editor_'+sourceNode._id;
        //genro._data.popNode('gnr.palettes.'+paletteCode);
        var tplpars = sourceNode.attr._tplpars;
        var templateHandler = sourceNode._templateHandler;
        var handler = this;
        var paletteId = paletteCode+'_floating';
        if(sourceNode._connectedPalette){
            var paletteNode = sourceNode._connectedPalette;
            paletteNode.getWidget().show();
        }else{
            var table = tplpars.table;
            var remote_datasourcepath =  sourceNode.absDatapath(sourceNode.attr.datasource);
            var showLetterhead = typeof(showLetterhead)=='string'?(sourceNode.getRelativeData(showLetterhead) || true):showLetterhead;
            var kw = {'paletteCode':paletteCode,'dockTo':'dommyDock:open',
                    title:'Template Edit '+table.split('.')[1],width:'750px',
                    maxable:true,
                    height:'500px',
                    remote:'te_chunkEditorPane',
                    remote_table:table,
                    remote_paletteId:paletteId,
                    remote_resource_mode:(templateHandler.dataInfo.respath!=null),
                    remote_datasourcepath:remote_datasourcepath,
                    remote_showLetterhead:showLetterhead,
                    remote_editorConstrain: editorConstrain
                    };
                    
            kw.palette_selfsubscribe_savechunk = function(){
                tplpars = sourceNode.evaluateOnNode(tplpars);
                var template = tplpars.template || new gnr.GnrBag();
                var data = this.getRelativeData('.data').deepCopy();
                var custom = data.pop('metadata.custom');
                if(typeof(template)=='string'){
                    var respath = handler.saveTemplate(sourceNode,data,tplpars,custom);
                    templateHandler.dataInfo.respath = respath;
                }else{
                    var tplpath = sourceNode.attr._tplpars.template;
                    var currdata = sourceNode.getRelativeData(tplpath,data);
                    currdata.clear();
                    data.forEach(function(n){currdata.setItem(n.label,n._value,n.attr)});
                }
                templateHandler.setNewData({data:data,template: data.getItem('compiled'),dataInfo:templateHandler.dataInfo});           
                sourceNode.updateTemplate();
                sourceNode.publish('onChunkEdit');
                this.widget.hide();
            }
            var palette = sourceNode._('palettePane',kw);
            var paletteNode = palette.getParentNode();  
            sourceNode._connectedPalette = paletteNode; 
        }
        paletteNode.setRelativeData('.data',templateHandler.data.deepCopy()); 
        var respath = templateHandler.dataInfo.respath;
        if(respath && respath.indexOf('_custom')>=0){
            paletteNode.setRelativeData('.data.metadata.custom',true);
        }
    },
    

    updateVirtualColumns:function(sourceNode,datasourceNode,dataProvider,mainNode){
        var vc,curr_vc;
        if(dataProvider){
            curr_vc = dataProvider.attr.virtual_columns
            vc = this.getVirtualColumns(mainNode.attr.virtual_columns,curr_vc);
            if(vc){
                dataProvider.attr.virtual_columns = vc.join(',');
                dataProvider.fireNode();
            }
        }else{
            curr_vc = datasourceNode.attr._virtual_columns;
            vc = this.getVirtualColumns(mainNode.attr.virtual_columns,curr_vc);
            if(vc){
                if(datasourceNode._resolver){
                    datasourceNode._resolver.kwargs.virtual_columns = vc.join(',');
                    datasourceNode._resolver.lastUpdate = null;                    
                    sourceNode.attr._virtual_column = dojo.map(vc,function(c){return datasourceNode.label+'.'+c;}).join(',');
                }else{
                    sourceNode.attr._virtual_column =  vc.join(',');
                }
            }
        }
    },
    
    loadTemplate:function(sourceNode,kw){
        kw.template = kw.template || new gnr.GnrBag();
        if(kw.template instanceof gnr.GnrBag){
            var data = kw.template;
            return {data:data,dataInfo:{},template:data.getItem('compiled')};
        }
        var template_address = kw.table+':'+kw.template;
        var result = genro.serverCall("loadTemplate",{template_address:template_address,asSource:kw.asSource});
        if(result.attr.html){
            var content = result.getValue().getItem('content');
             return {template:content,dataInfo:result.attr,data:new gnr.GnrBag({'content':content})};
        }
        if(kw.asSource){
            var data = result.getValue();
            return {data:data,dataInfo:result.attr,template:data instanceof gnr.GnrBag?data.getItem('compiled'):''};
        }
        return {template:result};
    },
    
    saveTemplate:function(sourceNode,data,kw,custom){
        var template_address = kw.table+':'+kw.template;
        var templateHandler = sourceNode._templateHandler;
        if(custom){
            template_address = template_address+',custom'
        }
        return genro.serverCall("saveTemplate",{template_address:template_address,data:data},null,null,'POST');
    },
    
    
    createContent:function(sourceNode, kw,children) {
        var resource = objectPop(kw,'resource');
        if(resource){
            console.warn('templateChunk warning: use "template" param instead of "resource" param');
        }
        var tplpars = objectExtract(kw,'table,template,editable');
        var editorConstrain = objectExtract(kw,'constrain_*',null,true);
        var showLetterhead = objectPop(kw, 'showLetterhead');
        if(typeof(showLetterhead)=='string'){
            showLetterhead = sourceNode.absDatapath(showLetterhead);
        }
        for(var k in editorConstrain){
            var c = editorConstrain[k];
            if(typeof(c)=='string' && (c[0]=='^' || c[0]=='=')){
                editorConstrain[k] = c[0]+sourceNode.absDatapath(c);
            }
        }
        var showAlways = tplpars.editable;
        tplpars.template = tplpars.template || resource;
        kw._tplpars = tplpars;
        kw._tplpars.editable = kw._tplpars.editable || (genro.isDeveloper? 'developer':false);
        kw._tplpars.showAlways = kw._tplpars.editable===true;
        kw._tplpars.asSource =  kw._tplpars.editable!=null;

        var dataProvider = objectPop(kw,'dataProvider');
        if(dataProvider){
            dataProvider = sourceNode.currentFromDatasource(dataProvider);
        }
        
        genro.assert(kw.datasource,'datasource is mandatory in templatechunk');
        var handler = this;
        if(tplpars.editable){
            kw.connect_ondblclick = function(evt){
                if(tplpars.editable==true || evt.metaKey){
                    handler.openTemplatePalette(this,editorConstrain,showLetterhead);
                }
           };
        }
        
        kw.onCreated = function(domnode,attributes){
            var sourceNode = this;
            sourceNode._templateHandler = {};
            var templateHandler=sourceNode._templateHandler
            templateHandler.showAlways = showAlways;
            templateHandler.cb = function(){
                this.setNewData(handler.loadTemplate(sourceNode,sourceNode.evaluateOnNode(tplpars))); 
            };
            templateHandler.setNewData= function(result){
                this.data = result.data;
                this.dataInfo = result.dataInfo;
                this.template = result.template;
                this.defaults = {};
               
                var datasourcePath = sourceNode.absDatapath(sourceNode.attr.datasource);
                var datasourceNode = genro.getDataNode(datasourcePath);
                if(this.template instanceof gnr.GnrBag){
                     var varsbag = this.data.getItem('varsbag');
                     var defaults = this.defaults;
                     if(varsbag){
                         varsbag.forEach(function(n){
                             var v = n.getValue();
                             defaults[v.getItem('fieldpath')] = '<span class="chunkeditor_varplaceholder">'+(v.getItem('fieldname')||'')+'</span>';
                             },'static');
                    }
                    var mainNode = this.template.getNode('main');
                    handler.updateVirtualColumns(sourceNode,datasourceNode,dataProvider,mainNode)  
                }else{
                    this.template = this.template || '<div class="chunkeditor_emptytemplate">Template not yet created</div>';
                }
            };
            sourceNode.updateTemplate = function(){
                this._templateHandler.template = null;
                this.domNode.innerHTML = dataTemplate(this._templateHandler, this, this.attr.datasource);
            }
            sourceNode.attr.template = this._templateHandler;
            sourceNode._('dataController',{'script':"this.getParentBag().getParentNode().updateTemplate();",_fired:tplpars.template});
        }
        return sourceNode._('div','templateChunk',kw)
    }

});

dojo.declare("gnr.widgets.ImgUploader", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var value = objectPop(kw,'value'); //^miorul
        var placeholder = objectPop(kw,'placeholder');
        var folder = objectPop(kw,'folder');
        var filename = objectPop(kw,'filename');
        var zoomImage = objectPop(kw,'zoomImage');
        var width = objectPop(kw,'crop_width');
        var height = objectPop(kw,'crop_height');
        if(zoomImage){
            kw.connect_ondblclick="genro.openWindow(this.currentFromDatasource(this.attr.src),"+zoomImage+")";
            kw.cursor = 'pointer';
        }
        var cb = function(result){
            sourceNode.setRelativeData(value,this.responseText,{_formattedValue:genro.formatter.asText(this.responseText,{format:'img'})});
        };
        var uploaderAttr = {'src':'==_src?_src:placeholder;',
                           'placeholder':placeholder,'_src':value,
                            'dropTarget':true,dropTypes:'Files', 
                            'drop_ext':kw.drop_ext || 'png,jpg,jpeg,gif',
                            'crop_width':width,
                            'crop_height':height
                            };
                            


        uploaderAttr.onDrop = function(data,files){
                 var f = files[0];
                 var currfilename = sourceNode.currentFromDatasource(filename);
                 if(!currfilename){
                     //genro.alert('Warning',"You complete your data before upload");
                     return false;
                 }
                 genro.rpc.uploadMultipart_oneFile(f,null,{uploadPath:sourceNode.currentFromDatasource(folder),filename:currfilename,
                                                      onResult:cb});
            };

        return sourceNode._('img',objectUpdate(uploaderAttr,kw));
    }
    
});


dojo.declare("gnr.widgets.SlotButton", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var inherithed=sourceNode.getInheritedAttributes();
        kw['showLabel'] = kw.iconClass? (kw['showLabel'] || false):true; 
        if (!kw['showLabel']){
            kw['_class']= kw['_class'] ? kw['_class']+' slotButtonIconOnly':' slotButtonIconOnly';
        }
        var targetNode,prefix;
        var target = objectPop(kw,'target') || inherithed.target;
        if(target!=false){
            if(target){
                targetNode = genro.nodeById(target,sourceNode);
                prefix = (targetNode.attr.nodeId || targetNode.getStringId());
            }
        }else{
            prefix=inherithed.slotbarCode;
        }
        var publish=objectPop(kw,'publish');
        if(!kw.action){
            kw.topic = prefix?prefix+'_'+publish:publish;
            kw.command = kw.command || null;
            kw.opt = objectExtract(kw,'opt_*');
            kw['action'] = "genro.publish(topic,{'command':command,modifiers:genro.dom.getEventModifiers(event),evt:event,opt:opt,_counter:_counter});";
        }
        return sourceNode._('button',kw);
    }

});
dojo.declare("gnr.widgets.StackButtons", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var frameCode = objectPop(kw,'frameCode');
        var stackNode = objectPop(kw,'stack');
        if(!stackNode){
            genro.assert(kw.stackNodeId,'Need the stack node or the stackNodeId')
            stackNode = genro.nodeById(kw.stackNodeId);
        }
        var that = this;
        kw = objectUpdate({connect_onclick:function(e){
            var childSourceNode = e.target.sourceNode.getInheritedAttributes()['_childSourceNode'];
            if(childSourceNode){
                stackNode.widget.selectChild(childSourceNode.widget);
            }
        },_class:'multibutton_container'},kw);
        var tabButtonsNode = sourceNode._('div',kw);
        stackNode._stackButtonsNodes = stackNode._stackButtonsNodes || [];
        stackNode._stackButtonsNodes.push(tabButtonsNode.getParentNode());
        dojo.connect(stackNode,'onNodeBuilt',function(widget){
            genro.callAfter(function(){
                that.initButtons(stackNode);
                dojo.connect(widget.gnr,'onShowHideChild',that,'onShowHideChild');
                dojo.connect(widget.gnr,'onAddChild',that,'onAddChild');
                dojo.connect(widget.gnr,'onRemoveChild',that,'onRemoveChild');
            },1)
        })
        return tabButtonsNode;
    },
    onAddChild:function(widget,child){
        var sn = widget.sourceNode;
        var controllerNodes = sn._stackButtonsNodes;
        
        if((!controllerNodes) && sn._isBuilding){
            return;
        }
        var that = this;
        sn.delayedCall(function(){
            dojo.forEach(controllerNodes,function(c){
                that.makeTabButton(c,child.sourceNode);
            });
        },100);
    },
    onRemoveChild:function(widget,child){
        var sn = widget.sourceNode;
        var controllerNodes = sn._stackButtonsNodes;
        
        if((!controllerNodes) && sn._isBuilding){
            return;
        }
        var paneId = child.sourceNode.getStringId();
        setTimeout(function(){
            dojo.forEach(controllerNodes,function(c){
                c._value.popNode(paneId);
            });
        },1)
    },
    onShowHideChild:function(widget, child, st){
        if(!child){
            return;
        }
        var paneId = child.sourceNode.getStringId();
        var controllerNodes = widget.sourceNode._stackButtonsNodes;
        if(!controllerNodes){
            return;
        }
        dojo.forEach(controllerNodes,function(c){
            genro.dom.setClass(c._value.getNode(paneId),'multibutton_selected',st)
        })
        
    },
    initButtons:function(stackNode){
        var controllerNodes = stackNode._stackButtonsNodes;
        var sc = stackNode.widget;
        var page;
        var that = this;
        stackNode._value.forEach(function(n){
            if(n.getWidget()){
                dojo.forEach(controllerNodes,function(c){
                    that.makeTabButton(c,n);
                });
            }
        });
    },
    makeTabButton:function(sourceNode,childSourceNode){
        var widget = childSourceNode.getWidget();
        var childSourceNode = widget.sourceNode;
        if(childSourceNode.attr.title){
            var btn = sourceNode._('div',childSourceNode.getStringId(),{_class:widget.selected? 'multibutton multibutton_selected' :'multibutton',_childSourceNode:childSourceNode})
            btn._('div',{innerHTML:childSourceNode.attr.title,_class:'multibutton_caption'});
        }
    }
});
dojo.declare("gnr.widgets.ComboArrow", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw,childSourceNode){
        var focusNode;
        var curNode = sourceNode;
        while (!focusNode){
            if(curNode.widget){
                focusNode = curNode.widget.focusNode;
            }
            curNode = curNode.getParentBag().getParentNode()
        }
        genro.dom.addClass(focusNode.parentNode,'comboArrowTextbox')
        var iconClass = objectPop(kw,'iconClass') || 'dijitArrowButtonInner';
        var box= sourceNode._('div',objectUpdate({'_class':'fakeButton',cursor:'pointer', width:'20px',
                                position:'absolute',top:0,bottom:0,right:0},kw))
        box._('div',{_class:iconClass,position:'absolute',top:0,bottom:0,left:0,right:0})
        return box;
    }
    
});
dojo.declare("gnr.widgets.ComboMenu", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw,childSourceNode){
        kw['modifiers'] = kw['modifiers'] || '*';
        kw['attachTo'] = sourceNode.getParentBag().getParentNode();
        return sourceNode._('comboArrow')._('menu',kw);
    }
});


dojo.declare("gnr.widgets.CheckBoxText", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var popup = objectPop(kw,'popup');
        var values = objectPop(kw,'values');
        var value = objectPop(kw,'value');
        var separator = objectPop(kw,'separator') || ',';
        var codeSeparator = objectPop(kw,'codeSeparator');
        if(codeSeparator!==false){
            codeSeparator =  codeSeparator || ':'
        }
        var rootNode = sourceNode;
        var cell_kw = objectExtract(kw,'cell_*');
        var row_kw = objectExtract(kw,'row_*');
        var table_kw = objectExtract(kw,'table_*');
        var label_kw = objectExtract(kw,'label_*',null,true);
        var has_code = values.indexOf(':')>=0;

        if(popup){
            var tb = sourceNode._('textbox',objectUpdate({'value':has_code?value+'?value_caption':value,position:'relative'},kw));
            rootNode = tb._('comboArrow')._('tooltipPane')._('div',{padding:'5px'});
        }
        var tbl = rootNode._('table',table_kw)._('tbody')
        var tblNode = tbl.getParentNode();
        var splitter = values.indexOf('\n')>=0? '\n':',';
        var valuelist = splitStrip(values,splitter);
        var curr_row = tblNode._('tr',row_kw);
        var cell,cbpars,label,_code;
        var that = this;
        tblNode.attr._textvaluepath = value.replace('^','');
        tblNode.attr._has_code = has_code;
        tblNode.attr.action = function(){that.onCheckboxCheck(tblNode,separator);};

        var dcNode = tblNode._('dataController',{'script':"this._readValue(textvalue,textdescription,_triggerpars,_node);",
                                    textvalue:value,textdescription:value+'?value_caption'}).getParentNode();
        dcNode._readValue = function(textvalue,textdescription,_triggerpars,_node){
            if(_triggerpars.kw.reason=='cbgroup'){return}
            if(!_triggerpars.kw.updvalue){
                textvalue=null;
            }
            that.readValue(tblNode,textvalue,textdescription,separator);
        }
        var cols = objectPop(kw,'cols');
        var i = 1;
        var colspan;
        dojo.forEach(valuelist,function(v){
            if(v=='/'){
                curr_row =  tblNode._('tr',row_kw);
                i = 1;
                return;
            }
            if(cols && i>cols){
                i = 1;
                curr_row =  tblNode._('tr',row_kw);
            }

            label = v;
            if(has_code){
                v = v.split(codeSeparator);
                _code = v[0];
                label = v[1];
            }  
            colspan = 1;
            if(label.indexOf('\\')>=0){
                label = label.split('\\');
                colspan = parseInt(label[1]);
                label = label[0];
            }
            var z = objectUpdate(cell_kw,{colspan:colspan});
            cell = curr_row._('td',z);  
            cbpars ={label:label,_code:_code};
            cell._('checkbox',objectUpdate(cbpars,label_kw));
            i= i + colspan;
        })
        return tbl;
        
    },
    onCheckboxCheck:function(sourceNode,separator){
        var textvaluepath = sourceNode.attr._textvaluepath;
        var has_code = sourceNode.attr._has_code;
        var i = 0;
        var labels = [];
        var codes = [];
        var rows = sourceNode.getValue().getItem('#0');
        var sourceNodes = dojo.query('.dijitCheckBoxInput',sourceNode.domNode).map(function(n){
            return dijit.getEnclosingWidget(n).sourceNode
        });
        dojo.forEach(sourceNodes,function(cbNode){
            if(cbNode.widget.checked){
                if(has_code){
                    codes.push(cbNode.attr._code);
                }
                labels.push(cbNode.attr.label)
            }
        });
        if(has_code){
            sourceNode.setRelativeData(textvaluepath,codes.join(','),{value_caption:labels.join(separator)},null,'cbgroup');
        }else{
            sourceNode.setRelativeData(textvaluepath,labels.join(separator),{},null,'cbgroup');
        }
    },
    readValue:function(sourceNode,textvalue,textdescription,separator){
        var splitter = separator;
        var textvaluepath = sourceNode.attr._textvaluepath;
        var checkcodes = textvalue && sourceNode.attr._has_code;
        sourceNode.setRelativeData(textvaluepath,null,{},null,'cbgroup');
        if(checkcodes){
            splitter = ',';
        }
        textvalue = textvalue || textdescription || '';
        var values = splitStrip(textvalue,splitter);
        var v;
        var compareCb = function(node,value){
            if(checkcodes){
                return node.attr._code == value;
            }
            return node.attr.label.toLowerCase() == value.toLowerCase()
        };
        sourceNode._value.walk(function(n){
            if(n.attr.tag=='checkbox'){
                n.widget.setAttribute('checked',dojo.some(values,function(v){return compareCb(n,v)}));
            }
        });
        this.onCheckboxCheck(sourceNode,separator)
    }
});


dojo.declare("gnr.widgets.FieldsTree", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var table = objectPop(kw,'table');
        var trash = objectPop(kw,'trash');
        var box = sourceNode._('div',{_class:'fieldsTreeBox',_lazyBuild:true});
        var explorerPath = objectPop(kw,'explorerPath');
        if(explorerPath){
            kw.explorerPath = sourceNode.absDatapath(explorerPath);
        }
        if (trash){
            var trashKw = {_class:'treeTrash'};
            trashKw.dropTarget=true;
            trashKw.dropTypes='trashable';
            trashKw.onDrop_trashable=function(dropInfo,data){
                var sourceNode=genro.src.nodeBySourceNodeId(dropInfo.dragSourceInfo._id);
                if(sourceNode&&sourceNode.attr.onTrashed){
                    funcCreate(sourceNode.attr.onTrashed,'dropInfo,data',sourceNode)(dropInfo,data);
                }
            };
            sourceNode._('div',trashKw);
        }
        genro.dev.fieldsTree(box,table,kw);
        return box;
    }
})

dojo.declare("gnr.widgets.SlotBar", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var frameNode = sourceNode.getParentNode().getParentNode();
        var side=sourceNode.getParentNode().attr.region;
        var framePars = frameNode.attr;
        var sidePars = objectExtract(framePars,'side_*',true);
        var default_orientation = side?((side=='top')||(side=='bottom'))?'horizontal':'vertical':'horizontal';
        var orientation = attributes.orientation || default_orientation;

        attributes.orientation=orientation;
        var buildKw={};
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
        attributes['_class'] = (attributes['_class'] || '')+' slotbar  slotbar_'+orientation+' slotbar_'+side;
        var toolbar = objectPop(attributes,'toolbar');
        if(toolbar===true){
            toolbar = 'top';
        }
        side = side || toolbar;
        if(side){
            attributes['side'] = side;
            attributes['slotbarCode'] = attributes['slotbarCode'] || attributes['frameCode'] +'_'+ side; 
            if(toolbar){
                attributes['_class'] += ' slotbar_toolbar';
                attributes['gradient_from'] = attributes['gradient_from'] || sidePars['gradient_from'] || genro.dom.themeAttribute('toolbar','gradient_from','silver');
                attributes['gradient_to'] = attributes['gradient_to'] || sidePars['gradient_to'] || genro.dom.themeAttribute('toolbar','gradient_to','whitesmoke');
                
                var css3Kw = {'left':[0,'right'],'top':[-90,'bottom'],
                            'right':[180,'left'],'bottom':[90,'top']};
                attributes['border_'+css3Kw[side][1]] = attributes['border_'+css3Kw[side][1]] || '1px solid '+ attributes['gradient_from'];
                attributes['gradient_deg'] = css3Kw[side][0];
            }
        }
        buildKw.lbl['_class'] = buildKw.lbl['_class'] || 'slotbar_lbl';
        buildKw.lbl_cell = objectExtract(buildKw.lbl,'cell_*');
        attributes['buildKw'] = buildKw;
        return attributes;
    },
    
    addClosableHandle:function(sourceNode,kw){
        var pane = sourceNode.getParentNode();
        var bc = pane.widget.parentBorderContainer;
        var side = kw.side;
        var orientation = kw.orientation;
        if(bc._splitters[side]){
            genro.dom.setClass(bc._splitters[side],'tinySplitter',true);
        }
        var togglecb = function(){
            var toClose = !dojo.hasClass(pane.widget.domNode,'closedSide');
            genro.dom.setClass(pane,'closedSide','toggle');
            if(bc._splitters[side]){
                genro.dom.setClass(bc._splitters[side],'hiddenSplitter','toggle');
            }
            if(toClose){
                pane.__currDimension = pane.widget.domNode.style.width;
                dojo.style(pane.widget.domNode,orientation=='vertical'?'width':'height',null);
            }else if(pane.__currDimension){
                dojo.style(pane.widget.domNode,orientation=='vertical'?'width':'height',pane.__currDimension);
            }
            bc._layoutChildren(side);
            bc.layout();
        }
        genro.dom.setClass(pane,'closableSide_'+orientation,true);
        var closablePars = objectExtract(kw,'closable_*');
        var iconClass = objectPop(closablePars,'iconClass');
        if('top' in closablePars){
            closablePars['margin_top'] = closablePars['margin_top'] || 0;
        }
        if('left' in closablePars){
            closablePars['margin_left'] = closablePars['margin_left'] || 0;
        }

        var splitter = objectPop(closablePars,'splitter');
        if(kw.closable=='close'){
            togglecb()
        }
        var _class = 'slotbarOpener'+' slotbarOpener_'+orientation+' slotbarOpener_'+side;
        var label = objectPop(closablePars,'label');
        var opener = sourceNode._('div',objectUpdate({_class:_class,connect_onclick:togglecb},closablePars));
        if(label){
            opener._('div',{'innerHTML':label,_class:'slotbarOpener_label_'+orientation});
        }
        if(iconClass){
            opener._('div',{_class:iconClass});
        }
    },
    
    createContent:function(sourceNode, kw,children) {
        if(kw.closable){
            this.addClosableHandle(sourceNode,kw)
        }
        var slots = objectPop(kw,'slots');
        var orientation = objectPop(kw,'orientation');
        var result = this['createContent_'+orientation](sourceNode,kw,kw.slotbarCode,slots,children);
        dojo.forEach(children._nodes,function(n){if(n.attr.tag=='slot'){children.popNode(n.label);}});
        return result;
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
        var counterSpacer = dojo.filter(slotArray,function(s){return s=='*';}).length;
        var spacerWidth = counterSpacer? 100/counterSpacer:100;
        var cellKwLbl = buildKw.lbl_cell;
        dojo.forEach(slotArray,function(slot){
            if(rlabel){
                labelCell = rlabel._('td',cellKwLbl);
            }else if(lblPos=='L'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl);
            }
            if(slot=='*'){
                r._('td',{'_class':'slotbar_elastic_spacer',width:spacerWidth+'%'});
                return;
            };
            if(slot==parseInt(slot)){
                r._('td')._('div',{width:slot+'px'});
                return;
            };
            if(slot=='|'){
                r._('td')._('div',{_class:'slotbar_spacer'});
                return;
            };
            cell = r._('td',objectUpdate({_slotname:slot},buildKw.cell));
            if(lblPos=='R'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl); 
            };
            slotNode = children.popNode(slot);
            if (!that['slot_'+slot] && slotNode){
                if(slotNode.attr.tag=='slot'){
                    slotValue = slotNode.getValue();
                }else{
                    slotValue = new gnr.GnrBag({'slot':slotNode});
                }
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
                    });
                }
            }
            slotKw = objectExtract(kw,slot+'_*');
            if(slotKw.width){
                cell.getParentNode().attr['width'] = slotKw.width;
                slotKw.width = '100%';
            }
            if(cell.len()==0){
                if(that['slot_'+slot]){
                    slotValue = objectPop(kw,slot);
                    lbl = objectPop(slotKw,'lbl');
                    kwLbl = objectExtract(slotKw,'lbl_*');
                    kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                    that['slot_'+slot](cell,slotValue,slotKw,kw.frameCode);
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

        var attr,row,cell,slotNode,slotValue,slotKw,slotValue;
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
            
            row = table._('tr',buildKw.row)
            cell = row._('td',objectUpdate({_slotname:slot},buildKw.cell));
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
            slotKw = objectUpdate({},slotNode.attr);
            objectExtract(slotKw,'tag,_childname')
            slotKw = objectUpdate(slotKw,objectExtract(kw,slot+'_*'));
            if(slotKw.height){
                row.getParentNode().attr['height'] = slotKw.height;
                slotKw.height = '100%';
            }
            if(cell.len()==0 && (that['slot_'+slot])){
                slotValue = objectPop(kw,slot);
                lbl = objectPop(slotKw,'lbl');
                kwLbl = objectExtract(slotKw,'lbl_*');
                kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                that['slot_'+slot](cell,slotValue,slotKw,kw.frameCode);
                if(labelCell){
                    labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                }
            }            
        });
        
        return table;
    },
    
    slot_searchOn:function(pane,slotValue,slotKw,frameCode){
        var div = pane._('div'); //{'width':slotKw.width || '15em'}
        div._('SearchBox', {searchOn:slotValue,nodeId:frameCode+'_searchbox',datapath:'.searchbox',parentForm:false,'width':slotKw.width});

    },
    slot_stackButtons:function(pane,slotValue,slotKw,frameCode){
        var scNode = objectPop(slotKw,'stackNode');
        if(scNode){
           scNode = pane.getParentNode().currentFromDatasource(scNode);
        }
        if (!scNode){
            var stackNodeId = objectPop(slotKw,'stackNodeId');
            scNode = stackNodeId?genro.nodeById(stackNodeId):genro.getFrameNode(frameCode,'center');
        }
        slotKw['height'] = slotKw['height'] || '20px'
        pane._('StackButtons',objectUpdate({stack:scNode},slotKw));
    },
    slot_parentStackButtons:function(pane,slotValue,slotKw,frameCode){
        slotKw['height'] = slotKw['height'] || '20px'
        pane._('StackButtons',objectUpdate(objectUpdate({stack:pane.getParentNode().attributeOwnerNode('tag','StackContainer')},slotKw)));
    },
    
    slot_fieldsTree:function(pane,slotValue,slotKw,frameCode){
        var table = objectPop(slotKw,'table');
        table = pane.getParentNode().currentFromDatasource(table);
        var dragCode = objectPop(slotKw,'dragCode');
        var treeKw = objectExtract(slotKw,'tree_*') || {};
        treeKw.dragCode = dragCode;
        slotKw.text_align = 'left';
        slotKw.position = 'relative';
        var currRecordPath = objectPop(slotKw,'currRecordPath');
        var explorerPath = objectPop(slotKw,'explorerPath');

        var slot = pane._('div',slotKw);
        slot._('FieldsTree',objectUpdate({table:table,trash:true,currRecordPath:currRecordPath,explorerPath:explorerPath},treeKw));
    },
    
    slot_count:function(pane,slotValue,slotKw,frameCode){
        var row = pane._('table',{datapath:'.count',nodeId:frameCode+'_countbox', _class:'countBox'})._('tbody')._('tr');
        row._('td')._('div',{innerHTML:'^.shown',_class:'countBoxPartial'});
        row._('td')._('div',{innerHTML:'^.total',_class:'countBoxTotal'});
    },
    
    slot_messageBox:function(pane,slotValue,slotKw,frameCode){        
        var mbKw = objectUpdate({duration:1000,delay:2000},slotKw);
        var subscriber = objectPop(mbKw,'subscribeTo');
        var default_delay = objectPop(mbKw,'delay');
        var default_duration= objectPop(mbKw,'duration');

        mbKw['subscribe_'+subscriber] = function(){
             var kwargs = arguments[0];
             var domNode = this.domNode;
             var sound = objectPop(kwargs,'sound');
             var duration = objectPop(kwargs,'duration') || default_duration;
             var delay = objectPop(kwargs,'delay') || default_delay;
             if(sound){
                 genro.playSound(sound);
             }
             var message = objectPop(kwargs,'message');
             var msgnode = document.createElement('span');
             msgnode.innerHTML = message;
             genro.dom.style(msgnode,kwargs);
             domNode.appendChild(msgnode);
             var customOnEnd = kwargs.onEnd;
             genro.dom.effect(domNode,'fadeout',{duration:duration,delay:delay,
                                onEnd:function(){
                                    domNode.innerHTML=null;if(customOnEnd){customOnEnd();}}});
        };
        pane._('span',mbKw);
    }
});

dojo.declare("gnr.widgets.SelectionStore", gnr.widgets.gnrwdg, {
     contentKwargs: function(sourceNode, attributes) {
         if ('name' in attributes){
             attributes['_name'] = objectPop(attributes,'name');
         }
         if ('content' in attributes){
             attributes['_content'] = objectPop(attributes,'content');
         }
         //attributes['path'] = attributes['storepath'];
         attributes.columns = attributes.columns || '==gnr.getGridColumns(this);';
         attributes.method = attributes.method || 'app.getSelection';
         if('chunkSize' in attributes && !('selectionName' in attributes)){
             attributes['selectionName'] = '*';
         }
         return attributes;
     },

     createContent:function(sourceNode, kw,children) {
         var chunkSize = objectPop(kw,'chunkSize',0);
         var storeType = chunkSize? 'VirtualSelection':'Selection';
         kw.row_count = chunkSize;
         var identifier = objectPop(kw,'_identifier') || '_pkey';
         kw['_delay'] = kw['_delay'] || 'auto';
         var selectionStore = sourceNode._('dataRpc',kw);
         var cb = "this.store.onLoaded(result,_isFiredNode);";
         selectionStore._('callBack',{content:cb});
         var rpcNode = selectionStore.getParentNode();
         var storeKw = {'identifier':identifier,'chunkSize':kw.row_count,'storeType':storeType,'unlinkdict':kw.unlinkdict};
         if('startLocked' in kw){
             storeKw.startLocked = kw.startLocked;
         }
         rpcNode.store = new gnr.stores[storeType](rpcNode,storeKw);
         return selectionStore;
     }
});

dojo.declare("gnr.stores._Collection",null,{
    messages:{
        delete_one : "You are about to delete the selected record.<br/>You can't undo this",
        delete_many : "You are about to delete $count records.<br/>You can't undo this",
        unlink_one:"You are about to remove the selected record from current $master",
        unlink_many:"You are about to discard the selected $count records from current $master"
    },
    
    constructor:function(node,kw){
        this.storeNode = node;
        this.storepath = this.storeNode.attr.storepath;
        this.storeNode.setRelativeData(this.storepath,null);
        this.locked = null;
        var startLocked= 'startLocked' in kw? objectPop(kw,'startLocked'):false;
        for (var k in kw){
            this[k] = kw[k];
        }
        var that = this;
        var cb = function(){
            that.storeNode.subscribe('setLocked',function(v){that.setLocked(v);});
            var parentForm = that.storeNode.getFormHandler();
            if(parentForm){
                parentForm.subscribe('onDisabledChange',function(kw){that.setLocked(kw.disabled);},null,that.storeNode);
            }
            startLocked = parentForm?parentForm.locked:startLocked;
            setTimeout(function(){that.setLocked(startLocked);},1);
        };
        genro.src.afterBuildCalls.push(cb);
    },
    currentPkeys:function(){
        console.warn('currentPkeys not implemented in this store',this);
        return null;
    },

    setLocked:function(value){
        if(value=='toggle'){
            value = !this.locked;
        }
        this.locked = value;
        var parentForm = this.storeNode.getFormHandler();
        var parentProtect = parentForm?parentForm.isProtectWrite():false;
        this.storeNode.setRelativeData('.locked',value);
        this.storeNode.setRelativeData('.disabledButton',value || parentProtect);
        this.storeNode.publish('onLockChange',{'locked':this.locked});
    },
    
    onLoaded:function(result){
        this.externalChangedKeys = null;
        this.storeNode.setRelativeData(this.storepath,result);
        return result;
    },
    
    deleteRows:function(pkeys){
        return;
    },

    deleteAsk:function(pkeys,deleteCb){        
        var count = pkeys.length;
        var deleteCb = deleteCb || this.deleteRows; 
        if(count==0){
            return;
        }
        var dlg = genro.dlg.quickDialog('Alert',{_showParent:true,width:'280px'});
        var msg = count==1?'one':'many';
        var del_type,master;
        if(this.unlinkdict){
            del_type = 'unlink';
            master = this.unlinkdict.one_name;
        }else{
            del_type = 'delete';
            master ='';
        }
        dlg.center._('div',{innerHTML:_T(this.messages[del_type+'_'+msg]).replace('$count',count).replace('$master',master), 
                            text_align:'center',_class:'alertBodyMessage'});
        var that = this;
        var slotbar = dlg.bottom._('slotBar',{slots:'*,cancel,delete',
                                                action:function(){
                                                    dlg.close_action();
                                                    if(this.attr.command=='deleteRows'){
                                                        deleteCb.call(that,pkeys);
                                                    }
                                                }});
        slotbar._('button','cancel',{label:'Cancel',command:'cancel'});
        var btnattr = {label:'Delete',command:'deleteRows'};
        if(count>1){
            var fb = genro.dev.formbuilder(dlg.center,1,{border_spacing:'1px',width:'100%',margin_bottom:'12px'});
            fb.addField('numberTextBox',{value:'^gnr._dev.deleteask.count',width:'5em',lbl_text_align:'right',
                                        lbl:'Records to delete',lbl_color:'#444',parentForm:false});
            btnattr['disabled']='==_count!=_tot;';
            btnattr['_tot'] = count;
            fb._('data',{path:'gnr._dev.deleteask.count',content:null});
            //genro.setData('gnr._dev.deleteask.count',null);
            btnattr['_count'] = '^gnr._dev.deleteask.count';
        }
        
        slotbar._('button','delete',btnattr);
        dlg.show_action();
    },
    
    onCounterChanges:function(counterField,changes){},
    
    getData:function(){
        return this.storeNode.getRelativeData(this.storepath) || new gnr.GnrBag();
    },
    
    getItems:function(){
        return this.getData()._nodes;
    },
    len:function(filtered){
        if(filtered && this._filtered){
            return this._filtered.length;
        }
        return this.getItems().length;
    },
    
    sort:function(sortedBy){
        this.sortedBy = sortedBy || this.sortedBy;
        var data = this.getData();
        var sl = [];
        dojo.forEach(this.sortedBy.split(','),function(n){
            if(n.slice(0,3)!='#a.'){
                n = '#a.'+n;
            }
            sl.push(n);
        });
        sl = sl.join(',');
        data.sort(sl);
    },
    
    absIndex:function(idx){
        if (this.filterToRebuild()) {
            console.log('invalid filter');
        }
        return this._filtered ? this._filtered[idx] : idx;
    },
  
    rowFromItem:function(item,grid){
        if(grid){
            return grid.rowFromBagNode(item);
        }
        return item;
    },
    getNavigationPkey:function(nav,currentPkey){
        var idx = nav == parseInt(nav) && nav;
        if(!idx){
            if(nav=='first'){
                idx = 0;
            }else if(nav=='last'){
                idx = this.len()-1;
            }else{
                idx = this.getIdxFromPkey(currentPkey);
                idx = nav=='next'? idx+1:idx-1;
            }
        }
        return this.getKeyFromIdx(idx);
    },
    
    getKeyFromIdx:function(idx){
        var data = this.getData();
        if(!data){
            return;
        }
        var item;
        data=data.getNodes();
        if ((idx<0)||( idx>(data.length-1))){
            return null;
        }    
        return this.keyGetter(data[idx]);
    },
    getIdxFromPkey:function(pkey){
        var result = -1;
        var data = this.getData();
        var that = this;
        if(pkey && data){
            data=data.getNodes();
            var k = -1;
            dojo.some(data,function(n){
                k++;
                if(that.keyGetter(n)==pkey){
                    result = k;
                    return true;
                }
            });
            return result;
        }
    },
    getGridRowDataByIdx:function(grid,idx){
        var rowdata={};
        var node=this.itemByIdx(idx);
        if (node){
            rowdata= grid.rowFromBagNode(node,this.externalChangedKeys);
        }
        return rowdata;
    },
    
    filterToRebuild: function(value) {
        if (this._filtered){
            this._filterToRebuild=value;
        }
    },
    invalidFilter: function() {
        return this._filterToRebuild;
    },
    resetFilter: function() {
        return this._filtered = null;
    },
    
    compileFilter:function(value,filterColumn,colType){
        if(value==null){
            return null;
        }
        var cb;
        if (colType in {'A':null,'T':null}) {
            var regexp = new RegExp(value, 'i');
            cb = function(rowdata, index, array) {
                var columns = filterColumn.split('+');
                var txt = '';
                for (var i = 0; i < columns.length; i++) {
                    txt = txt + ' ' + rowdata[columns[i]];
                }
                return regexp.test(txt);
            };
        } else {
            var toSearch = /^(\s*)([\<\>\=\!\#]+)(\s*)(.+)$/.exec(value);
            if (toSearch) {
                var val;
                var op = toSearch[2];
                if (op == '=') {op = '==';}
                if ((op == '!') || (op == '#')) {op = '!=';}
                if (colType in {'R':null,'L':null,'I':null,'N':null}) {
                    val = dojo.number.parse(toSearch[4]);
                } else if (colType == 'D') {
                    val = dojo.date.locale.parse(toSearch[4], {formatLength: "short",selector:'date'});
                } else if (colType == 'DH') {
                    val = dojo.date.locale.parse(toSearch[4], {formatLength: "short"});
                }                
                cb = function(rowdata, index, array) {
                    return genro.compare(op,rowdata[filterColumn],val);
                };
            }
        }
        return cb;
    },

    createFiltered:function(grid,currentFilterValue,filterColumn,colType){
        var cb = this.compileFilter(currentFilterValue,filterColumn,colType);
        if (!cb && !grid.excludeListCb){
            this._filtered = null;
            return null;
        }
        var filtered=[];
        var excludeList = null;
        if (grid.excludeListCb) {
            excludeList = grid.excludeListCb.call(this.sourceNode);
        }
        dojo.forEach(this.getItems(), 
                    function(n,index,array){
                        var rowdata = grid.rowFromBagNode(n);
                        var result = cb? cb(rowdata,index,array):true; 
                        if(result){
                            if ((!excludeList)||(dojo.indexOf(excludeList, rowdata[grid.excludeCol]) == -1)) {
                                filtered.push(index);
                            }
                        }
                    });
        this._filtered=filtered;
        this._filterToRebuild=false;
    }
});

dojo.declare("gnr.stores.BagRows",gnr.stores._Collection,{
    keyGetter :function(n){
        return n.getValue('static').getItem(this.identifier);
    },
    getRowByIdx:function(idx){
        return ;
    },
    getItems:function(){
        var data=this.getData();
        return data?data.getNodes():[];
    },
    rowFromItem:function(n,grid){
        if(grid){
            return grid.rowFromBagNode(n);
        }
        return n.getValue();
    }
});

dojo.declare("gnr.stores.Selection",gnr.stores.BagRows,{
    constructor:function(){
        var that = this;
        if(this.storeNode.attr.externalChanges){
            var cb = function(){that.storeNode.registerSubscription('dbevent_'+that.storeNode.attr.table.replace('.','_'),that,function(kw){
                that.onExternalChange(kw.changelist,kw.pkeycol,kw.changeattr);          
                });};
                genro.src.afterBuildCalls.push(cb);
        }
    },
    currentPkeys:function(){
        var data = this.getData();
        var result = [];
        data.forEach(function(n){result.push(n.attr._pkey)});
        return result;
    },
    
    onExternalChange:function(changelist,pkeycol,changeattr){
        var eventdict = {};
        var dbevt,pkeys,wasInSelection,willBeInSelection;
        var insOrUpdKeys = [];
        var delKeys = [];
        var data = this.getData();
        var that = this;
        if(!data){
            return;
        }
        dojo.forEach(changelist,function(change){
            if (change['dbevent']=='D'){
                if (dojo.indexOf(delKeys,change.pkey)<0){
                     delKeys.push(change.pkey);
                }
               
            }else{
                if (dojo.indexOf(insOrUpdKeys,change.pkey)<0){
                    insOrUpdKeys.push(change.pkey);
                }
            }
        });
        if (insOrUpdKeys.length>0) {
            var original_condition =  this.storeNode.attr.condition;
            var newcondition = ' ( $'+pkeycol+' IN :_pkeys ) ';
            var kw = objectUpdate({},this.storeNode.attr);
            objectExtract(kw,'_*');
            kw._sourceNode = this.storeNode;
            kw._pkeys = insOrUpdKeys;
            kw.condition = original_condition?original_condition+' AND '+newcondition:newcondition;
            genro.rpc.remoteCall('app.getSelection', 
                                kw,null,'POST',null,
                                function(result){
                                            willBeInSelection={};
                                            result.getValue().forEach(function(n){
                                                willBeInSelection[n.attr['_pkey']] = n;
                                            },'static');
                                            that.checkExternalChange(delKeys,insOrUpdKeys,willBeInSelection,changeattr);
                                            return result;
                                    });
        }else if (delKeys.length>0) {
            this.checkExternalChange(delKeys,[],[],changeattr);
        }

    },
    
    onCounterChanges:function(counterField,changes){
        genro.serverCall('app.counterFieldChanges',{table:this.storeNode.attr.table,counterField:counterField,changes:changes});
    },
    
    linkedGrids:function(){
        var result = [];
        var storeCode;
        var storeNodeId = this.storeNode.attr.nodeId;
        genro.src._main.walk(function(n){
            if(n.widget && n.widget.selectionKeeper){
                storeCode = n.attr.store || n.attr.nodeId;
                if(storeCode+'_store'==storeNodeId){
                    result.push(n.widget);
                }
            }
        },'static');
        return result;
    },
    
    
    checkExternalChange:function(delKeys,insOrUpdKeys,willBeInSelection,changeattr){
        var linkedGrids = this.linkedGrids();
        var selectedPkeysDict = {};
        var selectedIndex,selectedPkey;
        var isExternalChange = changeattr.from_page_id!=genro.page_id;
        dojo.forEach(linkedGrids,function(grid){
            //grid.batchUpdating(true);
            genro.dom.removeClass(grid.sourceNode,'onExternalChanged');
            selectedIndex = grid.selection.selectedIndex;
            if(selectedIndex!=null&&selectedIndex>=0){
                selectedPkey = grid.rowIdByIndex(selectedIndex);
                selectedPkeysDict[selectedPkey] = selectedPkeysDict[selectedPkey] || [];
                selectedPkeysDict[selectedPkey].push(grid);
            }
            
        });
        var changedRows = {};
        var wasInSelection;
        var changed = false;
        var data = this.getData();
        var that = this;
        var toUpdate = false;
        var pkeys,wasInSelection,wasInSelectionNode,willBeInSelectionNode,pkey;
        this.externalChangedKeys = this.externalChangedKeys || {};
        var wasInSelectionCb = function(pkeys){
            var result = {};
            data.forEach(function(n){
                if (dojo.indexOf(pkeys,n.attr._pkey)>=0){
                    result[n.attr._pkey] = n;
                }
            },'static');  
            return result;
        };
        if(delKeys.length>0){
            wasInSelection = wasInSelectionCb(delKeys);
             for(pkey in wasInSelection){
                 toUpdate = true;
                 data.popNode(wasInSelection[pkey].label);
            }
        }
        if(insOrUpdKeys.length>0){
            wasInSelection = wasInSelectionCb(insOrUpdKeys);
            dojo.forEach(insOrUpdKeys,function(pkey){
                    wasInSelectionNode = wasInSelection[pkey];
                    willBeInSelectionNode = willBeInSelection[pkey];
                    if(wasInSelectionNode){
                        toUpdate=true;
                        if (willBeInSelectionNode) {
                            that.externalChangedKeys[pkey] = true;
                            var rowNode = data.getNodeByAttr('_pkey',willBeInSelectionNode.attr._pkey);
                            var rowValue = rowNode.getValue('static');
                            var newattr = objectUpdate({},willBeInSelectionNode.attr);
                            if(isExternalChange){
                                for(var attrname in willBeInSelectionNode.attr){
                                    changedRows[rowNode.attr._pkey] = rowNode;
                                    if(!isEqual(rowNode.attr[attrname],willBeInSelectionNode.attr[attrname])){
                                        if(rowValue instanceof gnr.GnrBag){
                                            var editedNode = rowValue.getNode(attrname);
                                            if(editedNode){
                                                editedNode.updAttributes({'_loadedValue':objectPop(newattr,attrname)},false);
                                            }
                                        }
                                        if(attrname in newattr){
                                            newattr['_customClass_'+attrname] = 'externalChangedCell';
                                        }
                                     }else if(rowValue instanceof gnr.GnrBag){
                                         var editedNode = rowValue.getNode(attrname);
                                         if(editedNode){
                                            editedNode.updAttributes({'_loadedValue':objectPop(newattr,attrname)},false);
                                         }
                                     }
                                }
                            }
                            rowNode.updAttributes(newattr,true);
                            if(selectedPkeysDict[pkey]){
                                dojo.forEach(selectedPkeysDict[pkey],function(grid){
                                    grid.sourceNode.publish('updatedSelectedRow');
                                });
                            }
                        }else{
                            data.popNode(wasInSelectionNode.label);
                        }
                    }else if(willBeInSelectionNode){
                        toUpdate = true;
                        that.externalChangedKeys[pkey] = true;
                        data.setItem('#id',willBeInSelectionNode);
                    }
                });
        }
        if(toUpdate && this.sortedBy){
            this.mustBeSorted = true;
        } 
        var that = this;
        dojo.forEach(linkedGrids,function(grid){
            //grid.batchUpdating(false);   
            if(toUpdate){
                if (!grid.gnrediting){
                    if(that.mustBeSorted){
                        that.sort();
                        that.filterToRebuild(true);
                        that.mustBeSorted = false;
                    }
                    grid.updateRowCount('*');
                }else{
                    grid.pendingSort = true;
                }

                grid.restoreSelectedRows();
            }
            for (var k in changedRows){
                var n = changedRows[k];
                objectExtract(n.attr,'_customClass_*');
                if(grid.gridEditor){
                    grid.gridEditor.onExternalChange(k);
                }
            }
            genro.userInfoCb.push(function(){
                genro.dom.addClass(grid.sourceNode,'onExternalChanged');
            });
            grid.sourceNode.publish('onExternalChanged');
        });

    },

    
    keyGetter :function(n){
        return n.attr[this.identifier];
    },
    
    rowFromItem:function(n,grid){
        if(grid){
            return grid.rowFromBagNode(n);
        }
        return n.attr();
    },
    itemByIdx:function(idx){
        var item=null;
        if (idx >= 0) {
            idx = this.absIndex(idx);
            var nodes=this.getItems();
            if (idx <= this.len()) {
                item=nodes[idx];
            }
        }
        return item;
    },

    deleteRows:function(pkeys){
        var that = this;
        var unlinkfield = this.unlinkdict?this.unlinkdict.field:null;
        genro.serverCall('app.deleteDbRows',{pkeys:pkeys,table:this.storeNode.attr.table,unlinkfield:unlinkfield},function(result){
            that.onDeletedRows(result);
        },null,'POST');
    },
    onDeletedRows:function(result){
        if(result && result.error){
            genro.dlg.alert(result.error,'Alert');
        }
    }

});


dojo.declare("gnr.stores.VirtualSelection",gnr.stores.Selection,{
    constructor:function(){
        this.pendingPages = {};
        this.lastIdx =0;
    },
    
    len:function(filtered){
        var data = this.getData();
        if(!data){
            return 0;
        }
        var dataNode = data.getParentNode();
        if(!dataNode){
            return 0;
        }
        var len = dataNode.attr['totalrows'] || 0;
        if(!filtered){
            len = dataNode.attr['totalRowCount']||len;
        }
        return len;
    },
    
    onLoaded:function(result,_isFiredNode){
        if(!_isFiredNode){
            this.externalChangedKeys = null;
        }
        if(result.error){
            return;
        }
        this.clearBagCache();
        var selection = result.getValue(); 
        var data = new gnr.GnrBag();
        var resultattr = result.attr;
        data.setItem('P_0',result.getValue()); 
        this.rowtotal = resultattr.rowcount;
        this.totalRowCount = resultattr.totalRowCount;
        this.selectionName = resultattr.selectionName;
        this.storeNode.setRelativeData(this.storepath,data,resultattr);
        return result;
    },
    onExternalChangeResult:function(changelist,result){
        if(changelist.length>0){
            var that = this;
            this.externalChangedKeys = this.externalChangedKeys || {};
            dojo.forEach(changelist,function(n){
                that.externalChangedKeys[n.pkey] = true;
            });
            this.storeNode.fireNode();
        }
    },
    
    onExternalChange:function(changelist){
        var parentNodeData = this.getData().getParentNode();
        if(!parentNodeData){
            return;
        }
        var selectionKw = parentNodeData.attr;
        var that = this;
        var rpc_attr = objectUpdate({},this.storeNode.attr);
        objectExtract(rpc_attr,'_*');
        objectUpdate(rpc_attr,{'selectionName':selectionKw.selectionName,
                                'changelist':changelist,'_sourceNode':this.storeNode});
        genro.rpc.remoteCall('app.checkFreezedSelection', 
                                            rpc_attr,null,null,null,
                                         function(result){
                                             that.onExternalChangeResult(changelist,result);
                                             return result;
                                          });
    },

    
    clearBagCache:function() {
        var data = this.getData();
        if(data){
            data.clear();
        }
        this.currRenderedRowIndex = null;
        this.currRenderedRow = null;
        this.currCachedPageIdx = null;
        this.currCachedPage = null;
    },

    itemByIdx:function(idx,sync) {
        var delta = idx-this.lastIdx;
        this.lastIdx = idx;
        var dataPage;
        var rowIdx = idx % this.chunkSize;
        var pageIdx = (idx - rowIdx) / this.chunkSize;
        if (this.currCachedPageIdx != pageIdx) {
            if(!sync){
                dataPage=this.getDataChunk(pageIdx);
            }else{
                dataPage=this.getData().getItem('P_' + pageIdx);
                if (!dataPage){
                    dataPage = this.loadBagPageFromServer(pageIdx,sync);
                }
            }
            
            if (dataPage){
                this.currCachedPageIdx = pageIdx;
                this.currCachedPage=dataPage;
                return this.currCachedPage.getNodes()[rowIdx];
            }else{
                this.currCachedPageIdx=-1;
                this.currCachedPage=null;
            }
        }else{
            if(((delta>0) && ((rowIdx/this.chunkSize)>.7 )) || ((delta<0) && ((rowIdx/this.chunkSize)<.3 ))){
                var guessPage = delta>0?pageIdx+1:pageIdx-1;
                if(guessPage>0){
                    if(guessPage!=this.guessPage){
                        this.getDataChunk(guessPage);
                        this.guessPage = guessPage;
                    }
                }
                
               
            }
            return this.currCachedPage.getNodes()[rowIdx];
        }
    },

    getDataChunk:function(pageIdx){
        if (pageIdx in this.pendingPages){
            return;
        }else{
            var pageData=this.getData().getItem('P_' + pageIdx);
            if (pageData){
                return pageData;    
            }
            if(this.isScrolling){
                return;
            }
            if(this.pendingTimeout){
                if (this.pendingTimeout.idx==pageIdx){
                    return;
                }else{
                    clearTimeout(this.pendingTimeout.handler);
                    this.pendingTimeout = {};
                }
            }
            var that = this;
            this.pendingTimeout={'idx':pageIdx,
                                'handler':setTimeout(function(){
                                that.loadBagPageFromServer(pageIdx);
                                },10)
            };
            return;
        }
    },
    onChunkLoaded:function(result,pageIdx){
        var data = result.getValue();
        this.getData().setItem('P_' + pageIdx, data,null,{'doTrigger':false});
        objectPop(this.pendingPages,pageIdx);
        this.storeNode.publish('updateRows');
        this.pendingTimeout = {};
       //if (this.pendingUpdateGrid){
       //    clearTimeout(this.pendingUpdateGrid);
       //}
       //var that = this;
       //this.pendingUpdateGrid=setTimeout(function(){
       //    that.storeNode.publish('updateRows');
       //},10);
        return data;
    },

    loadBagPageFromServer:function(pageIdx,sync) {
        console.log('loadBagPageFromServer components',pageIdx,sync)
        var that = this;
        var row_start = pageIdx * this.chunkSize;
        var kw = this.getData().getParentNode().attr;
        var result = genro.rpc.remoteCall(kw.method, {'selectionName':kw.selectionName,
            'row_start':row_start,
            'row_count':this.chunkSize,
            'sortedBy':this.sortedBy,
            'table':kw.table,
            'recordResolver':false},
            null,
            null,
            null,
            sync?null:function(result){return that.onChunkLoaded(result,pageIdx);});
        if(sync){
            return this.onChunkLoaded(result,pageIdx);
        }else{
            this.pendingPages[pageIdx] = result;
        }
     },
     
     getIdxFromPkey:function(pkey){
        var result = -1;
        var dataNode = this.getData().getNodeByAttr('_pkey',pkey);
        if(dataNode){
            result = dataNode.attr.rowidx;
        }
        return result;
    },
    getKeyFromIdx:function(idx){
        var dataNode = this.itemByIdx(idx,true);
        //var dataNode = this.getData().getNodeByAttr('rowidx',idx);
        return this.keyGetter(dataNode);
    }
    
});




