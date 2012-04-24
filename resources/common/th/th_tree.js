var THTree = {
    refreshTree:function(dbChanges,store,treeNode){
        treeNode.widget.saveExpanded();
        var selectedNode = treeNode.widget.currentSelectedNode
        var selectedIdentifier = selectedNode? selectedNode.item.attr.treeIdentifier:'';       
        this.refreshDict = {};
        this.store = store;
        var n;
        var that = this;
        dojo.forEach(dbChanges,function(c){
            if(c.parent_id){
                that.addToRefreshDict(c.parent_id)
            }
            if(c.old_parent_id){
                that.addToRefreshDict(c.old_parent_id)
            }
        });
        for (var k in this.refreshDict){
            this.refreshDict[k].refresh(true);
        }
        treeNode.widget.restoreExpanded();
        if(selectedIdentifier){
            var n = this.store.getNodeByAttr('treeIdentifier',selectedIdentifier);
            var p = n.getFullpath(null, treeNode.widget.model.store.rootData());
            if(p){
                treeNode.widget.setSelectedPath(null,{value:p});
            }
        }
    },
    addToRefreshDict:function(parent_id){
        var n = this.store.getNodeByAttr('treeIdentifier',parent_id || '_root_');
        if(n && ! n.getResolver()){
            n = n.getParentNode();
        }
        if(n){
            this.refreshDict[n.getStringId()] = n;
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