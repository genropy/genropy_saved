# -*- coding: UTF-8 -*-

# th_view.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs,metadata
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import slugify


class TableHandlerView(BaseComponent):
    py_requires = """th/th_lib:QueryHelper,
                     th/th_view:THViewUtils,
                     th/th_picker:THPicker,
                     gnrcomponents/framegrid:FrameGrid,
                     gnrcomponents/tpleditor:PaletteTemplateEditor,
                     gnrcomponents/batch_handler/batch_handler:TableScriptRunner,
                     js_plugins/chartjs/chartjs:ChartManager
                     """
                         
    @extract_kwargs(condition=True,store=True)
    @struct_method
    def th_tableViewer(self,pane,frameCode=None,table=None,th_pkey=None,viewResource=None,
                       virtualStore=None,condition=None,condition_kwargs=None,**kwargs):
        self._th_mixinResource(frameCode,table=table,resourceName=viewResource,defaultClass='View')
        options = self._th_hook('options',mangler=frameCode)() or dict()
        self._th_setDocumentation(table=table,resource = viewResource or 'View',doc=options.get('doc'),
                                    custdoc=options.get('custdoc'))
        kwargs.update(dictExtract(options,'grid_'),slice_prefix=False)
        if options.get('addrow') and options.get('addrow') is not True:
            kwargs['top_addrow_defaults'] = kwargs.get('top_addrow_defaults') or options['addrow']
        resourceConditionPars = self._th_hook('condition',mangler=frameCode,dflt=dict())()
        resourceCondition = resourceConditionPars.pop('condition',None)
        if resourceCondition:
            condition = condition='( %s ) AND ( %s ) ' %(condition,resourceCondition) if condition else resourceCondition
            condition_kwargs.update(dictExtract(resourceConditionPars,'condition_'))      

        view = pane.thFrameGrid(frameCode=frameCode,th_root=frameCode,th_pkey=th_pkey,table=table,
                                 virtualStore=virtualStore,
                                 condition=condition,condition_kwargs=condition_kwargs,
                                 **kwargs)
        
        for side in ('top','bottom','left','right'):
            hooks = self._th_hook(side,mangler=frameCode,asDict=True)
            for k in sorted(hooks.keys()):
                hooks[k](getattr(view,side))
        viewhook = self._th_hook('view',mangler=frameCode)
        if viewhook:
            viewhook(view)
        return view

    @extract_kwargs(top=True,preview=True)
    @struct_method
    def th_thFrameGrid(self,pane,frameCode=None,table=None,th_pkey=None,virtualStore=None,extendedQuery=None,
                       top_kwargs=None,condition=None,condition_kwargs=None,grid_kwargs=None,configurable=True,
                       unlinkdict=None,searchOn=True,count=None,title=None,root_tablehandler=None,structCb=None,preview_kwargs=None,loadingHider=True,
                       store_kwargs=None,parentForm=None,liveUpdate=None,**kwargs):
        extendedQuery = virtualStore and extendedQuery
        condition_kwargs = condition_kwargs
        if condition:
            condition_kwargs['condition'] = condition
        top_kwargs=top_kwargs or dict()
        if extendedQuery:
            virtualStore = True
            if 'adm' in self.db.packages and not self.isMobile:
                templateManager = 'templateManager'
            else:
                templateManager = False
            if extendedQuery == '*':
                base_slots = ['5','fastQueryBox','runbtn','queryMenu','viewsMenu','5','filterSelected,menuUserSets','15','export','importer','resourcePrints','resourceMails','resourceActions','5',templateManager,'chartjs','*']
                if self.isMobile:
                    base_slots = ['5','fastQueryBox','runbtn','queryMenu','viewsMenu','5','menuUserSets','*']

            elif extendedQuery is True:
                base_slots = ['5','fastQueryBox','runbtn','queryMenu','viewsMenu','5','chartjs','*','count','5']
            else:
                base_slots = extendedQuery.split(',')
        elif not virtualStore:
            if root_tablehandler:
                base_slots = ['5','searchOn','5','count','viewsMenu','*','export','5','chartjs','5','resourcePrints','resourceMails','resourceActions','10']
                if searchOn is False:
                    base_slots.remove('searchOn')
            else:
                base_slots = ['5','vtitle','count','*'] if count is not False else ['5','vtitle','*']
                if searchOn:
                    base_slots.append('searchOn')

        else:
            base_slots = ['5','vtitle','count','*']
        base_slots = ','.join([b for b in base_slots if b])
        if 'slots' in top_kwargs:
            top_kwargs['slots'] = top_kwargs['slots'].replace('#',base_slots)
        else:
            top_kwargs['slots']= base_slots
        #top_kwargs['height'] = top_kwargs.get('height','20px')
        top_kwargs['_class'] = 'th_view_toolbar'
        grid_kwargs['configurable'] = configurable
        grid_kwargs.setdefault('gridplugins', 'configurator,chartjs,stats' if virtualStore else 'configurator,chartjs')
        grid_kwargs['item_name_singular'] = self.db.table(table).name_long
        grid_kwargs['item_name_plural'] = self.db.table(table).name_plural or grid_kwargs['item_name']
        grid_kwargs.setdefault('loadingHider',loadingHider)
        grid_kwargs.setdefault('selfsubscribe_loadingData',"this.setRelativeData('.loadingData',$1.loading);if(this.attr.loadingHider!==false){this.setHiderLayer($1.loading,{message:''});}")
        frame = pane.frameGrid(frameCode=frameCode,childname='view',table=table,
                               struct = self._th_hook('struct',mangler=frameCode,defaultCb=structCb),
                               datapath = '.view',top_kwargs = top_kwargs,_class = 'frameGrid',
                               grid_kwargs = grid_kwargs,iconSize=16,_newGrid=True,**kwargs)  
        
        self._th_menu_sources(frame)
        if configurable:
            frame.right.viewConfigurator(table,frameCode,configurable=configurable)   
        self._th_viewController(frame,table=table,default_totalRowCount=extendedQuery == '*')
        store_kwargs = store_kwargs or dict()
        store_kwargs['parentForm'] = parentForm
        frame.gridPane(table=table,th_pkey=th_pkey,virtualStore=virtualStore,
                        condition=condition_kwargs,unlinkdict=unlinkdict,title=title,
                        liveUpdate=liveUpdate,store_kwargs=store_kwargs)
        self._th_view_contextMenu(frame.grid)
        if virtualStore:    
            self._extTableRecords(frame)
        frame.dataController("""if(!firedkw.res_type){return;}
                            var kw = {selectionName:batch_selectionName,gridId:batch_gridId,table:batch_table};
                            objectUpdate(kw,firedkw);
                            if(kw.template_id){
                                kw.extra_parameters = new gnr.GnrBag({template_id:objectPop(kw,'template_id'),table:kw.table});
                                kw.table = null;
                            }
                            th_view_batch_caller(kw);
                            """,batch_selectionName=frameCode,batch_gridId='%s_grid' %frameCode,batch_table=table,firedkw='^.th_batch_run',_if='firedkw')

        if preview_kwargs:
            frame.grid.attributes.update(preview_kwargs=preview_kwargs)
            frame.grid.tooltip(callback="""
                    var r = n;
                    while(!r || r.gridRowIndex==null){
                        r = r.parentElement;
                    }
                    var grid = dijit.getEnclosingWidget(n).grid;
                    var pkey = grid.rowIdByIndex(r.gridRowIndex);
                    var table = grid.sourceNode.attr.table;
                    var preview_kwargs = grid.sourceNode.attr.preview_kwargs;
                    var tpl = preview_kwargs.tpl;
                    tpl = tpl==true?'preview':preview_kwargs.tpl;
                    return genro.serverCall('renderTemplate',{record_id:pkey,table:table,tplname:tpl,missingMessage:'Preview not available'},null,null,'POST');
                """,modifiers='Ctrl',validclass='dojoxGrid-cell,cellContent')
        return frame

    def _th_view_contextMenu(self,grid):
        b = Bag()
        b.rowchild(label='!!Reload',action="$2.widget.reload();")
        b.rowchild(label='-')
        b.rowchild(label='!!Show Archived Records',checked='^.#parent.showLogicalDeleted',
                                action="""SET .#parent.showLogicalDeleted= !GET .#parent.showLogicalDeleted;
                                           $2.widget.reload();""")
        b.rowchild(label='!!Totals count',action='SET .#parent.tableRecordCount= !GET .#parent.tableRecordCount;',
                            checked='^.#parent.tableRecordCount')
        b.rowchild(label='-')
        b.rowchild(label='!!User Configuration',action='genro.dev.tableUserConfiguration($2.attr.table);')
        grid.data('.contextMenu',b)

    @struct_method
    def th_viewLeftDrawer(self,pane,table,th_root):
        bar = pane.slotBar('drawerStack',min_width='160px',closable='close',
                            splitter=True,border_right='1px solid silver')
        bar.drawerStack.attributes['height'] = '100%'
        sc = bar.drawerStack.stackContainer(height='100%')
        sc.contentPane(background='red')

    @struct_method
    def th_viewConfigurator(self,pane,table,th_root,configurable=None):
        bar = pane.slotBar('confBar,fieldsTree,*',width='160px',closable='close',
                            fieldsTree_table=table,
                            fieldsTree_checkPermissions=True,
                            fieldsTree_tree_searchCode='%s_fieldsTreeConfigurator' %th_root,
                            fieldsTree_height='100%',splitter=True,border_left='1px solid silver')
        confBar = bar.confBar.slotToolbar('viewsMenu,currviewCaption,*,defView,saveView,deleteView',background='whitesmoke')
        confBar.currviewCaption.div('^.grid.currViewAttrs.caption',font_size='.9em',color='#666',line_height='16px')

        gridId = '%s_grid' %th_root
        confBar.defView.slotButton('!!Favorite View',iconClass='th_favoriteIcon iconbox star',
                                        action='genro.grid_configurator.setCurrentAsDefault(gridId);',gridId=gridId)
        confBar.saveView.slotButton('!!Save View',iconClass='iconbox save',
                                        action='genro.grid_configurator.saveGridView(gridId);',gridId=gridId)
        confBar.deleteView.slotButton('!!Delete View',iconClass='iconbox trash',
                                    action='genro.grid_configurator.deleteGridView(gridId);',
                                    gridId=gridId,disabled='^.grid.currViewAttrs.pkey?=!#v')
        if table==getattr(self,'maintable',None) or configurable=='*':
            bar.replaceSlots('#','#,footerBar')
            footer = bar.footerBar.formbuilder(cols=1,border_spacing='3px 5px',font_size='.8em',fld_color='#555',fld_font_weight='bold')
            footer.numberSpinner(value='^.hardQueryLimit',lbl='!!Limit',width='6em',smallDelta=1000)
            

    @struct_method
    def th_slotbar_vtitle(self,pane,**kwargs):
        pane.div('^.title' ,_class='frameGridTitle')


    @struct_method
    def th_slotbar_importer(self,pane,**kwargs):
        options = self._th_hook('options',mangler=pane)() or dict()
        tags = options.get('uploadTags') or '_DEV_,superadmin'
        if not self.application.checkResourcePermission(tags, self.userTags):
            pane.div()
            return
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        pane.PaletteImporter(table=table,paletteCode='%(th_root)s_importer' %inattr,
                            match_values=','.join(self.db.table(table).model.columns.keys()),
                            dockButton_iconClass='iconbox inbox',title='!!Importer')


    @struct_method
    def th_slotbar_sum(self,pane,label=None,format=None,width=None,**kwargs):
        sum_column = kwargs['sum']
        table = pane.getInheritedAttributes()['table']
        sum_column_attr = self.db.table(table).column(sum_column).attributes
        format = format or sum_column_attr.get('format','###,###,###.00')
        pane.data('.sum_columns_source.%s' %sum_column,True)
        box = pane.div(hidden='==_sumvalue===false',_sumvalue='^.store?sum_%s' %sum_column)
        box.div(label or sum_column_attr.get('name_short') or sum_column_attr['name_long'],_class='gnrfieldlabel',font_size='.9em',
                    display='inline-block',padding_right='3px')
        box.div('==_sumvalue|| 0;',_sumvalue='^.store?sum_%s' %sum_column,format=format,width=width or '5em',_class='fakeTextBox',
                 font_size='.9em',text_align='right',padding_right='2px',display='inline-block')

    def _th_section_from_type(self,tblobj,sections,condition=None,condition_kwargs=None,
                            all_begin=None,all_end=None,codePkey=False,include_inherited=None):
        rt = tblobj.column(sections).relatedTable() 
        if rt:
            section_table = tblobj.column(sections).relatedTable().dbtable
            pkeyfield = section_table.pkey
            caption_field = section_table.attributes.get('caption_field')
            condition_kwargs = condition_kwargs or dict()
            default_order_by = section_table.attributes.get('order_by','$%s' %caption_field)
            f = section_table.query(columns='*,$%s' %caption_field,where=condition,order_by=default_order_by,**condition_kwargs).fetch()
        else:
            caption_field = 'description'
            pkeyfield = 'code'
            f = []
            for s in tblobj.column(sections).attributes['values'].split(','):
                s = s.split(':')
                f.append(dict(code=s[0],description=s[1] if len(s)==2 else s[0]))
        s = []
        sec_cond = '$%s=:s_id' %sections
        if include_inherited:
            sec_cond = '(($%s IS NULL) OR ($%s=:s_id))' %(sections,sections)
        if all_begin is None and all_end is None:
            all_begin = True
        if all_begin:
            s.append(dict(code='c_all_begin',caption='!!All' if all_begin is True else all_begin))
        for i,r in enumerate(f):
            s.append(dict(code=slugify(r[pkeyfield],'_'),caption=r[caption_field],condition=sec_cond,condition_s_id=r[pkeyfield]))
        if all_end:
            s.append(dict(code='c_all_end',caption='!!All' if all_end is True else all_end))
        return s

    @extract_kwargs(condition=True,lbl=dict(slice_prefix=False))
    @struct_method
    def th_slotbar_sections(self,parent,sections=None,condition=None,condition_kwargs=None,
                            all_begin=None,all_end=None,include_inherited=False,multiButton=None,lbl=None,lbl_kwargs=None,**kwargs):
        inattr = parent.getInheritedAttributes()    
        th_root = inattr['th_root']
        pane = parent.div(datapath='.sections.%s' %sections)
        tblobj = self.db.table(inattr['table'])
        m = self._th_hook('sections_%s' %sections,mangler=th_root,defaultCb=False)
        sectionslist = None
        if m:
            sectionslist = m()
            dflt = getattr(m,'default',None)
            multivalue=getattr(m,'multivalue',False)
            isMain = getattr(m,'isMain',False)
            variable_struct = getattr(m,'variable_struct',False)
            mandatory=getattr(m,'mandatory',True)
            multiButton = getattr(m,'multiButton',multiButton)
            lbl = lbl or getattr(m,'lbl',None)
            lbl_kwargs = lbl_kwargs or dictExtract(dict(m.__dict__),'lbl_',slice_prefix=False)
            depending_condition = getattr(m,'_if',False)
            depending_condition_kwargs = dictExtract(dict(m.__dict__),'_if_')
        elif sections in  tblobj.model.columns and (tblobj.column(sections).relatedTable() is not None or 
                                                tblobj.column(sections).attributes.get('values')):
            sectionslist = self._th_section_from_type(tblobj,sections,condition=condition,condition_kwargs=condition_kwargs,
                                                    all_begin=all_begin,all_end=all_end,include_inherited=include_inherited)
            dflt = None
            multivalue = True
            variable_struct = False
            isMain = False
            mandatory = None
            depending_condition = False
            depending_condition_kwargs = dict()
        if not sectionslist:
            return
        sectionsBag = Bag()
        for i,kw in enumerate(sectionslist):
            code = kw.get('code') or 'r_%i' %i
            if kw.get('isDefault'):
                dflt = dflt or code
            sectionsBag.setItem(code,None,**kw)
        pane.data('.data',sectionsBag)
        if not dflt:

            dflt = sectionsBag.getNode('#0').label
        pane.data('.current',dflt)
        pane.data('.variable_struct',variable_struct)
        if multivalue and variable_struct:
            raise Exception('multivalue cannot be set with variable_struct')
        multiButton = multiButton is True or multiButton is None or multiButton and len(sectionsBag)<=multiButton
        if multiButton:
            mb = pane.multiButton(items='^.data',value='^.current',multivalue=multivalue,mandatory=mandatory,
                                disabled='^.#parent.#parent.grid.loadingData',**kwargs)
    
        else:
            mb = pane.formbuilder(cols=1,border_spacing='3px',**lbl_kwargs)
            lbl = lbl or sections.capitalize()
            if multivalue:
                mb.checkBoxText(values='^.data',value='^.current',lbl=lbl,
                                labelAttribute='caption',parentForm=False,
                                disabled='^.#parent.#parent.grid.loadingData',
                                        popup=True,cols=1)
            else:
                mb.filteringSelect(storepath='.data',value='^.current',lbl=lbl,
                                disabled='^.#parent.#parent.grid.loadingData',
                                storeid='#k',parentForm=False,
                                validate_notnull=mandatory,
                                popup=True,cols=1)
        parent.dataController("""var enabled = depending_condition?funcApply('return '+depending_condition,_kwargs):true;
                                genro.dom.toggleVisible(__mb,enabled)
                                SET .%s.enabled = enabled;
                                FIRE .#parent.sections_changed;
                                """ %sections,
                                __mb=mb,ss=sections,datapath='.sections',
                                depending_condition=depending_condition,_onBuilt=True,
                                        **depending_condition_kwargs)
        pane.dataController("""
            genro.assert(currentSection,'missing current section for sections %s')
            var sectionNode = sectionbag.getNode(currentSection);
            if(isMain){
                FIRE .#parent.#parent.clearStore;
                SET .#parent.#parent.excludeDraft = !sectionNode.attr.includeDraft;
            } 
            FIRE .#parent.#parent.sections_changed;
            """ %sections
            ,isMain=isMain,_onBuilt=True,
            currentSection='^.current',sectionbag='=.data',
            _delay=1,
            th_root=th_root)
 

    @struct_method
    def th_slotbar_queryMenu(self,pane,**kwargs):
        pane.div(_class='iconbox menubox magnifier').menu(storepath='.query.menu',_class='smallmenu',modifiers='*',
                    action="""
                                SET .query.currentQuery = $1.fullpath;
                                if(!$1.pkey){
                                    SET .query.queryEditor = false;
                                }
                                SET .query.menu.__queryeditor__?disabled=$1.selectmethod!=null;
                            """)

    @public_method
    @metadata(prefix='query',code='default_duplicate_finder',description='!!Find all duplicates')
    def th_default_find_duplicates(self, tblobj=None,sortedBy=None,date=None, where=None,**kwargs):
        pkeys = tblobj.findDuplicates()
        query = tblobj.query(where='$%s IN :pkd' %tblobj.pkey,pkd=pkeys,**kwargs)
        return query.selection(sortedBy=sortedBy, _aggregateRows=True) 
    @public_method
    @metadata(prefix='query',code='default_duplicate_finder_to_del',description='!!Find duplicates to delete')
    def th_default_find_duplicates_to_del(self, tblobj=None,sortedBy=None,date=None, where=None,**kwargs):
        pkeys = tblobj.findDuplicates(allrecords=False)
        query = tblobj.query(where='$%s IN :pkd' %tblobj.pkey,pkd=pkeys,**kwargs)
        return query.selection(sortedBy=sortedBy, _aggregateRows=True) 

    def _th_menu_sources(self,pane):
        inattr = pane.getInheritedAttributes()
        th_root = inattr['th_root']
        table = inattr['table']
        gridId = '%s_grid' %th_root

        #SOURCE MENUQUERIES
        pane.dataController("""TH(th_root).querymanager.onChangedQuery(currentQuery);
                          """,currentQuery='^.query.currentQuery',th_root=th_root)
        pane.dataController("""
            genro.dlg.thIframePalette({table:'adm.userobject',palette_top:'100px',palette_right:'600px',current_tbl:tbl,current_pkg:pkg,title:title,viewResource:'ViewCustomColumn',formResource:'FormCustomColumn'})
            """,tbl=table,_fired='^.handle_custom_column',pkg=table.split('.')[0],title='!!Custom columns')
        q = Bag()
        pyqueries = self._th_hook('query',mangler=th_root,asDict=True)
        if self.db.table(table).column('_duplicate_finder') is not None and self.application.checkResourcePermission('_DEV_,superadmin', self.userTags):
            pyqueries['default_duplicate_finder'] = self.th_default_find_duplicates
            pyqueries['default_duplicate_finder_to_del'] = self.th_default_find_duplicates_to_del
        for k,v in pyqueries.items():
            pars = dictExtract(dict(v.__dict__),'query_')
            code = pars.get('code')
            q.setItem(code,None,tip=pars.get('description'),selectmethod=v,**pars)
        pane.data('.query.pyqueries',q)
        pane.dataRemote('.query.menu',self.th_menuQueries,pyqueries='=.query.pyqueries',
                        _resolved_pyqueries=q,
                       # favoriteQueryPath='=.query.favoriteQueryPath',
                        table=table,th_root=th_root,caption='Queries',cacheTime=15,
                        _resolved=True)
        pane.dataController("TH(th_root).querymanager.queryEditor(open);",
                        th_root=th_root,open="^.query.queryEditor")
        if 'adm' not in self.db.packages:
            return
        pane.dataRemote('.query.savedqueries',self.th_menuQueries,
                        #favoriteQueryPath='=.query.favoriteQueryPath',
                        table=table,th_root=th_root,cacheTime=5,editor=False,
                        _resolved=True)
        
        pane.dataRemote('.query.helper.in.savedsets',self.th_menuSets,
                        objtype='list_in',table=table,cacheTime=5)
                        
        pane.dataRpc('dummy',self.db.table('adm.userobject').deleteUserObject,pkey='=.query.queryAttributes.pkey',_fired='^.query.delete',
                   _onResult='FIRE .query.currentQuery="__newquery__";FIRE .query.refreshMenues;')

        #SOURCE MENUVIEWS
        pane.dataController("""genro.grid_configurator.loadView(gridId, (currentView || favoriteView),th_root);
                                """,
                            currentView="^.grid.currViewPath",
                            favoriteView='^.grid.favoriteViewPath',
                            gridId=gridId,th_root=th_root)
        q = Bag()
        pyviews = self._th_hook('struct',mangler=th_root,asDict=True)
        for k,v in pyviews.items():
            prefix,name=k.split('_struct_')
            q.setItem(name,self._prepareGridStruct(v,table=table),caption=v.__doc__)
        pane.data('.grid.resource_structs',q)
        pane.dataRemote('.grid.structMenuBag',self.th_menuViews,pyviews=q.digest('#k,#a.caption'),currentView="=.grid.currViewPath",
                        table=table,th_root=th_root,favoriteViewPath='=.grid.favoriteViewPath',cacheTime=30)

        options = self._th_hook('options',mangler=pane)() or dict()
        #SOURCE MENUPRINT
        pane.dataRemote('.resources.print.menu',self.th_printMenu,table=table,flags=options.get('print_flags'),
                        from_resource=options.get('print_from_resource',True),cacheTime=5)

        #SOURCE MENUMAIL
        pane.dataRemote('.resources.mail.menu',self.th_mailMenu,table=table,flags=options.get('mail_flags'),
                        from_resource=options.get('mail_from_resource',True),cacheTime=5)

        #SOURCE MENUACTIONS
        pane.dataRemote('.resources.action.menu',self.table_script_resource_tree_data,
                        res_type='action', table=table,cacheTime=5)

    @struct_method
    def th_slotbar_viewsMenu(self,pane,**kwargs):
        b = pane.div(_class='iconbox list',datapath='.grid')
        b.menu(storepath='.structMenuBag',_class='smallmenu',modifiers='*',selected_fullpath='.currViewPath')

    @struct_method
    def th_slotbar_resourcePrints(self,pane,flags=None,from_resource=None,**kwargs):
        pane.div(_class='iconbox menubox print').menu(modifiers='*',storepath='.resources.print.menu',_class='smallmenu',
                    action="""FIRE .th_batch_run = {resource:$1.resource,template_id:$1.template_id,res_type:'print'};""")

    @public_method
    def th_printMenu(self,table=None,flags=None,from_resource=True,**kwargs):
        return self._printAndMailMenu(table=table,flags=flags,from_resource=from_resource,res_type='print')
        
    @struct_method
    def th_slotbar_resourceActions(self,pane,**kwargs):
        pane.div(_class='iconbox gear').menu(modifiers='*',storepath='.resources.action.menu',action="""
                            FIRE .th_batch_run = {resource:$1.resource,res_type:"action"};
                            """,_class='smallmenu')
    @struct_method
    def th_slotbar_resourceMails(self,pane,from_resource=None,flags=None,**kwargs):
        pane.div(_class='iconbox mail').menu(modifiers='*',storepath='.resources.mail.menu',
                        action="""FIRE .th_batch_run = {resource:$1.resource,template_id:$1.template_id,res_type:'mail'};""")

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
        if templates and len(templates)>0:
            result.update(templates)
        result.walk(self._th_addTpl,res_type=res_type)
        return result
    
    def _th_addTpl(self,node,res_type=None):
        if node.attr.get('code'):
            node.attr['resource'] ='%s_template' %res_type
            node.attr['template_id'] = node.attr['pkey']
        
    @struct_method
    def th_slotbar_templateManager(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        paletteCode = '%(thlist_root)s_template_manager' %inattr
        pane.paletteTemplateEditor(maintable=table,paletteCode=paletteCode,dockButton_iconClass='iconbox document')

      
    @struct_method
    def th_gridPane(self, frame,table=None,th_pkey=None,
                        virtualStore=None,condition=None,unlinkdict=None,
                        title=None,liveUpdate=None,store_kwargs=None):
        table = table or self.maintable
        th_root = frame.getInheritedAttributes()['th_root']
        sortedBy=self._th_hook('order',mangler=th_root)()
        tblobj = self.db.table(table)
        default_sort_col = 'pkey'
        if tblobj.model.column('__ins_ts') is not None:
            default_sort_col = '__ins_ts'
        if sortedBy :
            sortedBy = sortedBy.strip().replace('$','').replace('@','_').replace('.','_')
            #if not filter(lambda e: e.startswith('pkey'),sortedBy.split(',')):
            #    sortedBy = sortedBy +',%s' %default_sort_col 
        elif tblobj.column('_row_count') is not None:
            sortedBy = '_row_count' or default_sort_col
        frame.data('.grid.sorted',sortedBy)
        if th_pkey:
            querybase = dict(column=self.db.table(table).pkey,op='equal',val=th_pkey,runOnStart=True)
        else:
            querybase = self._th_hook('query',mangler=th_root)() or dict()
        queryBag = self._prepareQueryBag(querybase,table=table)
        frame.data('.baseQuery', queryBag)
        options = self._th_hook('options',mangler=th_root)() or dict()
        pageOptions = self.pageOptions or dict()
        #liveUpdate: 'NO','LOCAL','PAGE'
        liveUpdate = liveUpdate or options.get('liveUpdate') or pageOptions.get('liveUpdate') or self.site.config['options?liveUpdate'] or 'LOCAL'
        if liveUpdate == '*':
            liveUpdate = True
        store_kwargs.setdefault('liveUpdate',liveUpdate)
        hardQueryLimit = options.get('hardQueryLimit') or self.application.config['db?hardQueryLimit']
        allowLogicalDelete = store_kwargs.pop('allowLogicalDelete',None) or options.get('allowLogicalDelete')
        frame.data('.hardQueryLimit',int(hardQueryLimit) if hardQueryLimit else None)
        frame.dataFormula('.title','(custom_title || name_plural || name_long)+sub_title',
                        custom_title=title or options.get('title') or False,
                        name_plural='=.table?name_plural',
                        name_long='=.table?name_long',
                        #view_title='=.title',
                        _sections='^.sections',
                        sub_title='==_sections?th_sections_manager.getSectionTitle(_sections):"";',
                        _onBuilt=True,_init=True)
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
                        draggable_row=True,
                        hiddencolumns=self._th_hook('hiddencolumns',mangler=th_root)(),
                        dragClass='draggedItem',
                        selfsubscribe_runbtn="""
                            var currLinkedSelection = GET .#parent.linkedSelectionPars;
                            if(currLinkedSelection && currLinkedSelection.getItem('masterTable')){
                                SET .#parent.linkedSelectionPars.command = 'unsubscribe';
                            }
                            if($1.modifiers=='Shift'){
                                FIRE .#parent.showQueryCountDlg;
                            }else{
                            FIRE .#parent.runQuery;
                        }""")
        gridattr.setdefault('userSets','.sets')

        if virtualStore:
            chunkSize= rowsPerPage * 4
            selectionName = '*%s' %th_root
        else:
            chunkSize = None
            selectionName = None
        if liveUpdate!='NO':
            self.subscribeTable(table,True,subscribeMode=liveUpdate)
        selectmethod = self._th_hook('selectmethod',mangler=frame,defaultCb=False)
        
        store_kwargs.update(condPars)
        _if = store_kwargs.pop('_if',None) or store_kwargs.pop('if',None)
        _onStart = store_kwargs.pop('_onStart',None) or store_kwargs.pop('onStart',None)
        _else = None
        if _if:
            _else = "this.store.clear();"
        frame.dataFormula('.sum_columns',"sum_columns_source && sum_columns_source.len()?sum_columns_source.keys().join(','):null",
                                        sum_columns_source='=.sum_columns_source',_onBuilt=True)
        frame.dataController("""
            th_sections_manager.updateSectionsStatus(sectionbag,genro.getFrameNode(th_root));
            var loadingData = GET .grid.loadingData;
            if(lastQueryTime!==null && !loadingData){
                FIRE .runQueryDo;
            }
            """,
            th_root=th_root,
            lastQueryTime = '=.store?servertime',
            sectionbag = '=.sections',
            _fired = '^.sections_changed',
            _if = 'sectionbag.len()',
            _delay = 100)

        store = frame.grid.selectionStore(table=table,
                               chunkSize=chunkSize,childname='store',
                               where='=.query.where',
                               queryMode='=.query.queryMode', 
                               sortedBy='=.grid.sorted',
                               pkeys='=.query.pkeys', _runQueryDo='^.runQueryDo',
                               _cleared='^.clearStore',
                               _onError="""return error;""", 
                               selectionName=selectionName, recordResolver=False, condition=condition,
                               sqlContextName='standard_list', totalRowCount='=.tableRecordCount',
                               row_start='0',
                               allowLogicalDelete=allowLogicalDelete,
                               excludeLogicalDeleted='=.excludeLogicalDeleted',
                               excludeDraft='=.excludeDraft',
                               applymethod=store_kwargs.pop('applymethod',None) or self._th_hook('applymethod',dflt=None,mangler=frame),
                               timeout=180000, selectmethod= selectmethod or '=.query.queryAttributes.selectmethod',
                               currentFilter = '=.query.currentFilter',
                               prevSelectedDict = '=.query.prevSelectedDict',
                               unlinkdict=unlinkdict,
                               userSets='.sets',_if=_if,_else=_else,
                               _sections='=.sections',
                               hardQueryLimit='=.hardQueryLimit',
                              # sum_columns='=.sum_columns',
                               _onStart=_onStart,
                               _th_root =th_root,
                               _POST =True,
                               httpMethod='WSK' if self.extraFeatures['wsk_grid'] else None,
                               _onCalling="""
                               %s
                               if(_sections){
                                    th_sections_manager.onCalling(_sections,kwargs);
                               }
                               if(kwargs['where'] && kwargs['where'] instanceof gnr.GnrBag){
                                    var newwhere = kwargs['where'].deepCopy();
                                    var where = kwargs['where'];
                                    where.walk(function(n){
                                        var p = n.getFullpath(null,where);
                                        if(p.indexOf('parameter_')==0){
                                            newwhere.popNode(p);
                                            kwargs[n.label.replace('parameter_','')] = n._value;
                                        }else{
                                            objectPop(newwhere.getNode(p).attr,'value_caption');
                                        }
                                    });
                                    kwargs['where'] = newwhere;
                               }
                               """
                               %self._th_hook('onQueryCalling',mangler=th_root,dflt='')(),
                               **store_kwargs)
        store.addCallback("""FIRE .queryEnd=true; 
                            return result;
                            """) 
        frame.dataController("""
            var reason,caption,tooltip;
            if(pkeys){
                reason = 'selectedOnly';
                caption = selectedOnlyCaption;
            } else if(linkedSelectionPars && linkedSelectionPars.getItem('masterTable')){
                var masterTableCaption = linkedSelectionPars.getItem('masterTableCaption');
                tooltip = linkedSelectionPars.getItem('pathDescription');
                if(!linkedSelectionPars.getItem('linkedSelectionName')){
                    reason = 'linkedSelectionPkeys';
                    caption = linkedSelectionCaption+masterTableCaption;
                }else{
                    reason = 'syncSelection';
                    caption = syncSelectionCaption+masterTableCaption;
                }
            }
            SET .query.pkeys = null;
            SET .internalQuery.tooltip = tooltip;
            SET .internalQuery.caption = caption || '';
            SET .internalQuery.reason = reason;
            """,pkeys='=.query.pkeys',
                selectedOnlyCaption='!!Selected only',linkedSelectionCaption='!!Depending from ',
                syncSelectionCaption='!!In sync with ',
                linkedSelectionPars='=.linkedSelectionPars',_fired='^.queryEnd',_delay=1,
                currentReason='=.internalQuery.reason') 
        frame.data('.internalQuery.reason',None)      
        frame.dataController("""
            genro.dom.setClass(fn,'filteredGrid',internalQueryReason);
            SET .query.queryAttributes.extended = internalQueryReason!=null;
            """,fn=frame,internalQueryReason='^.internalQuery.reason')
        if virtualStore:
            frame.dataRpc('.currentQueryCount', 'app.getRecordCount', condition=condition,
                         _updateCount='^.updateCurrentQueryCount',
                         table=table, where='=.query.where',_showCount='=.tableRecordCount',
                         excludeLogicalDeleted='=.excludeLogicalDeleted',
                         excludeDraft='=.excludeDraft',_if='%s && (_updateCount || _showCount) ' %(_if or 'true'),
                         _else='return 0;',
                         **store_kwargs)
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
    def th_slotbar_filterSelected(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        btn = pane.slotButton('!!Only highlighted',action="""
            var highlighted = genro.wdgById(th_root_code+'_grid').getSelectedPkeys();
            if(highlighted){
                this.setRelativeData('.query.pkeys',highlighted.join(','));
                this.fireEvent('.runQuery');
            }
            """,th_root_code=inattr['th_root'],iconClass='iconbox bulb_off')
        
        pane.dataController("""
            var highlighted = genro.wdgById(th_root_code+'_grid').getSelectedPkeys();
            if(highlighted.length>0){
                btn.widget.setIconClass('iconbox bulb_on');
                btn.widget.setAttribute('disabled',false);
            }else{
                btn.widget.setIconClass('iconbox bulb_off');
                btn.widget.setAttribute('disabled',true);
            }
        """,btn=btn,selected='^.grid.selectedId',th_root_code=inattr['th_root'],_fired='^.queryEnd')

    @struct_method
    def th_slotbar_menuUserSets(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        pane.dataController("""
                                var th = TH(th_root);
                                th.datasetmanager = new gnr.THDatasetManager(th,this,table);
                                var cb = function(){
                                    return th.datasetmanager.datasetsMenu();
                                }

                                SET .usersets.menu = new gnr.GnrBagCbResolver({method:cb});

                                """,
                        _onStart=True,th_root = inattr['th_root'],table = inattr['table'])

        pane.div(_class='iconbox heart',tip='!!User sets').menu(storepath='.usersets.menu',
                                                                _class='smallmenu',modifiers='*')
       
    @struct_method
    def th_slotbar_fastQueryBox(self, pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table'] 
        th_root = inattr['th_root']
        tablecode = table.replace('.','_')
        pane.dataController(
               """var th = TH(th_root);
                  
                  th.querymanager = th.querymanager || new gnr.QueryManager(th,this,table);
               """ 
               , _init=True, _onBuilt=True, table=table,th_root = th_root)
    
        pane.dataController("""
                   var qm = TH(th_root).querymanager;
                   qm.createMenuesQueryEditor();
                   dijit.byId(qm.relativeId('qb_fields_menu')).bindDomNode(genro.domById(qm.relativeId('fastQueryColumn')));
                   dijit.byId(qm.relativeId('qb_not_menu')).bindDomNode(genro.domById(qm.relativeId('fastQueryNot')));
                   dijit.byId(qm.relativeId('qb_queryModes_menu')).bindDomNode(genro.domById(qm.relativeId('searchMenu_a')));
                   qm.setFavoriteQuery();
        """,_onStart=True,th_root=th_root)   
        fmenupath = 'gnr.qb.%s.fieldsmenu' %tablecode
        options = self._th_hook('options',mangler=pane)() or dict()
        pane.dataRemote(fmenupath,self.relationExplorer,item_type='QTREE',
                        branch=options.get('branch'),
                        table=table,omit='_*')
        pane.data('gnr.qb.sqlop',self.getSqlOperators())   
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
        box = pane.div(datapath='.query.where',onEnter='genro.nodeById(this.getInheritedAttributes().target).publish("runbtn",{"modifiers":null});')
        box.data('.#parent.queryMode','S',caption='!!Search')
        box.div('^.#parent.queryMode?caption',_class='gnrfieldlabel th_searchlabel',
                nodeId='%s_searchMenu_a' %th_root)
        querybox_stack = box.div(style='display:inline-block')
        querybox = box.div(_class='th_querybox',hidden='^.#parent.queryAttributes.extended')
        querybox.div('^.c_0?column_caption', _class='th_querybox_item',
                 nodeId='%s_fastQueryColumn' %th_root,
                  dropTarget=True,
                 **{str('onDrop_gnrdbfld_%s' %tablecode):"TH('%s').querymanager.onChangedQueryColumn(this,data);" %th_root})
        #tbox.tree(storepath=fmenupath,popup=True,
        #        connect_onClick="""function(bagNode,treeNode){
        #                            var qm = TH('%s').querymanager;
        #                            qm.onChangedQueryColumnDo(this,this.absDatapath('.c_0'),bagNode.attr)
        #                        }""" %th_root)
        querybox.div('^.c_0?not_caption', selected_caption='.c_0?not_caption', selected_fullpath='.c_0?not',
                width='1.5em', _class='th_querybox_item', nodeId='%s_fastQueryNot' %th_root)
        querybox.div('^.c_0?op_caption', nodeId='%s_fastQueryOp' %th_root, 
                selected_fullpath='.c_0?op', selected_caption='.c_0?op_caption',
                connectedMenu='==TH("%s").querymanager.getOpMenuId(_dtype);' %th_root,
                _dtype='^.c_0?column_dtype',
                _class='th_querybox_item')
        value_textbox = querybox.div(_class='th_querybox_item th_queryboxfield',
                                    connect_onclick="""if($1.target===this.domNode){
                                        this.getChild('searchboxTextbox').widget.focus();
                                    }
                                    """).textbox(value='^.c_0?value_caption',
            _autoselect=True,relpath='.c_0',childname='searchboxTextbox',
            validate_onAccept='TH("%s").querymanager.checkQueryLineValue(this,value)' %th_root,
            disabled='==(_op in TH("%s").querymanager.helper_op_dict)'  %th_root, _op='^.c_0?op',
            connect_onclick="TH('%s').querymanager.getHelper(this);" %th_root,width='8em' if self.isMobile else '12em')

        value_textbox.div('^.c_0?value_caption', hidden='==!(_op in  TH("%s").querymanager.helper_op_dict)' %th_root,
                         _op='^.c_0?op', _class='helperField')


        querybox_stack.div("==_internalQueryCaption || _caption",_caption='^.#parent.queryAttributes.caption',
                        _internalQueryCaption='^.#parent.#parent.internalQuery.caption', 
                        _class='th_querybox_extended',
                        tooltip='==_internalQueryTooltip || _internalQueryCaption || _caption',
                                    _internalQueryTooltip='^.#parent.#parent.internalQuery.tooltip',
                                    hidden='^.#parent.queryAttributes.extended?=!#v',min_width='20em')

        
    def _th_viewController(self,pane,table=None,th_root=None,default_totalRowCount=None):
        table = table or self.maintable
        tblattr = dict(self.db.table(table).attributes)
        tblattr.pop('tag',None)
        pane.data('.table',table,**tblattr)
        options = self._th_hook('options',mangler=pane)() or dict()
        excludeLogicalDeleted = options.get('excludeLogicalDeleted',True)
        showLogicalDeleted = not excludeLogicalDeleted
        pane.data('.excludeLogicalDeleted', 'mark' if showLogicalDeleted else True)
        pane.dataController("""SET .excludeLogicalDeleted = show?'mark':true;
                               genro.dom.setClass(dojo.body(),'th_showLogicalDeleted',show);
                            """,show="^.showLogicalDeleted")
        pane.data('.showLogicalDeleted',showLogicalDeleted)
        pane.data('.excludeDraft', options.get('excludeDraft',True))
        pane.data('.tableRecordCount',options.get('tableRecordCount',default_totalRowCount))

    def _prepareQueryBag(self,querybase,table=None):
        result = Bag()
        if not querybase:
            return result
        table = table or self.maintable
        tblobj = self.db.table(table)
        op_not = querybase.get('op_not', 'yes')
        column = querybase.get('column')
        column_dtype = None
        val = querybase.get('val')
        if column:
            column_dtype = tblobj.column(column).getAttr('query_dtype') or tblobj.column(column).getAttr('dtype')
        not_caption = '&nbsp;' if op_not == 'yes' else '!!not'
        result.setItem('c_0', val,
                       {'op': querybase.get('op'), 'column': column,
                        'op_caption': self.db.whereTranslator.opCaption(querybase.get('op')),
                        'not': op_not, 'not_caption': not_caption,
                        'column_dtype': column_dtype,
                        'column_caption': self.app._relPathToCaption(table, column),
                        'value_caption':val})
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
    def th_menuViews(self,table=None,th_root=None,pyviews=None,favoriteViewPath=None,currentView=None,**kwargs):
        result = Bag()
        currentView = currentView or favoriteViewPath or '__baseview__'
        gridId = '%s_grid' %th_root
        result.setItem('__baseview__', None,caption='Base View',gridId=gridId,checked = currentView=='__baseview__')
        if pyviews:
            for k,caption in pyviews:
                result.setItem(k.replace('_','.'),None,description=caption,caption=caption,viewkey=k,gridId=gridId)
        userobjects = self.db.table('adm.userobject').userObjectMenu(objtype='view',flags='%s_%s' % (self.pagename, gridId),table=table)
        if self.pagename.startswith('thpage'):
            #compatibility old saved views
            userobjects.update(self.db.table('adm.userobject').userObjectMenu(objtype='view',flags='thpage_%s' % gridId,table=table))
        if len(userobjects)>0:
            result.update(userobjects)
        result.walk(self._th_checkFavoriteLine,favPath=favoriteViewPath,currentView=currentView,gridId=gridId)
        return result
    
    def _th_checkFavoriteLine(self,node,favPath=None,currentView=None,gridId=None):
        if node.attr.get('code'):
            if gridId:
                node.attr['gridId'] = gridId
            if node.attr['code'] == currentView:
                print 'curr',node.attr['code']
                node.attr['checked'] = True
            elif node.attr['code'] == favPath:
                node.attr['favorite'] = True
            
        else:
            node.attr['favorite'] = None
        
    
    @public_method
    def th_menuQueries(self,table=None,th_root=None,pyqueries=None,editor=True,**kwargs):
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
        #if self.application.checkResourcePermission('_DEV_,dbadmin', self.userTags):
        #    querymenu.setItem('__custom_columns__',None,caption='!!Custom columns',action="""FIRE .handle_custom_column;""")
        #querymenu.walk(self._th_checkFavoriteLine,favPath=favoriteQueryPath)
        return querymenu
            
    @public_method
    def getSqlOperators(self):
        result = Bag()
        listop = ('equal', 'startswith', 'wordstart', 'contains','similar', 'startswithchars', 'greater', 'greatereq',
                  'less', 'lesseq', 'between', 'isnull', 'istrue', 'isfalse', 'nullorempty', 'in', 'regex')
        optype_dict = dict(alpha=['contains', 'startswith', 'equal', 'wordstart',
                                  'startswithchars', 'isnull', 'nullorempty', 'in', 'regex',
                                  'greater', 'greatereq', 'less', 'lesseq', 'between'],
                           alpha_phonetic = ['contains','similar', 'startswith', 'equal', 'wordstart',
                                  'startswithchars', 'isnull', 'nullorempty', 'in', 'regex',
                                  'greater', 'greatereq', 'less', 'lesseq', 'between'],
                           date=['equal', 'in', 'isnull', 'greater', 'greatereq', 'less', 'lesseq', 'between'],
                           number=['equal', 'greater', 'greatereq', 'less', 'lesseq', 'isnull', 'in'],
                           boolean=['istrue', 'isfalse', 'isnull'],
                           others=['equal', 'greater', 'greatereq', 'less', 'lesseq', 'in'])
        queryModes = (('S','!!Search'),('U','!!Union'),('I','!!Intersect'),('D','!!Difference'))
        wt = self.db.whereTranslator
        for op,caption in queryModes:
            result.setItem('queryModes.%s' % op, None, caption=caption)
        for op in listop:
            result.setItem('op.%s' % op, None, caption=wt.opCaption(op))
        for optype, values in optype_dict.items():
            for operation in values:
                result.setItem('op_spec.%s.%s' % (optype, operation), operation,
                               caption=wt.opCaption(operation))
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


    def _extTableRecords(self,frame):
        gridattr = frame.grid.attributes
        gridattr['onDrag_ext_table_records'] = """if(!('dbrecords' in dragValues)){return;}
                                                var kw = objectUpdate({}, dragValues['dbrecords']);
                                                kw.selectionName = dragInfo.widget.collectionStore().selectionName;
                                                dragValues['ext_table_records'] = kw;
                                                """
        gridattr['dropTarget_grid'] = 'ext_table_records' if not gridattr.get('dropTarget_grid') else 'ext_table_records,%(dropTarget_grid)s' %gridattr
        gridattr['onDrop_ext_table_records'] = """if(dropInfo.selfdrop){
            return;
        }
        this.publish('queryFromLinkedGrid',{data:data,modifiers:dropInfo.modifiers,
                                                                dragSourceInfo:dropInfo.dragSourceInfo});
                                                """

        gridattr['selfsubscribe_queryFromLinkedGrid'] = """
            genro.lockScreen(true,'searchingRelation');
            var pkeys = $1.data.pkeys.join(',');
            var that = this;
            var persistent = $1.modifiers == 'Shift';
            var linkedSelectionName = $1.data.selectionName;
            var linkedPageId = $1.dragSourceInfo.page_id;
            var gridNodeId = this.attr.nodeId;
            var masterTable = $1.data.table;
            var slaveTable = this.attr.table;
            var cb = function(selectedPath,masterTableCaption,pathDescription){
                var kw = {pkeys:pkeys,relationpath:selectedPath,slaveTable:slaveTable,
                            masterTable:masterTable,masterTableCaption:masterTableCaption,
                            command:'subscribe',pathDescription:pathDescription};
                if(persistent){
                    kw.linkedSelectionName = linkedSelectionName;
                    kw.linkedPageId = linkedPageId;
                    kw.gridNodeId = gridNodeId;
                }
                that.setRelativeData('.#parent.linkedSelectionPars',new gnr.GnrBag(kw));
                that.fireEvent('.#parent.runQueryDo',true);
            }

            genro.serverCall('th_searchRelationPath',{
                    table:masterTable,
                    destTable:slaveTable},
                    function(result){
                        var v = result.relpathlist;
                        var masterTableCaption = result.masterTableCaption;
                        var cbdict = objectFromString(result.cbvalues);
                        if(v.length>1){
                            genro.dlg.prompt(_T('Warning'),{msg:_T('Multiple relation to table ')+masterTableCaption,
                                                            widget:'checkBoxText',
                                                            wdg_values:result.cbvalues,
                                                            wdg_cols:1,
                                                            action:function(r){
                                                                    if(!r){return;}
                                                                    var captionPath = r.split(',').map(function(k){return cbdict[k]}).join('<br/>OR ');
                                                                    cb(r,masterTableCaption,captionPath)
                                                                }
                                                            });
                        }else{
                            cb(v[0],masterTableCaption,cbdict[v[0]]);
                        }
                    });
            genro.lockScreen(false,'searchingRelation');
        """ 
        frame.data('.linkedSelectionPars',None,serverpath='linkedSelectionPars.%s' %frame.store.attributes['selectionName'].replace('*',''))
        gridattr['selfsubscribe_refreshLinkedSelection'] = """SET .#parent.linkedSelectionPars.pkeys = null;
                                                               FIRE .#parent.runQueryDo;"""

    @public_method
    def th_searchRelationPath(self,table=None,destTable=None,**kwargs):
        joiners = self.db.table(destTable).model.getTableJoinerPath(table)
        result = []
        values = []
        cbdict = dict()
        for j in joiners:
            caption_path = []
            relpath_list = []
            for r in j:
                relpath_list.append(r['relpath'])
                tblobj = self.db.table(r['table'])
                caption_path.append(self._(tblobj.name_plural if r['mode'] == 'M' else tblobj.name_long))
            if len(relpath_list)>1:
                relpath = '.'.join(relpath_list)
            else:
                relpath = relpath_list[0]
                if not relpath.startswith('@'):
                    relpath = '$%s' %relpath
            result.append(relpath)
            values.append('%s:%s' %(relpath,'/'.join(caption_path)))
            cbdict[relpath] = caption_path

        return dict(relpathlist=result,masterTableCaption=self._(self.db.table(table).name_long),cbvalues=','.join(values))



