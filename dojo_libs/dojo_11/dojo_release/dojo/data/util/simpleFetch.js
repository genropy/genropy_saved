/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojo.data.util.simpleFetch"]){dojo._hasResource["dojo.data.util.simpleFetch"]=true;dojo.provide("dojo.data.util.simpleFetch");dojo.require("dojo.data.util.sorter");dojo.data.util.simpleFetch.fetch=function(_1){_1=_1||{};if(!_1.store){_1.store=this;}var _2=this;var _3=function(_4,_5){if(_5.onError){var _6=_5.scope||dojo.global;_5.onError.call(_6,_4,_5);}};var _7=function(_8,_9){var _a=_9.abort||null;var _b=false;var _c=_9.start?_9.start:0;var _d=_9.count?(_c+_9.count):_8.length;_9.abort=function(){_b=true;if(_a){_a.call(_9);}};var _e=_9.scope||dojo.global;if(!_9.store){_9.store=_2;}if(_9.onBegin){_9.onBegin.call(_e,_8.length,_9);}if(_9.sort){_8.sort(dojo.data.util.sorter.createSortFunction(_9.sort,_2));}if(_9.onItem){for(var i=_c;(i<_8.length)&&(i<_d);++i){var _10=_8[i];if(!_b){_9.onItem.call(_e,_10,_9);}}}if(_9.onComplete&&!_b){var _11=null;if(!_9.onItem){_11=_8.slice(_c,_d);}_9.onComplete.call(_e,_11,_9);}};this._fetchItems(_1,_7,_3);return _1;};}