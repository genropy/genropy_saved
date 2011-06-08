dojo.declare("gnr.FramedIndexManager", null, {
    constructor:function(sourceNode){
        this.sourceNode = sourceNode;
        this.stack = sourceNode.getValue()
    },
    selectIframePage:function(kw){
        var url = this.getPageUrl(kw);
        var sc = this.stack;
        var sourceNode = this.sourceNode;
        var name = kw.key || url.replace(/\W/g,'_');
        var page = this.sourceNode.widget.gnrPageDict[name];
        var label = kw.label;
        var that = this;
        if (page){
            sourceNode.setRelativeData('selectedFrame',name);
            return;
        }
        var root = genro.src.newRoot();
        var bc = root._('BorderContainer',name,{pageName:name,title:label});
        var center = bc._('ContentPane',{'region':'center','overflow':'hidden'});
        var iframeattr = {'height':'100%','width':'100%','border':0,'id':'iframe_'+name};
        var iframesbag = this.iframesbag;
        if(!iframesbag){
         iframesbag = this.iframesbag = new gnr.GnrBag();
         genro._data.setItem('iframes',iframesbag);
        }
        var that = this;
        iframeattr.onStarted = function(){
         this._dojo.subscribe("updateIframeIndexTab",function(title,label){
             that.updateIframeTab(iframesbag.getNode(name),title,label);
         });
        }
        var iframe = center._('iframe',iframeattr);
        var node = root.popNode('#0');
        sc.setItem(node.label,node);
        iframesbag.setItem(name,null,{'fullname':label,pageName:name,fullpath:kw.fullpath,url:url});
        sourceNode.setRelativeData('selectedFrame',name);
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
            if(pageName==selectedFrame){
                kw._class+=' iframetab_selected';
            }
            button = root._('div',pageName,kw);
            
            button._('div',{'innerHTML':n.attr.fullname,'_class':'iframetab_caption'});
        },'static');
        sourceNode.setValue(root, true);
    },
    updateIframeTab:function(n,title,label){
        if(label){
            var stack = this.sourceNode.widget;
            var oldkey = n.label;
            if(oldkey!=label){
                stack.gnrPageDict[label] = stack.gnrPageDict[oldkey];
                stack.gnrPageDict[oldkey] = null;
                objectPop(stack.gnrPageDict,oldkey);
                var tab = stack.gnrPageDict[label].sourceNode
                tab.attr.pageName=label;
                tab.label = label;
                n.label = label;
                n.attr.pageName = label;
                this.sourceNode.setRelativeData('selectedFrame',label,null,null,false);
            }
        }
        if(title){
            n.updAttributes({fullname:title});
        }

       
    },
    selectedFrame:function(){
        return genro.getData('selectedFrame');
    }
    
});
