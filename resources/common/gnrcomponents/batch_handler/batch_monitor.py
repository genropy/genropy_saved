# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_monitor/batch_handler'
    css_requires = 'gnrcomponents/batch_monitor/batch_handler'
        
    def bm_monitor_pane(self,pane):
        pane.dataController("batch_monitor.on_datachange(_triggerpars.kw);",_fired="^gnr.batch")
        pane.div(nodeId='bm_rootnode',_class='bm_rootnode',overflow='auto',height='100%')
        pane.dataRpc('dummy','setStoreSubscription',subscribe_bm_monitor_open=True,
                    storename='user',client_path='gnr.batch',active=True,
                    _onResult='genro.rpc.setPolling(1,1);')
        pane.dataRpc('dummy','setStoreSubscription',active=False,subscribe_bm_monitor_close=True,
                    _onCalling='genro.rpc.setPolling();',storename='user')
        
class BatchRunner(BaseComponent):
    def toolboxScriptRunner(self,datapath=None):
        pane = self.pageSource()
        pane.div(datapath=datapath).remote('toolboxParameters',
                                            resource='=.resource',
                                            res_type='=list.toolboxSelected',
                                            _fired='^.ask')
        controller = pane.dataController(nodeId="toolboxScriptRunner",datapath=datapath)
        controller.dataController("""
                                SET .resource = attr.resource;
                                if(attr.has_parameters){
                                    FIRE .ask;
                                    FIRE #toolboxScriptDlg.open;
                                }else{
                                    FIRE .run;
                                }""",
                              attr="^.call")
        
        controller.dataController("""
                            FIRE .run_rpc_dispatcher; 
                            this.setRelativeData("list.toolbox."+res_type+".tree.path",null);
                            FIRE list.showToolbox = false;
                            PUBLISH bm_monitor_open;
                            """,_fired="^.run",res_type='=list.toolboxSelected')
        
        controller.dataRpc('.res_result','toolboxResourceDispatcher',
                _fired='^.run_rpc_dispatcher',
                pars='=.pars',resource='=.resource',
                res_type='=list.toolboxSelected',
                selectionName='=list.selectionName',
                selectedRowidx="==genro.wdgById('maingrid').getSelectedRowidx();")

    def remote_toolboxParameters(self,pane,resource='',res_type=None,title=None,**kwargs):
        pkgname,tblname = self.maintable.split('.')
        if not resource:
            return
        resource = resource.replace('.py','')
        cl=self.site.loadResource(pkgname,'tables',tblname,res_type,"%s:Main" %resource)
        self.mixin(cl,methods='parameters_pane',prefix='toolbox')
        def cb_center(parentBc,**kwargs):
            center=parentBc.contentPane(datapath='.pars',**kwargs)
            self.toolbox_parameters_pane(center)
            center_attr = center.getNode('#0').attr
            dlg_attr = center.parentNode.parentbag.parentNode.attr
            dlg_attr['height'] = center_attr.get('height') or dlg_attr['height']
            dlg_attr['width'] = center_attr.get('width') or dlg_attr['width']

        dlg = self.simpleDialog(pane,title=title,datapath='.parsDlg',height='300px',width='400px',
                         cb_center=cb_center,dlgId='toolboxScriptDlg')
        dlg.dataController("FIRE .close; SET #toolboxScriptRunner.pars=pars; FIRE #toolboxScriptRunner.run;",
                            _fired="^.save",pars='=.pars')
         
        
    def toolboxFields(self,pane):
        treediv=pane.div(_class='treeContainer')
        treediv.tree(storepath='gnr.qb.fieldstree',persist=False,
                     inspect='shift', labelAttribute='caption',
                     _class='fieldsTree',
                     hideValues=True,
                     getIconClass='if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}',
                     dndController="dijit._tree.dndSource",
                     onDndDrop="function(){this.onDndCancel();}::JS",
                     checkAcceptance='function(){return false;}::JS',
                     checkItemAcceptance='function(){return false;}::JS')
    
    def bm_resource_pane(self, parent,res_type=None):
        datapath = 'list.toolbox.%s' %res_type
        sc = parent.stackContainer(datapath=datapath,selectedPage='^.currentPage')
        sc.dataFormula(".currentPage","resource?'pars':'tree';",
                        resource="^.tree.path?resource")
        treestack = sc.contentPane(pageName='tree')
        treestack.dataRemote('.tree.store', 'tableResourceTree', tbl=self.maintable, cacheTime=10,res_type=res_type)
        treestack.tree(storepath='.tree.store', persist=False, 
                          labelAttribute='caption',hideValues=True,
                          _class='toolboxResourceTree',
                          selectedPath='.tree.path',
                          selectedLabelClass='selectedTreeNode',
                          tooltip_callback="return sourceNode.attr.description || sourceNode.label;") 
        parsstack = sc.borderContainer(pageName='pars')
        top = parsstack.contentPane(region='top',_class='pbl_roundedGroupLabel').div('^.tree.path?caption')
        bottom = parsstack.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
        bottom.button('!!Confirm',action="""FIRE #toolboxScriptRunner.call = GET .tree.path?;""",float='right')
        bottom.button('!!Cancel',action='SET .tree.path=null;',float='right')
        center = parsstack.contentPane(region='center')
        center.div('^.tree.path?description')
        center.div('!!rows')
        
    def rpc_toolboxResourceDispatcher(self,resource=None,res_type=None,selectionName=None,selectedRowidx=None,**kwargs):
        res_obj=self.site.loadTableScript(self,self.tblobj,'%s/%s' %(res_type,resource),class_name='Main')
        res_obj.defineSelection(selectionName=selectionName,selectedRowidx=selectedRowidx)
        res_obj(**kwargs)
        
    def rpc_tableResourceTree(self,tbl,res_type):
        pkg,tblname = tbl.split('.')
        result = Bag()
        resources = self.site.resource_loader.resourcesAtPath(pkg,'tables/%s/%s' %(tblname,res_type),'py')
        forbiddenNodes = []
        def cb(node,_pathlist=None):
            has_parameters = False
            if node.attr['file_ext'] == 'py':
                resmodule = gnrImport(node.attr['abs_path'])
                tags = getattr(resmodule,'tags','') 
                
                if tags and not self.application.checkResourcePermission(tags, self.userTags):
                    if node.label=='_doc':
                        forbiddenNodes.append('.'.join(_pathlist))
                    return
                caption = getattr(resmodule,'caption',node.label)
                description = getattr(resmodule,'description','')
                if  node.label=='_doc':
                    result.setAttr('.'.join(_pathlist),dict(caption=caption,description=description,tags=tags,
                                                            has_parameters=has_parameters))
                else:
                    mainclass = getattr(resmodule,'Main',None)
                    assert mainclass,'Main class is mandatory in tablescript resource'
                    has_parameters = hasattr(mainclass,'parameters_pane')
                    result.setItem('.'.join(_pathlist+[node.label]),None,caption=caption,description=description,
                                    resource=node.attr['rel_path'][:-3],has_parameters=has_parameters)            
        resources.walk(cb,_pathlist=[])
        for forbidden in forbiddenNodes:
            result.pop(forbidden)
        return result