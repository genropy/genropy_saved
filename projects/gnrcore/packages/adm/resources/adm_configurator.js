var ConfTreeEditor = {
    selfDragDropTree:function(sourceNode,data,dropInfo){
        if(!dropInfo.selfdrop){
            return;
        }
        var put_before =  dropInfo.treeItem.attr.dtype || dropInfo.modifiers == 'Shift';
        var b = sourceNode.widget.storebag();
        var destpath = dropInfo.treeItem.getFullpath(null,b);
        if(destpath==data){
            return;
        }
        var destNode = b.getNode(destpath);
        var destBag,dragNode,label;
        if(put_before){
            if(destpath=='root'){
                return;
            }
            destBag = destNode.getParentBag();
            dragNode = b.popNode(data);
            destBag.setItem('#id',dragNode,null,{_position:'<'+destNode.label});
        }else{
            destBag = destNode.getValue();
            if(!destBag){
                destBag = new gnr.GnrBag();
                destNode.setValue(destBag);
            }
            dragNode = b.popNode(data);
            destBag.setItem('#id',dragNode);
        }
    }
};


var PermissionComponent = {
    colsPermissionsData:function(data){
        var result = new gnr.GnrBag();
        data.forEach(function(cnode){
            if(!isNullOrBlank(cnode.attr.forbidden) || !isNullOrBlank(cnode.attr.readonly) || !isNullOrBlank(cnode.attr.blurred)){
                result.setItem(cnode.label,null,{forbidden:cnode.attr.forbidden,
                                                readonly:cnode.attr.readonly,
                                                blurred:cnode.attr.blurred,
                                                colname:cnode.label});
            }
        });
        return result;
    }
};