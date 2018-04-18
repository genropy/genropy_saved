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


caption = 'Linked chart'
description = 'Linked chart'
item_parameters = [dict(value='^.linkedGrid',lbl='Linked store',
                        tag='callbackSelect',callback="""function(kw){
                            return genro.dashboards.availableChartGrid(kw);
                        }""",hasDownArrow=True)]

class Main(BaseDashboardItem):

    def content(self,pane,linkedGrid=None,editMode=None,**kwargs):
        pane.chartPane(connectedTo=linkedGrid,configurator=True)

    def configuration(self,pane,linkedStore=None,**kwargs):
        pass
