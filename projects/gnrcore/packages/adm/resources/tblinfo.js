var QTREEEditor = {
    selfDragDropTree:function(sourceNode,data,dropInfo){
        if(!dropInfo.selfdrop){
            return;
        }
        var put_before =  dropInfo.treeItem.attr.dtype || dropInfo.modifiers == 'Shift';
        var b = sourceNode.widget.storebag();
        var destpath = dropInfo.treeItem.getFullpath(null,b);
        if(destpath==data){
            return
        }
        var destNode = b.getNode(destpath);
        if(put_before){
            if(destpath=='root'){
                return;
            }
            var destBag = destNode.getParentBag();
            var dbaglen = destBag.len();
            var dragNode = b.popNode(data);
            var label = dragNode.attr.name+'_'+dbaglen+genro.getCounter();
            destBag.setItem(label,dragNode,null,{_position:'<'+destNode.label});
        }else{
            var destBag = destNode.getValue();
            if(!destBag){
                destBag = new gnr.GnrBag();
                destNode.setValue(destBag);
            }
            var dbaglen = destBag.len();
            var dragNode = b.popNode(data);
            var label = dragNode.attr.name+'_'+dbaglen+genro.getCounter();
            destBag.setItem(dragNode.label,dragNode);
        }
    }
}