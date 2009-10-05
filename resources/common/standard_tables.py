#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

"""
DOJO 11
"""
import os

from gnr.core.gnrstring import templateReplace
from gnr.web.gnrwebpage import BaseComponent
from gnr.sql.gnrsql_exceptions import GnrSqlException,GnrSqlSaveChangesException,GnrSqlExecutionException
from gnr.core.gnrbag import Bag

class TableHandler(BaseComponent):
    css_requires = 'standard_tables'
    js_requires = 'standard_tables'
    
    def userCanWrite(self):
        return self.application.checkResourcePermission(self.tableWriteTags(), self.userTags)
    
    def userCanDelete(self):
        return self.application.checkResourcePermission(self.tableDeleteTags(), self.userTags)
    
    def tableWriteTags(self):
         return 'superadmin'
    
    def tableDeleteTags(self):
         return 'superadmin'
    
    def rowsPerPage(self):
        return 25
    
    def hierarchicalViewConf(self):
        return None
    
    def conditionBase(self):
        return (None,None)
    
    def formTitleBase(self,pane):
        pane.data("form.title", self.tblobj.attributes.get('name_long','Record'))
    
    def columnsBase(self):
        return ''
    
    def lstBase(self,):
        struct = self.newGridStruct()
        r=struct.view().rows()
        r.fields(self.columnsBase())
        return struct
    
    def main(self, root, pkey=None, **kwargs):
        root.data('selectedPage',0)
        root.data('gnr.maintable',self.maintable)
        self.setOnBeforeUnload(root, cb="genro.getData('gnr.forms.formPane.changed')",
                               msg="!!There are unsaved changes, do you want to close the page without saving?")
        pages,top,bottom = self.pbl_rootStackContainer(root,title='^list.title_bar', selected='^selectedPage',_class='pbl_mainstack')
        
        self.pageList(pages)
        self.pageForm(pages,bottom)
        self.joinConditions()
        
        if pkey == '*newrecord*':
            root.dataController('FIRE list.newRecord; FIRE status.unlock',_fired='^gnr.onStart',_delay=4000)
        elif pkey and self.db.table(self.maintable).existsRecord(pkey):
            pages.data('initialPkey',pkey)
            
        #root.defineContext('sql_selection','_serverCtx.sql_selection', self.sqlContextSelection())
        #root.defineContext('sql_record','_serverCtx.sql_record', self.sqlContextRecord())
    
    def joinConditions(self):
        """hook to define all join conditions for retrieve records related to the current edited record
           using method self.setJoinCondition
        """
        pass
    
    def pluralRecordName(self):
        return self.tblobj.attributes.get('name_plural','Records')
    
    def listController(self,pane):
        pane.data('list.excludeLogicalDeleted',True)
        pane.data('aux.showDeleted',False)
        pane.dataController("""genro.querybuilder = new gnr.GnrQueryBuilder("query_root", "%s", "list.query.where");""" % self.maintable,_init=True)
        pane.dataController("""genro.viewEditor = new gnr.GnrViewEditor("view_root", "%s", "maingrid");""" % self.maintable,_onStart=True)
        pane.dataController("""genro.querybuilder.createMenues();
                                  dijit.byId('qb_fields_menu').bindDomNode(genro.domById('fastQueryColumn'));
                                  dijit.byId('qb_op_menu').bindDomNode(genro.domById('fastQueryOp'));
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
        
        pane.dataRpc('list.rowtotal','app.getRecordCount',_onStart=300,
                      table=self.maintable, where=condition,**condPars)
       
       #pane.data('list',dict(plural=self.pluralRecordName(), rowcount=0,
       #                      rowtotal=self.tblobj.query(where=condition,**condPars).count())) # mettere come RPC per aggiornare non solo al caricamento
        pane.dataFormula('list.title_bar', "plural+' : '+rowcount+'/'+rowtotal", selectedPage='^selectedPage',
                        plural='^list.plural',rowcount='^list.rowcount',rowtotal='^list.rowtotal',
                        _if='selectedPage == 0',_else='formtitle',formtitle='^form.title',_init=True)
        pane.dataFormula('list.canWrite','(!locked ) && writePermission',locked='^status.locked',writePermission='=usr.writePermission',_init=True)
        pane.dataFormula('list.canDelete','(!locked) && deletePermission',locked='^status.locked',deletePermission='=usr.deletePermission',_init=True)
        pane.dataController("SET list.selectedIndex=-1;", fired='^list.newRecord')
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
                                    if(idx == -2){SET selectedPage=0;} else {SET selectedPage = 1;}""" ,
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
        #pane.dataController("""var pkeys = genro.wdgById("maingrid").getSelectedPkeys();
        #                           genro.serverCall('app.onSelectionDo', {table:table, selectionName:selectionName, command:'action',
        #                                             callmethod:action, pkeys:pkeys}, 'function(result){genro.dlg.alert(result)}')""",
        #                confirm='^list.act_result', action='=list.act_value', _if='confirm=="confirm"',
        #                table=self.maintable, selectionName='=list.selectionName')
    
    def listToolbar(self, pane, datapath=None,arrows=True):
        self.listController(pane)
        tb = pane.toolbar(height='26px')
        t_r = tb.div(float='right',width='110px')
        t_l = tb.div(width='20px',margin_left='2px',float='left',border_right='1px solid gray',height='25px')
        t_l.div(_class='db_treebtn',connect_onclick="SET list.showToolbox = ! (GET list.showToolbox);")
        t_l.div(_class='db_querybtn',connect_onclick="SET list.showExtendedQuery =! (GET list.showExtendedQuery);")
        t_l2 = tb.div(margin_left='8px',height='100%', float='left')
        t_c = tb.div(margin_left='8px',height='100%')
        
        if self.queryBase().get('runOnStart'):
            pane.dataController('FIRE list.runQuery',fired='^gnr.onStart',_delay=500)
        
        querypane = t_l2.formbuilder(cols=3,datapath='list.query.where',_class='query_pane',
                                          border_spacing='4px',onEnter='FIRE list.runQuery=true;')
        
        tb = querypane.div('^.c_0?column_caption',min_width='12em',_class='smallFakeTextBox floatingPopup',lbl='!!Query',
                              dnd_onDrop="""SET .c_0?column_caption = item.attr.fullcaption;
                                          SET .c_0?column = item.attr.fieldpath;""",
                              dnd_allowDrop="return !(item.attr.one_relation);",
                              
                              nodeId='fastQueryColumn',
                              selected_fieldpath='.c_0?column',
                              selected_fullcaption='.c_0?column_caption')
        querypane.div('^.c_0?op_caption',lbl='!!Op.', min_width='7em',nodeId='fastQueryOp',readonly=True,
                                                        selected_fullpath='.c_0?op',
                                                        selected_caption='.c_0?op_caption',
                                                        _class='smallFakeTextBox floatingPopup')
        querypane.textbox(lbl='!!Value',value='^.c_0',width='12em', _autoselect=True)
        t_c.button('!!Run query', fire='list.runQuery', iconClass="tb_button db_query",showLabel=False)
        #->Buttons for query changed or new records
        #t_c.button('!!New records', fire_newrecords='list.querySet', showLabel=True)
        #t_c.button('!!Changed records', fire_changedrecords='list.querySet', showLabel=True)
        
        #querypane.div(connect_onclick="genro.querybuilder.addDelFunc('add',1,$1)", _class='qb_btn qb_add');
        trbtn=t_r.div(width='110px',nodeId='query_buttons')
        if self.userCanDelete() or self.userCanWrite():
            trbtn.button('!!Unlock', float='right',fire='status.unlock', iconClass="tb_button icnBaseLocked", showLabel=False,hidden='^status.unlocked')
            trbtn.button('!!Lock', float='right',fire='status.lock', iconClass="tb_button icnBaseUnlocked", showLabel=False,hidden='^status.locked')
        trbtn.button('!!Add', float='right',fire='list.newRecord', iconClass="tb_button db_add", visible='^list.canWrite', showLabel=False)
       #trbtn.button('!!Delete', float='right',fire='list.deleteRecords', iconClass="tb_button db_del",visible='^list.canDelete',
       #                       disabled='^list.noSelection', showLabel=False)
       ##trbtn.button('!!Query', float='right',fire='list.runQuery', iconClass="tb_button db_query",showLabel=False)
    
    def pageListController(self,pane):
        """docstring for pageListController"""
        pane.dataController('genro.dom.disable("query_buttons");SET list.gridpage = 1;SET list.queryRunning = true;FIRE list.runQueryDo = true;',
                                                                    running='=list.queryRunning', _if='!running', fired='^list.runQuery')
        pane.dataController('SET list.noSelection=true;SET list.rowIndex=null;', fired='^list.runQuery', _init=True)
        
        pane.dataController("""SET selectedPage=1;
                                   SET list.query.pkeys=initialPkey;
                                   FIRE list.runQuery = true;""",
                                 _onStart=True, initialPkey='=initialPkey', _if='initialPkey')
                                 
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
    
    def pageList(self, pane):
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
        toolboxPane = bc.borderContainer(width='250px',region = 'left',_class='toolbox',splitter=True,hidden=True)
        if self.tblobj.logicalDeletionField:
            delprefpane = toolboxPane.contentPane(region='bottom',height='20px',background_color='lightgray', _class='pbl_roundedGroup', margin='3px')
            delprefpane.checkbox(value='^aux.showDeleted', label='!!Show hidden records')
            delprefpane.dataController("""SET list.excludeLogicalDeleted =!showDeleted;""",showDeleted='^aux.showDeleted')
        self.toolboxFields(toolboxPane.contentPane(region='top',height='50%',splitter=True))
        toolboxPane = toolboxPane.tabContainer(region='center', selected='^list.selectedLeft',margin='5px',margin_top='10px')
        self.toolboxQueries(toolboxPane.borderContainer(title='',tip='!!Queries',iconClass='icnBaseLens'))
        self.toolboxViews(toolboxPane.borderContainer(title='',tip='!!Views',iconClass='icnBaseView'))
        self.toolboxActions(toolboxPane.borderContainer(title='',tip='!!Actions',iconClass='icnBaseAction'))
        toolboxPane.contentPane(title='',tip='!!Mail',iconClass='icnBaseEmail')
        toolboxPane.contentPane(title='',tip='!!Print',iconClass='icnBasePrinter')
        
        topStackContainer = bc.stackContainer(region='top',height='20%', splitter=True,hidden=True,selected='^list.selectedTop')
        extendedQueryPane = topStackContainer.contentPane(onEnter='FIRE list.runQuery=true;')
        self.editorPane('query', extendedQueryPane, datapath='list.query.where')
        
        ve_editpane = topStackContainer.contentPane()
        fb = ve_editpane.dropdownbutton('', hidden=True, nodeId='ve_colEditor', datapath='^vars.editedColumn').tooltipdialog().formbuilder(border_spacing='3px', font_size='0.9em', cols=1)
        fb.textbox(lbl='Name', value='^.?name', nodeId='pippo') #?
        fb.textbox(lbl='Width', value='^.?width')
        fb.textbox(lbl='Color', value='^.?color')
        fb.textbox(lbl='Background', value='^.?background_color')
        self.editorPane('view', ve_editpane, datapath='list.view.structure')
        self.listBottomPane(bc,region='bottom')
        st = bc.stackContainer(region='center',datapath='list.grid', margin='5px',
                                     nodeId='_gridpane_', selected='^list.gridpage')
        self.gridPane(st)
        st.contentPane().div(_class='waiting')
    
    def listBottomPane(self,bc,**kwargs):
        """
        CALLBACK of standardTable
        """
        bottomPane_list = sorted([func_name for func_name in dir(self) if func_name.startswith('bottomPane_')])
        if not bottomPane_list:
            return
        pane = bc.contentPane(height='27px',font_size='0.9em',background_color='silver',**kwargs)
        for func_name in bottomPane_list:
            getattr(self,func_name)(pane)
            
    def editorPane(self, restype, pane, datapath):
        parentdatapath, resname = datapath.rsplit('.', 1)
        top = pane.div(_class='st_editor_bar', datapath=parentdatapath)        
        top.div(_class='icnBase10_Doc buttonIcon',float='right',
                                connect_onclick="FIRE .new=true;",
                                margin_right='5px', margin_top='2px', tooltip='!!New %s' % restype);
        
        top.div(_class='icnBase10_Save buttonIcon', float='right',
                                              onCreated="genro.dlg.connectTooltipDialog($1,'save_%s_btn')" % restype,
                                             margin_right='5px', margin_top='2px', tooltip='!!Save %s' % restype);
        
        top.div(_class='icnBase10_Trash buttonIcon', float='right',
                                                onCreated="genro.dlg.connectTooltipDialog($1,'delete_%s_btn')" % restype,
                                                margin_left='5px', margin_right='15px',
                                                margin_top='2px', tooltip='!!Delete %s' % restype,
                                                visible='^.%s?id' % resname)
        
        top.div(content='^.%s?code' % resname, _class='st_editor_title')
        pane.div(_class='st_editor_body st_editor_%s' % restype, nodeId='%s_root' % restype, datapath=datapath)
    
    def treePane(self, pane):
        client = pane.borderContainer(region = 'center')
        client.data('hv_conf', self.hierarchicalViewConf())
        client.dataRemote('.tree_view.tree', 'selectionAsTree', selectionName='^.selectionName' )
        leftpane = client.contentPane(region = 'center', overflow='auto')
        leftpane.dataRecord('.tree_view.current_record', self.maintable, pkey='^.tree_view.selected_id')
        leftpane.tree(storepath ='.tree_view.tree',
                     selected_pkey ='.tree_view.selected_id',
                     isTree =False,
                     selected_rec_type = '.tree_view.current_rec_type',
                     inspect ='shift',
                     labelAttribute ='caption',
                     fired ='^.queryEnd')
        infocontainer = client.borderContainer(region = 'right', width='40%', splitter=True)
        infopane_top= infocontainer.contentPane(region = 'top', height='50%',
                                                          splitter=True,_class='infoGrid',padding ='6px')
        infopane_top.dataScript('.tree_view.info_table',
                            """var current_rec_type= current_record.getItem('rec_type');
                               var result = new gnr.GnrBag();
                               var fields = info_fields.getNodes()
                               for (var i=0; i<fields.length; i++){
                                   var fld_rec_types = fields[i].getAttr('rec_types',null);
                                   var fld_label = fields[i].getAttr('label');
                                   if (fld_rec_types){
                                       fld_rec_types=fld_rec_types.split(',');
                                   }
                                   var fld_val_path = fields[i].getAttr('val_path');
                                   var fld_show_path = fields[i].getAttr('show_path');
                                   
                                   var fld_value = current_record.getItem(fld_val_path);
                                   var fld_show = current_record.getItem(fld_show_path);
                                   if (!fld_rec_types || dojo.indexOf(fld_rec_types, current_rec_type)!=-1){
                                       result.setItem('R_'+i,
                                                       null,
                                                      {'lbl':fld_label, 'val':fld_value,'show':fld_show})
                                   }
                               }
                               return result""",
                               info_fields = '=hv_conf',
                               current_record='=.tree_view.current_record',
                               fired='^.tree_view.current_record.id')
        infopane_top.includedView(storepath='.tree_view.info_table', struct=self._infoGridStruct())
        infoStackContainer = infocontainer.stackContainer(region = 'center',
                                                          selected='^.tree_view.stack.selectedPage')
        infoStackContainer.contentPane()
        callbacks = [(x.split('_')[1],x) for x in dir(self) if x.startswith('infoPane_')]
        infoStackContainer.data('rec_types', ','.join([x[0] for x in callbacks]))
        infoStackContainer.dataController("""rec_types = rec_types.split(',');
                                             var n = dojo.indexOf(rec_types,rec_type);
                                             if (n!=-1){SET list.tree_view.stack.selectedPage=n+1;};""",
                                           rec_types = '=rec_types',
                                           rec_type = '^.tree_view.current_rec_type')
        for cb in callbacks:
            getattr(self, cb[1])(infoStackContainer.contentPane(padding ='6px',
                                                                _class='pbl_roundedGroup',
                                                                datapath='.tree_view.current_record'))
        
    
    def _infoGridStruct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('lbl', name='Field',width='10em', headerStyles='display:none;', cellClasses='infoLabels', odd=False)
        r.cell('val', name='Value',width='10em', headerStyles='display:none;', cellClasses='infoValues', odd=False)
        return struct
    
    def gridPane(self,pane):
        if self.hierarchicalViewConf():
            tc = pane.tabContainer()
            gridpane =  tc.contentPane(title='!!Standard view')
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
        pane.dataSelection('list.data_start', self.maintable, columns='=.columns',
                             where='=list.query.where', sortedBy='=list.grid.sorted',
                             pkeys='=list.query.pkeys', fired='^list.runQueryDo',
                             selectionName='*', recordResolver=False, condition=condition,
                             sqlContextName='standard_list', totalRowCount=True,
                             row_start='0', row_count=self.rowsPerPage(),
                             excludeLogicalDeleted='^list.excludeLogicalDeleted',
                             _onResult='FIRE list.queryEnd=true;',**condPars)
                                     
        grid = gridpane.virtualGrid(nodeId='maingrid', structpath="list.view.structure", storepath=".data", autoWidth=False,
                                selectedIndex='list.rowIndex', rowsPerPage=self.rowsPerPage(), sortedBy='^list.grid.sorted',
                                connect_onSelectionChanged='SET list.noSelection = (genro.wdgById("maingrid").selection.getSelectedCount()==0)',
                                connect_onRowDblClick='SET list.selectedIndex = GET list.rowIndex;',
                                connect_onRowContextMenu="FIRE list.onSelectionMenu = true;")
        
    
    def toolboxFields(self,pane):
        treediv=pane.div(_class='treeContainer')
        treediv.tree(storepath='gnr.qb.fieldstree',persist=False,
                     inspect='shift', labelAttribute='caption',
                     _class='fieldsTree',
                     getIconClass='if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}',
                     dndController="dijit._tree.dndSource",
                     onDndDrop="function(){this.onDndCancel();}::JS",
                     checkAcceptance='function(){return false;}::JS',
                     checkItemAcceptance='function(){return false;}::JS')
        
        #left.accordionPane(title='!!Campi collegati')
         #action="""FIRE list.query.loadQuery=$1.pkey;
    
    def toolboxQueries(self, container):
        self.savedQueryController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.query.saved_menu',persist=False, inspect='shift',
                          labelAttribute='caption',connect_ondblclick='FIRE list.runQuery = true;',
                          selected_pkey='list.query.selectedId', selected_code='list.query.selectedCode',
                          _class='queryTree',
                             _saved='^list.query.saved', _deleted='^list.query.deleted')
        #btnpane = container.contentPane(region='top', height='30px').toolbar()
        self.saveQueryButton(treepane)
        self.deleteQueryButton(treepane)
        #btnpane.button('Add new query', iconClass='tb_button db_add', fire='list.query.new',showLabel=False)

    
    def savedQueryController(self, pane):
        pane.dataRemote('list.query.saved_menu', 'list_query', tbl=self.maintable, cacheTime=10)
        pane.dataRpc('list.query.where', 'load_query', id='^list.query.selectedId', _if='id',
                  _onResult='genro.querybuilder.buildQueryPane();')
        
        pane.dataRpc('list.query.where', 'new_query', filldefaults=True, _init=True, sync=True)
        
        pane.dataRpc('list.query.where', 'new_query', _fired='^list.query.new', _deleted='^list.query.deleted',
                                    _onResult='genro.querybuilder.buildQueryPane();')

    
    def saveQueryButton(self, pane):
        dlg = pane.dropdownbutton('Save Query', iconClass='tb_button db_save',nodeId='save_query_btn',hidden=True,
                                  arrow=False,showLabel=False).tooltipDialog(nodeId='save_query_dlg', width='35em', datapath='list.query',height='35ex')
        fields = dlg.div(font_size='0.9em',_class='pbl_roundedGroup')
        fb = fields.formbuilder(cols=1)
        fb.textBox(lbl='!!Code' ,value='^.where?code', width='25em')
        fb.textarea(lbl='!!Description' ,value='^.where?description', width='25em', border='1px solid gray')
        fb.checkbox(lbl='!!Private' ,value='^.where?private')
        fb.textBox(lbl='!!Permissions' ,value='^.where?auth_tags', width='25em')
        buttons = dlg.div(font_size='0.9em', _class='tt_dialog_bottom')
        buttons.div('Save',connect_onclick='FIRE .save', _class='tt_bottom_btn', float='right')
        buttons.div('cancel',connect_onclick='genro.wdgById("save_query_dlg").onCancel();',_class='tt_bottom_btn', float='right')
        
        dlg.dataRpc('.saveResult', 'save_query', userobject='=.where',
                       _fired='^.save', _POST=True, _onResult='genro.wdgById("save_query_dlg").onCancel();FIRE .saved = true')

    
    def deleteQueryButton(self, pane):
        dlg = pane.dropdownbutton('Delete query', nodeId='delete_query_btn',iconClass='icnBaseTrash',
                                hidden=True, arrow=False,showLabel=False).tooltipDialog(nodeId='delete_query_dlg', width='25em', datapath='list.query')
        msg = dlg.div(font_size='0.9em',_class='pbl_roundedGroup',height='3ex',padding='10px')
        msg.div('!!Do you really want to delete the query: ')
        msg.span('^.selectedCode')
        
        buttons = dlg.div(font_size='0.9em', _class='tt_dialog_bottom')
        buttons.div('!!Delete', connect_onclick='FIRE ^.delete', _class='tt_bottom_btn', float='right')
        buttons.div('!!Cancel', connect_onclick='genro.wdgById("delete_query_dlg").onCancel();', _class='tt_bottom_btn', float='right')

        
        dlg.dataRpc('.deleteResult', 'delete_query', id='=list.query.selectedId',
                       _fired='^.delete', _onResult='genro.wdgById("delete_query_dlg").onCancel();FIRE .deleted = true')
    
    
    def toolboxActions(self, container):
        self.actionsController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.actions.actions_menu', persist=False, inspect='shift',
                          labelAttribute='caption',
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
                          _class='queryTree',
                             _saved='^list.view.saved', _deleted='^list.view.deleted')
        #btnpane = container.contentPane(region='top', height='30px').toolbar()
        self.saveViewButton(treepane)
        self.deleteViewButton(treepane)
        #btnpane.button('Add View', iconClass='tb_button db_add', fire='list.view.new',showLabel=False)
        
    def savedViewController(self, pane):
        pane.dataRemote('list.view.saved_menu', 'list_view', tbl=self.maintable, cacheTime=10)
        pane.dataRpc('list.view.structure', 'load_view', id='^list.view.selectedId', _if='id',
                    _onResult='genro.viewEditor.colsFromBag();'
                  )
        
        #pane.dataRpc('list.view.structure', 'new_view', filldefaults=True, _init=True, sync=True)
        
        pane.dataRpc('list.view.structure', 'new_view', _fired='^list.view.new', _deleted='^list.view.deleted',
                                    _onResult='genro.viewEditor.colsFromBag();', filldefaults='^gnr.onStart'
                                    )

    
    def saveViewButton(self, pane):
        dlg = pane.dropdownbutton('Save Views', iconClass='tb_button db_save',nodeId='save_view_btn', hidden=True,
                                  arrow=False,showLabel=False).tooltipDialog(nodeId='save_view_dlg', width='35em', datapath='list.view')
        
        fields = dlg.div( font_size='0.9em')
        fb = fields.formbuilder(cols=1)
        fb.textBox(lbl='!!Code' ,value='^.structure?code', width='25em')
        fb.textarea(lbl='!!Description' ,value='^.structure?description', width='25em', border='1px solid gray')
        fb.checkbox(lbl='!!Private' ,value='^.structure?private')
        fb.textBox(lbl='!!Permissions' ,value='^.structure?auth_tags', width='25em')
        
        buttons = dlg.div(height='2em',  font_size='0.9em')
        buttons.button('!!Save', fire='.save', iconClass='icnBaseOk', float='right')
        buttons.button('!!Cancel', action='genro.wdgById("save_view_dlg").onCancel();', iconClass='icnBaseCancel', float='right')
        
        dlg.dataRpc('.saveResult', 'save_view', userobject='=.structure',
                       _fired='^.save', _POST=True, _onResult='genro.wdgById("save_view_dlg").onCancel();FIRE .saved = true')

    
    def deleteViewButton(self, pane):
        dlg = pane.dropdownbutton(iconClass='icnBaseTrash', hidden=True, arrow=False,showLabel=False,nodeId='delete_view_btn').tooltipDialog(nodeId='delete_view_dlg', width='25em', datapath='list.view')
        msg = dlg.div( font_size='0.9em')
        msg.span('!!Do you really want to delete the query: ')
        msg.span('^.selectedCode')
        
        buttons = dlg.div(height='2em',  font_size='0.9em')
        buttons.button('!!Delete', fire='^.delete', iconClass='icnBaseTrash', float='right')
        buttons.button('!!Cancel', action='genro.wdgById("delete_view_dlg").onCancel();', iconClass='icnBaseCancel', float='right')        
        dlg.dataRpc('.deleteResult', 'delete_view', id='=list.view.selectedId',
                       _fired='^.delete', _onResult='genro.wdgById("delete_view_dlg").onCancel();FIRE .deleted = true')
    
        
    def formController(self,pane):
        self.formTitleBase(pane)
        pane.dataFormula('form.locked','statusLocked || recordLocked',statusLocked='^status.locked',
                                     recordLocked='=form.recordLocked',fired='^gnr.forms.formPane.loaded')
        pane.dataFormula('form.unlocked','!locked',locked='^form.locked')
        pane.dataFormula('form.canWrite','(!locked ) && writePermission',locked='^form.locked',writePermission='=usr.writePermission',_init=True)
        pane.dataFormula('form.canDelete','(!locked) && deletePermission',locked='^form.locked',deletePermission='=usr.deletePermission',_init=True)
        pane.dataFormula('form.lockAcquire','(!statusLocked) && lock',statusLocked='^status.locked',
                                     lock=self.recordLock or False)
        pane.dataController("""
                               SET form.logical_deleted = (GET form.record.__del_ts != null);
                               if (lockId){
                                   alert('lockId:'+lockId)
                               }
                               else if (username){
                                   alert('already locked by:'+username)
                                   SET status.locked=true;
                               }
                              
                            """,
                            lockId='=form.record?lockId',
                            username='=form.record?locking_username',
                            _fired='^form.onRecordLoaded')
        
        self.formLoader('formPane', resultPath='form.record',_fired='^form.doLoad',lock='=form.lockAcquire',
                        table=self.maintable, pkey='=list.selectedId',method='loadRecordCluster',
                        loadingParameters='=gnr.tables.maintable.loadingParameters',
                        onLoading='FIRE form.onRecordLoaded',
                        sqlContextName='sql_record')
        self.formSaver('formPane',resultPath='form.save_result',method='saveRecordCluster',
                        table=self.maintable,_fired='^form.save',_onCalling='FIRE pbl.bottomMsg=msg;',
                        msg ='!!Saving...')
        pane.dataController(""" var msg = '';
                                if(reason=='invalid'){
                                    msg = msg_invalid;
                                }
                                else if(reason=='nochange'){
                                    msg = msg_nochange;
                                }
                                if(msg){
                                    genro.dlg.alert(msg,title);
                                }
                                """,reason="^gnr.forms.formPane.save_failed",
                              msg_nochange='!!No change to save.', 
                              msg_invalid='!!Invalid data, please check the form.',
                              title="!!Warning")
        pane.dataRpc('form.delete_result','deleteRecordCluster', data='=form.record?=genro.getFormChanges("formPane");', _POST=True,
                        table=self.maintable,toDelete='^form.doDeleteRecord')
        pane.dataController("""genro.dlg.ask(askTitle,saveMessage,{save:saveButton,forget:cancelButton},'form.dlgAction');
                              SET form.dlgidx = newidx;
                                   """,
                                newidx='^form.newidx',changed='=gnr.forms.formPane.changed',
                                askTitle="!!Unsaved changes",
                                saveMessage='!!There are unsaved changes',saveButton='!!Save changes',
                                cancelButton='!!Forget changes',
                                _if='changed',_else='SET list.selectedIndex=newidx')
        
        pane.dataController("FIRE form.save;",newidx='=form.dlgidx',
                            result='^form.dlgAction',_if="result=='save'",
                            _else='SET list.selectedIndex=newidx')

        pane.dataFormula('form.atBegin','(idx==0)',idx='^list.selectedIndex')
        pane.dataFormula('form.atEnd','(idx==rowcount-1)',idx='^list.selectedIndex',rowcount='=list.rowcount')
        pane.dataController("""var newidx;
                               if (btn == 'add'){newidx = -1;}
                               else if (btn == 'first'){newidx = 0;}
                               else if (btn == 'last'){newidx = rowcount-1;}
                               else if ((btn == 'prev') && (idx > 0)){newidx = idx-1;}
                               else if ((btn == 'next') && (idx < rowcount-1)){newidx = idx+1;}
                               FIRE form.newidx = newidx;
                            """,btn='^form.navbutton',idx='=list.selectedIndex',
                                rowcount='=list.rowcount')
                                
        pane.dataController(""" var currSet;
                                if (old_pkey != '*newrecord*'){
                                    var newrecords = GET list.newrecords || [];
                                    if(dojo.indexOf(newrecords,pkey)<0){
                                        genro.wdgById("maingrid").rowBagNodeUpdate(idx,record,pkey);
                                        currSet = 'changedrecords';
                                    } 
                               }else{
                                    //Insert
                                        currSet = 'newrecords';
                               }
                               if(currSet){
                                   var cs = genro.getData('list.'+currSet);
                                       if (!cs){
                                            cs = [];
                                            genro.setData('list.'+currSet, cs);
                                       }
                                   cs.push(pkey);
                               }
                               SET list.selectedId = pkey;
                               FIRE pbl.bottomMsg = msg;
                               FIRE form.doLoad;
                            """, record='=form.record',
                                 msg='!!Record saved',
                                 idx='=list.selectedIndex',
                                 pkey='^form.save_result',
                                 old_pkey='=list.selectedId',
                                 error='=form.save_result?msg',
                                 _if='!error',
                                 _else='genro.dlg.alert(error)')
          
        pane.dataController("""SET list.selectedId = null;
                               FIRE pbl.bottomMsg = msg;
                               SET selectedPage = 0;
                               FIRE list.runQuery=true;
                            """,  msg='!!Record deleted', result='^form.delete_result', 
                            _if='result=="ok"', _else='FIRE pbl.bottomMsg=result;')
                                     
    def pageForm(self,pane,bottom):
        bc=pane.borderContainer(nodeId='formRoot',
                                sqlContextName='sql_record',
                                sqlContextRoot='form.record',
                                sqlContextTable=self.maintable)
        self.formController(bc)
        self.formToolbar(bc.contentPane(region='top',_class='sttbl_list_top'))
        self.formBase(bc,datapath='form.record',disabled='^form.locked',region='center',formId='formPane')
        if self.tblobj.logicalDeletionField:
            self.setLogicalDeletionCheckBox(bottom['left'])
                          
    def setLogicalDeletionCheckBox(self, elem):
        elem.div(padding_left='5px',
                 padding_top='2px',
                 hidden='^aux.listpage').checkbox(label='!!Hidden',
                                                  value='^form.logical_deleted',
                                                  disabled='^form.locked')
        elem.dataFormula('aux.listpage', '!selectedpage', selectedpage='^selectedPage', _init=True)
        elem.dataController("""if(logical_deleted){
                                   SET form.record.__del_ts =new Date();
                                   genro.dom.addClass("formRoot", "logicalDeleted");
                               }else{
                                   SET form.record.__del_ts = null;
                                   genro.dom.removeClass("formRoot", "logicalDeleted");
                               }""",
                          logical_deleted='^form.logical_deleted' )

    def formToolbar(self, pane):
        tb = pane.toolbar(height='26px')
        self.confirm(pane,title='!!Confirm record deletion',width='50em',
                           msg='!!Are you sure to delete ?',
                           btn_ok='!!Delete',btn_cancel='!!Cancel',
                           action_ok='FIRE form.doDeleteRecord',
                           fired='^form.deleteRecord')
        t_l = tb.div(float='left',margin_left='4px',width='130px')
        t_l.button('!!First', fire_first='form.navbutton', iconClass="tb_button icnNavFirst", disabled='^form.atBegin', showLabel=False)
        t_l.button('!!Previous', fire_prev='form.navbutton', iconClass="tb_button icnNavPrev", disabled='^form.atBegin', showLabel=False)
        t_l.button('!!Next', fire_next='form.navbutton', iconClass="tb_button icnNavNext", disabled='^form.atEnd', showLabel=False)
        t_l.button('!!Last', fire_last='form.navbutton', iconClass="tb_button icnNavLast", disabled='^form.atEnd', showLabel=False)
        t_r = tb.div(position='absolute',right='0',width='200px')
        self.formtoolbar_right(t_r)
        #t_c = tb.div(height='25px')
                
    def formtoolbar_right(self,t_r):
        if self.userCanDelete() or self.userCanWrite():
            t_r.button('!!Unlock', float='right',fire='status.unlock', 
                        iconClass="tb_button icnBaseLocked", showLabel=False,hidden='^status.unlocked')
            t_r.button('!!Lock', float='right',fire='status.lock', 
                        iconClass="tb_button icnBaseUnlocked", showLabel=False,hidden='^status.locked')
        t_r.button('!!List view', float='right',margin_left='10px', action='FIRE form.newidx = -2;', 
                    iconClass="tb_button tb_listview", showLabel=False)
        t_r.div(position='absolute',top='5px',right='75px',nodeId='formStatus',hidden='^status.locked')
        t_r.data('form.statusClass','greenLight')
        t_r.dataController("""genro.dom.removeClass('formStatus',"greenLight redLight yellowLight");
                              if(isValid){
                                 if(isChanged){
                                     genro.dom.addClass('formStatus',"yellowLight");
                                 }else{
                                     genro.dom.addClass('formStatus',"greenLight");
                                 }
                              }else{
                                    genro.dom.addClass('formStatus',"redLight");
                              }
                              """,isChanged="^gnr.forms.formPane.changed",
                            isValid='^gnr.forms.formPane.valid')
        if self.userCanWrite():
            t_r.button('!!Save', position='absolute',right='90px',fire="form.save", 
                        iconClass="tb_button db_save",showLabel=False,
                        hidden='^status.locked')
            t_r.button('!!Revert',position='absolute', right='115px',fire='form.doLoad', iconClass="tb_button db_revert",
                         disabled='== !_changed', _changed='^gnr.forms.formPane.changed', 
                         showLabel=False, hidden='^status.locked')
            if self.userCanDelete():
                t_r.button('!!Delete', float='left',fire='form.deleteRecord', iconClass="tb_button db_del",
                                   visible='^form.canDelete',disabled='^form.noDelete', showLabel=False)
            t_r.button('!!Add', float='left', fire_add='form.navbutton', iconClass="tb_button db_add",
                         disabled='^form.noAdd', showLabel=False,visible='^form.canWrite')
            
        
    
    def selectionBatchRunner(self, pane, title='', resultpath='aux.cmd.result', fired=None, batchFactory=None,
                             rpc=None,thermofield=None, thermoid=None, endScript=None,
                             stopOnError=False, forUpdate=False, onRow=None, **kwargs):
        """Prepare a batch action on the maintable with a thermometer
           @param pane: it MUST NOT BE a container. Is the pane where selectionBatchRunner
                  append dataController and dialog.
           @param resultpath: the path into the datastore where the result is stored.
           @param fired: the path where you fire the event that launch the dataRpc of selectionBatchRunner.
           @param batchFactory: is used instead of rpc. Name of the Factory Class, used as
                                plugin of table, which executes the standard batch action.
           @param rpc: is used instead of batchFactory. The name of the custum rpc you can use for the batch
                       for every selected row.
        """
        thermoid = None
        if thermofield:
            thermoid = self.getUuid()
            self.thermoDialog(pane, thermoid=thermoid, title=title, fired=fired, alertResult=True)
        pane.dataRpc(resultpath, rpc or 'app.runSelectionBatch',
                     table=self.maintable, selectionName='=list.selectionName',
                     batchFactory=batchFactory, thermoid=thermoid,
                     thermofield=thermofield,
                     pkeys='==genro.wdgById("maingrid").getSelectedPkeys()',
                     fired=fired, _onResult=endScript,
                     stopOnError=stopOnError, forUpdate=forUpdate, onRow=onRow, **kwargs)
        
        dlgid = self.getUuid()
        pane.dataController('genro.wdgById(dlgid).show()', _if='errors',
                            dlgid=dlgid, errors='^%s.errors' % resultpath)
        d = pane.dialog(nodeId=dlgid, title="!!Errors in batch execution", width='27em', height='27em')
        struct = self.newGridStruct()
        rows = struct.view().rows()
        rows.cell('caption',width='8em',name='!!Caption')
        rows.cell('error', name='!!Error')
        d.div(position='absolute', top='28px', right='4px',
            bottom='4px', left='4px').includedView(storepath='%s.errors' % resultpath, struct=struct)
  
    def rpc_new_query(self, filldefaults=False, **kwargs):
        result = Bag()
        if filldefaults:
            querybase = self.queryBase()
        else:
            querybase = {'op':'equal'}
        result.setItem('c_0', querybase.get('val'), op=querybase.get('op'), column=querybase.get('column'),
                                   op_caption='!!%s' % self.db.whereTranslator.opCaption(querybase.get('op')),
                                   column_caption = self.app._relPathToCaption(self.maintable, querybase.get('column')))
        
        resultattr = dict(objtype='query', tbl=self.maintable)
        return result, resultattr

    def rpc_load_query(self, **kwargs):
        return self.app.rpc_loadUserObject(**kwargs)
    
    def rpc_save_query(self, userobject, userobject_attr):
        return self.app.rpc_saveUserObject(userobject, userobject_attr)
    
    def rpc_delete_query(self, id):
        return self.app.rpc_deleteUserObject(id)
    
    def rpc_list_query(self, **kwargs):
        return self.app.rpc_listUserObject(objtype='query', **kwargs)
    
    def rpc_new_view(self, filldefaults=False, **kwargs):
        if filldefaults:
            result=self.lstBase()
        else:
            result = self.newGridStruct()
            result.view().rows()
        resultattr = dict(objtype='view', tbl=self.maintable)
        return result, resultattr
    
    def rpc_load_view(self, **kwargs):
        return self.app.rpc_loadUserObject(**kwargs)
    
    def rpc_save_view(self, userobject, userobject_attr):
        return self.app.rpc_saveUserObject(userobject, userobject_attr)
    
    def rpc_delete_view(self, id):
        return self.app.rpc_deleteUserObject(id)
    
    def rpc_list_view(self, **kwargs):
        return self.app.rpc_listUserObject(objtype='view', **kwargs)
    
    def rpc_list_actions(self, tbl, **kwargs):
        #pkg, tbl = tbl.split('.')
        #actionFolders = self.getResourceList(os.path.join('addOn', tbl))
        #result = Bag()
        #for r in objectsel.data:
        #    attrs = dict([(str(k), v) for k,v in r.items()])
        #    result.setItem(r['code'], None, **attrs)
        #return result
        return
    
    #def rpc_setViewColumns(self, gridId=None, relation_path=None, query_columns=None, **kwargs):
    #    self.app.setContextJoinColumns(self.maintable, contextName='sql_record', reason=gridId,
    #                                   path=relation_path, columns=query_columns)
                                                                                  
    def xmlDebug(self, bag, filename):
        bag.toXml(self.pageLocalDocument('%s.xml' % filename))
    
class ViewExporter(object):
    def rpc_rpcSavedSelection(self, table, view=None, query=None, userid=None, out_mode='tabtext', **kwargs):
        tblobj = self.db.table(table)
        
        columns = tblobj.pkg.loadUserObject(code=view, objtype='view',  tbl=table, userid=userid)[0]
        where = tblobj.pkg.loadUserObject(code=query, objtype='query',  tbl=table, userid=userid)[0]
        
        selection = self.app._default_getSelection(tblobj=tblobj, columns=columns, where=where, **kwargs)
        return selection.output(out_mode)
        
    def savedQueryResult(self, table, view=None, query=None,
                                  order_by=None,group_by=None,
                                  having=None,distinct=False,
                                  excludeLogicalDeleted=True,
                                  **kwargs):
        tblobj = self.db.table(table)
        
        columnsBag = tblobj.pkg.loadUserObject(code=view, objtype='view',  tbl=table)[0]
        columns = self.app._columnsFromStruct(columnsBag)      
        whereBag = tblobj.pkg.loadUserObject(code=query, objtype='query',  tbl=table)[0]
        whereBag._locale = self.locale
        whereBag._workdate = self.workdate
        where, kwargs = tblobj.sqlWhereFromBag(whereBag, kwargs)
        
        query=tblobj.query(columns=columns,distinct=distinct, where=where,
                        order_by=order_by, group_by=group_by,having=having,
                        excludeLogicalDeleted=excludeLogicalDeleted,**kwargs)
        return query
