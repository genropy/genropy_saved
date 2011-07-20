# -*- coding: UTF-8 -*-

# th_view.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method

from gnr.core.gnrlang import extract_kwargs
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrbag import Bag

class TableHandlerView(BaseComponent):
    py_requires = """th/th_lib:QueryHelper,
                     th/th_view:THViewUtils,
                     gnrcomponents/framegrid:FrameGrid"""
                         
    @extract_kwargs(condition=True)
    @struct_method
    def th_tableViewer(self,pane,frameCode=None,table=None,relation=None,th_pkey=None,viewResource=None,
                       reloader=None,virtualStore=None,condition=None,condition_kwargs=None,**kwargs):
        resourceName= self._th_mixinResource(frameCode,table=table,resourceName=viewResource,defaultClass='View')
        resourceCondition = self._th_hook('condition',mangler=frameCode,dflt=dict())()
        condition = condition or resourceCondition.pop('condition',None)
        condition_kwargs.update(dictExtract(resourceCondition,'condition_'))
        if relation:
            table,condition = self._th_relationExpand(pane,relation=relation,condition=condition,condition_kwargs=condition_kwargs,**kwargs)             
        view = pane.thFrameGrid(frameCode=frameCode,th_root=frameCode,th_pkey=th_pkey,table=table,
                                 reloader=reloader,virtualStore=virtualStore,
                                 condition=condition,condition_kwargs=condition_kwargs,**kwargs)
        for side in ('top','bottom','left','right'):
            hooks = self._th_hook(side,mangler=frameCode,asDict=True)
            for hook in hooks.values():
                hook(getattr(view,side))
        return view
    
    @extract_kwargs (top=True)
    @struct_method
    def th_thFrameGrid(self,pane,frameCode=None,table=None,th_pkey=None,reloader=None,virtualStore=None,
                       top_kwargs=None,condition=None,condition_kwargs=None,**kwargs):
        queryTool = kwargs['queryTool'] if 'queryTool' in kwargs else virtualStore
        condition_kwargs = condition_kwargs
        if condition:
            condition_kwargs['condition'] = condition
        top_kwargs=top_kwargs or dict()
        if queryTool:
            base_slots = ['tools','5','vtitle','5','queryfb','|','queryTool','queryMenu','viewsMenu','*','count','5']
        else:
            base_slots = ['tools','5','vtitle','count','*','searchOn']
        base_slots = ','.join(base_slots)
        if 'slots' in top_kwargs:
            top_kwargs['slots'] = top_kwargs['slots'].replace('#',base_slots)
        else:
            top_kwargs['slots']= base_slots
        leftTools = '5,gridConfigurator,5,gridTrashColumns,5,gridPalette,10,|,40,export,*,optionsMenu,gridReload'
        top_kwargs['height'] = top_kwargs.get('height','20px')
        frame = pane.frameGrid(frameCode=frameCode,childname='view',
                               struct=self._th_hook('struct',mangler=frameCode),
                               datapath='.view',top_kwargs=top_kwargs,_class='frameGrid',tools=leftTools,**kwargs)        
        self._th_viewController(frame,table=table)
        frame.gridPane(table=table,reloader=reloader,th_pkey=th_pkey,virtualStore=virtualStore,
                        condition=condition_kwargs)
        return frame


    @struct_method
    def th_slotbar_optionsMenu(self,pane,**kwargs):
        menu = pane.div(tip='!!Query options',_class='buttonIcon icnBaseAction').menu(_class='smallmenu',modifiers='*')
        menu.menuline('!!Show logical deleted',
                    action='SET .excludeLogicalDeleted=!GET .excludeLogicalDeleted;',
                    checked='^.excludeLogicalDeleted?=!#v')
        table = pane.getInheritedAttributes()['table']
        if self.db.table(table).draftField:
            menu.menuline('!!Show drafts',
                            action='SET .excludeDraft=!GET .excludeDraft;',
                            checked='^.excludeDraft?=!#v')
        
    @struct_method
    def th_slotbar_vtitle(self,pane,**kwargs):
        pane.div('^.title',font_size='.9')

    @struct_method
    def th_slotbar_queryMenu(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        mangler = inattr['th_root']
        table = inattr['table']
        menu = pane.div(_class='buttonIcon icnSavedQuery',tip='!!Stored query',datapath='.query').menu(storepath='.menu',_class='smallmenu',modifiers='*')
        q = Bag()
        pyqueries = self._th_hook('query',mangler=mangler,asDict=True)
        for k,v in pyqueries.items():
            prefix,name=k.split('_query_')
            q.setItem(name,self._prepareQueryBag(v(),table=table),caption=v.__doc__)
        pane.data('.query.standard',q)
        pane.dataRemote('.query.menu',self.th_menuQueries,pyqueries=q.digest('#k,#a.caption'),
                        table=table,mangler=mangler,caption='Queries',cacheTime=10)
        pane.dataController("""
                                var q = key=='__basequery__'? baseQuery:standard.getItem(key);
                                SET .query.where = q.deepCopy(); 
                                SET .query.querypkey = null;SET .query.meta = new gnr.GnrBag();
                                if(key!='__basequery__'){
                                    FIRE .runQuery;
                                }
                                """,
                            key="^.query.loadstandard",baseQuery='=.baseQuery',standard='=.query.standard')
        rpc = pane.dataRpc('dummy',self.th_loadUserObject,pkey='^.query.querypkey',table=table,_if='pkey')
        rpc.addCallback("""
            SET .query.meta = new gnr.GnrBag(result.attr);
            SET .query.where = result._value.deepCopy();
            FIRE .runQuery;
            return result;
        """)

    @struct_method
    def th_slotbar_viewsMenu(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        mangler = inattr['th_root']
        table = inattr['table']
        menu = pane.div(padding_left='5px',_class='buttonIcon vieselectorIcn',tip='!!Stored query',datapath='.grid').menu(storepath='.th_viewmenu',_class='smallmenu',modifiers='*')
        q = Bag()
        pyqueries = self._th_hook('struct',mangler=mangler,asDict=True)
        for k,v in pyqueries.items():
            prefix,name=k.split('_struct_')
            q.setItem(name,self._prepareGridStruct(v,table=table),caption=v.__doc__)
        pane.data('.grid.resource_structs',q)
        pane.dataRemote('.grid.th_viewmenu',self.th_menuViews,pyviews=q.digest('#k,#a.caption'),
                        table=table,mangler=mangler,cacheTime=10)


    @struct_method
    def th_gridPane(self, frame,table=None,reloader=None,th_pkey=None,
                        virtualStore=None,condition=None):
        table = table or self.maintable
        mangler = frame.getInheritedAttributes()['th_root']
        sortedBy=self._th_hook('order',mangler=mangler)()
        if sortedBy :
            if not filter(lambda e: e.startswith('pkey'),sortedBy.split(',')):
                sortedBy = sortedBy +',pkey' 
        frame.data('.grid.sorted',sortedBy or 'pkey')
        if th_pkey:
            querybase = dict(column=self.db.table(table).pkey,op='equal',val=th_pkey,runOnStart=True)
        else:
            querybase = self._th_hook('query',mangler=mangler)() or dict()
        queryBag = self._prepareQueryBag(querybase,table=table)
        frame.data('.baseQuery', queryBag)
        frame.dataFormula('.title','view_title || name_plural',name_plural='=.table?name_plural',view_title='=.title',_init=True)
        frame.dataFormula('.query.where', 'q.deepCopy();',q='=.baseQuery',_onStart=True)
        condPars = {}
        if isinstance(condition,dict):
            condPars = condition
            condition = condPars.pop('condition',None)
        elif condition:
            condPars = condition[1] or {}
            condition = condition[0]
        frame.dataController("""
        var columns = gnr.columnsFromStruct(struct);
        if(hiddencolumns){
            var hiddencolumns = hiddencolumns.split(',');
            columns = columns+','+hiddencolumns;
        }
        
        SET .grid.columns = columns;
        """, hiddencolumns=self._th_hook('hiddencolumns',mangler=mangler)(),
                            struct='^.grid.struct', _init=True)

        gridattr = frame.grid.attributes
        
        gridattr.update(rowsPerPage=self.rowsPerPage(),
                        dropTypes=None,dropTarget=True,
                        draggable=True, draggable_row=True,
                        dragClass='draggedItem',
                        onDrop=""" for (var k in data){
                                        this.setRelativeData('.#parent.external_drag.'+k,new gnr.GnrBag(data[k]));
                                   }""",
                        selfsubscribe_runbtn="""
                            if($1.modifiers=='Shift'){
                                FIRE .#parent.showQueryCountDlg;
                            }else{
                            FIRE .#parent.runQuery;
                        }""")
        chunkSize=self.rowsPerPage()*4   if virtualStore else None  
        if virtualStore:
            chunkSize=self.rowsPerPage()*4
            selectionName = '*%s' %mangler
        else:
            chunkSize = None
            selectionName = None
        
        self.subscribeTable(table,True)
        store = frame.grid.selectionStore(table=table, columns='=.grid.columns',
                               chunkSize=chunkSize,childname='store',
                               where='=.query.where', sortedBy='=.grid.sorted',
                               pkeys='=.query.pkeys', _fired='^.runQueryDo',
                               selectionName=selectionName, recordResolver=False, condition=condition,
                               sqlContextName='standard_list', totalRowCount='=.tableRecordCount',
                               row_start='0', externalChanges=True,
                               excludeLogicalDeleted='=.excludeLogicalDeleted',
                               excludeDraft='=.excludeDraft',
                               applymethod='onLoadingSelection',
                               timeout=180000, selectmethod='=.selectmethod',
                               selectmethod_prefix='customQuery',
                               _onCalling=self._th_hook('onQueryCalling',mangler=mangler)(),
                               **condPars)
        store.addCallback('FIRE .queryEnd=true; SET .selectmethod=null; return result;')        
        if virtualStore:
            frame.dataRpc('.currentQueryCount', 'app.getRecordCount', condition=condition,
                         _updateCount='^.updateCurrentQueryCount',
                         table=table, where='=.query.where',_showCount='=.tableRecordCount',
                         excludeLogicalDeleted='=.excludeLogicalDeleted',
                         excludeDraft='=.excludeDraft',_if='_updateCount || _showCount',
                         **condPars)
        
        frame.dataController("""
                               SET .grid.selectedId = null;
                               if(runOnStart){
                                    FIRE .runQuery;
                               }
                            """,
                            _onStart=True,
                            runOnStart=querybase.get('runOnStart', False))

    
    @struct_method
    def th_slotbar_queryfb(self, pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table'] 
        tablecode = table.replace('.','_')
        mangler = inattr['th_root']
        pane.dataController(
                """this._querybuilder = new gnr.GnrQueryBuilder(this,table,"query_root");
                   this._queryanalyzer = new gnr.GnrQueryAnalyzer(this,table);
                """ 
                , _init=True,table=table,nodeId='%s_queryscripts' %mangler)
        
        pane.dataController("""
                               genro.querybuilder(mangler).cleanQueryPane(); 
                               SET .queryRunning = true;
                               var parslist = genro.queryanalyzer(mangler).translateQueryPars();
                               if (parslist.length>0){
                                  genro.queryanalyzer(mangler).buildParsDialog(parslist);
                               }else{
                                  FIRE .runQueryDo = true;
                               }
                            """,mangler=mangler,_fired="^.runQuery")
        pane.dataFormula('.currentQueryCountAsString', 'msg.replace("_rec_",cnt)',
                            cnt='^.currentQueryCount', _if='cnt', _else='',
                            msg='!!Current query will return _rec_ items')
        pane.dataController("""SET .currentQueryCountAsString = waitmsg;
                               FIRE .updateCurrentQueryCount;
                                genro.dlg.alert(alertmsg,dlgtitle);
                                  """, _fired="^.showQueryCountDlg", waitmsg='!!Working.....',
                               dlgtitle='!!Current query record count',alertmsg='^.currentQueryCountAsString')
        pane.dataController("""
                    var qb = genro.querybuilder(mangler);
                    qb.createMenues();
                    dijit.byId(qb.relativeId('qb_fields_menu')).bindDomNode(genro.domById(qb.relativeId('fastQueryColumn')));
                    dijit.byId(qb.relativeId('qb_not_menu')).bindDomNode(genro.domById(qb.relativeId('fastQueryNot')));
                    qb.buildQueryPane();
        """,_onStart=True,mangler=mangler)
        
        fb = pane.formbuilder(cols=6, datapath='.query.where', _class='query_form',
                                   border_spacing='0', onEnter='genro.nodeById(this.getInheritedAttributes().target).publish("runbtn",{"modifiers":null});')
        fb.div('^.c_0?column_caption', min_width='12em', _class='fakeTextBox floatingPopup',
                  nodeId='%s_fastQueryColumn' %mangler,
                   dropTarget=True,
                  lbl='!!Search',**{str('onDrop_gnrdbfld_%s' %table.replace('.','_')):"genro.querybuilder('%s').onChangedQueryColumn(this,data);" %mangler})
        optd = fb.div(_class='fakeTextBox', lbl='!!Op.', lbl_width='4em')

        optd.div('^.c_0?not_caption', selected_caption='.c_0?not_caption', selected_fullpath='.c_0?not',
                 display='inline-block', width='1.5em', _class='floatingPopup', nodeId='%s_fastQueryNot' %mangler,
                 border_right='1px solid silver')
                 
        optd.div('^.c_0?op_caption', min_width='7em', nodeId='%s_fastQueryOp' %mangler, 
                 selected_fullpath='.c_0?op', selected_caption='.c_0?op_caption',
                 connectedMenu='==genro.querybuilder("%s").getOpMenuId(_dtype);' %mangler,
                 action="console.log(this,arguments);genro.querybuilder('%s').onChangedQueryOp($2,$1);" %mangler,
                 _dtype='^.c_0?column_dtype',
                 _class='floatingPopup', display='inline-block', padding_left='2px')
                 
        value_textbox = fb.textbox(lbl='!!Value', value='^.c_0', width='12em', lbl_width='5em',
                                        _autoselect=True,
                                        row_class='^.c_0?css_class', position='relative',
                                        disabled='==(_op in genro.querybuilder("%s").helper_op_dict)'  %mangler, _op='^.c_0?op',
                                        connect_onclick="genro.querybuilder('%s').getHelper(this);" %mangler,
                                        validate_onAccept='genro.queryanalyzer("%s").checkQueryLineValue(this,value);' %mangler,
                                        _class='st_conditionValue')

        value_textbox.div('^.c_0', hidden='==!(_op in  genro.querybuilder("%s").helper_op_dict)' %mangler,
                          _op='^.c_0?op', _class='helperField')
                          
        fb.slotButton(label='!!Run query',publish='runbtn',
                                baseClass='no_background',
                                iconClass='tb_button db_query')
        
    def _th_viewController(self,pane,table=None,mangler=None):
        table = table or self.maintable
        tblattr = dict(self.db.table(table).attributes)
        tblattr.pop('tag',None)
        pane.data('.table',table,**tblattr)
        options = self._th_hook('options',mangler=pane)() or dict()
        pane.data('.excludeLogicalDeleted', options.get('excludeLogicalDeleted',True))
        pane.data('.excludeDraft', options.get('excludeDraft',True))
        pane.data('.tableRecordCount',options.get('tableRecordCount',True))

    def _prepareQueryBag(self,querybase,table=None):
        result = Bag()
        if not querybase:
            return result
        table = table or self.maintable
        tblobj = self.db.table(table)
        op_not = querybase.get('op_not', 'yes')
        column = querybase.get('column')
        column_dtype = None
        if column:
            column_dtype = tblobj.column(column).getAttr('dtype')
        not_caption = '&nbsp;' if op_not == 'yes' else '!!not'
        result.setItem('c_0', querybase.get('val'),
                       {'op': querybase.get('op'), 'column': column,
                        'op_caption': '!!%s' % self.db.whereTranslator.opCaption(querybase.get('op')),
                        'not': op_not, 'not_caption': not_caption,
                        'column_dtype': column_dtype,
                        'column_caption': self.app._relPathToCaption(table, column)})
        return result

class THViewUtils(BaseComponent):

    @struct_method
    def th_slotbar_queryTool(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        mangler = inattr['th_root']
        table = inattr['table']
        pane.dataRpc('.querypkey',self.th_saveUserObject,objtype='query',table=table,id='=.meta.id',data='=.where',code='=.meta.code',
                    description='=.meta.description', authtags='=.meta.authtags', private='=.meta.private', 
                    _fired='^.save',_if='code',_onResult='FIRE .saved;',datapath='.query')
        pane.dataRpc('dummy',self.th_deleteUserObject,pkey='=.query.querypkey',table=table,_fired='^.query.delete',
                    _onResult='FIRE .query.loadstandard="__basequery__";')
        dialog = pane.dialog(title='==_code?_pref+_code:_newtitle;',_newtitle='!!Save new query',
                                _pref='!!Save query: ',_code='^.code',datapath='.query.meta')

        self.th_saveUserObjectDialog(dialog,table)
        palette = pane.palettePane('%s_queryTool' %mangler,title='!!Query tool',
                        dockButton_iconClass='icnBaseLens',
                        datapath='.query.where',
                        dockButton_baseClass='no_background',
                        height='150px',width='400px')
        bar = palette.slotToolbar('cap,*,show_fields,editmenu',font_size='.8em',datapath='.#parent')
        bar.cap.div(innerHTML='==pref+(code||"-");',pref="!!Query:",code='^.meta.code')
        bar.show_fields.button('!!Show fields',
                                palettetitle='!!Fields',
                                table=table,
                                action="genro.dev.relationExplorer(table,palettetitle,{'left':'20pxpx','top':'20px','height':'270px','width':'180px'})")
        menu = bar.editmenu.div(_class='icnBaseEdit buttonIcon').menu(modifiers='*')
        menu.menuline(label='!!Save Query',action='this.getAttributeFromDatasource("dialog").show();',dialog=dialog.js_widget)
        menu.menuline(label='!!Save As...',action='SET .meta = new gnr.GnrBag(); this.getAttributeFromDatasource("dialog").show();',
                                    dialog=dialog.js_widget,disabled='^.querypkey?=!#v')
        menu.menuline(label='-')
        menu.menuline(label='!!Delete Query',action='FIRE .delete;',disabled='^.querypkey?=!#v')

        palette.div(nodeId='%s_query_root' %mangler)

    @public_method
    def th_listUserObject(self,table, objtype=None,namespace=None, **kwargs):
        result = Bag()
        if hasattr(self.package, 'listUserObject'):
            objectsel = self.package.listUserObject(objtype=objtype,namespace=namespace, userid=self.user, tbl=table,
                                                    authtags=self.userTags)
            if objectsel:
                for i, r in enumerate(objectsel.data):
                    attrs = dict([(str(k), v) for k, v in r.items()])
                    result.setItem(r['code'] or 'r_%i' % i, None, **attrs)
        return result
            
    @public_method
    def th_loadUserObject(self, table=None, pkey=None,**kwargs):
        pkg,tbl = table.split('.')
        package = self.db.package(pkg)
        data, metadata = package.loadUserObject(id=pkey)
        return (data, metadata)

    @public_method
    def th_menuViews(self,table=None,mangler=None,pyviews=None,**kwargs):
        result = Bag()
        gridId = '%s_grid' %mangler
        result.setItem('_baseview_', None,
                       action="genro.grid_configurator.loadGridBaseView(this.attr.gridId)",
                       label='Base View',gridId=gridId)
        if pyviews:
            for k,caption in pyviews:
                result.setItem(k.replace('_','.'),None,caption=caption,action="""genro.grid_configurator.loadGridBaseView(this.attr.gridId,this.attr.viewkey);""",viewkey=k,gridId=gridId)
        result.setItem('r_1',None,caption='-')
        self.grid_configurator_savedViewsMenu(result,gridId,action="genro.grid_configurator.loadCustomView(this.attr.gridId, this.attr.pkey);")
        return result
        
    
    @public_method
    def th_menuQueries(self,table=None,mangler=None,pyqueries=None,**kwargs):
        querymenu = Bag()
        querymenu.setItem('r_0',None,caption='!!Base Query',action='FIRE .loadstandard="__basequery__";')
        if pyqueries:
            querymenu.setItem('r_1',None,caption='-')
            for k,caption in pyqueries:
                querymenu.setItem(k.replace('_','.'),None,caption=caption,action='FIRE .loadstandard=$1.querykey;',querykey=k)
                
        savedqueries = self.package.listUserObject(objtype='query', userid=self.user, tbl=table,authtags=self.userTags)
        if savedqueries:
            querymenu.setItem('r_2',None,caption='-')
            for i, r in enumerate(savedqueries.data):
                attrs = dict([(str(k), v) for k, v in r.items()])
                querymenu.setItem(r['code'] or 's_%i' % i, None, action='SET .querypkey = $1.pkey;',**attrs)
        return querymenu
        
        
    @public_method
    def th_saveUserObject(self, table=None,objtype=None,namespace=None,pkey=None,data=None,code=None,  userid=None,
                       description=None, authtags=None, private=False, inside_shortlist=None,quicklist=False,**kwargs):
        pkg,tbl = table.split('.')
        package = self.db.package(pkg)
        record = dict(data=data,objtype=objtype,namespace=namespace,
                    pkg=pkg,tbl=table,userid=self.user,quicklist=quicklist or False,
                    code=code,table=table,authtags=authtags,id=pkey,
                    description=description,private=private or False)
        package.dbtable('userobject').insertOrUpdate(record)
        self.db.commit()
        return record['id']

    @public_method
    def th_deleteUserObject(self,table=None,pkey=None):
        pkg,tbl = table.split('.')
        package = self.db.package(pkg)
        package.deleteUserObject(pkey)
        self.db.commit()
        
    
    @public_method
    def getSqlOperators(self):
        result = Bag()
        listop = ('equal', 'startswith', 'wordstart', 'contains', 'startswithchars', 'greater', 'greatereq',
                  'less', 'lesseq', 'between', 'isnull', 'istrue', 'isfalse', 'nullorempty', 'in', 'regex')
        optype_dict = dict(alpha=['contains', 'startswith', 'equal', 'wordstart',
                                  'startswithchars', 'isnull', 'nullorempty', 'in', 'regex',
                                  'greater', 'greatereq', 'less', 'lesseq', 'between'],
                           date=['equal', 'in', 'isnull', 'greater', 'greatereq', 'less', 'lesseq', 'between'],
                           number=['equal', 'greater', 'greatereq', 'less', 'lesseq', 'isnull', 'in'],
                           boolean=['istrue', 'isfalse', 'isnull'],
                           others=['equal', 'greater', 'greatereq', 'less', 'lesseq', 'in'])

        wt = self.db.whereTranslator
        for op in listop:
            result.setItem('op.%s' % op, None, caption='!!%s' % wt.opCaption(op))
        for optype, values in optype_dict.items():
            for operation in values:
                result.setItem('op_spec.%s.%s' % (optype, operation), operation,
                               caption='!!%s' % wt.opCaption(operation))
        customOperatorsHandlers = [(x[12:], getattr(self, x)) for x in dir(self) if x.startswith('customSqlOp_')]
        for optype, handler in customOperatorsHandlers:
            operation, caption = handler(optype_dict=optype_dict)
            result.setItem('op_spec.%s.%s' % (optype, operation), operation, caption=caption)
            result.setItem('op.%s' % operation, None, caption=caption)

        result.setItem('op_spec.unselected_column.x', None, caption='!!Please select the column')

        result.setItem('jc.and', None, caption='!!AND')
        result.setItem('jc.or', None, caption='!!OR')

        result.setItem('not.yes', None, caption='&nbsp;')
        result.setItem('not.not', None, caption='!!NOT')
        return result

    def th_saveUserObjectDialog(self,dialog,table):
        frame = dialog.framePane(width='350px',height='200px')
        fb = frame.formbuilder(cols=3, width='320px', border_spacing='5px',margin='10px',margin_top='10px')
        fb.div(lbl='Flags:', colspan=1)
        fb.checkbox(value='^.private', lbl='', label='!!Private',tooltip='!!Only for me.',colspan=2)
        fb.textbox(value='^.code', colspan=3, tooltip='Dotted path and name',lbl='!!Code')
        fb.textbox(value='^.authtags', colspan=3, lbl='!!Permissions', tooltip='!!Comma separated list of auth tags.')
        fb.simpleTextarea(lbl='!!Description', value='^.description', height='3.75em',
                          width='100%', border='1px solid gray', lbl_vertical_align='top', colspan=3)
        jsdlg = dialog.js_widget
        footer = frame.bottom.slotBar('*,cancel,confirm')
        footer.cancel.button('!!Cancel',action='dialog.hide();',dialog=jsdlg)
        footer.confirm.button('!!Confirm',action='FIRE .#parent.save; dialog.hide();',dialog=jsdlg)