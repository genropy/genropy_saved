# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrbag import Bag


class TableHandlerGroupBy(BaseComponent):
    js_requires = 'gnrdatasets,th/th_groupth'

    @extract_kwargs(condition=True,store=True,grid=True,tree=dict(slice_prefix=False))
    @struct_method
    def th_groupByTableHandler(self,pane,frameCode=None,title=None,table=None,linkedTo=None,
                                struct=None,where=None,viewResource=None,
                                condition=None,condition_kwargs=None,store_kwargs=None,datapath=None,
                                treeRoot=None,configurable=True,
                                dashboardIdentifier=None,static=False,pbl_classes=None,
                                grid_kwargs=None,tree_kwargs=None,groupMode=None,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = table or inattr.get('table')
        if not (dashboardIdentifier or where or condition):
            linkedTo = linkedTo or inattr.get('frameCode')
        
        if linkedTo:
            frameCode = frameCode or '%s_groupedView' %linkedTo 
            if not struct:
                struct = self._th_hook('groupedStruct',mangler=linkedTo,defaultCb=self._thg_defaultstruct)
        if not linkedTo:
            self.subscribeTable(table,True,subscribeMode=True)
        else:
            pane.dataController("""
  
                var groupbystore = genro.nodeById('{frameCode}_grid_store');
                if(!groupbystore){
                    return;
                }
                if(groupbystore.getRelativeData('.grid.currentGrouperPkey')){{
                    return;
                }}
                groupbystore.store.loadData();
            """.format(frameCode=frameCode),currentGrouperPkey='=.grid.currentGrouperPkey',
                **{'subscribe_{linkedTo}_grid_onNewDatastore'.format(linkedTo=linkedTo):True})
            pane.dataController("""
                var groupbystore = genro.nodeById('{frameCode}_grid_store');
                if(!groupbystore){
                    return;
                }
                if(groupbystore.getRelativeData('.grid.currentGrouperPkey')){{
                    return;
                }}
                groupbystore.store.loadData();""",
            datapath='#{linkedTo}_frame'.format(linkedTo=linkedTo),
            currentGrouperPkey='=.grid.currentGrouperPkey',
            _runQuery='^.runQueryDo',_sections_changed='^.sections_changed',
           linkedTo=linkedTo,_delay=200)
        frameCode = frameCode or 'thg_%s' %table.replace('.','_')
        datapath = datapath or '.%s' %frameCode
        rootNodeId = frameCode
        if not struct and viewResource:
            self._th_mixinResource(frameCode,table=table,resourceName=viewResource,defaultClass='View')
            struct = self._th_hook('groupedStruct',mangler=frameCode)
            store_kwargs['applymethod'] = store_kwargs.get('applymethod') or self._th_hook('groupedApplymethod',mangler=frameCode)
        sc = pane.stackContainer(datapath=datapath,_class='group_by_th',selectedPage='^.output',_anchor=True,
                                nodeId=rootNodeId,_forcedGroupMode=groupMode,
                                _linkedTo = linkedTo,table=table,
                                selfsubscribe_viewMode="""
                                    var viewMode = $1.split('_');
                                    SET .groupMode = viewMode[0];
                                    SET .output = viewMode[1];
                                """,
                                selfsubscribe_saveDashboard="genro.groupth.saveAsDashboard(this,$1);",
                                selfsubscribe_loadDashboard="genro.groupth.loadDashboard(this,$1)",
                                selfsubscribe_deleteCurrentDashboard="genro.groupth.deleteCurrentDashboard(this,$1)",

                                _dashboardRoot=True,**kwargs)  
        gridstack = sc.stackContainer(pageName='grid',title='!!Grid View',selectedPage='^.groupMode')

        #gridstack.dataFormula('.currentTitle','',defaultTitle='!!Group by')
        frame = gridstack.frameGrid(frameCode=frameCode,grid_onDroppedColumn="""
                                    genro.groupth.addColumnCb(this,{data:data, column:column,fieldcellattr:fieldcellattr,treeNode:treeNode});
                                    """,
                                    datamode='attr',
                                struct=struct or self._thg_defaultstruct,_newGrid=True,pageName='flatview',title='!!Flat',
                                grid_kwargs=grid_kwargs)

        
        frame.dataFormula('.changets.flatview','new Date();',store='^.store',struct='^.grid.struct',
                            _delay=1)
        if dashboardIdentifier:
            frame.dataController("root.publish('loadDashboard',{pkey:dashboardIdentifier});",root=sc,
                                dashboardIdentifier=dashboardIdentifier,_onBuilt=1)
        
        if static:
            slots = '5,vtitle,count,*,searchOn,export,5'
            if pbl_classes is None:
                pbl_classes = True
            if pbl_classes:
                bar = frame.top.slotBar(slots,_class='pbl_roundedGroupLabel',vtitle=title)
                frame.attributes['_class'] = 'pbl_roundedGroup'
            else:
                bar = frame.top.slotToolbar(slots)
                bar.vtitle.div(title,font_size='.9em',color='#666',font_weight='bold')

        else:
            frame.dataFormula('.currentTitle',"basetitle+' '+(loadedDashboard || currentView || '')",
                                    basetitle='!!Group by',
                                    currentView='^.grid.currViewAttrs.description',
                                    loadedDashboard='^.dashboardMeta.description')
            frame.data('.grid.showCounterCol',True)
            frame.dataRemote('.dashboardsMenu',self.thg_dashboardsMenu,cacheTime=5,table=table,
                                rootNodeId=rootNodeId,_fired='^.refreshDashboardsMenu')
            configuratorSlot = 'configuratorPalette' if configurable else '2'
            bar = frame.top.slotToolbar('5,ctitle,stackButtons,10,groupByModeSelector,counterCol,*,searchOn,count,viewsMenu,%s,chartjs,export,dashboardsMenu,5' %configuratorSlot,
                                        dashboardsMenu_linkedTo=linkedTo,
                                        stackButtons_stackNodeId=frameCode)
            bar.ctitle.div(title,color='#444',font_weight='bold')
            bar.counterCol.div().checkbox(value='^.grid.showCounterCol',label='!!Counter column',label_color='#444')
            frame.grid.dataController("""
            if(showCounterCol){
                structrow.setItem('_grp_count',null,{field:'_grp_count',name:'Cnt',width:'5em',group_aggr:'sum',dtype:'L'});
            }else{
                structrow.popNode('_grp_count');
            }
            """,structrow='=.struct.#0.#0',showCounterCol='^.showCounterCol',_if='structrow')
            frame.stackedView = self._thg_stackedView(gridstack,title=title,grid=frame.grid,frameCode=frameCode,linkedTo=linkedTo,table=table)
            frame.treeView = self._thg_treeview(sc,title=title,grid=frame.grid,treeRoot=treeRoot,linkedTo=linkedTo,tree_kwargs=tree_kwargs)
            frame.dataController("""
                grid.collectionStore().loadInvisible = always || genro.dom.isVisible(sc);
            """,output='^.output',groupMode='^.groupMode',always='=.always',
                grid=frame.grid.js_widget,sc=sc,_delay=1)



        gridId = frame.grid.attributes['nodeId']
        frame.dataController("""genro.grid_configurator.loadView(gridId, (currentView || favoriteView));
                                    """,
                                currentView="^.grid.currViewPath",
                                favoriteView='^.grid.favoriteViewPath',
                                gridId=gridId)
        self._thg_structMenuData(frame,table=table,linkedTo=linkedTo)
        if configurable:
            frame.viewConfigurator(table,queryLimit=False,toolbar=False)
        else:
            frame.grid.attributes['gridplugins'] = False
        self._thg_groupByStore(frame,table=table,where=where,condition=condition,linkedTo=linkedTo,
                                condition_kwargs=condition_kwargs,**store_kwargs)
        return frame

    
    def _thg_groupByStore(self,frame,table=None,where=None,linkedTo=None,
                            condition=None,condition_kwargs=None,**store_kwargs):
        frame.grid.attributes.setdefault('selfsubscribe_loadingData',
                                            "this.setRelativeData('.loadingData',$1.loading);if(this.attr.loadingHider!==false){this.setHiderLayer($1.loading,{message:'%s'});}" %self._th_waitingElement())
        store_kwargs.update(condition_kwargs)
        store_kwargs['_forcedReload'] = '^.reloadMain'
        frame.grid.selectionStore(table=table,where=where,selectmethod=self._thg_selectgroupby,
                                childname='store',struct='=.grid.struct',
                                groupByStore=True,liveUpdate=True if not linkedTo else 'NO',
                                _linkedTo=linkedTo,
                                _onCalling="""
                                if(!_linkedTo){
                                    return;
                                }
                                var originalAttr = genro.wdgById(_linkedTo+'_grid').collectionStore().storeNode.currentAttributes();
                                var runKwargs = objectUpdate({},originalAttr);
                                var storeKw = objectExtract(runKwargs,_excludeList);
                                if(storeKw._sections){
                                    th_sections_manager.onCalling(storeKw._sections,runKwargs);
                                }
                                objectUpdate(kwargs,runKwargs);
                                if(condition){
                                    kwargs.condition = kwargs.condition? kwargs.condition +' AND '+condition:condition;
                                }
                                """,
                                _excludeList="""columns,sortedBy,currentFilter,customOrderBy,row_count,hardQueryLimit,limit,liveUpdate,method,nodeId,selectionName,
                            selectmethod,sqlContextName,sum_columns,table,timeout,totalRowCount,userSets,_sections,
                            _onCalling,_onResult,applymethod,sum_columns,prevSelectedDict""",
                    condition=condition,**store_kwargs)

    


    def _thg_defaultstruct(self,struct):
        r=struct.view().rows()
        r.cell('_grp_count',name='Cnt',width='5em',group_aggr='sum',dtype='L',childname='_grp_count')

    @struct_method
    def thg_slotbar_groupByModeSelector(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        _forcedGroupMode = inattr.get('_forcedGroupMode')
        if _forcedGroupMode:
            pane.dataFormula('#ANCHOR.groupMode','groupMode',groupMode=_forcedGroupMode,_onBuilt=100)
        else:
            pane.multiButton(value='^#ANCHOR.groupMode',values='flatview:[!![en]Flat],stackedview:[!![en]Stacked]')

    
    def _thg_structMenuData(self,frame,table=None,linkedTo=None):
        q = Bag()
        if linkedTo:
            pyviews = self._th_hook('groupedStruct',mangler=linkedTo,asDict=True)
            for k,v in pyviews.items():
                prefix,name=k.split('_groupedStruct_')
                q.setItem(name,self._prepareGridStruct(v,table=table),caption=v.__doc__)
            frame.data('.grid.resource_structs',q)
        frame.dataRemote('.grid.structMenuBag',self.th_menuViews,pyviews=q.digest('#k,#a.caption'),currentView="^.grid.currViewPath",
                        table=table,th_root=frame.attributes['frameCode'],objtype='grpview',
                        favoriteViewPath='^.grid.favoriteViewPath',cacheTime=30)



    def _thg_stackedView(self,parentStack,title=None, grid=None,frameCode=None,linkedTo=None,table=None,**kwargs):
        frame = parentStack.bagGrid(frameCode='%s_stacked' %frameCode,title='!!Stacked',pageName='stackedview',
                                    datapath='.stacked',table=table,
                                    storepath='.store',addrow=False,delrow=False,
                                    datamode='attr')
        bar = frame.top.bar.replaceSlots('#','5,ctitle,stackButtons,10,groupByModeSelector,*,searchOn,export,5,dashboardsMenu',
                                        stackButtons_stackNodeId=frameCode,dashboardsMenu_linkedTo=linkedTo)
        bar.ctitle.div(title,color='#444',font_weight='bold')
        frame.dataController("""
            if(groupMode!='stackedview' && !linkedChart){
                return;    
            }
            var r = genro.groupth.getPivotGrid(flatStore,flatStruct);
            if(!r){
                SET .store = new gnr.GnrBag();
                return;
            }
            SET .grid.struct = r.struct;
            SET .store = r.store;
            SET #ANCHOR.changets.stackedview = changets_flatview;
        """,flatStore='=#ANCHOR.store',
            flatStruct='=#ANCHOR.grid.struct',
            groupMode='^#ANCHOR.groupMode',
            linkedChart='=.grid.linkedChart',
            changets_flatview ='^#ANCHOR.changets.flatview')
        return frame


    def _thg_treeview(self,parentStack,title=None, grid=None,treeRoot=None,linkedTo=None,tree_kwargs=None,**kwargs):
        frame = parentStack.framePane(title='Tree View',pageName='tree')
        bar = frame.top.slotToolbar('5,ctitle,parentStackButtons,10,groupByModeSelector,addTreeRoot,*,searchOn,dashboardsMenu,5',
                                    dashboardsMenu_linkedTo=linkedTo)
        bar.ctitle.div(title,color='#444',font_weight='bold')
        fb = bar.addTreeRoot.div(_class='iconbox tag').tooltipPane().formbuilder(cols=1,border_spacing='2px',color='#666')
        fb.textbox(value='^.treeRootName',lbl='!!Root',width='7em')
        bar.data('.treeRootName',treeRoot)
        pane = frame.center.contentPane()
        frame.dataController("""
            var nodeLabel = _node.label;
            var v = _node.getValue();
            var lastTs = v instanceof Date?v:null;
            if(output!='tree' || (lastTs && nodeLabel!=groupMode) ){
                return;
            }
            lastTs = groupMode=='stackedview'?changets_stackedview:changets_flatview;
            var treekw = objectExtract(_kwargs,'tree_*',true);
            if(changets_tree!=lastTs){
                var struct = flatStruct;
                var store = flatStore;
                if(groupMode=='stackedview'){
                    struct = stackedStruct;
                    store = stackedStore;
                }
                if(nodeLabel!='treeRootName'){
                    genro.groupth.buildGroupTree(pane,struct,treekw);
                }
                SET .treestore = genro.groupth.groupTreeData(store,struct,treeRoot,treekw);
            }
            """,
            pane=pane,
            storepath='.treestore',
            flatStruct='=.grid.struct',
            flatStore='=.store',
            stackedStruct = '=.stacked.grid.struct',
            stackedStore ='=.stacked.store',
            changets_tree='=.changets.tree',
            changets_flatview ='^.changets.flatview',
            changets_stackedview = '^.changets.stackedview',
            groupMode='^.groupMode',
            output='^.output',
            treeRoot='^.treeRootName',**tree_kwargs)
        return frame


    @public_method
    def _thg_selectgroupby(self,struct=None,groupLimit=None,groupOrderBy=None,**kwargs):
        columns_list = list()
        group_list = list()
        having_list = list()
        custom_order_by = list()
        if groupOrderBy:
            for v in groupOrderBy.values():
                field = v['field']
                if not field.startswith('@'):
                    field = '$%s' %field
                field = field if not v['group_aggr'] else '%s(%s)' %(v['group_aggr'],field)
                custom_order_by.append('%s %s' %(field,('asc' if v['sorting'] else 'desc')))
            custom_order_by = ' ,'.join(custom_order_by)
        def asName(field,group_aggr):
            return '%s_%s' %(field.replace('.','_').replace('@','_').replace('-','_'),
                    group_aggr.replace('.','_').replace('@','_').replace('-','_').replace(' ','_').lower())
        for v in struct['#0.#0'].digest('#a'):
            if v['field'] =='_grp_count' or v.get('calculated'):
                continue
            col = v.get('queryfield') or v['field']
            if not col.startswith('@'):
                col = '$%s' %col
            
            dtype = v.get('dtype')
            group_aggr =  v.get('group_aggr') 
            if dtype in ('N','L','I','F','R') and group_aggr is not False:
                group_aggr =  group_aggr or 'sum'
                col_asname = asName(v['field'],group_aggr)
                grouped_col = '%s(%s)' %(group_aggr,col)
                col = '%s AS %s' %(grouped_col,col_asname)
                having_chunk = list()

                if v.get('not_zero'):
                    having_chunk.append('(%s != 0)' %grouped_col)
                if v.get('min_value') is not None:
                    parname = '%s_min_value' %col_asname
                    kwargs[parname] = v['min_value']
                    having_chunk.append('%s>=:%s' %(grouped_col,parname))
                if v.get('max_value') is not None:
                    parname = '%s_max_value' %col_asname
                    kwargs[parname] = v['max_value']
                    having_chunk.append('%s<=:%s' %(grouped_col,parname))
                if len(having_chunk):
                    having_list.append(' AND '.join(having_chunk))
            else:
                if group_aggr:
                    if dtype in ('D','DH'):
                        col =  "to_char(%s,'%s')" %(col,group_aggr)
                        group_list.append(col)
                        col = '%s AS %s' %(col, asName(v['field'],group_aggr))
                    #if dtype in ('T','C','A'):
                else:
                    groupcol = col
                    if ' AS ' in col:
                        groupcol,asname = col.split(' AS ')
                    group_list.append(groupcol)
                    caption_field = v.get('caption_field')
                    if caption_field:
                        if not caption_field.startswith('@'):
                            caption_field = '$%s' %caption_field
                        group_list.append(caption_field)
                        columns_list.append(caption_field)
            columns_list.append(col)
        columns_list.append('count(*) AS _grp_count_sum')
        if not group_list:
            return False
        kwargs['columns'] = ','.join(columns_list)
        kwargs['group_by'] = ','.join(group_list)
        kwargs['order_by'] = custom_order_by or kwargs['group_by']
        if having_list:
            kwargs['having'] = ' OR '.join(having_list)
        kwargs['hardQueryLimit'] = False
        if groupLimit:
            kwargs['limit'] = groupLimit
        selection = self.app._default_getSelection(_aggregateRows=False,**kwargs)
        #_thgroup_pkey column 
        group_list_keys = [c.replace('@','_').replace('.','_').replace('$','_') for c in group_list]
        def cb(row):
            resdict = {}
            resdict['_thgroup_pkey'] = '|'.join([str(row.get(c) or '_') for c in group_list_keys])
            return resdict
        selection.apply(cb)

        
        return selection    




    @struct_method
    def thg_slotbar_dashboardsMenu(self,pane,linkedTo=None,**kwargs):
        if not (linkedTo and self.db.package('biz')):
            return pane.div()
        menu = pane.menudiv(tip='!!Advanced tools',
                            iconClass='iconbox menu_gray_svg',
                            storepath='#ANCHOR.dashboardsMenu',**kwargs)
    
    @public_method
    def thg_dashboardsMenu(self,currentDashboard=None,rootNodeId=None,table=None,**kwargs):
        result = Bag()
        result.rowchild(label='!!Save dashboard',
                        action="""this.attributeOwnerNode('_dashboardRoot').publish('saveDashboard');""")
        result.rowchild(label='!!Save dashboard as',
                        action="""this.attributeOwnerNode('_dashboardRoot').publish('saveDashboard',{saveAs:true});""")
        result.rowchild(label='!!Delete current dashboard',
                        action="""this.attributeOwnerNode('_dashboardRoot').publish('deleteCurrentDashboard');""")
        objtype = 'dash_groupby'
        flags='groupth|%s' %rootNodeId
        userobjects = self.db.table('adm.userobject').userObjectMenu(objtype=objtype,flags=flags,table=table)
        if len(userobjects)>0:
            loadAction = """this.attributeOwnerNode('_dashboardRoot').publish('loadDashboard',{pkey:$1.pkey});"""
            loadmenu = Bag()
            loadmenu.update(userobjects)
            result.setItem('r_%s' %len(result),loadmenu,label='!!Load dashboard',action=loadAction)
        return result

    @struct_method
    def thgp_linkedGroupByAnalyzer(self,view,**kwargs):
        linkedTo=view.attributes.get('frameCode')
        table = view.grid.attributes.get('table')
        frameCode = '%s_gp_analyzer' %linkedTo
        pane = view.grid_envelope.contentPane(region='bottom',height='300px',closable='close',margin='2px',splitter=True,
                                             border_top='1px solid #efefef')
        view.dataController("""
            var analyzerNode = genro.nodeById(analyzerId);
            if(currentSelectedPkeys && currentSelectedPkeys.length){
                analyzerNode.setRelativeData('.analyzer_condition', '$'+pkeyField+' IN :analyzed_pkeys');
                analyzerNode.setRelativeData('.analyzed_pkeys',currentSelectedPkeys);
            }else{
                analyzerNode.setRelativeData('.analyzer_condition',null);
                analyzerNode.setRelativeData('.analyzed_pkeys',null);
            }
        """,pkeyField='=.table?pkey',
            currentSelectedPkeys='^.grid.currentSelectedPkeys',
            analyzerId=frameCode,_delay=500)

        pane.groupByTableHandler(frameCode=frameCode,linkedTo=linkedTo,
                                    table=table,datapath='.analyzerPane',
                                    condition='=.analyzer_condition',
                                    condition_analyzed_pkeys='^.analyzed_pkeys')

