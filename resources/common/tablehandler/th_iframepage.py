    
# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-03-11.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag

class TableHandlerPage(BaseComponent):
    def onIniting(self, url_parts, request_kwargs):
        self.mixin_path = '/'.join(url_parts)
        pkg = url_parts.pop(0)
        tablename = url_parts.pop(0)
        table = '%s.%s' %(pkg,tablename)
        self.maintable = str(table)
        self.mixinComponent(pkg,'tables',tablename,'lists','%s:Main' %tablename)
        while len(url_parts)>0: 
            url_parts.pop(0)

    def main(self, root,**kwargs):
        frame = root.framePane(frameCode='mainstack',datapath='main',center_widget='StackContainer')
        frame.iframe()

class RecordPage(BaseComponent):
    py_requires='gnrcomponents/formhandler:FormHandler'
    def tableWriteTags(self):
        return 'user'

    def tableDeleteTags(self):
        return 'user'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def onIniting(self, url_parts, request_kwargs):
        self.mixin_path = '/'.join(url_parts)
        pkg = url_parts.pop(0)
        tablename = url_parts.pop(0)
        table = '%s.%s' %(pkg,tablename)
        self.maintable = table
        self.mixinComponent(pkg,'tables',tablename,'forms','%s:Main' %tablename)
        if url_parts:
            request_kwargs['pkey'] = url_parts.pop(0)
        while len(url_parts)>0: 
            url_parts.pop(0)

    def userRecord(self, path=None):
        if not hasattr(self, '_userRecord'):
            user = self.pageArgs.get('_user_')
            if not user or not( 'passpartout' in self.userTags):
                user = self.user
            self._userRecord = self.db.table('adm.user').record(username=user).output('bag')
        return self._userRecord[path]
    
    def main(self, root, pkey='*newrecord*',**kwargs):
        form = root.frameForm(frameCode = 'mainform', datapath= 'form',
                              pkeyPath='.pkey',
                              center_widget='BorderContainer')
        form.formStore(storepath ='.record',
                       table= self.maintable,
                       handler = 'recordCluster',
                       onSaved='reload',
                       startKey = pkey)
        top = form.top.slotToolbar('*,|,semaphore,|,formcommands,|,locker')
        self.formCb(form,region='center')
        
    def formCb(self, bc):
        pass

class ListPage(BaseComponent):
    py_requires=""" tablehandler/th_core,
                    tablehandler/th_extra:TagsHandler,
                     tablehandler/th_extra:QueryHelper,
                     tablehandler/th_extra:FiltersHandler,
                     tablehandler/th_extra:HierarchicalViewHandler"""
    js_requires = 'tablehandler/th_script'
    css_requires = 'tablehandler/th_style'
    
    def onIniting(self, url_parts, request_kwargs):
        self.mixin_path = '/'.join(url_parts)
        pkg = url_parts.pop(0)
        tablename = url_parts.pop(0)
        table = '%s.%s' %(pkg,tablename)
        self.maintable = str(table)
        self.mixinComponent(pkg,'tables',tablename,'lists','%s:Main' %tablename)
        while len(url_parts)>0: 
            url_parts.pop(0)
            
            
    def main(self, root,**kwargs):
        condition = self.conditionBase()
        condPars = {}
        if condition:
            condPars = condition[1] or {}
            condition = condition[0]
        
        frame = root.framePane(frameCode='mainlist',datapath='list')
        self.listToolbar(frame.top)
        self.listController(frame)
        iv = frame.includedView(struct=self.lstBase,_newGrid=True)
        store = iv.selectionStore(table=self.maintable, columns='=.columns',
                           chunkSize=self.rowsPerPage()*4,
                           where='=.query.where', sortedBy='=.sorted',
                           pkeys='=.query.pkeys', _fired='^.runQuery',
                           selectionName='*', recordResolver=False, condition=condition,
                           sqlContextName='standard_list', totalRowCount='=.tableRecordCount',
                           row_start='0', 
                           excludeLogicalDeleted='^.excludeLogicalDeleted',
                           applymethod='onLoadingSelection',
                           timeout=180000, selectmethod='=.selectmethod',
                           selectmethod_prefix='customQuery',
                           _onCalling=self.onQueryCalling(),
                           **condPars)  
        store.addCallback('FIRE list.queryEnd=true; SET list.selectmethod=null; return result;')
        frame.data('.baseQuery', self.queryFromQueryBase())
        frame.dataRpc('list.currentQueryCount', 'app.getRecordCount', condition=condition,
                     fired='^list.updateCurrentQueryCount',
                     table=self.maintable, where='=list.query.where',
                     excludeLogicalDeleted='=list.excludeLogicalDeleted',
                     **condPars)
        frame.dataController("""genro.setData("list.query.where",baseQuery.deepCopy(),{objtype:"query", tbl:maintable});
                               //genro.querybuilder.buildQueryPane(); 
                               SET list.view.selectedId = null;
                               if(!fired&&runOnStart){
                                    FIRE list.runQuery
                               }
                            """,
                            _onStart=True, baseQuery='=list.baseQuery', maintable=self.maintable,
                            fired='^list.query.new',
                            runOnStart=self.queryBase().get('runOnStart', False))
                           
    
    
    
######################################## COMPATIBILITY LAYER ##################################
    def tableRecordCount(self):
        """redefine to avoid the count query"""
        return True

    
    def rowsPerPage(self):
        return 20
        
    def conditionBase(self):
        return dict()
    
    def rpc_onLoadingSelection(self,selection):
        pass
        
    def onQueryCalling(self):
        return None
    
    def listCustomCbBag(self, prefix=None, basename=None, cb=None):
        cblist = sorted(
                [func_name for func_name in dir(self) if func_name.startswith(prefix) and func_name != prefix]) or []
        if basename:
            cblist = [basename] + cblist
        menuBag = Bag()
        for funcname in cblist:
            name = funcname[len(prefix):]
            handler = getattr(self, funcname)
            label = name or '_base'
            if cb:
                cb(label, handler)
            menuBag.setItem(label, None, caption=handler.__doc__ or name.title() or 'Base')
        return menuBag

    
    def listViewStructures(self, pane):
        """Prepare databag for"""
        structures = Bag()

        def setInStructureCb(label, handler):
            structures.setItem(label, handler(self.newGridStruct(maintable=self.maintable)), objtype='view', tbl=self.maintable)

        viewMenu = self.listCustomCbBag('lstBase_', 'lstBase', cb=setInStructureCb)
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

    def userCanWrite(self):
        return self.application.checkResourcePermission(self.tableWriteTags(), self.userTags)

    def userCanDelete(self):
        return self.application.checkResourcePermission(self.tableDeleteTags(), self.userTags)

    def tableWriteTags(self):
        return 'superadmin'

    def tableDeleteTags(self):
        return 'superadmin'
    def pluralRecordName(self):
        return self.tblobj.attributes.get('name_plural', 'Records')


    def listController(self, pane):
        pane.data('list.excludeLogicalDeleted', True)
        pane.data('aux.showDeleted', False)
        self.listViewStructures(pane)
        pane.dataController(
                """genro.querybuilder = new gnr.GnrQueryBuilder("query_root", "%s", "list.query.where");""" % self.maintable
                , _init=True)
        pane.dataController(
                """genro.queryanalyzer = new gnr.GnrQueryAnalyzer("translator_root","list.query.where","list.runQueryDo")"""
                , _onStart=True)
        pane.dataController("""genro.querybuilder.createMenues();
                                  dijit.byId('qb_fields_menu').bindDomNode(genro.domById('fastQueryColumn'));
                                  dijit.byId('qb_not_menu').bindDomNode(genro.domById('fastQueryNot'));
                                  //genro.querybuilder.buildQueryPane();
                                  """, _onStart=True)
        pane.data('usr.writePermission', self.userCanWrite())
        pane.data('usr.deletePermission', self.userCanDelete())
        pane.data('usr.unlockPermission', self.userCanDelete() or self.userCanWrite())
        pane.dataFormula('status.locked', 'true', _onStart=True)
        condition = self.conditionBase()
        condPars = {}
        if condition:
            condPars = condition[1] or {}
            condition = condition[0]
        pane.data('list.plural', self.pluralRecordName())
        pane.data('list.rowcount', 0)

        if self.tableRecordCount():
            pane.dataRpc('list.rowtotal', 'app.getRecordCount', _onStart=300,
                         table=self.maintable, where=condition, **condPars)

        #pane.data('list',dict(plural=self.pluralRecordName(), rowcount=0,
        #                      rowtotal=self.tblobj.query(where=condition,**condPars).count())) # mettere come RPC per aggiornare non solo al caricamento

        pane.dataFormula('list.canWrite', '(!locked ) && writePermission', locked='^status.locked',
                         writePermission='=usr.writePermission', _init=True)
        pane.dataFormula('list.canDelete', '(!locked) && deletePermission', locked='^status.locked',
                         deletePermission='=usr.deletePermission', _init=True)
        
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
                           
    def listToolbar(self, pane):
        toolbarKw = dict()
        tagSlot = ''
        if self.hasTags():
            tagSlot = '15,|,tagsbtn,|,'
            toolbarKw['tagsbtn_mode'] = 'list'
        pane.slotToolbar('left_top_opener,|,5,queryfb,iv_runbtn,%sviewmenu,filtermenu,*,|,form_add,form_locker,5' %tagSlot,
                        iv_runbtn_action='FIRE list.runQueryButton;',form_add_parentForm='formPane',
                        form_locker_parentForm='formPane',**toolbarKw)

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
    def th_mainlist_queryfb(self, pane,**kwargs):
        queryfb = pane.formbuilder(cols=5, datapath='.query.where', _class='query_form',
                                   border_spacing='0', onEnter='genro.fireAfter("list.runQuery",true,10);',
                                   float='left')
        queryfb.div('^.c_0?column_caption', min_width='12em', _class='smallFakeTextBox floatingPopup',
                    nodeId='fastQueryColumn',
                     dropTarget=True,
                    lbl='!!Search',**{'onDrop_gnrdbfld_%s' %self.maintable.replace('.','_'):"genro.querybuilder.onChangedQueryColumn(this,data);"})
        optd = queryfb.div(_class='smallFakeTextBox', lbl='!!Op.', lbl_width='4em')

        optd.div('^.c_0?not_caption', selected_caption='.c_0?not_caption', selected_fullpath='.c_0?not',
                 display='inline-block', width='1.5em', _class='floatingPopup', nodeId='fastQueryNot',
                 border_right='1px solid silver')
        optd.div('^.c_0?op_caption', min_width='7em', nodeId='fastQueryOp', readonly=True,
                 selected_fullpath='.c_0?op', selected_caption='.c_0?op_caption',
                 connectedMenu='==genro.querybuilder.getOpMenuId(_dtype);',
                 action="genro.querybuilder.onChangedQueryOp($2,$1);",
                 _dtype='^.c_0?column_dtype',
                 _class='floatingPopup', display='inline-block', padding_left='2px')
        value_textbox = queryfb.textbox(lbl='!!Value', value='^.c_0', width='12em', lbl_width='5em',
                                        _autoselect=True,
                                        row_class='^.c_0?css_class', position='relative',
                                        disabled='==(_op in genro.querybuilder.helper_op_dict)', _op='^.c_0?op',
                                        validate_onAccept='genro.queryanalyzer.checkQueryLineValue(this,value);',
                                        _class='st_conditionValue')

        value_textbox.div('^.c_0', hidden='==!(_op in genro.querybuilder.helper_op_dict)',
                          connect_onclick="if(GET .c_0?op in genro.querybuilder.helper_op_dict){FIRE list.helper.queryrow='c_0';}"
                          ,
                          _op='^.c_0?op', _class='helperField')
        
        queryfb.dataFormula('list.currentQueryCountAsString', 'msg.replace("_rec_",cnt)',
                            cnt='^list.currentQueryCount', _if='cnt', _else='',
                            msg='!!Current query will return _rec_ items')
        queryfb.dataController("""if(fired=='Shift'){
                                     FIRE list.showQueryCountDlg;
                                     }else{
                                         FIRE list.runQuery;
                                     }""", fired='^list.runQueryButton')
        queryfb.dataController("""SET list.currentQueryCountAsString = waitmsg;
                                     genro.fireAfter('list.updateCurrentQueryCount');
                                     genro.dlg.alert('^list.currentQueryCountAsString',dlgtitle);
                                  """, _fired="^list.showQueryCountDlg", waitmsg='!!Working.....',
                               dlgtitle='!!Current query record count')
      
    def queryFromQueryBase(self):
        result = Bag()
        querybase = self.queryBase()
        op_not = querybase.get('op_not', 'yes')
        column = querybase.get('column')
        column_dtype = None
        if column:
            column_dtype = self.tblobj.column(column).getAttr('dtype')
        not_caption = '&nbsp;' if op_not == 'yes' else '!!not'
        result.setItem('c_0', querybase.get('val'),
                       {'op': querybase.get('op'), 'column': column,
                        'op_caption': '!!%s' % self.db.whereTranslator.opCaption(querybase.get('op')),
                        'not': op_not, 'not_caption': not_caption,
                        'column_dtype': column_dtype,
                        'column_caption': self.app._relPathToCaption(self.maintable, column)})
        return result
