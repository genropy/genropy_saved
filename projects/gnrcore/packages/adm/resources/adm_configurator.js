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
        var destBag,dbaglen,dragNode,label;
        if(put_before){
            if(destpath=='root'){
                return;
            }
            destBag = destNode.getParentBag();
            dbaglen = destBag.len();
            dragNode = b.popNode(data);
            label = dragNode.attr.name+'_'+dbaglen+genro.getCounter();
            destBag.setItem(label,dragNode,null,{_position:'<'+destNode.label});
        }else{
            destBag = destNode.getValue();
            if(!destBag){
                destBag = new gnr.GnrBag();
                destNode.setValue(destBag);
            }
            dbaglen = destBag.len();
            dragNode = b.popNode(data);
            label = dragNode.attr.name+'_'+dbaglen+genro.getCounter();
            destBag.setItem(dragNode.label,dragNode);
        }
    }
};


var PermissionComponent = {
    colsPermissionsData:function(data){
        var result = new gnr.GnrBag();
        data.forEach(function(cnode){
            if(!isNullOrBlank(cnode.attr.forbidden) || !isNullOrBlank(cnode.attr.readonly)){
                result.setItem(cnode.label,null,{forbidden:cnode.attr.forbidden,readonly:cnode.attr.readonly,colname:cnode.label})
            }
        });
        return result;
    }
}