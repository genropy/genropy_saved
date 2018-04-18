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
    title_template = '$title $whereParsFormatted'

    def content(self,pane,workpath=None,table=None,userobject_id=None,storepath=None,itemRecord=None,**kwargs):
        self.page.mixinComponent('th/th:TableHandler')
        bc = pane.borderContainer()
        center = bc.contentPane(region='center',_class='hideInnerToolbars')
        frameCode = itemRecord['id']
        data,metadata = self.page.db.table('adm.userobject').loadUserObject(id=userobject_id)
        frame = center.groupByTableHandler(table=table,frameCode=frameCode,
                                    configurable=False,
                                    struct=data['groupByStruct'],
                                    where='=.query.where',
                                    store__fired='^.runStore',
                                    datapath=workpath)
        frame.dataController("""
            if(queryPars){
                queryPars.forEach(function(n){
                    where.setItem(n.attr.relpath,wherePars.getItem(n.label));
                });
            }
            FIRE .runStore;
        """,wherePars='=%s.conf.wherePars' %storepath,
            queryPars='=.query.queryPars',
            where='=.query.where',
            _fired='^%s.runItem' %workpath)
        bc.dataFormula('.whereParsFormatted',"wherePars?wherePars.getFormattedValue({joiner:' - '}):'-'",
                    wherePars='^.conf.wherePars')

        bc.dataController("""
        if(output=='tree'){
            SET .chart_gridId=false;
        }else if(groupMode=='stacked'){
            SET .chart_gridId=frameCode+'_stacked_grid';
        }else{
            SET .chart_gridId=frameCode+'_grid';;
        }
        """,
            output='^.output',groupMode='^.groupMode',frameCode=frameCode,
            datapath=workpath)
        


        self.queryPars = data['queryPars']
        frame.data('.query.where',data['where'])
        frame.data('.query.queryPars',data['queryPars'])

        center.dataController("""
            viewMode = viewMode || defaultGroupMode+'_'+defaultOutput;
            genro.nodeById(frameCode).publish('viewMode',viewMode);
        """,viewMode='^.conf.viewMode',
        defaultOutput= data['output'],frameCode=frameCode,
        defaultGroupMode = data['groupMode'],
        _fired='^%s.runItem' %workpath)


    def configuration(self,pane,table=None,userobject_id=None,workpath=None,itemRecord=None,**kwargs):
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').div(padding='10px').formbuilder()
        fb.filteringSelect(value='^.viewMode',lbl='Mode',
                            values='flatview_grid:Flat grid,stackedview_grid:Stacked view,flatview_tree:Tree,stackedview_tree:Stacked tree')
        
        if not self.queryPars:
            center = bc.contentPane(region='center')
            return
        center = bc.roundedGroup(title='!!Query parameters',region='center')
        fb = center.div(padding='8px').formbuilder(dbtable=table,datapath='.wherePars',
                            fld_validate_onAccept="SET %s.runRequired =true;" %workpath)
        for code,pars in self.queryPars.digest('#k,#a'):
            field = pars['field']
            rc = self.db.table(table).column(field).relatedColumn()
            wherepath = pars['relpath']
            if pars['op'] == 'equal' and rc is not None:
                fb.dbSelect(field,value='^.%s' %code,lbl=pars['lbl'],
                            default_value=pars['dflt'],
                            dbtable=rc.table.fullname)
            else:
                fb.textbox(value='^.%s' %code,
                            default_value=pars['dflt'],
                            lbl=pars['lbl'])
