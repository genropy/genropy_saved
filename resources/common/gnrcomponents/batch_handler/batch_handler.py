# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag


class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_handler/batch_handler'
    css_requires = 'gnrcomponents/batch_handler/batch_handler'
        
    def bm_monitor_pane(self,pane):
        pane.dataController("batch_monitor.on_datachange(_triggerpars.kw);",_fired="^gnr.batch")
        pane.div(nodeId='bm_rootnode',_class='bm_rootnode',overflow='auto',height='100%')
        pane.dataRpc('dummy','setStoreSubscription',subscribe_bm_monitor_open=True,
                    storename='user',client_path='gnr.batch',active=True,
                    _onResult='genro.rpc.setPolling(1,1);')
        pane.dataRpc('dummy','setStoreSubscription',active=False,subscribe_bm_monitor_close=True,
                    _onCalling='genro.rpc.setPolling();',storename='user')
        
class TableScriptRunner(BaseComponent):
    py_requires='foundation/dialogs'
    def onMain_table_script_runner(self):
        print 'on_main'
        page = self.pageSource()
        plugin_main = page.div(datapath='gnr.plugin.table_script_runner',nodeId='table_script_runner')
        plugin_main.dataController(""" var params = table_script_run[0];
                                       SET .res_type= params['res_type'];
                                       SET .table =  params['table'];
                                       SET .resource =  params['resource'];
                                       SET .selectionName =  params['selectionName'];
                                       SET .selectedRowidx =  params['selectedRowidx'];
                                       FIRE .build_pars_dialog;
                                       FIRE .parsDlg.open;
                                    """,subscribe_table_script_run=True)
        plugin_main.dataRpc('dummy','table_script_run',
                _fired='^.run',
                _onCalling='PUBLISH bm_monitor_open;console.log($2)',
                pars='=.pars',resource='=.resource',
                res_type='=.res_type',
                table='=.table',
                selectionName='=.selectionName',
                selectedRowidx="=.selectedRowidx",subscribe_pippone=True)
                
        plugin_main.div().remote('table_script_parameters',
                            resource='=.resource',
                            res_type='=.res_type',
                            title='=.title',
                            table='=.table',
                            _fired='^.build_pars_dialog')

    def remote_table_script_parameters(self,pane,resource='',res_type=None,title=None,table=None,**kwargs):
        table = table or self.maintable
        pkgname,tblname = table.split('.')
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
                         cb_center=cb_center,dlgId='table_script_dlg_parameters')
        dlg.dataController("""FIRE .close;
                            SET #table_script_runner.pars=pars;
                            FIRE #table_script_runner.run;""",
                            _fired="^.save",pars='=.pars')
                     
    def rpc_table_script_run(self,table=None,resource=None,res_type=None,selectionName=None,selectedRowidx=None,**kwargs):
        tblobj = self.tblobj or self.db.table(table)
        res_obj=self.site.loadTableScript(self,tblobj,'%s/%s' %(res_type,resource),class_name='Main')
        res_obj.defineSelection(selectionName=selectionName,selectedRowidx=selectedRowidx)
        res_obj(**kwargs)
        
    def rpc_table_script_resource_tree(self,tbl,res_type):
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