# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrlang import gnrImport,objectExtract

from gnr.core.gnrbaghtml import BagToHtml
from gnr.core.gnrstring import templateReplace

from gnr.core.gnrbag import Bag


class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_handler/batch_handler'
    css_requires = 'gnrcomponents/batch_handler/batch_handler'
        
    def mainLeft_batch_monitor(self,tc):
        """!!Batch"""
        self.bm_monitor_pane(tc.contentPane(title='!!Batch',pageName='batch_monitor'))
    
    def bm_monitor_pane(self,pane):
        pane.dataController("batch_monitor.on_datachange(_triggerpars.kw);",_fired="^gnr.batch")
        #dovrei modificare il clieant in modo che mi prenda l elemento di classe bm_rootnode visibile
        # e gli appiccichi i termometri senza usare il node id
        pane.div(nodeId='bm_rootnode',_class='bm_rootnode')
        pane.dataRpc('dummy','setStoreSubscription',subscribe_batch_monitor_on=True,
                    storename='user',client_path='gnr.batch',active=True,
                    _onResult='genro.rpc.setPolling(1,1);')
        pane.dataRpc('dummy','setStoreSubscription',active=False,subscribe_batch_monitor_off=True,
                    _onCalling='genro.rpc.setPolling();',storename='user')
        
class TableScriptRunner(BaseComponent):
    py_requires='foundation/dialogs,gnrcomponents/printer_option_dialog:PrinterOption'
    js_requires = 'gnrcomponents/batch_handler/batch_handler'

    def onMain_table_script_runner(self):
        page = self.pageSource()
        plugin_main = page.div(datapath='gnr.plugin.table_script_runner',nodeId='table_script_runner')
        plugin_main.dataController(""" var params = table_script_run[0];
                                       SET .res_type= params['res_type'];
                                       SET .table =  params['table'];
                                       SET .resource =  params['resource'];
                                       SET .structpath =  params['structpath'];
                                       SET .selectionName =  params['selectionName'];
                                       SET .publishOnResult = params['publishOnResult'];
                                       SET .selectionFilterCb =  params['selectionFilterCb'];
                                       SET .gridId = params['gridId'];
                                       SET .selectedRowidx =  params['selectedRowidx'];
                                       SET .paramspath = params['paramspath'];
                                       FIRE .build_pars_dialog;
                                       FIRE #table_script_dlg_parameters.open;
                                    """,subscribe_table_script_run=True)
                                    
        plugin_main.dataRpc('dummy','table_script_run',
                _fired='^.run',
                _onResult='if(kwargs._publishOnResult){genro.publish(kwargs._publishOnResult);}',
                parameters='=.parameters',
                resource='=.resource',
                res_type='=.res_type',
                table='=.table',
                gridId='=.gridId',
                _publishOnResult='=.publishOnResult',
                selectionName='=.selectionName',
                struct='==this.getRelativeData(_structpath);',
                _structpath='=.structpath',
                printerOptions='==this.getRelativeData("gnr.server_print.printers."+resource);',
                selectionFilterCb='=.selectionFilterCb',
                selectedRowidx="=.selectedRowidx")
                
        plugin_main.div().remote('table_script_parameters',
                            resource='=.resource',
                            res_type='=.res_type',
                            title='=.title',
                            table='=.table',
                            _fired='^.build_pars_dialog')
                            
    def table_script_resource_tree(self,pane,table=None,res_type=None,selectionName=None,gridId=None,_class=None,**kwargs):
        pane.dataRemote('.tree.store', 'table_script_resource_tree_data', table=table, cacheTime=10,res_type=res_type)
        pane.tree(storepath='.tree.store', persist=False, 
                          labelAttribute='caption',hideValues=True,
                          _class=_class,
                          selected_resource ='.resource',
                          connect_ondblclick='FIRE .run_table_script',
                          tooltip_callback="return sourceNode.attr.description || sourceNode.label;",
                          **kwargs) 
                          
        pane.dataController("""
                            var selectedRowidx = gridId?genro.wdgById(gridId).getSelectedRowidx():null;
                            var pars = {table:table,res_type:res_type,selectionName:selectionName,selectedRowidx:selectedRowidx,resource:resource,gridId:gridId}
                            console.log(pars);
                            PUBLISH table_script_run=pars;""",
                            _fired="^.run_table_script",selectionName=selectionName,table=table,
                            gridId=gridId,res_type=res_type,resource='=.resource')

    
    def table_script_dialog_center(self,parentBc,hasParameters=None,**kwargs):
        if hasattr(self,'table_script_option_pane'):
            paramsBc = parentBc.borderContainer(pageName='params',datapath='.data',**kwargs)
            if hasParameters:
                parameters_pane = paramsBc.contentPane(region='top',_class='ts_parametersPane')
                parameters_pane.mainStack = parentBc.mainStack
                self.table_script_parameters_pane(parameters_pane)
            self.table_script_option_pane(paramsBc.contentPane(region='bottom',datapath='.batch_options',
                                                                _class='ts_optionsPane'))
        elif hasParameters:
            parameters_pane = parentBc.contentPane(pageName='params',datapath='.data',**kwargs)
            parameters_pane.mainStack = parentBc.mainStack
            self.table_script_parameters_pane(parameters_pane)
        self.table_script_waitingpane(parentBc.mainStack.contentPane(pageName='waiting'))
        
    def table_script_waitingpane(self,pane):
        bc = pane.borderContainer()
        bottom = bc.contentPane(region='bottom',_class='dialog_bottom')
        bottom.button('!!Close',float='right',margin='1px',
                      action='PUBLISH batch_monitor_off; FIRE .close')
        center = bc.contentPane(region='center', nodeId='table_script_waitingpane',_class='pbl_viewbox')
        center.dataController("""if(page=='waiting'){
                                    batch_monitor.create_local_root('table_script_waitingpane');
                                 }
                                    """,page="^.selected_stack_page")
        
        
    
    def remote_table_script_parameters(self,pane,table=None,res_type=None,resource='',title=None,**kwargs):
        pkgname,tblname = table.split('.')
        if not resource:
            return
        resource = resource.replace('.py','')
        cl=self.site.loadResource(pkgname,'tables',tblname,res_type,"%s:Main" %resource) #faccio mixin con prefisso
        self.mixin(cl,methods='table_script_*,rpc_table_script_*')
        batch_dict = objectExtract(cl,'batch_') 
        batch_dict['resource_name'] = resource
        batch_dict['res_type'] = res_type
        pane.data('.batch',batch_dict)
        hasParameters = hasattr(self,'table_script_parameters_pane')
        
        dlg_dict = objectExtract(cl,'dialog_')
        dialog_height_no_par = dlg_dict.pop('height_no_par',dlg_dict.get('height'))
        if not hasParameters:
            dlg_dict['height'] = dialog_height_no_par 
        dlg_dict['title'] = dlg_dict.get('title',batch_dict.get('title'))
        pane.data('.dialog',dlg_dict)        
        dlg = self.simpleDialog(pane,datapath='.dialog',title='^.title',height='^.height',width='^.width',
                             cb_center=self.table_script_dialog_center,dlgId='table_script_dlg_parameters',
                             hasParameters=hasParameters,dialog_height_no_par=dialog_height_no_par)
                         
        dlg.dataController("""
                            var modifier = _node.attr.modifier;
                            if (modifier=='Shift'){
                                FIRE .close;
                                //PUBLISH batch_monitor_open;
                                SET #table_script_runner.parameters=pars;
                                FIRE #table_script_runner.run;
                            }else{
                                //FIRE .close;
                                PUBLISH table_script_dlg_parameters_page = 'waiting';
                                //batch_monitor.create_local_root('_pageRoot');
                                SET #table_script_runner.parameters=pars;
                                PUBLISH batch_monitor_on;
                                FIRE #table_script_runner.run;
                            }
                            """,
                            _fired="^.save",pars='=.data')
                     
    def rpc_table_script_run(self,table=None,resource=None,res_type=None,selectionName=None,selectionFilterCb=None,selectedRowidx=None,
                            parameters=None,printerOptions=None,**kwargs):
        tblobj = self.tblobj or self.db.table(table)
        res_obj=self.site.loadTableScript(self,tblobj,'%s/%s' %(res_type,resource),class_name='Main')
        res_obj.defineSelection(selectionName=selectionName,selectedRowidx=selectedRowidx,selectionFilterCb=selectionFilterCb)
        parameters = parameters or {}
        parameters['_printerOptions'] = printerOptions
        res_obj(parameters=parameters,**kwargs)
        
    def rpc_table_script_resource_tree_data(self,table=None,res_type=None):
        #pkg,tblname = table.split('.')
        tblobj=self.db.table(table)
        pkg=tblobj.pkg.name
        tblname=tblobj.name
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
        
    def rpc_table_script_renderTemplate(self,doctemplate=None,record_id=None,templates=None,**kwargs):
        doctemplate_tbl =  self.db.table('adm.doctemplate')
        tplbuilder = doctemplate_tbl.getTemplateBuilder(doctemplate=doctemplate,templates=templates)
        return doctemplate_tbl.renderTemplate(tplbuilder,record_id=record_id,extraData=Bag(dict(host=self.request.host)))