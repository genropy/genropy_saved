# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrlang import gnrImport, objectExtract
from gnr.core.gnrbag import Bag


class TableScriptHandlerCaller(BaseComponent):
    def onMain_table_script_caller(self):
        if self.root_page_id and not ('table_script_caller' in self._register_nodeId):
            self.pageSource().dataController("""
                                        var kw = table_script_run[0];
                                        kw['sourcepage_id'] = page_id;
                                        genro.mainGenroWindow.genro.publish("table_script_run",kw);
                                    """, 
                                    subscribe_table_script_run=True,nodeId='table_script_caller',page_id=self.page_id)


class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_handler/batch_handler'
    css_requires = 'gnrcomponents/batch_handler/batch_handler'

    def mainLeft_batch_monitor(self, pane):
        """!!Batch"""
        self.bm_monitor_pane(pane)

    def bm_monitor_pane(self, pane):
        pane.dataController("batch_monitor.on_datachange(_triggerpars.kw);", _fired="^gnr.batch")
        #dovrei modificare il clieant in modo che mi prenda l elemento di classe bm_rootnode visibile
        # e gli appiccichi i termometri senza usare il node id
        pane.div(nodeId='bm_rootnode', _class='bm_rootnode')
        pane.dataRpc('dummy', 'setStoreSubscription', subscribe_batch_monitor_on=True,
                     storename='user', client_path='gnr.batch', active=True,
                     _onResult='genro.rpc.setPolling(1,1);')
        pane.dataRpc('dummy', 'setStoreSubscription', active=False, subscribe_batch_monitor_off=True,
                     _onCalling='genro.rpc.setPolling();', storename='user')

class TableScriptHandler(BaseComponent):
    py_requires = 'gnrcomponents/printer_option_dialog:PrinterOption'
    
    def _table_script_imports(self,pane,res_obj):
        css_requires = getattr(res_obj,'css_requires','')
        js_requires = getattr(res_obj,'js_requires','')
        py_requires = getattr(res_obj,'py_requires','')
        for py in py_requires.split(','):
            if py:
                self.mixinComponent(py)
        for css in css_requires.split(','):
            if css and not css in self.dynamic_css_requires and not css in self.css_requires:
                url = self.getResourceUri(css,'css',add_mtime=True)
                if url:
                    pane.dataController('genro.dom.loadCss(url)' ,url=url,_onBuilt=True)
        for js in js_requires.split(','):
            if js and not js in self.dynamic_js_requires and not js in self.js_requires:
                url = self.getResourceUri(js,'js',add_mtime=True)
                if url:
                    pane.dataController('genro.dom.loadJs(url)', url=url,_onBuilt=True)
            
    @public_method
    def table_script_parameters(self, pane, table=None, res_type=None, resource='', title=None, 
                            extra_parameters=None,selectedRowidx=None,selectionName=None,sourcepage_id=None,
                            selectedPkeys=None,selectionFilterCb=None,sortBy=None,**kwargs):
        if not resource:
            return
        resource = resource.replace('.py', '')
        res_obj = self.site.loadTableScript(self, table, '%s/%s' % (res_type, resource), class_name='Main')
        res_obj.sourcepage_id = sourcepage_id or self.page_id
        self._table_script_imports(pane,res_obj)
        if selectionName:
            res_obj.defineSelection(selectionName=selectionName, selectedRowidx=selectedRowidx,
                                    selectionFilterCb=selectionFilterCb, sortBy=sortBy)
            count = len(res_obj.get_selection_pkeys() or [])
        else:
            res_obj.selectedPkeys = selectedPkeys
            count = len(selectedPkeys or [])
        self.current_batch = res_obj
        self.mixin(res_obj, methods='table_script_*,rpc_table_script_*')
        batch_dict = objectExtract(res_obj, 'batch_')
        batch_dict['resource_name'] = resource
        batch_dict['res_type'] = res_type
        pane.data('.batch', batch_dict)
        pane.data('#table_script_runner.data',Bag())
        pane.data('#table_script_runner.dialog_pars',Bag())
        pane.data('#table_script_runner.dialog_options',Bag())

        hasParameters = hasattr(self, 'table_script_parameters_pane')
        hasOptions = hasattr(self, 'table_script_option_pane')
        dlgpars = pane.dialog(title='^.title',datapath='.dialog_pars',position='relative')
        dlgoptions = pane.dialog(title='^.title',datapath='.dialog_options',position='relative')
        pane = pane.div(datapath='#table_script_runner')
        if hasParameters:
            parsbox = dlgpars.div(datapath='#table_script_runner.data',
                            min_width='300px',min_height='150px')
            if batch_dict.get('title'):
                dlgpars.dataFormula('.title','dlgtitle',dlgtitle="!!%s(%i)" %(batch_dict['title'],count),_onBuilt=True)
            self.table_script_parameters_pane(parsbox,extra_parameters=extra_parameters,record_count=count,**batch_dict)
            self.table_script_parameters_footer(dlgpars.div(left=0,right=0,position='absolute',bottom=0),**batch_dict)    
            dlgpars.dataController("dlgoptions.show();",confirm="^.confirm",dlg=dlgpars.js_widget,
                                    dlgoptions=dlgoptions.js_widget,
                                    hasOptions=hasOptions,_if='hasOptions&&confirm==true',
                                    _else='FIRE #table_script_runner.confirm;')  
            dlgpars.dataController("dlg.hide()",_fired="^.cancel",dlg=dlgpars.js_widget)  
        if hasOptions:
            self.table_script_option_pane(dlgoptions.div(datapath='#table_script_runner.data.batch_options'), resource=resource,**batch_dict)
            self.table_script_option_footer(dlgoptions.div(left=0,right=0,position='absolute',bottom=0),**batch_dict)    
            dlgoptions.dataController("FIRE #table_script_runner.confirm;",_fired="^.confirm",dlg=dlgoptions.js_widget)                
            dlgoptions.dataController("dlg.hide()",_fired="^.cancel",dlg=dlgoptions.js_widget)  

        pane.dataController("""
                            dlgpars.hide();
                            dlgoptions.hide();
                            SET #table_script_runner.parameters=pars;
                            if (immediate){
                                genro.dom.setClass(dojo.body(),'runningBatch',true);
                            }else{
                                var modifier = _node.attr.modifier;
                                if(modifier!='Shift'){
                                    genro.publish({parent:true,topic:'open_batch'});
                                }                                
                            }
                            FIRE .run;
                            """,
                           _fired="^.confirm", pars='=.data',
                           immediate=batch_dict.get('immediate',False),
                           dlgpars=dlgpars.js_widget,dlgoptions=dlgoptions.js_widget) 
        pane.dataController(
        """if(hasParameters){
                dlgpars.show();
            }else if(hasOptions){
                dlgoptions.show();
            }else{
                FIRE .confirm;
            }
        """,_onBuilt=True,
            dlgpars=dlgpars.js_widget,
            dlgoptions=dlgoptions.js_widget,
            hasParameters=hasParameters,hasOptions=hasOptions)


    @public_method
    def table_script_run(self, table=None, resource=None, res_type=None, selectionName=None, selectedPkeys=None,selectionFilterCb=None,
                             sortBy=None,
                             selectedRowidx=None,sourcepage_id=None,
                             parameters=None, printerOptions=None, extra_parameters=None,**kwargs):
        res_obj = self.site.loadTableScript(self, table, '%s/%s' % (res_type, resource), class_name='Main')
        res_obj.sourcepage_id = sourcepage_id or self.page_id
        if selectionName:
            res_obj.defineSelection(selectionName=selectionName, selectedRowidx=selectedRowidx,
                                    selectionFilterCb=selectionFilterCb, sortBy=sortBy)
        else:
            res_obj.selectedPkeys = selectedPkeys
        parameters = parameters or {}
        parameters['_printerOptions'] = printerOptions
        if extra_parameters:
            parameters['extra_parameters'] = extra_parameters
        res_obj(parameters=parameters, **kwargs)
        
    @public_method
    def table_script_resource_tree_data(self, table=None, res_type=None):
        #pkg,tblname = table.split('.')
        tblobj = self.db.table(table)
        pkg = tblobj.pkg.name
        tblname = tblobj.name
        result = Bag()
        resources = self.site.resource_loader.resourcesAtPath(pkg, 'tables/%s/%s' % (tblname, res_type), 'py')
        resources_custom = self.site.resource_loader.resourcesAtPath(self.package.name, 'tables/_packages/%s/%s/%s' % (pkg,tblname, res_type), 'py')
        resources.update(resources_custom)
        forbiddenNodes = []
        def cb(node, _pathlist=None):
            has_parameters = False
            if node.attr['file_ext'] == 'py':
                resmodule = gnrImport(node.attr['abs_path'])
                tags = getattr(resmodule, 'tags', '')
                if tags and not self.application.checkResourcePermission(tags, self.userTags):
                    if node.label == '_doc':
                        forbiddenNodes.append('.'.join(_pathlist))
                    return
                caption = getattr(resmodule, 'caption', node.label)
                description = getattr(resmodule, 'description', '')
                if  node.label == '_doc':
                    result.setAttr('.'.join(_pathlist), dict(caption=caption, description=description, tags=tags,
                                                             has_parameters=has_parameters))
                else:
                    mainclass = getattr(resmodule, 'Main', None)
                    assert mainclass, 'Main class is mandatory in tablescript resource'
                    has_parameters = hasattr(mainclass, 'parameters_pane')
                    result.setItem('.'.join(_pathlist + [node.label]), None, caption=caption, description=description,
                                   resource=node.attr['rel_path'][:-3], has_parameters=has_parameters)
        resources.walk(cb, _pathlist=[])
        for forbidden in forbiddenNodes:
            result.pop(forbidden)
        return result


class TableScriptRunner(TableScriptHandler):
    py_requires = 'foundation/dialogs,gnrcomponents/printer_option_dialog:PrinterOption'
    js_requires = 'gnrcomponents/batch_handler/batch_handler'

    def onMain_table_script_runner(self):
        page = self.pageSource()
        self.table_script_controllers(page)
        
    def table_script_resource_tree(self, pane, table=None, res_type=None, selectionName=None, gridId=None, _class=None,
                                   **kwargs):
        pane.dataRemote('.tree.store', self.table_script_resource_tree_data, table=table, cacheTime=10, res_type=res_type)
        pane.tree(storepath='.tree.store', persist=False,
                  labelAttribute='caption', hideValues=True,
                  _class=_class,
                  selected_resource='.resource',
                  connect_ondblclick='FIRE .run_table_script',
                  tooltip_callback="return sourceNode.attr.description || sourceNode.label;",
                  **kwargs)
        pane.dataController("""
                            var selectedRowidx = gridId?genro.wdgById(gridId).getSelectedRowidx():null;
                            var pars = {table:table,res_type:res_type,selectionName:selectionName,selectedRowidx:selectedRowidx,resource:resource,gridId:gridId}
                            console.log(pars);
                            PUBLISH table_script_run=pars;""",
                            _fired="^.run_table_script", selectionName=selectionName, table=table,
                            gridId=gridId, res_type=res_type, resource='=.resource')

    
    def table_script_controllers(self,page):
        plugin_main = page.div(datapath='gnr.plugin.table_script_runner', nodeId='table_script_runner')
        plugin_main.dataController(""" var params = table_script_run[0];
                                       SET .res_type= objectPop(params,'res_type');
                                       SET .table =  objectPop(params,'table');
                                       SET .resource =  objectPop(params,'resource');
                                       SET .selectionName =  objectPop(params,'selectionName');
                                       SET .publishOnResult = objectPop(params,'publishOnResult');
                                       SET .selectionFilterCb =  objectPop(params,'selectionFilterCb'); 
                                       SET .selectedRowidx =  copyArray(objectPop(params,'selectedRowidx') || []);
                                       SET .sortBy =  objectPop(params,'sortBy');
                                       SET .onCalling = objectPop(params,'onCalling');
                                       SET .sourcepage_id = objectPop(params,'sourcepage_id');
                                       var pkey =  objectPop(params,'pkey');
                                       if (pkey){
                                            params.selectedPkeys = [pkey];
                                       }
                                       SET .selectedPkeys = copyArray(objectPop(params,'selectedPkeys') || []);
                                       var extra_parameters = objectPop(params,'extra_parameters');
                                       extra_parameters = extra_parameters? extra_parameters.deepCopy() : new gnr.GnrBag();
                                       for(var k in params){
                                            extra_parameters.setItem(k,params[k]);
                                       }
                                       if(extra_parameters.len()>0){
                                            SET .extra_parameters = extra_parameters;
                                       }
                                       FIRE .build_pars_dialog;
                                    """, subscribe_table_script_run=True)

        plugin_main.dataRpc('dummy', self.table_script_run,
                            _fired='^.run',
                            _onCalling='=.onCalling',
                            _onResult="""if(kwargs._publishOnResult){genro.publish(kwargs._publishOnResult);}""",
                            parameters='=.parameters',
                            resource='=.resource',
                            res_type='=.res_type',
                            table='=.table',
                            gridId='=.gridId',
                            _publishOnResult='=.publishOnResult',
                            selectionName='=.selectionName',
                            printerOptions='==this.getRelativeData("gnr.server_print.printers."+resource);',
                            selectionFilterCb='=.selectionFilterCb',
                            sourcepage_id='=.sourcepage_id',
                            selectedRowidx="=.selectedRowidx",
                            extra_parameters='=.extra_parameters',
                            sortBy="=.sortBy",
                            selectedPkeys='=.selectedPkeys',
                            _POST=True, timeout=0)

        plugin_main.div(width=0).remote(self.table_script_parameters,
                                 resource='=.resource',
                                 res_type='=.res_type',
                                 title='=.title',
                                 table='=.table',
                                 selectionName='=.selectionName',
                                 selectedRowidx="=.selectedRowidx",
                                 selectedPkeys='=.selectedPkeys',
                                 sourcepage_id='=.sourcepage_id',
                                 selectionFilterCb='=.selectionFilterCb',
                                 extra_parameters='=.extra_parameters',
                                 _fired='^.build_pars_dialog')

