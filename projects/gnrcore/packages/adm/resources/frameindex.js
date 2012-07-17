dojo.declare("gnr.FramedIndexManager", null, {
    constructor:function(stackSourceNode){
        this.stackSourceNode = stackSourceNode;
        this.dbstore =  genro.getData('gnr.dbstore');
        var default_uri =  genro.getData('gnr.default_uri')||'/';
        var thurl = 'sys/thpage/'
        this.thpage_url = this.dbstore?(default_uri+this.dbstore+'/'+thurl):(default_uri+thurl);
    },
    
    createIframePage:function(kw){
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
        var center = root._('ContentPane',pageName,{'region':'center','overflow':'hidden',pageName:pageName,title:label,_lazyBuild:true});
        var iframeattr = {'height':'100%','width':'100%','border':0,'id':'iframe_'+pageName,frameName:pageName,src:url};
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
        var iframe = center._('div',{'height':'100%','width':'100%',overflow:'hidden'})._('iframe',iframeattr);
        var node = root.popNode('#0');
        sc.setItem(node.label,node);
        this.iframesbag.setItem(pageName,null,{'fullname':label,pageName:pageName,fullpath:kw.fullpath,url:url,subtab:kw.subtab});
        return pageName;
    },

    selectIframePage:function(kw){
        var pageName = this.createIframePage(kw);
        this.stackSourceNode.setRelativeData('selectedFrame',pageName);
        //setTimeout(function(){iframe.getParentNode().domNode.src = url;},1); non serve
    },
    
    
    getPageUrl:function(kw){
        var url = kw.file;
        var table = kw.table;
        var urlPars = {};
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
    },
    menuAction:function(menuitem,ctxSourceNode,event){
        var action = menuitem.code;
        var pageattr = ctxSourceNode.getParentNode().attr;
        var title = ctxSourceNode.attr.innerHTML;
        var fullpath = this.iframesbag.getNode(pageattr.pageName).attr['fullpath'];
        if(action =='detach'){
            this.detachPage(pageattr,title,event);
        }else if(action=='remove'){
            this.removeFromFavorite(fullpath);
        }
        else if(action=='clearfav'){
            this.removeFromFavorite(true);
        }
        else{
            if(fullpath){
                this.addToFavorite(fullpath,action=='start');
            }
        }
    },
    removeFromFavorite:function(fullpath){
        if(fullpath==true){
            favlist = [];
        }else if(fullpath){
            var favlist = genro.getFromStorage('locale','framedindex_favorites') || [];
            var ind = dojo.indexOf(favlist,fullpath);
            if(ind>=0){
                favlist.splice(ind,1);
            }
        }
        genro.setInStorage('locale','framedindex_favorites',favlist);

    },

    addToFavorite:function(fullpath,start){
        var favlist = genro.getFromStorage('locale','framedindex_favorites') || [];
        var ind = dojo.indexOf(favlist,fullpath);
        if(ind==-1){
            if(start){
                favlist = [fullpath].concat(favlist);
            }else{
                favlist.push(fullpath);
            }
        }else if(start){
            favlist.splice(ind,1);
            favlist = [fullpath].concat(favlist);
        }
        genro.setInStorage('locale','framedindex_favorites',favlist);
    },

    loadFavorites:function(){
        var favlist = genro.getFromStorage('locale','framedindex_favorites');
        if(favlist){
            var that = this;
            var i = 0;
            var firstPage;
            var pageName;
            dojo.forEach(favlist,function(fullpath){
                pageName = that.createIframePage(genro.getDataNode(fullpath).attr);
                if(i==0){
                    firstPage = pageName;
                }
                i++;
            });
            this.stackSourceNode.setRelativeData('selectedFrame',firstPage);
        }
    },

    detachPage:function(attr,title,evt){
        var that = this;
        var iframenode = this.stackSourceNode._value.getItem(attr.pageName).getNode('#0');
        var iframedomnode = iframenode.domNode;
        var paletteCode = attr.pageName;
        var kw = {height:_px(iframedomnode.clientHeight),width:_px(iframedomnode.clientWidth),maxable:true,evt:evt,
                title:title,palette__class:'detachPalette',dockTo:false};
        kw['palette_connect_close'] = function(){
            that.stackSourceNode._value.getNode(attr.pageName).widget.domNode.appendChild(iframedomnode);
        }
        var paletteNode = genro.dlg.quickPalette(paletteCode,kw);
        var newparentNode = paletteNode.getValue().getNode('#0.#0.#0').widget.domNode;
        newparentNode.appendChild(iframedomnode);
    }
});
