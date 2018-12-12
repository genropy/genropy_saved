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
from gnr.core.gnrbag import Bag


caption = 'Group by chart'
description = 'Group by chart'


class Main(BaseDashboardItem):
    title_template = '$chart_title'

    def content(self,pane,linkedGrid=None,linkedItem=None,**kwargs):
        bc = pane.borderContainer(_workspace=True,_workspace_path='.chart_parameters')
        root = bc.contentPane(childname='chartroot',parentForm=False,region='center')
        bc.div(position='absolute',childname='dropArea',_class='chartDrop',dropCodes='gridcolumn',dropTarget=True,
                                    dropTypes='gridcolumn',
                                    dropTargetCb="""
                                    if(dropInfo.sourceNodeId!='%s'){
                                        return false;
                                    }
                                    return dropInfo;                                    
                                    """ %linkedGrid,
                                    onDrop_gridcolumn="""
                                    var cell = genro.wdgById(data.gridId).getCell(data.column);
                                    var cellcap = cell.tree_name? cell.tree_name.replace('<br/>',' '):cell.original_name;
                                    genro.nodeById('cp_%s').gnrwdg.addDataset({field:cell.field,
                                                                                caption:cellcap});
                                    """ %self.itemIdentifier)
        pane.dataController("""
        pane.getValue().popNode('chartNode');
        genro.pluginCommand({plugin:'chartjs'});
        var that = this;

        var onClick = function(event,elements){
            if(!event.shiftKey){
                return;
            }
            var cp = genro.nodeById('cp_'+itemIdentifier);
            var chart = genro.nodeById(itemIdentifier).externalWidget;
            var elem = chart.getElementAtEvent(event);
            if(!elem){
                return;
            }
            var datasetIndex = elem[0]._datasetIndex;
            var rowDataNode = genro.getDataNode(cp.absDatapath('#WORKSPACE.datasets.#'+datasetIndex));
            var rowpath = cp.absDatapath('#WORKSPACE.datasets.'+rowDataNode.label);
            genro.dlg.quickTooltipPane({datapath:rowpath,domNode:event.target,modal:true},
                                            function(pane,kw){cp.gnrwdg.datasetForm(pane,kw)},{rowDataNode:rowDataNode});

        };

        this.watch('waitingGrid',function(){
            return genro.chartjs && genro.wdgById(connectedTo);
        },function(){
            var gridnode = genro.nodeById(connectedTo);
            var cp = pane._('chartPane','chartNode',{connectedTo:connectedTo,nodeId:itemIdentifier,
                                _workspace:false,configurator:{palette:itemIdentifier+'_parameters',userObject:false},
                                filterpath:workpath+'.linkedRows',onClick:onClick});
            gridnode.setRelativeData('.linkedChart',true);
        });
        """,connectedTo='=.parameters.linkedGrid',_onBuilt=True,pane=root,itemIdentifier=self.itemIdentifier,workpath=self.workpath)
        pane.dataController("""
            genro.nodeById(itemIdentifier).externalWidget.gnr_updateChart();
        """,_fired='^.configuration_changed',datapath=self.workpath,itemIdentifier=self.itemIdentifier,_delay=20)
        pane.dataFormula('.chart_title',"""(caption_template || title).replace('#',linkedTitle);""",
                        linkedTitle='^%s.%s.current_title' %(self.workspaces,linkedItem),
                        caption_template='^.conf.caption_template',title='^.title',
                        _onBuilt=True)
        
        #pane.chartPane(connectedTo='=.parameters.linkedGrid',configurator=True)

    def configuration(self,pane,linkedStore=None,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.caption_template',lbl='!!Caption')
        chartconf = '%s.chart_parameters' %self.storepath
        fb.filteringSelect(value='^.chartType',lbl='!!Chart type',
                    values='bar,line,pie,doughnut',datapath=chartconf)
        fb.checkbox(value='^.options.maintainAspectRatio',label='!!Aspect ratio',datapath=chartconf)
        fb.callbackSelect(value='^.captionField',lbl='!!Chart caption',datapath=chartconf,
                            callback="""
                            function(kw){
                                var cp = genro.nodeById('cp_%s');
                                var currentValue = this.sourceNode.getRelativeData('.captionField');
                                var currentCaption = this.sourceNode.getRelativeData('.captionField?_displayedValue');
                                return (cp && cp.gnrwdg)? cp.gnrwdg.captionGetter(kw):{data:[{_pkey:currentValue,caption:currentCaption}]} 
                            }
                            """ %self.itemIdentifier,hasDownArrow=True)
