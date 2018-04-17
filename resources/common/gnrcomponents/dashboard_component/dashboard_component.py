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


from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag


class DashboardItem(BaseComponent):
    css_requires='gnrcomponents/dashboard_component/dashboard_component'
    js_requires='gnrcomponents/dashboard_component/dashboard_component'

    @struct_method
    def di_dashboardItem(self,parent,table=None,itemName=None,**kwargs):
        parent.remote(self.di_buildRemoteItem,table=table,itemName=itemName,**kwargs)
    
    @public_method
    def di_buildRemoteItem(self,pane=None,table=None,itemName=None,itemRecord=None,**kwargs):
        table = table or itemRecord['table']
        resource = itemName or itemRecord['resource']
        itemClass = self.loadTableScript(table=table,respath='dashboard/%s' %resource)
        itemClass(pane.contentPane(childname='remoteItem'),title=itemRecord['title'],parameters=itemRecord['parameters'],itemRecord=itemRecord,**kwargs)

class DashboardGallery(BaseComponent):
    css_requires='gnrcomponents/dashboard_component/dashboard_component'

    js_requires='gnrcomponents/dashboard_component/dashboard_component'
    py_requires='gnrcomponents/dashboard_component/dashboard_component:DashboardItem'

    @struct_method
    def di_dashboardGallery(self,parent,pkg=None,code=None,datapath=None,**kwargs):
        datapath =datapath or 'dashboard_%s_%s' %(pkg,code)
        bc = parent.borderContainer(_anchor=True,datapath=datapath,**kwargs)
        bc.dataRecord('.dashboard_record','adm.dashboard',pkgid=pkg,code=code,_onBuilt=True)
        bc.dashboardViewer(storepath='.dashboard_record.data',region='center')

    @struct_method
    def di_itemsViewer(self,parent,storepath=None,datapath=None,**kwargs):
        parent.bagGrid(storepath=storepath,datapath=datapath,struct=self._di_itemsStruct,**kwargs)

    def _di_itemsStruct(self,struct):
        r=struct.view().rows()
        r.cell('id',name='Id',width='8em')
        r.cell('table',name='Item table',width='8em')
        r.cell('resource',name='Resource',width='10em')
        r.cell('title',name='Title',width='12em')
        r.cell('parameters',name='Parameters',width='20em',
                _customGetter="""function(row){return row['parameters']?row['parameters'].getFormattedValue():'-';}""")

        r.cell('conf',name='Configuration',width='20em',
                _customGetter="""function(row){return row['conf']?row['conf'].getFormattedValue():'-';}""")

    @struct_method
    def di_dashboardViewer(self,parent,storepath=None,edit=False,**kwargs):
        frame = parent.framePane(**kwargs)
        sc = frame.center.stackContainer(selectedPage='^.selectedDashboard',frameTarget=True,margin='2px',
                                        selfsubscribe_addpage="genro.dashboards.addPage()",
                                selfsubscribe_delpage="genro.dashboards.delPage()",
                                selfsubscribe_duppage="genro.dashboards.dupPage()",
                                _editMode = edit,_anchor=True,
                                onCreated="""if(!genro.dashboards){
                                    genro.dashboards = objectPop(window,'genro_plugin_dashboards');
                                }
                                genro.dashboards.root = this;
                                genro.dashboards.edit = this.attr._editMode;
                                var storepath = this.absDatapath('%s');
                                genro.dashboards.dashboardspath = storepath+'.dashboards';
                                genro.dashboards.itemspath = storepath+'.items';
                                genro.dashboards.workspaces = this.absDatapath('.dashboards');

                                """ %storepath)
        
        parent.dataController("""
            try {
                if(_triggerpars.kw.evt=='ins'){
                    genro.dashboards.rebuild();
                }else if(_triggerpars.kw.evt=='del'){
                    genro.dashboards.root.getValue().popNode(_triggerpars.kw.node.label);
                }else if(_reason=='container'){
                    genro.dashboards.rebuild();
                }else if (_reason=='child'){
                }else{
                    genro.dashboards.rebuild();
                }
            } catch (error) {
                console.error('error in dashboard store controller',error);
            }
        """,data='^%s.dashboards' %storepath)
        
        if edit:
            #parent.dataController("""
            #        console.log('selectedDashboard',selectedDashboard);
            #        var wdg = sc.getValue().getNode(selectedDashboard).widget;
            #        console.log('wdg',wdg);
            #        wdg._layoutChildren();
            #        """,
            #    sc=sc,
            #    selectedDashboard='^#FORM.dashboardEditor.selectedDashboard')

            parent.dataController("""genro.dashboards.clearRoot();""",
            formsubscribe_onLoading=True)

            
        
        bar = frame.top.slotToolbar('5,stackButtons,*')
        if edit:
            bar.replaceSlots('#','#,edittitle,10,paletteDashboardItems,10,delbtn,addbtn,dupbtn,5')
            self.di_dashboardConfPalette(bar.edittitle.div(_class='iconbox gear',tip='!!Config'))
            bar.addbtn.slotButton(iconClass='iconbox add_row',publish='addpage')
            bar.delbtn.slotButton(iconClass='iconbox delete_row',publish='delpage')
            bar.dupbtn.slotButton(iconClass='iconbox copy',publish='duppage')
            palette = bar.paletteDashboardItems.paletteTree(paletteCode='dashboardItems',title='Dashboard items',dockButton=True)
            palette.data('.store',self.dashboardItemsMenu(),childname='store')
    
    def di_dashboardConfPalette(self,parent):
        tp = parent.tooltipPane(modal=True,
            onOpening="""genro.dashboards.configurationPane(dialogNode);""")


    @public_method
    def dashboardItemsMenu(self,**kwargs):
        result = Bag()
        for pkgId,pkgObj in self.packages.items():
            for tblid,tblobj in pkgObj.tables.items():
                data = self.utils.tableScriptResourceMenu(table=tblobj.fullname,res_type='dashboard',
                                                            module_parameters=['item_parameters'])
                if data:
                    packagebag = result[pkgId] 
                    if not packagebag:
                        packagebag = Bag()
                        result.setItem(pkgId,packagebag,label=pkgId)
                    packagebag.setItem(tblid,data,label=tblid)
        #result.rowchild(label='!!Paperino',action="genro.bp(true)")
        #result.rowchild(label='!!Pippo',action="genro.bp(true)")
        return result