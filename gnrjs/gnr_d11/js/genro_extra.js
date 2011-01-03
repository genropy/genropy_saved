dojo.declare("gnr.widgets.dummy", null, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    _beforeCreation: function(sourceNode) {
        sourceNode.freeze()
        var children = sourceNode.getValue();
        sourceNode.clearValue();
        var content = this.createContent(sourceNode, this.contentKwargs(objectUpdate({}, sourceNode.attr)));
        if (children) {
            children.forEach(function(n) {
                content._(n.attr.tag, objectUpdate({}, n.attr));
            })
        }
        sourceNode.unfreeze(true);
        return false;
    },
    contentKwargs: function(attributes) {
        return attributes;
    }


});
dojo.declare("gnr.widgets.pPane", gnr.widgets.dummy, {

});

dojo.declare("gnr.widgets.pGroup", gnr.widgets.dummy, {
    contentKwargs: function(attributes) {
        var groupCode = objectPop(attributes, 'groupCode');
        var dockTo = objectPop(attributes, 'dockTo');
        var title = objectPop(attributes, 'title') || 'Palette ' + groupCode;
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
        var nodeId = 'paletteGroup_' + groupCode + '_floating';
        var floating_kwargs = {nodeId:nodeId,dockTo:dockTo,title:title,
            dockable:true,closable:false,resizable:true};
        return objectUpdate({height:'400px',width:'300px',
            top:top,right:right,left:left,bottom:bottom,
            visibility:'hidden',groupCode:groupCode},
                floating_kwargs);


    },
    createContent:function(sourceNode, kw) {
        var groupCode = objectPop(kw, 'groupCode');
        var floating = sourceNode._('floatingPane', kw);
        var tc = floating._('tabContainer', {selectedPage:'^gnr.palettes.?' + groupCode});
        return tc;
    }
    /*
     def pm_paletteGroup(self,pane=None,groupCode=None,title=None,dockTo=None,**kwargs):
     floating = self._pm_floatingPalette(pane,nodeId='paletteGroup_%s_floating' %groupCode,
     title=title or '!!Palette %s' %groupCode,dockTo=dockTo,**kwargs)
     return floating.tabContainer(selectedPage='^gnr.palettes.?%s' %groupCode,groupCode=groupCode)

     def _pm_floating_kwargs(self,top=None,left=None,right=None,bottom=None,**kwargs):
     if (left is None) and (top is None) and (right is None) and (bottom is None):
     if not hasattr(self,'_last_floating'):
     self._last_floating = dict(top=0,right=0)
     self._last_floating['top']=self._last_floating['top']+10
     self._last_floating['right'] = self._last_floating['right'] +10
     top = '%ipx' %self._last_floating['top']
     right = '%ipx' %self._last_floating['right']
     palette_kwargs = dict(height='400px',width='300px',top=top,right=right,left=left,bottom=bottom,
     visibility='hidden')
     palette_kwargs.update(kwargs)
     return palette_kwargs

     def _pm_floatingPalette(self,pane,nodeId=None,title=None,dockTo=None,**kwargs):
     dockTo = dockTo or 'default_dock'
     return pane.floatingPane(nodeId=nodeId,dockTo=dockTo,title=title,
     dockable=True,closable=False,resizable=True,
     **self._pm_floating_kwargs(**kwargs))

     */

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
            this.render(newobj)
        })
      
    },
    setStorepath:function(obj, value) {
        obj.gnr.update(obj)
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
        return span
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
             this._doRender(domNode)
             sourceNode.visError=null
        } catch(e) {
            console.log('error in rendering protovis '+sourceNode.attr.nodeId)
            sourceNode.visError=e
        }
        
    },
    _doRender:function(domNode) {
        var sourceNode = domNode.sourceNode;
        if (sourceNode.attr.js) {
            var vis = new pv.Panel()
            var protovis = pv.parse(sourceNode.getAttributeFromDatasource('js'));
            funcApply(protovis, objectUpdate({'vis':vis}, sourceNode.currentAttributes()), sourceNode);
        }
        else if (sourceNode.attr.storepath) {
            var storepath = sourceNode.attr.storepath
            var visbag = sourceNode.getRelativeData(storepath)
            vis = this.bnode(sourceNode, visbag.getNode('source.#0'))
        }
        this.attachToDom(domNode, vis)
        sourceNode.vis = vis;
        vis.render()
    },
    storegetter:function(sourceNode, path) {
        var p = path
        var s = sourceNode
        return function() {
            console.log('getting: ' + p)
            return s.getRelativeData(p)
        }
    },
    bnode:function(sourceNode, node, parent) {

        var storepath = sourceNode.attr.storepath;
        var attr = objectUpdate({}, node.attr);
        var tag = objectPop(attr, 'tag');
        var obj;
        if (!parent) {
            obj = new pv[tag]();
        } else {
            obj = parent.add(pv[tag])
        }
        for (var k in attr) {
            var v = attr[k];
            if (stringEndsWith(k,'_js')){
                k=k.slice(0,-3)
                v=genro.evaluate(v);
            }
            else if (stringEndsWith(k,'_fn')){
                k=k.slice(0,-3)
                v=genro.evaluate('function(){return '+v+'}');
            }
            else if(k.indexOf('_fn_')>0){
                k=k.split('_fn_')
                var fn='function('+k[1]+'){return ('+v+')}'
                console.log(fn)
                v=genro.evaluate(fn);
                k=k[0]
            }
            
            if ((typeof(v) == 'string') && (v[0] == '=')) {
                path = v.slice(1)
                if (path[0] == '.') {
                    path = storepath + path
                }
                v = this.storegetter(sourceNode, path)
            }
            if(k.indexOf('_')>0){
                k=k.split('_');
                obj[k[0]](k[1],v);
            }else{
                obj[k](v);
            }
            
        }
        var v = node.getValue();
        _this = this
        if (v instanceof gnr.GnrBag) {
            v.forEach(function(n) {
                _this.bnode(sourceNode, n, obj)
            })
        }
        return obj
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