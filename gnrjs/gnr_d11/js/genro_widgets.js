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

//######################## genro  #########################

gnr.convertFuncAttribute = function(sourceNode, name, parameters) {
    if (sourceNode.attr[name] && (typeof(sourceNode.attr[name]) == 'string')) {
        sourceNode.attr[name] = funcCreate(sourceNode.attr[name], parameters, sourceNode);
    }
};
gnr.setOrConnectCb = function(widget, name, cb) {
    if (name in widget) {
        dojo.connect(widget, name, cb);
    } else {
        widget[name] = cb;
    }
};
gnr.columnsFromStruct = function(struct, columns) {
    if (columns == undefined) {
        columns = [];
    }
    if (!struct) {
        return '';
    }
    var nodes = struct.getNodes();
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        if (node.attr['calculated']) {
            continue;
        }
        var fld = node.attr.field;
        if (fld) {
            if ((!stringStartsWith(fld, '$')) && (!stringStartsWith(fld, '@'))) {
                fld = '$' + fld;
            }
            arrayPushNoDup(columns, fld);
            if (node.attr.zoomPkey) {
                var zoomPkey = node.attr.zoomPkey;
                if ((!stringStartsWith(zoomPkey, '$')) && (!stringStartsWith(zoomPkey, '@'))) {
                    zoomPkey = '$' + zoomPkey;
                }
                arrayPushNoDup(columns, zoomPkey);
            }
        }

        if (node.getValue() instanceof gnr.GnrBag) {
            gnr.columnsFromStruct(node.getValue(), columns);
        }
    }
    return columns.join(',');
};

gnr.menuFromBag = function (bag, appendTo, menuclass, basepath) {
    var menuline,attributes;
    var bagnodes = bag.getNodes();
    for (var i = 0; i < bagnodes.length; i++) {
        var bagnode = bagnodes[i];
        attributes = objectUpdate({}, bagnode.attr);
        attributes.label = attributes.caption || attributes.label || bagnode.label;
        attributes.fullpath = basepath ? basepath + '.' + bagnode.label : bagnode.label;
        menuline = appendTo._('menuline', attributes);
        if (bagnode.getResolver()) {
            newmenu = menuline._('menu', {fullpath:attributes.fullpath,
                '_class':menuclass,
                'content':bagnode.getResolver()});
        }
        else {
            var menucontent = bagnode.getValue();
            if (menucontent instanceof gnr.GnrBag) {
                var newmenu = menuline._('menu', {'_class':menuclass});
                gnr.menuFromBag(menucontent, newmenu, menuclass, attributes.fullpath);
            }
        }
    }
};
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
        var editWidgetNode = this.widgetRootNode._(fldDict.tag, attr).getParentNode();
        editWidgetNode.editedRowIndex = row;
        this.onEditCell(true);
        if (cellDataNode.attr._validationError || cellDataNode.attr._validationWarnings) {
            editWidgetNode._validations = {'error':cellDataNode.attr._validationError,'warnings':cellDataNode.attr._validationWarnings};
            editWidgetNode.updateValidationStatus();
        }
        ;
        editWidgetNode.widget.focus();

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
dojo.declare("gnr.widgets.baseHtml", null, {
    _defaultValue:'',
    _defaultEvent:'onclick',
    constructor: function(application) {
        this._domtag = null;
        this._dojotag = null;
        this._dojowidget = false;
    },

    connectChangeEvent:function(obj) {
        if ('value' in obj) {
            dojo.connect(obj, 'onchange', this, 'onChanged');
        }
    },

    onChanged:function(evt) {
        var domnode = evt.target;
        //genro.debug('onDomChanged:'+domnode.value);
        //domnode.sourceNode.setAttributeInDatasource('value',domnode.value);
        this._doChangeInData(domnode, domnode.sourceNode, domnode.value);
    },
    _doChangeInData:function(domnode, sourceNode, value, valueAttr) {
        var valueAttr = valueAttr || null;
        var path = sourceNode.attrDatapath('value');
        genro._data.setItem(path, value, valueAttr, {'doTrigger':sourceNode});
    },
    _makeInteger: function(attributes, proplist) {
        dojo.forEach(proplist, function(prop) {
            if (prop in attributes) {
                attributes[prop] = attributes[prop] / 1;
            }
        });
    },

    _creating:function(attributes, sourceNode) {
        /*receives some attributes, calls creating, updates savedAttrs and returns them*/
        var extension = objectPop(attributes, 'extension');
        if (extension) {
            sourceNode[extension] = new gnr.ext[extension](sourceNode);
        }

        this._makeInteger(attributes, ['sizeShare','sizerWidth']);
        var savedAttrs = {};
        objectExtract(attributes, 'onDrop,onDrag,dragTag,dropTag,dragTypes,dropTypes');
        objectExtract(attributes, 'onDrop_*');
        savedAttrs['dropTarget'] = objectPop(attributes, 'dropTarget');
        savedAttrs['dropTargetCb'] = objectPop(attributes, 'dropTargetCb');

        savedAttrs.connectedMenu = objectPop(attributes, 'connectedMenu');
        savedAttrs.onEnter = objectPop(attributes, 'onEnter');
        objectUpdate(savedAttrs, this.creating(attributes, sourceNode));
        var formId = objectPop(attributes, 'formId');
        if (attributes._for) {
            attributes['for'] = objectPop(attributes, '_for');
        }
        if (attributes.onShow) {
            attributes['onShow'] = funcCreate(attributes.onShow, 'console.log("showing")', sourceNode);
        }
        if (attributes.onHide) {
            attributes['onHide'] = funcCreate(attributes.onHide, '', sourceNode);
        }

        if (sourceNode && sourceNode.attr.zoomFactor) {
            savedAttrs['zoomFactor'] = objectPop(attributes, 'zoomFactor');
            sourceNode.setZoomFactor = function (factor) {
                if (typeof(factor) == 'string' && factor[factor.length - 1] == '%') {
                    factor = factor.slice(0, factor.length - 1) / 100;
                }
                domNode = this.getDomNode();
                dojo.style(domNode, 'zoom', factor);
                dojo.style(domNode, 'MozTransformOrigin', 'top left');
                dojo.style(domNode, 'MozTransform', 'scale(' + factor + ')');

            };
        }
        if (sourceNode && formId) {
            if (sourceNode.attr.nodeId && (sourceNode.attr.nodeId != formId)) {
                alert('formId ' + formId + ' will replace nodeId ' + sourceNode.attr.nodeId);
            }
            //for having form information inside the form datapath
            var controllerPath = objectPop(attributes, 'controllerPath');
            var pkeyPath = objectPop(attributes, 'pkeyPath');
            var formDatapath = objectPop(attributes, 'formDatapath') || sourceNode.absDatapath();
            sourceNode.attr.nodeId = formId;
            sourceNode.defineForm(formId, formDatapath, controllerPath, pkeyPath);
        }
        //Fix Colspan in Internet explorer
        if (dojo.isIE > 0) {
            if (attributes['colspan']) {
                attributes.colSpan = attributes['colspan'];
            }
        }
        return savedAttrs;
    },
    creating:function(attributes, sourceNode) {
        /*override this for each widget*/

        return {};
    },
    setControllerTitle:function(attributes, sourceNode) {
        var iconClass = objectPop(attributes, 'iconClass');
        var title = attributes['title'];
        if (iconClass) {
            if (attributes['title']) {
                attributes['title'] = '<span class="' + iconClass + '"/><span style="padding-left:20px;">' + attributes['title'] + '</span>';
            }
            else if (attributes['title_tip']) {
                attributes['title'] = '<div class="' + iconClass + '" title="' + attributes['title_tip'] + '"/>';
            }
            else {
                attributes['title'] = '<div class="' + iconClass + '"/>';
            }
        }
        ;
        if (attributes['title']) {
            var tip = objectPop(attributes, 'tip') || title || '';
            attributes['title'] = '<span title="' + tip + '">' + attributes['title'] + '</span>';
        }
        ;
    },
    setDraggable:function(domNode, value) {
        domNode.setAttribute('draggable', value);
    },
    setDropTarget:function(domNode, value) {
        domNode.sourceNode.dropTarget = value;
    },


    _created:function(newobj, savedAttrs, sourceNode, ind) {
        this.created(newobj, savedAttrs, sourceNode);
        if (savedAttrs.connectedMenu) {
            var menu = savedAttrs.connectedMenu;
            var domNode = newobj.domNode || newobj;
            if (typeof(menu) == 'string') {
                menu = dijit.byId(menu);
            }
            if (menu) {
                menu.bindDomNode(domNode);
            }

        }
        if (!sourceNode) {
            return;
        }
        if (savedAttrs.dropTargetCb) {
            sourceNode.dropTargetCb = funcCreate(savedAttrs.dropTargetCb, 'dropInfo', sourceNode);
        }
        if (savedAttrs.dropTarget) {
            if (newobj.setDropTarget) {
                newobj.setDropTarget(savedAttrs.dropTarget);
            } else {
                newobj.gnr.setDropTarget(newobj, savedAttrs.dropTarget);
            }
        }
        ;
        if (savedAttrs.zoomFactor) {
            sourceNode.setZoomFactor(savedAttrs.zoomFactor);
        }

        var draggable = sourceNode.getAttributeFromDatasource('draggable') || sourceNode.getAttributeFromDatasource('detachable');
        if (draggable && 'setDraggable' in newobj) {
            newobj.setDraggable(draggable)
        }


        var parentNode = sourceNode.getParentNode();
        if (parentNode.attr.tag) {
            if (parentNode.attr.tag.toLowerCase() == 'tabcontainer') {
                objectFuncReplace(newobj, 'setTitle', function(title) {
                    if (title) {
                        if (this.controlButton) {
                            this.controlButton.setLabel(title);
                        }
                    }
                });
            }
            else if (parentNode.attr.tag.toLowerCase() == 'accordioncontainer') {
                objectFuncReplace(newobj, 'setTitle', function(title) {
                    this.titleTextNode.innerHTML = title;

                });
            }
        }
        ;

        if (savedAttrs.onEnter) {
            var callback = dojo.hitch(sourceNode, funcCreate(savedAttrs.onEnter));
            var kbhandler = function(evt) {
                if (evt.keyCode == genro.PATCHED_KEYS.ENTER) {
                    evt.target.blur();
                    setTimeout(callback, 100);
                }
            };
            var domnode = newobj.domNode || newobj;
            dojo.connect(domnode, 'onkeypress', kbhandler);
        }
        ;
        dojo.connect(newobj, 'onfocus', function(e) {
            genro.currentFocusedElement = newobj.domNode || newobj;
        });
        if (sourceNode.attr['hasGhost']) {
            var _textbox = newobj.textbox;
            dojo.connect(newobj.textbox, 'onfocus', function(e) {
                genro.dom.ghostOnEvent(e);
            });
            dojo.connect(newobj.textbox, 'onblur', function(e) {
                genro.dom.ghostOnEvent(e);
            });
            dojo.connect(newobj.textbox, 'onkeyup', function(e) {
                genro.dom.ghostOnEvent(e);
            });
            dojo.connect(newobj, 'setValue', function(value) {
                genro.dom.ghostOnEvent({type:'setvalue',value:value,obj:newobj});
            });
            dojo.connect(newobj, 'onChange', function(value) {
                genro.dom.ghostOnEvent({type:'setvalue',value:value,obj:newobj});
            });

        }
    },
    onDragStart:function(dragInfo) {
        var event = dragInfo.event;
        var sourceNode = dragInfo.sourceNode;
        if ('dragValue' in sourceNode.attr) {
            value = sourceNode.currentFromDatasource(sourceNode.attr['dragValue']);
        }
        else if ('value' in sourceNode.attr) {
            value = sourceNode.getAttributeFromDatasource('value');
        }
        else if ('innerHTML' in sourceNode.attr) {
            value = sourceNode.getAttributeFromDatasource('innerHTML');
        }
        else {
            value = dragInfo.domnode.innerHTML;
        }
        return {'text/plain':value};
    },
    fillDragInfo:function(dragInfo) {

    },
    fillDropInfo:function(dropInfo) {
        dropInfo.outline = dropInfo.domnode;
    },

    setTrashPosition: function(dragInfo) {
        /*override this for each widget*/
    },

    created:function(newobj, savedAttrs, sourceNode) {
        /*override this for each widget*/
        return null;
    }
});

dojo.declare("gnr.widgets.iframe", gnr.widgets.baseHtml, {
    creating:function(attributes, sourceNode) {
        sourceNode.savedAttrs = objectExtract(attributes, 'rowcount,tableid,src,rpcCall,onLoad');
        var condFunc = objectPop(attributes, 'condition_function');
        var condValue = objectPop(attributes, 'condition_value');
        var onUpdating = objectPop(attributes, 'onUpdating');

        if (onUpdating) {
            sourceNode.attr.onUpdating = funcCreate(onUpdating, '', sourceNode);
        }
        if (condFunc) {
            sourceNode.condition_function = funcCreate(condFunc, 'value');
        }
        return sourceNode.savedAttrs;
    },
    created:function(newobj, savedAttrs, sourceNode) {
        if (savedAttrs.rowcount && savedAttrs.tableid) {

            var rowcount = savedAttrs.rowcount;
            var tableid = savedAttrs.tableid;
            var fnc = dojo.hitch(newobj, function() {
                var nlines = 0;
                var tbl = this.contentDocument.getElementById(tableid);
                if (tbl) {
                    nlines = tbl.rows.length;
                }
                genro.setData(rowcount, nlines);
            });
            dojo.connect(newobj, 'onload', fnc);

        }
        if (savedAttrs.onLoad) {
            dojo.connect(newobj, 'onload', funcCreate(savedAttrs.onLoad));
        }
        this.setSrc(newobj, savedAttrs.src);
    },
    prepareSrc:function(domnode) {
        var sourceNode = domnode.sourceNode;
        var attributes = sourceNode.attr;
        if (attributes['src']) {
            return sourceNode.getAttributeFromDatasource('src');
        } else if (attributes['rpcCall']) {
            params = objectExtract(attributes, 'rpc_*', true);
            params.mode = params.mode ? params.mode : 'text';
            return genro.remoteUrl(attributes['rpcCall'], params, sourceNode, false);

        }
    },
    set_print:function(domnode, v, kw) {
        genro.dom.iFramePrint(domnode);
    },
    set_if:function(domnode, v, kw) {
        domnode.gnr.setSrc(domnode);
    },
    setCondition_value:function(domnode, v, kw) {
        domnode.sourceNode.condition_value = v;
        domnode.gnr.setSrc(domnode);
    },
    set_reloader:function(domnode, v, kw) {
        domnode.gnr.setSrc(domnode);
    },
    setSrc:function(domnode, v, kw) {
        var sourceNode = domnode.sourceNode;
        if (sourceNode.attr._if && !sourceNode.getAttributeFromDatasource('_if')) {
            var v = '';
        } else if (sourceNode.condition_function && !sourceNode.condition_function(sourceNode.condition_value)) {
            var v = '';
        }
        else {
            var v = v || this.prepareSrc(domnode);
        }
        if (sourceNode.currentSetTimeout) {
            clearTimeout(sourceNode.currentSetTimeout);
        }
        if (v) {
            sourceNode.currentSetTimeout = setTimeout(function(d, url) {
                var absUrl = document.location.protocol + '//' + document.location.host + url;
                if (absUrl != d.src) {
                    if (d.src && sourceNode.attr.onUpdating) {
                        sourceNode.attr.onUpdating();
                    }
                    d.src = url;
                }
            }, sourceNode.attr.delay || 1, domnode, v);
        }

    }
});

dojo.declare("gnr.widgets.baseDojo", gnr.widgets.baseHtml, {
    _defaultEvent:'onClick',
    constructor: function(application) {
        this._domtag = 'div';
        this._dojowidget = true;
    },
    _doChangeInData:function(domnode, sourceNode, value, valueAttr) {
        /*if(value==undefined){
         sourceNode.widget._isvalid = false;
         }*/
        if (sourceNode._modifying) { // avoid recursive _doChangeInData when calling widget.setValue in validations

            return;
        }
        var path = sourceNode.attrDatapath('value');
        var datanode = genro._data.getNode(path, null, true); //7/06/2006
        if (datanode.getValue() === value) {
            return;
        }
        var validateresult;
        valueAttr = objectUpdate(objectUpdate({}, datanode.attr), valueAttr);
        if (sourceNode.hasValidations()) {
            validateresult = sourceNode.validationsOnChange(sourceNode, value);
            value = validateresult['value'];
            objectExtract(valueAttr, '_validation*');
            if (validateresult['error']) {
                valueAttr._validationError = validateresult['error'];
            }
            if (validateresult['warnings'].length) {
                valueAttr._validationWarnings = validateresult['warnings'];
            }

        }

        value = this.convertValueOnBagSetItem(sourceNode, value);

        genro._data.setItem(path, value, valueAttr, {'doTrigger':sourceNode});
    },
    mixin_setTip: function (tip) {
        this.setAttribute('title', tip);
    },
    convertValueOnBagSetItem: function(sourceNode, value) {
        return value;
    },
    mixin_setDraggable:function(value) {
        this.domNode.setAttribute('draggable', value);
    },
    mixin_setDropTarget:function(value) {
        this.sourceNode.dropTarget = value;
    },
    validatemixin_validationsOnChange: function(sourceNode, value) {
        var result = genro.vld.validate(sourceNode, value, true);
        if (result['modified']) {
            sourceNode._modifying = true;
            sourceNode.widget.setValue(result['value']);
            sourceNode._modifying = false;
        }
        sourceNode.setValidationError(result);
        var formHandler = sourceNode.getFormHandler();
        if (formHandler) {
            formHandler.updateInvalidField(sourceNode, sourceNode.attrDatapath('value'));
        }
        return result;
    },
    mixin_mainDomNode: function() {
        return this.inputNode || this.textInputNode || this.domNode;
    },
    connectChangeEvent:function(widget) {
        if ('onChange' in widget) {
            dojo.connect(widget, 'onChange', dojo.hitch(this, function(val) {
                this.onChanged(widget, val);
            }));
        }
    },
    onChanged:function(widget, value) {
        //genro.debug('onChanged:'+value);
        //widget.sourceNode.setAttributeInDatasource('value',value);
        this._doChangeInData(widget.domNode, widget.sourceNode, value);

    },
    setUrlRemote: function(widget, method, arguments) {
        var url = genro.rpc.rpcUrl(method, arguments);
        widget.setHref(url);
    },
    mixin_setVisible: function(visible) {
        dojo.style(this.domNode, 'visibility', (visible ? 'visible' : 'hidden'));
    },

    mixin_setHidden: function(hidden) {
        dojo.style(this.domNode, 'display', (hidden ? 'none' : ''));
    },
    mixin_setSizeShare: function(value) {
        this.sizeShare = value;
        dijit.byId(this.domNode.parentNode.id).layout();
    }
    // Removed to avoid conflicts with 1.2. Check if we can survive without it
    // mixin_setDisabled: function(value){
    //     var value=value? true:false;
    //     this.setAttribute('disabled', value);
    // }

});
dojo.declare("gnr.widgets.Dialog", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._attachTo = 'mainWindow';
        this._domtag = 'div';
        this._dojotag = 'Dialog';
    },

    creating:function(attributes, sourceNode) {
        objectPop(attributes, 'parentDialog');
        objectPop(attributes, 'centerOn');
        objectPop(attributes, 'position');
        var closable = ('closable' in attributes) ? objectPop(attributes, 'closable') : true;
        attributes.title = attributes.title || '';
        if (!closable) {
            attributes.templateString = "<div class=\"dijitDialog\" tabindex=\"-1\" waiRole=\"dialog\" waiState=\"labelledby-${id}_title\">\n\t<div dojoAttachPoint=\"titleBar\" class=\"dijitDialogTitleBar\">\n\t<span dojoAttachPoint=\"titleNode\" class=\"dijitDialogTitle\" id=\"${id}_title\">${title}</span>\n\t</div>\n\t\t<div dojoAttachPoint=\"containerNode\" class=\"dijitDialogPaneContent\"></div>\n</div>\n";
        } else if (closable == 'ask') {
            attributes.templateString = "<div class=\"dijitDialog\" tabindex=\"-1\" waiRole=\"dialog\" waiState=\"labelledby-${id}_title\">\n\t<div dojoAttachPoint=\"titleBar\" class=\"dijitDialogTitleBar\">\n\t<span dojoAttachPoint=\"titleNode\" class=\"dijitDialogTitle\" id=\"${id}_title\">${title}</span>\n\t<span dojoAttachPoint=\"closeButtonNode\" class=\"dijitDialogCloseIcon\" dojoAttachEvent=\"onclick: onAskCancel\">\n\t\t<span dojoAttachPoint=\"closeText\" class=\"closeText\">x</span>\n\t</span>\n\t</div>\n\t\t<div dojoAttachPoint=\"containerNode\" class=\"dijitDialogPaneContent\"></div>\n</div>\n";

            sourceNode.closeAttrs = objectExtract(attributes, 'close_*');
        }
    },
    created:function(newobj, savedAttrs, sourceNode) {
        if (dojo_version == '1.5') {
            var position = sourceNode.attr.position;
            if (position) {
                position = position.split(',');
                newobj._relativePosition = {x:position[0],y:position[1]};
            }
        }
        if (dojo_version == '1.1') {
            dojo.connect(newobj, "show", newobj,
                        function() {
                            if (this != genro.dialogStack.slice(-1)[0]) {
                                genro.dialogStack.push(this);
                                if (genro.dialogStack.length > 1) {
                                    genro.dialogStack.slice(-2)[0].hide();
                                }
                            }

                        });
            dojo.connect(newobj, "hide", newobj,
                        function() {
                            if (this == genro.dialogStack.slice(-1)[0]) {
                                genro.dialogStack.pop();
                                if (genro.dialogStack.length > 0) {
                                    genro.dialogStack.slice(-1)[0].show();
                                }
                            }
                        });
        }
        genro.dragDropConnect(newobj.domNode);

    },
    versionpatch_11__position: function() {
        var centerOn = this.sourceNode.attr.centerOn;
        if (!centerOn) {
            this._position_replaced();
        }
        else {
            genro.dom.centerOn(this.domNode, centerOn);
            //var viewport=dojo.coords(genro.domById(centerOn));
            //viewport.l=viewport.x;
            //viewport.t=viewport.y;
            //var mb = dojo.marginBox(this.domNode);
            //var style = this.domNode.style;
            //style.left = Math.floor((viewport.l + (viewport.w - mb.w)/2)) + "px";
            //style.top = Math.floor((viewport.t + (viewport.h - mb.h)/2)) + "px";
        }
    },

    attributes_mixin_onAskCancel:function() {
        var closeAttrs = this.sourceNode.closeAttrs;
        var _this = this;
        var closeAction;
        if (closeAttrs.action) {
            closeAction = dojo.hitch(this.sourceNode, funcCreate(closeAttrs.action));
        } else {
            closeAction = dojo.hitch(this, 'onCancel');
        }
        genro.dlg.ask('', closeAttrs['msg'], {confirm:closeAttrs['confirm'],
            cancel:closeAttrs['cancel']}, {confirm:closeAction, cancel:''});
    },
    mixin_setTitle:function(title) {
        this.titleNode.innerHTML = title;
    }

});
dojo.declare("gnr.widgets.Editor", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'textarea';
    },
    creating:function(attributes, sourceNode) {
        dojo.require("dijit._editor.plugins.AlwaysShowToolbar");
        dojo.require("dijit._editor.plugins.FontChoice");
        dojo.require("dijit._editor.plugins.TextColor");
        dojo.require("dijit._editor.plugins.LinkDialog");
        var extraPlugins = objectPop(attributes, 'extraPlugins');
        var disabled = objectPop(attributes, 'disabled');
        if (extraPlugins) {
            attributes.extraPlugins = extraPlugins.split(',');
        }
    },
    // mixin_setDisabled:null, // removed as SetDisabled was removed in dojoBase
    created:function(newobj, savedAttrs, sourceNode) {
        if (sourceNode.attr['disabled']) {
            var disabled = sourceNode.getAttributeFromDatasource('disabled');
            if (disabled) {
                setTimeout(function() {
                    newobj.setDisabled(true);
                }, 10);
            }
        }
        ;
        if (sourceNode.attr['value']) {
            var value = sourceNode.getAttributeFromDatasource('value');
            if (value != null) {
                newobj.setValue(value);
            }
        }
        ;
    }
});

dojo.declare("gnr.widgets.SimpleTextarea", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'textarea';
    },
    creating:function(attributes, sourceNode) {
        var savedAttrs = objectExtract(attributes, 'value');
        return savedAttrs;
    },
    created:function(newobj, savedAttrs, sourceNode) {
        if (savedAttrs.value) {
            newobj.setValue(savedAttrs.value);
        }
        ;
        dojo.connect(newobj.domNode, 'onchange', dojo.hitch(this, function() {
            this.onChanged(newobj);
        }));
    },
    onChanged:function(widget) {
        var value = widget.getValue();
        this._doChangeInData(widget.domNode, widget.sourceNode, value);

    }
});

dojo.declare("gnr.widgets.ProgressBar", gnr.widgets.baseDojo, {
    mixin_setProgress: function(value) {
        if (value == undefined) {
            value = null;
        }
        this.update({'progress':value, 'indeterminate':(value == null)});
    },
    mixin_setIndeterminate: function(value) {
        if (value != null) {
            this.update({'indeterminate':value});
        }
    },
    mixin_setMaximum: function(value) {
        this.update({'maximum':value});
    },
    mixin_setPlaces: function(value) {
        this.update({'places':value});
    }

});

dojo.declare("gnr.widgets.StackContainer", gnr.widgets.baseDojo, {
    creating:function(attributes, sourceNode) {
        objectPop(attributes, 'selected');
        objectPop(attributes, 'selectedPage');
        return {};
    },
    created: function(widget, savedAttrs, sourceNode) {
        dojo.connect(widget, 'addChild', dojo.hitch(this, 'onAddChild', widget));
        dojo.connect(widget, 'removeChild', dojo.hitch(this, 'onRemoveChild', widget));
        //dojo.connect(widget,'_transition',widget, 'onChildTransition');

    },

    mixin_setSelected:function(p) {
        var child = this.getChildren()[p || 0];
        if (this.getSelected() != child) {
            this.selectChild(child);
        }

    },
    mixin_setSelectedPage:function(pageName) {
        var child = this.gnrPageDict[pageName];
        if (child && this.getSelected() != child) {
            this.selectChild(child);
        }
    },

    mixin_getSelected: function() {
        var selected = {n:null};
        dojo.forEach(this.getChildren(), function(n) {
            if (n.selected) {
                selected.n = n;
            }
        });
        return selected.n;
    },
    mixin_getSelectedIndex: function() {
        return this.getChildIndex(this.getSelected());
    },

    mixin_getChildIndex:function(obj) {
        return dojo.indexOf(this.getChildren(), obj);
    },

    onShowHideChild:function(widget, child, st) {
        if (widget._duringLayoutCall) {
            return;
        }
        var sourceNode = widget.sourceNode;
        var selpath = sourceNode.attr['selected'];
        var selpage = sourceNode.attr['selectedPage'];
        var nodeId = sourceNode.attr.nodeId;
        var cbUpd = function(path, newpage, st) {
            if (st) {
                if (genro.src.building) {
                    setTimeout(function() {
                        if (!sourceNode.getRelativeData(path)) {
                            sourceNode.setRelativeData(path, newpage);
                        }
                    }, 1);
                } else {
                    sourceNode.setRelativeData(path, newpage);
                }
            }
            if (nodeId) {
                genro.publish(nodeId + '_selected', {'change':newpage + '_' + (st ? 'show' : 'hide'),'page':newpage,'selected':st});
            }
        };
        if (selpath) {
            cbUpd(selpath, widget.getChildIndex(child), st);
        }
        if (selpage) {
            cbUpd(selpage, child.sourceNode.attr.pageName, st);
        }
    },

    onAddChild:function(widget, child) {
        gnr.setOrConnectCb(child, 'onShow', dojo.hitch(this, 'onShowHideChild', widget, child, true));
        gnr.setOrConnectCb(child, 'onHide', dojo.hitch(this, 'onShowHideChild', widget, child, false));
        var pageName = child.sourceNode.attr.pageName;
        if (pageName) {
            widget.gnrPageDict = widget.gnrPageDict || {};
            widget.gnrPageDict[pageName] = child;
        }
    },
    onRemoveChild:function(widget, child) {
        var pageName = child.sourceNode.attr.pageName;
        if (pageName) {
            objectPop(widget.gnrPageDict, pageName);
        }
    }

});

dojo.declare("gnr.widgets.TabContainer", gnr.widgets.StackContainer, {
    ___created: function(widget, savedAttrs, sourceNode) {
        // dojo.connect(widget,'addChild',dojo.hitch(this,'onAddChild',widget));
    },
    ___onAddChild:function(widget, child) {
    },

    versionpatch_11_layout: function() {
        // Summary: Configure the content pane to take up all the space except for where the tabs are
        if (!this.doLayout) {
            return;
        }
        // position and size the titles and the container node
        var titleAlign = this.tabPosition.replace(/-h/, "");
        var children = [
            { domNode: this.tablist.domNode, layoutAlign: titleAlign },
            { domNode: this.containerNode, layoutAlign: "client" }
        ];
        dijit.layout.layoutChildren(this.domNode, this._contentBox, children);

        // Compute size to make each of my children.
        // children[1] is the margin-box size of this.containerNode, set by layoutChildren() call above
        this._containerContentBox = dijit.layout.marginBox2contentBox(this.containerNode, children[1]);

        if (this.selectedChildWidget) {
            this._duringLayoutCall = true;
            this._showChild(this.selectedChildWidget);
            this._duringLayoutCall = false;
            if (this.doLayout && this.selectedChildWidget.resize) {
                this.selectedChildWidget.resize(this._containerContentBox);
            }
        }
    }
});
dojo.declare("gnr.widgets.BorderContainer", gnr.widgets.baseDojo, {
    creating: function(attributes, sourceNode) {
        if (dojo_version != '1.1') {
            attributes.gutters = attributes.gutters || false;
        }
        this.setControllerTitle(attributes, sourceNode);
    },
    created: function(widget, savedAttrs, sourceNode) {
        dojo.connect(widget, 'startup', dojo.hitch(this, 'afterStartup', widget));
        if (dojo_version == '1.7') {
            dojo.connect(widget, 'addChild', dojo.hitch(this, 'onAddChild', widget));
        }
    },
    afterStartup:function(widget) {
        var sourceNode = widget.sourceNode;
        if (dojo_version != '1.7') {
            widget._splitterConnections = {};
            var region,splitter;
            for (region in widget._splitters) {
                if (!widget._splitterConnections[region]) {
                    //splitter=widget.getSplitter(region);
                    splitter = dijit.byNode(widget._splitters[region]);
                    widget._splitterConnections[region] = dojo.connect(splitter, '_stopDrag', dojo.hitch(this, 'onSplitterStopDrag', widget, splitter));
                }
            }
        }
        if (sourceNode.attr.regions) {
            var regions = sourceNode.getRelativeData(sourceNode.attr.regions);
            if (!regions) {
                regions = new gnr.GnrBag();
                sourceNode.setRelativeData(sourceNode.attr.regions, regions);
            }
            var regions = regions.getNodes();
            for (var i = 0; i < regions.length; i++) {
                widget.setRegions(null, {'node':regions[i]});
            }
            ;
        }

    },
    /* onAddChild:function(widget,child){
     var splitter=widget._splitters[child.region];
     if(splitter){
     splitter=dijit.getEnclosingWidget(splitter);
     dojo.connect(splitter,'_stopDrag',dojo.hitch(this,'onSplitterStopDrag',widget,splitter));
     }
     },*/
    onSplitterStopDrag:function(widget, splitter) {
        var sourceNode = widget.sourceNode;
        if (sourceNode.attr.regions) {
            var region = splitter.region;
            var regions = sourceNode.getRelativeData(sourceNode.attr.regions);
            var value = splitter.child.domNode.style[splitter.horizontal ? "height" : "width"];
            regions.setItem(region, value, null, {'doTrigger':sourceNode});
        }
    },
    mixin_setRegions:function(value, kw) {
        var region = kw.node.label;
        if (('_' + region) in this) {
            var size = kw.node.getValue();
            if (size) {
                this['_' + region].style[(region == 'top' || region == 'bottom' ) ? "height" : "width"] = size;
                this._layoutChildren();
            }
        }
        if ('show' in kw.node.attr) {
            this.showHideRegion_one(region, kw.node.attr.show);
        }
    },
    mixin_getRegionVisibility: function(region) {
        return (this._splitterThickness[region] != 0);
    },

    mixin_showHideRegion: function(region, show) {
        var regions = region.split(',');
        for (var i = 0; i < regions.length; i++) {
            show = this.showHideRegion_one(regions[i], show);
        }
        ;
        return show;
    },
    mixin_showHideRegion_one: function(region, show) {
        if (this._splitters[region]) {
            this._computeSplitterThickness(region);
        }
        var regionNode = this['_' + region];
        if (regionNode) {
            if (show == 'toggle') {
                show = (this._splitterThickness[region] == 0);
            }
            var disp = show ? '' : 'none';
            var splitterNode = this._splitters[region];
            if (splitterNode) {
                var tk = this._splitterThickness['_' + region] || this._splitterThickness[region];
                this._splitterThickness['_' + region] = tk;
                this._splitterThickness[region] = show ? tk : 0;
                var st = dojo.style(splitterNode, 'display', disp);
            }
            dojo.style(regionNode, 'display', disp);
            this._layoutChildren();
        }
        return show;
    }
});

dojo.declare("gnr.widgets.FloatingPane", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._attachTo = 'mainWindow';
        this._dojotag = 'FloatingPane';
        genro.dom.loadCss("/_dojo/11/dojo/dojox/layout/resources/FloatingPane.css");
        genro.dom.loadCss("/_dojo/11/dojo/dojox/layout/resources/ResizeHandle.css");
    },

    created: function(widget, savedAttrs, sourceNode) {
        widget._startZ = 600;
        var nodeId = sourceNode.attr.nodeId;
        if (nodeId){
            dojo.connect(widget,'show',function(){
                genro.publish(nodeId+'_show');
            });
        }
    },

});


dojo.declare("gnr.widgets.ColorPicker", gnr.widgets.baseDojo, {
    created: function(widget, savedAttrs, sourceNode) {
        dojo.connect(widget, 'onChange', function() {
            console.log(arguments);
        });
    }
});
dojo.declare("gnr.widgets.ColorPalette", gnr.widgets.baseDojo, {
    created: function(widget, savedAttrs, sourceNode) {
        dojo.connect(widget, 'onChange', function() {
            return;
        });
    },

    mixin_setValue:function(value) {
        this.value = value;
    },
    mixin_getValue:function() {
        return this.value;
    }
});
dojo.declare('gnr.widgets.AccordionPane', gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = '*';
        var dojotag = dojo_version > '1.4' ? 'ContentPane' : 'AccordionPane';
        this._dojotag = dojotag;
        this._basedojotag = dojotag;
    }
});
dojo.declare("gnr.widgets.Menuline", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = '*';
        this._dojotag = 'MenuItem';
        this._basedojotag = 'MenuItem';
    },
    creating:function(attributes, sourceNode) {
        var savedAttrs = {};
        objectPop(attributes, 'action');
        if (sourceNode.attr.label == '-') {
            this._dojotag = 'MenuSeparator';
        }
        if (attributes.checked) {
            attributes.iconClass = 'tick_icon10';
        }
        else {
            if (sourceNode.getResolver()) {
                this._dojotag = 'PopupMenuItem';
            }
            else {
                var content = sourceNode.getValue();
                if (content instanceof gnr.GnrBag && content.len() > 0) {
                    this._dojotag = 'PopupMenuItem';
                } else {
                    this._dojotag = 'MenuItem';
                }
            }
        }
        return savedAttrs;
    },

    mixin_setChecked: function(val, kw) {
        if (val) {
            dojo.addClass(this.iconNode, 'tick_icon10');
        } else {
            dojo.removeClass(this.iconNode, 'tick_icon10');
        }
    },
    mixin_addChild: function(popUpContent) {
        //called for submenu
        if (popUpContent.declaredClass == 'dijit.Menu') {
            this.popup = popUpContent;
        }
        if (this.addChild_replaced) {
            this.addChild_replaced.call(this, popUpContent);
        }
    },
    patch_onClick:function(evt) {
        var originalTarget = this.getParent().originalContextTarget;
        var ctxSourceNode;
        var sourceNode = this.sourceNode;
        if (!originalTarget) {
            ctxSourceNode = sourceNode;
        } else {
            if (originalTarget.sourceNode) {
                ctxSourceNode = originalTarget.sourceNode;
            }
            else {
                ctxSourceNode = dijit.getEnclosingWidget(originalTarget).sourceNode;
            }
        }
        // var ctxSourceNode = originalTarget ? originalTarget.sourceNode || dijit.byId(originalTarget.attributes.id.value).sourceNode :sourceNode
        var inAttr = sourceNode.getInheritedAttributes();
        var actionScope = sourceNode;
        var action = inAttr.action;
        if (ctxSourceNode && ctxSourceNode.attr.action) {
            action = ctxSourceNode.attr.action;
            actionScope = ctxSourceNode;
        }
        f = funcCreate(action);
        if (f) {
            f.call(actionScope, sourceNode.getAttr(), ctxSourceNode, evt);
        }
        var selattr = objectExtract(inAttr, 'selected_*', true);
        if (ctxSourceNode) {
            selattr = objectUpdate(selattr, objectExtract(ctxSourceNode.getInheritedAttributes(), 'selected_*', true));
        }
        for (var sel in selattr) {
            ctxSourceNode.setRelativeData(selattr[sel], sourceNode.attr[sel], null, null, sourceNode);
        }
        if (inAttr.selected) {
            ctxSourceNode.setRelativeData(inAttr.selected, sourceNode.label, null, null, sourceNode);
        }
    }
});
dojo.declare("gnr.widgets.ContentPane", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'ContentPane';
    },
    creating:function(attributes, sourceNode) {
        attributes.isLoaded = true;
        this.setControllerTitle(attributes, sourceNode);
    }
});

dojo.declare("gnr.widgets.Menu", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = '*';
        this._dojotag = 'Menu';
    },
    creating:function(attributes, sourceNode) {
        var savedAttrs = objectExtract(attributes, 'modifiers,validclass,storepath');
        if (savedAttrs.storepath) {
            sourceNode.registerDynAttr('storepath');
        }
        if (!attributes.connectId) {
            savedAttrs['connectToParent'] = true;
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        if (savedAttrs.storepath) {
            var contentNode = genro.getDataNode(sourceNode.absDatapath(savedAttrs.storepath));
            if (contentNode) {
                var content = contentNode.getValue('static');
                //var content=sourceNode.getRelativeData(savedAttrs.storepath);
                if (content) {
                    var menubag = new gnr.GnrDomSource();
                    gnr.menuFromBag(content, menubag, sourceNode.attr._class);
                    sourceNode.setValue(menubag, false);
                } else if (contentNode.getResolver()) {
                    sourceNode.setResolver(contentNode.getResolver());
                }
            }
        }

        if (sourceNode && savedAttrs['connectToParent']) {
            var parentNode = sourceNode.getParentBag().getParentNode();
            var parentWidget = parentNode.widget;
            if (parentWidget) {
                if (!(('dropDown' in  parentWidget) || ('popup' in parentWidget ))) {
                    widget.bindDomNode(parentWidget.domNode);
                }
            } else if (parentNode.domNode) {
                widget.bindDomNode(parentNode.domNode);
            } else {
                widget.bindDomNode(dojo.byId(genro.domRootName));
            }
            if (parentNode.attr.tag != 'menuline') {
                sourceNode.stopInherite = true;
            }
        }

        dojo.connect(widget, 'onOpen', function() {
            genro.dom.addClass(document.body, 'openingMenu');
        });
        dojo.connect(widget, 'onClose', function() {
            genro.dom.removeClass(document.body, 'openingMenu');
        });
        widget.modifiers = savedAttrs['modifiers'];
        widget.validclass = savedAttrs['validclass'];


    },
    mixin_setStorepath:function(val, kw) {
        this.sourceNode.rebuild();
    },
    mixin_setChecked: function(menuline, val) {
        if (this.currentChecked && this.currentChecked != menuline) {
            this.currentChecked.setChecked(false);
        }
        menuline.setChecked(val);
        this.currentChecked = val ? menuline : null;
    },
    patch_destroy: function() {
        if (this._bindings) {
            dojo.forEach(this._bindings, function(b) {
                dojo.forEach(b, dojo.disconnect);
            });
            delete this._bindings;
        }
        this.destroy_replaced.call(this);
    },
    versionpatch_11__contextMouse: function (e) {
        this.originalContextTarget = e.target;
        var sourceNode = this.sourceNode;
        if (sourceNode) {
            var resolver = sourceNode.getResolver();
            if (resolver && resolver.expired()) {
                var result = sourceNode.getValue('notrigger');
                if (result instanceof gnr.GnrBag) {
                    var menubag = new gnr.GnrDomSource();
                    var old_bindings = [];
                    dojo.forEach(this._bindings, function(k) {
                        old_bindings.push(k[0][0]);
                    });
                    gnr.menuFromBag(result, menubag, sourceNode.attr._class, sourceNode.attr.fullpath);
                    sourceNode.setValue(menubag);
                    var new_bindings = [];
                    dojo.forEach(sourceNode.widget._bindings, function(k) {
                        new_bindings.push(k[0][0]);
                    });
                    dojo.forEach(old_bindings, function(n) {
                        if (dojo.indexOf(new_bindings, n) < 0) {
                            sourceNode.widget.bindDomNode(n);
                        }
                    });
                } else {
                    sourceNode.setValue(result);
                }
            }
        }
        if ((e.button == 2) && (!this.modifiers)) {
            this._contextMouse_replaced.call(this, e);
        }
        else if (this.modifiers && genro.wdg.filterEvent(e, this.modifiers, this.validclass)) {
            this._contextMouse_replaced.call(this, e);
            var wdg = sourceNode.widget;
            wdg._openMyself_replaced.call(wdg, e);

        }
    },
    versionpatch_15__openMyself: function (e) {
        this.originalContextTarget = e.target;
        var sourceNode = this.sourceNode;
        if (sourceNode) {
            var resolver = sourceNode.getResolver();
            if (resolver && resolver.expired()) {
                var result = sourceNode.getValue('notrigger');
                if (result instanceof gnr.GnrBag) {
                    var menubag = new gnr.GnrDomSource();
                    gnr.menuFromBag(result, menubag, sourceNode.attr._class, sourceNode.attr.fullpath);
                    sourceNode.setValue(menubag);
                } else {
                    sourceNode.setValue(result);
                }
            }
        }
        if ((e.button == 2) && (!this.modifiers)) {
            this._openMyself_replaced.call(this, e);
        }
        else if (this.modifiers && genro.wdg.filterEvent(e, this.modifiers, this.validclass)) {
            this._openMyself_replaced.call(this, e);
        }
    },
    versionpatch_11__openMyself: function (e) {
        if ((e.button == 2) && (!this.modifiers)) {
            this._openMyself_replaced.call(this, e);
        }
    },
    patch__openPopup: function (e) {
        var sourceNode = this.focusedChild.popup.sourceNode;
        if (sourceNode) {
            var resolver = sourceNode.getResolver();
            if (resolver && resolver.expired()) {
                var result = sourceNode.getValue('notrigger');
                if (result instanceof gnr.GnrBag) {
                    var menubag = new gnr.GnrDomSource();
                    gnr.menuFromBag(result, menubag, sourceNode.attr._class, sourceNode.attr.fullpath);
                    sourceNode.setValue(menubag);
                } else {
                    sourceNode.setValue(result);
                }
                this.focusedChild.popup = sourceNode.widget;
            }
        }

        this.focusedChild.popup.originalContextTarget = this.originalContextTarget;
        this._openPopup_replaced.call(this, e);
    }

});

dojo.declare("gnr.widgets.Tooltip", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = '*';
        this._dojotag = 'Tooltip';
    },
    creating:function(attributes, sourceNode) {
        var callback = objectPop(attributes, 'callback');
        if (callback) {
            attributes['label'] = funcCreate(callback, 'n', sourceNode);
        }
        var savedAttrs = objectExtract(attributes, 'modifiers,validclass');
        if (! attributes.connectId) {
            savedAttrs['connectToParent'] = true;
        }
        return savedAttrs;
    },

    created: function(widget, savedAttrs, sourceNode) {
        widget.modifiers = savedAttrs['modifiers'];
        widget.validclass = savedAttrs['validclass'];
        if (sourceNode && savedAttrs['connectToParent']) {
            var parentNode = sourceNode.getParentBag().getParentNode();
            var domnode = parentNode.domNode || parentNode.widget.domNode;
            widget.connectOneNode(domnode);
        }
    },

    patch__onHover: function(/*Event*/ e) {
        if (genro.wdg.filterEvent(e, this.modifiers, this.validclass)) {
            this._onHover_replaced.call(this, e);
        }
    }
    ,
    attributes_mixin_postCreate: function() {
        if (dojo_version == '1.1') {
            if (this.srcNodeRef) {
                this.srcNodeRef.style.display = "none";
            }
        } else {
            dojo.addClass(this.domNode, "dijitTooltipData");
        }
        this.connectAllNodes(this.connectId);
    },
    attributes_mixin_connectAllNodes:function(nodes) {
        var node;
        this._connectNodes = [];
        dojo.forEach(nodes, function(node) {
            if (typeof(node) == 'string') {
                node = dojo.byId(node);
            }
            this.connectOneNode(node);
        });
    },
    mixin_connectOneNode:function(node) {
        this._connectNodes.push(node);
        var eventlist;
        if (dojo_version == '1.1') {
            eventlist = ["onMouseOver", "onMouseOut", "onFocus", "onBlur", "onHover", "onUnHover"];
        }
        else if (dojo_version == '1.5') {
            eventlist = ["onTargetMouseEnter", "onTargetMouseLeave", "onTargetFocus", "onTargetBlur", "onHover", "onUnHover"];
        }
        else {
            eventlist = ["onMouseEnter", "onMouseLeave", "onFocus", "onBlur"];
        }

        dojo.forEach(eventlist, function(evt) {
            this.connect(node, evt.toLowerCase(), "_" + evt);
        }, this);
        if (dojo.isIE) {
            // BiDi workaround
            node.style.zoom = 1;
        }
    }

});

dojo.declare("gnr.widgets.Button", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'Button';
    },
    creating:function(attributes, sourceNode) {
        var buttoNodeAttr = 'height,width,padding';
        var savedAttrs = objectExtract(attributes, 'fire_*');
        savedAttrs['_style'] = genro.dom.getStyleDict(objectExtract(attributes, buttoNodeAttr));
        savedAttrs['action'] = objectPop(attributes, 'action');
        savedAttrs['fire'] = objectPop(attributes, 'fire');
        return savedAttrs;


    },
    created: function(widget, savedAttrs, sourceNode) {
        dojo.connect(widget, 'onClick', sourceNode, this.onClick);
        objectExtract(sourceNode._dynattr, 'fire_*');
        objectPop(sourceNode._dynattr, 'fire');
        if (savedAttrs['_style']) {
            var buttonNode = dojo.query(".dijitButtonNode", widget.domNode)[0];
            dojo.style(buttonNode, savedAttrs['_style']);
        }
    },
    onClick:function(e) {
        var modifier = eventToString(e);
        var action = this.getInheritedAttributes().action;
        if (action) {
            //funcCreate(action).call(this,e);
            funcApply(action, objectUpdate(this.currentAttributes(), {event:e}), this);
        }
        if (this.attr.fire) {
            var s = eventToString(e) || true;
            this.setRelativeData(this.attr.fire, s, {modifier:modifier}, true);
        }
        var fire_list = objectExtract(this.attr, 'fire_*', true);
        for (var fire in fire_list) {
            this.setRelativeData(fire_list[fire], fire, {modifier:modifier}, true);
        }

    }
});

dojo.declare("gnr.widgets.Calendar", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'Calendar';
    },
    creating:function(attributes, sourceNode) {
        var storepath = sourceNode.absDatapath(objectPop(attributes, 'storepath'));
        sourceNode.registerDynAttr('storepath', storepath);
//      attributes.storebag=genro.getDataNode(storepath,true,new gnr.GnrBag()).getValue();
    },
    created: function(widget, savedAttrs, sourceNode) {
        var bagnodes = widget.getStorebag().getNodes();
        for (i = 0; i < bagnodes.length; i++) {
            widget.setCalendarEventFromBagNode(bagnodes[i]);
        }
    },
    mixin_setStorepath: function(val, kw) {
        if (kw.evt == 'ins') {
            this.setCalendarEventFromBagNode(kw.node);
        }
        else if (kw.evt == 'upd') {
            var bagnodes = this.getStorebag().getNodes();
            this.emptyCalendar();
            for (i = 0; i < bagnodes.length; i++) {
                this.setCalendarEventFromBagNode(bagnodes[i]);
            }
        }

    },
    mixin_getStorebag: function() {
        var storepath = this.sourceNode.absDatapath(this.sourceNode.attr['storepath']);
        var storebag = genro.getData(storepath);
        if (!storebag) {
            storebag = new gnr.GnrBag();
            genro.setData(storepath, storebag);
        }
        return storebag;
    }
    ,
    mixin_setCalendarEventFromBagNode: function(node) {
        var event_record = node.attr;
        //var event_type=objectPop(node.attr,'event_type');
        //event_record.start_time=dojo.date.stamp.toISOString(objectPop(node.attr,'starttime'))
        //event_record.end_time=dojo.date.stamp.toISOString(objectPop(node.attr,'endtime'))
        //var event_attr=objectExtract(node.attr,'event_*');
        //event_record.event_type=event_type.split(',');
        //event_record.attributes=event_attr;
        this.addCalendarEntry(node.attr.date, event_record);
    },
    patch_onValueChanged: function(date, mode) {
        var bagnodes = this.getStorebag().getNodes();
        for (i = 0; i < bagnodes.length; i++) {
            this.setCalendarEventFromBagNode(bagnodes[i]);
        }
    },
    patch_onChangeEventDate: function(item_id, newDate) {
        //this.getStorebag().getNode(item_id).attr.date.setYear(newDate.getFullYear());
        //this.getStorebag().getNode(item_id).attr.date.setMonth(newDate.getMonth());
        this.getStorebag().getNode(item_id).attr.date.setDate(newDate.getDate());
    },
    patch_onChangeEventTime: function(item, newDate) {
        var bagnodes = this.getStorebag().getNodes();
        for (i = 0; i < bagnodes.length; i++) {
            this.setCalendarEventFromBagNode(bagnodes[i]);
        }
    },
    patch_onChangeEventDateTime: function(item, newDate, newTime) {
        var bagnodes = this.getStorebag().getNodes();
        for (i = 0; i < bagnodes.length; i++) {
            this.setCalendarEventFromBagNode(bagnodes[i]);
        }
    }
});

dojo.declare("gnr.widgets.RadioButton", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'RadioButton';
    },
    creating:function(attributes, sourceNode) {
        var savedAttrs = objectExtract(attributes, 'action,callback');
        var label = objectPop(attributes, 'label');
        objectPop(attributes, 'width');
        attributes.name = objectPop(attributes, 'group');
        if (label) {
            attributes['id'] = attributes['id'] || 'id_' + sourceNode._id;
            savedAttrs['label'] = label;
            savedAttrs['labelattrs'] = objectExtract(attributes, 'label_*');
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        var label = savedAttrs['label'];
        if (label) {
            var labelattrs = savedAttrs['labelattrs'];
            labelattrs['for'] = widget.id;
            labelattrs['margin_left'] = labelattrs['margin_left'] || '3px';
            var domnode = genro.wdg.create('label', widget.domNode.parentNode, labelattrs);
            domnode.innerHTML = label;
        }
        if (sourceNode.hasDynamicAttr('value')) {
            var value = sourceNode.getAttributeFromDatasource('value');
            //widget.setChecked(value);
            widget.setAttribute('checked', value);
        }
    },
    patch_onClick:function(e) {
        var action = this.sourceNode.getInheritedAttributes().action;
        if (action) {
            dojo.hitch(this.sourceNode, funcCreate(action))(this.sourceNode.attr, this.sourceNode, e);
        }
    },
    patch_setValue: function(/*String*/ value, pc) {
        if (value == null) {
            value = "";
        }
        this.setAttribute('checked', value);
    }
});

dojo.declare("gnr.widgets.CheckBox", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'CheckBox';
    },
    creating:function(attributes, sourceNode) {
        objectPop(attributes, 'width');
        var savedAttrs = objectExtract(attributes, 'action,callback');
        var label = objectPop(attributes, 'label');

        if (label) {
            attributes['id'] = attributes['id'] || 'id_' + sourceNode._id;
            savedAttrs['label'] = label;
            savedAttrs['labelattrs'] = objectExtract(attributes, 'label_*');
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        var label = savedAttrs['label'];
        if (label) {
            var labelattrs = savedAttrs['labelattrs'];
            labelattrs['for'] = widget.id;
            labelattrs['margin_left'] = labelattrs['margin_left'] || '3px';
            var domnode = genro.wdg.create('label', widget.domNode.parentNode, labelattrs);
            domnode.innerHTML = label;
        }
        if (sourceNode.hasDynamicAttr('value')) {
            var value = sourceNode.getAttributeFromDatasource('value');
            //widget.setChecked(value);
            widget.setAttribute('checked', value);
        }
    },
    mixin_displayMessage:function() {
        //patch
    },
    patch_onClick:function(e) {
        //if(this.sourceNode._dynattr && this.sourceNode._dynattr.value){
        //    this.sourceNode.setAttributeInDatasource('value',this.checked)
        //}
        var action = this.sourceNode.getInheritedAttributes().action;
        if (action) {
            dojo.hitch(this, funcCreate(action))(this.sourceNode.attr, this.sourceNode, e);
            //funcCreate(action)(this.sourceNode.attr,this.sourceNode,e);
        }
    },
    patch_setValue: function(/*String*/ value, pc) {
        //this.setChecked(value);
        this.setAttribute('checked', value);
    }
});

dojo.declare("gnr.widgets.TextArea_", gnr.widgets.baseDojo, {
    constructor: function() {
        this._domtag = 'textarea';
        this._dojotag = 'TextArea';
    },
    creating: function(attributes, sourceNode) {
        var x = 1;
    },
    created: function(widget, savedAttrs, sourceNode) {
        var x = 1;
    }
});
dojo.declare("gnr.widgets.DateTextBox", gnr.widgets.baseDojo, {

    onChanged:function(widget, value) {
        //genro.debug('onChanged:'+value);
        //widget.sourceNode.setAttributeInDatasource('value',value);
        if (value) {
            this._doChangeInData(widget.domNode, widget.sourceNode, value, {dtype:'D'});
        }
        else {
            this._doChangeInData(widget.domNode, widget.sourceNode, null);
        }
    },

    constructor: function() {
        this._domtag = 'input';
        this._dojotag = 'DateTextBox';
    },
    creating: function(attributes, sourceNode) {
        if ('popup' in attributes && (objectPop(attributes, 'popup') == false)) {
            attributes.popupClass = null;
        }

    }


});
dojo.declare("gnr.widgets.TextBox", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'input';
        this._dojotag = 'ValidationTextBox';
    },
    /*mixin_displayMessage: function(message){
     //genro.dlg.message(message, null, null, this.domNode)
     genro.setData('_pbl.errorMessage', message)
     },*/
    creating: function(attributes, sourceNode) {
        var savedAttrs = {};
        attributes.trim = (attributes.trim == false) ? false : true;
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        this.connectFocus(widget, savedAttrs, sourceNode);
    },
    connectFocus: function(widget, savedAttrs, sourceNode) {
        if (sourceNode.attr._autoselect) {
            dojo.connect(widget, 'onFocus', widget, function(e) {
                setTimeout(dojo.hitch(this, 'selectAllInputText'), 1);
            });
        }
    },
    mixin_selectAllInputText: function() {
        dijit.selectInputText(this.focusNode);
    }


});
dojo.declare("gnr.widgets.TimeTextBox", gnr.widgets.baseDojo, {
    onChanged:function(widget, value) {
        if (value) {
            this._doChangeInData(widget.domNode, widget.sourceNode, value, {dtype:'H'});
        }
        else {
            this._doChangeInData(widget.domNode, widget.sourceNode, null);
        }
    },
    creating: function(attributes, sourceNode) {
        if ('ftype' in attributes) {
            attributes.constraints['type'] = objectPop(attributes['ftype']);
        }
    },
    mixin_setPickInterval:function(interval) {
        var timeInt = 'T00:' + interval + ':00';
        this.constraints.clickableIncrement = timeInt;

    }
});

dojo.declare("gnr.widgets.NumberTextBox", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'input';
        this._dojotag = 'NumberTextBox';
    },
    creating: function(attributes, sourceNode) {
        attributes._class = attributes._class ? attributes._class + ' numberTextBox' : 'numberTextBox';
        attributes.constraints = objectExtract(attributes, 'min,max,places,pattern,round,currency,fractional,symbol,strict,locale');
        if ('ftype' in attributes) {
            attributes.constraints['type'] = objectPop(attributes['ftype']);
        }
        ;
    },
    convertValueOnBagSetItem: function(sourceNode, value) {
        if (value === "") {
            value = null;
        }
        return value;
    }
});
dojo.declare("gnr.widgets.CurrencyTextBox", gnr.widgets.NumberTextBox, {
    constructor: function(application) {
        this._domtag = 'input';
        this._dojotag = 'CurrencyTextBox';
    }
});
dojo.declare("gnr.widgets.NumberSpinner", gnr.widgets.NumberTextBox, {
    constructor: function(application) {
        this._domtag = 'input';
        this._dojotag = 'NumberSpinner';
    }
});

// ********* Grid ************
dojo.declare("gnr.widgets.Grid", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'Grid';
        if (dojo_version == '1.1') {
            if (!dojox.grid) {
                dojo.require('dojox.grid._grid.builder');
            }
            ;
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
    mixin_setStructpath:function(val, kw) {
        this.structBag = genro.getData(this.sourceNode.attrDatapath('structpath'));
        this.cellmap = {};
        this.setStructure(this.gnr.structFromBag(this.sourceNode, this.structBag, this.cellmap));
        this.onSetStructpath(this.structBag);
    },
    mixin_setDraggable_column:function(draggable) {
        if (draggable === undefined) {
            var draggable = this.sourceNode.getAttributeFromDatasource('draggable_column');
        }
        dojo.query('[role="wairole:columnheader"]', this.domNode).forEach(function(n) {
            n.draggable = true;
        });
    },
    mixin_setDraggable_row:function(draggable, view) {
        var view = view || this.views.views[0];
        var draggable = draggable == false ? false : true;
        var builder = view.content;
        builder._table = builder._table.replace('<table draggable="true" ', '<table ');
        if (draggable) {
            builder._table = builder._table.replace('<table ', '<table draggable="true" ');
        }
        dojo.query('.dojoxGrid-row-table', this.domNode).forEach(function(n) {
            n.draggable = true;
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
        genro.formById(this.sourceNode.attr.linkedForm).openForm(idx, this.rowIdByIndex(idx));
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
        sourceNode.attr.onTrashed = sourceNode.attr.onTrashed || 'this.widget.deleteColumn(data);';
    },
    selfDragRowsPrepare:function(sourceNode) {
        gnr.convertFuncAttribute(sourceNode, 'selfDragRows', 'info');
        gnr.convertFuncAttribute(sourceNode, 'onSelfDropRows', 'rows,dropInfo');
        gnr.convertFuncAttribute(sourceNode, 'afterSelfDropRows', 'rows,dropInfo');
        sourceNode.attr.draggable_row = true;
        var onDropCall = function(dropInfo, rows) {
            if (!('row' in dropInfo ) || (dropInfo.row < 0)) {
                return;
            }
            if (sourceNode.attr.onSelfDropRows) {
                sourceNode.attr.onSelfDropRows(rows, dropInfo);
            }
            else {
                dropInfo.widget.moveRow(rows, dropInfo.row);
                var row_counter_changes = dropInfo.widget.updateCounterColumn();
            }
            if (sourceNode.attr.afterSelfDropRows) {
                sourceNode.attr.afterSelfDropRows(rows, dropInfo, row_counter_changes);
            }
        };
        sourceNode.attr['onDrop_selfdragrow_' + sourceNode._id] = onDropCall;
    },

    creating_common: function(attributes, sourceNode) {
        sourceNode.attr.nodeId = sourceNode.attr.nodeId || 'grid_' + sourceNode.getStringId();
        sourceNode.gridControllerPath = sourceNode.attr.controllerPath ? sourceNode.absDatapath(sourceNode.attr.controllerPath) : 'grids.' + sourceNode.attr.nodeId;
        if (sourceNode.attr.configurable) {
            sourceNode.attr.selfDragColumns = 'trashable';
            var tablecode = sourceNode.attr.table.replace('.', '_');
            sourceNode.attr['onDrop_gnrdbfld_' + tablecode] = function(dropInfo, data) {
                var grid = this.widget;
                grid.addColumn(data, dropInfo.column);
                if (grid.rowCount > 0) {
                    setTimeout(function() {
                        grid.reload();
                    }, 1);
                }
            };
            sourceNode.attr.dropTarget_column = sourceNode.attr.dropTarget_column ? sourceNode.attr.dropTarget_column + ',' + 'gnrdbfld_' + tablecode : 'gnrdbfld_' + tablecode;
        }
        if (sourceNode.attr.selfDragRows) {
            this.selfDragRowsPrepare(sourceNode);
        }
        if (sourceNode.attr.selfDragColumns) {
            this.selfDragColumnsPrepare(sourceNode);
        }
        var savedAttrs = objectExtract(attributes, 'selected*');
        var identifier = attributes.identifier || '_pkey';
        attributes.datamode = attributes.datamode || 'attr';
        attributes.rowsPerPage = attributes.rowsPerPage || 10;
        attributes.rowCount = attributes.rowCount || 0;
        attributes.fastScroll = attributes.fastScroll || false;
        sourceNode.dropModes = objectExtract(sourceNode.attr, 'dropTarget_*', true);
        if (!sourceNode.dropTarget && objectNotEmpty(sourceNode.dropModes)) {
            sourceNode.dropTarget = true;
        }
        var attributesToKeep = 'autoHeight,autoRender,autoWidth,defaultHeight,elasticView,fastScroll,keepRows,model,rowCount,rowsPerPage,singleClickEdit,structure,';
        attributesToKeep = attributesToKeep + 'datamode,sortedBy,filterColumn,excludeCol,excludeListCb,editorEnabled';
        var gridAttributes = objectExtract(attributes, attributesToKeep);
        objectPopAll(attributes);
        objectUpdate(attributes, gridAttributes);
        attributes._identifier = identifier;

        return savedAttrs;
    },

    creating_structure: function(attributes, sourceNode) {
        structBag = sourceNode.getRelativeData(sourceNode.attr.structpath);
        if (structBag) {
            sourceNode.baseStructBag = structBag.deepCopy();
        }
        if (genro.grid_configurator) {
            genro.grid_configurator.onStructCreating(sourceNode);
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
        if (genro.grid_configurator) {
            genro.grid_configurator.onGridCreated(sourceNode);
        }
        var gridContent = sourceNode.getValue();
        if (gridContent instanceof gnr.GnrBag) {
            var gridEditorNode = gridContent.getNodeByAttr('tag', 'gridEditor');
            if (gridEditorNode) {
                widget.gridEditor = new gnr.GridEditor(widget, sourceNode, gridEditorNode);
            }
            ;
        }
        ;
        if ('draggable_row' in sourceNode.attr) {
            dojo.connect(widget.views, 'addView', dojo.hitch(widget, 'onAddedView'));
            if (widget.views.views.length > 0) {
                var draggable_row = sourceNode.getAttributeFromDatasource('draggable_row');
                widget.setDraggable_row(draggable_row, widget.views.views[0]);
            }
        }

        if ('draggable_column' in sourceNode.attr) {
            dojo.connect(widget, 'postrender', dojo.hitch(widget, 'setDraggable_column'));
        }
        if (sourceNode.attr.openFormEvent) {
            dojo.connect(widget, sourceNode.attr.openFormEvent, widget, 'openLinkedForm');
            if (genro.isTouchDevice) {
                dojo.connect(widget, 'longTouch', widget, 'openLinkedForm');
            }
        }
        objectFuncReplace(widget.selection, 'clickSelectEvent', function(e) {
            this.clickSelect(e.rowIndex, e.ctrlKey || e.metaKey, e.shiftKey);
        });
        dojo.subscribe(sourceNode.attr.nodeId + '_reload', widget, function(keep_selection) {
            this.reload(keep_selection !== false)
        });
    },
    created: function(widget, savedAttrs, sourceNode) {
        this.created_common(widget, savedAttrs, sourceNode);
        dojo.connect(widget, 'onSelected', widget, '_gnrUpdateSelect');
        genro.src.afterBuildCalls.push(dojo.hitch(widget, 'render'));
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
        ;
        return dojo.query(condition, this.domNode);
    },
    mixin_rowIdByIndex: function(idx) {
        if (idx != null) {
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
        if (objectNotEmpty(selattr)) {
            var row = this.rowByIndex(idx);
            var value;
            for (var sel in selattr) {
                if (idx >= 0) {
                    value = row[sel];
                } else {
                    value = null;
                }
                var path = this.sourceNode.setRelativeData(selattr[sel], value);
            }
        }
        if (this.sourceNode.attr.selectedIndex) {
            this.sourceNode.setAttributeInDatasource('selectedIndex', ((idx < 0) ? null : idx), null, null, true);
        }
        if (this.sourceNode.attr.selectedPkeys) {
            this.sourceNode.setAttributeInDatasource('selectedPkeys', this.getSelectedPkeys(), null, null, true);
        }
        if (this.sourceNode.attr.selectedRowidx) {
            this.sourceNode.setAttributeInDatasource('Rowidx', this.getSelectedRowidx(), null, null, true);
        }
        if (this.sourceNode.attr.selectedNodes) {
            var nodes = this.getSelectedNodes();
            if (nodes) {
                var selNodes = new gnr.GnrBag();
                dojo.forEach(nodes,
                            function(node) {
                                selNodes.setItem(node.label, null, node.getAttr());
                            }
                        );
            }
            var path = this.sourceNode.attrDatapath('selectedNodes');
            genro.setData(path, selNodes, {'count':selNodes.len()});
        }
        if (this.sourceNode.attr.selectedId) {
            var selectedId = null;
            var row = {};
            if (idx >= 0) {
                selectedId = this.rowIdentity(this.rowByIndex(idx));
                var row = this.rowByIndex(idx);
            }
            this.sourceNode.setAttributeInDatasource('selectedId', selectedId, null, row, true);
        }
    },
    mixin_indexByRowAttr:function(attrName, attrValue, op, backward) {
        var op = op || '==';
        if (backward) {
            for (var i = this.rowCount - 1; i >= 0; i--) {
                var row = this.rowByIndex(i);
                if (genro.compareDict[op].call(this, row[attrName], attrValue, op)) {
                    return i;
                }
            }
            ;
        }
        else {
            for (var i = 0; i < this.rowCount; i++) {
                var row = this.rowByIndex(i);
                if (genro.compareDict[op].call(this, row[attrName], attrValue, op)) {
                    return i;
                }
            }
        }
        return -1;
    },
    mixin_indexByCb:function(cb, backward) {
        if (backward) {
            for (var i = this.rowCount - 1; i >= 0; i--) {
                if (cb(this.rowByIndex(i))) {
                    return i;
                }
            }
            ;
        }
        else {
            for (var i = 0; i < this.rowCount; i++) {
                if (cb(this.rowByIndex(i))) {
                    return i;
                }
            }
        }
        return -1;
    },
    mixin_hasRow:function(attr, value) {
        if (typeof(attr) == 'function') {
            cb = attr;
        } else {
            cb = function(n) {
                return n[attr] == value
            };
        }
        return this.indexByCb(cb) >= 0;
    },
    mixin_selectByRowAttr:function(attrName, attrValue, op) {
        var selection = this.selection;
        if (typeof (attrValue) == 'object') {
            selection.unselectAll();
            var grid = this;
            dojo.forEach(attrValue, function(v) {
                selection.addToSelection(grid.indexByRowAttr(attrName, v));
            });
        } else {
            selection.select(this.indexByRowAttr(attrName, attrValue, op));
        }

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
    mixin_getSelectedPkeys: function(noneIsAll) {
        var sel = this.selection.getSelected();
        var result = [];
        if (sel.length > 0) {
            for (var i = 0; i < sel.length; i++) {
                result.push(this.rowIdByIndex(sel[i]));
            }
        } else if (noneIsAll) {
            for (var i = 0; i < this.rowCount; i++) {
                result.push(this.rowIdByIndex(i));
            }
        }


        return result;
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
    structFromBag: function(sourceNode, struct, cellmap) {
        var cellmap = cellmap || {};
        var result = [];
        var _cellFormatter = function(formatOptions, cellClassCB) {
            var opt = objectUpdate({}, formatOptions);
            var cellClassFunc;
            if (cellClassCB) {
                cellClassFunc = funcCreate(cellClassCB, 'cell,v,inRowIndex');
            }
            return function(v, inRowIndex) {

                if (cellClassFunc) {
                    cellClassFunc(this, v, inRowIndex);
                }
                opt['cellPars'] = {rowIndex:inRowIndex};
                var zoomPage = opt['zoomPage'];
                if (typeof(v) == 'number' && v < 0) {
                    this.customClasses.push('negative_number');
                }
                if (this.grid.gridEditor && this.grid.gridEditor.invalidCell(this, inRowIndex)) {
                    this.customClasses.push('invalidCell');
                }
                v = genro.format(v, opt);
                if (v == null) {
                    return  '&nbsp;';
                }
                var template = opt['template'];
                if (template) {
                    v = template.replace(/#/g, v);
                }
                if (opt['js']) {
                    v = opt['js'](v, this.grid.storebag().getNodes()[inRowIndex]);
                }
                ;
                if (zoomPage) {
                    var zoomPkey = opt['zoomPkey'];
                    if (zoomPkey) {
                        zoomPkey = zoomPkey.replace(/\W/g, '_');
                    }
                    var key = this.grid.currRenderedRow[zoomPkey ? zoomPkey : this.grid._identifier];
                    // changed to support ctrl+click on non mac platforms v = "<a onclick='var ev = arguments[0]; if(!ev.metaKey){dojo.stopEvent(ev);}' class='gnrzoomcell' href='/"+zoomPage+"?pkey="+key+"&autoLinkFrom="+genro.page_id+"'>"+v+"</a>";
                    v = "<a onclick='if((genro.isMac&&!event.metaKey)||(!genro.isMac&&!event.ctrlKey)){dojo.stopEvent(event);}' class='gnrzoomcell' href='/" + zoomPage + "?pkey=" + key + "&autoLinkFrom=" + genro.page_id + "'>" + v + "</a>";
                }
                var draggable = this.draggable ? ' draggable=true ' : '';
                return '<div ' + draggable + 'class="cellContent">' + v + '</div>';

            };
        };
        if (struct) {
            var bagnodes = struct.getNodes();
            var formats, dtype, editor;
            var view, viewnode, rows, rowsnodes, i, k, j, cellsnodes, row, cell, rowattrs, rowBag;
            var localTypes = {'R':{places:2},'L':{places:0},'I':{places:0},'D':{date:'short'},'H':{time:'short'},'DH':{datetime:'short'}};
            for (i = 0; i < bagnodes.length; i++) {
                viewnode = bagnodes[i];
                view = objectUpdate({}, viewnode.attr);
                delete view.tag;
                rows = [];
                rowsnodes = viewnode.getValue().getNodes();
                for (k = 0; k < rowsnodes.length; k++) {
                    rowattrs = objectUpdate({}, rowsnodes[k].attr);
                    rowattrs = objectExtract(rowattrs, 'classes,headerClasses,cellClasses');
                    rowBag = rowsnodes[k].getValue();

                    if (!(rowBag instanceof gnr.GnrBag)) {
                        rowBag = new gnr.GnrBag();
                        rowsnodes[k].setValue(rowBag, false);
                    }

                    if (genro.isTouchDevice) {
                        var cellattr = {'format_isbutton':true,'format_buttonclass':'zoomIcon buttonIcon',
                            'format_onclick':'this.widget.openLinkedForm(kw);',
                            'width':'30px','calculated':true,
                            'field':'_edit_record','name':' '};
                        rowBag.setItem('cell_editor', null, cellattr, {doTrigger:false});
                    }

                    cellsnodes = rowBag.getNodes();
                    row = [];
                    for (j = 0; j < cellsnodes.length; j++) {
                        cell = objectUpdate({}, rowattrs);
                        cell = objectUpdate(cell, cellsnodes[j].attr);
                        dtype = cell.dtype;
                        cell.original_field = cell.field;
                        if (cell.field) {
                            cell.field = cell.field.replace(/\W/g, '_');
                            if (dtype) {
                                cell.cellClasses = (cell.cellClasses || '') + ' cell_' + dtype;
                            }
                            cell.cellStyles = objectAsStyle(genro.dom.getStyleDict(cell, [ 'width']));
                            formats = objectExtract(cell, 'format_*');
                            format = objectExtract(cell, 'format');
                            var zoomPage = objectPop(cell, 'zoomPage');
                            var template = objectPop(cell, 'template');
                            var js = objectPop(cell, 'js');
                            if (template) {
                                formats['template'] = template;
                            }
                            formats['dtype'] = dtype;
                            if (js) {
                                formats['js'] = genro.evaluate(js);
                            }
                            if (zoomPage)
                                formats['zoomPage'] = zoomPage;
                            formats['zoomPkey'] = objectPop(cell, 'zoomPkey');
                            if (format) {
                                formats['format'] = format;
                            }
                            if (cell.counter) {
                                sourceNode.attr.counterField = cell.field;
                                dtype = 'L';
                            }
                            if (cell.hidden) {
                                cell.classes = (cell.classes || '') + ' hiddenColumn';
                            }
                            if (dtype) {
                                formats = objectUpdate(objectUpdate({}, localTypes[dtype]), formats);
                            }

                            //formats = objectUpdate(formats, localTypes[dtype]);
                            var cellClassCB = objectPop(cell, 'cellClassCB');
                            cell.formatter = _cellFormatter(formats, cellClassCB);
                            delete cell.tag;
                            row.push(cell);
                            cellmap[cell.field] = cell;
                        }
                    }

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
            var nodeToMove = colsBag.popNode('#' + col);
            colsBag.setItem(nodeToMove.label, null, nodeToMove.attr, {'_position':toPos});
        }

    },
    mixin_moveRow:function(row, toPos) {
        if (toPos != row) {
            var storebag = this.storebag();
            storebag.moveNode(row, toPos);
        }

    },
    mixin_addColumn:function(col, toPos) {
        //if(!('column' in drop_event.dragDropInfo)){ return }
        var colsBag = this.structBag.getItem('#0.#0');
        colsBag.setItem('cellx_' + genro.getCounter(), null, {'width':'8em','name':col.fullcaption,
            'dtype':col.dtype, 'field':col.fieldpath,
            'tag':'cell'}, {'_position':toPos + 1});
    },
    onDragStart:function(dragInfo) {
        var dragmode = dragInfo.dragmode;
        var event = dragInfo.event;
        var widget = dragInfo.widget;
        var value = {};

        if (dragmode == 'row') {
            var cells = widget.structure[0]['rows'][0]
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
            var valTextPlain = [];
            var valTextXml = [];
            var valTextHtml = [];
            var innerHtml = [];
            var idx = 0;
            dojo.forEach(sel, function(k) {
                var rdata = widget.rowByIndex(k);
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
                innerHtml.push(widget.views.views[0].rowNodes[k].innerHTML);
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
            if (sel.length > 1) {
                //console.log(rowNodes)
                var auxDragImage = dragInfo.dragImageNode = dojo.byId('auxDragImage');
                dragInfo.dragImageNode = document.createElement('div');
                dragInfo.dragImageNode.innerHTML = innerHtml.join('');
                dojo.addClass(dragInfo.dragImageNode, 'draggedItem rowsetdragging');
                auxDragImage.appendChild(dragInfo.dragImageNode);
                dragInfo.event.dataTransfer.setDragImage(auxDragImage, 0, 0);
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
                columndata.push(v);
                textcol = textcol + convertToText(v)[1] + '\n';
            }
            ;
            value['gridcolumn'] = {'column':dragInfo.column,'columndata':columndata,'gridId':widget.sourceNode.attr.nodeId};
            value['text/plain'] = textcol;
            var selfDragColumns = dragInfo.sourceNode.attr.selfDragColumns;
            if (typeof(selfDragColumns) == 'function') {
                selfDragColumns = selfDragColumns(dragInfo);
            }
            if (selfDragColumns) {
                value['selfdragcolumn_' + dragInfo.sourceNode._id] = dragInfo.column;
                if (selfDragColumns == 'trashable') {
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
        for (var k in dropModes) {
            if (dojo.filter(dropModes[k].split(','),
                           function (value) {
                               return arrayMatch(draggedTypes, value).length > 0;
                           }).length > 0) {
                dropmode = k;
                break;
            }
            ;
        }
        dropmode = dropmode || dragSourceInfo.dragmode;
        if (!dropmode && (dojo.indexOf(draggedTypes, 'selfdragrow_' + dropInfo.sourceNode._id) >= 0)) {
            var selfDragRows = dropInfo.sourceNode.attr.selfDragRows;
            if (typeof(selfDragRows) == 'function') {
                selfDragRows = selfDragRows(dropInfo);
            }
            if (selfDragRows) {
                dropmode = 'row';
            }
        }
        if (!dropmode && (dojo.indexOf(draggedTypes, 'selfdracolumn_' + dropInfo.sourceNode._id) >= 0)) {
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
        if (widget.grid) {
            widget.content.decorateEvent(event);
            widget = widget.grid;
        } else {
            widget.views.views[0].header.decorateEvent(event);
        }
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
            }
        }
        dropInfo.widget = widget;
        dropInfo.sourceNode = widget.sourceNode;

    },
    fillDragInfo:function(dragInfo) {
        var event = dragInfo.event;
        var widget = dragInfo.widget;
        if (widget.grid) {
            widget.content.decorateEvent(event);
            widget = widget.grid;
        } else {
            widget.views.views[0].header.decorateEvent(event);
        }
        dragInfo.column = event.cellIndex;
        dragInfo.row = event.rowIndex;
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
        dragInfo.widget = widget;
        dragInfo.sourceNode = widget.sourceNode;
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
dojo.declare("gnr.widgets.VirtualGrid", gnr.widgets.Grid, {
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
        attributes.canSort = function() {
            return true;
        };
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
            if (attr._customClasses) {
                var customClasses = null;
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
        }
        this.onStyleRow_replaced(row);
    }
});


dojo.declare("gnr.widgets.VirtualStaticGrid", gnr.widgets.Grid, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'VirtualGrid';
    },
    creating: function(attributes, sourceNode) {
        var savedAttrs = this.creating_common(attributes, sourceNode);
        this.creating_structure(attributes, sourceNode);
        sourceNode.registerDynAttr('storepath');
    },

    created: function(widget, savedAttrs, sourceNode) {
        this.created_common(widget, savedAttrs, sourceNode);
        genro.src.afterBuildCalls.push(dojo.hitch(widget, 'render'));
        dojo.connect(widget, 'onSelected', widget, '_gnrUpdateSelect');
        widget.updateRowCount('*');
    },

    attributes_mixin_get: function(inRowIndex) {
        var rowdata = this.grid.rowCached(inRowIndex);
        return this._customGetter ? this._customGetter.call(this, rowdata) : rowdata[this.field];
    },

    mixin_rowCached:function(inRowIndex) {
        if (this.currRenderedRowIndex != inRowIndex) {
            this.currRenderedRowIndex = inRowIndex;
            this.currRenderedRow = this.rowByIndex(inRowIndex);
        }
        return this.currRenderedRow;
    },

    attributes_mixin_canSort: function() {
        return ('canSort' in this.sourceNode.attr ) ? this.sourceNode.attr.canSort : true;
    },
    mixin_filterExcluded: function(rowdata, index) {
        if (this.excludeList) {
            if (dojo.indexOf(this.excludeList, rowdata[this.excludeCol]) != -1) {
                return;
            }
        }
        this.filtered.push(index);
    },
    mixin_applyFilter: function(filtered_value, rendering, filterColumn) {
        if (filterColumn) {
            this.filterColumn = filterColumn;
        }
        var cb;
        this.excludeList = null;
        if (this.excludeListCb) {
            this.excludeList = this.excludeListCb();
        }
        if ((!filtered_value) || ((filtered_value == true) && (!this.filtered_value))) {
            this.filtered = null;
            if (this.excludeList) {
                cb = function(node, index, array) {
                    var rowdata = this.rowFromBagNode(node);
                    this.filterExcluded(rowdata, index);
                };
                this.filtered = [];
                dojo.forEach(this.storebag().getNodes(), cb, this);
            }
            this.filtered_value = null;
            this.filtered_compvalue = null;
        } else {
            this.filtered = null;
            this.filtered_value = (filtered_value == true) ? this.filtered_value : filtered_value;
            this.filtered_compvalue = null;
            var cb, colType;
            if (this.filterColumn.indexOf('+') > 0) {
                colType = 'T';
            } else {
                colType = this.cellmap[this.filterColumn]['dtype'] || 'A';
            }
            if (colType in {'A':null,'T':null}) {
                this.filtered_compvalue = new RegExp(this.filtered_value, 'i');
                cb = function(node, index, array) {
                    var result;
                    var columns = this.filterColumn.split('+');
                    var txt = '';
                    var rowdata = this.rowFromBagNode(node);
                    for (var i = 0; i < columns.length; i++) {
                        txt = txt + ' ' + rowdata[columns[i]];
                    }
                    ;
                    result = this.filtered_compvalue.test(txt);
                    if (result) {
                        this.filterExcluded(rowdata, index);
                    }
                };
            } else {
                cb = function(node, index, array) {
                    var op = this.filtered_compvalue.op;
                    var val = this.filtered_compvalue.val;
                    var rowdata = this.rowFromBagNode(node);
                    var result = this.filtered_compvalue.func.apply(this, [rowdata[this.filterColumn], val]);
                    if (result) {
                        this.filterExcluded(rowdata, index);
                    }
                };
                var toSearch = /^(\s*)([\<\>\=\!\#]+)(\s*)(.+)$/.exec(this.filtered_value);
                if (toSearch) {
                    var val;
                    var op = toSearch[2];
                    if (op == '=') {
                        op = '==';
                    }
                    if ((op == '!') || (op == '#')) {
                        op = '!=';
                    }
                    if (colType in {'R':null,'L':null,'I':null,'N':null}) {
                        val = dojo.number.parse(toSearch[4]);
                    } else if (colType == 'D') {
                        val = dojo.date.locale.parse(toSearch[4], {formatLength: "short",selector:'date'});
                    } else if (colType == 'DH') {
                        val = dojo.date.locale.parse(toSearch[4], {formatLength: "short"});
                    }
                    if (op && val) {
                        var func = "return (colval " + op + " fltval)";
                        func = funcCreate(func, 'colval,fltval');
                        this.filtered_compvalue = {'op':op, 'val':val, 'func':func};
                    }
                }
            }
            if (this.filtered_compvalue) {
                this.filtered = [];
                dojo.forEach(this.storebag().getNodes(), cb, this);
            }
        }
        this.filterToRebuild = false;
        if (!rendering) {
            this.updateRowCount('*');
        }
    },
    mixin_newDataStore:function(val, kw) {
        this.updateRowCount(0);
        this.filtered = null;
        if (this.sortedBy) {
            var storebag = this.storebag();
            storebag.sort(this.sortedBy);
        }
        this.updateRowCount();
        this.selection.unselectAll();
        this.selectionKeeper('load');
        if (this.autoSelect && (this.selection.selectedIndex < 0)) {
            var sel = this.autoSelect == true ? 0 : this.autoSelect();
            this.selection.select(sel);

        }
    },
    mixin_setStorepath:function(val, kw) {
        if ((!this._updatingIncludedView) && (! this._batchUpdating)) {
            //this.filterToRebuild=true;
            if (kw.evt == 'fired') {
                var storepath = this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
                var storenode = genro._data.getNode(storepath);
                if (storenode instanceof dojo.Deferred) {
                    console.log('Deferred!!')
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
                        this.updateRow(rowIdx);
                        // dojo.publish('upd_grid_cell', [this.sourceNode, rowLabel, rowIdx]);
                    } else {
                        // upd of the parent Bag
                        this.newDataStore();
                    }
                } else if (kw.evt == 'ins') {//ATTENZIONE: questo trigger fa scattare il ridisegno della grid e cambia l'indice di riga
                    if (parent_lv == 1 || (parent_lv == 2 && this.datamode == 'bag')) {
                        this.updateRowCount();
                        //fa srotellare in presenza di parametri con ==
                        this.setSelectedIndex(kw.ind);
                    } else {
                        //if ((storebag == kw.where) && (parent_lv<1)){
                        //}
                    }
                } else if (kw.evt == 'del') {
                    if (parent_lv == 1) {
                        this.updateRowCount();
                        this.setSelectedIndex(kw.ind);
                    } else {
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

    mixin_setRefreshOn:function() {

    },
    patch_onStyleRow:function(row) {
        var attr = this.rowCached(row.index);
        if (attr._customClasses) {
            var customClasses = null;
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
        console.log('patch_onApplyCellEdit');
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
        if ((n == null) || (n == '*')) {
            if (this.filterToRebuild) {
                this.applyFilter(true, true);
            }
        }
        if (n == '*') {
            this.updateRowCount_replaced(0);
            this.selection.unselectAll();
            n = null;
        }
        if (n == null) {
            var n = this.storeRowCount();
        }
        this.currRenderedRowIndex = null;
        this.currRenderedRow = null;
        this.updateRowCount_replaced(n);
    },
    mixin_setSortedBy:function(sortedBy) {
        this.sortedBy = sortedBy;
        var storebag = this.storebag();
        storebag.sort(this.sortedBy);
        this.filterToRebuild = true;
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
        var storepath = this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
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
    mixin_selectionKeeper:function(flag) {
        if (flag == 'save') {
            var prevSelectedIdentifiers = [];
            var identifier = this._identifier;
            dojo.forEach(this.getSelectedNodes(), function(node) {
                if (node) {
                    prevSelectedIdentifiers.push(node.attr[identifier]);
                }
                ;
            });
            this.prevSelectedIdentifiers = prevSelectedIdentifiers;
            this.prevScrollTop = this.scrollTop;
        } else if (flag == 'clear') {
            this.prevSelectedIdentifiers = null;
        } else if (flag == 'load') {
            if ((this.prevSelectedIdentifiers) && (this.prevSelectedIdentifiers.length > 0 )) {
                this.selectByRowAttr(this._identifier, this.prevSelectedIdentifiers);
                this.prevSelectedIdentifiers = null;
                if (this.prevScrollTop) {
                    this.setScrollTop(this.prevScrollTop);
                    this.prevScrollTop = null;
                }
            }
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
            var selectionNode = genro.nodeById(nodeId + '_selection');
            if (selectionNode) {
                if (this.filtered) {
                    this.filterToRebuild = true;
                }
                selectionNode.fireNode();
            }
        }
        if (nodeId) {
            genro.publish(nodeId + '_data_loaded');
        }
    },

    mixin_onSetStructpath: function(structBag) {
        this.query_columns = this.gnr.getQueryColumns(this.sourceNode, structBag);
        if (this.rpcViewColumns) {
            this.rpcViewColumns.call();
        }

        //var columns = gnr.columnsFromStruct(structure);
        //   if(this.sourceNode.hiddencolumns){
        //       columns = columns+','+this.sourceNode.hiddencolumns;
        //   }
        //   this.query_columns= columns;
        //
        //  if (this.rpcViewColumns){
        //      this.rpcViewColumns.call();
        //  }
        //  //this.reload(); test
    },

    mixin_absIndex: function(inRowIndex) {
        if (this.filterToRebuild) {
            console.log('invalid filter');
        }
        return this.filtered ? this.filtered[inRowIndex] : inRowIndex;
    },
    mixin_storeRowCount: function() {
        if (this.filtered) {
            return this.filtered.length;
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
        var nodes = this.storebag().getNodes();
        if (nodes.length > inRowIndex) {
            return nodes[inRowIndex];
        }
    },
    mixin_getSelectedNodes: function() {
        var sel = this.selection.getSelected();
        var result = [];
        for (var i = 0; i < sel.length; i++) {
            result.push(this.dataNodeByIndex(sel[i]));
        }
        return result;
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
        if (this.datamode != 'bag' && !this.gridEditor) {
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
        if (fldName) {
            var chNode = storebag.getNode(rowLabel);
            var cellAttr, value, gridfield;
            var currAttr = chNode.attr;
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
        }
        return storebag.index(rowLabel);
    },
    mixin_editBagRow: function(r, delay) {
        var r = r || this.selection.selectedIndex;
        var rc = this.gridEditor.findNextEditableCell({row: r, col: -1}, {r:0, c:1});
        var grid = this;
        if (rc) {
            if (delay) {
                if (this._delayedEditing) {
                    clearTimeout(this._delayedEditing);
                }
                this._delayedEditing = setTimeout(function() {
                    grid.gridEditor.startEdit(rc.row, rc.col);
                }, delay);
            } else {
                this.gridEditor.startEdit(rc.row, rc.col);
            }

        }
    },
    mixin_newBagRow: function(defaultArgs) {
        var defaultArgs = defaultArgs || {}
        var newRowDefaults = this.sourceNode.attr.newRowDefaults
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
        return newrow;
    },

    mixin_updateCounterColumn: function() {
        var storebag = this.storebag();
        var cb;
        var k = 0;
        var changes = [];
        var counterField = this.sourceNode.attr.counterField;
        if (!counterField) {
            return;
        }
        if (this.datamode == 'bag' || this.gridEditor) {
            cb = function(n) {
                var row = n.getValue();
                var oldk = row.getItem(counterField);
                if (k != oldk) {
                    row.setItem(counterField, k);
                }
                k++;
            };
        } else {
            cb = function(n) {
                var row = n.attr;
                var oldk = row.counterField;
                if (k != oldk) {
                    n.setAttribute(counterField, k);
                    changes.push({'node':n,'old':oldk,'new':k});
                }
                k++;
            };
        }
        storebag.forEach(cb, 'static');
        return changes;
    },
    mixin_addBagRow: function(label, pos, newnode, event, nodupField) {
        var label = label || 'r_' + newnode._id;
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
        if (pos == '*') {
            var curSelRow = this.absIndex(this.selection.selectedIndex);
            if (curSelRow < 0) {
                pos = event.shiftKey ? 0 : storebag.len();
            } else {
                pos = event.shiftKey ? curSelRow : curSelRow + 1;
            }
        }
        var kw = {'_position':pos};

        storebag.setItem(label, newnode, null, kw); //questa provoca la chiamata della setStorePath che ha trigger di ins.
        // ATTENZIONE: Commentato questo perchè il trigger di insert già ridisegna ed aggiorna l'indice, ma non fa apply filter.
        // Cambiare l'indice di selezione corrente nelle includedview con form significa cambiare datapath a tutti i widget. PROCESSO LENTO.

        //if(!this._batchUpdating){
        //this.applyFilter();
        //this.selection.select(kw._new_position);
        //alert('ex apply filter')
        //}
        this.updateCounterColumn();
        return kw._new_position;
    },
    mixin_delBagRow: function(pos, many, params) {
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
            pos = (pos == '*') ? this.absIndex(this.selection.selectedIndex) : pos;
            removed.push(storebag.popNode('#' + pos));
        }
        removed.reverse();
        this.filterToRebuild = true;
        this.updateCounterColumn();
        this.updateRowCount('*');

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
        if (this.gnrediting) {

        } else if (dijit.getEnclosingWidget(e.target) == this) {
            this.onKeyDown(e);
        }
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
        var addCheckBoxColumn = sourceNode.attr.addCheckBoxColumn;
        if (addCheckBoxColumn) {
            var kw = addCheckBoxColumn == true ? null : addCheckBoxColumn;
            this.addCheckBoxColumn(kw, sourceNode);
        }
        this.creating_structure(attributes, sourceNode);
        sourceNode.registerDynAttr('storepath');
        attributes.query_columns = this.getQueryColumns(sourceNode, attributes.structBag);
        var inAttrs = sourceNode.getInheritedAttributes();
        var ctxRoot = sourceNode.absDatapath(inAttrs.sqlContextRoot);
        var abs_storepath = sourceNode.absDatapath(sourceNode.attr.storepath);
        var relation_path = abs_storepath;
        if (abs_storepath.indexOf(ctxRoot) == 0) {
            relation_path = abs_storepath.replace(ctxRoot + '.', '');
        }
        attributes.relation_path = relation_path;
        attributes.sqlContextName = inAttrs['sqlContextName'];
        attributes.sqlContextTable = inAttrs['sqlContextTable'];
        if (attributes.excludeListCb) {
            attributes.excludeListCb = funcCreate(attributes.excludeListCb);
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
    mixin_onCheckedColumn:function(idx) {
        var rowpath = '#' + idx;
        var storebag = this.storebag();
        var currNode = storebag.getNode(rowpath);
        if (currNode.attr.disabled) {
            return;
        }
        var newval = !currNode.attr._checked;
        currNode.setAttr({'_checked':newval}, true, true);
        var gridId = this.sourceNode.attr.nodeId;
        if (gridId) {
            genro.publish(gridId + '_row_checked', currNode.label, newval, currNode.attr);
        }
    },
    mixin_addCheckBoxColumn:function(kw) {
        this.gnr.addCheckBoxColumn(kw, this.sourceNode);
    },
    addCheckBoxColumn:function(kw, sourceNode) {
        var position = position || 'left';
        var structbag = sourceNode.getRelativeData(sourceNode.attr.structpath);
        var celldata = {};
        var kw = kw || {};
        celldata['field'] = '_checked';
        celldata['name'] = kw.name || ' ';
        celldata['dtype'] = 'B';
        celldata['width'] = '20px';

        celldata['format_trueclass'] = kw.format_trueclass || 'checkboxOn';
        celldata['classes'] = kw.classes || 'row_checker';
        celldata['format_falseclass'] = kw.format_falseclass || 'checkboxOff';
        celldata['calculated'] = true;
        celldata['format_onclick'] = 'this.widget.onCheckedColumn(kw.rowIndex);';
        structbag.setItem('view_0.rows_0.cell_checked', null, celldata, {_position:kw.position || 0});
    },
    created: function(widget, savedAttrs, sourceNode) {
        this.created_common(widget, savedAttrs, sourceNode);
        var selectionId = sourceNode.attr['selectionId'] || sourceNode.attr.nodeId + '_selection';
        widget.autoSelect = sourceNode.attr['autoSelect'];
        if (typeof(widget.autoSelect) == 'string') {
            widget.autoSelect = funcCreate(widget.autoSelect, null, widget);
        }
        widget.linkedSelection = genro.nodeById(selectionId);
        genro.src.afterBuildCalls.push(dojo.hitch(widget, 'render'));
        //dojo.connect(widget, 'onSelected', widget,'_gnrUpdateSelect');
        dojo.connect(widget, 'modelAllChange', dojo.hitch(sourceNode, this.modelAllChange));

        if (sourceNode.attr.editbuffer) {
            sourceNode.registerDynAttr('editbuffer');
        }
        if (sourceNode.attr.multiSelect == false) {
            widget.selection.multiSelect = false;
        }
        widget.rpcViewColumns();
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

    mixin_batchUpdating: function(state) {
        this._batchUpdating = state;
    },
    mixin_setEditorEnabled: function(enabled) {
        this.editorEnabled = enabled;
    },
    mixin_rpcViewColumns: function() {
        if ((this.relation_path) && (this.relation_path.indexOf('@') == 0)) {
            genro.rpc.remoteCall('setViewColumns', {query_columns:this.query_columns,
                contextName:this.sqlContextName,
                contextTable:this.sqlContextTable,
                relation_path:this.relation_path});
        }
    }
});

dojo.declare("gnr.widgets.BaseCombo", gnr.widgets.baseDojo, {
    creating: function(attributes, sourceNode) {
        objectExtract(attributes, 'maxLength,_type');
        var values = objectPop(attributes, 'values');
        var val,xval;
        if (values) {
            var localStore = new gnr.GnrBag();
            values = values.split(',');
            for (var i = 0; i < values.length; i++) {
                val = values[i];
                xval = {};
                if (val.indexOf(':') > 0) {
                    val = val.split(':');
                    xval['id'] = val[0];
                    xval['caption'] = val[1];
                } else {
                    xval['caption'] = val;
                }
                localStore.setItem('root.r_' + i, null, xval);
            }
            var store = new gnr.GnrStoreBag({mainbag:localStore});
            attributes.searchAttr = 'caption';
            store._identifier = 'id';
        } else {
            var storeAttrs = objectExtract(attributes, 'storepath,storeid,storecaption');
            var savedAttrs = {};
            var store = new gnr.GnrStoreBag({datapath: sourceNode.absDatapath(storeAttrs.storepath)});
            attributes.searchAttr = store.rootDataNode().attr['caption'] || storeAttrs['storecaption'] || 'caption';
            attributes.autoComplete = attributes.autoComplete || false;
            store._identifier = store.rootDataNode().attr['id'] || storeAttrs['storeid'] || 'id';
        }
        attributes.store = store;
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        var tag = 'cls_' + sourceNode.attr.tag;
        dojo.addClass(widget.domNode.childNodes[0], tag);
        this.connectFocus(widget);
        this.connectForUpdate(widget, sourceNode);
        if (dojo_version == '1.1') {
            if (dojo.isSafari) {
                dojo.connect(widget.focusNode, 'onkeydown', widget, '_onKeyPress');
            }
        }
    },
    /*patch__onBlur: function(){
     this._hideResultList();
     this._arrowIdle();
     this.inherited(arguments);
     }*/

    connectFocus: function(widget, savedAttrs, sourceNode) {
        var timeoutId = null;

        dojo.connect(widget, 'onFocus', widget, function(e) {
            // select all text in the current field -- (TODO: reason for the delay)
            timeoutId = setTimeout(dojo.hitch(this, 'selectAllInputText'), 300);
        });
        dojo.connect(widget, 'onBlur', widget, function(e) {
            clearTimeout(timeoutId); // prevent selecting all text (and thus messing with focus) if we're moving to another field before the timeout fires
            this.validate(e);
        });
    },

    mixin_selectAllInputText: function() {
        dijit.selectInputText(this.focusNode);
    },
    mixin__updateSelect: function(item) {
        //var item=this.lastSelectedItem;
        var row = item ? item.attr : {};
        if (this.sourceNode.attr.selectedRecord) {
            var path = this.sourceNode.attrDatapath('selectedRecord');
            this.sourceNode.setRelativeData(path, new gnr.GnrBag(row));
        }
        if (this.sourceNode.attr.selectedCaption) {
            var path = this.sourceNode.attrDatapath('selectedCaption');
            this.sourceNode.setRelativeData(path, row['caption'], null, false, 'selected_');
        }
        var selattr = objectExtract(this.sourceNode.attr, 'selected_*', true);
        var val;
        for (var sel in selattr) {
            var path = this.sourceNode.attrDatapath('selected_' + sel);
            val = row[sel];
            this.sourceNode.setRelativeData(path, val, null, false, 'selected_');
        }
    },
    connectForUpdate: function(widget, sourceNode) {
        return;
    }
});
dojo.declare("gnr.widgets.dbBaseCombo", gnr.widgets.BaseCombo, {
    creating: function(attributes, sourceNode) {
        var savedAttrs = {};
        var hasDownArrow;
        if (attributes.hasDownArrow) {
            attributes.limit = attributes.limit || 0;
        } else {
            attributes.hasDownArrow = false
        }
        var resolverAttrs = objectExtract(attributes, 'method,dbtable,columns,limit,condition,alternatePkey,auxColumns,hiddenColumns,rowcaption,order_by,selectmethod,weakCondition,storename');
        var selectedColumns = objectExtract(attributes, 'selected_*');
        if (objectNotEmpty(selectedColumns)) {
            var hiddenColumns;
            if (hiddenColumns in resolverAttrs) {
                hiddenColumns = resolverAttrs['hiddenColumns'].split(',');
                for (var i = 0; i < hiddenColumns.length; i++) {
                    selectedColumns[hiddenColumns[i]] = null;
                }
            }
            hiddenColumns = [];
            for (hiddenColumn in selectedColumns) {
                hiddenColumns.push(hiddenColumn);
            }
            resolverAttrs['hiddenColumns'] = hiddenColumns.join(',');
        }
        resolverAttrs['method'] = resolverAttrs['method'] || 'app.dbSelect';
        var clientCache = objectPop(attributes, 'clientCache', genro.cache_dbselect); //to set default true after testing
        resolverAttrs['notnull'] = attributes['validate_notnull'];
        savedAttrs['dbtable'] = resolverAttrs['dbtable'];
        savedAttrs['auxColumns'] = resolverAttrs['auxColumns'];
        var storeAttrs = objectExtract(attributes, 'store_*');
        objectExtract(attributes, 'condition_*');
        objectUpdate(resolverAttrs, objectExtract(sourceNode.attr, 'condition_*', true));
        resolverAttrs['exclude'] = sourceNode.attr['exclude']; // from sourceNode.attr because ^ has to be resolved at runtime
        resolverAttrs._id = '';
        resolverAttrs._querystring = '';

        var store;
        savedAttrs['record'] = objectPop(storeAttrs, 'record');
        attributes.searchAttr = storeAttrs['caption'] || 'caption';
        store = new gnr.GnrStoreQuery({'searchAttr':attributes.searchAttr});

        store._identifier = resolverAttrs['alternatePkey'] || storeAttrs['id'] || '_pkey';
        if (clientCache) {
            var storageMode = 'sessionStorage' in window ? 'session' : 'localStorage' in window ? 'local' : null;
            if (storageMode) {
                store.storageMode = storageMode;
                store.cachePrefix = 'DBSEL_' + savedAttrs['dbtable'] + '_';
            }
        }
        resolverAttrs._sourceNode = sourceNode;
        //resolverAttrs.sync = true
        var resolver = new gnr.GnrRemoteResolver(resolverAttrs, true, 0);

        resolver.sourceNode = sourceNode;

        store.rootDataNode().setResolver(resolver);
        attributes.searchDelay = attributes.searchDelay || 300;
        attributes.autoComplete = attributes.autoComplete || false;
        attributes.ignoreCase = (attributes.ignoreCase == false) ? false : true;
        //store._remote;
        attributes.store = store;
        return savedAttrs;
    },
    mixin_setDbtable:function(value) {
        this.store.rootDataNode()._resolver.kwargs.dbtable = value;
    },
    mixin_onSetValueFromItem: function(item, priorityChange) {
        if (!item.attr.caption) {
            return;
        }
        this.store._lastSelectedItem = item;
        this.store._lastSelectedCaption = this.labelFunc(item, this.store);

        if (this.sourceNode.attr.gridcell) {
            this._updateSelect(item);
            if (priorityChange) {
                this.cellNext = 'RIGHT';
                this.onBlur();
            }
        }
        else {
            if (this._hasBeenBlurred) {
                this._updateSelect(item);
                this._hasBeenBlurred = false;
            }
        }
    },
    connectForUpdate: function(widget, sourceNode) {
        return;
    },
    created: function(widget, savedAttrs, sourceNode) {
        if (savedAttrs.auxColumns) {
            widget._popupWidget = new gnr.Gnr_ComboBoxMenu({onChange: dojo.hitch(widget, widget._selectOption)});
        }
        this.connectForUpdate(widget, sourceNode);
        var tag = 'cls_' + sourceNode.attr.tag;
        dojo.addClass(widget.domNode.childNodes[0], tag);
        this.connectFocus(widget, savedAttrs, sourceNode);
        if (dojo_version == '1.1') {
            if (dojo.isSafari) {
                dojo.connect(widget.focusNode, 'onkeydown', widget, '_onKeyPress');
            }
        }
        //dojo.connect(widget, '_doSelect', widget,'_onDoSelect');                 
    }
});

dojo.declare("gnr.widgets.FilteringSelect", gnr.widgets.BaseCombo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'FilteringSelect';
    },
    //this patch will fix the problem where the displayed value stuck for a new record
    patch_setValue:function(value, priorityChange) {
        this.setValue_replaced(value, priorityChange);
        if (!this._isvalid) {
            this.valueNode.value = null;
            this.setDisplayedValue('');
        }
    },
    connectForUpdate: function(widget, sourceNode) {
        var selattr = objectExtract(widget.sourceNode.attr, 'selected_*', true);
        if (objectNotEmpty(selattr)) {
            dojo.connect(widget, '_doSelect', widget, function() {
                this._updateSelect(this.item);
            });
        }
    }
});
dojo.declare("gnr.widgets.ComboBox", gnr.widgets.BaseCombo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'ComboBox';
    }
});

dojo.declare("gnr.widgets.dbSelect", gnr.widgets.dbBaseCombo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'FilteringSelect';
    },
    connectForUpdate: function(widget, sourceNode) {
        dojo.connect(widget, '_setValueFromItem', widget, 'onSetValueFromItem');
        if (!("validate_dbselect" in sourceNode.attr)) {
            sourceNode.attr.validate_dbselect = true;
        }
        if (!("validate_dbselect_error" in sourceNode.attr)) {
            sourceNode.attr.validate_dbselect_error = 'Not existing value';
        }
    }
});

dojo.declare("gnr.widgets.dbComboBox", gnr.widgets.dbBaseCombo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'ComboBox';
    },
    connectForUpdate: function(widget, sourceNode) {
        var selattr = objectExtract(widget.sourceNode.attr, 'selected_*', true);
        if ('selectedRecord' in widget.sourceNode.attr || objectNotEmpty(selattr)) {
            dojo.connect(widget, '_doSelect', widget, function() {
                this._updateSelect(this.item);
            });
        }
    }
});


dojo.declare("gnr.widgets.DropDownButton", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'DropDownButton';
    },
    creating:function(attributes, sourceNode) {
        var savedAttrs = {};
        var buttoNodeAttr = 'height,width,padding';
        var savedAttrs = objectExtract(attributes, 'fire_*');
        savedAttrs['_style'] = genro.dom.getStyleDict(objectExtract(attributes, buttoNodeAttr));
        savedAttrs['action'] = objectPop(attributes, 'action');
        savedAttrs['fire'] = objectPop(attributes, 'fire');
        savedAttrs['arrow'] = objectPop(attributes, 'arrow');
        attributes['label'] = attributes['label'] || '';
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        if (savedAttrs.arrow == false) {
            var arrow = dojo.query(".dijitArrowButtonInner", widget.domNode);
            if (arrow.length > 0) {
                arrow = arrow[0];
                arrow.parentNode.removeChild(arrow);
            }
        }
        if (savedAttrs['_style']) {
            var buttonNode = dojo.query(".dijitButtonNode", widget.domNode)[0];
            dojo.style(buttonNode, savedAttrs['_style']);
        }
    },
    patch_addChild:function(dropDownContent) {
        this.dropDown = dropDownContent;
    },
    patch_destroy: function() {
        if (this.dropDown) {
            this.dropDown.destroyRecursive();
        }
        this.destroy_replaced.call(this);
    },
    versionpatch_15_openDropDown: function() {
        var sourceNode = this.dropDown.sourceNode;
        if (sourceNode) {
            sourceNode.refresh();
            this.dropDown = sourceNode.widget;
        }
        this.openDropDown_replaced();
    }
    ,
    versionpatch_11__openDropDown: function(evtDomNode) {
        var sourceNode = this.dropDown.sourceNode;
        if (sourceNode) {
            sourceNode.refresh();
            this.dropDown = sourceNode.widget;
        }
        var dropDown = this.dropDown;
        var oldWidth = dropDown.domNode.style.width;
        var self = this;

        dijit.popup.open({
            parent: this,
            popup: dropDown,
            around: evtDomNode || this.domNode,
            orient:
                // TODO: add user-defined positioning option, like in Tooltip.js
                    this.isLeftToRight() ? {'BL':'TL', 'BR':'TR', 'TL':'BL', 'TR':'BR'}
                            : {'BR':'TR', 'BL':'TL', 'TR':'BR', 'TL':'BL'},
            onExecute: function() {
                self._closeDropDown(true);
            },
            onCancel: function() {
                self._closeDropDown(true);
            },
            onClose: function() {
                dropDown.domNode.style.width = oldWidth;
                self.popupStateNode.removeAttribute("popupActive");
                this._opened = false;
            }
        });
        if (this.domNode.offsetWidth > dropDown.domNode.offsetWidth) {
            var adjustNode = null;
            if (!this.isLeftToRight()) {
                adjustNode = dropDown.domNode.parentNode;
                var oldRight = adjustNode.offsetLeft + adjustNode.offsetWidth;
            }
            // make menu at least as wide as the button
            dojo.marginBox(dropDown.domNode, {w: this.domNode.offsetWidth});
            if (adjustNode) {
                adjustNode.style.left = oldRight - this.domNode.offsetWidth + "px";
            }
        }
        this.popupStateNode.setAttribute("popupActive", "true");
        this._opened = true;
        if (dropDown.focus) {
            dropDown.focus();
        }
        // TODO: set this.checked and call setStateClass(), to affect button look while drop down is shown
    },
    patch_startup: function() {
        // the child widget from srcNodeRef is the dropdown widget.  Insert it in the page DOM,
        // make it invisible, and store a reference to pass to the popup code.
        if (!this.dropDown) {
            var dropDownNode = dojo.query("[widgetId]", this.dropDownContainer)[0];
            this.dropDown = dijit.byNode(dropDownNode);
            delete this.dropDownContainer;
        }
        dojo.body().appendChild(this.dropDown.domNode);
        this.dropDown.domNode.style.display = "none";
    }
});


// Tree d11 ---------------------
dojo.declare("gnr.widgets.Tree", gnr.widgets.baseDojo, {
    constructor: function() {
        this._domtag = 'div';
        this._dojotag = 'Tree';
    },
    creating: function(attributes, sourceNode) {
        dojo.require("dijit.Tree");
        // var nodeAttributes = objectExtract(attributes,'node_*');
        var storepath = sourceNode.absDatapath(objectPop(attributes, 'storepath'));
        var labelAttribute = objectPop(attributes, 'labelAttribute');
        var labelCb = objectPop(attributes, 'labelCb');
        var hideValues = objectPop(attributes, 'hideValues');
        var _identifier = objectPop(attributes, 'identifier') || '#id';
        if (labelCb) {
            labelCb = funcCreate(labelCb);
        }
        var store = new gnr.GnrStoreBag({datapath:storepath,_identifier:_identifier,
            hideValues:hideValues,
            labelAttribute:labelAttribute,
            labelCb:labelCb});
        var model = new dijit.tree.ForestStoreModel({store: store,childrenAttrs: ["#v"]});
        attributes['model'] = model;
        attributes['showRoot'] = false;
        attributes['persist'] = attributes['persist'] || false;
        if (attributes['getLabel']) {
            var labelGetter = funcCreate(attributes['getLabel'], 'node');
            attributes.getLabel = function(node) {
                if (node.attr) {
                    return labelGetter(node);
                }
            };
        }
        if (!attributes['getLabelClass']) {
            attributes['getLabelClass'] = function(node, opened) {
                var labelClass;
                if (opened) {
                    return node.attr.labelClassOpened || node.attr.labelClass;
                } else {
                    return node.attr.labelClassClosed || node.attr.labelClass;
                }
            };
        }
        var labelClassGetter = funcCreate(attributes['getLabelClass'], 'node,opened');

        var selectedLabelClass = attributes['selectedLabelClass'];
        attributes.getLabelClass = function(node, opened) {
            if (node.attr) {
                var labelClass = labelClassGetter.call(this, node, opened);
                if (selectedLabelClass) {
                    return (this.currentSelectedNode && this.currentSelectedNode.item == node) ? labelClass + ' ' + selectedLabelClass : labelClass;
                } else {
                    return labelClass;
                }
            }
            ;
        };
        if (attributes['getIconClass']) {
            var iconGetter = funcCreate(attributes['getIconClass'], 'node,opened');
            attributes.getIconClass = function(node, opened) {
                if (node.attr) {
                    return iconGetter(node, opened);
                }
            };
        }
        if (attributes.onChecked) {
            attributes.getIconClass = function(node, opened) {
                if (!(node instanceof gnr.GnrBagNode)) {
                    return;
                }
                if (node.attr) {
                    if (!('checked' in node.attr)) {
                        node.attr.checked = this.tree.checkBoxCalcStatus(node);
                    }
                    return (node.attr.checked == -1) ? "checkboxOnOff" : node.attr.checked ? "checkboxOn" : "checkboxOff";
                }
            };
        }
        if (attributes.selectedPath) {
            sourceNode.registerDynAttr('selectedPath');
        }
        var tooltipAttrs = objectExtract(attributes, 'tooltip_*');
        var savedAttrs = objectExtract(attributes, 'inspect,autoCollapse,onChecked');
        if (objectNotEmpty(tooltipAttrs)) {
            savedAttrs['tooltipAttrs'] = tooltipAttrs;
        }
        ;
        // attributes.gnrNodeAttributes=nodeAttributes;
        attributes.sourceNode = sourceNode;
        return savedAttrs;

    },
    created: function(widget, savedAttrs, sourceNode) {
        if (savedAttrs.tooltipAttrs) {

            var funcToCall = funcCreate(savedAttrs.tooltipAttrs.callback, 'sourceNode,treeNode', widget);
            var cb = function(n) {
                var item = dijit.getEnclosingWidget(n).item;
                return funcToCall(item, n);
            };

            genro.wdg.create('tooltip', null, {label:cb,
                validclass:'dijitTreeLabel',
                modifiers:savedAttrs.tooltipAttrs.modifiers
            }).connectOneNode(widget.domNode);
        }
        ;
        if (savedAttrs.inspect) {
            var modifiers = (savedAttrs.inspect == true) ? '' : savedAttrs.inspect;
            genro.wdg.create('tooltip', null, {label:function(n) {
                return genro.dev.bagAttributesTable(n);
            },
                validclass:'dijitTreeLabel',
                modifiers:modifiers
            }).connectOneNode(widget.domNode);
        }
        ;

        //dojo.connect(widget,'onClick',widget,'_updateSelect');
        var storepath = widget.model.store.datapath;
        if ((storepath == '*D') || (storepath == '*S'))
            widget._datasubscriber = dojo.subscribe('_trigger_data',
                    widget, function(kw) {
                this.setStorepath('', kw);
            });
        else {
            sourceNode.registerDynAttr('storepath');
        }
        if (savedAttrs.onChecked) {
            widget.checkBoxTree = true;
            if (savedAttrs.onChecked != true) {
                widget.onChecked = funcCreate(savedAttrs.onChecked, 'node,event');
            }
            ;
        }
        if (savedAttrs.autoCollapse) {
            dojo.connect(widget, '_expandNode', function(node) {
                dojo.forEach(node.getParent().getChildren(), function(n) {
                    if (n != node && n.isExpanded) {
                        n.tree._collapseNode(n);
                    }
                });
            });
        }
    },
    fillDragInfo:function(dragInfo) {
        dragInfo.treenode = dragInfo.widget;
        dragInfo.widget = dragInfo.widget.tree;
        dragInfo.treeItem = dragInfo.treenode.item;

    },
    fillDropInfo:function(dropInfo) {
        dropInfo.treenode = dropInfo.widget;
        dropInfo.widget = dropInfo.widget.tree;
        dropInfo.treeItem = dropInfo.treenode.item;
        dropInfo.outline = dropInfo.treenode.domNode;

    },
    onDragStart:function(dragInfo) {
        var item = dragInfo.treenode.item;
        var result = {};
        if (item instanceof gnr.GnrBagNode) {
            var v = item.getValue('static');
            result['text/plain'] = v;
            result['text/xml'] = v;
        } else {
            result['text/plain'] = item.label;
        }
        result['treenode'] = {'fullpath':item.getFullpath(),'relpath':item.getFullpath(null, dragInfo.treenode.tree.model.store.rootData())};
        return result;
    },
    attributes_mixin_checkBoxCalcStatus:function(bagnode) {
        var checked;
        if (bagnode._resolver && bagnode._resolver.expired()) {
            return false;
        } else if (bagnode._value instanceof gnr.GnrBag) {
            var ck = null;
            bagnode._value.forEach(function(node) {
                var checked = ('checked' in node.attr) ? node.attr.checked : -1;
                ck = (ck == null) ? checked : (ck != checked) ? -1 : ck;
            }, 'static');
        }
        return ck;
    },
    mixin_clickOnCheckbox:function(bagnode, e) {
        var checked = bagnode.attr.checked ? false : true;
        var walkmode = this.sourceNode.attr.eagerCheck ? null : 'static';
        var updBranchCheckedStatus = function(bag) {
            bag.forEach(function(n) {
                var v = n.getValue(walkmode);
                if (v instanceof gnr.GnrBag) {
                    updBranchCheckedStatus(v);
                    var checkedStatus = dojo.every(v.getNodes(), function(cn) {
                        return cn.attr.checked == true;
                    });
                    if (!checkedStatus) {
                        var allUnchecked = dojo.every(v.getNodes(), function(cn) {
                            return cn.attr.checked == false;
                        });
                        checkedStatus = allUnchecked ? false : -1;
                    }
                    n.setAttr({'checked':checkedStatus}, true, true);

                } else if (n._resolver && n._resolver.expired()) {
                    n.setAttr({'checked':false}, true, true);
                } else {
                    n.setAttr({'checked':checked}, true, true);
                }
            });
        };
        if (bagnode.getValue) {
            var value = bagnode.getValue();
            if (value instanceof gnr.GnrBag) {
                updBranchCheckedStatus(value);
            }
        }
        bagnode.setAttr({'checked':checked}, true, true);
        var parentNode = bagnode.getParentNode();
        var rootNodeId = genro.getDataNode(this.model.store.datapath)._id;
        while (parentNode && (parentNode._id != rootNodeId)) {
            parentNode.setAttr({'checked':this.checkBoxCalcStatus(parentNode)}, true, true);
            var parentNode = parentNode.getParentNode();
        }
        if (this.sourceNode.attr.nodeId) {
            genro.publish(this.sourceNode.attr.nodeId + '_checked', bagnode);
        }

    },
    versionpatch_11__onClick:function(e) {
        var nodeWidget = dijit.getEnclosingWidget(e.target);
        if (dojo.hasClass(e.target, 'dijitTreeIcon') && this.tree.checkBoxTree) {
            var bagnode = nodeWidget.item;
            if (bagnode instanceof gnr.GnrBagNode) {
                var onCheck = this.onChecked ? this.onChecked(bagnode, e) : true;
                if (onCheck != false) {
                    this.tree.clickOnCheckbox(bagnode, e);
                }
            }
            dojo.stopEvent(e);
            return;
        }
        var nodeWidget = dijit.getEnclosingWidget(e.target);
        if (nodeWidget.htmlLabel && (!dojo.hasClass(e.target, 'dijitTreeExpando'))) {
            return;
        }
        if (nodeWidget == nodeWidget.tree.rootNode) {
            return;
        }
        nodeWidget.__eventmodifier = eventToString(e);
        this._onClick_replaced(e);
        if (genro.wdg.filterEvent(e, '*', 'dijitTreeLabel,dijitTreeContent')) {
            this.setSelected(nodeWidget);
            this._updateSelect(nodeWidget.item, nodeWidget);
        }
    },
    versionpatch_15__onClick:function(nodeWidget, e) {
        // summary:
        //		Translates click events into commands for the controller to process
        if (dojo.hasClass(e.target, 'dijitTreeIcon') && this.tree.checkBoxTree) {
            var bagnode = nodeWidget.item;
            if (bagnode instanceof gnr.GnrBagNode) {
                var onCheck = this.onChecked ? this.onChecked(bagnode, e) : true;
                if (onCheck != false) {
                    this.tree.clickOnCheckbox(bagnode, e);
                }
            }
            dojo.stopEvent(e);
            return;
        }
        if (nodeWidget.htmlLabel && (!dojo.hasClass(e.target, 'dijitTreeExpando'))) {
            return;
        }
        if (nodeWidget == nodeWidget.tree.rootNode) {
            return;
        }
        nodeWidget.__eventmodifier = eventToString(e);
        this._onClick_replaced(nodeWidget, e);
        if (genro.wdg.filterEvent(e, '*', 'dijitTreeLabel,dijitTreeContent')) {
            this.setSelected(nodeWidget);
            this._updateSelect(nodeWidget.item, nodeWidget);
        }
    },
    mixin_getItemById: function(id) {
        return this.model.store.rootData().findNodeById(id);
    },
    attributes_mixin__saveState: function() {
        //summary: create and save a cookie with the currently expanded nodes identifiers
        if (!this.persist) {
            return;
        }
        var cookiepars = {};
        if (this.persist == 'site') {
            cookiepars.path = genro.getData('gnr.homeUrl');
        }
        var ary = [];
        for (var id in this._openedItemIds) {
            ary.push(id);
        }
        dojo.cookie(this.cookieName, ary.join(","), cookiepars);
    },
    mixin_loadState:function(val, kw) {
        var cookie = dojo.cookie(this.cookieName);
        this._openedItemIds = {};
        if (cookie) {
            dojo.forEach(cookie.split(','), function(item) {
                this._openedItemIds[item] = true;
            }, this);
        }
    },
    mixin_setStorepath:function(val, kw) {
        //genro.debug('trigger_store:'+kw.evt+' at '+kw.pathlist.join('.'));
        if (kw.evt == 'upd') {
            if (kw.updvalue) {
                if (kw.value instanceof gnr.GnrBag) {
                    this._onItemChildrenChange(/*dojo.data.Item*/ kw.node, /*dojo.data.Item[]*/ kw.value.getNodes());
                } else {
                    this._onItemChange({id:kw.node._id + 'c',label:kw.value});
                }
            } else if (kw.updattr) {
                this._onItemChange(kw.node);
            }
            //this.model.store._triggerUpd(kw);
        } else if (kw.evt == 'ins') {
            this.model.store._triggerIns(kw);
        } else if (kw.evt == 'del') {
            this._onItemChildrenChange(/*dojo.data.Item*/ kw.where.getParentNode(), /*dojo.data.Item[]*/ kw.where.getNodes());
            //this.model.store._triggerDel(kw);
        }
    },

    mixin_setSelectedPath:function(path, kw) {
        if (kw.reason == this) {
            return;
        }
        var curr = this.model.store.rootData();
        var currNode,treeNode;
        if (!kw.value) {
            this.setSelected(null);
            this._updateSelect(null);
            return;
        }
        var pathList = kw.value.split('.');
        for (var i = 0; i < pathList.length; i++) {
            currNode = curr.getNode(pathList[i]);
            treeNode = this._itemNodeMap[currNode._id];
            curr = currNode.getValue();
            if (i < pathList.length - 1) {
                if (!treeNode.isExpanded) {
                    this._expandNode(treeNode);
                }
                ;
            }

        }
        ;


        var currTree = this;
        setTimeout(function() {
            currTree.focusNode(treeNode);
            currTree.setSelected(treeNode);
            currTree._updateSelect(currNode);
        }, 100);
    },
    mixin_setSelected:function(node) {
        var prevSelectedNode = this.currentSelectedNode;
        this.currentSelectedNode = node;
        if (prevSelectedNode) {
            prevSelectedNode._updateItemClasses(prevSelectedNode.item);
        }
        if (node) {
            node._updateItemClasses(node.item);
        }
        ;
    },
    mixin_isSelectedItem:function(item) {
        return this.currentSelectedNode ? this.currentSelectedNode.item == item : false;
    },

    mixin__updateSelect: function(item, node) {
        var modifiers = objectPop(node, '__eventmodifier');
        var reason = this;
        var attributes = {};
        if (modifiers) {
            attributes._modifiers = modifiers;
        }
        if (!item) {
            var item = new gnr.GnrBagNode();
        }
        else if (!item._id) {
            item = node.getParent().item;
        }
        if (this.sourceNode.attr.selectedLabel) {
            var path = this.sourceNode.attrDatapath('selectedLabel');
            this.sourceNode.setRelativeData(path, item.label, attributes, null, reason);
        }
        if (this.sourceNode.attr.selectedItem) {
            var path = this.sourceNode.attrDatapath('selectedItem');
            this.sourceNode.setRelativeData(path, item, attributes, null, reason);
        }
        if (this.sourceNode.attr.selectedPath) {
            var path = this.sourceNode.attrDatapath('selectedPath', reason);
            var root = this.model.store.rootData();
            this.sourceNode.setRelativeData(path, item.getFullpath(null, root), objectUpdate(attributes, item.attr), null, reason);
        }
        var selattr = objectExtract(this.sourceNode.attr, 'selected_*', true);
        for (var sel in selattr) {
            var path = this.sourceNode.attrDatapath('selected_' + sel);
            this.sourceNode.setRelativeData(path, item.attr[sel], attributes, null, reason);
        }
    }
});

dojo.declare("gnr.widgets.GoogleMap", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    creating: function(attributes, sourceNode) {
        savedAttrs = objectExtract(attributes, 'map_*');
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        var center = (savedAttrs.center || "37.4419,-122.1419").split(',');
        var maptype = savedAttrs.maptype || 'normal';
        var controls = savedAttrs.controls;
        var zoom = savedAttrs.zoom || 13;
        if (GBrowserIsCompatible()) {
            var map = new GMap2(widget);
            sourceNode.googleMap = map;
            map.setCenter(new GLatLng(parseFloat(center[0]), parseFloat(center[1])), zoom);
            map.setMapType(window['G_' + maptype.toUpperCase() + '_MAP']);
            if (controls) {
                controls = controls.split(',');
                for (var i = 0; i < controls.length; i++) {
                    var cnt = window['G' + controls[i] + 'Control'];
                    map.addControl(new cnt());
                }
            }
            var mapcommands = objectExtract(this, 'map_*', true);
            for (var command in mapcommands) {
                sourceNode[command] = mapcommands[command];
            }
        } else {
            alert('not compatible browser');
        }
    },

    map_getMapLoc: function(center) {
        var c = center.split(',');
        return new GLatLng(parseFloat(c[1]), parseFloat(c[0]));
    },
    map_newMarker: function(center) {
        return new GMarker(this.getMapLoc(center));
    }
});


dojo.declare("gnr.widgets.fileInput", gnr.widgets.baseDojo, {
    constructor: function() {
        this._domtag = 'input';
        this._dojotag = 'FileInput';
    },
    creating: function(attributes, sourceNode) {
        dojo.require("dojo.io.iframe");
        var remotePars = objectExtract(attributes, 'remote_*');
        var savedAttrs = objectExtract(attributes, 'method');
        savedAttrs.onUpload = objectPop(attributes, 'onUpload', 'alert("Upload Done")');
        savedAttrs.remotePars = remotePars;
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        widget.savedAttrs = savedAttrs;
    },
    mixin_uploadFile: function() {
        var fname = this.fileInput.value;
        if (!fname || this._sent) {
            return;
        }
        var ext = fname.slice(fname.lastIndexOf('.'));
        this.savedAttrs.remotePars.ext = ext;
        var remotePars = genro.rpc.serializeParameters(genro.src.dynamicParameters(this.savedAttrs.remotePars));
        var method = this.savedAttrs.method;
        var url = genro.remoteUrl(method, remotePars);
        var _newForm = document.createElement('form');
        _newForm.setAttribute("enctype", "multipart/form-data");
        var node = dojo.clone(this.fileInput);
        _newForm.appendChild(this.fileInput);
        this.fileInput.setAttribute('name', 'fileHandle');
        dojo.body().appendChild(_newForm);
        var handle = dojo.hitch(this, funcCreate(this.savedAttrs.onUpload));
        dojo.io.iframe.send({
            url: url,
            form: _newForm,
            handleAs: "text",
            handle: handle
        });
    }
});

dojo.declare("gnr.widgets.fileInputBlind", gnr.widgets.fileInput, {
    constructor: function() {
        this._domtag = 'input';
        this._dojotag = 'fileInputBlind';
    }});

dojo.declare("gnr.widgets.fileUploader", gnr.widgets.baseDojo, {
    constructor: function() {
        this._domtag = 'textarea';
        this._dojotag = 'dojox.widget.FileInputAuto';
    },
    creating: function(attributes, sourceNode) {
        var uploadPars = objectUpdate({}, sourceNode.attr);
        uploadPars.mode = 'html';
        objectExtract(uploadPars, 'tag,method,blurDelay,duration,uploadMessage,cancelText,label,name,id,onComplete');
        savedAttrs = objectExtract(attributes, 'method');
        dojo.require("dojox.widget.FileInputAuto");
        var onComplete = objectPop(attributes, 'onComplete');
        savedAttrs.uploadPars = uploadPars;
        if (onComplete) {
            attributes.onComplete = funcCreate(onComplete);
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        widget.savedAttrs = savedAttrs;
    },
    mixin__sendFile: function(/* Event */e) {
        // summary: triggers the chain of events needed to upload a file in the background.
        if (!this.fileInput.value || this._sent) {
            return;
        }
        var uploadPars = genro.rpc.serializeParameters(genro.src.dynamicParameters(this.savedAttrs.uploadPars));
        var method = this.savedAttrs.method;
        var url = genro.remoteUrl(method, uploadPars);
        dojo.style(this.fakeNodeHolder, "display", "none");
        dojo.style(this.overlay, "opacity", "0");
        dojo.style(this.overlay, "display", "block");
        this.setMessage(this.uploadMessage);
        dojo.fadeIn({ node: this.overlay, duration:this.duration }).play();
        var _newForm = document.createElement('form');
        _newForm.setAttribute("enctype", "multipart/form-data");
        var node = dojo.clone(this.fileInput);
        _newForm.appendChild(this.fileInput);
        this.fileInput.setAttribute('name', 'fileHandle');
        dojo.body().appendChild(_newForm);
        dojo.io.iframe.send({
            url: url,
            form: _newForm,
            handleAs: "text",
            handle: dojo.hitch(this, "_handleSend")
        });
    },
    mixin__handleSend: function(data, ioArgs) {
        // summary: The callback to toggle the progressbar, and fire the user-defined callback

        if (!dojo.isIE) {
            // otherwise, this throws errors in ie? FIXME:
            this.overlay.innerHTML = "";
        }

        this._sent = true;
        dojo.style(this.overlay, "opacity", "0");
        dojo.style(this.overlay, "border", "none");
        dojo.style(this.overlay, "background", "none");

        this.overlay.style.backgroundImage = "none";
        this.fileInput.style.display = "none";
        this.fakeNodeHolder.style.display = "none";
        dojo.fadeIn({ node:this.overlay, duration:this.duration }).play(250);

        dojo.disconnect(this._blurListener);
        dojo.disconnect(this._focusListener);
        alert('fatto:' + data);
        this.onComplete(data, ioArgs, this);
    },

    onComplete : function(data, ioArgs, widget) {
        // this function is fired for every programatic FileUploadAuto
        // when the upload is complete. It uses dojo.io.iframe, which
        // expects the results to come wrapped in TEXTAREA tags.
        // this is IMPORTANT. to utilize FileUploadAuto (or Blind)
        // you have to pass your respose data in a TEXTAREA tag.
        // in our sample file (if you have php5 installed and have
        // file uploads enabled) it _should_ return some text in the
        // form of valid JSON data, like:
        // { status: "success", details: { size: "1024" } }
        // you can do whatever.
        //
        // the ioArgs is the standard ioArgs ref found in all dojo.xhr* methods.
        //
        // widget is a reference to the calling widget. you can manipulate the widget
        // from within this callback function 
        if (data) {
            var d = dojo.fromJson(data);
            if (d.status && d.status == "success") {
                widget.overlay.innerHTML = "success!";
            } else {
                widget.overlay.innerHTML = "error? ";
            }
        } else {
            // debug assist
        }
    }
});
    
    

