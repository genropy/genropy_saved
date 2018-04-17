# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari
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


from gnr.web.gnrbaseclasses import BaseDashboardItem

caption = 'Stats Grouped'
description = 'Stats Grouped'
item_parameters = [dict(value='^.table',lbl='Table',tag='dbselect',dbtable='adm.tblinfo',validate_notnull=True,hasDownArrow=True),
                    dict(value='^.userobject_id',lbl='Stat',dbtable='adm.userobject',tag='dbselect',validate_notnull=True,
                        condition='$tbl=:seltbl AND $objtype=:t',condition_t='dash_groupby',
                        condition_seltbl='=.table',hasDownArrow=True)]

class Main(BaseDashboardItem):
    """Choose table and saved stat"""
    item_name = 'Stats Grouped'

    def content(self,pane,workpath=None,table=None,userobject_id=None,storepath=None,itemRecord=None,**kwargs):
        self.page.mixinComponent('th/th:TableHandler')
        bc = pane.borderContainer()
        center = bc.contentPane(region='center',_class='hideInnerToolbars')
        frameCode = 'statgroup_%s_%s' %(table.replace('.','_'),self.page.getUuid())
        data,metadata = self.page.db.table('adm.userobject').loadUserObject(id=userobject_id)
        gh = center.groupByTableHandler(table=table,frameCode=frameCode,
                                    configurable=False,
                                    struct=data['groupByStruct'],
                                    where='=.where',
                                    store__fired='^.runItem',
                                    datapath=workpath)
        gh.data('.where',data['where'])
        center.dataController("""
            viewMode = viewMode || defaultGroupMode+'_'+defaultGroupMode;
            gh.publish('viewMode',viewMode);
        """,viewMode='^.conf.viewMode',gh=gh,
        defaultOutput= data['output'],
        defaultGroupMode = data['groupMode'],
        _fired='^%s.runItem' %workpath)

    def configuration(self,pane,table=None,userobject_id=None,workpath=None,itemRecord=None,**kwargs):
        fb = pane.formbuilder()
        fb.filteringSelect(value='^.viewMode',lbl='Mode',
                            values='flatview_grid:Flat grid,stackedview_grid:Stacked view,flatview_tree:Tree,stackedview_tree:Stacked tree')
        
