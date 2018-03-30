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
    @extract_kwargs(condition=True)
    @struct_method
    def th_groupByTableHandler(self,pane,frameCode=None,title=None,table=None,linkedTo=None,struct=None,where=None,viewResource=None,
                                condition=None,condition_kwargs=None,datapath=None,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = table or inattr.get('table')
        frameCode = frameCode or 'thg_%s' %table.replace('.','_')
        datapath = datapath or '.%s' %frameCode
        linkedNode = None
        if not (where or condition or condition_kwargs):
            linkedTo = linkedTo or inattr.get('frameCode')
            if not linkedTo:
                raise self.exception('generic',msg='Missing condition or where in groupByTableHandler')
            linkedNode = self.pageSource().findNodeByAttr('frameCode',linkedTo)
            if not linkedNode:
                raise self.exception('generic',msg='Missing linked tableHandler in groupByTableHandler')
            if not struct:
                struct = self._th_hook('groupedStruct',mangler=linkedTo)
        frame = pane.frameGrid(frameCode=frameCode,grid_onDroppedColumn="""
                                    if('RNLIF'.indexOf(data.dtype)<0){
                                        return;
                                    }else if (!data.group_aggr){
                                        data.cell_group_aggr = 'sum';
                                    }
                                    """,
                                    grid_configurable=True,
                                struct=struct,_newGrid=True,
                                grid_title='!!Grid',
                                _class='group_by_th',
                                datapath=datapath,**kwargs)
        bar = frame.top.slotToolbar('5,vtitle,*,searchOn,viewsMenu,export,10,stackButtons,5')
        bar.vtitle.div(title or '!!Grouped view',color='#444',font_weight='bold')
        self._thg_treeview(frame.contentPane(title='Tree'))
        
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
        frame.dataRemote('.grid.structMenuBag',self.th_menuViews,currentView="=.grid.currViewPath",
                        table=table,th_root=frameCode,favoriteViewPath='=.grid.favoriteViewPath',
                        cacheTime=30)
        frame.grid.viewConfigurator(table,queryLimit=False)
        frame.grid.selectionStore(table=table,where=where,selectmethod=self.th_selectgroupby,
                                childname='store',struct='=.grid.struct',
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
                                _excludeList="""columns,currentFilter,customOrderBy,hardQueryLimit,limit,liveUpdate,method,nodeId,selectionName,
                            selectmethod,sqlContextName,sum_columns,table,timeout,totalRowCount,userSets,_sections,
                            _onCalling,_onResult""",
                                condition=condition,**condition_kwargs)
    def _thg_treeview(self,pane,**kwargs):
        pass
        
    
    @public_method
    def th_selectgroupby(self,struct=None,**kwargs):
        columns_list = list()
        group_list = list()
        for v in struct['#0.#0'].digest('#a'):
            col = v['field']
            if not col.startswith('@'):
                col = '$%s' %col
            dtype = v.get('dtype')
            if dtype in ('N','L','I','F','R') and v.get('group_aggr') is not False:
                group_aggr =  v.get('group_aggr') or 'sum'
                col = '%s(%s) AS %s' %(group_aggr,col, '%s_%s' %(v['field'].replace('.','_'),group_aggr))
            else:
                group_list.append(col)
                caption_field = v.get('caption_field')
                if caption_field:
                    if not caption_field.startswith('@'):
                        caption_field = '$%s' %caption_field
                    group_list.append(caption_field)
                    columns_list.append(caption_field)
            columns_list.append(col)
        kwargs['columns'] = ','.join(columns_list)
        kwargs['group_by'] = ','.join(group_list)
        return self.app._default_getSelection(**kwargs)
