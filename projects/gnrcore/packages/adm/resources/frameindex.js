var loginManager = {
    notificationManager:function(notification_id){
        genro.setData('notification.confirm',null);
        var notification_data = genro.serverCall('_table.adm.user_notification.getNotification',{pkey:notification_id});
        var dlg = genro.dlg.quickDialog(notification_data['title'],{_showParent:true,width:'900px',datapath:'notification',background:'white'});
        var box = dlg.center._('div',{overflow:'auto',height:'500px',overflow:'auto',padding:'10px'});
        box._('div',{innerHTML:notification_data.notification,border:'1px solid transparent',padding:'10px'});
        var bar = dlg.bottom._('slotBar',{slots:'cancel,*,confirm_checkbox,2,confirm',height:'22px'});
        bar._('button','cancel',{'label':'Cancel',command:'cancel',action:function(){genro.logout();}});
        bar._('checkbox','confirm_checkbox',{value:'^.confirm',label:(notification_data.confirm_label || 'Confirm')})
        bar._('button','confirm',{'label':'Confirm',command:'confirm',disabled:'^.confirm?=!#v',action:function(){
                                                    genro.serverCall('_table.adm.user_notification.confirmNotification',{pkey:notification_id},
                                                            function(n_id){
                                                                dlg.close_action();
                                                                if(n_id){
                                                                    loginManager.notificationManager(n_id);
                                                                }else{
                                                                    genro.publish('end_notification')
                                                                }
                                                            }
                                                    )

                                                }});
        dlg.show_action();
    },

}


dojo.declare("gnr.FramedIndexManager", null, {
    constructor:function(stackSourceNode){
        this.stackSourceNode = stackSourceNode;
        this.dbstore =  genro.getData('gnr.dbstore');
        var default_uri =  genro.getData('gnr.defaultUrl')||'/';
        var thurl = 'sys/thpage/';
        var lookup_url = 'sys/lookuptables';
        this.thpage_url = this.dbstore?(default_uri+this.dbstore+'/'+thurl):(default_uri+thurl);
        this.lookup_url = this.dbstore?(default_uri+this.dbstore+'/'+lookup_url):(default_uri+lookup_url);

    },
    
    createIframeRootPage:function(kw){
        this.makePageUrl(kw);
        var url = kw.url;
        var stackSourceNode = this.stackSourceNode;
        var rootPageName = kw.rootPageName;
        var stackWidget=this.stackSourceNode.widget;
        if(stackWidget.hasPageName(rootPageName)){
            return rootPageName;
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
        var fp = root._('framePane',rootPageName,{frameCode:kw.name+'_#',pageName:rootPageName,title:kw.label});
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
        var openKw = objectPop(kw,'openKw');
        var rootPageName = this.createIframeRootPage(kw);
        var that = this;
        var cb = function(){
            that.stackSourceNode.setRelativeData('selectedFrame',rootPageName);
            if(openKw){
                that.stackSourceNode.watch('loadingOpenKw',function(){
                    return that.getCurrentIframe(rootPageName);
                },function(){
                    var iframe = that.getCurrentIframe(rootPageName);
                    iframe.gnr.postMessage(iframe.sourceNode,openKw);
                })
            }
        };
        var n = this.iframesbag.getNode(kw.rootPageName);
        var hasBeenSelected = this.iframesbag.getNode(kw.rootPageName).attr.hasBeenCreated;
        if(!hasBeenSelected){
            genro.callAfter(function(){
                n.attr.hasBeenCreated = true;
            },1);
            genro.callAfter(cb,500,this,'creating')
        }else{
            cb();
        }
        
        //setTimeout(function(){iframe.getParentNode().domNode.src = url;},1); non serve
    },
    
    
    makePageUrl:function(kw){
        var url = kw.file;
        var table = kw.table;
        var lookup_manager = kw.lookup_manager;
        var urlPars = {};
        if(kw.unique){
            urlPars.ts = new Date().getMilliseconds()
        }
        if(table){
            url = this.thpage_url+table.replace('.','/');
            urlPars['th_from_package'] = kw['pkg_menu'] || genro.getData("gnr.package");
        }else if(lookup_manager){
            url = this.lookup_url+(lookup_manager=='*'?'':('/'+lookup_manager.replace('.','/')));
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

    reloadSelectedIframe:function(rootPageName,modifiers){
        var iframe = this.getCurrentIframe(rootPageName);
        if(iframe){
            var dodebug = modifiers=='Shift';
            iframe.sourceNode._genro.pageReload({debug_sql:dodebug,pageReloading:true,dojo_source:true});
        }
    },

    getCurrentIframe:function(rootPageName){
        var iframesbag= genro.getData('iframes');
        var iframePageId = iframesbag.getItem(rootPageName+'?selectedPage');
        var iframeId = iframePageId;
        if(rootPageName!=iframePageId){
            iframeId = rootPageName+'_'+iframePageId;
        }
        return dojo.byId("iframe_"+iframeId);
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
        var favorite_pages = genro.userPreference('adm.index.favorite_pages') || new gnr.GnrBag();
        if(fullpath==true){
            favorite_pages = null;
        }else{
            var l = fullpath.replace(/\W/g,'_');
            favorite_pages.popNode(l);      
        }
        genro.setUserPreference('index.favorite_pages',favorite_pages,'adm')
    },

    addToFavorite:function(fullpath,start){
        var favorite_pages = genro.userPreference('adm.index.favorite_pages') || new gnr.GnrBag();
        var l = fullpath.replace(/\W/g,'_');
        if(favorite_pages.len() && start){
            favorite_pages.forEach(function(n){
                n._value.setItem('start',false);
            },'static')
        }else{
            start=true;
        }
        favorite_pages.setItem(l,new gnr.GnrBag({pagepath:fullpath,start:start}));
        genro.setUserPreference('index.favorite_pages',favorite_pages,'adm')
    },

    loadFavorites:function(){
        var favorite_pages = genro.userPreference('adm.index.favorite_pages');
        if(favorite_pages){
            var that = this;
            var v;
            var startPage;
            var kw,inattr;
            var pageName;
            var treenode;
            favorite_pages.forEach(function(n){
                v = n.getValue();
                treenode = genro.getDataNode(v.getItem('pagepath'))
                if(!treenode){
                    return;
                }
                kw = treenode.attr;

                var labelClass= treenode.attr.labelClass;
                if(labelClass.indexOf('menu_existing_page')<0){
                    treenode.setAttribute('labelClass',labelClass+' menu_existing_page');
                }                
                inattr = treenode.getInheritedAttributes();    
                kw = objectUpdate({name:treenode.label,pkg_menu:inattr.pkg_menu,"file":null,
                                    table:null,formResource:null,viewResource:null,
                                    fullpath:v.getItem('pagepath'),modifiers:null},
                                    treenode.attr)
                pageName = that.createIframeRootPage(kw);
                if(v.getItem('start')){
                    startPage = pageName;
                }
            },'static');
            setTimeout(function(){
                that.stackSourceNode.setRelativeData('selectedFrame',startPage || pageName);
            },100);
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
