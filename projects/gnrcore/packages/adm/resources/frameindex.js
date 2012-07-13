dojo.declare("gnr.FramedIndexManager", null, {
    constructor:function(stackSourceNode){
        this.stackSourceNode = stackSourceNode;
        this.dbstore =  genro.getData('gnr.dbstore');
        var thurl = '/sys/thpage/'
        this.thpage_url = this.dbstore?'/'+this.dbstore+thurl:thurl;
    },
    
    selectIframePage:function(kw){
        var url = this.getPageUrl(kw);
        var stackSourceNode = this.stackSourceNode;
        var sc = stackSourceNode.getValue();
        var pageName = kw.pageName || url.replace(/\W/g,'_');
        var stackWidget=this.stackSourceNode.widget;
        if(stackWidget.hasPageName(pageName)){
            stackWidget.switchPage(pageName);
            return;
        }
        var label = kw.label;
        var that = this;
        var root = genro.src.newRoot();
        var bc = root._('BorderContainer',pageName,{pageName:pageName,title:label});
        var center = bc._('ContentPane',{'region':'center','overflow':'hidden'});
        var iframeattr = {'height':'100%','width':'100%','border':0,'id':'iframe_'+pageName,frameName:pageName};
        this.iframesbag = genro.getData('iframes');
        if(!this.iframesbag){
         this.iframesbag = new gnr.GnrBag();
         genro._data.setItem('iframes',this.iframesbag);
        }
        var that = this;
        var onStartCallbacks = objectPop(kw,'onStartCallbacks');
        if(onStartCallbacks){
            iframeattr['onStarted'] = function(){
                for (var i=0; i < onStartCallbacks.length; i++) {
                    onStartCallbacks[i].call(this,this._genro);
                };
            }
        }
        var iframe = center._('iframe',iframeattr);
        var node = root.popNode('#0');
        sc.setItem(node.label,node);
        this.iframesbag.setItem(pageName,null,{'fullname':label,pageName:pageName,fullpath:kw.fullpath,url:url,subtab:kw.subtab});
        stackSourceNode.setRelativeData('selectedFrame',pageName);
        setTimeout(function(){iframe.getParentNode().domNode.src = url;},1);
    },
    
    
    getPageUrl:function(kw){
        var url = kw.file;
        var table = kw.table;
        var urlPars = {_root_page_id:genro.page_id};
        if(kw.unique){
            urlPars.ts = new Date().getMilliseconds()
        }
        if(table){
            url = this.thpage_url+table.replace('.','/');
            urlPars['th_from_package'] = genro.getData("gnr.package");
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
    
    createTablist:function(sourceNode,data,onCreatingTablist){
        var root = genro.src.newRoot();
        var selectedFrame = this.selectedFrame();
        var button,kw,pageName;
        var cb = function(n){
            pageName = n.attr.pageName;
            kw = {'_class':'iframetab',pageName:pageName};
            if (n.attr.subtab){
                kw['_class']+=' iframesubtab';
            }
            if(n.attr.hiddenPage){
                return;
            }
            if(pageName==selectedFrame){
                kw._class+=' iframetab_selected';
            }
            button = root._('div',pageName,kw);
            
            button._('div',{'innerHTML':n.attr.fullname,'_class':'iframetab_caption',connectedMenu:'_menu_tab_opt_'});
        }
        data.forEach(cb,'static');
        if(onCreatingTablist){
            onCreatingTablist = funcCreate(onCreatingTablist,'root,selectedPage',this)
            onCreatingTablist(root,selectedFrame);
        }
        sourceNode.setValue(root, true);
    },
    

    selectedFrame:function(){
        return genro.getData('selectedFrame');
    },
    changeFrameLabel:function(kw){
        this.iframesbag.getNode(kw.pageName).updAttributes({fullname:kw.title});
    },
    deleteFramePage:function(pageName){
        var sc = this.stackSourceNode.widget;
        var selected = sc.getSelectedIndex();
        var iframesbag= genro.getData('iframes');
        var node = iframesbag.getNode(pageName);
        genro.publish({topic:'onDeletingIframePage',iframe:'iframe_'+pageName},pageName);
        if(node.attr.subtab=='recyclable'){
            node.updAttributes({'hiddenPage':true});
        }else{
            iframesbag.popNode(pageName);
            this.stackSourceNode.getValue().popNode(pageName);
            var treeItem = genro.getDataNode(node.attr.fullpath);
            if(treeItem){
                var itemclass = treeItem.attr.labelClass.replace('menu_existing_page','');
                itemclass = itemclass.replace('menu_current_page','');
                treeItem.setAttribute('labelClass',itemclass);
            }
        }
        var tablist = genro.nodeById('frameindex_tab_button_root');
        var curlen = tablist.getValue().len();
        selected = selected>=curlen? curlen-1:selected;
        selected = selected<0? 0:selected;
        var nextPageName = tablist.getValue().getNode('#'+selected)? tablist.getValue().getNode('#'+selected).attr.pageName:'indexpage';
        this.stackSourceNode.setRelativeData('selectedFrame',nextPageName); //PUT
    }
});
