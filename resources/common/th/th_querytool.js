dojo.declare("gnr.FakeTableHandler",null,{
    constructor: function(sourceNode) {
        this.table = objectPop(sourceNode.attr,'query_table');
        this.sourceNode = sourceNode;
        this.th_root = sourceNode.attr.nodeId || sourceNode.getStringId();
        var faketh = TH(this.th_root);
        faketh.querymanager = new gnr.QueryManager(this,sourceNode,this.table,true);
        faketh.querymanager._editorRoot = function(){
            sourceNode._value.popNode('where');
            return sourceNode._('div','where',{datapath:'.query.where'});
        };
        var that = this;
        var startup = function(){
            if(!genro.getDataNode('gnr.qb.sqlop')){
                genro.serverCall('getSqlOperators',{},function(result){
                    genro.setData('gnr.qb.sqlop',result);
                    that.createMenu();
                    that.createQueryPane();
                });
            }else{
                setTimeout(function(){
                    that.createMenu();
                    that.createQueryPane();
                },1);
            }
        };
        var fieldsmenupath = 'gnr.qb.'+this.table.replace('.','_')+'.fieldsmenu';
        if (!genro.getDataNode(fieldsmenupath)){
            genro.serverCall('relationExplorer',{table:this.table, omit:'_*',item_type:'QTREE'},function(result){
                genro.setData(fieldsmenupath,result);
                startup();
            });
        }else{
            startup();
        }
    },

    createMenu:function(){
        TH(this.th_root).querymanager.createMenuesQueryEditor();
    },
    createQueryPane:function(){
        var querybag = this.sourceNode.getRelativeData('.query.where');
        if(!querybag){
            querybag = new gnr.GnrBag();
            querybag.setItem('c_0', null, 
                            {op:null,column:null,
                             op_caption:null,
                             column_caption:null});
            this.sourceNode.setRelativeData('.query.where',querybag);
        }
        var that = this;
        this.sourceNode.watch(function(){
            return genro.dom.isVisible(genro.nodeById(that.th_root));
        },function(){
            TH(that.th_root).querymanager.buildQueryPane();
        });
        

        
    }
});

dojo.declare("gnr.QueryManager", null, {
    constructor: function(th,sourceNode, maintable,faketh) {
        this.th = th;
        this.sourceNode = sourceNode;
        this.maintable = maintable;
        this.tablecode = maintable.replace('.','_');
        this.th_root = this.th.th_root;
        this.frameNode = genro.getFrameNode(this.th_root);
        this.wherepath = this.sourceNode.absDatapath('.query.where');
        this.dtypes_dict = {'A':'alpha','T':'alpha','C':'alpha','X':'alpha',
            'PHONETIC':'alpha_phonetic',
            'D':'date','DH':'date','DHZ':'date','I':'number',
            'L':'number','N':'number','R':'number','B':'boolean','TAG':'tagged'};
        this.helper_op_dict = {'in':'in','tagged':'tagged'};
        var qm = this;
        if(faketh){
            return;
        }
        this.sourceNode.delayedCall(function(){
            qm.createMenuesQueryEditor();
            dijit.byId(qm.relativeId('qb_fields_menu')).bindDomNode(genro.domById(qm.relativeId('fastQueryColumn')));
            dijit.byId(qm.relativeId('qb_not_menu')).bindDomNode(genro.domById(qm.relativeId('fastQueryNot')));
            dijit.byId(qm.relativeId('qb_queryModes_menu')).bindDomNode(genro.domById(qm.relativeId('searchMenu_a')));
            qm.setFavoriteQuery();
        });
        
        //genro.setDataFromRemote('gnr.qb.'+this.tablecode+'.fieldsmenu', "relationExplorer", {table:maintable, omit:'_*'});
        //genro.setDataFromRemote('gnr.qb.'+this.tablecode+'.fieldsmenu_tree', "relationExplorer", {table:maintable, omit:'_*'});
        //genro.setDataFromRemote('gnr.qb.sqlop', "getSqlOperators");
    },

    getDtypeGroup:function(dtype) {
        var dflt = ('other_' + dtype).toLowerCase();
        dflt = 'other';
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
    
    createMenuesQueryEditor: function() {
        genro.src.getNode()._('div', this.relativeId('_qbmenues'));
        var node = genro.src.getNode(this.relativeId('_qbmenues'));
        node.clearValue();
        node.freeze();
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.queryModes',
                                        id:this.relativeId('qb_queryModes_menu'),
                                       action:'$2.setRelativeData(".#parent.queryMode",$1.fullpath,{caption:$1.caption})'});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.jc',id:this.relativeId('qb_jc_menu')});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.not',id:this.relativeId('qb_not_menu')});
        var querymanager = this;
        node._('tree', {storepath:'gnr.qb.'+this.tablecode+'.fieldsmenu',
                        popup_id:this.relativeId('qb_fields_menu'),popup:true,
                        popup_closeEvent:'onClick',
                        connect__updateSelect:function(item,node,evt){
                            if(item.attr.dtype=='RM'){
                                return;
                            }
                            var originalContextNode = this.widget.originalContextTarget.sourceNode;
                            querymanager.onChangedQueryColumn(originalContextNode,item.attr,originalContextNode.attr.relpath);
                        }});

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
        label = label || 'c_0';
        var relpath = '.' + label;
        this.onChangedQueryColumnDo(contextNode,relpath,column_attr);
    },

    onChangedQueryColumnDo:function(sourceNode,path,column_attr){
        var column = column_attr.fieldpath;
        var fullcaption = column_attr.fullcaption;
        var dtype = column_attr.dtype;
        if(column_attr.fkey){
            dtype = column_attr.fkey.dtype;
            var fc = fullcaption.split('/');
            var fl = column.split('.');
            var fkeyfield = fl[fl.length-1].slice(1);
            fl[fl.length-1] = fkeyfield;
            fc[fc.length-1] = fkeyfield;
            fullcaption = fc.join('/');
            column = fl.join('.');
            sourceNode.setRelativeData(path + '?column_relationTo', column_attr.one_relation);
        }else{
            sourceNode.setRelativeData(path + '?column_relationTo', null);
        }
        sourceNode.setRelativeData(path + '?column_caption', fullcaption);
        sourceNode.setRelativeData(path + '?column', column);
        var currentDtype = sourceNode.getRelativeData(path + '?column_dtype');
        if (currentDtype != dtype) {
            sourceNode.setRelativeData(path + '?column_dtype', column_attr.query_dtype || dtype);
            var default_op = genro._('gnr.qb.sqlop.op_spec.' + this.getDtypeGroup(dtype) + '.#0');
            if (default_op) {
                sourceNode.setRelativeData(path + '?op', default_op);
                sourceNode.setRelativeData(path + '?op_caption',
                        genro.getDataNode('gnr.qb.sqlop.op.' + default_op).attr.caption);
            }
            sourceNode.setRelativeData(path, '');
            sourceNode.setRelativeData(path+'?value_caption', '');
        }
        sourceNode.setRelativeData(path + '?_owner_package', column_attr._owner_package);
    },

    queryEditor:function(queryEditor){
        var that = this;
        var currentQuery = this.sourceNode.getRelativeData('.query.currentQuery');
        var palette = genro.wdgById(this.th_root+'_queryEditor_floating');
        if(!queryEditor){
            if(['__basequery__','__newquery__','__queryeditor__'].indexOf(currentQuery)>=0){
                let where = this.sourceNode.getRelativeData('.query.where');
                if(where.len()==1){
                    if(currentQuery=='__queryeditor__'){
                        this.sourceNode.setRelativeData('.query.currentQuery','__basequery__',{},false,false);
                    }
                    this.sourceNode.setRelativeData('.query.queryAttributes.caption',_T('Plain query'));
                    this.sourceNode.setRelativeData('.query.queryAttributes.extended',false);
                }
            }
            if(palette){
                palette.hide();
            }
            return;
        }
        if(palette){
            palette.show();
            return;
        }
        var datapath = this.sourceNode.absDatapath();
        genro.src.getNode()._('div', '_advancedquery_');
        var node = genro.src.getNode('_advancedquery_').clearValue();
        node.freeze();
        var pane = node._('palettePane',{paletteCode:this.th_root+'_queryEditor',
                                        'title':'Query Tool',dockTo:'dummyDock:open',
                                        datapath:datapath+'.query',
                                        height:'300px',width:'450px',
                                        selfsubscribe_hiding:function(){
                                            if(that.sourceNode.getRelativeData('.query.queryEditor')){
                                                that.sourceNode.setRelativeData('.query.queryEditor',false);
                                            }
                                        }});


        var frame = pane._('framePane',{'frameCode':'_innerframe_#',
                                        center_widget:'tabContainer'});
        var topbar = frame._('slotBar',{'slots':'queryname,*,favoritebtn,5,savebtn,deletebtn,10,runbtn',toolbar:true,'side':'top'});

        var qtitle = topbar._('div','queryname',{innerHTML:'^.queryAttributes.caption',padding_right:'10px',padding_left:'2px',
                            color:'#555',font_weight:'bold',_class:'floatingPopup',cursor:'pointer'});
        qtitle._('menu',{'_class':'smallmenu',storepath:'.savedqueries',modifiers:'*',action:'SET .currentQuery = $1.fullpath;'});
        topbar._('slotButton','savebtn',{'label':_T('Save'),iconClass:'iconbox save',action:function(){that.saveQuery();}});
        topbar._('slotButton','deletebtn',{'label':_T('Delete'),iconClass:'iconbox trash',action:'FIRE .delete;',disabled:'^.queryAttributes.pkey?=!#v'});
        
        topbar._('slotButton','favoritebtn',{'label':_T('Default Query'),action:function(){that.setCurrentAsDefault();},
                               iconClass:'th_favoriteIcon iconbox star'});
                               
        topbar._('slotButton','runbtn',{'label':_T('Run Query'),action:'FIRE .#parent.runQuery;',
                               iconClass:'iconbox run'});


        var editorRoot = frame._('contentPane',{title:_T('Query')})._('div',{datapath:'.where',margin:'2px',nodeId:this.th_root+'_queryEditorRoot'});
        if(currentQuery=='__querybysample__'){
            this.onChangedQuery('__newquery__');
        }
        this.joinConditions(frame._('contentPane',{title:_T('Join conditions'),margin:'2px'}));
        this.queryExtra(frame._('contentPane',{title:_T('Query Extra')}));
        this.multidbStorePicker(frame);
        node.unfreeze();
        this.buildQueryPane();
        this.checkFavorite();
    },
    joinConditions:function(pane){
        var g = pane._('quickGrid',{value:'^.joinConditions',
                                        addCheckBoxColumn:{field:'one_one',position:'>',name:'One'}
                                    });
        var t = g._('tools',{tools:'delrow,addrow',title:_T('Join conditions')});

        g._('column',{field:'relation',edit:true,width:'20em',name:'Relation'});
        
        var condition_cell = {field:'condition',width:'100%',name:'Condition'};
        condition_cell._customGetter = function(row){
                        return row.condition?row.condition.getFormattedValue():'-';
                    };
        condition_cell.edit = {modal:true,mode:'dialog'};
        var that = this;
        condition_cell.edit.contentCb = function(pane,kw){
            var sn = pane.getParentNode();
            var condbag = sn.getRelativeData();
            if(!condbag){
                condbag = new gnr.GnrBag();
                condbag.setItem('c_0', null, 
                                {op:null,column:null,
                                 op_caption:null,
                                 column_caption:null});
            }
            that._buildQueryGroup(pane._('div','root',{height:'300px',width:'600px',overflow:'auto'}),condbag, 0);
        };
        g._('column',condition_cell);
    },

    multidbStorePicker:function(parent){
        var multidbStoreQueryPicker = this.sourceNode.getRelativeData('.query.multidb.pickermethod');
        if (!multidbStoreQueryPicker){
            return;
        }
        var pane = parent._('contentPane',{title:_T('Db Stores'),_anchor:true,_workspace:true});
        pane._('ContentPane',{remote:multidbStoreQueryPicker});
    },

    queryExtra:function(parent){
        var bc = parent._('BorderContainer');
        var top = bc._('BorderContainer',{region:'top',height:'50%'});
        var topleft = top._('contentPane',{region:'center',_class:'pbl_roundedGroup',margin:'2px'});

        var fb = genro.dev.formbuilder(topleft, 1, {border_spacing:'6px'});

        fb.addField('numberTextBox',{lbl:_T('Limit'),value:'^.limit', width:'5em'});
        fb.addField('dbselect',{lbl:_T('Saved view'),tag:'dbselect',
                    hasDownArrow:true,value:'^.#parent.grid.currViewPath',
                    dbtable:'adm.userobject',width:'15em',alternatePkey:'code',
                    rowcaption:'$description',
                    condition:'$tbl=:tbl AND $objtype=:obj',condition_tbl:this.maintable,
                        condition_obj:'view'});
        //var topright = top._('borderContainer',{region:'right',_class:'pbl_roundedGroup',margin:'2px',width:'50%'});
        //topright._('contentPane',{region:'top',_class:'pbl_roundedGroupLabel',height:'20px'})._('div',{'innerHTML':'Extra query pars'});
        //topright._('contentPane',{region:'center'})._('MultiValueEditor',{value:'^.extraPars'});
        this.orderByGrid(bc._('FramePane',{frameCode:'_customOrderBy_#',_class:'pbl_roundedGroup',
                                region:'bottom',height:'50%',margin:'2px'}));
    },

    orderByGrid:function(frame){
        frame._('slotBar', {slots:'*,fieldsTree,*',width:'160px',
                            'fieldsTree_table':this.maintable,
                            'fieldsTree_checkPermissions':true,
                            'fieldsTree_height':'100%','splitter':true,
                            'border_left':'1px solid silver',
                            'side':'right'});
        frame._('slotBar',{slots:'2,vtitle,*',_class:'pbl_roundedGroupLabel',vtitle:_T('Order by'),side:'top'});
        var dropCode = 'gnrdbfld_'+this.tablecode;
        var gridkw = {value:'^.customOrderBy',selfDragRows:true,_class:'noheader noselect',
                     dropTarget_grid:dropCode+',gridcolumn'};

        gridkw['onDrop_'+dropCode] = function(p1,p2,kw){
            this.widget.addBagRow('#id', '*', this.widget.newBagRow({'fieldpath':kw.data.fieldpath,sorting:true}));
        };
        gridkw.onDrop_gridcolumn = function(p1,p2,kw){
            this.widget.addBagRow('#id', '*', this.widget.newBagRow({'fieldpath':kw.data.field,'field':kw.data.original_field,
                                                                    group_aggr:kw.data.group_aggr,sorting:true}));
        };
        var g = frame._('quickGrid',gridkw);
        g._('column',{field:'fieldpath',edit:{},width:'100%'});
        g._('column',{field:'sorting',dtype:'B',format_trueclass:'iconbox arrow_up',format_falseclass:"iconbox arrow_down",
                    format_onclick:'var r = this.widget.storebag().getItem("#"+$1.rowIndex);r.setItem("sorting",!r.getItem("sorting"));',
                    width:'3em'});
        g._('column',{field:'delrow',width:'3em',
                    format_isbutton:true,
                    format_onclick:'this.widget.storebag().popNode("#"+$1.rowIndex);',
                    format_buttonclass:'iconbox qb_del'});
    },

    viewAndExtra:function(frame){
        
    },


    pkeySetToQuery:function(pkeys){
        if(!pkeys){
            return;
        }
        this.sourceNode.setRelativeData('.query.currentQuery','__basequery__');

        var where = new gnr.GnrBag();
        var pkeyfield = this.sourceNode.getRelativeData('.table?pkey');
        where.setItem('c_'+0,pkeys,{column_dtype:'A',op:'in',op_caption:'in',jc:'and',not:'yes',not_caption:'&nbsp;',
                                        value_caption:pkeys,
                                        column:pkeyfield,column_caption:pkeyfield});
        this.sourceNode.setRelativeData('.query.where',where);
    },

    queryParsBag:function(){
        var queryPars = new gnr.GnrBag();
        this.translateQueryPars().forEach(function(pardict){
            queryPars.setItem(pardict.parcode,null,{
                lbl:pardict.lbl,
                field:pardict.column,
                relpath:pardict.relpath,
                op:pardict.op,
                dflt:pardict.dflt,
                parcode:pardict.parcode
            });
        });
        return queryPars;
    },

    prepareQueryData:function(){
        var where = this.sourceNode.getRelativeData('.query.where');
        var customOrderBy = this.sourceNode.getRelativeData('.query.customOrderBy');
        var currViewPath = this.sourceNode.getRelativeData('.grid.currViewPath');
        var queryLimit = this.sourceNode.getRelativeData('.query.limit');
        var extraPars = this.sourceNode.getRelativeData('.query.extraPars');
        var joinConditions = this.sourceNode.getRelativeData('.query.joinConditions');
        var multiStores = this.sourceNode.getRelativeData('.query.multiStores');
        var queryPars = this.queryParsBag();
        var data = new gnr.GnrBag();
        if(queryPars.len()){
            data.setItem('queryPars',queryPars);
        }
        data.setItem('extraPars',extraPars);
        data.setItem('where',where.deepCopy());
        if(customOrderBy){
            data.setItem('customOrderBy',customOrderBy.deepCopy());
        }
        if(joinConditions){
            data.setItem('joinConditions',joinConditions);
        }
        data.setItem('queryLimit',queryLimit);
        data.setItem('currViewPath',currViewPath);
        data.setItem('multiStores',multiStores);
        return data;
    },

    saveQuery:function(){
        var datapath =  this.sourceNode.absDatapath('.query.queryAttributes');
        var code = this.sourceNode.getRelativeData('.query.queryAttributes.code');
        var data = this.prepareQueryData();
        var that = this;
        saveCb = function(dlg) {
            var metadata = genro.getData(datapath);
            if (!metadata.getItem('code')){
                genro.publish('floating_message',{message:_T('Missing code'),messageType:'error'});
                return;
            }
            genro.serverCall('_table.adm.userobject.saveUserObject',
            {'objtype':'query','table':that.maintable,'data':data,metadata:metadata},
            function(result) {
                dlg.close_action();
                that.sourceNode.setRelativeData('.query.currentQuery',result.attr.code);
                that.refreshQueryMenues();
            });
        };
        genro.dev.userObjectDialog(code ? 'Save Query ' + code : 'Save New Query',datapath,saveCb);
    },

    _editorRoot:function(){
        var n = genro.nodeById(this.th_root+'_queryEditorRoot');
        return n? n.getValue():null;
    },
    onChangedQuery: function(currentQuery){
        var sourceNode = this.sourceNode;
        var that = this;
        var finalize = function(data,run){
            var customOrderBy;
            var currViewPath;
            var customLimit;
            var joinConditions;
            var multiStores;
            if(data.getItem('where')){
                where = data.pop('where');
                customOrderBy = data.pop('customOrderBy');
                joinConditions = data.pop('joinConditions');
                multiStores = data.pop('multiStores');
                customView = data.pop('customView');
                currViewPath = data.pop('currViewPath');
                customLimit = data.pop('queryLimit');
            }else{
                where = data;
            }
            var editorRoot = that._editorRoot();
            if(editorRoot){
                editorRoot.popNode('root');
            }
            sourceNode.setRelativeData('.query.where',where);
            sourceNode.setRelativeData('.query.customOrderBy',customOrderBy);
            sourceNode.setRelativeData('.query.joinConditions',joinConditions);

            sourceNode.setRelativeData('.query.multiStores',multiStores);

            sourceNode.setRelativeData('.query.limit',customLimit);
            if(currViewPath && currViewPath!='__baseview__'){
                sourceNode.setRelativeData('.grid.currViewPath',currViewPath);
            }
            if(editorRoot){
                that.buildQueryPane();
            }
            that.checkFavorite();
            if(run){
                sourceNode.fireEvent('.runQuery'); //provvisorio
            }
        }
        
        var queryBag = this.sourceNode.getRelativeData('.query.menu');
        var queryNode =  queryBag.getNode(currentQuery);
        var queryAttributes=queryNode? queryNode.attr:{extended:true,caption:_T('New Query')};
        //queryAttributes['id'] = queryAttributes['pkey']
        if(!('extended' in queryAttributes)){
            queryAttributes.extended = true;
        }
        sourceNode.setRelativeData('.query.queryAttributes',new gnr.GnrBag(queryAttributes));
        if(currentQuery=='__basequery__'){
            finalize(this.sourceNode.getRelativeData('.baseQuery').deepCopy(),false);
        }
        else if (currentQuery=='__newquery__'){
            finalize(new gnr.GnrBag());
        }else if(currentQuery=='__querybysample__'){
            sourceNode.getRelativeData('.query.queryEditor',false);
            finalize(new gnr.GnrBag());
        }
        else if(queryAttributes.pkey){
            genro.serverCall('_table.adm.userobject.loadUserObject',{userObjectIdOrCode:queryAttributes.pkey,
                                                                     tbl:this.maintable,objtype:queryAttributes.objtype},
                                                                    function(result){
                                                                        finalize(result._value.deepCopy(),!sourceNode.getRelativeData('.query.queryEditor'));
                                                                    });
        }else if(queryAttributes.filteringPkeys){
            finalize(new gnr.GnrBag(),true);
        }
    },

    buildQueryPane: function() {
        var editorRoot = this._editorRoot();
        if(editorRoot){
            editorRoot.popNode('root');
            this._buildQueryGroup(editorRoot._('div','root'), 
                                this.sourceNode.getRelativeData('.query.where'), 
                                0);
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
                                        if(typeof(result._value)=='string'){
                                            helperBag.setItem('items',result._value);//legacy
                                        }else{
                                            helperBag.setItem('items',result._value.getItem('items'));//savedbag
                                        }
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
                     'data':new gnr.GnrBag({'items':helperBag.getItem('items')}),
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

            var input_attrs = {value:'^' + relpath + '?value_caption', width:'12em',relpath:relpath,
                _autoselect:true,_class:'st_conditionValue',validate_onAccept:curr_th+'.querymanager.checkQueryLineValue(this,value);'};
            input_attrs.dropTarget = true;
            input_attrs['onDrop_gnrdbfld_'+this.maintable.replace('.','_')] = function(dropInfo,data){
                this.widget.setValue(data.fieldpath.startsWith('@')?data.fieldpath:'$'+data.fieldpath,true);
            };

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
        var tbl = container._('table', {_class:'qb_table'})._('tbody');
        for (var i = 0; i < bagnodes.length; i++) {
            node = bagnodes[i];
            this._buildQueryRow(tbl._('tr', {_class:'^.' + node.label + '?css_class'}), bagnodes[i], i, level);
        }
    },

    checkQueryLineValue:function(sourceNode, value) {
        var relpath = sourceNode.attr.relpath;
        value = value || '';
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
        return genro.dev.translateQueryPars(genro._(this.wherepath));
    },

    onQueryCalling:function(querybag,filteringPkeys){
        var parslist=[];
        var sourceNode = this.sourceNode;
        if(filteringPkeys){
            var currAttrs = this.sourceNode.getRelativeData('.query.queryAttributes').asDict();
            var params = objectExtract(currAttrs,'parameter_*');
            var dflt = objectExtract(currAttrs,'default_*');
            for(var k in params){
                parslist.push({value_caption:'?'+(k in dflt? params[k]+'|'+dflt[k] : params[k]), relpath:'parameter_'+k});
            }
        }else if(querybag.getItem("#0?column")){
            this.cleanQueryPane(querybag); 
            parslist = this.translateQueryPars();
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
        if(this._editorRoot()){
            genro.dom.setClass(this._editorRoot().getParentNode().attributeOwnerNode('frameCode'),
                            'th_isFavoriteQuery',currfavorite==currPath);
        }
    },
    refreshQueryMenues:function(){
        this.sourceNode.getRelativeData('.query').getNode('menu').getResolver().reset();
        //this.sourceNode.getRelativeData('.query.savedqueries').getParentNode().getResolver().reset();
    },
    
    setFavoriteQuery:function(){
        var favoritePath = genro.getFromStorage("local", this.storeKey());
        if(favoritePath && (!this.sourceNode.getRelativeData('.query.menu').getNode(favoritePath) || favoritePath=='__basequery__')){
            favoritePath = null;
        }
        var defaultQuery = this.sourceNode.getRelativeData('.query.bySampleIsDefault')?'__querybysample__':'__basequery__';
        favoritePath = favoritePath || defaultQuery;
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
        genro.dev.dynamicQueryParsFb(center,sourceNode.getRelativeData(this.wherepath),parslist,1);
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


