/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojo._base.array"]){dojo._hasResource["dojo._base.array"]=true;dojo.require("dojo._base.lang");dojo.provide("dojo._base.array");(function(){var _1=function(_2,_3,cb){return [dojo.isString(_2)?_2.split(""):_2,_3||dojo.global,dojo.isString(cb)?new Function("item","index","array",cb):cb];};dojo.mixin(dojo,{indexOf:function(_5,_6,_7,_8){var _9=1,_a=_5.length||0,i=0;if(_8){i=_a-1;_9=_a=-1;}if(_7!=undefined){i=_7;}if((_8&&i>_a)||i<_a){for(;i!=_a;i+=_9){if(_5[i]==_6){return i;}}}return -1;},lastIndexOf:function(_c,_d,_e){return dojo.indexOf(_c,_d,_e,true);},forEach:function(_f,_10,_11){if(!_f||!_f.length){return;}var _p=_1(_f,_11,_10);_f=_p[0];for(var i=0,l=_p[0].length;i<l;i++){_p[2].call(_p[1],_f[i],i,_f);}},_everyOrSome:function(_15,arr,_17,_18){var _p=_1(arr,_18,_17);arr=_p[0];for(var i=0,l=arr.length;i<l;i++){var _1c=!!_p[2].call(_p[1],arr[i],i,arr);if(_15^_1c){return _1c;}}return _15;},every:function(arr,_1e,_1f){return this._everyOrSome(true,arr,_1e,_1f);},some:function(arr,_21,_22){return this._everyOrSome(false,arr,_21,_22);},map:function(arr,_24,_25){var _p=_1(arr,_25,_24);arr=_p[0];var _27=(arguments[3]?(new arguments[3]()):[]);for(var i=0;i<arr.length;++i){_27.push(_p[2].call(_p[1],arr[i],i,arr));}return _27;},filter:function(arr,_2a,_2b){var _p=_1(arr,_2b,_2a);arr=_p[0];var _2d=[];for(var i=0;i<arr.length;i++){if(_p[2].call(_p[1],arr[i],i,arr)){_2d.push(arr[i]);}}return _2d;}});})();}