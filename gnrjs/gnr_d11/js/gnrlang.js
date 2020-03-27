/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module lang : Genro utility functions
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

//funzioni di utilità varie

//########################  Lang #########################
const _lf = '\n';
const _crlf = '\r\n';
const _tab = '\t';

function _px(v){
    v+='';
    if(v.indexOf('px')<0){
        v+='px';
    }
    return v;
};
function _T(str,lazy){
    if(isNullOrBlank(str)){
        return str;
    }
    var locale = genro.locale() || 'en-EN';
    var language = locale.split('-')[0];
    var localekey = 'localsdict_'+language;
    var noLocMarker = (str.search(/^!!|\[!!/)<0);
    if(lazy && noLocMarker){
        return str;
    }
    var localsdict = genro.getFromStorage('local',localekey) || {};
    if(isNullOrBlank(localsdict[str])){
        var toTranslate = noLocMarker?'!!'+str:str;
        var result = genro.serverCall('getRemoteTranslation',{txt:toTranslate,language:language}) || {};
        var localizedString = result['translation'];
        if(result.status!='OK'){
            localsdict[str] ='<span class="unlocalized">'+localizedString+'</span>';
        }
        localsdict[str] = localizedString;
        genro.setInStorage('local',localekey,localsdict);
        return localizedString;
    }else{
        return localsdict[str];
    }
    return str;
}

function _F(val,format,dtype){
    return gnrformatter.asText(val,{format:format,dtype:dtype});
};
function _IN(val,str){
    var l = str.split(',');
    return l.indexOf(val)>=0;
};
function isBag(value){
    return value &&(value.htraverse!=null);
};

function isNumericType(dtype){
    return dtype in  {'R':null,'L':null,'I':null,'N':null};
}

function pyref(ref,mode){    
    var node = genro.src._main.getNodeByAttr('__ref',ref);
    if (mode=='w'){
        return node.widget;
    }
    if (mode=='d'){
        return node.getDomNode();
    }
    if (mode=='f'){
        return node.form;
    }
    return node;
    
};
function bagAsObj(bag) {
    var result = {};
    var parentNode = bag.getParentNode();
    if (parentNode) {
        result._a = parentNode.attr;
    }
    dojo.forEach(bag.getNodes(), function(n) {
        result[n.label] = n.getValue();
    });
    return result;
};

function objectAsGrid(obj,labels){
    var labels = labels || 'label,value';
    labels = labels.split(',');
    var result = new gnr.GnrBag();
    if(!obj){
        return result;
    }
    var i=0;
    var v;
    for(var k in obj){
        v = new gnr.GnrBag();
        v.setItem(labels[0],k);
        v.setItem(labels[1],obj[k]);
        result.setItem('r_'+i,v);
        i++;
    }
    result.sort('#k');
    return result;
};
function objectAsHTMLTable(obj,labels){
    labels = labels || 'label,value';
    var b = objectAsGrid(obj);
    return b.asHtmlTable({cells:labels});
};

function arrayContains(arr, item) {
    for (var i = 0; i < arr.length; i++) {
        if (arr[i] == item) {
            return true;
        }
    }
    return false;
}
function copyArray(arraylike){
    if (!arraylike){
        return [];
    }
    var result = [];
    dojo.forEach(arraylike,function(n){result.push(n);});
    return result;
};

function arrayIndexOf(arr, item) {
    for (var i = 0; i < arr.length; i++) {
        if (arr[i] == item) {
            return i;
        }
    }
    return -1;
}
function arrayPushNoDup(arr, item) {
    if (dojo.indexOf(arr, item) < 0) {
        arr.push(item);
    }
    ;
};

function arrayUniquify(arr){
    var result = [];
    dojo.forEach(arr,function(n){
        if(dojo.indexOf(result, n) < 0){
            result.push(n);
        }
    });
    return result;
};


function arrayMatch(a, matchString) {
    if (matchString.indexOf('*') >= 0) {
        matchString = matchString.replace('*', '(.*)');
    }
    return dojo.filter(a, function(item) {
        return item.match(matchString);
    });
}

//funzione di utilità per una split insensibile al punto 
function smartsplit(/*string*/path, /*string*/on) {
    var escape = "\\" + on;
    var pathlist = null;
    if (path.indexOf(escape) != -1) {
        var chrOne = new java.lang.Character(1);
        path = path.replace(escape, chrOne);
        pathlist = path.split(on);
        for (var i in pathlist) {
            pathlist[i].replace(chrOne, on);
        }
    }
    else pathlist = path.split(on);
    return pathlist;
}
function stringSplit(s, c, n) {
    if (n) {
        var f = s.split(c, n);
        var g = s.split(c);
        if (f.length < g.length) {
            f.push(g.slice(f.length).join(c));
        }
        return f;
    } else {
        return s.split(c);
    }
}
function stringEndsWith(s, v) {
    return (s.slice(-v.length) == v);
}

function stringStartsWith(s, v) {
    return (s.slice(0, v.length) == v);
}
function stringContains(s, v) {
    return (s.indexOf(v) >= 0);
}

function stringCapitalize(str,firstOnly) {
    if (firstOnly){
        return str[0].toUpperCase() + str.slice(1);
    }
    return str.replace(/\w+/g, function(a) {
        //return a.charAt(0).toUpperCase() + a.substr(1).toLowerCase();
        return a.charAt(0).toUpperCase() + a.substr(1);

    });
};


function dataTemplate(str, data, path, showAlways,kw) {
    var kw = kw || {};
    var defaults = kw.defaults || {};
    if (!str) {
        return '';
    }
    if (typeof(str)=='object' && str.cb){
        var templateHandler = str;
        if (!templateHandler.template){
            templateHandler.cb.call(templateHandler);
        }
        str = templateHandler.template;
        defaults = templateHandler.defaults || defaults;
        showAlways = showAlways || templateHandler.showAlways;
        
    }
    var templates = kw.templates;
    var masks=kw.masks || {};
    var df_templates= kw.df_templates || {};
    var formats = kw.formats || {};
    var dtypes = kw.dtypes || {};
    var editcols = kw.editcols || {};
    var auxattr = {};
    var scopeSourceNode = null;
    var regexpr = /\$(\#?\@?[a-zA-Z0-9_]+)(\.@?[a-zA-Z0-9_]+)*(\?[a-zA-Z0-9_]+)?(\^[a-zA-Z0-9_]+)?/g;
    var result;
    var is_empty = true;
    var has_field = false;
    
    if(str instanceof gnr.GnrBag){
         templates=str;
         var mainNode =templates.getNode('main');
         str = mainNode.getValue();
         masks = mainNode.attr.masks || masks;
         editcols = mainNode.attr.editcols || editcols;
         formats = mainNode.attr.formats || formats;
         df_templates = mainNode.attr.df_templates || df_templates;
         dtypes = mainNode.attr.dtypes || dtypes;

    }
    
    if (data && typeof(data) == 'string') {
        data = genro._data.getItem(data);
    }
    else if (data instanceof gnr.GnrDomSourceNode) {
        auxattr = data.currentAttributes();
        scopeSourceNode = data;
        data = genro._data.getItem(data.absDatapath(path));
    }
    if (!data && !showAlways) {
        return '';
    }
    if(str.indexOf('${')>=0){
        str = str.replace(/\${(([^}]|\n)*)}/g,function(s0,content){
            if(!content){
                return '';
            }
            var m = content.match(/\$([_a-z\\@][_a-z0-9\\(.|\n)\\@]*)/);
            if(!m){
                return '';
            }
            var k = data.getItem? data.getItem(m[1]):data[m[1]];
            return isNullOrBlank(k)? '':content;
        });
    }
 
    if (data instanceof gnr.GnrBag) {
        if (!data && !showAlways) {
            return '';
        }
        result = str.replace(regexpr,
                            function() {
                                var l = arguments.length;
                                has_field=true;
                                var path=arguments[0].slice(1);
                                path = path.indexOf('^')>=0?path.split('^')[0]:path;
                                var value,valueNode;
                                var as_name = arguments[l-3];
                                as_name = as_name? as_name.slice(1):path;
                                var attrname = arguments[l-4];
                                attrname = attrname?attrname.slice(1):null;
                                var valueattr = {};
                                var dtype = dtypes[as_name];
                                var editpars = editcols[as_name];
                                if(scopeSourceNode && stringStartsWith(path,'#')){
                                    valueNode = genro.getDataNode(scopeSourceNode.absDatapath(path));
                                }else{
                                    valueNode = data.getNode(path);
                                }
                                if (valueNode){
                                   valueattr = valueNode.attr;
                                   dtype = valueattr.dtype || dtype;
                                   value = attrname?valueattr[attrname]:valueNode.getValue(null,{_sourceNode:scopeSourceNode});
                                   if('values' in valueattr){
                                        value = objectFromString(valueattr.values)[value];
                                   }
                                }else{
                                    value = auxattr[as_name]
                                }
                                if(value instanceof gnr.GnrBag){
                                    var subtpl = templates?templates.getItem(as_name):null;
                                    if (subtpl){
                                        var subval=[];
                                        var vl;
                                        value.forEach(function(n){
                                            vl = n.getValue();
                                            subval.push(dataTemplate(subtpl, vl));
                                        });
                                        value = subval.join('');
                                    }else if(as_name in df_templates){
                                        value = dataTemplate(data.getItem(df_templates[as_name]),value);
                                    }else{
                                        value = value.getFormattedValue();
                                    }
                                }else{
                                    if(editpars){
                                        if(editpars['relating_column'] && editpars['caption_field']){
                                            value = data.getItem(editpars['caption_field']);
                                        }
                                    }else{
                                        value = valueattr._displayedValue || value;
                                    }
                                    if(formats[as_name]){
                                        value = gnrformatter.asText(value,{format:formats[as_name],dtype:dtype});
                                    }
                                    if(editpars){                                  
                                        value = '<div class="gnrinlinewidget_container"><div class="gnreditabletext" ondblclick="inlineWidget(event)" varname="'+as_name+'" >'+(isNullOrBlank(value)?'&nbsp':value)+'</div></div>';
                                    }
              
                                    if(masks[as_name]){
                                        value = gnrformatter.asText(value,{mask:masks[as_name]});
                                    }else if(valueattr._formattedValue){
                                        value = valueattr._formattedValue;
                                    }
                                }
                                if (value != null) {
                                    is_empty = false;
                                    if (value instanceof Date) {
                                        value = dojo.date.locale.format(value, {selector:dtype=='H'?'time':'date', format:'short'});
                                    }
                                    return value;
                                } else if(showAlways){
                                    is_empty =false;
                                    return defaults[as_name];
                                }else{
                                    return '';
                                }
                            });
    } else {
        data = data || {};
        var p,plist,sub;
        result = str.replace(regexpr,
                          function(path) {
                              has_field=true;
                              plist = path.slice(1).split('.');
                              p = plist[0];
                              var value = data[p];
                              if (value != null) {
                                    is_empty = false;
                                    sub = plist.slice(1);
                                    if(sub.length && value instanceof gnr.GnrBag){
                                        return gnrformatter.asText(value.getItem(sub));
                                    }
                                    return gnrformatter.asText(value,formats[p]);
                              }else{
                                    return '';
                              }
                          });
    }
    if (has_field && is_empty && !showAlways) {
        return '';
    } else {
        return result;
    }
}
;


function stringStrip(s) {
    if (!s) return s;
    return s.replace(/^[ \t\r\n]+/, '').replace(/[ \t\r\n]+$/, '');
}
function splitStrip(s, sp) {
    r = [];
    var sp = sp || ',';
    dojo.forEach(s.split(sp), function(v) {
        r.push(stringStrip(v));
    });
    return r;
}
function argumentsReplace(s) {
    return s.replace(/\$(\d+)/g, function(s, n) {
        return "arguments[" + (parseInt(n) - 1) + "]";
    });
}

function keyName(keyCode){
    var dk = dojo.keys;
    for(var keyName in dk){
        if(dk[keyName]==keyCode){
            return keyName;
        }
    }
};

function bagPathJoin(path1, path2) {
    var path1 = path1.split('.');
    while (path2.indexOf('../') == 0) {
        path2 = path2.slice(3);
        path1.pop();
    }
    path1 = path1.concat(path2.split('.'));
    return path1.join('.');
}
function objectPop(obj, key, dflt) {
    var result;
    if (obj && (key in obj)) {
        result = obj[key];
        delete obj[key];
    } else {
        result = (typeof dflt == 'undefined') ? null : dflt;
    }
    return result;
}
function objectPopAll(obj) {
    for (var key in obj) {
        delete obj[key];
    }
}
function objectKeyByIdx(obj, idx) {
    var k = 0;
    for (var prop in obj) {
        if (k == idx) {
            return prop;
        }
        k++;
    }
}
function isEqual(a,b){
    if((a===null || a===undefined) && (b===null || b===undefined)){
        return true;
    }
    if(a instanceof gnr.GnrBag && b instanceof gnr.GnrBag){
        return a.isEqual(b);
    }
    if(a instanceof Array && b instanceof Array){
        return a.length == b.length && !a.some(function(elem,idx){return !isEqual(elem,b[idx])});
    }
    a = a instanceof Date ? a.valueOf() : a;
    b = b instanceof Date ? b.valueOf() : b;
    return objectIsEqual(a,b);
};

function objectIsEqual(obj1, obj2) {
    if (obj1 == obj2) {
        return true;
    } else {
        if ((obj1 instanceof Object) && (obj2 instanceof Object)) {
            for (a in obj1) {
                if (!(obj2[a] === obj1[a])) {
                    return false;
                }
            }
            for (a in obj2) {
                if (!(obj2[a] === obj1[a])) {
                    return false;
                }
            }
            return true;
        } else {
            return false;
        }
    }
}

function isNullOrBlank(elem){
    return elem === null || elem===undefined || elem === '';
}

function localType(dtype){
    return {'R':{places:2},'L':{places:0},'I':{places:0},'D':{date:'short'},'H':{time:'short'},'HZ':{time:'short'},'DH':{datetime:'short'},'DHZ':{datetime:'short'}}[dtype];
}
   
function normalizeKwargs(kwargs,str){
    if(!kwargs){
        return;
    }
    var p = objectPop(kwargs,str);
    var kw = objectExtract(kwargs,str+'_*');
    if(!p && !objectNotEmpty(kw)){
        kw = null;
    }
    if(p===true || p===null){
        return kw || (p?{}:null);
    }
    if(typeof(p) == 'object'){
        kw = objectUpdate(kw || {},p);
    }else{
        kw._ = p;
    }
    return kw;
}

function objectExtract(obj, keys, dontpop,dontslice) {
    if(!obj){
        return {};
    }
    var result = {};
    var key,m;
    if (keys.slice(-1) == '*') {
        key = keys.slice(0, -1);
        var key_len = key.length;
        for (var prop in obj) {
            if (prop.slice(0, key_len) == key) {
                result[dontslice?prop:prop.slice(key_len)] = obj[prop];
                if (!dontpop) {
                    delete obj[prop];
                } else if (dontpop != true) {
                    if (!(prop in dontpop)) {
                        delete obj[prop];
                    }
                }
            }
        }
    } else {
        keys = keys.split(',');
        for (var i = keys.length; i--;) {
            key = stringStrip(keys[i]);
            if (key in obj) {
                result[key] = obj[key];
                if (!(dontpop)) {
                    delete obj[key];
                }
            }
        }
    }
    return result;
}

function objectNotEmpty(obj) {
    if (obj) {
        for (var prop in obj) {
            return true;
        }
    }
    return false;
}

function objectAny(obj,cb) {
    if (obj) {
        for (var k in obj) {
            if(cb(k,obj[k])){
                return true;
            }
        }
    }
    return false;
}

function mapConvertFromText(value){
    if(isNullOrBlank(value)){
        return value;
    }
    if (value instanceof Array){
        return value.map(mapConvertFromText);
    }
    if (typeof(value)=='string'){
        return convertFromText(value);
    }
    if(typeof(value)=='object' && !(value instanceof Date)){
        var result = {};
        for (var k in value){
            result[k] = mapConvertFromText(value[k]);
        }
        return result;
    }
    return value;
}

function objectString(obj) {
    var result = [];
    for (var prop in obj) {
        result.push(prop + ':' + obj[prop]);
    }
    return result.join(',');
}
function objectSize(obj) {
    var n = 0;
    for (var prop in obj) {
        n = n + 1;
    }
    return n;
}

function objectKeys(obj) {
    var keys = [];
    for (var prop in obj) {
        keys.push(prop);
    }
    return keys;
}

function objectItems(obj) {
    var keys = [];
    for (var prop in obj) {
        keys.push({key:prop,value:obj[prop]});
    }
    return keys;
}

function objectValues(obj) {
    var values = [];
    for (var prop in obj) {
        values.push(obj[prop]);
    }
    return values;
}

function objectFuncReplace(obj, funcname, func) {
    var oldfunc = obj[funcname];
    obj[funcname] = func;
    if (oldfunc) {
        obj[funcname + '_replaced'] = oldfunc;
    }
}

function objectMixin(obj, source) {
    if (source) {
        for (var prop in source) {
            objectFuncReplace(obj, prop, source[prop]);
        }
    }
    return obj;
}
function objectMap(obj,func){
    for(var k in obj){
        obj[k] = func(obj[k]);
    }
}

function copyJson(obj){
    return JSON.parse(JSON.stringify(obj));
}

function objectUpdate(obj, source, removeNulls) {
    if (source) {
        if (source instanceof gnr.GnrBag){
            source = source.asDict();
        }
        var val;
        for (var prop in source) {
            val = source[prop];
            if (removeNulls && (val == null)) {
                delete obj[prop];
            } else {
                obj[prop] = source[prop];
            }
        }
    }
    return obj;
}

function objectIsContained(obj1, obj2) {
    for (a in obj1) {
        if (!(obj2[a] === obj1[a])) {
            return false;
        }
    }
    return true;
}

function objectRemoveNulls(obj, blackList) {
    blackList = blackList || [null];
    var result = {};
    for (var prop in obj) {
        if ((obj[prop] != null) && (obj[prop] != '')) {
            result[prop] = obj[prop];
        }
    }
    return result;
}

function objectDifference(objOld, objNew) {
    var result = {};
    for (var prop in objNew) {
        if (! prop in objOld) {
            result[prop] = ['I',objNew[prop]];
        } else if (objOld[prop] != objNew[prop]) {
            result[prop] = ['U',objOld[prop],objNew[prop]];
        }
    }
    for (var prop in objOld) {
        if (! (prop in objNew)) {
            result[prop] = ['D',objOld[prop]];
        }
    }
    return result;
}

function objectAsXmlAttributes_old(obj, sep) {
    var sep = sep || ' ';
    var val;
    var result = [];
    for (var prop in obj) {
        val = obj[prop];
        if (typeof(val) == 'string') {
            val = val.replace(/\</g, '&lt;');
            val = val.replace(/\&/g, '&amp;');
            val = val.replace(/\>/g, '&gt;');
            val = val.replace(/\"/g, '&quot;');
            val = val.replace(/\'/g, '&apos;');
            val = val.replace(/\n/g, '&#10;');
            val = val.replace(/\r/g, '&#13;');
            val = val.replace(/\t/g, '&#09;');
            result.push(prop + "=" + quoted(val));

        } else if (typeof(obj[prop]) != 'function') {
            result.push(prop + "=" + quoted(asTypedTxt(obj[prop])));
        }
    }
    return result.join(sep);
}
function objectAsXmlAttributes(obj, sep) {
    sep = sep || ' ';
    var val;
    var result = [];
    for (var prop in obj) {
        val = obj[prop];
        if(typeof(val)=='function'){
            continue;
        }
        if (typeof(val) != 'string') {
            val = asTypedTxt(val);
        }
        val = val.replace(/\</g, '&lt;');
        val = val.replace(/\&/g, '&amp;');
        val = val.replace(/\>/g, '&gt;');
        val = val.replace(/\"/g, '&quot;');
        val = val.replace(/\'/g, '&apos;');
        val = val.replace(/\n/g, '&#10;');
        val = val.replace(/\r/g, '&#13;');
        val = val.replace(/\t/g, '&#09;');
        result.push(prop + "=" + quoted(val));
    }
    return result.join(sep);
}


function objectAsStyle(obj) {
    var sep = sep || ' ';
    var result = [];
    var val;
    for (var prop in obj) {
        val = obj[prop];
        if(!isNullOrBlank(val)){
            result.push(prop + ":" + obj[prop] + ';');
        }
    }
    return result.join(' ');
}

function objectFromStyle(style) {
    var result = {};
    if (style) {
        stylelist = style.split(';');
        for (var i = 0; i < stylelist.length; i++) {
            var onestyle = stylelist[i];
            if (stringContains(onestyle, ':')) {
                var kv = onestyle.split(':');
                result[stringStrip(kv[0])] = stringStrip(kv[1]);
            }
        }
    }
    return result;
};

function objectFromString(values,sep,mode){
    if(!values){
        return {};
    }
    var ch = sep || (values.indexOf('\n')>=0?'\n':',');
    values = values.split(ch);
    var result = {};
    for (var i = 0; i < values.length; i++) {
        val = values[i];
        if (val.indexOf(':') > 0) {
            val = val.split(':');
            result[val[0]] = val[1];
        }else if(mode=='k'){
            result[val] = true;
        }else if(mode=='kv'){
            result[val]=val;
        }else {
            result['caption_'+i] = val;
        }
    }
    return result;
};


//funzione di utilità che elimina i blank attorno ad una stringa.
stripBlank = function(string) {
    var re = /\w+/;
    return re.exec(string);
};


//+++++++++++++++++templateReplace (da spostare in dict o string)++++++
templateReplace = function(string, symbolsdict) {
    var re = /\$([\w]*)/;
    while (string.search(re) != -1) {
        var k = re.exec(string)[1];
        var v = symbolsdict[k] || '';
        string = string.replace(re, v);
    }
    return string;
};

zip = function(list) {
    var result = [];
    var curr = null;
    var tuple;
    var tc = list.length;
    if(tc==0){
        return [];
    }
    var tn = list[0].length;

    for (var i = 0; i < tn; i++) {
        tuple = [];
        for (var j = 0; j < tc; j++) {
            tuple.push(list[j][i]);
        }
        result.push(tuple);
    }
    return result;
};

function asTypedTxt(value, dtype) {
    if(typeof(value)=='function'){
        return;
    }
    var typedText = convertToText(value, {'xml':true,'dtype':dtype});
    var valType = typedText[0];
    var valText = typedText[1];
    if (valType != '' && valType != 'T') {
        value = valText + '::' + valType;
    }
    return value;
}
;

function quoted(astring) {
    var mystring = new String(astring);
    if (mystring.indexOf('"') == -1) {
        return '"' + mystring + '"';
    }
    if (mystring.indexOf("'") == -1) {
        return "'" + mystring + "'";
    }
    else {
        return "invalid string";
    }
}
;


function convertFromText(value, t, fromLocale) {
    if(isNullOrBlank(value)){
        return null
    }
    if (typeof(value)!='string') {
        return value;
    }
    if (!t){
        var k = value.lastIndexOf('::');
        if(k>=0){
            t = value.slice(k).slice(2);
            if(['HTML','JS','RPC','JSON','NN','BAG','A','T','L','N','I','B','D','H','DH','DHZ','P','X'].indexOf(t)>=0){
                value = value.slice(0,k);
            }
        }
    }
    var t = t || 'T';
    var result;
    t = t.toUpperCase();
    if (t == 'NN') {
        return null;
    }
    else if (t == 'L') {
        if (fromLocale) {
            value = dojo.number.parse(value);
        } else {
            value = parseInt(value);
        }
        value._gnrdtype = t;
        return value;
    }
    else if (t == 'R' || t == 'N') {
        if (fromLocale) {
            value = dojo.number.parse(value);
        } else {
            value = parseFloat(value);
        }
        value._gnrdtype = t;
        return value;
    }
    else if (t == 'B') {
        return (value.toLowerCase() == 'true');
    }
    else if ((t == 'D') || (t == 'DH') || (t == 'DHZ')) {
        if (fromLocale) {
            var selector = (t == 'DH' || t == 'DHZ') ? 'datetime' : 'date';
            result = dojo.date.locale.parse(value, {selector:selector});
        } else {
            if(t=='D'){
                value = value.split('.')[0].replace(/\-/g, '/');
            }
            result = new Date(value); 
        }
        result._gnrdtype=t;
        return result;
    }
    else if (t == 'H') {
        if (fromLocale) {
            result = dojo.date.locale.parse(value, {selector:'time'});
        } else {
            value = value.split(':');
            if (value.length < 3) {
                value.push('00');
            }
            result = new Date(1971, null, null, Number(value[0]), Number(value[1]), Number(value[2]));
        }
        result._gnrdtype=t;
        return result;
    }
    else if (t == 'JS') {
        if(window.genro){
            return genro.evaluate(value);
        }else{
            return dojo.fromJson(value);
        }
    }
    else if (t == 'BAG' || t=='X') {
        try{
            return new gnr.GnrBag(value);
        }catch(e){
            console.error('Parsing error',e.toString());
            return new gnr.GnrBag({error:e.toString()});
        }
        
    }
    return value;
}
var gnrformatter = {
    asText :function (value,valueAttr){
        var formatKw =  objectUpdate({},valueAttr);
        var dtype = objectPop(formatKw,'dtype');
        var formattedValue;
        var format = objectPop(formatKw,'format');
        if((value===null || value===undefined) && dtype!='B'){
            if(isNumericType(dtype) && format && format.includes(';')){ 
                value = 0;
            }else{
                return '';
            }
        }
        dtype = dtype|| guessDtype(value);
        if(format && typeof(format)!='string'){
            var formatdict = format;
            format = objectPop(format,'format') || objectPop(format,'pattern');
            objectUpdate(formatKw,formatdict);
        }
        
        if(format && dtype=='L' && format.indexOf('.')>=0){
            dtype='N';
        }
        objectUpdate(formatKw,objectExtract(formatKw,'format_*'));
        var handler = this['format_'+dtype];
        var mask = formatKw.mask;
        if(handler){
            formattedValue = handler.call(this,value,format,formatKw);
        }else{
            formattedValue = value+'';
        }
        if(!mask || !formattedValue){
            return formattedValue;
        }
        return mask.replace(/%s/g, formattedValue);

    },
    format_P:function(value,format,formatKw){
        if (!format){
            return value;
        }
        var c,c_zoom;
        if(typeof(format)=='string' && stringStartsWith(format,'auto')){
            if(format.indexOf(':')){
                format = format.split(':')
                var c_zoom = parseFloat(format[1]);
            }
            if(value.indexOf('?')>=0){
                var parsedUrl = parseURL(value);
                format = objectExtract(parsedUrl.params,'v_*');
                value = value.split('?')[0];
                if(parsedUrl.params._pc){
                    value = genro.addParamsToUrl(value,{_pc:parsedUrl.params._pc});
                }
            }
        }
        if(typeof(format)=='string'){
            format = objectFromString(format);
        }
        if(formatKw){
            format = objectUpdate(format,formatKw);
        }
        format['style'] = format['style'] || '';
        if('h' in format){
            var c_style = '';
            if(c_zoom){
                format['h'] = format['h'] * c_zoom;
                format['w'] = format['w'] * c_zoom;
            }
            var c ='<div style="height:'+format["h"]+'px;width:'+format["w"]+'px;overflow:hidden;'+format["style"]+'">';
            objectPop(format,'style');
            if (c_zoom){
                c_style = "-webkit-transform:scale("+c_zoom+");-webkit-transform-origin:0px 0px;-moz-transform:scale("+c_zoom+");-moz-transform-origin:0px 0px;"
            }
            c = c+'<div style="'+c_style+'">';
        }
        var img_style = 'margin-top:'+(-parseFloat(format['y'] || 0))+'px; margin-left:'+(-parseFloat(format['x'] || 0))+'px;-webkit-transform:scale('+parseFloat(format['z'] || 1)+') rotate('+parseFloat(format['r'] || 0)+'deg); -moz-transform:scale('+parseFloat(format['z'] || 1)+') rotate('+parseFloat(format['r'] || 0)+'deg);';
        var img =  '<img style="'+img_style + (format['style'] ||'') +'" src="'+value+'"/>';
        if(c){
            return c_zoom?c+img+'</div></div>':c+img+'</div>';
        }
        return img;
    },
    
    format_T:function(value,format,formatKw){
        if(value===''){
            return value;
        }
        if(!format){
            return value;
        }
        if(format=='autolink'){
            return highlightLinks(value);
        }
        if(format=='mailto'){
            return makeLink('mailto:'+value,value);
        }
        if(format=='phone'){
            return makeLink('tel:'+value,value);
        }
        if(format=='skype'){
            return makeLink('skype:'+value,value);
        }
        if(format=='download'){
            return makeLink(value,'Download',true);
        }
        if(format=='playsound'){
            return makeLink('javascript:genro.lockScreen(true,"sound"); genro.playUrl("'+value+'",function(){genro.lockScreen(false,"sound")});','<div class="iconbox sound"></div>')
        }
        if(typeof(format)=='string' && format.indexOf('#')>=0){ //to check
            format = format.split('');
            value = value.split('');
            var result = [];
            dojo.forEach(format,function(n){
                if(n==value[0] || n=='#'){
                    if(value.length>0){
                        result.push(value.shift());
                    }
                }else{
                    result.push(n);
                }
            });
            result = result.concat(value);
            return result.join('');
        }
    },
    format_D:function(value,format,formatKw){
        if(!value){
            return '';
        }
        var opt = {selector:'date'};
        var standard_format = 'long,short,medium,full';
        var week_format = 'W,w,WD'
        var result = '';
        if(format){
            if(standard_format.indexOf(format)>=0){
                opt.formatLength = format;
            }else if (week_format.indexOf(format)>=0){
                return ''+deltaWeeks(null,value,format);;
            }else{
                opt.datePattern = format;
            }
        }
        return dojo.date.locale.format(value, objectUpdate(opt, formatKw));
    },
    
    format_H:function(value,format,formatKw){
        var opt = {selector:'time'};
        var standard_format = 'long,short,medium,full'
        if(format){
            if(standard_format.indexOf(format)>=0){
                opt.formatLength = format;
            }else{
                opt.timePattern = format;
            }
        }
        return dojo.date.locale.format(value, objectUpdate(opt, formatKw));
    },
    
    format_DH:function(value,format,formatKw){
        if (typeof(value)=="number"){
            value=new Date(value)
        }
        var opt = {selector:'datetime'};
        var standard_format = 'long,short,medium,full';
        if(format){
            if(standard_format.indexOf(format)>=0){
                opt.formatLength = format;
            }else{
                format = format.split('|');
                opt.datePattern = format[0];
                opt.timePattern = format[1];
            }
        }
        return dojo.date.locale.format(value, objectUpdate(opt, formatKw));
    },

    format_B:function(value,format,formatKw){
        var format = format || 'true,false';
        format = format.split(',');
        return (value === null && format.length==3)?format[2]:(value?format[0]:format[1]);
    },
    format_L:function(value,format,formatKw){
        formatKw.places=0;
        return this.format_N(value,format,formatKw);
    },
    format_R:function(value,format,formatKw){
        return this.format_N(value,format,formatKw);
    },
    
    format_N:function(value,format,formatKw){
        /*formatKw:
            currency: ISO4217 currency code, a three letter sequence like "USD"
            locale: override the locale used to determine formatting rules
            pattern override formatting pattern with this string
            places(Number) fixed number of decimal places to show. This overrides any information in the provided pattern.
            round (Number) 5 rounds to nearest .5; 0 rounds to nearest whole (default). -1 means don't round.
            symbol localized currency symbol;
        */
        var opt = {};
        var standard_format = 'decimal,scientific,percent,currency'; //decimal default;

        if(format){
            if(format.indexOf(';')>=0){
                var formats = format.split(';'); //format='#0,00;-;(#0,00)'
                if(value===0){
                    return formats[1];
                }
                if(value<0 && formats.length>2){
                    format = formats[2];
                    value = -value;
                }else{
                    format = formats[0];
                }
            }
            if(standard_format.indexOf(format)>=0){
                opt.type = format;
            }else{
                opt.pattern = format;
            }
        }
        if(format=='meter' || format=='progress'){
            formatKw = formatKw || {};
            formatKw.min = formatKw.min || 0;
            formatKw.max = formatKw.max || 100;
            var p = [];
            for(var k in formatKw){
                p.push(k+'="'+formatKw[k]+'"')
            }
            return '<'+format+' style="width:100%;" value="'+value+'"'+' ' +p.join(' ')+ ' ></'+format+'>';
        }
        if(format=='bytes'){
            var s = ['Bytes','KB','MB','GB','TB'];
            if (value == 0) {return '0 Bytes'};
            var i = parseInt(Math.floor(Math.log(value) / Math.log(1024)));
            return (value / Math.pow(1024, i)).toFixed(1) + ' ' + s[[i]]
        }
        if(format=='epoch'){
            return _F(new Date(value*1000))
        }
        if(format=='DHMS'){
            var r = []
            var curr = value;
            r.push(curr%60+'s');
            curr = Math.floor(curr/60);
            if(curr){
                r.push(curr%60+'m');
                curr = Math.floor(curr/60);
                if(curr){
                    r.push(curr%24+'h');
                    curr = Math.floor(curr/24);
                    if(curr){
                        r.push(curr+'d');
                    }
                }
            }
            r.reverse();
            return r.join(' ')
        }
        return (formatKw.currency ? dojo.currency:dojo.number).format(value, objectUpdate(opt, formatKw))
    },
    format_X:function(value,format,formatKw){
        return value.getFormattedValue(format);
        //var tpl = formatKw.tpl;
        //var rowtpl = formatKw.rowtpl;
        //if(!tpl){
        //    
        //}else if (tpl){
        //    return dataTemplate(value,tpl);
        //}else if(rowtpl){
        //    var r = [];
        //    value.forEach(function(n),{
        //        r.push(dataTemplate(n._value));
        //    });
        //}
    },
    format_AR:function(value,joiner,formatKw){
        value = dojo.map(value,function(n){return _F(n)});
        return value.join(joiner || ',');
    },
    format_NN:function(value,format,formatKw){
        return '';
    },
    format_FUNC:function(value,format,formatKw){
        return value.toString();
    },
    format_OBJ:function(value,format,formatKw){
        var result = [];
        var v;
        var indent = formatKw.indent || '';
        if(indent){
            result.push('')
        }
        formatKw.format_indent = indent+'  ';
        for(var k in value){
            v = this.asText(value[k],formatKw);
            result.push(indent+k+':'+v);
        }
        formatKw.format_indent = indent;
        return result.join(format || '\n');
    }
}

function guessDtype(value){
    if (value instanceof File){
        return 'FILE';
    }
    if(value===null || value===undefined){
        return 'NN';
    }
    if(isBag(value)){
        return 'X'
    }
    if(value instanceof gnr.GnrBagNode){
        return 'BAGNODE';
    }
    var t = typeof(value);
    if(t=='string'){
        return 'T';
    }
    if(t=='boolean'){
        return 'B';
    }
    if(t=='number'){
        return value%1==0?'L':'N';
    }if(t=='function'){
        return 'FUNC';
    }
    if(value instanceof Date){
        if(( value.getFullYear()==1970) && (value.getMonth()==11) && (value.getDate()==31)){
            return 'H';
        }
        if ( (value.getHours()==0) && (value.getMinutes()==0) && (value.getSeconds()==0) && (value.getMilliseconds()==0)){
            return 'D';
        }
        return 'DH';
    }
    if(value instanceof Array){
        return 'AR';
    }
    return 'OBJ';
};

function convertToText(value, params) {
    if (value == null || value == undefined) {
        return ['NN', ''];
    }
    var result;
    var opt;
    params = objectUpdate({}, params);
    var mask = objectPop(params, 'mask');
    var format = objectPop(params, 'format');
    var dtype = objectPop(params, 'dtype');
    var forXml = objectPop(params, 'xml');
    var t = typeof(value);
    if (t == 'string') {
        result = ['T', value];
    }
    else if (t == 'boolean') {
        format = format || 'true,false';
        format = format.split(',');
        if (value === null && format.length==3) {
            result = format[2];
        }else {
            result = value?format[0]:format[1];
        }
        result = ['B', result];
        
    } else if (t == 'number') {
        if (format) {
            var v = numFormat(value, format);
        } else {
            var v = value.toString();
        }
        if (dtype) {
            result = [dtype,v];
        }
        else {
            if (value == parseInt(v)) {
                result = ['L', v];
            } else {
                result = ['N', v];
            }
        }
    }
    else if (value instanceof Date) {
        var selectors = {'D':'date','H':'time','DH':null};
        if (!dtype) {
            dtype = value._gnrdtype || (value.toString().indexOf('Thu Dec 31 1970') == 0 ? 'H' : 'D');
        }
        var opt = {'selector':selectors[dtype]};
        if(dtype=='DHZ'){
            return ['DHZ',value.toISOString()]
        }
        if (forXml) {
            opt.timePattern = 'HH:mm:ss';
            opt.datePattern = 'yyyy-MM-dd';
        } else {
            opt = objectUpdate(opt, params);
            opt.formatLength = format;
        }
        var result = [dtype || 'D',v = dojo.date.locale.format(value, opt)];

    }

    else if (value.toXml) {
        result = ['bag',value.toXml({mode:'static'})];
    }
    else if (t == 'object') {
        result = ['JS',dojo.toJson(value)];
    }
    if (mask) {
        result[1] = mask.replace(/%s/g, result[1]);
    }
    return result;
};

function asText(value, params) {
    return convertToText(value, params)[1];
};


function numFormat(num, params) {
    if (typeof(params) == 'string') {
        var decimal_precision = params[2];
        var thousand_sep = params[0];
        var decimal_sep = params[1];
    } else {
        params = params || {};
        var decimal_precision = params['decimal_precision'] || 0;
        var thousand_sep = params['thousand_sep'] || ',';
        var decimal_sep = params['decimal_sep'] || '.';
    }
    num = num || 0;
 
    if (typeof(num) == 'string') {
        num = parseFloat(num);
    }
 
    num_str = num.toFixed(decimal_precision);
 
    var arr, int_str, dec_str;
    if (num_str.indexOf('.') != -1) {
        arr = num_str.split('.');
        int_str = arr[0];
        dec_str = arr[1];
    } else {
        int_str = num_str;
        dec_str = '0';
    }
 
    var c = 0;
    var sep_str = "";
 
    for (var x = int_str.length; x > 0; x--) {
        c = c + 1;
        if (c == 4 && int_str[x - 1] != '-') {
            c = 0;
            sep_str = thousand_sep + sep_str;
        }
        sep_str = int_str[x - 1] + sep_str;
    }
 
    if (decimal_precision > 0) {
        return sep_str + decimal_sep + dec_str;
    } else {
        return sep_str;
    }
}





function parseArgs(arglist) {
    var kwargs = {};
    if (arglist.length > 1) {
        if (arglist[arglist.length - 1] instanceof Object) {
            kwargs = arglist.pop();
        }
    }
    return [arglist,kwargs];
}


function isdigit(value) {
    return !(value.replace(/\d/g, ""));
}

function xml_buildTag(tagName, value, attributes, xmlMode) {
    var dtype = attributes ? attributes.dtype : null;
    var typedText = convertToText(value, {'dtype':dtype,xml:true});
    var valType = typedText[0];
    var valText = typedText[1];

    var attrAsText = objectAsXmlAttributes(attributes);

    var originalTag = tagName;

    tagName = originalTag.replace(/\W/g, '_').replace('__', '_');
    if (isdigit(tagName.slice(0, 1))) {
        tagName = '_' + tagName;
    }

    if (tagName != originalTag) {
        var result = '<' + tagName + ' _tag="' + originalTag + '"';
    } else {
        var result = '<' + tagName;
    }

    if (valType != '' && valType != 'T') {
        result = result + ' _T=' + quoted(valType);
    }
    if (attrAsText) {
        result = result + ' ' + attrAsText;
    }
    if (valText != '') {
        if (!xmlMode) {
            if (valText.search(/<|>|&/) != -1) {
                valText = '<![CDATA[' + valText + ']]>';
            }
        }
        if (valText.indexOf('\n') != -1) {
            valText = '\n' + valText + '\n';
        }
        result = result + '>' + valText + '</' + tagName + '>';
    }
    else {
        result = result + '/>';
    }
    return result;
}

function timeStamp() {
    var d = new Date();
    return d.valueOf();
}
function macroExpand_GET(fnc) {
    var macroGET = /(\W|^)GET (?:\s*)(\^?[\w\.\#\@\$\?-]+)/g;
    fnc = fnc.replace(macroGET, "$1this.getRelativeData('$2')");
    return fnc;
}
function macroExpand_SET(fnc) {
    var macroSET = /(\W|^)SET (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/gm;
    fnc = fnc.replace(/;SET/g, '; SET').replace(macroSET, "$1this.setRelativeData('$2', $3)$4 ");
    return fnc;
}
function macroExpand_PUT(fnc) {
    var macroSET = /(\W|^)PUT (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/gm;
    fnc = fnc.replace(/;PUT/g, '; PUT').replace(macroSET, "$1this.setRelativeData('$2', $3, null, false, false)$4 ");
    return fnc;
}
function macroExpand_FIRE(fnc) {
    var macroSET = /(\W|^)FIRE (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/g;
    fnc = fnc.replace(/;FIRE/g, '; FIRE').replace(macroSET, "$1this.setRelativeData('$2', $3, null, true)$4 ");

    var macroSET = /(\W|^)FIRE (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)(;?)/g;
    fnc = fnc.replace(/;FIRE/g, '; FIRE').replace(macroSET, "$1this.setRelativeData('$2', true, null, true)$3 ");
    return fnc;
}
function macroExpand_FIRE_AFTER(fnc) {
    var macroSET = /(\W|^)FIRE_AFTER (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/g;
    fnc = fnc.replace(/;FIRE_AFTER/g, '; FIRE_AFTER').replace(macroSET, "$1this.setRelativeData('$2', $3, null, true,null,10)$4 ");

    var macroSET = /(\W|^)FIRE_AFTER (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)(;?)/g;
    fnc = fnc.replace(/;FIRE_AFTER/g, '; FIRE_AFTER').replace(macroSET, "$1this.setRelativeData('$2', true, null, true,null,10)$3 ");
    return fnc;
}

function macroExpand_PUBLISH(fnc) {
    var macroSET = /(\W|^)PUBLISH (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/g;
    fnc = fnc.replace(/;PUBLISH/g, '; PUBLISH').replace(macroSET, "$1genro.publish('$2', $3)$4 ");

    var macroSET = /(\W|^)PUBLISH (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)(;?)/g;
    fnc = fnc.replace(/;PUBLISH/g, '; PUBLISH').replace(macroSET, "$1genro.publish('$2')$3 ");
    return fnc;
}

function cleanJsCode(code) {
    return code.replace(/\n/g, '').replace(/;(\s)+/g, ';');
}
function escapeLiterals(code) {
    return code.replace(/'/g, "\\\'").replace(/"/g, "\\\'");
}
function eventToString(e) {
    var result = '';
    if (e.shiftKey) {
        result += "Shift";
    }
    if (e.ctrlKey) {
        result += "Ctrl";
    }
    if (e.altKey) {
        result += "Alt";
    }
    if (e.metaKey) {
        result += "Meta";
    }
    return result;
}
function serialize(_obj) {
    // Other browsers must do it the hard way
    switch (typeof _obj) {
        // numbers, booleans, and functions are trivial:
        // just return the object itself since its default .toString()
        // gives us exactly what we want
        case 'number':
        case 'boolean':
        case 'function':
            return _obj;
            break;

        // for JSON format, strings need to be wrapped in quotes
        case 'string':
            return '\'' + _obj + '\'';
            break;

        case 'object':
            var str;
            if (_obj.constructor === Array || typeof _obj.callee !== 'undefined') {
                str = '[';
                var i, len = _obj.length;
                for (i = 0; i < len - 1; i++) {
                    str += serialize(_obj[i]) + ',';
                }
                str += serialize(_obj[i]) + ']';
            }
            else {
                str = '{';
                var key;
                for (key in _obj) {
                    str += key + ':' + serialize(_obj[key]) + ',';
                }
                str = str.replace(/\,$/, '') + '}';
            }
            return str;
            break;

        default:
            return 'UNKNOWN';
            break;
    }
}
function stringHash(str){
    var result = str.split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0);return a&a},0);
    return Math.abs(result);
};

function stringToColour(str) {
    if(!str){
        return;
    }
    while(str.length<30){
        str+=str;
    }
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    var colour = '#';
    for (var i = 0; i < 3; i++) {
      var value = (hash >> (i * 8)) & 0xFF;
      colour += ('00' + value.toString(16)).substr(-2);
    }
    return colour;
};

function parseURL(url) {
    var a =  document.createElement('a');
    a.href = url;
    return {
        source: url,
        protocol: a.protocol.replace(':',''),
        host: a.hostname,
        port: a.port,
        query: a.search,
        origin:a.origin,
        pathname:a.pathname,
        params: (function(){
            var ret = {},
                seg = a.search.replace(/^\?/,'').split('&'),
                len = seg.length, i = 0, s;
            for (;i<len;i++) {
                if (!seg[i]) { continue; }
                s = seg[i].split('=');
                ret[s[0]] = s[1];
            }
            return ret;
        })(),
        file: (a.pathname.match(/\/([^\/?#]+)$/i) || [,''])[1],
        hash: a.hash.replace('#',''),
        path: a.pathname.replace(/^([^\/])/,'/$1'),
        relative: (a.href.match(/tps?:\/\/[^\/]+(.+)/) || [,''])[1],
        segments: a.pathname.replace(/^\//,'').split('/')
    };
}

function serializeURL(parsedUrl){
    var result = parsedUrl.origin+parsedUrl.pathname || '';
    return genro.addParamsToUrl(result,parsedUrl.params);
};


function funcCreate(fnc, pars, scope,showError) {
    if (fnc) {
        var pars = pars || '';
        if (typeof(fnc) == 'string') {
            if (scope && (fnc in scope)) {
                return scope[fnc];
            }
            var fnc = stringStrip(fnc);
            fnc = argumentsReplace(fnc);
            fnc = macroExpand_GET(fnc);
            fnc = macroExpand_SET(fnc);
            fnc = macroExpand_PUT(fnc);
            fnc = macroExpand_FIRE_AFTER(fnc);
            fnc = macroExpand_PUBLISH(fnc);
            fnc = macroExpand_FIRE(fnc);
            if (!stringStartsWith(fnc, 'function')) {
                fnc = 'function(' + pars + '){' + fnc + '\n}';
            }
            fnc = genro.evaluate(fnc,showError);
            if (scope) {
                fnc = dojo.hitch(scope, fnc);
            }
        }
        return fnc;
    }
}
function makeLink(href, title,dl,target) {
    var target = target || '';
    var dl = dl || false;
    if (dl){
        href = href+'?download=True';
    }
    if (target){
        return "<a href='" + href + "' target=\"+target+\">" + title + "</a>";
    }
    else{
        return "<a href='" + href + "'>" + title + "</a>";
    }
}

function highlightLinks(text) {
    var safedict = {};
    var k = 0;
    var safekey;
    text = text.replace(/(?:<a)(.*?)(?:a>)/gim, function(reallink){
        safekey = 'RLINK_'+k;
        safedict[safekey] = reallink;
        k++;
        return safekey;
    });

    text = text.replace(/(?:\b|\+)(?:mailto:)?([\w\.+#-]+)@([\w\.-]+\.\w{2,4})\b/g, function(address) {
        return makeLink('mailto:' + address, address);
    });
    text = text.replace(/((\w+:\/\/)[-a-zA-Z0-9:@;?&=\/%\+\.\*!'\(\),\$_\{\}\^~\[\]`#|]+)/g, function(link) {
        return makeLink(link, link,false,'_blank');
    });
    for(var k in safedict){
        text = text.replace(k,safedict[k]);
    }
    return text;
}

function funcApply(fnc, parsobj, scope,argNames,argValues,showError) {
    var parsobj = parsobj || {};
    var argNames = argNames || [];
    var argValues = argValues || [];
    for (var attr in parsobj) {
        argNames.push(attr);
        argValues.push(parsobj[attr]);
    }
    argNames.forEach(function(arg,idx){
        if(!(arg in parsobj)){
            parsobj[arg] = argValues[idx];
        }
    });
    
    argNames.push('_kwargs');
    argValues.push(parsobj);
    if(typeof(fnc)=='function'){
        var signature = fnc.toString().match(/function *\(([\w \,]*)\)/)[1];
        var idx;
        if(signature){
            var argValuesCopy = copyArray(argValues);
            var valid = true;
            splitStrip(signature).reverse().forEach(function(par){
                idx = argNames.indexOf(par);
                if(idx>0){
                    argNames = argNames.splice(idx,1).concat(argNames);
                    argValuesCopy = argValuesCopy.splice(idx,1).concat(argValuesCopy);
                }else{
                    valid = false;
                }
            });
            argValues = valid?argValuesCopy:argValues;
        }       
    }else{
        fnc = funcCreate(fnc, argNames.join(','),scope,showError);
    }
    return fnc.apply(scope, argValues);
}
function deltaWeeks(dateStart,dateEnd,format){
    var today = new Date();
    var dd = deltaDays(dateStart || today,dateEnd || today);
    format = format || 'w';
    if (format=='W'){
        return Math.trunc(dd/7);
    }
    if (format=='w'){
        return Math.round10(dd/7,-2);
    }
    if (format=='WD'){
        return `${Math.trunc(dd/7)}w${dd%7}d`
    }
};

function deltaDays(dateStart,dateEnd,excludeWD){
    var excludeWD = excludeWD || '';
    var delta = 1;
    var result = 0;
    var currDate = new Date(dateStart);
    var wd;
    if(dateStart>dateEnd){
        delta = -1;
    }
    while(currDate.toLocaleDateString()!=dateEnd.toLocaleDateString()){
        result+=delta;
        currDate.setDate(currDate.getDate()+delta);
        wd = currDate.getDay();
    }
    return result;
};

function addDaysToDate(dateStart,daysToAdd,excludeWD){
    var excludeWD = excludeWD || '';
    var currDate = new Date(dateStart);
    var delta = 1;
    var wd;
    if(daysToAdd<0){
        daysToAdd = -daysToAdd;
        delta = -1;
    }
    while(daysToAdd>0){
        currDate.setDate(currDate.getDate()+delta);
        wd = currDate.getDay();
        if(excludeWD.indexOf(wd)<0){
            daysToAdd--;
        }
    }
    return currDate;
};

function localeParser(/*String*/value, /*Object?*/options) {
    // summary:
    //      Convert a properly formatted string to a primitive Date object,
    //      using locale-specific settings.
    //
    // description:
    //      Create a Date object from a string using a known localized pattern.
    //      By default, this method parses looking for both date and time in the string.
    //      Formatting patterns are chosen appropriate to the locale.  Different
    //      formatting lengths may be chosen, with "full" used by default.
    //      Custom patterns may be used or registered with translations using
    //      the addCustomFormats method.
    //      Formatting patterns are implemented using the syntax described at
    //      http://www.unicode.org/reports/tr35/#Date_Format_Patterns
    //
    // value:
    //      A string representation of a date
    //
    // options: object {selector: string, formatLength: string, datePattern: string, timePattern: string, locale: string, strict: boolean}
    //      selector- choice of 'time', 'date' (default: date and time)
    //      formatLength- choice of long, short, medium or full (plus any custom additions).  Defaults to 'short'
    //      datePattern,timePattern- override pattern with this string
    //      am,pm- override strings for am/pm in times
    //      locale- override the locale used to determine formatting rules
    //      strict- strict parsing, off by default

    var info = dojo.date.locale._parseInfo(options);
    var tokens = info.tokens, bundle = info.bundle;
    var re = new RegExp("^" + info.regexp + "$");
    var match = re.exec(value);
    //console.log('value:'+value+'  -  re:'+"^" + info.regexp + "$"+'   -match:'+match)
    if (!match) {
        return null;
    } // null

    var widthList = ['abbr', 'wide', 'narrow'];
    //1972 is a leap year.  We want to avoid Feb 29 rolling over into Mar 1,
    //in the cases where the year is parsed after the month and day.
    var result = new Date(1972, 0);
    var expected = {};
    var amPm = "";
    dojo.forEach(match, function(v, i) {

        if (!i) {
            return;
        }
        var token = tokens[i - 1];
        var l = token.length;
        //console.log('match :'+match[i]+'  -token:'+token+'  - result:'+result)
        switch (token.charAt(0)) {
            case 'y':

                if (l != 2) {
                    //interpret year literally, so '5' would be 5 A.D.
                    result.setFullYear(v);
                    expected.year = v;

                } else {
                    if (v < 100) {
                        v = Number(v);
                        //choose century to apply, according to a sliding window
                        //of 80 years before and 20 years after present year
                        var year = '' + new Date().getFullYear();
                        var century = year.substring(0, 2) * 100;
                        var yearPart = Number(year.substring(2, 4));
                        var cutoff = Math.min(yearPart + 20, 99);
                        var num = (v < cutoff) ? century + v : century - 100 + v;
                        result.setFullYear(num);
                        expected.year = num;

                    } else {
                        //we expected 2 digits and got more...
                        if (options.strict) {
                            return null;
                        }
                        //interpret literally, so '150' would be 150 A.D.
                        //also tolerate '1950', if 'yyyy' input passed to 'yy' format
                        result.setFullYear(v);
                        expected.year = v;

                    }
                }
                break;
            case 'M':
                if (l > 2) {
                    var months = bundle['months-format-' + widthList[l - 3]].concat();
                    if (!options.strict) {
                        //Tolerate abbreviating period in month part
                        //Case-insensitive comparison
                        v = v.replace(".", "").toLowerCase();
                        months = dojo.map(months, function(s) {
                            return s.replace(".", "").toLowerCase();
                        });
                    }
                    v = dojo.indexOf(months, v);
                    if (v == -1) {
//                      console.debug("dojo.date.locale.parse: Could not parse month name: '" + v + "'.");
                        return null;
                    }
                } else {
                    v--;
                }
                result.setMonth(v);
                expected.month = v;
                //console.log('expected.month = v;'+v)
                break;
            case 'E':
            case 'e':
                var days = bundle['days-format-' + widthList[l - 3]].concat();
                if (!options.strict) {
                    //Case-insensitive comparison
                    v = v.toLowerCase();
                    days = dojo.map(days, "".toLowerCase);
                }
                v = dojo.indexOf(days, v);
                if (v == -1) {
//                  console.debug("dojo.date.locale.parse: Could not parse weekday name: '" + v + "'.");
                    return null;
                }

                //TODO: not sure what to actually do with this input,
                //in terms of setting something on the Date obj...?
                //without more context, can't affect the actual date
                //TODO: just validate?
                break;
            case 'd':
                result.setDate(v);
                expected.date = v;
                //console.log('case d: result.setDate(v);'+v+'   result:'+result)
                break;
            case 'D':
                //FIXME: need to defer this until after the year is set for leap-year?
                result.setMonth(0);
                result.setDate(v);
                break;
            case 'a': //am/pm
                var am = options.am || bundle.am;
                var pm = options.pm || bundle.pm;
                if (!options.strict) {
                    var period = /\./g;
                    v = v.replace(period, '').toLowerCase();
                    am = am.replace(period, '').toLowerCase();
                    pm = pm.replace(period, '').toLowerCase();
                }
                if (options.strict && v != am && v != pm) {
//                  console.debug("dojo.date.locale.parse: Could not parse am/pm part.");
                    return null;
                }

                // we might not have seen the hours field yet, so store the state and apply hour change later
                amPm = (v == pm) ? 'p' : (v == am) ? 'a' : '';
                break;
            case 'K': //hour (1-24)
                if (v == 24) {
                    v = 0;
                }
            // fallthrough...
            case 'h': //hour (1-12)
            case 'H': //hour (0-23)
            case 'k': //hour (0-11)
                //TODO: strict bounds checking, padding
                if (v > 23) {
//                  console.debug("dojo.date.locale.parse: Illegal hours value");
                    return null;
                }

                //in the 12-hour case, adjusting for am/pm requires the 'a' part
                //which could come before or after the hour, so we will adjust later
                result.setHours(v);
                break;
            case 'm': //minutes
                result.setMinutes(v);
                break;
            case 's': //seconds
                result.setSeconds(v);
                break;
            case 'S': //milliseconds
                result.setMilliseconds(v);
//              break;
//          case 'w':
//TODO              var firstDay = 0;
//          default:
//TODO: throw?
//              console.debug("dojo.date.locale.parse: unsupported pattern char=" + token.charAt(0));
        }
    });

    var hours = result.getHours();
    if (amPm === 'p' && hours < 12) {
        result.setHours(hours + 12); //e.g., 3pm -> 15
    } else if (amPm === 'a' && hours == 12) {
        result.setHours(0); //12am -> 0
    }

    //validate parse date fields versus input date fields
    if (expected.year && result.getFullYear() != expected.year) {
//      console.debug("dojo.date.locale.parse: Parsed year: '" + result.getFullYear() + "' did not match input year: '" + expected.year + "'.");
        return null;
    }
    if (expected.month && result.getMonth() != expected.month) {

//      console.debug("dojo.date.locale.parse: Parsed month: '" + result.getMonth() + "' did not match input month: '" + expected.month + "'.");
        return null;
    }
    // ----------------- Patch per 28 maggio  INIZIO ------------------------
    if ((expected.date == 28) && (expected.month == 4) && (result.getDate() == 27)) {
        result.setDate(expected.date);
    }
    // ----------------- Patch per 28 maggio  FINE------------------------
    if (expected.date && result.getDate() != expected.date) {
        return null;
    }

    //TODO: implement a getWeekday() method in order to test 
    //validity of input strings containing 'EEE' or 'EEEE'...
    return result; // Date
}
;

function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function flattenString(str,forbidden,replacer){
    replacer = replacer || '_';
    var forbidden = forbidden || ['.'];
    var result = str;
    var pattern;
    forbidden.forEach(function(c){
        pattern = new RegExp("\\"+c,'g');
        result = result.replace(pattern,replacer);
    });
    return result;
}

function canAccessIFrame(iframe) {
    var html = null;
    try { 
      // deal with older browsers
      var doc = iframe.contentDocument || iframe.contentWindow.document;
      html = doc.body.innerHTML;
    } catch(err){
      // do nothing
    }

    return(html !== null);
}