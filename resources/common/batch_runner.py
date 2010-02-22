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
                         selectionName=None,selectedRowidx=None,recordId=None, 
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
        thermoParams = thermoParams or dict()
        thermoid = None
        if 'field' in thermoParams:
            thermoid = self.getUuid()
            self.thermoDialog(pane, thermoid=thermoid, title=thermoParams.get('title', 'Batch Running'),
                            thermolines=thermoParams.get('lines',1), fired='^.openthermo', alertResult=True)
        pane.dataRpc('%s.result' % resultpath, 'runBatch', timeout=0, _POST=True,
                     table=kwargs.pop('table', self.maintable), selectionName=selectionName,
                     recordId = recordId,datapath=datapath,
                     batch_class=batch_class,
                     selectionFilterCb=selectionFilterCb,
                     thermofield=thermoParams.get('field'), thermoid = thermoid,
                     selectedRowidx =selectedRowidx,
                     _fired=fired, _onResult=_onResult,
                     commitAfterPrint=commitAfterPrint,
                     forUpdate=forUpdate, _onCalling='console.log("call thermo");FIRE .openthermo',
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
            thermoid:
            thermofield: the field of the main table to use for thermo display or * for record caption
            stopOnError: at the first error stop execution
            forUpdate: load records for update and commit at end (always use for writing batch)
            onRow: optional method to execute on each record in selection, use if no batchFactory is given
            """
        tblobj = self.db.table(table)  
        if data_method:
            handler = getattr(self, 'rpc_%s'%data_method)
            runKwargs = kwargs['runKwargs']
            data = handler(selectionName=selectionName, selectedRowidx=selectedRowidx, selectionFilterCb=selectionFilterCb, pars=runKwargs)
            batch_class = 'PrintRecord'
        elif recordId:
            data = tblobj.record(pkey=recordId,ignoreMissing=True).output('bag')
        else:   
            data = self.unfreezeSelection(tblobj, selectionName)
            if selectionFilterCb:
                filterCb=getattr(self, 'rpc_%s' % selectionFilterCb)
                data.filter(filterCb)
            elif selectedRowidx:
                if isinstance(selectedRowidx, basestring):
                    selectedRowidx = [int(x) for x  in selectedRowidx.split(',')]
                selectedRowidx = set(selectedRowidx)
                data.filter(lambda r: r['rowidx'] in selectedRowidx)
            
        batch_class = self.batch_loader(batch_class)
        if batch_class:
            batch = batch_class(data=data, table=table, page=self, thermocb=self.app.setThermo,
                                commitAfterPrint=commitAfterPrint, **kwargs)
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