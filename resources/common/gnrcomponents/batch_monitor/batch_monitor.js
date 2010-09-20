var batch_monitor = {};


batch_monitor.on_datachange = function(kw){
    if(!kw.reason){
        genro.bp(kw);
        return;
    }
    var callname = 'on_'+kw.reason;
    var node = kw.node;
    if(callname in batch_monitor){
     this[callname].call(this,node);
    }
}

batch_monitor.on_btc_create = function(node){
    var batch_id = node.label;
    var batch_bag = node.getValue();
    var thermopane = this.create_batchpane(batch_id,batch_bag);
    var lines = batch_bag.getItem('lines');
    if (typeof(lines)=='string') {
        lines = lines.split(',');
    }
    var k=0
    dojo.forEach(lines,function(line){
        batch_monitor.create_thermoline(thermopane,line,k);
        k=k+1;
    });    
};
batch_monitor.on_btc_end = function(node){
   
};
batch_monitor.on_btc_result_doc = function(node){
    var batch_id = node.label;
    var batch_value = node.getValue();
    var resultpane = this.thermopane(node.label);
    resultpane.clearValue().freeze();
    var result = batch_value.getItem('result');
    var url = batch_value.getItem('result?url');
    if (result) {
        resultpane._('div',{innerHTML:result});
    };
    if (url) {
        resultpane._('div')._('a',{href:url,innerHTML:'download'});
    };
    topright = genro.nodeById('bm_top_right_'+batch_id).clearValue();
    topright._('div',{_class:'buttonIcon icnTabClose',connect_onclick:'genro.serverCall("btc.remove_batch",{"batch_id":"'+batch_id+'"})'});
    resultpane._('div',{innerHTML:'Batch completed - total time:'+batch_value.getItem('time_delta')})
    resultpane.unfreeze();
};
batch_monitor.on_btc_error = function(node){
    genro.bp(node);
};
batch_monitor.on_btc_error_doc = function(node){
    genro.bp(node);
};
batch_monitor.on_btc_aborted = function(node){
    this.batch_remove(node.label);
};
batch_monitor.on_th_cleanup = function(node){
    genro.bp(node);
};
batch_monitor.on_tl_start = function(node){
    //genro.bp(node);
};
batch_monitor.on_tl_upd = function(node){
    //genro.bp(node);
};

batch_monitor.on_btc_removed = function(node){
    this.batch_remove(node.label);
};

batch_monitor.batch_remove = function(batch_id){
    this.batchpane(batch_id)._destroy();
    genro._data.delItem(this.batchpath(batch_id));
}

batch_monitor.get_batch_node_id = function(batch_id){
    return 'batch_'+batch_id;
};
batch_monitor.get_batch_thermo_node_id = function(batch_id){
    return 'batch_'+batch_id+'_thermo';
};

batch_monitor.batchpath = function(batch_id){
    return 'gnr.batch.'+batch_id;
};
batch_monitor.batchpane = function(batch_id){
    var node =  genro.nodeById(this.get_batch_node_id(batch_id));
    return node;
};
batch_monitor.thermopane = function(batch_id){
    return genro.nodeById(this.get_batch_thermo_node_id(batch_id));
};

batch_monitor.create_batchpane = function(batch_id,batch_data){
    var batch_node_id = this.get_batch_node_id(batch_id);
    var batchpane = genro.nodeById(batch_node_id);
    var batchpath = this.batchpath(batch_id);
    if (!batchpane){
        var rootNode = genro.nodeById('bm_rootnode');
        batchpane = rootNode._('div',{datapath:batchpath,nodeId:batch_node_id,title:'^.note',
                                    _class:'bm_batchpane'});
        var titlediv = batchpane._('div',{_class:'bm_batchlabel'});
        titlediv._('div',{innerHTML:'^.title', _class:'bm_batchtitle'});
        titlediv._('div',{_class:'bm_label_action_link',nodeId:'bm_top_right_'+batch_id})._('a',{innerHTML:'Stop',
                                                visible:'^.cancellable',
                    href:'javascript:genro.dlg.ask("Stopping batch","Do you want really stop batch"+"'+batch_data.getItem('title')+'"+"?",null,{confirm:function(){genro.serverCall("btc.abort_batch",{"batch_id":"'+batch_id+'"})}})'});
        return batchpane._('div',{_class:'bm_contentpane',datapath:'.thermo',nodeId:this.get_batch_thermo_node_id(batch_id)});
    }
};


batch_monitor.create_thermoline = function(pane,line,k){
    var code = line;
    var custom_attr = {};
    if (typeof(line)!='string') {
        code = objectPop(line,'code');
        custom_attr = line;
    }      
    var custom_msg_attr = objectExtract(custom_attr,'msg_*');
    var innerpane = pane._('div',{datapath:'.'+code});
    var cb = function(percent){
        return line+':'+dojo.number.format(percent, {type: "percent", places: this.places, locale: this.lang});
    };
    var thermo_attr = {progress:'^.?progress',maximum:'^.?maximum',indeterminate:'^.?indeterminate',_class:'bm_thermoline bm_line_'+k,
                     places:'^.?places',report:cb};
    var msg_attr = {innerHTML:'^.?message',_class:'bm_thermomsg'};
    thermo_attr = objectUpdate(thermo_attr,custom_attr);   
    msg_attr = objectUpdate(msg_attr,custom_msg_attr);
    //if (!msg_attr['hidden']){
    //    innerpane._('div',msg_attr);
    //}
    innerpane._('div',{_class:'bm_thermoline_box'})._('progressBar',thermo_attr);
};