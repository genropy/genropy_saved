/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dijit.form._Spinner"]){
dojo._hasResource["dijit.form._Spinner"]=true;
dojo.provide("dijit.form._Spinner");
dojo.require("dijit.form.ValidationTextBox");
dojo.declare("dijit.form._Spinner",dijit.form.RangeBoundTextBox,{defaultTimeout:500,timeoutChangeRate:0.9,smallDelta:1,largeDelta:10,templateString:"<div class=\"dijit dijitReset dijitInlineTable dijitLeft\"\n\tid=\"widget_${id}\"\n\tdojoAttachEvent=\"onmouseenter:_onMouse,onmouseleave:_onMouse,onmousedown:_onMouse\" waiRole=\"presentation\"\n\t><div class=\"dijitInputLayoutContainer\"\n\t\t><div class=\"dijitReset dijitSpinnerButtonContainer\"\n\t\t\t>&nbsp;<div class=\"dijitReset dijitLeft dijitButtonNode dijitArrowButton dijitUpArrowButton\"\n\t\t\t\tdojoAttachPoint=\"upArrowNode\"\n\t\t\t\tdojoAttachEvent=\"onmouseenter:_onMouse,onmouseleave:_onMouse\"\n\t\t\t\tstateModifier=\"UpArrow\"\n\t\t\t\t><div class=\"dijitArrowButtonInner\">&thinsp;</div\n\t\t\t\t><div class=\"dijitArrowButtonChar\">&#9650;</div\n\t\t\t></div\n\t\t\t><div class=\"dijitReset dijitLeft dijitButtonNode dijitArrowButton dijitDownArrowButton\"\n\t\t\t\tdojoAttachPoint=\"downArrowNode\"\n\t\t\t\tdojoAttachEvent=\"onmouseenter:_onMouse,onmouseleave:_onMouse\"\n\t\t\t\tstateModifier=\"DownArrow\"\n\t\t\t\t><div class=\"dijitArrowButtonInner\">&thinsp;</div\n\t\t\t\t><div class=\"dijitArrowButtonChar\">&#9660;</div\n\t\t\t></div\n\t\t></div\n\t\t><div class=\"dijitReset dijitValidationIcon\"><br></div\n\t\t><div class=\"dijitReset dijitValidationIconText\">&Chi;</div\n\t\t><div class=\"dijitReset dijitInputField\"\n\t\t\t><input class='dijitReset' dojoAttachPoint=\"textbox,focusNode\" type=\"${type}\" dojoAttachEvent=\"onfocus:_update,onkeyup:_onkeyup,onkeypress:_onKeyPress\"\n\t\t\t\twaiRole=\"spinbutton\" autocomplete=\"off\" name=\"${name}\"\n\t\t/></div\n\t></div\n></div>\n",baseClass:"dijitSpinner",adjust:function(_1,_2){
return _1;
},_arrowState:function(_3,_4){
this._active=_4;
this.stateModifier=_3.getAttribute("stateModifier")||"";
this._setStateClass();
},_arrowPressed:function(_5,_6){
if(this.disabled||this.readOnly){
return;
}
this._arrowState(_5,true);
this.setValue(this.adjust(this.getValue(),_6*this.smallDelta),false);
dijit.selectInputText(this.textbox,this.textbox.value.length);
},_arrowReleased:function(_7){
this._wheelTimer=null;
if(this.disabled||this.readOnly){
return;
}
this._arrowState(_7,false);
},_typematicCallback:function(_8,_9,_a){
if(_9==this.textbox){
_9=(_a.keyCode==dojo.keys.UP_ARROW)?this.upArrowNode:this.downArrowNode;
}
if(_8==-1){
this._arrowReleased(_9);
}else{
this._arrowPressed(_9,(_9==this.upArrowNode)?1:-1);
}
},_wheelTimer:null,_mouseWheeled:function(_b){
dojo.stopEvent(_b);
var _c=0;
if(typeof _b.wheelDelta=="number"){
_c=_b.wheelDelta;
}else{
if(typeof _b.detail=="number"){
_c=-_b.detail;
}
}
var _d,_e;
if(_c>0){
_d=this.upArrowNode;
_e=+1;
}else{
if(_c<0){
_d=this.downArrowNode;
_e=-1;
}else{
return;
}
}
this._arrowPressed(_d,_e);
if(this._wheelTimer!=null){
clearTimeout(this._wheelTimer);
}
var _f=this;
this._wheelTimer=setTimeout(function(){
_f._arrowReleased(_d);
},50);
},postCreate:function(){
this.inherited("postCreate",arguments);
this.connect(this.textbox,dojo.isIE?"onmousewheel":"DOMMouseScroll","_mouseWheeled");
this._connects.push(dijit.typematic.addListener(this.upArrowNode,this.textbox,{keyCode:dojo.keys.UP_ARROW,ctrlKey:false,altKey:false,shiftKey:false},this,"_typematicCallback",this.timeoutChangeRate,this.defaultTimeout));
this._connects.push(dijit.typematic.addListener(this.downArrowNode,this.textbox,{keyCode:dojo.keys.DOWN_ARROW,ctrlKey:false,altKey:false,shiftKey:false},this,"_typematicCallback",this.timeoutChangeRate,this.defaultTimeout));
if(dojo.isIE){
var _10=this;
this.connect(this.domNode,"onresize",function(){
setTimeout(dojo.hitch(_10,function(){
this.upArrowNode.style.behavior="";
this.downArrowNode.style.behavior="";
this._setStateClass();
}),0);
});
}
}});
}
