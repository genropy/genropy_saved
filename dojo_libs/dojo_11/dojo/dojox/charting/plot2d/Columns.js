/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.charting.plot2d.Columns"]){
dojo._hasResource["dojox.charting.plot2d.Columns"]=true;
dojo.provide("dojox.charting.plot2d.Columns");
dojo.require("dojox.charting.plot2d.common");
dojo.require("dojox.charting.plot2d.Base");
dojo.require("dojox.lang.utils");
dojo.require("dojox.lang.functional");
dojo.require("dojox.lang.functional.reversed");
(function(){
var df=dojox.lang.functional,du=dojox.lang.utils,dc=dojox.charting.plot2d.common,_4=df.lambda("item.purgeGroup()");
dojo.declare("dojox.charting.plot2d.Columns",dojox.charting.plot2d.Base,{defaultParams:{hAxis:"x",vAxis:"y",gap:0,shadows:null},optionalParams:{},constructor:function(_5,_6){
this.opt=dojo.clone(this.defaultParams);
du.updateWithObject(this.opt,_6);
this.series=[];
this.hAxis=this.opt.hAxis;
this.vAxis=this.opt.vAxis;
},calculateAxes:function(_7){
var _8=dc.collectSimpleStats(this.series);
_8.hmin-=0.5;
_8.hmax+=0.5;
this._calc(_7,_8);
return this;
},render:function(_9,_a){
if(this.dirty){
dojo.forEach(this.series,_4);
this.cleanGroup();
var s=this.group;
df.forEachRev(this.series,function(_c){
_c.cleanGroup(s);
});
}
var t=this.chart.theme,_e,_f,_10,f,gap=this.opt.gap<this._hScaler.scale/3?this.opt.gap:0;
for(var i=this.series.length-1;i>=0;--i){
var run=this.series[i];
if(!this.dirty&&!run.dirty){
continue;
}
run.cleanGroup();
var s=run.group;
if(!run.fill||!run.stroke){
_e=run.dyn.color=new dojo.Color(t.next("color"));
}
_f=run.stroke?run.stroke:dc.augmentStroke(t.series.stroke,_e);
_10=run.fill?run.fill:dc.augmentFill(t.series.fill,_e);
var _15=Math.max(0,this._vScaler.bounds.lower),_16=_a.l+this._hScaler.scale*(0.5-this._hScaler.bounds.lower)+gap,_17=_9.height-_a.b-this._vScaler.scale*(_15-this._vScaler.bounds.lower);
for(var j=0;j<run.data.length;++j){
var v=run.data[j],_1a=this._hScaler.scale-2*gap,_1b=this._vScaler.scale*(v-_15),h=Math.abs(_1b);
if(_1a>=1&&h>=1){
var _1d={x:_16+this._hScaler.scale*j,y:_17-(_1b<0?0:_1b),width:_1a,height:h},_1e=s.createRect(_1d).setFill(_10).setStroke(_f);
run.dyn.fill=_1e.getFill();
run.dyn.stroke=_1e.getStroke();
}
}
run.dirty=false;
}
this.dirty=false;
return this;
}});
})();
}
