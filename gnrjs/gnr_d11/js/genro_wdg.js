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
            'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'ul', 'var','embed','audio','video','canvas','progress'];
        for (var i = 0; i < htmlspace.length; i++) {
            tag = htmlspace[i];
            this.namespace[tag.toLowerCase()] = ['html',tag];
        }
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
            'dygraph':'',
            'protovis':'',
            'codemirror':'',
            'LightButton':''
        };
        this.updateWidgetCatalog();
    },
    updateWidgetCatalog:function(){
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

    create:function(tag, destination, attributes, ind, sourceNode) {
        attributes = attributes || {};
        var newobj, domnode,domtag;
        var handler = this.getHandler(tag);
        genro.assert(handler,'missing handler for tag:'+tag);
        if (handler._beforeCreation) {
            var goOn = handler._beforeCreation(attributes,sourceNode);
            if (goOn === false) {
                return false;
            }
            console.warn('should never happen _beforeCreation not returning false');
            domtag =objectPop(attributes,'domtag');
        }
        var onCreating = objectPop(attributes,'onCreating');
        if (onCreating) {
            funcCreate(onCreating).call(sourceNode, attributes,handler);
        }
        var zoomToFit = objectPop(attributes,'zoomToFit')
        domtag = domtag || handler._domtag || tag;
        if (ind == 'replace') {
            domnode = destination;
        } else if (domtag == '*') {
            domnode = null;
        } else {
            var _attachTo = attributes._attachTo || handler._attachTo;
            destination = _attachTo ? dojo.byId(_attachTo) : destination;
            domnode = this.makeDomNode(domtag, destination, ind);

        }
        if (typeof(ind) == 'object') {
            ind = -1; // should be index of domnode in destination ???
        }
        var tip = objectPop(attributes, 'tip');
        if('visible' in attributes && !objectPop(attributes, 'visible')){
            attributes.visibility = 'hidden';
        }
        var currentHidden;
        if('hidden' in attributes){
            currentHidden = objectPop(attributes, 'hidden');
            if(currentHidden){
                attributes.display = 'none';
            }

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
                newobj = genro.dom.autoScaleWrapper(newobj,zoomToFit);
            }
            this.linkSourceNode(newobj, sourceNode, kw);
            newobj.gnr = handler;

        }
        else {//This is dojo widget
            newobj = this.createDojoWidget(tag, domnode, attributes, kw, sourceNode);
            /*
            GENERIC SETTER MANAGER IT COULD BE A NEW WAY TO HANDLE SETTING OF DYNAMIC ATTRIBUTES
            if(sourceNode){
                for (var kattr in sourceNode.attr){
                    var vattr = sourceNode.attr[kattr];
                    var setterName = 'set'+stringCapitalize(kattr);
                    if(kattr!='value' && typeof(vattr)=='string' && sourceNode.isPointerPath(vattr) && newobj[setterName]){
                        console.log('setter for kattr',kattr,sourceNode.attr.tag)
                    }
                }
            }
            */
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
            if(newobj.setHidden && currentHidden){
                genro.src.onBuiltCall(function(){
                    newobj.setHidden(currentHidden);
                });
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
        if ((innerHTML==undefined) && sourceNode) {
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
            var vattr = attributes[oneattr];
            if((vattr===null || vattr===undefined) && oneattr=='value'){
                vattr = '';
            }
            domnode.setAttribute(oneattr, vattr);
        }
        if (innerHTML!=undefined) {
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
        var dojoAttributes = objectExtract(handler, 'dojo_*',true);
        
        var validations = objectExtract(attributes, 'validate_*');
        var extracted = objectExtract(attributes, '_*', {'_type':null, '_identifier':null}); // strip all attributes used only for triggering rebuild or as input for ==function
        objectUpdate(attributes, attrmixins);
        objectUpdate(attributes,dojoAttributes);
        var newobj = handler.createDojoWidget(wdgFactory,attributes,domnode,sourceNode);
        if (kw.readonly) {
            var field = dojo.byId(newobj.id);
            field.readOnly = true;
            field.style.cursor = 'default';
            dojo.connect(field, 'onfocus', function () {
                field.blur();
            });
        }
        if (objectNotEmpty(validations) || handler._validatingWidget) {
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
    setIsValidMethod:function(obj) {
        if (obj.isValid) {
            obj.isValid = function(isFocused) {
                if (isFocused) {
                    this.sourceNode.editing = true;
                    return true;
                } else {
                    if (this.sourceNode.editing) { //loosing focus after editing
                        this.sourceNode.editing = false;
                        if (this.gnr._validatingWidget) {
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
            var moddict = {'shiftKey':'shift','ctrlKey':'ctrl','altKey':'alt','metaKey':'meta'};
            for(var c in moddict){
                if(e[c]){
                    if(modif.indexOf(moddict[c])<0){
                        return false;
                    }
                    modif = modif.replace(moddict[c], '');
                }
            }
            modif = modif.replace(/,/g, '').replace(/ /g, '');
            if (modif == '') {
                result = true;
            }
        }
        return result;
    }
});


dojo.declare("gnr.RowEditor", null, {
    constructor:function(gridEditor,rowNode){
        this.gridEditor = gridEditor;
        this.grid = this.gridEditor.grid;
        rowNode.attr._pkey = rowNode.attr._pkey || rowNode.label;
        var row = this.grid.rowFromBagNode(rowNode,true);
        this.rowId = this.grid.rowIdentity(row);
        this._pkey = rowNode.attr._pkey;
        this.original_values = objectUpdate({},row);
        this.newrecord = rowNode.attr._newrecord;
        this.rowLabel = rowNode.label;
        rowNode._rowEditor = this;
        this.grid.currRenderedRowIndex = this.grid.storebag().index(this.rowLabel);
        var data = rowNode.getValue();
        if(data){
            data.clearBackRef();
            this.inititializeData(data);
            data.setBackRef(rowNode,rowNode._parentbag);
        }else{
            this.inititializeData();
            rowNode.setValue(this.data);
        }
    },

    replaceData:function(newdata,reason){
        var rowNode = this.data.getParentNode();
        rowNode.setValue(newdata,reason);
        this.data = newdata;
    },

    inititializeData:function(data){
        data = data || new gnr.GnrBag();
        this.data = data;
        var cellmap = this.grid.cellmap;
        default_kwargs = objectUpdate({},this.gridEditor.editorPars.default_kwargs);
        var k;
        for(k in cellmap){
            objectPop(default_kwargs,k);
            var kw = {dtype:cellmap[k].dtype};
            var wdg_dtype = data.getAttr(k,'wdg_dtype') ;
            if(!kw.dtype && wdg_dtype){
                kw.dtype = wdg_dtype;
                kw.wdg_dtype = wdg_dtype;
            }
            data.setItem(k,this.original_values[k],kw);
        }
        if(this.newrecord){
            for (k in default_kwargs){
                data.setItem(k,this.original_values[k]);
            }
            this.checkNotNull();
        }
    },

    checkNotNull:function(){
        var cellmap = this.grid.cellmap;
        var data = this.data;
        var n,err,v;
        this.grid.currRenderedRowIndex = this.grid.storebag().index(this.rowLabel);
        for(var k in cellmap){
            var cell = cellmap[k];
            var editpars = cell.edit;
            if(this.grid.sourceNode.currentFromDatasource(cell.editDisabled)){
                continue;
            }
            if(editpars && editpars!==true){
                editpars = this.grid.sourceNode.evaluateOnNode(editpars);
                if('validate_notnull' in editpars){
                    n = data.getNode(k);
                    if(editpars.validate_notnull){
                        err = editpars.validate_notnull_error || 'not null';
                        v = n.getValue();
                        if(isNullOrBlank(v)){
                            n.attr._validationError = err;
                        }else if(n.attr._validationError==err){
                            delete n.attr._validationError;
                        }
                    }else{
                        delete n.attr._validationError;
                    }
                }
            }
        }
    },


    hasChanges:function(){
        var changed = false;
        if(this.newrecord){
            return true
        }
        if(this.data.getNodeByAttr('_loadedValue')){
            changed = true;
        }
        return changed;
    },

    getChangeset:function(){
        if(this.hasChanges()){
            return this.data.deepCopy()
        }
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
        this.grid.currRenderedRowIndex = this.grid.storebag().index(this.rowLabel);
        this.checkNotNull();
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
        var rowIndex = this.grid.indexByRowAttr('_pkey',this.rowId);
        //genro.assert(rowIndex>=0,'not found '+this.rowId);
        if(rowIndex>=0){
            this.grid.updateRow(rowIndex);
        }
        var rowNode = this.data.getParentNode();
        if(this.grid.datamode!='bag' && rowNode){
            rowNode.clearValue(); //deleting data because dbevents remove changes
            delete rowNode._rowEditor;
        }
    },

    checkRowEditor:function(){
        var rowIndex = this.grid.indexByRowAttr('_pkey',this.rowId);
       //if(!this.hasChanges()){
       //    this.deleteRowEditor();
       //}else{
       //
       //}
        if(rowIndex>=0){
            this.grid.updateRow(rowIndex);
        }
    }
});

dojo.declare("gnr.GridEditor", null, {
    constructor:function(grid) {
        this.grid = grid;
        var that = this;
        var sourceNode = grid.sourceNode;
        sourceNode.subscribe('duplicateCommand',function(e){
            if(that.enabled()){
                grid.addRows(null,e,true);
            }
        });
        this.viewId = sourceNode.attr.nodeId;
        this.table= sourceNode.attr.table;
        this.editorPars = objectUpdate({},sourceNode.attr.gridEditorPars);
        this.autoSave =this.editorPars.autoSave || false;
        if(this.autoSave===true){
            this.autoSave = 3000;
        }
        this.remoteRowController = sourceNode.attr.remoteRowController;
        this.remoteRowController_default = sourceNode.attr.remoteRowController_default;
        if(this.remoteRowController_default){
            var caller_kw = {'script':"this.getParentNode().widget.gridEditor.callRemoteControllerBatch('*')",'_delay':500,
                            '_userChanges':true};
            objectUpdate(caller_kw,this.remoteRowController_default);
            sourceNode._('dataController','remoteRowController_default_caller',caller_kw);
        }
        
        this.status = {};
        this.columns = {};
        this.formId = sourceNode.getInheritedAttributes()['formId'];
        this.deletedRows = new gnr.GnrBag()
        this._status_list = ['error','changed'];
        this.grid.rows.isOver = function(inRowIndex) {
            return ((this.overRow == inRowIndex) && !grid.gnrediting);
        };
        this.grid.selection.isSelected = function(inRowIndex) {
            return this.selected[inRowIndex] && !grid.gnrediting;
        };
        var sourceNodeContent = sourceNode.getValue();
        var gridEditorNode = sourceNodeContent.getNodeByAttr('tag', 'grideditor',true);
        this.widgetRootNode = sourceNodeContent.getNode('_grideditor_',null,true);
        if(gridEditorNode){
            console.warn('legacy mode: use new grid and edit attribute in cell instead of this way')
            var gridEditorColumns = gridEditorNode.getValue();
            var attr;
            gridEditorColumns.forEach(function(node) {
                attr = objectUpdate({},node.attr);
                genro.assert(attr.gridcell,"Missing gridcell parameter");
                that.addEditColumn(attr.gridcell,attr);
            });
            gridEditorNode.setValue(null,false);
            gridEditorNode.attr.tag=null;
        }else{
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
                            if(that.grid.sourceNode.form && that.grid.sourceNode.form.opStatus){
                                return;
                            }
                            that.saveChangedRows();
                        }
                    }
                    return false;
                },function(){},500);
            }
        }
        this.applyStorepath();
        //this.widgetRootNode.attr.datapath = sourceNode.absDatapath(sourceNode.attr.storepath);
        var _this = this;
        if(genro.isMobile){
            sourceNode.subscribe('doubletap',function(info){
                var e = info.event;
                if (_this.enabled() && _this.editableCell(e.cellIndex,e.rowIndex,true) && !grid.gnrediting) {
                    _this.startEdit(e.rowIndex, e.cellIndex,e.dispatch);
                }
            })
        }else{
            var editOn = this.widgetRootNode.attr.editOn || 'onCellDblClick';
            editOn = stringSplit(editOn, ',', 2);
            var modifier = editOn[1];
            dojo.connect(grid, editOn[0], function(e) {
                if (genro.wdg.filterEvent(e, modifier)) {
                    if (_this.enabled() && _this.editableCell(e.cellIndex,e.rowIndex,true) && !grid.gnrediting) {
                        e.stopPropagation();
                        e.preventDefault();
                        _this.startEdit(e.rowIndex, e.cellIndex,e.dispatch);
                    }
                }
            });
        }
    },

    applyStorepath:function(){
        var sourceNode = this.grid.sourceNode;
        var absStorepath = sourceNode.absDatapath(sourceNode.attr.storepath)
        if (sourceNode.form && sourceNode.attr.parentForm!==false){
            this.storeInForm = sourceNode.attr.storeInForm || absStorepath.indexOf(sourceNode.form.sourceNode.absDatapath(sourceNode.form.formDatapath))==0
        }
        this.widgetRootNode.attr.datapath = absStorepath;
    },
    batchAssign:function(){
        var fields = [];
        var editable_cols = this.columns;
        this.grid.getColumnInfo().keys().forEach(function(f){
            var c = editable_cols[f];
            if(!c){return;}
            if(c.attr.batch_assign){
                var wdgkw = objectUpdate({lbl:c.attr.original_name,value:'^.'+c.attr.field},c.attr);
                objectExtract(wdgkw,'selectedSetter,selectedCb')
                fields.push(wdgkw);
            }
        });
        var grid = this.grid;

        var promptkw = {widget:fields,
            action:function(result){
                grid.getSelectedRowidx().forEach(function(idx){
                    result.forEach(function(node){
                        grid.gridEditor.setCellValue(idx,node.label,node.getValue());
                    });
                });
            }
        };
        genro.dlg.prompt(_T('Multi assigment'),promptkw);
    },

    onFormatCell:function(cell, inRowIndex,renderedRow){
        if (this.invalidCell(cell, inRowIndex)) {
            cell.customClasses.push('invalidCell');
        }
        if(renderedRow._newrecord && this.grid.sourceNode.attr.table && this.grid.sourceNode.form && this.grid.sourceNode.form.store && !this.grid.sourceNode.form.store.autoSave){
            cell.customClasses.push('newRowCell');
        }
    },

    resetEditor:function(){
        this.deletedRows = new gnr.GnrBag();
        this.updateStatus(true);
    },

    updateStatus:function(reset){
        var status;
        if(!reset){
            status = this.deletedRows.len()>0?'changed':null;
            var store = this.grid.collectionStore();
            if(store.hasErrors()){
                status = 'error';
            }else if(store.hasChanges()){
                status = 'changed';
            }
        }
        this.status[this.grid.sourceNode.attr.storepath] = status;
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
            var widgets = {'L':'NumberTextBox','I':'NumberTextBox','D':'DateTextbox','DH':'DatetimeTextbox','R':'NumberTextBox','N':'NumberTextBox','H':'TimeTextBox','B':'CheckBox'};
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
        var lowertag = colattr['tag'].toLowerCase();
        var wdghandler = genro.wdg.getHandler(colattr['tag']);
        wdghandler.cell_onCreating(this,colname,colattr);
        this.columns[colname.replace(/\W/g, '_')] = {'tag':colattr.tag,'attr':colattr};
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
    onEditCell:function(start,rowIdx,cellIdx) {
        var grid = this.grid;
        grid.gnrediting = start;
        genro.dom.setClass(grid.sourceNode,'editingGrid',start);
        grid.sourceNode.publish('onEditCell',{editing:start,rowIdx:rowIdx,cellIdx:cellIdx});
        grid.updateRowStyles(rowIdx)
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
        var grid = this.grid;
        var updated = changeset.getItem('updated');
        var inserted = changeset.getItem('inserted');
        if(updated){
            updated.forEach(function(n){
                var rowId = n.attr.rowId;
                var rowEditor = grid.getRowEditor({rowId:rowId});
                if(rowEditor){
                    rowEditor.deleteRowEditor();
                }
            });
        }
        if(inserted){
            inserted.forEach(function(n){
                var rowId = n.attr.rowId;
                var rowEditor = grid.getRowEditor({rowId:rowId});
                if(rowEditor){
                    rowEditor.deleteRowEditor();
                }
            });
        }

        var insertedRows = result.getItem('insertedRecords');
        if(insertedRows){
            insertedRows.forEach(function(n){
                var r = that.grid.storebag().getNode(n.attr.rowId);
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
        if(collectionStore.pendingLoading){
            return changeset;
        }
        collectionStore.getData().forEach(function(n){
            var rowEditor = n._rowEditor;
            if(rowEditor && rowEditor.hasChanges()){
                var cannotSave = this.autoSave && (rowEditor.getErrors() || rowEditor.currentCol);
                if (!cannotSave){
                        var prefix = rowEditor.newrecord?'inserted.':'updated.';
                        changeset.setItem(prefix+'#id',rowEditor.getChangeset(),{_pkey:rowEditor.newrecord?null:rowEditor._pkey,rowId:rowEditor.rowId});
                        rowEditor.sendingStatus = sendingStatus;
                }
            }

        });
        var deletedRows = new gnr.GnrBag();
        this.deletedRows.forEach(function(n){
            deletedRows.setItem('#id',null,{_pkey:n.attr._pkey});
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
        var grid = this.grid;
        var storebag = this.grid.storebag();
        dojo.forEach(pkeys,function(n){
            var rowEditor = grid.getRowEditor({rowId:n});
            if(rowEditor && rowEditor.newrecord){
                var rowLabel = rowEditor.rowLabel;
                rowEditor.deleteRowEditor();
                storebag.popNode(rowLabel);
            }else if(!isNullOrBlank(n)){
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
            that.deletedRows.setItem(node.label,node);
            var rowEditor = node._rowEditor;
            if(rowEditor){
                rowEditor.deleteRowEditor();
            }
        });
        if(this.autoSave && pkeys&&pkeys.length>0){
            this.lastEditTs = new Date();
        }
        this.grid.updateCounterColumn();
        if(this.storeInForm){
            var n = storebag.getParentNode().attributeOwnerNode('dtype','X');
            if(n){n.attr._sendback = true;}

        }
        this.updateStatus();
    },

    getNewRowDefaults:function(externalDefaults){
        var editorDefaults = this.editorPars.default_kwargs;
        if(typeof(editorDefaults)=='function'){
            editorDefaults = editorDefaults.call();
        }
        var default_kwargs = objectUpdate({},(editorDefaults || {}));
        if(externalDefaults){
            default_kwargs = objectUpdate(default_kwargs,externalDefaults);
        }
        var result =  this.widgetRootNode.evaluateOnNode(default_kwargs);
        var cellmap = this.grid.cellmap;
        var queries = new gnr.GnrBag();
        var rcol,hcols;
        for(var k in cellmap){
            var cmap = cellmap[k];
            if(cmap.related_table){ //if should be on rcol instead of cmap.related_table #fporcari
                rcol = cmap.relating_column;
                if(result[rcol]){
                    hcols = [];
                    for(var j in cellmap){
                        if(cellmap[j].relating_column==rcol && result[cellmap[j].field_getter]===undefined){
                            hcols.push(cellmap[j].related_column);
                        }
                    }
                    if(hcols.length>0){
                        //queries.setItem(rcol,null,{table:cmap.related_table,columns:hcols.join(','),pkey:result[rcol],where:'$pkey =:pkey'}); OLDVERSION

                        //FIX: it should be the related_table of relating_column instead of cmap related table which is the last related table in relation path
                        // @product_id.@product_type_id.description ---> relating_column:product_id, related_table:product_type -- related_table of relating column: foo.product
                        queries.setItem(rcol,null,{table:cellmap[rcol].related_table,columns:hcols.join(','),pkey:result[rcol],where:'$pkey =:pkey'});

                    }
                }
            }
        }
        if(queries.len()>0){
            var sourceNode = this.grid.sourceNode;
            var remoteDefaults = genro.serverCall('app.getMultiFetch',{'queries':queries,_sourceNode:sourceNode},null,null,'POST');
            var node,keyAttr;
            for(var k in cellmap){
                rcol = cellmap[k].relating_column;
                if (rcol){
                    node = remoteDefaults.getNode(rcol+'.#0');
                    keyAttr = cellmap[k].related_column.replace(/\W/g, '_');
                    if(node && keyAttr in node.attr){
                        result[cellmap[k].field_getter] = node.attr[keyAttr];
                    }
                }
            }
        }
        return result;
    },

    startEditRemote:function(n,colname,rowIndex){
        var rowData = n.getValue();
        var rowId = this.grid.rowIdByIndex(rowIndex);
        if(!rowId && n.attr._newrecord){
            rowId = n.attr._pkey = n.label;

        }
        var rowEditor = this.grid.getRowEditor({rowId:rowId});
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
        var rowEditor = new gnr.RowEditor(this,rowNode);
        return rowEditor;
    },

    addNewRows:function(rows){
        var that = this;
        dojo.forEach(rows,function(n){
            that.addNewRows_one(n);
        });
        this.updateStatus();
        this.grid.collectionStore().sort();
        this.grid.updateRowCount();
        this.lastEditTs = new Date()
    },
    addNewRows_one:function(row){
        var grid = this.grid;
        var label = '#id';
        if(grid.rowIdentity(row)){
            label = flattenString(grid.rowIdentity(row),['.',' '])
        }
        var newnode = grid.addBagRow(label, '*', grid.newBagRow(row));
        this.newRowEditor(newnode);
    },

    updateRowFromRemote:function(rowId,value){
        var rowEditor = this.grid.getRowEditor({rowId:rowId});
        if(!rowEditor){
            rowEditor = this.newRowEditor(this.grid.rowBagNodeByIdentifier(rowId));
        }
        if(this.grid.datamode=='bag'){
            rowEditor.replaceData(value,'remoteController');
        }else{
            var row_attributes = value.pop('_row_attributes');
            if(row_attributes){
                rowEditor.data.getParentNode().updAttributes(row_attributes,false);
            }
            rowEditor.data.update(value,null,'remoteController');
        }
        rowEditor.checkNotNull();
        rowEditor.checkRowEditor();
    },

    callRemoteControllerBatch:function(rows,kw){
        var that = this;
        kw = kw || objectUpdate({},this.remoteRowController_default);
        if(rows=='*'){
            rows = this.grid.storebag().deepCopy();
        }
        var result = genro.serverCall('remoteRowControllerBatch',
                                    objectUpdate(kw,{handlerName:this.remoteRowController,
                                    rows:rows,_sourceNode:this.grid.sourceNode})
                                    );
        var grid = this.grid;
        result.forEach(function(n){
            that.updateRowFromRemote(grid.rowIdentity(grid.rowFromBagNode(n)) || n.label,n.getValue());
        },'static');
        this.updateStatus();
        this.grid.sourceNode.publish('remoteRowControllerDone',{result:result})
        return result
    },

    callRemoteController:function(rowNode,field,oldvalue,batchmode){
        var rowId = this.grid.rowIdentity(this.grid.rowFromBagNode(rowNode)) || rowNode.label;
        var field_kw = field? this.grid.cellmap[field]['edit']['remoteRowController']:{};
        var kw = objectUpdate({},this.remoteRowController_default);
        objectUpdate(kw,field_kw)
        if(batchmode){
            this._pendingRemoteController = this._pendingRemoteController || [];
            this._pendingRemoteController.push(rowId);
            genro.callAfter(function(){
                var rows = new gnr.GnrBag();
                var store = this.grid.storebag();
                this._pendingRemoteController.forEach(function(l){
                    var n = store.getNode(l);
                    if(n){
                        rows.setItem(n.label,n.getValue(),objectUpdate({},n.attr));
                    }
                });
                var result = this.callRemoteControllerBatch(rows,kw);
                this._pendingRemoteController = null;
                this.grid.sourceNode.publish('remoteRowControllerDone',{result:result});
            },1,this,'callRemoteControllerBatch_'+this.grid.sourceNode._id);
            return;
        }
        var that = this;
        var row = rowNode.getValue().deepCopy();
        objectUpdate(kw,{field:field,row:row,row_attr:objectUpdate({},rowNode.attr)});
        kw['_sourceNode'] = this.grid.sourceNode;
        var result = genro.serverCall(this.remoteRowController,kw);
        this.updateRowFromRemote(rowId,result);
        this.updateStatus()
        var editingWidgetNode = this.widgetRootNode._value?this.widgetRootNode._value.getNode('cellWidget'):null;
        if(editingWidgetNode){
            var widget = editingWidgetNode.widget || editingWidgetNode.externalWidget;
            if(widget._focused){
                widget.cellNext = 'RIGHT';
                widget.focusNode.blur();
            }else if(widget.focusManager && widget.focusManager.hasFocus){
                widget.cellNext = 'RIGHT';
                widget.focusManager.blur();
            }
        }
        this.grid.sourceNode.publish('remoteRowControllerDone',{result:result})
    },

    updateRow:function(rowNode, updkw){
        var row = this.grid.rowFromBagNode(rowNode,true);
        var rowEditor = this.grid.getRowEditor({row:row});
        if (!rowEditor){
            rowEditor = this.newRowEditor(rowNode);
        }
        for(var k in updkw){
            if(k in this.grid.cellmap){
                var rowData = rowEditor.data;
                var m = this.grid.cellmap[k];
                if(rowData.index(k)<0){
                    rowData.setItem(k,row[k],{_loadedValue:row[k]});
                }
                rowData.setItem(k,updkw[k]);
            }
        }
        this.lastEditTs = new Date();
        this.updateStatus();
    },

    copyFromCellAbove:function(sourceNode){
        if(sourceNode.editedRowIndex>0){
            sourceNode.widget.setValue(this.getCellValue(sourceNode.editedRowIndex-1,sourceNode.attr.field),true);
        }
    },

    getCellValue:function(rowIdx,cellname){
        return this.grid.rowByIndex(rowIdx,true)[cellname];
    },


    setCellValue:function(rowIdxOrNode,cellname,value,valueCaption){
        var grid = this.grid;
        var rowNode = typeof(rowIdxOrNode)=='number'? grid.dataNodeByIndex(rowIdxOrNode): rowIdxOrNode;
        var row = grid.rowFromBagNode(rowNode,true);
        var rowEditor = this.grid.getRowEditor({row:row});
        if (!rowEditor){
            rowEditor = this.newRowEditor(rowNode);
        }
        var cellmap = this.grid.cellmap;
        genro.assert(cellname in cellmap,'cell '+cellname,+' does not exist');
        var cell = cellmap[cellname];
        if(cell.edit || cell.counter || cell.isCheckBoxCell){
            var n = rowEditor.data.setItem(cellname,value);
            delete n.attr._validationError //trust the programmatical value
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
                this.setCellValue(rowNode,p,kw[selected]);
            }
        }if(valueCaption!=undefined) {
            newAttr[cell.field_getter] = valueCaption
        }
        this.grid.collectionStore().updateRowNode(rowNode,newAttr);
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
        editedRowId= this.startEditRemote(rowDataNode,colname,row);
        if(!editedRowId){
            return;
        }
        this.widgetRootNode.form = null;
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
        objectExtract(attr,'editDisabled,editLazy,hidden');
        var lastRenderedRowIndex = grid.currRenderedRowIndex;
        grid.currRenderedRowIndex = row;
        attr = grid.sourceNode.evaluateOnNode(attr,function(path){return path.indexOf('#ROW')>=0});
        var remote = fldDict.attr.remote;
        if('fields' in attr || 'contentCb' in attr || remote){
            var fields = attr.fields;
            if(typeof(fields)=='string'){
                fields = funcApply(fields,{rowDataNode:rowDataNode,grid:grid},this);
            }
            if(attr.mode=='dialog' || remote){
                var currdata;
                if (attr.rowEdit == true){
                    currdata = rowData.deepCopy();
                }else{
                    currdata = rowDataNode.getValue().getItem(attr.field);
                }
                var that = this;
                var promptkw = {widget:attr.contentCb || attr.fields,
                    dflt:currdata?currdata.deepCopy():null,
                    mandatory:attr.validate_notnull,
                    action:function(result){
                          if(attr.rowTemplate){
                              rowData.update(result);
                          }else{
                              that.setCellValue(row,attr.field,result);
                          }
                    }
                };
                if(remote){
                    var remotekw = objectExtract(fldDict.attr,'remote_*',true,true)
                    remotekw.remote = remote;
                    objectUpdate(promptkw,remotekw);
                }
                var dlgkw = objectExtract(fldDict.attr,'dlg_*',true,true);
                objectUpdate(promptkw,dlgkw);
                genro.dlg.prompt(attr.original_name || attr.field,promptkw, grid.sourceNode);
            }else{
                var rowpath = this.widgetRootNode.absDatapath('.' + rowLabel);
                genro.dlg.quickTooltipPane({datapath:rowpath,fields:attr.fields,domNode:cellNode,modal:attr.modal},
                                            funcCreate(attr.contentCb,'pane,kw',grid.sourceNode),
                                            {rowDataNode:rowDataNode,grid:grid,cell:cell});
            }
            return
        }
        if(attr.editOnOpening && funcApply(attr.editOnOpening,{rowIndex:row,field:attr.field,rowData:rowData,cellNode:cellNode},this)===false){
            return;
        }
        grid.currRenderedRowIndex = lastRenderedRowIndex;
        grid.selection.select(grid.currRenderedRowIndex);
        attr.datapath = this.widgetRootNode.absDatapath('.' + rowLabel);
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
            var widget = this.widget || this.externalWidget;
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
                if(widget.focusManager){
                    widget.focusManager.blur();
                }else{
                    widget.focusNode.blur();
                }
                //widget._onBlur();
                //setTimeout(dojo.hitch(this.focusNode, 'blur'), 1);
            }
        };
        var gridEditor = this;
        var cbBlur = function(e) {
            var widget = this.widget || this.externalWidget;
            var deltaDict = {'UP': {'r': -1, 'c': 0},
                    'DOWN': {'r': 1, 'c': 0},
                    'LEFT': {'r': 0, 'c': -1},
                    'RIGHT': {'r': 0, 'c': 1},
                    'STAY':{'r': 0, 'c': 0}
                };
            var cellNext = widget.cellNext; //|| 'RIGHT'; dannoso
            widget.cellNext = null;
            //START Safari checkbox in cell bugfix
            if(dojo.isSafari && widget && widget.focusNode && widget.focusNode.type=='checkbox'){
                if(genro._lastMouseEvent.mousedown.target===widget.focusNode){
                    widget.focus();
                    return;
                }
            }
            //END Safari checkbox in cell bugfix

            setTimeout(function(){
                gridEditor.endEdit(widget,deltaDict[cellNext],editingInfo);
            },1);

        };
        attr._parentDomNode = cellNode;
        attr._class = attr._class ? attr._class + ' widgetInCell' : 'widgetInCell';
        attr.connect_keydown = cbKeys;
        attr.connect_onBlur = cbBlur;
        attr._autoselect = true;
        attr._inGridEditor = true;
        var wdgtag = fldDict.tag;

        if (cellDataNode.attr.wdg_dtype || !wdgtag && attr.autoWdg) {
            var dt = cellDataNode.attr.wdg_dtype || convertToText(cellDataNode.getValue())[0];
            wdgtag = {'L':'NumberTextBox','I':'NumberTextBox','D':'DateTextbox','R':'NumberTextBox','N':'NumberTextBox','H':'TimeTextBox','B':'CheckBox'}[dt] || 'Textbox';
            attr.tag = wdgtag;
        }
        this.onEditCell(true,row,col);
        var editWidgetNode = this.widgetRootNode._(wdgtag,'cellWidget', attr).getParentNode();
        editWidgetNode.setCellValue = function(cellname,value,valueCaption){
            gridEditor.setCellValue(this.editedRowIndex,cellname,value,valueCaption);
        };
        editWidgetNode.editedRowIndex = row;
        if (cellDataNode.attr._validationError || cellDataNode.attr._validationWarnings) {
            editWidgetNode._validations = {'error':cellDataNode.attr._validationError,'warnings':cellDataNode.attr._validationWarnings};
            editWidgetNode.updateValidationStatus();
        }
        if(editWidgetNode.widget && editWidgetNode.widget.focus){
            editWidgetNode.widget.focus();
        }
        editWidgetNode.grid = gridEditor.grid;

    },

    endEdit:function(blurredWidget, delta, editingInfo) {
        var cellNode = editingInfo.cellNode;
        var contentText = editingInfo.contentText;
        var editWidgetNode = this.widgetRootNode._value.getNode('cellWidget');
        var that = this;
        editWidgetNode.watch('waiting_rpc',function(){
            return !(editWidgetNode._waiting_rpc || editWidgetNode._exitValidation);
        },function(){
            var h = editWidgetNode.widget || editWidgetNode.gnrwdg || editWidgetNode.domNode;
            h.gnr.cell_onDestroying(editWidgetNode,that,editingInfo);
            editWidgetNode._destroy();
            editingInfo.cellNode.innerHTML = contentText;
            that.onEditCell(false,editingInfo.row,editingInfo.col);
            if(editingInfo.editedRowId){
                var rowEditor = that.grid.getRowEditor({rowId:editingInfo.editedRowId});
                if(rowEditor){
                    rowEditor.endEditCell(editingInfo);
                    that.grid.currRenderedRowIndex = null;
                    that.grid.updateRow(editingInfo.row);
                }
            }
            if (delta) {
                var rc = that.findNextEditableCell({row:editingInfo.row, col:editingInfo.col}, delta);
                if (rc) {
                    that.startEdit(rc.row, rc.col);
                }
            }
        });
    },

    editableCell:function(col,row,clicked) {
        var cell = this.grid.getCell(col);
        if (!(cell.field in this.columns)){return false;}
        if ((cell.classes || '').indexOf('hiddenColumn')>=0){return false}
        this.grid.currRenderedRowIndex = row;
        var rowdict = this.grid.rowByIndex(row);
        if(rowdict._is_readonly_row){
            return false;
        }
        if(this.grid.sourceNode.currentFromDatasource(cell.editDisabled)){
            return false;
        }else if(clicked){
            return true;
        }else if(this.grid.sourceNode.currentFromDatasource(cell.editLazy)){
            var editpars = cell.edit==true?{}:this.grid.sourceNode.evaluateOnNode(cell.edit);
            return (editpars.validate_notnull && this.grid.rowByIndex(row)[cell.field]===null);
        }else{
            return true;
        }

    },

    onExternalChange:function(pkey){
        var rowEditor = this.grid.getRowEditor({rowId:pkey});
        if(rowEditor){
            rowEditor.checkRowEditor();
        }
        this.updateStatus();
    },

    statusColGetter:function(rowdata,idx){
        var statusClass = 'rowEditorStatus_noedit';
        var rowId = this.grid.rowIdentity(rowdata);
        var rowEditor = this.grid.getRowEditor({rowId:rowId});
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
        } while (!this.editableCell(col,row));
        rc.col = col;
        rc.row = row;
        return rc;
    }

});

dojo.declare("gnr.GridFilterManager", null, {
    constructor:function(grid){
        this.grid = grid;
    },
    filterset:function(){
        return this.grid.sourceNode.getRelativeData('.filterset');
    },
    isInFilterSet:function(row){
        var gridNode = this.grid.sourceNode;
        var cb_attr,cb;
        return this.activeFilters().some(function(kw){
            cb_attr = gridNode.evaluateOnNode(kw.cb_attr);
           
            objectUpdate(cb_attr,row);
            for (var k in gridNode.widget.cellmap){
                cb_attr[k] = cb_attr[k] || null;
            }
            return funcApply("return "+kw.cb,cb_attr,gridNode);
        });
    },

    activeFilters:function(){
        var result = [];
        var fn;
        this.filterset().forEach(function(n){
            var data = n.getValue().getItem('data');
            var current = n.getValue().getItem('current');
            if(!(current && data  && data.len())){
                return;
            }
            current.split(',').forEach(function(f){
                fn = data.getNode(f);
                if(!fn){
                    console.error('missing filter',n.label+'.'+f)
                }
                if(fn.attr.cb){
                    result.push({cb:fn.attr.cb,cb_attr:objectExtract(fn.attr,'cb_*',true)})
                }
            });
        });
        return result;
    },

    hasActiveFilter:function(){
        return this.activeFilters().length>0;
    }
});


dojo.declare("gnr.GridChangeManager", null, {
    constructor:function(grid){
        this.grid = grid;
        this.sourceNode = grid.sourceNode;
        this.initialize();
        var that = this;
        this.sourceNode.subscribe('onNewDatastore',function(){
            that.grid.storebag().subscribe('rowLogger',{'upd':dojo.hitch(that, "triggerUPD"),
                                               'ins':dojo.hitch(that, "triggerINS"),
                                               'del':dojo.hitch(that, "triggerDEL")});
            that.resolveCalculatedColumns();
            that.resolveTotalizeColumns();
            });
        this.sourceNode.subscribe('onSetStructpath',function(){
            this.delayedCall(function(){
                if(that.grid.storebag()){
                    that.resolveCalculatedColumns();
                    that.resolveTotalizeColumns();
                }
            },1,'resolveCalculatedColumns')
        });
    },

    initialize:function(){
        this.formulaColumns = {};
        this.totalizeColumns = {};
        this.triggeredColumns = {};
        this.remoteControllerColumns = {};
        this.sourceNode.unregisterSubscription('cellpars');
        this.cellpars = {};
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

    calculateFilteredTotals:function(){
        var filteredStore;
        var selectedIdx =this.grid.getSelectedRowidx();
        if(selectedIdx.length>1){
            filteredStore = new gnr.GnrBag();
            this.grid.getSelectedNodes().forEach(function(n){
                filteredStore.setItem(n.label,n._value,n.attr);
            });
        }else if(this.grid.isFiltered()){
            filteredStore = this.grid.storebag(true);
        }else{
            this.sourceNode.setRelativeData('.filtered_totalize',null);
            return
        }
        var filtered_totalize = new gnr.GnrBag();
        for(let k in this.totalizeColumns){
            //this.updateTotalizer(k);
            var totvalue = filteredStore.sum(this.grid.datamode=='bag'?k:'#a.'+k);
            filtered_totalize.setItem(k,totvalue);
        }
        this.sourceNode.setRelativeData('.filtered_totalize',filtered_totalize);
    },

    updateTotalizer:function(k){
        var storebag = this.grid.storebag();
        var storeattr = storebag.getParentNode().attr;
        var _serverTotalizeColumns = this.grid.sourceNode._serverTotalizeColumns || {};
        if((k in _serverTotalizeColumns) && !isNullOrBlank(storeattr['sum_'+k])){
            //already set from server values
            return;
        }
        var totvalue = this.grid.storebag().sum(this.grid.datamode=='bag'?k:'#a.'+k);
        totvalue = Math.round10(totvalue);
        this.sourceNode.setRelativeData(this.grid.cellmap[k].totalize,totvalue);
        this.sourceNode.publish('onUpdateTotalize',{'column':k,'value':totvalue});
    },

    recalculateOneFormula:function(key){
        var that = this;
        var isBagMode = this.grid.datamode=='bag';
        this.grid.storebag().walk(function(n){
            if('pageIdx' in n.attr){return;}
            that.calculateFormula(key,n);
        },'static',null,isBagMode);
    },

    addRemoteControllerColumn:function(field,kw){
        this.remoteControllerColumns[field] = true;
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
        var pars = this.grid.rowFromBagNode(rowNode,true);

        if(formula.startsWith("+=") || formula.startsWith("%=")){
            var masterField = formula.slice(2).trim();
            var store = this.grid.collectionStore();
            if(!masterField){
                return;
            }
            if(formula.startsWith("+=")){
                let idx = store.getIdxFromPkey(pars._pkey);
                let prev_row_value = idx<=0? 0 : Math.round10((store.rowByIndex(idx-1)[formulaKey] || 0));
                formula = prev_row_value+' + '+masterField;
            }else if(formula.startsWith("%=")){
                let masterTotal = store.sum(masterField);
                if(masterTotal instanceof dojo.Deferred){
                    //console.log('wait')
                }else{
                    formula = 'Math.round10('+masterField+'/'+masterTotal+' * 100)';
                }
            }
        }
        var cellmap = this.grid.cellmap;
        pars._currcell = cellmap[formulaKey];
        pars._rowNode = rowNode;
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
        var values = {};
        if(formula=='#'){
            result = rowNode.attr.rowidx || this.grid.currRenderedRowIndex;
        }else{
            try{
                result = funcApply('return '+formula,pars,this.sourceNode);
            }catch(e){
                result = null;
            }
        }
        values[formulaKey] = result;
        this.grid.collectionStore().updateRowNode(rowNode,values);
        //rowNode.setAttribute(formulaKey,result,true);
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
            var trigger_reason = this.sourceNode.getTriggerReason(this.sourceNode.absDatapath(p),kw);
            if(trigger_reason && trigger_reason!='child'){
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
            var grid = this.grid;
            this.sourceNode.delayedCall(function(){
                grid.setStructpath();
            },1);
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
        var idx;
        var sourceNode = this.sourceNode;
        var that = this;
        if(kw.updvalue && kw.value instanceof gnr.GnrBag ){
            var storeNode = this.grid.storebag().getParentNode();
            var parent_lv = kw.node.parentshipLevel(storeNode);
            if(parent_lv<2){
                if(kw.reason=='remoteController'){
                    sourceNode.delayedCall(function(){
                        that.resolveCalculatedColumns();
                        that.resolveTotalizeColumns();
                    },1,'resolveCalculatedColumns')
                }
                return;
            }
        }
        if(kw.updvalue && this.grid.datamode =='bag'){
            var l = kw.node.label;
            if(l in this.triggeredColumns){
                changedPars[l] = true;
            }
            rowNode = kw.node.getParentBag().getParentNode();
            if(l in this.totalizeColumns){
                this.updateTotalizer(l);
            }
        }else if(kw.updattr){
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
        if(kw.updvalue){
            var gridEditor = this.grid.gridEditor;
            var cell = this.grid.cellmap[kw.node.label];
            if(kw.value!=kw.oldvalue && gridEditor && ((kw.node.label in gridEditor.columns) || (cell && (cell.counter || cell.isCheckBoxCell)))){
                var attr = kw.node.attr;
                if(!('_loadedValue' in attr)){
                    if(kw.oldvalue instanceof gnr.GnrBag){
                        attr['_loadedValue'] = kw.oldvalue.deepCopy()
                    }else{
                        attr['_loadedValue'] = kw.oldvalue;
                    }
                }else if (attr._loadedValue == kw.value || ( isNullOrBlank(kw.value) && isNullOrBlank(attr._loadedValue) )) {//value = _loadedValue
                    delete attr._loadedValue;
                }
            }
            if(kw.reason!='remoteController' && kw.node.label in this.remoteControllerColumns){
                this.grid.sourceNode.delayedCall(function(){
                    gridEditor.callRemoteController(kw.node.getParentNode(),kw.node.label,kw.oldvalue);
                    that.resolveCalculatedColumns();
                    that.resolveTotalizeColumns();
                },1,'afterRemoteController')
            }
        }
    },
    triggerINS:function(kw){
        if(kw.reason=='remoteController'){
            return;
        }
        var storeNode = this.grid.storebag().getParentNode();
        var parent_lv = kw.node.parentshipLevel(storeNode);
        var gridEditor = this.grid.gridEditor;
        if(gridEditor && parent_lv<2){
            var rowEditor = this.grid.getRowEditor({rowId:kw.node.label});
            if(!rowEditor){
                rowEditor = gridEditor.newRowEditor(kw.node);
                if(gridEditor.remoteRowController && rowEditor.data.getItem(this.grid.masterEditColumn())!==null ){
                    gridEditor.callRemoteController(kw.node,null,null,true);
                }
            }
        }
        this.resolveTotalizeColumns();
        this.resolveCalculatedColumns();
    },
    triggerDEL:function(kw){
        this.resolveTotalizeColumns();
        if(this.grid.gridEditor){
            this.grid.gridEditor.updateStatus();
        }
    }
});
