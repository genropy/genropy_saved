# -*- coding: UTF-8 -*-

# th_view.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrlang import extract_kwargs
from gnr.core.gnrbag import Bag

class TableHandlerView(BaseComponent):
    py_requires = """th/th_lib:QueryHelper,
                     th/th_lib:LstQueryHandler,
                     gnrcomponents/framegrid:FrameGrid"""
                         
                         
    @extract_kwargs(condition=True)
    @struct_method
    def th_tableViewer(self,pane,frameCode=None,table=None,relation=None,th_pkey=None,viewResource=None,
                       reloader=None,virtualStore=None,condition=None,condition_kwargs=None,**kwargs):
        if relation:
            table,condition = self._th_relationExpand(pane,relation=relation,condition=condition,condition_kwargs=condition_kwargs,**kwargs)             
        self._th_mixinResource(frameCode,table=table,resourceName=viewResource,defaultClass='View')
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
        condition_kwargs = condition_kwargs or dict()
        if condition:
            condition_kwargs['condition'] = condition
        top_kwargs=top_kwargs or dict()
        if queryTool:
            base_slots = ['tools','5','vtitle','5','queryfb','|','queryTool','*','count','5']
            top_kwargs['queryfb_table'] = table
        else:
            base_slots = ['tools','5','vtitle','count','*','searchOn']
        base_slots = ','.join(base_slots)
        if 'slots' in top_kwargs:
            top_kwargs['slots'] = top_kwargs['slots'].replace('#',base_slots)
        else:
            top_kwargs['slots']= base_slots   
        frame = pane.frameGrid(frameCode=frameCode,childname='view',
                               struct=self._th_hook('struct',mangler=frameCode),
                               datapath='.view',top_kwargs=top_kwargs,_class='frameGrid',**kwargs)        
        self._th_listController(frame,table=table)
        if queryTool:
            self._th_queryToolController(frame,table=table)
        frame.gridPane(table=table,reloader=reloader,th_pkey=th_pkey,virtualStore=virtualStore,
                        condition=condition_kwargs)
        return frame

    @struct_method
    def th_slotbar_queryTool(self,pane,**kwargs):
       # pane = pane.div(width='20px',height='16px',_class='icnBaseLens hiddenDock')
        mangler = pane.getInheritedAttributes()['th_root']
        pane.palettePane('%s_queryTool' %mangler,title='Query tool',nodeId='%s_query_root' %mangler,
                        dockButton_iconClass='icnBaseLens',
                        dockButton_baseClass='no_background',
                        datapath='.query.where',
                        height='150px',width='400px')
    @struct_method
    def th_slotbar_vtitle(self,pane,**kwargs):
        pane.div('^.title',font_size='.9')
    
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
        if not condition:
            condition = self._th_hook('condition',mangler=mangler)()
        
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
            condition = condPars.pop('condition')
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
                               excludeLogicalDeleted='^.excludeLogicalDeleted',
                               applymethod='onLoadingSelection',
                               timeout=180000, selectmethod='=.selectmethod',
                               selectmethod_prefix='customQuery',
                               _onCalling=self.onQueryCalling(),
                               #_reloader=reloader,
                               **condPars)
        store.addCallback('FIRE .queryEnd=true; SET .selectmethod=null; return result;')        
        frame.dataRpc('.currentQueryCount', 'app.getRecordCount', condition=condition,
                     _updateCount='^.updateCurrentQueryCount',
                     table=table, where='=.query.where',_showCount='=.tableRecordCount',
                     excludeLogicalDeleted='=.excludeLogicalDeleted',_if='_updateCount || _showCount',
                     **condPars)
        
        frame.dataController("""
                               SET .grid.selectedId = null;
                               if(runOnStart){
                                    FIRE .runQuery;
                               }
                            """,
                            _onStart=True,
                            runOnStart=querybase.get('runOnStart', False))

    def onQueryCalling(self):
        return None
    
    @struct_method
    def th_slotbar_queryfb(self, pane,table=None,**kwargs):
        table = table or self.maintable
        tablecode = table.replace('.','_')
        mangler = pane.getInheritedAttributes()['th_root']
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
        
    def _th_listController(self,pane,table=None,mangler=None):
        table = table or self.maintable
        tblattr = dict(self.db.table(table).attributes)
        tblattr.pop('tag',None)
        pane.data('.table',table,**tblattr)
        options = self._th_hook('options',mangler=pane)() or dict()
        pane.data('.excludeLogicalDeleted', options.get('excludeLogicalDeleted',True))
        pane.data('.showDeleted', options.get('excludeLogicalDeleted',False))
        pane.data('.tableRecordCount',options.get('tableRecordCount',True))


    def _th_queryToolController(self,pane,table=None):
        mangler = pane.attributes['th_root']
        table = table or self.maintable
        pane.dataController(
                """this._querybuilder = new gnr.GnrQueryBuilder(this,table,"query_root");
                   var qb = this._querybuilder;
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

    def rpc_fieldExplorer(self, table=None, omit=None):
        result = self.rpc_relationExplorer(table=table, omit=omit)
        if hasattr(self,'customQuery_'):
            self._th_fieldExplorerCustomQuery(result)
        return result

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

