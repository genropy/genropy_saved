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
    

gnr.columnsFromStruct = function(struct, columns){
        if (columns==undefined){
            columns = [];
        }
        if (!struct){
            return '';
        }
        var nodes = struct.getNodes();
        for (var i=0; i < nodes.length; i++){
            var node = nodes[i];
            if (node.attr['calculated']){
                continue;
            }
            var fld = node.attr.field;
            if (fld){
                if ((!stringStartsWith(fld,'$')) && (!stringStartsWith(fld,'@'))){
                    fld = '$'+fld;
                }
                arrayPushNoDup(columns,fld);
                if (node.attr.zoomPkey){
                    var zoomPkey=node.attr.zoomPkey;
                    if ((!stringStartsWith(zoomPkey,'$')) && (!stringStartsWith(zoomPkey,'@'))){
                        zoomPkey = '$'+zoomPkey;
                    }
                    arrayPushNoDup(columns,zoomPkey);
                }
            }

            if (node.getValue() instanceof gnr.GnrBag){
                gnr.columnsFromStruct(node.getValue(), columns);
            }
        }
        return columns.join(',');
    };
    
gnr.menuFromBag = function (bag, appendTo,menuclass,basepath){
    var menuline,attributes;
    var bagnodes=bag.getNodes();
    for(var i=0; i< bagnodes.length; i++){
        var bagnode = bagnodes[i];
        attributes=objectUpdate({},bagnode.attr);
        attributes.label=attributes.caption || attributes.label || bagnode.label;
        attributes.fullpath=basepath? basepath+'.'+bagnode.label : bagnode.label;
        menuline=appendTo._('menuline',attributes);
        if (bagnode.getResolver() ){
            newmenu= menuline._('menu',{fullpath:attributes.fullpath,
                                '_class':menuclass,
                               'content':bagnode.getResolver()});
        } 
        else  {
            var menucontent = bagnode.getValue();
            if (menucontent instanceof gnr.GnrBag){
                var newmenu= menuline._('menu',{'_class':menuclass});
                gnr.menuFromBag(menucontent,newmenu,menuclass,attributes.fullpath);
            }
        }
    }
};
dojo.declare("gnr.widgets.baseHtml",null,{
    _defaultValue:'',
    _defaultEvent:'onclick',
    constructor: function(application){
        this._domtag = null;
        this._dojotag = null;
        this._dojowidget = false;
    },
    
    connectChangeEvent:function(obj){
        if ('value' in obj){
            dojo.connect(obj,'onchange', this, 'onChanged');
        }
    },
    
    onChanged:function(evt){
        var domnode=evt.target;
        //genro.debug('onDomChanged:'+domnode.value);
        //domnode.sourceNode.setAttributeInDatasource('value',domnode.value);
        this._doChangeInData(domnode, domnode.sourceNode, domnode.value);
    },
    _doChangeInData:function(domnode, sourceNode, value,valueAttr){
        var valueAttr=valueAttr || null;
        var path = sourceNode.attrDatapath('value');
        genro._data.setItem(path,value,valueAttr,{'doTrigger':sourceNode});
    },
    _makeInteger: function(attributes,proplist){
        dojo.forEach(proplist,function(prop){
            if(prop in attributes){
                attributes[prop]=attributes[prop]/1;
            }
        });
    },

    _creating:function(attributes,sourceNode){
        /*receives some attributes, calls creating, updates savedAttrs and returns them*/
        var extension = objectPop(attributes,'extension');
        if(extension){
            sourceNode[extension] = new gnr.ext[extension](sourceNode);
        }
        
        this._makeInteger(attributes,['sizeShare','sizerWidth']);
        var savedAttrs = {};
        savedAttrs.connectedMenu=objectPop(attributes,'connectedMenu');
        savedAttrs.dragDrop = objectExtract(attributes,'dnd_*');
        savedAttrs.onEnter = objectPop(attributes,'onEnter');
        objectUpdate(savedAttrs, this.creating(attributes,sourceNode));
        if(sourceNode && objectNotEmpty(savedAttrs.dragDrop) && (!attributes.id)){
            attributes['id'] = sourceNode.getStringId();
            savedAttrs.dom_id = attributes['id'];
        }
        var formId = objectPop(attributes,'formId');
        if(attributes._for){
            attributes['for'] = objectPop(attributes,'_for');
        }
        if(attributes.onShow){
            attributes['onShow'] = funcCreate(attributes.onShow,'',sourceNode);
        }
        if(attributes.onHide){
            attributes['onHide'] = funcCreate(attributes.onHide,'',sourceNode);
        }
        if(sourceNode && formId){
            if(sourceNode.attr.nodeId && (sourceNode.attr.nodeId != formId)){
                alert('formId '+formId+' will replace nodeId '+ sourceNode.attr.nodeId);
            }
            var dlgId = objectPop(attributes,'dlgId');
            sourceNode.attr.nodeId = formId;
            sourceNode.defineForm(formId,sourceNode.absDatapath(),dlgId);
        }
        //Fix Colspan in Internet explorer
        if(dojo.isIE>0){
           if(attributes['colspan']){
               attributes.colSpan = attributes['colspan'];
           }
        }
        return savedAttrs;
    },
    creating:function(attributes,sourceNode){
         /*override this for each widget*/
         
         return {};
    },
    setControllerTitle:function(attributes, sourceNode){
        var iconClass = objectPop(attributes,'iconClass');
        if (iconClass) {
            if (attributes['title']) {
                attributes['title'] = '<span class="'+iconClass+'"/><span style="padding-left:20px;">'+attributes['title']+'</span>';
            }
            else{
                attributes['title'] = '<div class="'+iconClass+'"/>';
            }
        };
        if (attributes['title']) {
            var tip = objectPop(attributes,'tip');
            attributes['title'] = '<span title="'+tip+'">'+attributes['title']+'</span>';
        };
    },

    dndSettings:function(newobj, sourceNode,savedAttrs){
        var dragDrop=savedAttrs.dragDrop;
        var domNode=newobj.domNode || newobj;
        if(!domNode){ return;}
        var checkAcceptance= function(source, nodes){
            // summary: checks, if the target can accept nodes from this source
            // source: Object: the source which provides items
            // nodes: Array: the list of transferred items
            if(this == source){ 
                return true;
            } else if (source.tree){
                return true;
                //source.tree.getItemById(nodes[0].id);
            } else {
                for(var i = 0; i < nodes.length; ++i){
                    var type = source.getItem(nodes[i].id).type;
                    // type instanceof Array
                    var flag = false;
                    for(var j = 0; j < type.length; ++j){
                        if(type[j] in this.accept){
                            flag = true;
                            break;
                        }
                    }
                    if(!flag){
                        return false;   // Boolean
                    }
                }
                return true;    // Boolean
            }
        };
        if(dragDrop.source || dragDrop.target){
            var dndPars={isSource: dragDrop.source || false,
                         horizontal: dragDrop.horizontal || false,
                         copyOnly: dragDrop.copyOnly || false,
                         skipForm: dragDrop.skipForm || false,
                         withHandles: dragDrop.withHandles || false,
                         accept: dragDrop.accept ? dragDrop.accept.split(',') :[],
                         singular:(dragDrop.singular ==false)  ? false: true
                         };
            if(dragDrop.onDndDrop){
                dndPars.onDndDrop = dragDrop.onDndDrop;
            }
        sourceNode.dndSource = new dojo.dnd.Source(savedAttrs.dom_id,dndPars);
        sourceNode.dndSource.checkAcceptance =checkAcceptance;
        
    }else if(dragDrop.target){
         sourceNode.dndTarget = new dojo.dnd.Target(savedAttrs.dom_id);
         sourceNode.dndTarget.checkAcceptance=checkAcceptance;
    }else if(dragDrop.allowDrop){
            sourceNode.dndTarget = new dojo.dnd.Target(savedAttrs.dom_id);
            var checkAcceptanceFunc = funcCreate(dragDrop.allowDrop || 'return true;', 'item');
            sourceNode.dndTarget.checkAcceptance = function(source, nodes){
                if(source.tree){
                    return checkAcceptanceFunc.call(sourceNode, source.tree.getItemById(nodes[0].id));
                } else {
                    // TODO Drag from non tree source
                }
            };
        }else if(dragDrop.itemType){
            var dndSource=domNode.sourceNode.getParentNode().dndSource;
            if( dndSource){
                dojo.addClass(domNode,'dojoDndItem');
                dndSource.setItem(domNode.id, {data: null, type: dragDrop.itemType});
            }
        }
        if(dragDrop['onDrop']){
            var onDndDropFunc = funcCreate(dragDrop['onDrop'], 'item, copy');
            sourceNode.dndTarget.onDndDrop = function(source, nodes, copy){
                if(source.tree){
                    if (this==dojo.dnd.manager().target){
                        onDndDropFunc.call(sourceNode, source.tree.getItemById(nodes[0].id), copy);
                    }
                } else {
                    // TODO Drag from non tree source
                }
            };
        }
        
    },

    _created:function(newobj, savedAttrs, sourceNode, ind){
        this.created(newobj, savedAttrs, sourceNode);
        if(savedAttrs.connectedMenu){
            var menu=savedAttrs.connectedMenu;
            var domNode=newobj.domNode || newobj;
            if (typeof(menu)=='string'){
                menu=dijit.byId(menu);
            }
            if(menu){
                menu.bindDomNode(domNode);
            }
            
        }
        if(!sourceNode){
            return;
        }
        if(objectNotEmpty(savedAttrs.dragDrop)){
            this.dndSettings(newobj, sourceNode, savedAttrs);
        }

        var parentNode=sourceNode.getParentNode();
        if(parentNode.attr.tag){
              if (parentNode.attr.tag.toLowerCase()=='tabcontainer'){
                    objectFuncReplace(newobj, 'setTitle', function(title){
                        if(title){
                            if(this.controlButton){
                                this.controlButton.setLabel(title);
                            }
                        }
                    });
                }
                else if(parentNode.attr.tag.toLowerCase()=='accordioncontainer'){
                    objectFuncReplace(newobj, 'setTitle', function(title){
                        this.titleTextNode.innerHTML=title;
        
                    });
               }
        };

        if(savedAttrs.onEnter){
            var callback=dojo.hitch(sourceNode,funcCreate(savedAttrs.onEnter));
            var kbhandler=function(evt){
                if(evt.keyCode==genro.PATCHED_KEYS.ENTER){
                    evt.target.blur();
                    setTimeout(callback,100);
                }
            };
            var domnode=newobj.domNode || newobj;
            dojo.connect(domnode,'onkeypress',kbhandler);
        };
        dojo.connect(newobj,'onfocus',function(e){
           genro.currentFocusedElement=newobj.domNode || newobj;
         });
     },
     created:function(newobj, savedAttrs, sourceNode){
         /*override this for each widget*/
         return null;
     }
});

dojo.declare("gnr.widgets.iframe",gnr.widgets.baseHtml,{
    creating:function(attributes, sourceNode){
        sourceNode.savedAttrs = objectExtract(attributes,'rowcount,tableid,src,rpcCall,onLoad');
        var condFunc= objectPop(attributes,'condition_function');
        var condValue= objectPop(attributes,'condition_value');
        if (condFunc){
            sourceNode.condition_function = funcCreate(condFunc, 'value');
        }
        return sourceNode.savedAttrs;
    },
    created:function(newobj, savedAttrs, sourceNode){
        if (savedAttrs.rowcount && savedAttrs.tableid){
            
            var rowcount = savedAttrs.rowcount;
            var tableid = savedAttrs.tableid;
            var fnc = dojo.hitch(newobj, function(){
                var nlines = 0;
                var tbl = this.contentDocument.getElementById(tableid);
                if(tbl){
                    nlines = tbl.rows.length;
                } 
                genro.setData(rowcount, nlines);
            });
            dojo.connect(newobj, 'onload', fnc);

        }
        if (savedAttrs.onLoad){
            dojo.connect(newobj, 'onload', funcCreate(savedAttrs.onLoad));
        }
        this.setSrc(newobj, savedAttrs.src);
    },
    prepareSrc:function(domnode){
        var sourceNode = domnode.sourceNode;
        var attributes = sourceNode.attr;
        if(attributes['src']){
            return attributes['src'];
        }else if(attributes['rpcCall']){
            params=objectExtract(attributes,'rpc_*', true);
            params.mode= params.mode? params.mode:'text';
            return genro.remoteUrl(attributes['rpcCall'],params, sourceNode, false);
            
        }
    },
    set_print:function(domnode,v,kw){
        genro.dom.iFramePrint(domnode);
    },
    set_if:function(domnode,v,kw){
        domnode.gnr.setSrc(domnode);
    },
    setCondition_value:function(domnode,v,kw){
        domnode.sourceNode.condition_value=v;
        domnode.gnr.setSrc(domnode);
    },
    set_reloader:function(domnode,v,kw){
        domnode.gnr.setSrc(domnode);
    },
    setSrc:function(domnode, v, kw){
        var sourceNode = domnode.sourceNode;
        if(sourceNode.attr._if && !sourceNode.getAttributeFromDatasource('_if')){
             var v='';
        }else if(sourceNode.condition_function && !sourceNode.condition_function(sourceNode.condition_value)){
            var v='';
        }
        else{
            var v = v || this.prepareSrc(domnode);
        }
        if (sourceNode.currentSetTimeout){
            clearTimeout(sourceNode.currentSetTimeout);
        }
        sourceNode.currentSetTimeout = setTimeout(function(d,url){
                                              var absUrl = document.location.protocol+'//'+document.location.host+url;
                                               if (absUrl!=d.src){
                                                   d.src = url;
                                               }
                                           }, sourceNode.attr.delay || 1 ,domnode,v);
    }
});

dojo.declare("gnr.widgets.baseDojo",gnr.widgets.baseHtml,{
    _defaultEvent:'onClick',
    constructor: function(application){
        this._domtag = 'div';
        this._dojowidget = true;
    },
    _doChangeInData:function(domnode, sourceNode, value, valueAttr){
        /*if(value==undefined){
            sourceNode.widget._isvalid = false;
            }*/
        if(sourceNode._modifying){ // avoid recursive _doChangeInData when calling widget.setValue in validations
            
            return;
        }
        var path = sourceNode.attrDatapath('value');
        var oldvalue=genro._data.getItem(path);
        if (oldvalue==value){
            return;
        }
        var validateresult;
        var valueAttr=valueAttr || null;
        if(sourceNode.hasValidations()){
            validateresult = sourceNode.validationsOnChange(sourceNode, value);
            value = validateresult['value'];
            /*if((validateresult['error']) || (objectNotEmpty(validateresult['warnings']))){
                setTimeout(function(){sourceNode.widget.focus();}, 1);
            }*/ 
        }
        value = this.convertValueOnBagSetItem(sourceNode,value);
        genro._data.setItem(path, value, valueAttr, {'doTrigger':sourceNode});
    },
    mixin_setTip: function (tip) {
        this.setAttribute('title',tip);
    },
    convertValueOnBagSetItem: function(sourceNode, value){
        return value;
    },
    validatemixin_validationsOnChange: function(sourceNode, value){
        var result = genro.vld.validate(sourceNode, value,true);
        if(result['modified']){
            sourceNode._modifying = true;
            sourceNode.widget.setValue(result['value']);
            sourceNode._modifying = false;
        }
        sourceNode.setValidationError(result);
        var formHandler = sourceNode.getFormHandler();
        if(formHandler){
            formHandler.updateInvalidField(sourceNode, sourceNode.attrDatapath('value'));
        }
        return result;
    },
    mixin_mainDomNode: function(){
        return this.inputNode || this.textInputNode || this.domNode;
    },
    connectChangeEvent:function(widget){
        if ('onChange' in widget ){
            dojo.connect(widget,'onChange', dojo.hitch(this,function(val){this.onChanged(widget,val);}));
        }
    },
    onChanged:function(widget, value){
        //genro.debug('onChanged:'+value);
        //widget.sourceNode.setAttributeInDatasource('value',value);
        this._doChangeInData(widget.domNode, widget.sourceNode, value);
        
    },
    setUrlRemote: function(widget, method, arguments){
        var url = genro.rpc.rpcUrl(method, arguments);
        widget.setHref(url);
    },
    mixin_setVisible: function(visible){
        dojo.style(this.domNode,'visibility',(visible? 'visible':'hidden'));
    },

    mixin_setHidden: function(hidden){
        dojo.style(this.domNode,'display',(hidden? 'none':''));
    },
    mixin_setSizeShare: function(value){
        this.sizeShare = value;
        dijit.byId(this.domNode.parentNode.id).layout();
    }
    // Removed to avoid conflicts with 1.2. Check if we can survive without it
  // mixin_setDisabled: function(value){
  //     var value=value? true:false;
  //     this.setAttribute('disabled', value);
  // }

});
dojo.declare("gnr.widgets.Dialog",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._attachTo = 'mainWindow';
        this._domtag = 'div';
        this._dojotag = 'Dialog';
    },
    
    creating:function(attributes, sourceNode){
        objectPop(attributes,'parentDialog');
        var closable = ('closable' in attributes) ? objectPop(attributes,'closable') : true;
        attributes.title = attributes.title || '';
        if (!closable){
            attributes.templateString = "<div class=\"dijitDialog\" tabindex=\"-1\" waiRole=\"dialog\" waiState=\"labelledby-${id}_title\">\n\t<div dojoAttachPoint=\"titleBar\" class=\"dijitDialogTitleBar\">\n\t<span dojoAttachPoint=\"titleNode\" class=\"dijitDialogTitle\" id=\"${id}_title\">${title}</span>\n\t</div>\n\t\t<div dojoAttachPoint=\"containerNode\" class=\"dijitDialogPaneContent\"></div>\n</div>\n";
        } else if (closable=='ask'){
            attributes.templateString = "<div class=\"dijitDialog\" tabindex=\"-1\" waiRole=\"dialog\" waiState=\"labelledby-${id}_title\">\n\t<div dojoAttachPoint=\"titleBar\" class=\"dijitDialogTitleBar\">\n\t<span dojoAttachPoint=\"titleNode\" class=\"dijitDialogTitle\" id=\"${id}_title\">${title}</span>\n\t<span dojoAttachPoint=\"closeButtonNode\" class=\"dijitDialogCloseIcon\" dojoAttachEvent=\"onclick: onAskCancel\">\n\t\t<span dojoAttachPoint=\"closeText\" class=\"closeText\">x</span>\n\t</span>\n\t</div>\n\t\t<div dojoAttachPoint=\"containerNode\" class=\"dijitDialogPaneContent\"></div>\n</div>\n";

            sourceNode.closeAttrs = objectExtract(attributes,'close_*');
        }
    },
    created:function(newobj, savedAttrs, sourceNode){
        dojo.connect(newobj,"show",newobj,
                    function(){
                        if (this!=genro.dialogStack.slice(-1)[0]) {
                            genro.dialogStack.push(this);
                            if (genro.dialogStack.length>1) {
                                genro.dialogStack.slice(-2)[0].hide();
                            }
                        }
                    });
        dojo.connect(newobj,"hide",newobj,
                    function(){ 
                            if (this==genro.dialogStack.slice(-1)[0]) {
                                    genro.dialogStack.pop();
                                    if (genro.dialogStack.length>0) {
                                        genro.dialogStack.slice(-1)[0].show();
                                    }}});
    },

    attributes_mixin_onAskCancel:function(){
        var closeAttrs = this.sourceNode.closeAttrs;
        var _this = this;
        var closeAction;
        if (closeAttrs.action){
            closeAction = dojo.hitch(this.sourceNode,funcCreate(closeAttrs.action));
        } else {
            closeAction = dojo.hitch(this, 'onCancel');
        }
        genro.dlg.ask('',closeAttrs['msg'],{confirm:closeAttrs['confirm'],
                      cancel:closeAttrs['cancel']},{confirm:closeAction, cancel:''});
    },
    mixin_setTitle:function(title){
        this.titleNode.innerHTML = title;
    }

});
dojo.declare("gnr.widgets.Editor",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'textarea';
    },
    creating:function(attributes, sourceNode){
        dojo.require("dijit._editor.plugins.AlwaysShowToolbar");
        dojo.require("dijit._editor.plugins.FontChoice"); 
        dojo.require("dijit._editor.plugins.TextColor");
        dojo.require("dijit._editor.plugins.LinkDialog");
        var extraPlugins=objectPop(attributes,'extraPlugins');
        var disabled=objectPop(attributes,'disabled');
        if (extraPlugins){
            attributes.extraPlugins=extraPlugins.split(',');
        }
    },
   // mixin_setDisabled:null, // removed as SetDisabled was removed in dojoBase
    created:function(newobj, savedAttrs, sourceNode){
        if (sourceNode.attr['disabled']) {
            var disabled = sourceNode.getAttributeFromDatasource('disabled') ;
            if (disabled){
                setTimeout(function(){newobj.setDisabled(true);},10);
            }
        };
        if (sourceNode.attr['value']) {
            var value = sourceNode.getAttributeFromDatasource('value');
            if (value!=null){
                newobj.setValue(value);
            }
        };
    }
});

dojo.declare("gnr.widgets.SimpleTextarea",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'textarea';
    },
    creating:function(attributes, sourceNode){
        var savedAttrs = objectExtract(attributes,'value');
        return savedAttrs;
    },
    created:function(newobj, savedAttrs, sourceNode){
        if (savedAttrs.value) {
            newobj.setValue(savedAttrs.value);
        };
        dojo.connect(newobj.domNode,'onchange',dojo.hitch(this,function(){this.onChanged(newobj);}));
    },
    onChanged:function(widget){
        var value=widget.getValue();
        this._doChangeInData(widget.domNode, widget.sourceNode, value);
        
    }
});

dojo.declare("gnr.widgets.ProgressBar",gnr.widgets.baseDojo,{
    mixin_setProgress: function(value){
        if (value == undefined){value = null;}
        this.update({'progress':value, 'indeterminate':(value==null)});
    },
    mixin_setIndeterminate: function(value){
        if (value!=null){
            this.update({'indeterminate':value});
        }
    },
    mixin_setMaximum: function(value){
        this.update({'maximum':value});
    },
    mixin_setPlaces: function(value){
        this.update({'places':value});
    }
    
});

dojo.declare("gnr.widgets.StackContainer",gnr.widgets.baseDojo,{
    creating:function(attributes, sourceNode){
        var savedAttrs = objectExtract(attributes,'selected');
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
        var selpath=sourceNode.attr.selected;
        widget.gnrPageDict={};
        if(selpath){
            var controller=widget.tablist || widget;
            var evt = (controller == widget) ? 'selectChild' :'onSelectChild';
            dojo.connect(controller, evt, dojo.hitch(widget,function(child){
                            if(!widget.sourceNode._isBuilding){
                                this.sourceNode.setRelativeData(selpath,this.getChildIndex(child));
                            }
                        }));
            dojo.connect(widget,'addChild',dojo.hitch(this,'onAddChild',widget));
            dojo.connect(widget,'removeChild',dojo.hitch(this,'onRemoveChild',widget));
        }
        
    },
    mixin_setSelected:function(p){
        this.selectChild(this.getChildren()[p||0]);
    },
    mixin_setSelectedPage:function(pageName){
        if( this.gnrPageDict[pageName]){
            this.selectChild(this.gnrPageDict[pageName]);
        }        
    },
        
    mixin_getChildIndex:function(obj){
        return dojo.indexOf(this.getChildren(),obj);
    },

    onAddChild:function(widget,child){
        var pageName=child.sourceNode.attr.pageName;
        if (pageName){
            widget.gnrPageDict[pageName]=child;
        }
    },
    onRemoveChild:function(widget,child){
        var pageName=child.sourceNode.attr.pageName;
        if (pageName ){
            objectPop(widget.gnrPageDict,pageName);
        }
    }
    
});

dojo.declare("gnr.widgets.TabContainer",gnr.widgets.StackContainer,{
    ___created: function(widget, savedAttrs, sourceNode){
       // dojo.connect(widget,'addChild',dojo.hitch(this,'onAddChild',widget));
    },
    ___onAddChild:function(widget,child){
       }
});
dojo.declare("gnr.widgets.BorderContainer",gnr.widgets.baseDojo,{
    creating: function(attributes, sourceNode){
        if (dojoversion!='1.1'){
            attributes.gutters=attributes.gutters || false;
        }
        this.setControllerTitle(attributes, sourceNode);
    },
    created: function(widget, savedAttrs, sourceNode){
        dojo.connect(widget,'startup',dojo.hitch(this,'afterStartup',widget));
        if (dojoversion=='1.7'){
            dojo.connect(widget,'addChild',dojo.hitch(this,'onAddChild',widget));
        }
    },
    afterStartup:function(widget){
        var sourceNode=widget.sourceNode;
        if (dojoversion!='1.7'){
            widget._splitterConnections={};
            var region,splitter;
            for (region in widget._splitters){
                if (!widget._splitterConnections[region]){
                    //splitter=widget.getSplitter(region);
                    splitter = dijit.byNode(widget._splitters[region]);
                    widget._splitterConnections[region]=dojo.connect(splitter,'_stopDrag',dojo.hitch(this,'onSplitterStopDrag',widget,splitter));
                }
            }
        }
        if (sourceNode.attr.regions){
            var regions=sourceNode.getRelativeData(sourceNode.attr.regions);
            if(!regions){
                regions=new gnr.GnrBag();
                sourceNode.setRelativeData(sourceNode.attr.regions,regions);
            }
            var regions=regions.getNodes();
            for (var i=0; i < regions.length; i++) {
                widget.setRegions(null,{'node':regions[i]});
            };
        }

    },
   /* onAddChild:function(widget,child){
        var splitter=widget._splitters[child.region];
        if(splitter){
            splitter=dijit.getEnclosingWidget(splitter);
            dojo.connect(splitter,'_stopDrag',dojo.hitch(this,'onSplitterStopDrag',widget,splitter));
        }
    },*/
    onSplitterStopDrag:function(widget,splitter){
        var sourceNode=widget.sourceNode;
        if (sourceNode.attr.regions){
            var region=splitter.region;
            var regions = sourceNode.getRelativeData(sourceNode.attr.regions);
            var value=splitter.child.domNode.style[splitter.horizontal ? "height" : "width"];
            regions.setItem(region,value,null,{'doTrigger':sourceNode});
        }
    },
    mixin_setRegions:function(value,kw){
        var region=kw.node.label;
        if (('_'+region) in this){
            var size = kw.node.getValue();
            if(size){
                this['_'+region].style[this.horizontal ? "height" : "width"] = size;
                this._layoutChildren();
            }
        }
        if('show' in kw.node.attr){
            this.showHideRegion_one(region,kw.node.attr.show);
        }
    },
    mixin_getRegionVisibility: function(region){
        return (this._splitterThickness[region]!=0);
    },

    mixin_showHideRegion: function(region, show){
        var regions=region.split(',');
        for (var i=0; i < regions.length; i++) {
           show = this.showHideRegion_one(regions[i],show);
        };
        return show;
    },
    mixin_showHideRegion_one: function(region, show){
        if(this._splitters[region]){
            this._computeSplitterThickness(region);
        }
        var regionNode = this['_'+region];
        if (regionNode){
            if(show=='toggle'){
                show = (this._splitterThickness[region]==0);
            }
            var disp=show? '':'none';
            var splitterNode = this._splitters[region];
            if (splitterNode){
                var tk=this._splitterThickness['_'+region] || this._splitterThickness[region];
                this._splitterThickness['_'+region]=tk;
                this._splitterThickness[region] =show? tk : 0;
                var st=dojo.style(splitterNode,'display',disp);
            }
            dojo.style(regionNode,'display',disp);
            this._layoutChildren();
        }
        return show;
    }
});

dojo.declare("gnr.widgets.FloatingPane",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'FloatingPane';
    }
});   
dojo.declare("gnr.widgets.Menuline",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = '*';
        this._dojotag = 'MenuItem';
        this._basedojotag = 'MenuItem';
    },
    creating:function(attributes, sourceNode){
        var savedAttrs = {};
        objectPop(attributes,'action');
        if (sourceNode.attr.label=='-'){
            this._dojotag = 'MenuSeparator';
        }
        else{
            if (sourceNode.getResolver()){
                this._dojotag = 'PopupMenuItem';
            } 
            else {
                var content=sourceNode.getValue();
                if (content instanceof gnr.GnrBag && content.len()>0 ){
                    this._dojotag ='PopupMenuItem';
                }else{
                    this._dojotag = 'MenuItem';
                }
            }
        }
        return savedAttrs;
    },
    mixin_addChild: function(popUpContent){   
        //called for submenu
        if(popUpContent.declaredClass =='dijit.Menu'){
            this.popup=popUpContent;
        }
        if (this.addChild_replaced){
            this.addChild_replaced.call(this,popUpContent);
        }
    },
    patch_onClick:function(){
        var originalTarget=this.getParent().originalContextTarget;
        var ctxSourceNode;
        var sourceNode=this.sourceNode;
        if (!originalTarget){
            ctxSourceNode=sourceNode;
        }else{
            if (originalTarget.sourceNode){
                ctxSourceNode= originalTarget.sourceNode;
            }
            else {
                ctxSourceNode=dijit.getEnclosingWidget(originalTarget).sourceNode;
            }
        }
       // var ctxSourceNode = originalTarget ? originalTarget.sourceNode || dijit.byId(originalTarget.attributes.id.value).sourceNode :sourceNode
        var inAttr=sourceNode.getInheritedAttributes();
        var action=inAttr.action;
        f=funcCreate(action);
        if (f){
            f.call(sourceNode,sourceNode.getAttr(),ctxSourceNode);
        }
        var selattr=objectExtract(inAttr,'selected_*',true);
        if(ctxSourceNode){
            selattr=objectUpdate(selattr,objectExtract(ctxSourceNode.getInheritedAttributes(),'selected_*',true));
        }
        for (var sel in selattr){
             ctxSourceNode.setRelativeData(selattr[sel],sourceNode.attr[sel],null,null,sourceNode);
        }
        if (inAttr.selected){
             ctxSourceNode.setRelativeData(inAttr.selected, sourceNode.label,null,null,sourceNode);
        }
    }
});
dojo.declare("gnr.widgets.ContentPane",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'ContentPane';
    },
    creating:function(attributes, sourceNode){
        attributes.isLoaded=true;
        this.setControllerTitle(attributes, sourceNode);
    }
});

dojo.declare("gnr.widgets.Menu",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = '*';
        this._dojotag = 'Menu';
    },
    creating:function(attributes, sourceNode){
        var savedAttrs = objectExtract(attributes, 'modifiers,validclass,storepath');
        if(!attributes.connectId){
            savedAttrs['connectToParent']=true;
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
        if (savedAttrs.storepath){
            var contentNode=genro.getDataNode(sourceNode.absDatapath(savedAttrs.storepath));
            if(contentNode){
                var content=contentNode.getValue('static');
                //var content=sourceNode.getRelativeData(savedAttrs.storepath);
                if (content){
                    var menubag=new gnr.GnrDomSource();
                    gnr.menuFromBag(content,menubag,sourceNode.attr._class);
                    sourceNode.setValue(menubag,false);
                }else if(contentNode.getResolver()){
                    sourceNode.setResolver(contentNode.getResolver());
                }
            }
        }
        
        if(sourceNode && savedAttrs['connectToParent']){
            var parentNode=sourceNode.getParentBag().getParentNode();
            var parentWidget = parentNode.widget;
            if(parentWidget){
                if(!(('dropDown' in  parentWidget)||('popup' in parentWidget ))){
                    widget.bindDomNode(parentWidget.domNode); 
                }
            }else if (parentNode.domNode) {
                widget.bindDomNode(parentNode.domNode); 
            }else{
                widget.bindDomNode(dojo.byId(genro.domRootName));
            }
            if (parentNode.attr.tag !='menuline'){
                sourceNode.stopInherite=true;
            }
        }
        
        dojo.connect(widget,'onOpen',function(){genro.dom.addClass(document.body, 'openingMenu');});
        dojo.connect(widget,'onClose',function(){genro.dom.removeClass(document.body, 'openingMenu');});
        widget.modifiers = savedAttrs['modifiers'];
        widget.validclass = savedAttrs['validclass'];
    
    
    },
   
    patch__contextMouse: function (e){
        this.originalContextTarget=e.target;
        var sourceNode=this.sourceNode;
        if (sourceNode){
            var resolver=sourceNode.getResolver();
            if (resolver && resolver.expired()){
                var result=sourceNode.getValue('notrigger');
                if ( result instanceof gnr.GnrBag){
                    var menubag=new gnr.GnrDomSource();
                    gnr.menuFromBag(result,menubag,sourceNode.attr._class,sourceNode.attr.fullpath);
                    sourceNode.setValue(menubag);
                }else{
                    sourceNode.setValue(result);
                }
            }
        }
        if((e.button==2) && (!this.modifiers)){
            this._contextMouse_replaced.call(this,e);
        }
        else if(this.modifiers && genro.wdg.filterEvent(e, this.modifiers, this.validclass)){
            this._contextMouse_replaced.call(this,e);
            this._openMyself_replaced.call(this,e);
        }
    },
    patch__openMyself: function (e){
        if((e.button==2)&&(!this.modifiers)){
            this._openMyself_replaced.call(this,e);
        }
   },
   patch__openPopup: function (e){
        var sourceNode=this.focusedChild.popup.sourceNode;
        if (sourceNode){
            var resolver=sourceNode.getResolver();
            if (resolver && resolver.expired()){
                    var result=sourceNode.getValue('notrigger');
                    if ( result instanceof gnr.GnrBag){
                        var menubag=new gnr.GnrDomSource();
                        gnr.menuFromBag(result,menubag,sourceNode.attr._class,sourceNode.attr.fullpath);
                        sourceNode.setValue(menubag);
                    }else{
                        sourceNode.setValue(result);
                    }
                    this.focusedChild.popup=sourceNode.widget;
            }
        }

        this.focusedChild.popup.originalContextTarget=this.originalContextTarget;
        this._openPopup_replaced.call(this,e);
    }

});

dojo.declare("gnr.widgets.Tooltip",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = '*';
        this._dojotag = 'Tooltip';
    },
    creating:function(attributes, sourceNode){
        var callback= objectPop(attributes,'callback');
        if (callback){
            attributes['label']=funcCreate(callback,'n',sourceNode);
        }
        var savedAttrs = objectExtract(attributes, 'modifiers,validclass');
        if( ! attributes.connectId){
            savedAttrs['connectToParent']=true;
        }
        return savedAttrs;
    },

    created: function(widget, savedAttrs, sourceNode){
        widget.modifiers = savedAttrs['modifiers'];
        widget.validclass = savedAttrs['validclass'];
        if(sourceNode && savedAttrs['connectToParent']){
            var parentNode=sourceNode.getParentBag().getParentNode();
            var domnode=parentNode.domNode || parentNode.widget.domNode;
            widget.connectOneNode(domnode);
        }
    },

    patch__onHover: function(/*Event*/ e){
         if (genro.wdg.filterEvent(e, this.modifiers, this.validclass)){
             this._onHover_replaced.call(this,e);
         }
    },
    patch_postCreate: function(){
        if (dojoversion=='1.1'){
            if(this.srcNodeRef){this.srcNodeRef.style.display = "none";}
        }else{
            dojo.addClass(this.domNode,"dijitTooltipData");
        }
        
        this.connectAllNodes(this.connectId);
    },
    mixin_connectAllNodes:function(nodes){
        var node;
        this._connectNodes = [];
        dojo.forEach(nodes, function(node) {
            if (typeof(node) == 'string'){
                node = dojo.byId(node);
            }
            this.connectOneNode(node);
        });
    },
    mixin_connectOneNode:function(node){
        this._connectNodes.push(node);
        var eventlist;
        if (dojoversion=='1.1'){
            eventlist = ["onMouseOver", "onMouseOut", "onFocus", "onBlur", "onHover", "onUnHover"];
        }else{
            eventlist = ["onMouseEnter", "onMouseLeave", "onFocus", "onBlur"];
        }

        dojo.forEach( eventlist, function(evt){
            this.connect(node, evt.toLowerCase(), "_"+evt);
            }, this);
        if(dojo.isIE){
            // BiDi workaround
            node.style.zoom = 1;
        }
    }
    
});

dojo.declare("gnr.widgets.Button",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag='Button';
    },
    creating:function(attributes, sourceNode){
        var buttoNodeAttr = 'height,width,padding';
        var savedAttrs = objectExtract(attributes, 'fire_*');
        savedAttrs['_style'] = genro.dom.getStyleDict(objectExtract(attributes,buttoNodeAttr));
        savedAttrs['action'] = objectPop(attributes, 'action');
        savedAttrs['fire'] = objectPop(attributes, 'fire');
        return savedAttrs;
        
        
    },
    created: function(widget, savedAttrs, sourceNode){
        dojo.connect(widget, 'onClick', sourceNode, this.onClick);
        objectExtract(sourceNode._dynattr, 'fire_*');
        objectPop(sourceNode._dynattr, 'fire');
        if(savedAttrs['_style']){
            var buttonNode = dojo.query(".dijitButtonNode", widget.domNode)[0];
            dojo.style(buttonNode,savedAttrs['_style']);
        }
    },
    onClick:function(e){
        var action = this.getInheritedAttributes().action;
        if (action){
            //funcCreate(action).call(this,e);
            funcApply(action, objectUpdate(this.currentAttributes(),{event:e}), this);
        }
        if (this.attr.fire){
            var s=eventToString(e) || true;
            this.setRelativeData(this.attr.fire, s, null, true);
        }
        var fire_list = objectExtract(this.attr, 'fire_*', true);
        for (var fire in fire_list){
            this.setRelativeData(fire_list[fire], fire, null, true);
        }

    }
});

dojo.declare("gnr.widgets.Calendar",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag='Calendar';
    },
    creating:function(attributes, sourceNode){
        var storepath = sourceNode.absDatapath(objectPop(attributes,'storepath'));
        sourceNode.registerDynAttr('storepath',storepath);
//      attributes.storebag=genro.getDataNode(storepath,true,new gnr.GnrBag()).getValue();
    },
    created: function(widget, savedAttrs, sourceNode){
        var bagnodes = widget.getStorebag().getNodes();
        for (i=0; i < bagnodes.length; i++){
            widget.setCalendarEventFromBagNode(bagnodes[i]);
        }
    },
    mixin_setStorepath: function(val,kw){
        if (kw.evt=='ins')
        {
            this.setCalendarEventFromBagNode(kw.node);
        }
        else if (kw.evt=='upd'){
            var bagnodes = this.getStorebag().getNodes();
            this.emptyCalendar();
            for (i=0; i < bagnodes.length; i++){
                this.setCalendarEventFromBagNode(bagnodes[i]);
            }
        }
        
    },
    mixin_getStorebag: function(){
        var storepath=this.sourceNode.absDatapath(this.sourceNode.attr['storepath']);
        var storebag=genro.getData(storepath);
        if (!storebag) {
            storebag=new gnr.GnrBag();
            genro.setData(storepath,storebag);
            }
        return storebag;
    }
    ,
    mixin_setCalendarEventFromBagNode: function(node){
        var event_record=node.attr;
        //var event_type=objectPop(node.attr,'event_type');
        //event_record.start_time=dojo.date.stamp.toISOString(objectPop(node.attr,'starttime'))
        //event_record.end_time=dojo.date.stamp.toISOString(objectPop(node.attr,'endtime'))
        //var event_attr=objectExtract(node.attr,'event_*');
        //event_record.event_type=event_type.split(',');
        //event_record.attributes=event_attr;
        this.addCalendarEntry(node.attr.date,event_record);
    },
    patch_onValueChanged: function(date,mode){
        var bagnodes = this.getStorebag().getNodes();
        for (i=0; i < bagnodes.length; i++){
            this.setCalendarEventFromBagNode(bagnodes[i]);
        }
    },
    patch_onChangeEventDate: function(item_id,newDate){
        //this.getStorebag().getNode(item_id).attr.date.setYear(newDate.getFullYear());
        //this.getStorebag().getNode(item_id).attr.date.setMonth(newDate.getMonth());
        this.getStorebag().getNode(item_id).attr.date.setDate(newDate.getDate());
    },
    patch_onChangeEventTime: function(item,newDate){
        var bagnodes = this.getStorebag().getNodes();
        for (i=0; i < bagnodes.length; i++){
            this.setCalendarEventFromBagNode(bagnodes[i]);
        }
    },
    patch_onChangeEventDateTime: function(item,newDate,newTime){
        var bagnodes = this.getStorebag().getNodes();
        for (i=0; i < bagnodes.length; i++){
            this.setCalendarEventFromBagNode(bagnodes[i]);
        }
    }
});
dojo.declare("gnr.widgets.ToggleButton",gnr.widgets.baseDojo,{
    created: function(widget, savedAttrs, sourceNode){
        if(sourceNode.hasDynamicAttr('value')){
            var value=sourceNode.getAttributeFromDatasource('value');
            //widget.setChecked(value);
            widget.setAttribute('checked',value);
        }
    },
    mixin_setValue: function(/*String*/ value,pc){
        //this.setChecked(value,pc);
        this.setAttribute('checked',pc);
    }
});

dojo.declare("gnr.widgets.RadioButton",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag='RadioButton';
    },
    creating:function(attributes, sourceNode){
        var savedAttrs = objectExtract(attributes, 'action,callback');
        var label=objectPop(attributes,'label');
        attributes.name=objectPop(attributes,'group');
        if(label){
            attributes['id'] = attributes['id'] || 'id_'+ sourceNode._id;
            savedAttrs['label']=label;
            savedAttrs['labelattrs']=objectExtract(attributes,'label_*');
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
          var label= savedAttrs['label'];
          if(label){
              var labelattrs=savedAttrs['labelattrs'];
              labelattrs['for'] = widget.id;
              labelattrs['margin_left']=labelattrs['margin_left'] || '3px';
              var domnode = genro.wdg.create ('label',widget.domNode.parentNode, labelattrs );
              domnode.innerHTML = label;
          }
      },
      patch_onClick:function(e){
          var action = this.sourceNode.getInheritedAttributes().action;
          if (action){
              dojo.hitch(this.sourceNode,funcCreate(action))(this.sourceNode.attr,this.sourceNode,e);
          }
      },
      patch_setValue: function(/*String*/ value,pc){
          if(value == null){ value = ""; }
             this.setAttribute('checked',value);
      }
});

dojo.declare("gnr.widgets.CheckBox",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag='CheckBox';
    },
    creating:function(attributes, sourceNode){
        var savedAttrs = objectExtract(attributes, 'action,callback');
        var label=objectPop(attributes,'label');

        if(label){
            attributes['id'] = attributes['id'] || 'id_'+ sourceNode._id;
            savedAttrs['label']=label;
            savedAttrs['labelattrs']=objectExtract(attributes,'label_*');
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
        var label= savedAttrs['label'];
        if(label){
            var labelattrs=savedAttrs['labelattrs'];
            labelattrs['for'] = widget.id;
            labelattrs['margin_left']=labelattrs['margin_left'] || '3px';
            var domnode = genro.wdg.create ('label', widget.domNode.parentNode,labelattrs);
            domnode.innerHTML = label;
        }
        if(sourceNode.hasDynamicAttr('value')){
            var value=sourceNode.getAttributeFromDatasource('value');
            //widget.setChecked(value);
            widget.setAttribute('checked',value);
        }
    },
    mixin_displayMessage:function(){
        //patch
    },
    patch_onClick:function(e){
       //if(this.sourceNode._dynattr && this.sourceNode._dynattr.value){
       //    this.sourceNode.setAttributeInDatasource('value',this.checked)
       //}
        var action = this.sourceNode.getInheritedAttributes().action;
        if (action){
            dojo.hitch(this,funcCreate(action))(this.sourceNode.attr,this.sourceNode,e);
            //funcCreate(action)(this.sourceNode.attr,this.sourceNode,e);
        }
    },
    patch_setValue: function(/*String*/ value,pc){
        //this.setChecked(value);
        this.setAttribute('checked',value);
    }
});

dojo.declare("gnr.widgets.TextArea_",gnr.widgets.baseDojo,{
    constructor: function(){
          this._domtag = 'textarea';
          this._dojotag='TextArea';
      },
     creating: function(attributes, sourceNode){
        var x=1;
     },
     created: function(widget, savedAttrs, sourceNode){
         var x=1;
     }
});
dojo.declare("gnr.widgets.DateTextBox",gnr.widgets.baseDojo,{
    
    onChanged:function(widget, value){
        //genro.debug('onChanged:'+value);
        //widget.sourceNode.setAttributeInDatasource('value',value);
        if (value){
            this._doChangeInData(widget.domNode, widget.sourceNode, value,{dtype:'D'});
        }
        else {
            this._doChangeInData(widget.domNode, widget.sourceNode, null);
        }
    },
    
    constructor: function(){
        this._domtag = 'input';
        this._dojotag='DateTextBox';
    },
    creating: function(attributes, sourceNode){
        
        if('popup' in attributes && (objectPop(attributes,'popup')==false)){
            attributes.popupClass=null;
        }
        
    }

        
});
dojo.declare("gnr.widgets.TextBox",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'input';
        this._dojotag='ValidationTextBox';
    },
    /*mixin_displayMessage: function(message){
        //genro.dlg.message(message, null, null, this.domNode)
        genro.setData('_pbl.errorMessage', message)
    },*/
    creating: function(attributes, sourceNode){
        var savedAttrs = {};
        attributes.trim = (attributes.trim == false) ? false : true;
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
        this.connectFocus(widget, savedAttrs, sourceNode);
    },
    connectFocus: function(widget, savedAttrs, sourceNode){
        if(sourceNode.attr._autoselect){
            dojo.connect(widget,'onFocus', widget, function(e){
                                        setTimeout(dojo.hitch(this, 'selectAllInputText'), 1);
                                    });
        }
    },
    mixin_selectAllInputText: function(){
        dijit.selectInputText(this.focusNode);
    }


});
dojo.declare("gnr.widgets.TimeTextBox",gnr.widgets.baseDojo,{
    onChanged:function(widget, value){
        if (value){
        this._doChangeInData(widget.domNode, widget.sourceNode, value,{dtype:'H'});
        }
        else {
            this._doChangeInData(widget.domNode, widget.sourceNode, null);
        }
    },
    creating: function(attributes, sourceNode){
        if ('ftype' in attributes) {
            attributes.constraints['type'] = objectPop(attributes['ftype']);
        }
    },
    mixin_setPickInterval:function(interval){
        var timeInt = 'T00:'+interval+':00';
        this.constraints.clickableIncrement=timeInt;
        
    }
});

dojo.declare("gnr.widgets.NumberTextBox",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'input';
        this._dojotag='NumberTextBox';
    },
    creating: function(attributes, sourceNode){
        attributes._class= attributes._class? attributes._class + ' numberTextBox' : 'numberTextBox';
        attributes.constraints = objectExtract(attributes,'min,max,places,pattern,round,currency,fractional,symbol,strict,locale');
        if ('ftype' in attributes) {
            attributes.constraints['type'] = objectPop(attributes['ftype']);
        };
    },
    convertValueOnBagSetItem: function(sourceNode, value){
        if (value === ""){
            value = null;
        }
        return value;
    }
});
dojo.declare("gnr.widgets.CurrencyTextBox",gnr.widgets.NumberTextBox,{
    constructor: function(application){
        this._domtag = 'input';
        this._dojotag='CurrencyTextBox';
    }
});
dojo.declare("gnr.widgets.NumberSpinner",gnr.widgets.NumberTextBox,{
    constructor: function(application){
        this._domtag = 'input';
        this._dojotag='NumberSpinner';
    }
});

dojo.declare("gnr.widgets.Grid",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'Grid';
        if(dojoversion=='1.1'){
            if (!dojox.grid) {
                dojo.require('dojox.grid._grid.builder');
            };
            if (!dojox.grid.Builder.prototype._gnrpatch){
                dojox.grid.Builder.prototype._gnrpatch=true;
                dojox.grid.Builder.prototype.findCellTarget = function(inSourceNode, inTopNode){
                    var n = inSourceNode;
                    try{
                        while(n && (!this.isCellNode(n) || (dojox.grid.gridViewTag in n.offsetParent.parentNode && n.offsetParent.parentNode[dojox.grid.gridViewTag] != this.view.id)) && (n!=inTopNode)){
                            n = n.parentNode;
                        }
                        return n!=inTopNode ? n : null ;
                    }catch(e){
                        return;
                    }
                };
            }
        }
    },

    mixin_setStructpath:function(val,kw){
        var structure = genro.getData(this.sourceNode.attrDatapath('structpath'));
        this.cellmap = {};
        this.setStructure(this.gnr.structFromBag(structure, this.cellmap, this.gnreditors));
        this.onSetStructpath(structure);
    },
    
    mixin_onSetStructpath: function(structure){
        return;
    },

    created: function(widget, savedAttrs, sourceNode){
         genro.src.afterBuildCalls.push(dojo.hitch(widget,'render'));
         dojo.connect(widget, 'onSelected', widget,'_gnrUpdateSelect');
         dojo.connect(widget, 'modelAllChange', dojo.hitch(sourceNode ,this.modelAllChange));
         objectFuncReplace(widget.selection,'clickSelectEvent',function(e){
             this.clickSelect(e.rowIndex, e.ctrlKey || e.metaKey , e.shiftKey);});
    },

    modelAllChange:function(){
        if (this.attr.rowcount){
            this.setRelativeData(this.attr.rowcount,this.widget.rowCount);
        }
        //this.widget._gnrUpdateSelect();
    },
    mixin_rowIdByIndex: function(idx){
        if (idx!=null){
            return this.rowIdentity(this.rowByIndex(idx));
        }
     },
    mixin_rowByIndex: function(idx){
        return this.model.getRow(idx);
    },
    mixin_rowIdentity: function(row){
        if (row){
            return row[this.rowIdentifier()];
        } else {
            return null;
        }
    },
    mixin_rowIdentifier: function(row){
          return this.model.store._identifier;
      },
    mixin_rowItemByIndex: function(idx){
        identifier=this.rowIdentity(this.rowByIndex(idx));
        return this.model.store.fetchItemByIdentity({identity:identifier});
    },
    mixin_rowItemByIdentity: function(identifier){
        return this.model.store.fetchItemByIdentity({identity:identifier});
    },

    mixin__gnrUpdateSelect: function(idx){
        if (this.sourceNode.attr.selectedDataPath){
            var selectedDataPath=null;
            if (idx>=0){
                selectedDataPath = this.dataNodeByIndex(idx).getFullpath(null, true);
            }
            this.sourceNode.setAttributeInDatasource('selectedDataPath',selectedDataPath);
        }        
        if (this.sourceNode.attr.selectedLabel){
            var selectedLabel=null;
            if (idx>=0){
                var datanode= this.dataNodeByIndex(idx);
                selectedLabel = datanode ? this.dataNodeByIndex(idx).label : null;
            }
            this.sourceNode.setAttributeInDatasource('selectedLabel',selectedLabel);
        }        
        var selattr=objectExtract(this.sourceNode.attr,'selected_*',true);
        if (objectNotEmpty(selattr)){
            var row=this.rowByIndex(idx);
            var value;
            for (var sel in selattr){
                if (idx>=0){
                    value=row[sel];
                }else{
                    value=null;
                }
                var path=this.sourceNode.setRelativeData(selattr[sel],value);
            }
        }
        if (this.sourceNode.attr.selectedIndex){
            this.sourceNode.setAttributeInDatasource('selectedIndex', ((idx < 0) ? null : idx),null,null,true);
        }
        if (this.sourceNode.attr.selectedNodes){
            var nodes = this.getSelectedNodes();
            if (nodes){
                var selNodes=new gnr.GnrBag();
                dojo.forEach(nodes,
                    function(node){selNodes.setItem(node.label,null,node.getAttr());}
                            );
            }
            var path=this.sourceNode.attrDatapath('selectedNodes');
            genro.setData(path,selNodes,{'count':selNodes.len()});
        }
        if (this.sourceNode.attr.selectedId){
            var selectedId=null;
            if (idx>=0){
                selectedId=this.rowIdentity(this.rowByIndex(idx));
            }
            this.sourceNode.setAttributeInDatasource('selectedId', selectedId,null,this.rowByIndex(idx),true);
        }
    },
    mixin_indexByRowAttr:function(attrName, attrValue,op,backward){
        var op = op || '==';        
        if (backward){
            for (var i = this.rowCount - 1; i >= 0; i--){
                var row = this.rowByIndex(i);
                if (genro.compareDict[op].call(this,row[attrName],attrValue,op)) {return i;}                   
            };
        }
        else{
            for (var i=0; i < this.rowCount; i++){
                var row = this.rowByIndex(i);
                if (genro.compareDict[op].call(this,row[attrName],attrValue,op)) {return i;}
            }
        }
        return -1;
    },
    mixin_indexByCb:function(cb,backward){     
        if (backward){
            for (var i = this.rowCount - 1; i >= 0; i--){
                if (cb(this.rowByIndex(i))) {return i;}                   
            };
        }
        else{
            for (var i=0; i < this.rowCount; i++){
                if (cb(this.rowByIndex(i))) {return i;} 
            }
        }
        return -1;
    },
    mixin_selectByRowAttr:function(attrName, attrValue,op){
        var selection=this.selection;
        if (typeof (attrValue)=='object'){
             selection.unselectAll();
             var grid=this;
             dojo.forEach(attrValue, function(v){selection.addToSelection(grid.indexByRowAttr(attrName, v)); });           
        }else{
           selection.select(this.indexByRowAttr(attrName, attrValue,op));
        }
      
    },

    mixin_rowBagNode: function(idx){
        var idx=(idx==null) ? this.selection.selectedIndex : idx;
        return this.model.store.rootData().getNodes()[idx];
    },
    mixin_rowBagNodeUpdate: function(idx,data){
        var bagnode=this.rowBagNode(idx);
        var attributes=bagnode.attr;
        for (var attr in attributes){
            var newvalue=data.getItem(attr);
            if (newvalue!=null){
               attributes[attr]=newvalue;
            }
        }
        bagnode.setAttr(attributes);
    },
    mixin_getSelectedPkeys: function(noneIsAll){
        var sel = this.selection.getSelected();
        var result = [];
        if (sel.length>0){
            for (var i=0; i < sel.length; i++){
                result.push(this.rowIdByIndex(sel[i]));
            }
        } else if(noneIsAll){
            for (var i=0; i < this.rowCount; i++){
                result.push(this.rowIdByIndex(i));
            }
        }
        

        return result;
    },
    mixin_getSelectedRow: function(){
        return  this.rowByIndex(this.selection.selectedIndex);
    },
    
    mixin_getSelectedRowidx: function(){
        var sel = this.selection.getSelected();
        var result = [];
        for (var i=0; i < sel.length; i++){
            var row = this.rowByIndex(sel[i]);
            result.push(row.rowidx);
        }
        return result;
    },
    structFromBag: function(struct, cellmap, gnreditors){
        var cellmap = cellmap || {};
        var result = [];
        var _cellFormatter=function(formatOptions, cellClassCB){

            var opt=objectUpdate({}, formatOptions);
            var cellClassFunc;
            if(cellClassCB){
                cellClassFunc = funcCreate(cellClassCB, 'cell,v,inRowIndex');
            }
            return function(v, inRowIndex){
                
                if(cellClassFunc){
                    cellClassFunc(this, v, inRowIndex);
                }
                opt['cellPars'] = {rowIndex:inRowIndex};
                var zoomPage=opt['zoomPage'];
                if(typeof(v)=='number' && v<0){
                    this.customClasses.push('negative_number');
                }
                v = genro.format(v,opt);
                if (v==null){
                    return  '&nbsp;';
                }
                var template=opt['template'];
                if(template){
                    v = template.replace(/#/g,v);
                }
                if(zoomPage){
                    var zoomPkey=opt['zoomPkey'];
                    if (zoomPkey){
                        zoomPkey = zoomPkey.replace(/\W/g,'_');
                    }
                    var key=this.grid.currRenderedRow[zoomPkey? zoomPkey : this.grid._identifier];
                    v = "<a onclick='var ev = arguments[0]; if(!ev.metaKey){dojo.stopEvent(ev);}' class='gnrzoomcell' href='/"+zoomPage+"?pkey="+key+"&autoLinkFrom="+genro.page_id+"'>"+v+"</a>";
                }
                return v;
                
                };
            };
        if(struct){
            var bagnodes = struct.getNodes();
            var formats, dtype, editor;
            var view, viewnode, rows, rowsnodes, i, k, j, cellsnodes, row, cell, rowattrs, rowBag;
            var localTypes = {'R':{places:2},'L':{places:0},'I':{places:0},'D':{date:'short'},'H':{time:'short'},'DH':{datetime:'short'}};
            for (i=0; i < bagnodes.length; i++){
                 viewnode = bagnodes[i];
                 view = objectUpdate({}, viewnode.attr);
                 delete view.tag;
                 rows = [];
                 rowsnodes = viewnode.getValue().getNodes();
                 for (k=0; k < rowsnodes.length; k++){
                     rowattrs = objectUpdate({},rowsnodes[k].attr);
                     rowattrs = objectExtract(rowattrs,'classes,headerClasses,cellClasses');
                     rowBag = rowsnodes[k].getValue();
                    
                     if(!(rowBag instanceof gnr.GnrBag)){
                         rowBag = new gnr.GnrBag();
                         rowsnodes[k].setValue(rowBag, false);
                     }
                     cellsnodes = rowBag.getNodes();
                     
                     row = [];
                     for (j=0; j < cellsnodes.length; j++){
                         cell = objectUpdate({}, rowattrs);
                         cell = objectUpdate(cell, cellsnodes[j].attr);
                         dtype = cell.dtype;
                         
                         if(gnreditors[cell.field]){
                             this.setCellEditor(cell, gnreditors[cell.field]);
                         }
                         cell.original_field = cell.field;
                         cell.field = cell.field.replace(/\W/g,'_');
                         if (dtype){
                             cell.cellClasses = (cell.cellClasses || '') + ' cell_' + dtype;
                         }                        
                         cell.cellStyles=objectAsStyle(genro.dom.getStyleDict(cell,[ 'width']));
                         formats=objectExtract(cell,'format_*');
                         format=objectExtract(cell,'format');
                         var zoomPage=objectPop(cell,'zoomPage');
                         var template=objectPop(cell,'template');
                         if (template){
                             formats['template']=template;
                         }
                         formats['dtype']=dtype;
                         if (zoomPage)
                            formats['zoomPage']=zoomPage;
                            formats['zoomPkey']=objectPop(cell,'zoomPkey');
                         if (format){
                             formats['format']=format;
                         }
                         if (dtype){
                             formats = objectUpdate(objectUpdate({}, localTypes[dtype]), formats);
                         }
                         //formats = objectUpdate(formats, localTypes[dtype]);
                         var cellClassCB=objectPop(cell,'cellClassCB');
                         cell.formatter=_cellFormatter(formats, cellClassCB);
                         delete cell.tag;
                         row.push(cell);
                         cellmap[cell.field] = cell;
                     }
              
                     rows.push(row);
                 }
                 view.rows = rows;
                 result.push(view);
             }
        }
        return result;
    },
    groupByFromStruct:function(struct, grouppable){
        if (grouppable==undefined){
            grouppable = [];
        }
        var nodes = struct.getNodes();
        for (var i=0; i < nodes.length; i++){
            var node = nodes[i];
            if (node.attr.group_by){
                var fld = node.attr.field;
                if ((!stringStartsWith(fld,'$')) && (!stringStartsWith(fld,'@'))){
                    fld = '$'+fld;
                }
                grouppable.push(fld);
            }
            if (node.getValue() instanceof gnr.GnrBag){
                this.groupByFromStruct(node.getValue(), grouppable);
            }
        }
        return grouppable.join(',');
    }
});
dojo.declare("gnr.widgets.VirtualGrid",gnr.widgets.Grid,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'VirtualGrid';
    },
    creating: function(attributes, sourceNode){
        var savedAttrs = objectExtract(attributes,'selected*');
        var sortedBy=objectPop(attributes,'sortedBy');
        var identifier=objectPop(attributes,'identifier','_pkey');
        var gridAttributes=objectExtract(attributes,'autoHeight,autoRender,autoWidth,defaultHeight,elasticView,fastScroll,keepRows,model,rowCount,rowsPerPage,singleClickEdit,structure');
        objectPopAll(attributes);
        objectUpdate(attributes,gridAttributes);
        attributes.rowsPerPage=attributes.rowsPerPage || 10;
        attributes.rowCount=attributes.rowCount || 0;
        
        attributes.fastScroll=attributes.fastScroll || false;
        var structpath = sourceNode.attr.structpath;
        var storepath = sourceNode.absDatapath(sourceNode.attr.storepath);
        sourceNode.registerDynAttr('structpath');
        structure = genro.getData(sourceNode.absDatapath(structpath));
        attributes._identifier=identifier;
        attributes.cellmap = {};
        attributes.gnreditors = {};
        attributes.structure=this.structFromBag(structure, attributes.cellmap, attributes.gnreditors);
        attributes.storebag=genro.getDataNode(storepath,true,new gnr.GnrBag());
        if (!(attributes.storebag.getValue() instanceof gnr.GnrBag)){
            attributes.storebag.setValue(new gnr.GnrBag());
        }
        attributes.get=function(inRowIndex){
            var grid=this.grid;
            if (grid.currRenderedRowIndex!=inRowIndex){
                grid.currRenderedRowIndex=inRowIndex;
                grid.currRenderedRow=grid.rowByIndex(inRowIndex);
            }
            return grid.currRenderedRow[this.field];
        };
        attributes.sortedBy=sortedBy;
        attributes.canSort=function(){return true;};
        sourceNode.attr.nodeId = sourceNode.attr.nodeId || 'grid_' + sourceNode.getStringId();
    },
    created: function(widget, savedAttrs, sourceNode){
         dojo.connect(widget, 'onSelected', widget,'_gnrUpdateSelect');
         objectFuncReplace(widget.selection,'clickSelectEvent',function(e){
             this.clickSelect(e.rowIndex, e.ctrlKey || e.metaKey , e.shiftKey);});
    },

    mixin_canEdit: function(inCell, inRowIndex){

        return false;
    },
    mixin_loadBagPageFromServer:function(pageIdx){
        var row_start=pageIdx*this.rowsPerPage;
        var kw=this.storebag.attr;
        var data=genro.rpc.remoteCall(kw.method, {'selectionName':kw.selectionName,
                                                  'row_start':row_start,
                                                  'row_count':this.rowsPerPage,
                                                  'sortedBy':this.sortedBy,
                                                  'table':kw.table,
                                                  'recordResolver':false});
        data=data.getValue();                                      
        this.storebag.getValue().setItem('P_'+pageIdx,data);
        return data;
    },  
    patch_sort: function(){
          var sortInfo=this.sortInfo;
          var order;
          if (sortInfo<0){order='d';sortInfo=-sortInfo;}else{order='a';}
          var cell=this.layout.cells[sortInfo-1];
          var sortedBy=cell.field+':'+order;
          if ((cell.dtype=='A')||( cell.dtype=='T')){
              sortedBy=sortedBy+'*';
          }
          var path=this.sourceNode.attrDatapath('sortedBy');
          genro._data.setItem(path,sortedBy);
          
    },
    mixin_clearBagCache:function(){
        this.storebag.getValue().clear();
        this.currRenderedRowIndex=null;
        this.currRenderedRow=null;
        this.currCachedPageIdx=null;
        this.currCachedPage=null;
        this.selection.unselectAll();
    },
    
    mixin_setSortedBy:function(sortedBy){
        this.sortedBy=sortedBy;
        var rowcount=this.rowCount;
        this.updateRowCount(0);
        this.clearBagCache();
        this.updateRowCount(rowcount);
    },
    mixin_rowBagNodeUpdate: function(idx,data,pkey){
        if(idx==-1){
            var storebag=this.storebag.getValue();
            var cells=this.layout.cells;
            var row={};
            var cell;
            for (var i=0;i<cells.length;i++){
                cell=cells[i];
                row[cell.field]=data.getItem(cell.field);
            }
            var identifier=this.rowIdentifier();
            data[identifier]=pkey;
            row[identifier]=pkey;
            storebag.setItem(pkey,null,row);
            this.updateRowCount(storebag.len());
        }
        else{
            var attributes=this.rowByIndex(idx);
            for (var attr in attributes){
                var newvalue=data.getItem(attr);
                if (newvalue!=null){
                   attributes[attr]=newvalue;
                }
            }
            var identifier=this.rowIdentifier();
            //data[identifier]=pkey;
            attributes[identifier]=pkey;
            this.updateRow(idx);
        }
    },
    mixin_rowIdByIndex: function(idx){
        if (idx!=null){
            return this.rowIdentity(this.rowByIndex(idx));
        }
     },
    
    mixin_rowByIndex:function(inRowIndex){
        var rowIdx = inRowIndex%this.rowsPerPage;
        var pageIdx=(inRowIndex-rowIdx)/this.rowsPerPage;
        if (this.currCachedPageIdx!=pageIdx){
            this.currCachedPageIdx=pageIdx;
            this.currCachedPage=this.storebag.getValue().getItem('P_'+pageIdx);
            if (!this.currCachedPage){
                this.currCachedPage = this.loadBagPageFromServer(pageIdx);
            }
        }
        return this.currCachedPage.getNodes()[rowIdx].attr;
    },
    
    mixin_rowIdentity: function(row){
        if (row){
            return row[this.rowIdentifier()];
        } else {
            return null;
        }
    },
    mixin_rowIdentifier: function(row){
          return this._identifier;
      },
    patch_onStyleRow:function(row){
        if(this.currRenderedRow){
            if(this.currRenderedRow._customClasses){
                row.customClasses = this.currRenderedRow._customClasses;
            }
            if(this.currRenderedRow._customStyles){
                row.customStyles = this.currRenderedRow._customStyles;
            }
        }   
        this.onStyleRow_replaced(row);
    }
});



dojo.declare("gnr.widgets.VirtualStaticGrid",gnr.widgets.Grid,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'VirtualGrid';
    },
    creating: function(attributes, sourceNode){
        var savedAttrs = objectExtract(attributes,'selected*');
        var sortedBy=objectPop(attributes,'sortedBy');
        var identifier=objectPop(attributes,'identifier','_pkey');
        var datamode=objectPop(attributes,'datamode','attr');
        var gridAttributes=objectExtract(attributes,'autoHeight,autoRender,autoWidth,defaultHeight,elasticView,fastScroll,keepRows,model,rowCount,rowsPerPage,singleClickEdit,structure,filterColumn');
        objectPopAll(attributes);
        sourceNode.registerDynAttr('storepath');
        sourceNode.registerDynAttr('structpath');
        
        objectUpdate(attributes,gridAttributes);
        attributes.rowCount=0;
        attributes.rowsPerPage=attributes.rowsPerPage || 10;
        attributes.fastScroll=attributes.fastScroll || false;
        var structpath = sourceNode.attr.structpath;
        structure = genro.getData(sourceNode.absDatapath(structpath));
        attributes.cellmap = {};
        attributes.gnreditors = {};
        attributes.structure = this.structFromBag(structure, attributes.cellmap, attributes.gnreditors);
        attributes._identifier = identifier;
        attributes.sortedBy=sortedBy;
        attributes.datamode = datamode;
        sourceNode.attr.nodeId = sourceNode.attr.nodeId || 'grid_' + sourceNode.getStringId();
    },
    created: function(widget, savedAttrs, sourceNode){
         genro.src.afterBuildCalls.push(dojo.hitch(widget,'render'));
         dojo.connect(widget, 'onSelected', widget,'_gnrUpdateSelect');
         objectFuncReplace(widget.selection,'clickSelectEvent',function(e){
             this.clickSelect(e.rowIndex, e.ctrlKey || e.metaKey , e.shiftKey);});

         //var storebag=genro.getData(widget.storepath);
         //if (!(storebag instanceof gnr.GnrBag)){
         //    storebag=new gnr.GnrBag();
         //    genro.setData(widget.storepath,storebag);
         //}
         widget.updateRowCount('*');
    },

    attributes_mixin_get: function(inRowIndex){
        return this.grid.rowCached(inRowIndex)[this.field];
    },
    
    mixin_rowCached:function(inRowIndex){
        if (this.currRenderedRowIndex!=inRowIndex){
            this.currRenderedRowIndex=inRowIndex;
            this.currRenderedRow=this.rowByIndex(inRowIndex);
        }
        return this.currRenderedRow;
    },
    
    attributes_mixin_canSort: function(){
        return ('canSort' in this.sourceNode.attr )? this.sourceNode.attr.canSort : true;
    },
    mixin_filterExcluded: function(rowdata, index){
        if(this.excludeList){
            if (dojo.indexOf(this.excludeList, rowdata[this.excludeCol]) != -1){
                return;
            }
        }
        this.filtered.push(index);
    },
    mixin_applyFilter: function(filtered_value, rendering){
        var cb;
        this.excludeList = null;
        if (this.excludeListCb){
            this.excludeList = this.excludeListCb();
        }
        if ((!filtered_value) || ((filtered_value == true) && (!this.filtered_value))){
            this.filtered = null;
            if(this.excludeList){
                cb = function(node, index, array){
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
            if (this.filterColumn.indexOf('+') > 0){
                colType = 'T';
            } else {
                colType = this.cellmap[this.filterColumn]['dtype'] || 'A';
            }
            if(colType in {'A':null,'T':null}){
                this.filtered_compvalue = new RegExp(this.filtered_value, 'i');
                cb = function(node, index, array){
                    var result;
                    var columns = this.filterColumn.split('+');
                    var txt = '';
                    var rowdata = this.rowFromBagNode(node);
                    for (var i=0; i < columns.length; i++) {
                        txt = txt + ' ' + rowdata[columns[i]];
                    };
                    result = this.filtered_compvalue.test(txt);
                    if (result){
                        this.filterExcluded(rowdata, index);
                    }
                };
            } else {
                cb = function(node, index, array){
                        var op = this.filtered_compvalue.op;
                        var val = this.filtered_compvalue.val;
                        var rowdata = this.rowFromBagNode(node);
                        var result = this.filtered_compvalue.func.apply(this, [rowdata[this.filterColumn], val]);
                        if (result){
                            this.filterExcluded(rowdata, index);
                        }
                    };
                var toSearch = /^(\s*)([\<\>\=\!\#]+)(\s*)(.+)$/.exec(this.filtered_value);
                if(toSearch){
                    var val;
                    var op = toSearch[2];
                    if(op=='='){
                        op = '==';
                    }
                    if((op=='!') || (op=='#')){
                        op = '!=';
                    }
                    if(colType in {'R':null,'L':null,'I':null}){
                        val = dojo.number.parse(toSearch[4]);
                    } else if(colType == 'D'){
                        val = dojo.date.locale.parse(toSearch[4], {formatLength: "short",selector:'date'});
                    } else if(colType == 'DH'){
                        val = dojo.date.locale.parse(toSearch[4], {formatLength: "short"});
                    }
                    if(op && val){
                        var func = "return (colval "+op+" fltval)";
                        func = funcCreate(func, 'colval,fltval');
                        this.filtered_compvalue = {'op':op, 'val':val, 'func':func};
                    }
                }
            }
            if(this.filtered_compvalue){
                this.filtered = [];
                dojo.forEach(this.storebag().getNodes(), cb, this);
            }
        }
        this.filterToRebuild = false;
        if(!rendering){
            this.updateRowCount('*');
        }
    },
    mixin_newDataStore:function(val,kw){
        this.updateRowCount(0);
        this.filtered = null;
        if (this.sortedBy){
            var storebag=this.storebag();
            storebag.sort(this.sortedBy);
        }
        this.updateRowCount();
        this.selection.unselectAll();
        if((this.prevSelectedIdentifiers) && (this.prevSelectedIdentifiers.length>0 )){
            this.selectByRowAttr(this._identifier,this.prevSelectedIdentifiers);
            this.prevSelectedIdentifiers = null;
        }
        if(this.autoSelect && (this.selection.selectedIndex<0)){
            var sel = this.autoSelect==true? 0:this.autoSelect();
            this.selection.select(sel);

        }
    },
    mixin_setStorepath:function(val,kw){
        if((!this._updatingIncludedView)&& (! this._batchUpdating)){
            //this.filterToRebuild=true;
            if (kw.evt=='fired'){
                var storepath = this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
                var storenode = genro._data.getNode(storepath);
                if(storenode instanceof dojo.Deferred){
                    }
            }else{
                this._updatingIncludedView=true;
                this.currRenderedRowIndex=null;
                var storebag=this.storebag();
                var parentNode=this.domNode.parentNode;
                var storeNode = storebag.getParentNode();
                var parent_lv = kw.node.parentshipLevel(storeNode);
                if(kw.evt=='upd') {
                    if(parent_lv > 0){
                        // a single child changed, not the whole selection
                        var rowIdx = this.sourceNode.updateGridCellAttr(kw, true);
                        //var rowIdx = this.getRowIdxFromNode(kw.node);
                        this.updateRow(rowIdx);
                        // dojo.publish('upd_grid_cell', [this.sourceNode, rowLabel, rowIdx]);
                    } else {
                        // upd of the parent Bag
                        this.newDataStore();
                    }
                } else if(kw.evt=='ins') {//ATTENZIONE: questo trigger fa scattare il ridisegno della grid e cambia l'indice di riga
                    if (parent_lv == 1){
                        this.updateRowCount();
                        //fa srotellare in presenza di parametri con ==
                        this.setSelectedIndex(kw.ind);
                    } else {
                        //if ((storebag == kw.where) && (parent_lv<1)){
                        //}
                    }                
                } else if(kw.evt=='del') {
                    if (parent_lv == 1){
                        this.updateRowCount();
                        this.setSelectedIndex(kw.ind);
                    } else {
                        //if (parent_lv<1){
                        //}
                    }
                }
                this.renderOnIdle();
                this._updatingIncludedView=false;
              // if (this.prevSelectedIdentifiers){
              //     
              // }
            }
        }
    },
    
    mixin_setSelectedIndex: function(idx){
        var nrow = this.rowCount;
        if(nrow==0 ){
            this.selection.unselectAll();
        } else {
            if(idx >= nrow){
                idx = nrow - 1;
            }
           // if(this.selection.isSelected(idx)){
                //this.selection.unselectAll();
           // }
            this.selection.select(idx);
        }
    },
    patch_onSelectionChanged:function(){
        this.onSelectionChanged_replaced();
        var idx = this.selection.getFirstSelected();
        if(! this._batchUpdating){
         this._gnrUpdateSelect(idx);
        }
    },
    patch_sort: function(){
          var sortInfo=this.sortInfo;
          var order, sortedBy;
          if (sortInfo<0){order='d';sortInfo=-sortInfo;}else{order='a';}
          var cell=this.layout.cells[sortInfo-1];
          if(this.datamode=='bag'){
              sortedBy = cell.field+':'+order;
          }else{
              sortedBy = '#a.'+cell.field+':'+order;
          }
          if ((cell.dtype=='A')||( cell.dtype=='T')){
              sortedBy=sortedBy+'*';
          }
          if(!this.sourceNode.attr.sortedBy){
              this.setSortedBy(sortedBy);
          }else{
              var path=this.sourceNode.attrDatapath('sortedBy');
              genro._data.setItem(path,sortedBy);
          }
    },
    
    mixin_setRefreshOn:function(){
        
    },
    patch_onStyleRow:function(row){
        var attr = this.rowCached(row.index);
        if(attr._customClasses){
            var customClasses = null;
            if (attr._customClasses.slice(0,1)=='!'){
                customClasses = attr._customClasses.slice(1);
            }else{
                customClasses = row.customClasses + ' ' + attr._customClasses;
            }
            row.customClasses = customClasses;
        }
        if(attr._customStyles){
            row.customStyles = attr._customStyles;
        }    
        this.onStyleRow_replaced(row);
    },
    mixin_canEdit: function(inCell, inRowIndex){
    // summary:
    // determines if a given cell may be edited
    // inCell: grid cell
    // inRowIndex: grid row index
    // returns: true if given cell may be edited
        return false;
    },
    
    
    patch_onStartEdit: function(inCell, inRowIndex){
        // summary:
        //      Event fired when editing is started for a given grid cell
        // inCell: Object
        //      Cell object containing properties of the grid column.
        // inRowIndex: Integer
        //      Index of the grid row
        },

    patch_onApplyCellEdit: function(inValue, inRowIndex, inFieldIndex){
        // summary:
        //      Event fired when editing is applied for a given grid cell
        // inValue: String
        //      Value from cell editor
        // inRowIndex: Integer
        //      Index of the grid row
        // inFieldIndex: Integer
        //      Index in the grid's data model
        
        var dtype = this.cellmap[inFieldIndex].dtype;
        if ((dtype) && (dtype!='T') && (typeof(inValue)=='string')){
            inValue = convertFromText(inValue, this.cellmap[inFieldIndex].dtype, true);
        }
        var editnode = this.dataNodeByIndex(inRowIndex);
        if(this.datamode=='bag'){
            editnode.getValue().setItem(inFieldIndex, inValue);
        } else {
            editnode.setAttr(inFieldIndex, inValue);
        }
    },
    
    patch_updateRowCount:function(n){
        if ((n==null)|| (n=='*')){
            if (this.filterToRebuild){this.applyFilter(true, true);}
        }
        if(n=='*'){
            this.updateRowCount_replaced(0);
            this.selection.unselectAll();
            n = null;
        }
        if (n==null){
            var n = this.storeRowCount();
        }
        this.currRenderedRowIndex=null;
        this.currRenderedRow=null;
        this.updateRowCount_replaced(n);
    },
    mixin_setSortedBy:function(sortedBy){
        this.sortedBy = sortedBy;
        var storebag=this.storebag();
        storebag.sort(this.sortedBy);
        this.filterToRebuild = true;
        this.updateRowCount('*');
    },
    mixin_rowBagNodeUpdate: function(idx,data,pkey){
        if(idx==-1){
            var storebag=this.storebag();
            var cells=this.layout.cells;
            var row={};
            var cell;
            for (var i=0;i<cells.length;i++){
                cell=cells[i];
                row[cell.field]=data.getItem(cell.field);
            }
            var identifier=this.rowIdentifier();
            data[identifier]=pkey;
            row[identifier]=pkey;
            storebag.setItem(pkey,null,row);
            this.updateRowCount();
        }
        else{
        var attributes=this.rowByIndex(idx);
        for (var attr in attributes){
            var newvalue=data.getItem(attr);
            if (newvalue!=null){
               attributes[attr]=newvalue;
            }
        }
            this.updateRow(idx);
        }
    },
    mixin_rowIdByIndex: function(idx){
        if (idx!=null){
            return this.rowIdentity(this.rowByIndex(idx));
        }
     },
    mixin_storebag:function(){
         var storepath = this.sourceNode.absDatapath(this.sourceNode.attr.storepath);
         //var storebag=genro.getData(storepath);
         var storebag = genro._data.getItem(storepath);
        if(storebag instanceof gnr.GnrBag){
            return storebag;
        }
        else if (storebag instanceof dojo.Deferred){
            return storebag;
        }
        else if (!storebag){
            storebag=new gnr.GnrBag();
            genro.setData(storepath,storebag);
            return storebag;
        }
         else{
             storebag=new gnr.GnrBag();
             genro.setData(storepath,storebag);
             return storebag;
         }
    },
    mixin_setReloader: function(){
        this.reload(true);
        
    },
    mixin_reload:function(keep_selection){
        if (keep_selection){
             prevSelectedIdentifiers=[];
             var identifier=this._identifier;
             dojo.forEach(this.getSelectedNodes(), function(node){
                    if (node) {prevSelectedIdentifiers.push(node.attr[identifier]);};
             });
             this.prevSelectedIdentifiers=prevSelectedIdentifiers;
        }else{
            this.prevSelectedIdentifiers=null;
        }
        var storebag = this.storebag();
        var storeParent = storebag.getParentNode();
        if (storeParent.getResolver()){
            storeParent.refresh(true);
        }
        else{
            var selectionNode=genro.nodeById(this.sourceNode.attr.nodeId+'_selection');
            if (selectionNode){
                selectionNode.fireNode();
            }
        }
    },
    
    mixin_onSetStructpath: function(structure){
     var columns = gnr.columnsFromStruct(structure);
        if(this.sourceNode.hiddencolumns){
            columns = columns+','+this.sourceNode.hiddencolumns;
        }
        this.query_columns= columns;
        if (this.rpcViewColumns){
            this.rpcViewColumns.call();
        }
        this.reload();
    },
    
    mixin_absIndex: function(inRowIndex){
        if (this.filterToRebuild){
            alert('filtro invalido');
        }
        return this.filtered ? this.filtered[inRowIndex] : inRowIndex;
    },
    mixin_storeRowCount: function(){
        if(this.filtered){
            return this.filtered.length;
        } else {
            return this.storebag().len();
        }
        
    },
    mixin_rowByIndex:function(inRowIndex){
        if (inRowIndex < 0){
            return {};
        }
        inRowIndex = this.absIndex(inRowIndex);
        var nodes=this.storebag().getNodes();
        if (nodes.length>inRowIndex){
            return this.rowFromBagNode(nodes[inRowIndex]);
        }else{
            return {};
        }
    },
    mixin_dataNodeByIndex:function(inRowIndex){
        inRowIndex = this.absIndex(inRowIndex);
        var nodes=this.storebag().getNodes();
        if (nodes.length>inRowIndex){
            return nodes[inRowIndex];
        }
    },
    mixin_getSelectedNodes: function(){
        var sel = this.selection.getSelected();
        var result = [];
        for (var i=0; i < sel.length; i++){
            result.push(this.dataNodeByIndex(sel[i]));
        }
        return result;
    },
    mixin_rowIdentity: function(row){
        if (row){
            return row[this.rowIdentifier()];
        } else {
            return null;
        }
    },
    mixin_rowIdentifier: function(row){
          return this._identifier;
    },
    mixin_getRowIdxFromNode: function(node){
        var storebag=this.storebag();
        var subPath = node.getFullpath(null, storebag).split('.');
        return storebag.index(subPath[0]);
    },
    mixin_getColumnValues: function(col){
        var storebag=this.storebag();
        if(col.slice(0,2)=='^.'){
            col = col.slice(2);
        }
        if(this.datamode!='bag'){
            col = '#a.' + col;
        }
        return storebag.columns(col)[0];
    },

    mixin_rowFromBagNode:function(node){
        var result = objectUpdate({},node.attr);
        if(this.datamode=='bag'){
            var value = node.getValue();
            if(value){
                var node;
                for (var i=0; i < value._nodes.length; i++) {
                    node = value._nodes[i]; 
                    result[node.label] = node.attr.caption ? node.attr.caption : node.getValue();
                };
            };
        }
        return result;
    },
    nodemixin_updateGridCellAttr: function(kw){ // update node attributes (for cell display) from new field values
        var grid = this.widget;
        var storebag=grid.storebag();
        var subPath = kw.node.getFullpath(null, storebag).split('.');
        var rowLabel = subPath[0];
        var fldName = subPath[1];
        if(fldName){
            var chNode = storebag.getNode(rowLabel);
            var cellAttr, value, gridfield;
            var currAttr = chNode.attr;
            var fld;
            var cells = grid.cellmap;
            for (fld in cells){
                    cellAttr = grid.cellmap[fld];
                    if(cellAttr.original_field.indexOf(fldName)==0){
                        value = chNode.getValue().getItem(cellAttr.original_field);
                        gridfield = cellAttr.field;
                        currAttr[gridfield] = value;
                    }
            };
        }
        return storebag.index(rowLabel);
    },
    mixin_editBagRow: function(r){
        var r = r || this.selection.selectedIndex;
        var rc = this.findNextEditableCell({row: r, col: -1}, {r:0, c:1});
        if(rc){
            this.fireEditCell(rc);
        }
    },
    mixin_newBagRow: function(defaultArgs){
        var dataproviderNode = this.storebag().getParentNode();
        if ('newBagRow' in dataproviderNode){
            if (defaultArgs instanceof Array){
                result = [];
                for (var i=0; i < defaultArgs.length; i++) {
                    result.push(this.newBagRow(defaultArgs[i]));
                };
                return result;
            }
            else{
                return dataproviderNode.newBagRow(defaultArgs);
            }
        } else {
            if (defaultArgs instanceof Array){
                result = [];
                for (var i=0; i < defaultArgs.length; i++) {
                    result.push(this.newBagRow(defaultArgs[i]));
                };
                return result;
            }
            if (this.datamode == 'bag'){
                return new gnr.GnrBagNode(null,'label', new gnr.GnrBag(defaultArgs));
            } else {
                return new gnr.GnrBagNode(null,'label', null, defaultArgs);
            }
        }
    },
    mixin_addBagRow: function(label, pos, newnode, event, nodupField){
        var label = label || 'r_' + newnode._id;
        var storebag=this.storebag();
        if(nodupField){
            var nodupValue;
            var colvalues = this.getColumnValues(nodupField);
            if(this.datamode=='bag'){
                nodupValue = newnode.getValue().getItem(nodupField);
            } else {
                nodupValue = newnode.attr[nodupField];
            }
            if(dojo.indexOf(colvalues, nodupValue) != -1){
                return;
            }
        }
        event = event || {};
        if (pos =='*'){
            var curSelRow = this.absIndex(this.selection.selectedIndex);
            if (curSelRow<0){
                pos = event.shiftKey ? 0 : storebag.len();
            }else{
                pos = event.shiftKey ? curSelRow : curSelRow+1;
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
        return kw._new_position;
    },
    mixin_delBagRow: function(pos, many, params){
        var storebag=this.storebag();
        var removed = [];
        if (many){
            var selected = this.selection.getSelected();
            this.batchUpdating(true);
            this.loadingContent(true);
            var pos;
            for (var i = selected.length - 1; i >= 0; i--){
                pos=this.absIndex(selected[i]);
                removed.push(storebag.popNode('#'+pos));
            }
            this.batchUpdating(false);
            this.loadingContent(false);

        } else {
            pos = (pos == '*') ? this.absIndex(this.selection.selectedIndex): pos;
            removed.push(storebag.popNode('#'+pos));
        }
        removed.reverse();
        this.filterToRebuild = true;
        this.updateRowCount('*');
        
        //if(params.del_register){
        //    var path = '#parent.' + storebag.getParentNode().label + '_removed.';
        //    for (var i=0; i < removed.length; i++) {
        //        storebag.setItem(path + removed[i].label, removed[i].value, removed[i].attr, {'doTrigger':'_removedRow'});
        //    };
        //};
        
        var delpath;
        if(this.sourceNode.attr.delstorepath){
            delpath = this.sourceNode.attr.delstorepath;
        } else {
            var storenode = storebag.getParentNode();
            if(storenode.label.indexOf('@')==0){
                delpath = storenode.getFullpath(null, true) + '_removed';
            }
        }
        if(delpath){
            for (var i=0; i < removed.length; i++) {
                if(!removed[i].attr._newrecord){
                    genro._data.setItem(delpath + '.' + removed[i].label, removed[i].value, removed[i].attr, {'doTrigger':'_removedRow'});
                }
            }
        }
        return removed;
    },
    mixin_exportData:function(mode){
        var mode = mode || 'csv';
        var meta = objectExtract(this.sourceNode.attr, 'meta_*', true);
        var pars = objectUpdate({'structbag':this.structbag(), 'storebag':this.storebag()}, meta);
        var curgrid = this;
        curgrid.loadingContent(true);
        genro.rpc.remoteCall(mode, 
                                pars, 
                                'bag', 'POST', null, 
                                function(url){
                                    
                                        //var url = genro.rpc.rpcUrl("app.exportStaticGridDownload_"+mode, {filename:filename});
                                        genro.download(url);
                                        curgrid.loadingContent(false);
                                    });
      },
    mixin_printData:function(){
        var meta = objectExtract(this.sourceNode.attr, 'meta_*', true);
        var pars = objectUpdate({'structbag':this.structbag(), 'storebag':this.storebag()}, meta);
        var curgrid = this;
        curgrid.loadingContent(true);
        genro.rpc.remoteCall('app.printStaticGrid', 
                                pars, 
                                'bag', 'POST', null, 
                                function(url){
                                        //var url = genro.rpc.rpcUrl("app.printStaticGridDownload", {filename:filename});
                                        genro.download(url,null,'print');
                                        curgrid.loadingContent(false);
                                    });
    },
    mixin_structbag:function(){
        return genro.getData(this.sourceNode.absDatapath(structpath));
    },
    
    mixin_getCellEditor:function(row, col){
        var cell = this.getCell(col);
        var editWidget = genro.wdgById(this.editorId + '_' + cell.field);
        if (editWidget){
            var cellNode = cell.getNode(row);
            editWidget.cellNode = cellNode;
            editWidget.cellRow = row;
            editWidget.cellCol = col;
            editWidget.cell = cell;
        }
        return editWidget;
    },
    mixin_startEditCell:function(row, col){
        var editWidget = this.getCellEditor(row, col);
        if(!editWidget){
            return;
        }
        this.gnrediting = true;
        if (this.sourceNode.currentEditedRow != row){
            var selectedDataPath = this.dataNodeByIndex(row).getFullpath(null, true);
            //this.sourceNode.setRelativeData('.edit_datapath',selectedDataPath);
            this.sourceNode.setRelativeData('_temp.grids.'+this.sourceNode.attr.nodeId+'.edit_datapath',
                                            selectedDataPath);
            this.sourceNode.currentEditedRow = row;
            setTimeout(dojo.hitch(this, 'startEditCell', row, col), 1);
            return;
        }
        editWidget.sourceNode.editedRowIndex = row;
        editWidget.replacedNode = editWidget.cellNode.childNodes[0];
        
        if(editWidget.replacedNode){
            editWidget.cellNode.replaceChild(editWidget.domNode, editWidget.replacedNode);
        } else {
            editWidget.cellNode.appendChild(editWidget.domNode, editWidget.replacedNode);
        }
        editWidget.focus();
        /*if(editWidget.selectAllInputText){
            editWidget.selectAllInputText();
        }*/
    },
    mixin_endEditCell:function(editWidget, delta){
        if (editWidget.cellNode){
             if (editWidget.cellNode.childNodes[0]==editWidget.domNode){
                if(editWidget.replacedNode){
                    editWidget.cellNode.replaceChild(editWidget.replacedNode, editWidget.domNode);
                }
                else {
                    editWidget.cellNode.removeChild(editWidget.domNode);
                }
             }
             if(editWidget.sourceNode.hasValidationError()){
                 //var cellNode = editWidget.cellNode;
                 //dojo.style(cellNode,'color','red');
                 //genro.dlg.alert(editWidget.sourceNode.getValidationError(),"Warning");
             }else{
                 //genro.dom.removeClass(editWidget.cellNode,'notValidCell');
             }
        }
       
        var nextEditWidget;
        if(delta){
            var rc = this.findNextEditableCell({row: editWidget.cellRow, col: editWidget.cellCol}, delta);
            if(rc){
                this.fireEditCell(rc);
            }
        }
        //this.edit.info = {};
        this.gnrediting = false;
        editWidget.sourceNode.editedRowIndex = null;
    },
    mixin_findNextEditableCell: function(rc, delta){
        var row = rc.row;
        var col = rc.col;
        var nextEditWidget;
        do{
            col = col + delta.c;
            if(col >= this.layout.cellCount){
                col = 0;
                row = row + 1;
            }
            if(col < 0){
                col = this.layout.cellCount - 1;
                row = row - 1;
            }
            
            row = row + delta.r;
            if ((row >= this.rowCount) || (row < 0)){
                return;
            }
            nextEditWidget = this.getCellEditor(row, col);
        } while (!nextEditWidget);
        rc.col = col;
        rc.row = row;
        return rc;
    },
    mixin_fireEditCell: function(rc){
        if(this.startEditTimeout){
            clearTimeout(this.startEditTimeout);
        }
        this.startEditTimeout = setTimeout(dojo.hitch(this, 'startEditCell', rc.row, rc.col), 1);
    },
    patch_dokeydown:function(e){
        if(this.gnrediting){
            
        } else if(dijit.getEnclosingWidget(e.target)==this){
            this.onKeyDown(e);
        }
    },
    patch_doclick: function(e){
        if(this.gnrediting){
            dojo.stopEvent(e);
        } else {
            if(e.cellNode){
                this.onCellClick(e);
            }else{
                this.onRowClick(e);
            }
        }
    }

});

dojo.declare("gnr.widgets.GridEditor",gnr.widgets.baseHtml,{
    constructor: function(application){
        this._domtag = 'div';
    },
    creating: function(attributes, sourceNode){
        var viewId = sourceNode.getParentNode().attr.nodeId;
        attributes.display='none';
        sourceNode.attr.nodeId='grided_' + sourceNode.getStringId();
        sourceNode.attr.datapath = '^_temp.grids.'+viewId+'.edit_datapath';
        //sourceNode.attr.datapath = '^'+sourceNode.getParentNode().absDatapath('.edit_datapath');
        sourceNode.registerDynAttr('datapath');
        
        
        var childnodes = sourceNode.getValue().getNodes();
        var node;
        for (var i=0; i < childnodes.length; i++) {
            node = childnodes[i];
            node.attr.nodeId = sourceNode.attr.nodeId + '_' + node.attr.gridcell.replace(/\W/g,'_');
            if ('value' in node.attr){
                if(node.attr.tag.toLowerCase() == 'dbselect'){
                    node.attr.selectedCaption = '.'+ node.attr.gridcell;
                }
            }
            else{
                node.attr['value'] = '^.' + node.attr.gridcell;
            }
            if(node.attr.exclude == true){
                node.attr.exclude = '==genro.wdgById("'+viewId+'").getColumnValues("'+node.attr['value']+'")';
            }
            var dflt = node.attr['default'] || node.attr['default_value'] || '';
            node.getAttributeFromDatasource('value', true, dflt);
        };
    },
    created: function(widget, savedAttrs, sourceNode){
        var gridnode = sourceNode.getParentNode();
        var grid = gridnode.widget;
        grid.editorId = 'grided_' + sourceNode.getStringId();
        var editOn = sourceNode.attr.editOn || 'onCellDblClick';
        editOn = stringSplit(editOn, ',', 2);
        var modifier = editOn[1];
        dojo.connect(grid, editOn[0], function(e){
            if(genro.wdg.filterEvent(e, modifier)){
                if (grid.editorEnabled){
                    grid.fireEditCell({row:e.rowIndex, col: e.cellIndex});
                }
            }
        });
    }
    
});

dojo.declare("gnr.widgets.IncludedView",gnr.widgets.VirtualStaticGrid,{
    constructor: function(application){
        //dojo.require("dojox.grid._data.editors");
        this._domtag = 'div';
        this._dojotag = 'VirtualGrid';
    },
    
    creating: function(attributes, sourceNode){
        var sortedBy = objectPop(attributes,'sortedBy');
        var multiSelect = objectPop(attributes,'multiselect');
        var datamode=objectPop(attributes,'datamode','attr');
        var savedAttrs = objectExtract(attributes,'selected*');
        var hiddencolumns = objectPop(attributes,'hiddencolumns');
        var gridAttributes=objectExtract(attributes,'autoHeight,autoRender,autoWidth,defaultHeight,elasticView,fastScroll,keepRows,model,rowCount,rowsPerPage,singleClickEdit,structure,filterColumn,excludeCol,excludeListCb,editorEnabled');
        objectPopAll(attributes);
        objectUpdate(attributes,gridAttributes);
        var structure, gnreditors, contents;
        var inAttrs= sourceNode.getInheritedAttributes();
        var ctxRoot = sourceNode.absDatapath(inAttrs.sqlContextRoot);
        var abs_storepath = sourceNode.absDatapath(sourceNode.attr.storepath);
        var relation_path = abs_storepath;
        if (abs_storepath.indexOf(ctxRoot) == 0){
            relation_path = abs_storepath.replace(ctxRoot+'.', '');
        }
        sourceNode.registerDynAttr('storepath');
        var structpath = sourceNode.attr.structpath;
        sourceNode.registerDynAttr('structpath');
        structure = genro.getData(sourceNode.absDatapath(sourceNode.attr.structpath));
        attributes.gnreditors = {};
        attributes.cellmap = {};
        attributes.structure = this.structFromBag(structure, attributes.cellmap, attributes.gnreditors);
        var columns = gnr.columnsFromStruct(structure);
        if(hiddencolumns){
            columns = columns+','+hiddencolumns;
        }
        attributes.query_columns= columns;
        
        attributes.relation_path= relation_path;
        attributes.sqlContextName= inAttrs['sqlContextName'];
        attributes.sqlContextTable= inAttrs['sqlContextTable'];
        if(attributes.excludeListCb){
            attributes.excludeListCb = funcCreate(attributes.excludeListCb);
        }
        attributes._identifier='_pkey';
        attributes.sortedBy=sortedBy;
        attributes.rowCount=0;
        attributes.datamode = datamode;
        sourceNode.attr.nodeId = sourceNode.attr.nodeId || 'grid_' + sourceNode.getStringId();
        if (attributes.query_columns){
            var controllerPath = sourceNode.absDatapath() || 'grids.' + sourceNode.attr.nodeId;
            sourceNode.setRelativeData(controllerPath+'.columns', attributes.query_columns);
        }
    },    
    created: function(widget, savedAttrs, sourceNode){
         var selectionId = sourceNode.attr['selectionId'] || sourceNode.attr.nodeId+'_selection';
         widget.autoSelect = sourceNode.attr['autoSelect'];
         if (typeof(widget.autoSelect)=='string'){
             widget.autoSelect = funcCreate(widget.autoSelect,null,widget);
         }
         widget.linkedSelection = genro.nodeById(selectionId);
         genro.src.afterBuildCalls.push(dojo.hitch(widget,'render'));
         //dojo.connect(widget, 'onSelected', widget,'_gnrUpdateSelect');
         dojo.connect(widget, 'modelAllChange', dojo.hitch(sourceNode ,this.modelAllChange));
         if (sourceNode.attr.editbuffer){
             sourceNode.registerDynAttr('editbuffer');
         }
         objectFuncReplace(widget.selection,'clickSelectEvent',function(e){
             this.clickSelect(e.rowIndex, e.ctrlKey || e.metaKey , e.shiftKey);
         });
         if(sourceNode.attr.multiSelect==false){
             widget.selection.multiSelect = false;
         }
         widget.rpcViewColumns();
         widget.updateRowCount('*');
    },
    useGridContent_OLD: function(gridcontent){
        var node, structure, attr, tag;
        var nodes = gridcontent.getNodes();
        var gnreditors = {};
        for (var i=0; i < nodes.length; i++) {
            node = nodes[i];
            if(node.label=='struct'){
                structure = node.getValue();
            } else {
                attr = objectUpdate({}, node.attr);
                tag = objectPop(attr, 'tag');
                gnreditors[attr.linkedCol] = genro.wdg.create(tag, null, attr);
            }
        };
        return {'gnreditors':gnreditors, 'structure':structure};
    },
    mixin_structbag:function(){
        //return genro.getData(this.sourceNode.absDatapath(structpath));
        return genro.getData(this.sourceNode.absDatapath(this.sourceNode.attr.structpath));
    },
    mixinex_structbag:function(){
        var structure = this.sourceNode.getValue();
        if (structure){
            structure=structure.getItem('struct');
        }else{
            structure = genro.getData(this.sourceNode.absDatapath(this.sourceNode.attr.structpath));
        }
        return structure;
    },
    
    mixin_loadingContent:function(flag){
        var scrollnode = dojo.query('.dojoxGrid-scrollbox',this.domNode)[0];
        var contentnode = dojo.query('.dojoxGrid-content',this.domNode)[0];
        if (flag) {
            if (scrollnode)  {genro.dom.addClass(scrollnode,'waiting');};
            if (contentnode) {genro.dom.addClass(contentnode,'dimmed');};
        }else{
            if (scrollnode)  {genro.dom.removeClass(scrollnode,'waiting');};
            if (contentnode) {genro.dom.removeClass(contentnode,'dimmed');};
        }
    },

    mixin_batchUpdating: function(state){
        this._batchUpdating=state;
    },
    mixin_setEditorEnabled: function(enabled){
        this.editorEnabled = enabled;
    },
    mixin_rpcViewColumns: function(){
        if ((this.relation_path) && (this.relation_path.indexOf('@')==0)){
            genro.rpc.remoteCall('setViewColumns', {query_columns:this.query_columns,
                                                    contextName:this.sqlContextName,
                                                    contextTable:this.sqlContextTable,
                                                    relation_path:this.relation_path});
        }
    }
});

dojo.declare("gnr.widgets.BaseCombo",gnr.widgets.baseDojo,{
    creating: function(attributes, sourceNode){
        objectExtract(attributes,'maxLength,_type');
        var values=objectPop(attributes,'values');
        var val,xval;
        if (values){
            var localStore=new gnr.GnrBag();
            values=values.split(',');
            for(var i=0; i< values.length; i++){
                val=values[i];
                xval={};
                if(val.indexOf(':')>0){
                    val=val.split(':');
                    xval['id']=val[0];
                    xval['caption']=val[1];
                }else{
                    xval['caption']=val;
                }
                localStore.setItem('root.r_'+i,null,xval);
            }
            var store=new gnr.GnrStoreBag({mainbag:localStore});
            attributes.searchAttr='caption';
            store._identifier='id';
        }else{
            var storeAttrs = objectExtract(attributes,'storepath,storeid,storecaption');
            var savedAttrs = {};
            var store=new gnr.GnrStoreBag({datapath: sourceNode.absDatapath(storeAttrs.storepath)});
            attributes.searchAttr=store.rootDataNode().attr['caption'] || storeAttrs['storecaption'] || 'caption';
            attributes.autoComplete=attributes.autoComplete || false;
            store._identifier = store.rootDataNode().attr['id'] || storeAttrs['storeid'] || 'id';
        }
        attributes.store=store;
        return savedAttrs;      
    },
    created: function(widget, savedAttrs, sourceNode){
        var tag = 'cls_'+sourceNode.attr.tag;        
        dojo.addClass(widget.domNode.childNodes[0],tag);
        this.connectFocus(widget);
    },
    connectFocus: function(widget, savedAttrs, sourceNode){
        dojo.connect(widget,'onFocus', widget, function(e){
                                        setTimeout(dojo.hitch(this, 'selectAllInputText'), 1);
                                    });
        dojo.connect(widget,'onBlur', widget, 'validate');
    },
    
    mixin_selectAllInputText: function(){
        dijit.selectInputText(this.focusNode);
    },
    mixin__updateSelect: function(item){
        //var item=this.lastSelectedItem;
        var row = item ? item.attr : {};
        if (this.sourceNode.attr.selectedRecord){
            var path=this.sourceNode.attrDatapath('selectedRecord');
            this.sourceNode.setRelativeData(path,new gnr.GnrBag(row));
        }
        if (this.sourceNode.attr.selectedCaption){
            var path=this.sourceNode.attrDatapath('selectedCaption');
            this.sourceNode.setRelativeData(path, row['caption'], null, false, 'selected_');
        }
        var selattr=objectExtract(this.sourceNode.attr,'selected_*',true);
        var val;
        for (var sel in selattr){
            var path=this.sourceNode.attrDatapath('selected_'+sel);
            val = row[sel];
            this.sourceNode.setRelativeData(path,val,null,false,'selected_');
        }
    }
    
});
dojo.declare("gnr.widgets.dbBaseCombo",gnr.widgets.BaseCombo,{
    creating: function(attributes, sourceNode){
        var savedAttrs = {};
        var hasDownArrow;
        if (!attributes.hasDownArrow){
            attributes.hasDownArrow=false;
        }
        var resolverAttrs = objectExtract(attributes,'method,dbtable,columns,limit,condition,alternatePkey,auxColumns,hiddenColumns,rowcaption,order_by,selectmethod,weakCondition');
        var selectedColumns = objectExtract(attributes,'selected_*');
        if (objectNotEmpty(selectedColumns)){
            var hiddenColumns;
            if (hiddenColumns in resolverAttrs)
            {
                hiddenColumns = resolverAttrs['hiddenColumns'].split(',');
                for (var i=0;i<hiddenColumns.length;i++)
                {
                    selectedColumns[hiddenColumns[i]]=null;
                }
            }
            hiddenColumns = [];
            for (hiddenColumn in selectedColumns){
                hiddenColumns.push(hiddenColumn);
            }
            resolverAttrs['hiddenColumns'] = hiddenColumns.join(',');
        }
        resolverAttrs['method'] = resolverAttrs['method'] || 'app.dbSelect';
        resolverAttrs['notnull'] = attributes['validate_notnull'];
        savedAttrs['dbtable'] = resolverAttrs['dbtable'];
        savedAttrs['auxColumns'] = resolverAttrs['auxColumns'];
        var storeAttrs = objectExtract(attributes,'store_*');
        objectExtract(attributes,'condition_*');
        objectUpdate(resolverAttrs, objectExtract(sourceNode.attr,'condition_*',true));
        resolverAttrs['exclude'] = sourceNode.attr['exclude']; // from sourceNode.attr because ^ has to be resolved at runtime
        resolverAttrs._id='';
        resolverAttrs._querystring='';
        
        var store;
        savedAttrs['record']=objectPop(storeAttrs,'record');
        attributes.searchAttr =  storeAttrs['caption'] || 'caption';
        store = new gnr.GnrStoreQuery({'searchAttr':attributes.searchAttr});
        
        store._identifier =resolverAttrs['alternatePkey'] || storeAttrs['id'] || '_pkey';
        resolverAttrs._sourceNode = sourceNode;
        var resolver = new gnr.GnrRemoteResolver(resolverAttrs, true ,0);
        resolver.sourceNode=sourceNode;
        store.rootDataNode().setResolver(resolver);
        attributes.searchDelay = attributes.searchDelay || 300;
        attributes.autoComplete = attributes.autoComplete || false;
        attributes.ignoreCase = (attributes.ignoreCase==false) ? false : true;
        //store._remote;
        attributes.store=store;
        return savedAttrs;      
    },
    mixin_onSetValueFromItem: function(item, priorityChange){
        if (!item.attr.caption){
            return;
        }
        this.store._lastSelectedItem = item;
        this.store._lastSelectedCaption = this.labelFunc(item, this.store);
        if (this.sourceNode.attr.gridcell){
            this._updateSelect(item);
            this.onBlur();
        }
        else {
            if (this._hasBeenBlurred){
                this._updateSelect(item);
                this._hasBeenBlurred = false;
            }
        }
    },
    connectForUpdate: function(widget,sourceNode){
        return;
    },
    created: function(widget, savedAttrs, sourceNode){
        if (savedAttrs.auxColumns){
            widget._popupWidget = new gnr.Gnr_ComboBoxMenu({onChange: dojo.hitch(widget, widget._selectOption)});
        }
        this.connectForUpdate(widget,sourceNode);
        var tag = 'cls_'+sourceNode.attr.tag;        
        dojo.addClass(widget.domNode.childNodes[0],tag);
        this.connectFocus(widget, savedAttrs, sourceNode);
        //dojo.connect(widget, '_doSelect', widget,'_onDoSelect');                 
    }
});

dojo.declare("gnr.widgets.FilteringSelect",gnr.widgets.BaseCombo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'FilteringSelect';
    },
    //this patch will fix the problem where the displayed value stuck for a new record
    patch_setValue:function(value,priorityChange){
        this.setValue_replaced(value,priorityChange);
        if (!this._isvalid){
            this.valueNode.value=null;
            this.setDisplayedValue('');
        }
    }
});
dojo.declare("gnr.widgets.ComboBox",gnr.widgets.BaseCombo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'ComboBox';
    }
});

dojo.declare("gnr.widgets.dbSelect",gnr.widgets.dbBaseCombo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'FilteringSelect';
    },
    connectForUpdate: function(widget,sourceNode){
        dojo.connect(widget, '_setValueFromItem', widget, 'onSetValueFromItem');
        if (!("validate_dbselect" in sourceNode.attr)){
            sourceNode.attr.validate_dbselect = true;
        }
        if (!("validate_dbselect_error" in sourceNode.attr)){
            sourceNode.attr.validate_dbselect_error = 'Not existing value';
        }
    }
});

dojo.declare("gnr.widgets.dbComboBox",gnr.widgets.dbBaseCombo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag = 'ComboBox';
    },
    connectForUpdate: function(widget,sourceNode){
        var selattr=objectExtract(widget.sourceNode.attr,'selected_*',true);
        if('selectedRecord' in widget.sourceNode.attr || objectNotEmpty(selattr)){
            dojo.connect(widget, '_doSelect', widget, function(){
                                this._updateSelect(this.item);
                            });
        } 
    }
});


dojo.declare("gnr.widgets.DropDownButton",gnr.widgets.baseDojo,{
    constructor: function(application){
        this._domtag = 'div';
        this._dojotag='DropDownButton';
    },
    creating:function(attributes, sourceNode){
        var savedAttrs = {};
        var buttoNodeAttr = 'height,width,padding';
        var savedAttrs = objectExtract(attributes, 'fire_*');
        savedAttrs['_style'] = genro.dom.getStyleDict(objectExtract(attributes,buttoNodeAttr));
        savedAttrs['action'] = objectPop(attributes, 'action');
        savedAttrs['fire'] = objectPop(attributes, 'fire');
        savedAttrs['arrow'] = objectPop(attributes, 'arrow');
        attributes['label'] = attributes['label'] || '';
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
        if (savedAttrs.arrow==false){
            var arrow = dojo.query(".dijitArrowButtonInner", widget.domNode);
            if (arrow.length>0){
                arrow=arrow[0];
                arrow.parentNode.removeChild(arrow) ;
            }
        }
        if(savedAttrs['_style']){
            var buttonNode = dojo.query(".dijitButtonNode", widget.domNode)[0];
            dojo.style(buttonNode,savedAttrs['_style']);
        }
    },
    patch_addChild:function(dropDownContent){
        this.dropDown=dropDownContent;
    },
    patch_destroy: function(){
        if (this.dropDown){
            this.dropDown.destroyRecursive();
        }
        this.destroy_replaced.call(this);
    },
    patch__openDropDown: function(evtDomNode){
        var sourceNode=this.dropDown.sourceNode;
        if (sourceNode){
            sourceNode.refresh();
            this.dropDown=sourceNode.widget;
        }
        var dropDown = this.dropDown;
        var oldWidth=dropDown.domNode.style.width;
        var self = this;

        dijit.popup.open({
            parent: this,
            popup: dropDown,
            around: evtDomNode || this.domNode,
            orient:
                // TODO: add user-defined positioning option, like in Tooltip.js
                this.isLeftToRight() ? {'BL':'TL', 'BR':'TR', 'TL':'BL', 'TR':'BR'}
                : {'BR':'TR', 'BL':'TL', 'TR':'BR', 'TL':'BL'},
            onExecute: function(){
                self._closeDropDown(true);
            },
            onCancel: function(){
                self._closeDropDown(true);
            },
            onClose: function(){
                dropDown.domNode.style.width = oldWidth;
                self.popupStateNode.removeAttribute("popupActive");
                this._opened = false;
            }
        });
        if(this.domNode.offsetWidth > dropDown.domNode.offsetWidth){
            var adjustNode = null;
            if(!this.isLeftToRight()){
                adjustNode = dropDown.domNode.parentNode;
                var oldRight = adjustNode.offsetLeft + adjustNode.offsetWidth;
            }
            // make menu at least as wide as the button
            dojo.marginBox(dropDown.domNode, {w: this.domNode.offsetWidth});
            if(adjustNode){
                adjustNode.style.left = oldRight - this.domNode.offsetWidth + "px";
            }
        }
        this.popupStateNode.setAttribute("popupActive", "true");
        this._opened=true;
        if(dropDown.focus){
            dropDown.focus();
        }
        // TODO: set this.checked and call setStateClass(), to affect button look while drop down is shown
    },
    patch_startup: function(){
        // the child widget from srcNodeRef is the dropdown widget.  Insert it in the page DOM,
        // make it invisible, and store a reference to pass to the popup code.
        if(!this.dropDown){
            var dropDownNode = dojo.query("[widgetId]", this.dropDownContainer)[0];
            this.dropDown = dijit.byNode(dropDownNode);
            delete this.dropDownContainer;
        }
        dojo.body().appendChild(this.dropDown.domNode);
        this.dropDown.domNode.style.display="none";
    }
});



// Tree d11 ---------------------
dojo.declare("gnr.widgets.Tree",gnr.widgets.baseDojo,{
    constructor: function(){
        this._domtag = 'div';
        this._dojotag='Tree';
    },
    creating: function(attributes, sourceNode){
        dojo.require("dijit._tree.dndSource");
        dojo.require("dijit.Tree");
        var storepath=sourceNode.absDatapath(objectPop(attributes,'storepath'));
        var labelAttribute=objectPop(attributes,'labelAttribute');
        var labelCb = objectPop(attributes,'labelCb');
        var hideValues = objectPop(attributes,'hideValues');
        var _identifier = objectPop(attributes,'identifier') || '#id';
        if (labelCb){
            labelCb=funcCreate(labelCb);
        }
        var store=new gnr.GnrStoreBag({datapath:storepath,_identifier:_identifier,
                                       hideValues:hideValues,
                                       labelAttribute:labelAttribute,
                                       labelCb:labelCb});
        var model = new dijit.tree.ForestStoreModel({store: store,childrenAttrs: ["#v"]});
        attributes['model']=model;
        attributes['showRoot'] =false;
        attributes['persist']=attributes['persist'] || false;
        if (attributes['getLabel']){
            var labelGetter = funcCreate(attributes['getLabel'],'node');
            attributes.getLabel=function(node){
                if(node.attr){
                    return labelGetter(node);
               }
            };
        }
        if (attributes['getLabelClass']){
            var labelClassGetter = funcCreate(attributes['getLabelClass'],'node,opened');
            attributes.getLabelClass=function(node,opened){
                if(node.attr){
                    return labelClassGetter(node,opened);
                }
            };
        }
        if (attributes['getIconClass']){
            var iconGetter = funcCreate(attributes['getIconClass'],'node,opened');
            attributes.getIconClass=function(node,opened){
                if(node.attr){
                    return iconGetter(node,opened);
                }
            };
        }
        var savedAttrs=objectExtract(attributes,'inspect');
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
        if(savedAttrs.inspect){
            var modifiers = (savedAttrs.inspect==true) ? '' : savedAttrs.inspect;
            genro.wdg.create('tooltip',null,{label:function(n){return genro.dev.bagAttributesTable(n);},
                                                       validclass:'dijitTreeLabel',
                                                       modifiers:modifiers
                                                       }).connectOneNode(widget.domNode)    ;                                        
        };
        //dojo.connect(widget,'onClick',widget,'_updateSelect');
        var storepath=widget.model.store.datapath;
        if ((storepath=='*D') || (storepath=='*S'))
         widget._datasubscriber=dojo.subscribe('_trigger_data',
                                                widget,function(kw){
                                                    this.setStorepath('',kw);});
         else{
             sourceNode.registerDynAttr('storepath');
         }
    },

    patch__onClick:function(e){
        var nodeWidget = dijit.getEnclosingWidget(e.target);
        if(!nodeWidget || !nodeWidget.isTreeNode){
            return;
        }
        nodeWidget.__eventmodifier = eventToString(e);
        this._onClick_replaced(e);
        this._updateSelect(nodeWidget.item, nodeWidget);
    },
    mixin_getItemById: function(id){
        return this.model.store.rootData().findNodeById(id);
    },
    attributes_mixin__saveState: function(){
        //summary: create and save a cookie with the currently expanded nodes identifiers
        if(!this.persist){
            return;
        }
        var cookiepars={};
        if (this.persist=='site'){
            cookiepars.path=genro.getData('gnr.homeUrl');
        }
        var ary = [];
        for(var id in this._openedItemIds){
            ary.push(id);
        }
        dojo.cookie(this.cookieName, ary.join(","),cookiepars);
    },
    mixin_loadState:function(val,kw){
        var cookie = dojo.cookie(this.cookieName);
        this._openedItemIds = {};
        if(cookie){
            dojo.forEach(cookie.split(','), function(item){
                this._openedItemIds[item] = true;
            }, this);
        }
    },
    mixin_setStorepath:function(val,kw){
        //genro.debug('trigger_store:'+kw.evt+' at '+kw.pathlist.join('.'));
        if(kw.evt=='upd'){
            if(kw.updvalue){
                if (kw.value instanceof gnr.GnrBag){
                    this._onItemChildrenChange(/*dojo.data.Item*/ kw.node, /*dojo.data.Item[]*/ kw.value.getNodes());
                }else{
                     this._onItemChange({id:kw.node._id+'c',label:kw.value});
                }
            }
            //this.model.store._triggerUpd(kw);
        }else if (kw.evt=='ins'){
            this.model.store._triggerIns(kw);
        }else if (kw.evt=='del'){
            this._onItemChildrenChange(/*dojo.data.Item*/ kw.where.getParentNode(), /*dojo.data.Item[]*/ kw.where.getNodes());
            //this.model.store._triggerDel(kw);
        }
    },
    mixin__updateSelect: function(item,node){
        var modifiers = objectPop(node,'__eventmodifier');
        var attributes = {};
        if (modifiers){
            attributes._modifiers = modifiers;
        };
        if(!item){
            return;
        }
        if (!item._id){
            item=node.getParent().item;
        }
        if (this.sourceNode.attr.selectedLabel){
            var path=this.sourceNode.attrDatapath('selectedLabel');
            genro.setData(path,item.label,attributes);
        }
        if (this.sourceNode.attr.selectedItem){
            var path=this.sourceNode.attrDatapath('selectedItem');
            genro.setData(path,item,attributes);
        }
        if (this.sourceNode.attr.selectedPath){
            var path=this.sourceNode.attrDatapath('selectedPath');
            genro.setData(path,item.getFullpath(),attributes);
        }
        var selattr=objectExtract(this.sourceNode.attr,'selected_*',true);
        for (var sel in selattr){
            var path=this.sourceNode.attrDatapath('selected_'+sel);
            genro.setData(path,item.attr[sel],attributes);
        }
    }
});

dojo.declare("gnr.widgets.GoogleMap",gnr.widgets.baseHtml,{
    constructor: function(application){
        this._domtag = 'div';
    },
    creating: function(attributes, sourceNode){
        savedAttrs=objectExtract(attributes,'map_*');
        return savedAttrs;
    },
     created: function(widget, savedAttrs, sourceNode){
         var center=(savedAttrs.center || "37.4419,-122.1419").split(',');
         var maptype=savedAttrs.maptype || 'normal';
         var controls=savedAttrs.controls;
         var zoom=savedAttrs.zoom || 13 ;
         if (GBrowserIsCompatible()) {
            var map =new GMap2(widget);
            sourceNode.googleMap = map;
            map.setCenter(new GLatLng(parseFloat(center[0]), parseFloat(center[1])), zoom);
            map.setMapType(window['G_'+maptype.toUpperCase()+'_MAP']);
            if (controls){
                controls=controls.split(',') ;
                for(var i=0; i< controls.length; i++){
                    var cnt= window['G'+controls[i]+'Control'];
                    map.addControl(new cnt());
                }
            }
            var mapcommands=objectExtract(this,'map_*',true);
            for (var command in mapcommands){
                sourceNode[command]=mapcommands[command];
            }
          }else{
              alert('not compatible browser');
          }
     },
     
     map_getMapLoc: function(center){
         var c=center.split(',');
         return new GLatLng(parseFloat(c[1]), parseFloat(c[0]));
     },
     map_newMarker: function(center){
         return new GMarker(this.getMapLoc(center));
     }
});
dojo.declare("gnr.widgets.CkEditor",gnr.widgets.baseHtml,{
    constructor: function(application){
        this._domtag = 'div';
    },
    creating: function(attributes, sourceNode){
        attributes.id=attributes.id || 'ckedit_'+sourceNode.getStringId();
        var toolbar=objectPop(attributes,'toolbar');
        var config = objectExtract(attributes,'config_*');
        if  (typeof(toolbar)=='string'){
            toolbar=genro.evaluate(toolbar);
        };
        if (toolbar){
            config.toolbar='custom';
            config.toolbar_custom=toolbar;
        };
        var savedAttrs={'config':config};
        return savedAttrs;
        
    },
    created: function(widget, savedAttrs, sourceNode){
          CKEDITOR.replace(widget,savedAttrs.config);
          var ckeditor=CKEDITOR.instances['ckedit_'+sourceNode.getStringId()];
          sourceNode.externalWidget=ckeditor;
          ckeditor.sourceNode=sourceNode;
          for (var prop in this){
              if (prop.indexOf('mixin_')==0){
                  ckeditor[prop.replace('mixin_','')]=this[prop];
              }
          }
          ckeditor.gnr_getFromDatastore();
          setTimeout(function(){ckeditor.gnr_readOnly(sourceNode.getAttributeFromDatasource('readOnly'));},1000);

    },
    connectChangeEvent:function(obj){
        var ckeditor=obj.sourceNode.externalWidget;
         dojo.connect(ckeditor.focusManager,'blur', ckeditor, 'gnr_setInDatastore');
    },
    
    mixin_gnr_value:function(value,kw,reason){
        this.setData(value);
    },
    mixin_gnr_getFromDatastore : function(){
        this.setData(this.sourceNode.getAttributeFromDatasource('value'));
    },
    mixin_gnr_setInDatastore : function(){
        this.sourceNode.setAttributeInDatasource('value',this.getData());
    },
    
    mixin_gnr_cancelEvent : function( evt ){
                                evt.cancel();
    },
    mixin_gnr_readOnly:function(value,kw,reason){
        this.gnr_setReadOnly(value);
    },
    mixin_gnr_setReadOnly:function(isReadOnly){
        
        this.document.$.body.disabled = isReadOnly;
        CKEDITOR.env.ie ? this.document.$.body.contentEditable = !isReadOnly
                         : this.document.$.designMode = isReadOnly ? "off" : "on";
        this[ isReadOnly ? 'on' : 'removeListener' ]( 'key', this.gnr_cancelEvent, null, null, 0 );
        this[ isReadOnly ? 'on' : 'removeListener' ]( 'selectionChange', this.gnr_cancelEvent, null, null, 0 );
        var command,
        commands = this._.commands,
        mode = this.mode;
        for ( var name in commands ){
            command = commands[ name ];
            isReadOnly ? command.disable() : command[ command.modes[ mode ] ? 'enable' : 'disable' ]();
            this[ isReadOnly ? 'on' : 'removeListener' ]( 'state', this.gnr_cancelEvent, null, null, 0 );
        }
    }

});
dojo.declare("gnr.widgets.fileInput",gnr.widgets.baseDojo,{
    constructor: function(){
        this._domtag = 'input';
        this._dojotag='FileInput';
    },
    creating: function(attributes, sourceNode){
        dojo.require("dojo.io.iframe");
        var remotePars=objectExtract(attributes,'remote_*');
        var savedAttrs=objectExtract(attributes,'method');
        savedAttrs.onUpload=objectPop(attributes,'onUpload','alert("Upload Done")');
        savedAttrs.remotePars=remotePars;
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
        widget.savedAttrs=savedAttrs;
    },
    mixin_uploadFile: function(){
        var fname=this.fileInput.value;
        if(!fname || this._sent){ return; }
        var ext=fname.slice(fname.lastIndexOf('.'));
        this.savedAttrs.remotePars.ext=ext;
        var remotePars=genro.rpc.serializeParameters(genro.rpc.dynamicParameters(this.savedAttrs.remotePars));
        var method=this.savedAttrs.method;
        var url=genro.remoteUrl(method,remotePars);
        var _newForm = document.createElement('form');
        _newForm.setAttribute("enctype","multipart/form-data");
        var node = dojo.clone(this.fileInput);
        _newForm.appendChild(this.fileInput);
        this.fileInput.setAttribute('name','fileHandle');
        dojo.body().appendChild(_newForm);
        var handle=dojo.hitch(this,funcCreate(this.savedAttrs.onUpload));
        dojo.io.iframe.send({
            url: url,
            form: _newForm,
            handleAs: "text",
            handle: handle
        });
    }
});

dojo.declare("gnr.widgets.fileInputBlind",gnr.widgets.fileInput,{
    constructor: function(){
        this._domtag = 'input';
        this._dojotag='fileInputBlind';
    }});

dojo.declare("gnr.widgets.fileUploader",gnr.widgets.baseDojo,{
    constructor: function(){
        this._domtag = 'textarea';
        this._dojotag='dojox.widget.FileInputAuto';
    },
    creating: function(attributes, sourceNode){
        var uploadPars=objectUpdate({},sourceNode.attr);
        uploadPars.mode='html';
        objectExtract(uploadPars,'tag,method,blurDelay,duration,uploadMessage,cancelText,label,name,id,onComplete');
        savedAttrs=objectExtract(attributes,'method');
        dojo.require("dojox.widget.FileInputAuto");
        var onComplete=objectPop(attributes,'onComplete');
        savedAttrs.uploadPars=uploadPars;
        if(onComplete){
            attributes.onComplete=funcCreate(onComplete);
        }
        return savedAttrs;
    },
    created: function(widget, savedAttrs, sourceNode){
        widget.savedAttrs=savedAttrs;
    },
    mixin__sendFile: function(/* Event */e){
        // summary: triggers the chain of events needed to upload a file in the background.
        if(!this.fileInput.value || this._sent){ return; }
        var uploadPars=genro.rpc.serializeParameters(genro.rpc.dynamicParameters(this.savedAttrs.uploadPars));
        var method=this.savedAttrs.method;
        var url=genro.remoteUrl(method,uploadPars);         
        dojo.style(this.fakeNodeHolder,"display","none");
        dojo.style(this.overlay,"opacity","0");
        dojo.style(this.overlay,"display","block");
        this.setMessage(this.uploadMessage);
        dojo.fadeIn({ node: this.overlay, duration:this.duration }).play();
        var _newForm = document.createElement('form');
        _newForm.setAttribute("enctype","multipart/form-data");
        var node = dojo.clone(this.fileInput);
        _newForm.appendChild(this.fileInput);
        this.fileInput.setAttribute('name','fileHandle');
        dojo.body().appendChild(_newForm);
        dojo.io.iframe.send({
            url: url,
            form: _newForm,
            handleAs: "text",
            handle: dojo.hitch(this,"_handleSend")
        });
    },
    mixin__handleSend: function(data,ioArgs){
        // summary: The callback to toggle the progressbar, and fire the user-defined callback
        
        if(!dojo.isIE){
            // otherwise, this throws errors in ie? FIXME:
            this.overlay.innerHTML = "";
        }
        
        this._sent = true;
        dojo.style(this.overlay,"opacity","0");
        dojo.style(this.overlay,"border","none");
        dojo.style(this.overlay,"background","none"); 

        this.overlay.style.backgroundImage = "none";
        this.fileInput.style.display = "none";
        this.fakeNodeHolder.style.display = "none";
        dojo.fadeIn({ node:this.overlay, duration:this.duration }).play(250);
        
        dojo.disconnect(this._blurListener);
        dojo.disconnect(this._focusListener);
        alert('fatto:'+data);
        this.onComplete(data,ioArgs,this);
    },
    
    onComplete : function(data,ioArgs,widget){
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
        if(data){
            var d = dojo.fromJson(data);
            if(d.status && d.status == "success"){
                widget.overlay.innerHTML = "success!";
            }else{
                widget.overlay.innerHTML = "error? ";
            }
        }else{
            // debug assist
        }
    }
});
    
    

