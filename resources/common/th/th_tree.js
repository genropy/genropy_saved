var THTree = {
    refreshTree:function(dbChanges,store,treeNode,rootIdentifier){
        treeNode.widget.saveExpanded();
        var selectedNode = treeNode.widget.currentSelectedNode;
        var selectedIdentifier = selectedNode? selectedNode.item.attr.treeIdentifier:'';       
        var refreshDict = {};
        var n;
        var that = this;
        var table = store.getParentNode().attr.table;
        var dbevent;
        rootIdentifier = rootIdentifier || '_root_';
        dojo.forEach(dbChanges,function(c){
            dbevent = c.dbevent;
            if(dbevent=='D'){
                selectedIdentifier = c.parent_id || rootIdentifier;
            }
            refreshDict[c.parent_id || rootIdentifier] = true;
            if(c.old_parent_id != c.parent_id){
                refreshDict[c.old_parent_id || rootIdentifier] = true;
            }            
        });
        var refreshed = {};
        for (var k in refreshDict){
            if (k=='_forest_'){
                n = store.getParentNode();
            }else{
                n = store.getNodeByAttr('treeIdentifier',k);
            }
            if(n && !(n.attr.treeIdentifier in refreshed)){
                if(n.getResolver()){
                    n.refresh(true)
                    refreshed[n.attr.treeIdentifier] = true;
                    content = n.getValue();
                    child_count = (content instanceof gnr.GnrBag)?content.len():0;
                    n.updAttributes({'child_count':child_count});
                }else{
                    n = n.getParentNode();
                    if(n && n.getResolver() && !(n.attr.treeIdentifier in refreshed)){
                        n.refresh(true);
                        refreshed[n.attr.treeIdentifier] = true;
                    }
                }
            }          
            }
        treeNode.widget.restoreExpanded();
        if(selectedIdentifier && dbevent!='I'){
            var treeWdg = treeNode.widget;
            var fullpath = this.fullPathByIdentifier(treeWdg,selectedIdentifier);
            if(fullpath=='root' && rootIdentifier=='_forest_'){
                var firstNode = store.getNode('#0');
                if(firstNode){
                    fullpath = firstNode.attr.pkey;
                }else{
                    fullpath = null;
                }
            }
            treeWdg.setSelectedPath(null,{value:fullpath});    
        }
    },

    fullPathByIdentifier:function(tree,pkey){
        var store = tree.storebag();
        var n = store.getNodeByAttr('treeIdentifier',pkey);
        if(n){
            return n.getFullpath(null, tree.model.store.rootData());
        }else{
            var storeNode = store.getParentNode();
            var inattr = storeNode.getInheritedAttributes();
            return genro.serverCall('_table.'+inattr['table']+'.pathFromPkey',{pkey:pkey,dbstore:inattr['dbstore']});
        }
    },

    dropTargetCbOnSelf:function(sourceNode,dropInfo){
        var pkey = dropInfo.treeItem.attr.pkey;
        var dataTransfer = dropInfo.event.dataTransfer;
        var nodeattr = genro.dom.getFromDataTransfer(dataTransfer,'nodeattr');
        var dragged_record = convertFromText(nodeattr);
        var draggedNode = sourceNode.widget.storebag().getNodeByAttr('pkey',dragged_record.pkey);
        var dropNode = dropInfo.treeItem;
        if(!draggedNode){
            console.log('Resolver damaged');
            return false;
        }
        if(draggedNode.isAncestor(dropNode)){
            return false;
        }
        var ondrop_record = dropNode.attr;
        var ondrop_pkey = ondrop_record.pkey;
        var drop_fullrec = ondrop_record._record || {};
        var drag_fullrec = dragged_record._record || {};
        if((drop_fullrec._virtual_node || false) !== (drag_fullrec._virtual_node || false) ){
            return false;
        }
        return (ondrop_pkey!=dragged_record.pkey && dragged_record.parent_id != ondrop_pkey);
    },
    
    dropTargetCb:function(sourceNode,dropInfo){
        if((sourceNode._id==dropInfo.dragSourceInfo._id) && (dropInfo.dragSourceInfo.page_id == genro.page_id)){
            return this.dropTargetCbOnSelf(sourceNode,dropInfo)
        }else{
            return true;
        }
        
    },

    onPickerDrop:function(sourceNode,data,dropInfo,kw){
        if(sourceNode.form.isNewRecord() || sourceNode.form.locked ){
            return false;
        }
        var types = [];
        if(data instanceof Array){
            dojo.forEach(data,function(n){types.push(n._pkey)})
            }else{
                types[0] = data['pkey'];
            }
            var onResult = function(result){
                sourceNode.setRelativeData('.tree.path','_root_.'+result);
            }
            var cb = objectPop(kw,'customCb');
            cb = cb || function(count){
                genro.serverCall('ht_htreeCreateChildren',{types:types,parent_id:dropInfo.treeItem.attr.pkey,
                                type_field:kw.type_field,maintable:kw.maintable,typetable:kw.typetable,how_many:count},onResult,null,'POST');
            }
        if(dropInfo.modifiers=='Shift'){
            genro.dlg.prompt("How Many",{msg:'How many copies do you want to insert?',widget:'numberTextBox',action:cb});
        }else{
            cb();
        }
    }
};
var THTreeRelatedTableHandler = {
    onRelatedRow:function(r,curr_hfkey,alt_relations){
        var result = [];
        if(r.one_hpkey == curr_hfkey){
            return;
        }
        if(r.one_hpkey && r.one_hpkey.indexOf(curr_hfkey)==0){
            r['_hieararchical_inherited'] = true;
            return '_hieararchical_inherited';
        }
        if(alt_relations){
            alt_relations = objectUpdate({},alt_relations);
            var curr_hfkey_list = curr_hfkey.split('/');
            var currpkey = curr_hfkey_list[curr_hfkey_list.length-1];
            var alt_relations_result = []
            for (var k in alt_relations){
                if(r[alt_relations[k]['fkey_name']]==currpkey){
                    r['_altrelation_'+k] = true;
                    alt_relations_result.push(alt_relations[k]['_class'] || '_altrelation_'+k)
                }
            }
            if(alt_relations_result.length){
                return alt_relations_result.join(' ');
            }
        }
        if(r.many_hpkey==curr_hfkey){
            if(r.one_hpkey){
                r['_alias_row'] = true;
                return '_alias_row'; 
            }else{
                return;
            }
        }else if(r.many_hpkey && r.many_hpkey.indexOf(curr_hfkey)==0){
            r['_hieararchical_inherited'] = true;
            if(r.one_hpkey){
                r['_alias_row'] = true;
                return '_alias_row _hieararchical_inherited'
            }else{
                return '_hieararchical_inherited';
            }
        }
    }
}