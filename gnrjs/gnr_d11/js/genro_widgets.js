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
        storeNode._currentColumns=result;
    }
    return result;
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
        var fld = node.attr.field;
        if(node.attr.template_columns){
            node.attr.template_columns.split(',').forEach(function(n){
                arrayPushNoDup(columns,(n[0]=='$' || n[0]=='@')?n:'$'+n);
            });
        }
        if (node.attr['calculated'] || (fld && fld.indexOf(':')>=0)) {
            continue;
        }
        if (fld) {
            if(node.attr.caption_field){
                arrayPushNoDup(columns,node.attr.caption_field);
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

gnr.menuFromBag = function (bag, appendTo, menuclass, basepath) {
    var menuline,attributes;
    var bagnodes = bag.getNodes();
    for (var i = 0; i < bagnodes.length; i++) {
        var bagnode = bagnodes[i];
        attributes = objectUpdate({}, bagnode.attr);
        var valuelabel = null;
        if(typeof(bagnode._value)=='string'){
            valuelabel = bagnode._value;
        }
        attributes.label = attributes.caption || attributes.label || valuelabel || bagnode.label;

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
    setValueInData:function(sourceNode,value,valueAttr){
       if (sourceNode.attr_kw){
           var attr_kw = sourceNode.evaluateOnNode(sourceNode.attr_kw);
           for (var k in attr_kw){
               valueAttr[k] = attr_kw[k];
           }
        }
        var path = sourceNode.attrDatapath('value');
        var valueAttr = valueAttr || {};
        value = this.onSettingValueInData(sourceNode,value,valueAttr);
        if (sourceNode.attr.mask || sourceNode.attr.format) {
            var valueToFormat = (typeof(value)=='string' && '_displayedValue' in valueAttr)? valueAttr['_displayedValue'] : value;
            var formattedValue = genro.formatter.asText(valueToFormat, sourceNode.currentAttributes());
            this.setFormattedValue(sourceNode,formattedValue);
            valueAttr['_formattedValue'] = formattedValue;
        }
        if ('_valuelabel' in sourceNode.attr){
            valueAttr['_valuelabel'] = sourceNode.attr['_valuelabel'];
        }
        if(sourceNode.attr.rejectInvalid && !sourceNode.widget.isValid()){
            return;
        }
        genro._data.setItem(path, value, valueAttr, {'doTrigger':sourceNode,lazySet:true});
        sourceNode.publish('onSetValueInData',value);
    },
    onSettingValueInData: function(sourceNode, value,valueAttr) {
        return value;
    },
    setFormattedValue:function(sourceNode,formattedValue){
        return;
    },
    
    _doChangeInData:function(domnode, sourceNode, value, valueAttr) {
        this.setValueInData(sourceNode,value,valueAttr);
        this.doChangeInData(sourceNode, value, valueAttr)
    },
    doChangeInData:function(sourceNode, value, valueAttr){

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
        if ('speech' in attributes){
            objectPop(attributes,'speech');
            if(genro.isChrome){
                savedAttrs['speech'] = true;
            }
        }
        savedAttrs['touchEvents'] = objectPop(attributes,'touchEvents');

        objectExtract(attributes, 'onDrop,onDrag,dragTag,dropTag,dragTypes,dropTypes');
        objectExtract(attributes, 'onDrop_*');
        savedAttrs['dropTarget'] = objectPop(attributes, 'dropTarget');
        savedAttrs['dropTargetCb'] = objectPop(attributes, 'dropTargetCb');
        savedAttrs['dropTargetCb_extra'] = objectExtract(attributes,'dropTargetCb_*');
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
        if(sourceNode && sourceNode.attr.default_value && sourceNode.attr.dtype){
            sourceNode.attr.default_value = convertFromText(sourceNode.attr.default_value,sourceNode.attr.dtype);
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
            sourceNode.defineForm(formId, formDatapath, controllerPath, pkeyPath,objectExtract(sourceNode.attr,'form_*'));
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
        if(sourceNode){
            sourceNode.attr_kw = objectExtract(sourceNode.attr,'attr_*',true);
        }
        this.created(newobj, savedAttrs, sourceNode);
        if(this.formattedValueHandler){
            this.formattedValueHandler(newobj, savedAttrs, sourceNode);
        }
        if('speech' in savedAttrs){
            if(newobj.focusNode){
                newobj.focusNode.setAttribute("x-webkit-speech","x-webkit-speech");
                newobj.focusNode.onwebkitspeechchange = function(){
                    if('onSpeechEnd' in newobj){
                        if(typeof(newobj.onSpeechEnd)=='function'){
                            newobj.onSpeechEnd();
                        }else{
                            newobj.sourceNode.onNodeCall(newobj.onSpeechEnd);
                        }
                    }
                }
            }
        }

        var domNode = newobj.domNode || newobj;
       //if('touchEvents' in savedAttrs){
       //    genro.dom.connectTouchEvents(domNode,savedAttrs['touchEvents']);
       //}
        if (savedAttrs.connectedMenu) {
            var menu = savedAttrs.connectedMenu;
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
        
        if(savedAttrs.dropTargetCb_extra && objectNotEmpty(savedAttrs.dropTargetCb_extra)){
            sourceNode.dropTargetCbExtra = {};
            for(var key in savedAttrs.dropTargetCb_extra){
                sourceNode.dropTargetCbExtra[key] = funcCreate(savedAttrs.dropTargetCb_extra[key], 'dropInfo,data', sourceNode);
            }
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

        var draggable = sourceNode.getAttributeFromDatasource('draggable'); //|| 
        if (draggable && 'setDraggable' in newobj) {
            newobj.setDraggable(draggable);
        }
        var detachable = sourceNode.getAttributeFromDatasource('detachable');
        if(detachable){
            var domNode = newobj.domNode || newobj;
            dojo.connect(domNode,'onmousemove',function(e){
                if(e.shiftKey){
                    dojo.addClass(domNode,'detachable');
                }
            });
            dojo.connect(domNode,'onmouseout',function(e){
                dojo.removeClass(domNode,'detachable');
            });
            dojo.connect(domNode,'onmousedown',function(e){
                if(e.shiftKey){
                    dojo.addClass(domNode,'detachable');
                    domNode.draggable = true;
                }else{
                    domNode.draggable = false;
                }
            });
            dojo.connect(domNode,'onmouseup',function(e){
                domNode.draggable = false;
            });
            
        }


        var parentNode = sourceNode.getParentNode();
        if (parentNode.attr.tag) {
            var parentTagLower = parentNode.attr.tag.toLowerCase()
            if (parentTagLower== 'tabcontainer') {
                objectFuncReplace(newobj, 'setTitle', function(title) {
                    if (title) {
                        if (this.controlButton) {
                            this.controlButton.setLabel(title);
                        }
                    }
                });
            }
            else if (parentTagLower == 'accordioncontainer') {
                objectFuncReplace(newobj, 'setTitle', function(title) {
                    this.titleTextNode.innerHTML = title;
                });
            }
            else if(parentTagLower =='stackcontainer'){
                newobj.setTitle = function(title){
                    return;
                }
            }
        }
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
        };
        
        if(newobj.domNode && newobj.isFocusable()){
           dojo.connect(newobj, 'onFocus', function(e) {
               genro.setCurrentFocused(newobj);
           });
           if(!('onBlur' in sourceNode.attr)){
               dojo.connect(newobj,'onBlur',function(e){
                   genro.setLastSelection(newobj.focusNode || newobj.domNode);
               });
           }

        }
        if(sourceNode.attr.placeholder){
            var placeholder = sourceNode.getAttributeFromDatasource('placeholder');
            if(sourceNode.widget){
                newobj.focusNode.setAttribute('placeholder',placeholder);
            }else{
                newobj.setAttribute('placeholder',placeholder);
            }
           
        }
        if(newobj.validate){
            newobj.validate_replaced = newobj.validate;
            newobj.validate = function(isFocused){
                if(this._isvalid==false && this.value){
                    this.sourceNode._validations.error = 'Invalid';
                }
                var isValid = this.validate_replaced(isFocused);
                var sourceNode = this.sourceNode;
                var gridwidget = sourceNode.attr.gridcell;
                if (sourceNode.form && !isFocused && !gridwidget){
                    sourceNode.form.dojoValidation(this,isValid);
                }
                return isValid;
            };
        }
        if(sourceNode.attr.keepable){
            this.setKeepable(sourceNode);
        }
    },

    _getKeeperRoot:function(sourceNode){
        return sourceNode.widget.domNode;
    },
    setKeepable:function(sourceNode){
        genro.dom.addClass(sourceNode.widget.focusNode,'iskeepable');
        var keeper = document.createElement('div');
        keeper.setAttribute('title','Keep this value');
        genro.dom.addClass(keeper,'fieldkeeper');
        var keeper_in = document.createElement('div');
        keeper.appendChild(keeper_in);
        var dn = this._getKeeperRoot(sourceNode);
        dn.appendChild(keeper);
        var npath = sourceNode.absDatapath(sourceNode.attr.value);
        sourceNode.widget.setKeeper = function(v){
            genro.dom.setClass(dn.parentNode,'keeper_on',v);
            var n = genro.getDataNode(npath);
            n.attr._keep = v;
            if(sourceNode.form){
                sourceNode.form.setKeptData(npath.replace(sourceNode.absDatapath()+'.',''),n._value,n.attr._keep);
            }
        };
        keeper.onclick = function(e){
            dojo.stopEvent(e);
            var n = genro.getDataNode(npath);
            var currvalue = n.attr._keep;
            sourceNode.widget.setKeeper(!currvalue);
        }
        sourceNode.subscribe('onSetValueInData',function(value){
            var n = genro.getDataNode(npath);
            if(sourceNode.form){
                sourceNode.form.setKeptData(npath.replace(sourceNode.absDatapath()+'.',''),value,n.attr._keep);
            }
        });

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

dojo.declare("gnr.widgets.htmliframe", gnr.widgets.baseHtml, {
    constructor:function(){
        this._domtag ='iframe';
    }
});

dojo.declare("gnr.widgets.iframe", gnr.widgets.baseHtml, {
    _default_ext : 'py,png,jpg,jpeg,gif,html,pdf',

    creating:function(attributes, sourceNode) {
        sourceNode.savedAttrs = objectExtract(attributes, 'rowcount,tableid,src,rpcCall,onLoad,autoSize,onStarted,documentClasses');
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
        var mainGenro =genro.mainGenroWindow.genro;
        dojo.connect(newobj, 'onload', function(){
            var cw = this.contentWindow;
            if(this.sourceNode.attr.documentClasses){
                genro.dom.removeClass(this,'emptyIframe');
                if(!cw.document.body.innerHTML){
                    genro.dom.addClass(this,'emptyIframe');
                }        
            }
            if(!cw.genro){
                dojo.connect(cw, 'onmouseup', function(e){
                    var currentDnDMover = mainGenro.currentDnDMover;
                    if (currentDnDMover){
                        currentDnDMover.destroy();
                    }
                });
            }
        });
        if (savedAttrs.onStarted){
            sourceNode.subscribe('pageStarted',funcCreate(savedAttrs.onStarted));
        }
        if(savedAttrs.documentClasses){
            genro.dom.addClass(newobj,'emptyIframe');
        }
        this.setSrc(newobj, savedAttrs.src);
        dojo.connect(sourceNode,'_onDeleting',function(){
            newobj.src = null;
        });
    },
    autoSize:function(iframe){
        console.log('autosize',iframe);
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
    setSrc:function(domnode,v,kw){
        var that = this;
        domnode.sourceNode.watch('isVisibile',
                        function(){return genro.dom.isVisible(domnode);},
                        function(){that.setSrc_do(domnode, v, kw);});
    },
    setSrc_do:function(domnode, v, kw) {
        var sourceNode = domnode.sourceNode;
        var attributes = sourceNode.attr;
        var main_call = objectPop(attributes,'main');
        var main_kwargs = objectExtract(attributes,'main_*') || {};
        var src_kwargs = objectExtract(attributes,'src_*') || {};
        objectUpdate(src_kwargs,main_kwargs);
        src_kwargs['_calling_page_id'] = genro.page_id;
        if (attributes._if && !sourceNode.getAttributeFromDatasource('_if')) {
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
        if(main_call){
            v = v || window.location.pathname;
            src_kwargs['main_call'] = main_call;
        }
        if (v) {     
            if(sourceNode.attr.documentClasses){
                genro.dom.removeClass(domnode,'emptyIframe');
            }
            src_kwargs = sourceNode.evaluateOnNode(src_kwargs);
            v = genro.addParamsToUrl(v,src_kwargs);   
            var doset = this.initContentHtml(domnode,v);
            if (doset){
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
            
        }else{
            domnode.src = '';
        }
    },

    initContentHtml:function(domnode,src){
        var parsedSrc = parseURL(src);
        var loadingpath;
        if(parsedSrc.file && parsedSrc.file.split('.')[1] && this._default_ext.indexOf(parsedSrc.file.split('.')[1].toLowerCase())<0){
            loadingpath = document.location.protocol + '//' + document.location.host +'/_gnr/11/css/icons/download_file.png';
            domnode.contentWindow.document.body.innerHTML = '<a href="'+src+'"><div style="height:100%;width:100%;background:#F6F6F6 url('+loadingpath+') no-repeat center center;"></div></a>'; 
            return false;
        }else if(!parsedSrc.file){
            domnode.src = '';
            return false
        }
        domnode.src = '';
        loadingpath = document.location.protocol + '//' + document.location.host +'/_gnr/11/css/icons/ajax-loader-1.gif';
        domnode.contentWindow.document.body.innerHTML = '<div style="height:100%;width:100%; background:#F6F6F6 url('+loadingpath+') no-repeat center center;"></div>';
        return true;
    },

    postMessage:function(sourceNode,message){
        sourceNode.watch('windowMessageReady',function(){
            return sourceNode.domNode.contentWindow && sourceNode.domNode.contentWindow._windowMessageReady;
        },function(){
            genro.dom.windowMessage(sourceNode.domNode.contentWindow,message);
        });
    }
    
});

dojo.declare("gnr.widgets.canvas", gnr.widgets.baseHtml, {

    creating:function(attributes, sourceNode) {
        var savedAttrs = {};
        return savedAttrs;
    },


    created:function(newobj, savedAttrs, sourceNode) {
        sourceNode.savePhoto = function(kw){
            this.domNode.gnr.savePhoto(sourceNode,kw);
        };
        sourceNode.takePhoto = function(video,kw){
            this.domNode.gnr.takePhoto(sourceNode,video,kw);
        };

        if('effect' in sourceNode.attr){
            genro._PixasticReady='loading'
            genro.dom.loadJs('/_rsrc/js_libs/pixastic.js',function(){
                genro._PixasticReady=true;
                sourceNode.pixasticEffects = objectKeys(Pixastic.Actions);
            });
            sourceNode._currentEffect = sourceNode.getAttributeFromDatasource('effect');
        }
    },
    savePhoto:function(sourceNode,kw) {
        var kw = kw || {};
        var photo = sourceNode.domNode;
        var ext = kw.ext || 'png';
        var toDataURLContent = "image/"+ext;
        var data = photo.toDataURL(toDataURLContent);
        kw = sourceNode.evaluateOnNode(kw);
        if(kw.uploadPath){
            this.uploadContent(sourceNode,data,kw)
        }else{
            data = data.replace(toDataURLContent,"image/octet-stream");
            document.location.href = data;
        }
    },
    uploadContent:function(sourceNode,data,kw){
            if(!kw.filename){
                genro.dlg.alert("Missing info to upload the image",'Warning');
                return false;
            }
            genro.rpc.uploadMultipart_oneFile(data,null,{uploadPath:kw.uploadPath,
                          filename:kw.filename,
                          onResult:function(result){
                              var url = this.responseText;
                              //sourceNode.setRelativeData(src,that.decodeUrl(sourceNode,url).formattedUrl);
                           }});
        },

    setEffect:function(domnode,v,kw){
        domnode.sourceNode._currentEffect = v;
    },
    takePhoto:function(sourceNode,video,kw){
        var that = this;
        var kw=kw || {}

        var video = genro.dom.getDomNode(video);
        var canvas = sourceNode.domNode;
        var context = canvas.getContext('2d');
        if (kw.mirror){         
            context.translate(canvas.width, 0);
            context.scale(-1, 1);
        }

        var ghostcanvas = document.createElement('canvas');
        ghostcanvas.width = canvas.width ;
        ghostcanvas.height = canvas.height;
        var imageData;
        var gctx = ghostcanvas.getContext('2d');
        if (kw.sync){
            var draw=function() {
                requestAnimationFrame(draw);
                var effect = sourceNode._currentEffect;
                if (effect &&(effect !='_')){
                    gctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    var options = {};
                    Pixastic.process(ghostcanvas, effect, options,function(resultcanvas){
                         imageData = resultcanvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height);
                          context.putImageData(imageData, 0, 0);
                    });
                }else{
                  context.drawImage(video, 0, 0, canvas.width, canvas.height);
                }
            }
            draw();
        }else{
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
        }
    }

});


dojo.declare("gnr.widgets.video", gnr.widgets.baseHtml, {
    creating:function(attributes, sourceNode) {

    },

    created:function(newobj, savedAttrs, sourceNode) {
        sourceNode.startCapture = function(kw){
            if(objectNotEmpty(kw)){
                this.domNode.gnr.startCapture(sourceNode,kw);
            }
        };
        sourceNode.takePhoto = function(canvas){
            if(canvas){
                this.domNode.gnr.takePhoto(sourceNode,canvas);
            }
        };
    },
    startCapture:function(sourceNode,capture_kw){
        var onErrorGetUserMedia = objectPop(capture_kw,'onReject');
        var onAccept = objectPop(capture_kw,'onAccept');
        var onErr=function(e){
            if(onErrorGetUserMedia){
                funcApply(onErrorGetUserMedia,{e:e});
            }else{
                genro.dlg.alert('Not allowed video capture '+e,'Error');
            }
        };
        var onOk=function(stream){
            if(onAccept){
                funcApply(onAccept,{},sourceNode);
            }
            sourceNode.domNode.src=window.webkitURL? window.webkitURL.createObjectURL(stream):stream;
        };
        if(navigator.webkitGetUserMedia){
            navigator.webkitGetUserMedia(capture_kw,onOk,onErr);
        }else{
            navigator.getUserMedia(capture_kw,onOk,onErr);
        }
    }
});

dojo.declare("gnr.widgets.baseDojo", gnr.widgets.baseHtml, {
    _defaultEvent:'onClick',
    constructor: function(application) {
        this._domtag = 'div';
        this._dojowidget = true;
    },
    createDojoWidget:function(factory,attributes,domnode,sourceNode){
        if (this.customizedTemplate){
            attributes['templateString'] = this.customizedTemplate(sourceNode,factory.prototype.templateString);
        }
        return new factory(attributes, domnode);
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
        var inattr = sourceNode.getInheritedAttributes();
        if(inattr.blankIsNull){
            value = value===''?null:value; // set blank value as null
        }
        if (datanode.getValue() === value) {
            return;
        }
        objectExtract(valueAttr,'_displayedValue,_formattedValue')
        var validateresult;
        valueAttr = objectUpdate(objectUpdate({}, datanode.attr), valueAttr);
        if (sourceNode.hasValidations()) {
            validateresult = sourceNode.validationsOnChange(sourceNode, value);
            value = validateresult['value'];
            objectExtract(valueAttr, '_validation*');
            var formHandler = sourceNode.getFormHandler();
            var fldname = sourceNode.attr._valuelabel || datanode.attr.name_long || datanode.label;
            if (validateresult['error']) {
                valueAttr._validationError = validateresult['error'];
                if(validateresult.error && formHandler){
                    formHandler.publish('message',{message:fldname+': '+validateresult.error,sound:'$onerror',messageType:'error'});
                }
            }
            if (validateresult['warnings'].length) {
                if(validateresult.warnings && formHandler){
                    formHandler.publish('message',{message:fldname+': '+validateresult.warnings.join(','),sound:'$onwarning',color:'orange',font_size:'1.1em',font_weight:'bold'});
                }
                valueAttr._validationWarnings = validateresult['warnings'];
            }

        }
        this.doChangeInData(sourceNode,value,valueAttr);
        this.setValueInData(sourceNode,value,valueAttr);
    },


    mixin_setTip: function (tip) {
        this.setAttribute('title', tip);
    },
    

    mixin_setDraggable:function(value) {
        this.domNode.setAttribute('draggable', value);
    },
    mixin_setDropTarget:function(value) {
        this.sourceNode.dropTarget = value;
    },
    validatemixin_validationsOnChange: function(sourceNode, value, validateOnly) {
        var result = genro.vld.validate(sourceNode, value, true, validateOnly);
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
                if(!widget.disabled){
                    this.onChanged(widget, val);
                }
            }));
        }
    },
    onChanged:function(widget, value) {
        //genro.debug('onChanged:'+value);
        //widget.sourceNode.setAttributeInDatasource('value',value);
        this._doChangeInData(widget.domNode, widget.sourceNode, value);
        this.onDataChanged(widget);

    },
    onDataChanged:function(widget) {
        
    },
    setUrlRemote: function(widget, method, args) {
        var url = genro.rpc.rpcUrl(method, args);
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
    patch_show:function(cb){
        this.onShowing();
        this.show_replaced(cb);
        if(this.sourceNode.attr.autoSize){
            genro.callAfter(this.autoSize,1,this,'autoSize');
        }
    },
    mixin_autoSize:function(){
        if(this.containerNode.firstChild.scrollWidth>this.containerNode.firstChild.clientWidth){
            this.containerNode.firstChild.style.width = this.containerNode.firstChild.scrollWidth+'px';
        }
    },

    mixin_onShowing:function(){},
    
    creating:function(attributes, sourceNode) {
        objectPop(attributes, 'parentDialog');
        objectPop(attributes, 'centerOn');
        objectPop(attributes, 'position');
        objectPop(attributes, 'autoSize');
        var closable = ('closable' in attributes) ? objectPop(attributes, 'closable') : false;
        attributes.title = attributes.title || '';
        if (!closable) {
            attributes.templateString = "<div class=\"dijitDialog\" tabindex=\"-1\" waiRole=\"dialog\" waiState=\"labelledby-${id}_title\">\n\t<div dojoAttachPoint=\"titleBar\" class=\"dijitDialogTitleBar\">\n\t<span dojoAttachPoint=\"titleNode\" class=\"dijitDialogTitle\" id=\"${id}_title\">${title}</span>\n\t</div>\n\t\t<div dojoAttachPoint=\"containerNode\" class=\"dijitDialogPaneContent\"></div>\n</div>\n";
        } else if (closable!=true) {
            var closeAction;
            if(closable=='ask'){
                closeAction='onAskCancel';
            }else if(closable=='publish'){
                closeAction='onCancelPublish';
            }
            attributes.templateString = "<div class=\"dijitDialog\" tabindex=\"-1\" waiRole=\"dialog\" waiState=\"labelledby-${id}_title\">\n\t<div dojoAttachPoint=\"titleBar\" class=\"dijitDialogTitleBar\">\n\t<span dojoAttachPoint=\"titleNode\" class=\"dijitDialogTitle\" id=\"${id}_title\">${title}</span>\n\t<span dojoAttachPoint=\"closeButtonNode\" class=\"dijitDialogCloseIcon\" dojoAttachEvent=\"onclick: "+closeAction+"\">\n\t\t<span dojoAttachPoint=\"closeText\" class=\"closeText\">x</span>\n\t</span>\n\t</div>\n\t\t<div dojoAttachPoint=\"containerNode\" class=\"dijitDialogPaneContent\"></div>\n</div>\n";

            sourceNode.closeAttrs = objectExtract(attributes, 'close_*');
        }
    },
    
    
    created:function(widget, savedAttrs, sourceNode) {
        if (dojo_version == '1.5') {
            var position = sourceNode.attr.position;
            if (position) {
                position = position.split(',');
                widget._relativePosition = {x:position[0],y:position[1]};
            }
        }
        if (dojo_version == '1.1') {
            dlgtype = 'modal';
            zindex = 800;
            if(sourceNode.attr.noModal){
                var dlgtype = 'nomodal';
                var zindex = 500;
            }
            var ds = genro.dialogStack;
            
            dojo.connect(widget, "show", widget,
                        function() {
                            if (this != ds.slice(-1)[0]) {
                                var parentDialog = ds.length>0?ds[ds.length-1]:null;
                                ds.push(this);
                                var zIndex = widget.sourceNode.attr.z_index || (zindex + ds.length*2);
                                dojo.style(this._underlay.domNode, 'zIndex', zIndex);
                                dojo.style(this.domNode, 'zIndex', zIndex + 1);
                                 if (parentDialog) {
                                    dojo.forEach(parentDialog._modalconnects, dojo.disconnect);
                                    parentDialog._modalconnects = [];
                                    if (sourceNode.attr.stacked){
                                        var parentNodeStyle = parentDialog.domNode.style;
                                        dojo.style(this.domNode,'top',(parseInt(parentNodeStyle.top)+16)+'px');
                                        dojo.style(this.domNode,'left',(parseInt(parentNodeStyle.left)+16)+'px');
                                    }
                                }
                            }

                        });
            dojo.connect(widget, "hide", widget,
                        function() {
                            if (this == ds.slice(-1)[0]) {
                                ds.pop(); 
                                var parentDialog = ds.length>0?ds[ds.length-1]:null;
                                if (parentDialog) {
                                     parentDialog._modalconnects.push(dojo.connect(window, "onscroll", parentDialog, "layout"));
                                     parentDialog._modalconnects.push(dojo.connect(dojo.doc.documentElement, "onkeypress", parentDialog, "_onKey"));
                                }                   
                            }
                        });
        }
        genro.dragDropConnect(widget.domNode);
        if (genro.isDeveloper){
            genro.dev.inspectConnect(widget.domNode);
        }

    },
   versionpatch_11__onKey:function(){
       //onkey block inactive (ckeditor)
   },
    
    versionpatch_11__position: function() {
        var centerOn = this.sourceNode.attr.centerOn;
        centerOn = centerOn?genro.dom.getDomNode(centerOn):null
        if (!centerOn) {
            this._position_replaced();
        }
        else {
            centerOn = this.sourceNode.currentFromDatasource(centerOn);
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
    attributes_mixin_onCancelPublish:function(event) {
        if(genro.activeForm && genro.activeForm.currentFocused){
            genro.activeForm.currentFocused.focusNode.blur();
            genro.activeForm.currentFocused = null;
            this.sourceNode.publish('close',{modifiers:genro.dom.getEventModifiers(event)});
            return;
        }
        this.sourceNode.publish('close',{modifiers:genro.dom.getEventModifiers(event)});
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
    onBuilding:function(sourceNode){
        //{value:,height,width}
        var areaAttr = objectUpdate({},sourceNode.attr);
        var speech = objectPop(areaAttr,'speech');
        var editor = objectPop(areaAttr,'editor');
        var tag = this._domtag;
        var notrigger = {'doTrigger':false};
        if (editor || speech){
            var parentNode =sourceNode.getParentNode();
            var insideTable = parentNode && parentNode.attr.tag=='td';
            var _class = 'textAreaWrapper';
            if(insideTable){
                _class+= ' textAreaWrapperInTable';
            }
            if(editor){
                _class+= ' textAreaIsEditor';
            }
            sourceNode.attr = {'tag':'div',_class:_class};
            var tKw = {overflow:'hidden',_class:'textAreaWrapperArea'}; 
            if(editor){
                tKw['border'] = '1px solid silver';
                tKw['rounded'] = 4;
            } 
            var top = sourceNode._('div',tKw,notrigger);
            var bottom = sourceNode._('div',{_class:'textAreaWrapperButtons',transition:'1s all'},notrigger)
            if(editor){
                bottom._('div',{_class:'TAeditorPalette',connect_onclick:function(){
                    genro.dlg.floatingEditor(textarea,{});
                }},{'doTrigger':false})
                tag = 'ckeditor';
                objectPop(areaAttr,'tag')
                areaAttr['toolbar'] = false;
                areaAttr['config_height']=objectPop(areaAttr,'height');
                areaAttr['config_width']=objectPop(areaAttr,'width');


                this._dojotag = null;
            }
            var textarea = top._(tag,areaAttr,notrigger).getParentNode();
            if(speech){
                var b = bottom._('div',{_class:'TAspeechInputBox'},notrigger);

                b._('input',{_class:'TAspeechInput','tabindex':32767,
                            "x-webkit-speech":"x-webkit-speech",onCreated:function(newobj,attributes){
                                newobj.onwebkitspeechchange = function(){
                                    var v = this.value;
                                    this.value = '';
                                    if(textarea.widget){
                                        textarea.widget.gnr.onSpeechEnd(textarea,v);
                                    }
                                    else if(textarea.externalWidget){
                                        textarea.externalWidget.gnr.onSpeechEnd(textarea,v);
                                    }

                                    
                                };
                            }          
                },{'doTrigger':false});
            }
        }
    },
    onSpeechEnd:function(sourceNode,v){
        var lastSelection = genro._lastSelection;
        if(lastSelection && (lastSelection.domNode == sourceNode.widget.domNode)){
            var oldValue = sourceNode.getAttributeFromDatasource('value');
            var fistchunk = oldValue.slice(0,lastSelection.start);
            var secondchunk =  oldValue.slice(lastSelection.end);
            v = fistchunk+v+secondchunk;
        }
        setTimeout(function(){
            sourceNode.setAttributeInDatasource('value',v,true);
            sourceNode.widget.domNode.focus();
        },1);
    },

    creating:function(attributes, sourceNode) {
        var savedAttrs = objectExtract(attributes, 'value,suggestions');
        return savedAttrs;
    },

    created:function(newobj, savedAttrs, sourceNode) {
        if (savedAttrs.value) {
            newobj.setValue(savedAttrs.value);
        }
       if(savedAttrs.suggestions){
           sourceNode._('menu','suggestionMenu',{'_class':'smallmenu',
                                                action:"genro.dom.setTextInSelection($2,($1.fullpath.indexOf('caption_')==0?$1.label:$1.fullpath));",values:savedAttrs.suggestions});
        }
        dojo.connect(newobj.domNode, 'onchange', dojo.hitch(this, function() {
            this.onChanged(newobj);
        }));
    },
    
    mixin_setSuggestions:function(suggestions){
        this.sourceNode._value.popNode('suggestionMenu');
        this.sourceNode._('menu','suggestionMenu',{'_class':'smallmenu',action:"genro.dom.setTextInSelection($2,($1.fullpath.indexOf('caption_')==0?$1.label:$1.fullpath));",values:suggestions});
    },
    onChanged:function(widget) {
        var value = widget.getValue();
        this._doChangeInData(widget.domNode, widget.sourceNode, value);
    },

    mixin_displayMessage: function(/*String*/ message){
    			// summary:
    			//		User overridable method to display validation errors/hints.
    			//		By default uses a tooltip.
    			if(this._message == message){ return; }
    			this._message = message;
    			dijit.hideTooltip(this.domNode);
    			if(message){
    				dijit.showTooltip(message, this.domNode, this.tooltipPosition);
    			}
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
        sourceNode.subscribe('switchPage',function(page){
            this.widget.switchPage(page);
        });
        widget.gnrPageDict = {};
        dojo.connect(widget, 'addChild', dojo.hitch(this, 'onAddChild', widget));
        dojo.connect(widget, 'removeChild', dojo.hitch(this, 'onRemoveChild', widget));
        //dojo.connect(widget,'_transition',widget, 'onChildTransition');

    },
    mixin_switchPage:function(p){
        var handler = (p==parseInt(p))?'setSelected':'setSelectedPage';
        this[handler](p);
    },
    patch_selectChild:function(page){
        var sourceNode = this.sourceNode;
        if(sourceNode.attr.nodeId){
            var oldselected = this.selectedChildWidget;
            if(oldselected){
                var oldpagename = oldselected.sourceNode.attr.pageName;
                if(oldpagename){
                    sourceNode.publish('hiding', {pageName:oldpagename});
                }
            }
            var newpagename = page.sourceNode.attr.pageName;
            if(newpagename){
                sourceNode.publish('showing', {pageName:newpagename});
            }
        }
        this.selectChild_replaced(page);
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
    mixin_hasPageName:function(pageName){
        return pageName in this.gnrPageDict;
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
            sourceNode.publish('selected', {'change':newpage + '_' + (st ? 'show' : 'hide'),'page':newpage,'selected':st});
        };
        if (selpath) {
            cbUpd(selpath, widget.getChildIndex(child), st);
        }
        if (selpage) {
            cbUpd(selpage, child.sourceNode.attr.pageName, st);
        }
    },

    onAddChild:function(widget, child) {
        if(!child.getParent){
            child.getParent = function(){
                return widget;
            };
        }
        gnr.setOrConnectCb(child, 'onShow', dojo.hitch(this, 'onShowHideChild', widget, child, true));
        gnr.setOrConnectCb(child, 'onHide', dojo.hitch(this, 'onShowHideChild', widget, child, false));
        var pageName = child.sourceNode.attr.pageName;
        if (pageName) {
            widget.gnrPageDict = widget.gnrPageDict || {};
            widget.gnrPageDict[pageName] = child;
        }
    },
    mixin_onDestroyingChild:function(child){
        this.removeChild(child);
    },
    onRemoveChild:function(widget, child) {
        var pageName = child.sourceNode.attr.pageName;
        if (pageName) {
            objectPop(widget.gnrPageDict, pageName);
        }
        setTimeout(function(){
            if(child.selected && widget.getChildren().length==0){
            var sourceNode = widget.sourceNode;
            var selpath = sourceNode.attr['selected'];
            var selpage = sourceNode.attr['selectedPage'];
            if(selpath){
                sourceNode.setRelativeData(selpath,null);
            }
            if(selpage){
                sourceNode.setRelativeData(selpage,null);
            }
        }

        },1);
        
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
        if (dojo_version == '1.1') {
            dojo.connect(widget, 'addChild', dojo.hitch(this, 'onAddChild', widget));
            dojo.connect(widget, 'removeChild', dojo.hitch(this, 'onRemoveChild', widget));
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
    
    onRemoveChild:function(widget,child){
        delete child.parentBorderContainer;
    },
    
    onAddChild:function(widget,child){
        child.parentBorderContainer=widget;
        var splitter=widget._splitters[child.region];
        if(splitter){
            if(child.domNode.style.display=='none'){
                dojo.style(splitter, 'display','none');
        }
         //splitter=dijit.getEnclosingWidget(splitter);
         
         //dojo.connect(splitter,'_stopDrag',dojo.hitch(this,'onSplitterStopDrag',widget,splitter));
        }
     },
     
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
    },
    mixin_setRegionVisible:function(region,show){
        var regionbox = this['_' + region];
        if(show=='toggle'){
            var show = regionbox.style.display=='none';
        }
        dojo.style(regionbox, 'display', show?'block':'none');
        if(this._splitters[region]){
            dojo.style(this._splitters[region], 'display', show?'block':'none');
        }
        this._layoutChildren(region);
        this.layout();
        return show;
    },
    mixin_isRegionVisible:function(region){
        return this['_'+region].style.display!='none';
    }
});

dojo.declare("gnr.widgets.TitlePane", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'TitlePane';
    },

    created: function(widget, savedAttrs, sourceNode) {
        if (sourceNode.hasDynamicAttr('open')) {
            var isOpen = sourceNode.getAttributeFromDatasource('open');

            if (widget.open != isOpen) {
                widget.toggle();
            }

            dojo.connect(widget, 'toggle', function(e) {
                sourceNode.setAttributeInDatasource('open', widget.open);
            });
        }
    },
    mixin_setOpen: function(isOpen, pc) {
        if (this.open != isOpen) {
            this.toggle();
        }
    }
});

dojo.declare("gnr.widgets.ResizeHandle", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'ResizeHandle';
        genro.dom.loadCss("/_dojo/11/dojo/dojox/layout/resources/ResizeHandle.css");
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
    creating:function(attributes,sourceNode){
        objectPop(attributes,'persist')
    },
    created: function(widget, savedAttrs, sourceNode) {
        widget._startZ = 700;
        var nodeId = sourceNode.attr.nodeId;
        if (nodeId){
            dojo.connect(widget,'show',function(){
                genro.publish(nodeId+'_show');
            });
        }
        dojo.subscribe("/dnd/move/stop",function(mover){
            var node=mover.host.node;
            var c=dojo.coords(node);
            if (c.y<0){
                node.style.top = "0px";
            }
            });
        if(widget.resizeHandle){
            dojo.connect(widget,'startup',function(){
                dojo.connect(this._resizeHandle,'_beginSizing',function(e){
                    this.screenStartPoint = {x:e.screenX,y:e.screenY};
                    this.page_id = genro.page_id;
                    genro.mainGenroWindow.genro.currentResizeHandle=this;
                });
                dojo.connect(this._resizeHandle,'_endSizing',function(e){
                    genro.mainGenroWindow.genro.currentResizeHandle=null;
                });
            });
        }
        dojo.connect(widget,'maximize',function(){
            this.resize({'t':'0','l':'0'});
        });
    },
    patch_close:function(cb){
        this.saveRect();
        this.sourceNode.getParentBag().popNode(this.sourceNode.label);
    },
    patch_hide:function(cb){
        this.saveRect();
        this.hide_replaced(cb);
    },
   
    patch_show:function(cb){
        this.restoreRect();
        this.onShowing();
        var that = this;
        this.show_replaced(cb);
        this.bringToTop();
    },
    

    mixin_onChangedContent:function(){   
        if(this.sourceNode.attr.autoSize!=false){
            this.autoSize();
        }     
    },
    mixin_restoreRect:function(){
        if(this.sourceNode.attr.nodeId && (this.sourceNode.attr.persist!==false)){
            var storeKey = 'palette_rect_' + genro.getData('gnr.pagename') + '_' + this.sourceNode.attr.nodeId;
            if(this.sourceNode.attr.fixedPosition){
                return;
            }
            var rect = genro.getFromStorage("local", storeKey, dojo.coords(this.domNode));
            if(rect && rect.w && rect.h){
                this.resize(rect);
            }
        }     
    },
    mixin_saveRect:function(){
        if(this.sourceNode.attr.nodeId && genro.dom.isVisible(this.domNode) && !this._maximized && (this.sourceNode.attr.persist!==false)){
            var storeKey = 'palette_rect_' + genro.getData('gnr.pagename') + '_' + this.sourceNode.attr.nodeId;
            genro.setInStorage("local", storeKey, dojo.coords(this.domNode));
        }     
    },
    mixin_onShowing:function(){
        if(this.sourceNode.attr.autoSize!=false &&(this.sourceNode.attr._lazyBuild || this.sourceNode._value._nodes.length==0)){
            var domNode = this.domNode;
            var oldwidth = domNode.style.width;
            var oldleft = domNode.style.left;
            domNode.style.left=parseInt(oldleft) +parseInt(oldwidth) +'px';
            domNode.style.width='1px';
            domNode.style.height='1px';
        }
        
    },
    
    mixin_autoSize:function(){
        var domNode = this.domNode;
        var layoutcoords = dojo.coords(this.containerNode.firstChild);
        var newcoords =  dojo.coords(domNode);
        newcoords['l'] =  newcoords['l']-(layoutcoords['w']-newcoords['w']);
        newcoords['h'] = layoutcoords['h']+16;
        newcoords['w'] = layoutcoords['w'];
        this.resize(newcoords);        
    },
    
    mixin_setBoxAttributes:function(kw){
        var dimensionDict = {'height':'h','width':'w','left':'l','right':'r','t':'top'};
        var resizer = {};
        for (var k in kw){
            if(k in dimensionDict){
                resizer[dimensionDict[k]] = parseInt(kw[k].replace('px',''));
            }else{
                this.setAttribute(k,kw[k]);
            }
        }
        if(objectNotEmpty(resizer)){
            this.resize(resizer);
        }
    }
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
        if(attributes.draggable){
            savedAttrs['draggable'] = objectPop(attributes,'draggable');
        }
        if (sourceNode.attr.label == '-') {
            this._dojotag = 'MenuSeparator';
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
        if (attributes.checked) {
            attributes.iconClass = 'tick_icon10';
        }
        if(attributes.favorite){
            attributes.iconClass = 'box16 star';
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        if(savedAttrs.draggable){
            widget.focusNode.setAttribute('draggable',true);
        }
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
        var savedAttrs = objectExtract(attributes, 'modifiers,validclass,storepath,values');
        if (savedAttrs.storepath) {
            sourceNode.registerDynAttr('storepath');
        }
        if (!attributes.connectId) {
            savedAttrs['connectToParent'] = true;
        }
        if(attributes.menuItemCb){
            attributes['menuItemCb'] = funcCreate(attributes.menuItemCb,'item',sourceNode);
        }
        if(attributes.disabledItemCb){
            attributes['disabledItemCb'] = funcCreate(attributes.disabledItemCb,'item',sourceNode);
        }
        if(attributes.hiddenItemCb){
            attributes['hiddenItemCb'] = funcCreate(attributes.hiddenItemCb,'item',sourceNode);
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        if(savedAttrs.values){
            var contentBag = new gnr.GnrBag(objectFromString(savedAttrs.values,',','kv'));
            var menubag = new gnr.GnrDomSource();
            gnr.menuFromBag(contentBag, menubag, sourceNode.attr._class);
            sourceNode.setValue(menubag, false);
        }
        else if (savedAttrs.storepath) {
            var contentNode = genro.getDataNode(sourceNode.absDatapath(savedAttrs.storepath));
            if (contentNode ) {
                var content = contentNode.getValue('static');
                if (content) {
                    var menubag = new gnr.GnrDomSource();
                    gnr.menuFromBag(content, menubag, sourceNode.attr._class);
                    sourceNode.setValue(menubag, false);
                }else if (contentNode.getResolver()) {
                    sourceNode.setResolver(contentNode.getResolver());
                }else{
                    console.warn('the menu at storepath:'+savedAttrs.storepath+' is empty');
                }
            }else{
                console.warn('the menu at storepath:'+savedAttrs.storepath+' is empty');
            }
        }

        if (sourceNode && savedAttrs['connectToParent']) {
            var parentNode = sourceNode.getParentBag().getParentNode();
            var parentWidget = parentNode.widget;
            if (parentWidget) {
                if (!(('dropDown' in  parentWidget) || ('popup' in parentWidget ))) {
                    if(parentWidget.downArrowNode){
                        parentWidget._downArrowMenu = true;
                        if(parentWidget.sourceNode.attr.connectedMenu!=sourceNode.attr.id){
                            widget.bindDomNode(parentWidget.downArrowNode);
                        }
                    }else{
                         widget.bindDomNode(parentWidget.domNode);
                    }
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
            var menu = this;
            dojo.forEach(this._bindings, function(b) {
                dojo.forEach(b,function(n){menu.unBindDomNode(n[0]);});
            });
            delete this._bindings;
        }
        this.destroy_replaced.call(this);
    },
    
versionpatch_11__contextMouse: function (e) {
        this.originalContextTarget = e.target;
        if(genro.dom.isDisabled(this.originalContextTarget,true)){
            return;
        }
        var sourceNode = this.sourceNode;
        var wdg = sourceNode.widget;
        if( (wdg.modifiers || wdg.validclass ) && !(genro.wdg.filterEvent(e, wdg.modifiers, wdg.validclass)) ){
            return;
        }

        if (sourceNode) {
            var resolver = sourceNode.getResolver();
            if (resolver && resolver.expired()) {
                if(sourceNode.attr.onOpeningMenu){
                    var optkwargs = funcApply(sourceNode.attr.onOpeningMenu,{evt:e},sourceNode);
                }
                var result = sourceNode.getValue('notrigger',optkwargs);
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
        wdg = sourceNode.widget;
        if (wdg.menuItemCb){
            dojo.forEach(wdg.getChildren(),wdg.menuItemCb);
        }
        if (wdg.disabledItemCb){
            dojo.forEach(wdg.getChildren(),function(item){
                item.setDisabled(wdg.disabledItemCb(item));
            });
        }
        if (wdg.hiddenItemCb){
            dojo.forEach(wdg.getChildren(),function(item){
                item.setHidden(wdg.hiddenItemCb(item));
            });
        }

        if(wdg.modifiers){
            wdg._contextMouse_replaced.call(wdg, e);
            wdg._openMyself_replaced.call(wdg, e);
        }
        else if (e.button == 2) {
            wdg._contextMouse_replaced.call(wdg, e);
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
    },
    mixin_onOpeningPopup:function(popupKwargs){
        var kw = this.sourceNode.currentAttributes();
        var aroundWidget = kw.attachTo? kw.attachTo.widget:null;

        if(!aroundWidget && this.originalContextTarget){
            var enclosingWidget = dijit.getEnclosingWidget(this.originalContextTarget);
            var cmenu = enclosingWidget.sourceNode.attr.connectedMenu;
            if(cmenu && cmenu == this.sourceNode.attr.id){
                aroundWidget = enclosingWidget;
            }
        }
        if(aroundWidget){
            this.gnrPlaceAround(popupKwargs,aroundWidget);
        }
    },
    mixin_gnrPlaceAround:function(popupKwargs,widget){
        popupKwargs.popup.domNode.style.width = widget.domNode.clientWidth+'px';
        popupKwargs.orient = this.isLeftToRight() ? {'BL':'TL', 'BR':'TR', 'TL':'BL', 'TR':'BR'}: {'BR':'TR', 'BL':'TL', 'TR':'BR', 'TL':'BL'};
        popupKwargs.around = widget.domNode;
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
        }else if(attributes.recordTemplate){
            var recordTemplate = objectPop(attributes,'recordTemplate');
            var tpltable = recordTemplate.table;
            var tplname = recordTemplate.template || 'tooltip';
            var pkeyCb = recordTemplate.pkeyCb;
            attributes['label'] = function(n){
                var pkey = pkeyCb?funcApply(pkeyCb,null,n.sourceNode):n.attr.pkey;
                return genro.serverCall('renderTemplate',{record_id:pkey,table:tpltable,tplname:tplname},null,null,'POST');
            }
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
        var defaultMod;
        if(this.tooltip_type=='help'){
            defaultMod = genro.tooltipHelpModifier();
        }
        if (genro.wdg.filterEvent(e, (this.modifiers || defaultMod), this.validclass)) {
            this._onHover_replaced.call(this, e);
        }
    }
    ,
   //patch_close:function(){
   //    return 'for debugging tooltip'
   //},

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
        savedAttrs['publish'] = objectPop(attributes, 'publish');
        savedAttrs['ask_params'] = objectPop(attributes,'ask');
        var focusOnTab = objectPop(attributes,'focusOnTab');
        if(attributes.iconRight){
            attributes.templateString = "<div class=\"dijit dijitReset dijitLeft dijitInline\"\n\tdojoAttachEvent=\"onclick:_onButtonClick,onmouseenter:_onMouse,onmouseleave:_onMouse,onmousedown:_onMouse\"\n\twaiRole=\"presentation\"\n\t><button class=\"dijitReset dijitStretch dijitButtonNode dijitButtonContents\" dojoAttachPoint=\"focusNode,titleNode\"\n\t\ttype=\"${type}\" waiRole=\"button\" waiState=\"labelledby-${id}_label\"\n\t\t><div class=\"dijitReset dijitInline\"><center class=\"dijitReset dijitButtonText\" id=\"${id}_label\" dojoAttachPoint=\"containerNode\">${label}</center></div\n\t><span class=\"dijitReset dijitInline ${iconClass}\" dojoAttachPoint=\"iconNode\" \n \t\t\t><span class=\"dijitReset dijitToggleButtonIconChar\">&#10003;</span \n\t\t></span\n\t\t></button\n></div>\n";
        }
        if (!focusOnTab){
            attributes['tabindex'] = 32767;
        }
        return savedAttrs;
    },
    
    created: function(widget, savedAttrs, sourceNode) {
        dojo.connect(widget, 'onClick', sourceNode, this.onClick);
        objectExtract(sourceNode._dynattr, 'fire_*');
        objectExtract(sourceNode._dynattr, 'fire,publish');
        if (savedAttrs['_style']) {
            var buttonNode = dojo.query(".dijitButtonNode", widget.domNode)[0];
            dojo.style(buttonNode, savedAttrs['_style']);
        }
        if(savedAttrs.ask_params){
            sourceNode._ask_params = savedAttrs.ask_params;
        }

    },


    onClick:function(e) {
        var inattr = this.getInheritedAttributes();
        //var _delay = '_delay' in inattr? inattr._delay: 100;
        var _delay = inattr._delay;
        if(!_delay){
            return this.widget._onClickDo(e,inattr);
        }
        if(this._pendingClick){
            var pc = this._pendingClick;
            delete this._pendingClick
            clearTimeout(pc);
        }
        var that = this;
        this._pendingClickCount = (this._pendingClickCount || 0)+1;
        this._pendingClick = setTimeout(function(){
            var count = that._pendingClickCount;
            that._pendingClickCount = 0;
            that.widget._onClickDo(e,inattr,count);
        },_delay);
    },
    mixin__onClickDo:function(e,inattr,count) {
        var modifier = eventToString(e);
        var action = inattr.action;
        var sourceNode = this.sourceNode;
        if (action) {
            var action_attributes = sourceNode.currentAttributes();
            var ask_params = sourceNode._ask_params;
            var modifiers = genro.dom.getEventModifiers(e);
            var skipOn,askOn,doAsk;
            if(ask_params){
                skipOn = ask_params.skipOn;
                askOn = ask_params.askOn;
                doAsk = !(askOn || skipOn) || (askOn && askOn==modifiers) || (skipOn && skipOn!=modifiers);
            }
            if(ask_params && doAsk){
                var promptkw = objectUpdate({},sourceNode._ask_params);
                promptkw.fields = promptkw.fields.map(function(kw){
                    kw = objectUpdate({},kw);
                    if(kw['name'] in action_attributes){
                        kw['default_value'] = action_attributes[kw['name']];
                    }
                    kw['value'] = '^.'+kw['name'];
                    return kw;
                })
                promptkw.widget = objectPop(promptkw,'fields');
                promptkw.action = function(result){
                    if(result && result.len()){
                        objectUpdate(action_attributes,result.asDict());
                    }
                    funcApply(action, objectUpdate(action_attributes, {event:e,_counter:count}), sourceNode);
                }

                genro.dlg.prompt(objectPop(promptkw,'title','Parameters'),promptkw);
            }else{
                if(ask_params && ask_params.fields){
                    for (var k in ask_params.fields){
                        action_attributes[ask_params.fields[k]['name']] = ask_params.fields[k]['default_value'];
                    }
                }
                funcApply(action, objectUpdate(action_attributes, {event:e,_counter:count}), sourceNode);
            }
            return;
        }
        if (sourceNode.attr.fire) {
            var s = eventToString(e) || true;
            sourceNode.setRelativeData(sourceNode.attr.fire, s, {modifier:modifier,_counter:count}, true);
        }
        if(sourceNode.attr.publish){
            genro.publish(sourceNode.attr.publish,true);
        }
        var fire_list = objectExtract(sourceNode.attr, 'fire_*', true);
        for (var fire in fire_list) {
            sourceNode.setRelativeData(fire_list[fire], fire, {modifier:modifier,_counter:count}, true);
        }
    },
    mixin_setIconClass:function(iconClass){
        var domNode = this.iconNode;
        dojo.removeClass(domNode,this.iconClass);
        this.iconClass = iconClass;
        dojo.addClass(domNode,this.iconClass);
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
        var dn = widget.domNode;
        var pn = widget.domNode.parentNode;
        var gnrcheckbox_wrapper = document.createElement('div')
        gnrcheckbox_wrapper.setAttribute('class','gnrcheckbox_wrapper')
        pn.replaceChild(gnrcheckbox_wrapper,dn);
        gnrcheckbox_wrapper.appendChild(dn);
        sourceNode._gnrcheckbox_wrapper = gnrcheckbox_wrapper;
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
    _getKeeperRoot:function(sourceNode){
        return sourceNode._gnrcheckbox_wrapper;
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

dojo.declare("gnr.widgets._BaseTextBox", gnr.widgets.baseDojo, {
    formattedValueHandler:function(widget, savedAttrs, sourceNode){
        if((sourceNode.attr.format || sourceNode.attr.mask) && sourceNode.attr.displayFormattedValue){
           sourceNode.freeze();
           sourceNode._('span',{'innerHTML':sourceNode.attr.value+'?_formattedValue',_class:'formattedViewer',
                               _attachPoint:'focusNode.parentNode'});
           sourceNode.unfreeze();
           dojo.addClass(widget.focusNode.parentNode,'formattedTextBox');
       }
    },
    patch_displayMessage:function(message){
        if(!isNullOrBlank(this.value)){
            this.displayMessage_replaced(message);
        }
    }

});

dojo.declare("gnr.widgets.TextBox", gnr.widgets._BaseTextBox, {
    constructor: function(application) {
        this._domtag = 'input';
        this._dojotag = 'ValidationTextBox';
    },
    
    /*mixin_displayMessage: function(message){
     //genro.dlg.message(message, null, null, this.domNode)
     genro.setData('_pbl.errorMessage', message)
     },*/
    creating: function(attributes, sourceNode) {
        objectPop(attributes,'multivalue');
        objectPop(attributes,'multivalueCb');

        attributes.trim = (attributes.trim == false) ? false : true;
        return {};
    },
    onBuilding:function(sourceNode){
        var attr = sourceNode.attr;
        var multivalue = attr.multivalue || attr.multivalueCb;
        if(attr.multivalueCb){
            sourceNode._getMultiValue = funcCreate('return '+attr.multivalueCb,null,sourceNode);
        }
        if(multivalue){     
            sourceNode.freeze();
            sourceNode._('tooltipMultivalue',{});
            sourceNode.unfreeze(true);
        }
    },
    onSettingValueInData: function(sourceNode, value,valueAttr) {
        if(sourceNode._onSettingValueInData){
            sourceNode._onSettingValueInData(sourceNode,value,valueAttr);
        }
        return value;
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

dojo.declare("gnr.widgets.DateTextBox", gnr.widgets._BaseTextBox, {
    constructor: function() {
        this._domtag = 'input';
        this._dojotag = 'DateTextBox';
    },
    
    onChanged:function(widget, value) {
        //genro.debug('onChanged:'+value);
        //widget.sourceNode.setAttributeInDatasource('value',value);
        console.log('onChanged',value)

        if (value) {
            this._doChangeInData(widget.domNode, widget.sourceNode, value, {dtype:'D'});
        }
        else {
            this._doChangeInData(widget.domNode, widget.sourceNode, null);
        }
    },
    patch__onFocus: function(/*Event*/ evt){
    // summary: open the TimePicker popup
    
    },

    creating: function(attributes, sourceNode) {
        
        attributes.constraints = objectExtract(attributes, 'formatLength,datePattern,fullYear,min,max,strict,locale');
        attributes.constraints.selector='date';
        if ('popup' in attributes && (objectPop(attributes, 'popup') == false)) {
            attributes.popupClass = null;
        }
    },
    created: function(widget, savedAttrs, sourceNode) {
        if(sourceNode.attr.noIcon){
            return
        }
        var focusNode;
        var curNode = sourceNode;
        genro.dom.addClass(widget.focusNode,'comboArrowTextbox')
        var box= sourceNode._('div',{cursor:'pointer', width:'20px',tabindex:-1,
                                position:'absolute',top:0,bottom:0,right:0,connect_onclick:function(){widget._open();}})
        box._('div',{_class:'dateTextBoxCal',position:'absolute',top:0,bottom:0,left:0,right:0,tabindex:-1})
    },

    patch_parse:function(value,constraints){
        if(value && value.match(/^\d{6}$|^\d{8}$/) && !this._focused){
            var tokens = dojo.date.locale._parseInfo(constraints).tokens;
            var d1 = parseInt(value.slice(0,2));
            var d2 = parseInt(value.slice(2,4));
            var y = parseInt(value.slice(4));
            var d,m;
            if(tokens[0]=='dd'){
                d = d1;
                m = d2;
            }else{
                m = d1;
                d = d2;
            }
            if(y<100){
                var pivotYear ='pivotYear' in this.sourceNode.attr?this.sourceNode.attr.pivotYear:20;
                var year = '' + new Date().getFullYear();
                var century = year.substring(0, 2) * 100;
                var cutoff = Math.min(Number(year.substring(2, 4)) + pivotYear, 99);
                var y = (y < cutoff) ? century + y : century - 100 + y;
            }
            var r = new Date(y,m-1,d);
            var that = this;
            setTimeout(function(){
                that.setValue(r,true);
            },1);
            return;
        }
        return dojo.date.locale.parse(value, constraints) || undefined; 
    }
});

dojo.declare("gnr.widgets.TimeTextBox", gnr.widgets._BaseTextBox, {
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
        if ('popup' in attributes && (objectPop(attributes, 'popup') == false)) {
            attributes.popupClass = null;
        }
        
    },
    mixin_setPickInterval:function(interval) {
        var timeInt = 'T00:' + interval + ':00';
        this.constraints.clickableIncrement = timeInt;

    }
});

dojo.declare("gnr.widgets.NumberTextBox", gnr.widgets._BaseTextBox, {
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
    onSettingValueInData: function(sourceNode, value,valueAttr) {
        if (value === "") {
            value = null;
        }
        return value;
    },
    patch_format:function(v,c){
        if(v==null){
            return '';
        }else{
            return this.format_replaced(v,c);
        }
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
dojo.declare("gnr.widgets.DojoGrid", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'DojoGrid';
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
    patch__textSizeChanged:function(){
        if(dojo.getComputedStyle(this.domNode)){
            //if is inside hidden iframe this method must not be called
            this._textSizeChanged_replaced();
        }
    },
    
    mixin_setStructpath:function(val, kw) {
        this.structBag = genro.getData(this.sourceNode.attrDatapath('structpath'));
        this.cellmap = {};
        this.setStructure(this.gnr.structFromBag(this.sourceNode, this.structBag, this.cellmap));
        this.onSetStructpath(this.structBag);
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
        this.sourceNode.publish('editrow',{pkey:this.rowIdByIndex(idx)})
    },
    mixin_linkedFormLoad: function(e) {
        var idx = e.rowIndex;
        this.sourceNode.publish('editrow',{pkey:this.rowIdByIndex(idx)})
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
                genro.dom.removeClass(frameNode,'treeShowTrash');
            });
            sourceNode._showTrash=function(show){
                genro.dom.addClass(frameNode,'treeShowTrash');
            };
            sourceNode.attr.onTrashed = sourceNode.attr.onTrashed || 'this.widget.deleteColumn(data);';
        }

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
            }else if(sourceNode.form && sourceNode.form.isDisabled()){
                return;
            }else {
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
        if(!sourceNode.attr.storepath){
            if(sourceNode.attr.store){
                var storeNode = genro.nodeById(sourceNode.attr.store+'_store');
                if(!storeNode){
                    console.log('missing storepath');
                }else{
                    sourceNode.attr.storepath = storeNode.absDatapath(storeNode.attr.storepath);//storeNode.absDatapath(storeNode.attr.path);
                    sourceNode._useStore=true;
                }
            }
        }
        sourceNode.attr.nodeId = sourceNode.attr.nodeId || 'grid_' + sourceNode.getStringId();
        var relativeWorkspace= sourceNode.attr.controllerPath || sourceNode.attr.relativeWorkspace;
        sourceNode.gridControllerPath = relativeWorkspace ? sourceNode.absDatapath() : 'grids.' + sourceNode.attr.nodeId;
        if (sourceNode.attr.selfDragRows) {
            this.selfDragRowsPrepare(sourceNode);
        }
        if (sourceNode.attr.selfDragColumns || sourceNode.attr.configurable) {
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
        var attributesToKeep = 'autoHeight,autoRender,autoWidth,defaultHeight,elasticView,fastScroll,keepRows,model,rowCount,rowsPerPage,singleClickEdit,structure,'; //continue
        attributesToKeep = attributesToKeep + 'datamode,sortedBy,filterColumn,excludeCol,excludeListCb,editorEnabled,filteringGrid,editorSaveMethod';
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
                if(currSet){
                    return currSet.match(new RegExp('(^|,)'+row._pkey+'($|,)'))!=null;
                }else{
                    return false;
                }
            }
        }
        return savedAttrs;
    },

    creating_structure: function(attributes, sourceNode) {
        var structBag = sourceNode.getRelativeData(sourceNode.attr.structpath);
        if (structBag) {
            if (genro.grid_configurator && sourceNode.attr.configurable) {
                 sourceNode.setRelativeData('.resource_structs.__baseview__',structBag.deepCopy(),{caption:_T('Base View')});
            }
        
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
        var gridContent = sourceNode.getValue();
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
        if (gridContent instanceof gnr.GnrBag) {
            var gridEditorNode = gridContent.getNodeByAttr('tag', 'grideditor',true);
            if (gridEditorNode) {
                widget.gridEditor = new gnr.GridEditor(widget);
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
            if (genro.isTouchDevice) {
                dojo.connect(widget, 'longTouch', widget, 'openLinkedForm');
            }
        }
        if (sourceNode.attr.loadFormEvent) {
            dojo.connect(widget, sourceNode.attr.loadFormEvent, widget, 'linkedFormLoad');
            if (genro.isTouchDevice) {
                dojo.connect(widget, 'longTouch', widget, 'linkedFormLoad');
            }
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
        sourceNode.subscribe('updatedSelectedRow',function(){
            var selectedIndex = widget.selection.selectedIndex;
            widget.sourceNode.setAttributeInDatasource('selectedId', widget.rowIdByIndex(selectedIndex), null, widget.rowByIndex(selectedIndex), true);
        });
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
                })
                setTimeout(function(){cb.call(widget);},1);
            }
            sourceNode.registerSubscription(searchBoxCode+'_changedValue',widget,function(v,field){
                this.applyFilter(v,null,field);
                genro.dom.setClass(this.domNode,'filteredGrid',v);
                this.updateTotalsCount();
                
            });
            sourceNode.subscribe('command',function(){
                widget[arguments[0]](arguments.slice(1));
            });
        };
        if (widget.filteringGrid){
            var filteringColumn = sourceNode.attr.filteringColumn.replace(/\./g, '_').replace(/@/g, '_');            
            var filteredColumn = filteringColumn;
            if(filteringColumn.indexOf(':')>=0){
                filteringColumn = filteringColumn.split(':');
                filteredColumn = filteringColumn[1];
                filteringColumn = filteringColumn[0];
            }
            var connectFilteringGrid=function(){
                var filteringGrid = widget.filteringGrid.widget || widget.filteringGrid;
                dojo.connect(filteringGrid,'updateRowCount',function(){
                    widget.filterToRebuild(true);widget.updateRowCount('*');
                });
                widget.excludeListCb=function(){
                    return filteringGrid.getColumnValues(filteredColumn);;
                };
                widget.excludeCol=filteringColumn;
            };
            genro.src.afterBuildCalls.push(connectFilteringGrid);
        }
        if(sourceNode.attr.rowCustomClassesCb){
            widget.rowCustomClassesCb = funcCreate(sourceNode.attr.rowCustomClassesCb,'row');
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

    },

    mixin_rowBagNodeByIdentifier:function(identifier){
        return this.storebag().getNodeByAttr(this.rowIdentifier(),pkey);
    },

    mixin_updateTotalsCount: function(countBoxNode){
        var countBoxCode =(this.sourceNode.attr.frameCode || this.sourceNode.attr.nodeId)+'_countbox';
        var countBoxNode = genro.nodeById(countBoxCode);
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
        var cellsbag = widget.structbag().getItem('#0.#0');
        var caption,cellattr,cell_cap,cell_field,fltList,colList,col;
        var cellmap = widget.cellmap;
        cellsbag.forEach(function(n){
            cellattr = n.attr;
            cell_cap = cellattr.name || cellattr.field;
            //cell_field = n.attr.field;
            cell_field = cellmap[n.attr.field.replace(/\W/g, '_')].field_getter;
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
        this.sourceNode.publish('onSelectedRow',{'idx':idx,'selectedId':idx>=0?this.rowIdentity(this.rowByIndex(idx)):null,
                                                'grid':this});
    },

    mixin_indexByRowAttr:function(attrName, attrValue, op,backward) {
        var op = op || '==';
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
        if(scrollTo && typeof(idx)=='number' && idx>=0){
            this.scrollToRow(scrollTo===true?idx:scrollTo);
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
        if(this.selectionStore){
            return this.selectionStore().currentPkeys(caption_field);
        }else{
            var result = [];
            for (var i = 0; i < this.rowCount; i++) {
                result.push(this.rowIdByIndex(i));
            }
            return result;
        }
        
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
            if (cellClassFunc) {
                cellClassFunc(this, v, inRowIndex,renderedRow[cell.field]);
            }
            var cellCustomClass = renderedRow['_customClass_'+cell.field];
            if(cellCustomClass){
                this.customClasses.push(cellCustomClass);
            }
            opt['cellPars'] = {rowIndex:inRowIndex};
            //var zoomPage = opt['zoomPage'];
            if (typeof(v) == 'number' && v < 0) {
                this.customClasses.push('negative_number');
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
                v = template.replace(/#/g, v);
            }
            if (opt['js']) {
                v = opt['js'](v, this.grid.storebag().getNodes()[inRowIndex]);
            }
            var zoomAttr = objectExtract(opt,'zoom_*',true);
            if (objectNotEmpty(zoomAttr)) {
                v = "<a draggable='false' onclick='if(event.shiftKey){dojo.stopEvent(event); genro.dlg.zoomFromCell(event);}' class='gnrzoomcell' href='#'>" + v + "</a>";
            }
            var draggable = this.draggable ? ' draggable=true ' : '';
            return '<div ' + draggable + 'class="cellContent">' + v + '</div>';
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
    
    structFromBag_cell:function(sourceNode,cellNode){
        var rowattrs = objectUpdate({}, cellNode.getParentNode().attr);
        rowattrs = objectExtract(rowattrs, 'classes,headerClasses,cellClasses');
        var cell = objectUpdate({}, rowattrs);
        cell = objectUpdate(cell, cellNode.attr);
        var dtype = cell.dtype;
        cell.original_field = cell.field;
        cell.original_name = cell.name;
        cell._nodelabel = cellNode.label;
        var userSets = objectPop(cell,'userSets');
        if(userSets){
            cellNode.attr['calculated'] = true;
            cell = this.getNewSetKw(sourceNode,cell);
            dtype ='B';
        }

        cell = sourceNode.evaluateOnNode(cell);

        if(sourceNode.attr.draggable_column){
            cell.name = '<div draggable="true">'+cell.name+'</div>';
        }
        if (cell.field) {
            if(cell.field.indexOf(':')>=0 && !cell._customGetter){
                var f = cell.field.split(':');
                cell._customGetter = this.subtableGetter;
                cell._subtable = f[0];
                cell._subfield = f[1];
            }
            if(typeof(cell.values)=='string' && cell.values.indexOf(':')>=0){
                var valuesdict = objectFromString(cell.values);
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
            cell.field = cell.field.replace(/\W/g, '_');
            cell.field_getter = cell.caption_field? cell.caption_field.replace(/\W/g, '_'):cell.field ;
            if(cell.caption_field || cell.values){
                dtype = 'T';
            }
            var checkboxPars = objectPop(cell,'checkBoxColumn');
            if(checkboxPars){
                cell = this.getCheckBoxKw(checkboxPars,sourceNode,cell);
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
            var format = objectExtract(cell, 'format');

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
            if (cell.hidden) {
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
            if(cell.dtype=='B'){
                formats['trueclass']= formats['trueclass'] || "checkboxOn";
                formats['falseclass']= formats['falseclass'] || "checkboxOff";
            }
            if(cell.semaphore){
                formats['trueclass'] = 'greenLight';
                formats['falseclass'] = 'redLight';
            }
            cell.formatter = this.structFromBag_cellFormatter(sourceNode,cell,formats, cellClassCB);
            delete cell.tag;
            return cell;
        }
    },
    structFromBag: function(sourceNode, struct, cellmap) {
        var cellmap = cellmap || {};
        var result = [];
        if (struct) {
            var bagnodes = struct.getNodes();
            var formats, dtype, editor;
            var view, viewnode, rows, rowsnodes, i, k, j, cellsnodes, row, cell, rowattrs, rowBag;
            var editorPars = sourceNode.attr.gridEditor;
            for (var i = 0; i < bagnodes.length; i++) {
                viewnode = bagnodes[i];
                view = objectUpdate({}, viewnode.attr);
                delete view.tag;
                rows = [];
                rowsnodes = viewnode.getValue().getNodes();
                for (k = 0; k < rowsnodes.length; k++) {

                    rowBag = rowsnodes[k].getValue();
                    if (genro.isTouchDevice) {
                        var cellattr = {'format_isbutton':true,'format_buttonclass':'zoomIcon buttonIcon',
                            'format_onclick':'this.widget.openLinkedForm(kw);',
                            'width':'20px','calculated':true,
                            'field':'_edit_record','name':' '};
                        rowBag.setItem('cell_editor', null, cellattr, {doTrigger:false,_position:0});
                    }

                    if (!(rowBag instanceof gnr.GnrBag)) {
                        rowBag = new gnr.GnrBag();
                        rowsnodes[k].setValue(rowBag, false);
                    }


                    if(editorPars && editorPars.statusColumn && dojo.some(rowBag.getNodes(),function(n){return n.attr.edit;})){
                        if(!rowBag.getNode('_rowEditorStatus')){
                            rowBag.setItem('_rowEditorStatus',null,{dtype:'T',width:'2em',
                                                                field:'_rowEditorStatus',
                                                                cellClasses:'rowEditorStatus',
                                                                headerClasses:'rowEditorStatus',
                                                                name:' ',calculated:true,
                                                                _customGetter:function(rowdata,rowIdx){
                                                                    return this.grid.gridEditor.statusColGetter(rowdata,rowIdx);
                                                                }});
                        }
                    }

                    //cellsnodes = rowBag.getNodes();
                    row = [];
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
                    var that = this;
                    rowBag.forEach(function(n){
                        cell = that.structFromBag_cell(sourceNode,n);
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
    mixin_addColumn:function(col, toPos,kw) {
        //if(!('column' in drop_event.dragDropInfo)){ return }
        var colsBag = this.structBag.getItem('#0.#0');
        if(!kw){
            var kw = {'width':'8em','name':col.fullcaption,
            'dtype':col.dtype, 'field':col.fieldpath,
            'tag':'cell'};
            objectUpdate(kw,objectExtract(col,'cell_*'));
            kw['format_pattern'] = col['format'];
            objectUpdate(kw,objectExtract(col,'format_*',null,true));
        }
        
        colsBag.setItem('cellx_' + genro.getCounter(), null, kw, {'_position':toPos + 1});
    },
    onDragStart:function(dragInfo) {
        var dragmode = dragInfo.dragmode;
        var event = dragInfo.event;
        var widget = dragInfo.widget;
        var value = {};

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
                if(widget && dropInfo.row!=null){
                    dropInfo.targetRowData = widget.rowByIndex(dropInfo.row);
                }
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
            console.log(info);
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
            if (attr._is_readonly_row){
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

    },

    created: function(widget, savedAttrs, sourceNode) {
        this.created_common(widget, savedAttrs, sourceNode);
        genro.src.afterBuildCalls.push(dojo.hitch(widget, 'render'));
        dojo.connect(widget, 'onSelected', widget, '_gnrUpdateSelect');
        widget.updateRowCount('*');
    },

    attributes_mixin_get: function(inRowIndex) {
        var rowdata = this.grid.rowCached(inRowIndex);
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
        }else{
            return rowdata[this.field_getter]
        }
        //return this._customGetter ? this._customGetter.call(this, rowdata,inRowIndex) : ;
    },

    mixin_rowCached:function(inRowIndex) {
        if (this.currRenderedRowIndex !== inRowIndex) {
            this.currRenderedRowIndex = inRowIndex;
            this.currRenderedRow = this.rowByIndex(inRowIndex);
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
        return this._filtered =null;
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
    mixin_newDataStore:function(val, kw) {
        this.updateRowCount(0);
        this.resetFilter();
        if(this.excludeCol){
            this.filterToRebuild(true);
        }
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
        this.sourceNode.publish('onNewDatastore');
        this.updateRowCount('*');
        this.restoreSelectedRows();
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
    
    mixin_setStorepath:function(val, kw) {
        if(kw.reason=='initStore'){
            return;
        }
        else if ((!this._updatingIncludedView) && (! this._batchUpdating)) {
            if (kw.evt == 'fired') {
                var storepath = this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
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
                        //if ((storebag == kw.where) && (parent_lv<1)){
                        //}
                    }
                } else if (kw.evt == 'del') {
                    if (parent_lv == 1) {
                        this.updateRowCount();
                        //this.setSelectedIndex(kw.ind); contrario al meccanismo dei dbevent
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
        var customClasses = null;
        if (attr._is_readonly_row){
            row.customClasses = row.customClasses?row.customClasses + ' _gnrReadOnlyRow': '_gnrReadOnlyRow';
        }else if(attr.__protection_tag){
            row.customClasses = row.customClasses?row.customClasses + ' _gnrProtectionPass': '_gnrProtectionPass';
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
            var n = this.storeRowCount();
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
            }
            
            this.updateTotalsCount(); 
            scrollBox.scrollLeft = scrollLeft;
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

    mixin_onSetStructpath: function(structBag) {
        this.query_columns = this.gnr.getQueryColumns(this.sourceNode, structBag);
        if(this.sourceNode._useStore){
            this.setEditableColumns();
        }
        this.setChangeManager();
        if(this.sourceNode._useStore){
            var store = this.collectionStore();
            if(store){
                store.onChangedView();
            }
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
        if (fldName) {
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
        if(r==null){
            var r = this.selection.selectedIndex;
        }
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
        var defaultArgs = (this.gridEditor?this.gridEditor.getNewRowDefaults(defaultArgs) : defaultArgs) || {};
        var newRowDefaults = this.sourceNode.attr.newRowDefaults;
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
        var k = 1;
        var changes = [];
        var serializableChanges = [];
        var that = this;
        var counterField = this.sourceNode.attr.counterField;
        if (!counterField) {
            return;
        }
        if (this.datamode == 'bag' || this.gridEditor) {
            if(this.collectionStore){
                //new gridEditor
                var ge = this.gridEditor;
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
    },
    mixin_absStorepath:function(){
        return this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
    },
    
    mixin_setEditableColumns:function(){
        var cellmap = this.cellmap;
        for(var k in cellmap){
            if(cellmap[k].edit){
                if(!this.gridEditor){
                    this.gridEditor = new gnr.GridEditor(this);
                }
                this.gridEditor.addEditColumn(cellmap[k].field,objectUpdate({},cellmap[k]));
            }else if(this.gridEditor){
                this.gridEditor.delEditColumn(cellmap[k].field);
            }
        }
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
        var formulaColumns = {};
        var cm = this.changeManager;
        if(cm){
            cm.resetCellpars();
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
            if(cell.formula){
                getChangeManager().addFormulaColumn(cellmap[k].field,objectUpdate({},cellmap[k]));
            }else if (this.changeManager){
                this.changeManager.delFormulaColumn(cellmap[k].field);
            }
            if(cell.totalize){
                getChangeManager().addTotalizer(cellmap[k].field,objectUpdate({},cellmap[k]));
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
    mixin_onCheckedColumn:function(idx,fieldname) {
        var structbag = this.sourceNode.getRelativeData(this.sourceNode.attr.structpath);
        var kw = this.cellmap[fieldname];   
        if(kw===true){
            kw = {};
        }
        var rowIndex = this.absIndex(idx);
        var rowpath = '#' + rowIndex;
        var datamodeBag = this.datamode=='bag';
        var sep = datamodeBag? '.':'?';
        var valuepath = rowpath+sep+kw.original_field;
        var storebag = this.storebag();
        var currNode = storebag.getNode(rowpath);
        var checked = storebag.getItem(valuepath);
        var checkedField = kw.checkedField || this.rowIdentifier();
        var checkedRowClass = kw.checkedRowClass;
        var action = kw.action;
        var action_delay = kw.action_delay;
        var sourceNode = this.sourceNode;

        if (currNode.attr.disabled) {
            return;
        }
        if(this.sourceNode.attr.parentForm!==false && this.sourceNode.form && this.sourceNode.form.isDisabled()){
            return;
        }
        var gridId = this.sourceNode.attr.nodeId;
        var newval = !checked;
        if(kw.radioButton){
            if(checked){
                return;
            }
            var currpath;
            for (var i=0; i<storebag.len(); i++){
                currpath = '#'+i+sep+fieldname;
                if(i==rowIndex){
                    storebag.setItem(currpath,true,null,{lazySet:true});
                }else{
                    storebag.setItem(currpath,false,null,{lazySet:true});
                }
            }
        }else{
            storebag.setItem(valuepath, !checked);
        }
        if(kw.checkedId){
            var checkedKeys = this.getCheckedId(fieldname,checkedField) || '';
            setTimeout(function(){
                sourceNode.setRelativeData(kw.checkedId,checkedKeys,null,null,sourceNode);
            },1);
        }
        if (gridId) {
            genro.publish(gridId + '_row_checked', currNode.label, newval, currNode.attr);
        }
        if (action){
            var changedRow = this.rowByIndex(idx);
            var changedKey = changedRow[checkedField];
            var changedValue = changedRow[fieldname];
            var actionKw = {};
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
        kw = this.gnr.getCheckBoxKw(kw, this.sourceNode);
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
                    sourceNode.widget.onCheckedColumn(e.rowIndex,fieldname);
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
        celldata['format_onclick'] = "this.widget.onCheckedColumn(kw.rowIndex,'"+fieldname+"')";
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
        genro.src.afterBuildCalls.push(dojo.hitch(widget, 'render'));
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
    mixin_addRows:function(counter,evt){
        var lenrows = this.storebag().len();
        var r = this.selection.selectedIndex;
        if(r>=0 && lenrows>0){
            r = r+1;
        }else{
            r = lenrows;
        }
        for(var i=0;i<counter;i++){
            this.addBagRow('#id', '*', this.newBagRow(),evt);
        }
        this.editBagRow(r);
        this.sourceNode.publish('onAddedRows');
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
    mixin_rowByIndex:function(inRowIndex){
        return this.collectionStore().rowByIndex(inRowIndex);
    },
    mixin_absIndex:function(idx,reverse){
         return this.collectionStore().absIndex(idx,reverse);
    },
    mixin_rowFromBagNode:function(node) {
        return this.collectionStore().rowFromItem(node);
    },
    mixin_rowBagNodeByIdentifier:function(identifier){
        return this.collectionStore().rowBagNodeByIdentifier(identifier);
    },


    mixin_rowIdByIndex:function(inRowIndex){
        if(inRowIndex!==null){
            return this.rowIdentity(this.rowByIndex(inRowIndex));
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
    
    mixin_indexByCb:function(cb, backward) {
        return this.collectionStore().indexByCb(cb, backward);
    },

    mixin_storeRowCount: function(all) {
        return this.collectionStore().len(!all);
    },
   // mixin_storebag:function(){
   //     return this.collectionStore().getData();
   // },
    mixin_addNewSetColumn:function(kw) {
        this.gnr.addNewSetColumn(this.sourceNode,kw);;
    },

    addNewSetColumn:function(sourceNode,kw) {
        var position = objectPop(kw,'position') || 0;
        var celldata = this.getNewSetKw(sourceNode,kw);
        var structbag = sourceNode.getRelativeData(sourceNode.attr.structpath);
        genro.callAfter(function(){
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

        var checkedField = '_pkey';
        celldata['checkedField'] = checkedField;
        celldata['userSets'] = true;    
        celldata['format_onclick'] = "this.widget.onChangeSetCol(kw.rowIndex,'"+fieldname+"',e)";
        celldata['_customGetter'] = function(rowdata,rowIdx){
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
        var sortedBy;
        if(this._virtual){
            sortedBy = cell.field_getter + ':' + order;
        }else{
            if (this.datamode == 'bag') {
                sortedBy = cell.field_getter + ':' + order;
            } else {
                sortedBy = '#a.' + cell.field_getter + ':' + order;
            }
        }
        if ((cell.dtype == 'A') || ( cell.dtype == 'T')) {
            sortedBy = sortedBy + '*';
        }
        this.sourceNode.publish('setSortedBy',sortedBy);
        //this.setSortedBy(sortedBy);

        //else {
        //    var path = this.sourceNode.attrDatapath('sortedBy');
        //    genro._data.setItem(path, sortedBy);
        //}        
    },
        
    mixin_setSortedBy:function(sortedBy) {
        this.sortedBy = sortedBy;
        var store = this.collectionStore();
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
                    },500);
            }, true);
            }
            
            
        }
        if(this.sortedBy){
            this._collectionStore.sortedBy = this.sortedBy;
        }
        return this._collectionStore;
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
            this.collectionStore().deleteAsk(pkeys,protectPkeys);
        }
    },
    
    mixin_filterToRebuild: function(value) {
        return this.collectionStore().filterToRebuild(value);
    },
    mixin_invalidFilter: function() {
        return this.collectionStore().invalidFilter();
    },
    mixin_resetFilter: function(value) {
        return this.collectionStore().resetFilter();
    },
    mixin_currentData:function(nodes, rawData){
        var nodes = nodes || (this.getSelectedRowidx().length<1?'all':'selected');
        var result = new gnr.GnrBag();
        var nodes;
        if (rawData===true){
            if(nodes=='all'){
                nodes = this.collectionStore().getData().getNodes();
            }else if(nodes=='selected'){
                nodes = this.getSelectedNodes();
            }
            dojo.forEach(nodes,function(n){result.setItem(n.label,n);});
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
                    result.setItem('r_'+curr_row, null, cell_attrs);
                    cell_attrs = {};
                    curr_row += 1;
                }
            }


        }
        
        return result;
    },
    mixin_serverAction:function(kw){
        var options = objectPop(kw,'opt');
        var method = objectPop(options,"method") || "app.includedViewAction";
        var kwargs = objectUpdate({},options);
        kwargs['action'] = objectPop(kw,'command');
        var sourceNode = this.sourceNode;
        genro.lockScreen(true,sourceNode.getStringId());
        if (this.collectionStore().storeType=='VirtualSelection'){
            kwargs['selectionName'] = this.collectionStore().selectionName;
            kwargs['selectedRowidx'] = this.getSelectedRowidx();
        }else{
            kwargs['data'] = this.currentData(null, options['rawData']===true);
        }
        kwargs['table'] =this.sourceNode.attr.table;
        kwargs['datamode'] = this.datamode;
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
        cells._nodes.forEach(function(n){
            if(!n.attr.hidden){
                return;
            }
            if(n.attr.hidden==true || sourceNode.getRelativeData(n.attr.hidden)){
                cells.popNode(n.label);
                return;
            }
        });
        return struct;
    }


});



dojo.declare("gnr.widgets.BaseCombo", gnr.widgets.baseDojo, {
    creating: function(attributes, sourceNode) {
        objectExtract(attributes, 'maxLength,_type');
        var values = objectPop(attributes, 'values');
        var val,xval;
        if (values) {
            var store = this.storeFromValues(values);
            attributes.searchAttr = 'caption';
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
    mixin_onSpeechEnd:function(){
        this._startSearchFromInput();
    },
    storeFromValues:function(values){
        var localStore = new gnr.GnrBag();
        if(!values){
            values = [];
        }else{
            var ch = values.indexOf('\n')>=0?'\n':',';
            values = values.split(ch);  
        }
        for (var i = 0; i < values.length; i++) {
            val = values[i];
            xval = {};
            if (val.indexOf(':') > 0) {
                val = val.split(':');
                xval['id'] = val[0];
                xval['caption'] = val[1];
            } else {
                xval['id'] = val;
                xval['caption'] = val;
            }
            localStore.setItem('root.r_' + i, null, xval);
        }
        var newstore = new gnr.GnrStoreBag({mainbag:localStore});
        newstore._identifier = 'id';
        return newstore;
    },
    mixin_setValues:function(values){
        this.store =  this.gnr.storeFromValues(values);
    },
    
  // patch__onBlur: function(){
  //     this._hideResultList();
  //     this._arrowIdle();
  //     this.inherited(arguments);
  //  },

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
        var row = item ? (item.attr || {}) : {};
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
            if(this.sourceNode._selectedSetter){
                this.sourceNode._selectedSetter(path, val);
            }
            else{
                this.sourceNode.setRelativeData(path, val, null, false, 'selected_');
            }
        }
        if(this.sourceNode._selectedCb){
            this.sourceNode._selectedCb(item);
        }
    },
    connectForUpdate: function(widget, sourceNode) {
        var selattr = objectExtract(widget.sourceNode.attr, 'selected_*', true);
        if (objectNotEmpty(selattr) || sourceNode.attr.selectedCaption) {
            dojo.connect(widget, '_doSelect', widget, function() {
                this._updateSelect(this.item);
            });
        }
    },
    doChangeInData:function(sourceNode, value, valueAttr){
        var displayedValue = sourceNode.widget.getDisplayedValue();
        if(value!=displayedValue){
            valueAttr['_displayedValue'] = displayedValue;
        }       
    },

    patch_displayMessage:function(message){
        if(!isNullOrBlank(this.value)){
            this.displayMessage_replaced(message);
        }
    }
});

dojo.declare("gnr.widgets.GeoCoderField", gnr.widgets.BaseCombo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'ComboBox';
    },
    creating: function(attributes, sourceNode) {
        objectExtract(attributes, 'maxLength,_type,country');
        if (sourceNode.attr._virtual_column){
            attributes.value = '^.$'+sourceNode.attr._virtual_column;
            sourceNode.attr.value= attributes.value;
            attributes.readOnly=false;
        }
        var savedAttrs = {};
        var localStore = new gnr.GnrBag();
        var store = new gnr.GnrStoreBag({mainbag:localStore});
        attributes.searchAttr = 'caption';
        attributes.hasDownArrow =false;
        store._identifier = 'id';
        attributes.store = store;
        return savedAttrs;
    },
    mixin_onSpeechEnd:function(){
        this.geocodevalue();
    },
    mixin_geocodevalue:function(){
        var address = this.textbox.value;
        if (address == this.geocoder.resultAddress && address.length == 1){
            return;
        }
        clearTimeout(this.waitingDelay);
        this.waitingDelay = setTimeout(dojo.hitch(this,
            function(){
                var geopars={ 'address': address}
                if (this.sourceNode.attr.country){
                    var country=this.sourceNode.getAttributeFromDatasource('country')
                    if(country){
                        geopars['componentRestrictions']={'country':country}
                    }
                    
                }
              this.geocoder.geocode(geopars, dojo.hitch(this, 'handleGeocodeResults'));
            }),200);
        
    },
    patch__onKeyPress: function(/*Event*/ evt){
        // summary: handles keyboard events

        //except for pasting case - ctrl + v(118)
        if(evt.altKey || (evt.ctrlKey && evt.charCode != 118)){
            return;
        }
        var doSearch = false;
        var pw = this._popupWidget;
        var dk = dojo.keys;
        if(this._isShowingNow){
            pw.handleKey(evt);
        }
        switch(evt.keyCode){
            case dk.PAGE_DOWN:
            case dk.DOWN_ARROW:
                if(!this._isShowingNow||this._prev_key_esc){
                    this._arrowPressed();
                    doSearch=true;
                }else{
                    this._announceOption(pw.getHighlightedOption());
                }
                dojo.stopEvent(evt);
                this._prev_key_backspace = false;
                this._prev_key_esc = false;
                break;

            case dk.PAGE_UP:
            case dk.UP_ARROW:
                if(this._isShowingNow){
                    this._announceOption(pw.getHighlightedOption());
                }
                dojo.stopEvent(evt);
                this._prev_key_backspace = false;
                this._prev_key_esc = false;
                break;

            case dk.ENTER:
                // prevent submitting form if user presses enter. Also
                // prevent accepting the value if either Next or Previous
                // are selected
                var highlighted;
                if( this._isShowingNow && 
                    (highlighted = pw.getHighlightedOption())
                ){
                    // only stop event on prev/next
                    if(highlighted == pw.nextButton){
                        this._nextSearch(1);
                        dojo.stopEvent(evt);
                        break;
                    }else if(highlighted == pw.previousButton){
                        this._nextSearch(-1);
                        dojo.stopEvent(evt);
                        break;
                    }
                }else{
                    this.setDisplayedValue(this.getDisplayedValue());
                }
                // default case:
                // prevent submit, but allow event to bubble
                evt.preventDefault();
                // fall through

            case dk.TAB:
                var newvalue = this.getDisplayedValue();
                // #4617: 
                //      if the user had More Choices selected fall into the
                //      _onBlur handler
                if(pw && (
                    newvalue == pw._messages["previousMessage"] ||
                    newvalue == pw._messages["nextMessage"])
                ){
                    break;
                }
                if(this._isShowingNow){
                    this._prev_key_backspace = false;
                    this._prev_key_esc = false;
                    if(pw.getHighlightedOption()){
                        pw.setValue({ target: pw.getHighlightedOption() }, true);
                    }
                    this._hideResultList();
                }
                break;

            case dk.SPACE:
                this._prev_key_backspace = false;
                this._prev_key_esc = false;
                if(this._isShowingNow && pw.getHighlightedOption()){
                    dojo.stopEvent(evt);
                    this._selectOption();
                    this._hideResultList();
                }else{
                    doSearch = true;
                }
                break;

            case dk.ESCAPE:
                this._prev_key_backspace = false;
                this._prev_key_esc = true;
                if(this._isShowingNow){
                    dojo.stopEvent(evt);
                    this._hideResultList();
                }
                this.inherited(arguments);
                break;

            case dk.DELETE:
            case dk.BACKSPACE:
                this._prev_key_esc = false;
                this._prev_key_backspace = true;
                doSearch = true;
                break;

            case dk.RIGHT_ARROW: // fall through
            case dk.LEFT_ARROW: 
                this._prev_key_backspace = false;
                this._prev_key_esc = false;
                break;

            default: // non char keys (F1-F12 etc..)  shouldn't open list
                this._prev_key_backspace = false;
                this._prev_key_esc = false;
                if(dojo.isIE || evt.charCode != 0){
                    doSearch = true;
                }
        }
        if(this.searchTimer){
            clearTimeout(this.searchTimer);
        }
        if(doSearch){
            // need to wait a tad before start search so that the event
            // bubbles through DOM and we have value visible
            setTimeout(dojo.hitch(this, "geocodevalue"),1);
        }
    },
    patch__onBlur: function(){
        if (this._popupWidget && !this.item){
            this._popupWidget.highlightFirstOption();
            var highlighted = this._popupWidget.getHighlightedOption();
            //if (highlighted.item){
                this._popupWidget.setValue({ target: highlighted.item?highlighted.item:null }, true);
            //}
        }
        this.store.mainbag=new gnr.GnrBag();
    },
    created: function(widget, savedAttrs, sourceNode){
        var tag = 'cls_' + sourceNode.attr.tag;
        dojo.addClass(widget.domNode.childNodes[0], tag);
        this.connectForUpdate(widget, sourceNode);
        if (dojo_version == '1.1') {
            if (dojo.isSafari) {
                dojo.connect(widget.focusNode, 'onkeydown', widget, '_onKeyPress');
            }
        }
        genro.google().setGeocoder(widget);
    },
    mixin_handleGeocodeResults: function(results, status){
        this.store.mainbag=new gnr.GnrBag();
         if (status == google.maps.GeocoderStatus.OK) {
             for (var i = 0; i < results.length; i++){
                 formatted_address=results[i].formatted_address;
                 var details = {id:i,caption:formatted_address,formatted_address:formatted_address};
                 var address_components=results[i].address_components;
                 for (var a in address_components){
                     var address_component=address_components[a];
                     details[address_component.types[0]]=address_component.short_name;
                     details[address_component.types[0]+'_long']=address_component.long_name;
                 }
                 
                 details['street_address'] = details['route_long']+', '+(details['street_number']||'??');
                 details['street_address_eng'] = (details['street_number']||'??')+' '+details['route_long'];
                 var position=results[i].geometry.location;
                 details['position']=position.lat()+','+position.lng();
             this.store.mainbag.setItem('root.r_' + i, null, details);

             }
         }else if (status == google.maps.GeocoderStatus.ZERO_RESULTS){
             this._updateSelect(this.store.mainbag);
         };
         var firstline = this.store.mainbag.getItem('#0');
         if (false && firstline && firstline.len()==1){
             this.setValue(this.store.mainbag.getItem('#0.#0?caption'),true);
             this._updateSelect(this.store.mainbag.getNode('#0.#0'));
         }
         else{
             this._startSearch("");
         }
        this.searchOnBlur=false;
     }

});

dojo.declare("gnr.widgets.dbBaseCombo", gnr.widgets.BaseCombo, {
    creating: function(attributes, sourceNode) {
        var savedAttrs = {};
        var hasDownArrow;
        if (attributes.hasDownArrow) {
            attributes.limit = attributes.limit || 0;
        } else {
            attributes.hasDownArrow = false;
        }
        if(attributes.readOnly){
            attributes.hasDownArrow = false;
            attributes['tabindex'] = -1;
        }
        var resolverAttrs = objectExtract(attributes, 'method,dbtable,columns,limit,alternatePkey,auxColumns,hiddenColumns,rowcaption,order_by,selectmethod,weakCondition,excludeDraft,preferred');
        if('_storename' in sourceNode.attr){
            resolverAttrs._storename = sourceNode.attr._storename;
        }
        var selectedColumns = objectExtract(attributes, 'selected_*');
        var selectedCb = objectPop(attributes,'selectedCb');
        if(selectedCb){
            sourceNode._selectedCb = funcCreate(selectedCb,'item',sourceNode);
        }
        var selectedSetter = objectPop(attributes,'selectedSetter');
        if(selectedSetter){
            sourceNode._selectedSetter = funcCreate(selectedSetter,'path,value',sourceNode);
        }
        if (objectNotEmpty(selectedColumns)) {
            var hiddenColumns;
            if ('hiddenColumns' in resolverAttrs) {
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
        resolverAttrs['notnull'] = attributes['validate_notnull'];
        savedAttrs['dbtable'] = resolverAttrs['dbtable'];
        savedAttrs['auxColumns'] = resolverAttrs['auxColumns'];
        var storeAttrs = objectExtract(attributes, 'store_*');
        objectExtract(attributes, 'condition_*');
        resolverAttrs['condition'] = sourceNode.attr.condition;
        objectUpdate(resolverAttrs, objectExtract(sourceNode.attr, 'condition_*', true));
        resolverAttrs['exclude'] = sourceNode.attr['exclude']; // from sourceNode.attr because ^ has to be resolved at runtime
        resolverAttrs._id = '';
        resolverAttrs._querystring = '';

        var store;
        savedAttrs['record'] = objectPop(storeAttrs, 'record');
        attributes.searchAttr = storeAttrs['caption'] || 'caption';
        store = new gnr.GnrStoreQuery({'searchAttr':attributes.searchAttr,_parentSourceNode:sourceNode});

        store._identifier = resolverAttrs['alternatePkey'] || storeAttrs['id'] || '_pkey';

        sourceNode.registerSubscription('changeInTable',sourceNode,function(kw){
            if(this.attr.dbtable==kw.table){
                this.widget.clearCache(kw.pkey);
            }
        });



        //store._parentSourceNode = sourceNode;
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
        savedAttrs['connectedArrowMenu'] = sourceNode.attr.connectedMenu;
        savedAttrs['connectedMenu'] = null

        return savedAttrs;
    },
    
    versionpatch_11__onArrowMouseDown:function(e){
        if(this._downArrowMenu){
            dojo.stopEvent(e);
        }else{
            this._onArrowMouseDown_replaced(e);
        }
    },
    mixin_setDbtable:function(value) {
        this.store.rootDataNode()._resolver.kwargs.dbtable = value;
    },
    mixin_clearCache:function(pkey){
        this.store.clearCache(pkey);
    },
    mixin_setCondition:function(value,kw){
        var vpath = this.sourceNode.attr.value;
        var currvalue = this.sourceNode.getRelativeData(vpath);
        //this.sourceNode.setRelativeData(vpath,null,null,null,false);
        if(!isNullOrBlank(currvalue)){
            this.setValue(null,true);
            this.setValue(currvalue,true);
        }
        //this.sourceNode.setRelativeData(vpath,currvalue);
    },
    
    mixin_onSetValueFromItem: function(item, priorityChange) {
        if (!item.attr.caption) {
            return;
        }
        if (this.sourceNode.editedRowIndex!=null && priorityChange) {
            this._updateSelect(item);
            if (priorityChange) {
                //this.cellNext = 'RIGHT';
                //this.onBlur();
            }
        }
        else {
            if (priorityChange) {
                this._updateSelect(item);
            }else{
                //console.log('no updateselect (!priorityChange)',item)
            }
        }
    },
    connectForUpdate: function(widget, sourceNode) {
        return;
    },
    onDataChanged:function(widget){
       // widget.focusNode.blur()
    },
    created: function(widget, savedAttrs, sourceNode) {
        if (savedAttrs.auxColumns) {
            widget._popupWidget = new gnr.Gnr_ComboBoxMenu({onChange: dojo.hitch(widget, widget._selectOption)});
            dojo.connect(widget,'open',function(){
                var popup = this._popupWidget.domNode.parentNode;
                var popupcoords = dojo.coords(popup);
                var bodycoords = dojo.coords(dojo.body());
                var popupDeltaOverflow = (popupcoords.x+popupcoords.w) -bodycoords.w +10;
                if(popupDeltaOverflow>0){
                    popup.style.left = (parseInt(popup.style.left)-popupDeltaOverflow)+'px';
                }
            });
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
        if(savedAttrs.connectedArrowMenu && widget.downArrowNode){
            var connectedMenu = savedAttrs.connectedArrowMenu; 
            genro.src.onBuiltCall(function(){
                var menu = dijit.byId(connectedMenu);
                if(menu){
                    menu.bindDomNode(widget.downArrowNode);
                    widget._downArrowMenu = true;
                }
            });
            
            
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
    patch_setValue: function(/*String*/ value, /*Boolean?*/ priorityChange){
        // summary
        //  Sets the value of the select.
        //  Also sets the label to the corresponding value by reverse lookup.

        //#3347: fetchItemByIdentity if no keyAttr specified
        var self=this;
        var handleFetchByIdentity = function(item, priorityChange){
            if(!isNullOrBlank(item)){
                if(self.store.isItemLoaded(item)){
                    self._callbackSetLabel([item], undefined, priorityChange);
                }else{
                    self.store.loadItem({
                        item: item, 
                        onItem: function(result, dataObject){
                            self._callbackSetLabel(result, dataObject, priorityChange);
                        }
                    });
                }
            }else{
                //self._isvalid=false;
                //self.validate(false);
                self.valueNode.value = null;
                self.setDisplayedValue('')
            }

        };
        this.store.fetchItemByIdentity({
            identity: value, 
            onItem: function(item){
                handleFetchByIdentity(item, priorityChange);

            }
        });
    },

   //patch__setValueFromItem: function(/*item*/ item, /*Boolean?*/ priorityChange){
   //    //  summary:
   //    //      Set the displayed valued in the input box, based on a
   //    //      selected item.
   //    //  description:
   //    //      Users shouldn't call this function; they should be calling
   //    //      setDisplayedValue() instead
   //    this._isvalid=true;
   //    this._setValue( this.store.getIdentity(item), 
   //                    this.labelFunc(item, this.store), 
   //                    priorityChange);
   //}

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
    },
    versionpatch_11__setBlurValue : function(){
            // if the user clicks away from the textbox OR tabs away, set the
            // value to the textbox value
            // #4617:
            // if value is now more choices or previous choices, revert
            // the value
            //console.log('SET BLUR VALUE')
            var displayedValue=this.getDisplayedValue();
            var lastValueReported=this._lastValueReported;
            var value;
            if(this._lastDisplayedValue==displayedValue){
                value=this.getValue();
            }
            var pw = this._popupWidget;
            if(pw && (
                displayedValue == pw._messages["previousMessage"] ||
                displayedValue == pw._messages["nextMessage"]
                )
            ){
                this.setValue(this._lastValueReported, true);
            }else{
                if (isNullOrBlank(displayedValue)){
                     this.setValue(null, true);
                     this.setDisplayedValue('');
                }else{
                    if ( isNullOrBlank(value)){
                        this.setValue(null, true);
                        if(!this.sourceNode.attr.firstMatchDisabled){
                            this.setDisplayedValue(displayedValue,true);
                        }
                    }else //if(value!=lastValueReported){
                        {
                        this.setValue(value, true);
                    }
                }
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
            dojo.connect(widget,'setValue',function(kw,priorityChange){
                if(priorityChange){
                    var item = this.item || {attr:{}};
                    this._updateSelect(item);
                }
            })
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
        var openKw = {
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
        };
        dijit.popup.open(openKw);
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
        var hasChildrenCb = objectPop(attributes, 'hasChildrenCb');
        if (hasChildrenCb){
            hasChildrenCb = funcCreate(hasChildrenCb);
        }

        if (labelCb) {
            labelCb = funcCreate(labelCb);
        }
        var store = new gnr.GnrStoreBag({datapath:storepath,_identifier:_identifier,
            hideValues:hideValues,
            labelAttribute:labelAttribute,
            labelCb:labelCb,
            hasChildrenCb:hasChildrenCb,
            sourceNode:sourceNode
            });
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
            if(attributes.checkedPaths){
                sourceNode.registerDynAttr('checkedPaths');
            }

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
        var nodeId = sourceNode.attr.nodeId;
        if(nodeId){
            var searchBoxCode = (sourceNode.attr.frameCode || nodeId)+'_searchbox';
            var searchBoxNode = genro.nodeById(searchBoxCode);
            if (searchBoxNode){
                sourceNode.registerSubscription(searchBoxCode+'_changedValue',widget,function(v,field){
                    this.applyFilter(v);
                });
            }
            var editBagBoxNode = genro.nodeById(nodeId+'_editbagbox_grid');
            if (editBagBoxNode){
                dojo.connect(widget,'_updateSelect',function(item,node){
                    if(!(item instanceof gnr.GnrBagNode)){
                        if(item===null){
                            return;
                        }
                        item = node.getParent().item;
                    }
                    genro.publish(nodeId+'_editbagbox_editnode',item);
                });
            }
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
        var caption = dragInfo.treenode.label;
        var result = {};
        
        result['text/plain'] = dragInfo.treenode.label;
        result['text/xml'] = dragInfo.treenode.label;

        result['nodeattr'] = item.attr;
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
                var checked = ('checked' in node.attr) ? (node.attr.checked || false) : -1;
                ck = (ck == null) ? checked : (ck != checked) ? -1 : ck;
            }, 'static');
        }
        return ck;
    },

    mixin_collapseAll:function(curr){
        var curr = curr || this.rootNode;
        var tree = this;
        dojo.forEach(curr.getChildren(), function(n) {
            if (n.isExpanded) {
                tree.collapseAll(n);
                tree._collapseNode(n);
            }
        });
    },

    mixin_applyFilter:function(search){
        var treeNodes=dojo.query('.dijitTreeNode',this.domNode);
        treeNodes.removeClass('hidden');
        if (!search){return;}
        var searchmode=null;
        if (search.indexOf('#')==0){
            var k=search.indexOf('=');
            if ((k<0 )||(k==(search.length-1))){
                return;
            }
            search=search.split('=');
            searchmode=search[0];
            search=search[1];
        }
        var _this=this;
        cb_match=function(n){
            if (!searchmode){
                var label=_this.getLabel(n);
                return (label.toLowerCase().indexOf(search)>=0);
            }else if(searchmode=='#'){
                console.log('ss');
            }else {
                var label=n.attr[searchmode.slice(1)]+'';
                if (label){
                    return (label.toLowerCase().indexOf(search)>=0);
                }
            }
            
        };
        var root=this.model.store.rootData();
        cb=function(n){
            if (cb_match(n)){
                var fullpath=n.getFullpath(null,root);
                _this.showNodeAtPath(fullpath);
            }
        };
        root.walk(cb,'static');
        treeNodes.addClass('hidden');
        treeNodes.forEach(function(n){
            var tn = dijit.getEnclosingWidget(n);
            var parent=tn.getParent();
            if((!parent) || cb_match(tn.item)){
                dojo.removeClass(tn.domNode,'hidden');
                while(parent&&dojo.hasClass(parent.domNode,'hidden')){
                    dojo.removeClass(parent.domNode,'hidden');
                    parent=parent.getParent();
                }
                
            };
        });
        
    },

    mixin_updateLabels:function(){
        var n;
        for (var k in this._itemNodeMap){
            n = this._itemNodeMap[k];
            if(n){
                n.setLabelNode(this.getLabel(n.item));
            }
        }
    },

    mixin_storebag:function(){
        return this.sourceNode.getRelativeData(this.sourceNode.attr.storepath);
    },

    mixin_clickOnCheckbox:function(bagnode, e) {
        var checked = bagnode.attr.checked ? false : true;
        var walkmode = this.sourceNode.attr.eagerCheck ? null : 'static';
        var updBranchCheckedStatus = function(bag) {
            bag.forEach(function(n) {
                var v = n.getValue(walkmode);
                if ((v instanceof gnr.GnrBag) && v.len()) {
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
            if ((value instanceof gnr.GnrBag) && this.sourceNode.attr.checkChildren!==false) {
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
        var checked_attr = objectExtract(this.sourceNode.attr,'checked_*',true)
      	var checked_attr_joiners = {};
      	var p;
      	for (var k in checked_attr){
      		p = checked_attr[k];
      		if(p.indexOf(':')>=0){
      			p = p.split(':');
      			checked_attr[k] = p[0]
      			checked_attr_joiners[k] = p[1];
      		}
      	}
        var checkedPaths = this.sourceNode.attr.checkedPaths;
        if(objectNotEmpty(checked_attr) || checkedPaths){
            this.updateCheckedAttr(checked_attr,checkedPaths,checked_attr_joiners)
        }
    },
    
    mixin_updateCheckedAttr:function(checked_attr,checkedPaths,checked_attr_joiners){
        var propagate = this.sourceNode.attr.checkChildren!==false;
        var walkmode = this.sourceNode.attr.eagerCheck ? null : 'static';
        var store = this.sourceNode.getRelativeData(this.sourceNode.attr.storepath);
        var result = {};
        var cp = [];
        var p;
        for(var k in checked_attr){
            result[k] = [];
        }

        store.walk(function(n){
            var v = n.getValue(walkmode);
            if(propagate && (v instanceof gnr.GnrBag )&& (v.len()>0)){
                return;
            }else if(n.attr.checked===true){
                for(var k in checked_attr){
                    var av = n.attr[k];
                    if(result[k].indexOf(av)<0){
                        result[k].push(av)
                    }
                    if(checkedPaths){
                        p = n.getFullpath('static',store);
                        if(cp.indexOf(p)<0){
                            cp.push(p);
                        }
                    }
                }
            }
        },walkmode);
        for(var k in checked_attr){
            this.sourceNode.setRelativeData(checked_attr[k],result[k].join(checked_attr_joiners[k] || ','))
        }
        if(checkedPaths){
            this.sourceNode.setRelativeData(checkedPaths,cp.join(','),null,null,this);
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
       //if (nodeWidget.htmlLabel && (!dojo.hasClass(e.target, 'dijitTreeExpando'))) {
       //    return;
       //}
        if (nodeWidget == nodeWidget.tree.rootNode) {
            return;
        }
        nodeWidget.__eventmodifier = eventToString(e);
        this._onClick_replaced(e);
        if (genro.wdg.filterEvent(e, '*', 'dijitTreeLabel,dijitTreeContent')) {
            this.setSelected(nodeWidget);
        }
    },
    versionpatch_15__onClick:function(nodeWidget, e) {
        // summary:
        //      Translates click events into commands for the controller to process
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
        }
    },
    mixin_getItemById: function(id) {
        return this.model.store.rootData().findNodeById(id);
    },
    mixin_saveExpanded:function(){
        var that = this;
        this._savedExpandedStatus = dojo.query('.dijitTreeContentExpanded',that.domNode).map(function(n){
                                            return that.model.store.getIdentity(dijit.getEnclosingWidget(n).item);});
    },
    
    mixin_restoreExpanded:function(){
        if (this._savedExpandedStatus){
            var that = this;
            dojo.forEach(this._savedExpandedStatus,function(n){
                if(n){
                    var tn = that._itemNodeMap[n];
                    if(tn){
                        that._expandNode(tn);
                    }
                }
            });
        }
    },

    attributes_mixin__saveState: function() {
        return;
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
    attributes_mixin_loadState:function(val, kw) {
        //var cookie = dojo.cookie(this.cookieName);
        this._openedItemIds = {};
        /*if (cookie) {
            dojo.forEach(cookie.split(','), function(item) {
                this._openedItemIds[item] = true;
            }, this);
        }*/
    },
    mixin_setStorepath:function(val, kw) {
        //genro.debug('trigger_store:'+kw.evt+' at '+kw.pathlist.join('.'));
        var storeAbsPath = this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
        var eventPath = kw.pathlist.join('.').slice(5);
        if (kw.evt == 'upd') {
            if (kw.updvalue) {
                if (kw.value instanceof gnr.GnrBag) {
                    if(storeAbsPath.indexOf(eventPath)==0){
                        this.sourceNode.rebuild();
                    }else{
                        this._onItemChildrenChange(/*dojo.data.Item*/ kw.node, /*dojo.data.Item[]*/ kw.value.getNodes());
                    }
                } else {
                    this._onItemChange({id:kw.node._id + 'c',label:kw.value});
                }
            } else if (kw.updattr) {
                this._onItemChange(kw.node);
            }
            //this.model.store._triggerUpd(kw);
        } else if (kw.evt == 'ins') {
            if(undefined in this._itemNodeMap && objectSize(this._itemNodeMap)==1){
                this.sourceNode.rebuild();
            }else{
                this.model.store._triggerIns(kw);
            }
            
        } else if (kw.evt == 'del') {
            this._onItemChildrenChange(/*dojo.data.Item*/ kw.where.getParentNode(), /*dojo.data.Item[]*/ kw.where.getNodes());
            //this.model.store._triggerDel(kw);
        }
    },
    
    patch__onItemChildrenChange:function(n,nodes){
        var that = this;
        var identifier;
        dojo.forEach(nodes,function(n){
            identifier = that.model.store.getIdentity(n);
            objectPop(that._itemNodeMap,identifier);
        });
        this._onItemChildrenChange_replaced(n,nodes);
    },

    mixin_setCheckedPaths:function(path,kw){
        if (kw.reason == this || kw.reason=='autocreate') {
            return;
        }
        var store = this.sourceNode.getRelativeData(this.sourceNode.attr.storepath);
        store.walk(function(n){
            n.setAttr({'checked':false}, true, true);
        },'static')
        var paths = this.sourceNode.getRelativeData(this.sourceNode.attr.checkedPaths);
        if(!paths){
            return;
        }
        paths = paths.split(',');
        var that = this;
        var treeNode;
        paths.forEach(function(path){
            var n = store.getNode(path);
            if(n){
                that.clickOnCheckbox(n);
            }
        });
    },

    mixin_setSelectedPath:function(path, kw) {
        if (kw.reason == this) {
            return;
        }
        var curr = this.model.store.rootData();
        var currNode,treeNode;
        if (!kw.value) {
            this.setSelected(null);
            return;
        }
        var pathList = kw.value.split('.');
        for (var i = 0; i < pathList.length; i++) {
            if(!curr){
                return;
            }
            if(!(curr instanceof gnr.GnrBag)){
                console.warn('TREE setSelectedPath warn curr is not a bag',curr);
                //genro.dev.addError('TREE setSelectedPath warn curr is not a bag','warn',true);
                return;
            }
            currNode = curr.getNode(pathList[i]);
            if(!currNode){
                return;
            }
            var identity = this.model.store.getIdentity(currNode);
            treeNode = this._itemNodeMap[identity];
            if (i < pathList.length - 1) {
                if (!treeNode.isExpanded) {
                    this._expandNode(treeNode);
                }
            }
            curr = currNode.getValue();
        }
        var currTree = this;
        setTimeout(function() {
            currTree.focusNode(treeNode);
            currTree.setSelected(treeNode);
            if(kw.expand){
                currTree._expandNode(treeNode);
            }
        }, 100);
    },
     mixin_showNodeAtPath:function(path) {
         var curr = this.model.store.rootData();
         var pathList = path.split('.');
         for (var i = 0; i < pathList.length; i++) {
            var currNode = curr.getNode(pathList[i]);
            if (!currNode){
                return;
            }
            var identity = this.model.store.getIdentity(currNode);
            var treeNode = this._itemNodeMap[identity];
            curr = currNode.getValue('static');
            if (i < pathList.length - 1) {
                if (!treeNode.isExpanded) {
                    this._expandNode(treeNode);
                };
            }
        }
     },
    mixin_setSelected:function(node) {
        if(node){
            if(node.item.attr._isSelectable===false || (this.sourceNode.attr.openOnClick===true && node.item.attr.child_count)){
                return;
            }
            
        }
        var prevSelectedNode = this.currentSelectedNode;
        this.currentSelectedNode = node;
        if (prevSelectedNode) {
            prevSelectedNode._updateItemClasses(prevSelectedNode.item);
        }
        if (node) {
            node._updateItemClasses(node.item);
            this._updateSelect(node.item, node);
        }
        
    },
    mixin_isSelectedItem:function(item) {
        return this.currentSelectedNode ? this.currentSelectedNode.item == item : false;
    },

    mixin_getContainingtMenu:function(){
        return this.sourceNode.attributeOwnerNode('tag','menu',true);
    },

    mixin__updateSelect: function(item, node) {
        var modifiers = objectPop(node, '__eventmodifier');
        var reason = this;
        var attributes = {};
        var setterNode = this.sourceNode;
        var countainingMenu = this.getContainingtMenu();
        if(countainingMenu){
            var targetWdg = dijit.getEnclosingWidget(countainingMenu.widget.originalContextTarget);
            setterNode = targetWdg? targetWdg.sourceNode:setterNode;
        }
        if (modifiers) {
            attributes._modifiers = modifiers;
        }
        if (!item) {
            var item = new gnr.GnrBagNode();
        }
        else if (!item._id) {
            item = node.getParent().item;
        }
        var root = this.model.store.rootData();
        var itemFullPath = item.getFullpath(null, root);
        if (this.sourceNode.attr.selectedLabel) {
            var path = this.sourceNode.attrDatapath('selectedLabel',setterNode);
            setterNode.setRelativeData(path, item.label, attributes, null, reason);
        }
        if (this.sourceNode.attr.selectedItem) {
            var path = this.sourceNode.attrDatapath('selectedItem',setterNode);
            setterNode.setRelativeData(path, item, attributes, null, reason);
        }
        if (this.sourceNode.attr.selectedPath) {
            var path = this.sourceNode.attrDatapath('selectedPath', setterNode);
            setterNode.setRelativeData(path, itemFullPath, objectUpdate(attributes, item.attr), null, reason);
        }
        var selattr = objectExtract(this.sourceNode.attr, 'selected_*', true);
        for (var sel in selattr) {
            var path = this.sourceNode.attrDatapath('selected_' + sel,setterNode);
            setterNode.setRelativeData(path, item.attr[sel], attributes, null, reason);
        }
        if(this.sourceNode.attr.onSelectedFire){
            setterNode.fireEvent(this.sourceNode.attr.onSelectedFire,true);
        }
        this.sourceNode.publish('onSelected',{path:itemFullPath,item:item,node:node})
    }
});




dojo.declare("gnr.widgets.uploadable", gnr.widgets.baseHtml, {
    onBuilding:function(sourceNode){
        var attr=sourceNode.attr;
        var crop = objectExtract(attr, 'crop_*');
        var that = this;
        if(objectNotEmpty(crop)){
            var innerImage=objectExtract(attr,'src,placeholder,height,width,edit,upload_maxsize,upload_folder,upload_filename,upload_ext,zoomWindow,format,mask,border');
            if (innerImage.placeholder===true){
                innerImage.placeholder = '/_gnr/11/css/icons/placeholder_img_dflt.png'
            }
            innerImage.cr_width=crop.width;
            innerImage.cr_height=crop.height;
            innerImage['onerror'] = "this.sourceNode.setRelativeData(this.sourceNode.attr.src,null);"
            attr.tag = 'div';
            objectUpdate(attr,crop)
            attr.overflow='hidden';
            sourceNode._(this._domtag,innerImage,{'doTrigger':false}) ;
        }else{
             var uploadAttr=objectExtract(attr,'upload_*');
             var cropAttr=objectExtract(attr,'cr_*',true);
             if(objectNotEmpty(uploadAttr)){
                 attr.dropTarget=true;
                 attr.dropTypes='Files,text/plain';
                 attr.drop_ext=uploadAttr.ext || this._default_ext;
                 var src=sourceNode.attr.src;
                 attr.onDrop_text_plain = function(dropInfo,data){
                     if(sourceNode.form && sourceNode.form.isDisabled()){
                        genro.dlg.alert("The form is locked",'Warning');
                        return false;
                    }
                    sourceNode.domNode.onload=function(){
                        that.centerImage(sourceNode,cropAttr);
                    };
                    sourceNode.setRelativeData(src,that.decodeUrl(sourceNode,data).formattedUrl);
                 };
                 var cbOnDropData = function(dropInfo,data){
                    if (uploadAttr.maxsize && data.size>uploadAttr.maxsize){
                        size_kb = uploadAttr.maxsize/1000
                        genro.dlg.alert("Image exeeds size limit ("+size_kb+"KB)",'Error');
                        return false;
                    }
                    if(sourceNode.form && sourceNode.form.isDisabled()){
                        genro.dlg.alert("The form is locked",'Warning');
                        return false;
                    }
                    if(objectNotEmpty(cropAttr)){
                        var domnode = sourceNode.domNode;
                        domnode.onload=function(){
                            that.centerImage(sourceNode,cropAttr);
                        };
                    }
                    var filename = sourceNode.currentFromDatasource(uploadAttr.filename);
                    if(!filename){
                        genro.dlg.alert("Missing info to upload the image",'Warning');
                        return false;
                    }
                    genro.rpc.uploadMultipart_oneFile(data,null,{uploadPath:sourceNode.currentFromDatasource(uploadAttr.folder),
                                  filename:filename,
                                  onResult:function(result){
                                      var url = this.responseText;
                                      
                                      sourceNode.setRelativeData(src,that.decodeUrl(sourceNode,url).formattedUrl);
                                   }});
                 }
                 attr.onDrop_dataUrl = function(dropInfo,data){
                    cbOnDropData(dropInfo,data)
                 }
                 attr.onDrop = function(dropInfo,files){
                    cbOnDropData(dropInfo,files[0]);
                };
            }
            //            attributes.title="<h3>click & drag to move<h3><br/><h3>Shift-clik drag up-down to zoom</h3><br/><h3>Alt-clik drag up-down to rotate</h3>"

        }
    },
    
    creating: function(attributes, sourceNode) {
        var edit=objectPop(attributes,'edit');
        savedAttrs={'edit':edit, zoomWindow:objectPop(attributes,'zoomWindow')};   
        objectUpdate(attributes,this.decodeUrl(sourceNode,objectPop(attributes, 'src')));
        if ((!attributes.src) && ('placeholder' in sourceNode.attr )){
            attributes.src=sourceNode.getAttributeFromDatasource('placeholder');
            if(sourceNode.attr.cr_height){
                 attributes.style = "width:100%;height:100%";
            }
        }
        return savedAttrs;
    },
    
    created: function(widget, savedAttrs, sourceNode) {
        var that=this;
        if(savedAttrs.edit){
            widget.onmousedown=function(e){
                return that.onMouseDown(e)
            }
        };
        if(savedAttrs.zoomWindow){
         dojo.connect(widget,'ondblclick',function(e){
                                              genro.openWindow(sourceNode.currentFromDatasource(this.src),'imagedetail',
                                              {'height':this.height,'width':this.width,'location':'no','menubar':'no','resizable':'yes',
                                              'top':e.clientY,'left':e.clientX,
                                              'toolbar':'no','titlebar':'no','status':'no'});
                                          });
        };
        var url=widget.getAttribute('src')
        //widget.setAttribute('src',null)
    },
    setPlaceHolder:function(sourceNode){
        var domnode = sourceNode.domNode;
        var src=sourceNode.getAttributeFromDatasource('placeholder');
        domnode.setAttribute('src',src);
        if(sourceNode.attr.cr_height){
            domnode.setAttribute('style',"width:100%;height:100%");
        }
    },
    
    centerImage:function(sourceNode,cropAttr){
        var domnode = sourceNode.domNode;
        var margin_top = (domnode.clientHeight-parseInt(cropAttr.height))/2;
        var margin_left = (domnode.clientWidth-parseInt(cropAttr.width))/2;
        var currUrl = sourceNode.getAttributeFromDatasource('src');
        if(currUrl){
            var parsedUrl = parseURL(currUrl);
            var params = parsedUrl.params;
            params = objectUpdate(params,{'v_y':margin_top,'v_x':margin_left});
            var url = this.encodeUrl(parsedUrl);
            sourceNode.setAttributeInDatasource('src',url,true);
        }

    },
     onEditImage:function(sourceNode,e){ 
         var dx=sourceNode.s_x-e.clientX;
         var dy=sourceNode.s_y-e.clientY;
         var body=dojo.body();
         sourceNode.s_x=e.clientX;
         sourceNode.s_y=e.clientY;
         var src=sourceNode.getAttributeFromDatasource('src');
         var parsedUrl=parseURL(src);
         var imgkw=parsedUrl.params;
         var v_x=parseInt(imgkw['v_x'])|| 0;
         var v_y=parseInt(imgkw['v_y']) || 0;
         var v_z=parseFloat(imgkw['v_z'])|| 1;
         var v_r=parseInt(imgkw['v_r']) || 0;
         if (sourceNode.edit_mode=='move'){
            imgkw['v_x']=parseInt((v_x+(dx/v_z)));
            imgkw['v_y']=parseInt((v_y+(dy/v_z)));
            body.style.cursor='move';
         }else if (sourceNode.edit_mode=='zoom'){
             v_z=v_z-(dy/100);
             imgkw['v_z']=(v_z<0.05?0.05:v_z).toFixed(2);
             body.style.cursor=dy>0?'n-resize':'s-resize';
         }else if (sourceNode.edit_mode=='rotate'){
             imgkw['v_r']=v_r+dy;
             body.style.cursor='crosshair';
         }
        if (sourceNode.attr.cr_height){
            imgkw['v_h'] = parseInt(sourceNode.attr.cr_height);
            imgkw['v_w'] = parseInt(sourceNode.attr.cr_width);
        }
        src = this.encodeUrl(parsedUrl);
        //src= genro.addParamsToUrl(parsedUrl.path,imgkw);
        sourceNode.setAttributeInDatasource('src',src,true);         
    },
     onEndEdit:function(sourceNode){
         dojo.body().style.cursor='auto';
         dojo.forEach(sourceNode.editConnections,function(c){
             dojo.disconnect(c);
         })
    },
     onMouseDown:function(e){
         var that=this;
         var modifiers=genro.dom.getEventModifiers(e);
         var sourceNode=e.target.sourceNode;
         sourceNode.edit_mode= (modifiers === '') ? 'move' : (modifiers=='Shift') ? 'zoom':(modifiers=='Alt') ? 'rotate' :null 
         if(sourceNode.edit_mode){
             e.stopPropagation();
             e.preventDefault();
             var src=sourceNode.getAttributeFromDatasource('src');
             if(!src || (sourceNode.form && sourceNode.form.isDisabled())){
                 return;
             }
             sourceNode.s_x=e.clientX;
             sourceNode.s_y=e.clientY;
             var domnode=sourceNode.domNode;
             sourceNode.editConnections=[
                                        dojo.connect(domnode, "onmousemove",function(e){
                                            that.onEditImage(sourceNode,e);
                                            }),
                                        dojo.connect(document, "onmouseup",  function(e){
                                            that.onEndEdit(sourceNode);
                                        })
                                        ];
         };
    },
        
    decodeUrl:function(sourceNode,url){
        if(!url){
            return {};
        }
        var parsedUrl = parseURL(url);
        var p = parsedUrl.params;
        if (!p._pc){
            p['_pc']=new Date().getMilliseconds()
        }
        p['v_x'] = parseFloat((p['v_x'] || 0));
        p['v_y'] = parseFloat((p['v_y'] || 0));
        p['v_z'] = parseFloat((p['v_z'] || 1));
        p['v_r'] = parseFloat((p['v_r'] || 0));
        if(sourceNode.attr.cr_height){
           p['v_h'] = parseFloat(sourceNode.attr.cr_height);
           p['v_w'] = parseFloat(sourceNode.attr.cr_width);
        }else{
           objectExtract(p,'v_h,v_w');
        }
        var result = {src:this.encodeUrl(parsedUrl,true),
                     formattedUrl:this.encodeUrl(parsedUrl),
                     styledict:{'margin_left':(-p['v_x'])+'px','margin_top':(-p['v_y'])+'px','transform_scale':p['v_z'],'transform_rotate':p['v_r']},
                     originalKw:parsedUrl.params
                     };
          
        return result;
    },
    
    encodeUrl:function(parsedUrl,dropFormatters){
        var kw = objectUpdate({},parsedUrl.params);
        var baseUrl;
        if(window.location.protocol.replace(':','')==parsedUrl.protocol && window.location.hostname == parsedUrl.host && window.location.port == parsedUrl.port){
            baseUrl = parsedUrl.path;
        }else{
            baseUrl = parsedUrl.protocol+'://'+parsedUrl.host+parsedUrl.path;
        }
        if (dropFormatters){
            objectExtract(kw,'v_*');
        }
        return genro.addParamsToUrl(baseUrl,kw);
    },
    
    setSrc:function(domnode,v){
        //qui il valore non credo che abbia i valori di croppatura
        var sourceNode = domnode.sourceNode;
        var kwimg=this.decodeUrl(sourceNode,v);
        var src=objectPop(kwimg,'src');
        if(src){
            if(src != domnode.getAttribute('src')){
                domnode.setAttribute('src',src);
            }
            var currStyle=objectFromStyle(domnode.style.cssText);
            if('cr_height' in sourceNode.attr){
                objectPop(currStyle,'height');
                objectPop(currStyle,'width');
            }
            var newStyle=genro.dom.getStyleDict(kwimg['styledict'])
            var style = objectAsStyle(objectUpdate(currStyle,newStyle));
            domnode.setAttribute('style',style);
        }
        else if (('placeholder' in sourceNode.attr)){
            this.setPlaceHolder(sourceNode);
        }
        var valueNode = genro.getDataNode(sourceNode.absDatapath(sourceNode.attr.src));
        if(valueNode){
            var formattedValue = genro.formatter.asText(kwimg.formattedUrl,{dtype:'P',format:sourceNode.attr.format,mask:sourceNode.attr.mask});
            valueNode.updAttributes({_formattedValue:formattedValue},sourceNode);  
        }
    }
});

dojo.declare("gnr.widgets.img", gnr.widgets.uploadable, {
    constructor: function(application) {
        this._domtag = 'img';
         this._default_ext='png,jpg,jpeg,gif';
    }
});

dojo.declare("gnr.widgets.embed", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'embed';
    },
    setSrc:function(domnode,v){
        domnode.sourceNode.rebuild();
    }
});

dojo.declare("gnr.widgets.StaticMap", gnr.widgets.baseHtml, {
    constructor: function(application) {
        this._domtag = 'img';
    },
    creating: function(attributes, sourceNode) {
        var urlPars = objectExtract(attributes, 'map_*');
        if(!urlPars['center']){
            attributes['src'] = null;
            return attributes;
        }
        urlPars.sensor=false;
        var sizeKw =  objectExtract(attributes,'height,width');
        var height = sizeKw.height? sizeKw.height.replace('px',''):'200';
        var width = sizeKw.width? sizeKw.width.replace('px',''):'200';
        urlPars.size = urlPars.size || (width+'x'+height);

        var markersBag = attributes.markers;
        var markersDict = objectExtract(attributes,'marker_*');
        var markers = [];
        if(attributes.centerMarker){
            markers.push('label:C%7C'+urlPars.center);
        }
        if(typeof(markersBag)=='string'){
            markersBag = sourceNode.getRelativeData(markersBag);
        }
        if(markersDict){
            for(var k in markersDict){
                markers.push('label:'+k[0].toUpperCase()+'%7C'+markersDict[k]);
            }
        }
        if(markersBag){
            markersBag.forEach(function(n){
                var nattr = n.attr;
                var str = '';
                if('color' in nattr){
                    str+='color:'+nattr.color+'%7C';
                }
                if('label' in nattr){
                    str+='label:'+nattr.label[0].toUpperCase()+'%7C';
                }
                markers.push(str);
            });
        }
        var url = genro.addParamsToUrl('http://maps.googleapis.com/maps/api/staticmap',urlPars);
        if(markers.length){
            markers = markers.join('&markers=');
            url+='&markers='+markers;
        }
        attributes['src'] = url; 
        return attributes;
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
        sourceNode.markers={};
        var that=this;
        genro.google().setGeocoder(sourceNode,function(){
              that.makeMap(sourceNode,savedAttrs);
        });
        sourceNode.gnr=this;
    },
    makeMap:function(sourceNode,kw){
        kw.mapTypeId=objectPop(kw,'type')||'roadmap';
        kw.zoom=kw.zoom || 8;
        var that = this;
        if(kw.center){
            this.onPositionCall(sourceNode,kw.center,function(center){
                kw.center=center;
                sourceNode.map=new google.maps.Map(sourceNode.domNode,kw);
                var centerMarker = sourceNode.attr.centerMarker;
                if(centerMarker){
                    that.setMarker(sourceNode,'center_marker',kw.center,centerMarker==true?{}:centerMarker);
                }
            });
        }
        
    },

    setMarker:function(sourceNode,marker_name,marker,kw){
        var kw = kw || {};
        if (marker_name in sourceNode.markers){
            sourceNode.markers[marker_name].setMap(null);
            objectPop(sourceNode.markers,marker_name);
        }
        if (!marker){
            return;
        }
        this.onPositionCall(sourceNode,marker,function(position){
            if (position){
                kw.position=position;
                kw.title=kw.title || marker_name;
                kw.map=sourceNode.map;
                sourceNode.markers[marker_name]=new google.maps.Marker(kw);
            }
        });
    },
    setMap_center:function(domnode,v){
        var sourceNode=domnode.sourceNode;
        if(!sourceNode.map){
            var kw = objectExtract(sourceNode.attr,'map_*',true);
            kw.center = v;
            return this.makeMap(sourceNode,kw);
        }
        var that = this;
        this.onPositionCall(sourceNode,v,function(center){
            if (center){
                 sourceNode.map.setCenter(center);
                 var centerMarker = sourceNode.attr.centerMarker;
                 if(centerMarker){
                    that.setMarker(sourceNode,'center_marker',center,centerMarker==true?{}:centerMarker);
                }
            }
        });
    },
    setMap_zoom:function(domnode,v){
        var sourceNode=domnode.sourceNode;
        sourceNode.map.setZoom(v);

    },
    setMap_type:function(domnode,v){
        var sourceNode=domnode.sourceNode;
        sourceNode.map.setMapTypeId(v);

    },
    setMap_markers:function(domnode,v){
        var sourceNode=domnode.sourceNode;
        sourceNode.map.setMapTypeId(v);
    },
    onPositionCall:function(sourceNode,v,cb){
        var result;
        if (typeof(v)!='string'){
            cb(v);
            return;
        }
        if (v.indexOf(',')){
            var c=v.split(',');
            c0=parseFloat(c[0]);
            if (c0){
                c1=parseFloat(c[1]);
                if(c1){
                    result= new google.maps.LatLng(c0, c1);
                    cb(result);
                    return;
                }
            }
        }
        sourceNode.geocoder.geocode({ 'address': v},function(results, status){
             if (status == google.maps.GeocoderStatus.OK) {
                 cb(results[0].geometry.location);
             }
        });
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
    
    

