dojo.declare("gnr.FramedIndexManager", null, {
    constructor:function(sourceNode){
        this.sourceNode = sourceNode;
        this.stack = sourceNode.getValue()
    },
    selectIframePage:function(kw){
        var url = this.getPageUrl(kw);
        var sc = this.stack;
        var sourceNode = this.sourceNode;
        var name = url.replace(/\W/g,'_');
        var page = sc.getItem(name);
        var label = kw.label;
        var that = this;
        if (page){
            sourceNode.setRelativeData('selectedFrame',name);
            if(kw.onFrameSelected){
                kw.onFrameSelected(page.connectedIframe);
            }
        }
        else{
             var root = genro.src.newRoot();
             var bc = root._('BorderContainer',name,{pageName:name,title:label});
             var center = bc._('ContentPane',{'region':'center','overflow':'hidden'});
             var iframe = center._('iframe',{'height':'100%','width':'100%','border':0,'id':'iframe_'+name,
                                            onStarted:function(){that.onIframeStarted(this,name,kw)}});
             var node = root.popNode('#0');
             sc.setItem(node.label,node);
             sourceNode.setRelativeData('iframes.'+name,null,{'fullname':label,pageName:name,fullpath:kw.fullpath,url:url});
             sourceNode.setRelativeData('selectedFrame',name);
             setTimeout(function(){iframe.getParentNode().domNode.src = url;},1);
        }
    },
    
    onIframeStarted:function(iframe,name,kw){
        this.stack.getItem(name).connectedIframe = iframe;
        if (kw.onFrameSelected){
            kw.onFrameSelected(iframe);
        }
    },
    
    getPageUrl:function(kw){
        var url = kw.file;
        var table = kw.table;
        var urlPars = {inframe:true};
        if(table){
            url = '/sys/thpage/'+table.replace('.','/');
            if(kw.formResource){
                urlPars['th_formResource'] = kw.formResource;
            }
            if(kw.viewResource){
                urlPars['th_viewResource'] = kw.viewResource;
            }
        }
        if(kw.workInProgress){
            urlPars.workInProgress = true;
        }
        objectUpdate(urlPars,objectExtract(kw,'url_*'));
        return genro.addParamsToUrl(url,urlPars);
    },
    
    createTablist:function(sourceNode,data){
        var root = genro.src.newRoot();
        data.forEach(function(n){
            var button = root._('div',n.attr.pageName,{'_class':'iframetab',pageName:n.attr.pageName});
            button._('div',{'innerHTML':n.attr.fullname,'_class':'iframetab_caption'});
        },'static');
        sourceNode.setValue(root, true);
    }    
});
