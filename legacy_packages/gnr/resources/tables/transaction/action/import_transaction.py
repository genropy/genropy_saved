# -*- coding: utf-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

gnrlogger = logging.getLogger('gnr')


caption = 'Sync transaction block'
tags = 'admin'
description='Sync transaction block'


class Main(BaseResourceAction):
    batch_prefix = 'TRD'
    batch_title = 'Sync transaction'
    batch_delay = 0.5
    commit_limit = 20
    limit = 1000
    
    def do(self):
        self._startLog()
        self.import_failed = False
       # self.btc.thermo_wrapper(records, maximum=len(self.get_selection()),enum=True ,**thermo_s):
        limit = self.batch_parameters.get('how_many',self.limit)

        commit_row = self.batch_parameters.get('commit_row',False)
        transactionToExpand = self.tblobj.transactionsToExpand(limit)
        k = 0
        for record in self.btc.thermo_wrapper(transactionToExpand,maximum=len(transactionToExpand),line_code='trans', message='Transaction'):
            imported = self.tblobj.expandTransaction(record)
            k+=1
            if not imported:
                self.import_failed=True
                break
            elif commit_row or k%self.commit_limit==0:
                self.db.commit()
        self.db.commit()

    def result_handler(self):
        if self.import_failed:
            return 'Import failed',dict()
        else:
            return 'Import ok',dict(autoDestroy=2)
    
    def table_script_parameters_pane(self,pane,**kwargs):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.numberTextBox(value='^.how_many',lbl='!!How many',default_value=200)
        fb.checkbox(value='^.commit_row',label='!!Commit on row')
        
    def _startLog(self):
        logdir = os.path.join(self.db.application.instanceFolder, 'logs')
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        logfile = os.path.join(logdir, 'gnrtrdaemon.log')
        loghandler = TimedRotatingFileHandler(logfile, 'MIDNIGHT', 1, 28)
        loghandler.setLevel(logging.DEBUG)
        formatter = Formatter('%(asctime)s - %(name)-12s: %(levelname)-8s %(message)s')
        loghandler.setFormatter(formatter)

        rootlogger = logging.getLogger('')
        rootlogger.setLevel(logging.DEBUG)
        rootlogger.addHandler(loghandler)
        if 'admin' in self.db.packages:
            self.db.package('admin').mailLog(self.processName)

    def checkTransactions(self, notify=None):
        print "Checking -- [%i-%i-%i %02i:%02i:%02i]" % (time.localtime()[:6])
        try:
            todo = True
            while todo:
                self._doNoQueue()
                todo = self._doQueue()
        except:
            config = self.config
            tb_text = errorLog(self.processName)
            gnrlogger.error(tb_text)
            raise
        return self.running



