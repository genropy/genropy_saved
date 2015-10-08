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
    }
});