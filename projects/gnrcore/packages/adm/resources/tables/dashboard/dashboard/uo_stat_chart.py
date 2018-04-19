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


caption = 'Group by chart'
description = 'Group by chart'


class Main(BaseDashboardItem):
    title_template = '$chart_title'


    def content(self,pane,linkedGrid=None,editMode=None,itemIdentifier=None,itemRecord=None,linkedItem=None,workspaces=None,**kwargs):
        root = pane.contentPane(_workspace=True,_workspace_path='.chart_parameters',childname='chartroot',parentForm=False)
        pane.dataController("""
        pane.getValue().popNode('chartNode');
        genro.pluginCommand({plugin:'chartjs'});
        this.watch('waitingGrid',function(){
            return genro.chartjs && genro.wdgById(connectedTo);
        },function(){
            var gridnode = genro.nodeById(connectedTo);
            pane._('chartPane','chartNode',{connectedTo:connectedTo,_workspace:false,
                                configurator:{palette:itemIdentifier+'_parameters',
                                userObject:false}});
            gridnode.setRelativeData('.linkedChart',true);
        });
        
        """,connectedTo='=.parameters.linkedGrid',_onBuilt=True,pane=root,itemIdentifier=itemIdentifier)
        pane.dataFormula('.chart_title',"""(caption_template || title).replace('#',linkedTitle);""",
                        linkedTitle='^%s.%s.current_title' %(workspaces,linkedItem),
                        caption_template='^.conf.caption_template',title='^.title',
                        _onBuilt=True)
        
        #pane.chartPane(connectedTo='=.parameters.linkedGrid',configurator=True)

    def configuration(self,pane,linkedStore=None,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.caption_template',lbl='!!Caption')

