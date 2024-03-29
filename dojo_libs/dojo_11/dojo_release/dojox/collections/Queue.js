/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.collections.Queue"]){dojo._hasResource["dojox.collections.Queue"]=true;dojo.provide("dojox.collections.Queue");dojo.require("dojox.collections._base");dojox.collections.Queue=function(_1){var q=[];if(_1){q=q.concat(_1);}this.count=q.length;this.clear=function(){q=[];this.count=q.length;};this.clone=function(){return new dojox.collections.Queue(q);};this.contains=function(o){for(var i=0;i<q.length;i++){if(q[i]==o){return true;}}return false;};this.copyTo=function(_5,i){_5.splice(i,0,q);};this.dequeue=function(){var r=q.shift();this.count=q.length;return r;};this.enqueue=function(o){this.count=q.push(o);};this.forEach=function(fn,_a){dojo.forEach(q,fn,_a);};this.getIterator=function(){return new dojox.collections.Iterator(q);};this.peek=function(){return q[0];};this.toArray=function(){return [].concat(q);};};}