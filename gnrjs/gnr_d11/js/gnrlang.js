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
function bagAsObj(bag){
    var result = {};
    var parentNode = bag.getParentNode();
    if (parentNode) {
        result._a = parentNode.attr;
    }
    dojo.forEach(bag.getNodes(),function(n){
            result[n.label] = n.getValue();
    });
    return result;
}

function arrayContains(arr,item){
    for (var i = 0; i < arr.length; i++) {
            if (arr[i] == item) {
                return true;
            }
        }
        return false;
}

function arrayIndexOf(arr,item){
    for (var i = 0; i < arr.length; i++) {
            if (arr[i] == item) {
                return i;
            }
        }
        return -1;
}

//funzione di utilità per una split insensibile al punto 
function smartsplit(/*string*/path, /*string*/on)
{
   var escape = "\\"+on;
   var pathlist=null;
   if (path.indexOf(escape)!=-1){
       var  chrOne=new java.lang.Character(1);
       path = path.replace(escape,chrOne);
       pathlist = path.split(on);
       for (var i in pathlist){
           pathlist[i].replace(chrOne,on);
       }
   }
   else pathlist = path.split(on);
   return pathlist; 
}
function stringSplit(s,c,n){
    if (n){
        var f = s.split(c,n);
        var g = s.split(c);
        if (f.length < g.length){
            f.push(g.slice(f.length).join(c));
        }
        return f;
    } else {
        return s.split(c);
    }
}
function stringEndsWith (s,v) {
    var lastIndex=s.lastIndexOf(v);
    return (lastIndex>=0) ? (lastIndex+v.length==s.length) : false;
}

function stringStartsWith (s,v) {
    return (s.indexOf(v)==0);
}
function stringContains(s,v) {
    return (s.indexOf(v)>=0);
}

function stringCapitalize(str){
    return str.replace(/\w+/g, function(a){
        //return a.charAt(0).toUpperCase() + a.substr(1).toLowerCase();
        return a.charAt(0).toUpperCase() + a.substr(1);
        
    });
};

function dataTemplate(str, data, path){
    var regexpr = /\$([a-z0-9.@?_]+)/g;
    var result;
    var is_empty = true;
    if(!data){
        return '';
    } 
    else if(typeof(data) == 'string'){
        data = genro._data.getItem(data);
    }
    else if(data instanceof gnr.GnrDomSourceNode){
        data = genro._data.getItem(data.absDatapath());
    }
    if(data instanceof gnr.GnrBag){
         if (path){
             data = data.getItem(path);
         }
         if (!data){
             return '';
         }
         result = str.replace(regexpr,
                              function(path){
                                  var value=data.getItem(path.slice(1));
                                  if (value !=null){
                                      is_empty = false;
                                      if (value instanceof Date){
                                          value = dojo.date.locale.format(value,{selector:'date', format:'short'});
                                      }
                                      return value;
                                  }else{
                                      return '';
                                  }
                              });       
    } else {
        return str.replace(regexpr,
                           function(path){
                               var value=data[path.slice(1)];
                               if (value !=null){
                                   is_empty = false;
                                   if (value instanceof Date){
                                    value = dojo.date.locale.format(value,{selector:'date', format:'short'});
                                   }
                                   return value;
                               }else{
                                   return '';
                               }
                           });
    }
    if (is_empty){
        return '';
    }else{
        return result;
    }    
};



function stringStrip(s) {
    if (!s) return s;
    return s.replace(/^[ \t\r\n]+/,'').replace(/[ \t\r\n]+$/,'');
}

function argumentsReplace(s) {
  return s.replace(/\$(\d+)/g, function(s, n){
                                      return "arguments[" + (parseInt(n)-1) + "]";
                                      });
}

function bagPathJoin (path1,path2) {
    var path1=path1.split('.');
    while (path2.indexOf('../')==0){
        path2=path2.slice(3);
        path1.pop();
    }
    path1=path1.concat(path2.split('.'));
    return path1.join('.');
}
function objectPop (obj, key, dflt) {
    var result;
    if (typeof dflt == 'undefined'){
        var dflt=null;
    }
    if ((obj instanceof Object) && (key in obj)){
        result = obj[key];
        delete obj[key];
    } else {
        result = dflt;
    }
    return result;
}
function objectPopAll (obj) {
    for (var key in obj){
        delete obj[key];
        }
}
function objectKeyByIdx(obj,idx){
    var k = 0;
    for (var prop in obj){
        if (k == idx){
            return prop;
        }
        k++;
    }
}

function objectExtract (obj, keys, dontpop) {
    var result = {};
    var key,m;
    if  (/[\*]$/.test(keys)){
        
        key='^'+keys.replace('*','(.*)');
        for (var prop in obj){
            m=prop.match(key);
            if (m){
                result[m[1]] = obj[prop];
                if(!dontpop){
                    delete obj[prop];
                } else if(dontpop!=true){
                    if (!(prop in dontpop)){
                        delete obj[prop];
                    }
                }
            }
        }
    }else{
        keys = keys.split(',');
        for (var i =0; i<keys.length; i++){
            key = stringStrip(keys[i]);
            if (key in obj){
                result[key] = obj[key];
                if(!(dontpop)){
                    delete obj[key];
                }
            }
        }
    }
    return result;
}
function objectExtract_ (obj, keys, dontpop) {
    keys = keys.split(',');
    var result = {};
    var key;
    for (var i =0; i<keys.length; i++){
        key = stringStrip(keys[i]);
        if (key in obj){
            result[key] = obj[key];
            if(!(dontpop)){
                delete obj[key];
            }
        }
    }
    return result;
}
function objectNotEmpty (obj) {
    if (obj){
        for (var prop in obj){
            return true;
        }
    }
    return false;
}
function objectString (obj) {
    var result=[];
    for (var prop in obj){
        result.push(prop+':'+obj[prop]);
    }
    return result.join(',');
}
function objectSize (obj) {
    var n=0;
    for (var prop in obj){
        n=n+1;
    }
    return n;
}

function objectKeys (obj) {
    var keys=[];
    for (var prop in obj){
        keys.push(prop);
    }
    return keys;
}
function objectFuncReplace(obj, funcname, func){
    var oldfunc = obj[funcname];
    obj[funcname]=func;
    if (oldfunc){
        obj[funcname+'_replaced']=oldfunc;
    }
}

function objectMixin (obj,source) {
    if (source){
        for (var prop in source){
            objectFuncReplace(obj, prop, source[prop]);
        }
    }
    return obj;
}

function objectUpdate (obj, source, removeNulls) {
    if (source){
        var val;
        for (var prop in source){
            val = source[prop];
            if (removeNulls && (val==null)){
                delete obj[prop];
            } else {
                obj[prop]=source[prop];
            }
        }
    }
    return obj;
}

function objectIsContained(obj1, obj2){
    for (a in obj1){
        if (!(obj2[a]===obj1[a])){
            return false;
        }
    }
    return true;
}

function objectIsEqual(obj1, obj2){
    if (obj1 == obj2){
        return true;
    }else{
        if ((obj1 instanceof Object)&&(obj2 instanceof Object)){
           for (a in obj1){
                if (!(obj2[a]===obj1[a])){
                    return false;
                }
            }
            for (a in obj2){
                if (!(obj2[a]===obj1[a])){
                    return false;
                }
            }
            return true;
        }else{
            return false;
        }
     
    }
    
}

function objectRemoveNulls (obj,blackList) {
    var blackList= blackList || [null];
    var result={};
    for (var prop in obj){
        if ((obj[prop]!=null) && (obj[prop]!='')){
        result[prop] = obj[prop];
        }
    }
    return result;
}

function objectDifference (objOld,objNew) {
    var result={};
    for (var prop in objNew){
        if (! prop in objOld){
            result[prop]=['I',objNew[prop]];
        }else if (objOld[prop]!=objNew[prop]){
            result[prop]=['U',objOld[prop],objNew[prop]];
        }
    }
    for (var prop in objOld){
        if (! prop in objNew){
            result[prop]=['D',objOld[prop]];
        }
    }
    return result;
}

function objectAsXmlAttributes (obj,sep){
    var sep = sep || ' ';
    var val;
    var result = [];
    for (var prop in obj){
        val=obj[prop];
        if (typeof(val)=='string'){
            val = val.replace(/\</g,'&lt;');
            val = val.replace(/\&/g,'&amp;');
            val = val.replace(/\>/g,'&gt;');
            val = val.replace(/\"/g,'&quot;');
            val = val.replace(/\'/g,'&apos;');
            val = val.replace(/\n/g,'&#10;');
            val = val.replace(/\r/g,'&#13;');
            val = val.replace(/\t/g,'&#09;');
            result.push(prop+"="+ quoted(val));
            
        }else{
            result.push(prop+"="+ quoted(asTypedTxt(obj[prop])));
        }
    }
    return result.join(sep);
}

function objectAsStyle (obj){
    var sep = sep || ' ';
    var result = [];
    for (var prop in obj){
        result.push(prop+":"+ obj[prop]+';');
    }
    return result.join(' ');
}

function objectFromStyle (style){
    var result = {};
    if (style){
        stylelist = style.split(';');
        for (var i=0; i < stylelist.length; i++){
            var onestyle = stylelist[i];
            if (stringContains(onestyle,':')){
                var kv = onestyle.split(':');
                result[stringStrip(kv[0])] = stringStrip(kv[1]);
            }   
        }
    }
    return result;
}



//funzione di utilità che elimina i blank attorno ad una stringa.
stripBlank= function(string){
    var re= /\w+/;
    return re.exec(string);
};


//+++++++++++++++++templateReplace (da spostare in dict o string)++++++
templateReplace = function(string, symbolsdict){
    var re=/\$([\w]*)/;
    while(string.search(re)!=-1){
        var k = re.exec(string)[1];
        var v = symbolsdict[k] || '';
        string=string.replace(re, v);
    }
    return string;
};

zip = function(list){
    var result = [];
    var curr = null;
    var tuple;
    var tc = list.length;
    var tn = list[0].length;

    for (var i = 0; i<tn; i++){
        tuple = [];
        for (var j=0; j<tc; j++){
            tuple.push(list[j][i]);
        }
        result.push(tuple);
    }
    return result;
};

function asTypedTxt(value){
    var typedText = convertToText(value);
    var valType = typedText[0];
    var valText = typedText[1];
    if (valType!='' && valType!='T'){
            value = valText + '::' + valType;
    }
    return value;
};

function quoted(astring){
    var mystring = new String(astring);
    if (mystring.indexOf('"') == -1){
        return '"'+ mystring + '"';
    }
    if (mystring.indexOf("'") == -1){
        return "'"+ mystring + "'";
    }
    else{return "invalid string";}
};


function convertFromText (value, t, fromLocale){
    t=t.toUpperCase();
    if (t=='NN'){
        return null;
    }
    else if (t=='L'){
        if(fromLocale){
            return dojo.number.parse(value);
        } else {
            return parseInt(value);
        }
    }   
    else if (t=='R'){
        if(fromLocale){
            return dojo.number.parse(value);
        } else {
            return parseFloat(value);
        }
    }
    else if (t=='B'){
        return (value.toLowerCase()=='true');
    }
    else if ((t=='D') || (t=='DH')){
        if(fromLocale){
            var selector = (t=='DH') ? 'datetime' : 'date';
            return dojo.date.locale.parse(value, {selector:selector});
        } else {
            return new Date(value.split('.')[0].replace(/\-/g,'/'));
        }
    }
    else if (t=='H'){
        if(fromLocale){
            return dojo.date.locale.parse(value, {selector:'time'});
        } else {
            value = value.split(':');
            if(value.length < 3){
                value.push('00');
            }
            return new Date(1971,null,null,Number(value[0]),Number(value[1]),Number(value[2]));
        }
    }
    else if (t=='JS'){
        return genro.evaluate(value);
    }
    else if (t='BAG' && !value){
        return new gnr.GnrBag();
    }
    return value;
}

function convertToText (value, params){
    if (value==null || value == undefined){
        return ['NN', ''];
    }
    var result;
    var opt;
    params = objectUpdate({}, params);
    var mask = objectPop(params,'mask');
    var format = objectPop(params,'format');
    var dtype = objectPop(params,'dtype');
    var forXml = objectPop(params,'xml');
    var t = typeof(value);
    
    if (t=='string') {
        result = ['T', value];
    } 
    else if (t=='boolean') {
        if(value){
            result = ['B', 'true'];
        } else {
            result = ['B', 'false'];
        }
    } else if (t=='number'){
        if (format){
            var v = numFormat(value, format);
        } else {
            var v = value.toString();
        }
        if (value == parseInt(v)){
            result = ['L', v];
        } else {
            result = ['R', v];
        }
     }  else if ((value instanceof Date) && dtype=='H'){
            if (forXml){
                opt = {selector:'time',timePattern:"H:mm:ss"};
            }
            else{
                opt = {selector:'time'};
            }
            opt = objectUpdate(opt,params);
            result = ['H',v= dojo.date.locale.format(value,opt)];
            
    }  else if (value instanceof Date) {
        if (format){
            opt = {selector:'date'};
            opt.formatLength = format;

            result = ['D', dojo.date.locale.format(value, opt)];
            
            //result = ['D', format.replace(
            //            '%Y', value.getFullYear()).replace(
            //            '%d', value.getDate()).replace(
            //            '%m', (value.getMonth()+1))
            //        ];
        } else {
            result = ['D', value.getFullYear() + '-' +
                          (value.getMonth()+1) + '-' +
                           value.getDate()];
        }
    }   
    else if (value instanceof gnr.GnrBag){
        result=['bag',value.toXml({mode:'static'})];
    }
     else if (t=='object'){
            result=['JS',dojo.toJson(value)];
    }
    
    if (mask){
        result[1] = mask.replace(/%s/g, result[1]);
    }
    return result;
    //elif isinstance(value, time): return 'H'  
};

function asText (value, params){
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
    if (num_str.indexOf('.')!=-1){
        arr = num_str.split('.');
        int_str = arr[0];
        dec_str = arr[1];
    } else {
        int_str = num_str;
        dec_str = '0';
    }
    
    var c = 0;
    var sep_str = "";
    
    for (var x = int_str.length; x > 0; x--){
        c = c + 1;
        if (c==4 && int_str[x-1]!='-'){
            c = 0;
            sep_str = thousand_sep + sep_str;
        }
        sep_str = int_str[x-1]+sep_str;
    }
    
    if (decimal_precision > 0){
        return sep_str + decimal_sep + dec_str;
    } else {
        return sep_str;
    }
}        
        
function parseArgs(arglist){
    var kwargs={};
    if (arglist.length>1){
        if (arglist[arglist.length-1] instanceof Object){
            kwargs = arglist.pop();
        }
    }
    return [arglist,kwargs];
}


function isdigit(value){
    return !(value.replace(/\d/g,""));
}

function xml_buildTag(tagName, value, attributes, xmlMode){
        var dtype=attributes? attributes.dtype : null;
        var typedText = convertToText(value,{'dtype':dtype,xml:true});
        var valType = typedText[0];
        var valText = typedText[1];
    
        var attrAsText = objectAsXmlAttributes(attributes);
        
        var originalTag = tagName;
        
        tagName = originalTag.replace(/\W/g, '_').replace('__','_');
        if (isdigit(tagName.slice(0,1))){
            tagName = '_' + tagName;
        }
        
        if (tagName != originalTag){
            var result = '<' + tagName + ' _tag="' + originalTag + '"';
        } else {
            var result = '<' + tagName;
        }
        
        if (valType!='' && valType!='T'){result=result+' _T='+ quoted(valType);}
        if (attrAsText){result=result+' '+attrAsText;}
        if (valText!=''){
            if (!xmlMode){
                if (valText.search(/<|>|&/) !=-1){
                    valText='<![CDATA[' + valText+ ']]>';
                    }
            }
            if (valText.indexOf('\n')!=-1){valText='\n' + valText+ '\n';}
            result = result + '>'+ valText+'</'+tagName+'>';
        }
        else{result=result +'/>';}
        return result;
}

function timeStamp(){
    var d = new Date();
    return d.valueOf();
}
function macroExpand_GET(fnc){
    var macroGET = /(\W|^)GET (?:\s*)(\^?[\w\.\#\@\$\?-]+)/g;
    fnc = fnc.replace(macroGET, "$1this.getRelativeData('$2')");
    return fnc;
}
function macroExpand_SET(fnc){
    var macroSET = /(\W|^)SET (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/gm;
    fnc = fnc.replace(/;SET/g,'; SET').replace(macroSET, "$1this.setRelativeData('$2', $3)$4 ");
    return fnc;
}
function macroExpand_PUT(fnc){
    var macroSET = /(\W|^)PUT (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/gm;
    fnc = fnc.replace(/;PUT/g,'; PUT').replace(macroSET, "$1this.setRelativeData('$2', $3, null, false, false)$4 ");
    return fnc;
}
function macroExpand_FIRE(fnc){
    var macroSET = /(\W|^)FIRE (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/g;
    fnc = fnc.replace(/;FIRE/g,'; FIRE').replace(macroSET, "$1this.setRelativeData('$2', $3, null, true)$4 ");

    var macroSET = /(\W|^)FIRE (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)(;?)/g;
    fnc = fnc.replace(/;FIRE/g,'; FIRE').replace(macroSET, "$1this.setRelativeData('$2', true, null, true)$3 ");
    return fnc;
}
function macroExpand_FIRE_AFTER(fnc){
    var macroSET = /(\W|^)FIRE_AFTER (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)=(?:\s*)([^;\r\n]*)(;?)/g;
    fnc = fnc.replace(/;FIRE_AFTER/g,'; FIRE_AFTER').replace(macroSET, "$1this.setRelativeData('$2', $3, null, true,null,10)$4 ");

    var macroSET = /(\W|^)FIRE_AFTER (?:\s*)(\^?[\w\.\#\@\$\?-]+)(?:\s*)(;?)/g;
    fnc = fnc.replace(/;FIRE_AFTER/g,'; FIRE_AFTER').replace(macroSET, "$1this.setRelativeData('$2', true, null, true,null,10)$3 ");
    return fnc;
}
function eventToString(e){
    var result='';
    if (e.shiftKey){result+="Shift";}
    if (e.ctrlKey){result+="Ctrl";}
    if (e.altKey){result+="Alt";}
    if (e.metaKey){result+="Meta";}
     return result;
}
function serialize(_obj){
   // Other browsers must do it the hard way
   switch (typeof _obj)
   {
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
         if (_obj.constructor === Array || typeof _obj.callee !== 'undefined')
         {
            str = '[';
            var i, len = _obj.length;
            for (i = 0; i < len-1; i++) { str += serialize(_obj[i]) + ','; }
            str += serialize(_obj[i]) + ']';
         }
         else
         {
            str = '{';
            var key;
            for (key in _obj) { str += key + ':' + serialize(_obj[key]) + ','; }
            str = str.replace(/\,$/, '') + '}';
         }
         return str;
         break;

      default:
         return 'UNKNOWN';
         break;
   }
}

function funcCreate(fnc, pars, scope){
    if (fnc){
        var pars=pars || '';
        if (typeof(fnc)=='string'){
            if(scope && (fnc in scope)){
                return scope[fnc];
            }
            var fnc = stringStrip(fnc);
            fnc = argumentsReplace(fnc);
            fnc = macroExpand_GET(fnc);
            fnc = macroExpand_SET(fnc);
            fnc = macroExpand_PUT(fnc);
            fnc = macroExpand_FIRE_AFTER(fnc);
            fnc = macroExpand_FIRE(fnc);
            if (!stringStartsWith(fnc, 'function')){
                fnc = 'function('+pars+'){'+fnc+'}';
            }
            return genro.evaluate(fnc);
        }
        else{
            return fnc;
        }
    }
}

function funcApply(fnc, parsobj, scope){
    var argNames = [];
    var argValues = [];
    for (var attr in parsobj){
        argNames.push(attr);
        argValues.push(parsobj[attr]);
    }
    var func = funcCreate(fnc, argNames.join(','));
    var result = func.apply(scope, argValues);
    return result;
}

function localeParser(/*String*/value, /*Object?*/options){
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
    if(!match){ return null; } // null

    var widthList = ['abbr', 'wide', 'narrow'];
    //1972 is a leap year.  We want to avoid Feb 29 rolling over into Mar 1,
    //in the cases where the year is parsed after the month and day.
    var result = new Date(1972, 0);
    var expected = {};
    var amPm = "";
    dojo.forEach(match, function(v, i){
        
        if(!i){return;}
        var token=tokens[i-1];
        var l=token.length;
        //console.log('match :'+match[i]+'  -token:'+token+'  - result:'+result)
        switch(token.charAt(0)){
            case 'y':
            
                if(l != 2){
                    //interpret year literally, so '5' would be 5 A.D.
                    result.setFullYear(v);
                    expected.year = v;
            
                }else{
                    if(v<100){
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
                        
                    }else{
                        //we expected 2 digits and got more...
                        if(options.strict){
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
                if(l>2){
                    var months = bundle['months-format-' + widthList[l-3]].concat();
                    if(!options.strict){
                        //Tolerate abbreviating period in month part
                        //Case-insensitive comparison
                        v = v.replace(".","").toLowerCase();
                        months = dojo.map(months, function(s){ return s.replace(".","").toLowerCase(); } );
                    }
                    v = dojo.indexOf(months, v);
                    if(v == -1){
//                      console.debug("dojo.date.locale.parse: Could not parse month name: '" + v + "'.");
                        return null;
                    }
                }else{
                    v--;
                }
                result.setMonth(v);
                expected.month = v;
                //console.log('expected.month = v;'+v)
                break;
            case 'E':
            case 'e':
                var days = bundle['days-format-' + widthList[l-3]].concat();
                if(!options.strict){
                    //Case-insensitive comparison
                    v = v.toLowerCase();
                    days = dojo.map(days, "".toLowerCase);
                }
                v = dojo.indexOf(days, v);
                if(v == -1){
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
                if(!options.strict){
                    var period = /\./g;
                    v = v.replace(period,'').toLowerCase();
                    am = am.replace(period,'').toLowerCase();
                    pm = pm.replace(period,'').toLowerCase();
                }
                if(options.strict && v != am && v != pm){
//                  console.debug("dojo.date.locale.parse: Could not parse am/pm part.");
                    return null;
                }

                // we might not have seen the hours field yet, so store the state and apply hour change later
                amPm = (v == pm) ? 'p' : (v == am) ? 'a' : '';
                break;
            case 'K': //hour (1-24)
                if(v==24){v=0;}
                // fallthrough...
            case 'h': //hour (1-12)
            case 'H': //hour (0-23)
            case 'k': //hour (0-11)
                //TODO: strict bounds checking, padding
                if(v > 23){
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
    if(amPm === 'p' && hours < 12){
        result.setHours(hours + 12); //e.g., 3pm -> 15
    }else if(amPm === 'a' && hours == 12){
        result.setHours(0); //12am -> 0
    }

    //validate parse date fields versus input date fields
    if(expected.year && result.getFullYear() != expected.year){
//      console.debug("dojo.date.locale.parse: Parsed year: '" + result.getFullYear() + "' did not match input year: '" + expected.year + "'.");
        return null;
    }
    if(expected.month && result.getMonth() != expected.month){
        
//      console.debug("dojo.date.locale.parse: Parsed month: '" + result.getMonth() + "' did not match input month: '" + expected.month + "'.");
        return null;
    }
    // ----------------- Patch per 28 maggio  INIZIO ------------------------
       if( (expected.date == 28) && (expected.month==4) && (result.getDate()==27)){
            result.setDate(expected.date);
        }
    // ----------------- Patch per 28 maggio  FINE------------------------
    if(expected.date && result.getDate() != expected.date){
        return null;
    }

    //TODO: implement a getWeekday() method in order to test 
    //validity of input strings containing 'EEE' or 'EEEE'...
    return result; // Date
};