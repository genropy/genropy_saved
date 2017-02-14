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

dojo.declare("gnr.GnrSharedObjectHandler", null, {
    constructor: function(application ) {
        this.application = application;
        this.lockedPaths={}
    },
   
    do_sharedObjectChange:function(data){
        var shared_id = data.getItem('shared_id');
        var path = data.getItem('path');
        var value = data.getItem('value');
        var attr = data.getItem('attr');
        if(attr && attr instanceof gnr.GnrBag){
            attr = attr.asDict();
        }
        var evt = data.getItem('evt');
        var fired = data.getItem('fired');

        var from_page_id = data.getItem('from_page_id');
        var so = genro._sharedObjects[shared_id];
        if(!so){
            return;
        }
        var sopath = so.path;
        var fullpath = path? sopath+ '.' +path: sopath;
        if(evt=='del'){
            genro._data.popNode(fullpath,'serverChange');
        }else{
            if(fired){
                genro._data.fireItem(fullpath,value,attr,'serverChange');
            }else{
                genro._data.setItem(fullpath, value, attr, objectUpdate({'doTrigger':'serverChange',lazySet:true}));
            }
            
        }
    },


    registerSharedObject:function(path,shared_id,kw){
        kw = kw || {};
        var on_unregistered = objectPop(kw,'on_unregistered');
        var on_registered = objectPop(kw,'on_registered');

        var that =this;
        if(!(shared_id in genro._sharedObjects)){
            genro._sharedObjects[shared_id] = {shared_id:shared_id,path:path,ready:false, on_unregistered:on_unregistered};
            var onResult = function(resultNode){
                var data = resultNode.getValue();
                genro.som.do_sharedObjectChange(data);
                var privilege = data.getItem('privilege');
                var so = genro._sharedObjects[shared_id];
                var innerPath = data.getItem('path');
                so.ready = true;
                so.privilege = privilege;
                genro._sharedObjects_paths[path] = shared_id; //in this way trigger are activated
                genro.publish('shared_'+shared_id,{ready:true,privilege:privilege});
                var sharedValuePath=function(domnode,path){
                    var sourceNode=genro.dom.getSourceNode(domnode);
                    if (sourceNode && sourceNode.attr.value){
                        var valuePath=sourceNode.absDatapath(sourceNode.attr.value)
                        if (valuePath.indexOf(path)===0){
                            return valuePath;
                        }
                    }
                      
                }
                window.addEventListener("focus", function(e){
                    var curr_path=sharedValuePath(e.target,path)
                    if (curr_path){
                            genro.wsk.send('som.onPathFocus',{shared_id:shared_id,curr_path:curr_path,focused:true});                        
                    }
                 },true)
                 window.addEventListener("blur", function(e){
                     var curr_path=sharedValuePath(e.target,path)
                     if (curr_path){
                         genro.wsk.send('som.onPathFocus',{shared_id:shared_id,curr_path:curr_path,focused:false});
                     }
                  },true)
                if (on_registered){
                    on_registered(shared_id);
                }
            }
            genro.wsk.call(objectUpdate({command:'som.subscribe',
                            shared_id:shared_id, _onResult:onResult},kw));
        }else{
            console.warn('shared_id',shared_id,'is already subscribed')
        }
    },
    
    unregisterSharedObject:function(shared_id){
        if(shared_id in genro._sharedObjects){
            genro.wsk.call({command:'som.unsubscribe',shared_id:shared_id,
                            _onResult:function(){
                                var so = objectPop(genro._sharedObjects,shared_id);
                                objectPop(genro._sharedObjects_paths,so.path);
                                if(so.on_unregistered){
                                    so.on_unregistered(shared_id)
                                }
                            }
            });
        }
    },

    saveSharedObject:function(shared_id){
        genro.wsk.call({command:'som.saveSharedObject',shared_id:shared_id,
                            _onResult:function(){
                                console.log('saved saveSharedObject',shared_id);
                            }
        });
    },

    loadSharedObject:function(shared_id){
        genro.wsk.call({command:'som.loadSharedObject',shared_id:shared_id,
                            _onResult:function(){
                                console.log('loaded loadSharedObject',shared_id);
                            }
        });
    },
    do_onPathLock:function(data){
        var lock_path = data.getItem('lock_path');
        var locked = data.getItem('locked');
        var user = data.getItem('user');
        if (locked){
            genro.som.lockedPaths[lock_path]=user
        }else{
            delete(genro.som.lockedPaths[lock_path])
        }
        var lockedNode=genro.src.getSource().walk(function(n){
            if (n instanceof gnr.GnrDomSourceNode){
                var p=n.absDatapath(n.attr.value);
                if (p==lock_path){
                    return n
                }
            }
        },'static')
        if (lockedNode){
            lockedNode.setDisabled(locked)
        }
    }

});
