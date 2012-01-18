/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dijit._editor.plugins.FontChoice"]){dojo._hasResource["dijit._editor.plugins.FontChoice"]=true;dojo.provide("dijit._editor.plugins.FontChoice");dojo.require("dijit._editor._Plugin");dojo.require("dijit.form.FilteringSelect");dojo.require("dojo.data.ItemFileReadStore");dojo.require("dojo.i18n");dojo.requireLocalization("dijit._editor","FontChoice",null,"ar,cs,da,de,el,es,fi,ROOT,fr,he,hu,it,ja,ko,nb,nl,pl,pt,pt-pt,ru,sv,tr,zh,zh-tw");dojo.declare("dijit._editor.plugins.FontChoice",dijit._editor._Plugin,{_uniqueId:0,buttonClass:dijit.form.FilteringSelect,_initButton:function(){var _1=this.command;var _2=this.custom||{fontName:this.generic?["serif","sans-serif","monospace","cursive","fantasy"]:["Arial","Times New Roman","Comic Sans MS","Courier New"],fontSize:[1,2,3,4,5,6,7],formatBlock:["p","h1","h2","h3","pre"]}[_1];var _3=dojo.i18n.getLocalization("dijit._editor","FontChoice");var _4=dojo.map(_2,function(_5){var _6=_3[_5]||_5;var _7=_6;switch(_1){case "fontName":_7="<div style='font-family: "+_5+"'>"+_6+"</div>";break;case "fontSize":_7="<font size="+_5+"'>"+_6+"</font>";break;case "formatBlock":_7="<"+_5+">"+_6+"</"+_5+">";}return {label:_7,name:_6,value:_5};});this.inherited(arguments,[{labelType:"html",labelAttr:"label",searchAttr:"name",store:new dojo.data.ItemFileReadStore({data:{identifier:"value",items:_4}})}]);this.button.isValid=function(){return true;};this.button.setValue=function(_8,_9){var _a=this;var _b=function(_c,_d){if(_c){if(_a.store.isItemLoaded(_c)){_a._callbackSetLabel([_c],undefined,_d);}else{_a.store.loadItem({item:_c,onItem:function(_e,_f){_a._callbackSetLabel(_e,_f,_d);}});}}else{_a._isvalid=false;_a.validate(false);_a._setValue("","",false);}};this.store.fetchItemByIdentity({identity:_8,onItem:function(_10){_b(_10,_9);}});};this.button.setValue("");this.connect(this.button,"onChange",function(_11){if(this.updating){return;}if(dojo.isIE){this.editor.focus();}else{dijit.focus(this._focusHandle);}if(this.command=="fontName"&&_11.indexOf(" ")!=-1){_11="'"+_11+"'";}this.editor.execCommand(this.editor._normalizeCommand(this.command),_11);});},updateState:function(){this.inherited(arguments);var _e=this.editor;var _c=this.command;if(!_e||!_e.isLoaded||!_c.length){return;}if(this.button){var _14;try{_14=_e.queryCommandValue(_c)||"";}catch(e){_14="";}var _15=dojo.isString(_14)&&_14.match(/'([^']*)'/);if(_15){_14=_15[1];}if(this.generic&&_c=="fontName"){var map={"Arial":"sans-serif","Helvetica":"sans-serif","Myriad":"sans-serif","Times":"serif","Times New Roman":"serif","Comic Sans MS":"cursive","Apple Chancery":"cursive","Courier":"monospace","Courier New":"monospace","Papyrus":"fantasy"};_14=map[_14]||_14;}else{if(_c=="fontSize"&&_14.indexOf&&_14.indexOf("px")!=-1){var _17=parseInt(_14);_14={10:1,13:2,16:3,18:4,24:5,32:6,48:7}[_17]||_14;}}this.updating=true;this.button.setValue(_14);delete this.updating;}this._focusHandle=dijit.getFocus(this.editor.iframe);},setToolbar:function(){this.inherited(arguments);var _18=this.button;if(!_18.id){_18.id=dijit._scopeName+"EditorButton-"+this.command+(this._uniqueId++);}var _19=dojo.doc.createElement("label");dojo.addClass(_19,"dijit dijitReset dijitLeft dijitInline");_19.setAttribute("for",_18.id);var _1a=dojo.i18n.getLocalization("dijit._editor","FontChoice");_19.appendChild(dojo.doc.createTextNode(_1a[this.command]));dojo.place(_19,this.button.domNode,"before");}});dojo.subscribe(dijit._scopeName+".Editor.getPlugin",null,function(o){if(o.plugin){return;}switch(o.args.name){case "fontName":case "fontSize":case "formatBlock":o.plugin=new dijit._editor.plugins.FontChoice({command:o.args.name});}});}