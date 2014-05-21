dojo.declare("gnr.QueryManager", null, {
    constructor: function(th,sourceNode, maintable) {
        this.th = th;
        this.sourceNode = sourceNode;
        this.maintable = maintable;
        this.tablecode = maintable.replace('.','_');
        this.th_root = this.th.th_root;
        this.frameNode = genro.getFrameNode(this.th_root);
        this.wherepath = this.sourceNode.absDatapath('.query.where');
        this.dtypes_dict = {'A':'alpha','T':'alpha','C':'alpha','X':'alpha',
            'PHONETIC':'alpha_phonetic',
            'D':'date','DH':'date','I':'number',
            'L':'number','N':'number','R':'number','B':'boolean','TAG':'tagged'};
        this.helper_op_dict = {'in':'in','tagged':'tagged'};
        
        
        genro.setDataFromRemote('gnr.qb.'+this.tablecode+'.fieldsmenu', "relationExplorer", {table:maintable, omit:'_*'});
        genro.setDataFromRemote('gnr.qb.sqlop', "getSqlOperators");
    },

    getDtypeGroup:function(dtype) {
        var dflt = ('other_' + dtype).toLowerCase();
        var dflt = 'other';
        return this.dtypes_dict[dtype] || dflt;
    },
    
    relativeId:function(id){
        if(this.th_root){
             return this.th_root + '_' + id;
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
            action:"TH('"+this.th_root+"').querymanager.onChangedQueryColumn($2,$1,$2.attr.relpath);"});

        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.op',id:this.relativeId('qb_op_menu')});

        var opmenu_types = ['alpha','alpha_phonetic','date','number','other','boolean','unselected_column'];
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
                //
               //var tnode = this.treefield.getNode(val);
               //if (tnode) {
               //    return tnode.attr.fullcaption || tnode.column || '&nbsp;';
               //}
               //console.log('missing column while looking for caption:' + val);
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
            contextNode.setRelativeData(relpath + '?column_dtype', column_attr.query_dtype || column_attr.dtype);
            var default_op = genro._('gnr.qb.sqlop.op_spec.' + this.getDtypeGroup(column_attr.dtype) + '.#0');
            if (default_op) {
                contextNode.setRelativeData(relpath + '?op', default_op);
                contextNode.setRelativeData(relpath + '?op_caption',
                        genro.getDataNode('gnr.qb.sqlop.op.' + default_op).attr.caption);
            }
        }
        contextNode.setRelativeData(relpath, '');
        contextNode.setRelativeData(relpath+'?value_caption', '');
    },


    queryEditor:function(open){
        var that = this;
        if(!open){
            var currentQuery = this.sourceNode.getRelativeData('.query.currentQuery');
            if(currentQuery=='__basequery__' || currentQuery=='__newquery__'){
                this.sourceNode.setRelativeData('.query.queryAttributes.extended',false);
            }
            var palette = genro.wdgById(this.th_root+'_queryEditor_floating');
            if(palette){
                palette.close();
            }
            return;
        }
        var datapath = this.sourceNode.absDatapath();
        genro.src.getNode()._('div', '_advancedquery_');
        var node = genro.src.getNode('_advancedquery_').clearValue();
        node.freeze();
        var pane = node._('palettePane',{paletteCode:this.th_root+'_queryEditor',
                                        'title':'Query Tool',dockTo:false,
                                        datapath:datapath+'.query',
                                        height:'300px',width:'450px',
                                        palette_connect_close:function(){
                                            that.sourceNode.setRelativeData('.query.queryEditor',false);
                                        }});
        var frame = pane._('framePane',{'frameCode':'_innerframe_#',
                                        gradient_from:'#E5E5E5',gradient_to:'#EDEDED',gradient_deg:'-90'});
        var topbar = frame._('slotBar',{'slots':'queryname,*,favoritebtn,savebtn,deletebtn,10,runbtn',toolbar:true,'side':'top'});
        var qtitle = topbar._('div','queryname',{innerHTML:'^.queryAttributes.caption',
                                                 padding_right:'10px',padding_left:'2px',
                                    color:'#555',font_weight:'bold',_class:'floatingPopup',cursor:'pointer'})
        qtitle._('menu',{'_class':'smallmenu',storepath:'.savedqueries',modifiers:'*',action:'SET .currentQuery = $1.fullpath;'});
        topbar._('slotButton','savebtn',{'label':_T('!!Save'),iconClass:'iconbox save',action:function(){that.saveQuery()}});
        topbar._('slotButton','deletebtn',{'label':_T('!!Delete'),iconClass:'iconbox trash',action:'FIRE .delete;',disabled:'^.queryAttributes.pkey?=!#v'});
        
        topbar._('slotButton','favoritebtn',{'label':_T('!!Default Query'),action:function(){that.setCurrentAsDefault()},
                               iconClass:'th_favoriteIcon iconbox star'});
                               
        topbar._('slotButton','runbtn',{'label':_T('!!Run Query'),action:'FIRE .#parent.runQuery;',
                               iconClass:'iconbox run'});


        var editorRoot = frame._('div',{datapath:'.where',margin:'2px'});
        node.unfreeze();
        this._editorRoot = editorRoot.getParentNode();
        this.buildQueryPane();
        this.checkFavorite();
    },
    saveQuery:function(){
        var datapath =  this.sourceNode.absDatapath('.query.queryAttributes');
        var code = this.sourceNode.getRelativeData('.query.queryAttributes.code');
        var data = this.sourceNode.getRelativeData('.query.where')
        var that = this;
        saveCb = function(dlg) {
            genro.serverCall('_table.adm.userobject.saveUserObject',
            {'objtype':'query','table':that.maintable,'data':data,metadata:genro.getData(datapath)},
            function(result) {
                dlg.close_action();
                that.sourceNode.setRelativeData('.query.currentQuery',result.attr.code);
                that.refreshQueryMenues();
            });
        };
        genro.dev.userObjectDialog(code ? 'Save Query ' + code : 'Save New Query',datapath,saveCb);
    },
    
    onChangedQuery: function(currentQuery){
        var sourceNode = this.sourceNode;
        var that = this;
        var finalize = function(where,run){
            sourceNode.setRelativeData('.query.where',where);
            that.checkFavorite();
            if(run){
                sourceNode.fireEvent('.runQuery'); //provvisorio
            }
        }
        if (currentQuery=='__newquery__'){
            sourceNode.setRelativeData('.query.queryAttributes',new gnr.GnrBag({extended:true,caption:_T('!!New Query')}));
            finalize(new gnr.GnrBag());
            return
        }
        var queryBag = this.sourceNode.getRelativeData('.query.menu');
        var queryAttributes= queryBag.getNode(currentQuery).attr;
        //queryAttributes['id'] = queryAttributes['pkey']
        if(!('extended' in queryAttributes)){
            queryAttributes.extended = true;
        }
        sourceNode.setRelativeData('.query.queryAttributes',new gnr.GnrBag(queryAttributes));
        if(currentQuery=='__basequery__'){
            finalize(this.sourceNode.getRelativeData('.baseQuery').deepCopy(),false);
        }
        else if(queryAttributes.pkey){
            genro.serverCall('_table.adm.userobject.loadUserObject',{pkey:queryAttributes.pkey,table:this.maintable},function(result){
                finalize(result._value.deepCopy(),!sourceNode.getRelativeData('.query.queryEditor'));
            })
        }else if(queryAttributes.selectmethod){
            finalize(new gnr.GnrBag(),true);
        }
    },
    
    buildQueryPane: function() {
        this._editorRoot.clearValue();
        this._editorRoot.freeze();
        this._buildQueryGroup(this._editorRoot, this.sourceNode.getRelativeData('.query.where'), 0);
        this._editorRoot.unfreeze();
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
    cleanQueryPane:function(querybag) {
        //var querybag = this.sourceNode.getRelativeData('.query.where');
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
        if(wrongLinesPathlist.length>0){
            for (var i = 0; i < wrongLinesPathlist.length; i++) {
                querybag.delItem(wrongLinesPathlist[i]);
            }
            this.buildQueryPane();
        }
    },
    
    getHelper:function(sourceNode){
        var op = sourceNode.getRelativeData(sourceNode.attr.relpath+'?op');
        if(op in this.helper_op_dict){
            this['helper_'+op](sourceNode)
        }
    },
    
    helper_in:function(rowNode){
        var dlg = genro.dlg.quickDialog(_T('Helper in'),{width:'280px',autoSize:true});
        var center = dlg.center;
        var relpath = rowNode.attr.relpath;
        var val = rowNode.getRelativeData(relpath);
        var caption = rowNode.getRelativeData(relpath+'?value_caption') ||'';
        var currentSetCaption =_T('New Set');
        if(caption.indexOf('set:')==0){
            currentSetCaption = caption.replace('set:','');
        }
        var that = this;
        var datapath = this.sourceNode.absDatapath('.query.helper.in');
        var helperBag = this.sourceNode.getRelativeData('.query.helper.in');
        helperBag.setItem('items',val?val.replace(/,+/g,'\n'):null);
        helperBag.setItem('currentsetAttr',new gnr.GnrBag({caption:currentSetCaption}))
        var toolbar = center._('slotBar',{slots:'menuset,*,saveset,delset',toolbar:true,datapath:datapath});
        var setTitle = toolbar._('div','menuset',{innerHTML:'^.currentsetAttr.caption',cursor:'pointer'});
        var resetSet = function(){
            helperBag.setItem('currentsetAttr',new gnr.GnrBag({caption:_T('New Set')}));
            helperBag.setItem('items','')
            rowNode.setRelativeData(relpath+'?value_caption','');
        }
        setTitle._('menu',{'_class':'smallmenu',storepath:'.savedsets',modifiers:'*',
                            action:function(item){
                                var code = item.fullpath;
                                if(code!='__newset__'){
                                    genro.serverCall('_table.adm.userobject.loadUserObject',{pkey:item.pkey,table:that.maintable},
                                    function(result){
                                        helperBag.setItem('items',result._value);
                                        result.attr.caption = result.attr.description;
                                        helperBag.setItem('currentsetAttr',new gnr.GnrBag(result.attr));
                                    });
                                }else{
                                    resetSet();
                                }
                            }});
        var saveAction = function(){
            var savepath = datapath+'.currentsetAttr';
            var kw = {'objtype':'list_in','table':that.maintable,
                     'data':helperBag.getItem('items'),
                     metadata:genro.getData(savepath)}
            genro.dev.userObjectDialog(_T('Save set'),savepath,function(dialog) {
                genro.serverCall('_table.adm.userobject.saveUserObject',kw,function(result) {
                    helperBag.setItem('currentsetAttr',new gnr.GnrBag(result.attr));
                    dialog.close_action();
                });
            });
        };
        toolbar._('slotButton','saveset',{iconClass:'iconbox save',action:saveAction});
        toolbar._('slotButton','delset',{iconClass:'iconbox trash',disabled:'^.currentsetAttr.id?=!#v',
                    action:function(){
                        genro.serverCall('_table.adm.userobject.deleteUserObject',{pkey:helperBag.getItem('currentsetAttr.id')},resetSet);
                    }});
        var box = center._('div', {datapath:datapath,padding:'5px'});
        var fb = genro.dev.formbuilder(box, 1, {border_spacing:'6px'});
        fb.addField('simpleTextArea', {lbl:_T("IN"),value:'^.items',
                                        width:'20em',height:'15ex',colspan:2,lbl_vertical_align:'top'});
        var footer = dlg.bottom._('slotBar',{slots:'*,cancel,confirm'});
        footer._('button','cancel',{label:_T('Cancel'),'action':dlg.close_action});
        footer._('button','confirm',{label:_T('Confirm'),action:function(){
            var items = helperBag.getItem('items');
            var splitPattern=/\s*[\n\,]+\s*/g;
            var cleanPattern=/(^\s*[\n\,]*\s*|\s*[\n\,]*\s*$)/g;
            items=items.replace(cleanPattern,'').split(splitPattern).join(',');
            var desc =helperBag.getItem('currentsetAttr.description');
            rowNode.setRelativeData(relpath+'?value_caption',desc?'set:'+desc:items);
            rowNode.setRelativeData(relpath,items);
            dlg.close_action();
        }});
        dlg.show_action();
        
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
            var curr_th = "TH('"+this.th_root+"')";
            attr.column_caption = this.getCaption('column', attr);
            attr.op_caption = this.getCaption('op', attr);
            var tdattr = {_class:'qb_div qb_field floatingPopup',connectedMenu:this.relativeId('qb_fields_menu'),relpath:node.label,dropTarget:true,
                            innerHTML:'^' + relpath + '?column_caption'};
            tdattr['onDrop_gnrdbfld_'+this.maintable.replace('.','_')]=curr_th+".querymanager.onChangedQueryColumn(this,data,'" + node.label + "');"
            tr._('td')._('div', tdattr);
            tr._('td')._('div', {_class:'qb_div qb_op floatingPopup',
                connectedMenu:'==_qb.getOpMenuId(_dtype);',
                _dtype:'^' + relpath + '?column_dtype',selected_fullpath:relpath + '?op',
                selected_caption: relpath + '?op_caption',innerHTML:'^' + relpath + '?op_caption',
                id:'_op_' + node.getStringId(),_fired:'^' + relpath + '?column_dtype',_qb:this});
            var valtd = tr._('td')._('div', {_class:'qb_value'});

            var input_attrs = {value:'^' + relpath + '?value_caption', width:'10em',relpath:relpath,
                _autoselect:true,_class:'st_conditionValue',validate_onAccept:curr_th+'.querymanager.checkQueryLineValue(this,value);'};
            input_attrs.position = 'relative';
            that = this;
            input_attrs.connect_onclick = function(){
                that.getHelper(this);
            }
            
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
        var sourceNode = this.sourceNode;
        var tbl = container._('table', {_class:'qb_table'})._('tbody');
        for (var i = 0; i < bagnodes.length; i++) {
            node = bagnodes[i];
            this._buildQueryRow(tbl._('tr', {_class:'^.' + node.label + '?css_class'}), bagnodes[i], i, level);
        }
    },

    checkQueryLineValue:function(sourceNode, value) {
        var relpath = sourceNode.attr.relpath;
        if (value.indexOf('set:')==0){
            return;
        }
        if (value.indexOf('?') == 0) {
            sourceNode.setRelativeData(relpath, null);
            sourceNode.setRelativeData(relpath + '?css_class', 'queryAsk');
            sourceNode.setRelativeData(relpath + '?dtype',sourceNode.getRelativeData(relpath + '?column_dtype'));
        }else{
            sourceNode.setRelativeData(relpath,value);
            sourceNode.setRelativeData(relpath + '?css_class', null);
        }
    },
    translateQueryPars: function() {
        var currwhere = genro._(this.wherepath);
        var parslist = [];
        var cb = function(node, parslist, idx) {
            if (node.attr.value_caption) {
                if(node.attr.value_caption[0]=='?'){
                     var relpath = node.getFullpath('static', currwhere);
                     var result = objectUpdate({}, node.attr);
                     result['relpath'] = relpath;
                    parslist.push(result);
                }else if(node.attr.value_caption && node.attr.value_caption.indexOf('set:')==0){
                    return;
                }else{
                    node.setValue(node.attr.value_caption);
                }
            }
        };
        currwhere.walk(cb, 'static', parslist);
        return parslist;
    },
    onQueryCalling:function(querybag,selectmethod){
        var parslist=[];
        var sourceNode = this.sourceNode;
        if(selectmethod){
            var currAttrs = this.sourceNode.getRelativeData('.query.queryAttributes').asDict();
            var params = objectExtract(currAttrs,'parameter_*');
            var dflt = objectExtract(currAttrs,'default_*');
            for(var k in params){
                parslist.push({value_caption:'?'+(k in dflt? params[k]+'|'+dflt[k] : params[k]), relpath:'parameter_'+k});
            }
        }else if(querybag.getItem("#0?column")){
            this.cleanQueryPane(querybag); 
            var parslist = this.translateQueryPars();
        }
        if (parslist.length>0){
            this.buildParsDialog(parslist);
        }else{
            this.runQuery();
        }
    },
    storeKey:function(){
        return 'view_' + genro.getData('gnr.pagename') + '_' + this.th_root +'_query';
    },
    setCurrentAsDefault:function(){
        genro.setInStorage("local", this.storeKey(), this.sourceNode.getRelativeData('.query.currentQuery'));
        this.checkFavorite();
    },
    checkFavorite:function(){
        var currPath = this.sourceNode.getRelativeData('.query.currentQuery');
        var currfavorite = genro.getFromStorage("local", this.storeKey());
        this.sourceNode.setRelativeData('.query.favoriteQueryPath',currfavorite);
        this.refreshQueryMenues();
        if(this._editorRoot){
            genro.dom.setClass(this._editorRoot.attributeOwnerNode('frameCode'),
                            'th_isFavoriteQuery',currfavorite==currPath);
        }
    },
    refreshQueryMenues:function(){
        this.sourceNode.getRelativeData('.query').getNode('menu').getResolver().reset();
        //this.sourceNode.getRelativeData('.query.savedqueries').getParentNode().getResolver().reset();
    },
    
    setFavoriteQuery:function(){
        var favoritePath = genro.getFromStorage("local", this.storeKey());
        if(favoritePath && !this.sourceNode.getRelativeData('.query.menu').getNode(favoritePath)){
            favoritePath = null;
        };
        favoritePath = favoritePath || '__basequery__';
        this.sourceNode.setRelativeData('.query.currentQuery',favoritePath);
        this.setCurrentAsDefault();
    },
    
    runQuery:function(){
        var sourceNode = this.sourceNode;
        genro.fireAfter(sourceNode.absDatapath('.runQueryDo'),true,500);
    },
    
    buildParsDialog:function(parslist) {
        var sourceNode = this.sourceNode;
        var dlg = genro.dlg.quickDialog('Complete query',{datapath:this.wherepath,width:'250px',autoSize:true});
        var that = this;
        var confirm = function(){
            that.runQuery()
            dlg.close_action();
        };
        var cancel = function(){
            dlg.close_action();
        };
        var count = function(){
            sourceNode.fireEvent('.showQueryCountDlg');
        };

        var center = dlg.center._('div',{padding:'10px'});
        var bottom = dlg.bottom._('slotBar',{'slots':'cancel,*,confirm'});
        var queryform = genro.dev.formbuilder(center,1,{border_spacing:'8px',onEnter:confirm,margin_top:'10px'})
        var tr, attrs;
        for (var i = 0; i < parslist.length; i++) {
            attrs = parslist[i];
            var lbl = attrs['value_caption'].slice(1);
            var dflt;
            if(lbl.indexOf('|')){
                var l = lbl.split('|');
                lbl=l[0];
                dflt = l[1] ;
            }
            if(dflt){
                sourceNode.setRelativeData(this.wherepath+'.'+attrs['relpath'],dflt);
            }
            queryform.addField('textbox',{lbl:lbl,value:'^.' + attrs['relpath'], width:'12em',tabindex:i})
        }
        bottom._('button', 'cancel',{label:'Cancel',baseClass:'bottom_btn',action:cancel});
        bottom._('button', 'confirm',{label:'Confirm',baseClass:'bottom_btn',action:confirm});
        //bottom._('button', 'countbtn',{label:'Count',baseClass:'bottom_btn',action:count});
        dlg.show_action();
    }
});

dojo.declare("gnr.THDatasetManager", null, {
    constructor: function(th,sourceNode, maintable) {
        this.th = th;
        this.sourceNode = sourceNode;
        this.maintable = maintable;
        this.tablecode = maintable.replace('.','_');
        this.th_root = this.th.th_root;
        this.frameNode = genro.getFrameNode(this.th_root);
        this.grid = genro.wdgById(this.th_root+'_grid');
    },
    datasetsMenu:function(){
        var result = new gnr.GnrBag();
        var that = this;
        result.setItem('r_0',null,{caption:_T('New set column'),
                                   action:function(){that.newSetColumn();}}
                                   );
        var grid = this.grid;
        var cellmap = grid.cellmap;
        var sn = grid.sourceNode;
        var currentsets = sn.getRelativeData(sn.attr.userSets);
        if(currentsets.len()){
            result.setItem('r_1',null,{caption:'-'});
            currentsets.forEach(function(setNode){
                var kw = cellmap[setNode.label];
                result.setItem(setNode.label,null,{caption:kw['name'],action:function(n,item){
                    that.sourceNode.setRelativeData('.query.pkeys',currentsets.getItem(n.fullpath));
                    that.sourceNode.fireEvent('.runQuery');
                }});
            });

            
            if(objectKeys(currentsets).length>1 && false){
                result.setItem('r_2',null,{caption:'-'});
                result.setItem('union',null,{caption:_T('Union'),action:function(){that.unionDataSet()}});
                result.setItem('intersect',null,{caption:_T('Intersect'),action:function(){that.intersectDataSet()}});
            }
//
        }
        //result.setItem('r_2',null,{caption:'-'});
        //result.setItem('r_3',null,{caption:_T('Clear clipboard')});

        return result;
    },

    unionDataSet:function(){
        var grid = this.grid;
        var wdg_values = '';
        for(var fieldname in currentsets){
            var kw = grid.cellmap[fieldname];
            wdg_values+=fieldname;
            wdg_values += ':'+ kw['name'];

        }
        //genro.dlg.prompt(_T('New dataset'), {msg:_T('Union between dataset'),
        //                                wdg:'checkBoxText'
        //                                action:
        //                                    function(name){
        //                                        grid.addNewSetColumn({name:name});
        //                                    }
        //                                });
    },
    newSetColumn:function(){
        var grid = this.grid;
        genro.dlg.prompt(_T('New dataset'), {msg:_T('Add a new dataset column'),
                                        lbl:'Name',
                                        action:
                                            function(name){
                                                grid.addNewSetColumn({name:name});
                                            }
                                        });
    }

});


