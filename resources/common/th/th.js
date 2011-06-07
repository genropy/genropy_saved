dojo.declare("gnr.widgets.ThIframe", gnr.widgets.gnrwdg, {
    thiframe: function(parent,kw){
        var table = objectPop(kw,'table');
        var url = objectPop(kw,'url') || '/sys/thpage/'+table.replace('.','/');
        var urlPars = {'th_public':false};
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
        this.table = sourceNode.attr.table;
        this.fakeFormId = sourceNode.attr._formId || 'LK_'+this.table.replace('.','_');
        this.embedded = sourceNode.attr._embedded;
        this.dialog_kwargs = sourceNode.attr._dialog_kwargs;
        this.default_kwargs = sourceNode.attr._default_kwargs;
    },
    
    openLinker:function(){
        var sourceNode = this.sourceNode;
        var that =this;
        if(sourceNode.form.locked){
            return;
        } 
        genro.dom.addClass(sourceNode,"th_enableLinker");
        if(this.embedded){
            setTimeout(function(){
                sourceNode.getChild('/selector').widget.focus();
            },1);
        }
    },

    closeLinker:function(){
        if(this.embedded || this.getCurrentPkey()){
            genro.dom.removeClass(this.sourceNode,"th_enableLinker");
        }
    },
    getCurrentPkey:function(){
        return this.sourceNode.getRelativeData(this.fieldpath);
    },
    setCurrentPkey:function(pkey){
        this.sourceNode.setRelativeData(this.fieldpath,null,null,null,false);
        this.sourceNode.setRelativeData(this.fieldpath,pkey);
    },    
    openrecord:function(pkey){
        if(this.form.locked){
            return;
        }
        if(this.linkerform){
            this.linkerform.load({destPkey:pkey,default_kw:this.sourceNode.evaluateOnNode(this.default_kwargs)});
            this.thdialog.show();
        }else{
            var that = this;
            var destPkey = pkey;
            var iframeDialogKw = {title:'',table:this.table,main:'form',
                                 main_th_linker:true,height:'300px',width:'400px',main_th_formId:this.fakeFormId,
                                 onStarted:function(){that.onIframeStarted(this,destPkey)}};
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
    
    onIframeStarted:function(iframe,pkey){
        this.linkerform = iframe._genro.formById(this.fakeFormId);
        this.linkerform.load({destPkey:pkey,default_kw:this.default_kw});
        var that = this;
        this.linkerform.subscribe('onSaved',function(kw){
            that.setCurrentPkey(kw.pkey);
            that.closeLinker();
            that.thdialog.hide();
        });
        this.linkerform.subscribe('onDismissed',function(kw){
            that.thdialog.hide();
        });
        
    },
    
    loadrecord:function(pkey){
        this.openrecord(this.getCurrentPkey());
    },
    
    newrecord:function(){
        this.openrecord('*newrecord*');
    }
});

dojo.declare("gnr.IframeFormManager", null, {
    constructor:function(sourceNode){
        this.sourceNode = sourceNode;
        this.sourceNode.attr._fakeForm=true;
        //this.form = this.sourceNode.form;
        this.formUrl = sourceNode.attr._formUrl;
        this.table = sourceNode.attr._table;
        this.default_kwargs = objectExtract(sourceNode.attr,'default_*');
        this.iframeAttr = sourceNode.attr._iframeAttr;
        this.fakeFormId = sourceNode.attr._fakeFormId || 'LK_'+this.table.replace('.','_');
        this.formStoreKwargs = sourceNode.attr._formStoreKwargs || {};
    },
    openrecord:function(pkey){
        genro.publish('form_'+this.fakeFormId+'_onLoading');
        if(this.iframeForm){
            this.iframeForm.load({destPkey:pkey});
        }else{
            var iframeAttr = this.iframeAttr;
            var that = this;
            iframeAttr['onStarted'] = function(){that.onIframeStarted(this,pkey)};
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
    onIframeStarted:function(iframe,pkey){
        var that = this;
        this.iframeForm = iframe._genro.formById(this.fakeFormId);
        this.iframeForm.store.handlers.load.defaultCb = function(){
            return that.sourceNode.evaluateOnNode(that.default_kwargs);
        }
        this.iframeForm.load({destPkey:pkey});
        if(this.formStoreKwargs.parentStore){
            this.iframeForm.store.parentStore = genro.getStore(this.formStoreKwargs.parentStore);
        }
    }
});


dojo.declare("gnr.GnrQueryBuilder", null, {
    constructor: function(sourceNode, maintable,rootId) {
        if (!genro.querybuilder){
            genro.querybuilder = function(mangler){
                return genro.nodeById(mangler+'_'+'queryscripts')._querybuilder;
            }
        }
        this.sourceNode = sourceNode;
        this.rootId = rootId;
        this.maintable = maintable;
        this.tablecode = maintable.replace('.','_');
        this.mangler = sourceNode.getInheritedAttributes()['th_root'];
        this.dtypes_dict = {'A':'alpha','T':'alpha','C':'alpha',
            'D':'date','DH':'date','I':'number',
            'L':'number','N':'number','R':'number','B':'boolean','TAG':'tagged'};
        this.helper_op_dict = {'in':'in','tagged':'tagged'};
        genro.setDataFromRemote('gnr.qb.'+this.tablecode+'.fieldstree', "relationExplorer", {table:maintable, omit:'_'});
        this.treefield = genro.getData('gnr.qb.'+this.tablecode+'.fieldstree');
        genro.setDataFromRemote('gnr.qb.'+this.tablecode+'.fieldsmenu', "fieldExplorer", {table:maintable, omit:'_*'});
        genro.setDataFromRemote('gnr.qb.sqlop', "getSqlOperators");
    },

    getDtypeGroup:function(dtype) {
        var dflt = ('other_' + dtype).toLowerCase();
        var dflt = 'other';
        return this.dtypes_dict[dtype] || dflt;
    },
    
    relativeId:function(id){
        if(this.mangler){
             return this.mangler + '_' + id;
        }else{
            return this.tablecode+'_'+id;
        }
       
    },
    
    getRelativeNode:function(id){
        return genro.nodeById(this.relativeId(id));
    },
    
    createMenues: function() {
        genro.src.getNode()._('div', this.relativeId('_qbmenues'));
        var node = genro.src.getNode(this.relativeId('_qbmenues'));
        node.clearValue();
        node.freeze();
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.jc',id:this.relativeId('qb_jc_menu')});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.not',id:this.relativeId('qb_not_menu')});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.'+this.tablecode+'.fieldsmenu',id:this.relativeId('qb_fields_menu'),
            action:"genro.querybuilder('"+this.mangler+"').onChangedQueryColumn($2,$1,$2.attr.relpath);"});

        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.op',id:this.relativeId('qb_op_menu')});

        var opmenu_types = ['alpha','date','number','other','boolean','unselected_column'];
        for (var i = 0; i < opmenu_types.length; i++) {
            node._('menu', {modifiers:'*',_class:'smallmenu',
                storepath:'gnr.qb.sqlop.op_spec.' + opmenu_types[i],id:this.relativeId('qb_op_menu_') + opmenu_types[i]});
        }
        node.unfreeze();
    },
    getOpMenuId: function(dtype) {
        var id = dtype ? "qb_op_menu_" + this.getDtypeGroup(dtype) : 'qb_op_menu_unselected_column';
        return this.relativeId(id);
    },
    getCaption: function(optype, pars) {
        var val = pars[optype];
        if (val) {
            if (optype == 'column') {
                var tnode = this.treefield.getNode(val);
                if (tnode) {
                    return tnode.attr.fullcaption || tnode.column || '&nbsp;';
                }
                console.log('missing column while looking for caption:' + val);
                return pars.column_caption || '&nbsp;';
            }
            else {
                return genro.getDataNode('gnr.qb.sqlop.' + optype + '.' + val).attr.caption;
            }
        } else {
            return '&nbsp;';
        }
    },
    onChangedQueryColumn: function(contextNode, column_attr, label) {
        var label = label || 'c_0';
        var relpath = '.' + label;
        contextNode.setRelativeData(relpath + '?column_caption', column_attr.fullcaption);
        contextNode.setRelativeData(relpath + '?column', column_attr.fieldpath);
        var currentDtype = contextNode.getRelativeData(relpath + '?column_dtype');
        if (currentDtype != column_attr.dtype) {
            contextNode.setRelativeData(relpath + '?column_dtype', column_attr.dtype);
            var default_op = genro._('gnr.qb.sqlop.op_spec.' + this.getDtypeGroup(column_attr.dtype) + '.#0');
            if (default_op) {
                contextNode.setRelativeData(relpath + '?op', default_op);
                contextNode.setRelativeData(relpath + '?op_caption',
                        genro.getDataNode('gnr.qb.sqlop.op.' + default_op).attr.caption);
            }

        }
        contextNode.setRelativeData(relpath, '');
    },
    onChangedQueryOp: function(contextNode, op_attr, label) {
        var label = label || 'c_0';
        var relpath = '.' + label;
    },
    onHelperOpen:function() {
        var node = genro._firingNode;
        node.setRelativeData('#helper_in.buffer', node.getRelativeData(node.attr._relpath));
    },

    buildQueryPane: function(startNode, datapath) {
        var startNode = startNode || genro.nodeById(this.rootId) ||  genro.nodeById(this.relativeId(this.rootId));
        if(startNode){
            startNode.clearValue();
            startNode.freeze();
            this._buildQueryGroup(startNode, this.sourceNode.getRelativeData('.query.where'), 0);
            startNode.unfreeze();
        }
    },
    addDelFunc : function(mode, pos, e) {
        var querybag,addblock;
        if (e) {
            var target = e.target;
            addblock = e.altKey;
            querybag = target.sourceNode.getRelativeData();
        } else {
            addblock = false;
            querybag = this.sourceNode.getRelativeData('.query.where');
        }
        if (mode == 'add') {
            if (addblock) {
                querybag.setItem('new', null, {jc:'and'}, {_position:pos});
                querybag.setItem('new.c_0', null, {jc:'and'});
            } else {
                querybag.setItem('new', null, {jc:'and'}, {_position:pos});
            }
        }
        else {
            querybag.delItem('#' + pos);
        }
        var nodes = querybag.getNodes();
        for (var i = 0; i < nodes.length; i++) {
            nodes[i]['label'] = 'c_' + i;
        }
        ;
        this.buildQueryPane();
    },
    createQuery:function(pars) {
        var querybag = this.sourceNode.getRelativeData('.query.where');
        querybag.clear();
        querybag.setItem('c_0', 0);
        querybag.setItem('c_0', pars.val, {op:pars.op,
            column:pars.column,
            op_caption:this.getCaption('op', pars),
            column_caption:this.getCaption('column', pars)});
        this.buildQueryPane();
    },
    cleanQueryPane:function() {
        var querybag = this.sourceNode.getRelativeData('.query.where');
        var wrongLinesPathlist = [];
        var cb = function(node) {
            var attr = node.attr;
            if (!attr.op || !attr.column) {
                if (!(node.getValue() instanceof gnr.GnrBag)) {
                    wrongLinesPathlist.push(node.getFullpath(null, querybag));
                }
            }
        };
        querybag.walk(cb);
        for (var i = 0; i < wrongLinesPathlist.length; i++) {
            querybag.delItem(wrongLinesPathlist[i]);
        }
        this.buildQueryPane();
    },
    
    getHelper:function(sourceNode){
        var op = sourceNode.getRelativeData(sourceNode.attr.value+'?op');
        if(op in this.helper_op_dict){
            console.log('get helper for',op);
        }
        
        //if(GET .c_0?op in genro.querybuilder('%s').helper_op_dict){FIRE .#parent.#parent.helper.queryrow='c_0';}
    },

    _buildQueryRow: function(tr, node, i, level) {
        var relpath = '.' + node.label;
        var val = node.getValue();
        var attr = node.getAttr();
        var noValueIndicator = "<span >&nbsp;</span>";
        attr.jc_caption = this.getCaption('jc', attr);
        attr.not_caption = this.getCaption('not', attr);
        cell = tr._('td');
        if (i > 0) {
            cell._('div', {_class:'qb_div qb_jc floatingPopup',connectedMenu:this.relativeId('qb_jc_menu'),selected_fullpath:relpath + '?jc',
                selected_caption:relpath + '?jc_caption',innerHTML:'^' + relpath + '?jc_caption'});
        } else {
            attr.jc = '';
            //cell._('div',{_class:'qb_jc_noicn'});
        }
        tr._('td')._('div', {_class:'qb_div qb_not floatingPopup', connectedMenu:this.relativeId('qb_not_menu'),selected_fullpath:relpath + '?not',
            selected_caption:relpath + '?not_caption',innerHTML:'^' + relpath + '?not_caption'});

        if (val instanceof gnr.GnrBag) {
            cell = tr._('td', {colspan:'3',datapath:relpath});
            this._buildQueryGroup(cell, val, level + 1);
        } else {
            var op_menu_id = 'qb_op_menu_' + (this.getDtypeGroup(attr.column_dtype || 'T'));
            attr.column_caption = this.getCaption('column', attr);
            attr.op_caption = this.getCaption('op', attr);
            var tdattr = {_class:'qb_div qb_field floatingPopup',connectedMenu:this.relativeId('qb_fields_menu'),relpath:node.label,dropTarget:true,
                            innerHTML:'^' + relpath + '?column_caption'};
            tdattr['onDrop_gnrdbfld_'+this.maintable.replace('.','_')]="console.log(arguments);genro.querybuilder('"+this.mangler+"').onChangedQueryColumn(this,data,'" + node.label + "');"
            tr._('td')._('div', tdattr);
            tr._('td')._('div', {_class:'qb_div qb_op floatingPopup',
                connectedMenu:'==genro.querybuilder("'+this.mangler+'").getOpMenuId(_dtype);',
                _dtype:'^' + relpath + '?column_dtype',selected_fullpath:relpath + '?op',
                selected_caption: relpath + '?op_caption',innerHTML:'^' + relpath + '?op_caption',
                id:'_op_' + node.getStringId(),_fired:'^' + relpath + '?column_dtype'});
            var valtd = tr._('td')._('div', {_class:'qb_div qb_value'});

            var input_attrs = {value:'^' + relpath, width:'10em',
                _autoselect:true,_class:'st_conditionValue',validate_onAccept:'genro.queryanalyzer("'+this.mangler+'").checkQueryLineValue(this,value);'};
            if (attr.value_caption) {
                var fld_id = node.getStringId() + '_value';
                input_attrs['id'] = fld_id;
                input_attrs['connect__onMouse'] = 'genro.dom.ghostOnEvent($1);';
                valtd._('label', {_for:fld_id,_class:'ghostlabel','id':fld_id + '_label'})._('span', {innerHTML:val ? '' : attr.value_caption});
            }
            input_attrs.position = 'relative';
            input_attrs.padding_right = '10px';
            that = this;
            input_attrs.connect_onclick = function(){
                that.getHelper(this);
            }
            
            //"var op = GET " + relpath + "?op;if(op in genro.querybuilder('"+this.mangler+"').helper_op_dict){FIRE .#parent.#parent.helper.queryrow='" + relpath.slice(1) + "';}";
            input_attrs.disabled = "==(_op in _helperOp);";
            input_attrs._helperOp = this.helper_op_dict;
            input_attrs._op = '^' + relpath + '?op';
            value_input = valtd._('textbox', input_attrs);
            value_input._('div', {innerHTML:'^' + relpath,hidden:'==!(_op in _helperOp)',
                _op:'^' + relpath + '?op',_helperOp:this.helper_op_dict,
                _class:'helperField'});
        }
        tr._('td')._('div', {connect_onclick:dojo.hitch(this, 'addDelFunc', 'add', i + 1), _class:'qb_btn qb_add'});
        if (i > 0) {
            tr._('td')._('div', {connect_onclick:dojo.hitch(this, 'addDelFunc', 'del', i), _class:'qb_btn qb_del'});
        }
    },

    _buildQueryGroup: function(sourceNode, querydata, level) {
        var bagnodes = querydata.getNodes();
        var node;
        if (level % 2 == 0) {
            oddeven = 'qb_group qb_group_even';
        } else {
            oddeven = 'qb_group qb_group_odd';
        }
        var container = sourceNode._('div', {_class:oddeven});
        var tbl = container._('table', {_class:'qb_table'})._('tbody');
        for (var i = 0; i < bagnodes.length; i++) {
            node = bagnodes[i];
            this._buildQueryRow(tbl._('tr', {_class:'^.' + node.label + '?css_class'}), bagnodes[i], i, level);
        }
    }
    
});
dojo.declare("gnr.GnrQueryAnalyzer", null, {
    constructor: function(sourceNode, table,mangler) {
        if (!genro.queryanalyzer){
            genro.queryanalyzer = function(mangler){
                return genro.nodeById(mangler+'_'+'queryscripts')._queryanalyzer;
            }
        }
        this.mangler = mangler;
        this.maintable = table;
        this.sourceNode = sourceNode;
        this.wherepath = this.sourceNode.absDatapath()+'.query.where';
    },
    checkQueryLineValue:function(sourceNode, value) {
        if (value.indexOf('?') == 0) {
            var relpath = sourceNode.attr.value.slice(1);
            if (value == '?') {
                sourceNode.setRelativeData(relpath + '?css_class', null);
                sourceNode.setRelativeData(relpath, null);
                sourceNode.setRelativeData(relpath + '?value_caption', null);
            } else {
                sourceNode.setRelativeData(relpath, null);
                sourceNode.setRelativeData(relpath + '?css_class', 'queryAsk');
                sourceNode.setRelativeData(relpath + '?value_caption', value.slice(1));
                sourceNode.setRelativeData(relpath + '?dtype', genro._('gnr.qb.fieldstree.' + sourceNode.attr.column + '?dtype'));
            }
        }
    },
    translateQueryPars: function() {
        var currwhere = genro._(this.wherepath);
        var parslist = [];
        var cb = function(node, parslist, idx) {
            if (node.attr.value_caption) {
                var relpath = node.getFullpath('static', currwhere);
                var result = objectUpdate({}, node.attr);
                result['relpath'] = relpath;
                parslist.push(result);
            }
        };
        currwhere.walk(cb, 'static', parslist);
        return parslist;
    },
    buildParsDialog:function(parslist) {
        genro.src.getNode()._('div', '_dlg_ask_querypars');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var action = "genro.wdgById('_dlg_ask_querypars').hide(); FIRE .#parent.#parent.runQueryDo;";
        var node = genro.src.getNode('_dlg_ask_querypars').clearValue().freeze();
        var dlg = node._('dialog', {nodeId:'_dlg_ask_querypars',title:'Complete query',datapath:this.wherepath});

        var bc = dlg._('borderContainer', {_class:'pbl_dialog_center',
            height:parslist.length * 30 + 100 + 'px',
            width:'350px'});
        var center = bc._('contentPane', {'region':'center'});
        var bottom = bc._('contentPane', {'region':'bottom',_class:'dialog_bottom'});
        var queryform = center._('div', {padding:'10px',font_size:'.8'})._('table', {border_spacing:'8px',onEnter:action,margin_top:'10px'})._('tbody');

        var tr, attrs;
        for (var i = 0; i < parslist.length; i++) {
            attrs = parslist[i];
            tr = queryform._('tr');
            tr._('td')._('div', {'innerHTML':attrs['value_caption'] + ':',_class:'gnrfieldlabel',width:'10em'});
            tr._('td')._('textBox', {'value':'^.' + attrs['relpath'], width:'12em', _class:'gnrfield',tabindex:i});
        }
        ;
        bottom._('button', {label:'Cancel',baseClass:'bottom_btn','float':'left',
            action:"genro.wdgById('_dlg_ask_querypars').hide();SET .#parent.#parent.queryRunning = false;SET .#parent.#parent.gridpage = 0;"});
        bottom._('button', {label:'Confirm',baseClass:'bottom_btn','float':'right',action:action});
        bottom._('button', {label:'Count',baseClass:'bottom_btn','float':'right',action:'FIRE .#parent.#parent.showQueryCountDlg;'});

        node.unfreeze();
        genro.wdgById('_dlg_ask_querypars').show();

    }
});