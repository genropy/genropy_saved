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
from gnr.core.gnrbag import Bag,DirectoryResolver
import os
import sys


class DashboardItem(BaseComponent):
    css_requires='dashboard_component/dashboard_component'
    js_requires='dashboard_component/dashboard_component,chroma.min.js'

    @struct_method
    def di_dashboardItem(self,parent,table=None,itemName=None,**kwargs):
        parent.remote(self.di_buildRemoteItem,table=table,itemName=itemName,_waitingMessage=True,**kwargs)

    @public_method
    def di_buildRemoteItem(self,pane=None,table=None,itemName=None,itemRecord=None,objtypes=None,**kwargs):
        table = table or itemRecord['table']
        if not objtypes:
            itemResources,objtypes = self.di_itemResourceData()
        resource = itemName or itemRecord['resource']
        objkw = objtypes[resource]
        itemInstance = self.loadResourceScript(objkw['resource'],pkg=objkw['pkg'])
        if  itemInstance.py_requires:
            for req in itemInstance.py_requires.split(','):
                self.mixinComponent(req)
        itemRecord = itemRecord or Bag()
        itemInstance(pane.contentPane(childname='remoteItem'),title=itemRecord['title'],parameters=itemRecord['parameters'],itemRecord=itemRecord,**kwargs)

    def di_itemResourceData(self):
        result = Bag()    
        typedict = {}
        def cb(node,pkg=None,**kwargs):
            if node.attr.get('file_ext') == 'py':
                resmodule = gnrImport(node.attr['abs_path'])
                objtype = getattr(resmodule,'objtype',None) or node.attr['file_name']
                caption = getattr(resmodule,'caption',None)
                description = getattr(resmodule,'description',None)
                resource = os.path.join('dashboard_items',os.path.splitext(node.attr['rel_path'])[0])
                kw = dict(objtype=objtype,caption=caption,description=description,resource=resource,pkg=pkg)
                typedict[objtype] = kw
                node.attr.update(kw)            
        for pkgid,pkgobj in self.db.application.packages.items():
            di_folder = os.path.join(pkgobj.packageFolder,'resources','dashboard_items') 
            d = DirectoryResolver(di_folder,include='*.py',exclude='_*')
            content = d()
            content.walk(cb,_mode='deep')
            result.setItem(pkgid,content,caption=pkgobj.attributes.get('name_long') or pkgid)
        return result,typedict

class DashboardGallery(BaseComponent):
    py_requires='dashboard_component/dashboard_component:DashboardItem'

    @extract_kwargs(channel=True)
    @struct_method
    def di_dashboardGallery(self,parent,pkg=None,code=None,datapath=None,nodeId=None,channel_kwargs=None,**kwargs):
        nodeId =nodeId or '%s_%s' %(pkg,code)
        datapath = datapath or '.%s' %nodeId
        bc = parent.borderContainer(_anchor=True,datapath=datapath,**kwargs)
        bc.dataRecord('.dashboard_record','biz.dashboard',applymethod=self.di_applyGalleryConfigurations,
                        pkgid=pkg,code=code,_onBuilt=True,_if='pkgid && code',_fired='^.refresh')
        bc.dataRpc(None,self.di_saveGalleryConfigurations,dashboard_key='=.dashboard_record.dashboard_key',
                            dashboard_data='^.dashboard_record.data',_delay=500,_if='_reason=="child"')
        frame = bc.dashboardViewer(storepath='.dashboard_record.data',region='center',nodeId=nodeId,channel_kwargs=channel_kwargs)
        if self.isDeveloper():
            bar = frame.top.bar.replaceSlots('#','#,editrec,5')  
            bar.editrec.slotButton('!!Edit',action="""
                                    var that = this;
                                    var onSavedCb=function(){
                                        that.fireEvent('.refresh',true);
                                    };
                                    var openKw = {default_pkgid:pkg,default_code:code,default_private:true};
                                    genro.dlg.thIframeDialog({windowRatio:.9,table:'biz.dashboard',title:'Edit dashboard',
                                                            pkey:dashboard_key || '*newrecord*',
                                                            formResource:'FormIncluded',main_call:'main_form',
                                                            onSavedCb:onSavedCb},openKw);
                                                        """,
                                    iconClass='iconbox pencil',pkg=pkg,code=code,
                                    dashboard_key='=.dashboard_record.dashboard_key')
        parent.dataController("""genro.nodeById(dashboardNodeId).publish('updatedChannels',_kwargs)""",
                            dashboardNodeId=nodeId,_delay=100,
                            **channel_kwargs)
        return bc

    @public_method
    def di_applyGalleryConfigurations(self,record,**kwargs):
        userconfig = self.db.table('biz.dashboard_config').record(dashboard_key=record['dashboard_key'],username=self.user,
                                                                    ignoreMissing=True).output('record')
        if not userconfig['data']:
            return
        record['data'].update(userconfig['data']) 
    
    @public_method
    def di_saveGalleryConfigurations(self,dashboard_key=None,dashboard_data=None,**kwargs):
        tblobj = self.db.table('biz.dashboard_config')
        with tblobj.recordToUpdate(username=self.user,dashboard_key=dashboard_key,insertMissing=True) as rec:
            rec['data'] = dashboard_data
        self.db.commit()

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
    
    def di_setItemResourcesData(self):
        if not hasattr(self,'_di_itemResources'):
            itemResources,objtypes = self.di_itemResourceData()
            self._di_itemResources = itemResources
            self._di_objtypes = objtypes
            self.pageSource().data('gnr.dashboardItemResorces',itemResources,objtypes=objtypes)

    @struct_method
    def di_dashboardViewer(self,parent,storepath=None,edit=False,nodeId=None,channel_kwargs=None,**kwargs):
        frameCode = '%s_frame' %nodeId if nodeId else None
        channel_kwargs = channel_kwargs or dict()
        frame = parent.framePane(frameCode=frameCode,**kwargs)
        dashboardNodeId = nodeId or '%(frameCode)s_dashboard' %frame.attributes
        self.di_setItemResourcesData()     
        sc = frame.center.stackContainer(selectedPage='^.selectedDashboard',frameTarget=True,margin='2px',
                                        selfsubscribe_addpage="this._dashboardManager.addPage()",
                                selfsubscribe_delpage="this._dashboardManager.delPage()",
                                selfsubscribe_duppage="this._dashboardManager.dupPage()",
                                selfsubscribe_channelsEdit = "this._dashboardManager.channelsEdit();",
                                selfsubscribe_updatedChannels="""this._dashboardManager.updatedChannels($1)""",
                                nodeId=dashboardNodeId,
                                _editMode = edit,_storepath=storepath,_anchor=True,
                                _externalChannels = channel_kwargs.keys(),
                                formsubscribe_onLoading = 'this._dashboardManager.clearRoot();' if edit else None,
                                onCreated="""if(!genro.dashboards){
                                    genro.dashboards = objectPop(window,'genro_plugin_dashboards');
                                }
                                if(this._dashboardManager){
                                    return;
                                }
                                this._dashboardManager = new gnr.DashboardManager(this);
                                genro.dashboards[this.attr.nodeId] = this._dashboardManager;
                                """)
        
        parent.dataController("""
            sc._dashboardManager.pageTrigger(_triggerpars.kw,_reason);
        """,data='^%s.dashboards' %storepath,sc=sc)
        bar = frame.top.slotToolbar('5,stackButtons,*,channelsEdit,5')
        if edit:
            bar.replaceSlots('#','#,confTooltip,10,dashboardItemPalettes,10,delbtn,addbtn,5')
            self.di_dashboardConfTooltip(bar.confTooltip.div(_class='iconbox gear',tip='!!Config'),dashboardNodeId=dashboardNodeId)
            bar.addbtn.slotButton(iconClass='iconbox add_row',publish='addpage',parentForm=True)
            bar.delbtn.slotButton(iconClass='iconbox delete_row',publish='delpage',parentForm=True)
            #bar.dupbtn.slotButton(iconClass='iconbox copy',publish='duppage')
            self.di_dashboardItemPalettes(bar.dashboardItemPalettes)
        
        bar.channelsEdit.slotButton('!!Channels',publish='channelsEdit',disabled='^.channels?=#v?#v.len()==0:true',
                                    datapath=storepath,parentForm=False)
        parent.dataController("""
        if(_reason!='child'){
            return;
        }
        genro.dashboards[dashboardNodeId].sourceNode.publish('updatedChannels',channelsdata.asDict());
        """,datapath=storepath,channelsdata='^.channels_data',_if='channelsdata',dashboardNodeId=dashboardNodeId)
        return frame

    def di_dashboardItemPalettes(self,pane):
        pg = pane.paletteGroup(groupCode='dasboardTools',width='700px',title='!!Dashboard Tools',dockButton=True)
        self.di_userObjectsTree(pg)
        self.di_itemClassesTree(pg)

    
    def di_itemClassesTree(self,pg):
        palette = pg.paletteTree(paletteCode='dashboardItemBuilder',title='!!Item Builder',
                                    searchOn=True,
                                    storepath='gnr.dashboardItemResorces',
                                    tree_selectedLabelClass='selectedTreeNode',
                                    tree__class=' branchtree noIcon',
                                    #tree_getLabelClass="return node.attr.itemClass "
                                    )
    

    def di_userObjectsTree(self,pg):
        palette = pg.paletteTree(paletteCode='dashboardUserObjectItems',title='!!Available Items',
                                    infoPanel=self.di_itemPrevew,
                                    searchOn=True,
                                    infoPanel_width='50%',
                                    infoPanel_border_left='1px solid #efefef',
                                    tree_openOnClick=True,
                                    tree_selectedLabelClass='selectedTreeNode',
                                    tree__class=' branchtree noIcon',
                                    tree_getLabelClass="return node.attr.itemClass ",
                                    dockButton=True)
        
        palette.onDbChanges(action="""
        if(dbChanges.some(c => c.objtype in objtypes)){
            FIRE .di_menu_refresh;
        }
        """,table='adm.userobject',objtypes='=gnr.dashboardItemResorces?objtypes')
        store = palette.dataRpc('.store',self.di_userObjectItems,childname='store',
                                objtypes='=gnr.dashboardItemResorces?objtypes',
                                _fired='^.di_menu_refresh',_onBuilt=True)

    def di_dashboardConfTooltip(self,parent,dashboardNodeId=None):
        tp = parent.tooltipPane(modal=True,
            onOpening="""genro.dashboards['%s'].configurationPane(dialogNode);""" %dashboardNodeId)

    @public_method
    def di_itemPrevew(self,pane,**kwargs):
        pane.dataController("""
        if(!(item.attr.pkey || item.attr.resource)){
            return;
        }       
        SET .userobject_id = item.attr.pke;
        """,subscribe_dashboardItems_tree_onSelected=True)
        pane.dataRpc('.preview_data',self.di_getUserObjectData,
                    userobject_id='^.userobject_id',objtypes='=gnr.dashboardItemResorces?objtypes',
                    _delay=500)
        pane.div(template="""${<div class='di_pr_caption'>$caption</div>}
                        ${<div class='di_pr_subcaption'>$dashboard_type</div>}
                        ${<div class='di_block'>$notes</div>}
                        <div class='di_info'>$itemInfo</div>
                        """,datasource='^.preview_data')
        box = pane.div(position='absolute',bottom='4px',left='4px',right='4px',height='200px',overflow='hidden')
        box.img(src='^.preview_data.preview',height='100%',hidden='^.preview_data.preview?=!#v')

    @public_method
    def di_getUserObjectData(self,userobject_id=None,objtypes=None):
        result = Bag()
        data,metadata = self.db.table('adm.userobject').loadUserObject(id=userobject_id)
        result['caption'] = metadata['description'] or metadata['code'].split('.')[-1].title()
        result['preview'] = metadata['preview']
        result['notes'] = metadata['notes']
        objtype = metadata['objtype']
        result['dashboard_type'] = objtype.split('_')[1].title()
        objkw = objtypes[objtype]
        itemInstance = self.loadResourceScript(objkw['resource'],pkg=objkw['pkg'])
        result['itemInfo'] = itemInstance.getDashboardItemInfo(table=metadata['tbl'],userObjectData=data)
        return result

    @public_method
    def di_userObjectItems(self,objtypes=None,**kwargs):
        result = Bag()
        for pkgId,pkgObj in self.packages.items():
            for tblid,tblobj in pkgObj.tables.items():
                userobjects = self.db.table('adm.userobject').userObjectMenu(objtype=objtypes.keys(),table=tblobj.fullname)
                if userobjects:
                    b = Bag()
                    b.update(userobjects)
                    packagebag = result[pkgId] 
                    if not packagebag:
                        packagebag = Bag()
                        result.setItem(pkgId,packagebag,caption=pkgObj.attributes.get('name_long') or pkgId,itemClass='di_folder di_pkg')
                    packagebag.setItem(tblid,b,caption=tblobj.name_long or tblid,itemClass='di_folder di_tbl')
        return result