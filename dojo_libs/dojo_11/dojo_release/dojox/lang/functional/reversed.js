/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.lang.functional.reversed"]){dojo._hasResource["dojox.lang.functional.reversed"]=true;dojo.provide("dojox.lang.functional.reversed");dojo.require("dojox.lang.functional.lambda");(function(){var d=dojo,df=dojox.lang.functional;d.mixin(df,{filterRev:function(a,f,o){if(typeof a=="string"){a=a.split("");}o=o||d.global;f=df.lambda(f);var t=[],v;for(var i=a.length-1;i>=0;--i){v=a[i];if(f.call(o,v,i,a)){t.push(v);}}return t;},forEachRev:function(a,f,o){if(typeof a=="string"){a=a.split("");}o=o||d.global;f=df.lambda(f);for(var i=a.length-1;i>=0;f.call(o,a[i],i,a),--i){}},mapRev:function(a,f,o){if(typeof a=="string"){a=a.split("");}o=o||d.global;f=df.lambda(f);var n=a.length,t=new Array(n);for(var i=n-1,j=0;i>=0;t[j++]=f.call(o,a[i],i,a),--i){}return t;},everyRev:function(a,f,o){if(typeof a=="string"){a=a.split("");}o=o||d.global;f=df.lambda(f);for(var i=a.length-1;i>=0;--i){if(!f.call(o,a[i],i,a)){return false;}}return true;},someRev:function(a,f,o){if(typeof a=="string"){a=a.split("");}o=o||d.global;f=df.lambda(f);for(var i=a.length-1;i>=0;--i){if(f.call(o,a[i],i,a)){return true;}}return false;}});})();}