#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy app - see LICENSE for details
# module gnrtransaction : Genro transaction agent from  4D db system.
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
from datetime import datetime, timedelta
import time
import logging

gnrlogger = logging.getLogger('gnr')

from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

#gnrlogger = logging.getLogger('gnr.app.gnrtransactiond')

from gnr.core.gnrlang import errorLog
from gnr.core.gnrbag import Bag
from gnr.app.gnrapp import GnrApp

from gnr.sql.gnrsql_exceptions import NotMatchingModelError
from gnr.xtnd.sync4Dtransaction import TransactionManager4D


class GnrAppTransactionAgent(GnrApp):
    def onInited(self):
        self._startLog()
        gnrpkg = self.db.package('gnr')
        self.listen_timeout = int(gnrpkg.getAttr('listen_timeout_seconds', 10)) or 10
        self.running = False
        self.db.inTransactionDaemon = True
        self.checkModel = False
        self.transaction4d = TransactionManager4D(self, 'gnr')
        self.transaction_pkgid = 'gnr'
        self.transaction_tname = '%s.transaction' % self.transaction_pkgid
        self.error_tname = '%s.error' % self.transaction_pkgid
        if self.config['logging.email']:
            mailhost = self.config['logging.email?host'] 
            fromaddr = self.config['logging.email?fromaddr'] 
            toaddr = self.config['logging.email?toaddr'] 
            subject = self.config['logging.email?subject'] 
            username = self.config['logging.email?username'] 
            password = self.config['logging.email?password']
            if username and password:
                credentials = (username, password)
            else:
                credentials = None
            hdlr = logging.SMTPHandler(mailhost, fromaddr, toaddr, subject, credentials=credentials)
            gnrlogger.addHandler(hdlr)

    def _startLog(self):
        logdir = os.path.join(self.instanceFolder, 'logs')
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


    def loop(self):
        if self.checkModel:
            changes = self.db.checkDb()
            if changes:
                raise NotMatchingModelError('\n'.join(self.db.model.modelChanges))
        self.running = True
        self.checkTransactions()
        self.db.listen('gnr_transaction_new', timeout=self.listen_timeout, onNotify=self.checkTransactions,
                       onTimeout=self.checkTransactions)

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

    def _get_processName(self):
        return 'transaction daemon: %s' % self.instanceFolder

    processName = property(_get_processName)


    def _doNoQueue(self):
        l = self.db.table(self.transaction_tname).query(columns='*,$data',
                                                        where="$execution_start IS NULL AND $queue_id IS NULL",
                                                        order_by="$request", limit=200).fetch()
        while l:
            for t in l:
                self.expandTransaction(t)
            l = self.db.table(self.transaction_tname).query(columns='*,$data',
                                                            where="$execution_start IS NULL AND $queue_id IS NULL",
                                                            order_by="$request", limit=200).fetch()

    def _doQueue(self):
        stoppedQueues = self.db.table(self.transaction_tname).query(columns='$queue_id',
                                                                    where="$error_id IS NOT NULL AND $queue_id IS NOT NULL").fetch()

        stoppedQueues = [r[0] for r in stoppedQueues]
        stoppedQuery = ""
        if stoppedQueues:
            stoppedQuery = "AND (NOT ($queue_id IN :stoppedQueues ))"
        l = self.db.table(self.transaction_tname).query(columns='*,$data',
                                                        where="""($execution_start IS NULL)
                                                              AND ($queue_id IS NOT NULL)
                                                              %s""" % stoppedQuery,
                                                        stoppedQueues=stoppedQueues,
                                                        order_by="$request", limit=200).fetch()
        for t in l:
            ok = self.expandTransaction(t)
            if not ok:
                break
        return (len(l) == 200)


    def expandTransaction(self, transaction):
        trargs = {'id': transaction['id'], 'execution_start': datetime.now()}
        print transaction['id']
        try:
            tablepath = transaction['maintable']
            data = Bag(transaction['data'])
            action = transaction['action'].strip()
            mode = transaction['mode'].strip()
            implementor = transaction['implementor']
            if implementor:
                implementor = implementor.strip()
            gnrlogger.info("%s -> %s" % (action, tablepath))
            if mode == 'import':
                self.transaction4d.do_import(data, tablepath)
            elif mode == 'sync':
                pkg, table = tablepath.split('.', 1)
                self.transaction4d.do_sync_trigger(data, pkg, table, action)
            elif implementor:
                self.executeTransaction(implementor, data)
            else:
                raise "unknown mode: '%s' %s" % (str(mode), str(mode == 'import'))

            trargs['execution_end'] = datetime.now()
            #self.db.execute("UPDATE gnr.gnr_transaction SET execution_start=:ts_start, execution_end=:ts_end WHERE id=:id;", ts_end=datetime.now(), **trargs)
            self.db.table(self.transaction_tname).update(trargs)
            self.db.commit() # commit all: before was: actually commit only modification to the transaction. do_ methods commits by themself
            result = True
        except:
            self.db.rollback()

            errtbl = self.db.table(self.error_tname)
            errid = errtbl.newPkeyValue()
            trargs['error_id'] = errid
            trargs['execution_end'] = datetime.now()

            #self.db.execute("UPDATE gnr.gnr_transaction SET error_id=:err_id, execution_start=:ts_start, execution_end=:ts_end WHERE id=:id;", err_id=err_id, ts_end=ts_end, **trargs)
            self.db.table(self.transaction_tname).update(trargs)
            tb_text = errorLog(self.processName)
            gnrlogger.error(tb_text)

            #self.db.execute("INSERT INTO gnr.gnr_error (id, ts, data) VALUES (:id, :ts, :data);", id=err_id, ts=ts_end, data=tb_text)

            errtbl.insert(dict(id=errid, ts=trargs['execution_end'], data=tb_text))
            self.db.commit()
            result = False
        self.db.clearCurrentEnv()
        return result
    
 
 