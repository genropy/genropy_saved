# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,customizable
from gnr.core.gnrlang import gnrImport, objectExtract
from gnr.core.gnrbag import Bag

class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_handler/batch_handler'
    css_requires = 'gnrcomponents/batch_handler/batch_handler'

    def mainLeft_batch_monitor(self, pane):
        """!!Batch"""
        self.bm_monitor_pane(pane)

    def btn_batch_monitor(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='batch_monitor_icon',tip='!!Batch monitor',
                 connect_onclick="""genro.publish('open_batch');""",
                 nodeId='plugin_block_batch_monitor')
        pane.dataController("SET left.selected='batch_monitor';genro.getFrameNode('standard_index').publish('showLeft')",subscribe_open_batch=True)


    def bm_monitor_pane(self, pane):
        pane.dataController("batch_monitor.on_datachange(_triggerpars.kw);", _fired="^gnr.batch")
        #dovrei modificare il client in modo che mi prenda l elemento di classe bm_rootnode visibile
        # e gli appiccichi i termometri senza usare il node id
        pane.div(nodeId='bm_rootnode', _class='bm_rootnode')
        pane.dataRpc('dummy', self.setStoreSubscription, subscribe_batch_monitor_on=True,
                     storename='user', client_path='gnr.batch', active=True,
                     _onResult='genro.setFastPolling(true);')
        pane.dataRpc('dummy', self.setStoreSubscription, active=False, _onCalling='genro.setFastPolling(false);',
                    subscribe_batch_monitor_off=True,storename='user')

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
            
    def table_script_plan(self,bar,plan_tag='admin',**kwargs):
        if self.application.checkResourcePermission(plan_tag,self.userTags):
            bar.replaceSlots('#','planbtn,#')
            bar.planbtn.slotButton('Plan')
            #if hasattr(self,'zumZum'):
            #    print bazinga
    
    @public_method
    def table_script_parameters(self, pane, table=None, res_type=None, resource='', title=None, 
                            extra_parameters=None,selectedRowidx=None,selectionName=None,
                            selectedPkeys=None,selectionFilterCb=None,sortBy=None,**kwargs):
        if not resource:
            return
        resource = resource.replace('.py', '')
        resource_path = '%s/%s' % (res_type, resource)
        res_obj = self.site.loadTableScript(self, table, resource_path, class_name='Main')
        self._table_script_imports(pane,res_obj)
        count = 0
        if selectedPkeys:
            if isinstance(selectedPkeys,basestring):
                selectedPkeys = selectedPkeys.strip(',').split(',')
            res_obj.selectedPkeys = selectedPkeys
            count = len(selectedPkeys or [])
        elif selectionName:
            res_obj.defineSelection(selectionName=selectionName, selectedRowidx=selectedRowidx,
                                    selectionFilterCb=selectionFilterCb, sortBy=sortBy)
            count = len(res_obj.get_selection_pkeys() or [])
        self.current_batch = res_obj
        self.mixin(res_obj, methods='table_script_*,rpc_table_script_*')
        batch_dict = objectExtract(res_obj, 'batch_')
        batch_dict['record_count'] = count
        batch_dict['resource_name'] = resource
        batch_dict['resource_path'] = resource_path
        batch_dict['res_type'] = res_type
        batch_dict['table'] = table
        self.table_script_dialogs(pane,batch_dict=batch_dict,extra_parameters=extra_parameters)
        
    @customizable
    def table_script_dialogs(self,pane,batch_dict=None,extra_parameters=None):
        pane.data('.batch', batch_dict)
        pane.data('#table_script_runner.data',Bag())
        pane.data('#table_script_runner.dialog_pars',Bag())
        pane.data('#table_script_runner.dialog_options',Bag())

        hasParameters = hasattr(self, 'table_script_parameters_pane')
        hasOptions = hasattr(self, 'table_script_option_pane')
        dlgpars = pane.dialog(title='^.title',datapath='.dialog_pars',position='relative',childname='parametersDialog',padding_bottom='25px')
        dlgoptions = pane.dialog(title='^.title',datapath='.dialog_options',position='relative',childname='optionsDialog')
        pane = pane.div(datapath='#table_script_runner')
        if hasParameters:
            parsbox = dlgpars.div(datapath='#table_script_runner.data',
                            min_width='300px',childname='contentNode',position='relative',top='0',
                            bottom='25px')
            if batch_dict.get('title'):
                dlgpars.dataFormula('.title','dlgtitle',dlgtitle="!!%s (%i)" %(batch_dict['title'],batch_dict.get('record_count')),_onBuilt=True)
            self.table_script_parameters_pane(parsbox,extra_parameters=extra_parameters,**batch_dict)
            footer = self.table_script_parameters_footer(dlgpars.div(left=0,right=0,position='absolute',bottom=0,
                                                         childname='footerNode',height='25px'),**batch_dict)    
            dlgpars.dataController("dlgoptions.show();",confirm="^.confirm",dlg=dlgpars.js_widget,
                                    dlgoptions=dlgoptions.js_widget,
                                    hasOptions=hasOptions,_if='hasOptions&&confirm==true',
                                    _else='FIRE #table_script_runner.confirm;')  
            dlgpars.dataController("dlg.hide()",_fired="^.cancel",dlg=dlgpars.js_widget)  
        if hasOptions:
            self.table_script_option_pane(dlgoptions.div(datapath='#table_script_runner.data.batch_options',childname='contentNode'),**batch_dict)
            footer = self.table_script_option_footer(dlgoptions.div(left=0,right=0,position='absolute',bottom=0,childname='footerNode'),**batch_dict) 
            
            dlgoptions.dataController("FIRE #table_script_runner.confirm;",_fired="^.confirm",dlg=dlgoptions.js_widget)                
            dlgoptions.dataController("dlg.hide()",_fired="^.cancel",dlg=dlgoptions.js_widget)  

        extra_parameters = extra_parameters or Bag()
        immediate = extra_parameters.getItem('batch_immediate') or batch_dict.get('immediate')
        pane.dataController("""
                            dlgpars.hide();
                            dlgoptions.hide();
                            SET #table_script_runner.parameters=pars;
                            if (immediate){
                                genro.dom.setClass(dojo.body(),'runningBatch',true);
                            }else{
                                var modifier = _node.attr.modifier;
                                if(modifier!='Shift'){
                                    genro.mainGenroWindow.genro.publish('open_batch');
                                }                                
                            }
                            FIRE .run;
                            """,
                           _fired="^.confirm", pars='=.data',
                           immediate=immediate or False,
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
                             selectedRowidx=None,
                             parameters=None, printerOptions=None, extra_parameters=None,**kwargs):
        res_obj = self.site.loadTableScript(self, table, '%s/%s' % (res_type, resource), class_name='Main')
        if selectedPkeys:
            if isinstance(selectedPkeys,basestring):
                selectedPkeys = selectedPkeys.strip(',').split(',')
            res_obj.selectedPkeys = selectedPkeys
        elif selectionName:
            res_obj.defineSelection(selectionName=selectionName, selectedRowidx=selectedRowidx,
                                    selectionFilterCb=selectionFilterCb, sortBy=sortBy)
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
        resources = self.site.resource_loader.resourcesAtPath(page=self,pkg=None,path='tables/_default/%s' % res_type)
        resources_pkg = self.site.resource_loader.resourcesAtPath(page=self,pkg=pkg, path='tables/%s/%s' % (tblname, res_type))
        resources_custom = self.site.resource_loader.resourcesAtPath(page=self,pkg=self.package.name, path='tables/_packages/%s/%s/%s' % (pkg,tblname, res_type))
        resources.update(resources_pkg)
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
                description = getattr(resmodule, 'needSelection', True)
                if  node.label == '_doc':
                    result.setAttr('.'.join(_pathlist), dict(caption=caption, description=description, tags=tags,
                                                             has_parameters=has_parameters))
                else:
                    mainclass = getattr(resmodule, 'Main', None)
                    assert mainclass, 'Main class is mandatory in tablescript resource'
                    has_parameters = hasattr(mainclass, 'parameters_pane')
                    result.setItem('.'.join(_pathlist + [node.label]), None, caption=caption, description=description,
                                   resource=node.attr['rel_path'][:-3], has_parameters=has_parameters)
        pl=[]     
        resources.walk(cb,_pathlist=pl)
        if '_common' in result:
            n = result.popNode('_common')
            if len(result):
                result.setItem('r_zz',None,caption='-')
            result.setItem(n.label,n.value,n.attr)
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
                            PUBLISH table_script_run=pars;""",
                            _fired="^.run_table_script", selectionName=selectionName, table=table,
                            gridId=gridId, res_type=res_type, resource='=.resource')

    
    def table_script_controllers(self,page):
        plugin_main = page.div(datapath='gnr.plugin.table_script_runner', nodeId='table_script_runner')
        plugin_main.dataController(""" var params = objectUpdate({},_subscription_kwargs);
                                       SET .res_type= objectPop(params,'res_type');
                                       SET .table =  objectPop(params,'table');
                                       SET .resource =  objectPop(params,'resource');
                                       SET .selectionName =  objectPop(params,'selectionName');
                                       SET .publishOnResult = objectPop(params,'publishOnResult');
                                       SET .selectionFilterCb =  objectPop(params,'selectionFilterCb'); 
                                       SET .selectedRowidx =  copyArray(objectPop(params,'selectedRowidx') || []);
                                       SET .sortBy =  objectPop(params,'sortBy');
                                       SET .onCalling = objectPop(params,'onCalling');
                                       var pkey =  objectPop(params,'pkey');
                                       if (pkey){
                                            params.selectedPkeys = [pkey];
                                       }
                                       var selectedPkeys = objectPop(params,'selectedPkeys') || [];
                                       if(typeof(selectedPkeys)!='string'){
                                            selectedPkeys = copyArray(selectedPkeys);
                                       }
                                       SET .selectedPkeys = selectedPkeys;
                                       var extra_parameters = objectPop(params,'extra_parameters');
                                       extra_parameters = extra_parameters? extra_parameters.deepCopy() : new gnr.GnrBag();
                                       for(var k in params){
                                            extra_parameters.setItem(k,params[k]);
                                       }
                                       SET .extra_parameters = extra_parameters.len()==0?null: extra_parameters;
                                       FIRE .build_pars_dialog;
                                    """, subscribe_table_script_run=True)

        plugin_main.dataRpc('dummy', self.table_script_run,
                            _fired='^.run',
                            _onCalling='=.onCalling',
                            _onResult="""
                                    if(kwargs._publishOnResult){
                                        genro.publish({topic:kwargs._publishOnResult,iframe:'*'});
                                    }""",
                            parameters='=.parameters',
                            resource='=.resource',
                            res_type='=.res_type',
                            table='=.table',
                            gridId='=.gridId',
                            _publishOnResult='=.publishOnResult',
                            selectionName='=.selectionName',
                            printerOptions='==this.getRelativeData("gnr.server_print.printers."+resource);',
                            selectionFilterCb='=.selectionFilterCb',
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
                                 selectionFilterCb='=.selectionFilterCb',
                                 extra_parameters='=.extra_parameters',
                                 _fired='^.build_pars_dialog')

