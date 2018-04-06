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
    js_requires = 'th/th_groupth'

    
    @extract_kwargs(condition=True)
    @struct_method
    def th_groupByTableHandler(self,pane,frameCode=None,title=None,table=None,linkedTo=None,
                                struct=None,where=None,viewResource=None,
                                condition=None,condition_kwargs=None,datapath=None,
                                treeRoot=None,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = table or inattr.get('table')
        tblobj = self.db.table(table)
        linkedNode = None
        if not (where or condition or condition_kwargs):
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
        sc = pane.stackContainer(datapath=datapath,_class='group_by_th',selectedPage='^.group_mode',**kwargs)  
        frame = sc.frameGrid(frameCode=frameCode,grid_onDroppedColumn="""
                                    if('RNLIF'.indexOf(data.dtype)<0){
                                        return;
                                    }else if (!data.group_aggr){
                                        data.cell_group_aggr = 'sum';
                                    }
                                    """,
                                grid_connect_onSetStructpath="""
                                            this.publish('changedStruct',{structBag:$1,kw:$2});
                                            """,
                                pageName='grid',
                                struct=struct,_newGrid=True,title='!!Grid View')
        frame.data('.grid.showCounterCol',True)
        bar = frame.top.slotToolbar('5,parentStackButtons,vtitle,counterCol,*,searchOn,viewsMenu,advancedTools,export,5')
        bar.vtitle.div(title,color='#444',font_weight='bold')
        bar.counterCol.div().checkbox(value='^.grid.showCounterCol',label='!!Counter column',label_color='#444')
        frame.grid.dataController("""
        if(showCounterCol){
            structrow.setItem('_grp_count',null,{field:'_grp_count',name:'Cnt',width:'5em',group_aggr:'sum',dtype:'L'});
        }else{
            structrow.popNode('_grp_count');
        }
        """,structrow='=.struct.#0.#0',showCounterCol='^.showCounterCol',_if='structrow')
        self._thg_treeview(sc.framePane(title='Tree View',pageName='tree'),title=title,grid=frame.grid,treeRoot=treeRoot)
        
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
       
        frame.viewConfigurator(table,queryLimit=False)
        frame.grid.attributes.setdefault('selfsubscribe_loadingData',"this.setRelativeData('.loadingData',$1.loading);if(this.attr.loadingHider!==false){this.setHiderLayer($1.loading,{message:'%s'});}" %self._th_waitingElement())

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
                            _onCalling,_onResult""",
                                condition=condition,**condition_kwargs)
    def _thg_defaultstruct(self,struct):
        r=struct.view().rows()
        r.cell('_grp_count',name='Cnt',width='5em',group_aggr='sum',dtype='L')

    
    def _thg_structMenuData(self,frame,table=None,linkedTo=None):
        q = Bag()
        if linkedTo:
            pyviews = self._th_hook('groupedStruct',mangler=linkedTo,asDict=True)
            for k,v in pyviews.items():
                prefix,name=k.split('_groupedStruct_')
                q.setItem(name,self._prepareGridStruct(v,table=table),caption=v.__doc__)
            frame.data('.grid.resource_structs',q)
        frame.dataRemote('.grid.structMenuBag',self.th_menuViews,pyviews=q.digest('#k,#a.caption'),currentView="=.grid.currViewPath",
                        table=table,th_root=frame.attributes['frameCode'],
                        favoriteViewPath='=.grid.favoriteViewPath',cacheTime=30)



    def _thg_treeview(self,frame,title=None, grid=None,treeRoot=None,**kwargs):
        bar = frame.top.slotToolbar('5,parentStackButtons,vtitle,addTreeRoot,*,searchOn,5')
        bar.vtitle.div(title,color='#444',font_weight='bold')
        fb = bar.addTreeRoot.div(_class='iconbox tag').tooltipPane().formbuilder(cols=1,border_spacing='2px',color='#666')
        fb.textbox(value='^.treeRootName',lbl='!!Root',width='7em')
        bar.data('.treeRootName',treeRoot)
        pane = frame.center.contentPane()
        frame.dataController("""
        genro.groupth.buildGroupTree(pane,struct);
        FIRE .refresh_tree_data;
        """,_delay=500,pane=pane,storepath='.treestore',
        _fired='^.rebuild_tree',
        struct='=.grid.struct',
        **{'subscribe_%s_changedStruct' %grid.attributes['nodeId']:True})
        
        frame.dataController("""

            SET .treestore = genro.groupth.groupTreeData(gridstore,struct,treeRoot);
        """,gridstore='^.store',_fired='^.refresh_tree_data',treeRoot='^.treeRootName',
        struct='=.grid.struct', _delay=1)
        frame.dataController("""
        grid.collectionStore().loadInvisible = (group_mode=='tree' && genro.dom.isVisible(pane));
        """,group_mode='^.group_mode',grid=grid.js_widget,pane=pane,_delay=1)

        
    @public_method
    def _thg_selectgroupby(self,struct=None,**kwargs):
        columns_list = list()
        group_list = list()
        def asName(field,group_aggr):
            return '%s_%s' %(field.replace('.','_').replace('@','_').replace('-','_'),
                    group_aggr.replace('.','_').replace('@','_').replace('-','_').replace(' ','_').lower())
        for v in struct['#0.#0'].digest('#a'):
            if v['field'] =='_grp_count':
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
