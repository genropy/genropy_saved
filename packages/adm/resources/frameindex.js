var frameIndex = {
    selectIframePage:function(sourceNode,name,label,file,table,formResource,viewResource){
        var sc = sourceNode.getValue();
        var page = sc.getItem(name);
        if (page){
            sourceNode.setRelativeData('selectedFrame',name);
        }
        else{
             var root = genro.src.newRoot();
             var bc = root._('BorderContainer',name,{pageName:name,title:label});
             var center = bc._('ContentPane',{'region':'center','overflow':'hidden'});
             sourceNode.setRelativeData('iframes.'+name,null,{'fullname':label,pageName:name});
             var iframe = center._('iframe',{'height':'100%','width':'100%','border':0});
             url = file;
             var urlPars = {inframe:true};
             if(table){
                url = '/adm/th/thrunner/'+table.replace('.','/');
                if(formResource){
                    urlPars['th_formResource'] = formResource;
                }
                if(viewResource){
                    urlPars['th_viewResource'] = viewResource;
                }
             }
             url = genro.addParamsToUrl(url,urlPars);
             var node = root.popNode('#0');
             sc.setItem(node.label,node);
             sourceNode.setRelativeData('selectedFrame',name);
             iframe.getParentNode().domNode.src = url;
        }
    },

    createTablist:function(sourceNode,data){
        var root = genro.src.newRoot();
        data.forEach(function(n){
            var button = root._('div',n.attr.pageName,{'_class':'iframetab',pageName:n.attr.pageName});
            button._('div',{'innerHTML':n.attr.fullname,'_class':'iframetab_caption'});
        },'static');
        sourceNode.setValue(root, true);
    }
}