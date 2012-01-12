/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.charting.plot2d.Grid"]){dojo._hasResource["dojox.charting.plot2d.Grid"]=true;dojo.provide("dojox.charting.plot2d.Grid");dojo.require("dojox.charting.Element");dojo.require("dojox.charting.plot2d.common");dojo.require("dojox.lang.functional");(function(){var du=dojox.lang.utils;dojo.declare("dojox.charting.plot2d.Grid",dojox.charting.Element,{defaultParams:{hAxis:"x",vAxis:"y",hMajorLines:true,hMinorLines:false,vMajorLines:true,vMinorLines:false,hStripes:"none",vStripes:"none"},optionalParams:{},constructor:function(_2,_3){this.opt=dojo.clone(this.defaultParams);du.updateWithObject(this.opt,_3);this.hAxis=this.opt.hAxis;this.vAxis=this.opt.vAxis;},clear:function(){this._hAxis=null;this._vAxis=null;this.dirty=true;return this;},setAxis:function(_4){if(_4){this[_4.vertical?"_vAxis":"_hAxis"]=_4;}return this;},addSeries:function(_5){return this;},calculateAxes:function(_6){return this;},getRequiredColors:function(){return 0;},render:function(_7,_8){if(!this.dirty){return this;}this.cleanGroup();var s=this.group,ta=this.chart.theme.axis,_b=this._vAxis.getScaler();if(this.opt.hMinorLines&&_b.minor.tick){for(var i=0;i<_b.minor.count;++i){var y=_7.height-_8.b-_b.scale*(_b.minor.start-_b.bounds.lower+i*_b.minor.tick);s.createLine({x1:_8.l,y1:y,x2:_7.width-_8.r,y2:y}).setStroke(ta.minorTick);}}if(this.opt.hMajorLines&&_b.major.tick){for(var i=0;i<_b.major.count;++i){var y=_7.height-_8.b-_b.scale*(_b.major.start-_b.bounds.lower+i*_b.major.tick);s.createLine({x1:_8.l,y1:y,x2:_7.width-_8.r,y2:y}).setStroke(ta.majorTick);}}_b=this._hAxis.getScaler();if(this.opt.vMinorLines&&_b.minor.tick){for(var i=0;i<_b.minor.count;++i){var x=_8.l+_b.scale*(_b.minor.start-_b.bounds.lower+i*_b.minor.tick);s.createLine({x1:x,y1:_8.t,x2:x,y2:_7.height-_8.b}).setStroke(ta.minorTick);}}if(this.opt.vMajorLines&&_b.major.tick){for(var i=0;i<_b.major.count;++i){var x=_8.l+_b.scale*(_b.major.start-_b.bounds.lower+i*_b.major.tick);s.createLine({x1:x,y1:_8.t,x2:x,y2:_7.height-_8.b}).setStroke(ta.majorTick);}}this.dirty=false;return this;}});})();}