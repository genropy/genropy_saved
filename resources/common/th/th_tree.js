var THTree = {
    refreshTree:function(dbChanges,store,treeNode,rootIdentifier){
        treeNode.widget.saveExpanded();
        var selectedNode = treeNode.widget.currentSelectedNode
        var selectedIdentifier = selectedNode? selectedNode.item.attr.treeIdentifier:'';       
        var refreshDict = {};
        var n;
        var that = this;
        var table = store.getParentNode().attr.table;
        var dbevent;
        var rootIdentifier = rootIdentifier || '_root_';
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
            n = store.getNodeByAttr('treeIdentifier',k);
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
        var p;
        if(selectedIdentifier && dbevent!='I'){
            var n = store.getNodeByAttr('treeIdentifier',selectedIdentifier);
            if(n){
                p = n.getFullpath(null, treeNode.widget.model.store.rootData());
                treeNode.widget.setSelectedPath(null,{value:p});
            }else{
                p = genro.serverCall('ht_pathFromPkey',{pkey:selectedIdentifier,table:table});
                if(p){
                    treeNode.widget.setSelectedPath(null,{value:'root.'+p});
                }
            }
            
        }
    },
    dropTargetCb:function(sourceNode,dropInfo){
        var pkey = dropInfo.treeItem.attr.pkey;
        var dataTransfer = dropInfo.event.dataTransfer;
        var nodeattr = genro.dom.getFromDataTransfer(dataTransfer,'nodeattr');
        if (!nodeattr){
            return false;
        }
        var dragged_record = convertFromText(nodeattr);
        var draggedNode = sourceNode.getRelativeData('.store').getNodeByAttr('pkey',dragged_record.pkey);
        var dropNode = dropInfo.treeItem;
        if(!draggedNode){
            console.log('Resolver damaged')
            return false;
        }
        if(draggedNode.isAncestor(dropNode)){
            return false;
        }
        var ondrop_record = dropNode.attr;
        var ondrop_pkey = ondrop_record.pkey;
        return (ondrop_pkey!=dragged_record.pkey && dragged_record.parent_id != ondrop_pkey);
    }
    
};