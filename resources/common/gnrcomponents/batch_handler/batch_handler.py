# -*- coding: utf-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from past.builtins import basestring
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,customizable
from gnr.core.gnrlang import gnrImport, objectExtract
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import boolean

class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_handler/batch_handler'
    css_requires = 'gnrcomponents/batch_handler/batch_handler'

    def mainLeft_batch_monitor(self, pane):
        """!!Batch"""
        self.bm_monitor_pane(pane)

    def btn_batch_monitor(self,pane,**kwargs):
        pane.pluginButton('batch_monitor',caption='!!Batch monitor',
                            iconClass='batch_monitor_icon')
        pane.dataController("""genro.publish('open_plugin',{plugin:'batch_monitor'});""",subscribe_open_batch=True) #legacy?

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
            if css and css not in self.envelope_css_requires and css not in self.css_requires:
                self.envelope_css_requires[css] =  self.getResourceUri(css,'css',add_mtime=True)
        for js in js_requires.split(','):
            if js and js not in self.envelope_js_requires and js not in self.js_requires:
                self.envelope_js_requires[js] = self.getResourceUri(js,'js',add_mtime=True)
            
    def table_script_plan(self,bar,plan_tag='admin',**kwargs):
        if self.application.checkResourcePermission(plan_tag,self.userTags):
            bar.replaceSlots('#','planbtn,#')
            bar.planbtn.slotButton('Plan')
            #if hasattr(self,'zumZum'):
            #    print bazinga
    
    @public_method
    def table_script_parameters(self, pane, table=None, res_type=None, resource='', title=None, 
                            extra_parameters=None,selectedRowidx=None,selectionName=None,
                            selectedPkeys=None,selectionCount=None,selectionFilterCb=None,sortBy=None,**kwargs):
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
            count = len(selectedRowidx) or selectionCount
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
        hasOptions = hasattr(self, 'table_script_option_pane') and batch_dict.get('batch_ask_options')
        dlgpars = pane.dialog(title='^.title',position='relative',
                            datapath='.dialog_pars',
                            connect_show="setTimeout(function(){genro.formById('_ts_parameters_').newrecord()},1)",
                            connect_hide="setTimeout(function(){genro.formById('_ts_parameters_').abort()},1)",

                            childname='parametersDialog',padding_bottom='25px')
        parsform = dlgpars.boxForm(formId='_ts_parameters_',store='dummy',
                                 formDatapath='#table_script_runner.data')
        dlgoptions = pane.dialog(title='^.title',datapath='.dialog_options',
                                position='relative',
                                connect_show="setTimeout(function(){genro.formById('_ts_options_').newrecord()},1)",
                                connect_dismiss="setTimeout(function(){genro.formById('_ts_options_').abort()},1)",
                                childname='optionsDialog')
        optionsform = dlgoptions.boxForm(formId='_ts_options_',store='dummy',
                                 formDatapath='#table_script_runner.data.batch_options')
        pane = pane.div(datapath='#table_script_runner')
        if hasParameters:
            parsbox = parsform.div(datapath='#table_script_runner.data',
                            min_width='300px',childname='contentNode',position='relative',top='0',
                            bottom='25px',padding='10px')
            if batch_dict.get('title'):
                record_count = batch_dict.get('record_count')
                dlgtitle = "!!%s (%i)" %(batch_dict['title'],record_count) if record_count else batch_dict['title']
                parsform.dataFormula('.title','dlgtitle',dlgtitle=dlgtitle,_onBuilt=True)
            self.table_script_parameters_pane(parsbox,extra_parameters=extra_parameters,**batch_dict)
            self.table_script_parameters_footer(dlgpars.div(left=0,right=0,position='absolute',bottom=0,
                                                         childname='footerNode',height='25px'),**batch_dict)  
            dlgpars.dataController("""
                var frm = genro.formById('_ts_parameters_');
                if(frm.isValid()){
                    FIRE .confirm_do;
                }else{
                    frm.publish('message',{message:_T(msg),sound:'$error',messageType:'error'});
                }
                """,confirm="^.confirm",msg="!!Invalid parameters")  
            dlgpars.dataController("dlgoptions.show();",
                            confirm="^.confirm_do",dlg=dlgpars.js_widget,
                                    dlgoptions=dlgoptions.js_widget,
                                    hasOptions=hasOptions,_if='hasOptions&&confirm==true',
                                    _else="""FIRE #table_script_runner.confirm;""")  
            parsform.dataController("dlg.hide()",_fired="^.cancel",dlg=dlgpars.js_widget)  
        if hasOptions:
            print(x)

            self.table_script_option_pane(optionsform.div(datapath='#table_script_runner.data.batch_options',childname='contentNode'),**batch_dict)
            self.table_script_option_footer(dlgoptions.div(left=0,right=0,position='absolute',bottom=0,childname='footerNode'),**batch_dict) 
            dlgoptions.dataController("""
                var frm = genro.formById('_ts_options_');
                if(frm.isValid()){
                    FIRE #table_script_runner.confirm;
                }else{
                    frm.publish('message',{message:_T(msg),sound:'$error',messageType:'error'});
                }
                """,_fired="^.confirm",msg='!!Invalid')                
            dlgoptions.dataController("dlg.hide()",_fired="^.cancel",dlg=dlgoptions.js_widget)  

        extra_parameters = extra_parameters or Bag()
        immediate = extra_parameters.getItem('batch_immediate') or batch_dict.get('immediate')
        pane.dataController("""
                            var that = this;
                            var modifier = _node.attr.modifier;
                            this.watch('pendingRpc',function(){
                                return !genro.rpc.hasPendingCall();
                            },function(){
                                dlgpars.hide();
                                dlgoptions.hide();
                                that.setRelativeData('#table_script_runner.parameters',pars);
                                if (immediate){
                                    genro.dom.setClass(dojo.body(),'runningBatch',true);
                                }else{
                                    if(modifier!='Shift'){
                                        genro.mainGenroWindow.genro.publish('open_batch');
                                    }                                
                                }
                                that.fireEvent('.run',true);
                            });
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
        return self.utils.tableScriptResourceMenu(table=table,res_type=res_type)



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
        plugin_main = page.div(datapath='gnr.plugin.table_script_runner', nodeId='table_script_runner',context_dbstore='=.context_dbstore')
        plugin_main.dataController(""" var params = objectUpdate({},_subscription_kwargs);
                                       SET .res_type= objectPop(params,'res_type');
                                       SET .table =  objectPop(params,'table');
                                       SET .resource =  objectPop(params,'resource');
                                       SET .selectionCount = objectPop(params,'selectionCount');
                                       SET .selectionName =  objectPop(params,'selectionName');
                                       SET .publishOnResult = objectPop(params,'publishOnResult');
                                       SET .selectionFilterCb =  objectPop(params,'selectionFilterCb'); 
                                       SET .selectedRowidx =  copyArray(objectPop(params,'selectedRowidx') || []);
                                       SET .sortBy =  objectPop(params,'sortBy');
                                       SET .onCalling = objectPop(params,'onCalling');
                                       SET .context_dbstore = objectPop(params,'context_dbstore');
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
        batch_pars = self.site.config.getAttr('batch_processes')
        if batch_pars and not boolean(batch_pars.get('disabled')):
            table_script_run = self.table_script_daemon_run
        else:
            table_script_run = self.table_script_run
        plugin_main.dataRpc('dummy', table_script_run,
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
                            selectionCount='=.selectionCount',
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
                                 selectionCount='=.selectionCount',
                                 selectionName='=.selectionName',
                                 selectedRowidx="=.selectedRowidx",
                                 selectedPkeys='=.selectedPkeys',
                                 selectionFilterCb='=.selectionFilterCb',
                                 extra_parameters='=.extra_parameters',
                                 _fired='^.build_pars_dialog')

