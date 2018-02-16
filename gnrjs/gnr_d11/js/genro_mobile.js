/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_dlg : todo
 * Copyright (c) : 2004 - 2007 Softwell sas - Milano
 * Written by    : Giovanni Porcari, Michele Bertoldi
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

dojo.declare("gnr.GnrMobileHandler", null, {
    constructor: function(application) {
        this.application = application;
        for(var k in this){
            if(stringStartsWith(k,'patch_')){
                this[k]();
            }
        }
        this.initialize();
    },
    initialize:function() {
        dojo.addClass(document.body,'touchDevice');
        dojo.addClass(document.body,'bodySize_'+genro.deviceScreenSize);

        this.lastTouchEnd = 0;
        document.addEventListener('touchend', function (event) {
            var now = (new Date()).getTime();
            if (now - genro.mobile.lastTouchEnd <= 300) {
                event.preventDefault();
            }
            genro.mobile.lastTouchEnd = now;
        }, false);

        
        this.startHammer(document.body);
        document.body.onorientationchange = function(e) {
            genro.setData('touch.orientation', window.orientation);
        };
    },

    startHammer:function(domNode){
        this.hammertime = new Hammer(domNode);
       // this.hammertime.on('pan', function(ev) {
       //     genro.publish('hammer_input',{'evt':ev,'type':'pan'})
       // });
        this.hammertime.on('tap', function(ev) {
            genro.mobile.handleMobileEvent(ev);
        });
        this.hammertime.on('doubletap', function(ev) {
            genro.mobile.handleMobileEvent(ev);
        });
        this.hammertime.on('press', function(ev) {
            genro.mobile.handleMobileEvent(ev);
        });
        this.hammertime.on('swipe', function(ev) {
            genro.mobile.handleMobileEvent(ev);
        });
        //this.hammertime.on('rotate', function(ev) {
        //    genro.publish('hammer_input',{'evt':ev,'type':'rotate'})
        //});

        // 'tap', 'doubletap', 'pan', 'swipe', 'press', 'pinch', 'rotate' 
       //this.hammertime.on("hammer.input", function(ev) {
       //    genro.publish('hammer_input',{'evt':ev});
       //});
    },

    handleMobileEvent:function(ev){
        var info = genro.dom.getEventInfo(ev);

        if(!info || !info.sourceNode){
            return;
        }
        //console.log('eventinfo',info.event.type,info)

        info.sourceNode.publish(info.event.type,info);
        genro.publish('mobile_'+info.event.type,info);
    },
    
    touchEventString:function(e){
        var b = '';
        for (var k in e) {
            b = b + k + ':' + e[k] + '<br/>';
        }
        return b;
    },

    patch_splitter:function(){
        dojo.require("dijit.layout.BorderContainer");
        dojo.require("dijit.layout._LayoutWidget");
        dijit.layout._Splitter.prototype.templateString = dijit.layout._Splitter.prototype.templateString.replace('onmousedown','ontouchstart');
        //console.log('patch_splitter',dijit.layout._Splitter);
        dijit.layout._Splitter.prototype._startDrag = function(e){
            if(!this.cover){
                this.cover = dojo.doc.createElement('div');
                dojo.addClass(this.cover, "dijitSplitterCover");
                dojo.place(this.cover, this.child.domNode, "after");
            }else{
                this.cover.style.zIndex = 1;
            }

            // Safeguard in case the stop event was missed.  Shouldn't be necessary if we always get the mouse up. 
            if(this.fake){ dojo._destroyElement(this.fake); }
            if(!(this._resize = this.live)){ //TODO: disable live for IE6?
                // create fake splitter to display at old position while we drag
                (this.fake = this.domNode.cloneNode(true)).removeAttribute("id");
                dojo.addClass(this.domNode, "dijitSplitterShadow");
                dojo.place(this.fake, this.domNode, "after");
            }
            dojo.addClass(this.domNode, "dijitSplitterActive");

            //Performance: load data info local vars for onmousevent function closure
            var factor = this._factor,
                max = this._maxSize,
                min = this._minSize || 10;
            var axis = this.horizontal ? "pageY" : "pageX";
            var pageStart = e[axis];
            var splitterStyle = this.domNode.style;
            var dim = this.horizontal ? 'h' : 'w';
            var childStart = dojo.marginBox(this.child.domNode)[dim];
            var splitterStart = parseInt(this.domNode.style[this.region]);
            var resize = this._resize;
            var region = this.region;
            var mb = {};
            var childNode = this.child.domNode;
            var layoutFunc = dojo.hitch(this.container, this.container._layoutChildren);

            var de = dojo.doc.body;
            this._handlers = (this._handlers || []).concat([
                dojo.connect(de, "ontouchmove", this._drag = function(e, forceResize){
                    var delta = e[axis] - pageStart,
                        childSize = factor * delta + childStart,
                        boundChildSize = Math.max(Math.min(childSize, max), min);

                    if(resize || forceResize){
                        mb[dim] = boundChildSize;
                        // TODO: inefficient; we set the marginBox here and then immediately layoutFunc() needs to query it
                        dojo.marginBox(childNode, mb);
                        layoutFunc(region);
                    }
                    splitterStyle[region] = factor * delta + splitterStart + (boundChildSize - childSize) + "px";
                }),
                dojo.connect(de, "ontouchend", this, "_stopDrag")
            ]);
            dojo.stopEvent(e);
        };
    },
    patch_moveable:function(){
        dojo.require("dojo.dnd.Moveable")
        var pr=dojo.dnd.Moveable.prototype
        pr._constructor = function(node, params){
        		// summary: an object, which makes a node moveable
        		// node: Node: a node (or node's id) to be moved
        		// params: Object: an optional object with additional parameters;
        		//	following parameters are recognized:
        		//		handle: Node: a node (or node's id), which is used as a mouse handle
        		//			if omitted, the node itself is used as a handle
        		//		delay: Number: delay move by this number of pixels
        		//		skip: Boolean: skip move of form elements
        		//		mover: Object: a constructor of custom Mover
        		this.node = dojo.byId(node);
        		if(!params){ params = {}; }
        		this.handle = params.handle ? dojo.byId(params.handle) : null;
        		if(!this.handle){ this.handle = this.node; }
        		this.delay = params.delay > 0 ? params.delay : 0;
        		this.skip  = params.skip;
        		this.mover = params.mover ? params.mover : dojo.dnd.Mover;
        		this.events = [
        			dojo.connect(this.handle, "ontouchstart", this, "onMouseDown"),
        			// cancel text selection and text dragging
        			dojo.connect(this.handle, "ondragstart",   this, "onSelectStart"),
        			dojo.connect(this.handle, "onselectstart", this, "onSelectStart")
        		];
        };
        pr.onMouseDown= function(e){
        	// summary: event processor for onmousedown, creates a Mover for the node
        	// e: Event: mouse event
        	if(this.skip && dojo.dnd.isFormElement(e)){ return; }
        	if(this.delay){
        		this.events.push(dojo.connect(this.handle, "ontouchmove", this, "onMouseMove"));
        		this.events.push(dojo.connect(this.handle, "ontouchend", this, "onMouseUp"));
        		this._lastX = e.pageX;
        		this._lastY = e.pageY;
        	}else{
        		new this.mover(this.node, e, this);
            }
            if(e.type!='touchstart'){
                dojo.stopEvent(e);
            }
        };

        
        dojo.require("dojo.dnd.Mover");
        var pr=dojo.dnd.Mover.prototype
    	pr._constructor= function(node, e, host){
    		// summary: an object, which makes a node follow the mouse, 
    		//	used as a default mover, and as a base class for custom movers
    		// node: Node: a node (or node's id) to be moved
    		// e: Event: a mouse event, which started the move;
    		//	only pageX and pageY properties are used
    		// host: Object?: object which implements the functionality of the move,
    		//	 and defines proper events (onMoveStart and onMoveStop)
    		this.node = dojo.byId(node);
    		this.marginBox = {l: e.pageX, t: e.pageY};
    		this.mouseButton = e.button;
    		var h = this.host = host, d = node.ownerDocument, 
    			firstEvent = dojo.connect(d, "ontouchmove", this, "onFirstMove");
    		this.events = [
    			dojo.connect(d, "ontouchmove", this, "onMouseMove"),
    			dojo.connect(d, "ontouchend",   this, "onMouseUp"),
    			// cancel text selection and text dragging
    			dojo.connect(d, "ondragstart",   dojo, "stopEvent"),
    			dojo.connect(d, "onselectstart", dojo, "stopEvent"),
    			firstEvent
    		];
    		// notify that the move has started
    		if(h && h.onMoveStart){
    			h.onMoveStart(this);
    		}
    	}
        
        
    }
    
});