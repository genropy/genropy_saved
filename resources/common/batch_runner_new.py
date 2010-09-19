#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#


from gnr.web.gnrbaseclasses import BaseComponent
import gnr.app.gnrbatch_new
from gnr.core.gnrlang import gnrImport
import os

class BatchRunner(BaseComponent):
    def buildBatchRunner(self, pane, resultpath='aux.cmd', datapath=None,
                         selectionName=None,selectedRowidx=None,recordId=None, 
                         fired=None, batch_class=None,batch_note=None,batch_forked=False,
                                selectionFilterCb=None,
                         _onResult=None,stopOnError=False,forUpdate=False,
                         onRow=None, commitAfterPrint=None, waitingDlg=None,**kwargs):
        """Prepare a batch action on the maintable with a thermometer
           @param resultpath: the path into the datastore where the result is stored.
           @param fired: the path where you fire the event that launch the dataRpc of selectionBatchRunner.
           @param batchFactory: is used instead of rpc. Name of the Factory Class, used as
                                plugin of table, which executes the standard batch action.
           @param rpc: is used instead of batchFactory. The name of the custum rpc you can use for the batch
                       for every selected row.
        """
        onBatchCalling = None
        #aggiunto da saverio (proviamo poi a fare questo con publish e subscribe)
        if waitingDlg:
            onBatchCalling = 'FIRE #pbl_waiting.open;'
            _onResult = '%s %s' % (_onResult, 'FIRE #pbl_waiting.close;')
    
        pane.data('.batch_call','runBatch',datapath=datapath)
        pane.dataRpc('%s.result' % resultpath, 'runBatch', timeout=0, _POST=True,
                     table=kwargs.pop('table', self.maintable), selectionName=selectionName,
                     recordId = recordId,datapath=datapath,
                     batch_class=batch_class,
                     selectionFilterCb=selectionFilterCb,
                     selectedRowidx =selectedRowidx,
                     _fired=fired, _onResult=_onResult,
                     commitAfterPrint=commitAfterPrint,
                     batch_note=batch_note,batch_forked=batch_forked,
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
            
            
    def rpc_runBatch_forked(self, *args, **kwargs):
        with self.pageStore() as store:
            store.setItem('_batch_args',args)
            store.setItem('_batch_kwargs',kwargs)
            store.setItem('_batch_user',self.user)
            store.setItem('_batch_connection_id',self.connection_id)

        request=self.request._request
        protocol = request.host_url.split('//')[0]
        host = '%s//localhost' % protocol
        if ':' in request.host:
            port = request.host.split(':')[1]
            host = '%s:%s' %(host,port)
        url = '%s%s?rpc=curl_runBatch&&page_id=%s' %(host,request.path_info,self.page_id)
        print url
        os.system("""nohup curl "%s" -o "%s" &""" %(url,'/result.txt'))
        
    def rpc_curl_runBatch(self):
        print 'inside forked process'
        store = self.pageStore()
        args = store.getItem('_batch_args')
        kwargs = store.getItem('_batch_kwargs')
        external_connection = store.getItem('_batch_connection_id')
        self.connection.getConnection(external_connection=external_connection)
        self.user = self.connection.user
        result = self.rpc_runBatch(*args,**kwargs)
        self.setInClientData(path='gnr.downloadurl',value=result,fired=True,public=True)

                   
    def rpc_runBatch(self, table, selectionName=None,selectionFilterCb=None,recordId=None ,batch_class=None, 
                   selectedRowidx=None, forUpdate=False, commitAfterPrint=None, data_method=None,
                    batch_note=None,batch_forked=None,**kwargs):
        """batchFactory: name of the Class, plugin of table, which executes the batch action
            thermoId:
            thermofield: the field of the main table to use for thermo display or * for record caption
            stopOnError: at the first error stop execution
            forUpdate: load records for update and commit at end (always use for writing batch)
            onRow: optional method to execute on each record in selection, use if no batchFactory is given
            """
        if batch_forked:
            print 'Forking...'
        if data_method:
            handler = getattr(self, 'rpc_%s'%data_method)
            runKwargs = kwargs['runKwargs']
            data = handler(selectionName=selectionName, selectedRowidx=selectedRowidx, selectionFilterCb=selectionFilterCb, pars=runKwargs)
            batch_class = 'PrintRecord'
        elif recordId:
            data = self.db.table(table).record(pkey=recordId,ignoreMissing=True).output('bag')
        elif selectionName:   
            data = self.getUserSelection(selectionName=selectionName,
                                         selectedRowidx=selectedRowidx,
                                         filterCb=selectionFilterCb)
        else:
            data=None
        batch_class = self.batch_loader(batch_class)
        if batch_class:
            batch = batch_class(data=data, table=table, page=self, thermocb=self.app.setThermo,
                                commitAfterPrint=commitAfterPrint,batch_note=batch_note,**kwargs)
            self.btc.run_batch(batch)
            #return batch.run()
        else:
            raise Exception
                
    def batch_loader(self, batch_class):
        if ':' in batch_class:
            module_path, class_name = batch_class.split(':')
            module = gnrImport(module_path)
        else:
            class_name = batch_class
            module = gnr.app.gnrbatch_new
        return getattr(module,class_name,None)
        