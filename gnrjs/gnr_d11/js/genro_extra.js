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
        sourceNode.registerSubscription(sourceNode.attr.nodeId + '_render', this, function() {
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
        if ((sourceNode.vis) && (!sourceNode.visError)) {
            sourceNode.vis.render();
        } else {
            this.render(domNode);
        }

    },
    render:function(domNode) {
        var sourceNode = domNode.sourceNode;
        try {
            this._doRender(domNode);
            sourceNode.visError = null;
        } catch(e) {
            console.log('error in rendering protovis ' + sourceNode.attr.nodeId + ' : ' + e);
            sourceNode.visError = e;
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
            _this = this;
            sourceNode.protovisEnv = {};
            visbag.forEach(function(n) {
                vis = _this.bnode(sourceNode, n) || vis;
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
        var env = sourceNode.protovisEnv;
        var storepath = sourceNode.attr.storepath;
        var attr = objectUpdate({}, node.attr);
        var tag = objectPop(attr, 'tag');
        if (tag == 'env') {
            console.log(node.getValue());
            env[node.label] = eval(node.getValue());
            return;
        }
        var obj = parent ? parent.add(pv[tag]) : new pv[tag]();
        this._convertAttr(sourceNode, obj, attr);
        var v = node.getValue();
        _this = this;
        if (v instanceof gnr.GnrBag) {
            v.forEach(function(n) {
                _this.bnode(sourceNode, n, obj);
            });
        }
        return obj;
    },
    _convertAttr:function(sourceNode, obj, attr) {
        var env = sourceNode.protovisEnv;
        var storepath = sourceNode.attr.storepath;
        for (var k in attr) {
            var v = attr[k];
            if (stringEndsWith(k, '_js')) {
                k = k.slice(0, -3);
                v = genro.evaluate(v);
            }
            else if (stringEndsWith(k, '_fn')) {
                k = k.slice(0, -3);
                v = genro.evaluate('function(){return ' + v + '}');
            }
            else if (k.indexOf('_fn_') > 0) {
                k = k.split('_fn_');
                var fn = 'function(' + k[1] + '){return (' + v + ')}';
                v = genro.evaluate(fn);
                k = k[0];
            }

            if ((typeof(v) == 'string') && (v[0] == '=')) {
                path = v.slice(1);
                if (path[0] == '.') {
                    path = storepath + path;
                }
                v = this.storegetter(sourceNode, path);
            }
            if (k.indexOf('_') > 0) {
                k = k.split('_');
                obj[k[0]](k[1], v);
            } else {
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
    dialog_tableProperties:function(definition,ckeditor){
        this.dialog_table(definition,ckeditor)
    },
    dialog_table:function(definition,ckeditor){
        definition.getContents('info').get('txtBorder')['default']=null;
        definition.getContents('advanced').get('advStyles')['default']='border-collapse:collapse;'
        definition.addContents({
            id : 'gnr_tableProperties',
            label : 'Genropy',
            accessKey : 'G',
            elements : [{id : 'row_datasource',type : 'text',label : 'Row Datasource',
                        setup: function(i) {
                            this.setValue(i.getAttribute('row_datasource') || '');
                        },
                        commit: function(i, j) {
                            if (this.getValue()) j.setAttribute('row_datasource', this.getValue());
                            else j.removeAttribute('row_datasource');
                        }}]
            });
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
        var parentDomNode=sourceNode.getParentNode().getDomNode();
        var cbResize=function(){
                sourceNode._rsz=null
                ckeditor.resize(parentDomNode.clientWidth,parentDomNode.clientHeight);
        }
        dojo.connect(parentWidget,'resize',function(){
            if(sourceNode._rsz){
                clearTimeout(sourceNode._rsz)
            }
            sourceNode._rsz=setTimeout(cbResize,100)
        });
        var that=this;
        CKEDITOR.on( 'dialogDefinition', function( ev ){
            if (that['dialog_'+ev.data.name]){
                that['dialog_'+ev.data.name].call(that,ev.data.definition)
            }
        })
        

         
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
        var value=this.getData()
        if(this.sourceNode.getAttributeFromDatasource('value')!=value){
            this.sourceNode.setAttributeInDatasource('value',value );
        }

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