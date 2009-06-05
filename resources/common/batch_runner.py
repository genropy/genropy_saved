#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import BaseComponent

class BatchRunner(BaseComponent):
    self.setBatchRunner(pane, resultpath, fired, gridId, thermoParams, )
    
    def setBatchRunner(self, pane, resultpath='aux.cmd.result', fired=None, batchFactory=None,
                             rpc=None,thermoParams=None, endScript=None,
                             stopOnError=False, forUpdate=False, onRow=None, **kwargs):
        """Prepare a batch action on the maintable with a thermometer
           @param pane: it MUST NOT BE a container. Is the pane where selectionBatchRunner
                  append dataController and dialog.
           @param resultpath: the path into the datastore where the result is stored.
           @param fired: the path where you fire the event that launch the dataRpc of selectionBatchRunner.
           @param batchFactory: is used instead of rpc. Name of the Factory Class, used as
                                plugin of table, which executes the standard batch action.
           @param rpc: is used instead of batchFactory. The name of the custum rpc you can use for the batch
                       for every selected row.
        """
        thermoid = None
        if thermofield:
            thermoid = self.getUuid()
            self.thermoDialog(pane, thermoid=thermoid, title=title, fired=fired, alertResult=True)
        pane.dataRpc(resultpath, rpc or 'app.runSelectionBatch',
                     table=self.maintable, selectionName='=list.selectionName',
                     batchFactory=batchFactory, thermoid=thermoid,
                     thermofield=thermofield,
                     pkeys='==genro.wdgById("maingrid").getSelectedPkeys()',
                     fired=fired, _onResult=endScript,
                     stopOnError=stopOnError, forUpdate=forUpdate, onRow=onRow, **kwargs)
        
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