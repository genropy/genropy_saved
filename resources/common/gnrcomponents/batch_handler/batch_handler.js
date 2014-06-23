var batch_monitor = {};

batch_monitor.owner_page_batch = function(batch_id) {
    if(genro.nodeById('bm_local_rootnode')){
        var batchBag = genro.getData(this.batchpath(batch_id))
        if (batchBag){
            return  (genro.page_id == batchBag.getItem('owner_page_id'))
        }
    }
   
};

batch_monitor.on_datachange = function(kw) {
    if (!kw.reason) {
        //genro.bp(kw);
        return;
    }
    var callname = 'on_' + kw.reason;
    var node = kw.node;
    if (callname in batch_monitor) {
        var batch_id = node.attr.batch_id || node.label;
        if(!node.attr.userBatch){
            var sourceNode = this.get_batch_sourceNode(batch_id);
             if (sourceNode) {
                 this[callname].call(this, node, sourceNode);
             }
        }
        if (this.owner_page_batch(batch_id)) {
                var sourceNode = this.get_batch_sourceNode(batch_id, true);
                if (sourceNode) {
                    this[callname].call(this, node, sourceNode);
                }
        }
    }
};


batch_monitor.create_local_root = function(sync) {
    if(sync){
        localRoot = genro.dlg.quickDialog('Local Batch',{nodeId:'localBatches_root'});
        localRoot.center._('div',{nodeId:'bm_local_rootnode',height:'85px',width:'200px',overflow_x:'hidden'});
        localRoot.show_action();
        return;
    }
    var paletteBtc = genro.wdgById('localBatches_floating');
    if(!paletteBtc){
        genro.src.getNode()._('div', '_devBtcRoot_');
        var node = genro.src.getNode('_devBtcRoot_').clearValue();
        node.freeze();
        var paletteBtc = node._('palettePane',{'paletteCode':'localBatches',
                                                    title:'Local batches',
                                                    dockTo:false,
                                                    width:'200px',
                                                    height:'250px',
                                                    selfsubscribe_showing:function(){
                                                        genro.publish('batch_monitor_on');
                                                    },
                                                    selfsubscribe_hiding:function(){
                                                        genro.publish('batch_monitor_off');
                                                    }});
    
        paletteBtc._('div',{nodeId:'bm_local_rootnode',height:'100%',overflow_x:'hidden'});
        node.unfreeze();
    }else{
        paletteBtc.show();
    }
};

batch_monitor.get_batch_sourceNode = function(batch_id, local) {
    var batch_sourceNode_id = 'batch_' + batch_id;
    var container_id = 'bm_rootnode';
    if (local) {
        batch_sourceNode_id = batch_sourceNode_id + '_local';
        container_id = 'bm_local_rootnode';
    }
    var sourceNode = genro.nodeById(batch_sourceNode_id);
    if (!sourceNode) {
        var container_node = genro.nodeById(container_id);
        if (container_node) {
            sourceNode = this.batch_sourceNode_create(container_node, batch_id, batch_sourceNode_id);
        }
    }
    if (sourceNode) {
        sourceNode.batch_id = batch_id;
    }
    return sourceNode;
};
batch_monitor.batch_sourceNode_create = function(container_node, batch_id, batch_sourceNode_id) {
    var batchpath = this.batchpath(batch_id);
    var batch_data = genro.getData(batchpath);
    if (!batch_data) {
        return;
    }
    var batchpane = container_node._('div', {datapath:batchpath,nodeId:batch_sourceNode_id,tip:'^.note',
        _class:'bm_batchpane'});
    var titlediv = batchpane._('div', {_class:'bm_batchlabel'});
    titlediv._('div', {innerHTML:'^.title', _class:'bm_batchtitle'});
    var topright = titlediv._('div', {_class:'bm_label_action_link'});
    topright._('a', {innerHTML:'Stop',visible:'^.cancellable',
        href:'#',connect_onclick:function(){
            batch_monitor.batch_ask_stop(batch_id);
        }});
    var thermopane = batchpane._('div', {_class:'bm_contentpane',datapath:'.thermo'});
    var bottompane = batchpane._('div', {_class:'bm_batchbottom'});
    sourceNode = genro.nodeById(batch_sourceNode_id);
    bottompane._('div', {innerHTML:'Started at:' + genro.format(sourceNode.getRelativeData('.start_ts'), {'time':'short'})});
    sourceNode.thermoSourceNode = thermopane.getParentNode();
    sourceNode.thermoSourceNode.thermolines = {};
    sourceNode.toprightSourceNode = topright.getParentNode();
    sourceNode.bottomSourceNode = bottompane.getParentNode();
    return sourceNode;
};

batch_monitor.batch_ask_stop=function(batch_id){
    var batchpath = this.batchpath(batch_id);
    var batch_data = genro.getData(batchpath);
    var msg = "Do you really want to stop the " + batch_data.getItem('title') + " batch?"
    genro.dlg.ask("Stopping batch",
                 msg,null,{
                     confirm:function(){
                         genro.serverCall("btc.abort_batch",{"batch_id":batch_id},function(){
                             genro.serverCall("btc.remove_batch",{"batch_id":batch_id});
                         })
                    }
                 })
}

//batch_monitor.on_btc_end = function(node,sourceNode){
//
//};
batch_monitor.on_btc_result_doc = function(node, sourceNode) {
    batch_monitor.btc_result(node, sourceNode);
};
batch_monitor.on_btc_error_doc = function(node, sourceNode) {
    batch_monitor.btc_result(node, sourceNode);
};

batch_monitor.btc_result = function(node, sourceNode) {
    var batch_id = sourceNode.batch_id;
    var batch_value = node.getValue();
    if(!sourceNode.thermoSourceNode){
        return;
    }
    var resultNode = sourceNode.thermoSourceNode;
    var resultpane = resultNode.getParentBag();
    resultNode.freeze()

    resultNode.clearValue();
    
    sourceNode.thermoSourceNode = null;
    var error = batch_value.getItem('error');
    var toprightNode = sourceNode.toprightSourceNode;
    var topright = toprightNode.getParentBag();
    topright.popNode(toprightNode.label);
    topright._('div', {_class:'buttonIcon icnTabClose bm_label_action_link',
                connect_onclick:function(kw){
                    genro.serverCall("btc.remove_batch",{"batch_id":batch_id,"all_batches":kw.shiftKey});
    }});
    if (error) {
        resultNode._('div', {innerHTML:error});
        return;
    }

    var resultHandlerNode = batch_value.getNode('result');
    var result = resultHandlerNode._value;
    var resultAttr = resultHandlerNode.attr;
    var url =resultAttr.url;
    var url_print = resultAttr.url_print;
    var tbl = resultNode._('table',{'width':'100%',border_spacing:'0',border_collapse:'collapse',text_align:'center'})._('tbody');
    var c1 = tbl._('tr')._('td',{'colspan':2});
    var r2 = tbl._('tr');
    var c21 = r2._('td');
    var c22 = r2._('td');

    if (url || url_print || result) {
        if (result) {
            tbl._('tr')._('td',{'colspan':2})._('div', {innerHTML:result});
        }
        if(resultAttr.document_name){
            tbl._('tr')._('td',{'colspan':2})._('div', {innerHTML:resultAttr.document_name});
        }
        if (url || url_print){
            var rlink = tbl._('tr');
            if (url) {
                rlink._('td',{_class:'bm_resulttd'})._('a',{href:url,display:'inline-block',_class:'bm_resultlink'})._('div')._('div', {_class:'iconbox inbox'});
            }
            if(url_print){
                rlink._('td',{_class:'bm_resulttd'})._('a',{href:url_print,display:'inline-block',_class:'bm_resultlink'})._('div')._('div', {_class:'iconbox print'});
            }
        }
        if (resultAttr.autoDestroy){
            var autoDestroy = resultAttr.autoDestroy * 1000;
            if (autoDestroy<0){
                autoDestroy = 1;
            }
            genro.callAfter(function(){
                genro.serverCall("btc.remove_batch",{"batch_id":batch_id});
            },autoDestroy);
        }
    }
    tbl._('tr')._('td', {innerHTML:'Execution time:' + batch_value.getItem('time_delta'),colspan:2,font_size:'.9em',font_style:'italic'});
    resultNode.unfreeze()

};

batch_monitor.on_btc_error = function(node, sourceNode) {
    sourceNode.setRelativeData('.error', true);
};

batch_monitor.on_btc_aborted = function(node, sourceNode) {
    this.batch_remove(sourceNode);
};
batch_monitor.on_th_cleanup = function(node, sourceNode) {
    genro.bp(node);
};
batch_monitor.on_tl_add = function(node, sourceNode) {
    this.create_thermoline(sourceNode, node.label, node.attr);
};
batch_monitor.on_tl_del = function(node, sourceNode) {
    this.delete_thermoline(sourceNode, node.label);
};

batch_monitor.on_tl_upd = function(node, sourceNode) {
    var last_change = node.attr._change_ts;
    var age = last_change ? (new Date() - last_change) / 1000 : 1000;
    if (false && (age > 300)) {
        var bag_error = new gnr.GnrBag();
        bag_error.setItem('error', 'Timeout');
        bag_error.setItem('time_delta', age);
        node.setValue(bag_error);
        batch_monitor.on_btc_error_doc(node, sourceNode);
    }
};

batch_monitor.on_btc_removed = function(node, sourceNode) {
    this.batch_remove(sourceNode);
};

batch_monitor.batch_remove = function(sourceNode) {
    var batch_id = sourceNode.batch_id;
    genro._data.delItem(this.batchpath(batch_id));
    sourceNode._destroy();
};

batch_monitor.batchpath = function(batch_id) {
    return 'gnr.batch.' + batch_id;
};

batch_monitor.waiting_pane = function(parentId) {

};


batch_monitor.delete_thermoline = function(sourceNode, code) {
    var node = sourceNode.thermoSourceNode.thermolines[code];
    if (node) {
        node._destroy();
    }
};

batch_monitor.create_thermoline = function(sourceNode, line, attributes) {
    var pane = sourceNode.thermoSourceNode;
    var code = line;
    var custom_attr = {};
    if (typeof(line) != 'string') {
        code = objectPop(line, 'code');
        custom_attr = line;
    }
    thermo_class = attributes.thermo_class || '';
    var custom_msg_attr = objectExtract(custom_attr, 'msg_*');
    var innerpane = pane._('div', {datapath:'.' + code});
    pane.thermolines[code] = innerpane.getParentNode();
    //var cb = function(percent){
    //    return line+':'+dojo.number.format(percent, {type: "percent", places: this.places, locale: this.lang});
    //};
    var cb = function(percent) {
        if (!this.domNode) {
            debugger;
        }
        var msg = this.domNode.parentNode.sourceNode.getRelativeData('.?message');
        return msg;
    };
    var thermo_attr = {progress:'^.?progress',maximum:'^.?maximum',indeterminate:'^.?indeterminate',
        _class:'bm_thermoline ' + thermo_class,places:'^.?places',report:cb};
    var msg_attr = {innerHTML:'^.?message',_class:'bm_thermomsg'};
    thermo_attr = objectUpdate(thermo_attr, custom_attr);

    msg_attr = objectUpdate(msg_attr, custom_msg_attr);
    //if (!msg_attr['hidden']){
    //    innerpane._('div',msg_attr);
    //}
    innerpane._('div', {_class:'bm_thermoline_box'})._('progressBar', thermo_attr);

};