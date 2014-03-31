var TH = function(th_root){
    genro.ext.th_instances = genro.ext.th_instances || {};
    if(!(th_root in genro.ext.th_instances)){
        genro.ext.th_instances[th_root] = {th_root:th_root};
    }
    return genro.ext.th_instances[th_root];
};
var th_unifyrecord = function(kw){
    genro.serverCall('th_getUnifierWarningBag',kw,function(messagebag){
        messagebag.setBackRef();
        var title = messagebag.getItem('title');
        if(messagebag.getItem('error')){
            genro.dlg.alert(messagebag.getItem('error'),title);
            return;
        }
        var message = messagebag.getItem('tabledata').getFormattedValue();
        message = '<div style="margin:auto;">' +message+'</div>';
        genro.dlg.ask(title,message,null,{confirm:function(){
            genro.serverCall('app.unifyRecords',kw,function(result){console.log('ok')});}
        });
    });
};

var th_view_batch_caller = function(kw){
    var grid = genro.wdgById(kw.gridId);
    var store = grid.collectionStore();
    if(store.storeType=='VirtualSelection'){
        kw['selectionName'] = store.selectionName;
    }else{
        kw['selectedPkeys'] = grid.getSelectedPkeys() || [];
        if (kw['selectedPkeys'].length==0){
            kw['selectedPkeys'] = grid.getAllPkeys();
        }
        
    }
    if(grid.cellmap._selected){
        kw['selectedPkeys'] = grid.sourceNode.getRelativeData('.sets._selected');
    }else{
        kw['selectedRowidx'] = grid.getSelectedRowidx();
    }
    genro.publish("table_script_run",kw);
}

var th_usersettings = function(th){
    var attr = th.attr;
    var formResource = attr.th_formResource;
    var viewResource = attr.th_viewResource;
    var table = attr.table;
    var key = (table+'/'+formResource).replace(/\:/g, '_').replace(/\./g, '_');
    var dlg = genro.dlg.quickDialog('User setting',{width:'300px'});
    dlg.center._('div',{remote:'th_userSetting',remote_thkey:key,height:'200px'});

    var bar = dlg.bottom._('slotBar',{slots:'*,cancel,confirm',action:function(){
                                                dlg.close_action();
                                                if(this.attr.command=='confirm'){
                                                    var data = genro.getData('gnr.thpref.'+key);
                                                    genro.serverCall('th_saveUserSetting',{data:data,thkey:key},function(){
                                                        genro.pageReload();
                                                    },null,'POST');
                                                }
                                            }});
    bar._('button','cancel',{'label':'Cancel',command:'cancel'});
    bar._('button','confirm',{'label':'Confirm',command:'confirm'});




    dlg.show_action()
};


var th_sections_manager = {
    onCalling:function(sections,kwargs){
        var currentSections = [];

        var original_condition = kwargs['condition'];
        var andlist = [];

        sections.forEach(function(n){
            var sectionsbag = n.getValue();
            var currents = sectionsbag.getItem('current').split(',');
            var orlist = [];
            var conditions = sectionsbag.getItem('data');
            currents.forEach(function(current){
                var cn = conditions.getNode(current);
                var cond = cn.attr.condition;
                if(cond){
                    var condpars = objectExtract(cn.attr,'condition_*',true);
                    for(var k in condpars){
                        var newcondkey = k+'_'+cn.attr.code;
                        kwargs[newcondkey] = condpars[k];
                        cond = cond.replace(new RegExp(':'+k,'g'),':'+newcondkey);
                    }
                    orlist.push(' ('+cond+') ');
                }
            });
            if(orlist.length>0){
                andlist.push(' (' +orlist.join(' OR ')+') ');
            }
            
        });
        var sections_condition = andlist.join(' AND ');
        if(sections_condition && original_condition){
            condition = ' ( '+sections_condition+' ) AND ( '+original_condition+' )';
        }else{
            condition = sections_condition || original_condition;
        }
        kwargs['condition'] =condition;
    },
    getSectionTitle:function(sections){
        var captions = [];
        sections.forEach(function(n){
            var sectionsbag = n.getValue();
            var current = sectionsbag.getItem('current');
            var currents = current ? current.split(','): [];
            var orlist = [];
            var titles = sectionsbag.getItem('data');
            currents.forEach(function(current){
                orlist.push(titles.getNode(current).attr.caption || '');
            });
            if(orlist.length>0){
                captions.push(orlist.join(' | '))
            }
        });
        return ' '+captions.join(' - ');
    }
};

dojo.declare("gnr.widgets.ThIframe", gnr.widgets.gnrwdg, {
    thiframe: function(parent,kw){
        var table = objectPop(kw,'table');
        var url = objectPop(kw,'url') || '/sys/thpage/'+table.replace('.','/');
        var urlPars = {'th_public':false,'th_from_package':genro.getData('gnr.package')};
        url = genro.addParamsToUrl(url,urlPars);
        var pkey = objectPop(kw,'pkey');
        if (pkey){
            url+='/'+pkey;
        }
        var main = objectPop(kw,'main');
        var iframeAttrs = {'src':url,main:main,_childname:'iframe',height:'100%',width:'100%',border:0};
        iframeAttrs['main_th_modal'] = true;
        iframeAttrs = objectUpdate(kw,iframeAttrs);
        return parent._('iframe',iframeAttrs);
    }
});

dojo.declare("gnr.widgets.ThIframeDialog", gnr.widgets.ThIframe, {
    createContent:function(sourceNode, kw) {
        var dialogAttrs = objectExtract(kw,'title,height,width');
        dialogAttrs.closable=true;
        dialogAttrs = objectUpdate({overflow:'hidden',_lazyBuild:true},dialogAttrs);
        var dialog = sourceNode._('dialog',objectUpdate(objectExtract(dialogAttrs,'title,closable'),objectExtract(kw,'dialog_*')));
        var onStarted = objectPop(kw,'onStarted');
        kw.onStarted = function(){
            var wdg = dialog.getParentNode().widget;
            this._genro._rootForm.subscribe('onChangedTitle',function(kw){
                wdg.setTitle(kw.title)
            });
            if(onStarted){
                onStarted.call(this);
            }
        }
        this.thiframe(dialog._('div',dialogAttrs),kw);
        return dialog;
    }
});

dojo.declare("gnr.widgets.ThIframePalette",gnr.widgets.ThIframe, {
    createContent:function(sourceNode, kw) {
        var paletteAttrs = objectExtract(kw,'title,top,bottom,left,right,height,width,_lazyBuild,autoSize,dockTo');
        objectUpdate(paletteAttrs,objectExtract(kw,'dockButton_*',null,true));
        objectUpdate(paletteAttrs,objectExtract(kw,'palette_*'));
        paletteAttrs = objectUpdate({overflow:'hidden',_lazyBuild:true},paletteAttrs);
        var palette = sourceNode._('palette',paletteAttrs);
        this.thiframe(palette,kw)
        return palette;
    }
});

dojo.declare("gnr.LinkerManager", null, {
    constructor:function(sourceNode){
        this.sourceNode = sourceNode;
        this.form = this.sourceNode.form;
        this.formUrl = sourceNode.attr._formUrl;
        this.formResource = sourceNode.attr._formResource;
        this.field = sourceNode.attr._field;
        this.fieldpath = '#FORM.record.'+this.field;
        this.resolverpath = '#FORM.record.@'+this.field;
        this.table = sourceNode.attr.table;
        this.fakeFormId = sourceNode.attr._formId || 'LK_'+this.table.replace('.','_');
        this.embedded = sourceNode.attr._embedded;
        this.dialog_kwargs = sourceNode.attr._dialog_kwargs;
        this.default_kwargs = sourceNode.attr._default_kwargs;
        this.sourceNode.registerSubscription('changeInTable',this,function(kw){
            if(kw.table==this.table){
                if(this.sourceNode.getRelativeData(this.fieldpath)==kw.pkey){
                    this.sourceNode.getRelativeData(this.resolverpath).getParentNode().getValue('reload');
                }
            }
        });
    },
    
    openLinker:function(focus){
        var sourceNode = this.sourceNode;
        var that =this;
        if(sourceNode.form.locked){
            return;
        } 
        genro.dom.addClass(sourceNode,"th_enableLinker");
        if(this.embedded && focus!=false){
            setTimeout(function(){
                sourceNode.getChild('/selector').widget.focus();
            },1);
        }
    },

    closeLinker:function(){
        genro.callAfter(function(){
            var selector = this.sourceNode.getChild('selector');
            if(selector && !selector.widget.isValid()){
                return;
            }
            if(this.embedded || this.getCurrentPkey()){
                genro.dom.removeClass(this.sourceNode,"th_enableLinker");
            }
        },10,this,'closing')
        
    },
    getCurrentPkey:function(){
        return this.sourceNode.getRelativeData(this.fieldpath);
    },
    setCurrentPkey:function(pkey){
        var currkey = this.sourceNode.getRelativeData(this.fieldpath);
        var dbselect = this.sourceNode.getChild('selector').widget;
        genro.publish('changeInTable',{pkey:pkey,table:this.table})
        dbselect.setValue(pkey,true);
    },    
    openrecord:function(pkey){
        if(this.form.locked){
            return;
        }
        var default_kw = this.sourceNode.evaluateOnNode(this.default_kwargs);
        if(this.linkerform){
            this.linkerform.load({destPkey:pkey,default_kw:default_kw});
            this.thdialog.show();
        }else{
            var that = this;
            var destPkey = pkey;
            var iframeDialogKw = {title:'',table:this.table,main:'main_form',
                                 main_th_linker:true,height:'300px',width:'400px',main_th_formId:this.fakeFormId,
                                 onStarted:function(){that.onIframeStarted(this,destPkey,default_kw)}};
            if(this.formResource){
                iframeDialogKw.main_th_formResource=this.formResource;
            }
            if(this.formUrl){
                iframeDialogKw.url = this.formUrl;
            }
            objectUpdate(iframeDialogKw,this.dialog_kwargs);
            var thdialog = genro.src.create('thIframeDialog',iframeDialogKw,this.sourceNode.getStringId());
            this.thdialog = thdialog.getParentNode().getWidget();
            this.thdialog.show();
        }
    },
    
    onIframeStarted:function(iframe,pkey,default_kw){
        var default_kw = default_kw || {};
        this.linkerform = iframe._genro.formById(this.fakeFormId);
        this.linkerform.load({destPkey:pkey,default_kw:default_kw});
        var that = this;
        this.linkerform.subscribe('onSaved',function(kw){
            that.setCurrentPkey(kw.pkey);
        });
        this.linkerform.subscribe('onDismissed',function(kw){
            that.thdialog.hide();
        });
        
    },
        
    loadrecord:function(pkey){
        this.openrecord(this.getCurrentPkey());
    },
    
    newrecord:function(){
        this.sourceNode.getChild('selector').widget.setDisplayedValue('')
        this.openrecord('*newrecord*');
    }
});
dojo.declare("gnr.pageTableHandlerJS",null,{
    constructor:function(sourceNode,mainpkey,kw){
        this.sourceNode = sourceNode;
        this.mainpkey = mainpkey;
        this.default_kwargs = kw.default_kwargs;
        this.pages_dict = {};
        this.recyclablePages = kw.recyclablePages;
        this.page_kw = {url_main_call:kw.main_call || 'main_form',url_th_public:true,subtab:this.recyclablePages?'recyclable':true,
                        url_th_linker:true,url_th_lockable:true,url_main_store_storeType:'Collection','url_th_from_package':genro.getData('gnr.package')};
        this.formUrl = kw.formUrl;
        this.loadingTitle = 'loading...'
        this.indexgenro = genro.mainGenroWindow.genro;
        this.viewStore = kw.viewStore.store;
        if(kw.th){
            for(var k in kw.th){
                this.page_kw['url_th_'+k] = kw.th[k];
            }
        }
    },
    
    openPage:function(pkey,dbname){
        var pageName;
        var formUrl = dbname?'/'+dbname+this.formUrl:this.formUrl;
        var recyclablePage = null;
        for (var k in this.pages_dict){
            var pagePkey = this.pages_dict[k];
            if(pagePkey==pkey){
                this.indexgenro.publish('selectIframePage',{pageName:k});
                return;
            }else if(!recyclablePage && !pagePkey){
                recyclablePage = k;
            }
        }
        if(recyclablePage){
            var recyiclableIframe = this.indexgenro.domById('iframe_'+recyclablePage);
            this.indexgenro.getDataNode('iframes.'+recyclablePage).updAttributes({'hiddenPage':false});
            this.indexgenro.publish('selectIframePage',{pageName:recyclablePage});
            recyiclableIframe.sourceNode._genro._rootForm.load({destPkey:pkey});

            return;
        }else{
            pageName = genro.page_id+'_'+genro.getCounter();
            this.pages_dict[pageName] = pkey;
        }
        var kw = objectUpdate({file:formUrl,pageName:pageName,label:this.loadingTitle},this.page_kw);
        if(pkey=='*newrecord*'){
            default_kwargs = this.sourceNode.evaluateOnNode(this.default_kwargs);
            for (var k in default_kwargs){
                kw['url_default_'+k] = default_kwargs[k];
            }
        }
        var cblist = [];
        var indexgenro = this.indexgenro;
        var that = this;

        cblist.push(function(iframegenro){
            var form = iframegenro._rootForm
            iframegenro.dojo.subscribe('form_'+form.formId+'_onLoaded',
                                    function(kw){
                                        that.pages_dict[pageName] = kw.pkey;
                                        indexgenro.publish('changeFrameLabel',{pageName:pageName,title:kw.data?kw.data.attr.caption:'loading...'});
                                    });
            iframegenro.dojo.subscribe('onDeletingIframePage',function(pageName){
                if(that.recyclablePages){
                    that.pages_dict[pageName] = null;
                    form.norecord();
                }else{
                    objectPop(that.pages_dict,pageName);
                }
            });
            form.store.parentStore = that.viewStore;
            form.setLocked(that.viewStore.locked);
            form.load({destPkey:that.pages_dict[pageName] || pkey});
        });
        kw['onStartCallbacks'] = cblist;
        this.indexgenro.publish('selectIframePage',kw);
    },
    
    checkMainPkey:function(mainpkey){
        if(mainpkey==this.mainpkey){
            return;
        }
        this.mainpkey = mainpkey;
        this.destroyPages();
    },
    destroyPages:function(){
        genro.mainGenroWindow.genro.publish('destroyFrames',this.pages_dict);
        this.pages_dict = {};
    }

});
dojo.declare("gnr.IframeFormManager", null, {
    constructor:function(sourceNode){
        this.sourceNode = sourceNode;
        this.sourceNode.attr._fakeform=true;
        //this.form = this.sourceNode.form;
        this.formUrl = sourceNode.attr._formUrl;
        this.table = sourceNode.attr._table;
        this.default_kwargs = objectPop(sourceNode.attr,'_default_kwargs');
        this.iframeAttr = sourceNode.attr._iframeAttr;
        this.fakeFormId = sourceNode.attr._fakeFormId || 'LK_'+this.table.replace('.','_');
        this.formStoreKwargs = sourceNode.attr._formStoreKwargs || {};
    },
    openrecord:function(kw){
        var kw = typeof(kw)=='string'?{destPkey:kw}:kw;
        genro.publish('form_'+this.fakeFormId+'_onLoading');
        if(this.iframeForm){
            this.iframeForm.load(kw);
        }else{
            var iframeAttr = this.iframeAttr;
            var that = this;
            iframeAttr['onStarted'] = function(){that.onIframeStarted(this,kw)};
            iframeAttr['main_th_formId'] = this.fakeFormId;
            objectUpdate(iframeAttr,{height:'100%',width:'100%',border:0});
            iframeAttr.src = iframeAttr.src || '/sys/thpage/'+this.table.replace('.','/');
            if(this.formStoreKwargs.parentStore){
                iframeAttr['main_th_navigation'] = true;
                iframeAttr['main_store_storeType'] = 'Collection';
            }
            this.iframeNode = this.sourceNode._('iframe',iframeAttr);
        }
    },
    closerecord:function(modifiers){
        this.iframeForm.dismiss(modifiers);
    },
    onIframeStarted:function(iframe,kw){
        var that = this;
        this.iframe = iframe;
        this.iframeForm = iframe._genro.formById(this.fakeFormId);
        this.iframeForm.publishToParent = true;
        this.iframeForm.store.handlers.load.defaultCb = function(){
            return that.sourceNode.evaluateOnNode(that.default_kwargs);
        }
        this.iframeForm.load(kw);
        var g = genro;
        this.iframeForm.subscribe('onSaved',function(){
            g.ping();
        });
        if(this.formStoreKwargs.parentStore){
            this.iframeForm.store.parentStore = genro.getStore(this.formStoreKwargs.parentStore);
        }
    }
});


