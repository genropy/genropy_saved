/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_wdg : Genro client widgets creator
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
dojo.require('dijit.Menu');

dojo.declare("gnr.GnrWdgHandler", null, {
    constructor: function(application) {
        this.application = application;
        this.noConvertStyle = {
            'table' :[ 'width', 'border'],
            'editor' :[ 'height'],
            'embed':['width','height'],
            'img':['width','height']};
        this.tagParameters = {};
        this.tagParameters['button'] = {'caption':'input'};
        this.tagParameters['contentpane'] = {'label':'input','layoutAlign':'select:top,bottom,left,right,client'};
        this.tagParameters['splitcontainer'] = {'activeSizing':'checkbox','sizerWidth':'input'};
        this.catalog = new gnr.GnrBag();
        this.namespace = {};
        //this.dummy_menu= new dijit.Menu();
        var htmlspace = ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'base', 'bdo', 'big', 'blockquote',
            'body', 'br', 'button', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
            'div', 'dfn', 'dl', 'dt', 'em', 'fieldset', 'form', 'frame', 'frameset',
            'h1', 'h2', 'h3','h4','h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe', 'img', 'input',
            'ins', 'kbd', 'label', 'legend', 'li', 'link', 'map', 'meta', 'noframes', 'noscript',
            'object', 'ol', 'optgroup', 'option', 'p', 'param', 'pre', 'q', 'samp', 'script',
            'select', 'small', 'span', 'strong', 'style', 'sub', 'sup', 'table', 'tbody', 'td',
            'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'ul', 'var','embed','audio','video'];
        for (var i = 0; i < htmlspace.length; i++) {
            tag = htmlspace[i];
            this.namespace[tag.toLowerCase()] = ['html',tag];
        }
        ;

        this.widgetcatalog = {'CheckBox':'dijit.form.CheckBox',
            'RadioButton':'dijit.form.CheckBox',
            'ComboBox':'dijit.form.ComboBox',
            'CurrencyTextBox':'dijit.form.CurrencyTextBox',
            'DateTextBox':'dijit.form.DateTextBox',
            'FilteringSelect':'dijit.form.FilteringSelect',
            'InlineEditBox':'dijit.InlineEditBox',
            'NumberSpinner':'dijit.form.NumberSpinner',
            'NumberTextBox':'dijit.form.NumberTextBox',
            'HorizontalSlider':'dijit.form.Slider',
            'VerticalSlider':'dijit.form.Slider',
            'SimpleTextarea':'dijit.form.SimpleTextarea',
            'MultiSelect':'dijit.form.MultiSelect',
            'TextBox':'dijit.form.TextBox',
            'TimeTextBox':'dijit.form.TimeTextBox',
            'ValidationTextBox':'dijit.form.ValidationTextBox',
            'AccordionContainer':'dijit.layout.AccordionContainer',
            'AccordionPane':'dijit.layout.AccordionContainer',
            'ContentPane':'dijit.layout.ContentPane',
            'BorderContainer':'dijit.layout.BorderContainer',
            'LayoutContainer':'dijit.layout.LayoutContainer',
            'SplitContainer':'dijit.layout.SplitContainer',
            'StackContainer':'dijit.layout.StackContainer',
            'TabContainer':'dijit.layout.TabContainer',
            'Button':'dijit.form.Button',
            'ToggleButton':'dijit.form.Button',
            'ComboButton':'dijit.form.Button,dijit.Menu',
            'DropDownButton':'dijit.form.Button,dijit.Menu',
            'Menu':'dijit.Menu',
            'MenuItem':'dijit.Menu',
            'MenuSeparator':'dijit.Menu',
            'PopupMenuItem':'dijit.Menu',
            'Toolbar':'dijit.Toolbar',
            'ToolbarSeparator':'dijit.Toolbar',
            'Dialog':'dijit.Dialog',
            'TooltipDialog':'dijit.Dialog',
            'ProgressBar':'dijit.ProgressBar',
            'TitlePane':'dijit.TitlePane',
            'Tooltip':'dijit.Tooltip',
            'ColorPalette':'dijit.ColorPalette',
            'Editor':'dijit.Editor,dijit._editor.plugins.LinkDialog,dijit._editor.plugins.FontChoice,dijit._editor.plugins.TextColor',
            'Tree':'dijit.Tree',
            'FloatingPane':'dojox.layout.FloatingPane',
            'Dock':'dojox.layout.FloatingPane',
            'RadioGroup':'dojox.layout.RadioGroup',
            'ResizeHandle':'dojox.layout.ResizeHandle',
            'SizingPane':'dojox.layout.SizingPane',
            'FisheyeList':'dojox.widget.FisheyeList',
            'Loader':'dojox.widget.Loader',
            'Toaster':'dojox.widget.Toaster',
            'FileInput':'dojox.widget.FileInput',
            'FileInputBlind':'dojox.widget.FileInputAuto',
            'FileInputAuto':'dojox.widget.FileInputAuto',
            'ColorPicker':'dojox.widget.ColorPicker',
            'SortList':'dojox.widget.SortList',
            'TimeSpinner':'dojox.widget.TimeSpinner',
            'Iterator':'dojox.widget.Iterator',
            'Gallery':'dojox.image.Gallery',
            'Lightbox':'dojox.image.Lightbox',
            'SlideShow':'dojox.image.SlideShow',
            'ThumbnailPicker':'dojox.image.ThumbnailPicker',
            'Deck':'dojox.presentation.Deck',
            'Slide':'dojox.presentation.Slide',
            'Grid':'dojox.grid.Grid:dojox.Grid',
            'VirtualGrid':'dojox.grid.VirtualGrid:dojox.VirtualGrid',
            'Calendar':'mywidgets.widget.Calendar,mywidgets.widget.Timezones',
            'GoogleMap':'',
            'GoogleChart':'',
            'GoogleVisualization':'',
            'CkEditor':'',
            'protovis':''
        };
        var tag;
        for (tag in this.widgetcatalog) {
            this.namespace[tag.toLowerCase()] = ['dojo',tag];
        }
        this.widgets = {};
        for (var wdg in gnr.widgets) {
            this.widgets[wdg.toLowerCase()] = wdg;
        }


    },
    makeDomNode:function(tag, destination, ind) {
        var ind = ind || -1;
        var domnode = document.createElement(tag);
        if (destination.containerNode) {
            destination.containerNode.appendChild(domnode);
        }
        else if (destination.domNode) {
            destination.domNode.appendChild(domnode);
        }
        else {
            if (typeof(ind) == 'object') {
                destination.replaceChild(domnode, ind);
            } else if (ind <= 0 || ind >= destination.childNodes.length) {
                destination.appendChild(domnode);
            } else {
                destination.insertBefore(domnode, destination.childNodes[ind]);
            }
        }
        return domnode;
    },
    getHandler:function(tag) {
        var lowertag = tag.toLowerCase();
        var handler = this.widgets[lowertag];
        if (!handler) {
            var nsItem = this.namespace[lowertag];
            if (!nsItem){
                return;
            }
            handler = this.widgets [('base' + nsItem[0]).toLowerCase()];
        }
        if (typeof(handler) == 'string') {
            this.widgets[lowertag] = new gnr.widgets[handler]();
            handler = this.widgets[lowertag];
        }
        return handler;
    },
    create:function(tag, destination, attributes, ind, sourceNode) {
        var attributes = attributes || {};
        var newobj, domnode;
        var handler = this.getHandler(tag);
        if (handler._beforeCreation) {
            var goOn = handler._beforeCreation(sourceNode);
            if (goOn === false) {
                return false;
            }
        }
        var domtag = handler._domtag || tag;
        if (ind == 'replace') {
            domnode = destination;
        } else if (domtag == '*') {
            domnode = null;
        } else {
            destination = handler._attachTo ? dojo.byId(handler._attachTo) : destination;
            domnode = this.makeDomNode(domtag, destination, ind);
        }
        if (typeof(ind) == 'object') {
            ind = -1; // should be index of domnode in destination ???
        }
        var tip = objectPop(attributes, 'tip');
        var visible = objectPop(attributes, 'visible');
        if (visible == false) {
            attributes.visibility = 'hidden';
        }
        var hidden = objectPop(attributes, 'hidden');
        if (hidden == true) {
            attributes.display = 'none';
        }
        //var disabled=objectPop(attributes, 'disabled') ? true:false;
        //attributes.disabled=disabled;
        var kw = {'postCreation':handler._creating(attributes, sourceNode),
            'readonly' : objectPop(attributes, 'readonly'),
            // 'disabled' : disabled,
            '_style': objectAsStyle(genro.dom.getStyleDict(attributes, (this.noConvertStyle[tag.toLowerCase()]))),
            '_class' : objectPop(attributes, '_class')
        };
        //var extracted = objectExtract(attributes, '_*'); // strip all attributes used only for triggering rebuild or as input for ==function
        //if(objectNotEmpty(extracted)){
        //    console.log('extracted: ' + extracted.toSource());
        //}
        if (! handler._dojowidget) {//This is an html object

            if (tip) {
                attributes['title'] = tip;
            }
            var extracted = objectExtract(attributes, '_*', {'_type':null}); // strip all attributes used only for triggering rebuild or as input for ==function
            newobj = this.createHtmlElement(domnode, attributes, kw, sourceNode);
            this.linkSourceNode(newobj, sourceNode, kw);
            newobj.gnr = handler;
        }
        else {//This is dojo widget
            newobj = this.createDojoWidget(tag, domnode, attributes, kw, sourceNode);
            //if(disabled){
            //    newobj.setAttribute('disabled', true);
            //}
            if (tip) {
                newobj.domNode.setAttribute('title', tip);
            }
            else {
                newobj.domNode.setAttribute('title', "");
            }
            this.linkSourceNode(newobj, sourceNode, kw);
            newobj.gnr = handler;
            if (destination && destination.addChild) {
                if (ind < 0) {
                    destination.addChild(newobj);
                }
                else {
                    destination.addChild(newobj, ind);
                }
            }
        }
        handler._created(newobj, kw.postCreation, sourceNode, ind);
        return newobj;

    },

    linkSourceNode:function(newobj, sourceNode, kw) {
        if (sourceNode) {
            if (newobj.domNode) {
                sourceNode.widget = newobj;
            } else {
                sourceNode.domNode = newobj;
            }
            newobj.sourceNode = sourceNode;
            //if(objectSize(kw.validators)>0){
            //     sourceNode.hasValidators = true;
            //     sourceNode.dataValidators = kw.validators;
            //}
        }
    },
    createHtmlElement:function(domnode, attributes, kw, sourceNode) {
        var innerHTML = objectPop(attributes, 'innerHTML');
        if ((!innerHTML) && sourceNode) {
            var template = objectPop(attributes, 'template');
            if (template) {
                objectPop(attributes, 'datasource');
                innerHTML = dataTemplate(template, sourceNode, sourceNode.attr.datasource);
            } else {
                innerHTML = sourceNode.getValue();
                innerHTML = (innerHTML instanceof gnr.GnrBag) ? null : innerHTML;
            }
        }

        if (kw._style) {
            domnode.style.cssText = kw._style;
        }
        if (kw._class) {
            genro.dom.addClass(domnode, kw._class);
        }
        if ('disabled' in attributes) {
            if (attributes.disabled) {
                attributes['disabled'] = 'disabled';
            }
            else {
                delete attributes['disabled'];
            }

        }
        if (kw.readonly) {
            attributes['readonly'] = 'readonly';
        }
        for (var oneattr in attributes) {
            domnode.setAttribute(oneattr, attributes[oneattr]);
        }
        if (innerHTML) {
            domnode.innerHTML = innerHTML;
        }
        return domnode;
    },
    getWidgetFactory: function(tag, handler) {
        var dojotag = this.namespace[(handler._dojotag || tag).toLowerCase()];
        var wdgpath;
        if (!dojotag) {
            wdgpath = handler._dojotag.split('.');
        } else {
            dojotag = dojotag[1];
            var requires = this.widgetcatalog[dojotag];
            if (stringContains(requires, ':')) {
                requires = requires.split(':');
                wdgpath = requires[1].split('.');
                requires = requires[0].split(',');
            }
            else {
                requires = requires.split(',');
                wdgpath = requires[0].split('.');
                wdgpath[wdgpath.length - 1] = dojotag;
            }
            for (var i = 0; i < requires.length; i++) {
                dojo.require(requires[i]);
            }
        }
        var wdgfactory = window;
        for (var i = 0; i < wdgpath.length; i++) {
            wdgfactory = wdgfactory[wdgpath[i]];
        }
        return wdgfactory;
    },
    createDojoWidget:function(tag, domnode, attributes, kw, sourceNode) {
        var handler = this.getHandler(tag);
        var wdgFactory = this.getWidgetFactory(tag, handler);
        var kw = kw || {};
        if (kw._style) {
            attributes['style'] = kw._style;
        }
        if (kw._class) {
            attributes['class'] = kw._class;
        }
        var proto = wdgFactory.prototype;
        for (var attr in attributes) {
            if (attr in proto) {
                if (typeof (proto[attr]) == 'function') {
                    attributes[attr] = funcCreate(attributes[attr]);
                }
            }
        }
        var attrmixins = objectExtract(handler, 'attributes_mixin_*', true);
        var validations = objectExtract(attributes, 'validate_*');
        var extracted = objectExtract(attributes, '_*', {'_type':null, '_identifier':null}); // strip all attributes used only for triggering rebuild or as input for ==function
        objectUpdate(attributes, attrmixins);
        var newobj = new wdgFactory(attributes, domnode);
        if (kw.readonly) {
            var field = dojo.byId(newobj.id);
            field.readOnly = true;
            field.style.cursor = 'default';
            dojo.connect(field, 'onfocus', function () {
                field.blur();
            });
        }
        if (objectNotEmpty(validations) || this.wdgIsSelect(sourceNode)) {
            sourceNode.setValidations();
            this.setIsValidMethod(newobj);
            dojo.connect(newobj, 'onFocus', function(e) {
                var errormessage = sourceNode.getValidationError();
                var warnings = sourceNode.getValidationWarnings();
                if (errormessage) {
                    setTimeout(function() {
                        sourceNode.widget.displayMessage(errormessage);
                    }, 1);
                } else if (warnings) {
                    warnings = warnings.join('<br />');
                    setTimeout(function() {
                        sourceNode.widget.displayMessage(warnings);
                    }, 1);
                }
            });
        }
        this.doMixin(newobj, handler, tag, sourceNode);
        return newobj;
    },
    wdgIsSelect: function(sourceNode) {
        if (sourceNode) { // tooltip and others are widgets w/o sourcenode
            return (sourceNode.attr.tag.toLowerCase() in {'dbselect':null,'filteringselect':null});
        }
    },
    setIsValidMethod:function(obj) {
        if (obj.isValid) {
            obj.isValid = function(isFocused) {
                if (isFocused) {
                    this.sourceNode.editing = true;
                    return true;
                } else {
                    if (this.sourceNode.editing) { //loosing focus after editing
                        this.sourceNode.editing = false;
                        if (genro.wdg.wdgIsSelect(this.sourceNode)) {
                            // FilteringSelect has no duoble isValid on exit, so return hasValidationError
                        } else {
                            return true; //go on to onChange to get new validations
                            //if value is not changed the next isValid call
                            //returns the old validationError (still correct)
                        }
                    }
                    return !this.sourceNode.hasValidationError();
                }
            };
        }
    },
    doMixin:function(obj, handler, tag, sourceNode) {
        var oldfunc, funcname, prefix,newfunc;
        var versionpatch = 'versionpatch_' + dojo.version.major + dojo.version.minor + '_';
        var ispatch;
        for (var prop in handler) {
            funcname = null;
            if (prop.indexOf('mixin_') == 0) {
                ispatch = false;
                funcname = prop.replace('mixin_', '');
            }
            else if (stringStartsWith(prop, 'versionpatch_')) {
                ispatch = true;
                if (stringStartsWith(prop, versionpatch)) {
                    funcname = prop.replace(versionpatch, '');
                }
            }
            else if (stringStartsWith(prop, 'patch_')) {
                ispatch = true;
                funcname = prop.replace('patch_', '');
            } else if (stringStartsWith(prop, 'nodemixin_')) {
                sourceNode[prop.replace('nodemixin_', '')] = handler[prop];
            } else if (stringStartsWith(prop, 'validatemixin_')) {
                if (sourceNode && (sourceNode.hasValidations())) {
                    sourceNode[prop.replace('validatemixin_', '')] = handler[prop];
                }
            }
            if (funcname) {
                oldfunc = obj[funcname];
                if (ispatch) {
                    obj[funcname] = handler[prop];
                    if (oldfunc) {
                        obj[funcname + '_replaced'] = oldfunc;
                    } else if ((!handler._basedojotag) || (handler._dojotag == handler._basedojotag)) {
                        genro.warning(tag + ' - Patch ' + prop + ': cannot find the replaced method.');
                    }
                } else {
                    if (oldfunc) {
                        genro.warning(tag + ' - Mixin ' + prop + ': method already existing.');
                        obj[funcname + '_replaced'] = oldfunc;
                    }
                    obj[funcname] = handler[prop];
                }
            }
        }
        return obj;
    },

    filterEvent: function (e, modifiers, validclass) {
        var result = false;
        var target = e.target;
        if (validclass && target.className && dojo.every(validclass.split(','), function(item) {
            return target.className.indexOf(item) < 0;
        })) {
            target = null;
        }
        if (target) {
            var modif = (modifiers || "").replace('*', '') || '';
            if (modif) {
                if (e.shiftKey) {
                    modif = modif.replace('shift', '');
                }
                if (e.ctrlKey) {
                    modif = modif.replace('ctrl', '');
                }
                if (e.altKey) {
                    modif = modif.replace('alt', '');
                }
                if (e.metaKey) {
                    modif = modif.replace('meta', '');
                }
                modif = modif.replace(/,/g, '').replace(/ /g, '');
            }
            if (modif == '') {
                result = true;
            }
            ;
        }
        return result;
    }
});

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
        if (cellDataNode.attr._editable === false) {
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
        if (attr.autoWdg) {
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
