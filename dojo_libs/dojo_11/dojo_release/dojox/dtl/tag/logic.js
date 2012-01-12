/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.dtl.tag.logic"]){dojo._hasResource["dojox.dtl.tag.logic"]=true;dojo.provide("dojox.dtl.tag.logic");dojo.require("dojox.dtl._base");(function(){var dd=dojox.dtl;var _2=dd.text;var _3=dd.tag.logic;_3.IfNode=dojo.extend(function(_4,_5,_6,_7){this.bools=_4;this.trues=_5;this.falses=_6;this.type=_7;},{render:function(_8,_9){var i,_b,_c,_d,_e;if(this.type=="or"){for(i=0;_b=this.bools[i];i++){_c=_b[0];_d=_b[1];_e=_d.resolve(_8);if((_e&&!_c)||(_c&&!_e)){if(this.falses){_9=this.falses.unrender(_8,_9);}return (this.trues)?this.trues.render(_8,_9,this):_9;}}if(this.trues){_9=this.trues.unrender(_8,_9);}return (this.falses)?this.falses.render(_8,_9,this):_9;}else{for(i=0;_b=this.bools[i];i++){_c=_b[0];_d=_b[1];_e=_d.resolve(_8);if(_e==_c){if(this.trues){_9=this.trues.unrender(_8,_9);}return (this.falses)?this.falses.render(_8,_9,this):_9;}}if(this.falses){_9=this.falses.unrender(_8,_9);}return (this.trues)?this.trues.render(_8,_9,this):_9;}return _9;},unrender:function(_f,_10){_10=(this.trues)?this.trues.unrender(_f,_10):_10;_10=(this.falses)?this.falses.unrender(_f,_10):_10;return _10;},clone:function(_11){var _12=(this.trues)?this.trues.clone(_11):null;var _13=(this.falses)?this.falses.clone(_11):null;return new this.constructor(this.bools,_12,_13,this.type);}});_3.IfEqualNode=dojo.extend(function(_14,_15,_16,_17,_18){this.var1=new dd._Filter(_14);this.var2=new dd._Filter(_15);this.trues=_16;this.falses=_17;this.negate=_18;},{render:function(_19,_1a){var _1b=this.var1.resolve(_19);var _1c=this.var2.resolve(_19);if((this.negate&&_1b!=_1c)||(!this.negate&&_1b==_1c)){if(this.falses){_1a=this.falses.unrender(_19,_1a);}return (this.trues)?this.trues.render(_19,_1a,this):_1a;}if(this.trues){_1a=this.trues.unrender(_19,_1a);}return (this.falses)?this.falses.render(_19,_1a,this):_1a;},unrender:function(_1d,_1e){return _3.IfNode.prototype.unrender.call(this,_1d,_1e);},clone:function(_1f){return new this.constructor(this.var1.getExpression(),this.var2.getExpression(),this.trues.clone(_1f),this.falses.clone(_1f),this.negate);}});_3.ForNode=dojo.extend(function(_20,_21,_22,_23){this.assign=_20;this.loop=new dd._Filter(_21);this.reversed=_22;this.nodelist=_23;this.pool=[];},{render:function(_24,_25){var i,j,k;var _29=false;var _2a=this.assign;for(k=0;k<_2a.length;k++){if(typeof _24[_2a[k]]!="undefined"){_29=true;_24.push();break;}}var _2b=this.loop.resolve(_24)||[];for(i=_2b.length;i<this.pool.length;i++){this.pool[i].unrender(_24,_25);}if(this.reversed){_2b=_2b.slice(0).reverse();}var _2c=dojo.isObject(_2b)&&!dojo.isArrayLike(_2b);var _2d=[];if(_2c){for(var key in _2b){_2d.push(_2b[key]);}}else{_2d=_2b;}var _2f=_24.forloop={parentloop:_24.forloop||{}};var j=0;for(i=0;i<_2d.length;i++){var _30=_2d[i];_2f.counter0=j;_2f.counter=j+1;_2f.revcounter0=_2d.length-j-1;_2f.revcounter=_2d.length-j;_2f.first=!j;_2f.last=(j==_2d.length-1);if(_2a.length>1&&dojo.isArrayLike(_30)){if(!_29){_29=true;_24.push();}var _31={};for(k=0;k<_30.length&&k<_2a.length;k++){_31[_2a[k]]=_30[k];}_24.update(_31);}else{_24[_2a[0]]=_30;}if(j+1>this.pool.length){this.pool.push(this.nodelist.clone(_25));}_25=this.pool[j].render(_24,_25,this);++j;}delete _24.forloop;for(k=0;k<_2a.length;k++){delete _24[_2a[k]];}if(_29){_24.pop();}return _25;},unrender:function(_32,_33){for(var i=0,_35;_35=this.pool[i];i++){_33=_35.unrender(_32,_33);}return _33;},clone:function(_36){return new this.constructor(this.assign,this.loop.getExpression(),this.reversed,this.nodelist.clone(_36));}});dojo.mixin(_3,{if_:function(_37,_38){var i,_3a,_3b,_3c=[],_3d=_2.pySplit(_38);_3d.shift();_38=_3d.join(" ");_3d=_38.split(" and ");if(_3d.length==1){_3b="or";_3d=_38.split(" or ");}else{_3b="and";for(i=0;i<_3d.length;i++){if(_3d[i].indexOf(" or ")!=-1){throw new Error("'if' tags can't mix 'and' and 'or'");}}}for(i=0;_3a=_3d[i];i++){var not=false;if(_3a.indexOf("not ")==0){_3a=_3a.slice(4);not=true;}_3c.push([not,new dd._Filter(_3a)]);}var _3f=_37.parse(["else","endif"]);var _40=false;var _41=_37.next();if(_41.text=="else"){_40=_37.parse(["endif"]);_37.next();}return new _3.IfNode(_3c,_3f,_40,_3b);},_ifequal:function(_42,_43,_44){var _45=_2.pySplit(_43);if(_45.length!=3){throw new Error(_45[0]+" takes two arguments");}var end="end"+_45[0];var _47=_42.parse(["else",end]);var _48=false;var _49=_42.next();if(_49.text=="else"){_48=_42.parse([end]);_42.next();}return new _3.IfEqualNode(_45[1],_45[2],_47,_48,_44);},ifequal:function(_4a,_4b){return _3._ifequal(_4a,_4b);},ifnotequal:function(_4c,_4d){return _3._ifequal(_4c,_4d,true);},for_:function(_4e,_4f){var _50=_2.pySplit(_4f);if(_50.length<4){throw new Error("'for' statements should have at least four words: "+_4f);}var _51=_50[_50.length-1]=="reversed";var _52=(_51)?-3:-2;if(_50[_50.length+_52]!="in"){throw new Error("'for' tag received an invalid argument: "+_4f);}var _53=_50.slice(1,_52).join(" ").split(/ *, */);for(var i=0;i<_53.length;i++){if(!_53[i]||_53[i].indexOf(" ")!=-1){throw new Error("'for' tag received an invalid argument: "+_4f);}}var _55=_4e.parse(["endfor"]);_4e.next();return new _3.ForNode(_53,_50[_50.length+_52+1],_51,_55);}});})();}