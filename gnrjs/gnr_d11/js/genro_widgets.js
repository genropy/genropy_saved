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

//######################## genro widgets #########################


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

gnr.menuFromBag = function (bag, appendTo, menuclass, basepath) {
    var menuline,attributes,newmenu,valuelabel;
    var bagnodes = bag.getNodes();
    for (var i = 0; i < bagnodes.length; i++) {
        var bagnode = bagnodes[i];
        attributes = objectUpdate({}, bagnode.attr);
        valuelabel = null;
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
                newmenu = menuline._('menu', {'_class':menuclass});
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
        valueAttr = valueAttr || {};
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
        this.doChangeInData(sourceNode, value, valueAttr);
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

    onBuilding:function(sourceNode){
        //OVERRIDE
    },

    _onBuilding:function(sourceNode){        
        if(sourceNode.getParentNode() && sourceNode.getParentNode().widget && sourceNode.getParentNode().widget.gnr.onChildBuilding){
            return sourceNode.getParentNode().widget.gnr.onChildBuilding(sourceNode.getParentNode(),sourceNode);
        }

        var lbl = objectPop(sourceNode.attr,'lbl');

        if(lbl){
            var inherited_attr = sourceNode.getInheritedAttributes();
            var lbl_attr = objectExtract(inherited_attr,'lbl_*');
            var wrp_attr = objectExtract(inherited_attr,'wrp_*')
            var attr = objectUpdate({},sourceNode.attr)
            var tag = objectPop(attr,'tag');
            var moveable = objectPop(attr,'moveable');
            if (moveable){
                wrp_attr.moveable=moveable;
                objectUpdate(wrp_attr, objectExtract(attr,'top,left,position'));
                lbl_attr.id='handle_'+sourceNode.getStringId()
                wrp_attr.moveable_handle=lbl_attr.id;
            }
            var children = sourceNode.getValue();
            sourceNode._value = null;
            var side = lbl_attr['side'] || 'top';
            sourceNode.attr = objectUpdate({tag:'div',_class:'innerLblWrapper innerLbl_'+side+ ' innerLblWrapper_widget_'+tag.toLowerCase()},wrp_attr);
            sourceNode._('div',objectUpdate({innerHTML:lbl,_class:'innerLbl'},lbl_attr),{'doTrigger':false});
            var c = sourceNode._(tag,attr,{'doTrigger':false});
            if(children && children.len()){
                c.concat(children);
            }
        }else{
            this.onBuilding(sourceNode);
        }
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
        if (attributes.moveable){
            savedAttrs['moveable'] = objectPop(attributes,'moveable');
            savedAttrs['moveable_kw'] = objectExtract(attributes,'moveable_*');
        }

         
        savedAttrs['touchEvents'] = objectPop(attributes,'touchEvents');

        objectExtract(attributes, 'onDrop,onDrag,dragTag,dropTag,dragTypes,dropTypes');
        objectExtract(attributes, 'onDrop_*');
        savedAttrs['dropTarget'] = objectPop(attributes, 'dropTarget');
        savedAttrs['dropTargetCb'] = objectPop(attributes, 'dropTargetCb');
        savedAttrs['dropTargetCb_extra'] = objectExtract(attributes,'dropTargetCb_*');
        savedAttrs.connectedMenu = objectPop(attributes, 'connectedMenu');
        savedAttrs.onEnter = objectPop(attributes, 'onEnter');
        savedAttrs._watchOnVisible = objectPop(attributes,'_watchOnVisible');
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
        if(attributes.drawer && attributes.region){
            attributes.splitter = true;
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
        if (attributes.title) {
            var tip = objectPop(attributes, 'tip') || title || '';
            attributes.title = '<span title="' + tip + '">' + attributes.title + '</span>';
        }
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
        if(savedAttrs._watchOnVisible){
            sourceNode.watch('_watchOnVisible',function(){
                return genro.dom.isVisible(sourceNode);
            },function(){
                sourceNode.publish('isVisible');
            });
        }
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
                };
            }
        }
        var domNode = newobj.domNode || newobj;
        if('moveable' in savedAttrs){
            var moveable_kw = savedAttrs.moveable_kw;
            //var inhattr = sourceNode.getInheritedAttributes();
            var constrain = objectPop(moveable_kw,'constrain');
            genro.src.onBuiltCall(function(){
                var publishOn;
                if(constrain===false){
                    sourceNode.mover = new dojo.dnd.Moveable(domNode,moveable_kw);
                    publishOn = genro;
                }else{
                    dojo.require('dojo.dnd.move');
                    moveable_kw.within = true;
                    sourceNode.mover = new dojo.dnd.move.parentConstrainedMoveable(domNode,moveable_kw);
                    publishOn = sourceNode.getParentNode();
                }
                var coords=dojo.coords(domNode);
                publishOn.publish('onMoveable',{'action':'created','sourceNode':sourceNode,'top':coords.t+'px','left':coords.l+'px'});
                dojo.connect(sourceNode.mover , "onMove", function(mover,topLeft){
                    publishOn.publish('onMoveable',{'action':'moved','sourceNode':sourceNode,
                              top:mover.node.style.top,left:mover.node.style.left
                    });            
                });
            });
        }
      
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
            domNode = newobj.domNode || newobj;
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
            var callback = savedAttrs.onEnter==true? null:dojo.hitch(sourceNode, funcCreate(savedAttrs.onEnter));
            var kbhandler = function(evt) {
                if (evt.keyCode == genro.PATCHED_KEYS.ENTER) {
                    evt.target.blur();
                    if(callback){
                        setTimeout(callback, 100);
                    }
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
                    this.sourceNode._validations.error = _T('Invalid');
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
        if(sourceNode.getParentNode() && sourceNode.getParentNode().widget && sourceNode.getParentNode().widget.gnr.onChildCreated){
            sourceNode.getParentNode().widget.gnr.onChildCreated(sourceNode.getParentNode(),sourceNode);
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
    },

    cell_onCreating:function(gridEditor,colname,colattr){
        //pass
    },

    cell_onDestroying:function(sourceNode,gridEditor,editingInfo){
        //pass
    }
});

dojo.declare("gnr.widgets.htmliframe", gnr.widgets.baseHtml, {
    constructor:function(){
        this._domtag ='iframe';
    },
    creating:function(attributes, sourceNode) {
        if(!attributes.src){
            objectPop(attributes,'src');
        }
        var savedAttrs = {};
        savedAttrs['shield'] = objectPop(attributes,'shield');
        savedAttrs['shield_kw'] = objectExtract(attributes,'shield_*') || {};
        savedAttrs['shield_kw']['_class'] = (savedAttrs['shield_kw']['_class'] || '') + 'shield_layer'
        return savedAttrs;
    },

    created:function(newobj, savedAttrs, sourceNode){
        if(savedAttrs.shield){
            var shield_kw = savedAttrs['shield_kw'];
            shield_kw.z_index = 10;
            shield_kw.opacity = .2;
            sourceNode.getParentNode().setHiderLayer(true,shield_kw);
        }
        if(genro.isMobile){
            genro.dom.setAutoSizer(sourceNode,newobj.parentNode,function(w,h){
                newobj.style.width = w+'px';
                newobj.contentWindow.postMessage({topic:'setClientWidth',width:w},'*');
            });
            dojo.connect(newobj, 'onload', function(){
                newobj.contentWindow.document.body.classList.add('touchDevice');
                setTimeout(function(){
                    genro.dom.resetAutoSizer(sourceNode);
                },50);
            });
        }if(sourceNode.attr.autoScale){
            dojo.connect(newobj, 'onload', function(){
                var scalables = newobj.contentWindow.document.getElementsByClassName('gnrAutoScale');
                for (var i = scalables.length - 1; i >= 0; i--) {
                    genro.dom.setAutoScale(scalables[i],sourceNode.attr.autoScale);
                };
            });
        }
    },

});

dojo.declare("gnr.widgets.iframe", gnr.widgets.baseHtml, {
    _default_ext : 'py,png,jpg,jpeg,gif,html,pdf',

    creating:function(attributes, sourceNode) {
        sourceNode.savedAttrs = objectExtract(attributes, 'rowcount,tableid,src,rpcCall,onLoad,autoSize,onStarted,documentClasses,avoidCache,externalSite');
        objectExtract(attributes,'rpc_*');
        objectUpdate(sourceNode.savedAttrs,objectExtract(sourceNode.attr,'rpc_*',true,true));

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
            try{
                if(!cw.location.host){
                    return;
                }
            }catch(e){
                console.warn('not loaded frame');
                return;
            }
            genro.dom.removeClass(this,'waiting');
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
        sourceNode.reloadIframe = function(delay){
            genro.callAfter(function(){
                this.domNode.gnr.setSrc(this.domNode)
            },delay || 200,sourceNode,'reloadingIframe_'+sourceNode._id);                                            
        };
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
            params = sourceNode.evaluateOnNode(objectExtract(sourceNode.savedAttrs, 'rpc_*', true));
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
        var sourceNode = domnode.sourceNode;
        sourceNode.rebuild();
        domnode = sourceNode.domNode;
        domnode.sourceNode.watch('isVisibile',
                        function(){return genro.dom.isVisible(domnode);},
                        function(){that.setSrc_do(domnode, v, kw);});
    },
    setSrc_do:function(domnode, v, kw) {
        var sourceNode = domnode.sourceNode;
        var attributes = objectUpdate({},sourceNode.attr);
        var main_call = objectPop(attributes,'main');
        var main_kwargs = objectExtract(attributes,'main_*') || {};
        var src_kwargs = objectExtract(attributes,'src_*') || {};
        objectUpdate(src_kwargs,main_kwargs);
        if(!sourceNode.savedAttrs.externalSite){
            src_kwargs._calling_page_id = genro.page_id;
        }
        if (attributes._if && !sourceNode.getAttributeFromDatasource('_if')) {
            v = '';
        } else if (sourceNode.condition_function && !sourceNode.condition_function(sourceNode.condition_value)) {
            v = '';
        }
        else {
            v = v || this.prepareSrc(domnode);
        }
        if(main_call){
            v = v || window.location.pathname;
            src_kwargs.main_call = main_call;
        }
        if (v) {     
            if(sourceNode.attr.documentClasses){
                genro.dom.removeClass(domnode,'emptyIframe');
                genro.dom.addClass(domnode,'waiting');
            }
            src_kwargs = sourceNode.evaluateOnNode(src_kwargs);
            if(sourceNode.savedAttrs.avoidCache){
                src_kwargs._nocache = genro.time36Id();
            }
            v = genro.addParamsToUrl(v,src_kwargs);   
            v = genro.dom.detectPdfViewer(v,sourceNode.attr.jsPdfViewer);
            var doset = this.initContentHtml(domnode,v);
            if (doset){
                sourceNode.watch('absurlUpdating',function(){
                    var absUrl = document.location.protocol + '//' + document.location.host + v;
                    return absUrl != domnode.src;
                },function(){
                    if (domnode.src && sourceNode.attr.onUpdating) {
                        sourceNode.attr.onUpdating();
                    }
                    domnode.src = v;
                });
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
            return false;
        }
        genro.dom.addClass(domnode,'waiting');
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
        objectExtract(attributes,'currentTime,playing,tracks,range_start,range_end');
        if(!attributes.src){
            objectPop(attributes,'src')
        }
    },

    created:function(newobj, savedAttrs, sourceNode) {
        if(sourceNode.attr.currentTime || sourceNode.attr.playing){
            dojo.connect(newobj,'play',function(evt){
                var d = evt.target;
                if(d.sourceNode._currentTimeSetter){
                    return;
                }
                d.sourceNode._currentTimeSetter = setInterval(function(){
                    d.gnr.setPlaying(d);
                    if(d.sourceNode.attr.currentTime){
                        d.sourceNode.setAttributeInDatasource('currentTime',Math.round(d.currentTime*10)/10,'player');
                    }
                },100);
            });
            dojo.connect(newobj,'pause',function(evt){
                var d = evt.target;
                var sn = d.sourceNode;
                d.gnr.setPlaying(d);
                if(sn._currentTimeSetter){
                    clearInterval(sn._currentTimeSetter);
                    delete sn._currentTimeSetter;
                }
            });
        }
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
        var that = this;
        newobj.addEventListener("loadedmetadata", function() { 
            that.setTracks(newobj);
        });
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
            sourceNode.domNode.src=window.URL? window.URL.createObjectURL(stream):stream;
        };
        if(navigator.webkitGetUserMedia){
            navigator.webkitGetUserMedia(capture_kw,onOk,onErr);
        }else{
            navigator.getUserMedia(capture_kw,onOk,onErr);
        }
    },
    setCurrentTime:function(domNode,currentTime,kw){
        var roundedCT = Math.round(domNode.currentTime*10)/10;
        var givenCT = Math.round(currentTime*10)/10;
        if(roundedCT!=givenCT){
            domNode.currentTime = givenCT;
        }
    },

    setPlaying:function(domNode){
        var sourceNode = domNode.sourceNode;
        if(sourceNode.attr.playing){
            sourceNode.setAttributeInDatasource('playing',!(domNode.paused || domNode.ended));
        }
    },

    addTrack:function(domNode,kw){
        var track = document.createElement('track');
        var cue_path = objectPop(kw,'cue_path');
        kw.label = kw.label || kw.kind+'_'+kw.srclang;
        kw['src'] = dataTemplate(kw['src'],kw);
        kw['idx'] = domNode.textTracks.length;
        var hidden = objectPop(kw,'hidden');
        var mode = hidden?'hidden':'showing';
        if(kw.default===false){
            objectPop(kw,'default');
        }else{
            kw.default=true;
        }
        if(!stringEndsWith(kw['src'],'.vtt')){
            kw['src']+='.vtt';
        }
        objectExtract(kw,'_*');
        for (var k in kw){
            track[k] = kw[k];
        }
        track.addEventListener("load", function() { 
            this.mode = mode;
            domNode.textTracks[this.idx].mode = mode; // thanks Firefox 
            domNode.textTracks[this.idx].oncuechange = function(){
                var cue = this.activeCues[0]; 
                if(cue_path && cue){
                    domNode.sourceNode.setRelativeData(cue_path,new gnr.GnrBag({'id':cue.id,text:cue.text,startTime:cue.startTime,endTime:cue.endTime}));
                }
            }
        }); 
        domNode.appendChild(track);
    },
    setSrc:function(domNode,src){
        dojo.forEach(domNode.children,function(c){domNode.removeChild(c)});
        domNode.setAttribute('src',src);
    },

    setTracks:function(domNode){
        var sn = domNode.sourceNode;
        var tracks = sn.attr.tracks;
        dojo.query('track',domNode).forEach(function(dn){
            domNode.removeChild(dn);
        })
        if(tracks){
            var that = this;
            tracks.forEach(function(kw){
                kw = sn.evaluateOnNode(kw);
                that.addTrack(domNode,kw);
            });
        }
    },

});

dojo.declare("gnr.widgets.baseDojo", gnr.widgets.baseHtml, {
    _defaultEvent:'onClick',
    constructor: function(application) {
        this._domtag = 'div';
        this._dojowidget = true;
    },
    createDojoWidget:function(factory,attributes,domnode,sourceNode){
        if('tabindex' in attributes){
            attributes['tabIndex'] = objectPop(attributes,'tabindex');
        }
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
        if(inattr.blankIsNull!==false){
            value = value===''?null:value; // set blank value as null
        }
        if (datanode.getValue() === value) {
            return;
        }
        objectExtract(valueAttr,'_displayedValue,_formattedValue')
        var validateresult;
        valueAttr = objectUpdate(objectUpdate({}, datanode.attr), valueAttr);
        if(typeof(value)=='string' && sourceNode._shortcutsDict){
            value = value.replace(/\b(\w)+\b/gim, function(m){
                if(m){
                    return sourceNode._shortcutsDict[m] || m;
                }
                return m;
                
            });
            if(sourceNode.widget){
                sourceNode.widget.setValue(value)
            }
        }
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
                }else{
                    genro.publish('floating_message',{message:fldname+': '+validateresult.error,sound:'$onerror',messageType:'error'});
                    return
                }
            }
            if (validateresult['warnings'].length) {
                if(validateresult.warnings && formHandler){
                    formHandler.publish('message',{message:fldname+': '+validateresult.warnings.join(','),sound:'$onwarning',messageType:'warning',font_size:'1.1em',font_weight:'bold'});
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
        if (result['modified'] && !validateOnly) {
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

    mixin_setShortcuts:function(shortcuts){
        this.sourceNode._value.popNode('shortcutsMenu');
        delete this.sourceNode._shortcutsDict;
        var shortcutsDict = {};
        var shortcutKeys = [];
        if (!shortcuts){
            return;
        }
        if(shortcuts===true){
            shortcuts = genro.getData('gnr.shortcuts.store');
            if(!shortcuts || shortcuts.len()==0){
                return;
            }
        }
        if(shortcuts instanceof gnr.GnrBag){
            shortcuts.forEach(function(n){
                shortcutsDict[n.attr.keycode] = n.attr.phrase;
                shortcutKeys.push(n.attr.keycode)
            });

        }else{ //shortcuts is string
            var hasKeyCode = shortcuts.indexOf(':')>=0;
            if(!hasKeyCode){
                //only suggestion menu
                this.sourceNode._('menu','shortcutsMenu',{'_class':'smallmenu',
                                                            action:"genro.dom.setTextInSelection($2,($1.fullpath.indexOf('caption_')==0?$1.label:$1.fullpath));",
                                                            values:shortcuts});
                return;
            }
            shortcutKeys = shortcuts.split(',').map(function(n){return n.split(':')[0]});
            shortcutsDict = objectFromString(shortcuts);
        }
        var values = new gnr.GnrBag()
        var i = 0;
        var tpl = '<div style="position:relative; padding-right:60px;">$phrase <div style="position:absolute;right:0;top:0;font-weight:bold;">$keycode</div></div>';
        shortcutKeys.forEach(function(keycode){
            values.setItem('r_'+i,null,{caption:dataTemplate(tpl,{keycode:keycode,phrase:shortcutsDict[keycode]}),phrase:shortcutsDict[keycode],keycode:keycode});
            i++;
        });
        if(values.len()){
            this.sourceNode._('menu','shortcutsMenu',{'_class':'smallmenu',
                                action:"genro.dom.setTextInSelection($2,$1.phrase);",values:values});
            this.sourceNode._shortcutsDict= shortcutsDict;
        }
        
    },

    mixin_setHidden: function(hidden) {
        this.sourceNode.setHidden(hidden);
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
        genro.callAfter(this.afterShow,1,this,'afterShow_'+this.sourceNode._id);
    },

    mixin_afterShow:function(){
        if(this.sourceNode.attr.autoSize){
            this.autoSize();
        }
        var ds = genro.dialogStack;
        var parentDialog = ds.length>1?ds[ds.length-2]:null;
        this.adjustDialogSize(parentDialog);
        this.resize();
    },

    mixin_autoSize:function(){
        if(this.containerNode.firstChild.scrollWidth>this.containerNode.firstChild.clientWidth){
            this.containerNode.firstChild.style.width = this.containerNode.firstChild.scrollWidth+'px';
        }
    },

    mixin_onShowing:function(){},

    mixin_onWindowResize:function(e){
        this.dialogResize();
    },

    mixin_dialogResize:function(parentDialog){
        this.adjustDialogSize(parentDialog);
        var ds = genro.dialogStack;
        if(ds.length>1){
            var idx = ds.indexOf(this);
            var childDialog = ds[idx+1];
            if (childDialog){
                var that = this;
                this.sourceNode.delayedCall(function(){
                    childDialog.dialogResize(that);
                },10);
            }
        }
    },


    mixin_containerNodeResize:function(){
        var fc = this.containerNode.firstChild;
        var c = dojo.coords(this.domNode);
        var t = dojo.coords(this.titleBar);
        var innercoords = {h:c.h-t.h-2,
                            w:this.containerNode.clientWidth
                        };
        if(fc.attributes.widgetid){
            var innerLayout = dijit.getEnclosingWidget(fc);
            innerLayout.resize(innercoords);
            if(innerLayout.layout){
                innerLayout.layout();
            }
        }else{
            fc.style.min_width = innercoords.w+'px';
            fc.style.min_height = innercoords.h+'px';

        }  
    },

    mixin_adjustDialogSize:function(parentDialog){
        var w = {h:Math.floor(window.innerHeight*.98),w:Math.floor(window.innerWidth*.98)};
        var windowRatio = this.sourceNode.attr.windowRatio;
        var parentRatio = this.sourceNode.attr.parentRatio;
        var c = dojo.coords(this.domNode);
        var doResize = false;
        var starting;
        if(parentRatio){
            w = parentDialog? dojo.coords(parentDialog.domNode):w;
            c['w'] = Math.floor(w.w*parentRatio);
            c['h'] = Math.floor(w.h*parentRatio);
            doResize = true;
        }
        else if(windowRatio){
            c['w'] = Math.floor(w.w*windowRatio);
            c['h'] = Math.floor(w.h*windowRatio);
            doResize = true;
        }else{
            for(var k in w){
                starting = '_starting_'+k;
                if(c[k]>w[k]){
                    if(!this[starting]){
                        this[starting] = c[k];
                    }
                    c[k] = w[k];
                    doResize = true;
                }else if(this[starting]){
                    if(this[starting]<=w[k]){
                        c[k] = this[starting];
                        delete this[starting];
                    }else{
                        c[k] = w[k];
                    }
                    doResize = true;
                }
            }
        }
        if(doResize){
            this.resize(c);
        }
        this.layout(); 
    },

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
            var startZindex = 800;
            if(sourceNode.attr.noModal){
                startZindex = 500;
            }
            var ds = genro.dialogStack;
            
            dojo.connect(widget, "show", widget,
                        function() {
                            var parentDialog = ds.length>0?ds[ds.length-1]:null;
                            if (this != ds.slice(-1)[0]) {
                                ds.push(this);
                                let zIndex = widget.sourceNode.attr.z_index || (startZindex + ds.length*2);
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
                            if(!parentDialog && !this._windowConnectionResize){
                                this._windowConnectionResize = dojo.connect(window,'onresize',widget,'onWindowResize');
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
                            if(this._windowConnectionResize){
                                dojo.disconnect(this._windowConnectionResize);
                                delete this._windowConnectionResize;
                            }
                        });
        }
        genro.dragDropConnect(widget.domNode);
        if (genro.isDeveloper){
            genro.dev.inspectConnect(widget.domNode);
        }
        dojo.connect(widget,'resize',widget,'containerNodeResize');
    },
   versionpatch_11__onKey:function(){
       //onkey block inactive (ckeditor)
   },
    
    versionpatch_11__position: function() {
        var centerOn = this.sourceNode.attr.centerOn; 
        if(genro.isMobile){
            genro.dom.centerOn(this.domNode, centerOn,null,-.9);
            return;
        }
        var xRatio = this.sourceNode.attr.xRatio;
        var yRatio = this.sourceNode.attr.yRatio;
        if(centerOn || xRatio || yRatio){
            centerOn = this.sourceNode.currentFromDatasource(centerOn);
            genro.dom.centerOn(this.domNode, centerOn,xRatio,yRatio);
        }else {
            this._position_replaced();
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
        if (editor){
            var parentNode =sourceNode.getParentNode();
            var insideTable = parentNode && parentNode.attr.tag=='td';
            var _class = 'textAreaWrapper';
            if(insideTable){
                _class+= ' textAreaWrapperInTable';
            }
            if(editor){
                _class+= ' textAreaIsEditor';
            }
            var currAttr = sourceNode.attr;
            sourceNode.attr = {'tag':'div',_class:_class};
            objectExtract(currAttr,'tag,width');
            var tKw = objectUpdate({overflow:'hidden',_class:'textAreaWrapperArea'},currAttr); 
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
        var savedAttrs = objectExtract(attributes, 'value,shortcuts');
        return savedAttrs;
    },


    created:function(newobj, savedAttrs, sourceNode) {
        if (savedAttrs.value) {
            newobj.setValue(savedAttrs.value);
        }
       if(savedAttrs.shortcuts){
            setTimeout(function(){
                newobj.setShortcuts(savedAttrs.shortcuts)
            },1)
        }
        dojo.connect(newobj.domNode, 'onchange', dojo.hitch(this, function() {
            this.onChanged(newobj);
        }));
        dojo.connect(sourceNode,'setValidationError',function(result){
            newobj.state = result.error?'Error':null;

        })
    },

    cell_onCreating:function(gridEditor,colname,colattr){
        colattr['z_index']= 1;
        colattr['position'] = 'fixed';
        colattr['height'] = colattr['height'] || '100px';
    },

    onChanged:function(widget) {
        var value = widget.getValue();
        this._doChangeInData(widget.domNode, widget.sourceNode, value);
    },

    mixin_displayMessage: function(/*String*/ message){
        // summary:
        //      User overridable method to display validation errors/hints.
        //      By default uses a tooltip.
        if(isNullOrBlank(this.value)){
            return;
        }
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

    mixin_setHiddenChild:function(child,value){
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
        child.setHidden = function(value){
            widget.setHiddenChild(this,value);
        };
        gnr.setOrConnectCb(child, 'onShow', dojo.hitch(this, 'onShowHideChild', widget, child, true));
        gnr.setOrConnectCb(child, 'onHide', dojo.hitch(this, 'onShowHideChild', widget, child, false));
        var pageName = child.sourceNode.attr.pageName;
        if (pageName) {
            widget.gnrPageDict = widget.gnrPageDict || {};
            widget.gnrPageDict[pageName] = child;
        }
    },
    mixin_deletePage:function(page){
        var pageNode = page.sourceNode;
        pageNode.getParentBag().popNode(pageNode.label);
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


    mixin_setHiddenChild:function(child,hidden){
        if(hidden && child.selected){
            var otherChildren = this.getChildren().filter(function(other){return other!==child});
            if(otherChildren.length>0){
                var that = this;
                this.switchPage(this.getChildIndex(otherChildren[0]));
            }
        }
        genro.dom.toggleVisible(child.controlButton.domNode,!hidden);
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
        widget._saved_size = {};
        dojo.connect(widget, 'startup', dojo.hitch(this, 'afterStartup', widget));
        if (dojo_version == '1.1') {
            dojo.connect(widget, 'addChild', dojo.hitch(this, 'onAddChild', widget));
            dojo.connect(widget, 'removeChild', dojo.hitch(this, 'onRemoveChild', widget));
        }
    },



    addClosableHandle:function(bc,pane,kw){
        var side = pane.attr.region;
        var orientation = ['left','right'].indexOf(side)>=0?'vertical':'horizontal';
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
                if(orientation=='vertical'){
                    pane.__currDimension = pane.widget.domNode.style.width;
                    dojo.style(pane.widget.domNode,'width',null);
                }else{
                    pane.__currDimension = pane.widget.domNode.style.height;
                    dojo.style(pane.widget.domNode,'height',null);
                }
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
        var opener = pane._('div',objectUpdate({_class:_class,connect_onclick:togglecb},closablePars),{doTrigger:false});
        if(label){
            opener._('div',{'innerHTML':label,_class:'slotbarOpener_label_'+orientation},{doTrigger:false});
        }
        if(iconClass){
            opener._('div',{_class:iconClass},{doTrigger:false});
        }
    },

    onChildCreated:function(sourceNode,childSourceNode){
        if(childSourceNode.attr.closable){
            var closable_kw = objectExtract(childSourceNode.attr,'closable_*',true,true) //normalizeKwargs(childSourceNode.attr,'closable');
            closable_kw.closable = childSourceNode.attr.closable;
            this.addClosableHandle(sourceNode.widget,childSourceNode,closable_kw);
        }
    },

    onChildBuilding:function(sourceNode,childSourceNode){
        if(!childSourceNode.attr.region || childSourceNode.attr.tag.toLowerCase() == 'bordercontainer' || !childSourceNode.attr.closable){
            return;
        }
        var wrapperNode = childSourceNode;
        var parentContent = sourceNode.getValue();
        var childLabel = childSourceNode.label;
        var wrapperAttr = childSourceNode.attr;
        var childContent = childSourceNode.getValue();
        childSourceNode.setValue(new gnr.GnrDomSource(),false);
        var childTag = objectPop(wrapperAttr,'tag');
        var childAttr = objectUpdate({},wrapperAttr);
        objectExtract(wrapperAttr,'margin,background,style,_class,nodeId,overflow');
        objectExtract(childAttr,'height,width,border,left,right,top,bottom')
        objectExtract(childAttr,'margin_*');
        objectExtract(childAttr,'border_*');

        objectPop(childAttr,'closable');
        objectExtract(childAttr,'closable_*');
        wrapperAttr.tag ='borderContainer';
        wrapperNode.attr._class = 'closableWrapper'
        wrapperNode.label = 'wrapper_'+childAttr.region;
        childAttr.region='center';
        childAttr.content = childContent;
        var src = wrapperNode._(childTag,childLabel,childAttr,{doTrigger:false});
        src.getParentNode().setValue(childContent,false);
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
            widget.sourceNode.watch('untillIsVisible',function(){
                return widget.domNode?genro.dom.isVisible(widget.domNode):false;
            },function(){
                var regions = sourceNode.getRelativeData(sourceNode.attr.regions);
                if (!regions) {
                    regions = new gnr.GnrBag();
                    sourceNode.setRelativeData(sourceNode.attr.regions, regions);
                }
                var regions = regions.getNodes();
                for (var i = 0; i < regions.length; i++) {
                    widget.setRegions(null, {'node':regions[i]});
                }
            });
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
            if(child.sourceNode.attr.drawer){
                widget.addDrawerHandle(child)
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
                show =  !this.isRegionVisible(region);//(this._splitterThickness[region] == 0);
            }
            var disp = show ? '' : 'none';
            var splitterNode = this._splitters[region];
            if (splitterNode) {
                var tk = this._splitterThickness['_' + region] || this._splitterThickness[region];
                this._splitterThickness['_' + region] = tk;
                this._splitterThickness[region] = show ? tk : 0;
                dojo.style(splitterNode,( region=='left' || region=='right')? 'width':'height', this._splitterThickness[region]+'px');
                //var st = dojo.style(splitterNode, 'display', disp);
            }
            dojo.style(regionNode, 'display', disp);
            if(!show){
                this._saved_size[region] = (region=='left' || region=='right')?regionNode.style.width:regionNode.style.height;
            }else if(region in this._saved_size){
                if(region=='left' || region=='right'){
                    regionNode.style.width = this._saved_size[region];
                }else{
                    regionNode.style.height = this._saved_size[region];
                }
            }
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
    },

    mixin_addDrawerHandle:function(child){
        var bc = this;
        var pane = child.sourceNode;
        var kw = objectUpdate({},pane.attr);
        var side = pane.attr.region;
        var splitter = bc._splitters[side];
        var drawerDom = document.createElement('div');
        splitter.appendChild(drawerDom);
        var drawerClass = objectPop(kw,'drawer_class');
        var drawerStyle = objectPop(kw,'drawer_style');
        var drawer_kw = objectExtract(kw,'drawer_*');
        var drawerLabel = objectPop(drawer_kw,'label');
        var styledict_kw = genro.dom.getStyleDict(drawer_kw);
        drawerDom.setAttribute('style',objectAsStyle(objectUpdate(objectFromStyle(drawerStyle),styledict_kw)));
        genro.dom.addClass(drawerDom,'drawerHandle');
        if(drawerClass){
            genro.dom.addClass(drawerDom,drawerClass);
        }
        if(drawerLabel){
            drawerDom.innerHTML = drawerLabel;
        }
        
        var drawer = pane.getAttributeFromDatasource('drawer');
        genro.dom.addClass(splitter,'drawerSplitter '+'drawer_region_'+side);
        if (!pane.getAttributeFromDatasource('splitter')){
            genro.dom.addClass(splitter,'drawerFixed')
            dijit.getEnclosingWidget(splitter)._startDrag = function(){};
        }
        if(drawer=='close'){
            dojo.connect(bc,'startup',function(){bc.showHideRegion(side,false);});
        }
        dojo.connect(drawerDom,'onclick',function(e){
            var show = bc.showHideRegion(side,'toggle');
            if(drawer_kw.onclick){
                funcApply(drawer_kw.onclick,{evt:e,show:show},pane);
            }
        })
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
        attributes.width = '2px';
        attributes.height = '2px';
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
                    genro.dom.addClass(dojo.body(),'active_click_palette');
                    this.screenStartPoint = {x:e.screenX,y:e.screenY};
                    this.page_id = genro.page_id;
                    genro.mainGenroWindow.genro.currentResizeHandle=this;
                });
                dojo.connect(this._resizeHandle,'_endSizing',function(e){
                    genro.mainGenroWindow.genro.currentResizeHandle=null;
                    genro.dom.removeClass(dojo.body(),'active_click_palette');
                });
            });
        }
        dojo.connect(widget,'maximize',function(){
            this.resize({'t':'0','l':'0'});
        });
        dojo.connect(sourceNode,'_onDeleting',function(){
            widget.destroyRecursive();
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
        var rect;
        if (this.sourceNode.attr.nodeId){
            var storeKey = 'palette_rect_' + genro.getData('gnr.pagename') + '_' + this.sourceNode.attr.nodeId;
            rect = genro.getFromStorage("local", storeKey, dojo.coords(this.domNode));
            if(rect){
                this._size_from_cache = true;
            }
        }
        var oh = this.domNode.parentElement.offsetHeight;
        var ow = this.domNode.parentElement.offsetWidth;
        if(!rect || this.sourceNode.attr.persist===false || this.sourceNode.attr.fixedPosition){
            var currAttr = this.sourceNode.currentAttributes();
            rect = {};
            var p = {'left':'l','top':'t','width':'w','height':'h'};
            for(var k in p){
                if(currAttr[k]){
                    rect[p[k]] = parseInt(currAttr[k]);
                }
            }
            if(!rect.l && currAttr.right){
                rect.l = ow - rect.w - parseInt(currAttr.right);
            }
        }
        if(rect.w+20>ow){rect.w = ow-20;}
        rect.l = Math.max(rect.l,10);
        if(rect.l+rect.w>ow-10){rect.l = ow-rect.w-10;}
        if(rect.h+20>oh){rect.h = oh-20;}
        rect.t = Math.max(rect.t,10);
        if(rect.t+rect.h>oh-10){rect.t = oh-rect.h-10;}
        this.resize(rect);
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
        var sourceNode = this.sourceNode;
        var ctxSourceNode = this.getParent().ctxTargetSourceNode || genro._lastCtxTargetSourceNode || sourceNode;
        var menuAttr = sourceNode.getAttr();
        var inAttr = sourceNode.getInheritedAttributes();
        var actionScope = sourceNode.attributeOwnerNode('action');
        var action = inAttr.action;
        if (ctxSourceNode && ctxSourceNode.attr.action) {
            action = ctxSourceNode.attr.action;
            actionScope = ctxSourceNode;
        }
        f = funcCreate(action);
        if (f) {
            f.call(actionScope, menuAttr, ctxSourceNode, evt);
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
    },
    created: function(widget, savedAttrs, sourceNode) {
        dojo.connect(widget, 'startup', dojo.hitch(this, 'afterStartup', widget));
    },

    afterStartup:function(widget) {
        if(widget._singleChild && widget._singleChild.sourceNode && (widget._singleChild.sourceNode.attr.tag.toLowerCase() in genro.src.layouttags)){
            widget.domNode.style.overflow = 'hidden';
        }
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
            var contentBag;
            if(typeof(savedAttrs.values)=='string'){
                contentBag = new gnr.GnrBag(objectFromString(savedAttrs.values,null,'kv'));
            }else{
                contentBag = savedAttrs.values;
            }
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
                    //console.warn('the menu at storepath:'+savedAttrs.storepath+' is empty');
                }
            }else{
                //console.warn('the menu at storepath:'+savedAttrs.storepath+' is empty');
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
            //console.log(zzz)
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
        var ctxSourceNode;
        if (this.originalContextTarget) {
            if (this.originalContextTarget.sourceNode) {
                ctxSourceNode = this.originalContextTarget.sourceNode;
            }
            else {
                var w = genro.dom.getBaseWidget(this.originalContextTarget);
                if(w){
                    ctxSourceNode = w.sourceNode;
                }
            }
        }
        genro._lastCtxTargetSourceNode = ctxSourceNode;
        this.ctxTargetSourceNode = ctxSourceNode;
        var sourceNode = this.sourceNode;
        var wdg = sourceNode.widget;

        if( (wdg.modifiers || wdg.validclass ) && !(genro.wdg.filterEvent(e, wdg.modifiers, wdg.validclass)) ){
            return;
        }
        var contextclick = (e.button==2 || genro.dom.getEventModifiers(e)=='Ctrl');
        if(!wdg.modifiers){
            if(!contextclick){
                //not modifiers nor contextclick
                return;
            }
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
        var widgetChildren = wdg.getChildren();
        widgetChildren.forEach(function(item){
            if(item.onOpen){
                funcApply(item.onOpen,null,sourceNode,['item','evt'],[item,e]);
            }
            if(wdg.menuItemCb){
                wdg.menuItemCb(item,e)
            }
            if(wdg.disabledItemCb){
                item.setDisabled(wdg.disabledItemCb(item,e));
            }
            if(wdg.hiddenItemCb){
                item.setHidden(wdg.hiddenItemCb(item,e));
            }
        });

        if(wdg.modifiers){
            wdg._contextMouse_replaced.call(wdg, e);
            wdg._openMyself_replaced.call(wdg, e);
        }
        else if (contextclick) {
            wdg._contextMouse_replaced.call(wdg, e);
        }

    },
    
    versionpatch_11__openMyself: function (e) {
        var contextclick = (e.button==2 ||  genro.dom.getEventModifiers(e)=='Ctrl');
        if(this.validclass && !genro.wdg.filterEvent(e,null,this.validclass)){
            return;
        }
        if (contextclick && (!this.modifiers)) {
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
            if(enclosingWidget.sourceNode){
                var cmenu = enclosingWidget.sourceNode.attr.connectedMenu;
                if(cmenu && cmenu == this.sourceNode.attr.id){
                    aroundWidget = enclosingWidget;
                }
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
        attributes.showDelay = attributes.showDelay || attributes.tooltip_type == 'help'? 2000:null;
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
        var modifiers = (this.modifiers || defaultMod);
        
        if (genro.wdg.filterEvent(e, modifiers, this.validclass)) {
            var showDelay = modifiers?50:this.showDelay;
            if(!this._showTimer){
                var target = e.target;
                this._showTimer = setTimeout(dojo.hitch(this, function(){this.open(target)}), showDelay);
            }
        }
    },
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
dojo.declare("gnr.widgets._ButtonLogic",null, {
    clickHandler:function(sourceNode,e) {
        e.stopPropagation();
        e.preventDefault();
        if(sourceNode.disabled){
            return;
        }
        var inattr = sourceNode.getInheritedAttributes();
        //var _delay = '_delay' in inattr? inattr._delay: 100;
        var _delay = inattr._delay;
        if(!_delay){
            sourceNode.setDisabled('*pendingclick*');
            sourceNode._clickTimeout = setTimeout(function(){
                sourceNode._clickTimeout = null;
                if(sourceNode.disabled=='*pendingclick*'){
                    sourceNode.setDisabled(false);
                }
            },200);
            return this._clickHandlerDo(sourceNode,e,inattr);
        }
        if(sourceNode._pendingClick){
            var pc = sourceNode._pendingClick;
            delete sourceNode._pendingClick
            clearTimeout(pc);
        }
        var that = this;
        sourceNode._pendingClickCount = (sourceNode._pendingClickCount || 0)+1;
        sourceNode._pendingClick = setTimeout(function(){
            var count = sourceNode._pendingClickCount;
            sourceNode._pendingClickCount = 0;
            that._clickHandlerDo(sourceNode,e,inattr,count);
        },_delay);
    },
    _clickHandlerDo:function(sourceNode,e,inattr,count) {
        var modifier = eventToString(e);
        var action = inattr.action;
        var modifiers = genro.dom.getEventModifiers(e);
        var argnames = ['event','_counter','modifiers'];
        var argvalues = [e,count,modifiers];
        if (action) {
            var action_attributes = sourceNode.currentAttributes();
            var ask_params = sourceNode._ask_params;
            
            var skipOn,askOn,doAsk,_if;
            if(ask_params){
                skipOn = ask_params.skipOn;
                askOn = ask_params.askOn;
                askIf = ask_params.askIf;
                if(askIf){
                    askIf = funcApply('return '+askIf,action_attributes,sourceNode);
                }
                doAsk = askIf || !(askOn || skipOn) || (askOn && askOn==modifiers) || (skipOn && skipOn!=modifiers);
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
                        result = result.asDict();
                        objectUpdate(action_attributes,result);
                        action_attributes._askResult = result;
                    }
                    funcApply(action, objectUpdate(action_attributes, {}), sourceNode,argnames,argvalues);
                }

                genro.dlg.prompt(objectPop(promptkw,'title','Parameters'),promptkw,sourceNode);
            }else{
                funcApply(action, objectUpdate(action_attributes, {}), sourceNode,argnames,argvalues);
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
    }
});
dojo.declare("gnr.widgets.LightButton", [gnr.widgets.baseHtml,gnr.widgets._ButtonLogic], {
    constructor: function(application) {
        this._domtag = 'div';
    },

    creating:function(attributes, sourceNode) {
        var savedAttrs = objectExtract(attributes, 'fire_*');
        var label = objectPop(attributes,'label');
        attributes.innerHTML = attributes.innerHTML || label;
        savedAttrs['action'] = objectPop(attributes, 'action');
        savedAttrs['fire'] = objectPop(attributes, 'fire');
        savedAttrs['publish'] = objectPop(attributes, 'publish');
        savedAttrs['ask_params'] = objectPop(attributes,'ask');
        return savedAttrs;
    },
    
    created: function(widget, savedAttrs, sourceNode) {
        var that = this;
        dojo.connect(widget, 'onclick', function(e){
            that.clickHandler(sourceNode,e);
        });
        objectExtract(sourceNode._dynattr, 'fire_*');
        objectExtract(sourceNode._dynattr, 'fire,publish');
        if(savedAttrs.ask_params){
            sourceNode._ask_params = savedAttrs.ask_params;
        }
    }
});

dojo.declare("gnr.widgets.Button", [gnr.widgets.baseDojo,gnr.widgets._ButtonLogic], {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'Button';
    },
    
    creating:function(attributes, sourceNode) {
        var buttoNodeAttr = 'height,width,padding,background,background_color';
        var savedAttrs = objectExtract(attributes, 'fire_*');
        savedAttrs.shortcut = objectPop(attributes,'_shortcut');        
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
        var that = this;
        dojo.connect(widget, 'onClick', function(e){
            that.clickHandler(sourceNode,e)
        });
        objectExtract(sourceNode._dynattr, 'fire_*');
        objectExtract(sourceNode._dynattr, 'fire,publish');
        if (savedAttrs['_style']) {
            var buttonNode = dojo.query(".dijitButtonNode", widget.domNode)[0];
            dojo.style(buttonNode, savedAttrs['_style']);
        }
        if(savedAttrs.ask_params){
            sourceNode._ask_params = savedAttrs.ask_params;
        }
        if(savedAttrs.shortcut){
            genro.dev.shortcut(savedAttrs.shortcut, function(e) {
                var domNode = sourceNode.getDomNode();
                if(!genro.dom.isVisible(domNode) || !genro.dom.isActiveLayer(domNode)){
                    return;
                }
                if(sourceNode.widget && sourceNode.widget.disabled){
                    return;
                }
                if(sourceNode.attr._shortcut_activeForm){
                    if(genro.activeForm && sourceNode.form!=genro.activeForm){
                        return;
                    }
                }
                that.clickHandler(sourceNode,e);
            },null,sourceNode);
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
        if(sourceNode._gnrcheckbox_wrapper){
            sourceNode._gnrcheckbox_wrapper.parentNode.removeChild(sourceNode._gnrcheckbox_wrapper);
            delete sourceNode._gnrcheckbox_wrapper;
        }
        var label = savedAttrs['label'];
        var dn = widget.domNode;
        var pn = widget.domNode.parentNode;
        var gnrcheckbox_wrapper = document.createElement('div')
        gnrcheckbox_wrapper.setAttribute('class','gnrcheckbox_wrapper')
        pn.replaceChild(gnrcheckbox_wrapper,dn);
        gnrcheckbox_wrapper.appendChild(dn);
        sourceNode._gnrcheckbox_wrapper = gnrcheckbox_wrapper;
        if (label) {
            if(sourceNode._labelNode){
                sourceNode._labelNode.parentNode.removeChild(sourceNode._labelNode);
                delete sourceNode._labelNode;
            }
            var labelattrs = savedAttrs['labelattrs'];
            labelattrs['for'] = widget.id;
            labelattrs['margin_left'] = labelattrs['margin_left'] || '3px';
            var domnode = genro.wdg.create('label', widget.domNode.parentNode, labelattrs);
            domnode.innerHTML = label;
            sourceNode._labelNode = domnode;
        }
        if (sourceNode.hasDynamicAttr('value')) {
            var value = sourceNode.getAttributeFromDatasource('value');
            //widget.setChecked(value);
            widget.setAttribute('checked', value);
        }
    },
    mixin_setHidden: function(hidden) {
        if(this.sourceNode._hiddenTargets){
            this.sourceNode.setHidden(hidden);
        }else{
            dojo.style(this.sourceNode._gnrcheckbox_wrapper, 'display', (hidden ? 'none' : ''));
        }
    },

    _getKeeperRoot:function(sourceNode){
        return sourceNode._gnrcheckbox_wrapper;
    },
    
    mixin_displayMessage:function() {
        //patch
    },
    patch_onClick:function(e) {
        var actionScope = this.sourceNode.attributeOwnerNode('action');
        if(actionScope){
            var action = actionScope.attr.action;
            if (action && actionScope.attr.tag!='button') {
                dojo.hitch(this, funcCreate(action))(this.sourceNode.attr, this.sourceNode, e);
            }
        }
        
        
    },
    patch_setValue: function(/*String*/ value, pc) {
        //this.setChecked(value);
        this.setAttribute('checked', value);
    },
    cell_onCreating:function(gridEditor,colname,colattr){
        colattr['margin'] = 'auto';
    },
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
    },
    connectFocus: function(widget, savedAttrs, sourceNode) {
        if (sourceNode.attr._autoselect && !genro.isMobile) {
            dojo.connect(widget, 'onFocus', widget, function(e) {
                setTimeout(dojo.hitch(this, 'selectAllInputText'), 1);
            });
        }
    },

    mixin_selectAllInputText: function() {
        dijit.selectInputText(this.focusNode);
    },

    creating:function(attributes, sourceNode) {
        var savedAttrs = objectExtract(attributes, 'shortcuts');
        return savedAttrs;
    },

    created: function(widget, savedAttrs, sourceNode) {
        this._baseTextBox_created(widget,savedAttrs,sourceNode);

    },

    _baseTextBox_created:function(widget, savedAttrs, sourceNode){
        if(genro.isMobile){
            widget.focusNode.setAttribute('autocapitalize','none');
            widget.focusNode.setAttribute('autocomplete','off');
            widget.focusNode.setAttribute('autocorrect','off');
        }
        this.connectFocus(widget, savedAttrs, sourceNode);
        if(savedAttrs.shortcuts){
            setTimeout(function(){
                widget.setShortcuts(savedAttrs.shortcuts)
            },1)
        }
    },
    
    cell_onDestroying:function(sourceNode,gridEditor,editingInfo){
        dijit.hideTooltip(sourceNode.widget.domNode);
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

        var savedAttrs = objectExtract(attributes, 'shortcuts');
        return savedAttrs;
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
        if ('popup' in attributes && (objectPop(attributes, 'popup') == false)) {
            attributes.popupClass = null;
        }
        if(this.dojo__selector=='datetime'){
            attributes.popup = false;
            sourceNode.attr.noIcon = true;
            if(objectPop(attributes,'seconds')){
                attributes.constraints.timePattern ='HH:mm:ss';
            }
        }
    },

    created: function(widget, savedAttrs, sourceNode) {
        if(!sourceNode.attr.noIcon){
            var focusNode;
            var curNode = sourceNode;
            genro.dom.addClass(widget.focusNode,'comboArrowTextbox')
            var box= sourceNode._('div',{cursor:'pointer', width:'20px',tabindex:-1,
                                    position:'absolute',top:0,bottom:0,right:0,connect_onclick:function(){
                                        widget._open();
                                    }});
            box._('div',{_class:'dateTextBoxCal',position:'absolute',top:0,bottom:0,left:0,right:0,tabindex:-1});
            this.connectFocus(widget, savedAttrs, sourceNode);
        }
        
    },

    patch_parse:function(value,constraints){
        if(value && !this._focused){
            var r,d1,d2,y;
            var info = dojo.date.locale._parseInfo(constraints);
            var tokens = info.tokens;
            var datesplit = value.split(' ');
            var match = datesplit[0].match(/^(\d{2})(\d{2})(\d{2}|\d{4})$/);
            var doSetValue = false;
            if(match){
                datesplit[0] = match[1]+'/'+match[2]+'/'+match[3];
                doSetValue = true;
            }
            if(constraints.selector=='datetime'){
                doSetValue = true;
                var timestr = datesplit[1];
                var timematch =timestr.match(/^(\d{2})(\d{2})?(\d{2})?$/);
                if (!timematch){
                    timematch =timestr.match(/^(\d{2}):(\d{2})(?::(\d{2}))?$/);
                }
                if(!timematch){
                    timematch = ['00:00:00','00','00','00'];
                }
                var tl = [timematch[1],timematch[2]];
                if(constraints.timePattern =='HH:mm:ss'){
                    tl.push(timematch[3] || '00');
                }
                datesplit[1] = tl.join(':');
            }
            value = datesplit.join(' ');
            var re = new RegExp("^" + info.regexp + "$");
            match = re.exec(value);
            if(match){
                var d,m,y,hours,minutes,seconds;
                if(tokens[0][0]=='d'){
                    d = match[1];
                    m = match[2];
                }else{
                    d = match[2];
                    m = match[1];
                }
                d = parseInt(d);
                m = parseInt(m)-1;
                y = parseInt(match[3]);
                if(constraints.selector=='datetime'){
                    hours = parseInt(match[4] || '0');
                    minutes = parseInt(match[5] || '0');
                    seconds = parseInt(match[6] || '0');
                }else{
                    hours = 0;
                    minutes = 0;
                    seconds =0;
                }
                if(y<100){
                    var pivotYear ='pivotYear' in this.sourceNode.attr?this.sourceNode.attr.pivotYear:20;
                    var year = '' + new Date().getFullYear();
                    var century = year.substring(0, 2) * 100;
                    var cutoff = Math.min(Number(year.substring(2, 4)) + pivotYear, 99);
                    var y = (y < cutoff) ? century + y : century - 100 + y;
                }
                r = new Date(y,m,d,hours,minutes,seconds);  
                
                if(doSetValue){
                    var that = this;
                    setTimeout(function(){
                        that.setValue(r,true);
                    });
                }
                return r;
            }else{
                var that = this;
                this.setValue(null);
                var sn = this.sourceNode;
                sn._waiting_rpc = true;
                genro.serverCall('decodeDatePeriod',{datestr:value},function(v){
                    if(v.getItem('from')){
                        that.setValue(v.getItem('from'),true);
                    }
                    if(that.sourceNode.attr.period_to){
                        that.sourceNode.setRelativeData(that.sourceNode.attr.period_to,v.getItem('to'));
                    }
                    sn._waiting_rpc = false;
                });
                return;
            }
        }
        return dojo.date.locale.parse(value, constraints) || undefined; 
    }
});

dojo.declare("gnr.widgets.DatetimeTextBox", gnr.widgets.DateTextBox, {
    dojo__selector:'datetime'
    //attributes_mixin__selector:'datetime'
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
        var format = objectPop(attributes,'format');
        var places = objectPop(attributes,'places');
        attributes.constraints = objectExtract(attributes, 'min,max,pattern,round,currency,fractional,symbol,strict,locale');
        attributes.constraints.pattern = attributes.constraints.pattern || format;
        if(!places && attributes.constraints.pattern && attributes.constraints.pattern.indexOf('.')){
            var s = attributes.constraints.pattern.split('.')[1];
            if(s){
                places = '0,'+s.length;
            }
        }
        sourceNode._parseDict = places?{places:places}:{};
        //attributes.editOptions = objectUpdate({})
        if ('ftype' in attributes) {
            attributes.constraints['type'] = objectPop(attributes['ftype']);
        }
    },

    created: function(widget, savedAttrs, sourceNode) {
        this._baseTextBox_created(widget, savedAttrs, sourceNode);
        if (dojo.number._parseInfo().decimal==','){
            dojo.connect(widget,'onkeyup',function(evt){
                if(evt.key=='.'){
                    widget.textbox.value = widget.textbox.value.replace('.',',');
                }
            });
        }
        widget.setValue(sourceNode.getRelativeData(sourceNode.attr.value)); //avoid set 0 as null value by dojo widget
    },

    onSettingValueInData: function(sourceNode, value,valueAttr) {
        if (isNullOrBlank(value)) {
            value = null;
        }
        return value;
    },
    patch_format:function(v,c){
        if(isNullOrBlank(v)){
            return '';
        }else{
            return this.format_replaced(v,c);
        }
    },
    patch_getValue: function(){
        var displayedValue = this.getDisplayedValue();
        var result = this.parse(displayedValue, this.constraints); //this.sourceNode._parseDict
        if(isNaN(result)){
            result = this.parse(displayedValue,  this.sourceNode._parseDict)
        }
        return result;
    },
    patch_isValid: function(/*Boolean*/ isFocused){
        if(isFocused){
            return true;
        }
        return this.validator(this.textbox.value, this.sourceNode._parseDict) || this.validator(this.textbox.value, this.constraints);
    },

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

dojo.declare("gnr.widgets.Slider", gnr.widgets.baseDojo, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'CurrencyTextBox';
    },
    created: function(widget, savedAttrs, sourceNode) {
        dojo.connect(widget.sliderHandle,'onmousedown',function(){
            widget._ignoreDataChanges = true;
        })
        dojo.connect(window,'onmouseup',function(){
            widget._ignoreDataChanges = false;
        })
    }
});

dojo.declare("gnr.widgets.HorizontalSlider", gnr.widgets.Slider, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'HorizontalSlider';
    }
});

dojo.declare("gnr.widgets.VerticalSlider", gnr.widgets.Slider, {
    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'VerticalSlider';
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
        store.searchAttr = attributes.searchAttr;
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
        if(!genro.isMobile){
                dojo.connect(widget, 'onFocus', widget, function(e) {
            // select all text in the current field -- (TODO: reason for the delay)
                timeoutId = setTimeout(dojo.hitch(this, 'selectAllInputText'), 300);
            });

        }

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
        var row = item && this.isValid() ? (item.attr || {}) : {};
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
        if (this.sourceNode.selectedCb){
            this.sourceNode.selectedCb(item);
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
                 var street_number = details['street_number']||'??'; //subpremise
                 if(details['subpremise']){
                    street_number = details['subpremise']+'/'+street_number;
                 }
                 details['street_address_eng'] = street_number+' '+details['route_long'];
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

dojo.declare("gnr.widgets.DynamicBaseCombo", gnr.widgets.BaseCombo, {
    _autoselectFirstOption:false,
    creating: function(attributes, sourceNode) {
        var savedAttrs = {};
        attributes.httpMethod = attributes.httpMethod || genro.extraFeatures.wsk_dbselect?'WSK':null;
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
        var resolverAttrs = objectExtract(attributes, 'method,columns,limit,auxColumns,hiddenColumns,alternatePkey,rowcaption,order_by,preferred,invalidItemCondition');
        resolverAttrs['notnull'] = attributes['validate_notnull'];
        savedAttrs['auxColumns'] = resolverAttrs['auxColumns'];
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
        objectExtract(attributes, 'condition_*');
        resolverAttrs['condition'] = sourceNode.attr.condition;
        objectUpdate(resolverAttrs, objectExtract(sourceNode.attr, 'condition_*', true));
        resolverAttrs['exclude'] = sourceNode.attr['exclude']; // from sourceNode.attr because ^ has to be resolved at runtime
        resolverAttrs._id = '';
        resolverAttrs._querystring = '';

        var storeAttrs = objectExtract(attributes, 'store_*');
        var store;
        savedAttrs['record'] = objectPop(storeAttrs, 'record');
        attributes.searchAttr = storeAttrs['caption'] || 'caption';
        var sw = objectExtract(attributes,'switch_*');
        var switches = {};
        for(var k in sw){
            var ks = k.split('_');
            if(ks.length==1){
                switches[k] = {'search':new RegExp('^'+sw[k])};
                objectUpdate(switches[k],objectExtract(sourceNode.attr,'switch_'+k+'_*',true));
                if(switches[k].action){
                    switches[k].action = funcCreate(switches[k].action,'match',sourceNode);
                }
            }
        }
        switches = objectNotEmpty(switches)?switches:null;
        store = new gnr.GnrStoreQuery({'searchAttr':attributes.searchAttr,_parentSourceNode:sourceNode,switches:switches});
        store._identifier = resolverAttrs['alternatePkey'] || storeAttrs['id'] || '_pkey';
        resolverAttrs._sourceNode = sourceNode;

        var resolver = this.resolver(sourceNode,attributes,resolverAttrs,savedAttrs);
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

    mixin_clearCache:function(pkey){
        this.store.clearCache(pkey);
    },
    mixin_setCondition:function(value,kw){
        var vpath = this.sourceNode.attr.value;
        var currvalue = this.sourceNode.getRelativeData(vpath);
        var reskwargs = this.store.rootDataNode().getResolver().kwargs;
        if(reskwargs.notnull){
            reskwargs = objectUpdate({},reskwargs);
            var reskwargs = objectUpdate(reskwargs,{limit:2,_querystring:'*',notnull:true});
            var singleOption = genro.serverCall(objectPop(reskwargs,'method'),reskwargs);
            if(singleOption._value.len()==1){
                currvalue = singleOption._value.getAttr('#0')[this.store._identifier];
            }
        }
        if(!isNullOrBlank(currvalue)){
            this.clearCache();
            this.setValue(null,true);
            this.setValue(currvalue,true);
        } 

        //this.sourceNode.setRelativeData(vpath,currvalue);
    },
    
    mixin_onSetValueFromItem: function(item, priorityChange) {
        if (!item.attr.caption) {
            return;
        }
        
        if(priorityChange && !this.item){
            this.item = item;
        }
        if (this.sourceNode.editedRowIndex!=null && priorityChange) {
            this._updateSelect(item);
            //if (priorityChange) {
                //this.cellNext = 'RIGHT';
                //this.onBlur();
            //}
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
                var that = this;
                setTimeout(function(){
                    if(that.gnr._autoselectFirstOption){
                        that._popupWidget.highlightFirstOption();
                    }
                },1);
                
            });
        }else{
            dojo.connect(widget,'_openResultList',function(){                
                if(widget.gnr._autoselectFirstOption){
                    widget._popupWidget.highlightFirstOption();
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
    },
    //patch__onBlur:function(){
    //    return;
    //}
});

dojo.declare("gnr.widgets.dbBaseCombo", gnr.widgets.DynamicBaseCombo, {
    resolver:function(sourceNode,attributes,resolverAttrs,savedAttrs){
        objectUpdate(resolverAttrs,objectExtract(attributes,'dbtable,table,selectmethod,weakCondition,excludeDraft,ignorePartition,distinct,httpMethod,dbstore'));
        resolverAttrs.dbtable = resolverAttrs.dbtable || objectPop(resolverAttrs,'table');
        if('_storename' in sourceNode.attr){
            resolverAttrs._storename = sourceNode.attr._storename;
        }
        if(resolverAttrs.dbstore){
            resolverAttrs.temp_dbstore = objectPop(resolverAttrs,'dbstore')
        }
        resolverAttrs['method'] = resolverAttrs['method'] || 'app.dbSelect';
        savedAttrs['dbtable'] = resolverAttrs['dbtable'];
        sourceNode.registerSubscription('changeInTable',sourceNode,function(kw){
            if(this.attr.dbtable==kw.table){
                this.widget.clearCache(kw.pkey);
            }
        });
        return new gnr.GnrRemoteResolver(resolverAttrs, true, 0);
    },
    mixin_setDbtable:function(value) {
        this.store.rootDataNode()._resolver.kwargs.dbtable = value;
    }

});


dojo.declare("gnr.widgets.LocalBaseCombo", gnr.widgets.DynamicBaseCombo, {
    resolver:function(sourceNode,attributes,resolverAttrs){
        objectUpdate(resolverAttrs,objectExtract(attributes,'kw_*'));
        var callback = objectPop(attributes,'callback');
        if(callback){
            var callback = funcCreate(callback,'kw');
            resolverAttrs.method = function(kw){
                var envelope = new gnr.GnrBag();
                var result = new gnr.GnrBag();
                var resultObj = callback.call(this,kw);
                var headers = resultObj.headers;
                var rows = resultObj.data || [];
                var i = 0;
                rows.forEach(function(r){
                    result.setItem('r_'+i,null,r);
                    i++;
                })
                var resultAttr = {};
                if(headers){
                    var columnslist = [];
                    var headerslist = [];
                    headers.split(',').forEach(function(c){
                        c = c.split(':');
                        columnslist.push(c[0]);
                        headerslist.push(c[1]);
                    })
                    resultAttr.columns = columnslist.join(',');
                    resultAttr.headers = headerslist.join(',');
                }
                envelope.setItem('result',result,resultAttr);
                return envelope.popNode('result');
            };
        }else{
            resolverAttrs.method = funcCreate(resolverAttrs.method,'kw');
        }
        return new gnr.GnrBagCbResolver({method:objectPop(resolverAttrs,'method'),parameters:resolverAttrs},true);
    }
});


dojo.declare("gnr.widgets.RemoteBaseCombo", gnr.widgets.DynamicBaseCombo, {
    resolver:function(sourceNode,attributes,resolverAttrs){
        objectUpdate(resolverAttrs,objectExtract(attributes,'kw_*'));
        return new gnr.GnrRemoteResolver(resolverAttrs, true, 0);
    }
});


dojo.declare("gnr.widgets.FilteringSelect", gnr.widgets.BaseCombo, {
    _validatingWidget:true,

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

dojo.declare("gnr.widgets.BaseSelect", null, {
    _validatingWidget:true,
    _autoselectFirstOption:true,

    constructor: function(application) {
        this._domtag = 'div';
        this._dojotag = 'FilteringSelect';
    },
    connectForUpdate: function(widget, sourceNode) {
        dojo.connect(widget, '_setValueFromItem', widget, 'onSetValueFromItem');
        if (!("validate_select" in sourceNode.attr)) {
            sourceNode.attr.validate_select = true;
        }
        if (!("validate_select_error" in sourceNode.attr)) {
            sourceNode.attr.validate_select_error = 'Not existing value';
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
                        this.sourceNode._wrongSearch = displayedValue;
                        if(!this.sourceNode.attr.firstMatchDisabled){
                            this.setDisplayedValue(displayedValue,true);
                        }
                    }else //if(value!=lastValueReported){
                        {
                        this.setValue(value, true);
                    }
                }
            }
    },

    cell_onCreating:function(gridEditor,colname,colattr){
        if(!gridEditor.editorPars){
            return;
        }
        var cellmap = gridEditor.grid.cellmap;
        var related_setter = {};
        var grid = gridEditor.grid;
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
            var selectRow = item?objectUpdate({},item.attr):{};
            var rowNode = this.getRelativeData().getParentNode();
            var values = {}; 
            for (var k in related_setter){
                values[related_setter[k]] = selectRow[k];
            }
            grid.collectionStore().updateRow(this.editedRowIndex,values);
        }
    }
});

dojo.declare("gnr.widgets.dbSelect", [gnr.widgets.dbBaseCombo,gnr.widgets.BaseSelect], {});

dojo.declare("gnr.widgets.CallBackSelect", [gnr.widgets.LocalBaseCombo,gnr.widgets.BaseSelect], {});

dojo.declare("gnr.widgets.RemoteSelect", [gnr.widgets.RemoteBaseCombo,gnr.widgets.BaseSelect], {});


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
        if(this.sourceNode.attr.onOpeningPopup){
            this.sourceNode.attr.onOpeningPopup.call(this.sourceNode,openKw,evtDomNode);
        }
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
        if(this.sourceNode.attr.onOpenedPopup){
            this.sourceNode.attr.onOpenedPopup.call(this.sourceNode,openKw,evtDomNode);
        }
        if (dropDown.focus) {
            dropDown.focus();
        }
        // TODO: set this.checked and call setStateClass(), to affect button look while drop down is shown
    },
    patch__onBlur: function(){
        if(this.sourceNode.attr.modal){
            return;
        }
        this._onBlur_replaced();
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

             
            //gnrwdg.fakeinputNode = fakeinput.getParentNode();

             if(objectNotEmpty(uploadAttr)){
                 attr.dropTarget=true;
                 attr.dropTypes='Files,text/plain';
                 attr.drop_ext=uploadAttr.ext || this._default_ext;
                 var src=sourceNode.attr.src;
                 attr.onDrop_text_html = function(dropInfo,data){
                    console.log('texthtml',dropInfo,data)
                 }
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
                        var size_kb = uploadAttr.maxsize/1000
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
                sourceNode._('input','fakeinput',{hidden:true,type:'file',
                connect_onchange:function(evt){
                    cbOnDropData({
                        evt:evt},evt.target.files[0]);
                        this.domNode.value = null;
                    }
                });
                var uploadhandler_key = genro.isMobile? 'selfsubscribe_doubletap':'connect_ondblclick';
                attr[uploadhandler_key] = function(){
                    this.getValue().getNode('fakeinput').domNode.click();
                };
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
        var savedAttrs={'edit':edit, zoomWindow:objectPop(attributes,'zoomWindow')};   
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
        if(url.startsWith('data:')){
            return {src:url};
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
        if(v && v.startsWith('data:')){
            domnode.setAttribute('src',v);
            return;
        }
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
         this._default_ext='png,jpg,jpeg,gif,svg';
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
        this.markers_types = {};
    },
    creating: function(attributes, sourceNode) {
        var savedAttrs = objectExtract(attributes, 'map_*');
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode) {
        sourceNode.markers={};
        var that=this;
        genro.google().setGeocoder(sourceNode,function(){
                that.markers_types['default'] = google.maps.Marker;
                that.makeMap(sourceNode,savedAttrs);
        });
        sourceNode.gnr=this;
    },
    makeMap:function(sourceNode,kw){
        kw.mapTypeId=objectPop(kw,'type')||'roadmap';
        kw.zoom=kw.zoom || 8;
        var that = this;
        if(kw.center || sourceNode.attr.autoFit){
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
    clearMarkers:function(sourceNode){
        for (var k in sourceNode.markers){
            sourceNode.markers[k].setMap(null);
            delete sourceNode.markers[k];
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
        var gnr = this;
        var marker_type = objectPop(kw,'marker_type') || 'default';
        var onClick = objectPop(kw, 'onClick')
        this.onPositionCall(sourceNode,marker,function(position){
            if (position){
                kw.position=position;
                kw.title=kw.title || marker_name;
                kw.map=sourceNode.map;
                if(kw.color){
                    objectUpdate(kw,gnr._markerColorKwargs(kw.color))
                }
                sourceNode.markers[marker_name] = new gnr.markers_types[marker_type](kw);
                if (onClick){
                    sourceNode.markers[marker_name].addListener('click', function(e){onClick(marker_name, e)});
                }               
            }
        });
        if(sourceNode.attr.autoFit){
            sourceNode.delayedCall(function(){
                var bounds = new google.maps.LatLngBounds();
                for(var k in sourceNode.markers){
                    bounds.extend(sourceNode.markers[k].position);
                }
                sourceNode.map.fitBounds(bounds);
            },10,'fitBounds'); 
        }
    },


    addMarkerType:function(code,cls){
        this.markers_types[code] = cls
    },

    _markerColorKwargs:function(color,shadow){
        var result = {};
        if(color){
            result.icon = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + color,
                new google.maps.Size(21, 34),
                new google.maps.Point(0,0),
                new google.maps.Point(10, 34));
        }
        if(shadow){
            result.shadow = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_shadow",
            new google.maps.Size(40, 37),
            new google.maps.Point(0, 0),
            new google.maps.Point(12, 35));
        }
        return result;
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
        var savedAttrs = objectExtract(attributes, 'method');
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