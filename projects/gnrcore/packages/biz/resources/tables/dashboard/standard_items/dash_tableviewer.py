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


from gnrpkg.biz.dashboard import BaseDashboardItem
from gnr.core.gnrbag import Bag


caption = 'Table view'
description = 'Table view'

class Main(BaseDashboardItem):
    title_template = '$title $whereParsFormatted'

    def content(self,pane,table=None,userobject_id=None,**kwargs):
        self.page.mixinComponent('th/th:TableHandler')
        bc = pane.borderContainer(datapath=self.workpath)
        center = bc.contentPane(region='center')
        
        selectionViewer = self._selectionViewer(center,table=table,
                                            userobject_id=userobject_id,
                                            datapath='.viewer')
        self.queryPars = selectionViewer.queryPars
        selectionViewer.dataController("""
            if(queryPars){
                queryPars.forEach(function(n){
                    where.setItem(n.attr.relpath,conf.getItem('wherepars_'+n.label));
                });
            }
            grid.collectionStore().loadData();
        """,conf='=%s.conf' %self.storepath,grid=selectionViewer.grid.js_widget,
            queryPars='=.query.queryPars',
            where='=.query.where',
            _fired='^%s.runItem' %self.workpath)
            
        pane.dataFormula('.whereParsFormatted',"wherePars?wherePars.getFormattedValue({joiner:' - '}):'-'",
                    wherePars='^.conf.wherePars')
        


    def configuration(self,pane,table=None,queryName=None,**kwargs):
        if not self.queryPars:
            return
        fb = pane.formbuilder(dbtable=table,
                            fld_validate_onAccept="SET %s.runRequired =true;" %self.workpath)
        for code,pars in self.queryPars.digest('#k,#a'):
            field = pars['field']
            rc = self.db.table(table).column(field).relatedColumn()
            wherepath = pars['relpath']
            if pars['op'] == 'equal' and rc is not None:
                fb.dbSelect(field,value='^.wherepars_%s' %code,lbl=pars['lbl'],
                            default_value=pars['dflt'],
                            dbtable=rc.table.fullname)
            else:
                fb.textbox(value='^.wherepars_%s' %code,
                            default_value=pars['dflt'],
                            lbl=pars['lbl'])

    def _selectionViewer(self,pane,table=None,userobject_id=None,fired=None,**kwargs):
        userobject_tbl = self.page.db.table('adm.userobject')
        tblobj = self.page.db.table(table)
        data,metadata = userobject_tbl.loadUserObject( id=userobject_id,
                                            objtype='query',
                                            tbl=table)
        customOrderBy = None
        limit = None
        queryPars = None
        limit = data['limit']
        viewName = data['currViewPath']
        customOrderBy = data['customOrderBy']
        joinConditions = data['joinConditions']
        queryPars = data.pop('queryPars')
        extraPars = data.pop('extraPars')
        where = data['where']
        struct = data['struct']
        frame = pane.frameGrid(struct=struct,_newGrid=True,**kwargs)
        frame.data('.query.limit',limit)
        frame.data('.query.where',where)
        frame.data('.query.extraPars',extraPars)
        frame.data('.query.queryPars',queryPars)
        frame.data('.query.customOrderBy',customOrderBy)
        frame.data('.query.joinConditions',joinConditions)
        frame.top.slotBar('*,vtitle,*',vtitle=metadata['description'])
        frame.queryPars = queryPars
        frame.grid.selectionStore(table=table,childname='store',where='=.query.where',
                                customOrderBy='=.query.customOrderBy',
                                joinConditions='=.query.joinConditions',
                                limit='=.query.limit',
                                _fired='^.run')
        return frame