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



function inlineWidget(evt){
    console.log('inlineWidget',domNode,evt);
    var domNode = evt.target;
    var varname = domNode.getAttribute('varname');
    var chunkNode = genro.dom.getBaseSourceNode(domNode);
    if(chunkNode.form && chunkNode.form.isDisabled()){
        return;
    }
    var templateHandler = chunkNode._templateHandler;
    var colattr = templateHandler.template.getAttr('main')['editcols'][varname];
    var containerNode = domNode.parentNode;

    if(!templateHandler._editRootNode){
        templateHandler._editRootNode = chunkNode.getValue().getNode('_chunk_inline_editor_',null,true);
        templateHandler._editRootNode.attr.datapath = chunkNode.absDatapath(chunkNode.attr.datasource);
    }

    var dt = colattr['dtype'];
    var widgets = {'L':'NumberTextBox','I':'NumberTextBox','D':'DateTextbox','R':'NumberTextBox','N':'NumberTextBox','H':'TimeTextBox','B':'CheckBox'};
    colattr['tag'] = widgets[dt] || 'Textbox';
    if('related_table' in colattr){
        colattr['tag'] = 'dbselect';
        colattr['dbtable'] = colattr['related_table'];
        if(colattr['related_table_lookup'] && !'hasDownArrow' in colattr){
            colattr['hasDownArrow'] = true;
        }
    }if('values' in colattr){
        colattr['tag'] = colattr.values.indexOf(':')>=0?'filteringselect':'combobox';
    }
    var sizer = templateHandler._editRootNode._('span',{_parentDomNode:containerNode,position:'absolute',
                                                                width:'auto',
                                                            top: -9999,
                                                            left: -9999}).getParentNode();

    sizer.domNode.innerHTML = domNode.innerHTML;

    if(colattr['tag'].toLowerCase()=='datetextbox'){
        colattr['width'] = '7em';
    }else{
        colattr['width'] = domNode.clientWidth+'px';
        colattr['connect_onkeyup'] = function(){
            var fn = this.widget.focusNode;
            sizer.domNode.innerHTML = fn.value;
            var dn = this.widget.domNode;
            dn.style.width = sizer.domNode.clientWidth+8+'px'
        }
    }
    colattr['min_width'] = '30px';
    colattr['value'] = '^.'+colattr['field'];
    colattr['_parentDomNode'] = containerNode;
    colattr['rejectInvalid'] = true;
    colattr['connect_onBlur'] = function(){
        var dataNodeAttr = genro.getDataNode(this.absDatapath(this.attr.value)).attr;
        this._destroy();
        sizer._destroy();
        genro.dom.removeClass(containerNode,'inlineediting')
    }

    colattr['attr__displayedValue']
   //var lowertag = colattr['tag'].toLowerCase();
   //if(this['tag_'+lowertag]){
   //    this['tag_'+lowertag].call(this,colname,colattr);
   //}
    //this.columns[colname.replace(/\W/g, '_')] = {'tag':colattr.tag,'attr':colattr};
    genro.dom.addClass(containerNode,'inlineediting')
    var widgetNode = templateHandler._editRootNode._(colattr.tag,colattr).getParentNode();
    widgetNode.widget.focus()

};

dojo.declare("gnr.GnrWdgHandler", null, {
    constructor: function(application) {
        this.application = application;
        this.noConvertStyle = {
            'table' :[ 'width', 'border'],
            'editor' :[ 'height'],
            'embed':['width','height'],
            'img':['width','height'],
            'canvas':['width','height']
            };
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
            'h1', 'h2', 'h3','h4','h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe','htmliframe', 'img', 'input',
            'ins', 'kbd', 'label', 'legend', 'li', 'link', 'map', 'meta', 'noframes', 'noscript',
            'object', 'ol', 'optgroup', 'option', 'p', 'param', 'pre', 'q', 'samp', 'script',
            'select', 'small', 'span', 'strong', 'style', 'sub', 'sup', 'table', 'tbody', 'td',
            'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'ul', 'var','embed','audio','video','canvas'];
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
            'DojoGrid':'dojox.grid.Grid:dojox.Grid',
            'VirtualGrid':'dojox.grid.VirtualGrid:dojox.VirtualGrid',
            //'Calendar':'mywidgets.widget.Calendar,mywidgets.widget.Timezones',
            'GoogleMap':'',
            'StaticMap':'',
            'Image':'',
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
        var ind = ind==null? -1:ind;
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
            } else if (ind < 0 || ind >= destination.childNodes.length) {
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

    _prepareZoomEnvelope:function(newobj,zoomToFit){
        var zoomEnvelope = document.createElement('div');
        zoomEnvelope.style.display = 'inline-block';
        newobj.appendChild(zoomEnvelope);
        setInterval(function(){
            zoomEnvelope.style.zoom = 1;
            var originalDomnode = zoomEnvelope.parentNode;
            var zoom_x = 1;
            var zoom_y = 1;
            var delta_x = 0;
            var delta_y = 0;
            if(zoomToFit===true || zoomToFit=='x'){
                delta_x = zoomEnvelope.clientWidth - originalDomnode.clientWidth;
            }
            if(zoomToFit===true || zoomToFit=='y'){
                delta_y = zoomEnvelope.clientHeight - originalDomnode.clientHeight;
            }
            if(delta_x>0){
                zoom_x = originalDomnode.clientWidth/ zoomEnvelope.clientWidth;
            }
            if(delta_y>0){
                zoom_x = originalDomnode.clientHeight/ zoomEnvelope.clientHeight;
            }
            zoomEnvelope.style.zoom =  Math.min(zoom_x,zoom_y);
        },50);
        return zoomEnvelope;
    },

    create:function(tag, destination, attributes, ind, sourceNode) {
        var attributes = attributes || {};
        var newobj, domnode,domtag;
        var handler = this.getHandler(tag,attributes,sourceNode);
        var zoomToFit = objectPop(attributes,'zoomToFit')

        genro.assert(handler,'missing handler for tag:'+tag);
        if (handler._beforeCreation) {
            var goOn = handler._beforeCreation(attributes,sourceNode);
            if (goOn === false) {
                return false;
            }
            domtag =objectPop(attributes,'domtag')
        }
        var domtag = domtag || handler._domtag || tag;
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
        if('visible' in attributes && !objectPop(attributes, 'visible')){
            attributes.visibility = 'hidden';
        }
        if('hidden' in attributes && objectPop(attributes, 'hidden')){
            attributes.display = 'none';
        }
        //var disabled=objectPop(attributes, 'disabled') ? true:false;
        //attributes.disabled=disabled;
        var kw = {'postCreation':handler._creating(attributes, sourceNode),
            'readonly' : objectPop(attributes, 'readonly'),
            // 'disabled' : disabled,
            '_style': objectAsStyle(genro.dom.getStyleDict(attributes, (this.noConvertStyle[domtag.toLowerCase()]))),
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
            if(zoomToFit){
                newobj = this._prepareZoomEnvelope(newobj,zoomToFit);
            }
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
                innerHTML = dataTemplate(sourceNode.getAttributeFromDatasource('template'), sourceNode, sourceNode.attr.datasource);
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
        objectPop(attributes,'format');
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
        var newobj = handler.createDojoWidget(wdgFactory,attributes,domnode,sourceNode);
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
                } else if (warnings && warnings.length>0) {
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
        modifiers = modifiers?modifiers.toLowerCase():modifiers;
        var result = false;
        var target = e.target;
        if (validclass){
            if(!target.className || (target.className && dojo.every(validclass.split(','), function(item) {return target.className.indexOf(item) < 0;}))){
                target = null;
            }
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


dojo.declare("gnr.RowEditor", null, {
    constructor:function(gridEditor,rowNode){
        this.gridEditor = gridEditor;
        this.grid = this.gridEditor.grid;
        rowNode.attr._pkey = rowNode.attr._pkey || rowNode.label;
        var row = this.grid.rowFromBagNode(rowNode);
        this.rowId = this.grid.rowIdentity(row);
        this._pkey = rowNode.attr._pkey;
        this.original_values = objectUpdate({},rowNode.attr);
        this.newrecord = rowNode.attr._newrecord;
        this.rowLabel = rowNode.label;
        this.gridEditor.rowEditors[this.rowId] = this;
        this.data = rowNode.getValue();
        if (this.data){
            return;
        }
        this.data = new gnr.GnrBag();
        var cellmap = this.grid.cellmap;
        var default_kwargs = objectUpdate({},this.gridEditor.editorPars.default_kwargs);
        for(var k in cellmap){
            objectPop(default_kwargs,k);
            var v = this.original_values[k];
            var nkw = {dtype:cellmap[k].dtype};
            if(this.newrecord){
                if(isNullOrBlank(v) && cellmap[k].validate_notnull){
                    nkw['_validationError'] = cellmap[k].validate_notnull_error || 'not null';
                }
            }else{
                nkw['_loadedValue'] = v;
            }
            this.data.setItem(k,v,nkw);
        }
        if(this.newrecord){
            for (var k in default_kwargs){
                this.data.setItem(k,this.original_values[k]);
            }
        }
        rowNode.setValue(this.data);
        
    },

    hasChanges:function(){
        var changed = false;
        this.data.forEach(function(n){
            if(n.attr._loadedValue!=n.getValue()){
                changed = true;
            }
        });
        return changed;
    },

    getChangeset:function(){
        var result = new gnr.GnrBag();
        var changed = false;
        this.data.forEach(function(n){
            if(n.attr._loadedValue!=n.getValue()){
                result.setItem(n.label,n.getValue(),n.attr);
            }
            changed = true;
        });
        return changed?result:null;
    },

    getErrors:function(){
        var errors = {};
        this.data.forEach(function(n){
            if(n.attr._validationError){
                errors[n.label] = n.attr._validationError;
            }
        });
        if(objectNotEmpty(errors)){
            return errors;
        }
        return null;
    },
    endEditCell:function(editingInfo){
        this.gridEditor.updateStatus();
        this.gridEditor.lastEditTs = new Date();
        this.currentCol = null;
        if(this.grid.pendingSort){
            this.grid.refreshSort();
        }
    },
    startEditCell:function(colname){
        this.currentCol = colname;
        this.gridEditor.lastEditTs = null;
        this.gridEditor.updateStatus();
    },
    deleteRowEditor:function(){
        objectPop(this.gridEditor.rowEditors,this.rowId);
        var rowIndex = this.grid.indexByRowAttr('_pkey',this.rowId);
        //genro.assert(rowIndex>=0,'not found '+this.rowId);
        if(rowIndex>=0){
            this.grid.updateRow(rowIndex);
        }
        if(this.data.getParentNode()){
            this.data.getParentNode().clearValue(); //deleting data because dbevents remove changes
        }
    },
    checkRowEditor:function(){
        var toDelete = true;
        var rowIndex = this.grid.indexByRowAttr('_pkey',this.rowId);

        this.data.forEach(function(n){
            if(n.attr._loadedValue!=n.getValue()){
                toDelete = false;
            }
        });
        if(toDelete){
            this.deleteRowEditor();
        }else{
            this.grid.updateRow(rowIndex);
        }
    }
});

dojo.declare("gnr.GridEditor", null, {
    constructor:function(grid) {
        this.grid = grid;
        var sourceNode = grid.sourceNode;
        this.viewId = sourceNode.attr.nodeId;
        this.table= sourceNode.attr.table;
        this.editorPars = sourceNode.attr.gridEditor;
        this.autoSave = this.editorPars? this.editorPars.autoSave:false;
        if(this.autoSave===true){
            this.autoSave = 3000;
        }
        if(sourceNode.attr.remoteRowController){
            var that = this;
            this.remoteRowController = function(rowIndex, cellname,kw){
                kw = kw || {};
                objectUpdate(kw,{field:cellname,row:new gnr.GnrBag(grid.rowByIndex(rowIndex))});
                genro.serverCall(sourceNode.attr.remoteRowController,kw,function(result){
                    result = result || {};
                    if(objectNotEmpty(result)){
                        that.updateRow(grid.dataNodeByIndex(rowIndex),result);
                    }
                });
            }
        }
        this.formId = sourceNode.getInheritedAttributes()['formId'];
        this.rowEditors = {};
        this.deletedRows = new gnr.GnrBag()
        this._status_list = ['error','changed'];
        this.grid.rows.isOver = function(inRowIndex) {
            return ((this.overRow == inRowIndex) && !grid.gnrediting);
        };
        this.grid.selection.isSelected = function(inRowIndex) {
            return this.selected[inRowIndex] && !grid.gnrediting;
        };
        
        this.columns = {};
        var sourceNodeContent = sourceNode.getValue();
        var gridEditorNode = sourceNodeContent.getNodeByAttr('tag', 'grideditor',true);
        var that = this;

        if(gridEditorNode){
            var gridEditorColumns = gridEditorNode.getValue();
            var attr;
            gridEditorColumns.forEach(function(node) {
                attr = objectUpdate({},node.attr);
                genro.assert(attr.gridcell,"Missing gridcell parameter");
                that.addEditColumn(attr.gridcell,attr);
            });
            gridEditorNode.setValue(null,false);
            gridEditorNode.attr.tag=null;
        }
        this.widgetRootNode = sourceNodeContent.getNode('_grideditor_',null,true);
        if(this.editorPars){
            if (sourceNode.form && sourceNode.attr.parentForm!==false){
                sourceNode.form.registerGridEditor(sourceNode.attr.nodeId,this);
            }
            sourceNode.subscribe('onNewDatastore',function(){
                that.resetEditor();
            });
            sourceNode.subscribe('saveChangedRows',function(){
                that.saveChangedRows();
            });
            if(this.autoSave){
                var autoSave = this.autoSave;
                this.widgetRootNode.watch('autoSave',function(){
                    if (that.grid.sourceNode.form && that.grid.sourceNode.form.isNewRecord()){
                        return false;
                    }
                    if(that.lastEditTs){
                        if((new Date()-that.lastEditTs)>autoSave){
                            that.lastEditTs = null;
                            that.saveChangedRows();
                        }
                    }
                    return false;
                },function(){
                   
                },500);
            }
        }
        this.widgetRootNode.attr.datapath = sourceNode.absDatapath(sourceNode.attr.storepath);
        var editOn = this.widgetRootNode.attr.editOn || 'onCellDblClick';
        editOn = stringSplit(editOn, ',', 2);
        var modifier = editOn[1];
        var _this = this;
        dojo.connect(grid, editOn[0], function(e) {
            if (genro.wdg.filterEvent(e, modifier)) {
                if (_this.enabled() && _this.editableCell(e.cellIndex) && !grid.gnrediting) {
                    _this.startEdit(e.rowIndex, e.cellIndex,e.dispatch);
                }
            }
        });
    },
    onFormatCell:function(cell, inRowIndex,renderedRow){
        if (this.invalidCell(cell, inRowIndex)) {
            cell.customClasses.push('invalidCell');
        }
        if(renderedRow._newrecord){
            cell.customClasses.push('newRowCell');
        }
    },
    resetEditor:function(){
        this.rowEditors = {};
        this.deletedRows = new gnr.GnrBag();
        this.updateStatus();
    },
    updateStatus:function(){
        var status = this.deletedRows.len()>0?'changed':null;
        for(var k in this.rowEditors){
            if(this.rowEditors[k].getErrors()){
                status = 'error';
                break;
            }
            if(!status && this.rowEditors[k].hasChanges()){
                status = 'changed';
            }
        }
        this.status = status;
        var viewNode = genro.getFrameNode(this.grid.sourceNode.attr.frameCode);
        dojo.forEach(this._status_list,function(st){
            genro.dom.setClass(viewNode,'editGrid_'+st,st==status);
        });
        this.grid.sourceNode.setRelativeData('.editor.status',status);
        if(this.grid.sourceNode.form){
            this.grid.sourceNode.form.updateStatus();
        }
    },
    addEditColumn:function(colname,colattr){
        colattr['parentForm'] = false;
        var edit = objectPop(colattr,'edit');
        objectPop(colattr,'width');
        if(edit!==true){
            colattr = objectUpdate(colattr,edit);
        }
        if(!('tag' in colattr)){
            var dt = colattr['dtype'];
            var widgets = {'L':'NumberTextBox','I':'NumberTextBox','D':'DateTextbox','R':'NumberTextBox','N':'NumberTextBox','H':'TimeTextBox','B':'CheckBox'};
            colattr['tag'] = widgets[dt] || 'Textbox';
            if('related_table' in colattr){
                colattr['tag'] = 'dbselect';
                colattr['dbtable'] = colattr['related_table'];
                if(colattr['related_table_lookup']){
                    colattr['hasDownArrow'] = true;
                }
            }if('values' in colattr){
                colattr['tag'] = colattr.values.indexOf(':')>=0?'filteringselect':'combobox';
            }
        }
        if(colattr.remoteRowController){
            var remoteRowControllerPars = colattr.remoteRowController;
            var remoteRowControllerCall = 'this.remoteRowController()';
            if(remoteRowControllerPars!=true){
                var variables = [];
                for (var k in remoteRowControllerPars){
                    colattr['validate_'+k] = remoteRowControllerPars[k];
                    variables.push(quoted(k)+':validations.'+k);
                }
                remoteRowControllerCall = 'this.remoteRowController({'+variables.join(',')+'})';
            }
            colattr.validate_onAccept = colattr.validate_onAccept? colattr.validate_onAccept + '; '+remoteRowControllerCall:remoteRowControllerCall;
        }
        var lowertag = colattr['tag'].toLowerCase();
        if(this['tag_'+lowertag]){
            this['tag_'+lowertag].call(this,colname,colattr);
        }
        this.columns[colname.replace(/\W/g, '_')] = {'tag':colattr.tag,'attr':colattr};
    },
    tag_simpletextarea:function(colname,colattr){
        colattr['z_index']= 1;
        colattr['position'] = 'fixed';
        colattr['height'] = colattr['height'] || '100px';
    },
    tag_checkbox:function(colname,colattr){
        colattr['margin'] = 'auto';
    },

    tag_dbselect:function(colname,colattr){
        if(!this.editorPars){
            return;
        }
        var cellmap = this.grid.cellmap;
        var related_setter = {};
        var grid = this.grid;
        colattr['dbtable'] = colattr['dbtable'] || colattr['related_table'];
        //colattr['selected_'+colattr['caption_field']] = '.'+colattr['caption_field'];
        var hiddencol = colattr['hiddenColumns']? colattr['hiddenColumns'].split(','):[];
        for(var k in cellmap){
            if(cellmap[k].relating_column == colname){
                hiddencol.push(cellmap[k].related_column);
                related_setter[cellmap[k].related_column.replace(/\W/g, '_')] = cellmap[k].field_getter;
            }
        }
        colattr['hiddenColumns'] = hiddencol.join(',');
        colattr.selectedSetter = function(path,value){
            if(path.indexOf('.')>=0){
                path = path.split('.');
                path = path[path.length-1];
            }
            this.setCellValue(path,value);
        }
        colattr.selectedCb = function(item){
            if(!item){
                return;
            }
            
            var selectRow = objectUpdate({},item.attr);
            var rowNode = this.getRelativeData().getParentNode();
            var values = {}; 
            for (var k in related_setter){
                values[related_setter[k]] = selectRow[k];
            }
            grid.collectionStore().updateRow(this.editedRowIndex,values)

            //rowNode.updAttributes(newAttr,{editedRowIndex:this.editedRowIndex});
            //setTimeout(function(){
            //rowNode.updAttributes(newAttr,{editedRowIndex:this.editedRowIndex});
            //},1)
        }
    },
    delEditColumn:function(colname){
        objectPop(this.columns,colname.replace(/\W/g, '_'));
    },
    enabled:function(){
        var gridSourceNode = this.grid.sourceNode;
        var form = gridSourceNode.form;
        var gridstore = this.grid.collectionStore?this.grid.collectionStore():null;
        if(gridstore){
            return !gridstore.locked;
        }
        if(form && form.store){
            return !form.isDisabled();
        }else{
            return 'editorEnabled' in gridSourceNode.attr? this.grid.editorEnabled:true;
        }
    },
    onEditCell:function(start,rowIdx) {
        var grid = this.grid;
        grid.gnrediting = start;
        grid.currentEditedRow =  start?rowIdx:null;
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
    onSavedChangedRows:function(changeset,result){
        var that = this;
        var updated = changeset.getItem('updated');
        var inserted = changeset.getItem('inserted');
        if(updated){
            updated.forEach(function(n){
                if(that.rowEditors && that.rowEditors[n.label]){
                    that.rowEditors[n.label].deleteRowEditor();
                }
            });
        }
        if(inserted){
            inserted.forEach(function(n){
                if(that.rowEditors && that.rowEditors[n.label]){
                    that.rowEditors[n.label].deleteRowEditor();
                }
            });
        }
        
        var insertedRows = result.getItem('insertedRecords');
        if(insertedRows){
            insertedRows.forEach(function(n){
                var r = that.grid.storebag().getNode(n.label);
                r.attr._pkey = n.getValue();
                r._value = null;
                r.label = n.label;
                delete r.attr._newrecord;
            });
        }
        this.resetEditor();
        this.grid.sourceNode.publish('savedRows');
        this.updateStatus();         
    },
    saveChangedRows:function(){
        var that = this;
        var changeset = this.getChangeset(true);
        var sourceNode = this.grid.sourceNode;
        if(changeset.len()>0){
            that.grid.updateRowCount();
            genro.serverCall(that.editorPars.saveMethod,{table:that.table,changeset:changeset,_sourceNode:sourceNode},
                            function(result){that.onSavedChangedRows(changeset,result);});
        }
    },

    getChangeset:function(sendingStatus){
        var changeset = new gnr.GnrBag();
        var collectionStore = this.grid.collectionStore();

        for(var k in this.rowEditors){
            var rowEditor = this.rowEditors[k];
            if(rowEditor.hasChanges() && !rowEditor.getErrors() && !rowEditor.currentCol){
                var prefix = rowEditor.newrecord?'inserted.':'updated.';
                changeset.setItem(prefix+rowEditor.rowId,rowEditor.getChangeset(),{_pkey:rowEditor.newrecord?null:rowEditor._pkey});
                rowEditor.sendingStatus = sendingStatus;
            }
        }
        var deletedRows = new gnr.GnrBag();
        this.deletedRows.forEach(function(n){
            deletedRows.setItem(n.attr._pkey,null,{_pkey:n.attr._pkey});
        });
        if(deletedRows.len()>0){
            var unlinkfield = collectionStore.unlinkdict?collectionStore.unlinkdict.field:null;
            changeset.setItem('deleted',deletedRows,{unlinkfield:unlinkfield});
        }
        //this.deletedRows = new gnr.GnrBag();
        return changeset;
    },

    deleteSelectedRows:function(pkeys,protectPkeys){
        //var selectedIdx = this.grid.selection.getSelected()
        if(pkeys=='*'){
            pkeys = this.grid.getAllPkeys();
        }
        var existingPkeys = [];
        var that = this;
        var storebag = this.grid.storebag();
        dojo.forEach(pkeys,function(n){
            if(that.rowEditors[n] && that.rowEditors[n].newrecord){
                var rowLabel = that.rowEditors[n].rowLabel;
                that.rowEditors[n].deleteRowEditor();
                storebag.popNode(rowLabel);
            }else{
                existingPkeys.push(n);
            }
        });
        if(existingPkeys.length>0){
            if(this.autoSave){
                var that = this;
                this.grid.collectionStore().deleteAsk(existingPkeys,protectPkeys,function(){that.markDeleted(pkeys)});
            }else{
                this.markDeleted(existingPkeys);
            }
        }
    },
    
    markDeleted:function(pkeys){
        var that = this;
        var grid = this.grid;
        var storebag = this.grid.storebag();
        dojo.forEach(pkeys,function(pkey){
            var node = grid.rowBagNodeByIdentifier(pkey);
            node = storebag.popNode(node.label);
            if(grid.sourceNode.attr.table){
                //is an inlinetablehandler
                that.deletedRows.setItem(node.label,node);
            }
            if(that.rowEditors[pkey]){
                that.rowEditors[pkey].deleteRowEditor();
            }
        });
        if(this.autoSave && pkeys&&pkeys.length>0){
            this.lastEditTs = new Date();
        }
        this.grid.updateCounterColumn();
        this.updateStatus();
    },
    getNewRowDefaults:function(externalDefaults){
        if(!this.editorPars){
            return externalDefaults;
        }
        else{
            var default_kwargs = objectUpdate({},(this.editorPars.default_kwargs || {}));
            if(externalDefaults){
                default_kwargs = objectUpdate(default_kwargs,externalDefaults);
            }
            var result =  this.widgetRootNode.evaluateOnNode(default_kwargs);
            var cellmap = this.grid.cellmap;
            var queries = new gnr.GnrBag();
            var rcol,hcols;
            for(var k in cellmap){
                var cmap = cellmap[k];
                if(cmap.related_table){
                    rcol = cmap.relating_column;
                    if(result[rcol]){
                        hcols = [];
                        for(var j in cellmap){
                            if(cellmap[j].relating_column==rcol && !(cellmap[j].field_getter in result)){
                                hcols.push(cellmap[j].related_column);
                            }
                        }
                        if(hcols.length>0){
                            queries.setItem(rcol,null,{table:cmap.related_table,columns:hcols.join(','),pkey:result[rcol],where:'$pkey =:pkey'});
                        }
                    }
                }
            }
            if(queries.len()>0){
                var sourceNode = this.grid.sourceNode;
                var remoteDefaults = genro.serverCall('app.getMultiFetch',{'queries':queries,_sourceNode:sourceNode},null,null,'POST');
                for(var k in cellmap){
                    rcol = cellmap[k].relating_column;
                    if (rcol){
                        result[cellmap[k].field_getter] = remoteDefaults.getItem(rcol+'.#0?'+cellmap[k].related_column.replace(/\W/g, '_'));
                    }
                }
            }
            result['_newrecord'] = true;
            return result;
        }
    },
    startEditRemote:function(n,colname,rowIndex){
        var rowData = n.getValue();
        var rowId = this.grid.rowIdByIndex(rowIndex);
        if(!rowId && n.attr._newrecord){
            rowId = n.attr._pkey = n.label;

        }
        var rowEditor = this.rowEditors[rowId];
        if(!rowEditor){
            rowEditor = this.newRowEditor(n);
            if(rowEditor.newrecord){
                this.grid.updateRow(rowIndex);
            }
        }
        if(rowEditor.sendingStatus){
            return;
        }
        var rowData = rowEditor.data;
        if(rowData.index(colname)<0){
            rowData.setItem(colname,n.attr[colname],{_loadedValue:n.attr[colname]});
        }

        rowEditor.startEditCell(colname);
        return rowId;
    },
    newRowEditor:function(rowNode){
        return new gnr.RowEditor(this,rowNode);
    },
    
    addNewRows:function(rows){
        var that = this;
        dojo.forEach(rows,function(n){
            that.addNewRows_one(n);
        });
        this.updateStatus();
    },
    addNewRows_one:function(row){
        var grid = this.grid;
        var newnode = grid.addBagRow('#id', '*', grid.newBagRow(row));
        this.newRowEditor(newnode);
    },
    updateRow:function(rowNode, updkw){
        if (updkw instanceof gnr.GnrBag){
            updkw = updkw.asDict();
        }
        var row = this.grid.rowFromBagNode(rowNode);
        var rowEditor = this.rowEditors[this.grid.rowIdentity(row)];
        if (!rowEditor){
            rowEditor = this.newRowEditor(rowNode);
        }
        for(var k in updkw){
            if(k in this.grid.cellmap){
                var rowData = rowEditor.data;
                if(rowData.index(k)<0){
                    rowData.setItem(k,row[k],{_loadedValue:row[k]});
                }
                rowData.setItem(k,updkw[k]);
            }
        }
        this.lastEditTs = new Date();
        this.updateStatus();
    },

    setCellValue:function(rowIdx,cellname,value,valueCaption){
        var grid = this.grid;
        var rowNode = grid.dataNodeByIndex(rowIdx);
        var row = grid.rowFromBagNode(rowNode);
        var rowEditor = this.rowEditors[grid.rowIdentity(row)];
        if (!rowEditor){
            rowEditor = this.newRowEditor(rowNode);
        }
        var cellmap = this.grid.cellmap;
        genro.assert(cellname in cellmap,'cell '+cellname,+' does not exist');
        var cell = cellmap[cellname];
        if(cell.edit || cell.counter){
            rowEditor.data.setItem(cellname,value);
            this.updateStatus();
            this.lastEditTs = new Date();
        }
        var newAttr = {};
        newAttr[cellname] = value;
        var rtable = cell.related_table;
        if(!valueCaption && cell.field!=cell.field_getter && rtable){
            var queries = new gnr.GnrBag();
            var hcols = [cell.related_column];
            var selectedKw = objectExtract(cell.edit,'selected_*',true);
            if(objectNotEmpty(selectedKw)){
                hcols = hcols.concat(objectKeys(selectedKw));
            }
            queries.setItem(cellname,null,{table:rtable,columns:hcols.join(','),pkey:value,where:'$pkey =:pkey'});
            var r = genro.serverCall('app.getMultiFetch',{'queries':queries},null,null,'POST');
            var rnode = r.getNode('#0.#0');
            var kw = rnode?rnode.attr:{};
            valueCaption = objectPop(kw,cell.related_column);
            for(var selected in selectedKw){
                var p = selectedKw[selected].split('.');
                p = p[p.length-1];
                this.setCellValue(rowIdx,p,kw[selected]);
            }
        }
        newAttr[cell.field_getter] = valueCaption || value;
        this.grid.collectionStore().updateRow(rowIdx,newAttr);
    },

    updateCounterColumn:function(rowNode,k,counterField){
        var row = this.grid.rowFromBagNode(rowNode);
        if(row[counterField]!=k){
            this.setCellValue(k-1,counterField,k);
        }
    },
    startEdit:function(row, col,dispatch) {
        var grid = this.grid;
        var cell = grid.getCell(col);
        var colname = cell.field;
        var fldDict = this.columns[colname];
        var gridcell = fldDict.attr.gridcell || colname;
        var rowDataNode = grid.dataNodeByIndex(row);
        if(rowDataNode && rowDataNode.attr._is_readonly_row){
            return;
        }
        var datachanged = false;
        var editedRowId=null;
        if (rowDataNode && rowDataNode._resolver && rowDataNode._resolver.expired()) {
            datachanged = true;
        }
        if(this.editorPars){
          editedRowId= this.startEditRemote(rowDataNode,colname,row);
          if(!editedRowId){
            return;
          }
          this.widgetRootNode.form = null;
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
        if(!cellNode){
            grid.scrollToRow(row);
            cellNode = cell.getNode(row);
        }

        var attr = objectUpdate({}, fldDict.attr);
        attr.datapath = '.' + rowLabel;
        attr.width = attr.width || (cellNode.clientWidth-10)+'px';
        if(attr.tag.toLowerCase()=='checkbox'){
            attr.margin_left = ( (cellNode.clientWidth-10-16)/2)+'px';
            attr.margin_top ='1px';
        }
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
            'row':row,'col':col,'editedRowId':editedRowId};
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
            gridEditor._exitCellTimeout = setTimeout(dojo.hitch(gridEditor, 'endEdit', this.widget, deltaDict[cellNext], editingInfo), 300);
        };
        attr._parentDomNode = cellNode;
        attr._class = attr._class ? attr._class + ' widgetInCell' : 'widgetInCell';
        attr.connect_keydown = cbKeys;
        attr.connect_onBlur = cbBlur;
        attr._autoselect = true;
        var wdgtag = fldDict.tag;
        if (!wdgtag || attr.autoWdg) {
            var dt = convertToText(cellDataNode.getValue())[0];
            wdgtag = {'L':'NumberTextBox','I':'NumberTextBox','D':'DateTextbox','R':'NumberTextBox','N':'NumberTextBox','H':'TimeTextBox'}[dt] || 'Textbox';
        }
        if('disabled' in attr){
            var disabled = objectPop(attr,'disabled');
            if(typeof(disabled)=='string'){
                if(disabled.indexOf('==')==0){
                    //method
                    disabled = funcApply('return '+disabled.slice(2),{rowLabel:rowLabel},this.widgetRootNode);
                }else{
                    var disabledpath = disabled.slice(1);
                    if(disabledpath[0]=='.'){
                        disabledpath = '.' + rowLabel + disabledpath;
                    } 
                    disabled = this.widgetRootNode.getRelativeData(disabledpath);
                }
            }
            if(disabled){
                var rc = this.findNextEditableCell({row:row, col:col}, {'r': 0, 'c': 1});
                if (rc && dispatch!='dodblclick') {
                    this.startEdit(rc.row, rc.col);
                }
                return;
            }
        }
        var editWidgetNode = this.widgetRootNode._(wdgtag,'cellWidget', attr).getParentNode();
        editWidgetNode.setCellValue = function(cellname,value,valueCaption){
            gridEditor.setCellValue(this.editedRowIndex,cellname,value,valueCaption);
        };
        editWidgetNode.remoteRowController = function(kw){
            gridEditor.remoteRowController(this.editedRowIndex,gridcell,kw)
        }
        editWidgetNode.editedRowIndex = row;
        this.onEditCell(true,row);
        if (cellDataNode.attr._validationError || cellDataNode.attr._validationWarnings) {
            editWidgetNode._validations = {'error':cellDataNode.attr._validationError,'warnings':cellDataNode.attr._validationWarnings};
            editWidgetNode.updateValidationStatus();
        }
        editWidgetNode.widget.focus();
        editWidgetNode.grid = gridEditor.grid;

    },

    endEdit:function(editWidget, delta, editingInfo) {
        var cellNode = editingInfo.cellNode;
        var contentText = editingInfo.contentText;
        var removedNode = editWidget.sourceNode._destroy();
        editingInfo.cellNode.innerHTML = contentText;
        this.onEditCell(false);
        if(editingInfo.editedRowId){
            if(this.rowEditors[editingInfo.editedRowId]){
                this.rowEditors[editingInfo.editedRowId].endEditCell(editingInfo);
                this.grid.currRenderedRowIndex = null;
                this.grid.updateRow(editingInfo.row);
            }
        }
        if(this._exitCellTimeout){
            this._exitCellTimeout = null;
        }
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
    onExternalChange:function(pkey){
        if(pkey in this.rowEditors){
            this.rowEditors[pkey].checkRowEditor();
        }
        this.updateStatus();
    },
    
    statusColGetter:function(rowdata,idx){
        var statusClass = 'rowEditorStatus_noedit';
        var rowId = this.grid.rowIdentity(rowdata);
        var rowEditor = this.rowEditors[rowId];
        if(rowEditor){
            if(rowEditor.sendingStatus){
                statusClass = 'waiting16';
            }else if(rowEditor.getErrors()){
                statusClass = 'redLight';
            }else if(rowEditor.hasChanges()){
                statusClass = 'yellowLight';
            }
        }
        return '<div class="'+statusClass+'"></div>'
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

dojo.declare("gnr.GridChangeManager", null, {
    constructor:function(grid){
        this.grid = grid;
        this.formulaColumns = {};
        this.totalizeColumns = {};

        this.triggeredColumns = {};
        this.cellpars = {};
        this.sourceNode = grid.sourceNode;
        var that = this;
        this.sourceNode.subscribe('onNewDatastore',function(){
                that.data = that.grid.storebag();
                that.data.subscribe('rowLogger',{'upd':dojo.hitch(that, "triggerUPD"),
                                                   'ins':dojo.hitch(that, "triggerINS"),
                                                   'del':dojo.hitch(that, "triggerDEL")});
                that.resolveCalculatedColumns();
                that.resolveTotalizeColumns();
                });
    },
    resolveCalculatedColumns:function(){
        var cellmap = this.grid.cellmap;
        for(var k in this.formulaColumns){
            if(cellmap[k].calculated){
                this.recalculateOneFormula(k);
            }
        }
    },


    resolveTotalizeColumns:function(){
        for(var k in this.totalizeColumns){
            this.updateTotalizer(k);
        }
    },
    updateTotalizer:function(k){
        this.sourceNode.setRelativeData(this.grid.cellmap[k].totalize,this.data.sum('#a.'+k));
    },
    recalculateOneFormula:function(key){
        var that = this;
        this.grid.storebag().forEach(function(n){
            that.calculateFormula(key,n);
        });
    },

    addFormulaColumn:function(field,kw){
        var cellmap = this.grid.cellmap;
        var formula = kw.formula;
        var re,par,dependencies;
        if(field in this.formulaColumns){
            this.delFormulaColumn(field);
        }
        for(var k in cellmap){
            par = cellmap[k].field;
            re= new RegExp('\\b'+par+'\\b');
            if(formula.match(re)){
                dependencies = this.triggeredColumns[par];
                if(!dependencies){
                    dependencies={}
                    this.triggeredColumns[par]=dependencies;
                }
                dependencies[field] = true;
            }
        }
        this.formulaColumns[field] = formula;
    },
    delFormulaColumn:function(field){
        for (var p in this.triggeredColumns){
            delete this.triggeredColumns[p][field];
        }
        delete this.formulaColumns[field];
    },
    addTotalizer:function(field,kw){
        this.totalizeColumns[field] = kw.totalize;
    },

    delTotalizer:function(field,kw){
        delete this.totalizeColumns[field];
    },
    calculateFormula:function(formulaKey,rowNode){
        var formula = this.formulaColumns[formulaKey];
        var result;
        var pars = this.grid.rowFromBagNode(rowNode);
        var cellmap = this.grid.cellmap;
        for (var cl in cellmap){
            pars[cl] = pars[cl];
        }
        var struct = this.grid.structBag.getItem('#0.#0');
        var bagcellattr = struct.getNode(cellmap[formulaKey]._nodelabel).attr;
        var dynPars = objectExtract(bagcellattr,'formula_*',true);        
       // for(var p in dynPars){
       //     if(dynPars[p][0] == '.'){
       //         dynPars[p] = rowNode.attr[p];
       //     }
       // }
        dynPars = this.sourceNode.evaluateOnNode(dynPars);
        objectUpdate(pars,dynPars);
        try{
            result = funcApply('return '+formula,pars,this.sourceNode);
        }catch(e){
            result = null;
        }
        var values = {};
        values[formulaKey] = result;
        this.grid.collectionStore().updateRowNode(rowNode,values);
        //rowNode.setAttribute(formulaKey,result,true);
    },
    resetCellpars:function(){
        this.sourceNode.unregisterSubscription('cellpars');
        this.cellpars = {};
    },
    registerParameters:function(){
        if(objectNotEmpty(this.cellpars)){
            this.sourceNode.registerSubscription('_trigger_data',this,this.onDataChange,'cellpars');
        }
    },
    
    onDataChange:function(kw){
        var dpath = kw.pathlist.slice(1).join('.');
        var struct = this.grid.structBag.getItem('#0.#0');
        var cellmap = this.grid.cellmap;
        var rebuildStructure = false;
        for(var p in this.cellpars){
            var abspath = this.sourceNode.absDatapath(p);
            if(dpath==abspath){
                for(var f in this.cellpars[p]){
                    var reasons = this.cellpars[p][f];
                    for(var reason in reasons){
                        if(reason.indexOf('formula_')==0){
                            if(f in this.formulaColumns){
                                this.recalculateOneFormula(f);
                            }
                        }else if(reason.indexOf('condition_')==0){
                            console.log('condition');
                        }else{
                            rebuildStructure = true;
                        }
                    }
                }
            }
        }
        if(rebuildStructure){
            this.grid.setStructpath();
        }
    }, 
    addDynamicCellPar:function(cell,parname,parpath){
        var dependences = this.cellpars[parpath];
        if(!dependences){
            dependences = {};
            this.cellpars[parpath] = dependences;
        }
        dependences[cell.field] = dependences[cell.field] || {};
        dependences[cell.field][parname] = true;
    },
    triggerUPD:function(kw){
        var changedPars = {};
        var k;
        var rowNode;
        if(kw.updvalue && this.grid.datamode =='bag'){
            var l = kw.node.label;
            if(l in this.triggeredColumns){
                changedPars[l] = true;
            }
            rowNode = kw.node.getParentBag().getParentNode();
            if(l in this.totalizeColumns){
                this.updateTotalizer(l);
            }
        }

        else if(kw.updattr){
            rowNode = kw.node;
            var newattr = kw.node.attr;
            var oldattr = kw.oldattr;
            for (k in newattr){
                if( (k in this.triggeredColumns) && (newattr[k]!=oldattr[k]) ){
                    changedPars[k] = true;
                }
                if(k in this.totalizeColumns){
                    this.updateTotalizer(k);
                }
            }
        }
        if(objectNotEmpty(changedPars)){
            var toRecalculate = {};
            for (k in changedPars){
                for (var f in this.triggeredColumns[k]){
                    toRecalculate[f] = true;
                }
            }
            for (k in toRecalculate){
                this.calculateFormula(k,rowNode);
            }
        }
    },
    triggerINS:function(kw){
        this.resolveTotalizeColumns();
        this.resolveCalculatedColumns();
    },
    triggerDEL:function(kw){
        this.resolveTotalizeColumns();
    }
});

