/*
*-*- coding: UTF-8 -*-
*--------------------------------------------------------------------------
* package       : Genro js - see LICENSE for details
* module genro_dom : Genro client utility functions
* Copyright (c) : 2004 - 2007 Softwell sas - Milano 
* Written by    : Giovanni Porcari, Francesco Cavazzana
*                 Saverio Porcari, Francesco Porcari
*--------------------------------------------------------------------------
*This library is free software; you can redistribute it and/or
*modify it under the terms of the GNU Lesser General Public
*License as published by the Free Software Foundation; either
*version 2.1 of the License, or (at your option) any later version.

*This library is distributed in the hope that it will be useful,
*but WITHOUT ANY WARRANTY; without even the implied warranty of
*MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
*Lesser General Public License for more details.

*You should have received a copy of the GNU Lesser General Public
*License along with this library; if not, write to the Free Software
*Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
*/
 
//######################## genro  #########################

dojo.declare("gnr.GnrDomHandler",null,{
    
    constructor: function(application){
        this.application=application;
        this.styleAttrNames=['height', 'width','top','left', 'right', 'bottom',
                              'visibility', 'overflow', 'float', 'clear', 'display',
                              'z_index', 'border','position','padding','margin',
                              'color','white_space','vertical_align','background'];
    },
    isStyleAttr:function(name){
        for (var i=0;i<this.styleAttrNames.length;i++){
            if ((name==this.styleAttrNames[i]) || (name.indexOf(this.styleAttrNames[i]+'_')==0)){
                return true;
            }
        }
    },
    
    iFramePrint: function(iframe){
        var contentWindow = genro.dom.iframeContentWindow(iframe);
        setTimeout(function(){contentWindow.print();},1);
    },
    
    iframeContentWindow: function(/* HTMLIFrameElement */iframe_el) {
		//	summary
		//	returns the window reference of the passed iframe
		var win = dijit.getDocumentWindow(genro.dom.iframeContentDocument(iframe_el)) ||
			// Moz. TODO: is this available when defaultView isn't?
			genro.dom.iframeContentDocument(iframe_el)['__parent__'] ||
			(iframe_el.name && document.frames[iframe_el.name]) || null;
		return win;	//	Window
	},

	iframeContentDocument: function(/* HTMLIFrameElement */iframe_el){
		//	summary
		//	returns a reference to the document object inside iframe_el
		var doc = iframe_el.contentDocument // W3
			|| (iframe_el.contentWindow && iframe_el.contentWindow.document) // IE
			|| (iframe_el.name && document.frames[iframe_el.name] && document.frames[iframe_el.name].document)
			|| null;
		return doc;	//	HTMLDocument
	},
	
    addStyleSheet:function(cssText,cssTitle){
        var style = document.createElement("style");
        style.setAttribute("type", "text/css");
        style.setAttribute('title',cssTitle);
        if(style.styleSheet){// IE
            var setFunc = function(){
                style.styleSheet.cssText = cssStr;
            };
            if(style.styleSheet.disabled){
                setTimeout(setFunc, 10);
            }else{
                setFunc();
            }
        }else{ // w3c
            var cssText = document.createTextNode(cssText);
            style.appendChild(cssText);
        }
        document.getElementsByTagName("head")[0].appendChild(style);
        style.disabled = false; //to control why appending child style change disable attr
    },
    loadCss: function(url,cssTitle) {var e = document.createElement("link");
                                                           e.href = url;
                                                           e.type = "text/css";
                                                           e.rel = "stylesheet";
                                                           e.media = "screen";
                                                           document.getElementsByTagName("head")[0].appendChild(e);
    },
    loadJs: function(url) {var e = document.createElement("script");
                                                           e.src = url;
                                                           e.type = "text/javascript";
                                                           document.getElementsByTagName("head")[0].appendChild(e);
    },
    
    addClass: function(where,cls){
        if(typeof(cls)=='string'){
            var domnode=this.getDomNode(where);
            if (!domnode) return;
            var classes=cls.split(' ');
            for (var i=0;i<classes.length;i++){
                if (domnode.addClass){
                    domnode.addClass(classes[i]);
                }else{
                    dojo.addClass(domnode, classes[i]);
                }
                
            }
        }  
    },
    style:function(where,attr,value){
        var domnode=this.getDomNode(where);
        if (domnode){
            if (typeof (attr) == 'string'){
                dojo.style(domnode,genro.dom.dojoStyleAttrName(attr),value);
            }else{
                var kw={};
                for (k in attr){
                    kw[genro.dom.dojoStyleAttrName(k)]=attr[k];
                }
                dojo.style(domnode,kw);
            }
            
        }
    },
    dojoStyleAttrName:function(attr){
        if(attr.indexOf('_')){
            attr=attr.split('_');
        }else if(attr.indexOf('-')){
            attr=attr.split('-');
        }else{
            return attr;
        }
        var r=attr.splice(0,1);
        dojo.forEach(attr,function(n){
            r=r+stringCapitalize(n);
        });
        return r;
    },
    getDomNode: function(where){
        if (typeof (where) == 'string'){
            var where=genro.domById(where);
        }
        if (!where){
            return;
        }
        if (where instanceof gnr.GnrDomSourceNode){
            where = where.getDomNode();
        }else if (where instanceof gnr.GnrDomSource){
            where = where.getParentNode().getDomNode();
        }
        return where;
    },
    removeClass: function(where, cls){
        if(typeof(cls)=='string'){
            var domnode=this.getDomNode(where);
            if (!domnode) return;
            var classes = cls.split(' ');
            for (var i=0;i<classes.length;i++){
                if (domnode.removeClass){
                    domnode.removeClass(classes[i]);
                }else{
                    dojo.removeClass(domnode, classes[i]);
                }
            } 
        }
        
    },
    setClass:function(where,cls,set){
        if (set=='toggle'){
            genro.dom.toggleClass(where,cls)
        }
        else if (set) {
            this.addClass(where,cls);
        }else {
            this.removeClass(where,cls);
        }
    },
    toggleClass:function(where,cls){
        if(typeof(cls)=='string'){
            var toggle=function (n,c){
                        dojo[dojo.hasClass(n,c)?'removeClass':'addClass'](n,c)
                       }
            var domnode=this.getDomNode(where);
            if (!domnode) return;
            var classes = cls.split(' ');
            for (var i=0;i<classes.length;i++){
                if (domnode.forEach){
                    domnode.forEach(function(n){toggle(n,classes[i])})
                }else{
                    toggle(domnode,classes[i])
                }
            }
        }
    },
    bodyClass:function(cls,set){
        genro.dom.setClass(dojo.body(),cls,set);
    },
    
    disable:function(where){
        this.addClass(where,'disabled');
    },
    enable:function(where){
        this.removeClass(where,'disabled');
    },
    hide:function(where){
         this.addClass(where,'hidden');
    },
    show:function(where){
        this.removeClass(where,'hidden');
    },
    toggleVisible:function(where, visible){
        if (visible){
            this.show(where);
        }else{
            this.hide(where);
        }
    },
    effect:function(where,effect,kw){
        var anim;
        var effect = effect.toLowerCase();
        var kw = kw || {};
        if ( typeof (where) == 'string'){
            var where=genro.domById(where);
        }
        if (!where){
            return;
        }
        kw.node = where;
        kw.duration = kw.duration || 300;
        if (effect == 'fadein'){
            genro.dom.style(where,{opacity:0});
            anim = dojo.fadeIn(kw);
        }
        else if (effect == 'fadeout'){
            genro.dom.style(where,{opacity:1});
            anim =dojo.fadeOut(kw);
        }
        else if (effect == 'wipein'){
            anim = dojo.fx.wipeIn(kw);
        }
        else if (effect == 'wipeout'){
            anim = dojo.fx.wipeOut(kw);
        }
        else{
            //genro.debug('the effect does not exist','console') ;
            return;
        }
        anim.play();
        return anim;
    },
    ghostOnEvent:function(evt){
        evt_type = evt.type;
        if (evt_type=='focus' || evt_type=='blur'){
            genro.dom[evt_type=='focus'?'addClass':'removeClass'](evt.target.id+"_label","ghostpartial");
        }
        else if (evt_type=='keyup'||evt_type=='keypress'){
            genro.dom[evt.target.value.length>0?'addClass':'removeClass'](evt.target.id+"_label","ghosthidden");
        }else if (evt_type=='setvalue'){
            genro.dom[evt.value.length>0?'addClass':'removeClass'](evt.obj.id+"_label","ghosthidden");
        }else{
            //console.log('line 179 genro_dom');
        }
    },
    html_maker:function(kw,bagnode){
        kw = genro.evaluate(kw);
        return genro.dom['html_'+kw.widget](kw,bagnode);
    },
    html_checkbox:function(kw,bagnode){
        if ('value' in kw){
            var path = kw.value;
            kw.onclick = dojo.hitch(bagnode,function(e){
                    var v = e.target.checked;
                    this.setAttr(path,v);
            });
            kw.checked = bagnode.getAttr(path);
        }
        return '<input type="checkbox" name="'+kw.name+'" checked="'+kw.checked+'" id="'+kw.id+'" onclick="'+kw.onclick+'"><label for="'+kw.id+'">'+kw.label+'</label>';
    },
    
    html_select:function(kw){
        var values = kw.values.split(',');
        var wdg = '<label for="'+kw.id+'">'+kw.label+'</label>';
        wdg = wdg+'<select name="'+kw.name+'" id="'+kw.id+'" onchange="'+kw.onchange+'" size="1">';
        wdg = wdg + '<option value="false">&nbsp</option>';
        for (var i=0; i < values.length; i++) {
            var val = values[i];
            var subwdg = null;
            if (val.indexOf(':')){
                val = val.split(':');
                subwdg = '<option value="'+val[0]+'">'+val[1]+'</option>';
            }else{
                subwdg = '<option value="'+val+'">'+val+'</option>';
            }
            wdg = wdg + subwdg;
        };
        wdg = wdg + '</select>';
        return wdg;
    },

    enableDisableNodes:function(where){
        if ( typeof (where) == 'string'){
                var where=genro.domById(where);
        }
    },
    resizeContainer:function(wdgt){
        if (wdgt.parent && wdgt.parent.isContainer ){
            this.resizeContainer(wdgt.parent);
        }else if (wdgt.isContainer){
            wdgt.onResized();
        }
    },
    
    getStyleDict: function(attributes/*{}*/, noConvertStyle){
        if (attributes.gnrIcon){
            attributes.iconClass='gnrIcon gnrIcon'+objectPop(attributes,'gnrIcon');
        }
        var noConvertStyle = noConvertStyle || [];
        var styledict =  objectFromStyle(objectPop(attributes, 'style'));
        var attrname;
        for (var i=0; i<this.styleAttrNames.length; i++){
           attrname = this.styleAttrNames[i];
           if (attrname in attributes && arrayIndexOf(noConvertStyle,attrname)==-1){
                  styledict[attrname.replace('_','-')]=objectPop(attributes,attrname);
           }
        }
        this.style_setall('min', styledict, attributes, noConvertStyle);
        this.style_setall('max', styledict, attributes, noConvertStyle);
        this.style_setall('background', styledict, attributes, noConvertStyle);
        this.style_setall('text', styledict, attributes, noConvertStyle);
        this.style_setall('font', styledict, attributes, noConvertStyle);
        this.style_setall('margin', styledict, attributes, noConvertStyle);
        this.style_setall('padding', styledict, attributes, noConvertStyle);
        this.style_setall('border', styledict, attributes, noConvertStyle);
        this.style_setall('overflow', styledict, attributes, noConvertStyle);
        return styledict;
    },  
    style_setall:  function(label, styledict/*{}*/, attributes/*{}*/,noConvertStyle){
        for(var attrname in attributes){
            if(stringStartsWith(attrname, label+'_') && arrayIndexOf(noConvertStyle,attrname)==-1 ){
                styledict[attrname.replace('_','-')]=objectPop(attributes,attrname);
            }
        }    
    },
    addCssRule: function(rule){
        var styles=document.styleSheets;
        for (var i=0;i<styles.length;i++){
            var stylesheet=styles[i];
            if (stylesheet.title=='localcss'){
                if (stylesheet.insertRule) {
                    stylesheet.insertRule(rule,0);
                }
                else
                {   
                    splittedrule = /(.*)\{(.*)\}/.exec(rule);
                    if (splittedrule[1] && splittedrule[2]) stylesheet.addRule(splittedrule[1], splittedrule[2]);
                }
                break;
            }
        }
        
    },
    cssRulesToBag:function(rules){
        var result = new gnr.GnrBag();
        var _importRule = 3;
        var _styleRule = 1;
        var rule,label,value,attr;
        for (var i=0, len=rules.length; i < len; i++) {
            r = rules.item(i);
            switch(r.type){
                case _styleRule:
                    label ='r_'+i;
                    value = genro.dom.styleToBag(r.style);
                    result.setItem(label,value,{selectorText:r.selectorText,_style:r.style});
                    this.css_selectors[r.selectorText] = value;
                    break;
                case _importRule:
                    attr = {href:r.href};
                    label = r.title || 'r_'+i;
                    result.setItem(label,genro.dom.cssRulesToBag(r.styleSheet.cssRules),attr);

                    break;
                // default:
                //     console.log('cssRulesToBag(): rule #' + i);
                //     console.log(r);
            }
        };
        
        return result;
    },
    setSelectorStyle: function(selector,kw,path){
        var path = path || 'gnr.stylesheet';
        var selectorbag = this.css_selectors[selector];
        for(st in kw){
            selectorbag.setItem(st,kw[st]);
        }
    },
    getSelectorBag: function(selector){
        return this.css_selectors[selector];
    },
    styleSheetBagSetter:function(value,kw){
        var setters = objectExtract(kw,'_set_*',true);
        for (var setter in setters){
            var setlist = setters[setter].split(':');
            var s={};
            s[setter.replace('_','-')]=genro.evaluate(setlist.slice(1).join(':').replace('#',value));
            genro.dom.setSelectorStyle(setlist[0],s);
        }   
    },
    
    styleSheetsToBag:function(){
        var styleSheets=document.styleSheets;
        var result = new gnr.GnrBag();
        var label,value,attr;
        var cnt = 0;
        this.css_selectors = {};
        dojo.forEach(styleSheets,function(s){
            label = s.title || 's_'+cnt;
            attr = {'type':s.type,'title':s.title};
            value = genro.dom.cssRulesToBag(s.cssRules);
            result.setItem(label,value,attr);
            cnt++;
        });
        return result;
    },
    styleToBag:function(s){
        result = new gnr.GnrBag();
        var rule;
        // for (var i=0; i < s.length; i++) {
        //     st = s[i];
        //     result.setItem(st, s.getPropertyValue(st)); 
        // };
        for(var i = s.length; s--;) {
            var st = s[i];
            result.setItem(st, s.getPropertyValue(st));
        }
        return result;
    },
    windowTitle:function(title){
        document.title=title;
    },
    styleTrigger:function(kw){
        var parentNode = kw.node.getParentNode();
        var st = parentNode.attr._style;
        if (!st){
            return;
        }
        if (kw.evt=='upd') {
            st.setProperty(kw.node.label,kw.value,null);
        }else if(kw.evt=='ins'){
            st.setProperty(kw.node.label,kw.node.getValue(),null);
        }else if(kw.evt=='del'){
           // console.log(kw);
        }
        var stylebag = genro.dom.styleToBag(st);
        parentNode.setValue(stylebag);
        this.css_selectors[parentNode.attr.selectorText] = stylebag;
    },
    cursorWait:function(flag){
        if (flag){
            genro.dom.addClass(document.body, 'cursorWait');
        } else {
            genro.dom.removeClass(document.body, 'cursorWait');
        }
    },
    makeReadOnlyById:function(fieldId) {
        var field = dojo.byId(fieldId);
        field.readOnly = true;
        field.style.cursor = 'default';
        dojo.connect(field, 'onfocus', function () { field.blur(); });
    },
    showHideSubRows:function (evt){
        var row = evt.target.parentNode.parentNode;
        var currlevel = row.getAttribute('lvl');
        var newstatus = '';
        if (row.getAttribute('isclosed') != 'y'){
            newstatus = 'y';
        }
        row.setAttribute('isclosed', newstatus);
        
        var rows = row.parentNode.rows;
        var rowlevel, sublevel;
        for (var i=0;i<rows.length;i++){
            rowlevel = rows[i].getAttribute('lvl');
            if(rowlevel.indexOf(currlevel)==0){  //row level starts with currlevel
                if (rowlevel != currlevel){      //but is longer (is a sublevel)
                    if (newstatus=='y'){ // hide all subchild 
                        rows[i].setAttribute('rowhidden', newstatus);
                        if (rowlevel.slice(-2) != '._'){
                            rows[i].setAttribute('isclosed', newstatus);
                        }
                    } else {
                        sublevel = rowlevel.replace(currlevel+'.','');
                        if(sublevel.indexOf('.')<0){ // open only first level subchild 
                            rows[i].setAttribute('rowhidden', newstatus);
                        }
                    }
                }
            }
        }
    },
    parseXmlString:function (txt){
        var result;
        if(dojo.isIE){
            result=new ActiveXObject("Microsoft.XMLDOM");
            result.async="false";
            result.loadXML(txt);
        }else{
            var parser = new DOMParser();
            result=parser.parseFromString(txt, 'text/xml');	//	DOMDocument
        }
        return result;
    },
    dispatchKey: function(keycode, domnode){
        var domnode = domnode || document.body;
        var e = document.createEvent('KeyboardEvent');
        // Init key event
        e.initKeyEvent('keydown', true, true, window, false, false, false, false, keycode, 0);
        // Dispatch event into document
        domnode.dispatchEvent(e);
    },
    canBeDropped:function(dataTransfer,sourceNode){
        if (!sourceNode){
            console.log('no sourceNode');
            return;
        }
        var supportedTypes=splitStrip(sourceNode.getInheritedAttributes().drop_types || 'text/plain');
        var draggedTypes =dataTransfer.types;
        if(dojo.filter(supportedTypes,function (value){ return dojo.indexOf(draggedTypes,value)>=0;}).length==0){
            return false;
        };
        var drop_tags=sourceNode.getInheritedAttributes().drop_tags;
        if(!drop_tags){
            return true;
        }
        var drag_tags=dataTransfer.getData('drag_tags') || '';
        if(!drag_tags){
            return false;
        }
        var drag_tags=splitStrip(drag_tags,',');
        var or_conditions=splitStrip(drop_tags,',');
        valid=false;
        for (var i=0; ((i < or_conditions.length) && !valid); i++) {
            var valid=true;
            var or_condition=or_conditions[i].replace(/' NOT '/g,' AND !');
            or_condition=splitStrip(or_condition,' AND ');
            for (var j=0; ((j < or_condition.length) && valid); j++) {
                var c=or_condition[j];
                exclude=false;
                if (c[0]=='!'){
                    c=c.slice(1);
                    exclude=true;
                }
                var match=dojo.some(drag_tags,function(k){return k==c;});
                valid = exclude? !match:match;
            };
            
        };
        return valid;
   
    },
    onDragOver:function(event){
        this.decorateEvent(event)
        var droppable=event.dragDropInfo;
        if (!droppable){ return;}
        event.stopPropagation();
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";

    },
    
    decorateEvent:function(event){
        var domnode = event.target;
        var widget = dijit.getEnclosingWidget(domnode);
        if (widget.declaredClass=='dojox.GridView' || widget.declaredClass=='dojox.VirtualGrid') {
            var eventDecorator;
            if (widget.declaredClass=='dojox.VirtualGrid'){
                eventDecorator = widget.views.views[0].header;
            }else{
                eventDecorator = widget.content;
                widget=widget.grid;
            }
            var sourceNode = widget.sourceNode;
            eventDecorator.decorateEvent(event)
        }
        event.widget=widget
        sourceNode= sourceNode || genro.dom.getSourceNode(domnode);
        event.sourceNode=sourceNode;
        if (sourceNode){
            sourceNode.getBuiltObj().gnr.onDragDropEvent(event)
        }else{
            console.log('No sourcenode');
            console.log(event)
            
        }
        
    },
    onDragEnter:function(event){
        this.decorateEvent(event)
        var droppable=event.dragDropInfo;
         console.log('onDragEnter:')
        if (!droppable){ 
            console.log('not droppable:')
            return;
        }
      //if(genro.dom._dragged){
      //    if((genro.dom._dragged.sourceNode==event.sourceNode) && (genro.dom._dragged.widget==event.widget) &&( genro.dom._dragged.domnode==event.domnode)){
      //       console.log('same object:')
      //        console.log(event)
      //        console.log(genro.dom._dragged)
      //        return
      //    }
      //}
        var domnode=droppable.domnode;
        var sourceNode=droppable.sourceNode;
        event.stopPropagation();
        event.preventDefault();
        var dataTransfer=event.dataTransfer;
        var canBeDropped=this.canBeDropped(dataTransfer,sourceNode);
        console.log('onDragEnter:'+canBeDropped)
        dataTransfer.effectAllowed=canBeDropped?'move':'none';
        dataTransfer.dropEffect=canBeDropped?'move':'none';
        if(droppable.outlineColumn){
            genro.dom.outlineShape(droppable.outlineColumn,canBeDropped,event)
        }else if(droppable.outlineCell){
            genro.dom.outlineShape(droppable.outlineCell,canBeDropped,event)
        }else if(droppable.outlineRow){
            genro.dom.outlineShape(droppable.outlineRow,canBeDropped,event)
        }else if(droppable.outlineGrid){
            genro.dom.outlineShape(droppable.outlineGrid,canBeDropped,event)
        }
        else if(droppable.outlineNode){
            genro.dom.outlineShape(droppable.outlineNode,canBeDropped,event)
        }
        
    },
    outlineShape:function(shape,canBeDropped,x){
         if(genro.dom._dragLastShape){
             genro.dom.removeClass(genro.dom._dragLastShape,'canBeDropped');
             genro.dom.removeClass(genro.dom._dragLastShape,'cannotBeDropped');
             genro.dom._dragLastShape=null
         }
         if (shape){
            genro.dom.setClass(shape,'cannotBeDropped',!canBeDropped);
            genro.dom.setClass(shape,'canBeDropped',canBeDropped);
            genro.dom._dragLastShape=shape
         }else{
            genro.dom.removeClass(dojo.body(),'drag_started')
            genro.dom.removeClass(dojo.body(),'drag_to_trash')
         }
    },
   
     onDrop:function(event){
        genro.dom.outlineShape(null)
        this.decorateEvent(event)
        var droppable=event.dragDropInfo;
        if (!droppable){ return;}
        var domnode=droppable.domnode;
        var sourceNode=droppable.sourceNode;
        var dataTransfer=event.dataTransfer;
        event.stopPropagation();
        genro.dom.removeClass(domnode,'canBeDropped');
        genro.dom.removeClass(domnode,'cannotBeDropped');
        canBeDropped=this.canBeDropped(dataTransfer,sourceNode);
        if(canBeDropped){
            var inherited=sourceNode.getInheritedAttributes();
            event.preventDefault();
            var action = inherited.drop_action;
            var dropped=null;
            if (action){
                var drop_types=(inherited.drop_types || 'text/plain').split(',');
                var params=objectUpdate(sourceNode.currentAttributes(),{'drop_object':dataTransfer,'event':event});
                if ((dojo.indexOf(dataTransfer.types,'Files')>=0 )&& (dojo.indexOf(drop_types,'Files')>=0)){
                    console.log('files');
                    var drop_ext=inherited.drop_ext;
                    var valid_ext=drop_ext?splitStrip(drop_ext):null;
                    var files=[];
                    dojo.forEach(dataTransfer.files,function(f){
                        if((!valid_ext) || (dojo.indexOf(drop_ext,f['name'].split('.').pop())>=0)){
                            files.push(f);
                        }
                    });
                    if(files.length>0){
                        params['files']=files;
                        funcApply(action,params, sourceNode);
                    }
                }else{
                    for (var i=0; i < drop_types.length; i++) {
                        if (dojo.indexOf(dataTransfer.types,drop_types[i])>=0){
                            var datatype=drop_types[i];
                            var value=dataTransfer.getData(datatype)
                            if (stringEndsWith(datatype,'/json')){
                                value=convertFromText(value,'JS');
                            }
                            params['drop_data']=value;
                            params['drop_item']=droppable.item;
                            params['drop_event']=event
                            params['drop_datatype']=datatype
                            funcApply(action,params, sourceNode);
                            break;
                        }
                    }
                }       
            }             
         }
     },
    onDragStart:function(event){
        event.stopPropagation();
        //console.log(event);
         console.log('onDragStart')
        this.decorateEvent(event);
        var domnode=event.target;
        var widget = event.widget;
        var sourceNode = event.sourceNode;
        var value;
        var dataTransfer=event.dataTransfer;
        var inherited=sourceNode.getInheritedAttributes();
        if ('drag_value_cb' in inherited){
            value=funcCreate(inherited['drag_value_cb'],'sourceNode,item,event')(sourceNode,widget.item,event);
        }else{
            if(widget.isTreeNode){
                value=(widget.item instanceof gnr.GnrBagNode)? widget.item.getValue():widget.item.label;
            }
            else if ('drag_value' in inherited){
                value=sourceNode.currentFromDatasource(inherited['drag_value']);
            }
            else if ('value' in sourceNode.attr){
                value=sourceNode.getAttributeFromDatasource('value');
            }
            else if ('innerHTML' in sourceNode.attr){
                value=sourceNode.getAttributeFromDatasource('innerHTML');
            }
            else{
                 value=domnode.innerHTML;
            }
            value={'text/plain':value}
        }
        var drag_class=inherited['drag_class'];
        if(drag_class){
            genro.dom.addClass(domnode,drag_class);
        }
        
        if (typeof(value)=='object'){
            if('trashable/json' in value){
                genro.dom.addClass(dojo.body(),'drag_to_trash');
                if(widget){
                    widget.gnr.setTrashPosition(event);
                }
            }
            for (var k in value){
                dataTransfer.setData(k, convertToText(value[k])[1]);
            }
        }else{
            dataTransfer.setData('text/plain', convertToText(value)[1]);
        }
        genro.dom._dragged={'sourceNode':event.sourceNode,'widget':event.widget,
                            'domnode':event.domnode}
      
        genro.dom.addClass(dojo.body(),'drag_started')
        var drag_tags=inherited['drag_tags'];
         
        if(drag_tags){
            dataTransfer.setData('drag_tags', drag_tags);
        }
    },
    onDragEnd:function(event){
        genro.dom.outlineShape(null)

    },
    onDrag:function(event){
        var domnode=event.target;
        var sourceNode=genro.dom.getSourceNode(domnode);
        var inherited=sourceNode.getInheritedAttributes();
        var drag_class=inherited['drag_class'];
        if(drag_class){
            genro.dom.removeClass(domnode,drag_class);
        }
    },
    getSourceNode:function(domnode){
        var widget=dijit.getEnclosingWidget(domnode);
        if (widget){
            if(widget.isTreeNode){
                return widget.tree.sourceNode;
            }else if  (widget.declaredClass=='dojox.GridView'){
                return widget.grid.sourceNode;
            }
        }
        while (domnode && !domnode.sourceNode && domnode!=widget.domNode){
            domnode=domnode.parentNode;
        }
        return domnode.sourceNode || widget.sourceNode;
    },
                    
    startTouchDevice:function(){
       document.body.ontouchmove= function(e){
            e.preventDefault();
        };
        /* 
        dojo.connect(document.body, 'ontouchstart', function(e){
            genro.setData('gnr.touch.orientation',window.orientation);
            for (var i=0; i < e.touches.length; i++) {
                var touch=e.touches[i]
                var t=''
                for (var k in touch){
                    genro.setData('touch.tc_'+i+'.'+k,e[k]);

                 }
            };
        
        });
       dojo.connect(document.body, 'touchend', function(e){

            var dx=e.screenX-this.startTouch_x
            var dy=e.screenY-this.startTouch_y
            //alert(dx+'  ,  '+dy)
            this.startTouch_x=null
            this.startTouch_y=null
        });*/

        document.body.onorientationchange= function(e){
            genro.setData('touch.orientation',window.orientation);
        };
        dojo.connect(document.body,'gestureend',  function(e){
            genro.dom.logTouchEvent('gesture',e);
        });
    
    },
    logTouchEvent:function(path,e){
        
        var b='';
        for (var k in e){
            b=b+k+':'+e[k]+'<br/>';
        }
        genro.setData('touch.event.'+path,b);
    },
    scrollableTable:function(domnode,gridbag,kw){
        var columns = kw.columns;
        var headers = kw.headers;
        var tblclass = kw.tblclass;
        var thead='<thead><tr>';
        for(var k=0; k< columns.length; k++){
             thead=thead+"<th>"+headers[k]+"</th>";
        }
        thead = thead+"<th style='width:10px; background-color:transparent;'>&nbsp</th></thead>";
        var nodes = gridbag.getNodes();
        var item,r, value;
        var tbl=["<tbody>"];
        for(var i=0; i< nodes.length; i++){
            r="";
            item=nodes[i].attr;
             for(var k=0; k< columns.length; k++){
                 value = item[columns[k]] || '&nbsp';
                 r=r+"<td>"+genro.format(value,{date:'short'});+"</td>";
             }
            tbl.push("<tr id='"+nodes[i].label+"'>"+r+"</tr>");
        }
        tbl.push("</tbody>"); 
        var tbody=tbl.join('');
        var cbf = function(cgr){
            
            var cgr_h = cgr?'<colgroup>'+cgr+'<col width=10 /></colgroup>':'';
            var cgr_b = cgr?'<colgroup>'+cgr+'</colgroup>':'';
            return '<div class="'+tblclass+'"><div><table>'+cgr_h+''+thead+'</table></div><div style="overflow-y:auto;max-height:180px;"><table>'+cgr_b+tbody+'</table></div></div>';
        };
        domnode.innerHTML=cbf('');
        var cb = function(){
            var hdrtr = dojo.query('thead tr',domnode)[0].children;
            var bodytr = dojo.query('tbody tr',domnode);
            var bodytr_first = bodytr[0].children;
            var colgroup = "";
            for (var i=0; i < bodytr_first.length; i++) {
                var wh = hdrtr[i].clientWidth;
                var wb = bodytr_first[i].clientWidth;
                var wt = wh>wb?wh:wb;
                colgroup=colgroup+'<col width="'+wt+'"/>';
            };  
            domnode.innerHTML=cbf(colgroup);
            dojo.style(domnode,{width:'auto'});
            var rows = dojo.query('tbody tr',domnode);
            for (var i=0; i < rows.length; i++) {
                rows[i].item = nodes[i];
            };
        };
        setTimeout(cb,1); 
    },
    centerOn: function(what,where){
        var whatDomNode = this.getDomNode(what);
        var whereDomNode = where?this.getDomNode(where): whatDomNode.parentNode;
        var viewport=dojo.coords(whereDomNode);
        var mb = dojo.marginBox(whatDomNode);
        var result = {};
        var style = whatDomNode.style;
        var whereposition = whereDomNode.style.position;
        var deltax = whereposition==viewport.l;
        var deltay = viewport.t;
        if (whereposition=='relative'){
            deltax = deltax +viewport.x;
            deltay = deltay + viewport.y;
        }
        style.left = Math.floor((deltax + (viewport.w - mb.w)/2)) + "px";
        style.top = Math.floor((deltay + (viewport.h - mb.h)/2)) + "px";
                   //var viewport=dojo.coords(genro.domById(centerOn));
           //viewport.l=viewport.x;
           //viewport.t=viewport.y;
           //var mb = dojo.marginBox(this.domNode);
           //var style = this.domNode.style;
           //style.left = Math.floor((viewport.l + (viewport.w - mb.w)/2)) + "px";
           //style.top = Math.floor((viewport.t + (viewport.h - mb.h)/2)) + "px";
    },
    makeHiderLayer: function(parentId,kw){
        var rootNode = parentId?genro.nodeById(parentId):genro.src.getNode();
        var default_kw = {'position':'absolute',top:'0',left:'0',right:'0','bottom':0,
                                  z_index:1000,background_color:'rgba(255,255,255,0.5)',id:parentId+'_hider'};
        var kw = objectUpdate(default_kw,kw);
        return rootNode._('div',kw).getParentNode();
    }
    
});