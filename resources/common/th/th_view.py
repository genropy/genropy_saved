# -*- coding: utf-8 -*-

# th_view.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.
from builtins import str
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs,metadata
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import slugify
from gnr.core.gnrdate import nextMonth


class TableHandlerView(BaseComponent):
    py_requires = """th/th_lib:QueryHelper,
                     th/th_view:THViewUtils,
                     th/th_picker:THPicker,
                     gnrcomponents/framegrid:FrameGrid,
                     gnrcomponents/tpleditor:PaletteTemplateEditor,
                     gnrcomponents/batch_handler/batch_handler:TableScriptRunner,
                     js_plugins/chartjs/chartjs:ChartManager
                     """
                         
    @extract_kwargs(condition=True,store=True,sections=True,structure_field=True)
    @struct_method
    def th_tableViewer(self,pane,frameCode=None,table=None,th_pkey=None,viewResource=None,
                       virtualStore=None,condition=None,condition_kwargs=None,
                       structure_field=None,structure_field_kwargs=None,sections_kwargs=None,store_kwargs=None,**kwargs):
        self._th_mixinResource(frameCode,table=table,resourceName=viewResource,defaultClass='View')
    
        options = self._th_hook('options',mangler=frameCode)() or dict()
        structure_field = structure_field or options.get('structure_field')
        store_kwargs.setdefault('subtable',options.get('subtable'))
        kwargs.update(dictExtract(options,'grid_'),slice_prefix=False)
        if options.get('addrow') and options.get('addrow') is not True:
            kwargs['top_addrow_defaults'] = kwargs.get('top_addrow_defaults') or options['addrow']
        resourceConditionPars = self._th_hook('condition',mangler=frameCode,dflt=dict())()
        resourceCondition = resourceConditionPars.pop('condition',None)
        if resourceCondition:
            condition = '( %s ) AND ( %s ) ' %(condition,resourceCondition) if condition else resourceCondition
            condition_kwargs.update(dictExtract(resourceConditionPars,'condition_'))      
        
        queryBySample = self._th_hook('queryBySample',mangler=frameCode)()

        kwargs['grid_selfsubscribe_batchAssign'] = """
            if(this.widget.gridEditor){
                //inlinetablehandler
                this.widget.gridEditor.batchAssign();
            }else{
                FIRE .#parent.th_batch_run = {resource:'_common/assign_values',res_type:'action'};
            }
        """
        view = pane.thFrameGrid(frameCode=frameCode,th_root=frameCode,th_pkey=th_pkey,table=table,
                                 virtualStore=virtualStore,bySample=queryBySample is not None,
                                 condition=condition,condition_kwargs=condition_kwargs,
                                 _sections_dict=sections_kwargs,
                                 selectedPage='^.viewPage',resourceOptions=options,
                                 store_kwargs=store_kwargs,**kwargs)
        
        if queryBySample:
            self._th_handleQueryBySample(view,table=table,pars=queryBySample)
        for side in ('top','bottom','left','right'):
            hooks = self._th_hook(side,mangler=frameCode,asDict=True)
            for k in sorted(hooks.keys()):
                hooks[k](getattr(view,side))
        viewhook = self._th_hook('view',mangler=frameCode)
        if viewhook:
            viewhook(view)
        self._th_view_printEditorDialog(view)

        if structure_field:
            
            view.left.borderContainer(closable=True,width='300px',
                                    border_right='1px solid silver'
                                    ).contentPane(region='center'
                                    ).structureTree(structure_field=structure_field,view=view,**structure_field_kwargs)
        return view
    
    def _th_view_printEditorDialog(self,view):
        th_root = view.attributes['th_root']
        dlgId = '{th_root}_print_editor_dlg'.format(th_root=th_root)
        gridattr = view.grid.attributes
        gridattr['selfsubscribe_open_print_editor'] = """genro.wdgById("{dlgId}").show();
                        if($1.new){{
                            genro.publish('{th_root}_print_editor_newObject');
                        }}
                        """.format(dlgId=dlgId,th_root=th_root)
        gridattr['selfsubscribe_close_print_editor'] = 'genro.wdgById("{dlgId}").hide()'.format(dlgId=dlgId)

        dlg = view.dialog(title='!!Print Editor',nodeId=dlgId,
                            closable=True,windowRatio=.9,noModal=True)
        dlg.contentPane().remote(self._th_buildPrintEditor,
                                    table=gridattr['table'],
                                    th_root=th_root)

    @public_method
    def _th_buildPrintEditor(self,pane,table=None,th_root=None):
        pane.printGridEditor(frameCode='{th_root}_print_editor'.format(th_root=th_root),
                            table=table,parentTH=th_root,datapath='.print_editor')

    def _th_handleQueryBySample(self,view,table=None,pars=None):
        fields = pars.pop('fields')
        pars['dbtable'] = table
        pars['datapath'] = '.queryBySample'
        pars['border_spacing'] = '2px'
        pars.setdefault('_class','th_querysampleform')
        view.data('.query.bySampleIsDefault',pars.pop('isDefault',False))
        bar = view.top.slotToolbar('fb,*',childname='queryBySample')
        bar.dataController("""
            var where = new gnr.GnrBag();
            var mainIdx = 0;
            var op;
            queryBySample.forEach(function(n){
                var value = n.getValue();
                if(!value){
                    return;
                }
                op = n.attr.op || 'contains';
                if(typeof(value)!='string'){
                    op = n.attr.op  || 'equal';
                }
                if(typeof(value)=='string' && value.indexOf(',')>=0){
                    var subwhere = new gnr.GnrBag();
                    value.split(',').forEach(function(chunk,idx){
                        if(chunk){
                            subwhere.setItem('c_'+idx,chunk.trim(),{column_dtype:n.attr.column_dtype,
                                                                    op:op,jc:'or',column:n.attr.column});
                        }
                    })
                    if(subwhere.len()){
                        where.setItem('c_'+mainIdx,subwhere,{jc:'and'});
                    }
                }else{
                    where.setItem('c_'+mainIdx,value,{column_dtype:n.attr.column_dtype,op:op,jc:'and',column:n.attr.column})
                }
                mainIdx++;
            });
            SET .query.where = where;
        """,queryBySample='^.queryBySample',currentQuery='^.query.currentQuery',
                            _if='currentQuery=="__querybysample__"')
        fb = bar.fb.formbuilder(onEnter='genro.nodeById(this.getInheritedAttributes().target).publish("runbtn",{"modifiers":null});',
                                **pars)
        bar.dataController("""genro.dom.toggleVisible(bar,currentQuery=="__querybysample__");
                            view.widget.resize();""", currentQuery='^.query.currentQuery',
                            view=view, bar=bar,_onBuilt=True)
        tblobj = self.db.table(table)
        for i,fkw in enumerate(fields):
            if isinstance(fkw,str):
                field = fkw
                fkw = {}
            else:
                field = fkw.pop('field')
            fieldobj = tblobj.column(field)
            permissions = fieldobj.getPermissions(**self.permissionPars)
            if permissions.get('user_forbidden'):
                continue
            fldattr = fieldobj.attributes
            fkw.setdefault('lbl',fldattr.get('name_short') or fldattr.get('name_long'))
            fb.child(fkw.pop('tag','textbox'),value='^.c_%s' %i,attr_column=field,attr_column_dtype=fldattr.get('dtype','T'),
                        attr_op=fkw.pop('op',None),
                        **fkw)

    def th_batchAssignEnabled(self,tblobj):
        result = False
        for colobj in list(tblobj.columns.values()):
            attr = colobj.attributes
            batch_assign = attr.get('batch_assign')
            if not batch_assign:
                continue
            kw = {}
            if batch_assign is not True:
                kw.update(batch_assign)
            if not self.application.checkResourcePermission(kw.pop('tags',None),self.userTags):
                continue
            result = 'batchAssign'
            break
        return result

    @extract_kwargs(top=True,preview=True)
    @struct_method
    def th_thFrameGrid(self,pane,frameCode=None,table=None,th_pkey=None,virtualStore=None,extendedQuery=None,
                       top_kwargs=None,condition=None,condition_kwargs=None,grid_kwargs=None,configurable=True,groupable=None,
                       unlinkdict=None,searchOn=True,count=None,title=None,root_tablehandler=None,structCb=None,preview_kwargs=None,loadingHider=True,
                       store_kwargs=None,parentForm=None,liveUpdate=None,bySample=None,resourceOptions=None,
                       excludeDraft=None,excludeLogicalDeleted=None,**kwargs):
        page_hooks = self._th_hook('page',mangler=frameCode,asDict=True)
        if condition:
            condition_kwargs['condition'] = condition
        top_kwargs=top_kwargs or dict()
        pageHooksSelector = 'pageHooksSelector' if page_hooks else False
        batchAssign =  self.th_batchAssignEnabled(self.db.table(table))
        statsEnabled = resourceOptions.get('stats')
        calling_grid_kwargs = grid_kwargs
        grid_kwargs = dictExtract(resourceOptions,'grid_')
        grid_kwargs.update(calling_grid_kwargs)
        if statsEnabled is None:
            statsEnabled = True if extendedQuery else False
        statsSlot = 'stats' if statsEnabled else False
        if extendedQuery:
            if 'adm' in self.db.packages and not self.isMobile:
                templateManager = 'templateManager'
            else:
                templateManager = False
            if extendedQuery == '*':
                base_slots = ['5','fastQueryBox','runbtn','queryMenu','viewsMenu','5','filterSelected,menuUserSets','15','export','importer','resourcePrints','resourceMails','resourceActions',batchAssign,'5',templateManager,'stats','advancedTools','10',pageHooksSelector,'*']
                if self.deviceScreenSize=='phone':
                    base_slots = ['5','fastQueryBox','runbtn','queryMenu','viewsMenu',statsSlot,'export','resourcePrints','resourceMails,5',pageHooksSelector,'*']
                    print ('phone', base_slots)
            elif extendedQuery is True:
                base_slots = ['5','fastQueryBox','runbtn','queryMenu','viewsMenu','5',statsSlot,'advancedTools','10',pageHooksSelector,'*','count','5']
            else:
                base_slots = extendedQuery.split(',')
        elif not virtualStore:
            if root_tablehandler:
                base_slots = ['5','searchOn','5','count','viewsMenu','5','menuUserSets','*','export','5',statsSlot,'advancedTools','10',pageHooksSelector,'5','resourcePrints','resourceMails','resourceActions',batchAssign,'10']
                if searchOn is False:
                    base_slots.remove('searchOn')
            else:
                base_slots = ['5','vtitle','count','10',statsSlot,pageHooksSelector,'*'] if count is not False else ['5','vtitle','10',statsSlot,pageHooksSelector,'*','5']
                if searchOn:
                    base_slots.append('searchOn')

        else:
            base_slots = ['5','vtitle','count','*']
        base_slots = ','.join([b for b in base_slots if b])
        if 'slots' in top_kwargs:
            top_kwargs['slots'] = top_kwargs['slots'].replace('#',base_slots)
        else:
            top_kwargs['slots']= base_slots
        top_kwargs['_class'] = 'th_view_toolbar'
        grid_kwargs.setdefault('gridplugins', 'configurator,chartjs,print' if extendedQuery else 'configurator,chartjs,export_xls,print')
        grid_kwargs['item_name_singular'] = self.db.table(table).name_long
        grid_kwargs['item_name_plural'] = self.db.table(table).name_plural or grid_kwargs['item_name']
        grid_kwargs.setdefault('loadingHider',loadingHider)

        grid_kwargs.setdefault('selfsubscribe_loadingData',"this.setRelativeData('.loadingData',$1.loading);if(this.attr.loadingHider!==false){this.setHiderLayer($1.loading,{message:'%s'});}" %self._th_waitingElement())
        if groupable is None:
            groupable = configurable and extendedQuery == '*'
        frame = pane.frameGrid(frameCode=frameCode,childname='view',table=table,
                               struct = self._th_hook('struct',mangler=frameCode,defaultCb=structCb),
                               datapath = '.view',top_kwargs = top_kwargs,_class = 'frameGrid',
                               grid_kwargs = grid_kwargs,iconSize=16,_newGrid=True,advancedTools=True,
                               configurable=configurable,groupable=groupable,**kwargs)  
        if statsEnabled:
            self._th_handle_stats_pages(frame)
            if extendedQuery == '*':
                frame.viewLinkedDashboard()
        self._th_handle_page_hooks(frame,page_hooks)
        self._th_menu_sources(frame,extendedQuery=extendedQuery,bySample=bySample)
        self._th_viewController(frame,table=table,
                            default_totalRowCount=extendedQuery == '*',
                            excludeDraft=excludeDraft,
                            excludeLogicalDeleted=excludeLogicalDeleted)
        store_kwargs = store_kwargs or dict()
        store_kwargs['parentForm'] = parentForm
        frame.gridPane(table=table,th_pkey=th_pkey,virtualStore=virtualStore,
                        condition=condition_kwargs,unlinkdict=unlinkdict,title=title,
                        liveUpdate=liveUpdate,store_kwargs=store_kwargs)
        if configurable:
            self._th_view_confMenues(frame,statsEnabled=statsEnabled,configurable=configurable)
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
    
    def _th_waitingElement(self):
        return """<div style="height:130px;opacity:.8; width:200px;" class="waiting">&nbsp;</div>"""

    def _th_view_confMenues(self,frame,statsEnabled=None,configurable=None):
        b = Bag()
        nodeId = frame.grid.attributes['nodeId']
        table = frame.grid.attributes['table']

        b.rowchild(label='!!Reload',action="$2.widget.reload();")
        b.rowchild(label='-')
        b.rowchild(label='!!Show Archived Records',checked='^.#parent.showLogicalDeleted',
                                action="""SET .#parent.showLogicalDeleted= !GET .#parent.showLogicalDeleted;
                                           $2.widget.reload();""")
        b.rowchild(label='!!Totals count',action='SET .#parent.tableRecordCount= !GET .#parent.tableRecordCount;',
                            checked='^.#parent.tableRecordCount')
        
        if self.application.checkResourcePermission('superadmin', self.userTags):
            b.rowchild(label='-')
            b.rowchild(label='!!User Configuration',action='genro.dev.tableUserConfiguration($2.attr.table);')
        frame.grid.data('.contextMenu',b)
        
        frame.dataRemote('.advancedTools',self._th_advancedToolsMenu,cacheTime=5,table=table,
                            rootNodeId=nodeId,_fired='^.refreshAdvancedToolsMenu',statsEnabled=statsEnabled)


    @public_method
    def _th_advancedToolsMenu(self,statsEnabled=None,table=None,rootNodeId=None,**kwargs):
        b = Bag()
        #b.rowchild(label='!!Show Archived Records',checked='^.#parent.showLogicalDeleted',
        #                        action="""SET .#parent.showLogicalDeleted= !GET .#parent.showLogicalDeleted;
        #                                 FIRE .runQueryDo;""")
        #b.rowchild(label='!!Totals count',action='SET #{rootNodeId}.#parent.tableRecordCount= !GET #{rootNodeId}.#parent.tableRecordCount;'.format(rootNodeId=rootNodeId),
        #                    checked='^#{rootNodeId}.#parent.tableRecordCount'.format(rootNodeId=rootNodeId))
        if self.application.checkResourcePermission('superadmin', self.userTags):
            b.rowchild(label='-')
            b.rowchild(label='!!User Configuration',action='genro.dev.tableUserConfiguration("%s");' %table)
        b.rowchild(label='!!Configure grid',action="genro.nodeById('%s').publish('configuratorPalette');" %rootNodeId)
        b.rowchild(label='!!Print rows',action="genro.nodeById('%s').publish('printRows');" %rootNodeId)

        b.rowchild(label='!!Show Archived Records',checked='^#{rootNodeId}.#parent.showLogicalDeleted'.format(rootNodeId=rootNodeId),
                                action="""SET #{rootNodeId}.#parent.showLogicalDeleted= !GET #{rootNodeId}.#parent.showLogicalDeleted;
                                           genro.nodeById('{rootNodeId}').widget.reload();""".format(rootNodeId=rootNodeId))
        b.rowchild(label='!!Totals count',action='SET #{rootNodeId}.#parent.tableRecordCount= !GET #{rootNodeId}.#parent.tableRecordCount;'.format(rootNodeId=rootNodeId),
                            checked='^#{rootNodeId}.#parent.tableRecordCount'.format(rootNodeId=rootNodeId))
        if statsEnabled:
            b.rowchild(label='-')
            b.rowchild(label='!!Group by',action='SET .statsTools.selectedPage = "groupby"; SET .viewPage= "statsTools";')
            if self.ths_pandas_available():
                b.rowchild(label='!!Pivot table',action='SET .statsTools.selectedPage = "pandas"; SET .viewPage= "statsTools";')
        if self.db.package('biz'):
            self._th_addDashboardCommands(b,rootNodeId,table)
        return b
    
    def _th_addDashboardCommands(self,b,nodeId,table):
        b.rowchild(label='!!Save dashboard',
                            action="""this.attributeOwnerNode('_dashboardRoot').publish('saveDashboard');""")
        b.rowchild(label='!!Save dashboard as',
                        action="""this.attributeOwnerNode('_dashboardRoot').publish('saveDashboard',{saveAs:true});""")
        b.rowchild(label='!!Delete current dashboard',
                        action="""this.attributeOwnerNode('_dashboardRoot').publish('deleteCurrentDashboard');""")
        objtype = 'dash_tableviewer'
        flags='grid|%s' %nodeId
        userobjects = self.db.table('adm.userobject').userObjectMenu(objtype=objtype,flags=flags,table=table)
        if len(userobjects)>0:
            loadAction = """this.attributeOwnerNode('_dashboardRoot').publish('loadDashboard',{pkey:$1.pkey});"""
            loadmenu = Bag()
            loadmenu.update(userobjects)
            b.setItem('r_%s' %len(b),loadmenu,label='!!Load dashboard',action=loadAction)

    def _th_handle_page_hooks(self,view,page_hooks):
        frameCode = view.attributes['frameCode']
        menu = Bag()
        menu.setItem('mainView',None,caption='!!Records',pageName='mainView')
        for k in sorted(page_hooks.keys()):
            handler = page_hooks[k]
            wdg = getattr(handler,'widget','contentPane')
            childname = k.replace('%s_page_' %frameCode,'')
            title = handler.__doc__ or childname.capitalize()
            menu.setItem(childname,None,caption=title,pageName=childname)
            handler(view.child(wdg,childname=childname,pageName=childname,title=title))
        view.data('.viewPages',menu)

    def _th_handle_stats_pages(self,view):
        bc = view.borderContainer(title='!!Stats tools',pageName='statsTools',childname='statsTools',
                                    margin='5px',rounded=4,border='1px solid silver',
                                    datapath='.statsTools')
        bar = bc.contentPane(region='top').slotToolbar('20,*,s_title,*,closbtn,2',
                                                    background='#444',height='22px',
                                                    rounded_top=4)
        bar.s_title.div('^.currentTitle',color='white')
        bar.dataFormula('.currentTitle','selectedPage=="groupby"?groupByTitle:pandasTitle',selectedPage='^.selectedPage',
                        groupByTitle='^.groupby.currentTitle',
                        pandasTitle='^.pandas.currentTitle',_delay=1)
        bar.closbtn.slotButton(iconClass='close_svg',action='SET .#parent.viewPage="mainView"')

        
        sc = bc.stackContainer(selectedPage='^.selectedPage',region='center')
        sc.contentPane(title='!!Group by',pageName='groupby').groupByTableHandler(datapath='.groupby')
        if self.ths_pandas_available():
            sc.contentPane(title='!!Pivot table',pageName='pandas').tableHandlerStats(datapath='.pandas')
        

    @struct_method
    def th_viewLeftDrawer(self,pane,table,th_root):
        bar = pane.slotBar('drawerStack',min_width='160px',closable='close',
                            splitter=True,border_right='1px solid silver')
        bar.drawerStack.attributes['height'] = '100%'
        sc = bar.drawerStack.stackContainer(height='100%')
        sc.contentPane(background='red')

    @struct_method
    def th_slotbar_vtitle(self,pane,**kwargs):
        pane.div('^.title' ,_class='frameGridTitle')

    @struct_method
    def th_slotbar_importer(self,pane,frameCode=None,importer=None,**kwargs):
        options = self._th_hook('options',mangler=pane)() or dict()
        tags = options.get('uploadTags') or '_DEV_,superadmin'
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        importerStructure = self.db.table(table).importerStructure()
        matchColumns= '*' if importerStructure else None
        pane.PaletteImporter(table=table,paletteCode='%(th_root)s_importer' %inattr,
                            matchColumns=matchColumns,
                            _tags=tags,
                            _tablePermissions=dict(table=table,permissions='ins,upd,import'),
                            match_values= ','.join(list(self.db.table(table).model.columns.keys())) if not matchColumns else None,
                            dockButton_iconClass='iconbox import_data_tool inbox',title='!!Importer',**kwargs)

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


    @public_method
    def _th_remoteSectionsDispatcher(self,remotehandler=None,th_root=None,**kwargs):
        m = self.getPublicMethod('remote',remotehandler)
        sectionslist = m(**kwargs)
        meta = dict(kwargs)
        sectionsBag = self._th_buildSectionsBag(sectionslist,meta=meta)
        result = Bag()
        result['sectionsBag'] = sectionsBag
        result['dflt'] = None if not sectionsBag else meta.get('dflt') or sectionsBag.getNode('#0').label
        return result


    def _th_sectionsMetadata(self,m=None,original_kwargs=None):
        remote = original_kwargs.pop('remote',None)
        m = m or remote
        if m:
            result = dict(
                dflt = getattr(m,'default',None),
                multivalue=getattr(m,'multivalue',False),
                isMain = getattr(m,'isMain',False),
                variable_struct = getattr(m,'variable_struct',False),
                mandatory=getattr(m,'mandatory',True),
                multiButton = getattr(m,'multiButton',original_kwargs.get('multiButton')),
                lbl = original_kwargs.get('lbl') or getattr(m,'lbl',None),
                lbl_kwargs = original_kwargs.get('lbl_kwargs') or dictExtract(dict(m.__dict__),'lbl_',slice_prefix=False),
                depending_condition = getattr(m,'_if',False),
                depending_condition_kwargs = dictExtract(dict(m.__dict__),'_if_'),
                exclude_fields = getattr(m,'exclude_fields',None),
                remote = remote,
                remotepars = dictExtract(dict(m.__dict__),'remote_')
            )
        else:
            result = dict(
                dflt = original_kwargs.get('dflt'),
                multivalue =original_kwargs.get('multivalue',True),
                variable_struct = original_kwargs.get('variable_struct',False),
                isMain = original_kwargs.get('isMain',False),
                mandatory = original_kwargs.get('mandatory',None),
                depending_condition = original_kwargs.get('depending_condition',False),
                depending_condition_kwargs = original_kwargs.get('depending_condition_kwargs',dict()),
                exclude_fields = original_kwargs.get('exclude_fields',None)
            )
        return result

    def _th_buildSectionsBag(self,sectionslist=None,meta=None):
        sectionslist = sectionslist or []
        sectionsBag = Bag()
        for i,kw in enumerate(sectionslist):
            code = kw.get('code') or 'r_%i' %i
            if kw.get('isDefault'):
                meta['dflt'] = meta.get('dflt') or code
            sectionsBag.setItem(code,None,**kw)
        return sectionsBag

    @extract_kwargs(condition=True,lbl=dict(slice_prefix=False))
    @struct_method
    def th_slotbar_sections(self,parent,sections=None,condition=None,condition_kwargs=None,
                            all_begin=None,all_end=None,include_inherited=False,
                            **kwargs):
        inattr = parent.getInheritedAttributes()
        th_root = inattr['th_root']
        pane = parent.div(datapath='.sections.%s' %sections)
        tblobj = self.db.table(inattr['table'])
        m = self._th_hook('sections_%s' %sections,mangler=th_root,defaultCb=False)
        sectionslist = None
        meta = self._th_sectionsMetadata(m,original_kwargs=kwargs)
        remote = meta.get('remote')
        if remote:
            parent.dataRpc(None,self._th_remoteSectionsDispatcher,
            _onResult="""
                if(!result){
                    return result;
                }
                PUT .%s.data = null;
                SET .%s.data = result.getItem('sectionsBag');
                genro.wdgById(kwargs.th_root+'_grid').setStoreBlocked('building_section_'+kwargs._sectionname,false);
                SET .%s.current = result.getItem('dflt');
            """ %(sections,sections,sections),
                _onCalling="""
                    genro.wdgById(th_root+'_grid').setStoreBlocked('building_section_'+_sectionname,true);
                    PUT .%s.current = null;
                """ %sections,
                th_root=th_root,datapath='.sections',_sectionname=sections,
                _onBuilt=True,remotehandler=remote,**meta.get('remotepars'))
        elif m:
            sectionslist = m()
        elif sections in  tblobj.model.columns and (tblobj.column(sections).relatedTable() is not None or 
                                                tblobj.column(sections).attributes.get('values')):
            sectionslist = self._th_section_from_type(tblobj,sections,condition=condition,condition_kwargs=condition_kwargs,
                                                    all_begin=all_begin,all_end=all_end,include_inherited=include_inherited)
        sectionsBag = self._th_buildSectionsBag(sectionslist,meta=meta)
        pars = dict(kwargs)
        pars.update(meta)
        self._th_buildSectionsGui(pane,parent=parent,sectionsBag=sectionsBag,sections=sections,th_root=th_root,**pars)
    
    def _th_buildSectionsGui(self,pane,parent=None,multiButton=None,sectionsBag=None,
                            multivalue=None,mandatory=None,
                            extra_section_kwargs=None,lbl=None,lbl_kwargs=None,
                            exclude_fields=None,sections=None,
                            isMain=None,th_root=None,depending_condition=None,
                            depending_condition_kwargs=None,dflt=None,variable_struct=None,**kwargs):
        
        inattr = parent.getInheritedAttributes()
        sections_dict=inattr['_sections_dict']
        extra_section_kwargs = dictExtract(sections_dict,'ALL_')
        extra_section_kwargs.update(dictExtract(sections_dict,'%s_' %sections))
        extra_section_kwargs.update(kwargs)
        th_root = inattr['th_root']
        channel = extra_section_kwargs.pop('channel',None) or th_root
        pane.data('.data',sectionsBag)
        pane.data('.variable_struct',variable_struct)
        if sectionsBag:
            if not dflt:
                
                dflt = sectionsBag.getNode('#0').label
            pane.data('.current',dflt)

        if multivalue and variable_struct:
            raise Exception('multivalue cannot be set with variable_struct')

        multiButton = multiButton is True or multiButton is None or multiButton and len(sectionsBag)<=multiButton
        if multiButton:
            mb = pane.multiButton(items='^.data',value='^.current',multivalue=multivalue,mandatory=mandatory,
                                disabled='^.#parent.#parent.grid.loadingData',**extra_section_kwargs)
    
        else:
            mb = pane.formbuilder(cols=1,border_spacing='0',**lbl_kwargs)
            lbl = lbl or sections.replace('_',' ').capitalize()
            if multivalue:
                mb.checkBoxText(values='^.data',value='^.current',lbl=lbl,
                                labelAttribute='caption',parentForm=False,
                                disabled='^.#parent.#parent.grid.loadingData',
                                        popup=True,cols=1,**extra_section_kwargs)
            else:
                mb.filteringSelect(storepath='.data',value='^.current',lbl=lbl,
                                disabled='^.#parent.#parent.grid.loadingData',
                                storeid='#k',parentForm=False,
                                validate_notnull=mandatory,
                                popup=True,cols=1,**extra_section_kwargs)
        if exclude_fields:
            pane.dataController("""
            var cb = function(n,value){
                return exclude_fields.split(',').indexOf(n.attr.column)>=0 && !isNullOrBlank(value);
            }
            var excluded = false;
            if(_reason=='child'){
                if(_triggerpars.kw.updvalue){
                    excluded = cb(_node,_triggerpars.kw.value);
                }
            }else if(_node.label=='where'){
                where.walk(function(n){
                    excluded = cb(n,n.getValue());
                    if(excluded){
                        return true;
                    }
                });
            }
            SET .excluded = excluded;
            """,
            exclude_fields=exclude_fields,where='^.#parent.#parent.query.where')
        parent.dataController("""var enabled = depending_condition?funcApply('return '+depending_condition,_kwargs):true;
                                SET .%s.enabled = enabled;
                                FIRE .#parent.sections_changed;
                                """ %sections,
                                ss=sections,datapath='.sections',
                                depending_condition=depending_condition,_onBuilt=True,
                                        **depending_condition_kwargs)
        pane.dataController("genro.publish(channel+'_changed_section',{section:sectionname,value:current})",
                            channel=channel,current='^.current',sectionname=sections)
        pane.dataController("""if(section==mysection && data.getNode(value)){
            SET .current = value;
        }""",mysection=sections,data='=.data',
        **{'subscribe_%s_changed_section' %channel:True})
        
        pane.dataController("""
            genro.dom.toggleVisible(__mb,enabled && !excluded);
        """,__mb=mb,enabled='^.enabled',excluded='^.excluded',
        _onBuilt=True,_delay=1)
        pane.dataController("""
            genro.assert(currentSection,'missing current section for sections %s')
            var sectionNode = sectionbag.getNode(currentSection);
            if(isMain){
                FIRE .#parent.#parent.clearStore;
                SET .#parent.#parent.excludeDraft = !sectionNode.attr.includeDraft;
            } 
            FIRE .#parent.#parent.sections_changed;
            """ %sections
            ,isMain=isMain,_onBuilt=True if sectionsBag else False,
            currentSection='^.current',sectionbag='=.data',
            _delay=1,
            th_root=th_root)

    def th_distinctSections(self,table,field=None,allPosition=True,**kwargs):
        allsection = [dict(code='all',caption='!!All')]
        sections = []
        f = self.db.table(table).query(columns='$%s' %field,addPkeyColumn=True,distinct=True,**kwargs).fetch()
        for i,r in enumerate(f):
            if r[field]:
                sections.append(dict(code='c_%i' %i,caption=r[field],condition="$%s=:v" %field,condition_v=r[field]))
        if allPosition:
            return allsection+sections if allPosition!='last' else sections+allsection
        return sections
 
    def th_monthlySections(self,column=None,dtstart=None,count=3,allPosition=True,over='>=',**kwargs):
        sections = []
        import datetime
        from dateutil import rrule
        dtstart = dtstart or self.workdate
        dtstart = datetime.date(dtstart.year,dtstart.month,1)
        for idx,dt in enumerate(rrule.rrule(rrule.MONTHLY, 
                                dtstart=dtstart, 
                                count=count)):
            currdate = dt.date()
            condition = "to_char({column},'YYYY-MM')=to_char(:currdate,'YYYY-MM')"\
                        .format(column=column)
            sections.append(dict(code='s{idx}'.format(idx=idx),
                            condition=condition,
                            condition_currdate=currdate,
                            isDefault=idx==0,
                            caption=self.toText(currdate,format='MMMM')))
        endlast = nextMonth(currdate)
        if over:
            sections.append(dict(code='after',condition='{column}>=:endlast'.format(column=column),
                                condition_endlast=endlast,
                                caption='!![en]Next months'))
        return sections

    @struct_method
    def th_slotbar_stats(self,pane,**kwargs):
        pane.slotButton(label='Group By',iconClass='iconbox statistica_tools sum',
                        action='SET .statsTools.selectedPage = "groupby"; SET .viewPage= "statsTools";')


    @struct_method
    def th_slotbar_queryMenu(self,pane,**kwargs):
        pane.div(_class='iconbox menubox magnifier').menu(storepath='.query.menu',_class='smallmenu',modifiers='*',
                    action="""
                    if($1.fullpath=='__queryeditor__'){
                        var currentQuery = GET .query.currentQuery;
                        if(currentQuery && !currentQuery.startsWith('__')){
                            SET .query.queryEditor=true;
                            return;
                        }
                        if(currentQuery=='__querybysample__'){
                            SET .query.currentQuery = '__basequery__';
                        }
                        SET .query.currentQuery = $1.fullpath;
                        SET .query.queryEditor=true; 
                        SET .query.queryAttributes.extended = true;
                    }else{
                        if($1.fullpath=='__basequery__'){
                            SET .query.queryEditor=false;
                        }
                        SET .query.currentQuery = $1.fullpath;
                        SET .query.menu.__queryeditor__?disabled=$1.filteringPkeys!=null;
                    }""")

    @public_method
    @metadata(prefix='query',code='default_duplicate_finder',description='!!Find all duplicates')
    def th_default_find_duplicates(self, tblobj=None,sortedBy=None,date=None, where=None,**kwargs):
        pkeys = tblobj.findDuplicates()
        query = tblobj.query(where='$%s IN :pkd' %tblobj.pkey,pkd=pkeys,**kwargs)
        selection= query.selection(sortedBy=None, _aggregateRows=True) 
        selection.forcedOrderBy='$_duplicate_finder,$__mod_ts'
        return selection

    @public_method
    @metadata(prefix='query',code='default_invalidrows_finder',description='!!Find invalid rows')
    def th_default_find_invalidRows(self, tblobj=None,sortedBy=None,date=None, where=None,**kwargs):
        query = tblobj.query(where='$__is_invalid_row IS TRUE',**kwargs)
        selection= query.selection(sortedBy=None, _aggregateRows=True) 
        return selection

    #@public_method
    #@metadata(prefix='query',code='default_duplicate_finder_to_del',description='!!Find duplicates to delete')
    #def th_default_find_duplicates_to_del(self, tblobj=None,sortedBy=None,date=None, where=None,**kwargs):
    #    pkeys = tblobj.findDuplicates(allrecords=False)
    #    query = tblobj.query(where='$%s IN :pkd' %tblobj.pkey,pkd=pkeys,**kwargs)
    #    return query.selection(sortedBy=sortedBy, _aggregateRows=True) 

    def _th_menu_sources(self,pane,extendedQuery=None,bySample=None):
        inattr = pane.getInheritedAttributes()
        th_root = inattr['th_root']
        table = inattr['table']
        gridId = '%s_grid' %th_root

        #SOURCE MENUQUERIES
        pane.dataController("""TH(th_root).querymanager.onChangedQuery(currentQuery);
                          """,currentQuery='^.query.currentQuery',th_root=th_root)
        pane.dataController("""
            genro.dlg.thIframePalette({table:'adm.userobject',palette_top:'100px',
                                    palette_right:'600px',current_tbl:tbl,
                                    current_pkg:pkg,title:title,
                                    viewResource:'ViewCustomColumn'
                                    ,formResource:'FormCustomColumn'})
            """,tbl=table,_fired='^.handle_custom_column',pkg=table.split('.')[0],title='!!Custom columns')
        q = Bag()
        pyqueries = self._th_hook('query',mangler=th_root,asDict=True)
        if self.db.table(table).column('_duplicate_finder') is not None and \
                self.application.checkResourcePermission('_DEV_,superadmin', self.userTags):
            pyqueries['default_duplicate_finder'] = self.th_default_find_duplicates
            #pyqueries['default_duplicate_finder_to_del'] = self.th_default_find_duplicates_to_del
        
        if self.db.table(table).hasInvalidCheck():
            pyqueries['default_invalidrows_finder'] = self.th_default_find_invalidRows        

        for k,v in pyqueries.items():
            pars = dictExtract(dict(v.__dict__),'query_')
            code = pars.get('code')
            q.setItem(code,None,tip=pars.get('description'),filteringPkeys=v,**pars)
        pane.data('.query.pyqueries',q)
        pane.dataRemote('.query.menu',self.th_menuQueries,pyqueries='=.query.pyqueries',
                        _resolved_pyqueries=q,editor=extendedQuery,bySample=bySample,
                        table=table,th_root=th_root,caption='Queries',cacheTime=15,
                        _resolved=extendedQuery)
        pane.dataController("TH(th_root).querymanager.queryEditor(queryEditor);",
                        th_root=th_root,queryEditor="^.query.queryEditor")
        if 'adm' not in self.db.packages:
            return
        pane.dataRemote('.query.savedqueries',self.th_menuQueries,
                        table=table,th_root=th_root,cacheTime=5,editor=False)

        
        pane.dataRemote('.query.helper.in.savedsets',self.th_menuSets,
                        objtype='list_in',table=table,cacheTime=5)
                        
        pane.dataRpc('dummy',self.db.table('adm.userobject').deleteUserObject,pkey='=.query.queryAttributes.pkey',_fired='^.query.delete',
                   _onResult='FIRE .query.currentQuery="__newquery__";FIRE .query.refreshMenues;')

        #SOURCE MENUVIEWS
        pane.dataController("""genro.grid_configurator.loadView(gridId, (currentView || favoriteView));
                                """,
                            currentView="^.grid.currViewPath",
                            favoriteView='^.grid.favoriteViewPath',
                            gridId=gridId,_onBuilt=1)
        q = Bag()
        pyviews = self._th_hook('struct',mangler=th_root,asDict=True)
        for k,v in list(pyviews.items()):
            prefix,name=k.split('_struct_')
            q.setItem(name,self._prepareGridStruct(v,table=table),caption=v.__doc__)
        pane.data('.grid.resource_structs',q)
        pane.dataRemote('.grid.structMenuBag',self.th_menuViews,pyviews=q.digest('#k,#a.caption'),currentView="^.grid.currViewPath",
                        table=table,th_root=th_root,favoriteViewPath='^.grid.favoriteViewPath',cacheTime=30)

        options = self._th_hook('options',mangler=pane)() or dict()
        #SOURCE MENUPRINT
        pane.dataRemote('.resources.print.menu',self.th_printMenu,table=table,
                        flags=options.get('print_flags'),
                        printEditorOpened='=.print_editor.viewer?=#v!==null',
                        from_resource=options.get('print_from_resource',True),
                        gridId=gridId,
                        cacheTime=5)

        #SOURCE MENUMAIL
        pane.dataRemote('.resources.mail.menu',self.th_mailMenu,table=table,flags=options.get('mail_flags'),
                        from_resource=options.get('mail_from_resource',True),cacheTime=5)

        #SOURCE MENUACTIONS
        pane.dataRemote('.resources.action.menu',self.table_script_resource_tree_data,
                        res_type='action', table=table,cacheTime=5)

        if 'multidb' in self.db.packages and not (self.dbstore or self.db.table(table).multidb=='*'):
            pane.data('.query.multidb.pickermethod',self.th_multidbStoreQueryPicker)


    @struct_method
    def th_slotbar_resourcePrints(self,pane,flags=None,from_resource=None,hidden=None,**kwargs):
        pane.menudiv(iconClass='iconbox menubox print',hidden=hidden,storepath='.resources.print.menu',
                    _tablePermissions=dict(table=pane.frame.grid.attributes.get('table'),
                                                        permissions='print'),
                    action="""FIRE .th_batch_run = {resource:$1.resource,template_id:$1.template_id,userobject:$1.userobject,res_type:'print'};""")

    @public_method
    def th_printMenu(self,table=None,flags=None,from_resource=True,
                    gridId=None,printEditorOpened=None,**kwargs):
        result = self._printAndMailMenu(table=table,flags=flags,from_resource=from_resource,res_type='print')
        gridprint = self.db.table('adm.userobject').userObjectMenu(table=table,objtype='gridprint')
        if gridprint and len(gridprint)>0:
            result.update(gridprint)
        result.walk(self._th_gridPrint)

        result.addItem('r_sep_edit',None,caption='-')
        if printEditorOpened:
            result.addItem('r_edit',None,caption='!!Edit current print',
                        action="genro.nodeById('{gridId}').publish('open_print_editor',{{new:false}});".format(gridId=gridId))
        result.addItem('r_new',None,caption='!!New Print',
                        action="genro.nodeById('{gridId}').publish('open_print_editor',{{new:true}});".format(gridId=gridId))
        return result
        
    @struct_method
    def th_slotbar_resourceActions(self,pane,**kwargs):
        pane.menudiv(iconClass='iconbox gear',storepath='.resources.action.menu',
                            _tablePermissions=dict(table=pane.frame.grid.attributes.get('table'),
                                                        permissions='action'),action="""
                            FIRE .th_batch_run = {resource:$1.resource,res_type:"action"};
                            """,_class='smallmenu')
    @struct_method
    def th_slotbar_resourceMails(self,pane,from_resource=None,flags=None,**kwargs):
        pane.menudiv(iconClass='iconbox mail',storepath='.resources.mail.menu',
                        _tablePermissions=dict(table=pane.frame.grid.attributes.get('table'),
                                                        permissions='mail'),
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
        if self.getPreference('print.enable_pdfform',pkg='sys') and self.site.getService('pdfform'):
            objtype = 'template,pdfform'
        else:
            objtype = 'template'
        templates = self.db.table('adm.userobject').userObjectMenu(table=table,objtype=objtype,flags=flags)
        if templates and len(templates)>0:
            result.update(templates)
        result.walk(self._th_addTpl,res_type=res_type)
        return result
    
    def _th_addTpl(self,node,res_type=None):
        if node.attr.get('code'):
            node.attr['resource'] ='%s_%s' %(res_type,node.attr['objtype'])
            node.attr['template_id'] = node.attr['pkey']

    def _th_gridPrint(self,node):
        if node.attr.get('code') and not node.attr.get('resource'):
            node.attr['resource'] ='_common/print_gridres'
            node.attr['userobject'] = node.attr['pkey']
        
        
    @struct_method
    def th_slotbar_templateManager(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        htmlPaletteCode = '%(thlist_root)s_template_manager' %inattr
        if self.getPreference('print.enable_pdfform',pkg='sys') and self.site.getService('pdfform'):
            self.mixinComponent("services/pdfform/pdftk/component:PalettePdfFormEditor")
            pdfPaletteCode = '%(thlist_root)s_pdf_template_manager' %inattr
            templatemenu = pane.menudiv(iconClass='iconbox create_edit_html_template',tip='!!Template menu')
            #costruiscimenu
            templatemenu.menuline(label='!!Html Template',action="PUBLISH %s_show"%htmlPaletteCode)
            templatemenu.menuline(label='!!Pdf Template',action="PUBLISH %s_show"%pdfPaletteCode)
            pane.paletteTemplateEditor(maintable=table,paletteCode=htmlPaletteCode,dockTo='dummyDock')
            pane.pdfFormEditorPalette(maintable=table, paletteCode=pdfPaletteCode,dockTo='dummyDock')
        else:
            pane.paletteTemplateEditor(maintable=table,paletteCode=htmlPaletteCode,dockButton_iconClass='iconbox create_edit_html_template')

    @struct_method
    def th_slotbar_pageHooksSelector(self,pane,**kwargs):
        pane.multiButton(items='^.viewPages',value='^.viewPage',identifier='pageName')
      
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
            
            querybase = self._th_hook('query',mangler=th_root)() or dict(column=(tblobj.attributes.get('caption_field') or tblobj.pkey),op='contains',val='')
        queryBag = self.th_prepareQueryBag(querybase,table=table)
        frame.data('.baseQuery', queryBag)
        options = self._th_hook('options',mangler=th_root)() or dict()
        pageOptions = self.pageOptions or dict()
        #liveUpdate: 'NO','LOCAL','PAGE'
        liveUpdate = liveUpdate or options.get('liveUpdate') or pageOptions.get('liveUpdate') or self.site.config['options?liveUpdate'] or 'LOCAL'
        externalLiveUpdateDelay = 5
        if liveUpdate == '*':
            liveUpdate = True
        elif isinstance(liveUpdate,str) and liveUpdate.isdigit():
            externalLiveUpdateDelay = int(liveUpdate)
            liveUpdate = True
        store_kwargs.setdefault('externalLiveUpdateDelay', externalLiveUpdateDelay)
        store_kwargs.setdefault('liveUpdate',liveUpdate)
        hardQueryLimit = options.get('hardQueryLimit')
        allowLogicalDelete = store_kwargs.pop('allowLogicalDelete',None) or options.get('allowLogicalDelete')
        frame.data('.hardQueryLimit',int(hardQueryLimit) if hardQueryLimit else None)
        frame.dataController("""
                            if(_node && _node.label!='current'){
                                return;
                            }
                            var sub_title = _sections?th_sections_manager.getSectionTitle(_sections):"";
                            SET .title = (custom_title || name_plural || name_long)+sub_title;
                        """,
                        custom_title=title or options.get('title') or False,
                        name_plural='=.table?name_plural',
                        name_long='=.table?name_long',
                        #view_title='=.title',
                        _sections='^.sections',
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
        gridattr.setdefault('draggable_row',not self.isMobile)
        gridattr.setdefault('userSets','.sets')

        if virtualStore:
            chunkSize= rowsPerPage * 4
            selectionName = '*%s' %th_root
        else:
            chunkSize = None
            selectionName = None
        if liveUpdate!='NO':
            self.subscribeTable(table,True,subscribeMode=liveUpdate)
        selectmethod = store_kwargs.pop('selectmethod',None) or self._th_hook('selectmethod',mangler=frame,defaultCb=False)
        filteringPkeys = store_kwargs.pop('filteringPkeys',None) or self._th_hook('filteringPkeys',mangler=frame,defaultCb=False)
        store_kwargs.update(condPars)
        _if = store_kwargs.pop('_if',None) or store_kwargs.pop('if',None)
        _onStart = store_kwargs.pop('_onStart',None) or store_kwargs.pop('onStart',None)
        _else = None
        if _if:
            _else = "this.store.clear();"
        frame.dataController("""
            grid.attr.multiStores = multiStores;
            grid.widget.setStructpath();
        """,multiStores='^.query.multiStores',grid=frame.grid)
        frame.dataFormula('.sum_columns',"sum_columns_source && sum_columns_source.len()?sum_columns_source.keys().join(','):null",
                                        sum_columns_source='=.sum_columns_source',_onBuilt=True)
        frame.dataController("""
            th_sections_manager.updateSectionsStatus(sectionbag,genro.getFrameNode(th_root));
            var loadingData = GET .grid.loadingData;
            var storeNode = grid.collectionStore().storeNode
            if(storeNode._lastRpcTs && !loadingData){
                FIRE .runQueryDo;
            }
            """,
            th_root=th_root,
            lastQueryTime = '=.store?servertime',
            sectionbag = '=.sections',
            _fired = '^.sections_changed',
            _if = 'sectionbag.len()',grid=frame.grid.js_widget,
            _delay = 100)
        frame.dataController("""
            this.fireEvent('.runQueryDo_'+viewPage,true);
        """,_runQueryDo='^.runQueryDo',viewPage='=.viewPage')
        store_kwargs.setdefault('weakLogicalDeleted',options.get('weakLogicalDeleted'))
        multiStores = store_kwargs.pop('multiStores',None)
        frame.data('.query.limit',store_kwargs.pop('limit',None))
        store = frame.grid.selectionStore(table=table,
                               chunkSize=chunkSize,childname='store',
                               where='=.query.where',
                               queryMode='=.query.queryMode', 
                               sortedBy='=.grid.sorted',
                               customOrderBy='=.query.customOrderBy',
                               multiStores=multiStores or '=.query.multiStores',
                               pkeys='=.query.pkeys', 
                               _runQueryDo='^.runQueryDo_mainView',
                               _cleared='^.clearStore',
                               _onError="""return error;""", 
                               selectionName=selectionName, recordResolver=False, condition=condition,
                               sqlContextName='standard_list', totalRowCount='=.tableRecordCount',
                               row_start='0',
                               allowLogicalDelete=allowLogicalDelete,
                               excludeLogicalDeleted='=.excludeLogicalDeleted',
                               excludeDraft='=.excludeDraft',
                               applymethod=store_kwargs.pop('applymethod',None) or self._th_hook('applymethod',dflt=None,mangler=frame),
                               timeout=180000, 
                               selectmethod= selectmethod,
                               filteringPkeys=filteringPkeys or '=.query.queryAttributes.filteringPkeys',
                               currentFilter = '=.query.currentFilter',
                               prevSelectedDict = '=.query.prevSelectedDict',
                               unlinkdict=unlinkdict,
                               userSets='.sets',_if=_if,_else=_else,
                               _sections='=.sections',
                               _use_grouper='=.use_grouper',
                               limit='=.query.limit',
                               queryExtraPars='=.query.extraPars',
                               joinConditions='=.query.joinConditions',
                               hardQueryLimit='=.hardQueryLimit',
                               _onStart=_onStart,
                               _th_root =th_root,
                               _POST =True,
                               httpMethod='WSK' if self.extraFeatures['wsk_grid'] else None,
                               _onCalling="""
                               %s
                               delete this._currentGrouper;
                               if(kwargs.fkey && this.form && this.form.isLogicalDeleted()){
                                   kwargs.excludeLogicalDeleted = 'mark';
                               }
                               if(_sections){
                                    if(th_sections_manager.onCalling(_sections,kwargs)===false){
                                        return false;
                                    }
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
                               if( _use_grouper){
                                   this._currentGrouper = th_grouper_manager.onCalling(kwargs);
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
                if(event.shiftKey){
                    TH(th_root_code).querymanager.pkeySetToQuery(highlighted.join(','));
                }else{
                    this.setRelativeData('.query.pkeys',highlighted.join(','));
                }
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
                        _onBuilt=1,th_root = inattr['th_root'],table = inattr['table'])

        pane.menudiv(iconClass='iconbox heart',tip='!!User sets',storepath='.usersets.menu')
       
    @struct_method
    def th_slotbar_fastQueryBox(self, pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table'] 
        th_root = inattr['th_root']
        tablecode = table.replace('.','_')
        pane.dataController(
               """var th = TH(th_root);
                  th.querymanager = th.querymanager || new gnr.QueryManager(th,this,table);""" 
               , _init=True, _onBuilt=True, table=table,th_root = th_root)
        fmenupath = 'gnr.qb.%s.fieldsmenu' %tablecode
        options = self._th_hook('options',mangler=pane)() or dict()
        pane.dataRemote(fmenupath,self.relationExplorer,item_type='QTREE',
                        branch=options.get('branch'),
                        table=table,omit='_*')
        pane.data('gnr.qb.sqlop',self.getSqlOperators())   
        pane.dataController("""var th=TH(th_root).querymanager.onQueryCalling(querybag,filteringPkeys);
                              """,th_root=th_root,_fired="^.runQuery",
                           querybag='=.query.where',
                           filteringPkeys='=.query.queryAttributes.filteringPkeys')
        pane.dataFormula('.currentQueryCountAsString', 'msg.replace("_rec_",cnt)',
                           cnt='^.currentQueryCount', _if='cnt', _else='',
                           msg='!!Current query will return _rec_ items')
        pane.dataController("""SET .currentQueryCountAsString = waitmsg;
                              FIRE .updateCurrentQueryCount;
                               genro.dlg.alert(alertmsg,dlgtitle);
                                 """, _fired="^.showQueryCountDlg", waitmsg='!!Working.....',
                              dlgtitle='!!Current query record count',alertmsg='=.currentQueryCountAsString')
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


        extendedQueryButton = querybox_stack.lightbutton("==_internalQueryCaption || _caption",
                        _caption='^.#parent.queryAttributes.caption',
                        _internalQueryCaption='^.#parent.#parent.internalQuery.caption', 
                        action="""if(!_querybysample){
                            SET .#parent.#parent.query.queryEditor=true;
                        }""",
                        _class='th_querybox_extended',
                        _querybysample = '=.#parent.#parent.query.currentQuery?=#v=="__querybysample__"',
                        hidden='^.#parent.queryAttributes.extended?=!#v',min_width='20em')
        extendedQueryButton.tooltip(callback="""
            var internalQueryTooltip = this.getRelativeData('.internalQuery.tooltip');
            var internalQueryCaption = this.getRelativeData('.internalQuery.caption');
            var whereAsPlainText = this.getRelativeData('.store?whereAsPlainText');
            var currentQuery = this.getRelativeData('.query.currentQuery');
            return internalQueryTooltip || whereAsPlainText || internalQueryCaption || _T('Click to show query');

        """,datapath='.#parent.#parent',modifiers='Shift')
        
            #_internalQueryTooltip='^.#parent.#parent.internalQuery.tooltip',
            #tooltip='==_internalQueryTooltip || _internalQueryCaption || _caption || _internalQueryCaption',
            #_internalQueryTooltip='^.#parent.#parent.internalQuery.tooltip',

        
    def _th_viewController(self,pane,table=None,th_root=None,
                        default_totalRowCount=None,excludeDraft=None,
                                        excludeLogicalDeleted=None):
        table = table or self.maintable
        tblattr = dict(self.db.table(table).attributes)
        tblattr.pop('tag',None)
        pane.data('.table',table,**tblattr)
        options = self._th_hook('options',mangler=pane)() or dict()
        excludeLogicalDeleted = options.get('excludeLogicalDeleted',excludeLogicalDeleted)
        if excludeLogicalDeleted is None:
            excludeLogicalDeleted = True
        if excludeDraft is None:
            excludeDraft = True
        showLogicalDeleted = not excludeLogicalDeleted
        pane.data('.excludeLogicalDeleted', 'mark' if showLogicalDeleted else True)
        pane.dataController("""SET .excludeLogicalDeleted = show?'mark':true;
                               genro.dom.setClass(dojo.body(),'th_showLogicalDeleted',show);
                            """,show="^.showLogicalDeleted")
        pane.data('.showLogicalDeleted',showLogicalDeleted)
        pane.data('.excludeDraft', options.get('excludeDraft',excludeDraft))
        pane.data('.tableRecordCount',options.get('tableRecordCount',default_totalRowCount))



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
    def th_menuViews(self,table=None,th_root=None,pyviews=None,objtype=None,favoriteViewPath=None,currentView=None,**kwargs):
        result = Bag()
        objtype = objtype or 'view'
        currentView = currentView or favoriteViewPath or '__baseview__'
        gridId = '%s_grid' %th_root
        result.setItem('__baseview__', None,caption='Base View',gridId=gridId,checked = currentView=='__baseview__')
        if pyviews:
            for k,caption in pyviews:
                result.setItem(k.replace('_','.'),None,description=caption,caption=caption,viewkey=k,gridId=gridId)
        userobjects = self.db.table('adm.userobject').userObjectMenu(objtype=objtype,flags='%s_%s' % (self.pagename, gridId),table=table)
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
                node.attr['checked'] = True
            elif node.attr['code'] == favPath:
                node.attr['favorite'] = True
            
        else:
            node.attr['favorite'] = None
    
    @public_method
    def th_menuQueries(self,table=None,th_root=None,pyqueries=None,editor=True,bySample=False,**kwargs):
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
        if bySample:
            querymenu.setItem('__querybysample__',None,caption='!!Query by sample',extended=True)
        if editor:
            querymenu.setItem('__queryeditor__',None,caption='!!Query editor',extended=False)
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
        for optype, values in list(optype_dict.items()):
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




