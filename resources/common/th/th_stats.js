var th_stats_js = {
    confTreeOnDrop:function(sourceNode,dropInfo,data){
        if(!dropInfo.selfdrop){
                return;
        }
        var put_before = dropInfo.modifiers == 'Shift';
        var b = sourceNode.widget.storebag();
        var destpath = dropInfo.treeItem.getFullpath(null,b);
        if(destpath==data){
            return;
        }
        var destNode = b.getNode(destpath);
        var destBag;
        var kw = {};
        if(destNode.attr.field){
            destBag = destNode.getParentBag();
            kw._position = (put_before?'<':'>')+destNode.label;
        }else{
            destBag = destNode.getValue();
        }
        var dragNode = b.popNode(data);
        destBag.setItem(dragNode.label,dragNode,null,kw);
    }
};