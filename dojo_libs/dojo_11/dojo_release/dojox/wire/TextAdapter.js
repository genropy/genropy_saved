/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.wire.TextAdapter"]){dojo._hasResource["dojox.wire.TextAdapter"]=true;dojo.provide("dojox.wire.TextAdapter");dojo.require("dojox.wire.CompositeWire");dojo.declare("dojox.wire.TextAdapter",dojox.wire.CompositeWire,{_wireClass:"dojox.wire.TextAdapter",constructor:function(_1){this._initializeChildren(this.segments);if(!this.delimiter){this.delimiter="";}},_getValue:function(_2){if(!_2||!this.segments){return _2;}var _3="";for(var i in this.segments){var _5=this.segments[i].getValue(_2);_3=this._addSegment(_3,_5);}return _3;},_setValue:function(_6,_7){throw new Error("Unsupported API: "+this._wireClass+"._setValue");},_addSegment:function(_8,_9){if(!_9){return _8;}else{if(!_8){return _9;}else{return _8+this.delimiter+_9;}}}});}