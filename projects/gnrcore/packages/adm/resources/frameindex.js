dojo.declare("gnr.FramedIndexManager", null, {
    constructor:function(sourceNode){
        this.sourceNode = sourceNode;
        this.stack = sourceNode.getValue()
    },
    selectIframePage:function(kw){
        var url = this.getPageUrl(kw);
        var sc = this.stack;
        var sourceNode = this.sourceNode;
        var pageName = kw.pageName || url.replace(/\W/g,'_');
        var page = this.sourceNode.widget.gnrPageDict[pageName];
        var label = kw.label;
        var that = this;
        if (page){
            sourceNode.setRelativeData('selectedFrame',pageName);
            return;
        }
        var root = genro.src.newRoot();
        var bc = root._('BorderContainer',pageName,{pageName:pageName,title:label});
        var center = bc._('ContentPane',{'region':'center','overflow':'hidden'});
        var iframeattr = {'height':'100%','width':'100%','border':0,'id':'iframe_'+pageName,frameName:pageName};
        var iframesbag = this.iframesbag;
        if(!iframesbag){
         iframesbag = this.iframesbag = new gnr.GnrBag();
         genro._data.setItem('iframes',iframesbag);
        }
        var that = this;
        var frameSubscriptions = objectPop(kw,'frameSubscriptions');
        iframeattr['onStarted'] = function(){
            for (var sub in frameSubscriptions){
                this._dojo.subscribe(sub,frameSubscriptions[sub]);
            }
        }
        var iframe = center._('iframe',iframeattr);
        var node = root.popNode('#0');
        sc.setItem(node.label,node);
        iframesbag.setItem(pageName,null,{'fullname':label,pageName:pageName,fullpath:kw.fullpath,url:url,subtab:kw.subtab});
        sourceNode.setRelativeData('selectedFrame',pageName);
        setTimeout(function(){iframe.getParentNode().domNode.src = url;},1);
    },
    
    
    getPageUrl:function(kw){
        var url = kw.file;
        var table = kw.table;
        var urlPars = {inframe:true};
        if(kw.unique){
            urlPars.ts = new Date().getMilliseconds()
        }
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
        var selectedFrame = this.selectedFrame();
        var button,kw,pageName;
        data.forEach(function(n){
            pageName = n.attr.pageName;
            kw = {'_class':'iframetab',pageName:pageName};
            if (n.attr.subtab){
                kw['_class']+=' iframesubtab'
            }
            if(pageName==selectedFrame){
                kw._class+=' iframetab_selected';
            }
            button = root._('div',pageName,kw);
            
            button._('div',{'innerHTML':n.attr.fullname,'_class':'iframetab_caption'});
        },'static');
        sourceNode.setValue(root, true);
    },
    

    selectedFrame:function(){
        return genro.getData('selectedFrame');
    },
    changeFrameLabel:function(kw){
        this.iframesbag.getNode(kw.pageName).updAttributes({fullname:kw.title});
    }
    
});
