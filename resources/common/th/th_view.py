# -*- coding: UTF-8 -*-

# th_view.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs

from gnr.core.gnrdict import dictExtract
from gnr.core.gnrbag import Bag

class TableHandlerView(BaseComponent):
    py_requires = """th/th_lib:QueryHelper,
                     th/th_view:THViewUtils,
                     gnrcomponents/framegrid:FrameGrid,
                     gnrcomponents/tpleditor:PaletteTemplateEditor,
                     gnrcomponents/batch_handler/batch_handler:TableScriptHandler,
                     gnrcomponents/batch_handler/batch_handler:TableScriptHandlerCaller
                     """
                         
    @extract_kwargs(condition=True)
    @struct_method
    def th_tableViewer(self,pane,frameCode=None,table=None,relation=None,th_pkey=None,viewResource=None,
                       virtualStore=None,condition=None,condition_kwargs=None,**kwargs):
        self._th_mixinResource(frameCode,table=table,resourceName=viewResource,defaultClass='View')
        resourceCondition = self._th_hook('condition',mangler=frameCode,dflt=dict())()
        condition = condition or resourceCondition.pop('condition',None)
        condition_kwargs.update(dictExtract(resourceCondition,'condition_'))
        if relation:
            table,condition = self._th_relationExpand(pane,relation=relation,condition=condition,condition_kwargs=condition_kwargs,original_kwargs=kwargs)             
        view = pane.thFrameGrid(frameCode=frameCode,th_root=frameCode,th_pkey=th_pkey,table=table,
                                 virtualStore=virtualStore,
                                 condition=condition,condition_kwargs=condition_kwargs,**kwargs)
        for side in ('top','bottom','left','right'):
            hooks = self._th_hook(side,mangler=frameCode,asDict=True)
            for hook in hooks.values():
                hook(getattr(view,side))
        viewhook = self._th_hook('view',mangler=frameCode)
        if viewhook:
            viewhook(view)
        return view
    
    @extract_kwargs (top=True)
    @struct_method
    def th_thFrameGrid(self,pane,frameCode=None,table=None,th_pkey=None,virtualStore=None,extendedQuery=None,
                       top_kwargs=None,condition=None,condition_kwargs=None,grid_kwargs=None,configurable=True,unlinkdict=None,**kwargs):
        extendedQuery = virtualStore and extendedQuery
        condition_kwargs = condition_kwargs
        if condition:
            condition_kwargs['condition'] = condition
        top_kwargs=top_kwargs or dict()
        if extendedQuery:
            if 'adm' in self.db.packages:
                templateManager = 'templateManager'
            else:
                templateManager = False
            base_slots = ['5','queryfb','runbtn','queryMenu','15','export','resourcePrints','resourceMails','resourceActions','5',templateManager,'*','count','5']
        elif not virtualStore:
            base_slots = ['5','vtitle','count','*','searchOn']
        else:
            base_slots = ['5','vtitle','count','*']
        base_slots = ','.join([b for b in base_slots if b])
        if 'slots' in top_kwargs:
            top_kwargs['slots'] = top_kwargs['slots'].replace('#',base_slots)
        else:
            top_kwargs['slots']= base_slots
        #top_kwargs['height'] = top_kwargs.get('height','20px')
        grid_kwargs['configurable'] = configurable
        frame = pane.frameGrid(frameCode=frameCode,childname='view',table=table,
                               struct=self._th_hook('struct',mangler=frameCode),
                               datapath='.view',top_kwargs=top_kwargs,_class='frameGrid',
                               grid_kwargs=grid_kwargs,iconSize=16,_newGrid=True,**kwargs)   
        if configurable:
            frame.left.viewConfigurator(table,frameCode)                         
        self._th_viewController(frame,table=table)
        frame.gridPane(table=table,th_pkey=th_pkey,virtualStore=virtualStore,
                        condition=condition_kwargs,unlinkdict=unlinkdict)
        return frame
        
    @struct_method
    def th_viewConfigurator(self,pane,table,th_root):
        bar = pane.slotBar('confBar,fieldsTree,*',min_width='160px',closable='close',fieldsTree_table=table,
                            fieldsTree_height='100%',splitter=True)
        confBar = bar.confBar.slotToolbar('viewsMenu,*,defView,saveView,deleteView',background='whitesmoke',border_right='1px solid gray')
        gridId = '%s_grid' %th_root
        confBar.defView.slotButton('!!Favorite View',iconClass='th_favoriteIcon iconbox star',
                                        action='genro.grid_configurator.setCurrentAsDefault(gridId);',gridId=gridId)
        confBar.saveView.slotButton('!!Save View',iconClass='iconbox save',
                                        action='genro.grid_configurator.saveGridView(gridId);',gridId=gridId)
        confBar.deleteView.slotButton('!!Delete View',iconClass='iconbox trash',
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
        pane.div('^.title',font_size='.9',line_height='20px')

    @struct_method
    def th_slotbar_queryMenu(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        th_root = inattr['th_root']
        table = inattr['table']
        pane.div(_class='iconbox menubox magnifier').menu(storepath='.query.menu',_class='smallmenu',modifiers='*',
                    action="""
                                SET .query.currentQuery = $1.fullpath;
                                if(!$1.pkey){
                                    SET .query.queryEditor = false;
                                }
                                SET .query.menu.__queryeditor__?disabled=$1.selectmethod!=null;
                            """)
                    
        pane.dataController("""TH(th_root).querymanager.onChangedQuery(currentQuery);
                                
                          """,currentQuery='^.query.currentQuery',th_root=th_root)
        q = Bag()
        pyqueries = self._th_hook('query',mangler=th_root,asDict=True)
        for k,v in pyqueries.items():
            pars = dictExtract(dict(v.__dict__),'query_')
            code = pars.get('code')
            q.setItem(code,None,tip=pars.get('description'),selectmethod=v,**pars)
        pane.data('.query.pyqueries',q)
        pane.dataRemote('.query.menu',self.th_menuQueries,pyqueries='=.query.pyqueries',
                        favoriteQueryPath='=.query.favoriteQueryPath',
                        table=table,th_root=th_root,caption='Queries',cacheTime=15)
        pane.dataController("TH(th_root).querymanager.queryEditor(open);",
                        th_root=th_root,open="^.query.queryEditor")
        if not 'adm' in self.db.packages:
            return
        pane.dataRemote('.query.savedqueries',self.th_menuQueries,
                        favoriteQueryPath='=.query.favoriteQueryPath',
                        table=table,th_root=th_root,cacheTime=5,editor=False)
        
        pane.dataRemote('.query.helper.in.savedsets',self.th_menuSets,
                        objtype='list_in',table=table,cacheTime=5)
                        

        pane.dataRpc('dummy',self.db.table('adm.userobject').deleteUserObject,pkey='=.query.queryAttributes.pkey',table=table,_fired='^.query.delete',
                   _onResult='FIRE .query.currentQuery="__newquery__";FIRE .query.refreshMenues;')


    @struct_method
    def th_slotbar_viewsMenu(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        th_root = inattr['th_root']
        table = inattr['table']
        gridId = '%s_grid' %th_root
        pane.div('^.currViewAttrs.caption',_class='floatingPopup',padding_right='10px',padding_left='2px',font_size='.9em',
                    margin='1px',rounded=4,width='10em',overflow='hidden',text_align='left',cursor='pointer',
                    color='#555',datapath='.grid').menu(storepath='.structMenuBag',
                _class='smallmenu',modifiers='*',selected_fullpath='.currViewPath')
        pane.dataController("genro.grid_configurator.loadView(gridId, selpath,th_root);",selpath="^.grid.currViewPath",
                            gridId=gridId,th_root=th_root,_onStart=True)
        q = Bag()
        pyviews = self._th_hook('struct',mangler=th_root,asDict=True)
        for k,v in pyviews.items():
            prefix,name=k.split('_struct_')
            q.setItem(name,self._prepareGridStruct(v,table=table),caption=v.__doc__)
        pane.data('.grid.resource_structs',q)
        

        pane.dataRemote('.grid.structMenuBag',self.th_menuViews,pyviews=q.digest('#k,#a.caption'),
                        table=table,th_root=th_root,favoriteViewPath='=.grid.favoriteViewPath',cacheTime=30)
    @struct_method
    def th_slotbar_resourcePrints(self,pane,flags=None,from_resource=None,**kwargs):
        inattr = pane.getInheritedAttributes()
        th_root = inattr['th_root']
        table = inattr['table']
        pane.div(_class='iconbox menubox print').menu(modifiers='*',storepath='.resources.print.menu',_class='smallmenu',
                    action="""
                            var kw = objectExtract(this.getInheritedAttributes(),"batch_*",true);
                            kw.resource = $1.resource;
                            if($1.template_id){
                                kw.extra_parameters = new gnr.GnrBag({template_id:$1.template_id,table:kw.table});
                                kw.table = null;
                            }
                            th_view_batch_caller(kw);
                            """,
                    batch_gridId='%s_grid' %th_root,batch_table=table,batch_res_type='print',batch_th_root=th_root,
                    batch_sourcepage_id=self.page_id)
        options = self._th_hook('options',mangler=pane)() or dict()
        pane.dataRemote('.resources.print.menu',self.th_printMenu,table=table,flags=flags or options.get('print_flags'),
                        from_resource=from_resource or options.get('print_from_resource',True),cacheTime=5)
    
    @public_method
    def th_printMenu(self,table=None,flags=None,from_resource=True,**kwargs):
        return self._printAndMailMenu(table=table,flags=flags,from_resource=from_resource,res_type='print')

    @struct_method
    def th_slotbar_resourceMails(self,pane,from_resource=None,flags=None,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        th_root = inattr['th_root']
        pane.div(_class='iconbox mail').menu(modifiers='*',storepath='.resources.mail.menu',action="""
                            var kw = objectExtract(this.getInheritedAttributes(),"batch_*",true);
                            kw.resource = $1.resource;
                            if($1.template_id){
                                kw.extra_parameters = new gnr.GnrBag({template_id:$1.template_id,table:kw.table});
                                kw.table = null;
                            }
                            th_view_batch_caller(kw);
                            """,
                    batch_selectionName=th_root,batch_gridId='%s_grid' %th_root,batch_table=table,batch_res_type='mail',
                    batch_sourcepage_id=self.page_id)
        options = self._th_hook('options',mangler=pane)() or dict()
        pane.dataRemote('.resources.mail.menu',self.th_mailMenu,table=table,flags=flags or options.get('mail_flags'),
                        from_resource=from_resource or options.get('mail_from_resource',True),cacheTime=5)
                        
    @public_method
    def th_mailMenu(self,table=None,flags=None,from_resource=True,**kwargs):
        return self._printAndMailMenu(table=table,flags=flags,from_resource=from_resource,res_type='mail')
        
    
    def _printAndMailMenu(self,table=None,flags=None,from_resource=True,res_type=None,**kwargs):
        result = Bag()
        if from_resource:
            resources = self.table_script_resource_tree_data(table=table,res_type=res_type)
            if resources:
                result.update(resources)
        flags = flags or 'is_%s' %res_type
        templates = self.db.table('adm.userobject').userObjectMenu(table=table,objtype='template',flags=flags)
        for t in templates:
            attr = t.attr
            result.setItem(attr['code'],None,resource='%s_template' %res_type,template_id=attr['pkey'],**attr)
        return result
        
    @struct_method
    def th_slotbar_templateManager(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        pane.paletteTemplateEditor(maintable=table,dockButton_iconClass='iconbox document')
        
    @struct_method
    def th_slotbar_resourceActions(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        th_root = inattr['th_root']
        pane.div(_class='iconbox gear').menu(modifiers='*',storepath='.resources.action.menu',action="""
                            var kw = objectExtract(this.getInheritedAttributes(),"batch_*",true);
                            kw.resource = $1.resource;
                            th_view_batch_caller(kw);
                            """,
                    batch_selectionName=th_root,batch_gridId='%s_grid' %th_root,batch_table=table,batch_res_type='action',
                    batch_sourcepage_id=self.page_id)
        pane.dataRemote('.resources.action.menu',self.table_script_resource_tree_data,res_type='action', table=table,cacheTime=5)
        
    @struct_method
    def th_gridPane(self, frame,table=None,th_pkey=None,
                        virtualStore=None,condition=None,unlinkdict=None):
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
        frame.dataFormula('.title','view_title || name_plural || name_long',name_plural='=.table?name_plural',name_long='=.table?name_long',view_title='=.title',_init=True)
        condPars = {}
        if isinstance(condition,dict):
            condPars = condition
            condition = condPars.pop('condition',None)
        elif condition:
            condPars = condition[1] or {}
            condition = condition[0]
        gridattr = frame.grid.attributes
        rowsPerPage = self._th_hook('rowsPerPage',dflt=25,mangler=frame)()
        gridattr.update(rowsPerPage=rowsPerPage,
                        dropTypes=None,dropTarget=True,
                        draggable=True, draggable_row=True,
                        hiddencolumns=self._th_hook('hiddencolumns',mangler=th_root)(),
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
        if virtualStore:
            chunkSize= rowsPerPage * 4
            selectionName = '*%s' %th_root
        else:
            chunkSize = None
            selectionName = None
        self.subscribeTable(table,True)
        frame.dataController("gridnode.setHiderLayer(hide,{message:''});",gridnode=frame.grid,hide='^.queryRunning',msg='!!Loading')
        store = frame.grid.selectionStore(table=table, #columns='=.grid.columns',
                               chunkSize=chunkSize,childname='store',
                               where='=.query.where', sortedBy='=.grid.sorted',
                               pkeys='=.query.pkeys', _fired='^.runQueryDo',
                               _onResult='SET .queryRunning=false;',
                               _onError='genro.publish("pbl_bottomMsg", {message:error,sound:"Basso",color:"red"});SET .queryRunning=false;return error;',
                               selectionName=selectionName, recordResolver=False, condition=condition,
                               sqlContextName='standard_list', totalRowCount='=.tableRecordCount',
                               row_start='0', externalChanges=True,
                               excludeLogicalDeleted='=.excludeLogicalDeleted',
                               excludeDraft='=.excludeDraft',
                               applymethod=self._th_hook('applymethod',dflt=None,mangler=frame),
                               timeout=180000, selectmethod='=.query.queryAttributes.selectmethod',
                               unlinkdict=unlinkdict,
                               _onCalling=""" 
                               %s
                              
                               if(kwargs['where'] && kwargs['where'] instanceof gnr.GnrBag){
                                    var newwhere = kwargs['where'].deepCopy();
                                    kwargs['where'].walk(function(n){
                                        if(n.label.indexOf('parameter_')==0){
                                            newwhere.popNode(n.label);
                                            kwargs[n.label.replace('parameter_','')]=n._value;
                                        }else{
                                            objectPop(newwhere.getNode(n.label).attr,'value_caption');
                                        }
                                    });
                                    kwargs['where'] = newwhere;
                               }
                               """
                               %self._th_hook('onQueryCalling',mangler=th_root,dflt='')(),
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
                               iconClass='iconbox run')
    
    @struct_method
    def th_slotbar_queryfb(self, pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table'] 
        th_root = inattr['th_root']
        pane.dataController(
               """var th = TH(th_root);
                  th.querymanager = new gnr.QueryManager(th,this,table);
               """ 
               , _init=True,table=table,th_root = th_root)

        pane.dataController("""var th=TH(th_root).querymanager.onQueryCalling(querybag,selectmethod);
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
                   var qm = TH(th_root).querymanager;
                   qm.createMenues();
                   dijit.byId(qm.relativeId('qb_fields_menu')).bindDomNode(genro.domById(qm.relativeId('fastQueryColumn')));
                   dijit.byId(qm.relativeId('qb_not_menu')).bindDomNode(genro.domById(qm.relativeId('fastQueryNot')));
                   qm.setFavoriteQuery();
        """,_onStart=True,th_root=th_root)        
        fb = pane.formbuilder(cols=3, datapath='.query.where', _class='query_form',width='600px',overflow='hidden',
                                  border_spacing='0', onEnter='genro.nodeById(this.getInheritedAttributes().target).publish("runbtn",{"modifiers":null});')
        fb.div('^.c_0?column_caption', min_width='12em', _class='fakeTextBox floatingPopup',
                 nodeId='%s_fastQueryColumn' %th_root,
                  dropTarget=True,row_hidden='^.#parent.queryAttributes.extended',
                 lbl='!!Search:',tdl_width='4em',
                 **{str('onDrop_gnrdbfld_%s' %table.replace('.','_')):"TH('%s').querymanager.onChangedQueryColumn(this,data);" %th_root})
        optd = fb.div(_class='fakeTextBox', lbl='!!Op.', lbl_width='4em')

        optd.div('^.c_0?not_caption', selected_caption='.c_0?not_caption', selected_fullpath='.c_0?not',
                display='inline-block', width='1.5em', _class='floatingPopup', nodeId='%s_fastQueryNot' %th_root,
                border_right='1px solid silver')
        optd.div('^.c_0?op_caption', min_width='7em', nodeId='%s_fastQueryOp' %th_root, 
                selected_fullpath='.c_0?op', selected_caption='.c_0?op_caption',
                connectedMenu='==TH("%s").querymanager.getOpMenuId(_dtype);' %th_root,
                _dtype='^.c_0?column_dtype',
                _class='floatingPopup', display='inline-block', padding_left='2px')
        value_textbox = fb.textbox(lbl='!!Value', value='^.c_0?value_caption', width='12em', lbl_width='5em',
                                       _autoselect=True,relpath='.c_0',
                                       row_class='^.c_0?css_class', position='relative',
                                       validate_onAccept='TH("%s").querymanager.checkQueryLineValue(this,value)' %th_root,
                                       disabled='==(_op in TH("%s").querymanager.helper_op_dict)'  %th_root, _op='^.c_0?op',
                                       connect_onclick="TH('%s').querymanager.getHelper(this);" %th_root,display='block',
                                       _class='st_conditionValue')
        value_textbox.div('^.c_0?value_caption', hidden='==!(_op in  TH("%s").querymanager.helper_op_dict)' %th_root,
                         _op='^.c_0?op', _class='helperField')
        fb.div('^.#parent.queryAttributes.caption',lbl='!!Search:',tdl_width='3em',colspan=3,
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
    js_requires='th/th_querytool,th/th_viewconfigurator'
        
    @public_method
    def th_menuSets(self,table=None,**kwargs):
        menu =self.db.table('adm.userobject').userObjectMenu(table=table,**kwargs)
        if len(menu)>0:
            menu.setItem('r_0',None,caption='-')
        menu.setItem('__newset__',None,caption='!!New Set')
        return menu

    @public_method
    def th_menuViews(self,table=None,th_root=None,pyviews=None,favoriteViewPath=None,**kwargs):
        result = Bag()
        gridId = '%s_grid' %th_root
        result.setItem('__baseview__', None,caption='Base View',gridId=gridId)
        if pyviews:
            for k,caption in pyviews:
                result.setItem(k.replace('_','.'),None,description=caption,caption=caption,viewkey=k,gridId=gridId)
        userobjects = self.db.table('adm.userobject').userObjectMenu(objtype='view',flags='%s_%s' % (self.pagename, gridId),table=table)
        if len(userobjects)>0:
            result.update(userobjects)
        result.walk(self._th_checkFavoriteLine,favPath=favoriteViewPath,gridId=gridId)
        return result
    
    def _th_checkFavoriteLine(self,node,favPath=None,gridId=None):
        if node.attr.get('code'):
            if gridId:
                node.attr['gridId'] = gridId
            if node.attr['code'] == favPath:
                node.attr['favorite'] = True
        else:
            node.attr['favorite'] = None
        
    
    @public_method
    def th_menuQueries(self,table=None,th_root=None,pyqueries=None,editor=True,favoriteQueryPath=None,**kwargs):
        querymenu = Bag()
        if editor:
            querymenu.setItem('__basequery__',None,caption='!!Plain Query',description='',
                                extended=False)
            querymenu.setItem('r_1',None,caption='-')
        savedquerymenu = self.db.table('adm.userobject').userObjectMenu(table,objtype='query') if 'adm' in self.db.packages else []
        if savedquerymenu:
            querymenu.update(savedquerymenu)
            querymenu.setItem('r_2',None,caption='-')
        if pyqueries:
            for n in pyqueries:
                querymenu.setItem(n.label,n.value,caption=n.attr.get('description'),_attributes=n.attr)
            querymenu.setItem('r_3',None,caption='-')
        
        if editor:
            querymenu.setItem('__queryeditor__',None,caption='!!Query editor',action="""
                                                                var currentQuery = GET .query.currentQuery;
                                                                SET .query.queryAttributes.extended=true; 
                                                                SET .query.queryEditor=true;""")
        else:
            querymenu.setItem('__newquery__',None,caption='!!New query',description='',
                                extended=True)
        querymenu.walk(self._th_checkFavoriteLine,favPath=favoriteQueryPath)
        return querymenu
            
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
