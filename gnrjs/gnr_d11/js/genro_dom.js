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
        var inherited=sourceNode.getInheritedAttributes()
        var dragSourceInfo=genro.dom.getDragSourceInfo(dataTransfer)
        var supportedTypes=splitStrip(sourceNode.getInheritedAttributes().dropTypes || 'text/plain');
        for (var k in objectExtract(inherited,'onDrop_*',true)){
            supportedTypes.push(k);
        }
        var draggedTypes=genro.dom.dataTransferTypes(dataTransfer)
        if(dojo.filter(supportedTypes,function (value){ return dojo.indexOf(draggedTypes,value)>=0;}).length==0){
            return false;
        };
        var dropTags=sourceNode.getInheritedAttributes().dropTags;
        if(!dropTags){
            return true;
        }
        //var dragTags=dataTransfer.getData('dragTags') || '';
        var dragTags = dragSourceInfo.dragTags
        if(!dragTags){
            return false;
        }
        var dragTags=splitStrip(dragTags,',');
        var or_conditions=splitStrip(dropTags,',');
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
                var match=dojo.some(dragTags,function(k){return k==c;});
                valid = exclude? !match:match;
            };
            
        };
        return valid;
   
    },
    onDragOver:function(event){
        if(false){
                var result=event.type+' ('+event.dataTransfer.getData('text/plain')+') :'
        var draggedTypes=event.dataTransfer.types
        for (var i=0; i < draggedTypes.length; i++) {
            result=result+draggedTypes[i]+'  '
        };
             console.log(result)
        }
    
        
        if(genro._lastDropTarget!=event.target){
            if(genro._lastDropTarget){
                genro.dom.onDragLeave(event)
            }
            genro._lastDropTarget=event.target
            genro.dom.onDragEnter(event)
        }
       event.stopPropagation();
       event.preventDefault();
       event.dataTransfer.dropEffect = "move";
       
    },
    getDragDropInfo:function(event){
        var domnode = event.target;
        while (!domnode.getAttribute){
             domnode=domnode.parentNode;
        }
        var info={'domnode':domnode};
        info.modifiers=genro.dom.getEventModifiers(event)
        var widget,handler,sourceNode;
        if(domnode.sourceNode){
            info.handler=domnode.gnr
            info.sourceNode=domnode.sourceNode 
            info.nodeId=domnode.sourceNode.attr.nodeId
        }
        else{
            widget=dijit.getEnclosingWidget(domnode)
            var rootwidget=widget.sourceNode?widget:widget.grid||widget.tree
            info.widget=widget
            if (!rootwidget){
                return;
            }
            info.handler=rootwidget.gnr
            info.sourceNode=rootwidget.sourceNode 
            info.nodeId=info.sourceNode.attr.nodeId
        }
        info.event=event;
        if (event.type=='dragstart'){
            info.dragmode=domnode.getAttribute('dragmode')
            info.handler.fillDragInfo(info)
        }else{
            var attr=info.sourceNode.attr
            var droppable=info.sourceNode.droppable
            if (droppable){
                info.dragSourceInfo=genro.dom.getDragSourceInfo(event.dataTransfer)
                info.sourceNodeId=info.dragSourceInfo.nodeId
                info.selfdrop=(info.nodeId && (info.nodeId==info.sourceNodeId))
                info.hasDragType=function(){
                    var draggedTypes=genro.dom.dataTransferTypes(event.dataTransfer)
                    return (dojo.filter(arguments,function (value){ return dojo.indexOf(draggedTypes,value)>=0;}).length>0)
                }
                if( typeof(droppable)=='function'){
                    droppable = funcApply(droppable, {'dropInfo':info}, info.sourceNode);
                }
            }
            if (droppable){
                info.dropmode=droppable
                info.handler.fillDropInfo(info)
            }else{
                info = null;
            }
        }
        return info
    },
    onDragLeave:function(event){
        if(genro.dom._dragLastOutlined){
            genro.dom.removeClass(genro.dom._dragLastOutlined,'canBeDropped');
            genro.dom.removeClass(genro.dom._dragLastOutlined,'cannotBeDropped');
            genro.dom._dragLastOutlined=null
        }
    },
    onDragEnter:function(event){
        var dropInfo=this.getDragDropInfo(event)
        
        if (!dropInfo){ 
            //console.log('not drag_info')
            return;
        }
        event.stopPropagation();
        event.preventDefault();
        var sourceNode=dropInfo.sourceNode;
        var dataTransfer=event.dataTransfer;
        var canBeDropped=this.canBeDropped(dataTransfer,sourceNode);
        dataTransfer.effectAllowed=canBeDropped?'move':'none';
        dataTransfer.dropEffect=canBeDropped?'move':'none';
        genro.dom.outlineShape(dropInfo.outline,canBeDropped,event)
    },
    outlineShape:function(shape,canBeDropped,x){
         if(genro.dom._dragLastOutlined){
             genro.dom.removeClass(genro.dom._dragLastOutlined,'canBeDropped');
             genro.dom.removeClass(genro.dom._dragLastOutlined,'cannotBeDropped');
             genro.dom._dragLastOutlined=null
         }
         if (shape){
            genro.dom.setClass(shape,'cannotBeDropped',!canBeDropped);
            genro.dom.setClass(shape,'canBeDropped',canBeDropped);
            genro.dom._dragLastOutlined=shape
         }else{
            genro.dom.removeClass(dojo.body(),'drag_started')
            genro.dom.removeClass(dojo.body(),'drag_to_trash')
         }
    },
   
     onDrop:function(event){
        genro.dom.outlineShape(null)
        event.stopPropagation();
        var dropInfo=this.getDragDropInfo(event)
        if (!dropInfo){ return;}
        var domnode=dropInfo.domnode;
        var sourceNode=dropInfo.sourceNode;
        var dataTransfer=event.dataTransfer;
        var canBeDropped=this.canBeDropped(dataTransfer,sourceNode); // dovrei già essere bono
        if(canBeDropped){
            var inherited=sourceNode.getInheritedAttributes();
            event.preventDefault();
            var dropped=null;
            var dataTransferTypes=genro.dom.dataTransferTypes(dataTransfer)
            var dropTypes=(inherited.dropTypes || 'text/plain').split(',');
            //var params=objectUpdate(sourceNode.currentAttributes(),{'drop_object':dataTransfer,'event':event});
            var params={'dropInfo':dropInfo}
            if ((dojo.indexOf(dataTransferTypes,'Files')>=0 )&& (dojo.indexOf(dropTypes,'Files')>=0)){
                 genro.dom.onDrop_files(dataTransfer,inherited,params,sourceNode)
            }else{
               genro.dom.onDrop_standard(dataTransfer,inherited,params,sourceNode,dropTypes,dataTransferTypes)
            }
         }
     },
    onDrop_files:function(dataTransfer,inherited,params,sourceNode){
        var onDropAction = inherited.onDrop;
        if (!onDropAction){return}
        console.log('files');
        var drop_ext=inherited.drop_ext;
        var valid_ext=drop_ext?splitStrip(drop_ext):null;
        var files=[];
        dojo.forEach(dataTransfer.files,function(f){
            if((!valid_ext) || (dojo.indexOf(drop_ext,f['name'].split('.').pop())>=0)){
                files.push(f);
            }});
        if(files.length>0){
            params['files']=files;
            funcApply(onDropAction,params, sourceNode);
        }
    },
    onDrop_standard:function(dataTransfer,inherited,params,sourceNode,dropTypes,dataTransferTypes){
        var onDropAction = inherited.onDrop;
        var values={}
        for (var i=0; i < dataTransferTypes.length; i++) {
            var datatype=dataTransferTypes[i];
            var datatype_code=datatype.replace(/\W/g,'_')
            if (inherited['onDrop_'+datatype_code] || (dojo.indexOf(dropTypes,dataTransferTypes[i])>=0)){
                 var value=genro.dom.getFromDataTransfer(dataTransfer,datatype)
                if (inherited['onDrop_'+datatype_code]){
                    params['data']=value;
                    funcApply(inherited['onDrop_'+datatype_code],params, sourceNode);
                }else{
                    values[datatype_code]=value
                }
            }  
        }
        if(objectNotEmpty(values) && onDropAction){
            params['data']=values
            funcApply(onDropAction,params, sourceNode);
        }
     },
    onDragStart:function(event){
        event.stopPropagation();
        if(event.target.draggable===false){
            event.preventDefault();
            return false;
        }
        var dragInfo=this.getDragDropInfo(event)
        var dragValues=dragInfo.handler.onDragStart(dragInfo)
        var sourceNode=dragInfo.sourceNode
        var inherited=sourceNode.getInheritedAttributes();
        if ('dragIf' in inherited) {
            var doDrag=funcCreate('return '+inherited['dragIf'],'dragValues,dragInfo,treeItem')(dragValues,dragInfo,dragInfo.treeItem)
            if (!doDrag){
                return
            }
        }
    
        if ('onDrag' in inherited){
            var result=funcCreate(inherited['onDrag'],'dragValues,dragInfo,treeItem')(dragValues,dragInfo,dragInfo.treeItem)
            if (result===false){
                return
            }
            if(typeof(result)=='object'){
                objectUpdate(dragValues,result)
            }
        }
        var domnode=dragInfo.target;
        var widget = dragInfo.widget;
        genro.dom._transferObj={}
        var dataTransfer=event.dataTransfer;
        var dragClass=inherited['dragClass'] || 'draggedItem';
        if(dragClass){
            genro.dom.addClass(dragInfo.domnode,dragClass);
            dragInfo.dragClass=dragClass;
            setTimeout(function(){genro.dom.removeClass(dragInfo.domnode,dragClass);},1);
        }
        if('trashable' in dragValues){
            genro.dom.addClass(dojo.body(),'drag_to_trash');
            if(widget){
                widget.gnr.setTrashPosition(event);
            }
        }
        var dragTags=inherited['dragTags'];
        var local_dragTags = objectPop(dragValues, 'dragTags');
        dragTags = dragTags? (local_dragTags? dragTags+','+local_dragTags : dragTags ): local_dragTags;
        genro.dom.setDragSourceInfo(dragInfo,dragValues,dragTags);
        for (var k in dragValues){
            genro.dom.setInDataTransfer(dataTransfer,k, dragValues[k])
        }
        genro.dom._lastDragInfo=dragInfo
        genro.dom.addClass(dojo.body(),'drag_started')
    },
    setInDataTransfer:function(dataTransfer,k,v){
        var v=convertToText(v)
        v=((k.indexOf('text/')==0) || (v[0]=='') || (v[0]=='T')) ? v[1] : v[1]+'::'+v[0]
        dataTransfer.setData(k, v);
        if(genro.dom.dragDropPatch()){
            genro.dom._transferObj[k]=v;
        }
    },
    setDragSourceInfo:function(dragInfo,dragValues,dragTags){
        if(dragInfo.nodeId){
            dragValues['sourceNode_nodeId:'+dragInfo.nodeId]=null
        }
        if(dragInfo.dragmode){
            dragValues['sourceNode_dragmode:'+dragInfo.dragmode]=null
        }
        dragValues['sourceNode_page_id:'+genro.page_id]=null
        if (dragTags){
            dragValues['sourceNode_dragTags:'+dragTags]=null
        }
     },
    getDragSourceInfo:function(dataTransfer){
        var draggedTypes=genro.dom.dataTransferTypes(dataTransfer)
        var dt;
        var result={};
        for (var i=0; i < draggedTypes.length; i++) {
            if(draggedTypes[i].indexOf('sourceNode_')==0){
                dt=draggedTypes[i].slice(11).split(':')
                result[dt[0]]=dt[1]
            }
        };
        return result
    },
    getFromDataTransfer:function(dataTransfer,k){
        var value= genro.dom.dragDropPatch() ? (genro.dom._transferObj?genro.dom._transferObj[k]:null):dataTransfer.getData(k)
        return convertFromText(value)
    },
    dataTransferTypes:function(dataTransfer){
        if (genro.dom.dragDropPatch()){
            var dt=[]
            if (genro.dom._transferObj){
                for (var k in genro.dom._transferObj){
                    dt.push(k)
                }
            }
            for (var i=0; i < dataTransfer.types.length; i++) {
                dt.push(dataTransfer.types[i]);
            };
            return dt
        }else{
            return dataTransfer.types
        }
         return dataTransfer.types
    },
    onDragEnd:function(event){
        genro.dom.outlineShape(null)
    },
    getEventModifiers:function(e){
        var m=[]
        if (e.shiftKey){m.push('Shift');}
        if (e.ctrlKey){m.push('Ctrl');}
        if (e.altKey){m.push('Alt');}
        if (e.metaKey){m.push('Meta');}
        return m.join()
    },
    dragDropPatch:function(){
        return (genro.isChrome)
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
        var deltax = viewport.l;
        var deltay = viewport.t;
       //if (whereposition=='relative' || whereposition=='absolute'){
       //    deltax = deltax +viewport.x;
       //    deltay = deltay + viewport.y;
       //}
        style.left = Math.floor((deltax + (viewport.w - mb.w)/2)) + "px";
        style.top = Math.floor((deltay + (viewport.h - mb.h)/2)) + "px";
    },
    makeHiderLayer: function(parentId,kw){
        var rootNode = parentId?genro.nodeById(parentId):genro.src.getNode();
        var default_kw = {'position':'absolute',top:'0',left:'0',right:'0','bottom':0,
                                  z_index:1000,background_color:'rgba(255,255,255,0.5)',id:parentId+'_hider'};
        var kw = objectUpdate(default_kw,kw);
        return rootNode._('div',kw).getParentNode();
    }
    
});