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

caption = 'Table view'
description = 'Table view'
item_parameters = [dict(value='^.table',lbl='Table'),
                  dict(value='^.queryName',lbl='Query name')]

class Main(BaseDashboardItem):
    """Scegli table e query per visualizzare il risultato"""
    item_name = 'Table view'

    def content(self,pane,workpath=None,table=None,queryName=None,**kwargs):
        self.page.mixinComponent('th/th:TableHandler')

        bc = pane.borderContainer(datapath=workpath)
        selectionViewer = bc.contentPane(region='center'
                ).selectionViewer(table=table,queryName=queryName,datapath='.viewer',
                                    store__parschanged='^%s.configuration_changed' %workpath,
                                    store__onBuilt=True)
        self.queryPars = selectionViewer.queryPars

 

    def configuration(self,pane,table=None,queryName=None,workpath=None,**kwargs):
        if not self.queryPars:
            return
        fb = pane.formbuilder(dbtable=table,datapath='%s.viewer.query.where' %workpath)
        for pars in self.queryPars.digest('#a'):
            field = pars['field']
            rc = self.db.table(table).column(field).relatedColumn()
            if pars['op'] == 'equal' and rc is not None:
                fb.dbSelect(field,value='^.%s' %pars['relpath'],lbl=pars['lbl'],
                            dbtable=rc.table.fullname)
            else:
                fb.textbox(value='^.%s' %pars['relpath'],lbl=pars['lbl'])
