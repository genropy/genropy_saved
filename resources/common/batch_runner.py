#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#


from gnr.web.gnrbaseclasses import BaseComponent
import gnr.app.gnrbatch
from gnr.core.gnrlang import gnrImport


class BatchRunner(BaseComponent):
    
##################### new stuff ###################

    #py_requires='thermo_utils:ThermoUtils'
    def buildBatch(self, name,datapath=None,**kwargs):
        controller = self.pageController(datapath=datapath,nodeId=name)
        controller.dataRpc('.result','runBatch',_fired='^.run',timeout=0,_POST=True,**kwargs)
        # FIRE #mybatch.run
    
    
##################### old stuff###################
    def buildBatchRunner(self, pane, resultpath='aux.cmd', datapath=None,
                         selectionName=None,selectedRowidx=None,recordId=None, thermoId=None,
                         fired=None, batch_class=None,selectionFilterCb=None,
                         thermoParams=None, _onResult=None,stopOnError=False,
                         forUpdate=False, onRow=None, commitAfterPrint=None,**kwargs):
        """Prepare a batch action on the maintable with a thermometer
           @param resultpath: the path into the datastore where the result is stored.
           @param fired: the path where you fire the event that launch the dataRpc of selectionBatchRunner.
           @param batchFactory: is used instead of rpc. Name of the Factory Class, used as
                                plugin of table, which executes the standard batch action.
           @param rpc: is used instead of batchFactory. The name of the custum rpc you can use for the batch
                       for every selected row.
        """
        onBatchCalling = None
        thermofield = None
        if thermoParams:
            if thermoParams is True:
                thermoParams= dict(field='*')
            thermoId = thermoId or self.getUuid()
            self.thermoDialog(pane,thermoId=thermoId,thermolines=thermoParams.get('lines',2),
                              title=thermoParams.get('title', 'Batch Running'),**kwargs)
            thermofield = thermoParams.get('field')
            onBatchCalling = 'FIRE #%s_dlg.open;' %thermoId
            
        pane.dataRpc('%s.result' % resultpath, 'runBatch', timeout=0, _POST=True,
                     table=kwargs.pop('table', self.maintable), selectionName=selectionName,
                     recordId = recordId,datapath=datapath,
                     batch_class=batch_class,
                     selectionFilterCb=selectionFilterCb,
                     thermofield=thermofield, thermoId = thermoId,
                     selectedRowidx =selectedRowidx,
                     _fired=fired, _onResult=_onResult,
                     commitAfterPrint=commitAfterPrint,
                     forUpdate=forUpdate, _onCalling=onBatchCalling,
                     **kwargs)
                     
        dlgid = self.getUuid()
        pane.dataController('genro.wdgById(dlgid).show()', _if='errors',
                            dlgid=dlgid, errors='^%s.errors' % resultpath)
        d = pane.dialog(nodeId=dlgid, title="!!Errors in batch execution", width='27em', height='27em')
        struct = self.newGridStruct()
        rows = struct.view().rows()
        rows.cell('caption',width='8em',name='!!Caption')
        rows.cell('error', name='!!Error')
        d.div(position='absolute', top='28px', right='4px',
            bottom='4px', left='4px').includedView(storepath='%s.errors' % resultpath, struct=struct)
            
    def rpc_runBatch(self, table, selectionName=None,selectionFilterCb=None,recordId=None ,batch_class=None, 
                    selectedRowidx=None, forUpdate=False, commitAfterPrint=None, data_method=None, **kwargs):
        """batchFactory: name of the Class, plugin of table, which executes the batch action
            thermoId:
            thermofield: the field of the main table to use for thermo display or * for record caption
            stopOnError: at the first error stop execution
            forUpdate: load records for update and commit at end (always use for writing batch)
            onRow: optional method to execute on each record in selection, use if no batchFactory is given
            """
        if data_method:
            handler = getattr(self, 'rpc_%s'%data_method)
            runKwargs = kwargs['runKwargs']
            data = handler(selectionName=selectionName, selectedRowidx=selectedRowidx, selectionFilterCb=selectionFilterCb, pars=runKwargs)
            batch_class = 'PrintRecord'
        elif recordId:
            data = self.db.table(table).record(pkey=recordId,ignoreMissing=True).output('bag')
        else:   
            data = self.getUserSelection(selectionName=selectionName,
                                         selectedRowidx=selectedRowidx,
                                         filterCb=selectionFilterCb)
        batch_class = self.batch_loader(batch_class)
        if batch_class:
            batch = batch_class(data=data, table=table, page=self, thermocb=self.app.setThermo,
                                commitAfterPrint=commitAfterPrint,**kwargs)
            return batch.run()
        else:
            raise Exception
        
    def batch_loader(self, batch_class):
        if ':' in batch_class:
            module_path, class_name = batch_class.split(':')
            module = gnrImport(module_path)
        else:
            class_name = batch_class
            module = gnr.app.gnrbatch
        return getattr(module,class_name,None)
        
        
    def thermoDialog(self,pane,thermoId=None,thermolines=2,title=None,**kwargs):
        def cb_center(parentBC,datapath=None,**kwargs):
            body = parentBC.contentPane(datapath='.result',**kwargs)
            for x in range(thermolines):
                tl = body.div(datapath='.t%i' % (x+1, ), border_bottom='1px solid gray', margin_bottom='3px')
                tl.div('^.message', height='1em', text_align='center')
                tl.data('')
                tl.progressBar(width='25em', indeterminate='^.indeterminate', maximum='^.maximum', height='17px',
                              places='^.places', progress='^.progress', margin_left='auto', margin_right='auto') 
        
        def cb_bottom(parentBC,**kwargs):
            footer = parentBC.contentPane(**kwargs)
            footer.button('!!Stop', float='right',action='SET .flag = "stop";')

            
        dlg = self.simpleDialog(pane,datapath='_thermo.%s' % thermoId,
                                dlgId='%s_dlg' %thermoId,cb_center=cb_center,
                                cb_bottom=cb_bottom,width='330px', title=title,
                                height='%ipx' %(100+thermolines*40),
                                connect_show='this.intervalRef = setInterval(function(){genro.fireEvent("_thermo.%s.getThermo")}, 500)' % thermoId,
                                connect_hide='clearInterval(this.intervalRef);')
        dlg.dataRpc('.result', 'app.getThermo', thermoId=thermoId,_fired='^.getThermo',
                    flag='=.flag',_onResult="""var status=result.getItem('status');
                                                                    if (status=='stopped' || status=='end'){
                                                                        FIRE .close;
                                                                    }
                                                                        """)  
                    
                    
    def thermoDialog___OLD(self, pane, thermoid='thermo', title='', thermolines=1, fired=None, alertResult=False,datapath=None):
        dlgid = 'dlg_%s' % thermoid
        dlg = pane.dialog(nodeId=dlgid, title=title,datapath='_thermo.%s.result' % thermoid,
                        closable='ask', close_msg='!!Stop the batch execution ?', close_confirm='Stop', close_cancel='Continue', 
                        close_action='FIRE ^_thermo.%s.flag = "stop"' % thermoid,
                        connect_show='this.intervalRef = setInterval(function(){genro.fireEvent("_thermo.%s.flag")}, 500)' % thermoid,
                        connect_hide='clearInterval(this.intervalRef);'
                        )
                        #onAskCancel
        bc=dlg.borderContainer(width='330px', height='%ipx' %(100+thermolines*40) )
        footer=bc.contentPane(region='bottom', _class='dialog_bottom')
        body=bc.contentPane(region='center')
        for x in range(thermolines):
            tl = body.div(datapath='.t%i' % (x+1, ), border_bottom='1px solid gray', margin_bottom='3px')
            tl.div('^.message', height='1em', text_align='center')
            tl.progressBar(width='25em', indeterminate='^.indeterminate', maximum='^.maximum', 
                          places='^.places', progress='^.progress', margin_left='auto', margin_right='auto')
                          
        footer.button('Stop', baseClass='bottom_btn',
                action='genro.wdgById("%s").onAskCancel();' % dlgid)
        controller =pane.dataController(datapath=datapath)
        controller.dataController('console.log("open thermo %s");genro.wdgById("%s").show()' %(dlgid,dlgid), fired=fired)
        controller.dataController('genro.wdgById(dlgid).hide();', dlgid=dlgid, 
                            status='^_thermo.%s.result.status' % thermoid, _if='(status=="stopped" || status=="end")')
        if alertResult:
            controller.dataFormula('gnr.alert', 'msg', msg='=_thermo.%s.result.message' % thermoid, 
                            status='^_thermo.%s.result.status' % thermoid, _if='(status=="stopped" || status=="end")')
        controller.dataRpc('_thermo.%s.result' % thermoid, 'app.getThermo', thermoid=thermoid,
                                                             flag='^_thermo.%s.flag' % thermoid)