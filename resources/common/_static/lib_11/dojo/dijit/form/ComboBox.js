/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dijit.form.ComboBox"]){
dojo._hasResource["dijit.form.ComboBox"]=true;
dojo.provide("dijit.form.ComboBox");
dojo.require("dijit.form.ValidationTextBox");
dojo.requireLocalization("dijit.form","ComboBox",null,"ar,ROOT,cs,da,de,el,es,fi,fr,he,hu,it,ja,ko,nb,nl,pl,pt,pt-pt,ru,sv,tr,zh,zh-tw");
dojo.declare("dijit.form.ComboBoxMixin",null,{item:null,pageSize:Infinity,store:null,query:{},autoComplete:true,searchDelay:100,searchAttr:"name",queryExpr:"${0}*",ignoreCase:true,hasDownArrow:true,templateString:"<div class=\"dijit dijitReset dijitInlineTable dijitLeft\"\n\tid=\"widget_${id}\"\n\tdojoAttachEvent=\"onmouseenter:_onMouse,onmouseleave:_onMouse,onmousedown:_onMouse\" dojoAttachPoint=\"comboNode\" waiRole=\"combobox\" tabIndex=\"-1\"\n\t><div style=\"overflow:hidden;\"\n\t\t><div class='dijitReset dijitRight dijitButtonNode dijitArrowButton dijitDownArrowButton'\n\t\t\tdojoAttachPoint=\"downArrowNode\" waiRole=\"presentation\"\n\t\t\tdojoAttachEvent=\"onmousedown:_onArrowMouseDown,onmouseup:_onMouse,onmouseenter:_onMouse,onmouseleave:_onMouse\"\n\t\t\t><div class=\"dijitArrowButtonInner\">&thinsp;</div\n\t\t\t><div class=\"dijitArrowButtonChar\">&#9660;</div\n\t\t></div\n\t\t><div class=\"dijitReset dijitValidationIcon\"><br></div\n\t\t><div class=\"dijitReset dijitValidationIconText\">&Chi;</div\n\t\t><div class=\"dijitReset dijitInputField\"\n\t\t\t><input type=\"text\" autocomplete=\"off\" name=\"${name}\" class='dijitReset'\n\t\t\tdojoAttachEvent=\"onkeypress:_onKeyPress, onfocus:_update, compositionend,onkeyup\"\n\t\t\tdojoAttachPoint=\"textbox,focusNode\" waiRole=\"textbox\" waiState=\"haspopup-true,autocomplete-list\"\n\t\t/></div\n\t></div\n></div>\n",baseClass:"dijitComboBox",_getCaretPos:function(_1){
var _2=0;
if(typeof (_1.selectionStart)=="number"){
_2=_1.selectionStart;
}else{
if(dojo.isIE){
var tr=dojo.doc.selection.createRange().duplicate();
var _4=_1.createTextRange();
tr.move("character",0);
_4.move("character",0);
try{
_4.setEndPoint("EndToEnd",tr);
_2=String(_4.text).replace(/\r/g,"").length;
}
catch(e){
}
}
}
return _2;
},_setCaretPos:function(_5,_6){
_6=parseInt(_6);
dijit.selectInputText(_5,_6,_6);
},_setAttribute:function(_7,_8){
if(_7=="disabled"){
dijit.setWaiState(this.comboNode,"disabled",_8);
}
},_onKeyPress:function(_9){
if(_9.altKey||(_9.ctrlKey&&_9.charCode!=118)){
return;
}
var _a=false;
var pw=this._popupWidget;
var dk=dojo.keys;
if(this._isShowingNow){
pw.handleKey(_9);
}
switch(_9.keyCode){
case dk.PAGE_DOWN:
case dk.DOWN_ARROW:
if(!this._isShowingNow||this._prev_key_esc){
this._arrowPressed();
_a=true;
}else{
this._announceOption(pw.getHighlightedOption());
}
dojo.stopEvent(_9);
this._prev_key_backspace=false;
this._prev_key_esc=false;
break;
case dk.PAGE_UP:
case dk.UP_ARROW:
if(this._isShowingNow){
this._announceOption(pw.getHighlightedOption());
}
dojo.stopEvent(_9);
this._prev_key_backspace=false;
this._prev_key_esc=false;
break;
case dk.ENTER:
var _d;
if(this._isShowingNow&&(_d=pw.getHighlightedOption())){
if(_d==pw.nextButton){
this._nextSearch(1);
dojo.stopEvent(_9);
break;
}else{
if(_d==pw.previousButton){
this._nextSearch(-1);
dojo.stopEvent(_9);
break;
}
}
}else{
this.setDisplayedValue(this.getDisplayedValue());
}
_9.preventDefault();
case dk.TAB:
var _e=this.getDisplayedValue();
if(pw&&(_e==pw._messages["previousMessage"]||_e==pw._messages["nextMessage"])){
break;
}
if(this._isShowingNow){
this._prev_key_backspace=false;
this._prev_key_esc=false;
if(pw.getHighlightedOption()){
pw.setValue({target:pw.getHighlightedOption()},true);
}
this._hideResultList();
}
break;
case dk.SPACE:
this._prev_key_backspace=false;
this._prev_key_esc=false;
if(this._isShowingNow&&pw.getHighlightedOption()){
dojo.stopEvent(_9);
this._selectOption();
this._hideResultList();
}else{
_a=true;
}
break;
case dk.ESCAPE:
this._prev_key_backspace=false;
this._prev_key_esc=true;
if(this._isShowingNow){
dojo.stopEvent(_9);
this._hideResultList();
}
this.inherited(arguments);
break;
case dk.DELETE:
case dk.BACKSPACE:
this._prev_key_esc=false;
this._prev_key_backspace=true;
_a=true;
break;
case dk.RIGHT_ARROW:
case dk.LEFT_ARROW:
this._prev_key_backspace=false;
this._prev_key_esc=false;
break;
default:
this._prev_key_backspace=false;
this._prev_key_esc=false;
if(dojo.isIE||_9.charCode!=0){
_a=true;
}
}
if(this.searchTimer){
clearTimeout(this.searchTimer);
}
if(_a){
setTimeout(dojo.hitch(this,"_startSearchFromInput"),1);
}
},_autoCompleteText:function(_f){
var fn=this.focusNode;
dijit.selectInputText(fn,fn.value.length);
var _11=this.ignoreCase?"toLowerCase":"substr";
if(_f[_11](0).indexOf(this.focusNode.value[_11](0))==0){
var _12=this._getCaretPos(fn);
if((_12+1)>fn.value.length){
fn.value=_f;
dijit.selectInputText(fn,_12);
}
}else{
fn.value=_f;
dijit.selectInputText(fn);
}
},_openResultList:function(_13,_14){
if(this.disabled||this.readOnly||(_14.query[this.searchAttr]!=this._lastQuery)){
return;
}
this._popupWidget.clearResultList();
if(!_13.length){
this._hideResultList();
return;
}
var _15=new String(this.store.getValue(_13[0],this.searchAttr));
if(_15&&this.autoComplete&&!this._prev_key_backspace&&(_14.query[this.searchAttr]!="*")){
this._autoCompleteText(_15);
}
this._popupWidget.createOptions(_13,_14,dojo.hitch(this,"_getMenuLabelFromItem"));
this._showResultList();
if(_14.direction){
if(1==_14.direction){
this._popupWidget.highlightFirstOption();
}else{
if(-1==_14.direction){
this._popupWidget.highlightLastOption();
}
}
this._announceOption(this._popupWidget.getHighlightedOption());
}
},_showResultList:function(){
this._hideResultList();
var _16=this._popupWidget.getItems(),_17=Math.min(_16.length,this.maxListLength);
this._arrowPressed();
this.displayMessage("");
with(this._popupWidget.domNode.style){
width="";
height="";
}
var _18=this.open();
var _19=dojo.marginBox(this._popupWidget.domNode);
this._popupWidget.domNode.style.overflow=((_18.h==_19.h)&&(_18.w==_19.w))?"hidden":"auto";
var _1a=_18.w;
if(_18.h<this._popupWidget.domNode.scrollHeight){
_1a+=16;
}
dojo.marginBox(this._popupWidget.domNode,{h:_18.h,w:Math.max(_1a,this.domNode.offsetWidth)});
dijit.setWaiState(this.comboNode,"expanded","true");
},_hideResultList:function(){
if(this._isShowingNow){
dijit.popup.close(this._popupWidget);
this._arrowIdle();
this._isShowingNow=false;
dijit.setWaiState(this.comboNode,"expanded","false");
dijit.removeWaiState(this.focusNode,"activedescendant");
}
},_setBlurValue:function(){
var _1b=this.getDisplayedValue();
var pw=this._popupWidget;
if(pw&&(_1b==pw._messages["previousMessage"]||_1b==pw._messages["nextMessage"])){
this.setValue(this._lastValueReported,true);
}else{
this.setDisplayedValue(_1b);
}
},_onBlur:function(){
this._hideResultList();
this._arrowIdle();
this.inherited(arguments);
},_announceOption:function(_1d){
if(_1d==null){
return;
}
var _1e;
if(_1d==this._popupWidget.nextButton||_1d==this._popupWidget.previousButton){
_1e=_1d.innerHTML;
}else{
_1e=this.store.getValue(_1d.item,this.searchAttr);
}
this.focusNode.value=this.focusNode.value.substring(0,this._getCaretPos(this.focusNode));
dijit.setWaiState(this.focusNode,"activedescendant",dojo.attr(_1d,"id"));
this._autoCompleteText(_1e);
},_selectOption:function(evt){
var tgt=null;
if(!evt){
evt={target:this._popupWidget.getHighlightedOption()};
}
if(!evt.target){
this.setDisplayedValue(this.getDisplayedValue());
return;
}else{
tgt=evt.target;
}
if(!evt.noHide){
this._hideResultList();
this._setCaretPos(this.focusNode,this.store.getValue(tgt.item,this.searchAttr).length);
}
this._doSelect(tgt);
},_doSelect:function(tgt){
this.item=tgt.item;
this.setValue(this.store.getValue(tgt.item,this.searchAttr),true);
},_onArrowMouseDown:function(evt){
if(this.disabled||this.readOnly){
return;
}
dojo.stopEvent(evt);
this.focus();
if(this._isShowingNow){
this._hideResultList();
}else{
this._startSearch("");
}
},_startSearchFromInput:function(){
this._startSearch(this.focusNode.value);
},_getQueryString:function(_23){
return dojo.string.substitute(this.queryExpr,[_23]);
},_startSearch:function(key){
if(!this._popupWidget){
var _25=this.id+"_popup";
this._popupWidget=new dijit.form._ComboBoxMenu({onChange:dojo.hitch(this,this._selectOption),id:_25});
dijit.removeWaiState(this.focusNode,"activedescendant");
dijit.setWaiState(this.textbox,"owns",_25);
}
this.item=null;
var _26=dojo.clone(this.query);
this._lastQuery=_26[this.searchAttr]=this._getQueryString(key);
this.searchTimer=setTimeout(dojo.hitch(this,function(_27,_28){
var _29=this.store.fetch({queryOptions:{ignoreCase:this.ignoreCase,deep:true},query:_27,onComplete:dojo.hitch(this,"_openResultList"),onError:function(_2a){
console.error("dijit.form.ComboBox: "+_2a);
dojo.hitch(_28,"_hideResultList")();
},start:0,count:this.pageSize});
var _2b=function(_2c,_2d){
_2c.start+=_2c.count*_2d;
_2c.direction=_2d;
this.store.fetch(_2c);
};
this._nextSearch=this._popupWidget.onPage=dojo.hitch(this,_2b,_29);
},_26,this),this.searchDelay);
},_getValueField:function(){
return this.searchAttr;
},_arrowPressed:function(){
if(!this.disabled&&!this.readOnly&&this.hasDownArrow){
dojo.addClass(this.downArrowNode,"dijitArrowButtonActive");
}
},_arrowIdle:function(){
if(!this.disabled&&!this.readOnly&&this.hasDownArrow){
dojo.removeClass(this.downArrowNode,"dojoArrowButtonPushed");
}
},compositionend:function(evt){
this.onkeypress({charCode:-1});
},constructor:function(){
this.query={};
},postMixInProperties:function(){
if(!this.hasDownArrow){
this.baseClass="dijitTextBox";
}
if(!this.store){
var _2f=this.srcNodeRef;
this.store=new dijit.form._ComboBoxDataStore(_2f);
if(!this.value||((typeof _2f.selectedIndex=="number")&&_2f.selectedIndex.toString()===this.value)){
var _30=this.store.fetchSelectedItem();
if(_30){
this.value=this.store.getValue(_30,this._getValueField());
}
}
}
},_postCreate:function(){
var _31=dojo.query("label[for=\""+this.id+"\"]");
if(_31.length){
_31[0].id=(this.id+"_label");
var cn=this.comboNode;
dijit.setWaiState(cn,"labelledby",_31[0].id);
dijit.setWaiState(cn,"disabled",this.disabled);
}
},uninitialize:function(){
if(this._popupWidget){
this._hideResultList();
this._popupWidget.destroy();
}
},_getMenuLabelFromItem:function(_33){
return {html:false,label:this.store.getValue(_33,this.searchAttr)};
},open:function(){
this._isShowingNow=true;
return dijit.popup.open({popup:this._popupWidget,around:this.domNode,parent:this});
},reset:function(){
this.item=null;
this.inherited(arguments);
}});
dojo.declare("dijit.form._ComboBoxMenu",[dijit._Widget,dijit._Templated],{templateString:"<ul class='dijitMenu' dojoAttachEvent='onmousedown:_onMouseDown,onmouseup:_onMouseUp,onmouseover:_onMouseOver,onmouseout:_onMouseOut' tabIndex='-1' style='overflow:\"auto\";'>"+"<li class='dijitMenuItem dijitMenuPreviousButton' dojoAttachPoint='previousButton'></li>"+"<li class='dijitMenuItem dijitMenuNextButton' dojoAttachPoint='nextButton'></li>"+"</ul>",_messages:null,postMixInProperties:function(){
this._messages=dojo.i18n.getLocalization("dijit.form","ComboBox",this.lang);
this.inherited("postMixInProperties",arguments);
},setValue:function(_34){
this.value=_34;
this.onChange(_34);
},onChange:function(_35){
},onPage:function(_36){
},postCreate:function(){
this.previousButton.innerHTML=this._messages["previousMessage"];
this.nextButton.innerHTML=this._messages["nextMessage"];
this.inherited("postCreate",arguments);
},onClose:function(){
this._blurOptionNode();
},_createOption:function(_37,_38){
var _39=_38(_37);
var _3a=dojo.doc.createElement("li");
dijit.setWaiRole(_3a,"option");
if(_39.html){
_3a.innerHTML=_39.label;
}else{
_3a.appendChild(dojo.doc.createTextNode(_39.label));
}
if(_3a.innerHTML==""){
_3a.innerHTML="&nbsp;";
}
_3a.item=_37;
return _3a;
},createOptions:function(_3b,_3c,_3d){
this.previousButton.style.display=(_3c.start==0)?"none":"";
dojo.attr(this.previousButton,"id",this.id+"_prev");
dojo.forEach(_3b,function(_3e,i){
var _40=this._createOption(_3e,_3d);
_40.className="dijitMenuItem";
dojo.attr(_40,"id",this.id+i);
this.domNode.insertBefore(_40,this.nextButton);
},this);
this.nextButton.style.display=(_3c.count==_3b.length)?"":"none";
dojo.attr(this.nextButton,"id",this.id+"_next");
},clearResultList:function(){
while(this.domNode.childNodes.length>2){
this.domNode.removeChild(this.domNode.childNodes[this.domNode.childNodes.length-2]);
}
},getItems:function(){
return this.domNode.childNodes;
},getListLength:function(){
return this.domNode.childNodes.length-2;
},_onMouseDown:function(evt){
dojo.stopEvent(evt);
},_onMouseUp:function(evt){
if(evt.target===this.domNode){
return;
}else{
if(evt.target==this.previousButton){
this.onPage(-1);
}else{
if(evt.target==this.nextButton){
this.onPage(1);
}else{
var tgt=evt.target;
while(!tgt.item){
tgt=tgt.parentNode;
}
this.setValue({target:tgt},true);
}
}
}
},_onMouseOver:function(evt){
if(evt.target===this.domNode){
return;
}
var tgt=evt.target;
if(!(tgt==this.previousButton||tgt==this.nextButton)){
while(!tgt.item){
tgt=tgt.parentNode;
}
}
this._focusOptionNode(tgt);
},_onMouseOut:function(evt){
if(evt.target===this.domNode){
return;
}
this._blurOptionNode();
},_focusOptionNode:function(_47){
if(this._highlighted_option!=_47){
this._blurOptionNode();
this._highlighted_option=_47;
dojo.addClass(this._highlighted_option,"dijitMenuItemHover");
}
},_blurOptionNode:function(){
if(this._highlighted_option){
dojo.removeClass(this._highlighted_option,"dijitMenuItemHover");
this._highlighted_option=null;
}
},_highlightNextOption:function(){
var fc=this.domNode.firstChild;
if(!this.getHighlightedOption()){
this._focusOptionNode(fc.style.display=="none"?fc.nextSibling:fc);
}else{
var ns=this._highlighted_option.nextSibling;
if(ns&&ns.style.display!="none"){
this._focusOptionNode(ns);
}
}
dijit.scrollIntoView(this._highlighted_option);
},highlightFirstOption:function(){
this._focusOptionNode(this.domNode.firstChild.nextSibling);
dijit.scrollIntoView(this._highlighted_option);
},highlightLastOption:function(){
this._focusOptionNode(this.domNode.lastChild.previousSibling);
dijit.scrollIntoView(this._highlighted_option);
},_highlightPrevOption:function(){
var lc=this.domNode.lastChild;
if(!this.getHighlightedOption()){
this._focusOptionNode(lc.style.display=="none"?lc.previousSibling:lc);
}else{
var ps=this._highlighted_option.previousSibling;
if(ps&&ps.style.display!="none"){
this._focusOptionNode(ps);
}
}
dijit.scrollIntoView(this._highlighted_option);
},_page:function(up){
var _4d=0;
var _4e=this.domNode.scrollTop;
var _4f=dojo.style(this.domNode,"height");
if(!this.getHighlightedOption()){
this._highlightNextOption();
}
while(_4d<_4f){
if(up){
if(!this.getHighlightedOption().previousSibling||this._highlighted_option.previousSibling.style.display=="none"){
break;
}
this._highlightPrevOption();
}else{
if(!this.getHighlightedOption().nextSibling||this._highlighted_option.nextSibling.style.display=="none"){
break;
}
this._highlightNextOption();
}
var _50=this.domNode.scrollTop;
_4d+=(_50-_4e)*(up?-1:1);
_4e=_50;
}
},pageUp:function(){
this._page(true);
},pageDown:function(){
this._page(false);
},getHighlightedOption:function(){
var ho=this._highlighted_option;
return (ho&&ho.parentNode)?ho:null;
},handleKey:function(evt){
switch(evt.keyCode){
case dojo.keys.DOWN_ARROW:
this._highlightNextOption();
break;
case dojo.keys.PAGE_DOWN:
this.pageDown();
break;
case dojo.keys.UP_ARROW:
this._highlightPrevOption();
break;
case dojo.keys.PAGE_UP:
this.pageUp();
break;
}
}});
dojo.declare("dijit.form.ComboBox",[dijit.form.ValidationTextBox,dijit.form.ComboBoxMixin],{postMixInProperties:function(){
dijit.form.ComboBoxMixin.prototype.postMixInProperties.apply(this,arguments);
dijit.form.ValidationTextBox.prototype.postMixInProperties.apply(this,arguments);
},postCreate:function(){
dijit.form.ComboBoxMixin.prototype._postCreate.apply(this,arguments);
dijit.form.ValidationTextBox.prototype.postCreate.apply(this,arguments);
},setAttribute:function(_53,_54){
dijit.form.ValidationTextBox.prototype.setAttribute.apply(this,arguments);
dijit.form.ComboBoxMixin.prototype._setAttribute.apply(this,arguments);
}});
dojo.declare("dijit.form._ComboBoxDataStore",null,{constructor:function(_55){
this.root=_55;
},getValue:function(_56,_57,_58){
return (_57=="value")?_56.value:(_56.innerText||_56.textContent||"");
},isItemLoaded:function(_59){
return true;
},fetch:function(_5a){
var _5b="^"+_5a.query.name.replace(/([\\\|\(\)\[\{\^\$\+\?\.\<\>])/g,"\\$1").replace("*",".*")+"$",_5c=new RegExp(_5b,_5a.queryOptions.ignoreCase?"i":""),_5d=dojo.query("> option",this.root).filter(function(_5e){
return (_5e.innerText||_5e.textContent||"").match(_5c);
});
var _5f=_5a.start||0,end=("count" in _5a&&_5a.count!=Infinity)?(_5f+_5a.count):_5d.length;
_5a.onComplete(_5d.slice(_5f,end),_5a);
return _5a;
},close:function(_61){
return;
},getLabel:function(_62){
return _62.innerHTML;
},getIdentity:function(_63){
return dojo.attr(_63,"value");
},fetchItemByIdentity:function(_64){
var _65=dojo.query("option[value='"+_64.identity+"']",this.root)[0];
_64.onItem(_65);
},fetchSelectedItem:function(){
var _66=this.root,si=_66.selectedIndex;
return dojo.query("> option:nth-child("+(si!=-1?si+1:1)+")",_66)[0];
}});
}
