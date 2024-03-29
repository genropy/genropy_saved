/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.gfx.Mover"]){dojo._hasResource["dojox.gfx.Mover"]=true;dojo.provide("dojox.gfx.Mover");dojo.declare("dojox.gfx.Mover",null,{constructor:function(_1,e,_3){this.shape=_1;this.lastX=e.clientX;this.lastY=e.clientY;var h=this.host=_3,d=document,_6=dojo.connect(d,"onmousemove",this,"onFirstMove");this.events=[dojo.connect(d,"onmousemove",this,"onMouseMove"),dojo.connect(d,"onmouseup",this,"destroy"),dojo.connect(d,"ondragstart",dojo,"stopEvent"),dojo.connect(d,"onselectstart",dojo,"stopEvent"),_6];if(h&&h.onMoveStart){h.onMoveStart(this);}},onMouseMove:function(e){var x=e.clientX;var y=e.clientY;this.host.onMove(this,{dx:x-this.lastX,dy:y-this.lastY});this.lastX=x;this.lastY=y;dojo.stopEvent(e);},onFirstMove:function(){this.host.onFirstMove(this);dojo.disconnect(this.events.pop());},destroy:function(){dojo.forEach(this.events,dojo.disconnect);var h=this.host;if(h&&h.onMoveStop){h.onMoveStop(this);}this.events=this.shape=null;}});}