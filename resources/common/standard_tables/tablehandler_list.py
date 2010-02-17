#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag

class TableHandlerForm(BaseComponent):
    def pageList(self, pane):
        filterpath='filter.%s' % self.pagename
        if not filterpath in self.clientContext:
            filterBase=self.filterBase()
            if filterBase:
                cookie=self.clientContext
                cookie[filterpath]=filterBase
                self.clientContext=cookie
                #pane.data('_clientCtx.%s'%filterpath, filterBase)
        pane.data('list.showToolbox', False)
        pane.data('list.showExtendedQuery', False)
        pane.dataController("""genro.wdgById("gridbc").showHideRegion("top",showquery);genro.resizeAll();""",
                        showquery='^list.showExtendedQuery',
                        _fired='^gnr.onStart')
        pane.dataController("""if(page==1){SET list.selectedTop=1;}
                                   else if(page==0){SET list.selectedTop=0;}
                                """, page='^list.selectedLeft')
        
        pane.dataController("""genro.wdgById("gridbc").showHideRegion("left",show);genro.resizeAll();""",
                        show='^list.showToolbox',_fired='^gnr.onStart')
        pane.dataFormula('list.showExtendedQuery', "true", _if='where.len()>1', where='^list.query.where')
        self.pageListController(pane)
        mainbc = pane.borderContainer()
        self.listToolbar(mainbc.contentPane(region='top',_class='sttbl_list_top'))
        bc = mainbc.borderContainer(region='center',design='sidebar',liveSplitters=False,nodeId='gridbc')
        #left
        toolboxPane = bc.borderContainer(width='250px',region = 'left',_class='toolbox',splitter=True,hidden=True)
        if self.tblobj.logicalDeletionField:
            delprefpane = toolboxPane.contentPane(region='bottom',height='20px',background_color='lightgray', _class='pbl_roundedGroup', margin='3px')
            delprefpane.checkbox(value='^aux.showDeleted', label='!!Show hidden records')
            delprefpane.checkbox(value='^list.tableRecordCount', label='!!Show total count',margin_left='5px')
            delprefpane.dataController("""SET list.excludeLogicalDeleted = showDeleted? 'mark':true;""",showDeleted='^aux.showDeleted')
        self.toolboxFields(toolboxPane.contentPane(region='top',height='50%',splitter=True))
        toolboxPane = toolboxPane.tabContainer(region='center', selected='^list.selectedLeft',margin='5px',margin_top='10px')
        self.toolboxQueries(toolboxPane.borderContainer(title='',tip='!!Queries',iconClass='icnBaseLens'))
        self.toolboxViews(toolboxPane.borderContainer(title='',tip='!!Views',iconClass='icnBaseView'))
        self.toolboxActions(toolboxPane.borderContainer(title='',tip='!!Actions',iconClass='icnBaseAction'))
        toolboxPane.contentPane(title='',tip='!!Mail',iconClass='icnBaseEmail')
        toolboxPane.contentPane(title='',tip='!!Print',iconClass='icnBasePrinter')
        
        #top
        topStackContainer = bc.stackContainer(region='top',height='20%', splitter=True,hidden=True,selected='^list.selectedTop')
        extendedQueryPane = topStackContainer.contentPane(onEnter='FIRE list.runQuery=true;')
        self.editorPane('query', extendedQueryPane, datapath='list.query.where')
        
        ve_editpane = topStackContainer.contentPane()
        fb = ve_editpane.dropdownbutton('', hidden=True, nodeId='ve_colEditor', datapath='^vars.editedColumn').tooltipdialog().formbuilder(border_spacing='3px', font_size='0.9em', cols=1)
        fb.textbox(lbl='Name', value='^.?name') 
        fb.textbox(lbl='Width', value='^.?width')
        fb.textbox(lbl='Color', value='^.?color')
        fb.textbox(lbl='Background', value='^.?background_color')
        self.editorPane('view', ve_editpane, datapath='list.view.structure')
        self.listBottomPane(bc,region='bottom')
        #center
        st = bc.stackContainer(region='center',datapath='list.grid', margin='5px',
                                     nodeId='_gridpane_', selected='^list.gridpage')
        self.gridPane(st)
        st.contentPane().div(_class='waiting')
        
    def listController(self,pane):
        pane.data('list.excludeLogicalDeleted',True)
        pane.data('aux.showDeleted',False)
        pane.data('list.view.structure',self.lstBase(self.newGridStruct()))
        pane.dataController("""genro.querybuilder = new gnr.GnrQueryBuilder("query_root", "%s", "list.query.where");""" % self.maintable,_init=True)
        pane.dataController("""genro.queryanalyzer = new gnr.GnrQueryAnalyzer("translator_root","list.query.where","list.runQueryDo")""",_onStart=True)
        pane.dataController("""genro.viewEditor = new gnr.GnrViewEditor("view_root", "%s", "maingrid"); genro.viewEditor.colsFromBag();""" % self.maintable,_onStart=True)
        pane.dataController("""genro.querybuilder.createMenues();
                                  dijit.byId('qb_fields_menu').bindDomNode(genro.domById('fastQueryColumn'));
                                  dijit.byId('qb_not_menu').bindDomNode(genro.domById('fastQueryNot'));
                                  genro.querybuilder.buildQueryPane();""" , _onStart=True)
        pane.data('usr.writePermission',self.userCanWrite())
        pane.data('usr.deletePermission',self.userCanDelete())
        pane.data('usr.unlockPermission',self.userCanDelete() or self.userCanWrite())
        pane.data('status.locked',True)
        pane.dataFormula('status.unlocked','!locked',locked='^status.locked',_init=True)
        condition=self.conditionBase()
        condPars={}
        if condition:
            condPars=condition[1] or {}
            condition=condition[0]
        pane.data('list.plural',self.pluralRecordName())
        pane.data('list.rowcount',0)
        
        if self.tableRecordCount():
            pane.dataRpc('list.rowtotal','app.getRecordCount',_onStart=300,
                        table=self.maintable, where=condition,**condPars)
                        
        pane.dataFormula('list.title_bar', "rowtotal?plural+' : '+rowcount+'/'+rowtotal:plural+' : '+rowcount", 
                            selectedPage='^selectedPage',plural='^list.plural',rowcount='^list.rowcount',
                            rowtotal='^list.rowtotal',_if='selectedPage == 0',_else='formtitle',
                            formtitle='^form.title',_init=True)

            
            #pane.data('list',dict(plural=self.pluralRecordName(), rowcount=0,
            #                      rowtotal=self.tblobj.query(where=condition,**condPars).count())) # mettere come RPC per aggiornare non solo al caricamento
            
        pane.dataFormula('list.canWrite','(!locked ) && writePermission',locked='^status.locked',writePermission='=usr.writePermission',_init=True)
        pane.dataFormula('list.canDelete','(!locked) && deletePermission',locked='^status.locked',deletePermission='=usr.deletePermission',_init=True)
        pane.dataController("SET list.selectedIndex=-1; SET selectedPage = 1", fired='^list.newRecord')
        pane.dataController(""" var pkey;
                                    if (idx < -1){pkey = null;PUT list.selectedIndex = null;}
                                    else if (idx == -1){
                                                        pkey = '*newrecord*';
                                                        PUT list.selectedIndex = null;}
                                    else {pkey = genro.wdgById("maingrid").rowIdByIndex(idx);}
                                    if(pkey){
                                        SET list.selectedId = pkey;
                                        FIRE form.doLoad = true;
                                    } else {
                                        SET form.record = new gnr.GnrBag();
                                        if (genro.formById("formPane")){
                                        genro.formById("formPane").reset();}
                                    }
                                    if(idx == -2){SET selectedPage=0; SET list.query.pkeys=null;}""" ,
                             idx='^list.selectedIndex')
        pane.dataController("SET status.locked=true;",fire='^status.lock')
        pane.dataController("SET status.locked=false;",fire='^status.unlock',_if='unlockPermission',
                                                                 unlockPermission='=usr.unlockPermission',
                                                                 forbiddenMsg = '==  unlockForbiddenMsg || dfltForbiddenMsg',
                                                                 unlockForbiddenMsg ='=usr.unlockForbiddenMsg',
                                                                 dfltForbiddenMsg = "!!You cannot unlock this table",
                                                                 _else='FIRE gnr.alert = forbiddenMsg') 
        
        pane.dataController("""genro.dlg.ask(askTitle, message,
                                                {export:exportButton, print:printButton, pdf:pdfButton, actions:actionsButton, cancel:cancelButton},
                                                'list.onSelectionCommands');""",
                               fired='^list.onSelectionMenu', askTitle='!!Commands', message="!!Export or Print the selection",
                               exportButton="!!Export", printButton="!!Print",pdfButton='!!Pdf', actionsButton='!!Actions', cancelButton='!!Cancel')
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
            """,#### MODIFICA MIKI 30 gennaio 2009
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
        pane.data('list.act_store', act_bag, id='#k',caption='#v')
        pane.dataController("""var selectedRowidx = genro.wdgById("maingrid").getSelectedRowidx();
                                   genro.serverCall('app.onSelectionDo', {table:table, selectionName:selectionName, command:'action',
                                                     callmethod:action, selectedRowidx:selectedRowidx}, 'function(result){genro.dlg.alert(result)}')""",
                        confirm='^list.act_result', action='=list.act_value', _if='confirm=="confirm"',
                        table=self.maintable, selectionName='=list.selectionName')

    def listToolbar(self, pane, datapath=None,arrows=True):
        self.listController(pane)
        tb = pane.toolbar(_class='th_toolbar')
        self.listToolbar_lefticons(tb.div(float='left',_class='th_toolbar_left'))
        self.listToolbar_center(tb)
        self.listToolbar_rightbuttons(tb)
        
    def listToolbar_lefticons(self, pane):
        buttons = pane.div(_class='button_placeholder',float='left')
        buttons.div(_class='db_treebtn',connect_onclick="SET list.showToolbox = ! (GET list.showToolbox);")
        buttons.div(_class='db_querybtn',connect_onclick="SET list.showExtendedQuery =! (GET list.showExtendedQuery);")
        if self.tblobj.hasRecordTags(): #or self.enableFilter():
            ddbutton = pane.div(_class='listOptMenu',float='left')
            menu = ddbutton.dropDownButton('^list.tbar.stacklabel').menu(action="""
                                                                    SET list.tbar.stacklabel= $1.label;
                                                                    SET list.tbar.stackpage= $1.page;""",
                                                                    _class='smallmenu')
            menu.menuline(label='!!Query',page=0)
            if self.tblobj.hasRecordTags():
                menu.menuline(label='!!Tags',page=1)
            #if self.enableFilter(): 
            #    menu.menuline(label='!!Filters',page=2)
            #
            pane.data('list.tbar.stacklabel','!!Query')
            pane.data('list.tbar.stackpage',0)

    def listToolbar_center(self, pane):
        sc = pane.stackContainer(float='left',selected='^list.tbar.stackpage')
        self.listToolbar_query(sc.contentPane(_class='center_pane'))
        tags_pane = sc.contentPane(_class='center_pane')
        filter_pane = sc.contentPane(_class='center_pane')
        if self.tblobj.hasRecordTags():
            self.lst_tags_main(tags_pane) #inside extra
        if self.enableFilter():
            self.listToolbar_filters(filter_pane) #inside extra
        
    def listToolbar_query(self,pane):
        queryfb = pane.formbuilder(cols=5,datapath='list.query.where',_class='query_form',
                                          border_spacing='2px',onEnter='genro.fireAfter("list.runQuery",true,10);',float='left')
        #self._query_helpers(queryfb)

        queryfb.div('^.c_0?column_caption',min_width='12em',_class='smallFakeTextBox floatingPopup',
                              dnd_onDrop="genro.querybuilder.onChangedQueryColumn(this,item.attr);",
                              dnd_allowDrop="return !(item.attr.one_relation);", nodeId='fastQueryColumn',
                              action="genro.querybuilder.onChangedQueryColumn($2,$1);",
                              lbl='!!Search')
        optd = queryfb.div(_class='smallFakeTextBox',lbl='!!Op.',lbl_width='4em')
        
        optd.div('^.c_0?not_caption',selected_caption='.c_0?not_caption',selected_fullpath='.c_0?not',
                display='inline-block',width='1.5em',_class='floatingPopup',nodeId='fastQueryNot',
                border_right='1px solid silver')
        optd.div('^.c_0?op_caption', min_width='7em',nodeId='fastQueryOp',readonly=True,
                    selected_fullpath='.c_0?op',selected_caption='.c_0?op_caption',
                    connectedMenu='==genro.querybuilder.getOpMenuId(_dtype);',
                    action="genro.querybuilder.onChangedQueryOp($2,$1);",
                    _dtype='^.c_0?column_dtype',
                    _class='floatingPopup',display='inline-block',padding_left='2px')

        queryfb.textbox(lbl='!!Value',value='^.c_0',width='12em',lbl_width='5em', _autoselect=True,row_class='^.c_0?css_class',
                        validate_onAccept='genro.queryanalyzer.checkQueryLineValue(this,value);',_class='st_conditionValue')
        pane.button('!!Run query', fire='list.runQueryButton',
                    iconClass="tb_button db_query",showLabel=False,float='left')
        queryfb.dataFormula('list.currentQueryCountAsString','msg.replace("_rec_",cnt)',
                            cnt='^list.currentQueryCount',_if='cnt',_else='',
                            msg='!!Current query will return _rec_ items')
        queryfb.dataController("""if(fired=='Shift'){
                                     FIRE list.showQueryCountDlg;
                                     }else{
                                         FIRE list.runQuery;
                                     }""",fired='^list.runQueryButton')
        queryfb.dataController("""SET list.currentQueryCountAsString = waitmsg;
                                     genro.fireAfter('list.updateCurrentQueryCount');
                                     genro.dlg.alert('^list.currentQueryCountAsString',dlgtitle);
                                  """,_fired="^list.showQueryCountDlg",waitmsg='!!Working.....',
                                                 dlgtitle='!!Current query record count')
        if self.enableFilter():
            self.th_filtermenu(queryfb)

    def _query_helpers(self,pane):
        dlgBC = self.hiddenTooltipDialog(pane, dlgId='helper_in', title="!!In",
                                         width="42em",height="23ex",fired='^list.query.helper.in', 
                                         datapath='list.query.helper',
                                         bottom_right='!!Add',onOpen='genro.querybuilder.onHelperOpen();',
                                         bottom_right_action="""var currpath = GET list.query.helper.currentpath;
                                                                genro.setData(currpath,GET list.query.helper.buffer);"""
                                            )
        dlgpane = dlgBC.contentPane(region='center',_class='pbl_dialog_center')
        box = dlgpane.div(position='absolute',top='1px',bottom='2px',left='1px',right='1px')
        box.simpleTextArea(value = '^.buffer',height='100%',width='100%')
        
    def listToolbar_rightbuttons(self, pane):
        pane = pane.div(nodeId='query_buttons',float='right')
        if self.userCanDelete() or self.userCanWrite():
            ph = pane.div(_class='button_placeholder',float='right')
            ph.button('!!Unlock',float='right',fire='status.unlock', iconClass="tb_button icnBaseLocked", showLabel=False,hidden='^status.unlocked')
            ph.button('!!Lock',float='right',fire='status.lock', iconClass="tb_button icnBaseUnlocked", showLabel=False,hidden='^status.locked')
        pane.button('!!Add',float='right',fire='list.newRecord', iconClass="tb_button db_add", visible='^list.canWrite', showLabel=False)


    def pageListController(self,pane):
        """docstring for pageListController"""
        pane.dataController('SET list.noSelection=true;SET list.rowIndex=null;', fired='^list.runQuery', _init=True)
        pane.dataController("""genro.dom.disable("query_buttons");
                               SET list.gridpage = 1;
                               SET list.queryRunning = true;
                               var parslist = genro.queryanalyzer.translateQueryPars();
                               
                               if (parslist.length>0){
                                  genro.queryanalyzer.buildParsDialog(parslist);
                               }else{
                                  FIRE list.runQueryDo = true;
                               }
                               
                               """,
                              running='=list.queryRunning', _if='!running', fired='^list.runQuery')   
        pane.dataController('SET list.query.selectedId = query_id; genro.fireAfter("list.runQueryButton",true,300)',
                                query_id="^list.query_id")
        
        pane.dataController("""    
                                   SET selectedPage=1;
                                   SET list.query.pkeys=initialPkey;
                                  FIRE list.runQuery = true;
                                   """,
                                 _onStart=1, initialPkey='=initialPkey', _if='initialPkey')
                                 
        pane.dataController("""var pkeys= genro.getData('list.'+dataset_name);
                                   if(pkeys){
                                       SET list.query.pkeys=pkeys;
                                       FIRE list.runQuery = true;
                                   }""",
                                 dataset_name='^list.querySet')
        
        pane.dataController('genro.wdgById("maingrid").updateRowCount(rowcount)',rowcount='^list.rowcount')
        
        pane.dataController("""var nodeStart=genro.getDataNode('list.data_start');
                                   var grid=genro.wdgById("maingrid");
                                   grid.clearBagCache();
                                   var rowcount=nodeStart.attr.totalrows;
                                   grid.storebag.attr=objectUpdate({},nodeStart.attr);
                                   grid.storebag.getValue().setItem('P_0',nodeStart.getValue());
                                   SET list.rowcount = rowcount;
                                   SET list.rowtotal = nodeStart.attr.totalRowCount;
                                   SET list.selectionName = nodeStart.attr.selectionName;
                                   grid.updateRowCount(0);
                                   grid.updateRowCount(rowcount);
                                   genro.dom.enable("query_buttons");
                                   SET list.queryRunning = false;
                                   SET list.gridpage = 0;
                                   
                                   PUT list.selectedIndex=null;
                                   if(initialPkey){
                                       SET list.selectedIndex=0;
                                       SET initialPkey=null;
                                   }
                                """,fired='^list.queryEnd', initialPkey='=initialPkey')
    def listBottomPane(self,bc,**kwargs):
        """
        CALLBACK of standardTable
        """
        bottomPane_list = sorted([func_name for func_name in dir(self) if func_name.startswith('bottomPane_')])
        if not bottomPane_list:
            return
        pane = bc.contentPane(_class='listbottompane',datapath='list.bottom',overflow='hidden',**kwargs)
        fb = pane.formbuilder(cols=15,border_spacing='2px')
        for func_name in bottomPane_list:
            getattr(self,func_name)(fb.div(datapath='.%s' %func_name[11:]))
            
    def onQueryCalling(self):
        return None
        
    def gridPane(self,pane):
        stats_main = getattr(self,'stats_main',None)
        if self.hierarchicalViewConf() or stats_main:
            tc = pane.tabContainer(selected='^list.selectedTab')
            gridpane =  tc.contentPane(title='!!Standard view')
            if stats_main:
                stats_main(tc,datapath='stats',title='!!Statistical view')
            if self.hierarchicalViewConf():
                treepane =  tc.contentPane(title='!!Hierarchical view', datapath='list')
                self.treePane(treepane)
        else:
            gridpane = pane
        pane.data('.sorted',self.orderBase())
        condition=self.conditionBase()
        condPars={}
        if condition:
            condPars=condition[1] or {}
            condition=condition[0]
        pane.dataFormula('.columns', 'gnr.columnsFromStruct(struct);', struct='^list.view.structure', _init=True)
        pane.data('list.tableRecordCount',self.tableRecordCount())
        pane.dataSelection('list.data_start', self.maintable, columns='=.columns',
                             where='=list.query.where', sortedBy='=list.grid.sorted',
                             pkeys='=list.query.pkeys', fired='^list.runQueryDo',
                             selectionName='*', recordResolver=False, condition=condition,
                             sqlContextName='standard_list', totalRowCount='=list.tableRecordCount',
                             row_start='0', row_count=self.rowsPerPage(),
                             excludeLogicalDeleted='^list.excludeLogicalDeleted',
                             applymethod='onLoadingSelection',
                             timeout=180000,
                             _onCalling=self.onQueryCalling(),
                             _onResult='FIRE list.queryEnd=true;',**condPars)
                                     
        grid = gridpane.virtualGrid(nodeId='maingrid', structpath="list.view.structure", storepath=".data", autoWidth=False,
                                selectedIndex='list.rowIndex', rowsPerPage=self.rowsPerPage(), sortedBy='^list.grid.sorted',
                                connect_onSelectionChanged='SET list.noSelection = (genro.wdgById("maingrid").selection.getSelectedCount()==0)',
                                connect_onRowDblClick='SET list.selectedIndex = GET list.rowIndex; SET selectedPage = 1;',
                                connect_onRowContextMenu="FIRE list.onSelectionMenu = true;")
        
        pane.dataRpc('list.currentQueryCount','app.getRecordCount', condition=condition,fired='^list.updateCurrentQueryCount',
                      table=self.maintable, where='=list.query.where',excludeLogicalDeleted='=list.excludeLogicalDeleted',
                      **condPars)
                      
class ListToolbox(BaseComponent):
    def toolboxFields(self,pane):
        treediv=pane.div(_class='treeContainer')
        treediv.tree(storepath='gnr.qb.fieldstree',persist=False,
                     inspect='shift', labelAttribute='caption',
                     _class='fieldsTree',
                     hideValues=True,
                     getIconClass='if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}',
                     dndController="dijit._tree.dndSource",
                     onDndDrop="function(){this.onDndCancel();}::JS",
                     checkAcceptance='function(){return false;}::JS',
                     checkItemAcceptance='function(){return false;}::JS')
        
        #left.accordionPane(title='!!Campi collegati')
         #action="""FIRE list.query.loadQuery=$1.pkey;
             
    def toolboxActions(self, container):
        self.actionsController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.actions.actions_menu', persist=False, inspect='shift',
                          labelAttribute='caption',hideValues=True,
                          _class='queryTree')
    
    def actionsController(self, pane):
        pane.dataRemote('list.actions.actions_menu', 'list_actions', tbl=self.maintable, cacheTime=10)
    
    def toolboxViews(self, container):
        self.savedViewController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.view.saved_menu',persist=False, inspect='shift',
                          labelAttribute='caption', connect_ondblclick='FIRE list.runQuery = true;',
                          selected_pkey='list.view.selectedId', selected_code='list.view.selectedCode',
                          _class='queryTree',hideValues=True,
                          _saved='^list.view.saved', _deleted='^list.view.deleted')
        #btnpane = container.contentPane(region='top', height='30px').toolbar()
        self.saveViewButton(treepane)
        self.deleteViewButton(treepane)
        #btnpane.button('Add View', iconClass='tb_button db_add', fire='list.view.new',showLabel=False)
        

