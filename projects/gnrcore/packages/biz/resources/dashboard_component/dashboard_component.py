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
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag
import os


class DashboardItem(BaseComponent):
    css_requires='dashboard_component/dashboard_component'
    js_requires='dashboard_component/dashboard_component,chroma.min.js'

    @struct_method
    def di_dashboardItem(self,parent,table=None,itemName=None,**kwargs):
        parent.remote(self.di_buildRemoteItem,table=table,itemName=itemName,_waitingMessage=True,**kwargs)

    @public_method
    def di_buildRemoteItem(self,pane=None,table=None,itemName=None,itemRecord=None,**kwargs):
        table = table or itemRecord['table']
        resource = itemName or itemRecord['resource']
        if table:
            itemInstance = self.loadTableScript(table=table,respath='dashboard/%s' %resource)
        else:
            itemInstance = self.loadTableScript(table='biz.dashboard',respath='standard_items/%s' %resource)
        if  itemInstance.py_requires:
            for req in itemInstance.py_requires.split(','):
                self.mixinComponent(req)
        itemRecord = itemRecord or Bag()
        itemInstance(pane.contentPane(childname='remoteItem'),title=itemRecord['title'],parameters=itemRecord['parameters'],itemRecord=itemRecord,**kwargs)

class DashboardGallery(BaseComponent):
    py_requires='dashboard_component/dashboard_component:DashboardItem'

    @struct_method
    def di_dashboardGallery(self,parent,pkg=None,code=None,datapath=None,**kwargs):
        datapath =datapath or 'dashboard_%s_%s' %(pkg,code)
        bc = parent.borderContainer(_anchor=True,datapath=datapath,**kwargs)
        bc.dataRecord('.dashboard_record','biz.dashboard',pkgid=pkg,code=code,_onBuilt=True)
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
    def di_channelsViewer(self,parent,storepath=None,datapath=None,**kwargs):
        parent.bagGrid(storepath=storepath,datapath=datapath,
                        struct=self._di_channelsStruct,addrow=False,**kwargs)

    def _di_channelsStruct(self,struct):
        r=struct.view().rows()
        r.cell('topic',name='Topic',width='8em')
        r.cell('dtype',name='DType',width='10em',values='T:Text,D:Date,B:Boolean,N:Numeric,L:Integer',edit=True)
        r.cell('wdg',name='Widget',width='20em',edit=True)
        r.cell('dbtable',name='Dbtable',width='20em',edit=True)
        r.cell('condition',name='Condition',width='20em',edit=True)

    @struct_method
    def di_dashboardViewer(self,parent,storepath=None,edit=False,**kwargs):
        frame = parent.framePane(**kwargs)
        dashboardNodeId = '%(frameCode)s_dashboard' %frame.attributes
        sc = frame.center.stackContainer(selectedPage='^.selectedDashboard',frameTarget=True,margin='2px',
                                        selfsubscribe_addpage="this._dashboardManager.addPage()",
                                selfsubscribe_delpage="this._dashboardManager.delPage()",
                                selfsubscribe_duppage="this._dashboardManager.dupPage()",
                                nodeId=dashboardNodeId,
                                _editMode = edit,_storepath=storepath,_anchor=True,
                                formsubscribe_onLoading = 'this._dashboardManager.clearRoot();' if edit else None,
                                onCreated="""if(!genro.dashboards){
                                    genro.dashboards = objectPop(window,'genro_plugin_dashboards');
                                }
                                this._dashboardManager = new gnr.DashboardManager(this);
                                genro.dashboards[this.attr.nodeId] = this._dashboardManager;
                                """)
        
        parent.dataController("""
            var dashboard = sc._dashboardManager;
            try {
                if(_triggerpars.kw.evt=='ins'){
                    dashboard.rebuild();
                }else if(_triggerpars.kw.evt=='del'){
                    dashboard.root.getValue().popNode(_triggerpars.kw.node.label);
                }else if(_reason=='container'){
                    dashboard.rebuild();
                }else if (_reason=='child'){
                }else{
                    dashboard.rebuild();
                }
            } catch (error) {
                console.error('error in dashboard store controller',error);
            }
        """,data='^%s.dashboards' %storepath,sc=sc)

        parent.dataController("""
            var subscriptions,config;
            items.values().forEach(function(item){
                config = item.getItem('conf');
                subscriptions = item.getItem('conf_subscriber');
                if(!subscriptions){
                    return;
                }
                subscriptions.values().forEach(function(sub){
                    if(sub.getItem('topic') in _subscription_kwargs){
                        config.setItem(sub.getItem('varpath'),_subscription_kwargs[sub.getItem('topic')]);
                    }
                });   
            });
        """,items='=%s.items' %storepath,
        subscribe_dashboardItemConfig=True)
        bar = frame.top.slotToolbar('5,stackButtons,*,channelsTooltip,5')
        if edit:
            bar.replaceSlots('#','#,confTooltip,10,paletteDashboardItems,10,delbtn,addbtn,5')
            self.di_dashboardConfTooltip(bar.confTooltip.div(_class='iconbox gear',tip='!!Config'),dashboardNodeId=dashboardNodeId)
            bar.addbtn.slotButton(iconClass='iconbox add_row',publish='addpage',parentForm=True)
            bar.delbtn.slotButton(iconClass='iconbox delete_row',publish='delpage',parentForm=True)
            #bar.dupbtn.slotButton(iconClass='iconbox copy',publish='duppage')
            palette = bar.paletteDashboardItems.paletteTree(paletteCode='dashboardItems',title='Dashboard items',dockButton=True)
            palette.data('.store',self.dashboardItemsMenu(),childname='store')
        self.di_channelsTooltip(bar.channelsTooltip.div(_class='iconbox menu_gray_svg',parentForm=False),
                                dashboardNodeId=dashboardNodeId)
        parent.dataController("""
        genro.publish('dashboardItemConfig',channelsdata.asDict());
        """,channelsdata='^%s.channels_data' %storepath,_if='channelsdata')

    def di_channelsTooltip(self,parent,dashboardNodeId=None):
        tp = parent.tooltipPane(modal=True,
            onOpening="""genro.dashboards['%s'].channelsPane(dialogNode);""" %dashboardNodeId)


    def di_dashboardConfTooltip(self,parent,dashboardNodeId=None):
        tp = parent.tooltipPane(modal=True,
            onOpening="""genro.dashboards['%s'].configurationPane(dialogNode);""" %dashboardNodeId)


    @public_method
    def dashboardItemsMenu(self,**kwargs):
        result = Bag()
        objtypes = ['dash_groupby','dash_tableviewer','dash_pandas']
        for pkgId,pkgObj in self.packages.items():
            for tblid,tblobj in pkgObj.tables.items():
                userobjects = self.db.table('adm.userobject').userObjectMenu(objtype=objtypes,table=tblobj.fullname)
                data = self.utils.tableScriptResourceMenu(table=tblobj.fullname,res_type='dashboard',
                                                            module_parameters=['item_parameters'])
                if userobjects or data:
                    b = Bag()
                    b.update(data)
                    b.update(userobjects)
                    packagebag = result[pkgId] 
                    if not packagebag:
                        packagebag = Bag()
                        result.setItem(pkgId,packagebag,label=pkgId)
                    packagebag.setItem(tblid,b,label=tblid)
        #result.rowchild(label='!!Paperino',action="genro.bp(true)")
        #result.rowchild(label='!!Pippo',action="genro.bp(true)")
        return result