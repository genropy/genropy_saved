dojo.declare("gnr.FramedIndexManager", null, {
    constructor:function(stackSourceNode){
        this.stackSourceNode = stackSourceNode;
        this.dbstore =  genro.getData('gnr.dbstore');
        var default_uri =  genro.getData('gnr.defaultUrl')||'/';
        var thurl = 'sys/thpage/'
        this.thpage_url = this.dbstore?(default_uri+this.dbstore+'/'+thurl):(default_uri+thurl);
    },
    
    createIframeRootPage:function(kw){
        this.makePageUrl(kw);
        var url = kw.url;
        var stackSourceNode = this.stackSourceNode;
        var rootPageName = kw.rootPageName;
        var stackWidget=this.stackSourceNode.widget;
        if(stackWidget.hasPageName(rootPageName)){
            stackWidget.switchPage(rootPageName);
            return;
        }
        this.iframesbag = genro.getData('iframes');
        if(!this.iframesbag){
            this.iframesbag = new gnr.GnrBag();
            genro._data.setItem('iframes',this.iframesbag);
        }
        var sc = stackSourceNode.getValue();
        if(!kw.subtab){
            var sc = this.makeMultiPageStack(sc,kw);
        }
        var node = this.createIframePage(kw);
        sc.setItem(node.label,node);
        this.iframesbag.setItem(rootPageName,null,{'fullname':kw.label,pageName:rootPageName,fullpath:kw.fullpath,url:url,subtab:kw.subtab,selectedPage:node.attr.pageName});
        return rootPageName;
    },

    makeMultiPageStack:function(parentStack,kw){
        var root = genro.src.newRoot();
        var rootPageName = kw.rootPageName;
        var label = kw.label;
        var fp = root._('framePane',rootPageName,{frameCode:label+'_#',pageName:rootPageName,title:label});
        this.framePageTop(fp,kw);
        var sc = fp._('StackContainer',{side:'center',nodeId:rootPageName+'_multipage',selectedPage:'^iframes.'+rootPageName+'?selectedPage'}); 
        var frameNode = root.popNode('#0');
        parentStack.setItem(frameNode.label,frameNode._value,frameNode.attr);
        return sc;
    },

    createIframePage:function(kw){
        var label = kw.label;
        var that = this;
        var root = genro.src.newRoot();
        var rootPageName = kw.rootPageName;
        var url = kw.url;
        var iframePageName,pane_kw;
        var iframeattr = {'height':'100%','width':'100%','border':0,src:url};
        if(kw.subtab){
            iframePageName = rootPageName;
            pane_kw = {_lazyBuild:true,overflow:'hidden',title:kw.title,pageName:rootPageName}
            objectUpdate(iframeattr,{'id':'iframe_'+rootPageName,frameName:rootPageName})
        }else{
            var iframePageName = 'm_'+genro.getCounter();
            var multipageIframePagePath = 'iframes.'+rootPageName+'.'+iframePageName;
            pane_kw = {_lazyBuild:true,overflow:'hidden',title:'^'+multipageIframePagePath+'.title',
                      pageName:iframePageName,closable:true,stackbutton_tooltip:'^'+multipageIframePagePath+'.title?titleFullDesc'}
            genro.setData(multipageIframePagePath+'.title',label+'...');
            objectUpdate(iframeattr,{'id':'iframe_'+rootPageName+'_'+iframePageName,
                            frameName:rootPageName+'_'+iframePageName,multipage_childpath:multipageIframePagePath})
        }
        var center = root._('ContentPane',iframePageName,pane_kw);
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
        return root.popNode('#0');
    },


    framePageTop:function(fp,kw){
        var bar = fp._('SlotBar',{slots:'multipageButtons,*',gradient_from:'#666',side:'top',toolbar:true,
                                        gradient_to:'#444',_class:'iframeroot_bar',
                                        closable:'close',closable_background:'white'});
        var stackNodeId = kw.rootPageName+'_multipage';
        var sbuttons = bar._('StackButtons','multipageButtons',{stackNodeId:stackNodeId,margin_left:'4px'});
        var that = this;
        sbuttons._('div',{innerHTML:'<div class="multipage_add">&nbsp;</div>',_class:'multibutton',
                         connect_onclick:function(){
                            var sc = genro.nodeById(stackNodeId);
                            var node = that.createIframePage(kw);
                            var iframePageName = node.attr.pageName;
                            sc._value.setItem(node.label,node);
                            setTimeout(function(){sc.widget.switchPage(iframePageName);},100);
                         }
                     });
        //div('<div class="multipage_add">&nbsp;</div>',connect_onclick="""FIRE gnr.multipage.new = genro.dom.getEventModifiers($1);""",_class='multibutton')
    },

    selectIframePage:function(kw){
        var rootPageName = this.createIframeRootPage(kw);
        this.stackSourceNode.setRelativeData('selectedFrame',rootPageName);
        //setTimeout(function(){iframe.getParentNode().domNode.src = url;},1); non serve
    },
    
    
    makePageUrl:function(kw){
        var url = kw.file;
        var table = kw.table;
        var urlPars = {};
        if(kw.unique){
            urlPars.ts = new Date().getMilliseconds()
        }
        if(table){
            url = this.thpage_url+table.replace('.','/');
            urlPars['th_from_package'] = kw['pkg_menu'] || genro.getData("gnr.package");
        }
        if(kw.formResource){
            urlPars['th_formResource'] = kw.formResource;
        }
        if(kw.viewResource){
            urlPars['th_viewResource'] = kw.viewResource;
        }
        if(kw.workInProgress){
            urlPars.workInProgress = true;
        }
        objectUpdate(urlPars,objectExtract(kw,'url_*'));
        kw.url = genro.addParamsToUrl(url,urlPars);
        kw.rootPageName = kw.pageName || kw.url.replace(/\W/g,'_');
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

    reloadSelectedIframe:function(rootPageName){
        var iframesbag= genro.getData('iframes');
        var iframePageId = iframesbag.getItem(rootPageName+'?selectedPage');
        var iframe = dojo.byId("iframe_"+rootPageName+'_'+iframePageId);
        iframe.sourceNode._genro.pageReload();
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
