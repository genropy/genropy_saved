# -*- coding: UTF-8 -*-
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

    
    @extract_kwargs(condition=True,store=True)
    @struct_method
    def th_groupByTableHandler(self,pane,frameCode=None,title=None,table=None,linkedTo=None,
                                struct=None,where=None,viewResource=None,
                                condition=None,condition_kwargs=None,store_kwargs=None,datapath=None,
                                treeRoot=None,configurable=True,dashboardIdentifier=None,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = table or inattr.get('table')
        tblobj = self.db.table(table)
        linkedNode = None
        if not (dashboardIdentifier or where or condition or condition_kwargs):
            linkedTo = linkedTo or inattr.get('frameCode')
            frameCode = frameCode or '%s_groupedView' %linkedTo 
            if not linkedTo:
                raise self.exception('generic',msg='Missing condition or where in groupByTableHandler')
            linkedNode = self.pageSource().findNodeByAttr('frameCode',linkedTo)
            if not linkedNode:
                raise self.exception('generic',msg='Missing linked tableHandler in groupByTableHandler')
            if not struct:
                struct = self._th_hook('groupedStruct',mangler=linkedTo,defaultCb=self._thg_defaultstruct)
        frameCode = frameCode or 'thg_%s' %table.replace('.','_')
        datapath = datapath or '.%s' %frameCode
        rootNodeId = frameCode
        sc = pane.stackContainer(datapath=datapath,_class='group_by_th',selectedPage='^.output',_anchor=True,
                                nodeId=rootNodeId,
                                _linkedTo = linkedTo,table=table,
                                selfsubscribe_viewMode="""
                                    var viewMode = $1.split('_');
                                    SET .groupMode = viewMode[0];
                                    SET .output = viewMode[1];
                                """,
                                selfsubscribe_saveDashboard="genro.groupth.saveAsDashboard(this,$1);",
                                selfsubscribe_loadDashboard="genro.groupth.loadDashboard(this,$1)",
                                _dashboardRoot=True,**kwargs)  
        gridstack = sc.stackContainer(pageName='grid',title='!!Grid View',selectedPage='^.groupMode')
        

        #gridstack.dataFormula('.currentTitle','',defaultTitle='!!Group by')
        frame = gridstack.frameGrid(frameCode=frameCode,grid_onDroppedColumn="""
                                    genro.groupth.addColumnCb(this,{data:data, column:column,fieldcellattr:fieldcellattr,treeNode:treeNode});
                                    """,
                                struct=struct or self._thg_defaultstruct,_newGrid=True,pageName='flatview',title='!!Flat')
        
        frame.dataFormula('.changets.flatview','new Date();',store='^.store',struct='^.grid.struct',
                            _delay=1)
        if dashboardIdentifier:
            frame.dataController("root.publish('loadDashboard',{pkey:dashboardIdentifier});",root=sc,
                                dashboardIdentifier=dashboardIdentifier,_onBuilt=1)


        frame.data('.grid.showCounterCol',True)
        frame.dataFormula('.currentTitle',"currentView?basetitle + ': '+currentView:basetitle",
                                basetitle='!!Gruop by',
                                currentView='^.grid.currViewAttrs.description')
        frame.dataRemote('.advancedOptions',self.thg_advancedOptions,cacheTime=5,table=table,
                            rootNodeId=rootNodeId,_fired='^.refreshAdvancedOptionsdMenu')
        configuratorSlot = 'configuratorPalette' if configurable else '2'
        bar = frame.top.slotToolbar('5,ctitle,stackButtons,10,groupByModeSelector,counterCol,*,searchOn,viewsMenu,%s,chartjs,export,advancedOptions,5' %configuratorSlot,
                                    advancedOptions_linkedTo=linkedTo,
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
        
        self._thg_stackedView(gridstack,title=title,grid=frame.grid,frameCode=frameCode,linkedTo=linkedTo)

        self._thg_treeview(sc,title=title,grid=frame.grid,treeRoot=treeRoot,linkedTo=linkedTo)
        

        frame.dataController("""
            grid.collectionStore().loadInvisible = genro.dom.isVisible(sc);
        """,output='^.output',groupMode='^.groupMode',
            grid=frame.grid.js_widget,sc=sc,_delay=1)

        if linkedNode:
            linkedNode.value.dataController("""
            groupbygrid.collectionStore().loadData();""",
            _runQuery='^.runQueryDo',_sections_changed='^.sections_changed',
            groupbygrid=frame.grid.js_widget,linkedTo=linkedTo,_delay=200)

        gridId = frame.grid.attributes['nodeId']
        frame.dataController("""genro.grid_configurator.loadView(gridId, (currentView || favoriteView));
                                """,
                            currentView="^.grid.currViewPath",
                            favoriteView='^.grid.favoriteViewPath',
                            gridId=gridId)
        self._thg_structMenuData(frame,table=table,linkedTo=linkedTo)
        if configurable:
            frame.viewConfigurator(table,queryLimit=False)
        else:
            frame.grid.attributes['gridplugins'] = False
        frame.grid.attributes.setdefault('selfsubscribe_loadingData',"this.setRelativeData('.loadingData',$1.loading);if(this.attr.loadingHider!==false){this.setHiderLayer($1.loading,{message:'%s'});}" %self._th_waitingElement())
        store_kwargs.update(condition_kwargs)
        store_kwargs['_forcedReload'] = '^.reloadMain'
        frame.grid.selectionStore(table=table,where=where,selectmethod=self._thg_selectgroupby,
                                childname='store',struct='=.grid.struct',
                                groupByStore=True,
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
                                """,
                                _excludeList="""columns,sortedBy,currentFilter,customOrderBy,row_count,hardQueryLimit,limit,liveUpdate,method,nodeId,selectionName,
                            selectmethod,sqlContextName,sum_columns,table,timeout,totalRowCount,userSets,_sections,
                            _onCalling,_onResult,applymethod,sum_columns""",
                                condition=condition,**store_kwargs)
        return frame


    def _thg_defaultstruct(self,struct):
        r=struct.view().rows()
        r.cell('_grp_count',name='Cnt',width='5em',group_aggr='sum',dtype='L',childname='_grp_count')

    @struct_method
    def thg_slotbar_groupByModeSelector(self,pane,**kwargs):
        pane.multiButton(value='^#ANCHOR.groupMode',values='flatview:[!![en]Flat],stackedview:[!![en]Stacked]')

    
    def _thg_structMenuData(self,frame,table=None,linkedTo=None):
        q = Bag()
        if linkedTo:
            pyviews = self._th_hook('groupedStruct',mangler=linkedTo,asDict=True)
            for k,v in pyviews.items():
                prefix,name=k.split('_groupedStruct_')
                q.setItem(name,self._prepareGridStruct(v,table=table),caption=v.__doc__)
            frame.data('.grid.resource_structs',q)
        frame.dataRemote('.grid.structMenuBag',self.th_menuViews,pyviews=q.digest('#k,#a.caption'),currentView="=.grid.currViewPath",
                        table=table,th_root=frame.attributes['frameCode'],objtype='grpview',
                        favoriteViewPath='=.grid.favoriteViewPath',cacheTime=30)



    def _thg_stackedView(self,parentStack,title=None, grid=None,frameCode=None,linkedTo=None,**kwargs):
        frame = parentStack.bagGrid(frameCode='%s_stacked' %frameCode,title='!!Stacked',pageName='stackedview',
                                    datapath='.stacked',
                                    storepath='.store',addrow=False,delrow=False,
                                    datamode='attr')
        bar = frame.top.bar.replaceSlots('#','5,ctitle,stackButtons,10,groupByModeSelector,*,searchOn,export,5,advancedOptions',
                                        stackButtons_stackNodeId=frameCode,advancedOptions_linkedTo=linkedTo)
        bar.ctitle.div(title,color='#444',font_weight='bold')
        frame.dataController("""
            if(groupMode!='stackedview'){
                return;    
            }
            var r = genro.groupth.getPivotGrid(flatStore,flatStruct);
            if(!r){
                return;
            }
            SET .grid.struct = r.struct;
            SET .store = r.store;
            SET #ANCHOR.changets.stackedview = changets_flatview;
        """,flatStore='=#ANCHOR.store',
            flatStruct='=#ANCHOR.grid.struct',
            groupMode='^#ANCHOR.groupMode',
            changets_flatview ='^#ANCHOR.changets.flatview')
        return frame


    def _thg_treeview(self,parentStack,title=None, grid=None,treeRoot=None,linkedTo=None,**kwargs):
        frame = parentStack.framePane(title='Tree View',pageName='tree')
        bar = frame.top.slotToolbar('5,ctitle,parentStackButtons,10,groupByModeSelector,addTreeRoot,*,searchOn,advancedOptions,5',
                                    advancedOptions_linkedTo=linkedTo)
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
            if(changets_tree!=lastTs){
                var struct = flatStruct;
                var store = flatStore;
                if(groupMode=='stackedview'){
                    struct = stackedStruct;
                    store = stackedStore;
                }
                if(nodeLabel!='treeRootName'){
                    genro.groupth.buildGroupTree(pane,struct);
                }
                SET .treestore = genro.groupth.groupTreeData(store,struct,treeRoot);
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
            treeRoot='^.treeRootName')
        return frame
        
    @public_method
    def _thg_selectgroupby(self,struct=None,**kwargs):
        columns_list = list()
        group_list = list()
        def asName(field,group_aggr):
            return '%s_%s' %(field.replace('.','_').replace('@','_').replace('-','_'),
                    group_aggr.replace('.','_').replace('@','_').replace('-','_').replace(' ','_').lower())
        for v in struct['#0.#0'].digest('#a'):
            if v['field'] =='_grp_count' or v.get('calculated'):
                continue
            col = v['field']
            if not col.startswith('@'):
                col = '$%s' %col
            dtype = v.get('dtype')
            group_aggr =  v.get('group_aggr')
            
            if dtype in ('N','L','I','F','R') and group_aggr is not False:
                group_aggr =  group_aggr or 'sum'
                col = '%s(%s) AS %s' %(group_aggr,col, asName(v['field'],group_aggr))
            else:
                if group_aggr:
                    if dtype in ('D','DH'):
                        col =  "to_char(%s,'%s')" %(col,group_aggr)
                        group_list.append(col)
                        col = '%s AS %s' %(col, asName(v['field'],group_aggr))
                    #if dtype in ('T','C','A'):
                else:
                    group_list.append(col)
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
        kwargs['order_by'] = kwargs['group_by']
        return self.app._default_getSelection(**kwargs)

    @struct_method
    def thg_slotbar_advancedOptions(self,pane,linkedTo=None,**kwargs):
        if not linkedTo:
            return pane.div()
        menu = pane.menudiv(tip='!!Advanced tools',
                            iconClass='iconbox menu_gray_svg',
                            storepath='#ANCHOR.advancedOptions',**kwargs)
    
    @public_method
    def thg_advancedOptions(self,currentDashboard=None,rootNodeId=None,table=None,**kwargs):
        result = Bag()
        result.rowchild(label='!!Save dashboard',
                        action="""this.attributeOwnerNode('_dashboardRoot').publish('saveDashboard');""")
        result.rowchild(label='!!Save dashboard as',
                        action="""this.attributeOwnerNode('_dashboardRoot').publish('saveDashboard',{saveAs:true});""")
        objtype = 'dash_groupby'
        flags='groupth|%s' %rootNodeId
        userobjects = self.db.table('adm.userobject').userObjectMenu(objtype=objtype,flags=flags,table=table)
        if len(userobjects)>0:
            loadAction = """this.attributeOwnerNode('_dashboardRoot').publish('loadDashboard',{pkey:$1.pkey});"""
            loadmenu = Bag()
            loadmenu.update(userobjects)
            result.setItem('r_%s' %len(result),loadmenu,label='!!Load dashboard',action=loadAction)
        return result
