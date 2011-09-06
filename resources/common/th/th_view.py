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
                     gnrcomponents/framegrid:FrameGrid,
                     gnrcomponents/batch_handler/batch_handler:TableScriptHandler
                     """
                         
    @extract_kwargs(condition=True)
    @struct_method
    def th_tableViewer(self,pane,frameCode=None,table=None,relation=None,th_pkey=None,viewResource=None,
                       reloader=None,virtualStore=None,condition=None,condition_kwargs=None,**kwargs):
        self._th_mixinResource(frameCode,table=table,resourceName=viewResource,defaultClass='View')
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
    def th_thFrameGrid(self,pane,frameCode=None,table=None,th_pkey=None,reloader=None,virtualStore=None,extendedQuery=None,
                       top_kwargs=None,condition=None,condition_kwargs=None,grid_kwargs=None,**kwargs):
        extendedQuery = virtualStore and extendedQuery
        condition_kwargs = condition_kwargs
        if condition:
            condition_kwargs['condition'] = condition
        top_kwargs=top_kwargs or dict()
        if virtualStore:
            base_slots = ['queryfb','2','runbtn','|','queryMenu','|','10','export','5','resourcePrints','5','resourceActions','5','resourceMails','*','count','5']
        else:
            base_slots = ['vtitle','count','*','searchOn']
        base_slots = ','.join(base_slots)
        if 'slots' in top_kwargs:
            top_kwargs['slots'] = top_kwargs['slots'].replace('#',base_slots)
        else:
            top_kwargs['slots']= base_slots
        leftTools = '5,fieldsTree,*'
        top_kwargs['height'] = top_kwargs.get('height','20px')
        grid_kwargs['configurable'] = grid_kwargs.get('configurable',True)
        frame = pane.frameGrid(frameCode=frameCode,childname='view',table=table,
                               struct=self._th_hook('struct',mangler=frameCode),
                               datapath='.view',top_kwargs=top_kwargs,_class='frameGrid',
                               tools=leftTools,grid_kwargs=grid_kwargs,**kwargs)   
        if grid_kwargs['configurable']:
            frame.left.viewConfigurator(table,frameCode)                         
        self._th_viewController(frame,table=table)
        frame.gridPane(table=table,reloader=reloader,th_pkey=th_pkey,virtualStore=virtualStore,
                        condition=condition_kwargs)
        return frame
        
    @struct_method
    def th_viewConfigurator(self,pane,table,th_root):
        bar = pane.slotBar('confBar,fieldsTree,*',min_width='160px',closable='close',fieldsTree_table=table,
                            fieldsTree_height='100%',splitter=True)
        confBar = bar.confBar.slotToolbar('viewsMenu,*,saveView,5,deleteView',_class='retinaSlotbar')
        gridId = '%s_grid' %th_root
        confBar.saveView.slotButton('Save View',iconClass='save16',
                                        action='genro.grid_configurator.saveGridView(gridId);',gridId=gridId)
        confBar.deleteView.slotButton('Delete View',iconClass='trash16',
                                    action='genro.grid_configurator.deleteGridView(gridId);',
                                    gridId=gridId,disabled='^.grid.currViewAttrs.pkey?=!#v')

        
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
        th_root = inattr['th_root']
        table = inattr['table']
        pane.div(_class='icnBaseLens buttonIcon').menu(storepath='.query.menu',_class='smallmenu',modifiers='*',
                    action="""
                                SET .query.currentQuery = $1.fullpath;
                                if(!$1.pkey){
                                    SET .query.queryEditor = false;
                                }
                                SET .query.menu.__queryeditor__?disabled=$1.selectmethod!=null;
                            """)
                    
        pane.dataController("""TH(th_root).querybuilder.onChangedQuery(currentQuery);
                                
                          """,currentQuery='^.query.currentQuery',th_root=th_root)
        q = Bag()
        pyqueries = self._th_hook('query',mangler=th_root,asDict=True)
        for k,v in pyqueries.items():
            pars = dictExtract(dict(v.__dict__),'query_')
            code = pars.get('code')
            q.setItem(code,None,tip=pars.get('description'),selectmethod=v,**pars)
        pane.data('.query.pyqueries',q)
        pane.dataRemote('.query.menu',self.th_menuQueries,pyqueries='=.query.pyqueries',
                        table=table,th_root=th_root,caption='Queries',cacheTime=5)
        pane.dataRemote('.query.savedqueries',self.th_menuQueries,
                        table=table,th_root=th_root,cacheTime=5,editor=False)
                        
        pane.dataController("TH(th_root).querybuilder.queryEditor(open);",
                        th_root=th_root,open="^.query.queryEditor")
        dialog = pane.dialog(title='==_code?_pref+_code:_newtitle;',_newtitle='!!Save new query',
                                _pref='!!Save query: ',_code='^.query.queryAttributes.code',
                                datapath='.query.queryAttributes')
        pane.dataController("dialog.show();",_fired="^.query.savedlg",dialog=dialog.js_widget)
        pane.dataRpc('dummy',self.th_deleteUserObject,pkey='=.query.queryAttributes.pkey',table=table,_fired='^.query.delete',
                   _onResult='FIRE .query.currentQuery="__newquery__";')
        pane.dataRpc('.queryAttributes.pkey',self.th_saveUserObject,objtype='query',table=table,id='=.queryAttributes.id',data='=.where',code='=.queryAttributes.code',
                    description='=.queryAttributes.description', authtags='=.queryAttributes.authtags', private='=.queryAttributes.private', 
                   _fired='^.save',_if='code',_onResult='FIRE .saved;',datapath='.query')
        self.th_saveUserObjectDialog(dialog,table)


    @struct_method
    def th_slotbar_viewsMenu(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        th_root = inattr['th_root']
        table = inattr['table']
        gridId = '%s_grid' %th_root
        pane.div('^.currViewAttrs.caption',_class='floatingPopup',font_size='.8em',padding_right='10px',padding_left='2px',
                    margin='1px',rounded=4,width='10em',overflow='hidden',text_align='left',cursor='pointer',
                    font_weight='bold',color='#555',datapath='.grid').menu(storepath='.structMenuBag',
                _class='smallmenu',modifiers='*',selected_fullpath='.currViewPath')
        pane.dataController("genro.grid_configurator.loadView(gridId, selpath);",selpath="^.grid.currViewPath",gridId=gridId,_onStart=True)
        q = Bag()
        pyviews = self._th_hook('struct',mangler=th_root,asDict=True)
        for k,v in pyviews.items():
            prefix,name=k.split('_struct_')
            q.setItem(name,self._prepareGridStruct(v,table=table),caption=v.__doc__)
        pane.data('.grid.resource_structs',q)
        

        pane.dataRemote('.grid.structMenuBag',self.th_menuViews,pyviews=q.digest('#k,#a.caption'),
                        table=table,th_root=th_root,cacheTime=5)
    @struct_method
    def th_slotbar_resourcePrints(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        th_root = inattr['th_root']
        table = inattr['table']
        pane.div(_class='buttonIcon icnBasePrinter').menu(modifiers='*',storepath='.resources.print.menu',
                    action="""
                            var kw = objectExtract(this.getInheritedAttributes(),"batch_*",true);
                            kw.resource = $1.resource;
                            kw['selectedRowidx'] = genro.wdgById(kw.gridId).getSelectedRowidx();
                            genro.publish({topic:"table_script_run",parent:true},kw)
                            """,
                    batch_selectionName=th_root,batch_gridId='%s_grid' %th_root,batch_table=table,batch_res_type='print',
                    batch_sourcepage_id=self.page_id)
        pane.dataRemote('.resources.print.menu',self.table_script_resource_tree_data,res_type='print', table=table,cacheTime=5)

    @struct_method
    def th_slotbar_resourceActions(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        th_root = inattr['th_root']
        pane.div(_class='buttonIcon icnBaseAction').menu(modifiers='*',storepath='.resources.action.menu',action="""
                            var kw = objectExtract(this.getInheritedAttributes(),"batch_*",true);
                            kw.resource = $1.resource;
                            kw['selectedRowidx'] = genro.wdgById(kw.gridId).getSelectedRowidx();
                            genro.publish({topic:"table_script_run",parent:true},kw)
                            """,
                    batch_selectionName=th_root,batch_gridId='%s_grid' %th_root,batch_table=table,batch_res_type='action',
                    batch_sourcepage_id=self.page_id)
        pane.dataRemote('.resources.action.menu',self.table_script_resource_tree_data,res_type='action', table=table,cacheTime=5)

    @struct_method
    def th_slotbar_resourceMails(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        th_root = inattr['th_root']
        pane.div(_class='buttonIcon icnBaseEmail').menu(modifiers='*',storepath='.resources.mail.menu',action="""
                            var kw = objectExtract(this.getInheritedAttributes(),"batch_*",true);
                            kw.resource = $1.resource;
                            kw['selectedRowidx'] = genro.wdgById(kw.gridId).getSelectedRowidx();
                            genro.publish({topic:"table_script_run",parent:true},kw)
                            """,
                    batch_selectionName=th_root,batch_gridId='%s_grid' %th_root,batch_table=table,batch_res_type='mail',
                    batch_sourcepage_id=self.page_id)        
        pane.dataRemote('.resources.mail.menu',self.table_script_resource_tree_data,res_type='mail', table=table,cacheTime=5)


    @struct_method
    def th_gridPane(self, frame,table=None,reloader=None,th_pkey=None,
                        virtualStore=None,condition=None):
        table = table or self.maintable
        th_root = frame.getInheritedAttributes()['th_root']
        sortedBy=self._th_hook('order',mangler=th_root)()
        if sortedBy :
            if not filter(lambda e: e.startswith('pkey'),sortedBy.split(',')):
                sortedBy = sortedBy +',pkey' 
        frame.data('.grid.sorted',sortedBy or 'pkey')
        if th_pkey:
            querybase = dict(column=self.db.table(table).pkey,op='equal',val=th_pkey,runOnStart=True)
        else:
            querybase = self._th_hook('query',mangler=th_root)() or dict()
        queryBag = self._prepareQueryBag(querybase,table=table)
        frame.data('.baseQuery', queryBag)
        frame.dataFormula('.title','view_title || name_plural',name_plural='=.table?name_plural',view_title='=.title',_init=True)
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
        """, hiddencolumns=self._th_hook('hiddencolumns',mangler=th_root)(),
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
            selectionName = '*%s' %th_root
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
                               timeout=180000, selectmethod='=.query.queryAttributes.selectmethod',
                               _onCalling=self._th_hook('onQueryCalling',mangler=th_root)(),
                               **condPars)
        store.addCallback('FIRE .queryEnd=true;return result;')        
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
    def th_slotbar_runbtn(self,pane,**kwargs):
        pane.slotButton(label='!!Run query',publish='runbtn',
                               baseClass='no_background',
                               iconClass='tb_button db_query')
    
    @struct_method
    def th_slotbar_queryfb(self, pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table'] 
        th_root = inattr['th_root']
        pane.dataController(
               """var th = TH(th_root);
                  th.querybuilder = new gnr.GnrQueryBuilder(th,this,table,"query_root");
                  th.queryanalyzer = new gnr.GnrQueryAnalyzer(th,this,table);
               """ 
               , _init=True,table=table,th_root = th_root)

        pane.dataController("""var th=TH(th_root)
                                var parslist=[];
                                if(selectmethod){
                                
                              }else if(querybag.getItem("#0?column")){
                                    th.querybuilder.cleanQueryPane(querybag); 
                                    SET .queryRunning = true;
                                    var parslist = th.queryanalyzer.translateQueryPars();
                              }
                              if (parslist.length>0){
                                    th.queryanalyzer.buildParsDialog(parslist);
                                }else{
                                    FIRE .runQueryDo = true;
                              }
                              """,th_root=th_root,_fired="^.runQuery",
                           querybag='=.query.where',
                           selectmethod='=.query.queryAttributes.selectmethod')
                           
        pane.dataFormula('.currentQueryCountAsString', 'msg.replace("_rec_",cnt)',
                           cnt='^.currentQueryCount', _if='cnt', _else='',
                           msg='!!Current query will return _rec_ items')
        pane.dataController("""SET .currentQueryCountAsString = waitmsg;
                              FIRE .updateCurrentQueryCount;
                               genro.dlg.alert(alertmsg,dlgtitle);
                                 """, _fired="^.showQueryCountDlg", waitmsg='!!Working.....',
                              dlgtitle='!!Current query record count',alertmsg='^.currentQueryCountAsString')
        pane.dataController("""
                   var qb = TH(th_root).querybuilder;
                   qb.createMenues();
                   dijit.byId(qb.relativeId('qb_fields_menu')).bindDomNode(genro.domById(qb.relativeId('fastQueryColumn')));
                   dijit.byId(qb.relativeId('qb_not_menu')).bindDomNode(genro.domById(qb.relativeId('fastQueryNot')));
                   SET .query.currentQuery = '__basequery__';
        """,_onStart=True,th_root=th_root)        
        fb = pane.formbuilder(cols=3, datapath='.query.where', _class='query_form',width='600px',overflow='hidden',
                                  border_spacing='0', onEnter='genro.nodeById(this.getInheritedAttributes().target).publish("runbtn",{"modifiers":null});')
        fb.div('^.c_0?column_caption', min_width='12em', _class='fakeTextBox floatingPopup',
                 nodeId='%s_fastQueryColumn' %th_root,
                  dropTarget=True,row_hidden='^.#parent.queryAttributes.extended',
                 lbl='!!Search:',tdl_width='4em',
                 **{str('onDrop_gnrdbfld_%s' %table.replace('.','_')):"TH('%s').querybuilder.onChangedQueryColumn(this,data);" %th_root})
        optd = fb.div(_class='fakeTextBox', lbl='!!Op.', lbl_width='4em')

        optd.div('^.c_0?not_caption', selected_caption='.c_0?not_caption', selected_fullpath='.c_0?not',
                display='inline-block', width='1.5em', _class='floatingPopup', nodeId='%s_fastQueryNot' %th_root,
                border_right='1px solid silver')
        optd.div('^.c_0?op_caption', min_width='7em', nodeId='%s_fastQueryOp' %th_root, 
                selected_fullpath='.c_0?op', selected_caption='.c_0?op_caption',
                connectedMenu='==TH("%s").querybuilder.getOpMenuId(_dtype);' %th_root,
                action="TH('%s').querybuilder.onChangedQueryOp($2,$1);" %th_root,
                _dtype='^.c_0?column_dtype',
                _class='floatingPopup', display='inline-block', padding_left='2px')
        value_textbox = fb.textbox(lbl='!!Value', value='^.c_0', width='12em', lbl_width='5em',
                                       _autoselect=True,
                                       row_class='^.c_0?css_class', position='relative',
                                       disabled='==(_op in TH("%s").querybuilder.helper_op_dict)'  %th_root, _op='^.c_0?op',
                                       connect_onclick="TH('%s').querybuilder.getHelper(this);" %th_root,
                                       _class='st_conditionValue')
        value_textbox.div('^.c_0', hidden='==!(_op in  TH("%s").querybuilder.helper_op_dict)' %th_root,
                         _op='^.c_0?op', _class='helperField')
        fb.div('^.#parent.queryAttributes.description',lbl='!!Search:',tdl_width='4em',colspan=3,
                    row_hidden='^.#parent.queryAttributes.extended?=!#v',width='99%', _class='fakeTextBox buttonIcon',connect_ondblclick='')
        
    def _th_viewController(self,pane,table=None,th_root=None):
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
    js_requires='th/th_querytool'

        
   #@struct_method
   #def th_slotbar_queryTool(self,pane,**kwargs):
   #    inattr = pane.getInheritedAttributes()
   #    mangler = inattr['th_root']
   #    table = inattr['table']
   #    pane.dataRpc('.querypkey',self.th_saveUserObject,objtype='query',table=table,id='=.queryAttributes.id',data='=.where',code='=.queryAttributes.code',
   #                description='=.queryAttributes.description', authtags='=.queryAttributes.authtags', private='=.queryAttributes.private', 
   #                _fired='^.save',_if='code',_onResult='FIRE .saved;',datapath='.query')
   #    pane.dataRpc('dummy',self.th_deleteUserObject,pkey='=.query.querypkey',table=table,_fired='^.query.delete',
   #                _onResult='FIRE .query.loadstandard="__basequery__";')
   #    dialog = pane.dialog(title='==_code?_pref+_code:_newtitle;',_newtitle='!!Save new query',
   #                            _pref='!!Save query: ',_code='^.code',datapath='.query.queryAttr')
   #
   #    self.th_saveUserObjectDialog(dialog,table)
   #    palette = pane.palettePane('%s_queryTool' %mangler,title='!!Query tool',
   #                    dockButton_iconClass='icnBaseLens',
   #                    datapath='.query.where',
   #                    dockButton_baseClass='no_background',
   #                    height='150px',width='400px')
   #    bar = palette.slotToolbar('cap,*,show_fields,editmenu',font_size='.8em',datapath='.#parent')
   #    bar.cap.div(innerHTML='==pref+(code||"-");',pref="!!Query:",code='^.queryAttributes.code')
   #    bar.show_fields.button('!!Show fields',
   #                            palettetitle='!!Fields',
   #                            table=table,
   #                            action="genro.dev.relationExplorer(table,palettetitle,{'left':'20pxpx','top':'20px','height':'270px','width':'180px'})")
   #    menu = bar.editmenu.div(_class='icnBaseEdit buttonIcon').menu(modifiers='*')
   #    menu.menuline(label='!!Save Query',action='this.getAttributeFromDatasource("dialog").show();',dialog=dialog.js_widget)
   #    menu.menuline(label='!!Save As...',action='SET .queryAttr = new gnr.GnrBag(); this.getAttributeFromDatasource("dialog").show();',
   #                                dialog=dialog.js_widget,disabled='^.querypkey?=!#v')
   #    menu.menuline(label='-')
   #    menu.menuline(label='!!Delete Query',action='FIRE .delete;',disabled='^.querypkey?=!#v')
   #
   #    palette.div(nodeId='%s_query_root' %mangler)

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
    def th_menuViews(self,table=None,th_root=None,pyviews=None,**kwargs):
        result = Bag()
        gridId = '%s_grid' %th_root
        result.setItem('__baseview__', None,caption='Base View',gridId=gridId)
        if pyviews:
            for k,caption in pyviews:
                result.setItem(k.replace('_','.'),None,caption=caption,viewkey=k,gridId=gridId)
        #result.setItem('r_1',None,caption='-')
        self.grid_configurator_savedViewsMenu(result,gridId)
        return result
        
    
    @public_method
    def th_menuQueries(self,table=None,th_root=None,pyqueries=None,editor=True,**kwargs):
        querymenu = Bag()
        if editor:
            querymenu.setItem('__basequery__',None,caption='!!Plain Query',description='!!New query',
                                extended=False)
            querymenu.setItem('r_1',None,caption='-')
        savedqueries = self.package.listUserObject(objtype='query', userid=self.user, tbl=table,authtags=self.userTags)            
        if savedqueries:
            for i, r in enumerate(savedqueries.data):
                attrs = dict([(str(k), v) for k, v in r.items()])
                querymenu.setItem(r['code'] or 's_%i' % i, None,_attributes=attrs)
            querymenu.setItem('r_2',None,caption='-')
        if pyqueries:
            for n in pyqueries:
                querymenu.setItem(n.label,n.value,_attributes=n.attr)
            querymenu.setItem('r_3',None,caption='-')
        
        if editor:
            querymenu.setItem('__queryeditor__',None,caption='!!Query editor',action="""
                                                                var currentQuery = GET .query.currentQuery;
                                                                SET .query.queryAttributes.extended=true; 
                                                                SET .query.queryEditor=true;""")
        else:
            querymenu.setItem('__newquery__',None,caption='!!New query',description='!!New query',
                                extended=True)

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