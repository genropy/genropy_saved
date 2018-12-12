# -*- coding: utf-8 -*-
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

caption = 'Stat view'
description = 'Stat view'
objtype = 'dash_pandas'

class Main(BaseDashboardItem):
    """Scegli table e query per visualizzare il risultato"""
    item_name = 'Stat view'

    def content(self,pane,table=None,statName=None,**kwargs):
        self.page.mixinComponent('th/th_stats:PivotTableViewer')
        bc = pane.borderContainer(datapath=self.workpath)
        userobject_tbl = self.db.table('adm.userobject')
        viewer = bc.contentPane(region='center').pivotTableViewer(table=table,
                                                                statIdentifier=statName,
                                                                _parschanged='^%s.configuration_changed' %self.workpath,
                                                                datapath='.viewer')
        self.queryPars = viewer.queryPars

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