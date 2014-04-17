/*
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

// ******************** GnrStoreBag **************************
dojo.require("dojo.data.util.filter");

dojo.declare("gnr.GnrStoreBag", null, {
    _identifier: '#id',
    _staticStore:true,
    _rootNodeName: 'root',
    hideValues: false,
    constructor: function(kw) {
        dojo.mixin(this, kw);
    },

    rootDataNode:function() {
        if (this.datapath) {
            return genro.getDataNode(this.datapath, true, new gnr.GnrBag());
        } else {
            if (!this.mainbag) {
                this.mainbag = new gnr.GnrBag();
            }
            return this.mainbag.getNode(this._rootNodeName, false, true, new gnr.GnrBag());
        }

    },
    rootData:function() {
        var rootData = this.rootDataNode().getValue();
        if (!(rootData instanceof dojo.Deferred)) {
            if (!(rootData instanceof gnr.GnrBag)) {
                rootData = new gnr.GnrBag();
                this.rootDataNode().setValue(rootData, false);
            }
        }
        return rootData;
    },
// -----------------------------------------common API ------------------------------
    getFeatures: function() {
        genro.debug('getFeatures');
        return {
            'dojo.data.api.Read': true,
            'dojo.data.api.Write': true,
            'dojo.data.api.Identity': true,
            'dojo.data.api.Notification': true
        };
    },
// -----------------------------------------read API ------------------------------

    getValue: function(/* item */ item, /* attribute-name-string */ attribute, /* value? */ defaultValue) {
        if(item==null){
            return;
        }
        genro.debug('getValue: item=' + item.label + ' - attribute-name-string=' + attribute + ' - default=' + defaultValue);
        var attributes = item.attr;
        if (attribute == '#k') {
            return item.label;
        }
        else if (attribute == '#v') {
            return item.getValue(null,{_sourceNode:this.sourceNode});
        }
        else if (attribute.indexOf('.') == 0) {
            return item.getValue().getItem(attribute.slice(1));
        }
        else if (attribute in attributes) {
            var result = attributes[attribute];
            if (result == undefined) {
                result = defaultValue;
            }
            return result;
        }
    },

    getValues: function(/* item */ item, /* attribute-name-string */ attribute) {
        genro.debug('getValues: item=' + item.label + ' - attribute-name-string=' + attribute);
        var attributes = item.getAttr();
        if (attribute == '#v') {
            var itemvalue = item.getValue(null,{_sourceNode:this.sourceNode});
            if (itemvalue instanceof gnr.GnrBag) {
                return itemvalue.getNodes();
            }
            else {
                return [
                    {'id':item._id + 'c','label':itemvalue,'attr':item.attr}
                ];
            }
        }
        else if (attribute.indexOf('.') == 0) {
            return [item.getValue().getItem(attribute.slice(1))];
        }
        else {
            if (attribute in attributes) {
                return [attributes[attribute]];
            }
            else {
                return [];
            }
        }
    },
    getAttributes: function(/* item */ item) {
        var attributes = [];

        if (item) {
            genro.debug('getAttributes: item=' + item.label);
            for (var key in item.getAttr()) {
                attributes.push(key);
            }
        }
        return attributes; // array
    },

    hasAttribute: function(/* item */ item, /* attribute-name-string */ attribute) {

        if (this.isItem(item)) {
            genro.debug('hasAttribute: item=' + item.label + ' - attribute-name-string=' + attribute);
            if (attribute == '#v') {
                var resolver = item.getResolver();
                if (resolver && !resolver.lastUpdate) {
                    return 'child_count' in item.attr ? item.attr.child_count > 0 : true;
                } else {
                    var result = item.getValue();
                    if(this.hasChildrenCb && this.hasChildrenCb(item)===false){
                        return null;
                    }
                    if (result instanceof gnr.GnrBag) {
                        return (result.len() > 0);
                    }
                    else if (this.hideValues) {
                        return null;
                    }
                    else {
                        //return (result != null);
                        return true;
                    }
                }
            }
            else {
                return (attribute in item.attr);
            }
        } else {
            return false;
        }


    },

    containsValue: function(/* item */ item, /* attribute-name-string */ attribute, /* anything */ value) {
        genro.debug('containsValue: item=' + item.label + ' - attribute-name-string=' + attribute + ' - value=' + value + ' ---->Unimplemeted', 'alert');
        return false; // boolean
    },

    isItem: function(/* anything */ something) {
        genro.debug('isItem');
        return (something instanceof gnr.GnrBagNode);
    },

    isItemLoaded: function(/* anything */ something) {
        genro.debug('isItemLoaded: something=' + something);

        if (this.isItem(something)) {
            return something.isLoaded();
        } else {
            return true;
        }

    },

    loadItem: function(/* object */ request) {
        genro.debug('loadItem: keywordArgs=' + objectString(request));
        if (!this.isItemLoaded(request.item)) {
            var scope = request.scope ? request.scope : dojo.global;
            var cb = dojo.hitch(scope, request.onItem);
            var result = request.item.getValue();
            if (result instanceof dojo.Deferred) {
                result.addCallback(cb);
            } else {
                cb(result);
            }
        }
    },

    fetch : function(/* Object */ request) {
        genro.debug('loadItem: request=' + objectString(request));
        request = request || {};
        if (!request.store) {
            request.store = this;
        }
        var self = this;
        var _errorHandler = function(errorData, requestObject) {
            if (requestObject.onError) {
                var scope = requestObject.scope || dojo.global;
                requestObject.onError.call(scope, errorData, requestObject);
            }
        };
        var _fetchHandler = function(items, requestObject, fetchMetadata) {
            var fetchMetadata = fetchMetadata || {};
            var oldAbortFunction = requestObject.abort || null;
            var aborted = false;
            var startIndex, endIndex;
            if (fetchMetadata.totalrows) {
                startIndex = 0;
                endIndex = items.length;
            } else {
                startIndex = requestObject.start ? requestObject.start : 0;
                endIndex = requestObject.count ? (startIndex + requestObject.count) : items.length;
            }

            requestObject.abort = function() {
                aborted = true;
                if (oldAbortFunction) {
                    oldAbortFunction.call(requestObject);
                }
            };
            var scope = requestObject.scope || dojo.global;
            if (!requestObject.store) {
                requestObject.store = self;
            }
            if (requestObject.onBegin && items) {
                requestObject.onBegin.call(scope, fetchMetadata.totalrows || items.length, requestObject);
            }
            if (requestObject.sort) {
                items.sort(dojo.data.util.sorter.createSortFunction(requestObject.sort, self));
            }
            if (requestObject.onItem) {
                for (var i = startIndex; (i < items.length) && (i < endIndex); ++i) {
                    var item = items[i];
                    if (!aborted) {
                        requestObject.onItem.call(scope, item, requestObject);
                    }
                }
            }
            if (requestObject.onComplete && !aborted) {
                var subset = null;
                if (!requestObject.onItem) {
                    subset = items.slice(startIndex, endIndex);
                    // if (subset.length==0){
                    // subset = null;
                    // }
                }

                requestObject.onComplete.call(scope, subset, requestObject);
            }
        };
        this._doFetch(request, _fetchHandler, _errorHandler);
        //this._fetchItems(request, _fetchHandler, _errorHandler);
        return request; // Object
    },
    _doFetch : function(request, findCallback, errCallback) {
        var query = request.query;
        var finalize = dojo.hitch(this, function(r) {
            var result = [];
            if (r) {
                var items = r.getNodes();
                if (query) {
                    var ignoreCase = request.queryOptions ? request.queryOptions.ignoreCase : false;
                    result = this._applyQuery(query, ignoreCase, items);
                } else {
                    for (var i = 0; i < items.length; ++i) {
                        var item = items[i];
                        if (item !== null) {
                            result.push(item);
                        }
                    }
                }
            }
            findCallback(result, request);
        });
        var rootData = this.rootData();
        if (rootData instanceof dojo.Deferred) {
            return rootData.addCallback(finalize);
        } else {
            return finalize(rootData);
        }
    },

    close: function(/*dojo.data.api.Request || keywordArgs || null */ request) {
        genro.debug('close: keywordArgs=' + objectString(keywordArgs) + ' - request' + objectString(request) + '  ---->Unimplemented', 'alert');
    },

    getLabel: function(/* item */ item) {
        if (this.isItem(item)) {
            genro.debug('getLabel: item=' + item.label);
            if (this.labelAttribute) {
                return item.attr[this.labelAttribute] || item.label;
            } else if (this.labelCb) {
                return this.labelCb.call(item);
            }
            return item.label;
        } else if (typeof(item) == 'object') {
            if (this.labelCb) {
                return this.labelCb.call(item);
            } else {
                return item.label;
            }
        }
        else {
            return item;
        }
        ;
    },

    getLabelAttributes: function(/* item */ item) {
        genro.debug('getLabelAttributes: item=' + item.label + '  ------>Unimplemented', 'alert');
    },

// -----------------------------------------write API ------------------------------

    newItem: function(/* Object? */ keywordArgs, /*Object?*/ parentInfo) {

        var newItem;
        genro.debug('newItem: item=' + objectString(keywordArgs) + '  ------>Unimplemented', 'alert');
        return newItem; // item
    },

    deleteItem: function(/* item */ item) {
        genro.debug('deleteItem: item=' + item.label + '  ------>Unimplemented', 'alert');
        return false; // boolean
    },

    setValue: function(/* item */ item, /* string */ attribute, /* almost anything */ value) {
        genro.debug('setValue: item=' + item.label + '  ------>Unimplemented', 'alert');
        return false; // boolean
    },

    setValues: function(/* item */ item, /* string */ attribute, /* array */ values) {
        genro.debug('setValues: item=' + item.label + '  ------>Unimplemented', 'alert');
        return false; // boolean
    },

    unsetAttribute: function(/* item */ item, /* string */ attribute) {
        genro.debug('unsetAttribute: item=' + item.label + '  ------>Unimplemented', 'alert');
        return false; // boolean
    },

    save: function(/* object */ keywordArgs) {
        genro.debug('save: keywordArgs=' + objectString(keywordArgs) + '  ------>Unimplemented', 'alert');
    },

    revert: function() {
        genro.debug('revert:   ------>Unimplemented', 'alert');
        return false; // boolean
    },

    isDirty: function(/* item? */ item) {
        genro.debug('isDirty: item=' + item.label + '  ------>Unimplemented', 'alert');
        return false; // boolean
    },
// -----------------------------------------identity API ------------------------------

    getIdentity: function(/* item */ item) {
        // if this._identifier is '#id' we use the _id  of the node
        // if this._identifier is '#k' we use the label  of the node
        // if this._identifier is '#i' we use the position  of the node
        // if this._identifier is '#p' we use the path  of the node
        // if this._identifier is '##' we use the numeric path  of the node
        // if this._identifier is '.xx' we use the child 'xx'  of the node
        // if this._identifier is 'xx' we use the attribute 'xx'  of the node
        if (!( item instanceof gnr.GnrBagNode)) {
            return item.id;
        }
        genro.debug('getIdentity: item=' + item.label);
        var identifier = this._identifier;
        if (identifier == '#id') {
            return item._id;
        } else if (identifier == '#k') {
            return item.label;
        } else if (identifier == '#i') {
            return item.getParentNode().getNodes().indexOf(item);
        }
        else if (identifier == '#p') {
            return item.getFullpath('', this.rootData());
        }
        else if (identifier == '##') {
            return item.getFullpath('##', this.rootData());
        }
        else if (identifier.indexOf('.') == 0) {
            return item.getValue().getItem(identifier.slice(1));
        } else {
            return item.getAttr(identifier);
        }
    },

    getIdentityAttributes: function(/* item */ item) {
        genro.debug('getIdentityAttributes: item=' + item.label + '  ------>Unimplemented', 'alert');
        return null; // string
    },

    fetchItemByIdentity: function(/* object */ request) {
        genro.debug('fetchItemByIdentity: identity=' + request.identity);
        if (!isNullOrBlank(request.identity)) {
            var id = request.identity;
            var item = null;
            var bagnode;
            var nodes = this.rootData().getNodes();
            genro.debug('trying fetchIdentity on ' + nodes.length + ' existing nodes');
            for (var i = 0; i < nodes.length; i++) {
                bagnode = nodes[i];
                if (this.getIdentity(bagnode) == id) {
                    item = bagnode;
                    break;
                }
            }
        }
        else {
            item = null;
        }
        if (request.onItem) {
            var scope = request.scope ? request.scope : dojo.global;
            request.onItem.call(scope, item);
        }
        else {
            return item;
        }

    },
// -----------------------------------------Notification API ------------------------------

    onSet: function(/* item */ item, /* attribute-name-string */ attribute, /* object | array */ oldValue, /* object | array */ newValue) {
        //genro.debug('onSet: item='+item.label+' - value:'+ item._value+' - status:'+item._status);
    },

    onNew: function(/* item */ newItem, /*object?*/ parentInfo) {
        //genro.debug('onNew: item='+newItem.label+'  ------>Unimplemented');
    },

    // item: someItem,                         //The parent item
    //          attribute:  "attribute-name-string",    //The attribute the new item was assigned to.
    //          oldValue: something //Whatever was the previous value for the attribute.  
    //                      //If it is a single-value attribute only, then this value will be a single value.
    //                      //If it was a multi-valued attribute, then this will be an array of all the values minues the new one.
    //          newValue: something //The new value of the attribute.  In the case of single value calls, such as setValue, this value will be
    //                      //generally be an atomic value of some sort (string, int, etc, object).  In the case of multi-valued attributes,
    //                      //it will be an array.

    onDelete: function(/* item */ deletedItem) {
        //genro.debug('onDelete: item='+deletedItem.label+'  ------>Unimplemented');
    },
    _triggerUpd:function(kw) {
        if (kw.updvalue) {
            this.onSet(kw.node, '#v', kw.oldvalue, kw.value);
        }
        if (kw.updattr) {
            for (var attr in kw.node.attr) {
                this.onSet(kw.node, attr, kw.oldattr[attr], kw.node.attr[attr]);
            }
        }
    },
    _triggerIns:function(kw) {
        var parentNode = kw.where.getParentNode();
        if (parentNode === this.rootDataNode()) {
            this.onNew(kw.node);
        } else {
            this.onNew(kw.node, {item:parentNode,attribute:'#v'});
        }

    },
    _triggerDel:function(kw) {
        this.onDelete(kw.node);
    },

// ----------------------------------------- common ------------------------------
    _applyQuery: function(query, ignoreCase, items) {
        var result = [];
        var regexpList = {};
        for (var key in query) {
            var value = query[key];
            if (typeof value === "string") {
                regexpList[key] = dojo.data.util.filter.patternToRegExp(value, ignoreCase);
            }
        }
        for (var i = 0; i < items.length; ++i) {
            var item = items[i];
            if (item != null) {
                var match = true;
                for (var key in query) {
                    var regexp = regexpList[key];
                    match = dojo.some(this.getValues(item, key),
                                     function(v) {
                                         if (v !== null && !dojo.isObject(v) && regexp) {
                                             return (v.toString().match(regexp) != null);
                                         } else if (v === query[key]) {
                                             return true;
                                         }
                                     }
                            );
                    if (!match) {
                        break;
                    }
                }
                if (match) {
                    result.push(item);
                }
            }
        }
        return result;
    }
});
// ******************** GnrStoreGrid **************************
dojo.declare("gnr.GnrStoreGrid", gnr.GnrStoreBag, {
    _doFetch : function(request, findCallback, errCallback) {
        //console.log('****doFetch:'+request.start+' - '+request.count);
        //this.rootData.clear(true)
        var cb = function(node) {
            var v = ( node instanceof gnr.GnrBagNode) ? node.getValue() : null;
            if (v instanceof gnr.GnrBag) {
                findCallback(v.getNodes(), request, node.getAttr());
            } else {
                findCallback([], request);
            }
        };
        if (request.start >= 0) {
            var kwargs = {row_start:request.start,row_count:request.count};
            var value = this.rootDataNode().getValue('', kwargs);
            if (value instanceof dojo.Deferred) {
                return value.addCallback(cb);
            } else {
                cb.call(this, value);
            }
        }
    },
    fetchItemByIdentity: function(/* object */ request) {
        genro.debug('fetchItemByIdentity: identity=' + request.identity);
        if (!request.identity) {
            genro.debug('fetchItemByIdentity: return null');
            return null;
        } else {
            var id = request.identity;
            var finalize = dojo.hitch(this, function(r) {
                var scope = request.scope ? request.scope : dojo.global;
                var result = r.getValue().getNode('#0');
                if (result) {
                    dojo.hitch(scope, request.onItem)(result);
                }
            });
            var result = this.rootDataNode().getValue('', {where:'id=:_pkey',_pkey:id});
            if (result instanceof dojo.Deferred) {
                result.addCallback(finalize);
            }
        }
    }
});

// ******************** GnrStoreQuery **************************
dojo.declare("gnr.GnrStoreQuery", gnr.GnrStoreBag, {

    constructor: function(kw) {
        this.cached_values = {};
        this.cache_time = 60;
    },

    clearCache:function(pkey){
        if(pkey){
            objectPop(this.cached_values,pkey);
        }else{
            this.cached_values = {};
        }
    },

    fetchItemByIdentity: function(/* object */ request) {
        genro.debug('fetchItemByIdentity: identity=' + request.identity);
        if (!request.identity) {
            genro.debug('fetchItemByIdentity: return null');
            var result = new gnr.GnrBagNode();
            result.attr[this.searchAttr] = '';
            var scope = request.scope ? request.scope : dojo.global;
            dojo.hitch(scope, request.onItem)(result);
        } else {
            var id = request.identity;
            if(id in this.cached_values){
                var cached = this.cached_values[id];
                var age = (new Date()-cached.ts)/1000;
                if(age<this.cache_time){
                    dojo.hitch(scope, request.onItem)(cached.result);
                    return;  
                }
            }
            if (isNullOrBlank(id)){
                dojo.hitch(scope, request.onItem)(null);
                return;     
            }
            var parentSourceNode = this._parentSourceNode;
           // if(parentSourceNode.widget && parentSourceNode.widget._lastValue==request.identity){
           //     //lastValue equal to requested identitiy: the fetchItemByIdentity is skipped 9/6/2013 fporcari
           //     return;
           // }
            var selectedAttrs = objectExtract(parentSourceNode.attr,'selected_*',true)
            if(!(('rowcaption' in parentSourceNode.attr) || parentSourceNode.attr._hdbselect || parentSourceNode.attr.condition || objectNotEmpty(selectedAttrs))){
                var recordNodePath = parentSourceNode.attr.value;
                recordNodePath = recordNodePath.slice(1);
                if(recordNodePath.indexOf('.')==0){
                    recordNodePath = recordNodePath.slice(1);
                }
                recordNodePath = recordNodePath.split('.');
                recordNodePath.push('@'+recordNodePath.pop());
                var recordNode = parentSourceNode.getRelativeData().getNode(recordNodePath);
                if(recordNode && 'caption' in recordNode.attr){
                    var value = recordNode.attr._newrecord? '': recordNode.attr.caption;
                    var scope = request.scope ? request.scope : dojo.global;
                    var result = new gnr.GnrBagNode();
                    result.attr[this.searchAttr] = value;
                    result.attr[this._identifier] = request.identity;
                    dojo.hitch(scope, request.onItem)(result);
                    return;                    
                }
            }
            var finalize = dojo.hitch(this, function(r) {
                var result;
                var scope = request.scope ? request.scope : dojo.global;
                result = r.getValue();
                if (result instanceof gnr.GnrBag) {
                    result = result.getNode('#0');
                } else {
                    result = null;
                }
                this.cached_values[request.identity] = {'result':result,'ts':new Date()};
                //if (result) {
                    if(!result){
                        console.log('no result',request);
                    }
                    dojo.hitch(scope, request.onItem)(result);
                //}
            });
            var result = this.rootDataNode().getValue('', {_id:id});
            if (result instanceof dojo.Deferred) {
                result.addCallback(finalize);
            }
        }
    },
    _doFetch : function(request, findCallback, errCallback) {
        //this.rootData.clear(true)
        var query = request.query;

        if (!query.caption) {
            findCallback([], request);
        } else {
            var ignoreCase = request.queryOptions ? request.queryOptions.ignoreCase : false;
            var kwargs = {_id:'',_querystring:query.caption,ignoreCase:ignoreCase};
            var cb = dojo.hitch(this, function(r) {
                var result;
                if (r instanceof gnr.GnrBagNode && r.getValue()) {
                    this.lastFetchAttrs = r.attr;
                    result = r.getValue().getNodes();
                }
                else {
                    result = [];
                    this.lastFetchAttrs = {};
                }
                findCallback(result, request);
            });
            var result = this.rootDataNode().getValue('', kwargs);
            if (result instanceof dojo.Deferred) {
                return  result.addCallback(cb);
            } else {
                return cb(result);
            }

        }
    }
});
