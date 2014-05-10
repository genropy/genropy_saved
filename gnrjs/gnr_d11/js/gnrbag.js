/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module GnrBag : Genro Bag clientside. An advantage data storage system
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

//########################  Bag #########################


//######################## class BagNode##########################


dojo.declare("gnr.GnrBagNode", null, {
    //summary:a bagnode is a slot of a bag
    //description: Or we could just get a new roomate.
    /**
     * @id gnr.GnrBagNode
     * is the function which is used as constructor of the Bagnode class
     * @classDescription a bag is a slot of a bag
     * @param {gnr.GnrBag} parentbag
     * @param {String} label
     * @param {Object} value
     * @param {Dictionary} attr
     * @param {Object} resolver
     * @constructor
     */
    _counter : [0],

    constructor: function(parentbag, label, value, _attr, _resolver) {
        this._id = this._counter[0] += 1;
        this.label = (label == '#id') ? this.getStringId() : label;
        this.locked = false;
        this._value = null;
        this.setResolver(_resolver);
        this.setParentBag(parentbag);
        this.attr = {};
        this._status = 'loaded';

        this._onChangedValue = null;
        if (_attr) { // && parentbag){ ??? a cosa serve? commentato da francesco per test 1/12/08
            var attr = objectUpdate({}, _attr);
            this.setAttr(attr, /*update trigger*/false);
        }
        if (value == undefined) {
            value = null;
        }
        if (!_resolver) {
            this.setValue(value, /*update trigger*/false);
            this._status = 'loaded';
        }
    },
    getStringId:function() {
        return 'n_' + this._id;
    },
    isExpired:function() {
        if (!this._resolver) {
            return false;
        }
        else {
            return this._resolver.expired();
        }
    },
    isLoaded:function() {
        //if(this.isExpired()){
        //    return false
        //}
        return (this._status == 'loaded');
    },
    isLoading:function() {
        return (this._status == 'loading');
    },
    /**
     * @id getParentBag
     */
    getParentNode: function() {
        if (this._parentbag) {
            return this._parentbag._parentnode;
        }
    },
    getParentBag: function() {
        if (this._parentbag) {
            return this._parentbag;
        }
    },
    orphaned:function(){
        this._parentbag = null;
        if(isBag(this._value)){
            this._value.clearBackRef();
        }
        return this;
    },
    isChildOf:function(bagOrNode){
        var node = bagOrNode instanceof gnr.GnrBagNode? bagOrNode:bagOrNode.getParentNode();
        var curr = this;
        do{
            var parentNode = curr.getParentNode();
            curr=parentNode;
        }while(parentNode  && parentNode !== node)
        return parentNode!=null;
    },

    /**
     * @id setParentBag
     */
    setParentBag: function(parentbag) {
        this._parentbag = null;
        if (parentbag != null) {
            this._parentbag = parentbag;
            if (parentbag.hasBackRef()) {
                if (isBag(this._value)) {
                    this._value.setBackRef(/*node*/this, /*parent*/ parentbag);
                }
            }
        }
    },
    getFullpath: function(mode, root) {
        var segment;
        var fullpath = '';
        var parentbag = this.getParentBag();
        if (parentbag) {
            fullpath = parentbag.getFullpath(mode, root);
            if (mode == '#' || mode == '##') {
                segment = parentbag.getNodes().indexOf(this);
                if (mode == '##') {
                    segment = '#' + segment;
                }
            } else {
                segment = this.label;
            }
            if (fullpath) {
                fullpath = fullpath + '.' + segment;
            }
            else {
                fullpath = segment;
            }
        }
        return fullpath;
    },
    /**
     * @id getValue
     */
    getValue2:function(mode/*str*/, optkwargs) {
        return this.getValue(mode, optkwargs);
    },
    getFormattedValue: function(kw,mode) {
        var v = this.getValue(mode);
        var kw = kw || {};
        kw.joiner = kw.joiner || '<br/>';
        kw.omitEmpty = 'omitEmpty' in kw? kw.omitEmpty : true;
        if(v instanceof gnr.GnrBag){
            v = v.getFormattedValue(kw,mode);
        }else{
            v = this.attr._formattedValue || this.attr._displayedValue || v;
        }
        return (v || !kw.omitEmpty)?((this.attr._valuelabel || this.attr.name_long || stringCapitalize(this.label)) +': ' +v):''; 
    },

    getValue: function(mode/*str*/, optkwargs) {
        var mode = mode || '';
        if ((this._resolver == null) || (mode.indexOf('static') >= 0) || (this._status == 'loading')) {
            return this._value;
        }
        if (this._resolver.isGetter) {
            //This kind of resolver returns the value but doesn't set it in the node.
            var finalize = function(r) {
                return r;
            };
            var result = this._resolver.resolve(optkwargs, this);
            if (result instanceof dojo.Deferred) {
                return result.addCallback(finalize);
            } else {
                return finalize(result);
            }
        }
        else if (this._status == 'resolving') {
            return this._resolver.meToo(dojo.hitch(this, "getValue2", mode, optkwargs));
        }
        else if ((this._status == 'loaded') && (!this._resolver.expired()) && (mode.indexOf('reload') < 0)) {
            return this._value;
        }
        else {
            this._status = 'resolving';
            var fullpath = this.getFullpath();
            var result = this._resolver.resolve(optkwargs, this);
            var finalize = dojo.hitch(this, function(result) {
                this._status = 'loading';
                this.setValue(result, (mode == 'notrigger' ? false : 'resolver'));
                this._status = 'loaded';
                if (this._resolver._pendingDeferred.length > 0) {
                    var pendingDeferred = this._resolver._pendingDeferred;
                    this._resolver._pendingDeferred = [];
                    setTimeout(dojo.hitch(this._resolver, "runPendingDeferred", pendingDeferred), 1);
                }
                //  for (var i=0; i<this._pendingDeferred.length; i++){
                //      this._pendingDeferred[i].callback(r)
                //      }
                if(this._resolver.onloaded){
                    this._resolver.onloaded.call(this);
                }
                return this._value;
            });
            if (result instanceof dojo.Deferred) {
                //genro.debug('Deferred adding callback (node.getValue) :'+this.label);
                return result.addCallback(finalize);
            }
            else {
                return finalize(result);
            }
        }
    },
    clearValue:function(doTrigger) {
        this.setValue(null, doTrigger);
        return this;
    },
    /**
     * @id setValue
     */
    setValue: function(value, doTrigger, _attributes, _updattr) {
        if (value instanceof gnr.GnrBagResolver) {
            this.setResolver(value);
            value = null;
            //this._resolver._parent = this._parentbag;

        }
        else if (value instanceof gnr.GnrBagNode) {
            var attr = {};
            if (_updattr) {
                objectUpdate(attr, this.attr);
            }
            objectUpdate(attr, value.attr);
            objectUpdate(attr, _attributes || {});
            var resolver = value.getResolver();
            var value = value._value;
            if (resolver) {
                this.setResolver(resolver);
            }
            var _attributes = attr;
        }
        if (doTrigger == null) {
            doTrigger = true;
        }
        if (this.locked == true) {
            alert("error");
        }
        var oldvalue = this._value;
        var oldattr;
        var updated_attr = false;
        this._value = value;
        //doTrigger = doTrigger && (oldvalue!=this._value);

        //if(objectNotEmpty(_attributes)){ 
        //replaced condition with if(_attributes)
        if (_attributes) {
            updated_attr = true;
            oldattr = objectUpdate({}, this.attr);
            this.setAttr(_attributes, /*trigger*/false, _updattr);
        }
        if (this._onChangedValue) {
            this._onChangedValue(this, value, oldvalue);
        }
        if (this._parentbag && this._parentbag._backref) {
            if (oldvalue!==value){
                if(isBag(oldvalue)){
                    oldvalue.clearBackRef();
                }
            }
            if (isBag(value)) {
                value.setBackRef(this, this._parentbag);
            }
            if (doTrigger) {
                this._parentbag.onNodeTrigger({'evt':'upd','node':this, 'pathlist':[this.label],
                    'oldvalue':oldvalue,'value':value,'oldattr':oldattr,
                    'updvalue':true,'updattr':updated_attr,'reason':doTrigger});
            }
        }
    },
    refresh: function(always) {
        if (always || this.isExpired()) {
            this.getValue('reload');
        }
    },
    getStaticValue: function() {
        return this._value;
    },

    setStaticValue:function(value) {
        this._value = value;
    },

    setResolver:function(resolver) {
        if (resolver) {
            resolver._parentNode = this;
            resolver.onSetResolver(this);
        }
        this._resolver = resolver;
        this._status = 'unloaded';
    },
    getResolver: function() {
        return this._resolver;
    },

    resetResolver: function() {
        this._resolver.reset();
    },


    /**
     * @id getAttr
     */
    getAttr: function(label, _default) {
        if (label) {
            if (label in this.attr) {
                return this.attr[label];
            } else {
                return _default || null;
            }
        }
        return this.attr;
    },
    getInheritedAttributes: function(attrname) {
        var curr = this;
        if(attrname){
            while(curr && !curr.attr[attrname]){
                curr = curr.getParentNode();
            }
            return curr?curr.attr[attrname]:null;
        }else{
            var inherited = {};
            var parentnode = this.getParentNode();
            if (parentnode){
                inherited =parentnode.stopInherite? objectUpdate(inherited, parentnode.attr) : parentnode.getInheritedAttributes();
            } 
            return objectUpdate(inherited, this.attr);
        }
    },
    isAncestor:function(n){
        do{
            if(n && (n._id==this._id)){
                 return true;
            }
            n = n.getParentNode();
        }while(n)
        return false;
    },
    
    isDescendant:function(n){
        return n.isAncestor(this);
    },
    
    
    attributeOwnerNode:function(attrname,attrvalue,caseInsensitive){
        var curr = this;
        var currattr = curr.attr || {};
        if(arguments.length==1){
            if(attrname.indexOf(',')<0){
                while(curr && !(attrname in curr.attr)){
                    curr = curr.getParentNode();
                }
            }else{
                attrname = attrname.split(',');
                while(curr && !dojo.some(attrname,function(n){return (n in curr.attr)})){
                    curr = curr.getParentNode();
                }
            }
        }else if(caseInsensitive){
            while(curr && (curr.attr[attrname] || '').toLowerCase()!=(attrvalue || '').toLowerCase()){
                curr = curr.getParentNode();
            }
        }else{
            while(curr && curr.attr[attrname]!=attrvalue){
                curr = curr.getParentNode();
            }
        }
        return curr;
    },

    hasAttr: function(label, value) {
        if (label in this.attr) {
            if (value) {
                return (this.attr[label] == value);
            } else {
                return true;
            }
        } else {
            return false;
        }
    },

    /**
     * IN PYTHON NON C'è , serve ancora??
     * @param {Object} attributes
     */
    replaceAttr: function(attributes) {
        this.attr = {};
        this.setAttr(attributes);
    },


    /**
     * @id setAttr
     */
    setAttribute:function(label, value, doTrigger) {
        var updDict = {};
        updDict[label] = value;
        this.setAttr(updDict, doTrigger, true,label);
    },

    updAttributes:function(attrDict, doTrigger) {
        this.setAttr(attrDict, doTrigger, true);
    },

    setAttr: function(attr, doTrigger, updateAttr, changedAttr) {
        if (doTrigger == null) {
            doTrigger = true;
        }
        var oldattr = objectUpdate({}, this.attr);
        if (updateAttr) {
            this.attr = objectUpdate(this.attr, attr);
        } else {
            this.attr = attr;
        }
        if (doTrigger) {
            if (this._parentbag && this._parentbag._backref) {
                this._parentbag.onNodeTrigger({'evt':'upd','node':this, 'pathlist':[this.label],
                    'oldattr':oldattr,'updattr':true, reason:doTrigger,
                    'changedAttr':changedAttr});
            }
        }
    },

    /**
     * @id delAttr
     */
    delAttr: function(attrToDelete/*String...*/) {
        if (typeof(attrToDelete) == "string") {
            attrToDelete = attrToDelete.split(',');
        }
        for (var i = 0; i < attrToDelete.length; i++) {
            delete this.attr[attrToDelete[i]];
        }
    },

    /**
     * esiste solo nella versione js questa implementazione
     * questo metodo serve esclusivamente per esser chiamato dalla classe Bag
     */
    _toXmlBlock: function(kwargs) {
        if (this.getResolver()) {
            var nodeValue = this.getValue('static');
        } else {
            var nodeValue = this.getValue();
        }

        var result = '';

        if (isBag(nodeValue)) {
            result = xml_buildTag(this.label,
                    nodeValue.toXmlBlock(kwargs),
                    this.getAttr(),
                    true);
        } else {
            result = xml_buildTag(this.label,
                    nodeValue,
                    this.getAttr());
        }
        return result;
    },


//in python non c'è, qui serve??
    toJSONString: function() {
        return {'label':this.label, 'value':this._value, 'attr':this.attr}.toJSONString();
    },
// ---------------Node async Calls--------------
    doWithValue: function(cb, kwargs) {
        var value = this.getValue('', kwargs);
        if (value instanceof dojo.Deferred) {
            //genro.debug('Deferred adding callback (node.doWithValue) :'+this.label);
            return value.addCallback(cb);
        } else {
            return cb(value);
        }
    },
    parentshipLevel: function(node) {
        if (this == node) {
            return 0;
        }
        var parentNode = this.getParentNode();
        var n = parentNode ? parentNode.parentshipLevel(node) : -1;
        return (n >= 0) ? n + 1 : n;
    }
});


//######################## class Bag##########################

dojo.declare("gnr.GnrBag", null, {
    //summary: A flexible container object. A Javascript version of python gnrBag.
    /**
     * @id gnr.GnrBag
     * @param {Object} source //not implemented yet
     */
    _nodeFactory: gnr.GnrBagNode,
    constructor: function(source) {
        this._nodes = [];
        this._backref = false;
        this._parentnode = null;
        this._parent = null;
        this._symbols = null;
        this._subscribers = {};
        if (source) {
            this.fillFrom(source);
        }

    },
    newNode: function(parentbag, label, value, _attr, _resolver) {
        return  new this._nodeFactory(parentbag, label, value, _attr, _resolver);
    },

    fillFrom: function(source) {
        if (source instanceof Array) {
            for (var i = 0; i < source.length; i++) {
                this.setItem(source[i][0], source[i][1]);
            }
        } else if (isBag(source)) {
            var dest = this;
            source.forEach(function(node) {
                dest.setItem(node.label, node.getValue(), objectUpdate({}, node.getAttr()));
            });
        }
        else if (source instanceof Object) {
            for (var k in source) {
                this.setItem(k, source[k]);
            }
        }

    },
    
    /**
     * @id getParent
     */
    getParent: function() {
        if (this._parent) return this._parent;
    },

    /**
     * @id setParent
     * @method
     * @memberOf{gnr.GnrBag}
     */
    setParent: function(parent) {
        this._parent = parent;
    },

    /**
     *
     * @param {gnr.GnrBagNode} node
     */
    setParentNode: function(node/*gnr.GnrBagNode*/) {
        this._parentnode = node;
    },

    getParentNode: function() {
        return this._parentnode;
    },
    attributes: function() {
        if (this._parentnode) {
            return this._parentnode.attr;
        }
    },
    resolver: function() {
        if (this._parentnode) {
            return this._parentnode._resolver;
        }
    },

    /**
     * @id getItem
     */
    asHtmlTable:function(kw){
        var kw = kw || {};
        var headers = kw.headers;
        var h ='';
        var hheadcel = this.getItem('#0');
        if(headers && hheadcel){
            if(headers===true){
                headers = '';
                hheadcel.forEach(function(n){
                    var calclabel = (n.attr._valuelabel || n.attr.name_long || stringCapitalize(n.label));
                    headers+=headers?','+calclabel:calclabel;
                })
            }
            h = '<thead>';
            headers = headers.split(',');
            dojo.forEach(headers,function(th){
               h+='<th>'+th+'</th>';
            });
            h+='</thead>';
        }
        var rows =''
        var r,b,v,vnode,format;
        var cells = kw.cells.split(',');
        //var cellformats = objectExtract

        this.forEach(function(n){
            r ='';
            b = n._value;
            dojo.forEach(cells,function(cell){
                var align = 'left'
                vnode = b.getNode(cell);
                if(vnode){
                    v = vnode._value;

                    if(v instanceof gnr.GnrBag){
                        v = v.getFormattedValue(kw,mode);
                    }else if(v==null){
                        v='';
                    }
                    else{
                        format = kw[cell];
                        if(format){
                            v = _F(v,format,vnode.attr.dtype);
                        }else{
                            v = vnode.attr._formattedValue || vnode.attr._displayedValue || v;
                        }
                        if(typeof(v)=='number'){
                            align ='right';
                        }
                    }
                }else{
                    v = '';
                }
                r+='<td style="text-align:'+align+'">'+v+'</td>';
            });
            rows+='<tr>'+r+'</tr>';
        },'static');
        return '<table class="formattedBagTable">'+h+'<tbody>'+rows+'</tbody></table>';
    },
     
    getFormattedValue:function(kw,mode){
        var kw = kw || {};
        if(this._parentnode && this._parentnode.attr.format_bag_cells){
            return this.asHtmlTable(objectExtract(this._parentnode.attr,'format_bag_*',true));
        }else if(kw.cells){
            return this.asHtmlTable(kw);
        }
        var r = [];
        var kw = kw || {};
        kw.joiner = kw.joiner || '<br/>';
        kw.omitEmpty = 'omitEmpty' in kw? kw.omitEmpty:true;
        var fv;
        this.forEach(function(n){
            if(n.label[0]!='_'){
                fv = n.getFormattedValue(kw,mode);
                if(kw.omitEmpty && !fv){
                    return;
                }
                r.push(fv);
            }
        },mode);
        return r.join(kw.joiner);
    },
    
    getItem: function(path, dft, mode) {
        var dft = (dft == '') ? dft : dft || null;
        if (!path) {
            return this;
        }
        var finalize = function(res) {
            var m = mode;
            var obj = res.value;
            var label = res.label;
            if (isBag(obj)) {
                return obj.get(label, dft, m);
            }
            else {
                return dft;
            }
        };
        var res = this.htraverse(path);
        if (res instanceof dojo.Deferred) {
            //genro.debug('Deferred adding callback (bag.getItem) :'+path);
            return res.addCallback(finalize);
        } else {
            return finalize(res);
        }

    },
    sort: function(pars) {
        //pars None: label ascending
        var cmp = function(a, b, reverse, caseInsensitive) {
            if (caseInsensitive) {
                if (typeof(a) == 'string') {
                    var a = a.toLowerCase();
                }
                if (typeof(b) == 'string') {
                    var b = b.toLowerCase();
                }
            }
            if (a == b) {
                return 0;
            }
            else if (reverse) {
                if (a < b) {
                    return 1;
                }
                else {
                    return -1;
                }
            } else {
                if (a > b) {
                    return 1;
                }
                else {
                    return -1;
                }
            }
        };
        var pars = pars || '#k:a';
        var level,what,mode,reverse,caseInsensitive;
        var levels = pars.split(',');
        levels.reverse();
        for (var i = 0; i < levels.length; i++) {
            level = levels[i];
            if (level.indexOf(':') >= 0) {
                level = level.split(':');
                what = level[0];
                mode = level[1];
            } else {
                what = level;
                mode = 'a';
            }
            what = stringStrip(what);
            mode = stringStrip(mode).toLowerCase();
            if (stringEndsWith(mode, '*')) {
                caseInsensitive = true;
                mode = mode.slice(0, -1);
            } else {
                caseInsensitive = false;
            }
            reverse = ! ((mode == 'a') || (mode == 'asc') || (mode == '>'));

            if (what == '#k') {
                this._nodes.sort(function(a, b) {
                    return cmp(a.label, b.label, reverse, caseInsensitive);
                });
            } else if (what == '#v') {
                this._nodes.sort(function(a, b) {
                    return cmp(a.getValue(), b.getValue(), reverse, caseInsensitive);
                });
            } else if (what.indexOf('#a') >= 0) {
                var attrname = what.slice(3);
                this._nodes.sort(function(a, b) {
                    return cmp(a.getAttr(attrname), b.getAttr(attrname), reverse, caseInsensitive);
                });
            } else {
                this._nodes.sort(function(a, b) {
                    return cmp(a.getValue().getItem(what), b.getValue().getItem(what), reverse, caseInsensitive);
                });
            }
        }
    },

    sum: function(path) {
        var result = 0;
        var n;
        var path = path || '#v';
        if (path) {
            var l = this.digest(path);
            for (var i = 0; i < l.length; i++) {
                n = l[i][0];
                if (typeof n == 'number') {
                    result = result + n;
                }
            }
        }
        return result;
    },

    /**
     * @id get
     */
    get: function(label, dflt, mode) {
        var result = null;
        var currnode = null;
        var currvalue = null;
        if (!label) {
            currnode = this._parentnode;
            currvalue = this;
        }
        else if (label == '#parent') {
            currnode = this._parent.getNode();
        }
        else {
            if (label.indexOf('?') >= 0) {
                var flabel = label.split('?');
                label = flabel[0];
                var getter = flabel[1] || '#attr';
            }
            var i = this.index(label);
            if (i < 0) {
                return dflt;
            }
            else {
                currnode = this._nodes[i];
            }
        }
        if (currnode) {
            currvalue = currnode.getValue();
        }
        if (!getter) {
            return currvalue;
        }
        var finalize = function(currvalue) {
            if (getter.indexOf('=') == 0) {
                genro.__evalAuxValue = currvalue;
                var expr = getter.slice(1).replace(/#v/g, 'genro.__evalAuxValue');
                currvalue = dojo.eval(expr);
                return currvalue;
            }
            if (getter.indexOf('#') < 0) {
                return currnode.getAttr(getter);
            }
            if (getter == '#attr') {
                return currnode.attr;
            }
            if (getter == '#keys') {
                return currvalue.keys();
            }
            if (getter == '#node') {
                return currnode;
            }
            if (getter == '#digest:') {
                return currvalue.digest(mode.split(':')[1]);
            }
        };
        if (currvalue instanceof dojo.Deferred) {
            //genro.debug('Deferred adding callback (bag.get) :'+label);
            return currvalue.addCallback(finalize);
        }
        else {
            return finalize(currvalue);
        }

    },

    /**
     * @id ee
     * @method
     * @memberOf gnr.GnrBag
     * this method receives a list that represents a hierarchical path and executes
     one step of the path, calling itself recursively. If autocreate mode is True,
     the method creates not existing nodes of the pathlist.
     @param pathlist: list of nodes'labels
     * @param {Object} pathlist
     * @param {Boolean} autocreate
     */

    htraverse: function(pathlist, autocreate) {
        var curr = this;
        if (typeof pathlist == "string") {
            if (pathlist.indexOf('?') >= 0) {
                var pl = pathlist.split('?');
                pathlist = smartsplit(pl[0].replace(/\.\.\//g, '#parent.'), '.');
                pathlist[pathlist.length - 1] = pathlist[pathlist.length - 1] + '?' + pl[1];
            } else {
                pathlist = smartsplit(pathlist.replace(/\.\.\//g, '#parent.'), '.');
            }
            ;

            /*pathlist = [x for x in pathlist if x]*/
            if (!pathlist) {
                return {value:curr, label: ''};
            }
        }
        var label = pathlist.shift();
        while (label == '#parent' && pathlist) {
            curr = curr.getParent();
            label = pathlist.shift();
        }
        if (pathlist.length == 0) {
            return {"value":curr, "label":label};
        }
        var i = curr.index(label);
        if (i < 0) {
            if (autocreate) {
                if (label && label.charAt(0) == '#') {
                    label = label.replace('#', '_');
                    //return null; //in verità: raise BagException ('Not existing index in #n syntax')
                }
                i = curr._nodes.length;
                var newbag = new curr.constructor();
                var newnode = curr.newNode(curr, label, newbag);
                curr._nodes.push(newnode);
                if (curr._backref) {
                    curr.onNodeTrigger({'evt':'ins','node':newnode,'where':curr,'ind':i,'reason':'autocreate'});
                }

            }
            else return {"value": null, "label":null};
        }
        var finalize = dojo.hitch(this, function(newcurr) {
            var isbag = isBag(newcurr);
            if (autocreate && !isbag) {
                var newcurr = new curr.constructor();
                this._nodes[i].setValue(newcurr, false);
                isbag = true;
            }
            if (isbag) {
                var result = newcurr.htraverse(pathlist, autocreate);
                if (result instanceof dojo.Deferred) {
                    //genro.debug('Deferred adding callback (bag.htraverse) :'+pathlist.toString());
                    return result.addCallback(function(r) {
                        return r;
                    });
                } else {
                    return result;
                }
            }
            else {
                return {"value":newcurr, "label":pathlist.join(".")};
            }
        });
        var newcurr = curr._nodes[i].getValue();
        if (newcurr instanceof dojo.Deferred) {
            //genro.debug('Deferred adding callback (bag.htraverse) :'+pathlist.toString());
            return newcurr.addCallback(finalize);
        } else {
            return finalize(newcurr);
        }

    },
    len: function() {
        return this._nodes.length;
    },

    __str2__: function(mode) {

        var mode = mode || 'static';
        var outlist = [];
        var el = null;
        var attrString = '';
        var j = 0;
        var key;
        var value = null;

        for (var i = 0; i < this._nodes.length; i++) {
            el = this._nodes[i];
            for (key in el.attr) {
                attrString = attrString + key + '=' + el.attr[key] + ' ';
            }
            if (attrString != '') {
                attrString = '||' + attrString + '||';
            }
            value = el.getValue(mode); //verificare getValue
            if (isBag(value)) {
                outlist.push(i + '-(' + value.declaredClass + ') ' + el.label + ': ' + attrString);

                if (el.visited) {
                    innerbagstr = 'visited at: ' + el.label;
                } else {
                    el.visited = true;
                    var inner = value.__str2__(mode).split('\n');
                    var auxlist = [];
                    for (var u = 0; u < inner.length; u++) {
                        var line = inner[u];
                        auxlist.push('----' + line);
                    }

                    var innerbagstr = auxlist.join('\n');
                }
                outlist.push(innerbagstr);
            } else {
                outlist.push(i + '-(' + (value.declaredClass || typeof value) + ') ' + el.label + ': ' + value.toString() + ' ' + attrString);

            }
        }
        return outlist.join('<br/>');
    },

    /**
     * todo
     */

    __str__: function(mode) {

        var mode = mode || 'static';
        var outlist = [];
        var el = null;
        var attrString = '';
        var j = 0;
        var key;
        var value = null;


        for (var i = 0; i < this._nodes.length; i++) {
            el = this._nodes[i];
            for (var key in el.attr) {
                attrString = attrString + key + '=' + el.attr[key] + ' ';
            }
            if (attrString != '') {
                attrString = '<' + attrString + '>';
            }
            value = el.getValue(mode); //verificare getValue
            if (isBag(value)) {
                outlist.push(i + '-(' + value.declaredClass + ') ' + el.label + ': ');

                if (el.visited) {
                    innerbagstr = 'visited at: ' + el.label;
                } else {
                    el.visited = true;
                    var inner = value.__str__(mode).split('\n');
                    var auxlist = [];
                    for (var u = 0; u < inner.length; u++) {
                        var line = inner[u];
                        auxlist.push('----' + line);
                    }

                    var innerbagstr = auxlist.join('\n');
                }
                outlist.push(innerbagstr);
            } else {
                var v = convertToText(value);
                outlist.push(i + '-(' + v[0] + ') ' + el.label + ': ' + v[1] + ' ' + attrString);

            }
        }
        return outlist.join('\n');
    },

    /**
     * todo
     */
    asString: function() {
        return this.__str2__();
    },

    /**
     * @id keys
     */
    keys: function() {
        var keys = [];
        for (var i = 0; i < this._nodes.length; i++) {
            keys.push(this._nodes[i].label);
        }
        return keys;
    },

    /**
     * @id values
     */
    values: function() {
        var values = [];
        for (var i = 0; i < this._nodes.length; i++) {
            values.push(this._nodes[i].getValue());
        }
        return values;
    },

    /**
     * @id items
     */
    items: function() {
        var items = [];
        for (var i = 0; i < this._nodes.length; i++) {
            items.push({key:this._nodes[i].label, value:this._nodes[i].getValue()});
        }
        return items;
    },

    /**
     * digest(iva)
     */
    digest: function(what, asColumns) {
        var obj = null;
        if (what == null) {
            what = '#k,#v,#a';
        }
        if (what.indexOf(':') != -1) {
            var s = what.split(':');
            var where = s[0];
            what = s[1];
            obj = this.getNode(where); //obj=self[where]
        }
        else {
            obj = this;
        }
        var result = [];
        var nodes = obj._nodes;
        var wl = what.split(',');
        var w = null;
        var aux = [];
        var path = '';
        var value = null;
        var x = null;

        for (var i = 0; i < wl.length; i++) {
            var ll = null;
            value = null;
            aux = [];
            w = wl[i];
            //w=stripBlank(w);
            if (w == '#k') {
                for (var j = 0; j < nodes.length; j++) {
                    aux.push(nodes[j].label);
                }
                result.push(aux);
            }
            else if (w == '#v') {
                for (var j = 0; j < nodes.length; j++) {
                    aux.push(nodes[j].getValue());
                }
                result.push(aux);
            }
            else if (w.slice(0, 3) == '#v.') {
                ll = w.split('.');
                w = ll.shift();
                path = ll.join('.');
                for (var j = 0; j < nodes.length; j++) {
                    x = nodes[j];
                    value = x.getValue();
                    if (isBag(value)) {
                        aux.push(value.getItem(path));
                    }
                    else {
                        aux.push(null);
                    }
                }
                result.push(aux);
            }
            else if (w == '#__v') {
                for (var j = 0; j < nodes.length; j++) {
                    aux.push(nodes[j].getValue('static'));
                }
                result.push(aux);
            }
            else if (w.slice(0, 2) == '#a') {
                var attr = null;
                if (w.indexOf('.') != -1) {
                    ll = w.split('.');
                    attr = ll[1];
                    w = ll[0];
                }
                if (w == '#a') {
                    for (var j = 0; j < nodes.length; j++) {
                        x = nodes[j];
                        aux.push(x.getAttr(attr));
                    }
                    result.push(aux);
                }
            }
            else {
                for (var j = 0; j < nodes.length; j++) {
                    x = nodes[j];
                    value = x.getValue();
                    if (isBag(value)) {
                        aux.push(value.getItem(w));
                    } else {
                        aux.push(null);
                    }
                }
                result.push(aux);
            }
        }
        if (asColumns) {
            return result;
        }
        return zip(result);
    },
    columns: function(cols, attrMode) {
        var mode = (attrMode) ? '#a.' : '';
        if (typeof(cols) == 'string') {
            cols = cols.split(',');
        }
        for (var i = 0; i < cols.length; i++) {
            cols[i] = mode + cols[i];
        }
        ;
        return this.digest(cols.join(','), true);
    },
    asObj: function(formatAttributes) {
        var nodes = this._nodes;
        var result = {};
        var v, node, attr;
        for (var i = 0; i < nodes.length; i++) {
            node = nodes[i];
            if (!node._resolver) {
                result[node.label] = node.getValue();
            } else {
                result[node.label] = '**';
            }
        }
        for (attr in formatAttributes) {
            result[attr] = asText(result[attr], formatAttributes[attr]);
        }
        return result;
    },
    asObjList: function(labelAs, formatAttributes) {
        formatAttributes = formatAttributes || {};
        var nodes = this._nodes;
        var result = [];
        for (var i = 0; i < nodes.length; i++) {
            var item = nodes[i].getValue().asObj(formatAttributes);
            if (labelAs) {
                item[labelAs] = nodes[i].label;
            }
            result.push(item);
        }
        return result;
    },
    getResolver: function(path) {
        return this.getNode(path).getResolver();
    },


    /**
     *
     * @param {Object} condition
     */
    getNodes: function(condition/*opzionale*/) {
        /*if(!condition)*/
        return this._nodes;
        /*else :
         return [n for n in self._nodes if condition (n)]
         */
    },

    /**
     *
     * @param {Object} path
     *
     */

    pop: function(path, doTrigger) {
        var n = this.popNode(path, doTrigger);
        if(n){
            return n.getValue()
        }
    },

    delItem: function(path, doTrigger) {
        this.pop(path, doTrigger);
    },
    moveNode:function(fromPos, toPos, doTrigger) {
        if (toPos < 0) {
            return;
        }
        var doTrigger = (doTrigger == null) ? true : doTrigger;
        var destlabel = this.getNodes()[toPos].label;
        if (fromPos instanceof Array && fromPos.length > 1) {
            fromPos.sort();
            var delta = (fromPos[0] < toPos) ? 1 : 0;
            var popped = [];
            for (var i = fromPos.length - 1; i >= 0; i--) {
                popped.push(this._pop('#' + fromPos[i], doTrigger));
            }
            var toPos = this.index(destlabel) + delta;
            var bag = this;
            dojo.forEach(popped, function(n) {
                bag._insertNode(n, toPos, doTrigger);
            });
        } else {
            if (fromPos instanceof Array) {
                fromPos = fromPos[0];
            }
            if (toPos != fromPos) {
                var node = this._pop('#' + fromPos, doTrigger);
                // if(toPos>fromPos){
                //     toPos=toPos-1;
                // }
                this._insertNode(node, toPos, doTrigger);
            }
        }


    },
    popNode: function(path, doTrigger) {
        var node = this.htraverse(path);
        var obj = node.value;
        var label = node.label;
        if (obj) {
            var n = obj._pop(label, doTrigger);
            if(n){
                return n.orphaned();
            }
        }

    },

    /**
     *
     * @param {Object} label
     */
    _pop: function(label, doTrigger) {      //per uso solo interno alla classe
        if (doTrigger == null) {
            doTrigger = true;
        }
        ;
        var p = this.index(label);
        var node = null;
        if (p >= 0) {
            //implementazione diversa da quella python
            node = this._nodes[p]; //ottengo il nodo p-esimo
            //elimino dalla lista dei nodi il nodo p-esimo
            var sx = this._nodes.slice(0, p);
            var dx = this._nodes.slice(p + 1, this._nodes.length);
            this._nodes = sx.concat(dx);
            if ((this._backref) && (doTrigger))
                this.onNodeTrigger({'evt':'del','node':node,'where':this, 'ind':p, 'reason':doTrigger});
        }
        return node;
    },

    /**
     * elimina tutto il contenuto della bag
     */
    clear: function(triggered) {

        if (!triggered) {
            this._nodes.splice(0, this._nodes.length);
        } else {
            var n;
            while (this._nodes.length > 0) {
                n = this._nodes.pop();
                if (this._backref)
                    this.onNodeTrigger({'evt':'del','node':n,'where':this, ind:this._nodes.length});
            }
        }

    },

    /**
     * todo
     */
    merge: function() {
    },
    
    update:function(bagOrObj,mode){
        if(!(bagOrObj instanceof gnr.GnrBag)){
            for(var k in bagOrObj){
                this.setItem(k,bagOrObj[k]);
            }
            return;
        }
        var that = this;
        bagOrObj.forEach(function(n){
            var node_resolver = n.getResolver();
            var node_value = null;
            if (!node_resolver || mode!='static'){
                node_value = n.getValue();
                node_resolver = null;
            }
            var currNode = that.getNode(n.label);
            if(currNode){
                 currNode.updAttributes(n.attr);
                 currNodeValue = currNode.getValue();
                 if (node_resolver){
                     currNode.setResolver(node_resolver);
                 }
                 if ((node_value instanceof gnr.GnrBag) && (currNodeValue instanceof gnr.GnrBag)){
                     currNodeValue.update(node_value)
                 }else{
                     currNode.setValue(node_value);
                 }
            }else{
                that.setItem(n.label,node_value,n.attr);
            }
            
        },mode);
    },
    
    concat: function(b){
        if(!b){
            return;
        }
        var that = this;
        dojo.forEach(b._nodes,function(n){
            n.setParentBag(that);
            that._nodes.push(n);
        });
    },

    /**
     * todo
     */

    deepCopy: function (deep) {
        var mode = deep? '' : 'static';
        var result = new gnr.GnrBag();
        var node;
        var bagnodes = this.getNodes();
        for (var i = 0; i < bagnodes.length; i++) {
            node = bagnodes[i];
            var value = node.getValue(mode);
            value = isBag(value) ? value.deepCopy(deep) : value;
            result.setItem(node.label, value, objectUpdate({}, node.attr));
        }
        return result;
    },
    //-------------------- getNode --------------------------------        
    
    getNodeByAttr: function(attr,value,caseInsensitive) {
        var value = caseInsensitive?value.toLowerCase():value;
        var f = function(n) {
            if((attr in n.attr) && (caseInsensitive?(n.attr[attr].toLowerCase()==value):(n.attr[attr]==value))){
                return n;
            }
        };
        return this.walk(f, 'static');
    },

    getNodeByValue:function(path,value){
        var nodes = this._nodes;
        var n;
        for(var i =0; i<nodes.length; i++){
            n = nodes[i];
            if(n.getValue().getItem(path)==value){
                break;
            };
        }
        return n;
    },

    /**
     * @id getNode
     * @method
     * @memberOf gnr.GnrBag
     * This method returns the BagNode stored at this path.
     * ho verificato in scripting che (5 instanceof Number) = a false
     * nella if ho messo quindi una verifica alternativa che path sia un int
     * @param {Object} path
     * @param {Boolean} asTuple
     * @param {Boolean} autocreate
     * @param {Object} dflt
     */

    getNode: function(path, asTuple, autocreate, _default) {
        if (!path) {
            return this.getParentNode();
        }
        /*if (path%1==0){ 
         alert('path intero')
         return this._nodes[path];
         }*/
        var mynode = this.htraverse(path, autocreate);
        /*if (mynode instanceof dojo.Deferred) {
            // console.error('deferred');
        }*/
        var obj = mynode.value;
        var label = mynode.label;
        var node = null;
        if (obj) {
            if (label.indexOf('?') >= 0) {
                var splittedlabel = label.split('?');
                label = splittedlabel[0];
                node = obj._getNode(label, autocreate);
                if (_default) {
                    node.attr[splittedlabel[1]] = _default;
                }
            } else {
                node = obj._getNode(label, autocreate, _default);
            }

            if (asTuple == true) {
                return {"obj":obj, "node":node};
            }
        }
        return node;
    },

    /**
     * Metodo usato dalla getnode
     * @param {Object} label
     * @param {Object} autocreate
     * @param {Object} dlf
     */
    _getNode: function(label, autocreate, _default) {
        var p = this.index(label);
        var node = null;
        if (p >= 0) {
            node = this._nodes[p];
        }
        else if (autocreate) {
            node = this.newNode(this, label, /*value=*/ _default);
            var i = this._nodes.length;
            this._nodes = this._nodes.concat(node);
            if (this._backref) {
                this.onNodeTrigger({'evt':'ins','node':node,'where':this,'ind':i,'reason':'autocreate'});
            }
        }
        return node;
    },

    /**
     * @id setAttr
     */
    setAttr: function(path, attr, args) {
        this.getNode(path, false, true).setAttr(attr/*, args questa opzione non l'ho implementata nel gnrnode*/);

    },

    /**
     * @id getAttr
     */
    getAttr: function (path, attr, dflt) {
        var node = this.getNode(path);
        if (node != null) {
            return node.getAttr(attr, dflt);
        } else {
            return dflt;
        }
    },

    /**
     * todo
     */
    pathsplit: function() {
    },

    /**
     * todo
     */
    asDict: function() {
        var result = {};
        var node;
        for (var i = 0; i < this._nodes.length; i++) {
            node = this._nodes[i];
            result[node.label] = node.getValue();
        }
        ;
        return result;
    },

    /**
     * @id addItem
     */
    addItem: function(path, value, _attributes, kwargs) {
        if (!kwargs) {
            var kwargs = {};
        }
        kwargs['_duplicate'] = true;
        return this.setItem(path, value, _attributes, kwargs);
    },


    /**
     * @id setItem
     */
    fireItem:function(path,value,attributes,reason){
        value = value==null?true:value;
        this.setItem(path, value, attributes, {'doTrigger':reason == null ? true : reason});
        this.setItem(path, null, attributes, {'doTrigger':false});
    },
    setItem: function(path, value, _attributes, kwargs) {
        if (!kwargs) {
            var kwargs = {};
        }
        if (path == '') {
            if (isBag(value)) {
                for (var i = 0; i < value.getNodes().length; i++) {
                    var node = value.getNodes()[i];
                    var v = node.getResolver() || node.getValue();
                    this.setItem(node.label, v, node.getAttr());
                }
            }
            else if (value instanceof Object) {
                for (var i in value) {
                    this.setItem(i, value[i].valueOf());
                }
            }
            return this;
        }
        else {
            var mynode = this.htraverse(path, /*autocreate*/true);
            var cb = function(mynode, value) {
                var obj = mynode.value;
                var label = mynode.label;
                if (label.indexOf('?') >= 0) {
                    var splittedlabel = label.split('?');
                    label = splittedlabel[0];
                    var attr = splittedlabel[1];
                    var node = obj.getNode(label, false, true);
                    if(kwargs.lazySet && ((node.attr[attr] === value) || ((node.attr[attr]==null) && (value==undefined)))){
                        return;
                    }
                    var auxattr = {};
                    auxattr[attr] = value;
                    var _doTrigger = true;
                    if ('doTrigger' in kwargs) {
                        _doTrigger = kwargs.doTrigger;
                    }
                    node.setAttr(auxattr, _doTrigger, true, attr);
                    return node;
                }
                else {
                    return obj.set(label, value, _attributes, kwargs);
                }
            };
            if (mynode instanceof dojo.Deferred) {
                mynode.addCallback(cb, value);
            }
            else {
                return cb(mynode, value);
            }

        }
    },


    /**
     * @id set
     */
    set: function(label, value, _attributes, kwargs) {
        if (!kwargs) {
            var kwargs = {};
        }
        var resolver = null;
        var _duplicate = kwargs._duplicate || false;
        var _updattr = kwargs._updattr || false;
        var _doTrigger = true;
        if ('doTrigger' in kwargs) {
            _doTrigger = kwargs.doTrigger;
        }
        if (value instanceof gnr.GnrBagResolver) {
            resolver = value;
            value = null;
            if (objectSize(resolver.attributes) >= 0) {
                _attributes = objectUpdate({}, _attributes);
                _attributes = objectUpdate(_attributes, resolver.attributes);
            }
        }

        var i = this.index(label);
        if (i < 0 || _duplicate) {
            if ((label != '#id') && (label[0] == '#')) {
                //raise BagException ('Not existing index in #n syntax')
                return null;
            }
            else {
                var nodeToInsert = this.newNode(this, label, value, _attributes, resolver);
                kwargs._new_position = this._insertNode(nodeToInsert, kwargs._position, _doTrigger);
                kwargs._new_label = nodeToInsert.label;
                return nodeToInsert;
            }
        }
        else {
            var node = this._nodes[i];
            if (resolver) {
                node.setResolver(resolver);
            }
            if(kwargs.lazySet){
                if((node._value===value) || ((node._value==null) && (value==undefined))){
                    return node;
                }
            }
            node.setValue(value, _doTrigger, _attributes, _updattr);
            return node;
        }
    },

    _insertNode: function(node, position, _doTrigger) {
        var n = null;
        var label;
        if (typeof(position) == 'number') {
            n = position;
        }
        else if (position == 0 || position == '<') {
            n = 0;
        } else if (!position || position == '>') {
            n = -1;
        }
        else if (position.charAt(0) == '#') {
            n = parseInt(position.slice(1));
        }
        else {
            if (position.charAt(0) == '<' || position.charAt(0) == '>') {
                label = position.slice(1);
                position = position.charAt(0);
            }
            else {
                label = position;
                position = '<';
            }
            if (label.charAt(0) == '#') {
                n = parseInt(label.slice(1));
            }
            else {
                n = this.index(label);
            }
            if (position == '>' && n >= 0) {
                n = n + 1;
            }
        }
        if (n < 0) {
            n = this._nodes.length;
        }

        this._nodes.splice(n, 0, node);

        if (this._backref && _doTrigger) {
            this.onNodeTrigger({'evt':'ins','node':node,'where':this,'ind':n, 'reason':_doTrigger});
        }
        return n;
    },

    /**
     * @id index
     */
    index: function(label) {
        var result = -1;
        var idx;
        if (label) {
            if (label[0] == '#') {
                if (label.indexOf('=') != -1) {
                    var myarr = label.slice(1).split('=');
                    var k = myarr[0];
                    var v = convertFromText(myarr[1]);
                    if (!k) k = 'id';
                    for (idx = 0; idx < this._nodes.length; idx++) {
                        if (this._nodes[idx].attr[k] == v) {
                            result = idx;
                            break;
                        }
                    }
                }
                else {
                    idx = parseInt(label.slice(1));
                    if (idx < this._nodes.length) {
                        result = idx;
                    }
                }
            }
            else {
                for (idx = 0; idx < this._nodes.length; idx++) {
                    if (this._nodes[idx].label == label) {
                        result = idx;
                        break;
                    }
                }
            }
        }
        return result;
    },

    findNodeById: function(id) {
        var f = function(n) {
            if (n._id == id) {
                return n;
            }
        };
        return this.walk(f, 'static');
    },

    
    forEach: function(callback, mode, kw) {
        this.walk(callback, mode, kw, true);
    },
    walk: function (callback, mode, kw, notRecursive) {
        var result;
        var bagnodes = this.getNodes();
        for (var i = 0; ((i < bagnodes.length) && ((result == null)|| (result=='__continue__'))); i++) {
            result = callback(bagnodes[i], kw, i);
            if (result == null) {
                var value = bagnodes[i].getValue(mode);
                if ((!notRecursive) && (isBag(value))) {
                    result = value.walk(callback, mode, kw);
                }
            }
        }
        return result;
    },
    getBackRef: function() {
        return this._backref;
    },

    hasBackRef: function() {
        return (this._backref == true);
    },

    setBackRef: function(node, parent) {
        if (this._backref != true) {
            this._backref = true;
            this._parent = parent;
            this._parentnode = node;
            for (var i = 0; i < this._nodes.length; i++) {
                this._nodes[i].setParentBag(this);
            }
        }
    },

    clearBackRef: function() {
        var node,value;
        if (this._backref) {
            this._backref = false;
            this._parent = null;
            this._parentnode = null;
            for (var i = 0; i < this._nodes.length; i++) {
                node = this._nodes[i];
                value = node.getStaticValue();
                if (isBag(value)) {
                    value.clearBackRef();
                }
            }
        }
    },

    runTrigger:function(kw) {
        var callbacks,cb;
        for (var subscriberId in this._subscribers) {
            callbacks = this._subscribers[subscriberId];
            cb = callbacks[kw.evt] || callbacks.any;
            if (cb) {
                cb(kw);
            }
        }
    },
    onNodeTrigger: function(/*node,where,ind,pathlist*/kw) {
        //genro.debug('onNodeTrigger:',kw.evt+' - '+kw.node.label );
        kw.pathlist = kw.pathlist || [kw.node.label];
        kw.base = this;
        this.runTrigger(kw);
        if (this._parent != null) {
            kw.pathlist = [this._parentnode.label].concat(kw.pathlist);
            this._parent.onNodeTrigger(kw);
        }
    },
    subscribe: function(subscriberId, kwargs/*obj*/) {
        if (this._backref == false)
            this.setBackRef();
        this._subscribers[subscriberId] = kwargs;
    },
    unsubscribe:function(subscriberId, events) {
        delete this._subscribers[subscriberId];
    },
    fromXmlDoc: function(source, clsdict) {
        var attributes, aux;
        var j;
        var node;

        var attrname,attrvalue;
        var childnode, istxtnode, convertAs;
        var resolverPars = null;
        var js_resolver = null;
        var js_resolvedInfo= null;
        var root = source;
        if (root.nodeType == 9) {
            root = root.lastChild;
        }
        for (var i = 0; i < root.childNodes.length; i++) {
            node = root.childNodes[i];
            convertAs = 'T';
            if (node.nodeType == 1) {
                var tagName = node.tagName || node.nodeName;
                attributes = {};
                resolverPars = null;
                js_resolver = null;
                js_resolvedInfo= null;
                for (j = 0; j < node.attributes.length; j++) {
                    attrname = node.attributes[j].name;
                    attrvalue = node.attributes[j].value;
                    if(attrname=='_resolvedInfo'){
                        js_resolvedInfo = convertFromText(node.attributes[j].value);
                    }
                    else if (attrname == '_resolver') {
                        resolverPars = node.attributes[j].value;
                    }
                    else if (attrname == '_resolver_name') {
                        js_resolver = node.attributes[j].value;
                    }
                    else if (attrname == '_tag') {
                        tagName = node.attributes[j].value;
                    }
                    else if (attrname == '_T') {
                        convertAs = node.attributes[j].value;
                    }
                    else {
                        if (attrvalue.indexOf('::') >= 0) {
                            aux = attrvalue.split('::');
                            var dt = aux.pop();
                            attrvalue = convertFromText(aux.join('::'), dt);
                        }
                        attributes[attrname] = attrvalue;
                    }
                }
                var newcls = objectPop(attributes, '__cls');
                istxtnode = true;
                var textContent = '';
                for (j = 0; j < node.childNodes.length; j++) {
                    childnode = node.childNodes[j];
                    if (!(childnode.nodeType == 3 || childnode.nodeType == 4)) {
                        istxtnode = false;
                        break;
                    }
                    else {
                        textContent = textContent + childnode.nodeValue;
                    }
                }

                if (istxtnode && convertAs!='BAG') {
                    var itemValue = textContent;
                    if (convertAs != 'T') {
                        itemValue = convertFromText(itemValue, convertAs);
                    } else if (stringContains(itemValue, '::')) {
                        itemValue = itemValue.split('::');
                        convertAs = itemValue[1];
                        itemValue = convertFromText(itemValue[0], convertAs);
                    }
                    if (convertAs == 'H') {
                        attributes.dtype = convertAs;
                    }
                    if (resolverPars != null) {
                        resolverPars = genro.evaluate(resolverPars);
                        var cacheTime = 'cacheTime' in attributes ? attributes.cacheTime : resolverPars.kwargs['cacheTime'];
                        resolverPars['cacheTime'] = 0;
                        //resolverPars = dojo.toJson(resolverPars);
                        itemValue = genro.rpc.remoteResolver('resolverRecall', {'resolverPars':resolverPars}, {'cacheTime':cacheTime});
                    } else if (js_resolver) {
                        itemValue = genro.getRelationResolver(attributes, js_resolver, this); // genro['remote_'+js_resolver].call(genro, this, tagName, attributes);
                    }
                    this.addItem(tagName, itemValue, attributes);
                }
                else {
                    var resolver =null;
                    var clsproto = this;
                    if (clsdict != null) {
                        if (newcls) {
                            newcls = clsdict[newcls];
                            if (newcls) {
                                clsproto = newcls.prototype;
                            }
                        }
                    }
                    var newBag = new clsproto.constructor();
                    var newBagNode = this.addItem(tagName, newBag, attributes);
                    if(js_resolver){
                        var resolver = genro.getRelationResolver(attributes, js_resolver, this);
                        newBagNode.setResolver(resolver);
                        newBagNode._status = 'loaded';
                        resolver.lastUpdate = new Date();
                        objectUpdate(newBagNode.attr,js_resolvedInfo);
                    }
                    newBag.fromXmlDoc(node, clsdict);
                }
            }
        }
    },

    /**
     * @id toXml
     */
    toXml: function(kwargs) {
        if (!kwargs) {
            var kwargs = {};
        }
        var encoding = kwargs['encoding'] || "utf-8";
        var result = '<?xml version="1.0" encoding="' + encoding + '"?>\n';
        result = result + xml_buildTag('GenRoBag', this.toXmlBlock(kwargs), null, true);
        return result;
    },


    /**
     * metodo ausiliario di toXml. da non confondere con l'omonimo delle bagNode
     */
    toXmlBlock: function(kwargs) {
        var result = new Array();
        var nodes = this._nodes;
        for (var i = 0; i < nodes.length; i++) {
            result.push(nodes[i]._toXmlBlock(kwargs));
        }
        return result.join('\n');
    },



//metodi sulle formule:

    formula: function(formula, kwargs) {
        this.setBackRef();
        if (this._symbols == null) {
            this._symbols = {};
        }
        var path = 'formula:' + formula;
        var formula = this._symbols[path] || formula;
        var result = new gnr.GnrBagFormula(this, formula, this._symbols, kwargs);
        return result;

    },
    defineSymbol: function(kwargs) {
        if (this._symbols == null) {
            this._symbols = {};
        }
        objectUpdate(this._symbols, fromKwargs(kwargs));

    },
    defineFormula: function(kwargs) {
        var path = null;
        if (this._symbols == null) {
            this._symbols = {};
        }
        if (!(kwargs != null)) {
            kwargs = objectUpdate({}, kwargs);
        }
        for (key in kwargs) {
            path = 'formula:' + key;
            this._symbols[path] = kwargs[key];
        }
    },
    setCallBackItem: function(path, callback, parameters, kwargs) {
        if (!kwargs) {
            var kwargs = {};
        }
        kwargs.method = callback;
        kwargs.parameters = parameters;
        var resolver = new gnr.GnrBagCbResolver(kwargs);
        this.setItem(path, resolver, kwargs);
    },
    get_modified: function() {
        return this._modified;
    },
    set_modified: function(value) {
        if (value == null) {
            this._modified = null;
            this.unsubscribe('modify__');
        }
        else if (this._modified == null) {
            this.subscribe('modify__', {'any':dojo.hitch(this, '_setModified')});
        }
        this._modified = value;
    },
    _setModified: function() {
        this._modified = true;
    },
    getRoot : function() {
        var parent = this.getParent();
        if (parent == null) {
            return this;
        } else {
            return parent.getRoot();
        }
    },
    getFullpath: function(mode, root) {
        if (root == true) {
            root = this.getRoot().getItem('#0');
        }
        var fullpath = '';
        var segment;
        var parentbag = this.getParent();
        if ((parentbag != null) && (!this.isEqual(root))) {
            var parentNode = this.getParentNode();
            if (mode == '#' || mode == '##') {
                segment = parentbag.getNodes().indexOf(parentNode) + '';
                if (mode == '##') {
                    segment = '#' + segment;
                }
            } else {
                segment = parentNode.label;
            }
            fullpath = parentbag.getFullpath(mode, root);
            if (fullpath) {
                fullpath = fullpath + '.' + segment;
            } else {
                fullpath = segment;
            }
        }
        return fullpath;
    },
    getIndex: function() {
        var path = [];
        var resList = [];
        var exploredNodes = [this];
        this._deepIndex(path, resList, exploredNodes);
        return resList;
    },
    isEqual: function(otherbag) {
        if (!otherbag) {
            return false;
        }
        if (this == otherbag) {
            return true;
        }
        ;
        if (this._parentnode && otherbag._parentnode) {
            return this._parentnode._id == otherbag._parentnode._id;
        }
        ;
        return false;
    },

    _deepIndex: function(path, resList, exploredNodes) {
        var node, v;
        for (var i = 0; i < this._nodes.length; i++) {
            node = this._nodes[i];
            v = node.getValue();
            resList.push([path.concat(node.label), node]);
            if ('_deepIndex' in v) {
                if (arrayIndexOf(exploredNodes, v) < 0) {
                    exploredNodes.push(v);
                    v._deepIndex(path.concat(node.label), resList, exploredNodes);
                }
            }
        }
    },

    getIndexList: function(asText) {
        var l = this.getIndex();
        result = [];
        for (var i = 0; i < l.length; i++) {
            result.push(l[i][0].join('.'));
        }
        if (asText) {
            return result.join('\n');
        } else {
            return result;
        }
    },


//------------------------ nuove aggiunte BAG------------------------

    delParentRef: function() {
        this.parent = null;
        this._backref = false;
    },

// --------------- Bag async Calls--------------
    doWithItem: function(path, cb, dflt) {
        var value = this.getItem(path, dflt);
        if (value instanceof dojo.Deferred) {
            //genro.debug('Deferred adding callback (bag.doWithItem) :'+path);
            return value.addCallback(cb);
        } else {
            return cb(value);
        }
    }
});


/*
 NUOVO RESOLVER

 dojo.declare("gnr.BagResolver",null,{
 constructor: function(args, kwargs){
 var a=parseArgs(arguments);
 this._initArgs=a[0];
 this._initKwargs=a[1];
 this._parent=null;

 }
 }
 */
//######################## class BagResolver##########################

dojo.declare("gnr.GnrBagResolver", null, {
    constructor: function(kwargs, isGetter, cacheTime, load) {
        /*  cacheTime > 0: resolve after cacheTime seconds
         cacheTime = 0: resolve always
         cacheTime < 0: resolve once
         */
        this._attributes = {};
        this.setCacheTime(cacheTime || 0);
        this.kwargs = kwargs;
        this.isGetter = isGetter;
        this.lastUpdate = null;
        this._pendingDeferred = [];
        if (load) {
            this.load = load;
        }
    },
    onSetResolver: function(node) {
        //override me
    },
    setCacheTime: function(cacheTime) {
        this.cacheTime = cacheTime; //timedelta(0, cacheTime)
    },
    getCacheTime: function() {
        return this.cacheTime;
    },

    reset: function() {
        this.lastUpdate = null;
    },
    expired: function(kwargs) {
        var expired = false;
        if (this.cacheTime < 0) {
            if (this.lastUpdate == null) {
                expired = true;
            }
        }
        else {
            var now = new Date();
            var delta = (now - (this.lastUpdate || new Date(0))) / 1000;
            expired = (delta > this.cacheTime);
        }
        return expired;
    },
    resolve: function(optkwargs, destinationNode) {
        var destFullpath = destinationNode ? destinationNode.getFullpath(null, genro._data) : '';
        var kwargs = objectUpdate({}, this.kwargs); // update kwargs
        kwargs._destFullpath=destFullpath;
        if (optkwargs) {
            objectUpdate(kwargs, optkwargs);
        }
        if (this.isGetter) {
            return this.load(kwargs);
        }
        else {
            var finalize = dojo.hitch(this, function(r) {
                this.lastUpdate = new Date();
                return r;
            });
            var result = this.load(kwargs,destinationNode); // non isGetter cannot change kwargs

            if (result instanceof dojo.Deferred) {
                //this._mainDeferred = result; // keep a reference for avoid garbage collector
                return result.addCallback(finalize);
                //return this.meToo();
            }
            else {
                return finalize(result, kwargs);
            }
        }
    },
    meToo: function(cb) {
        console.error('Calling meToo');
        var newdeferred = new dojo.Deferred();
        newdeferred.addCallback(cb);
        this._pendingDeferred.push(newdeferred);
        return newdeferred;
    },
    runPendingDeferred:function(pendingDeferred) {
        for (var i = 0; i < pendingDeferred.length; i++) {
            pendingDeferred[i].callback();
        }

    },

    load: function(kwargs, cb) {
        //must be implemented
        return;
    },
    setParentNode: function(parentNode) {
        this._parentNode = parentNode;
    },
    getParentNode: function(parentnode) {
        return this._parentNode;
    },
    htraverse: function(kwargs) {
        var pathlist = kwargs.pathlist;
        var autocreate = kwargs.autocreate;
        return this.resolve().htraverse(pathlist, autocreate);
    },

    keys: function() {
        return this.resolve().keys();
    },
    items: function() {
        return this.resolve().items();
    },
    values: function() {
        return this.resolve().values();
    },
    digest: function(k) {
        var key = k || null;
        return this.resolve().digest(key);
    },
    sum: function(k) {
        var key = k || null;
        return this.resolve().sum(key);
    },
    contains: function() {
        return this.resolve().contains();
    },
    len: function() {
        return this.resolve().len();
    },
    getAttr: function() {
        return this._attributes;
    },
    setAttr: function(attributes) {
        objectUpdate(this._attributes, attributes);
    },
    resolverDescription: function() {
        return this.resolve().toString();
    }

});


//######################## class BagFormula##########################

dojo.declare("gnr.GnrBagFormula", gnr.GnrBagResolver, {
    constructor: function(root, expr, symbols, kwargs) {
        this.root = root;

        if (symbols != null) {
            var symbols = objectUpdate({}, symbols);
        }
        else {
            var symbols = {};
        }
        objectUpdate(symbols, fromKwargs(kwargs));
        this.expr = templateReplace(expr, symbols);
    },


    load: function() {
        var root = this.root;
        var curr = this._parent;
        return eval(this.expr);
    }
});

var fromKwargs = function(kwargs) {
    var key;
    var v = null;
    var bag = 'curr';
    var result = {};
    for (key in kwargs) {
        v = kwargs[key];
        if (stringStartsWith(key, '_')) {
            result[key] = bag + ".getResolver('" + v + "')";
        }
        else {
            result[key] = bag + ".getItem('" + v + "')";
        }
    }
    return result;
};


dojo.declare("gnr.GnrBagGetter", gnr.GnrBagResolver, {
    constructor: function(bag, path, what) {
        this.path = path;
        this.what = what || 'node';
    },
    load: function() {
        var node = genro.getNode(this.path);
        if (thisWhat || this == 'node') {
            return node;
        }
        else if (thisWhat == 'value') {
            return node.getValue();
        }
        else if (thisWhat == 'attr') {
            return node.getAttr();
        }

    }
});
//*******************BagCbResolver****************************

dojo.declare("gnr.GnrBagCbResolver", gnr.GnrBagResolver, {
    constructor: function(kwargs) {
        this.method = kwargs.method;
        this.parameters = kwargs.parameters;
    },

    load: function() {
        return this.method.call(this, this.parameters);
    }
});


gnr.bagRealPath = function(path) {
    if (path.indexOf('#parent') > 0) {
        var lpath = path.split('.');
        path = [];
        for (var i = 0; i < lpath.length; i++) {
            if (lpath[i] != '#parent') {
                path.push(lpath[i]);
            } else {
                path.pop();
            }
        }
        path = path.join('.');
    }
    return path;
};
