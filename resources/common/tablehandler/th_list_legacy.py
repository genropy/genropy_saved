from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag

class TableHandlerListLegacy(BaseComponent):
    py_requires='tablehandler/th_list:TableHandlerList'
    legacy_dict = dict(form='formBase',struct='lstBase',query='queryBase',order='orderBase',condition='conditionBase',hiddencolumns='hiddencolumnsBase')
    
    @struct_method
    def th_listPage(self,pane,frameCode=None):
        self._queryTool=True
        self.query_helper_main(pane)
        self._th_setFilter()
        thframe = pane.framePane(frameCode=frameCode,th_root=frameCode,datapath='list')
        self._th_pageListController(thframe)
        self._th_listController_legacy(thframe)
        thframe.top.listToolbar()
        bc = thframe.center.borderContainer(design='sidebar', nodeId='gridbc')
        self.lstToolbox(bc.borderContainer(width='250px', region='left', _class='toolbox', splitter=True, hidden=True))
        self.lstEditors_main(bc.stackContainer(region='top', height='20%', splitter=True, hidden=True, selected='^list.selectedTop'))
        self._th_listBottomPane(bc, region='bottom')
        st = bc.stackContainer(region='center', datapath='list.grid', margin='0px',
                              nodeId='_gridpane_', selected='^list.gridpage')
        st.gridPane()
        st.contentPane().div(_class='waiting')
    
    
    @struct_method
    def th_listToolbar(self,pane):
        toolbarKw = dict()
        tagSlot = ''
        tagFilter = ''
        if self.hasTags():
            tagSlot = '15,|,tagsbtn,|,'
            toolbarKw['tagsbtn_mode'] = 'list'
        if self.enableFilter():
            tagFilter = 'filtermenu,'
        pane.slotToolbar('left_top_opener,|,5,queryfb,iv_runbtn,%sviewmenu,%s*,|,list_add,list_locker,5' %(tagSlot,tagFilter),
                        **toolbarKw)

    
    def _th_listViewStructures(self, pane):
        """Prepare databag for"""
        structures = Bag()

        def setInStructureCb(label, handler):
            structures.setItem(label, handler(self.newGridStruct(maintable=self.maintable)), objtype='view', tbl=self.maintable)

        viewMenu = self._th_listCustomCbBag('struct', cb=setInStructureCb)
        viewMenu.addItem('-', None)
        jsresolver = "genro.rpc.remoteResolver('getQuickView',null,{cacheTime:'5'})"
        viewMenu.addItem('savedview', jsresolver, _T='JS', caption='!!Custom view',
                         action='FIRE list.view_id = $1.pkey;')
        viewMenu.setItem('editview', None, caption='!!Edit view', action="""
                                                                    SET list.showToolbox = true;
                                                                    SET list.toolboxSelected = 'view';
                                                                    """)
        viewMenu.setItem('saveview', None, caption='!!Save view', action="FIRE list.save_userobject='view';")
        pane.data('list.view.menu', viewMenu)
        pane.data('list.view.pyviews', structures, baseview='_base')
        
    def _th_listCustomCbBag(self, basename=None, cb=None):
        customViewDict = self._th_hook(basename,asDict=True)
        cblist = sorted(customViewDict.keys())
        menuBag = Bag()
        basehandler = self._th_hook(basename)
        menuBag.setItem('_base', None, caption=basehandler.__doc__ or 'Base')
        if cb:
            cb('_base',basehandler)
        for funcname in cblist:
            name = funcname.split('_',1)[1]
            handler = customViewDict[funcname]
            if cb:
                cb(name, handler)
            menuBag.setItem(name, None, caption=handler.__doc__ or name.title() or 'Base')
        return menuBag


    def _th_listController_legacy(self, pane):
        self._th_listController(pane)
        self._th_listViewStructures(pane)
        pane.data('usr.writePermission', self.userCanWrite())
        pane.data('usr.deletePermission', self.userCanDelete())
        pane.data('usr.unlockPermission', self.userCanDelete() or self.userCanWrite())
        pane.dataFormula('status.locked', 'true', _onStart=True)
        condition = self._th_hook('condition')()
        condPars = {}
        if condition:
            condPars = condition[1] or {}
            condition = condition[0]
        pane.data('list.plural', self.pluralRecordName())
        pane.data('list.rowcount', 0)

        if self.tableRecordCount():
            pane.dataRpc('list.rowtotal', 'app.getRecordCount', _onStart=300,
                         table=self.maintable, where=condition, **condPars)

        pane.dataController("""var listtitle=rowtotal?plural+' : '+rowcount+'/'+rowtotal:plural+' : '+rowcount
                               SET list.title_bar=listtitle;
                               var titlebar=(selectedPage == 0)?listtitle:formtitle;
                               genro.publish('public_caption',titlebar)""",
                         selectedPage='^selectedPage', plural='^list.plural', rowcount='^list.rowcount',
                         rowtotal='^list.rowtotal',
                         formtitle='^form.title', _init=True)

        #pane.data('list',dict(plural=self.pluralRecordName(), rowcount=0,
        #                      rowtotal=self.tblobj.query(where=condition,**condPars).count())) # mettere come RPC per aggiornare non solo al caricamento

        pane.dataFormula('list.canWrite', '(!locked ) && writePermission', locked='^status.locked',
                         writePermission='=usr.writePermission', _init=True)
        pane.dataFormula('list.canDelete', '(!locked) && deletePermission', locked='^status.locked',
                         deletePermission='=usr.deletePermission', _init=True)
        pane.dataController("SET list.selectedIndex=-1; SET selectedPage = 1", fired='^list.newRecord')
        pane.dataController(""" var pkey;
                                console.log(idx);
                                    if (idx < -1){
                                        pkey = null;
                                        PUT list.selectedIndex = null;
                                        SET selectedPage=0; 
                                        SET list.query.pkeys=null;
                                        return;
                                    }
                                    else if (idx == -1){
                                                        pkey = '*newrecord*';
                                                        PUT list.selectedIndex = null;}
                                    else {
                                          pkey = genro.wdgById("maingrid").rowIdByIndex(idx);
                                         }
                                    if(pkey){
                                        SET list.selectedId = pkey;
                                        FIRE form.doLoad = true;
                                    } 
                                    """,
                            idx='^list.selectedIndex')
        pane.dataController("SET status.locked=true;", fired='^status.lock')
        pane.dataController("SET status.locked=false;", fired='^status.unlock', _if='unlockPermission',
                            unlockPermission='=usr.unlockPermission',
                            forbiddenMsg='==  unlockForbiddenMsg || dfltForbiddenMsg',
                            unlockForbiddenMsg='=usr.unlockForbiddenMsg',
                            dfltForbiddenMsg="!!You cannot unlock this table",
                            _else='FIRE gnr.alert = forbiddenMsg')

        pane.dataController("""genro.dlg.ask(askTitle, message,
                                                {export:exportButton, print:printButton, pdf:pdfButton, actions:actionsButton, cancel:cancelButton},
                                                'list.onSelectionCommands');""",
                            fired='^list.onSelectionMenu', askTitle='!!Commands',
                            message="!!Export or Print the selection",
                            exportButton="!!Export", printButton="!!Print", pdfButton='!!Pdf', actionsButton='!!Actions'
                            , cancelButton='!!Cancel')
        pane.dataController("""
            //var pkeys = genro.wdgById("maingrid").getSelectedPkeys();
            var selectedRowidx = genro.wdgById("maingrid").getSelectedRowidx();
            if(command=='print'){
                var url = genro.rpc.rpcUrl("app.onSelectionDo", {table:table, selectionName:selectionName, command:'print',
                                                             callmethod:null, selectedRowidx:selectedRowidx})
                genro.dev.printUrl(url);
            }
            else if((command=='export')||(command='pdf')){
                //var url = genro.rpc.rpcUrl("app.onSelectionDo", {table:table, selectionName:selectionName, command:command,
                //                                            callmethod:null, selectedRowidx:selectedRowidx})
                
                genro.download('', {method:"app.onSelectionDo",table:table, selectionName:selectionName, command:command,
                                                             callmethod:null, selectedRowidx:selectedRowidx});
            }
            else if(command=='actions'){
                genro.dlg.listChoice(act_title, act_msg, {confirm:btn_confirm,cancel:btn_cancel},
                                     act_resultPath, act_valuePath, act_storePath);
            }
            """, #### MODIFICA MIKI 30 gennaio 2009
                            command='^list.onSelectionCommands',
                            table=self.maintable,
                            selectionName='=list.selectionName',
                            act_title='!!Actions',
                            act_msg='!!Choose the action to execute: ',
                            btn_confirm='!!Confirm',
                            btn_cancel='!!Cancel',
                            act_resultPath='list.act_result',
                            act_valuePath='list.act_value',
                            act_storePath='list.act_store'
                            )
        act_bag = Bag()
        for action in [m[7:] for m in dir(self) if m.startswith('action_')]:
            act_bag[action] = '!!%s' % action.capitalize().replace('_', ' ')
        pane.data('list.act_store', act_bag, id='#k', caption='#v')
        pane.dataController("""var selectedRowidx = genro.wdgById("maingrid").getSelectedRowidx();
                                   genro.serverCall('app.onSelectionDo', {table:table, selectionName:selectionName, command:'action',
                                                     callmethod:action, selectedRowidx:selectedRowidx}, 'function(result){genro.dlg.alert(result)}')"""
                            ,
                            confirm='^list.act_result', action='=list.act_value', _if='confirm=="confirm"',
                            table=self.maintable, selectionName='=list.selectionName')


    def _th_pageListController(self, pane):
        """docstring for pageListController"""        
        pane.dataController('SET list.noSelection=true;SET list.rowIndex=null;', fired='^list.runQuery', _init=True)
        pane.dataController("""genro.dom.disable("query_buttons");
                               SET list.gridpage = 1;                              
                            """,
                            running='=.queryRunning', _if='!running', fired='^.runQuery')
        pane.dataController('SET list.query.selectedId = query_id; genro.fireAfter("list.runQueryButton",true,300)',
                            query_id="^list.query_id")
        pane.dataController("""SET list.view.selectedId = view_id; 
                                if(selectionName){
                                    genro.fireAfter("list.runQueryButton",true,300);
                                }
                                """,
                            view_id="^list.view_id", selectionName='=list.selectionName')

        pane.dataController("""if((!initialPkey) && (window.location.hash.indexOf('#pk_')==0)){
                                    initialPkey=window.location.hash.slice(4);
                                    if(initialPkey == '*newrecord*') {
                                        initialPkey = null;
                                        window.location.hash = '';
                                    }
                                    SET initialPkey=initialPkey;
                                }
                                if(initialPkey){
                                    SET selectedPage=1;
                                    SET list.query.pkeys=initialPkey;
                                    FIRE list.runQuery = true;
                                }
                                   """,
                            _onStart=.5, initialPkey='=initialPkey') # pkg/page#pk_*newrecord* disabled because it doesn't work

        pane.dataController("""var pkeys= genro.getData('list.'+dataset_name);
                                   if(pkeys){
                                       SET list.query.pkeys=pkeys;
                                       FIRE list.runQuery = true;
                                   }""",
                            dataset_name='^list.querySet')

        pane.dataController('genro.wdgById("maingrid").updateRowCount(rowcount)', rowcount='^list.rowcount')

        pane.dataController("""
                                   var nodeStart=genro.getDataNode('list.grid.store');
                                   var grid=genro.wdgById("maingrid");
                                   //grid.clearBagCache();
                                   var rowcount=nodeStart.attr.totalrows;
                                   
                                   SET list.rowcount = rowcount;
                                   SET list.rowtotal = nodeStart.attr.totalRowCount;
                                   SET list.selectionName = nodeStart.attr.selectionName;
                                   //grid.updateRowCount(0);
                                   //grid.updateRowCount(rowcount);
                                   //grid.selection.unselectAll();                            
                                   genro.dom.enable("query_buttons");
                                   SET list.queryRunning = false;
                                   SET list.gridpage = 0;
                                   PUT list.selectedIndex=null;
                                   if(initialPkey){
                                       SET list.selectedIndex=0;
                                       SET initialPkey=null;
                                   }
                                """, fired='^list.queryEnd', initialPkey='=initialPkey')
        
    @struct_method
    def th_mainlist_left_top_opener(self,pane,**kwargs):
        pane.button('!!Show Fields',iconClass='db_treebtn', showLabel=False,action="SET list.showToolbox = ! (GET list.showToolbox);")
        pane.button('!!Extended Query',iconClass='db_querybtn',showLabel=False, action="SET list.showExtendedQuery =! (GET list.showExtendedQuery);")        


    @struct_method
    def th_mainlist_viewmenu(self,pane,**kwargs):
        ddb = pane.dropdownbutton('!!Select view', showLabel=False,
                                     iconClass='vieselectorIcn', _class='dropDownNoArrow')
        ddb.menu(_class='smallmenu', storepath='list.view.menu',
                 action="""
                            SET list.view.pyviews?baseview = $1.fullpath;
                            //to correct the path name
                            FIRE list.view.new; 
                            //end to correct
                            if(GET list.selectionName){
                                FIRE list.runQuery;
                            }
                           """)
    
    @struct_method
    def th_mainlist_list_add(self, pane,**kwargs):
        pane.slotButton('!!Add',action='FIRE list.newRecord;',
                        iconClass="tb_button db_add",
                        subscribe_form_formPane_onLockChange="this.widget.setAttribute('disabled',$1.locked);",**kwargs)
        
    @struct_method
    def th_mainlist_list_locker(self, pane,**kwargs):
        pane.button('!!Locker',width='20px',iconClass='icnBaseUnlocked',showLabel=False,
                    action='genro.formById("formPane").publish("setLocked","toggle");',
                    subscribe_form_formPane_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'icnBaseLocked':'icnBaseUnlocked');""")
                                                  
    def rpc_load_query(self, **kwargs):
        return self.rpc_loadUserObject(**kwargs)

    def rpc_save_query(self, userobject, userobject_attr):
        return self.rpc_saveUserObject(userobject, userobject_attr)

    def rpc_list_query(self, **kwargs):
        return self.rpc_listUserObject(objtype='query', **kwargs)

    def rpc_list_view(self, **kwargs):
        return self.rpc_listUserObject(objtype='view', **kwargs)

    def rpc_getQuickQuery(self, **kwargs):
        result = self.rpc_listUserObject(objtype='query', tbl=self.maintable, onlyQuicklist=True, **kwargs)
        return result

    def rpc_getQuickView(self, **kwargs):
        result = self.rpc_listUserObject(objtype='view', tbl=self.maintable, onlyQuicklist=True, **kwargs)
        return result
        
    def _th_listBottomPane(self, bc, **kwargs):
        """
        CALLBACK of standardTable
        """
        bottomPane_list = sorted([func_name for func_name in dir(self) if func_name.startswith('bottomPane_')])
        if not bottomPane_list:
            return
        pane = bc.contentPane(_class='listbottompane', datapath='list.bottom', overflow='hidden', **kwargs)
        fb = pane.formbuilder(cols=15, border_spacing='2px')
        for func_name in bottomPane_list:
            getattr(self, func_name)(fb.div(datapath='.%s' % func_name[11:]))
    
    @struct_method
    def th_gridPane(self, pane,table=None):
        lstkwargs = dict()
        stats_main = getattr(self, 'stats_main', None)
        querybase = self._th_hook('query')()
        queryBag = self._prepareQueryBag(querybase,table=table)
        pane.data('list.baseQuery', queryBag)
        if self.hierarchicalViewConf() or self.hierarchicalEdit() or stats_main:
            tc = pane.tabContainer(selected='^list.selectedTab')
            gridpane = tc.contentPane(title='!!Standard view')
            if stats_main:
                stats_main(tc, datapath='stats', title='!!Statistical view')
            if self.hierarchicalViewConf():
                self.hv_main_view(tc.borderContainer(title='!!Hierarchical view', datapath='list.hv.view'))
            if self.hierarchicalEdit():
                self.hv_main_form(tc.borderContainer(title='!!Hierarchical edit', datapath='list.hv.edit'))

        else:
            gridpane = pane
        pane.data('.sorted', self._th_hook('order')())
        condition = self._th_hook('condition')()
        condPars = {}
        if condition:
            condPars = condition[1] or {}
            condition = condition[0]
        pane.dataController("""
        var columns = gnr.columnsFromStruct(struct);
        if(hiddencolumns){
            var hiddencolumns = hiddencolumns.split(',');
            columns = columns+','+hiddencolumns;
        }
        
        SET .columns = columns;
        """, hiddencolumns=self._th_hook('hiddencolumns')(),
                            struct='^list.view.structure', _init=True)

        pane.data('list.tableRecordCount', self.tableRecordCount())

        customOnDrops = dict(
                [('onDrop_%s' % k[10:], getattr(self, k)()) for k in dir(self) if k.startswith('lstOnDrop_')])
        lstkwargs.update(customOnDrops)
        dbfieldcode = 'gnrdbfld_%s' % self.maintable.replace('.', '_')
        lstkwargs[
        'onDrop_%s' % dbfieldcode] = "this.widget.addColumn(data,dropInfo.column);if(this.widget.rowCount>0){genro.fireAfter('list.runQueryDo',true);}"

        iv = gridpane.includedView(parentFrame='mainlist',nodeId='maingrid', 
                                 structpath="list.view.structure", autoWidth=False,
                                 datapath='.wdg',
                                 selectedIndex='list.rowIndex', rowsPerPage=self.rowsPerPage(), sortedBy='^list.grid.sorted',
                                 _newGrid=True,
                                 connect_onSelectionChanged='SET list.noSelection = (genro.wdgById("maingrid").selection.getSelectedCount()==0)',
                                 linkedForm='formPane', openFormEvent='onRowDblClick', dropTypes=None,
                                 dropTarget=True,
                                 selfDragColumns='trashable',
                                 dropTarget_column=dbfieldcode,
                                 dropTarget_grid='explorer_*',
                                 onDrop_gnrdbfld="""this.widget.addColumn(data,dropInfo.column);if(this.widget.rowCount>0){genro.fireAfter('list.runQueryDo',true);}"""
                                 ,
                                 onDrop_gridrow='console.log("dropped gridrow");console.log(data);',
                                 draggable=True, draggable_row=True,
                                 dragClass='draggedItem',
                                 onDrop=""" for (var k in data){
                                                 this.setRelativeData('list.external_drag.'+k,new gnr.GnrBag(data[k]));
                                              }""",
                                 connect_onRowContextMenu="FIRE list.onSelectionMenu = true;",
                                 selfsubscribe_runbtn="""
                                                        if($1.modifiers=='Shift'){
                                                            FIRE list.showQueryCountDlg;
                                                         }else{
                                                            FIRE list.runQuery;
                                                         }""",
                                 **lstkwargs)
                             
        store = iv.selectionStore(table=self.maintable, columns='=.columns',
                           chunkSize=self.rowsPerPage()*4,
                           where='=list.query.where', sortedBy='=list.grid.sorted',
                           pkeys='=list.query.pkeys', _fired='^list.runQueryDo',
                           selectionName='*', recordResolver=False, condition=condition,
                           sqlContextName='standard_list', totalRowCount='=list.tableRecordCount',
                           row_start='0', 
                           excludeLogicalDeleted='^list.excludeLogicalDeleted',
                           applymethod='onLoadingSelection',
                           timeout=180000, selectmethod='=list.selectmethod',
                           selectmethod_prefix='customQuery',
                           _onCalling=self.onQueryCalling(),
                           **condPars)
        store.addCallback('FIRE list.queryEnd=true; SET list.selectmethod=null; return result;')

        pane.dataController("SET list.selectedIndex = idx; SET selectedPage = 1;",
                            idx="^gnr.forms.formPane.openFormIdx")

        pane.dataRpc('list.currentQueryCount', 'app.getRecordCount', condition=condition,
                     fired='^list.updateCurrentQueryCount',
                     table=self.maintable, where='=list.query.where',
                     excludeLogicalDeleted='=list.excludeLogicalDeleted',
                     **condPars)
        pane.dataController("""genro.setData("list.query.where",baseQuery.deepCopy(),{objtype:"query", tbl:maintable});
                               genro.querybuilder(maintable).buildQueryPane(); 
                               SET list.view.selectedId = null;
                               if(!fired&&runOnStart){
                                    FIRE list.runQuery
                               }
                            """,
                            _onStart=True, baseQuery='=list.baseQuery', maintable=self.maintable,
                            fired='^list.query.new',
                            runOnStart=querybase.get('runOnStart', False))

    def _th_setFilter(self):
        filterpath = 'filter.%s' % self.pagename
        if not filterpath in self.clientContext:
            filterBase = self.filterBase()
            if filterBase:
                cookie = self.clientContext
                cookie[filterpath] = filterBase
                self.clientContext = cookie