/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.widget.Wizard"]){
dojo._hasResource["dojox.widget.Wizard"]=true;
dojo.provide("dojox.widget.Wizard");
dojo.require("dijit.layout.StackContainer");
dojo.require("dijit.layout.ContentPane");
dojo.require("dijit.form.Button");
dojo.require("dojo.i18n");
dojo.requireLocalization("dijit","common",null,"ar,ROOT,cs,da,de,el,es,fi,fr,he,hu,it,ja,ko,nb,nl,pl,pt,pt-pt,ru,sv,tr,zh,zh-tw");
dojo.requireLocalization("dojox.widget","Wizard",null,"ar,cs,da,de,el,es,fi,fr,he,hu,it,ja,ko,nb,nl,pl,pt,pt-pt,ru,sv,tr,ROOT,zh,zh-tw");
dojo.declare("dojox.widget.WizardContainer",[dijit.layout.StackContainer,dijit._Templated],{widgetsInTemplate:true,templateString:"<div class=\"dojoxWizard\" dojoAttachPoint=\"wizardNode\">\n    <div class=\"dojoxWizardContainer\" dojoAttachPoint=\"containerNode\"></div>\n    <div class=\"dojoxWizardButtons\" dojoAttachPoint=\"wizardNav\">\n        <button dojoType=\"dijit.form.Button\" dojoAttachPoint=\"previousButton\">${previousButtonLabel}</button>\n        <button dojoType=\"dijit.form.Button\" dojoAttachPoint=\"nextButton\">${nextButtonLabel}</button>\n        <button dojoType=\"dijit.form.Button\" dojoAttachPoint=\"doneButton\" style=\"display:none\">${doneButtonLabel}</button>\n        <button dojoType=\"dijit.form.Button\" dojoAttachPoint=\"cancelButton\">${cancelButtonLabel}</button>\n    </div>\n</div>\n",nextButtonLabel:"",previousButtonLabel:"",cancelButtonLabel:"",doneButtonLabel:"",cancelFunction:"",hideDisabled:false,postMixInProperties:function(){
this.inherited(arguments);
var _1=dojo.mixin({cancel:dojo.i18n.getLocalization("dijit","common",this.lang).buttonCancel},dojo.i18n.getLocalization("dojox.widget","Wizard",this.lang));
for(prop in _1){
if(!this[prop+"ButtonLabel"]){
this[prop+"ButtonLabel"]=_1[prop];
}
}
},startup:function(){
this.inherited(arguments);
this.connect(this.nextButton,"onClick","_forward");
this.connect(this.previousButton,"onClick","back");
if(this.cancelFunction){
this.cancelFunction=dojo.getObject(this.cancelFunction);
this.connect(this.cancelButton,"onClick",this.cancelFunction);
}else{
this.cancelButton.domNode.style.display="none";
}
this.connect(this.doneButton,"onClick","done");
this._subscription=dojo.subscribe(this.id+"-selectChild",dojo.hitch(this,"_checkButtons"));
this._checkButtons();
},_checkButtons:function(){
var sw=this.selectedChildWidget;
var _3=sw.isLastChild;
this.nextButton.setAttribute("disabled",_3);
this._setButtonClass(this.nextButton);
if(sw.doneFunction){
this.doneButton.domNode.style.display="";
if(_3){
this.nextButton.domNode.style.display="none";
}
}else{
this.doneButton.domNode.style.display="none";
}
this.previousButton.setAttribute("disabled",!this.selectedChildWidget.canGoBack);
this._setButtonClass(this.previousButton);
},_setButtonClass:function(_4){
_4.domNode.style.display=(this.hideDisabled&&_4.disabled)?"none":"";
},_forward:function(){
if(this.selectedChildWidget._checkPass()){
this.forward();
}
},done:function(){
this.selectedChildWidget.done();
},destroy:function(){
dojo.unsubscribe(this._subscription);
this.inherited(arguments);
}});
dojo.declare("dojox.widget.WizardPane",dijit.layout.ContentPane,{canGoBack:true,passFunction:"",doneFunction:"",postMixInProperties:function(){
if(this.passFunction){
this.passFunction=dojo.getObject(this.passFunction);
}
if(this.doneFunction){
this.doneFunction=dojo.getObject(this.doneFunction);
}
this.inherited(arguments);
},startup:function(){
this.inherited(arguments);
if(this.isFirstChild){
this.canGoBack=false;
}
},_checkPass:function(){
var r=true;
if(this.passFunction&&dojo.isFunction(this.passFunction)){
var _6=this.passFunction();
switch(typeof _6){
case "boolean":
r=_6;
break;
case "string":
alert(_6);
r=false;
break;
}
}
return r;
},done:function(){
if(this.doneFunction&&dojo.isFunction(this.doneFunction)){
this.doneFunction();
}
}});
}
