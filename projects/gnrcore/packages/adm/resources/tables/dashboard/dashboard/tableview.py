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
from gnr.core.gnrbag import Bag


caption = 'Table view'
description = 'Table view'
item_parameters = [dict(value='^.table',lbl='Table',tag='dbselect',dbtable='adm.tblinfo',hasDownArrow=True),
                   dict(value='^.query_id',lbl='Query',dbtable='adm.userobject',tag='dbselect',
                        condition='$tbl=:seltbl AND $objtype=:t',condition_t='query',condition_seltbl='=.table',objtype='query',hasDownArrow=True),
                    dict(value='^.view_id',lbl='View',dbtable='adm.userobject',tag='dbselect',
                        condition='$tbl=:seltbl AND $objtype=:t',condition_t='view',condition_seltbl='=.table',objtype='query',hasDownArrow=True)]

class Main(BaseDashboardItem):
    item_name = 'Table view'

    def content(self,pane,workpath=None,table=None,query_id=None,view_id=None,storepath=None,**kwargs):
        self.page.mixinComponent('th/th:TableHandler')
        bc = pane.borderContainer(datapath=workpath)
        center = bc.contentPane(region='center')
        selectionViewer = self._selectionViewer(center,table=table,query_id=query_id,view_id=view_id,datapath='.viewer')
        self.queryPars = selectionViewer.queryPars
        selectionViewer.dataController("""
            if(queryPars){
                queryPars.forEach(function(n){
                    where.setItem(n.attr.relpath,wherePars.getItem(n.label));
                });
            }
            grid.collectionStore().loadData();
        """,wherePars='=%s.conf.wherePars' %storepath,grid=selectionViewer.grid.js_widget,
            queryPars='=.query.queryPars',
            where='=.query.where',
            _fired='^%s.runItem' %workpath)
        


    def configuration(self,pane,table=None,queryName=None,workpath=None,**kwargs):
        if not self.queryPars:
            return
        fb = pane.formbuilder(dbtable=table,datapath='.wherePars',
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

    def _selectionViewer(self,pane,table=None,query_id=None,
                            view_id=None,fired=None,**kwargs):
        userobject_tbl = self.page.db.table('adm.userobject')
        where = None
        customOrderBy = None
        queryPars = None
        extraPars = None
        limit = None
        struct = None
        tblobj = self.page.db.table(table)
        viewName = None
        metadata = Bag()
        def defaultstruct(struct):
            r = struct.view().rows()
            r.fieldcell(tblobj.attributes['caption_field'], name=tblobj.name_long, width='100%')

        if query_id:
            where,metadata = userobject_tbl.loadUserObject( id=query_id,
                                                objtype='query',
                                                tbl=table)
            customOrderBy = None
            limit = None
            queryPars = None
            if where['where']:
                limit = where['queryLimit']
                viewName = where['currViewPath']
                customOrderBy = where['customOrderBy']
                queryPars = where.pop('queryPars')
                extraPars = where.pop('extraPars')
                where = where['where']
        if view_id or viewName:
            userobject_tbl = self.db.table('adm.userobject')
            struct = userobject_tbl.loadUserObject(code=viewName, objtype='view', 
                                                    id=view_id,
                                                    tbl=table)[0]
        if struct is None:
            struct = defaultstruct    
        frame = pane.frameGrid(struct=struct,_newGrid=True,**kwargs)
        frame.data('.query.limit',limit)
        frame.data('.query.where',where)
        frame.data('.query.extraPars',extraPars)
        frame.data('.query.queryPars',queryPars)
        frame.data('.query.customOrderBy',customOrderBy)
        frame.top.slotBar('*,vtitle,*',vtitle=metadata['description'])
        frame.queryPars = queryPars
        frame.grid.selectionStore(table=table,childname='store',where='=.query.where',
                                customOrderBy='=.query.customOrderBy',
                                limit='=.query.limit',
                                _fired='^.run')
        return frame