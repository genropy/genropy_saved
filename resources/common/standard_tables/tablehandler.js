//dojo.declare("gnr.GnrViewEditor",null,{
//      constructor: function(nodeId, maintable, widgetNodeId){
//        this.nodeId = nodeId;
//        this.maintable=maintable;
//        this.sourceNode=genro.nodeById(widgetNodeId);
//        this.width_em = 10;
//    }
//});

dojo.declare("gnr.GnrQueryBuilder", null, {
    constructor: function(nodeId, maintable, datapath) {
        this.nodeId = nodeId;
        this.maintable = maintable;
        this.datapath = datapath;
        this.dtypes_dict = {'A':'alpha','T':'alpha','C':'alpha',
            'D':'date','DH':'date','I':'number',
            'L':'number','N':'number','R':'number','B':'boolean','TAG':'tagged'};
        this.helper_op_dict = {'in':'in','tagged':'tagged'};
        genro.setDataFromRemote('gnr.qb.fieldstree', "relationExplorer", {table:maintable, omit:'_'});
        this.treefield = genro.getData('gnr.qb.fieldstree');
        genro.setDataFromRemote('gnr.qb.fieldsmenu', "fieldExplorer", {table:maintable, omit:'_*'});
        genro.setDataFromRemote('gnr.qb.sqlop', "getSqlOperators");
    },

    getDtypeGroup:function(dtype) {
        var dflt = ('other_' + dtype).toLowerCase();
        var dflt = 'other';
        return this.dtypes_dict[dtype] || dflt;
    },

    createMenues: function() {
        genro.src.getNode()._('div', '_qbmenues');
        var node = genro.src.getNode('_qbmenues');
        node.clearValue();
        node.freeze();
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.jc',id:'qb_jc_menu'});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.not',id:'qb_not_menu'});
        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.fieldsmenu',id:'qb_fields_menu',
            action:"genro.querybuilder.onChangedQueryColumn($2,$1,$2.attr.relpath);"});

        node._('menu', {modifiers:'*',_class:'smallmenu',storepath:'gnr.qb.sqlop.op',id:'qb_op_menu'});

        var opmenu_types = ['alpha','date','number','other','boolean','unselected_column'];
        for (var i = 0; i < opmenu_types.length; i++) {
            node._('menu', {modifiers:'*',_class:'smallmenu',
                storepath:'gnr.qb.sqlop.op_spec.' + opmenu_types[i],id:'qb_op_menu_' + opmenu_types[i]});
        }
        node.unfreeze();
    },
    getOpMenuId: function(dtype) {
        return dtype ? "qb_op_menu_" + this.getDtypeGroup(dtype) : 'qb_op_menu_unselected_column';
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
        var startNode = startNode || genro.nodeById(this.nodeId);
        var datapath = datapath || this.datapath;
        var querydata = genro.getData(datapath);
        startNode.clearValue();
        startNode.freeze();
        this._buildQueryGroup(startNode, querydata, 0);
        startNode.unfreeze();
    },
    addDelFunc : function(mode, pos, e) {
        var datapath,addblock;
        if (e) {
            var target = e.target;
            addblock = e.altKey;
            datapath = target.sourceNode.absDatapath();
        } else {
            addblock = false;
            datapath = this.datapath;
        }
        var querybag = genro.getData(datapath);
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
        var querybag = genro.getData(this.datapath);
        querybag.clear();
        querybag.setItem('c_0', 0);
        querybag.setItem('c_0', pars.val, {op:pars.op,
            column:pars.column,
            op_caption:this.getCaption('op', pars),
            column_caption:this.getCaption('column', pars)});
        this.buildQueryPane();
    },
    cleanQueryPane:function() {
        var querybag = genro._(this.datapath);
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

    _buildQueryRow: function(tr, node, i, level) {
        var relpath = '.' + node.label;
        var val = node.getValue();
        var attr = node.getAttr();
        var noValueIndicator = "<span >&nbsp;</span>";
        attr.jc_caption = this.getCaption('jc', attr);
        attr.not_caption = this.getCaption('not', attr);
        cell = tr._('td');
        if (i > 0) {
            cell._('div', {_class:'qb_div qb_jc floatingPopup',connectedMenu:'qb_jc_menu',selected_fullpath:relpath + '?jc',
                selected_caption:relpath + '?jc_caption',innerHTML:'^' + relpath + '?jc_caption'});
        } else {
            attr.jc = '';
            //cell._('div',{_class:'qb_jc_noicn'});
        }
        tr._('td')._('div', {_class:'qb_div qb_not floatingPopup', connectedMenu:'qb_not_menu',selected_fullpath:relpath + '?not',
            selected_caption:relpath + '?not_caption',innerHTML:'^' + relpath + '?not_caption'});

        if (val instanceof gnr.GnrBag) {
            cell = tr._('td', {colspan:'3',datapath:relpath});
            this._buildQueryGroup(cell, val, level + 1);
        } else {
            var op_menu_id = 'qb_op_menu_' + (this.getDtypeGroup(attr.column_dtype || 'T'));
            attr.column_caption = this.getCaption('column', attr);
            attr.op_caption = this.getCaption('op', attr);
            var tdattr = {_class:'qb_div qb_field floatingPopup',connectedMenu:'qb_fields_menu',relpath:node.label,dropTarget:true,
                            innerHTML:'^' + relpath + '?column_caption'};
            tdattr['onDrop_gnrdbfld_'+this.maintable.replace('.','_')]="console.log(arguments);genro.querybuilder.onChangedQueryColumn(this,data,'" + node.label + "');"
            tr._('td')._('div', tdattr);
            tr._('td')._('div', {_class:'qb_div qb_op floatingPopup',
                connectedMenu:'==genro.querybuilder.getOpMenuId(_dtype);',
                _dtype:'^' + relpath + '?column_dtype',selected_fullpath:relpath + '?op',
                selected_caption: relpath + '?op_caption',innerHTML:'^' + relpath + '?op_caption',
                id:'_op_' + node.getStringId(),_fired:'^' + relpath + '?column_dtype'});
            var valtd = tr._('td')._('div', {_class:'qb_div qb_value'});

            var input_attrs = {value:'^' + relpath, width:'10em',
                _autoselect:true,_class:'st_conditionValue',validate_onAccept:'genro.queryanalyzer.checkQueryLineValue(this,value);'};
            if (attr.value_caption) {
                var fld_id = node.getStringId() + '_value';
                input_attrs['id'] = fld_id;
                input_attrs['connect__onMouse'] = 'genro.dom.ghostOnEvent($1);';
                valtd._('label', {_for:fld_id,_class:'ghostlabel','id':fld_id + '_label'})._('span', {innerHTML:val ? '' : attr.value_caption});
            }
            input_attrs.position = 'relative';
            input_attrs.padding_right = '10px';
            input_attrs.connect_onclick = "var op = GET " + relpath + "?op;if(op in genro.querybuilder.helper_op_dict){FIRE list.helper.queryrow='" + relpath.slice(1) + "';}";
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
    saveQueryDialog:function(title, actions, buttons, labels) {
        var querypath = this.datapath;
        genro.src.getNode()._('div', '_dlg_savequery');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var labels = labels || {code:'Code', description:'Description', priv:'Private', tags:'Tags'};
        var node = genro.src.getNode('_dlg_savequery').clearValue().freeze();
        var dlg = node._('dialog', {nodeId:'_dlg_savequery',title:title})._('div', {_class:'dlg_ask'});

        var inputs = dlg._('div', {padding:'10px',font_size:'.8'})._('table', {border_spacing:'8px'})._('tbody');
        var tr;
        tr = inputs._('tr');
        tr._('td')._('div', {'innerHTML':labels['code'],_class:'gnrfieldlabel',font_weight:'bold'});
        tr._('td')._('textBox', {'value':'^' + querypath + '?code',width:'25em',_class:'gnrfield'});

        tr = inputs._('tr');
        tr._('td')._('div', {'innerHTML':labels['description'],_class:'gnrfieldlabel',font_weight:'bold'});
        tr._('td')._('textarea', {'value':'^' + querypath + '?description',width:'25em',border:'1px solid gray',_class:'gnrfield'});

        tr = inputs._('tr');
        tr._('td')._('div', {'innerHTML':labels['priv'],_class:'gnrfieldlabel',font_weight:'bold'});
        tr._('td')._('checkbox', {'value':'^' + querypath + '?private',_class:'gnrfield'});
        tr = inputs._('tr');
        tr._('td')._('div', {'innerHTML':labels['tags'],_class:'gnrfieldlabel',font_weight:'bold'});
        tr._('td')._('textBox', {'value':'^' + querypath + '?auth_tags',width:'25em',_class:'gnrfield'});

        var btns = dlg._('div', {'action':"genro.wdgById('_dlg_savequery').hide();if (this.attr.act){this.attr.act.call()}"});
        for (var btn in buttons) {
            btns._('button', {'_class':'dlg_ask_btn','label':buttons[btn],'act':actions[btn]});
        }
        node.unfreeze();
        genro.wdgById('_dlg_savequery').show();
    },

    deleteQueryDialog:function(title, actions, buttons, confirmMessage, noQueryMessage) {
        var qnode = genro.getDataNode(this.datapath);
        var pkey = qnode.getAttr('id');
        if (pkey) {
            genro.dlg.ask(title, confirmMessage.replace('$', qnode.getAttr('code')), buttons, actions);
        } else {
            genro.dlg.alert(noQueryMessage);
        }
    },
    doDelete:function() {
        genro.deleteUserObject(this.datapath);
        this.addDelFunc('add', 1);
        this.buildQueryPane();
    },

    _queryParametersDialog: function(kw, resultpath, title, buttons) {
        var querypath = this.datapath;
        genro.src.getNode()._('div', '_dlg_loadquery');
        var buttons = buttons || {confirm:'Confirm',cancel:'Cancel'};
        var node = genro.src.getNode('_dlg_loadquery').clearValue().freeze();
        var dlg = node._('dialog', {nodeId:'_dlg_loadquery',title:title})._('div', {_class:'dlg_ask'});

        var inputs = dlg._('div', {padding:'10px',font_size:'.8'})._('table', {border_spacing:'8px'})._('tbody');

        var tr, path, attrs;
        for (path in kw) {
            attrs = kw[path];
            tr = inputs._('tr');
            tr._('td')._('div', {'innerHTML':attrs['column_caption'] + ' ' + attrs['op_caption'],
                _class:'gnrfieldlabel', font_weight:'bold'});
            tr._('td')._('textBox', {'value':'^' + querypath + '.' + path, width:'25em', _class:'gnrfield'});
        }
        ;
        var btns = dlg._('div', {'action':"genro.wdgById('_dlg_loadquery').hide();genro.setData('" + resultpath + "',this.attr.actCode);"});

        for (var btn in buttons) {
            btns._('button', {'_class':'dlg_ask_btn','label':buttons[btn],'actCode':btn});
        }
        node.unfreeze();
        genro.wdgById('_dlg_loadquery').show();
    }
});
dojo.declare("gnr.GnrQueryAnalyzer", null, {
    constructor: function(nodeId, wherepath, triggerpath) {
        this.nodeId = nodeId;
        this.wherepath = wherepath;
        this.triggerpath = triggerpath;
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
        var action = "genro.wdgById('_dlg_ask_querypars').hide(); genro.fireEvent('" + this.triggerpath + "');";
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
            action:"genro.wdgById('_dlg_ask_querypars').hide();SET list.queryRunning = false;SET list.gridpage = 0;"});
        bottom._('button', {label:'Confirm',baseClass:'bottom_btn','float':'right',action:action});
        bottom._('button', {label:'Count',baseClass:'bottom_btn','float':'right',action:'FIRE list.showQueryCountDlg;'});

        node.unfreeze();
        genro.wdgById('_dlg_ask_querypars').show();

    }
});