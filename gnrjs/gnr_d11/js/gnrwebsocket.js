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

dojo.declare("gnr.GnrWebSocketHandler", null, {
    constructor: function(application, wsroot, options) {
        this.application = application;
        this.wsroot=wsroot;
        this.url=(window.location.protocol=='https:'?'wss://':'ws://')+window.location.host+wsroot;
        this.options=objectUpdate({ debug: false, reconnectInterval: 4000, ping_time:1000 },
                                  options);
        this.waitingCalls={};
        
    },
    create:function(){
        if (this.wsroot){
            this.socket=new ReconnectingWebSocket(this.url, null,this.options);
            var that=this;
            this.socket.onopen=function(){
                that.onopen();
            };
            this.socket.onclose=function(){
                that.onclose();
            };
            this.socket.onmessage=function(e){
                that.onmessage(e);
            };
            this.socket.onerror=function(error){
                that.onerror(error);
            };
        }
        
    },

    addhandler:function(name,cb){
        this[name] = cb;
    },

    onopen:function(){
        that=this;
        this.send('connected',{'page_id':genro.page_id});
        this._interval=setInterval(function(){
                                     genro.wsk.ping();
                                   },this.options.ping_time);
    },
    onclose:function(){
        clearInterval(this._interval);
        console.log('disconnected websocket');
    },
    onerror:function(error){
        console.error('WebSocket Error ' + error);
    },
    ping:function(){
        this.send('ping',{lastEventAge:(new Date()-genro._lastUserEventTs)});
    },

    onmessage:function(e){
        var data=e.data;
        if (data=='pong'){
            return;
        }
        
        if (data.indexOf('<?xml')==0){
            var result=this.parseResponse(e.data);
            var token=result.getItem('token') 
            if (token){
                this.receivedToken(token,result.getItem('envelope'))
            }else{
                this.receivedCommand(result.getItem('command'),result.getItem('data'))
            }
        }else{
            genro.publish('websocketMessage',data)
        }
    },
    receivedCommand:function(command,data){
        var handler;
        if (command){
            if (command.indexOf('.')>0){
                comlst=command.split('.')
                handler=genro[comlst[0]]['do_'+comlst.splice(1).join('.')]
            }
            else{
                handler=this['do_'+command] || this.do_publish
            }
        }else{
            handler=this.do_publish
        }
        handler.apply(this,[data])
    },
    receivedToken:function(token,envelope){
        var deferred=objectPop(this.waitingCalls,token);
        envelope = envelope || new gnr.GnrBag();
        var dataNode = envelope.getNode('data');
        var error = envelope.getItem('error');
        if (error){
            deferred.callback({'error':error,'dataNode':dataNode});
        }
        else{
            deferred.callback(dataNode);
        }
    
   },
    do_alert:function(data){
        alert(data)
    },
    do_set:function(data){
        var path=data.getItem('path')
        var valueNode=data.getNode('data')
        var fired=data.getItem('fired')
        genro.setData(path,valueNode._value,valueNode.attr, true)
        if (fired){
            genro.setData(path,null,null,false)
        }
        
    },

    do_setInClientData:function(data){
        var value = data.getItem('value');
        var attributes = data.getItem('attributes');
        if(attributes){
            attributes = attributes.asDict();
        }
        var path = data.getItem('path');
        var reason = data.getItem('reason');
        var fired = data.getItem('fired');
        var nodeId = data.getItem('nodeId');
        var noTrigger = data.getItem('noTrigger');
        var root = nodeId? genro.nodeById(nodeId):genro.src.getNode();
        root.setRelativeData(path,value,attributes,fired,reason,null,noTrigger?{doTrigger:false}:null)
    },

    do_datachanges:function(datachanges){
        genro.rpc.setDatachangesInData(datachanges)
    },

    do_sharedObjectChange:function(data){
        var shared_id = data.getItem('shared_id');
        var path = data.getItem('path');
        var value = data.getItem('value');
        var attr = data.getItem('attr');
        var evt = data.getItem('evt');
        var from_page_id = data.getItem('from_page_id');
        var so = genro._sharedObjects[shared_id];
        if(!so){
            return;
        }
        var sopath = so.path;
        var fullpath = path? sopath+ '.' +path: sopath;
        if(evt=='del'){
            genro._data.popNode(fullpath,'serverChange')
        }else{
            genro._data.setItem(fullpath, value, attr, objectUpdate({'doTrigger':'serverChange',lazySet:true}));
        }
    },

    do_publish:function(data){
        var topic=data.getItem('topic')
        var nodeId = data.pop('nodeId');
        var iframe = data.pop('iframe');
        var parent = data.pop('parent');
        if (!topic){
            topic='websocketMessage';
        }else{
            var data = data.getItem('data');
            if(data instanceof gnr.GnrBag){
                data = data.asDict();
            }
        }
        if(nodeId || iframe || parent){
            topic = {topic:topic,nodeId:nodeId,iframe:iframe,parent:parent};
        }
        genro.publish(topic,data)
    },
    call:function(kw,omitSerialize,cb){
        var deferred = new dojo.Deferred();
        var kw= objectUpdate({},kw);
        var _onResult = objectPop(kw,'_onResult');
        var _onError = objectPop(kw,'_onError');
        var token='wstk_'+genro.getCounter('wstk');
        kw['result_token']=token;
        kw['command']= kw['command'] || 'call';
        if (!omitSerialize){
            kw=genro.rpc.serializeParameters(genro.src.dynamicParameters(kw));
        }
        this.waitingCalls[token] = deferred;
        //console.log('sending',kw)
        this.socket.send(dojo.toJson(kw));
        deferred.addCallback(function(result){
            if(result && result.error){
                if(_onError){
                    funcApply(_onError,{result:result});
                }else{
                    console.error('WSK ERROR',result.error);
                    genro.setData('gnr.wsk.lastErrorTraceback',result.dataNode);
                    genro.dev.openBagInspector('gnr.wsk.lastErrorTraceback',{title:'WSK error'});
                    //console.log('ERROR TRACEBACK',result.dataNode.getValue());
                }
            }
            return result;
        });
        if(_onResult){
            deferred.addCallback(_onResult);
        }
        return deferred;
    },
    send:function(command,kw){
        var kw=kw || {};
        kw['command']=command
        kw=genro.rpc.serializeParameters(genro.src.dynamicParameters(kw));
        var msg = dojo.toJson(kw);
        this.socket.send(msg);
    },
    
    parseResponse:function(response){
        var result = new gnr.GnrBag();
        var parser=new window.DOMParser()
        result.fromXmlDoc(parser.parseFromString(response, "text/xml")
                                            ,genro.clsdict);
        return result
    },
    
    sendCommandToPage:function(page_id,command,data){
        var envelope=new gnr.GnrBag({'command':command,'data':data})
         this.send('route',{'target_page_id':page_id,'envelope':envelope.toXml()})
    },
    setInClientData:function(page_id,path,data){
        this.sendCommandToPage(page_id,'set',new gnr.GnrBag({'data':data,'path':path}))
    },
    fireInClientData:function(page_id,path,data){
        this.sendCommandToPage(page_id,'set',new gnr.GnrBag({'data':data,'path':path,'fired':true}))
    },
    publishToClient:function(page_id,topic,data){
        this.sendCommandToPage(page_id,'publish',new gnr.GnrBag({'data':data,'topic':topic}))
    },
    errorHandler:function(error){
        console.log('wsk errorHandler',error)
    }
});

// MIT License:
//
// Copyright (c) 2010-2012, Joe Walnes
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

/**
 * This behaves like a WebSocket in every way, except if it fails to connect,
 * or it gets disconnected, it will repeatedly poll until it successfully connects
 * again.
 *
 * It is API compatible, so when you have:
 *   ws = new WebSocket('ws://....');
 * you can replace with:
 *   ws = new ReconnectingWebSocket('ws://....');
 *
 * The event stream will typically look like:
 *  onconnecting
 *  onopen
 *  onmessage
 *  onmessage
 *  onclose // lost connection
 *  onconnecting
 *  onopen  // sometime later...
 *  onmessage
 *  onmessage
 *  etc...
 *
 * It is API compatible with the standard WebSocket API, apart from the following members:
 *
 * - `bufferedAmount`
 * - `extensions`
 * - `binaryType`
 *
 * Latest version: https://github.com/joewalnes/reconnecting-websocket/
 * - Joe Walnes
 *
 * Syntax
 * ======
 * var socket = new ReconnectingWebSocket(url, protocols, options);
 *
 * Parameters
 * ==========
 * url - The url you are connecting to.
 * protocols - Optional string or array of protocols.
 * options - See below
 *
 * Options
 * =======
 * Options can either be passed upon instantiation or set after instantiation:
 *
 * var socket = new ReconnectingWebSocket(url, null, { debug: true, reconnectInterval: 4000 });
 *
 * or
 *
 * var socket = new ReconnectingWebSocket(url);
 * socket.debug = true;
 * socket.reconnectInterval = 4000;
 *
 * debug
 * - Whether this instance should log debug messages. Accepts true or false. Default: false.
 *
 * automaticOpen
 * - Whether or not the websocket should attempt to connect immediately upon instantiation. The socket can be manually opened or closed at any time using ws.open() and ws.close().
 *
 * reconnectInterval
 * - The number of milliseconds to delay before attempting to reconnect. Accepts integer. Default: 1000.
 *
 * maxReconnectInterval
 * - The maximum number of milliseconds to delay a reconnection attempt. Accepts integer. Default: 30000.
 *
 * reconnectDecay
 * - The rate of increase of the reconnect delay. Allows reconnect attempts to back off when problems persist. Accepts integer or float. Default: 1.5.
 *
 * timeoutInterval
 * - The maximum time in milliseconds to wait for a connection to succeed before closing and retrying. Accepts integer. Default: 2000.
 *
 */
(function (global, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module !== 'undefined' && module.exports){
        module.exports = factory();
    } else {
        global.ReconnectingWebSocket = factory();
    }
})(this, function () {

    if (!('WebSocket' in window)) {
        return;
    }

    function ReconnectingWebSocket(url, protocols, options) {

        // Default settings
        var settings = {

            /** Whether this instance should log debug messages. */
            debug: false,

            /** Whether or not the websocket should attempt to connect immediately upon instantiation. */
            automaticOpen: true,

            /** The number of milliseconds to delay before attempting to reconnect. */
            reconnectInterval: 1000,
            /** The maximum number of milliseconds to delay a reconnection attempt. */
            maxReconnectInterval: 30000,
            /** The rate of increase of the reconnect delay. Allows reconnect attempts to back off when problems persist. */
            reconnectDecay: 1.5,

            /** The maximum time in milliseconds to wait for a connection to succeed before closing and retrying. */
            timeoutInterval: 2000,

            /** The maximum number of reconnection attempts to make. Unlimited if null. */
            maxReconnectAttempts: null
        }
        if (!options) { options = {}; }

        // Overwrite and define settings with options if they exist.
        for (var key in settings) {
            if (typeof options[key] !== 'undefined') {
                this[key] = options[key];
            } else {
                this[key] = settings[key];
            }
        }

        // These should be treated as read-only properties

        /** The URL as resolved by the constructor. This is always an absolute URL. Read only. */
        this.url = url;
        this.pendingMessagesToSend=[]
        

        /** The number of attempted reconnects since starting, or the last successful connection. Read only. */
        this.reconnectAttempts = 0;

        /**
         * The current state of the connection.
         * Can be one of: WebSocket.CONNECTING, WebSocket.OPEN, WebSocket.CLOSING, WebSocket.CLOSED
         * Read only.
         */
        this.readyState = WebSocket.CONNECTING;

        /**
         * A string indicating the name of the sub-protocol the server selected; this will be one of
         * the strings specified in the protocols parameter when creating the WebSocket object.
         * Read only.
         */
        this.protocol = null;

        // Private state variables

        var self = this;
        var ws;
        var forcedClose = false;
        var timedOut = false;
        var eventTarget = document.createElement('div');

        // Wire up "on*" properties as event handlers

        eventTarget.addEventListener('open',       function(event) { self.onopen(event); });
        eventTarget.addEventListener('close',      function(event) { self.onclose(event); });
        eventTarget.addEventListener('connecting', function(event) { self.onconnecting(event); });
        eventTarget.addEventListener('message',    function(event) { self.onmessage(event); });
        eventTarget.addEventListener('error',      function(event) { self.onerror(event); });

        // Expose the API required by EventTarget

        this.addEventListener = eventTarget.addEventListener.bind(eventTarget);
        this.removeEventListener = eventTarget.removeEventListener.bind(eventTarget);
        this.dispatchEvent = eventTarget.dispatchEvent.bind(eventTarget);

        /**
         * This function generates an event that is compatible with standard
         * compliant browsers and IE9 - IE11
         *
         * This will prevent the error:
         * Object doesn't support this action
         *
         * http://stackoverflow.com/questions/19345392/why-arent-my-parameters-getting-passed-through-to-a-dispatched-event/19345563#19345563
         * @param s String The name that the event should use
         * @param args Object an optional object that the event will use
         */
        function generateEvent(s, args) {
            var evt = document.createEvent("CustomEvent");
            evt.initCustomEvent(s, false, false, args);
            return evt;
        };

        this.open = function (reconnectAttempt) {
            ws = new WebSocket(self.url, protocols || []);

            if (reconnectAttempt) {
                if (this.maxReconnectAttempts && this.reconnectAttempts > this.maxReconnectAttempts) {
                    return;
                }
            } else {
                eventTarget.dispatchEvent(generateEvent('connecting'));
                this.reconnectAttempts = 0;
            }

            if (self.debug || ReconnectingWebSocket.debugAll) {
                console.debug('ReconnectingWebSocket', 'attempt-connect', self.url);
            }

            var localWs = ws;
            var timeout = setTimeout(function() {
                if (self.debug || ReconnectingWebSocket.debugAll) {
                    console.debug('ReconnectingWebSocket', 'connection-timeout', self.url);
                }
                timedOut = true;
                localWs.close();
                timedOut = false;
            }, self.timeoutInterval);

            ws.onopen = function(event) {
                clearTimeout(timeout);
                if (self.debug || ReconnectingWebSocket.debugAll) {
                    console.debug('ReconnectingWebSocket', 'onopen', self.url);
                }
                self.protocol = ws.protocol;
                self.readyState = WebSocket.OPEN;
                self.reconnectAttempts = 0;
                var e = generateEvent('open');
                e.isReconnect = reconnectAttempt;
                reconnectAttempt = false;
                eventTarget.dispatchEvent(e);
                while (self.pendingMessagesToSend.length>0){
                    console.log('send pending')
                    self.send(self.pendingMessagesToSend.shift())
                }
            };

            ws.onclose = function(event) {
                clearTimeout(timeout);
                ws = null;
                if (forcedClose) {
                    self.readyState = WebSocket.CLOSED;
                    eventTarget.dispatchEvent(generateEvent('close'));
                } else {
                    self.readyState = WebSocket.CONNECTING;
                    var e = generateEvent('connecting');
                    e.code = event.code;
                    e.reason = event.reason;
                    e.wasClean = event.wasClean;
                    eventTarget.dispatchEvent(e);
                    if (!reconnectAttempt && !timedOut) {
                        if (self.debug || ReconnectingWebSocket.debugAll) {
                            console.debug('ReconnectingWebSocket', 'onclose', self.url);
                        }
                        eventTarget.dispatchEvent(generateEvent('close'));
                    }

                    var timeout = self.reconnectInterval * Math.pow(self.reconnectDecay, self.reconnectAttempts);
                    setTimeout(function() {
                        self.reconnectAttempts++;
                        self.open(true);
                    }, timeout > self.maxReconnectInterval ? self.maxReconnectInterval : timeout);
                }
            };
            ws.onmessage = function(event) {
                if (self.debug || ReconnectingWebSocket.debugAll) {
                    console.debug('ReconnectingWebSocket', 'onmessage', self.url, event.data);
                }
                var e = generateEvent('message');
                e.data = event.data;
                eventTarget.dispatchEvent(e);
            };
            ws.onerror = function(event) {
                if (self.debug || ReconnectingWebSocket.debugAll) {
                    console.debug('ReconnectingWebSocket', 'onerror', self.url, event);
                }
                eventTarget.dispatchEvent(generateEvent('error'));
            };
        }

        // Whether or not to create a websocket upon instantiation
        if (this.automaticOpen == true) {
            this.open(false);
        }

        /**
         * Transmits data to the server over the WebSocket connection.
         *
         * @param data a text string, ArrayBuffer or Blob to send to the server.
         */
        this.send = function(data) {
            if (ws) {
                if (self.debug || ReconnectingWebSocket.debugAll) {
                    console.debug('ReconnectingWebSocket', 'send', self.url, data);
                }
                return ws.send(data);
            } else {
                console.log('socket not ready - adding to queue')
                this.pendingMessagesToSend.push(data)
                //console.log ('Error sending :',data);
                //throw 'INVALID_STATE_ERR : Pausing to reconnect websocket'
            }
        };

        /**
         * Closes the WebSocket connection or connection attempt, if any.
         * If the connection is already CLOSED, this method does nothing.
         */
        this.close = function(code, reason) {
            // Default CLOSE_NORMAL code
            if (typeof code == 'undefined') {
                code = 1000;
            }
            forcedClose = true;
            if (ws) {
                ws.close(code, reason);
            }
        };

        /**
         * Additional public API method to refresh the connection if still open (close, re-open).
         * For example, if the app suspects bad data / missed heart beats, it can try to refresh.
         */
        this.refresh = function() {
            if (ws) {
                ws.close();
            }
        };
    }

    /**
     * An event listener to be called when the WebSocket connection's readyState changes to OPEN;
     * this indicates that the connection is ready to send and receive data.
     */
    ReconnectingWebSocket.prototype.onopen = function(event) {};
    /** An event listener to be called when the WebSocket connection's readyState changes to CLOSED. */
    ReconnectingWebSocket.prototype.onclose = function(event) {};
    /** An event listener to be called when a connection begins being attempted. */
    ReconnectingWebSocket.prototype.onconnecting = function(event) {};
    /** An event listener to be called when a message is received from the server. */
    ReconnectingWebSocket.prototype.onmessage = function(event) {};
    /** An event listener to be called when an error occurs. */
    ReconnectingWebSocket.prototype.onerror = function(event) {};

    /**
     * Whether all instances of ReconnectingWebSocket should log debug messages.
     * Setting this to true is the equivalent of setting all instances of ReconnectingWebSocket.debug to true.
     */
    ReconnectingWebSocket.debugAll = false;

    ReconnectingWebSocket.CONNECTING = WebSocket.CONNECTING;
    ReconnectingWebSocket.OPEN = WebSocket.OPEN;
    ReconnectingWebSocket.CLOSING = WebSocket.CLOSING;
    ReconnectingWebSocket.CLOSED = WebSocket.CLOSED;

    return ReconnectingWebSocket;
});