/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.help.console"]){dojo._hasResource["dojox.help.console"]=true;dojo.provide("dojox.help.console");dojo.require("dojox.help._base");dojo.mixin(dojox.help,{_plainText:function(_1){return _1.replace(/(<[^>]*>|&[^;]{2,6};)/g,"");},_displayLocated:function(_2){var _3={};dojo.forEach(_2,function(_4){_3[_4[0]]=(+dojo.isFF)?{toString:function(){return "Click to view";},item:_4[1]}:_4[1];});console.dir(_3);},_displayHelp:function(_5,_6){if(_5){var _7="Help for: "+_6.name;console.log(_7);var _8="";for(var i=0;i<_7.length;i++){_8+="=";}console.log(_8);}else{if(!_6){console.log("No documentation for this object");}else{var _a=false;for(var _b in _6){var _c=_6[_b];if(_b=="returns"&&_6.type!="Function"&&_6.type!="Constructor"){continue;}if(_c&&(!dojo.isArray(_c)||_c.length)){_a=true;console.info(_b.toUpperCase());_c=dojo.isString(_c)?dojox.help._plainText(_c):_c;if(_b=="returns"){var _d=dojo.map(_c.types||[],"return item.title;").join("|");if(_c.summary){if(_d){_d+=": ";}_d+=dojox.help._plainText(_c.summary);}console.log(_d||"Uknown");}else{if(_b=="parameters"){for(var j=0,_f;_f=_c[j];j++){var _10=dojo.map(_f.types,"return item.title").join("|");console.log((_10)?(_f.name+": "+_10):_f.name);var _11="";if(_f.optional){_11+="Optional. ";}if(_f.repating){_11+="Repeating. ";}_11+=dojox.help._plainText(_f.summary);if(_11){_11="  - "+_11;for(var k=0;k<_f.name.length;k++){_11=" "+_11;}console.log(_11);}}}else{console.log(_c);}}}}if(!_a){console.log("No documentation for this object");}}}}});dojox.help.init();}