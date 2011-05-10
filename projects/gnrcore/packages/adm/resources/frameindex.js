var frameIndex = {
    selectIframePage:function(sourceNode,name,label,file,table,formResource,viewResource,fullpath,attributes){
        console.log(attributes);
        var sc = sourceNode.getValue();
        var page = sc.getItem(name);
        if (page){
            sourceNode.setRelativeData('selectedFrame',name);
        }
        else{
             var root = genro.src.newRoot();
             var bc = root._('BorderContainer',name,{pageName:name,title:label});
             var center = bc._('ContentPane',{'region':'center','overflow':'hidden'});
             var iframe = center._('iframe',{'height':'100%','width':'100%','border':0,'id':'iframe_'+name});
             url = file;
             var urlPars = {inframe:true};
             if(table){
                url = '/sys/thpage/'+table.replace('.','/');
                if(formResource){
                    urlPars['th_formResource'] = formResource;
                }
                if(viewResource){
                    urlPars['th_viewResource'] = viewResource;
                }
             }
             if(attributes.workInProgress){
                 urlPars.workInProgress = true;
             }
             url = genro.addParamsToUrl(url,urlPars);
             var node = root.popNode('#0');
             sc.setItem(node.label,node);
             sourceNode.setRelativeData('iframes.'+name,null,{'fullname':label,pageName:name,fullpath:fullpath,url:url});
             sourceNode.setRelativeData('selectedFrame',name);
             
             setTimeout(function(){iframe.getParentNode().domNode.src = url;},1);
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