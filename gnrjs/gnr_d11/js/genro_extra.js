dojo.declare("gnr.GridEditor", null, {
    constructor:function(widget, sourceNode, gridEditorNode) {
        var gridEditorColumns = gridEditorNode.getValue();
        this.grid = widget;
        var grid = this.grid;
        this.viewId = sourceNode.attr.nodeId;
        this.formId = sourceNode.getInheritedAttributes()['formId'];
        this.grid.rows.isOver = function(inRowIndex) {
            return ((this.overRow == inRowIndex) && !grid.gnrediting);
        };
        this.grid.selection.isSelected = function(inRowIndex) {
            return this.selected[inRowIndex] && !grid.gnrediting;
        };
        var columns = {};
        var attr;
        // dojo.connect(widget,'onCellMouseOver',this,'onCellMouseOver')
        this.widgetRootNode = gridEditorNode;
        gridEditorColumns.forEach(function(node) {
            attr = node.attr;
            if (!attr.gridcell) {
                throw "Missing gridcell parameter";
            }
            columns[attr.gridcell.replace(/\W/g, '_')] = {'tag':attr.tag,'attr':attr};
        });
        this.columns = columns;
        gridEditorNode.setValue(null, false);
        gridEditorNode.attr.tag = null;
        gridEditorNode.attr.datapath = sourceNode.absDatapath(sourceNode.attr.storepath);
        var editOn = gridEditorNode.attr.editOn || 'onCellDblClick';
        editOn = stringSplit(editOn, ',', 2);
        var modifier = editOn[1];
        var _this = this;

        dojo.connect(widget, editOn[0], function(e) {
            if (genro.wdg.filterEvent(e, modifier)) {
                if (grid.editorEnabled && _this.editableCell(e.cellIndex) && !grid.gnrediting) {
                    dojo.stopEvent(e);
                    if (_this.grid._delayedEditing) {
                        clearTimeout(_this.grid._delayedEditing);
                    }
                    _this.grid._delayedEditing = setTimeout(function() {
                        _this.startEdit(e.rowIndex, e.cellIndex);
                    }, 1);
                }
            }
        });
    },
    onEditCell:function(start) {
        var grid = this.grid;
        grid.gnrediting = start;
        dojo.setSelectable(grid.domNode, grid.gnrediting);
    },

    invalidCell:function(cell, row) {
        var rowNode = this.grid.dataNodeByIndex(row);
        if (!rowNode) {
            console.log('missing rowNode');
            return;
        }
        var rowData = rowNode.getValue('static');
        if (rowData) {
            var datanode = rowData.getNode(cell.field);
            return datanode ? datanode.attr._validationError : false;
        }
    },

    startEdit:function(row, col) {
        var grid = this.grid;
        var cell = grid.getCell(col);
        var colname = cell.field;
        var fldDict = this.columns[colname];
        var gridcell = fldDict.attr.gridcell;
        var rowDataNode = grid.dataNodeByIndex(row);
        var datachanged = false;
        if (rowDataNode && rowDataNode._resolver && rowDataNode._resolver.expired()) {
            datachanged = true;
        }
        var rowData = rowDataNode.getValue();
        var cellDataNode = rowData.getNode(gridcell);
        if (!cellDataNode) {
            datachanged = true;
            cellDataNode = rowData.getNode(gridcell, null, true);
        }
        else if (cellDataNode._resolver && cellDataNode._resolver.expired()) {
            datachanged = true;
            cellDataNode.getValue();
        }
        if (datachanged) {
            setTimeout(dojo.hitch(this, 'startEdit', row, col), 1);
            return;
        }
        if(cellDataNode.attr._editable===false){
            return;
        }
        var rowLabel = rowDataNode.label;
        var cellNode = cell.getNode(row);

        var attr = objectUpdate({}, fldDict.attr);
        attr.datapath = '.' + rowLabel;
        //attr.preventChangeIfIvalid = true;     
        if ('value' in attr) {
            if (attr.tag.toLowerCase() == 'dbselect') {
                attr.selectedCaption = '.' + gridcell;
            }
        }
        else {
            attr['value'] = '^.' + gridcell;
        }
        if (this.viewId) {
            if (attr.exclude == true) {
                attr.exclude = '==genro.wdgById("' + this.viewId + '").getColumnValues("' + attr['value'] + '")';
            }
        }
        ;
        /*
         var dflt = attr['default'] || attr['default_value'] || '';
         node.getAttributeFromDatasource('value', true, dflt);
         */


        var editingInfo = {'cellNode':cellNode,'contentText':cellNode.innerHTML,
            'row':row,'col':col};
        cellNode.innerHTML = null;
        var cbKeys = function(e) {
            var keyCode = e.keyCode;
            var keys = genro.PATCHED_KEYS;
            var widget = this.widget;
            if ((keyCode == keys.SHIFT) || (keyCode == keys.CTRL) || (keyCode == keys.ALT)) {
                return;
            }
            if (keyCode == keys.TAB) {
                widget.cellNext = e.shiftKey ? 'LEFT' : 'RIGHT';
                //console.log('tabkey '+widget.cellNext);
            }
            if ((e.shiftKey) && ((keyCode == keys.UP_ARROW) ||
                    (keyCode == keys.DOWN_ARROW) ||
                    (keyCode == keys.LEFT_ARROW) ||
                    (keyCode == keys.RIGHT_ARROW))) {

                if (keyCode == keys.UP_ARROW) {
                    widget.cellNext = 'UP';
                } else if (keyCode == keys.DOWN_ARROW) {
                    widget.cellNext = 'DOWN';
                } else if (keyCode == keys.LEFT_ARROW) {
                    widget.cellNext = 'LEFT';
                } else if (keyCode == keys.RIGHT_ARROW) {
                    widget.cellNext = 'RIGHT';
                }
                dojo.stopEvent(e);
                widget.focusNode.blur();
                //widget._onBlur();
                //setTimeout(dojo.hitch(this.focusNode, 'blur'), 1);
            }

        };
        var gridEditor = this;

        var cbBlur = function(e) {
            var cellNext = this.widget.cellNext; //|| 'RIGHT'; dannoso
            this.widget.cellNext = null;
            deltaDict = {'UP': {'r': -1, 'c': 0},
                'DOWN': {'r': 1, 'c': 0},
                'LEFT': {'r': 0, 'c': -1},
                'RIGHT': {'r': 0, 'c': 1},
                'STAY':{'r': 0, 'c': 0}
            };
            setTimeout(dojo.hitch(gridEditor, 'endEdit', this.widget, deltaDict[cellNext], editingInfo), 300);
        };
        attr._parentDomNode = cellNode;
        attr._class = attr._class ? attr._class + ' widgetInCell' : 'widgetInCell';
        attr.connect_keydown = cbKeys;
        attr.connect_onBlur = cbBlur;
        attr._autoselect = true;
        var wdgtag = fldDict.tag;
        if(attr.autoWdg){
            var dt = convertToText(cellDataNode.getValue())[0];
            wdgtag = {'L':'NumberTextBox','D':'DateTextbox','R':'NumberTextBox','N':'NumberTextBox','H':'TimeTextBox'}[dt] || 'Textbox';
        }
        var editWidgetNode = this.widgetRootNode._(wdgtag, attr).getParentNode();
        editWidgetNode.editedRowIndex = row;
        this.onEditCell(true);
        if (cellDataNode.attr._validationError || cellDataNode.attr._validationWarnings) {
            editWidgetNode._validations = {'error':cellDataNode.attr._validationError,'warnings':cellDataNode.attr._validationWarnings};
            editWidgetNode.updateValidationStatus();
        }
        ;
        editWidgetNode.widget.focus();
        editWidgetNode.grid = gridEditor.grid;

    },

    endEdit:function(editWidget, delta, editingInfo) {
        var cellNode = editingInfo.cellNode;
        var contentText = editingInfo.contentText;
        editWidget.sourceNode._destroy();
        editingInfo.cellNode.innerHTML = contentText;
        this.onEditCell(false);
        if (delta) {
            var rc = this.findNextEditableCell({row:editingInfo.row, col:editingInfo.col}, delta);
            if (rc) {
                this.startEdit(rc.row, rc.col);
            }
        }

    },
    editableCell:function(col) {
        return (this.grid.getCell(col).field in this.columns);
    },
    findNextEditableCell: function(rc, delta) {
        var row = rc.row;
        var col = rc.col;
        var grid = this.grid;
        do{
            col = col + delta.c;
            if (col >= grid.layout.cellCount) {
                col = 0;
                row = row + 1;
            }
            if (col < 0) {
                col = grid.layout.cellCount - 1;
                row = row - 1;
            }

            row = row + delta.r;
            if ((row >= grid.rowCount) || (row < 0)) {
                return;
            }
        } while (!this.editableCell(col));
        rc.col = col;
        rc.row = row;
        return rc;
    }

});

//GNRWDG WIDGET DEFINITION BASE
dojo.declare("gnr.widgets.gnrwdg", null, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    _beforeCreation: function(sourceNode) {
        sourceNode.gnrwdg = {'gnr':this,'sourceNode':sourceNode};
        var attributes = objectUpdate({},sourceNode.attr);
        objectExtract(sourceNode.attr,'nodeId');
        var contentKwargs = this.contentKwargs(sourceNode,attributes);
        sourceNode.freeze();
        var children = sourceNode.getValue();
        sourceNode.clearValue();
        var content = this.createContent(sourceNode, contentKwargs);
        content.concat(children);
        sourceNode._stripData();
        sourceNode.unfreeze(true);
        return false;
    },
    onStructChild:function(attributes){
        if (!attributes.datapath){
            var defaultDatapath=this.defaultDatapath(attributes);
            if(defaultDatapath){
                attributes.datapath = defaultDatapath;
            }
        }
       
    },
    
    contentKwargs: function(sourceNode,attributes) {
        return attributes;
    },
    defaultDatapath:function(attributes){
        return null;
    }
});

dojo.declare("gnr.widgets.Palette", gnr.widgets.gnrwdg, {
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
        var dockTo = objectPop(attributes,'dockTo');
        var floating_kwargs = objectUpdate(attributes,{dockable:true,closable:false,visibility:'hidden'});
        var showOnStart = false;
        if(dockTo===false){
            floating_kwargs.closable = true;
            floating_kwargs.dockable = false;
            showOnStart = true;
        }else if(dockTo && dockTo.indexOf(':open')>=0){
            dockTo = dockTo.split(':')[0];
            objectPop(floating_kwargs,'visibility');
            showOnStart = true;
        }
        if(showOnStart){
            floating_kwargs.onCreated = function(widget){
                setTimeout(function(){
                    widget.show();
                    widget.bringToTop();
                },1);};
        }
        if(!dockTo && dockTo!==false){
            dockTo = 'default_dock';
        }
        if(dockTo){
            floating_kwargs.dockTo=dockTo;
        }
        return objectUpdate({height:'400px',width:'300px',
                            top:top,right:right,left:left,bottom:bottom,
                            resizable:true},floating_kwargs);
    },
    createContent:function(sourceNode, kw) {
        if(kw.dockTo=='*'){
            var dockId =  sourceNode._id+'_dock';
            sourceNode._('dock',{id:dockId});
            kw.dockTo = dockId;
        }
        if(kw.nodeId){
            kw.connect_show= function(){
                genro.publish(kw.nodeId+'_showing');
            };
            kw.connect_hide= function(){
                genro.publish(kw.nodeId+'_hiding');
            };
        }
        return sourceNode._('floatingPane', kw);
    }
});


dojo.declare("gnr.widgets.PalettePane", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode,attributes){
        var inattr = sourceNode.getInheritedAttributes();
        var groupCode = inattr.groupCode;
        attributes.nodeId = attributes.nodeId || 'palette_'+attributes.paletteCode;
        attributes._class = attributes._class || "basePalette";
        if(groupCode){
            attributes.groupCode = groupCode;
            attributes.pageName = attributes.paletteCode;
        }
        return attributes;
    },

    defaultDatapath:function(attributes){
        return  'gnr.palettes.'+attributes.paletteCode;
    },
    createContent:function(sourceNode, kw) {
        var paletteCode = objectPop(kw,'paletteCode');
        var groupCode = objectPop(kw,'groupCode');
        if (groupCode){
            var pane = sourceNode._('ContentPane',objectExtract(kw,'title,pageName'))._('ContentPane',objectUpdate({'detachable':true},kw));
            var controller_kw = {'script':"SET gnr.palettes._groups.pagename."+groupCode+" = paletteCode;",
                                 'paletteCode':paletteCode}
            controller_kw['subscribe_show_palette_'+paletteCode] = true;
            pane._('dataController',controller_kw);
            return pane;
        }else{
            var palette_kwargs = objectExtract(kw,'title,dockTo,top,left,right,bottom,maxable');
            palette_kwargs['nodeId'] = paletteCode+'_floating';
            palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + paletteCode;
            objectUpdate(palette_kwargs,objectExtract(kw,'palette_*'));
            palette_kwargs.selfsubscribe_showing = function(){
                genro.publish('palette_'+paletteCode+'_showing');
            }
            var floating = sourceNode._('palette', palette_kwargs);
            return floating._('ContentPane',kw);
        }
    }
});
dojo.declare("gnr.widgets.PaletteGrid", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var grid_kwargs = {margin:'6px', draggable_row:true,configurable:true,
                            storepath:(objectPop(kw,'storepath') || '.#parent.store'),
                            structpath:(objectPop(kw,'structpath') || '.struct'),
                            relativeWorkspace:true,datapath:'.grid',
                            table:kw.table};
        var paletteCode = kw.paletteCode;
        var gridId =objectPop(kw,'gridId') || 'palette_'+paletteCode+'_grid';
        grid_kwargs.nodeId = gridId;
        grid_kwargs.onDrag = function(dragValues,dragInfo){
            if(dragInfo.dragmode=='row'){
                dragValues[paletteCode]=dragValues.gridrow.rowsets;
            }
        };
        kw.selfsubscribe_showing=function(){
            var grid = genro.wdgById(gridId);
            if(grid.storebag().len()==0){
                grid.reload();
            }
        }
        objectUpdate(grid_kwargs ,objectExtract(kw,'grid_*'));
        var pane = sourceNode._('PalettePane',kw);
        if (kw.searchOn){
            var bc = pane._('BorderContainer');
            var top = bc._('ContentPane',{region:'top'})._('Toolbar',{height:'18px'});
            pane = bc._('ContentPane',{region:'center'});
            top._('SearchBox',{searchOn:kw.searchOn,nodeId:gridId+'_searchbox',datapath:'.searchbox'});
        }
        var grid = pane._('includedview',grid_kwargs);
        return pane;
    }
});
dojo.declare("gnr.widgets.PaletteTree", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var paletteCode = kw.paletteCode;
        var editable = objectPop(kw,'editable');
        var treeId =objectPop(kw,'treeId') || 'palette_'+paletteCode+'_tree';
        var storepath = objectPop(kw,'storepath') || '.store';
        var tree_kwargs = {_class:'fieldsTree', hideValues:true,
                           margin:'6px', draggable:true,nodeId:treeId,
                           storepath:storepath,labelAttribute:'caption'};
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
        var bc = pane._('BorderContainer');
        if (searchOn || editable){
            if(searchOn){
                var top = bc._('ContentPane',{region:'top'})._('Toolbar',{height:'18px'});
                top._('SearchBox',objectUpdate({searchOn:searchOn,nodeId:treeId+'_searchbox',datapath:'.searchbox'},objectExtract(kw,'searchOn_*')));
            }if(editable){
                var bottom = bc._('ContentPane',{'region':'bottom',height:'30%',
                                                 splitter:true}); 
                bottom._('BagNodeEditor',{nodeId:treeId+'_editbagbox',datapath:'.bagNodeEditor',bagpath:pane.getParentNode().absDatapath(storepath)});
            }    
        }
        pane = bc._('ContentPane',{region:'center'});
        var tree = pane._('tree',tree_kwargs);
        return pane;
    }
});
dojo.declare("gnr.widgets.PaletteBagNodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var nodeId = objectPop(kw,'nodeId');
        var pane = sourceNode._('PalettePane',kw);
        pane._('BagNodeEditor',{nodeId:nodeId,datapath:'.bagNodeEditor',bagpath:kw.bagpath});
        
        return pane;
        
    }
});

dojo.declare("gnr.widgets.BagNodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw){
        var gnrwdg = sourceNode.gnrwdg;
        var nodeId = objectPop(kw,'nodeId');
        var readOnly = objectPop(kw,'readOnly',false);
        var valuePath = objectPop(kw,'valuePath');
        var showBreadcrumb = objectPop(kw,'showBreadcrumb',true);
        var bc =sourceNode._('BorderContainer',{'nodeId':nodeId,detachable:true,_class:'bagNodeEditor'});
        if(showBreadcrumb){
            var top = bc._('ContentPane',{'region':'top',background_color:'navy',color:'white'});
            top._('span',{'innerHTML':'Path : '});
            top._('span',{'innerHTML':'^.currentEditPath'});
        }
        var box = bc._('ContentPane',{'region':'center',_class:'formgrid'});
        var gridId = nodeId+'_grid';
        var topic = nodeId+'_editnode';
        var bagpath= objectPop(kw,'bagpath');
        this.prepareStruct();
        gnrwdg.bagpath = bagpath;
        gnrwdg.valuePath = valuePath;
        gnrwdg.readOnly = readOnly ;
        dojo.subscribe(topic,this,function(item){gnrwdg.gnr.setCurrentNode(gnrwdg,item)});
        var grid = box._('includedview',{'storepath':'.data','structpath':'gnr._dev.bagNodeEditorStruct',
                                         'datamode':'bag','relativeWorkspace':true,'nodeId':gridId,
                                         autoWidth:false,'editorEnabled':true});
        if(!readOnly){
            var gridEditor = grid._('gridEditor');
            var cellattr = {'gridcell':'attr_value','autoWdg':true};
            cellattr.validate_onAccept = function(value,result,validations,rowIndex,userChange){
                var dataNode = this.grid.storebag().getParentNode().attr.dataNode;
                var attr_name = this.getRelativeData('.attr_name');
                if(attr_name=='*value'){
                    dataNode.setValue(value);
                }else{
                    var newattr = !('attr_name' in dataNode.attr);
                    dataNode.setAttribute(attr_name,value);
                    if(!value){
                        objectPop(dataNode.attr,attr_name);
                    }
                    if(newattr || !value)
                        setTimeout(function(){
                            genro.publish(topic,dataNode);
                        },300);
                }                    
            };
            gridEditor._('textbox',{gridcell:'attr_name'});
            gridEditor._('textbox',cellattr);
        }
        return box;
    },
    setCurrentNode:function(gnrwdg,item){
        var bagpath = gnrwdg.bagpath;
        var sourceNode = gnrwdg.sourceNode;
        if(typeof(item)=='string'){
            item = sourceNode.getRelativeData(bagpath).getNode(item);
        }
        var itempath = item.getFullpath(null,sourceNode.getRelativeData(bagpath));
        sourceNode.setRelativeData('.currentEditPath',itempath);
        gnrwdg.currentEditPath = itempath;
        var newstore = new gnr.GnrBag();
        for(var k in item.attr){
            var row = new gnr.GnrBag(); 
            row.setItem('attr_name',k,{_editable:false});
            row.setItem('attr_value',item.attr[k]);
            newstore.setItem('#id',row);
        }
        var itemvalue=item.getValue('static');
        
        if(gnrwdg.valuePath){
            sourceNode.setRelativeData(gnrwdg.valuePath,itemvalue);
        }else{
            var editable = true;
            row = new gnr.GnrBag();
            row.setItem('attr_name','*value',{_editable:false});
            if(itemvalue instanceof gnr.GnrBag){
                var editable = false;
                itemvalue = '*bag*';
            }
            row.setItem('attr_value',itemvalue,{_editable:editable});
            newstore.setItem('#id',row);
        }
        
        newstore.sort('attr_name');
        //newstore.forEach(function(n){if(n.label.indexOf('~~')==0){n.label=n.label.slice(2);}});
        if(!gnrwdg.readOnly){
            newstore.setItem('#id',new gnr.GnrBag({'attr_name':null,'attr_value':null}));
        }
        sourceNode.setRelativeData('.data',newstore,{'dataNode':item});
    },
    prepareStruct:function(){
        if(genro.getData('gnr._dev.bagNodeEditorStruct')){return;}
        var rowstruct =new gnr.GnrBag();
        rowstruct.setItem('cell_0',null,{field:'attr_name',name:'Name',width:'30%',
                                         cellStyles:'background:gray;color:white;border-bottom:1px solid white;'});
        rowstruct.setItem('cell_1',null,{field:'attr_value',name:'Value',width:'70%',
                                        cellStyles:'border-bottom:1px solid lightgray;'});
        genro.setData('gnr._dev.bagNodeEditorStruct.view_0.row_0',rowstruct);
    }
});

dojo.declare("gnr.widgets.SearchBox", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode,attributes){
        //var topic = attributes.nodeId+'_keyUp';
        var delay = 'delay' in attributes? objectPop(attributes,'delay'): 100;
        attributes.onKeyUp = function(e){
            var sourceNode = e.target.sourceNode;
            if(sourceNode._onKeyUpCb){
                clearTimeout(sourceNode._onKeyUpCb);
            }
            var v = e.target.value;
            sourceNode._onKeyUpCb = setTimeout(function(){
               //console.log(sourceNode);
               //console.log(sourceNode.absDatapath())
                sourceNode.setRelativeData('.currentValue',v);
                //genro.publish(topic,v,sourceNode.getRelativeData('.field'));
                },delay);
        };
        return attributes;
    },
    defaultDatapath:function(attributes){
        return '.searchbox';
    },
    createContent:function(sourceNode, kw) {
        var searchOn = objectPop(kw,'searchOn');
        var searchDtypes;
        if(searchOn[0]=='*'){
            searchDtypes = searchOn.slice(1);
            searchOn=true;
        }
        var nodeId = objectPop(kw,'nodeId');
        var menubag;
        var databag = new gnr.GnrBag();
        var defaultLabel = objectPop(kw,'searchLabel') || 'Search';
        databag.setItem('menu_dtypes',searchDtypes);
        databag.setItem('caption',defaultLabel);
        this._prepareSearchBoxMenu(searchOn,databag);
        sourceNode.setRelativeData(null,databag);
        var searchbox = sourceNode._('div',{nodeId:nodeId});
        sourceNode._('dataController',{'script':'genro.publish(searchBoxId+"_changedValue",currentValue,field)',
                                       'searchBoxId':nodeId,currentValue:'^.currentValue',field:'^.field'});
        var searchlbl = searchbox._('div',{'float':'left', margin_top:'2px'});
        searchlbl._('span',{'innerHTML':'^.caption',_class:'buttonIcon'});
        searchlbl._('menu',{'modifiers':'*',_class:'smallmenu',storepath:'.menubag',
                            selected_col:'.field',selected_caption:'.caption'});
        
        searchbox._('input',{'value':'^.value',_class:'searchInput',
                      connect_onkeyup:kw.onKeyUp,
                      width:kw.width});
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
        var defaultLabel = menubag.getItem('#0?caption');
        if(defaultLabel){
            databag.setItem('caption',defaultLabel);
        }
        databag.setItem('menubag',menubag);
        databag.setItem('value','');
    }
    
});


dojo.declare("gnr.widgets.PaletteGroup", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var groupCode = objectPop(kw, 'groupCode');
        var palette_kwargs = objectExtract(kw,'title,dockTo,top,left,right,bottom');
        palette_kwargs['nodeId'] = palette_kwargs['nodeId'] || groupCode+'_floating';
        palette_kwargs.selfsubscribe_showing = function(){
            genro.publish('palette_'+this.getRelativeData('gnr.palettes._groups.pagename.'+groupCode)+'_showing'); //gnr.palettes?gruppopiero=palettemario
        }
        palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + groupCode;
        var floating = sourceNode._('palette', palette_kwargs);
        var tab_kwargs = objectUpdate(kw,{selectedPage:'^gnr.palettes._groups.pagename.' + groupCode,groupCode:groupCode,_class:'smallTabs'});
        var tc = floating._('tabContainer', tab_kwargs);
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
            console.log(node.getValue());
            env[node.label]=eval(node.getValue());
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
        var storepath = sourceNode.attr.storepath;
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