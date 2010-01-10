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
        genro.dom.iframeContentWindow(iframe).print();
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
	
    insertCss:function(css){
        if (stringContains(css,'{')){
            dojo.html.insertCssText(css);
        }else{
            dojo.html.insertCssFile(css);
        }
    },
    addClass: function(where,cls){
        if(typeof(cls)=='string'){
            if ( typeof (where) == 'string'){
                var where=genro.domById(where);
            }
            if (where instanceof gnr.GnrDomSourceNode){
                where = where.getDomNode();
            }
            var classes=cls.split(' ');
            for (var i=0;i<classes.length;i++){
                dojo.addClass(where, classes[i]);
            }
        }  
    },
    removeClass: function(where, cls){
        if(typeof(cls)=='string'){
            if ( typeof (where) == 'string'){
                    var where=genro.domById(where);
            }
            if (where instanceof gnr.GnrDomSourceNode){
                where = where.getDomNode();
            }
            var classes = cls.split(' ');
            for (var i=0;i<classes.length;i++){
                dojo.removeClass(where, classes[i]);
            }
        }
        
    },
    setClass:function(where,cls,set){
        if (set) {
            this.addClass(where,cls);
        }else{
            this.removeClass(where,cls);
        }
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
    style:function(where,kw){
            if ( typeof (where) == 'string'){
                var where=genro.domById(where);
            }
    dojo.style(where,kw);
    },
    
    
    effect:function(where,effect,kw){
        var anim;
        var effect = effect.toLowerCase();
        var kw = kw || {};
        if ( typeof (where) == 'string'){
            var where=genro.domById(where);
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
        var evt_type = evt.type;
        if (evt_type=='focus' || evt_type=='blur'){
            genro.dom[evt_type=='focus'?'addClass':'removeClass'](evt.target.id+"_label","ghostpartial");
        }
        else if (evt_type=='keyup'){
            genro.dom[evt.target.value.length>0?'addClass':'removeClass'](evt.target.id+"_label","ghosthidden");
        }
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
    windowTitle:function(title){
        document.title=title;
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
    }


});