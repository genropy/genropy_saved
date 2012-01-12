/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.dtl.html"]){dojo._hasResource["dojox.dtl.html"]=true;dojo.provide("dojox.dtl.html");dojo.require("dojox.dtl._base");dojo.require("dojox.dtl.Context");(function(){var dd=dojox.dtl;var _2=dd.text;var _3=dd.html={types:dojo.mixin({change:-11,attr:-12,custom:-13,elem:1,text:3},_2.types),_attributes:{},_re4:/^function anonymous\(\)\s*{\s*(.*)\s*}$/,getTemplate:function(_4){if(typeof this._commentable=="undefined"){this._commentable=false;var _5=document.createElement("div");_5.innerHTML="<!--Test comment handling, and long comments, using comments whenever possible.-->";if(_5.childNodes.length&&_5.childNodes[0].nodeType==8&&_5.childNodes[0].data=="comment"){this._commentable=true;}}if(!this._commentable){_4=_4.replace(/<!--({({|%).*?(%|})})-->/g,"$1");}var _6;var _7=[[true,"select","option"],[dojo.isSafari,"tr","th"],[dojo.isSafari,"tr","td"],[dojo.isSafari,"thead","tr","th"],[dojo.isSafari,"tbody","tr","td"]];for(var i=0,_9;_9=_7[i];i++){if(!_9[0]){continue;}if(_4.indexOf("<"+_9[1])!=-1){var _a=new RegExp("<"+_9[1]+"[\\s\\S]*?>([\\s\\S]+?)</"+_9[1]+">","ig");while(_6=_a.exec(_4)){var _b=false;var _c=dojox.string.tokenize(_6[1],new RegExp("(<"+_9[2]+"[\\s\\S]*?>[\\s\\S]*?</"+_9[2]+">)","ig"),function(_d){_b=true;return {data:_d};});if(_b){var _e=[];for(var j=0;j<_c.length;j++){if(dojo.isObject(_c[j])){_e.push(_c[j].data);}else{var _10=_9[_9.length-1];var k,_12="";for(k=2;k<_9.length-1;k++){_12+="<"+_9[k]+">";}_12+="<"+_10+" iscomment=\"true\">"+dojo.trim(_c[j])+"</"+_10+">";for(k=2;k<_9.length-1;k++){_12+="</"+_9[k]+">";}_e.push(_12);}}_4=_4.replace(_6[1],_e.join(""));}}}}var re=/\b([a-zA-Z]+)=['"]/g;while(_6=re.exec(_4)){this._attributes[_6[1].toLowerCase()]=true;}var _5=document.createElement("div");_5.innerHTML=_4;var _14={nodes:[]};while(_5.childNodes.length){_14.nodes.push(_5.removeChild(_5.childNodes[0]));}return _14;},tokenize:function(_15){var _16=[];for(var i=0,_18;_18=_15[i++];){if(_18.nodeType!=1){this.__tokenize(_18,_16);}else{this._tokenize(_18,_16);}}return _16;},_swallowed:[],_tokenize:function(_19,_1a){var _1b=this.types;var _1c=false;var _1d=this._swallowed;var i,j,tag,_21;if(!_1a.first){_1c=_1a.first=true;var _22=dd.register.getAttributeTags();for(i=0;tag=_22[i];i++){try{(tag[2])({swallowNode:function(){throw 1;}},"");}catch(e){_1d.push(tag);}}}for(i=0;tag=_1d[i];i++){var _23=_19.getAttribute(tag[0]);if(_23){var _1d=false;var _24=(tag[2])({swallowNode:function(){_1d=true;return _19;}},_23);if(_1d){if(_19.parentNode&&_19.parentNode.removeChild){_19.parentNode.removeChild(_19);}_1a.push([_1b.custom,_24]);return;}}}var _25=[];if(dojo.isIE&&_19.tagName=="SCRIPT"){_25.push({nodeType:3,data:_19.text});_19.text="";}else{for(i=0;_21=_19.childNodes[i];i++){_25.push(_21);}}_1a.push([_1b.elem,_19]);var _26=false;if(_25.length){_1a.push([_1b.change,_19]);_26=true;}for(var key in this._attributes){var _28="";if(key=="class"){_28=_19.className||_28;}else{if(key=="for"){_28=_19.htmlFor||_28;}else{if(key=="value"&&_19.value==_19.innerHTML){continue;}else{if(_19.getAttribute){_28=_19.getAttribute(key,2)||_28;if(key=="href"||key=="src"){if(dojo.isIE){var _29=location.href.lastIndexOf(location.hash);var _2a=location.href.substring(0,_29).split("/");_2a.pop();_2a=_2a.join("/")+"/";if(_28.indexOf(_2a)==0){_28=_28.replace(_2a,"");}_28=decodeURIComponent(_28);}if(_28.indexOf("{%")!=-1||_28.indexOf("{{")!=-1){_19.setAttribute(key,"");}}}}}}if(typeof _28=="function"){_28=_28.toString().replace(this._re4,"$1");}if(!_26){_1a.push([_1b.change,_19]);_26=true;}_1a.push([_1b.attr,_19,key,_28]);}for(i=0,_21;_21=_25[i];i++){if(_21.nodeType==1&&_21.getAttribute("iscomment")){_21.parentNode.removeChild(_21);_21={nodeType:8,data:_21.innerHTML};}this.__tokenize(_21,_1a);}if(!_1c&&_19.parentNode&&_19.parentNode.tagName){if(_26){_1a.push([_1b.change,_19,true]);}_1a.push([_1b.change,_19.parentNode]);_19.parentNode.removeChild(_19);}else{_1a.push([_1b.change,_19,true,true]);}},__tokenize:function(_2b,_2c){var _2d=this.types;var _2e=_2b.data;switch(_2b.nodeType){case 1:this._tokenize(_2b,_2c);return;case 3:if(_2e.match(/[^\s\n]/)&&(_2e.indexOf("{{")!=-1||_2e.indexOf("{%")!=-1)){var _2f=_2.tokenize(_2e);for(var j=0,_31;_31=_2f[j];j++){if(typeof _31=="string"){_2c.push([_2d.text,_31]);}else{_2c.push(_31);}}}else{_2c.push([_2b.nodeType,_2b]);}if(_2b.parentNode){_2b.parentNode.removeChild(_2b);}return;case 8:if(_2e.indexOf("{%")==0){var _31=dojo.trim(_2e.slice(2,-2));if(_31.substr(0,5)=="load "){var _32=dd.text.pySplit(dojo.trim(_31));for(var i=1,_34;_34=_32[i];i++){dojo["require"](_34);}}_2c.push([_2d.tag,_31]);}if(_2e.indexOf("{{")==0){_2c.push([_2d.varr,dojo.trim(_2e.slice(2,-2))]);}if(_2b.parentNode){_2b.parentNode.removeChild(_2b);}return;}}};dd.HtmlTemplate=dojo.extend(function(obj){if(!obj.nodes){var _36=dojo.byId(obj);if(_36){dojo.forEach(["class","src","href","name","value"],function(_37){_3._attributes[_37]=true;});obj={nodes:[_36]};}else{if(typeof obj=="object"){obj=_2.getTemplateString(obj);}obj=_3.getTemplate(obj);}}var _38=_3.tokenize(obj.nodes);if(dd.tests){this.tokens=_38.slice(0);}var _39=new dd._HtmlParser(_38);this.nodelist=_39.parse();},{_count:0,_re:/\bdojo:([a-zA-Z0-9_]+)\b/g,setClass:function(str){this.getRootNode().className=str;},getRootNode:function(){return this.rootNode;},getBuffer:function(){return new dd.HtmlBuffer();},render:function(_3b,_3c){_3c=_3c||this.getBuffer();this.rootNode=null;var _3d=this.nodelist.render(_3b||new dd.Context({}),_3c);this.rootNode=_3c.getRootNode();for(var i=0,_3f;_3f=_3c._cache[i];i++){if(_3f._cache){_3f._cache.length=0;}}return _3d;},unrender:function(_40,_41){return this.nodelist.unrender(_40,_41);}});dd.HtmlBuffer=dojo.extend(function(_42){this._parent=_42;this._cache=[];},{concat:function(_43){var _44=this._parent;if(_43.parentNode&&_43.parentNode.tagName&&_44&&!_44._dirty){return this;}if(_43.nodeType==1&&!this.rootNode){this.rootNode=_43||true;}if(!_44){if(_43.nodeType==3&&dojo.trim(_43.data)){throw new Error("Text should not exist outside of the root node in template");}return this;}if(this._closed&&(_43.nodeType!=3||dojo.trim(_43.data))){throw new Error("Content should not exist outside of the root node in template");}if(_44._dirty){if(_43._drawn&&_43.parentNode==_44){var _45=_44._cache;if(_45){for(var i=0,_47;_47=_45[i];i++){this.onAddNode(_47);_44.insertBefore(_47,_43);this.onAddNodeComplete(_47);}_45.length=0;}}_44._dirty=false;}if(!_44._cache){_44._cache=[];this._cache.push(_44);}_44._dirty=true;_44._cache.push(_43);return this;},remove:function(obj){if(typeof obj=="string"){if(this._parent){this._parent.removeAttribute(obj);}}else{if(obj.nodeType==1&&!this.getRootNode()&&!this._removed){this._removed=true;return this;}if(obj.parentNode){this.onRemoveNode();if(obj.parentNode){obj.parentNode.removeChild(obj);}}}return this;},setAttribute:function(key,_4a){if(key=="class"){this._parent.className=_4a;}else{if(key=="for"){this._parent.htmlFor=_4a;}else{if(this._parent.setAttribute){this._parent.setAttribute(key,_4a);}}}return this;},addEvent:function(_4b,_4c,fn,_4e){if(!_4b.getThis()){throw new Error("You must use Context.setObject(instance)");}this.onAddEvent(this.getParent(),_4c,fn);var _4f=fn;if(dojo.isArray(_4e)){_4f=function(e){this[fn].apply(this,[e].concat(_4e));};}return dojo.connect(this.getParent(),_4c,_4b.getThis(),_4f);},setParent:function(_51,up,_53){if(!this._parent){this._parent=this._first=_51;}if(up&&_53&&_51===this._first){this._closed=true;}if(up){var _54=this._parent;var _55="";var ie=dojo.isIE&&_54.tagName=="SCRIPT";if(ie){_54.text="";}if(_54._dirty){var _57=_54._cache;for(var i=0,_59;_59=_57[i];i++){if(_59!==_54){this.onAddNode(_59);if(ie){_55+=_59.data;}else{_54.appendChild(_59);}this.onAddNodeComplete(_59);}}_57.length=0;_54._dirty=false;}if(ie){_54.text=_55;}}this.onSetParent(_51,up);this._parent=_51;return this;},getParent:function(){return this._parent;},getRootNode:function(){return this.rootNode;},onSetParent:function(_5a,up){},onAddNode:function(_5c){},onAddNodeComplete:function(_5d){},onRemoveNode:function(_5e){},onClone:function(_5f,to){},onAddEvent:function(_61,_62,_63){}});dd._HtmlNode=dojo.extend(function(_64){this.contents=_64;},{render:function(_65,_66){this._rendered=true;return _66.concat(this.contents);},unrender:function(_67,_68){if(!this._rendered){return _68;}this._rendered=false;return _68.remove(this.contents);},clone:function(_69){return new this.constructor(this.contents);}});dd._HtmlNodeList=dojo.extend(function(_6a){this.contents=_6a||[];},{push:function(_6b){this.contents.push(_6b);},unshift:function(_6c){this.contents.unshift(_6c);},render:function(_6d,_6e,_6f){_6e=_6e||dd.HtmlTemplate.prototype.getBuffer();if(_6f){var _70=_6e.getParent();}for(var i=0;i<this.contents.length;i++){_6e=this.contents[i].render(_6d,_6e);if(!_6e){throw new Error("Template node render functions must return their buffer");}}if(_70){_6e.setParent(_70);}return _6e;},dummyRender:function(_72,_73,_74){var div=document.createElement("div");var _76=_73.getParent();var old=_76._clone;_76._clone=div;var _78=this.clone(_73,div);if(old){_76._clone=old;}else{_76._clone=null;}_73=dd.HtmlTemplate.prototype.getBuffer();_78.unshift(new dd.ChangeNode(div));_78.push(new dd.ChangeNode(div,true));_78.render(_72,_73);if(_74){return _73.getRootNode();}var _79=div.innerHTML;return (dojo.isIE)?_79.replace(/\s*_(dirty|clone)="[^"]*"/g,""):_79;},unrender:function(_7a,_7b){for(var i=0;i<this.contents.length;i++){_7b=this.contents[i].unrender(_7a,_7b);if(!_7b){throw new Error("Template node render functions must return their buffer");}}return _7b;},clone:function(_7d){var _7e=_7d.getParent();var _7f=this.contents;var _80=new dd._HtmlNodeList();var _81=[];for(var i=0;i<_7f.length;i++){var _83=_7f[i].clone(_7d);if(_83 instanceof dd.ChangeNode||_83 instanceof dd._HtmlNode){var _84=_83.contents._clone;if(_84){_83.contents=_84;}else{if(_7e!=_83.contents&&_83 instanceof dd._HtmlNode){var _85=_83.contents;_83.contents=_83.contents.cloneNode(false);_7d.onClone(_85,_83.contents);_81.push(_85);_85._clone=_83.contents;}}}_80.push(_83);}for(var i=0,_83;_83=_81[i];i++){_83._clone=null;}return _80;}});dd._HtmlVarNode=dojo.extend(function(str){this.contents=new dd._Filter(str);this._lists={};},{render:function(_87,_88){this._rendered=true;var str=this.contents.resolve(_87);if(str&&str.render&&str.getRootNode){var _8a=this._curr=str.getRootNode();var _8b=this._lists;var _8c=_8b[_8a];if(!_8c){_8c=_8b[_8a]=new dd._HtmlNodeList();_8c.push(new dd.ChangeNode(_88.getParent()));_8c.push(new dd._HtmlNode(_8a));_8c.push(str);_8c.push(new dd.ChangeNode(_88.getParent()));}return _8c.render(_87,_88);}else{if(!this._txt){this._txt=document.createTextNode(str);}this._txt.data=str;return _88.concat(this._txt);}},unrender:function(_8d,_8e){if(!this._rendered){return _8e;}this._rendered=false;if(this._curr){return this._lists[this._curr].unrender(_8d,_8e);}else{if(this._txt){return _8e.remove(this._txt);}}return _8e;},clone:function(){return new this.constructor(this.contents.getExpression());}});dd.ChangeNode=dojo.extend(function(_8f,up,_91){this.contents=_8f;this.up=up;this.root=_91;},{render:function(_92,_93){return _93.setParent(this.contents,this.up,this.root);},unrender:function(_94,_95){if(!this.contents.parentNode){return _95;}if(!_95.getParent()){return _95;}return _95.setParent(this.contents);},clone:function(){return new this.constructor(this.contents,this.up,this.root);}});dd.AttributeNode=dojo.extend(function(key,_97,_98){this.key=key;this.value=_97;this.nodelist=_98||(new dd.Template(_97)).nodelist;this.contents="";},{render:function(_99,_9a){var key=this.key;var _9c=this.nodelist.dummyRender(_99);if(this._rendered){if(_9c!=this.contents){this.contents=_9c;return _9a.setAttribute(key,_9c);}}else{this._rendered=true;this.contents=_9c;return _9a.setAttribute(key,_9c);}return _9a;},unrender:function(_9d,_9e){return _9e.remove(this.key);},clone:function(_9f){return new this.constructor(this.key,this.value,this.nodelist.clone(_9f));}});dd._HtmlTextNode=dojo.extend(function(str){this.contents=document.createTextNode(str);},{set:function(_a1){this.contents.data=_a1;},render:function(_a2,_a3){return _a3.concat(this.contents);},unrender:function(_a4,_a5){return _a5.remove(this.contents);},clone:function(){return new this.constructor(this.contents.data);}});dd._HtmlParser=dojo.extend(function(_a6){this.contents=_a6;},{i:0,parse:function(_a7){var _a8=_3.types;var _a9={};var _aa=this.contents;if(!_a7){_a7=[];}for(var i=0;i<_a7.length;i++){_a9[_a7[i]]=true;}var _ac=new dd._HtmlNodeList();while(this.i<_aa.length){var _ad=_aa[this.i++];var _ae=_ad[0];var _af=_ad[1];if(_ae==_a8.custom){_ac.push(_af);}else{if(_ae==_a8.change){var _b0=new dd.ChangeNode(_af,_ad[2],_ad[3]);_af[_b0.attr]=_b0;_ac.push(_b0);}else{if(_ae==_a8.attr){var fn=_2.getTag("attr:"+_ad[2],true);if(fn&&_ad[3]){_ac.push(fn(null,_ad[2]+" "+_ad[3]));}else{if(dojo.isString(_ad[3])&&(_ad[3].indexOf("{%")!=-1||_ad[3].indexOf("{{")!=-1)){_ac.push(new dd.AttributeNode(_ad[2],_ad[3]));}}}else{if(_ae==_a8.elem){var fn=_2.getTag("node:"+_af.tagName.toLowerCase(),true);if(fn){_ac.push(fn(null,_af,_af.tagName.toLowerCase()));}_ac.push(new dd._HtmlNode(_af));}else{if(_ae==_a8.varr){_ac.push(new dd._HtmlVarNode(_af));}else{if(_ae==_a8.text){_ac.push(new dd._HtmlTextNode(_af.data||_af));}else{if(_ae==_a8.tag){if(_a9[_af]){--this.i;return _ac;}var cmd=_af.split(/\s+/g);if(cmd.length){cmd=cmd[0];var fn=_2.getTag(cmd);if(typeof fn!="function"){throw new Error("Function not found for "+cmd);}var tpl=fn(this,_af);if(tpl){_ac.push(tpl);}}}}}}}}}}if(_a7.length){throw new Error("Could not find closing tag(s): "+_a7.toString());}return _ac;},next:function(){var _b4=this.contents[this.i++];return {type:_b4[0],text:_b4[1]};},skipPast:function(_b5){return dd.Parser.prototype.skipPast.call(this,_b5);},getVarNodeConstructor:function(){return dd._HtmlVarNode;},getTextNodeConstructor:function(){return dd._HtmlTextNode;},getTemplate:function(loc){return new dd.HtmlTemplate(_3.getTemplate(loc));}});})();}