/*
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_widget : Genro ajax widgets module
 * Copyright (c) : 2004 - 2007 Softwell sas - Milano
 * Written by    : Giovanni Porcari, Francesco Cavazzana
 *                 Saverio Porcari, Francesco Porcari
 *--------------------------------------------------------------------------
 *This library is free software; you can redistribute it and/or
 *modify it under the terms of the GNU Lesser General Public
 *License as published by the Free Software Foundation; either
 *version 2.1 of the License, or (at your option) any later version.

 *This library is distributed in the hope that it will be useful,
 *but WITHOUT ANY WARRANTY; without even the implied warranty of
 *MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 *Lesser General Public License for more details.

 *You should have received a copy of the GNU Lesser General Public
 *License along with this library; if not, write to the Free Software
 *Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */

//######################## genro grid #########################

gnr.getGridColumns = function(storeNode) {
    var storeNodeId,destFullpath;
    if(typeof(storeNode)=='string'){
        destFullpath=storeNode;
        //console.warn('*DEPRECATION* gnr.getGridColumns with storeNode as string')
        //usa i resolver js sulle selection (esempio i template risolti lato client)
    }else{
        storeNodeId=storeNode.attr.nodeId;
    }
    var columns= {};
    var storeCode;
    genro.src._main.walk(function(n){
        if(n.widget && n.widget.selectionKeeper){
            storeCode = n.attr.store || n.attr.nodeId;
            if((storeCode+'_store'==storeNodeId)||(destFullpath == n.widget.absStorepath())){
                //n.widget.selectionKeeper('save');
                var cols = n.widget.query_columns.split(',');
                dojo.forEach(cols,function(c){
                    columns[c] = c;
                });
            }
        }
        
    },'static');
    var result = objectKeys(columns).join(',');
    if(storeNodeId){
        storeNode._previousColumns = storeNode._currentColumns;
        storeNode._currentColumns=result;
    }
    return result;
};
gnr.columnsFromStruct = function(struct, columns) {
    if (isNullOrBlank(columns)) {
        columns = [];
    }
    if (!struct) {
        return '';
    }
    var nodes = struct.getNodes();
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        var fld = node.attr.queryfield || node.attr.field;
        if(node.attr.group_aggr){
            fld = fld+'_'+node.attr.group_aggr.toLowerCase().replace(/\W/g, '_');
        }
        if(node.attr.template_columns){
            node.attr.template_columns.split(',').forEach(function(n){
                arrayPushNoDup(columns,(n[0]=='$' || n[0]=='@')?n:'$'+n);
            });
        }
        if (node.attr.rowTemplate || node.attr.calculated || (fld && fld.indexOf(':')>=0)) {
            continue;
        }
        if (fld) {
            if(node.attr.caption_field){
                var caption_field = node.attr.caption_field;
                caption_field = (stringStartsWith(caption_field, '$') || stringStartsWith(caption_field, '@'))?caption_field:'$'+caption_field;
                arrayPushNoDup(columns,caption_field);
            }
            if(node.attr['_joiner_storename']){
                //_extname considerare
                arrayPushNoDup(columns,node.attr['_external_name']);
                arrayPushNoDup(columns,node.attr['_external_fkey']);
                arrayPushNoDup(columns,node.attr['_joiner_storename']+' AS _external_store');
            }
            if(node.attr._subtable){
                fld = '*'+fld;
            }
            if ((!stringStartsWith(fld, '$')) && (!stringStartsWith(fld, '@')) &&  (!stringStartsWith(fld, '*'))) {
                fld = '$' + fld;
            }
            arrayPushNoDup(columns, fld);
            if (node.attr.zoom_pkey) {
                var zoom_pkey = node.attr.zoom_pkey;
                if ((!stringStartsWith(zoom_pkey, '$')) && (!stringStartsWith(zoom_pkey, '@'))) {
                    zoom_pkey = '$' + zoom_pkey;
                }
                arrayPushNoDup(columns, zoom_pkey);
            }
        }

        if (node.getValue() instanceof gnr.GnrBag) {
            gnr.columnsFromStruct(node.getValue(), columns);
        }
    }
    return columns.join(',');
};

// ********* Grid ************
dojo.declare("gnr.widgets.DojoGrid", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'DojoGrid';
        if (dojo_version == '1.1') {
            if (!dojox.grid) {
                dojo.require('dojox.grid._grid.builder');
            }
            if (!dojox.grid.Builder.prototype._gnrpatch) {
                dojox.grid.Builder.prototype._gnrpatch = true;
                dojox.grid.Builder.prototype.findCellTarget = function(inSourceNode, inTopNode) {
                    var n = inSourceNode;
                    try {
                        while (n && (!this.isCellNode(n) || (dojox.grid.gridViewTag in n.offsetParent.parentNode && n.offsetParent.parentNode[dojox.grid.gridViewTag] != this.view.id)) && (n != inTopNode)) {
                            n = n.parentNode;
                        }
                        return n != inTopNode ? n : null;
                    } catch(e) {
                        return;
                    }
                };
            }
        }
    },
    patch__textSizeChanged:function(){
        if(dojo.getComputedStyle(this.domNode)){
            //if is inside hidden iframe this method must not be called
            this._textSizeChanged_replaced();
        }
    },
    
    mixin_setStructpath:function(val, kw) {
        kw = kw || {};
        this.structBag = genro.getData(this.sourceNode.attrDatapath('structpath')) || new gnr.GnrBag();
        this.cellmap = {};
        try {
            this.setStructure(this.gnr.structFromBag(this.sourceNode, this.structBag, this.cellmap));
            this.onSetStructpath(this.structBag,kw);
            this.sourceNode.publish('onSetStructpath');
        } catch (error) {
            console.error('error in structure',error);
        }
        
    },

    mixin_getColumnInfo:function(cell){
        var result = new gnr.GnrBag();
        if(!this.views.views[0]){
            return result; // empty structure
        }
        var headerList = dojo.query('th',this.viewsHeaderNode);

        var structureList = this.views.views[0].structure.rows[0];
        var hiddenBetween = 0;
        var headerNode,isHidden,rel_index;
        structureList.forEach(function(n){
            headerNode = headerList[n.index];
            isHidden = !genro.dom.isVisible(headerNode);
            rel_index = n.index;
            if(isHidden){
                hiddenBetween+=1;
                rel_index = -1;
            }else{
                rel_index-=hiddenBetween;
            }
            result.setItem(n.field,null,{cell:n,headerNode:headerNode,isHidden:isHidden,rel_index:rel_index});
        });
        return cell?result.getAttr(cell):result;
    },

    onBuilding:function(sourceNode){
        sourceNode.attr.scaleX = sourceNode.attr.scaleX || '^.scaleX';
        sourceNode.attr.scaleY = sourceNode.attr.scaleY || '^.scaleY';
        if(sourceNode._wrapperNode){
            return;
        }
        var extendedLayout = objectPop(sourceNode.attr,'_extendedLayout');

        if(extendedLayout){
            var content = sourceNode._value;
            var footers = new gnr.GnrBag();
            var node;
            content.digest('#k,#a.tag').forEach(function(n){
                if(n[1]=='footer'){
                    node = content.popNode(n[0]);
                    footers.addItem(node.label,node._value,node.attr);
                }
            });
            var structInfo = sourceNode.getRelativeData(sourceNode.absDatapath(sourceNode.attr.structpath)+'.info') || new gnr.GnrBag();
            var columnsets = structInfo.getItem('columnsets');
            var autoFooter = objectPop(sourceNode.attr,'footer');
            var autoColumnset = objectExtract(sourceNode.attr,'columnset_*');
            if(objectNotEmpty(autoColumnset) && !columnsets){
                columnsets = new gnr.GnrBag();
                //console.log('columnset_ syntax is deprecated. Define your columnsets inside the struct',autoColumnset);
                for(var k in autoColumnset){
                    var cl = k.split('_');
                    var cn = columnsets.getNode(cl[0],null,true);
                    cn.attr[cl[1] || 'name'] = autoColumnset[k];
                }
                sourceNode.setRelativeData(sourceNode.absDatapath(sourceNode.attr.structpath)+'.info.columnsets',columnsets,null,false);
            }
            var gridattr = objectUpdate({},sourceNode.attr);
            var _columnsetsNode,_footersNode;
            var containerAttr = objectExtract(gridattr,'region,pageName,title,margin,height,width');
            containerAttr.tag = 'BorderContainer';
            sourceNode.attr = containerAttr;
            sourceNode.label = 'grid_wrapper';
            sourceNode.setValue(new gnr.GnrDomSource(),false);
            var top = sourceNode._('ContentPane','columnsets',{region:'top',
                                    datapath:gridattr.datapath,hidden:true},{'doTrigger':false});
            _columnsetsNode = top.getParentNode();
            top._('div','scrollbox',{_class:'gr_columnset gr_scrollbox'},{'doTrigger':false});
            var bottom = sourceNode._('ContentPane','footers',{region:'bottom',datapath:gridattr.datapath,hidden:true},{'doTrigger':false});
            _footersNode = bottom.getParentNode();
            bottom._('div','scrollbox',{_class:'gr_footer gr_scrollbox'},{'doTrigger':false});
            gridattr.fillDown = gridattr.fillDown===false?false: true;
            var center = sourceNode._('ContentPane','gridpane',{region:'center'},{'doTrigger':false});
            var gridNode = center.setItem('grid',content,gridattr,{'doTrigger':false});
            gridNode._columnsetsNode =_columnsetsNode;
            gridNode._footersNode = _footersNode;
            gridNode._footers = footers;
            gridNode._autoFooter = autoFooter;
            gridNode._wrapperNode = sourceNode;

        }
    },

    mixin_catch_columnset:function(value,kw,attr){
        this.updateColumnsetsAndFooters();
    },

    mixin_columnsetsAndFooters_size:function(){
        
        var headerList = dojo.query('th',this.viewsHeaderNode);
        var headerTable = dojo.query('table',this.viewsHeaderNode)[0];
        var totalWidth =headerTable? headerTable.clientWidth:0;
        var cb = function(container){
            if(!container){
                return;
            }
            container.updAttributes({width:(totalWidth+2+'px')});
            var tr = container.getValue().getItem('#0.#0.#0');
            var idx = 0;
            tr.forEach(function(n){
                var c = headerList[n.attr.idx];
                var width = c.clientWidth+'px';
                n.updAttributes({width:width});
                idx++;
            });
        };
        var columnsets = this.structBag.getItem('info.columnsets');
        var showColumnset = columnsets && columnsets.len()>0;
        if(this.sourceNode._columnsetsNode){
            this.sourceNode._wrapperNode.widget.setRegionVisible('top',showColumnset);
            cb(this.sourceNode._columnsetsNode.getValue().getNode('scrollbox.itemcontainer'));
        }
        if(this.sourceNode._footersNode){
            var showFooter = true;
            if(this.sourceNode._footers.len()==1 && this.sourceNode._footers.getItem('#0').len()==0){
                showFooter = false;
            }
            genro.dom.setClass(this.sourceNode._footersNode,'gr_noFooter',!showFooter);
            this.sourceNode._wrapperNode.widget.setRegionVisible('bottom',showFooter || showColumnset);
            genro.dom.setClass(this.sourceNode._wrapperNode,'gr_wrap_footers',showFooter || showColumnset);
            cb(this.sourceNode._footersNode.getValue().getNode('scrollbox.itemcontainer'));
        }
    },

    mixin__columnsetsAndFooters_one:function(parent,source,colinfo,autoTitle){
        var scrollbox = parent._value.getNode('scrollbox');
        var tbl = scrollbox._('div','itemcontainer',{_class:'gr_itemcontainer'})._('table','tableNode',{_class:'gr_table selectable'});
        var tbody = tbl._('tbody',{});
        var headerList = dojo.query('th',this.viewsHeaderNode); //.filter(function(n){return genro.dom.isVisible(n);});
        var totCols = 0;
        var h = tbody._('tr','fakeHeader',{height:'0'});
        var idx = 0;
        headerList.forEach(function(th){
            if(genro.dom.isVisible(th)){
                h._('th',{idx:idx,'border_right':'1px solid transparent'});
                totCols++;
            }
            idx++;
        });
        var that = this;
        source.forEach(function(n){
            that._columnsetsAndFooters_row(tbody,n,colinfo,totCols,n.label=='footer_auto'?autoTitle:null);
        });
    },

    mixin__columnsetsAndFooters_row:function(pane,dataNode,colinfo,totCols,autoTitle){
        var data = dataNode.getValue();
        if(!data || data.len()===0){
            return;
        }
        var rowattr = objectUpdate({},dataNode.attr);
        objectPop(rowattr,'tag');
        rowattr._class = 'columnsets_footers_row';
        var sourceNode = this.sourceNode;
        var rootsrc = genro.src.newRoot();
        var tr = rootsrc._('tr',rowattr);
        var currIdx = 0;
        var sum_columns;
        if(this.collectionStore()){
            sum_columns = this.collectionStore().storeNode.getRelativeData('.sum_columns_source');
        }
        var itemlist = [];
        data.forEach(function(n){
            var item = objectUpdate({},n.attr);
            objectPop(item,'tag');
            var infopars = colinfo.getAttr(item.field);

           //if(!infopars){
           //    return;
           //}
            
            var cell = infopars.cell;
            item.idx = infopars.rel_index;
            var value = objectPop(item,'value');
            if(item.footerCell && !value){
                if(cell.totalize){
                    value = '^'+cell.totalize;
                    item._totalized_value = value;
                    item._filtered_totalized_value = '^.filtered_totalize.'+cell.field;
                    item.text_align = 'right';
                    item.innerHTML = '==_filtered_totalized_value!==null?_filtered_totalized_value:_totalized_value';
                }else if(sum_columns && sum_columns.getItem(cell.field)){
                    //nothing
                }else{
                    value = '&nbsp;';
                }
            }else{
                item.innerHTML = value;
            }
            itemlist.push(item);
        });
        itemlist.sort(function(a,b){return a.idx-b.idx;});
        itemlist.forEach(function(item){
            //console.log('beta',item.field,item.idx,currIdx);
            var colspan;
            var idx = objectPop(item,'idx');
            if(idx!=currIdx){
                colspan = idx-currIdx;
                tr._('td',{colspan:colspan,idx:currIdx})._('div',{innerHTML:autoTitle || '&nbsp;',text_align:'right'});
                autoTitle = null;
            }
            colspan = objectPop(item,'colspan') || 1;
            currIdx = idx+colspan;
            item._class = (item._class) || '' +' groupcontent';
            item.selfsubscribe_clickAndHold = function(kw){
                console.log('clickAndHold',this,kw);
                if(sourceNode.attr.configurable){
                    //inside cellHeader
                    sourceNode.widget.configuratorColsetTooltip(this.attr,kw.event);
                }
            };
            tr._('td',item.field,{idx:idx,colspan:colspan})._('div',item);
        });
        if(currIdx<totCols){
            tr._('td',{colspan:totCols-currIdx,idx:currIdx})._('div',{innerHTML:'&nbsp;',width:'100%'});
        }
        var n = rootsrc.popNode('#0');
        return pane.addItem(n.label,n._value,n.attr);
    },


    mixin_columnsetsAndFooters_autodata:function(){
        var colinfo = this.getColumnInfo();
        var autoRow = new gnr.GnrBag();
        var row_kw =  this.sourceNode.evaluateOnNode(objectExtract(this.sourceNode.attr,'footer_*',true));
        colinfo.forEach(function(n){
            if(n.attr.isHidden){
                return;
            }
            var cell = n.attr.cell;
            var footer_kw = objectExtract(cell,'footer_*',true);
            if(cell.totalize || objectNotEmpty(footer_kw)){
                footer_kw.footerCell = true;
                footer_kw.idx = cell.index;
                footer_kw.field = cell.field;
                footer_kw.dtype = cell.dtype;
                if(cell._formats){
                    footer_kw.format =footer_kw.format || cell._formats.format || cell._formats.pattern;
                }
                footer_kw.format = footer_kw.format || row_kw.format;
                autoRow.setItem(cell.field,null,footer_kw);
            }
        });
        this.sourceNode._footers.setItem('footer_auto',autoRow,row_kw,{_position:0});
        var columnsets = this.structBag.getItem('info.columnsets');
        if(columnsets){
            var sn = this.sourceNode;
            var columnset_groups =  {};
            columnsets.forEach(function(n){
                columnset_groups[n.label] =  objectUpdate({},n.attr);
                columnset_groups[n.label].value = objectPop(columnset_groups[n.label],'name');
            });
            var columnsetRow = new gnr.GnrBag();
            colinfo.forEach(function(n){
                var cell = n.attr.cell;
                if(!n.attr.isHidden && (cell.columnset && cell.columnset in columnset_groups)){
                    var columnset_kw = columnset_groups[cell.columnset];
                    var idx = n.attr.rel_index;
                    if((!('last_idx' in columnset_kw)) || (idx-columnset_kw.last_idx>1)){
                        columnset_kw.idx = idx;
                        columnset_kw.field = cell.field;
                        columnset_kw.colspan = 1;
                    }else{
                        columnset_kw.colspan += 1;
                    }
                    columnset_kw.last_idx = idx;
                    var cnode = columnsetRow.getNode(columnset_kw.field,null,true);
                    objectUpdate(cnode.attr,columnset_kw);
                }
            });
            this.sourceNode._columnsets = new gnr.GnrBag();
            this.sourceNode._columnsets.setItem('columnset_auto',columnsetRow);
        }else{
            this.sourceNode._columnsets = new gnr.GnrBag();
            this.sourceNode._columnsets.setItem('columnset_auto',new gnr.GnrBag());

        }
    },

    mixin_columnsetsAndFooters_make:function(){
        var that = this;
        var colinfo = this.getColumnInfo();
        var scrollbox;
        var sourceNode = this.sourceNode;
        if(sourceNode._columnsetsNode){
            this._columnsetsAndFooters_one(sourceNode._columnsetsNode,
                                          sourceNode._columnsets,colinfo);
        }
        if(sourceNode._footersNode){
            var autoTitle = sourceNode._autoFooter;
            autoTitle = autoTitle && typeof(autoTitle)=='string'?autoTitle:null;
            this._columnsetsAndFooters_one(sourceNode._footersNode,
                                            sourceNode._footers,
                                            colinfo,autoTitle);
            scrollbox = sourceNode._footersNode._value.getNode('scrollbox');
            genro.dom.setEventListener(scrollbox.domNode,'scroll',function(e){
                var sn = that.views.views[0].scrollboxNode;
                sn.scrollLeft = e.target.scrollLeft;
                if(sourceNode._columnsetsNode){
                    sourceNode._columnsetsNode._value.getNode('scrollbox').domNode.scrollLeft = e.target.scrollLeft;
                }
            });
        }else{
            genro.dom.setEventListener(sourceNode.widget.domNode,'scroll',function(e){
                if(e.target===that.views.views[0].scrollboxNode){
                    sourceNode._columnsetsNode._value.getNode('scrollbox').domNode.scrollLeft = e.target.scrollLeft;
                }
            },true);
        }
    },

    mixin_drawFiller:function(){
        if (!this.views.views[0]){
            return;
        }
        var sb = this.views.views[0].scrollboxNode;
        if(this.sourceNode._footersNode){
            sb.style.height = this.sourceNode.getParentNode().widget.domNode.clientHeight - this.viewsHeaderNode.clientHeight+1 +'px';
            //sb.style.height =sb.clientHeight+18+'px';
        }
        var delta = sb.clientHeight - sb.firstElementChild.clientHeight;
        var filler = dojo.query('.fillernode',sb)[0];
        if(delta<=0){
            if(filler){
                sb.removeChild(filler);
            }
            return;
        }
        if(!filler){
            filler = document.createElement('div');
            filler.setAttribute('class','fillernode');
            sb.appendChild(filler);
        }
        var vn = dojo.query('table',this.viewsHeaderNode)[0];
        if(!vn){
            return;
        }

        filler.style.height = delta+'px';
        var totalWidth = vn.clientWidth;
        var tdlist = [];
        var colinfo = this.getColumnInfo();
        var cellinfo;
        dojo.query('th',this.viewsHeaderNode).forEach(function(n,idx){
            if(!n.clientWidth){
                return; 
            }
            var style = "width:"+n.clientWidth+"px;";
            if(colinfo){
                cellinfo = colinfo.getAttr('#'+idx);
                if(cellinfo && cellinfo.cell && cellinfo.cell.cellStyles){
                    style+=cellinfo.cell.cellStyles;
                }
            }
            return tdlist.push('<td style="'+style+'"></td>');
        });
        filler.innerHTML = '<table class="grid_filler" style="width:'+totalWidth+'px;"><tbody><tr>'+tdlist.join('')+'</tr></tbody></table>';
    },

    mixin_setDraggable_row:function(draggable, view) {
        if(genro.isMobile){
            return;
        }
        view = view || this.views.views[0];
        draggable = draggable === false ? false : true;
        var builder = view.content;
        builder._table = builder._table.replace('<table draggable="true" ', '<table ');
        if (draggable) {
            builder._table = builder._table.replace('<table ', '<table draggable="true" ');
        }
        dojo.query('.dojoxGrid-row-table', this.domNode).forEach(function(n) {
            n.draggable = draggable;
        });
    },
    mixin_setDropTarget_row:function(value) {
        this.sourceNode.dropModes.row = value;
    },
    mixin_setDropTarget_column:function(value) {
        this.sourceNode.dropModes.column = value;
    },
    mixin_setDropTarget_cell:function(value) {
        this.sourceNode.dropModes.cell = value;
    },
    mixin_onSetStructpath: function(structure) {
        return;
    },
    mixin_openLinkedForm: function(e) {
        var idx = e.rowIndex;
        this.sourceNode.publish('editrow',{pkey:this.rowIdByIndex(idx)});
    },
    mixin_linkedFormLoad: function(e) {
        var idx = e.rowIndex;
        this.sourceNode.publish('editrow',{pkey:this.rowIdByIndex(idx)});
    },
    
    selfDragColumnsPrepare:function(sourceNode) {
        if (sourceNode.attr.selfDragColumns != 'trashable') {
            gnr.convertFuncAttribute(sourceNode, 'selfDragColumns', 'info');
        }
        sourceNode.attr.draggable_column = true;
        var onDropCall = function(dropInfo, col) {
            this.widget.moveColumn(col, dropInfo.column);
        };
        sourceNode.attr['onDrop_selfdragcolumn_' + sourceNode._id] = onDropCall;
        if(sourceNode.attr.configurable){
            var frameNode = genro.getFrameNode(sourceNode.attr.frameCode);
            sourceNode.registerSubscription('endDrag',sourceNode,function(){
                genro.dom.removeClass(sourceNode.attr.configuratorId || frameNode,'treeShowTrash');
            });
            sourceNode._showTrash=function(show){
                genro.dom.addClass(sourceNode.attr.configuratorId || frameNode,'treeShowTrash');
            };
            sourceNode.attr.onTrashed = sourceNode.attr.onTrashed || 'this.widget.deleteColumn(data);';
        }

    },

    selfDragRowsPrepare:function(sourceNode) {
        gnr.convertFuncAttribute(sourceNode, 'selfDragRows', 'info');
        gnr.convertFuncAttribute(sourceNode, 'onSelfDropRows', 'rows,dropInfo');
        gnr.convertFuncAttribute(sourceNode, 'afterSelfDropRows', 'rows,dropInfo');
        sourceNode.attr.draggable_row = true;
        var row_counter_changes;
        var onDropCall = function(dropInfo, rows) {
            if (!('row' in dropInfo ) || (dropInfo.row < 0)) {
                return;
            }
            if (sourceNode.attr.onSelfDropRows) {
                sourceNode.attr.onSelfDropRows(rows, dropInfo);
            }else if(sourceNode.form && sourceNode.form.isDisabled()){
                return;
            }else {
                dropInfo.widget.moveRow(rows, dropInfo.row);
                row_counter_changes = dropInfo.widget.updateCounterColumn();
            }
            if (sourceNode.attr.afterSelfDropRows) {
                sourceNode.attr.afterSelfDropRows(rows, dropInfo, row_counter_changes);
            }
        };
        sourceNode.attr['onDrop_selfdragrow_' + sourceNode._id] = onDropCall;
    },

    creating_common: function(attributes, sourceNode) {
        if(!sourceNode.attr.storepath){
            if(sourceNode.attr.store){
                var storeNode = genro.nodeById(sourceNode.attr.store+'_store');
                if(!storeNode){
                    console.log('missing storepath');
                }else{
                    sourceNode.attr.storepath = storeNode.absDatapath(storeNode.attr.storepath);//storeNode.absDatapath(storeNode.attr.path);
                    sourceNode._useStore=true;
                    if(storeNode.store && storeNode.store._linkedGrids){
                        genro.src.onBuiltCall(function(){
                            storeNode.store._linkedGrids.push(sourceNode.widget);
                        },1);
                    }
                }
            }
        }
        sourceNode.attr.nodeId = sourceNode.attr.nodeId || 'grid_' + sourceNode.getStringId();
        if(sourceNode.attr.controllerPath && sourceNode.attr.controllerPath!=true){
            sourceNode.gridControllerPath = sourceNode.attr.controllerPath;
        }
        else{
            var relativeWorkspace= sourceNode.attr.controllerPath || sourceNode.attr.relativeWorkspace;
            sourceNode.gridControllerPath = relativeWorkspace ? sourceNode.absDatapath() : 'grids.' + sourceNode.attr.nodeId;
        }
        
        if (sourceNode.attr.selfDragRows) {
            this.selfDragRowsPrepare(sourceNode);
        }
        if (sourceNode.attr.selfDragColumns || (sourceNode.attr.configurable && sourceNode.attr.selfDragColumns!==false)) {
            this.selfDragColumnsPrepare(sourceNode);
        }
        objectExtract(attributes, 'selected*');
        var savedAttrs = {};        
        var identifier = attributes.identifier || '_pkey';
        attributes.datamode = attributes.datamode || 'attr';
        attributes.rowsPerPage = attributes.rowsPerPage || 10;
        attributes.rowCount = attributes.rowCount || 0;
        attributes.fastScroll = attributes.fastScroll || false;
        sourceNode.dropModes = objectExtract(sourceNode.attr, 'dropTarget_*', true);
        if (!sourceNode.dropTarget && objectNotEmpty(sourceNode.dropModes)) {
            sourceNode.dropTarget = true;
        }
        var attributesToKeep = '_class,pageName,autoHeight,autoRender,autoWidth,defaultHeight,elasticView,fastScroll,keepRows,model,rowCount,rowsPerPage,singleClickEdit,structure,'; //continue
        var styleDict=genro.dom.getStyleDict(attributes);
        if (styleDict.width=='auto'){
            delete styleDict.width;
            attributes.autoWidth=true;
        }
        if (styleDict.height=='auto'){
            delete styleDict.height;
            attributes.autoHeight=true;
        }
        attributes.style=objectAsStyle(styleDict);
        attributesToKeep = attributesToKeep + 'style,scaleX,scaleY,datamode,sortedBy,filterColumn,excludeCol,excludeListCb,editorEnabled,editorSaveMethod,autoInsert,autoDelete';
        var gridAttributes = objectExtract(attributes, attributesToKeep);
        objectPopAll(attributes);
        objectUpdate(attributes, gridAttributes);
        attributes._identifier = identifier;
        sourceNode.highlightExternalChanges = sourceNode.attr.highlightExternalChanges || true;
        if(sourceNode.attr.userSets){
            sourceNode.registerDynAttr('userSets');
            var userSets = new gnr.GnrBag();
            sourceNode.setRelativeData(sourceNode.attr.userSets,userSets);
            sourceNode._usersetgetter = function(cellname,row,idx){
                //var currSet = userSets.getItem(cellname);
                var currSet = sourceNode.getRelativeData(sourceNode.attr.userSets+'.'+cellname);
                var checkedField = this.widget.cellmap[cellname].checkedField;
                if(currSet){
                    return currSet.match(new RegExp('(^|,)'+row[checkedField]+'($|,)'))!==null;
                }else{
                    return false;
                }
            }
        }
        return savedAttrs;
    },

    creating_structure: function(attributes, sourceNode) {
        var structBag = sourceNode.getRelativeData(sourceNode.attr.structpath);
        if (structBag && genro.grid_configurator) {
            sourceNode.setRelativeData('.resource_structs.__baseview__',structBag.deepCopy(),{caption:_T('Base View')});
        }
        attributes.structBag = structBag; 
        sourceNode.registerDynAttr('structpath');
        attributes.cellmap = {};
        attributes.structure = this.structFromBag(sourceNode, attributes.structBag, attributes.cellmap);
    },
    mixin_onAddedView:function(view) {
        var draggable_row = this.sourceNode.getAttributeFromDatasource('draggable_row');
        if (draggable_row) {
            this.setDraggable_row(true, view);
        }
    },

    created_common:function(widget, savedAttrs, sourceNode) {
        var nodeId = sourceNode.attr.nodeId;
        var gridContent = sourceNode.getValue() || new gnr.GnrDomSource();
        if (genro.grid_configurator) {
            if(sourceNode.attr.configurable){
                genro.src.onBuiltCall(function(){
                    genro.grid_configurator.addGridConfigurator(sourceNode);
                    genro.grid_configurator.setFavoriteView(sourceNode.attr.nodeId);
                },1);
            }            
        }
        if(sourceNode._useStore){
            widget.setEditableColumns();
            widget.setChangeManager();
        }
        var gridEditorNode = gridContent.getNodeByAttr('tag', 'grideditor',true);
        if (gridEditorNode) {
            widget.gridEditor = new gnr.GridEditor(widget);
        }
        var menuNode = gridContent.getNodeByAttr('tag', 'menu',true);
        if(!menuNode && sourceNode.attr.gridplugins!==false){
            sourceNode.setRelativeData('.contextMenu',this.pluginContextMenuBag(sourceNode));
            sourceNode._('menu','contextMenu',{storepath:'.contextMenu',_class:'smallmenu'},{doTrigger:false});
            gridContent = sourceNode.getValue();
            menuNode = gridContent.getNode('contextMenu');
        }
        if(menuNode){
            widget.onCellContextMenu = function(e){
                menuNode.rowIndex = e.rowIndex;
                menuNode.cellIndex = e.cellIndex;
            };
        }
        if ('draggable_row' in sourceNode.attr) {
            dojo.connect(widget.views, 'addView', dojo.hitch(widget, 'onAddedView'));
            if (widget.views.views.length > 0) {
                var draggable_row = sourceNode.getAttributeFromDatasource('draggable_row');
                widget.setDraggable_row(draggable_row, widget.views.views[0]);
            }
        }
        if (sourceNode.attr.openFormEvent) {
            dojo.connect(widget, sourceNode.attr.openFormEvent, widget, 'openLinkedForm');
        }
        if (sourceNode.attr.loadFormEvent) {
            dojo.connect(widget, sourceNode.attr.loadFormEvent, widget, 'linkedFormLoad');
        }
        objectFuncReplace(widget.selection, 'clickSelectEvent', function(e) {
            if(sourceNode.attr.selectGroupColumns && ( e.shiftKey && (e.ctrlKey || e.metaKey) ) ){
                sourceNode.widget.groupColumnsSelect(e.rowIndex,sourceNode.attr.selectGroupColumns);
            }else{
                this.clickSelect(e.rowIndex, e.ctrlKey || e.metaKey, e.shiftKey);
            }
            
        });
        sourceNode.registerSubscription(nodeId + '_reload', widget, function(keep_selection) {
            this.reload(keep_selection !== false);
        });
        sourceNode.registerSubscription(nodeId + '_serverAction',widget,function(kw){
            if(this.serverAction){
                this.serverAction(kw);
            }
        });
        sourceNode.registerSubscription(nodeId + '_printRows',widget,function(kw){
            if(this.printRows){
                this.printRows(kw);
            }
        });
        sourceNode.subscribe('pluginCommand',function(kw){
            kw.grid = this.widget;
            genro.pluginCommand(kw);
        });
        sourceNode.subscribe('updatedSelectedRow',function(){
            var selectedIndex = this.widget.selection.selectedIndex;
            this.widget.sourceNode.setAttributeInDatasource('selectedId', this.widget.rowIdByIndex(selectedIndex), 
                                                                null, this.widget.rowByIndex(selectedIndex), true);
        });
        sourceNode.subscribe('configuratorPalette',function(){
            this.widget.configuratorPalette();
        });

        sourceNode.subscribe('clickAndHold',function(kw){
            var event = kw.event;
            if(this.attr.configurable){
                //inside cellHeader
                this.widget.configuratorCellTooltip(event);
            }
            
        });


        if(sourceNode.getRelativeData('.filterset')){
            widget.filterManager = new gnr.GridFilterManager(widget);
            sourceNode.attr.filterset = '.filterset';
            sourceNode.registerDynAttr('filterset');
        }
        //dojo.subscribe(gridId+'_searchbox_keyUp',this,function(v){console.log(v)});
        var searchBoxCode =(sourceNode.attr.frameCode || nodeId)+'_searchbox';
        var searchBoxNode = genro.nodeById(searchBoxCode);
        if (searchBoxNode){
            if(searchBoxNode.getRelativeData('.menu_auto')){
                _this = this;
                var cb = function(){
                    genro.publish(searchBoxCode+'_updmenu',
                                  _this._getFilterAutoValues(widget,searchBoxNode.getRelativeData('.menu_dtypes')));
                };
                dojo.connect(widget,'onSetStructpath',widget,cb);
                dojo.connect(widget,'newDataStore',function(){
                    searchBoxNode.setRelativeData('.currentValue','');
                    searchBoxNode.setRelativeData('.value','');
                });
                setTimeout(function(){cb.call(widget);},1);
            }
            sourceNode.registerSubscription(searchBoxCode+'_changedValue',widget,function(v,field){
                this.applyFilter(v,null,field);
                genro.dom.setClass(this.domNode,'filteredGrid',v);
                this.updateTotalsCount();
                
            });
            sourceNode.registerSubscription(searchBoxCode+'_stopSearch',widget,function(kw){
                kw.finalize();
            });
            sourceNode.subscribe('command',function(){
                widget[arguments[0]](arguments.slice(1));
            });
        }
        if (widget.sourceNode.attr.filteringGrid){
            widget.filteringMode = widget.sourceNode.currentFromDatasource(sourceNode.attr.filteringMode) || 'exclude';
            var filteringColumn = sourceNode.attr.filteringColumn.replace(/\./g, '_').replace(/@/g, '_');            
            var filteredColumn = filteringColumn;
            if(filteringColumn.indexOf(':')>=0){
                filteringColumn = filteringColumn.split(':');
                filteredColumn = filteringColumn[1];
                filteringColumn = filteringColumn[0];
            }
            var connectFilteringGrid=function(){
                var filteringGrid = widget.sourceNode.currentFromDatasource(widget.sourceNode.attr.filteringGrid);
                filteringGrid = filteringGrid.widget;
                if (filteringGrid.gridEditor){
                    dojo.connect(filteringGrid,'setStorepath',function(p,kw){
                        if(kw.node.label==filteredColumn || kw.evt=='ins' || kw.evt=='del' || kw.reason=='loadData'){
                            widget.filterToRebuild(true);
                            widget.updateRowCount('*');
                        }
                    });
                }else {
                    dojo.connect(filteringGrid,'newDataStore',function(){
                        widget.filterToRebuild(true);
                        widget.updateRowCount('*');
                    });
                }
                widget.excludeListCb=function(){
                    //widget.sourceNode.currentFromDatasource(widget.sourceNode.attr.filteringGrid);
                    return filteringGrid.getColumnValues(filteredColumn);
                };
                widget.excludeCol=filteringColumn;
            };
            genro.src.onBuiltCall(connectFilteringGrid);
        }
        if(sourceNode.attr.rowCustomClassesCb){
            widget.rowCustomClassesCb = funcCreate(sourceNode.attr.rowCustomClassesCb,'row');
        }
        if(sourceNode.attr.fillDown || sourceNode._wrapperNode){
            dojo.connect(widget,'postrender',function(){
                if(!sourceNode._columnsetAndFootersInitialized){
                    var widget = this;
                    sourceNode.delayedCall(function(){
                        widget.updateColumnsetsAndFooters();
                    },1,'updateColumnsetsAndFooters');
                }
                if(this.sourceNode.attr.fillDown){
                    this.drawFiller();
                }
            });

            dojo.connect(sourceNode.getParentNode().getParentNode().widget,'resize',function(){
                sourceNode._columnsetAndFootersInitialized = false;
            });
            if(sourceNode.attr.fillDown){
                dojo.connect(widget,'updateRowCount',function(){
                    var that = this;
                    setTimeout(function(){that.drawFiller();},1);
                });
            }
        }

        dojo.connect(widget,'onKeyEvent',function(e){
            if(e.type=='keydown' && !widget.gnrediting){
                var kt = keyName(e.keyCode);
                if(kt){
                    if((kt=='DOWN_ARROW')||(kt=='UP_ARROW')){
                        widget.moveSelectedRow((kt=='DOWN_ARROW'?1:-1),true);
                        e.preventDefault();
                    }
                }
            }
        });
        dojo.connect(sourceNode.widget,'setCellWidth',function(inIndex, inUnitWidth){
            this.structBag.getItem('view_0.rows_0').getNode('#'+inIndex).updAttributes({width:inUnitWidth});
            //this.structBag.getNodeByAttr('field',this.getCell(inIndex).original_field).updAttributes({width:inUnitWidth});
        });
        dojo.connect(widget,'onFocus',function(){
            this.changedFocus(true); 
            this.sourceNode.publish('onFocus',{});
        });
        dojo.connect(widget,'onBlur',function(){
            this.changedFocus(false); 
            this.sourceNode.publish('onBlur',{});
        });
        dojo.connect(widget,'onCellClick',function(evt){
            this.sourceNode.publish('onCellClick',{evt:evt,cellNode:evt.cellNode});
        });
        if(sourceNode.attr.autoInsert){
            dojo.connect(widget,'setStorepath',function(val,kw){
                if(kw.evt=='upd' && kw.reason!='autoRow' && kw.node.label==widget.masterEditColumn()){
                    if(!isNullOrBlank(kw.value) && isNullOrBlank(kw.oldvalue) && this.autoInsert){
                        this.autoInsertHandler();
                    }
                }
            });
        }
        var gridData = sourceNode.getRelativeData();
        gridData.setCallBackItem('menuColsConfigMenu',function(){
            var result = new gnr.GnrBag();
            var grid = sourceNode.widget;
            var cells = grid.getColumnInfo();
            cells.getNodes().forEach(function(n,idx){
                result.addItem(n.label,null,{caption:n.attr.cell.name,cell:n.attr.cell});
            });
            result.addItem('-',null,{caption:'-'});
            result.addItem('_newcol',null,{caption:_T('New formula cell'),cell:'newcell'});

            return result;
        });
        setTimeout(function(){widget.updateRowCount('*');},1);
    },

    cm_plugin_configurator:function(sourceNode,menu){
        menu.setItem('#id',null,{caption:_T('Configure grid'),action:"$2.widget.configuratorPalette();"});
    },

    cm_plugin_export_xls:function(sourceNode,menu){
        menu.setItem('#id',null,{caption:_T('Export XLS'),action:"$2.widget.serverAction({command:'export',allRows:true,opt:{export_mode:'xls',downloadAs:$2.attr.nodeId+'_export'}});"});
    },


   // cm_plugin_print:function(sourceNode,menu){
   //     menu.setItem('#id',null,{caption:_T('Print'),action:"$2.widget.serverAction({command:'print',allRows:true,opt:{rawData:true,downloadAs:$2.attr.nodeId+'_print',respath:'print/_common/print_gridres'}});"});
   // },

    cm_plugin_print:function(sourceNode,menu){
        menu.setItem('#id',null,{caption:_T('Print'),action:'$2.publish("printRows");'});
    },

    cm_plugin_chartjs:function(sourceNode,menu){
        menu.setItem('#id',
            genro.dev.userObjectMenuData({'objtype':'chartjs',
                  'flags':genro.getData('gnr.pagename')+'_'+sourceNode.attr.nodeId,
                    'table':sourceNode.attr.table},[{pkey:'__newchart__',caption:_T('New chart')}]),
            {caption:_T('Charts'),
            action:"$2.publish('pluginCommand',{plugin:'chartjs',command:'openGridChart',pkey:$1.pkey,caption:$1.caption});"});
        
    },
    cm_plugin_stats:function(sourceNode,menu){
        menu.setItem('#id',
            genro.dev.userObjectMenuData({'objtype':'stats',
                  'flags':genro.getData('gnr.pagename')+'_'+sourceNode.attr.nodeId,
                    'table':sourceNode.attr.table},[{pkey:'__newobj__',caption:_T('New stats')}]),
            {caption:_T('Stats'),
            action:"$2.publish('pluginCommand',{plugin:'statspane',command:'openGridStats',pkey:$1.pkey,caption:$1.caption});"});
    },

    pluginContextMenuBag:function(sourceNode){
        var gridplugins = sourceNode.attr.gridplugins;
        if(!gridplugins){
            gridplugins = 'chartjs,export_xls,print';
            if(sourceNode.attr.configurable && genro.grid_configurator){
                gridplugins = 'configurator,'+gridplugins;
            }
        }
        var contextMenuBag = sourceNode.getRelativeData('.contextMenu') || new gnr.GnrBag();
        gridplugins = gridplugins?gridplugins.split(','):[];
        var that = this;
        if(gridplugins){
            contextMenuBag.setItem('r_'+contextMenuBag.len(),null,{caption:'-'});
            gridplugins.forEach(function(cm_plugin){
                that['cm_plugin_'+cm_plugin](sourceNode,contextMenuBag);
            });
        }
        contextMenuBag.setItem('r_'+contextMenuBag.len(),null,{caption:_T('Toggle line number'),
                                checked:'^'+sourceNode.attr.structpath+'.info.showLineNumber',
                                action:function(line,gridNode){gridNode.widget.toggleLineNumberColumn()}})
        return contextMenuBag;
    },

    mixin_printRows:function(){
        var kw = {res_type:'print',table:this.sourceNode.attr.table,
                    resource:'_common/print_gridres',
                    gridId:this.sourceNode.attr.nodeId};
        objectUpdate(kw,this.currentSelectionPars());
        if(kw.selectedPkeys){
            kw.allSelectionPkeys = this.getAllPkeys();
        }
        genro.publish('table_script_run',kw);
    },

    mixin_setAutoInsert:function(autoInsert){
        this.autoInsert = autoInsert;
    },

    mixin_setAutoDelete:function(autoDelete){
        this.autoDelete = autoDelete;
    },

    mixin_setFilteringMode:function(filteringMode){
        this.filteringMode = filteringMode || 'exclude' ;
        this.filterToRebuild(true);
        this.updateRowCount();
    },

    mixin_changedFocus:function(focus){
        genro.dom.setClass(this.domNode,'focusedGrid',focus);
        this.sourceNode.setRelativeData('.focused',focus);
        this.isFocused = focus;
        if(this.autoInsert){
            var that = this;
            var wastabbed = genro._lastKeyDown?genro._lastKeyDown.code=='Tab':false;
            var slen = that.storebag().len();
            setTimeout(function(){
                var insertedNode = that.autoInsertHandler();
                if(insertedNode){
                    that.domNode.focus();//because lost focus after insert
                }
                if(wastabbed || slen==0){
                    that.editBagRow(genro._lastKeyDown && genro._lastKeyDown.shiftKey?-1:0);
                }
            },1);
            
        }
    },

    mixin_autoInsertHandler:function(){},

    mixin_rowBagNodeByIdentifier:function(identifier){
        return this.storebag().getNodeByAttr(this.rowIdentifier(),pkey);
    },

    mixin_updateTotalsCount: function(countBoxNode){
        var countBoxCode =(this.sourceNode.attr.frameCode || this.sourceNode.attr.nodeId)+'_countbox';
        countBoxNode = genro.nodeById(countBoxCode);
        if (countBoxNode){
            var shown =this.storeRowCount();
            var total = this.storeRowCount(true);
            genro.dom.setClass(countBoxNode,'unfilteredCount',shown==total);
            genro.dom.setClass(countBoxNode,'countBoxVisible',total>=0);
            countBoxNode.setRelativeData('.shown', shown);
            countBoxNode.setRelativeData('.total', total);
        }
    },
    
    _getFilterAutoValues: function(widget,dtypes){
        //console.log(widget);
        var structbag = widget.structbag();
        var values = [];
        var auto = [];
        values.push(null);
        var struct = widget.structbag();
        var cellsbag = struct && struct.getItem('#0.#0')?struct.getItem('#0.#0'): new gnr.GnrBag();
        var caption,cellattr,cell_cap,cell_field,fltList,colList,col;
        var cellmap = widget.cellmap;
        var cellobj;
        var fld;
        cellsbag.forEach(function(n){
            cellattr = n.attr;
            
            cell_cap = cellattr.name || cellattr.field;
            cell_field = n.attr.field.replace(/\W/g, '_');
            if(n.attr.group_aggr){
                cell_field += '_'+ n.attr.group_aggr.toLowerCase().replace(/\W/g, '_');
            }
            cellobj = cellmap[cell_field];
            if(cellobj.classes && cellobj.classes.indexOf('hiddenColumn')>=0){
                return;
            }
            cell_field = cellobj.field_getter;
            if (!dtypes || (dtypes.indexOf(cellattr.dtype) >=0)){
                values.push(cell_cap+':'+cell_field);
                auto.push(cell_field);
            }
        });
        values[0]='Auto:'+auto.join('+');
        return values.join(',');
    },
    created: function(widget, savedAttrs, sourceNode) {
        this.created_common(widget, savedAttrs, sourceNode);
        dojo.connect(widget, 'onSelected', widget, '_gnrUpdateSelect');
        genro.src.onBuiltCall(dojo.hitch(widget, 'render'));
        dojo.connect(widget, 'modelAllChange', dojo.hitch(sourceNode, this.modelAllChange));


    },

    modelAllChange:function() {
        if (this.attr.rowcount) {
            this.setRelativeData(this.attr.rowcount, this.widget.rowCount);
        }
        //this.widget._gnrUpdateSelect();
    },
    mixin_columnNodelist:function(idx, includeHeader) {
        var condition = 'td.dojoxGrid-cell[idx="' + idx + '"]';
        if (includeHeader) {
            condition = 'td.dojoxGrid-cell[idx="' + idx + '"], th.dojoxGrid-cell[idx="' + idx + '"]';
        }
        return dojo.query(condition, this.domNode);
    },
    mixin_rowIdByIndex: function(idx) {
        if (idx !== null) {
            return this.rowIdentity(this.rowByIndex(idx));
        }
    },
    mixin_rowByIndex: function(idx) {
        return this.model.getRow(idx);
    },
    mixin_rowIdentity: function(row) {
        if (row) {
            return row[this.rowIdentifier()];
        } else {
            return null;
        }
    },
    mixin_rowIdentifier: function(row) {
        return this.model.store._identifier;
    },
    mixin_rowItemByIndex: function(idx) {
        identifier = this.rowIdentity(this.rowByIndex(idx));
        return this.model.store.fetchItemByIdentity({identity:identifier});
    },
    mixin_rowItemByIdentity: function(identifier) {
        return this.model.store.fetchItemByIdentity({identity:identifier});
    },
    mixin_moveSelectedRow:function(delta,cycle){
        var row = (this.selection.selectedIndex || 0)+delta;
        var rowMax = this.rowCount-1;
        if ((row>rowMax) || (row<0)){
            if (cycle){
                row = row>rowMax?0:rowMax;
                this.selection.select(row);
                this.scrollToRow(row);
            }
        }else{
            if(row>(this.scroller.lastVisibleRow)){
                 this.scrollToRow(row);
                 //console.log('row >last',row,this.scroller.lastVisibleRow,this.scroller.firstVisibleRow);
            }else if(row<this.scroller.firstVisibleRow){
                this.scrollToRow(row);
                //console.log('row <first',row,this.scroller.firstVisibleRow);
            }
            this.selection.select(row);
        }
    },

    mixin__gnrUpdateSelect: function(idx) {
        if (this.sourceNode.attr.selectedDataPath) {
            var selectedDataPath = null;
            if (idx >= 0) {
                selectedDataPath = this.dataNodeByIndex(idx).getFullpath(null, true);
            }
            this.sourceNode.setAttributeInDatasource('selectedDataPath', selectedDataPath);
        }
        if (this.sourceNode.attr.selectedLabel) {
            var selectedLabel = null;
            if (idx >= 0) {
                var datanode = this.dataNodeByIndex(idx);
                selectedLabel = datanode ? this.dataNodeByIndex(idx).label : null;
            }
            this.sourceNode.setAttributeInDatasource('selectedLabel', selectedLabel);
        }
        var selattr = objectExtract(this.sourceNode.attr, 'selected_*', true);
        var selectedPkeys = this.getSelectedPkeys();
        var row = {};
        var selectedId = null;
        if(idx>=0){
            row = this.rowByIndex(idx);
            selectedId = this.rowIdentity(row);
        }
        for (var sel in selattr) {
            this.sourceNode.setRelativeData(selattr[sel], row[sel]);
        }
        if (this.sourceNode.attr.selectedIndex) {
            this.sourceNode.setAttributeInDatasource('selectedIndex', ((idx < 0) ? null : idx));
        }
        if (this.sourceNode.attr.selectedPkeys) {
            this.sourceNode.setAttributeInDatasource('selectedPkeys', selectedPkeys);
        }
        if (this.sourceNode.attr.selectedRowidx) {
            this.sourceNode.setAttributeInDatasource('selectedRowidx', this.getSelectedRowidx().join(','));
        }
        if (this.sourceNode.attr.selectedNodes) {
            var nodes = this.getSelectedNodes();
            var selNodes;
            if (nodes) {
                selNodes = new gnr.GnrBag();
                dojo.forEach(nodes,
                    function(node) {
                        selNodes.setItem(node.label, null, node.getAttr());
                    }
                );
            }
            genro.setData(this.sourceNode.attrDatapath('selectedNodes'), 
                            selNodes, {'count':selNodes.len()});
        }
        if(this.sourceNode.attr.selectedId) {
            this.sourceNode.setAttributeInDatasource('selectedId', selectedId, null, row, true);
        }
        if(this.sourceNode.attr.selectedRowData){
            var rowDataBag = new gnr.GnrBag(row);
            rowDataBag.popNode('_pkey');
            this.sourceNode.setAttributeInDatasource('selectedRowData', rowDataBag);
        }
        this.sourceNode.setRelativeData('.currentSelectedPkeys',selectedPkeys);
        this.sourceNode.publish('onSelectedRow',{'idx':idx,'selectedId':selectedId,
                                                'grid':this,'selectedPkeys':selectedPkeys});
    },

    mixin_indexByRowAttr:function(attrName, attrValue, op,backward) {
        op = op || '==';
        var that = this;
        var cmp = genro.compareDict[op];
        var cb = function(row){
            return cmp.call(that, row[attrName], attrValue);
        };
        var result = this.indexByCb(cb,backward);
        return result;
    },

    mixin_indexByCb:function(cb, backward) {
        var n = this.rowCount;
        for (var i = 0; i < n; i++) {
            var k_i = backward?n-i:i;
            if (cb(this.rowByIndex(k_i))) {
                return k_i;
            }
        }
        return -1;
    },

    mixin_hasRow:function(attr, value) {
        if (typeof(attr) == 'function') {
            cb = attr;
        } else {
            cb = function(n) {
                return n[attr] == value;
            };
        }
        return this.indexByCb(cb) >= 0;
    },
    mixin_selectByRowAttr:function(attrName, attrValue, op,scrollTo,default_idx) {
        var selection = this.selection;
        var idx = -1;
        if (attrValue instanceof Array && attrValue.length==1){
            attrValue = attrValue[0];
        }
        if (attrValue instanceof Array) {
            selection.unselectAll();
            var grid = this;
            dojo.forEach(attrValue, function(v) {
                var idx = grid.indexByRowAttr(attrName, v);
                if(idx>=0){
                    selection.addToSelection(idx);
                }
            });
        } else {
            var idx = this.indexByRowAttr(attrName, attrValue, op);
            if(idx<0 && default_idx!=null && default_idx>=0 ){
                idx = default_idx;
            }
            if(idx>=0){
                selection.select(idx);
            }
        }
        if(scrollTo===true && typeof(idx)=='number' && idx>=0){
            scrollTo = idx;
        }
        if(scrollTo){
            this.scrollToRow(scrollTo);
        }
        return idx;
    },

    mixin_rowBagNode: function(idx) {
        var idx = (idx == null) ? this.selection.selectedIndex : idx;
        return this.model.store.rootData().getNodes()[idx];
    },
    mixin_rowBagNodeUpdate: function(idx, data) {
        var bagnode = this.rowBagNode(idx);
        var attributes = bagnode.attr;
        for (var attr in attributes) {
            var newvalue = data.getItem(attr);
            if (newvalue != null) {
                attributes[attr] = newvalue;
            }
        }
        bagnode.setAttr(attributes);
    },
    mixin_getSelectedPkeys: function(caption_field) {
        var sel = this.selection.getSelected();
        var result = [];
        var r;
        if (sel.length > 0) {
            for (var i = 0; i < sel.length; i++) {
                r = this.rowByIndex(sel[i]);
                result.push(caption_field? {'pkey':this.rowIdentity(r),'caption':r[caption_field]} : this.rowIdentity(r))
            }
        } 
        return result;
    },
    mixin_getAllPkeys:function(caption_field){ 
        if(this.collectionStore){
            return this.collectionStore().currentPkeys(caption_field);
        }else{
            var result = [];
            for (var i = 0; i < this.rowCount; i++) {
                result.push(this.rowIdByIndex(i));
            }
            return result;
        }
        
    },
    mixin_cellCurrentDatapath:function(path){
        console.error('not implemented')
    },
    mixin_getSelectedRow: function() {
        return  this.rowByIndex(this.selection.selectedIndex);
    },
    mixin_longTouch:function(e) {
        alert('longtouch');
    },
    mixin_getSelectedRowidx: function() {
        var sel = this.selection.getSelected();
        var result = [];
        for (var i = 0; i < sel.length; i++) {
            var row = this.rowByIndex(sel[i]);
            result.push(row.rowidx);
        }
        return result;
    },
    structFromBag_cellFormatter :function(sourceNode, cell,formatOptions, cellClassCB) {
        var opt = objectUpdate({}, formatOptions);
        var cellClassFunc;
        if (cellClassCB) {
            cellClassFunc = funcCreate(cellClassCB, 'cell,v,inRowIndex,originalValue',this);
        }
        return function(v, inRowIndex) {
            var renderedRow = this.grid.currRenderedRow;
            if(!objectNotEmpty(renderedRow)){
                return '<div class="cellContent">' + '&nbsp;' + '</div>';
            }
            var baseStyleDict = objectUpdate(objectFromStyle(this.cellStyles),
                                                     sourceNode.evaluateOnNode(genro.dom.getStyleDict(objectUpdate({},this), [ 'width'])))
            var ranges = objectExtract(cell,'range_*',true);
            
            if(objectNotEmpty(ranges)){
                var rangepars = objectUpdate({},renderedRow);
                rangepars.value = v;
                rangepars._kwargs = rangepars;
                for(var rng in ranges){
                    if(stringEndsWith(rng,'_condition') || rng.indexOf('_')<=0){
                        var condition = funcApply('return '+ranges[rng],rangepars,sourceNode);
                        if(condition){
                            var prefix = rng.replace('_condition','');
                            var styleKw = objectExtract(ranges,prefix+'_*',true);
                            objectUpdate(baseStyleDict,sourceNode.evaluateOnNode(genro.dom.getStyleDict(styleKw, [ 'width'])))
                        }
                    }
                }
            }
            var styles = objectExtract(renderedRow,'style_'+cell.field+'_*',true);
            objectUpdate(baseStyleDict,styles);
            this.customStyles.push(objectAsStyle(baseStyleDict));
            if (cellClassFunc) {
                var cellClassFuncResult = cellClassFunc(this, v, inRowIndex,renderedRow[cell.field]);
                if(cellClassFuncResult){
                    this.customClasses.push(cellClassFuncResult);
                }
            }
            var cellCustomClass = renderedRow['_customClass_'+cell.field];
            if(cellCustomClass){
                this.customClasses.push(cellCustomClass);
            }
            if(this.edit){
                this.customClasses.push('cell_editable');    
                if(this.editDisabled){
                    if(this.grid.sourceNode.currentFromDatasource(this.editDisabled)){ 
                        this.customClasses.push('cell_disabled');
                    }
                }
                if(this.editLazy){
                    if(this.grid.sourceNode.currentFromDatasource(this.editLazy)){
                        this.customClasses.push('cell_editLazy');
                    }
                }
                //this.grid.rowSourceNode(inRowIndex).getRelativeData()
            }

            opt['cellPars'] = {rowIndex:inRowIndex};
            //var zoomPage = opt['zoomPage'];
            if (typeof(v) == 'number') {
                if(v < 0){
                    this.customClasses.push('negative_number');
                }
                if(this.emptyZero && v===0){
                    v = null;
                }
            }
            if (this.grid.gridEditor) {
                this.grid.gridEditor.onFormatCell(this,inRowIndex,renderedRow);
            }
            var v = genro.format(v, opt);
            if (v == null) {
                v = '&nbsp;';
            }
            var template = opt['template'];
            if (template) {
                if(template.indexOf('$'+cell.field)>=0){
                    v = dataTemplate(template,renderedRow);
                }else{
                    v = template.replace(/#/g, v);
                }
                
            }
            if (opt['js']) {
                v = opt['js'](v, this.grid.storebag().getNodes()[inRowIndex]);
            }
            var zoomAttr = objectExtract(opt,'zoom_*',true);
            var draggable = this.draggable ? ' draggable=true ' : '';
            if (objectNotEmpty(zoomAttr)) {
                return "<div "+draggable+" class='cellContent gnrzoomcell' onclick='if(event.shiftKey){dojo.stopEvent(event); genro.dlg.zoomFromCell(event);}'>" + v + "</div>";
            }else{
                return '<div ' + draggable + 'class="cellContent">' + v + '</div>';
            }
            
        };
    },
    subtableGetter:function(row,idx){
        //the scope is the cell
        var cellattr = this.grid.cellmap[this.field];        
        var data = row[cellattr._subtable];
        if (cellattr.key){
            data = data[this.grid.sourceNode.currentFromDatasource(cellattr.key)];
        }
        if (data){
            return data[cellattr._subfield];
        }
    },
    
    structFromBag_cell:function(sourceNode,cellNode,columnsets){
        var rowattrs = objectUpdate({}, cellNode.getParentNode().attr);
        rowattrs = objectExtract(rowattrs, 'classes,headerClasses,cellClasses');

        var cell = objectUpdate({field:cellNode.label}, rowattrs);
        var columnset = cellNode.attr.columnset;
        if(columnset){
            var columnsetAttrs = columnsets.getAttr(columnset) || {};
            objectUpdate(cell,objectExtract(columnsetAttrs,'cells_*',true));
        }
        
        cell = objectUpdate(cell, cellNode.attr);
        if(!cell.width && cell.dfltwidth){
            cell.width = cell.dfltwidth;
        }
        var dtype = cell.dtype;
        var cell_name = _F(sourceNode.currentFromDatasource(cell.name),cell.name_format);
        cell.original_field = cell.field;
        cell.original_name = cell_name;
        cell._nodelabel = cellNode.label;
        var userSets = objectPop(cell,'userSets');
        if(userSets){
            cellNode.attr['calculated'] = true;
            cell = this.getNewSetKw(sourceNode,cell);
            dtype ='B';
        }
        var rowBasedAttr = {};
        for (var k in cell){
            if(typeof(cell[k])=='string' && cell[k].indexOf('#ROW')>=0){
                rowBasedAttr[k] = cell[k];
            }
        }
        for (k in rowBasedAttr){
            delete cell[k];
        }
        //cell = sourceNode.evaluateOnNode(cell);

        cell.name = '<div '+ ((sourceNode.attr.draggable_column)?'draggable="true"' :'' )+ ' class="cellHeaderContent" >'+cell_name || '&nbsp;'+'</div>';
        if (cell.field) {
            if(cell.field.indexOf(':')>=0 && !cell._customGetter){
                var f = cell.field.split(':');
                cell._customGetter = this.subtableGetter;
                cell._subtable = f[0];
                cell._subfield = f[1];
            }

            if(typeof(cell.values)=='string'){
                var values = sourceNode.currentFromDatasource(cell.values);
                if(values.indexOf(':')>=0){
                    var valuesdict = objectFromString(values);
                    cell._customGetter = function(rowdata,idx){
                        var currvalue = rowdata[this.field_getter];
                        if(currvalue){
                            var valuetoset = [];
                            currvalue = (currvalue+'').split(',');
                            dojo.forEach(currvalue,function(n){
                                valuetoset.push(valuesdict[n]);
                            });
                            return valuetoset.join(',');
                        }
                        return currvalue;  
                    };
                }
            }
            if(cell.rowTemplate){
                cell.rowTemplate = sourceNode.currentFromDatasource(cell.rowTemplate);
            }
            cell.field = cell.field.replace(/\W/g, '_');
            if(cell.group_aggr){
                cell.field += '_'+cell.group_aggr.toLowerCase().replace(/\W/g, '_');
                if(cell.dtype=='D' || cell.dtype=='DH'){
                    dtype = 'T';
                }
            }
            cell.field_getter = cell.caption_field? cell.caption_field.replace(/\W/g, '_'):cell.field ;
            if(cell.caption_field || cell.values){
                dtype = 'T';
            }
            var checkboxPars = objectPop(cell,'checkBoxColumn');

            if(checkboxPars){
                cell = this.getCheckBoxKw(checkboxPars,sourceNode,cell);
                cell.isCheckBoxCell = true;
                this.setCheckedIdSubscription(sourceNode,cell);
                dtype ='B';
            }     
            if (dtype) {
                cell.cellClasses = (cell.cellClasses || '') + ' cell_' + dtype;
            }                       
            var zoomAttr = objectExtract(cell,'zoom_*',true,true);
            cell.cellStyles = objectAsStyle(objectUpdate(objectFromStyle(cell.cellStyles),
                                            genro.dom.getStyleDict(cell, [ 'width'])));
            var formats = objectExtract(cell, 'format_*');
            var format = objectPop(cell, 'format');
            var template = objectPop(cell, 'template');
            var js = objectPop(cell, 'js');
            if (template) {
                formats['template'] = template;
            }
            formats['dtype'] = dtype;
            if (js) {
                formats['js'] = genro.evaluate(js);
            }
            if (objectNotEmpty(zoomAttr)){
                objectUpdate(formats,zoomAttr);
            }
            if (format) {
                formats['format'] = format;
            }
            if (cell.counter) {
                sourceNode.attr.counterField = cell.field;
                dtype = 'L';
            }
            if ('hidden' in cell && sourceNode.currentFromDatasource(cell.hidden)) {
                cell.classes = (cell.classes || '') + ' hiddenColumn';
            }
            if (dtype) {
                if (!formats.pattern){
                    formats = objectUpdate(objectUpdate({}, localType(dtype)), formats);
                }
            }
            //formats = objectUpdate(formats, localType(dtype);
            var cellClassCB = objectPop(cell, 'cellClassCB');
            var _customGetter = objectPop(cell,'_customGetter');
            if(_customGetter){
                cell._customGetter = funcCreate(_customGetter);
            }
            if(dtype=='B'){
                formats['trueclass']= formats['trueclass'] || "checkboxOn";
                formats['falseclass']= formats['falseclass'] || "checkboxOff";
            }
            if(cell.totalize){
                cell.totalize = cell.totalize===true?'.totalize.'+cell.field:cell.totalize;
            }
            if(cell.semaphore){
                formats['trueclass'] = 'greenLight';
                formats['falseclass'] = 'redLight';
            }else if(cell.inv_semaphore){
                formats['falseclass'] = 'greenLight';
                formats['trueclass'] = 'redLight';
            }else if(cell.highlight_semaphore){
                formats['falseclass'] = ' ';
                formats['trueclass'] = 'yellowLight';
            }
            cell._formats = formats;
            cell.formatter = this.structFromBag_cellFormatter(sourceNode,cell,formats, cellClassCB);
            delete cell.tag;
            objectUpdate(cell,rowBasedAttr);
            return cell;
        }
    },
    structFromBag: function(sourceNode, struct, cellmap) {
        cellmap = cellmap || {};
        var result = [];
        if (struct) {
            sourceNode._serverTotalizeColumns = {};
            var bagnodes = struct.getNodes();
            var columnsets = struct.getItem('info.columnsets') || new gnr.GnrBag();
            var formats, dtype, editor;
            var view, viewnode, rows, rowsnodes, i, k, j, cellsnodes, row, cell, rowattrs, rowBag;
            var editorPars = sourceNode.attr.gridEditorPars;
            for (var i = 0; i < bagnodes.length; i++) {
                viewnode = bagnodes[i];
                if(viewnode.label=='info'){
                    continue;
                }
                view = objectUpdate({}, viewnode.attr);
                delete view.tag;
                rows = [];
                rowsnodes = viewnode.getValue().getNodes();
                for (var k = 0; k < rowsnodes.length; k++) {

                    rowBag = rowsnodes[k].getValue();

                    if (!(rowBag instanceof gnr.GnrBag)) {
                        rowBag = new gnr.GnrBag();
                        rowsnodes[k].setValue(rowBag, false);
                    }
                    if(rowBag.getNode('_rowEditorStatus')){
                        rowBag.popNode('_rowEditorStatus',false);
                    }
                    if(editorPars && editorPars.statusColumn && dojo.some(rowBag.getNodes(),function(n){return n.attr.edit;})){
                        rowBag.setItem('_rowEditorStatus',null,{dtype:'T',width:'2em',
                                                            field:'_rowEditorStatus',
                                                            cellClasses:'rowEditorStatus',
                                                            headerClasses:'rowEditorStatus',
                                                            name:' ',calculated:true,
                                                            _customGetter:function(rowdata,rowIdx){
                                                                return this.grid.gridEditor.statusColGetter(rowdata,rowIdx);
                                                            }}, {'doTrigger':false});
                    }

                    //cellsnodes = rowBag.getNodes();
                    row = [];
                    var showLineNumber = sourceNode.getRelativeData(sourceNode.attr.structpath+'.info.showLineNumber');
                    if (isNullOrBlank(showLineNumber)){
                        showLineNumber = sourceNode.attr.showLineNumber;
                    }
                    if(showLineNumber){
                        if(!rowBag.getNode('_linenumber')){
                            rowBag.setItem('_linenumber',null,{'calculated':true,'dtype':'L','name':' ','width':'3em',
                                'classes':'gnrgridlineno','field':'_linenumber','format':'#,###',
                                '_customGetter':function(row,idx){
                                    return idx+1;
                                }
                            },{_position:0});
                        }
                    }else{
                        rowBag.popNode('_linenumber');
                    }

                    if(sourceNode.attr.rowStatusColumn){
                        if(!rowBag.getNode('_protectionStatus')){
                            rowBag.setItem('_protectionStatus',null,{
                                field:'_protectionStatus',name:' ',width:'20px',
                                calculated:true,_customGetter:function(){
                                    return '<div class="_statusIcon"></div>'
                                }
                            },{_position:0});
                        }
                    }
                    if(genro.isMobile && sourceNode.attr.draggable_row){
                        if(!rowBag.getNode('drag_handle')){
                            rowBag.setItem('drag_handle',null,{
                                field:'_drag_handle',name:' ',width:'23px',
                                calculated:true,_customGetter:function(){
                                    return '<div class="menu_white_svg" style="background-color:#888; height:22px;border-radius:4px;" draggable="true">&nbsp;</div>';
                                }
                            },{_position:0});
                        }
                    }
                    if(sourceNode.attr.multiStores){
                        if(!rowBag.getNode('_storenameCol')){
                            rowBag.setItem('_storenameCol',null,{
                                field:'_dbstore_',name:_T('Storename'),width:'15em',
                                calculated:true
                            });
                        }
                    }

                    var that = this;
                    rowBag.forEach(function(n){
                        cell = that.structFromBag_cell(sourceNode,n,columnsets);
                        row.push(cell);
                        cellmap[cell.field] = cell;
                    },'static');
                    rows.push(row);
                }

                view.rows = rows;
                result.push(view);
            }
        }
        

        return result;
    },
    groupByFromStruct:function(struct, grouppable) {
        if (grouppable == undefined) {
            grouppable = [];
        }
        var nodes = struct.getNodes();
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            if (node.attr.group_by) {
                var fld = node.attr.field;
                if ((!stringStartsWith(fld, '$')) && (!stringStartsWith(fld, '@'))) {
                    fld = '$' + fld;
                }
                grouppable.push(fld);
            }
            if (node.getValue() instanceof gnr.GnrBag) {
                this.groupByFromStruct(node.getValue(), grouppable);
            }
        }
        return grouppable.join(',');
    },
    mixin_deleteColumn:function(col) {
        var colsBag = this.structBag.getItem('#0.#0');
        colsBag.popNode('#' + col);
    },
    mixin_moveColumn:function(col, toPos) {
        if (toPos != col) {
            var colsBag = this.structBag.getItem('#0.#0');
            var nodeToMove = colsBag.popNode('#' + col,false);
            colsBag.setItem(nodeToMove.label, null, nodeToMove.attr, {'_position':toPos});
        }

    },
    mixin_moveRow:function(row, toPos) {
        if (toPos!=null && toPos>=0 && toPos!= row) {
            var storebag = this.storebag();
            storebag.moveNode(row, toPos,'movingRows');
        }

    },
    mixin_addColumn:function(col, toPos,kw) {
        //if(!('column' in drop_event.dragDropInfo)){ return }
        var colsBag = this.structBag.getItem('#0.#0');
        if(!kw){
            kw = {'width':'8em','name':col.fullcaption,
            'dtype':col.dtype, 'field':col.fieldpath,
            'tag':'cell'};
            if (col._owner_package){
                kw._owner_package = col._owner_package;
            }
            if(kw.field.length>63){
                var hashname = 'relation_'+stringHash(kw.field)+'_'+kw.field.split('.').slice(-1);
                kw.queryfield = kw.field +' AS '+hashname;
                kw.field = hashname;
            }
            objectUpdate(kw,objectExtract(col,'cell_*'));
            kw.format_pattern = col.format;
            objectUpdate(kw,objectExtract(col,'format_*',null,true));
        }
        
        colsBag.setItem('cellx_' + genro.time36Id(), null, kw, {'_position':toPos + 1});
    },
    onDragStart:function(dragInfo) {
        var dragmode = dragInfo.dragmode;
        var event = dragInfo.event;
        var widget = dragInfo.widget;
        var value = {};
        if (widget.gridEditor && widget.gnrediting){
            return false;
        }

        if (dragmode == 'row') {
            var cells = widget.structure[0]['rows'][0];
            var sel = widget.selection.getSelected();
            var rowdata = widget.rowByIndex(dragInfo.row);
            if (sel.length == 1) {
                sel = [];
            }
            if (sel.indexOf(dragInfo.row) < 0) {
                sel.push(dragInfo.row);
            }
            sel.sort();
            var rowset = [];
            var pkeys = [];
            var valTextPlain = [];
            var valTextXml = [];
            var valTextHtml = [];
            var innerHtml = [];
            var idx = 0;
            var rn; 
            var innerHtmlTxt = sel.length>20?'<div style="width:600px;text-align:center;">'+sel.length+' '+widget.sourceNode.attr.item_name_plural+' </div>':null;
            dojo.forEach(sel, function(k) {
                var rdata = widget.rowByIndex(k);
                pkeys.push(widget.rowIdentity(rdata));
                rowset.push(rdata);
                var r = [];
                var r_xml = [];
                var r_html = [];
                cells.forEach(function(n) {
                    var field = n.field;
                    var v = convertToText(rdata[field], {'xml':true,'dtype':+n.dtype})[1];
                    r.push(v);
                    r_xml.push('<' + field + '>' + v + '</' + field + '>');
                    r_html.push('<td name="' + field + '">' + v + '</td>');
                });
                if(!innerHtmlTxt){
                    rn = widget.views.views[0].rowNodes[k];
                    if(rn){
                        innerHtml.push(rn.innerHTML);
                    }
                }
                valTextPlain.push(r.join('\t'));
                valTextXml.push('<r_' + idx + '>' + r_xml.join('') + '</r_' + idx + '>');
                valTextHtml.push('<tr>' + r_html.join('') + '</tr>');
                idx = idx + 1;
            });
            
            var selfDragRows = dragInfo.sourceNode.attr.selfDragRows;
            if (typeof(selfDragRows) == 'function') {
                selfDragRows = selfDragRows(dragInfo);
            }
            if (selfDragRows) {
                value['selfdragrow_' + dragInfo.sourceNode._id] = sel;
            }
            value['text/plain'] = valTextPlain.join('\n');
            value['text/xml'] = valTextXml.join('\n');
            value['text/html'] = '<table>\n' + valTextHtml.join('\n') + '\n</table>';
            value['gridrow'] = {'row':dragInfo.row,'rowdata':rowdata,'rowset':rowset,'gridId':widget.sourceNode.attr.nodeId};
            if(widget.collectionStore && widget.collectionStore()){
                var storeAttr = widget.collectionStore().storeNode.attr;
                value['dbrecords'] = {table:storeAttr['table'],pkeys:pkeys,objtype:'record'};
            }
            if (sel.length > 0) {
                var auxDragImage = dragInfo.dragImageNode = dojo.byId('auxDragImage');
                dragInfo.dragImageNode = document.createElement('div');
                var auxnode = document.createElement('div');
                dojo.addClass(auxnode,'rowsetdragging');
                dragInfo.dragImageNode.appendChild(auxnode);
                auxnode.innerHTML = innerHtmlTxt || innerHtml.join('');
                dojo.addClass(dragInfo.dragImageNode, 'rowsetdragging_background');
                auxDragImage.appendChild(dragInfo.dragImageNode);
                dragInfo.event.dataTransfer.setDragImage(auxDragImage.firstChild, 0, 0);
                setTimeout(function() {
                    auxDragImage.removeChild(dragInfo.dragImageNode);
                }, 1);
            }
        } else if (dragmode == 'cell') {
            var celldata = widget.rowByIndex(dragInfo.row)[event.cell.field];
            var rowdata = widget.rowByIndex(dragInfo.row);
            value['gridcell'] = {'row':dragInfo.row,'column':dragInfo.column,'celldata':celldata,'rowdata':rowdata,'gridId':widget.sourceNode.attr.nodeId};
            value['text/plain'] = convertToText(celldata)[1];
        } else if (dragmode == 'column') {
            var textcol = '';
            var field = event.cell.field;
            columndata = [];
            for (var i = 0; i < widget.rowCount; i++) {
                var row = widget.rowByIndex(i, true);
                var v = row ? row[field] : '';
                if(!isBag(v)){
                    columndata.push(v);
                }
                textcol = textcol + convertToText(v)[1] + '\n';
            }
            value.gridcolumn = {'column':dragInfo.column,'columndata':columndata,'gridId':widget.sourceNode.attr.nodeId,
                                    'field':field,'original_field':event.cell.original_field,'group_aggr':event.cell.group_aggr};
            value['text/plain'] = textcol;
            var selfDragColumns = dragInfo.sourceNode.attr.selfDragColumns;
            if (typeof(selfDragColumns) == 'function') {
                selfDragColumns = selfDragColumns(dragInfo);
            }
            if (selfDragColumns) {
                value['selfdragcolumn_' + dragInfo.sourceNode._id] = dragInfo.column;
                if (selfDragColumns == 'trashable') {
                    if(dragInfo.sourceNode._showTrash){
                        dragInfo.sourceNode._showTrash(true);
                    }
                    value['trashable'] = dragInfo.column;
                }
            }
        }

        return value;
    },
    fillDropInfo:function(dropInfo) {
        //console.log('fillDropInfo')
        var dragSourceInfo = dropInfo.dragSourceInfo;
        var event = dropInfo.event;
        var draggedTypes = genro.dom.dataTransferTypes(event.dataTransfer);
        var dropModes = dropInfo.sourceNode.dropModes;
        var dropmode;
        var selfdrop = (genro.page_id==dragSourceInfo.page_id) && (dragSourceInfo._id == dropInfo.sourceNode._id);
        for (var k in dropModes) {
            if(k=='grid' && selfdrop){
                continue;
            }
            if (dojo.filter(dropModes[k].split(','),
                           function (value) {
                               return arrayMatch(draggedTypes, value).length > 0;
                           }).length > 0) {
                dropmode = k;
                break;
            }
            ;
        }
        //dropmode = dropmode || dragSourceInfo.dragmode;
        if (!dropmode && dragSourceInfo.dragmode=='row' && (dojo.indexOf(draggedTypes, 'selfdragrow_' + dropInfo.sourceNode._id) >= 0)) {
            var selfDragRows = dropInfo.sourceNode.attr.selfDragRows;
            if (typeof(selfDragRows) == 'function') {
                selfDragRows = selfDragRows(dropInfo);
            }
            if (selfDragRows) {
                dropmode = 'row';
            }
        }
        if (!dropmode && dragSourceInfo.dragmode=='column' && (dojo.indexOf(draggedTypes, 'selfdragcolumn_' + dropInfo.sourceNode._id) >= 0)) {
            var selfDragColumns = dropInfo.sourceNode.attr.selfDragColumns;
            if (typeof(selfDragColumns) == 'function') {
                selfDragColumns = selfDragColumns(dropInfo);
            }
            if (selfDragColumns) {
                dropmode = 'column';
            }
        }
        if (!dropmode) {
            return false;
        }
        var widget = dropInfo.widget;
        if (dropmode == 'grid') {
            dropInfo.outline = widget.domNode;
        }
        else if (dropmode == 'column') {
            dropInfo.column = event.cellIndex;
            dropInfo.outline = widget.columnNodelist(event.cellIndex, true);
        } else {
            dropInfo.row = event.rowIndex;
            if (dropmode == 'cell') {
                dropInfo.column = event.cellIndex;
                dropInfo.outline = event.cellNode;
            } else if (dropmode == 'row') {
                dropInfo.outline = event.rowNode;
                if(widget && dropInfo.row!=null){
                    dropInfo.targetRowData = widget.rowByIndex(dropInfo.row);
                }
            }
        }
        dropInfo.widget = widget;
        dropInfo.sourceNode = widget.sourceNode;

    },
    customEventInfo:function(info){
        var event = info.event;
        var widget = info.widget;
        if (widget.grid) {
            widget.content.decorateEvent(event);
            widget = widget.grid;
        } else {
            widget.views.views[0].header.decorateEvent(event);
        }
        info.column = event.cellIndex;
        info.row = event.rowIndex;
        info.widget = widget;
        info.sourceNode = widget.sourceNode;
    },

    fillDragInfo:function(dragInfo) {
        var widget = dragInfo.widget;
        var event = dragInfo.event;
        if(event.cell && event.cell.field=='_drag_handle'){
            event.cellIndex=-1;
        }
        if ((event.cellIndex >= 0) && (event.rowIndex == -1)) {
            dragInfo.dragmode = 'column';
            dragInfo.outline = widget.columnNodelist(event.cellIndex, true);
            dragInfo.colStruct = widget.cellmap[event.cell.field];
        } else if ((event.cellIndex == -1) && (event.rowIndex >= 0)) {
            dragInfo.dragmode = 'row';
            dragInfo.outline = event.rowNode;
        } else if ((event.cellIndex >= 0) && (event.rowIndex >= 0)) {
            dragInfo.dragmode = 'cell';
            dragInfo.outline = event.cellNode;
            dragInfo.colStruct = widget.cellmap[event.cell.field];
        }
    },
    setTrashPosition: function(dragInfo) {
        var cellNode = dragInfo.event.cellNode;
        if (cellNode) {
            var trash = genro.dom.getDomNode('trash_drop');
            var mb = dojo.marginBox(trash);
            var vp = dojo.coords(cellNode);
            trash.style.left = Math.floor(vp.x) + "px";
            trash.style.top = Math.floor(vp.y + vp.h + 1) + "px";
            return true;
        }
    }
});
// **************** Virtual Grid ****************
dojo.declare("gnr.widgets.VirtualGrid", gnr.widgets.DojoGrid, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'VirtualGrid';
    },
    creating: function(attributes, sourceNode) {
        var savedAttrs = this.creating_common(attributes, sourceNode);
        this.creating_structure(attributes, sourceNode);
        var storepath = sourceNode.absDatapath(sourceNode.attr.storepath);
        attributes.storebag = genro.getDataNode(storepath, true, new gnr.GnrBag());
        if (!(attributes.storebag.getValue() instanceof gnr.GnrBag)) {
            attributes.storebag.setValue(new gnr.GnrBag());
        }

        attributes.get = function(inRowIndex) {
            var grid = this.grid;
            if (grid.currRenderedRowIndex != inRowIndex) {
                grid.currRenderedRowIndex = inRowIndex;
                grid.currRenderedRow = grid.rowByIndex(inRowIndex);
            }
            return grid.currRenderedRow[this.field];
        };
        attributes.canSort = function(info) {
            return true;
        };
        return savedAttrs
    },

    created: function(widget, savedAttrs, sourceNode) {
        this.created_common(widget, savedAttrs, sourceNode);
        dojo.connect(widget, 'onSelected', widget, '_gnrUpdateSelect');
    },

    mixin_canEdit: function(inCell, inRowIndex) {

        return false;
    },
    mixin_loadBagPageFromServer:function(pageIdx) {
        var row_start = pageIdx * this.rowsPerPage;
        var kw = this.storebag.attr;
        var data = genro.rpc.remoteCall(kw.method, {'selectionName':kw.selectionName,
            'row_start':row_start,
            'row_count':this.rowsPerPage,
            'sortedBy':this.sortedBy,
            'table':kw.table,
            'recordResolver':false});
        data = data.getValue();
        this.storebag.getValue().setItem('P_' + pageIdx, data);
        return data;
    },

    patch_sort: function() {
        var sortInfo = this.sortInfo;
        var order;
        if (sortInfo < 0) {
            order = 'd';
            sortInfo = -sortInfo;
        } else {
            order = 'a';
        }
        var cell = this.layout.cells[sortInfo - 1];
        var sortedBy = cell.field + ':' + order;
        if ((cell.dtype == 'A') || ( cell.dtype == 'T')) {
            sortedBy = sortedBy + '*';
        }
        var path = this.sourceNode.attrDatapath('sortedBy');
        genro._data.setItem(path, sortedBy);

    },
    mixin_clearBagCache:function() {
        this.storebag.getValue().clear();
        this.currRenderedRowIndex = null;
        this.currRenderedRow = null;
        this.currCachedPageIdx = null;
        this.currCachedPage = null;
    },

    mixin_setSortedBy:function(sortedBy) {
        this.sortedBy = sortedBy;
        var rowcount = this.rowCount;
        this.updateRowCount(0);
        this.clearBagCache();
        this.updateRowCount(rowcount);
    },
    mixin_rowBagNodeUpdate: function(idx, data, pkey) {
        if (idx == -1) {
            var storebag = this.storebag.getValue();
            var cells = this.layout.cells;
            var row = {};
            var cell;
            for (var i = 0; i < cells.length; i++) {
                cell = cells[i];
                row[cell.field] = data.getItem(cell.field);
            }
            var identifier = this.rowIdentifier();
            data[identifier] = pkey;
            row[identifier] = pkey;
            storebag.setItem(pkey, null, row);
            this.updateRowCount(storebag.len());
        }
        else {
            var attributes = this.rowByIndex(idx);
            for (var attr in attributes) {
                var newvalue = data.getItem(attr);
                if (newvalue != null) {
                    attributes[attr] = newvalue;
                }
            }
            var identifier = this.rowIdentifier();
            //data[identifier]=pkey;
            attributes[identifier] = pkey;
            this.updateRow(idx);
        }
    },
    mixin_rowIdByIndex: function(idx) {
        if (idx != null) {
            return this.rowIdentity(this.rowByIndex(idx));
        }
    },

    mixin_rowByIndex:function(inRowIndex, lazy) {
        var rowIdx = inRowIndex % this.rowsPerPage;
        var pageIdx = (inRowIndex - rowIdx) / this.rowsPerPage;
        if (this.currCachedPageIdx != pageIdx) {
            this.currCachedPageIdx = pageIdx;
            this.currCachedPage = this.storebag.getValue().getItem('P_' + pageIdx);
            if (!this.currCachedPage) {
                if (lazy) {
                    return;
                }
                this.currCachedPage = this.loadBagPageFromServer(pageIdx);
            }
        }
        return this.currCachedPage ? this.currCachedPage.getNodes()[rowIdx].attr : null;
    },

    mixin_rowIdentity: function(row) {
        if (row) {
            return row[this.rowIdentifier()];
        } else {
            return null;
        }
    },
    mixin_rowIdentifier: function(row) {
        return this._identifier;
    },
    patch_onStyleRow:function(row) {
        var attr = this.rowByIndex(row.index);
        if (attr) {
            if (attr._protection_info=='DU'){
                row.customClasses = row.customClasses?row.customClasses + ' _gnrReadOnlyRow': '_gnrReadOnlyRow';
            }else if(attr.__protection_tag){
                row.customClasses = row.customClasses?row.customClasses + ' _gnrProtectionPass': '_gnrProtectionPass';
            }
            if (attr._customClasses) {
                var customClasses = null;
                if ( typeof(attr._customClasses)=='function'){
                    customClasses=attr._customClasses(row);
                }
                
                if (attr._customClasses.slice(0, 1) == '!') {
                    customClasses = attr._customClasses.slice(1);
                } else {
                    customClasses = row.customClasses + ' ' + attr._customClasses;
                }
                row.customClasses = customClasses;
            }
            if (attr._customStyles) {
                row.customStyles =( typeof(_customStyles)=='function')?attr._customStyles(row) : attr._customStyles;
            }
        }
        row.over = this.enableOver  && row.over;
        this.onStyleRow_replaced(row);
    }
});


dojo.declare("gnr.widgets.VirtualStaticGrid", gnr.widgets.DojoGrid, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'VirtualGrid';
    },
    creating: function(attributes, sourceNode) {
        var savedAttrs = this.creating_common(attributes, sourceNode);
        this.creating_structure(attributes, sourceNode);
        sourceNode.registerDynAttr('storepath');
        return savedAttrs;

    },

    created: function(widget, savedAttrs, sourceNode) {
        this.created_common(widget, savedAttrs, sourceNode);
        genro.src.onBuiltCall(dojo.hitch(widget, 'render'));
        dojo.connect(widget, 'onSelected', widget, '_gnrUpdateSelect');
        widget.updateRowCount('*');
    },

    attributes_mixin_get: function(inRowIndex,ignoreFilter) {
        var rowdata;
        if(!ignoreFilter){
            rowdata = this.grid.rowCached(inRowIndex);
        }else{
            rowdata = this.grid.rowByIndex(inRowIndex,true,true);
        }
        
        if(!rowdata){
            console.log('no rowdata:',rowdata);
        }
        var result;
        if(this._customGetter){
            try{
                return this._customGetter.call(this, rowdata,inRowIndex)
            }catch(e){
                console.error(e)
                return 'err';
            }
        }else if(this.rowTemplate){
            var formats = {};
            var c;
            for(var k in this.grid.cellmap){
                c = this.grid.cellmap[k];
                formats[c.field] = c._formats;
            }
            return dataTemplate(this.rowTemplate,new gnr.GnrBag(rowdata),null,null,{formats:formats});
        }else{
            return rowdata[this.field_getter]
        }
        //return this._customGetter ? this._customGetter.call(this, rowdata,inRowIndex) : ;
    },

    mixin_rowCached:function(inRowIndex) {
        if (this.currRenderedRowIndex !== inRowIndex) {
            this.currRenderedRowIndex = inRowIndex;
            this.currRenderedRow = this.rowByIndex(inRowIndex,true);
        }
        return this.currRenderedRow;
    },

    attributes_mixin_canSort: function(colindex) {
        var cellattr = this.getCell(colindex-1) || {};
        var canSort = 'canSort' in this.sourceNode.attr?this.sourceNode.attr.canSort:true; 
        if(typeof(canSort)=='string'){
            canSort= funcCreate(canSort);
        }
        return typeof(canSort)=='function'? funcCreate(canSort.call(this,colindex)):'sortable' in cellattr?cellattr.sortable:canSort;
    },
    
    mixin_filterToRebuild:function(value){
        if (this._filtered){
            this._filterToRebuild=value;
        }
    },
    mixin_invalidFilter:function(){
        return this._filterToRebuild;
    },
    mixin_resetFilter: function() {
        this.setClass('gridFilterActive',false);
        return this._filtered =null;
    },
    mixin_isFiltered:function(){
        return this._filtered !==null;
    },
    
    mixin_applyFilter: function(filterValue, rendering, filterColumn) {
        if (filterColumn) {
            this.filterColumn = filterColumn;
        }
        this.currentFilterValue = (filterValue === true) ? this.currentFilterValue : filterValue;
        var colType;
        if (this.filterColumn){
            var col = this.cellmap[this.filterColumn];
            var colType = 'A';
            if(col){
                colType = (this.filterColumn.indexOf('+') > 0) ? 'T':(this.cellmap[this.filterColumn]['dtype'] || 'A');
            }
            }
        this.createFiltered(this.currentFilterValue,this.filterColumn,colType);
        if (!rendering) {
            this.updateRowCount('*');
        }
        if(this.changeManager && objectNotEmpty(this.changeManager.totalizeColumns)){
            if(isNullOrBlank(this.currentFilterValue)){
                this.sourceNode.setRelativeData('.filtered_totalize',null);
            }else{
                this.changeManager.calculateFilteredTotals();
            }
        }
        this.setClass('gridFilterActive',this.isFiltered());
    },

    mixin_setClass:function(cls,set){
        genro.dom.setClass((this.sourceNode._wrapperNode || this.sourceNode),cls,set);
    },
    
    mixin_compileFilter:function(value,filterColumn,colType){
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
                if (isNumericType(colType)) {
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
    
    mixin_createFiltered:function(currentFilterValue,filterColumn,colType){
        var cb = this.compileFilter(currentFilterValue,filterColumn,colType);
        if (!cb && !this.excludeListCb){
            this._filtered=null;
            return null;
        }
        var filtered=[];
        var excludeList = null;
        if (this.excludeListCb) {
            excludeList = this.excludeListCb.call(this.sourceNode);
        }
        dojo.forEach(this.storebag().getNodes(), 
                    function(n,index,array){
                        var rowdata = this.rowFromBagNode(n);
                        var result = cb? cb(rowdata,index,array):true; 
                        if(result){
                            if ((!excludeList)||(dojo.indexOf(excludeList, rowdata[this.excludeCol]) == -1)) {
                                filtered.push(index);
                            }
                        }
                    },
                    this);
        this._filtered=filtered;
        this._filterToRebuild=false;
        
    },

    mixin_getCellText:function(field,rowIdx,ignoreFilter){
        var c = this.layout.cells.filter(function(n){return n.field==field});
        if(c.length){
            return c[0].get(rowIdx,ignoreFilter);
        }
    },


    mixin_getRowText:function(rowIdx,joiner,fields,ignoreFilter){
        var result = [];
        var cb;
        if(fields){
            cb = function(c){
                if (fields.indexOf(c.field_getter || c.field)>=0){
                    result.push(c.get(rowIdx,ignoreFilter));
                }
            }
        }else{
            cb = function(c){
                if(!c.classes || c.classes.indexOf('hiddenColumn')<0){
                    result.push(c.get(rowIdx,ignoreFilter));
                }
            }
        }
        this.layout.cells.forEach(cb);
        return result.join(joiner || '');
    },



    mixin_getRowTextObj:function(rowIdx,ignoreFilter){
        var result = {};
        this.layout.cells.forEach(function(c){
            result[c.field] = c.get(rowIdx,ignoreFilter);
        });
        return result;
    },

    mixin_sortStore:function(){
        console.warn('OLD GRID FIX ME')
        //FOR LEGACY GRID IT SHOULD NOT BE CALLED
        //WE ASSUME THAT START SORT FOR A NEW DATASTORE IS RIGHT
        if (this.sortedBy) { 
            var storebag = this.storebag();
            var sortedBy = this.sortedBy;
            if(this.datamode!='bag'){
                sortedBy = sortedBy.split(',');
                var l = [];
                dojo.forEach(sortedBy,function(n){l.push('#a.'+n);});
                sortedBy = l.join(',');
            }
            storebag.sort(sortedBy);
        }
    },

    mixin_fillServerTotalize:function(){

    },

    mixin_newDataStore:function() {
        this.updateRowCount(0);
        this.resetFilter();
        if(this.excludeCol){
            this.filterToRebuild(true);
        }
        this.sortStore();
        this.sourceNode.publish('onNewDatastore');
        this.updateRowCount('*');
        this.restoreSelectedRows();

        this.fillServerTotalize();
    },

    mixin_restoreSelectedRows:function(){
        this.selection.unselectAll();
        this.selectionKeeper('load');
        if (this.autoSelect && (this.selection.selectedIndex < 0)) {
            var sel = this.autoSelect == true ? 0 : this.autoSelect();
            this.selection.select(sel);
        }
    },

    patch_onCellDblClick:function(e){
        if(dojo.isIE){
            this.edit.setEditCell(this._click[1].cell, this._click[1].rowIndex);
        }else if( /*patch_start*/ this._click[0] /*patch_end*/&& this._click[0].rowIndex != this._click[1].rowIndex){ 
            this.edit.setEditCell(this._click[0].cell, this._click[0].rowIndex);
        }else{
            this.edit.setEditCell(e.cell, e.rowIndex);
        }
        this.onRowDblClick(e);

    },

    mixin_setFilterset:function(val,kw){
        if(kw.reason=='autocreate'){
            return;
        }
        this.applyFilter();
    },

    
    mixin_setStorepath:function(val, kw) {
        if(kw.reason=='autocreate'){
            return;
        }
        else if ((!this._updatingIncludedView) && (! this._batchUpdating)) {
            if (kw.evt == 'fired') {
                var storepath = this.absStorepath();
                var storenode = genro._data.getNode(storepath);
                if (storenode instanceof dojo.Deferred) {
                    console.log('Deferred!!');
                } else {
                    this.updateRowCount();
                }
            } else {
                this._updatingIncludedView = true;
                this.currRenderedRowIndex = null;
                var storebag = this.storebag();
                var parentNode = this.domNode.parentNode;
                var storeNode = storebag.getParentNode();
                var parent_lv = kw.node.parentshipLevel(storeNode);
                if (kw.evt == 'upd') {
                    if (parent_lv > 0) {
                        // a single child changed, not the whole selection
                        var rowIdx = this.sourceNode.updateGridCellAttr(kw, true);
                        //var rowIdx = this.getRowIdxFromNode(kw.node);
                        if((!(this.gnrediting && this.gridEditor.editorPars)) || (rowIdx!=this.currentEditedRow)){
                            this.updateRow(this.absIndex(rowIdx,true));
                        }
                        
                        // dojo.publish('upd_grid_cell', [this.sourceNode, rowLabel, rowIdx]);
                    } else {
                        // upd of the parent Bag
                        this.newDataStore();
                    }
                } else if (kw.evt == 'ins') {//ATTENZIONE: questo trigger fa scattare il ridisegno della grid e cambia l'indice di riga
                    if (parent_lv == 1 || (parent_lv == 2 && this.datamode == 'bag')) {
                        this.updateRowCount();
                        //fa srotellare in presenza di parametri con ==
                        //(parent_lv == 1){ contrario al meccanismo dei dbevent deve essere esterna la selezione
                        //    this.setSelectedIndex(kw.ind);
                        //}
                    } else {
                        //console.log('parent_lv_ins',parent_lv, val, kw)
                        //if ((storebag == kw.where) && (parent_lv<1)){
                        //}
                    }
                } else if (kw.evt == 'del') {
                    if (parent_lv == 1) {
                        var currSelectedIdx = this.selection.selectedIndex;
                        this.selection.unselectAll()
                        var lastSelectable = this.storebag().len()-1;
                        if(currSelectedIdx>lastSelectable){
                            currSelectedIdx = lastSelectable;
                        }
                        this.filterToRebuild(true);
                        this.updateRowCount();
                        var that = this;
                        if(lastSelectable>=0){
                            setTimeout(function(){
                                that.setSelectedIndex(lastSelectable);
                            },1);
                        }
                        
                        //this.setSelectedIndex(kw.ind); contrario al meccanismo dei dbevent
                    } else {
                        //console.log('parent_lv_del',parent_lv,val, kw)
                        //if (parent_lv<1){
                        //}
                    }
                }
                //this.renderOnIdle(); 
                this._updatingIncludedView = false;
                // if (this.prevSelectedIdentifiers){
                //
                // }
            }
        }
    },

    mixin_setSelectedIndex: function(idx) {
        var nrow = this.rowCount;
        if (nrow == 0) {
            this.selection.unselectAll();
        } else {
            if (idx >= nrow) {
                idx = nrow - 1;
            }
            // if(this.selection.isSelected(idx)){
            //this.selection.unselectAll();
            // }
            this.selection.select(idx);
        }
    },

    patch_onSelectionChanged:function() {
        this.onSelectionChanged_replaced();
        var idx = this.selection.getFirstSelected();
        if (! this._batchUpdating) {
            this._gnrUpdateSelect(idx);
        }
        var selectedMany = this.selection.getSelected().length>1;
        if(this.changeManager){
            this.changeManager.calculateFilteredTotals();
        }
        this.setClass('multiSelectionActive',selectedMany);
    },
    patch_sort: function() {
        var sortInfo = this.sortInfo;
        var order, sortedBy;
        if (sortInfo < 0) {
            order = 'd';
            sortInfo = -sortInfo;
        } else {
            order = 'a';
        }
        var cell = this.layout.cells[sortInfo - 1];
        if (this.datamode == 'bag') {
            sortedBy = cell.field + ':' + order;
        } else {
            sortedBy = '#a.' + cell.field + ':' + order;
        }
        if ((cell.dtype == 'A') || ( cell.dtype == 'T')) {
            sortedBy = sortedBy + '*';
        }
        if (!this.sourceNode.attr.sortedBy) {
            this.setSortedBy(sortedBy);
        } else {
            var path = this.sourceNode.attrDatapath('sortedBy');
            genro._data.setItem(path, sortedBy);
        }
    },

    mixin_absStorepath:function(){
        return this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
    },

    mixin_setRefreshOn:function() {

    },
    patch_onStyleRow:function(row) {
        var attr = this.rowCached(row.index);
        var customClasses = null;
        if (attr._is_readonly_row){
            row.customClasses = row.customClasses?row.customClasses + ' _gnrReadOnlyRow': '_gnrReadOnlyRow';
        }else if(attr._is_readonly_row === false){
            row.customClasses = row.customClasses?row.customClasses + ' _gnrProtectionPass': '_gnrProtectionPass';
        }
        if (attr._is_invalid_row){
            row.customClasses = row.customClasses?row.customClasses + ' _gnrInvalidRow': '_gnrInvalidRow';
        }else if(attr._is_invalid_row === false){
            row.customClasses = row.customClasses?row.customClasses + ' _gnrRegularRow': '_gnrRegularRow';
        }
        if(this.rowCustomClassesCb){
            row.customClasses = (row.customClasses || '')+' '+(this.rowCustomClassesCb(attr)||'');
        }
        if (attr._customClasses) {
            
            if (attr._customClasses.slice(0, 1) == '!') {
                customClasses = attr._customClasses.slice(1);
            } else {
                customClasses = row.customClasses + ' ' + attr._customClasses;
            }
            row.customClasses = customClasses;
        }
        if (attr._customStyles) {
            row.customStyles = attr._customStyles;
        }
        row.over = this.enableOver && row.over;
        this.onStyleRow_replaced(row);
    },
    
    mixin_canEdit: function(inCell, inRowIndex) {
        // summary:
        // determines if a given cell may be edited
        // inCell: grid cell
        // inRowIndex: grid row index
        // returns: true if given cell may be edited
        return false;
    },


    patch_onStartEdit: function(inCell, inRowIndex) {
        // summary:
        //      Event fired when editing is started for a given grid cell
        // inCell: Object
        //      Cell object containing properties of the grid column.
        // inRowIndex: Integer
        //      Index of the grid row
    },

    patch_onApplyCellEdit: function(inValue, inRowIndex, inFieldIndex) {
        // summary:
        //      Event fired when editing is applied for a given grid cell
        // inValue: String
        //      Value from cell editor
        // inRowIndex: Integer
        //      Index of the grid row
        // inFieldIndex: Integer
        //      Index in the grid's data model
        var dtype = this.cellmap[inFieldIndex].dtype;
        if ((dtype) && (dtype != 'T') && (typeof(inValue) == 'string')) {
            inValue = convertFromText(inValue, this.cellmap[inFieldIndex].dtype, true);
        }
        var editnode = this.dataNodeByIndex(inRowIndex);
        if (this.datamode == 'bag') {
            editnode.getValue().setItem(inFieldIndex, inValue);
        } else {
            editnode.setAttr(inFieldIndex, inValue);
        }
    },

    patch_updateRowCount:function(n) {
        if(this.sourceNode._isBuilding && this.sourceNode._useStore){
            return;
        }
        if ((n == null) || (n == '*')) {
            if (this.invalidFilter()) {
                this.applyFilter(true, true);
            }
        }
        if (n == '*') {
            //this.selectionKeeper('save');
            this.updateRowCount_replaced(0);
            this.selection.unselectAll();
            n = null;
        }
        if (n == null) {
            var n = this.hideAllRows?0:this.storeRowCount();
        }
        var view = this.views.views[0];
        var scrollBox,scrollLeft;
        if(view){
            //genro.callAfter(function(){
            scrollBox = view.scrollboxNode;
            scrollLeft = scrollBox.scrollLeft;
            this.currRenderedRowIndex = null;
            this.currRenderedRow = null;
            try{
                this.updateRowCount_replaced(n);
            }catch(e){
                console.warn('error in updaterowcount',e);
            }
            
            this.updateTotalsCount(); 
            scrollBox.scrollLeft = scrollLeft;
            //this.updateColumnsetsAndFooters(); makes grids slower
            //},1,this);
        }
    },
    mixin_setSortedBy:function(sortedBy) {
        this.sortedBy = sortedBy;
        var storebag = this.storebag();
        storebag.sort(this.sortedBy);
        this.filterToRebuild(true);
        this.updateRowCount('*');
    },
    mixin_rowBagNodeUpdate: function(idx, data, pkey) {
        if (idx == -1) {
            var storebag = this.storebag();
            var cells = this.layout.cells;
            var row = {};
            var cell;
            for (var i = 0; i < cells.length; i++) {
                cell = cells[i];
                row[cell.field] = data.getItem(cell.field);
            }
            var identifier = this.rowIdentifier();
            data[identifier] = pkey;
            row[identifier] = pkey;
            storebag.setItem(pkey, null, row);
            this.updateRowCount();
        }
        else {
            var attributes = this.rowByIndex(idx);
            for (var attr in attributes) {
                var newvalue = data.getItem(attr);
                if (newvalue != null) {
                    attributes[attr] = newvalue;
                }
            }
            this.updateRow(idx);
        }
    },
    mixin_rowIdByIndex: function(idx) {
        if (idx != null) {
            return this.rowIdentity(this.rowByIndex(idx));
        }
    },
    mixin_storebag:function() {
        //var storepath = this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
        var storepath = this.absStorepath();

        //var storebag=genro.getData(storepath);
        var storebag = genro._data.getItem(storepath);
        if (storebag instanceof gnr.GnrBag) {
            return storebag;
        }
        else if (storebag instanceof dojo.Deferred) {
            return storebag;
        }
        else if (!storebag) {
            storebag = new gnr.GnrBag();
            genro.setData(storepath, storebag);
            return storebag;
        }
        else {
            storebag = new gnr.GnrBag();
            genro.setData(storepath, storebag);
            return storebag;
        }
    },
    mixin_setReloader: function() {
        var filterNode = genro.nodeById(this.sourceNode.attr.nodeId + '_filterReset');
        if (filterNode) {
            filterNode.fireNode();
        }
        this.reload(true);
    },

    mixin_selectionKeeper:function(flag,loadkw) {
        if (flag == 'save') {
            var prevSelectedIdentifiers = [];
            var prevSelectedIndexes = this.selection.getSelected();
            var identifier = this._identifier;
            var that = this;
            var k;
            dojo.forEach(prevSelectedIndexes, function(idx) {
                k = that.rowIdByIndex(idx);
                if(k){
                    prevSelectedIdentifiers.push(k);
                }
                
            });
            this.prevSelectedIdentifiers = prevSelectedIdentifiers;
            this.prevFirstVisibleRow= this.scroller.firstVisibleRow;
            this.prevSelectedIdx = (prevSelectedIndexes.length==1) ?prevSelectedIndexes[0]:-1;
            return {prevSelectedIdentifiers:this.prevSelectedIdentifiers ,prevFirstVisibleRow:this.prevFirstVisibleRow,prevSelectedIdx:this.prevSelectedIdx};

            //this.prevFilterValue = this.currentFilterValue;
        } else if (flag == 'clear') {
            this.prevSelectedIdentifiers = null;
        } else if (flag == 'load') {
            loadkw = loadkw || this._saved_selections;
            if(loadkw){
                this.prevSelectedIdentifiers = loadkw.prevSelectedIdentifiers;
                this.prevFirstVisibleRow = loadkw.prevFirstVisibleRow;
                this.prevSelectedIdx = loadkw.prevSelectedIdx;
                this._saved_selections = null;
            }
            if ((this.prevSelectedIdentifiers) && (this.prevSelectedIdentifiers.length > 0 )) {
                this.selectByRowAttr(this._identifier, this.prevSelectedIdentifiers,null,this.prevFirstVisibleRow,this.prevSelectedIdx);
                this.prevSelectedIdx = null;
                this.prevSelectedIdentifiers = null;
                this.prevFirstVisibleRow = null;
            }else if(this.prevFirstVisibleRow){
                this.scrollToRow(this.prevFirstVisibleRow);
                this.prevFirstVisibleRow = null;
            }
           //if(this.prevFilterValue){
           //    this.applyFilter(this.prevFilterValue);
           //    this.prevFilterValue = null;
           //}
        }
    },

    mixin_reload:function(keep_selection) {
        this.selectionKeeper(keep_selection ? 'save' : 'clear');
        var nodeId = this.sourceNode.attr.nodeId;
        var storebag = this.storebag();
        var storeParent = storebag.getParentNode();
        if (storeParent.getResolver()) {
            storeParent.refresh(true);
        }
        else {
            var selectionNode = genro.nodeById(nodeId + '_store') || genro.nodeById(this.sourceNode.attr.store + '_store'); 
            this.filterToRebuild(true);
            if(selectionNode.store){
                //scrupolo eccessivo
                selectionNode.store.loadData();
            }
            else{
                //non dovrebbe capitarci mai
                selectionNode.fireNode();
            }
        }
        if (nodeId) {
            genro.publish(nodeId + '_data_loaded');
        }
    },

    mixin_setScaleY(v){
        this._setScale();
    },

    mixin_setScaleX(v){
        this._setScale();
    },

    mixin__setScale(v){
        var scaleX = this.sourceNode.getAttributeFromDatasource('scaleX') || 1;
        var scaleY = this.sourceNode.getAttributeFromDatasource('scaleY') || 1;
        scalecb = function(domNode){
            domNode.style.transform = "scale("+scaleX+","+scaleY+")";   
            domNode.style.transformOrigin = '0 0';
        }
        if(this.sourceNode._footersNode || this.sourceNode._columnsetsNode){
            if(this.sourceNode._columnsetsNode){
                scalecb(this.sourceNode._columnsetsNode.widget.domNode);
            }
            if(this.sourceNode._footersNode){
                scalecb(this.sourceNode._footersNode.widget.domNode);
            }
        }
        scalecb(dojo.query('.dojoxGrid-row-table', this.viewsHeaderNode)[0]);
        scalecb(dojo.query('.dojoxGrid-content', this.domNode)[0]);
    },

    mixin_onSetStructpath: function(structBag,kw) {
        this.query_columns = this.gnr.getQueryColumns(this.sourceNode, structBag);
        if(this.sourceNode._useStore){
            this.setEditableColumns();
        }
        this.setChangeManager();
        kw = kw || {};
        if(this.sourceNode._useStore){
            var store = this.collectionStore();
            if(store){
                store.onChangedView();
            }
        }
        this.updateColumnsetsAndFooters();
    },

    mixin_updateColumnsetsAndFooters:function(){
        if(this.sourceNode._footersNode || this.sourceNode._columnsetsNode){
            if(!genro.dom.isVisible(this.sourceNode._wrapperNode)){
                return;
            }
            this.columnsetsAndFooters_autodata();
            this.columnsetsAndFooters_make();
            this.columnsetsAndFooters_size();
            this.sourceNode._wrapperNode.widget.resize();
            this.sourceNode._columnsetAndFootersInitialized = true;
        }
    },

    mixin_absIndex: function(idx,reverse) {
       //if (this.invalidFilter()) {
       //    console.log('invalid filter');
       //}
        if(!this._filtered){
            return idx;
        }
        return reverse ? dojo.indexOf(this._filtered,idx):this._filtered[idx];



    },

    
    mixin_storeRowCount: function(all) {
        if (this._filtered && !all) {
            return this._filtered.length;
        } else {
            return this.storebag().len();
        }
    },
    mixin_rowByIndex:function(inRowIndex) {
        if (inRowIndex < 0) {
            return {};
        }
        inRowIndex = this.absIndex(inRowIndex);
        var nodes = this.storebag().getNodes();
        if (nodes.length > inRowIndex) {
            return this.rowFromBagNode(nodes[inRowIndex]);
        } else {
            return {};
        }
    },
    mixin_dataNodeByIndex:function(inRowIndex) {
        inRowIndex = this.absIndex(inRowIndex);
        var storebag = this.storebag();
        if(storebag instanceof gnr.GnrBag){
            var nodes = storebag.getNodes();
            if (nodes.length > inRowIndex) {
                return nodes[inRowIndex];
            };
        }
    },
    mixin_getSelectedNodes: function() {
        var sel = this.selection.getSelected();
        var result = [];
        for (var i = 0; i < sel.length; i++) {
            var n = this.dataNodeByIndex(sel[i]);
            if(n){
                result.push(n);
            }
        }
        return result;
    },

    mixin_getSelectedProtectedPkeys:function(){
        var that = this;
        var protectPkeys = [];
        this.getSelectedNodes().forEach(function(n){
            if(n.attr._protect_delete || n.attr._is_readonly_row){
                protectPkeys.push(that.rowIdentity(n.attr));
            }
        });
        return protectPkeys.length?protectPkeys:null;
    },

    mixin_rowIdentity: function(row) {
        if (row) {
            return row[this.rowIdentifier()];
        } else {
            return null;
        }
    },
    mixin_rowIdentifier: function(row) {
        return this._identifier;
    },
    mixin_getRowIdxFromNode: function(node) {
        var storebag = this.storebag();
        var subPath = node.getFullpath(null, storebag).split('.');
        return storebag.index(subPath[0]);
    },
    mixin_getColumnValues: function(col) {
        var storebag = this.storebag();
        if (col.slice(0, 2) == '^.') {
            col = col.slice(2);
        }
        if (this.datamode != 'bag') {
            col = '#a.' + col;
        }
        return storebag.columns(col)[0];
    },

    mixin_rowFromBagNode:function(node) {
        var result = objectUpdate({}, node.attr);
        if (this.datamode == 'bag') {
            var value = node.getValue();
            if (value) {
                for (var cellname in this.cellmap) {
                    var cell = this.cellmap[cellname];
                    result[cell.field] = value.getItem(cell.original_field);
                }
            }
            ;
        }
        return result;
    },
    nodemixin_updateGridCellAttr: function(kw) { // update node attributes (for cell display) from new field values
        var grid = this.widget;
        var storebag = grid.storebag();
        var subPath = kw.node.getFullpath(null, storebag).split('.');
        var rowLabel = subPath[0];
        var fldName = subPath[1];
        if (fldName && grid.datamode!='bag') {
            var chNode = storebag.getNode(rowLabel);
            var cellAttr, value, gridfield;
            var currAttr = objectUpdate({},chNode.attr);
            var fld;
            var cells = grid.cellmap;
            for (fld in cells) {
                cellAttr = grid.cellmap[fld];
                if (cellAttr.original_field.indexOf(fldName) == 0) {
                    value = chNode.getValue().getItem(cellAttr.original_field);
                    gridfield = cellAttr.field;
                    currAttr[gridfield] = value;
                }
            }
            ;
            chNode.updAttributes(currAttr);
        }
        
        var idx = storebag.index(rowLabel);
        if(grid._filtered){
            idx = dojo.indexOf(grid._filtered,idx);
        }
        return idx;        
    },
    mixin_editBagRow: function(r, delay) {
        if(r==-1){
            r = this.storeRowCount()-1;
        }
        if(r==null){
            var r = this.selection.selectedIndex;
        }
        var rc = this.gridEditor.findNextEditableCell({row: r, col: -1}, {r:0, c:1});
        var grid = this;
        var ge = this.gridEditor;
        if (rc) {
            if(ge.remoteRowController){
                var d = new Date();
                this.sourceNode.watch('pendingRemoteController',
                        function(){return !ge._pendingRemoteController},
                        function(){
                            ge.startEdit(rc.row, rc.col);
                        },10);
            }
            else if (delay) {
                if (this._delayedEditing) {
                    clearTimeout(this._delayedEditing);
                }
                this._delayedEditing = setTimeout(function() {
                    ge.startEdit(rc.row, rc.col);
                }, delay);
            } else {
                ge.startEdit(rc.row, rc.col);
            }

        }
    },

    mixin_newBagRow: function(defaultArgs) {
        var defaultArgs = (this.gridEditor?this.gridEditor.getNewRowDefaults(defaultArgs) : defaultArgs) || {};
        var newRowDefaults = this.sourceNode.attr.newRowDefaults;
        var newrow;
        if (newRowDefaults) {
            if (typeof(newRowDefaults) == 'string') {
                newRowDefaults = funcCreate(newRowDefaults)();
            }
            newRowDefaults = genro.src.dynamicParameters(newRowDefaults);
            objectUpdate(defaultArgs, newRowDefaults);
        }
        var dataproviderNode = this.storebag().getParentNode();
        if ('newBagRow' in dataproviderNode) {
            if (defaultArgs instanceof Array) {
                result = [];
                for (var i = 0; i < defaultArgs.length; i++) {
                    result.push(this.newBagRow(defaultArgs[i]));
                }
                ;
                return result;
            }
            else {
                newrow = dataproviderNode.newBagRow(defaultArgs);
            }
        } else {
            if (defaultArgs instanceof Array) {
                result = [];
                for (var i = 0; i < defaultArgs.length; i++) {
                    result.push(this.newBagRow(defaultArgs[i]));
                }
                ;
                return result;
            }
            if (this.datamode == 'bag') {

                newrow = new gnr.GnrBagNode(null, 'label', new gnr.GnrBag(defaultArgs));
            } else {
                newrow = new gnr.GnrBagNode(null, 'label', null, defaultArgs);
            }
        }
        newrow.attr._newrecord=true;
        return newrow;
    },

    mixin_updateCounterColumn: function() {
        var storebag = this.storebag();
        var cb;
        var k = 1;
        var changes = [];
        var serializableChanges = [];
        var that = this;
        var counterField = this.sourceNode.attr.counterField;
        if (!counterField) {
            return;
        }
        if (this.datamode == 'bag' || this.gridEditor) {
            var ge = this.gridEditor;
            if(this.collectionStore && ge){
                //new gridEditor
                var cb = function(n){
                    ge.updateCounterColumn(n,k,counterField);
                    k++;
                }
            }
            else{
                cb = function(n) {
                    var row = n.getValue();
                    var oldk = row.getItem(counterField);
                    if (k != oldk) {
                        row.setItem(counterField, k);
                    }
                    k++;
                };
            }

        } else {
            cb = function(n) {
                var row = n.attr;
                var oldk = row[counterField];
                if (k != oldk) {
                    n.setAttribute(counterField, k);
                    changes.push({'node':n,'old':oldk,'new':k});
                    oldk = oldk || -1;
                    serializableChanges.push({'_pkey':that.rowIdentity(n.attr),'old':oldk,'new':k});
                }
                k++;
            };
        }
        storebag.forEach(cb, 'static');
        
        if(changes.length>0){
            var collectionStore = this.collectionStore;
            if(collectionStore){

                this.collectionStore().onCounterChanges(counterField,serializableChanges);
            }else{
                this.sourceNode.publish('counterChanges',{'changes':serializableChanges,'table':this.sourceNode.attr.table});
            }
        }
        return changes;
    },
    mixin_addBagRow: function(label, pos, newnode, event, nodupField) {
        var label = label || 'r_' + newnode._id;
        this.resetFilter();
        var storebag = this.storebag();
        if (nodupField) {
            var nodupValue;
            var colvalues = this.getColumnValues(nodupField);
            if (this.datamode == 'bag') {
                nodupValue = newnode.getValue().getItem(nodupField);
            } else {
                nodupValue = newnode.attr[nodupField];
            }
            if (dojo.indexOf(colvalues, nodupValue) != -1) {
                return;
            }
        }
        event = event || {};
        var addRowMode = this.sourceNode.attr.addRowMode;
        if(addRowMode){
            pos = addRowMode;
        }
        if (pos == '*') {
            var curSelRow = this.absIndex(this.selection.selectedIndex);
            if (curSelRow < 0) {
                pos = event.shiftKey ? 0 : '>';
            } else {
                pos = event.shiftKey ? curSelRow : curSelRow + 1;
            }
        }
        var kw = {'_position':pos};
        newnode = storebag.setItem(label, newnode, null, kw); //questa provoca la chiamata della setStorePath che ha trigger di ins.
        // ATTENZIONE: Commentato questo perchè il trigger di insert già ridisegna ed aggiorna l'indice, ma non fa apply filter.
        // Cambiare l'indice di selezione corrente nelle includedview con form significa cambiare datapath a tutti i widget. PROCESSO LENTO.

        //if(!this._batchUpdating){
        //this.applyFilter();
        //this.selection.select(kw._new_position);
        //alert('ex apply filter')
        //}
        this.updateCounterColumn();
        return newnode;
    },
    mixin_delBagRow: function(pos, many, params) {
        var pos = (pos == '*') ? this.absIndex(this.selection.selectedIndex) : pos;
        var storebag = this.storebag();
        var removed = [];
        if (many) {
            var selected = this.selection.getSelected();
            this.batchUpdating(true);
            this.loadingContent(true);
            var pos;
            for (var i = selected.length - 1; i >= 0; i--) {
                pos = this.absIndex(selected[i]);
                removed.push(storebag.popNode('#' + pos));
            }
            this.batchUpdating(false);
            this.loadingContent(false);

        } else {
            removed.push(storebag.popNode('#' + pos));
        }
        removed.reverse();
        this.filterToRebuild(true);
        this.updateCounterColumn();
        this.updateRowCount('*');
        var newpos = pos>0?pos-1:0;
        this.selection.select(newpos);

        //if(params.del_register){
        //    var path = '#parent.' + storebag.getParentNode().label + '_removed.';
        //    for (var i=0; i < removed.length; i++) {
        //        storebag.setItem(path + removed[i].label, removed[i].value, removed[i].attr, {'doTrigger':'_removedRow'});
        //    };
        //};

        var delpath;
        if (this.sourceNode.attr.delstorepath) {
            delpath = this.sourceNode.attr.delstorepath;
        } else {
            var storenode = storebag.getParentNode();
            if (storenode.label.indexOf('@') == 0) {
                delpath = storenode.getFullpath(null, true) + '_removed';
            }
        }
        if (delpath) {
            for (var i = 0; i < removed.length; i++) {
                if (!removed[i].attr._newrecord) {
                    genro._data.setItem(delpath + '.' + removed[i].label, removed[i].value, removed[i].attr, {'doTrigger':'_removedRow'});
                }
            }
        }
        return removed;
    },
    mixin_exportData:function(mode) {
        var mode = mode || 'csv';
        var meta = objectExtract(this.sourceNode.attr, 'meta_*', true);
        var pars = objectUpdate({'structbag':this.structbag(), 'storebag':this.storebag()}, meta);
        var curgrid = this;
        curgrid.loadingContent(true);
        genro.rpc.remoteCall(mode,
                pars,
                'bag', 'POST', null,
                            function(url) {

                                //var url = genro.rpc.rpcUrl("app.exportStaticGridDownload_"+mode, {filename:filename});
                                genro.download(url);
                                curgrid.loadingContent(false);
                            });
    },
    mixin_printData:function() {
        var meta = objectExtract(this.sourceNode.attr, 'meta_*', true);
        var pars = objectUpdate({'structbag':this.structbag(), 'storebag':this.storebag()}, meta);
        var curgrid = this;
        curgrid.loadingContent(true);
        genro.rpc.remoteCall('app.printStaticGrid',
                pars,
                'bag', 'POST', null,
                            function(url) {
                                //var url = genro.rpc.rpcUrl("app.printStaticGridDownload", {filename:filename});
                                genro.download(url, null, 'print');
                                curgrid.loadingContent(false);
                            });
    },
    mixin_structbag:function() {
        return genro.getData(this.sourceNode.absDatapath(structpath));
    },

    patch_dokeydown:function(e) {
        //prevent dojo onKeyDown
    },

    patch_doclick: function(e) {
        if (this.gnrediting) {
            dojo.stopEvent(e);
        } else {
            if (e.cellNode) {
                this.onCellClick(e);
            } else {
                this.onRowClick(e);
            }
        }
    }
});

dojo.declare("gnr.widgets.IncludedView", gnr.widgets.VirtualStaticGrid, {
    constructor: function(application) {
        //dojo.require("dojox.grid._data.editors");
        this._domtag = 'div';
        this._dojotag = 'VirtualGrid';
    },

    creating: function(attributes, sourceNode) {
        var savedAttrs = this.creating_common(attributes, sourceNode);
        this.creating_structure(attributes, sourceNode);
        sourceNode.registerDynAttr('storepath');
        attributes.query_columns = this.getQueryColumns(sourceNode, attributes.structBag);
        if (attributes.excludeListCb) {
            attributes.excludeListCb = funcCreate(attributes.excludeListCb);
        }
        return savedAttrs;
    },
    
    mixin_setEditableColumns:function(){
        var cellmap = this.cellmap;
        var batch_assign = false;
        for(var k in cellmap){
            if(cellmap[k].edit){
                if(cellmap[k].edit!==true && cellmap[k].edit.batch_assign){
                    batch_assign = true;
                }
                if(!this.gridEditor){
                    this.gridEditor = new gnr.GridEditor(this);
                }
                this.gridEditor.addEditColumn(cellmap[k].field,objectUpdate({},cellmap[k]));
            }else if(this.gridEditor){
                this.gridEditor.delEditColumn(cellmap[k].field);
            }
        }
        this.sourceNode.setRelativeData('.batchAssignEnabled',batch_assign);
    },
    
    
    mixin_setChangeManager:function(){
        var that = this;
        if(!this.structBag){
            return;
        }
        var getChangeManager = function(){
            if(!that.changeManager){
                that.changeManager = new gnr.GridChangeManager(that);
            }
            return that.changeManager;
        };
        var struct = this.structBag.getItem('#0.#0');
        var cellmap = this.cellmap;
        var cm = this.changeManager;
        if(cm){
            cm.initialize();
        }
        for(var k in cellmap){
            var cell = cellmap[k];
            var structNode = struct.getNode(cell._nodelabel);
            if(!structNode){
                continue;
            }
            var bagcellattr = structNode.attr;
            for(var p in bagcellattr){
                if(typeof(bagcellattr[p])=='string' && bagcellattr[p].indexOf('^') == 0){
                    getChangeManager().addDynamicCellPar(cell,p,bagcellattr[p].slice(1));
                }
            }
            if(cell.edit){
                var cm = getChangeManager()
                if(cell.edit.remoteRowController){
                    cm.addRemoteControllerColumn(cellmap[k].field,objectUpdate({},cellmap[k]));
                }
            }
            if(cell.formula){
                getChangeManager().addFormulaColumn(cellmap[k].field,objectUpdate({},cellmap[k]));
            }else if (this.changeManager){
                this.changeManager.delFormulaColumn(cellmap[k].field);
            }
            if(cell.totalize){
                var snode = genro.nodeById(this.sourceNode.attr.store+'_store');
                var virtualStore = snode.attr.selectionName && snode.attr.row_count;
                var selectionStore = snode.attr.method == 'app.getSelection';
                if(selectionStore && !cell.formula && !this.gridEditor){
                    this.sourceNode._serverTotalizeColumns[cell.field] = cell.totalize; //server totals
                }
                if(!virtualStore){
                    getChangeManager().addTotalizer(cellmap[k].field,objectUpdate({},cellmap[k]));
                }
            }else if (this.changeManager){
                this.changeManager.delTotalizer(cellmap[k].field);
            }
        }
        if(this.changeManager){
            this.changeManager.registerParameters();
        }
    },


    getQueryColumns:function(sourceNode, structure) {
        var columns = gnr.columnsFromStruct(structure);
        if (sourceNode.attr.hiddencolumns) {
            columns = columns + ',' + sourceNode.attr.hiddencolumns;
        }
        if (columns) {
            sourceNode.setRelativeData(sourceNode.gridControllerPath + '.columns', columns);
        }
        return columns;
    },
    mixin_onCheckedColumn:function(idx,fieldname,evt) {
        if(this.sourceNode.attr.parentForm!==false && this.sourceNode.form && this.sourceNode.form.isDisabled()){
            return;
        }
        var kw = this.cellmap[fieldname];   
        if(kw===true){
            kw = {};
        }
        var rowIndex = this.absIndex(idx);
        var rowpath = '#' + rowIndex;
        var sep = this.datamode=='bag'? '.':'?';
        var storebag = this.storebag();
        var valuepath = rowpath+sep+kw.original_field;
        var checked = storebag.getItem(valuepath);
        var selectedIdx;
        if (kw.radioButton===true){
            selectedIdx = [idx];
        }else{
            selectedIdx = this.getSelectedRowidx();
            if(selectedIdx.indexOf(idx)<0){
                selectedIdx = [idx];
            }
        }
        var that = this;
        selectedIdx.forEach(function(idx){
            that.onCheckedColumn_one(idx,fieldname,checked,kw,evt);
        });
    },

    mixin_onCheckedColumn_one:function(idx,fieldname,checked,cellkw,evt) {
        var rowIndex = this.absIndex(idx);
        var grid = this;
        var rowpath = '#' + rowIndex;
        var sep = this.datamode=='bag'? '.':'?';
        var valuepath = rowpath+sep+cellkw.original_field;
        var storebag = this.storebag();
        var currNode = storebag.getNode(rowpath);
        var checked = storebag.getItem(valuepath);
        var checkedField = cellkw.checkedField || this.rowIdentifier();
        var checkedRowClass = cellkw.checkedRowClass;
        var action = cellkw.action;
        var action_delay = cellkw.action_delay;
        var sourceNode = this.sourceNode;
        var gridEditor = this.gridEditor;
        var cellsetter;
        var currpath;
        var changedFields = [];
        if(gridEditor){
            cellsetter = function(idx,cellname,value){
                gridEditor.setCellValue(idx,cellname,value);
            }
        }else{
            cellsetter = function(idx,cellname,value){
                currpath = '#'+grid.absIndex(idx)+sep+cellname;
                storebag.setItem(currpath,value,null,{lazySet:true});
            }
        }
        if (currNode.attr.disabled) {
            return;
        }
        var newval = !checked;
        if(cellkw.radioButton){
            if(checked && !evt.shiftKey){
                return;
            }
            if(cellkw.radioButton===true){
                var oldcheckedpath; 
                for (var i=0; i<storebag.len(); i++){
                    oldcheckedpath = '#'+i+sep+fieldname;
                    if(storebag.getItem(oldcheckedpath)){
                        if(gridEditor){
                            gridEditor.setCellValue(i,fieldname,false);
                        }else{
                            storebag.setItem(oldcheckedpath,false,null,{lazySet:true});
                        }
                        break;
                    }
                }
                cellsetter(idx,fieldname,true);
            }else{
                for (var c in this.cellmap){
                    var s_cell = this.cellmap[c];
                    if(s_cell.radioButton==cellkw.radioButton){
                        changedFields.push(s_cell.original_field);
                        cellsetter(idx,s_cell.original_field,(fieldname==s_cell.original_field) && !evt.shiftKey);
                    }
                }
            }



        }else{
            cellsetter(idx,cellkw.original_field,!checked);
        }
        if(cellkw.checkedId){
            var checkedKeys = this.getCheckedId(fieldname,checkedField) || '';
            setTimeout(function(){
                sourceNode.setRelativeData(cellkw.checkedId,checkedKeys,null,null,sourceNode);
            },1);
        }
        var gridId = this.sourceNode.attr.nodeId;
        if (gridId) {
            genro.publish(gridId + '_row_checked', currNode.label, newval, currNode.attr);
        }
        if (action){
            var changedRow = this.rowByIndex(rowIndex);
            var changedKey = changedRow[checkedField];
            var changedValue = changedRow[fieldname];
            var actionKw = {_idx:rowIndex,_row:changedRow,_fields:changedFields};
            actionKw[changedKey] = changedValue;
            if (!action_delay){
                action.call(this.sourceNode,actionKw);
            }else{
                if(sourceNode._pendingCheck){
                    clearTimeout(sourceNode._pendingCheck);
                    var changes = sourceNode._pendingChanges;
                    if(changedKey in changes){
                        objectPop(changes,changedKey);
                    }else{
                        changes[changedKey] = changedValue;
                    }
                }else{
                    sourceNode._pendingChanges = actionKw;
                }
                sourceNode._pendingCheck = setTimeout(function(){
                    sourceNode._pendingCheck = null;
                    if(objectNotEmpty(sourceNode._pendingChanges)){
                        action.call(sourceNode,sourceNode._pendingChanges);
                    }
                }, action_delay);    
            }
        }
    },
    mixin_addCheckBoxColumn:function(kw) {
        //kw = this.gnr.getCheckBoxKw(kw, this.sourceNode);
        this.gnr.addCheckBoxColumn(kw, this.sourceNode);
        this.gnr.setCheckedIdSubscription(this.sourceNode,kw);
    },
    addCheckBoxColumn:function(kw, sourceNode) {
        var celldata = this.getCheckBoxKw(kw, sourceNode);
        var structbag = sourceNode.getRelativeData(sourceNode.attr.structpath);
        var position = objectPop(kw,'position') || 0;
        genro.callAfter(function(){
            structbag.setItem('view_0.rows_0.cell_'+celldata.field, null, celldata, {_position:position});
        },1);
    },


    setCheckedIdSubscription:function(sourceNode,kw){
        if(kw.checkedId && !sourceNode.attr.checkedId){
            sourceNode.attr.checkedId = kw.checkedId;
            sourceNode.registerDynAttr('checkedId');
            var checkedIdPath = kw.checkedId;
            var fieldname = kw.field;
            var checkedField = kw.checkedField;
            sourceNode.subscribe('onNewDatastore',function(){
                var checkedInStore = sourceNode.widget.getCheckedId(fieldname,checkedField);
                if(typeof(getCheckedId)=='string'){
                    sourceNode.setRelativeData(checkedIdPath,checkedInStore,null,null,sourceNode);
                }else{
                    genro.callAfter(function(){
                        sourceNode.widget.setCheckedId(checkedIdPath,kw);
                    },1);
                }
            });
            if(kw.checkedOnRowClick){
                dojo.connect(sourceNode.widget,'onRowClick',function(e){
                    sourceNode.widget.onCheckedColumn(e.rowIndex,fieldname,e);
                });
            }
        }
    },
    getCheckBoxKw:function(kw, sourceNode,celldata) {
        var kw = kw || {};
        var celldata = celldata || {};
        var fieldname =  kw.field || celldata['field'] || '_checked';
        var radioButton = kw.radioButton || false;
        celldata['field'] = fieldname;
        celldata['name'] =  kw.name ||  celldata.name ||  ' ';
        celldata['dtype'] = 'B';
        celldata['width'] = celldata.width || '20px';
        celldata['radioButton'] = radioButton;
        celldata['format_trueclass'] = kw.trueclass || (radioButton?'radioOn':'checkboxOn'); //mettere classi radio
        celldata['classes'] = kw.classes || 'row_checker';
        celldata['format_falseclass'] = kw.falseclass || (radioButton?'radioOff':'checkboxOff'); //mettere classi radio
        celldata['calculated'] = kw.calculated;
        celldata['checkedId'] = kw.checkedId;
        celldata['checkedField'] = kw.checkedField;
        celldata['action'] = kw.action ? funcCreate(kw.action,'changes',sourceNode):null;
        celldata['action_delay'] = kw.action_delay;
        if (kw.remoteUpdate && sourceNode.attr.table){
            celldata.action = function(changes){
                genro.serverCall("app.updateCheckboxPkeys",{table:sourceNode.attr.table,field:fieldname,changesDict:changes});
            };
            celldata['action_delay'] = typeof(kw.remoteUpdate)=='number'?kw.remoteUpdate:1000;
        }
        celldata['format_onclick'] = "this.widget.onCheckedColumn(kw.rowIndex,'"+fieldname+"',e)";
        return celldata;
    },
    mixin_getCheckedId:function(fieldname,checkedField){
        checkedField = checkedField || this.rowIdentifier();
        var checkedIdList = [];
        var that = this;
        var row;
        var instore = false;
        
        this.storebag().forEach(function(n){
            row = that.rowFromBagNode(n);
            if(fieldname in row){
                instore = true;
            }
            if(row[fieldname]){
                checkedIdList.push(row[checkedField]);
            }
        },'static');
        return instore?checkedIdList.join(','):false;
        
    },
    mixin_setCheckedId:function(path,kw,trigger_reason){
        var value = this.sourceNode.getRelativeData(path);
        if(typeof(value)!='string'){
            return;
        }
        var pkeys= value?value.split(','):[];
        var datamodeBag = this.datamode=='bag';
        var checkedField = kw.checkedField || this.rowIdentifier();
        var fieldname = kw.field || '_checked';
        var grid = this;
        var v;
        this.storebag().forEach(function(n){
            var row = grid.rowFromBagNode(n);
            var pkey = row[checkedField];
            v = dojo.indexOf(pkeys,pkey)>=0? true:false;
            if(datamodeBag){
                n.getValue('static').setItem(fieldname,v);
            }else{
                var newattr = {};
                newattr[fieldname] = v;
                n.updAttributes(newattr);
            }
        },'static');
        
        
    },
    mixin_serverAction:function(kw){
        var options = objectPop(kw,'opt');
        var method = objectPop(options,"method") || "app.includedViewAction";
        var kwargs = objectUpdate({},options);
        kwargs['action'] = objectPop(kw,'command');
        kwargs['data'] = this.storebag();
        kwargs['datamode'] = this.datamode;
        kwargs['struct'] = this.structbag();
        var cb = function(result){
            genro.download(result);
        };
        kwargs['meta'] = objectExtract(this.sourceNode.attr, 'meta_*', true);
        genro.rpc.remoteCall(method, kwargs, null, 'POST', null,cb);
    },
    
    created: function(widget, savedAttrs, sourceNode) {
        this.created_common(widget, savedAttrs, sourceNode);
        var selectionId = sourceNode.attr['selectionId'] || sourceNode.attr.nodeId + '_store';
        widget.autoSelect = sourceNode.attr['autoSelect'];
        if (typeof(widget.autoSelect) == 'string') {
            widget.autoSelect = funcCreate(widget.autoSelect, null, widget);
        }
        widget.linkedSelection = genro.nodeById(selectionId);
        genro.src.onBuiltCall(dojo.hitch(widget, 'render'));
        //dojo.connect(widget, 'onSelected', widget,'_gnrUpdateSelect');
        dojo.connect(widget, 'modelAllChange', dojo.hitch(sourceNode, this.modelAllChange));

        if (sourceNode.attr.editbuffer) {
            sourceNode.registerDynAttr('editbuffer');
        }
        if (sourceNode.attr.multiSelect == false) {
            widget.selection.multiSelect = false;
        }
        //widget.rpcViewColumns();
        var addCheckBoxColumn = sourceNode.attr.addCheckBoxColumn;
        if (addCheckBoxColumn) {
            var kw = addCheckBoxColumn == true ? null : addCheckBoxColumn;
            widget.addCheckBoxColumn(kw);
        }
        widget.updateRowCount('*');
    },
    mixin_structbag:function() {
        //return genro.getData(this.sourceNode.absDatapath(structpath));
        return genro.getData(this.sourceNode.absDatapath(this.sourceNode.attr.structpath));
    },
    mixinex_structbag:function() {
        var structure = this.sourceNode.getValue();
        if (structure) {
            structure = structure.getItem('struct');
        } else {
            structure = genro.getData(this.sourceNode.absDatapath(this.sourceNode.attr.structpath));
        }
        return structure;
    },

    mixin_loadingContent:function(flag) {
        var scrollnode = dojo.query('.dojoxGrid-scrollbox', this.domNode)[0];
        var contentnode = dojo.query('.dojoxGrid-content', this.domNode)[0];
        if (flag) {
            if (scrollnode) {
                genro.dom.addClass(scrollnode, 'waiting');
            }
            ;
            if (contentnode) {
                genro.dom.addClass(contentnode, 'dimmed');
            }
            ;
        } else {
            if (scrollnode) {
                genro.dom.removeClass(scrollnode, 'waiting');
            }
            ;
            if (contentnode) {
                genro.dom.removeClass(contentnode, 'dimmed');
            }
            ;
        }
    },
    mixin_deleteSelectedRows:function(){
        
        this.delBagRow('*', true);
        
        this.sourceNode.publish('onDeletedRows');
    },

    mixin_addRows:function(counterOrSource,evt,duplicate,onEditNode){
        if(duplicate && !this.gridEditor){
            var pkeys = this.getSelectedPkeys();
            this.collectionStore().duplicateRows(pkeys);

            return;
        }
        if(this.sourceNode.attr.defaultPrompt){
            var defaultPrompt = this.sourceNode.attr.defaultPrompt;
            if(typeof(counterOrSource)=='number'){
                counterOrSource = {};
            }
            var that = this;
            genro.dlg.prompt(defaultPrompt.title || _T('Fill parameters'),{
                widget:defaultPrompt.fields,
                action:function(result){
                    objectUpdate(counterOrSource,result.asDict());
                    that.addRowsDo([counterOrSource],evt,duplicate,onEditNode);
                }
            });
            return;
        }
        this.addRowsDo(counterOrSource,evt,duplicate,onEditNode);
    },

    mixin_addRowsDo(counterOrSource,evt,duplicate,onEditNode){
        var addrow_kwargs = this.sourceNode.evaluateOnNode(objectExtract(this.sourceNode.attr,'addrow_*',true));
        var source = [];
        counterOrSource = counterOrSource || 1;
        if(!(counterOrSource instanceof Array)){
            for(var i=0; i<counterOrSource; i++){
                source.push(null);
            }
        }else{
            source = counterOrSource;
        }
        var firstRow;
        var that = this;
        if(duplicate){
            var sel = this.selection.getSelected();
            var row;
            var identifier = this.rowIdentifier();
            sel.forEach(function(n){
                row = that.rowByIndex(n);
                objectPop(row,identifier);
                that.addBagRow('#id', null, that.newBagRow(row),evt)
            });
        }else{
            var that = this;
            source.forEach(function(dflt){
                firstRow = firstRow || that.addBagRow('#id', addrow_kwargs.position || '*', that.newBagRow(dflt),evt);
            });
        }
        this.sourceNode.publish('onAddedRows');
        if(!duplicate){
            var doEdit = true;
            if(onEditNode){
                doEdit=onEditNode(firstRow);
            }
            if(this.gridEditor && doEdit!==false){
                this.editBagRow(this.storebag().index(firstRow.label));
            }
        }
        return firstRow;
    },

    mixin_batchUpdating: function(state) {
        this._batchUpdating = state;
    },
    mixin_setEditorEnabled: function(enabled) {
        this.editorEnabled = enabled;
    }

   //mixin_rpcViewColumns: function() {
   //    if ((this.relation_path) && (this.relation_path.indexOf('@') == 0)) {
   //        genro.rpc.remoteCall('setViewColumns', {query_columns:this.query_columns,
   //            contextName:this.sqlContextName,
   //            contextTable:this.sqlContextTable,
   //            relation_path:this.relation_path});
   //    }
   //}
});

dojo.declare("gnr.widgets.NewIncludedView", gnr.widgets.IncludedView, {
    mixin_rowByIndex:function(inRowIndex,bagFields,ignoreFilter){
        var store = this.collectionStore();
        if(ignoreFilter){
            return this.rowFromBagNode(store.getItems()[inRowIndex],bagFields);
        }
        return store.rowByIndex(inRowIndex,bagFields);
    },

    mixin_absIndex:function(idx,reverse){
         return this.collectionStore().absIndex(idx,reverse);
    },
    mixin_rowFromBagNode:function(node,bagFields) {
        return this.collectionStore().rowFromItem(node,bagFields);
    },
    mixin_rowBagNodeByIdentifier:function(identifier){
        return this.collectionStore().rowBagNodeByIdentifier(identifier);
    },
    mixin_setStoreBlocked:function(reason,doset){
        this.collectionStore().setBlockingReason(reason,doset);
    },

    mixin_setSelectedId: function(pkey) {
        var nrow = this.rowCount;
        if (nrow == 0 || isNullOrBlank(pkey)) {
            this.selection.unselectAll();
        } else {
            var idx = this.collectionStore().getIdxFromPkey(pkey);
            if (idx >= nrow) {
                idx = nrow - 1;
            }
            this.selection.select(idx);
        }
    },

    mixin_configuratorPalette:function(){
        if(this.sourceNode.attr.configurable && genro.grid_configurator){
            genro.grid_configurator.configuratorPalette(this.sourceNode.attr.nodeId || this.sourceNode._id);
        }
    },


    mixin_configuratorColsetTooltip:function(colset,event){
        if(this.sourceNode.attr.configurable && genro.grid_configurator){
            genro.grid_configurator.configuratorColsetTooltip(this.sourceNode.attr.nodeId || this.sourceNode._id,colset,event);
        }
    },

    mixin_configuratorCellTooltip:function(event){
        if(this.sourceNode.attr.configurable && genro.grid_configurator){
            genro.grid_configurator.configuratorCellTooltip(this.sourceNode.attr.nodeId || this.sourceNode._id,event.cell,event.target);
        }
    },


    mixin_setDynamicStorepath:function(newstorepath){
        newstorepath = newstorepath || '.store';
        var store = this.collectionStore();
        store.setNewStorepath(newstorepath);
    },

    mixin_absStorepath:function(){
        return this.collectionStore().storepath;
    },

    mixin_getSelectedRowidx: function() {
        var sel = this.selection.getSelected();
        if(!this._virtual){
            return sel.sort();
        }
        var result = [];
        for (var i = 0; i < sel.length; i++) {
            var row = this.rowByIndex(sel[i]);
            result.push(row.rowidx);
        }
        return result.sort();
    },

    mixin_cellCurrentDatapath:function(path,inRowIndex){
        inRowIndex = inRowIndex==null?this.currRenderedRowIndex:inRowIndex; 
        var node = this.collectionStore().itemByIdx(inRowIndex);
        genro.assert(node,'missing storenode');
        return path.replace('#ROW.',node.getFullpath(null,genro._data)+'~')
    },

    mixin_rowIdByIndex:function(inRowIndex){
        if(inRowIndex!==null){
            return this.rowIdentity(this.rowByIndex(inRowIndex));
        }
    },

    mixin_getRowEditor:function(kw){
        var rowId = kw.rowId;
        if(!rowId){
            if(kw.rowIndex){
                rowId = this.rowIdByIndex(kw.rowIndex);
            }else{
                rowId = this.rowIdentity(kw.row);
            }
        }
        var rowNode = this.rowBagNodeByIdentifier(rowId);
        if(rowNode){
            return rowNode._rowEditor;
        }
    },


    mixin_filteredRowsIndex:function(filteringObject){
        return this.collectionStore().filteredRowsIndex(filteringObject);
    },

    mixin_groupColumnsSelect:function(inIndex,columns){
        var selection = this.selection;
        selection.unselectAll(inIndex);
        var baserow = this.rowByIndex(inIndex);
        var groupRows = this.filteredRowsIndex(objectExtract(baserow,columns));
        selection.beginUpdate();
        dojo.forEach(groupRows,function(idx){
            selection.addToSelection(idx);
        })
        selection.endUpdate();
    },
    
    mixin_fillServerTotalize:function(){
        var totalizeColumns = this.sourceNode._serverTotalizeColumns;
        if(!objectNotEmpty(totalizeColumns)){
            return;
        }
        var data = this.storebag();
        var result_attr = data.getParentNode().attr;
        for(var field in totalizeColumns){
            var sfield = 'sum_'+field;
            if(sfield in result_attr){
                this.sourceNode.setRelativeData(totalizeColumns[field],result_attr[sfield]);
            }
        }
    },

    mixin_indexByCb:function(cb, backward) {
        return this.collectionStore().indexByCb(cb, backward);
    },

    mixin_storeRowCount: function(all) {
        return this.collectionStore().len(!all);
    },
    
    mixin_storebag:function(filtered){
        return this.collectionStore().getData(filtered);
    },

    mixin_masterEditColumn:function(){
        if (this.sourceNode.attr.masterColumn){
            return this.sourceNode.attr.masterColumn;
        }
        var colinfo = this.getColumnInfo();
        var colnodes = colinfo.getNodes()
        var item,n;
        for(var i=0; i<colnodes.length; i++){
            item = colnodes[i].attr;
            if(!item.isHidden && item.cell.edit){
                return item.cell.field;
            }
        }
    },


    mixin_autoInsertHandler:function(){
        var data = this.storebag();
        var lastidx = data.len()-1;
        var masterEditColumn = this.masterEditColumn();
        var emptyRowCb = function(n){
            var result = isNullOrBlank(n.getValue().getItem(masterEditColumn));
            return result;
        };
        if(this.isFocused && !(lastidx>=0 && emptyRowCb(data.getNode('#'+lastidx)))){
            return data.setItem('#id',this.newBagRow(),null,{doTrigger:'autoRow'});
        }
        else if(!this.isFocused && !this.gnrediting){
            var idxToDel = [lastidx];
            if(this.autoDelete){
                idxToDel = data.getNodes().map(function(n,idx){
                    return emptyRowCb(n)?idx:-1});
            }
            idxToDel.filter(function(idx){return idx>=0}).sort(function(a,b){return b>a?1:-1}).forEach(function(idx){
                data.popNode('#'+idx,'autoRow');
            });
        }
    },

    mixin_toggleLineNumberColumn:function(kw) {
        let currShow = this.sourceNode.getRelativeData(this.sourceNode.attr.structpath+'.info.showLineNumber');
        this.sourceNode.setRelativeData(this.sourceNode.attr.structpath+'.info.showLineNumber',!currShow);
    },

    mixin_addNewSetColumn:function(kw) {
        this.gnr.addNewSetColumn(this.sourceNode,kw);;
    },

    addNewSetColumn:function(sourceNode,kw) {
        var position = objectPop(kw,'position') || 0;
        var celldata = this.getNewSetKw(sourceNode,kw);
        
        genro.callAfter(function(){
            var structbag = sourceNode.getRelativeData(sourceNode.attr.structpath);
            structbag.setItem('view_0.rows_0.cell_'+celldata.field, null, celldata, {_position:position});
        },1);
    },

    mixin_setUserSets:function(v,kw){
        this.updateRowCount();
    },

    getNewSetKw:function(sourceNode,celldata) {
        var celldata = celldata || {};
        var fieldname =  celldata['field'] || '_set_'+genro.getCounter();
        var radioButton = objectPop(celldata,'radioButton') || false;
        celldata['field'] = fieldname;
        celldata['name'] =  celldata.name ||  ' ';
        celldata['dtype'] = 'B';
        celldata['width'] = celldata.width || '20px';
        celldata['radioButton'] = radioButton;
        celldata['format_trueclass'] = objectPop(celldata,'trueclass')|| (radioButton?'radioOn':'checkboxOn'); //mettere classi radio
        celldata['classes'] = celldata.classes || 'row_checker';
        celldata['format_falseclass'] = objectPop(celldata,'falseclass')|| (radioButton?'radioOff':'checkboxOff'); //mettere classi radio
        celldata['calculated'] = true;
        celldata['checkedId'] = sourceNode.attr.userSets+'.'+fieldname;
        if(celldata['userSets_caption']){
            celldata['checkedCaption'] = sourceNode.attr.userSets+'_caption.'+fieldname;
        }
        var identifier = sourceNode.widget?sourceNode.widget.rowIdentifier():sourceNode.attr.identifier; //widget could be not already created
        celldata['checkedField'] = celldata['checkedField'] || identifier || '_pkey';
        celldata['userSets'] = true;    
        celldata['format_onclick'] = "this.widget.onChangeSetCol(kw.rowIndex,'"+fieldname+"',e)";
        celldata['_customGetter'] = celldata['_customGetter'] || function(rowdata,rowIdx){
            return sourceNode._usersetgetter(this.field,rowdata,rowIdx)
        };
        return celldata;
    },

    mixin_onChangeSetCol:function(rowIndex,fieldname,e){
        dojo.stopEvent(e);
        var changeset=function(currSet,elements,ischecked){
            dojo.forEach(elements,function(element){
                var m = currSet.match(new RegExp('(^|,)'+element+'($|,)'));
                if(ischecked){
                    if(m){
                        currSet = currSet.replace(m[0],(m[1]+m[2])==',,'?',':'');
                    }
                }else if(!m){
                    currSet = currSet?currSet+','+element:element;
                }
            });
            return currSet;
        }
        var modifiers = genro.dom.getEventModifiers(e);
        var structbag = this.sourceNode.getRelativeData(this.sourceNode.attr.structpath);
        var kw = this.cellmap[fieldname];   
        var store = this.collectionStore();
        //var rowIndex = this.absIndex(rowIndex);
        var node = store.itemByIdx(rowIndex);
        var currSet = this.sourceNode.getRelativeData(kw['checkedId']) || '';
        var currSetCaption = this.sourceNode.getRelativeData(kw['checkedCaption']) || '';
        var checkedElement = node.attr[kw['checkedField']];
        var ischecked = currSet.match(new RegExp('(^|,)'+checkedElement+'($|,)'))!=null;
        var pkeys;
        var caption_field = kw['userSets_caption'];
        var pl = [];
        var cl = [];
        if(modifiers=='Shift'){
            pkeys = this.getAllPkeys(caption_field);   
        }else{
            pkeys = this.getSelectedPkeys(caption_field);
        }
        if(caption_field){
           pkeys.forEach(function(n){pl.push(n.pkey);cl.push(n.caption)});
           pkeys = pl;
        }
        if(modifiers!='Shift' && (dojo.indexOf(pkeys,checkedElement)<0)){
            pkeys = [checkedElement];  
            if(caption_field){
                cl = [node.attr[caption_field]]
            }         
        }  
        if(!ischecked){
            var group = kw['userSets_group'];
            if(group){
                var relatedcell;
                var pset;
                var cset;
                for (var c in this.cellmap){
                    relatedcell = this.cellmap[c];
                    if(relatedcell.userSets_group==group && c!=fieldname){
                        pset = this.sourceNode.getRelativeData(relatedcell['checkedId']);
                        if(pset){
                            this.sourceNode.setRelativeData(relatedcell['checkedId'],changeset(pset,pkeys,true));
                        }
                        if(relatedcell.userSets_caption){
                            cset = this.sourceNode.getRelativeData(relatedcell['checkedCaption']);
                            if(cset){
                                this.sourceNode.setRelativeData(relatedcell['checkedCaption'],changeset(cset,cl,true));
                            }
                        }
                    }
                }
            }
        }
        this.sourceNode.setRelativeData(kw['checkedId'],changeset(currSet,pkeys,ischecked));
        if(caption_field){
            this.sourceNode.setRelativeData(kw['checkedCaption'],changeset(currSetCaption,cl,ischecked));
        }
    },

    patch_sort: function() {  
        var sortInfo = this.sortInfo;
        var order;
        if (sortInfo < 0) {
            order = 'd';
            sortInfo = -sortInfo;
        } else {
            order = 'a';
        }
        var cell = this.layout.cells[sortInfo - 1];
        var sortedBy = cell.field_getter + ':' + order;
        this.sourceNode.publish('setSortedBy',sortedBy);
        if ('sortedBy' in this.sourceNode.attr){
            var sortpath = this.sourceNode.attr['sortedBy'];
            if (this.sourceNode.isPointerPath(sortpath)){
                this.sourceNode.setAttributeInDatasource('sortedBy',sortedBy)
            }   
        }
        this.sortStore(sortedBy);      
    },
        
    mixin_setSortedBy:function(sortedBy){
        if (sortedBy.indexOf(':')<0){
            sortedBy+=':a';
        }   
        var s = sortedBy.split(':');
        var sortIndex = this.layout.cells.map(function(c){return c.field}).indexOf(s[0]);
        if(sortIndex>=0){
            this.setSortIndex(sortIndex,s[1][0]=='a');
        }
    },

    mixin_sortStore:function(sortedBy) {
        var store = this.collectionStore();
        if(!sortedBy){
            var storeSortedBy = store.storeNode.getAttributeFromDatasource('sortedBy');
            if(store.storeNode && storeSortedBy==this.sortedBy){
                //store is already sorted by the server
                return;
            }
            sortedBy = this.sortedBy || storeSortedBy;
        }
        this.sortedBy = sortedBy;
        store.sortedBy = sortedBy;
        if (this._virtual){
            var rowcount = this.rowCount;
            this.updateRowCount(0);
            store.clearBagCache();
            this.updateRowCount(rowcount);
        }
        else{
            store.sort();
            store.filterToRebuild(true);
            this.updateRowCount('*');
        }
        this.pendingSort = false;
    },
    mixin_refreshSort:function(){
        this.setSortedBy(this.sortedBy);
    },

    mixin_collectionStore:function(){
        if(!this._collectionStore){
            var storeNode = genro.nodeById(this.sourceNode.attr.store+'_store');
            this._collectionStore = storeNode.store;
            var that = this;
            storeNode.subscribe('updateRows',function(){
                var wasfocused = that._focused;
                that.updateRowCount();
            });
            
            var store = this._collectionStore;
            this._virtual = store.storeType=='VirtualSelection';
            if(this._virtual){
                this.domNode.addEventListener("scroll", function(e) { 
                    var lastRow = that.scroller.lastVisibleRow;
                    if(store._scroll_timeout){
                        clearTimeout(store._scroll_timeout);
                    }else{
                        store.isScrolling=true;
                    }
                    store._scroll_timeout=setTimeout(function(){
                        store.isScrolling=false;
                        store._scroll_timeout=null;
                        if(lastRow!=that.scroller.lastVisibleRow){
                            storeNode.publish('updateRows');
                        }
                    },50);
            }, true);
            }
        }
        if(this.sortedBy){
            this._collectionStore.sortedBy = this.sortedBy;
        }
        return this._collectionStore;
    },
    mixin_currentSelectionPars:function(){
        var kw = {};
        var store = this.collectionStore();
        if(store.storeType=='VirtualSelection'){
            kw.selectionName = store.selectionName;
        }else if(store.storeType=='Selection' && !store.storeNode.attr.groupByStore){
            kw.selectedPkeys = this.getSelectedPkeys() || [];
            if (kw.selectedPkeys.length==0){
                kw.selectedPkeys = this.getAllPkeys();
            }else if(kw.selectedPkeys.length==1){
                kw.allPkeys = this.getAllPkeys();
            }
        }else{
            kw.currentData = this.currentData(null,true);
            if(this.getSelectedRowidx()==1){
                kw.allGridData = this.storebag().deepCopy();
            }
        }
        if(this.cellmap._selected){
            kw.selectedPkeys = this.sourceNode.getRelativeData('.sets._selected');
        }else{
            kw.selectedRowidx = this.getSelectedRowidx();
        }
        kw.selectionCount = store.len(true);
        return kw;
    },

    mixin_createFiltered:function(currentFilterValue,filterColumn,colType){
        return this.collectionStore().createFiltered(this,currentFilterValue,filterColumn,colType);
    },

    mixin_getSelectedNodes: function() {
        var sel = this.selection.getSelected();
        var result = [];
        var store = this.collectionStore();
        if(!store || !store.len(true)){
            return result;
        }
        var n;
        for (var i = 0; i < sel.length; i++) {
            n = store.itemByIdx(sel[i]);
            if(n){
                result.push(n);
            }
        }
        return result;
    },
    
    mixin_deleteSelectedRows:function(){
        var pkeys = this.getSelectedPkeys();
        var protectPkeys;
        if(this.collectionStore().allowLogicalDelete){
            protectPkeys = this.getSelectedProtectedPkeys();
        }
        if(this.gridEditor){
            this.gridEditor.deleteSelectedRows(pkeys,protectPkeys);
            this.sourceNode.publish('onDeletedRows');
        }else{
            var store = this.collectionStore();
            if (store.askToDelete){
                store.deleteAsk(pkeys,protectPkeys);
            }else{
                store.deleteRows(pkeys,protectPkeys);
            }
            
        }
    },

    mixin_archiveSelectedRows:function(kw){
        var pkeys = this.getSelectedPkeys();
        var protectPkeys;
        if(this.collectionStore().allowLogicalDelete){
            protectPkeys = this.getSelectedProtectedPkeys();
        }
        this.collectionStore().archiveAsk(pkeys,protectPkeys);
            
    },
    
    mixin_filterToRebuild: function(value) {
        return this.collectionStore().filterToRebuild(value);
    },
    mixin_invalidFilter: function() {
        return this.collectionStore().invalidFilter();
    },
    mixin_resetFilter: function(value) {
        this.sourceNode.setRelativeData('.filtered_totalize',null);
        this.setClass('gridFilterActive',false);
        return this.collectionStore().resetFilter();
    },

    mixin_isFiltered:function(){
        return this.collectionStore().isFiltered();
    },
    
    
    mixin_currentData:function(nodes, rawData,filtered){
        var nodes = nodes || (this.getSelectedRowidx().length<1?'all':'selected');
        var result = new gnr.GnrBag();
        var nodes;
        if (rawData===true){
            var filtered = this.collectionStore()._filtered || [];
            if(nodes=='all'){
                nodes = this.collectionStore().getData().getNodes();
            }else if(nodes=='selected'){
                nodes = this.getSelectedNodes();
            }
            nodes.forEach(function(n,idx){
                if(filtered.length == 0 || filtered.indexOf(idx)>=0){
                    result.addItem(n.label,n);
                }
            });
        }else{
            var col_fields = this.structbag().getItem('#0.#0').digest('#a.field,#a.hidden');
            var col_names = [];
            dojo.forEach(col_fields, function(c){if(!c[1]) col_names.push(c[0].replace(/\W/g, '_'))});
            var col_length = col_fields.length;
            var selector = nodes=='selected'?'.dojoxGrid-view .dojoxGrid-row-selected .dojoxGrid-cell':'.dojoxGrid-view .dojoxGrid-cell';
            var cells = dojo.query(selector, this.domNode);
            var curr_row = 0;
            var cell_attrs = {};
            var cell_idx;
            for (var i=0;i<cells.length;i++){
                var cell = cells[i];
                cell_idx = i%col_length;
                cell_attrs[col_names[cell_idx]]=cell.childNodes[0].innerHTML.replace('&nbsp;','');
                if ((i+1)%col_length==0){
                    result.addItem('r_'+curr_row, null, cell_attrs);
                    cell_attrs = {};
                    curr_row += 1;
                }
            }
        }
        return result;
    },

    mixin_serverAction:function(kw){
        var options = objectPop(kw,'opt');
        var allRows = objectPop(options,'allRows');
        var method = objectPop(options,"method") || "app.includedViewAction";
        var kwargs = objectUpdate({},options);
        var useRawData = options['rawData']===true;
        kwargs['action'] = objectPop(kw,'command');
        var sourceNode = this.sourceNode;
        genro.lockScreen(true,sourceNode.getStringId());

        if (this.collectionStore().storeType=='VirtualSelection'){
            kwargs['selectionName'] = this.collectionStore().selectionName;
            kwargs['selectedRowidx'] = allRows?[]:this.getSelectedRowidx();
        }else{
            kwargs['data'] = this.currentData(allRows?'all':null , useRawData,true);
        }
        kwargs['table'] =this.sourceNode.attr.table;
        kwargs['datamode'] = useRawData?this.datamode:'attr';
        kwargs['struct'] =  this.getExportStruct();
        kwargs['_sourceNode'] = sourceNode;
        var cb = function(result){
            genro.lockScreen(false,sourceNode.getStringId());
            genro.download(result);
        };
        kwargs['meta'] = objectExtract(this.sourceNode.attr, 'meta_*', true);
        genro.rpc.remoteCall(method, kwargs, null, 'POST', null,cb);
    },
    mixin_getExportStruct:function(){
        var struct = this.structbag().deepCopy();
        var cells = struct.getItem('#0.#0');
        var sourceNode = this.sourceNode;

        var headerList = dojo.query('th',this.viewsHeaderNode);
        var headerTable = dojo.query('table',this.viewsHeaderNode)[0];
        const totalWidth =headerTable? headerTable.clientWidth:0;

        cells._nodes.forEach(function(n,idx){
            if((n.attr.hidden && (n.attr.hidden==true || sourceNode.getRelativeData(n.attr.hidden))) || !genro.dom.isVisible(headerList[idx])){
                cells.popNode(n.label);
                return;
            }
            n.attr.q_width = Math.round10(headerList[idx].clientWidth/totalWidth)
        });
        return struct;
    }
});
