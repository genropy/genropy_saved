#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy sql - see LICENSE for details
# module gnrsqlclass : Genro transaction manager
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
import weakref

from datetime import datetime

from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import boolean

#from gnr.core.gnrlog import logging
import logging

gnrlogger = logging.getLogger(__name__)

class TransactionManager4D(object):
    def __init__(self, app, pkgid):
        self.app = app
        self.transaction_pkgid = pkgid
        self.transaction_tname = '%s.transaction' % self.transaction_pkgid
        self.error_tname = '%s.error' % self.transaction_pkgid

    def _get_db(self):
        return self.app.db

    db = property(_get_db)

    def _set_app(self, app):
        if app is None:
            self._app = app
        else:
            self._app = weakref.ref(app)

    def _get_app(self):
        if self._app:
            return self._app()

    app = property(_get_app, _set_app)

    def writeTransaction(self, mode, action, maintable, data,
                         request_id=None, request_ts=None, user_id=None, session_id=None,
                         user_ip=None, queue_id=None, file_name=None):
        kwargs = {}
        trtable = self.db.table(self.transaction_tname)
        kwargs['id'] = trtable.newPkeyValue()
        kwargs['request'] = datetime.now()
        kwargs['mode'] = mode
        kwargs['action'] = action
        kwargs['maintable'] = maintable
        kwargs['request_id'] = request_id
        kwargs['request_ts'] = request_ts
        kwargs['user_id'] = user_id
        kwargs['session_id'] = session_id
        kwargs['user_ip'] = user_ip
        kwargs['queue_id'] = queue_id
        kwargs['file_name'] = file_name

        if not isinstance(data, Bag):
            data = Bag(data)

        for k in data.keys():
            if k.startswith('@'):
                data.pop(k)
        kwargs['data'] = data.toXml()

        if not request_id: # import
            trtable.insert(kwargs)
        else: # sync triggers
            prevTransactions = trtable.query(columns="$id, $error_id",
                                             where="$request_id=:request_id AND $queue_id = :queue_id",
                                             request_id=request_id, queue_id=queue_id).fetch()
            if len(prevTransactions) == 0: # normal case: is a new transaction
                trtable.insert(kwargs)
            elif len(prevTransactions) == 1: # the transaction yet exists
                if prevTransactions[0]['error_id']:
                    kwargs.pop('request') # leave the old request timestamp in order to not alter the execution order
                    trtable.update(kwargs)
                    gnrlogger.warning(
                            "Replacing old wrong transaction %s with new from file %s" % (request_id, file_name))
                else:
                    gnrlogger.error("Skipping duplicated transaction %s from file %s" % (request_id, file_name))
            else:
                gnrlogger.critical("More than one old transactions with id %s from file %s" % (request_id, file_name))
                raise

        self.db.notify("gnr_transaction_new")
        self.db.commit()

    def do_import(self, data, tablepath):
        for record_data in data.values():
            if record_data:
                self.db.table(tablepath).insertOrUpdate(record_data.asDict(ascii=True, lower=True))
        self.db.commit()

    def do_sync_trigger(self, data, pkg, table, action):
        record_data = data.pop('data').asDict(ascii=True, lower=True)
        for tr, attr in data.digest('#v,#a'):
            if '.' in attr['from']:
                sub_pkg, sub_table = attr['from'].split('.', 1)
            else:
                sub_pkg = pkg
                sub_table = attr['from']
            self.do_sync_trigger(tr, sub_pkg, sub_table, attr['mode'])
        self.do_trigger(record_data, '%s.%s' % (pkg, table), action)

    def do_trigger(self, data, tablepath, action):
        if action == 'INS':
            self.db.table(tablepath).insertOrUpdate(data)
        elif action == 'UPD':
            self.db.table(tablepath).insertOrUpdate(data)
        elif action == 'DEL':
            self.db.table(tablepath).delete(data)
        self.db.commit()