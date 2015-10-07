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
        this.initialize();
    },
    initialize:function() {
        dojo.addClass(document.body,'touchDevice')
       //document.body.ontouchmove = function(e) {
       //    //e.preventDefault();
       //};
        this.startHammer(document.body);
        document.body.onorientationchange = function(e) {
            genro.setData('touch.orientation', window.orientation);
        };
       //dojo.connect(document.body, 'gestureend', function(e) {
       //    genro.dom.logTouchEvent('gesture', e);
       //});

        //dojo.connect(document.body, 'touchstart',genro.dom,'touchEvent_start');
        //dojo.connect(document.body, 'touchend',genro.dom,'touchEvent_end');
        //dojo.connect(document.body, 'touchmove',genro.dom,'touchEvent_move');
        //dojo.connect(document.body, 'touchcancel',genro.dom,'touchEvent_cancel');
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

   //connectTouchEvents:function(domNode,touchEvents){
   //    dojo.connect(domNode,'touchstart',this.touchEvent_start);
   //    dojo.connect(domNode,'touchend',this.touchEvent_start);

   //},

   //touchEvent_start:function(e){
   //    console.log('touchEvent_start',e,e.target.id)

   //},

   //touchEvent_end:function(e){
   //    console.log('touchEvent_end',e,e.target.id)

   //},

   //touchEvent_move:function(e){
   //    console.log('touchEvent_move',e,e.target.id)


   //},


   //touchEvent_cancel:function(e){
   //    console.log('touchEvent_cancel',e,e.target.id)

 
   //},
});