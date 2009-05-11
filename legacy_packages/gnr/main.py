#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Saverio Porcari on 2007-05-10.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import datetime

from gnr.core.gnrbag import Bag

class Package(object):
    
    def config_attributes(self):
        return dict(sqlschema='gnr', comment='Transaction Manager',name_short='Transaction Manager', reserved='y')

    def config_db(self, pkg):
        transactions = pkg.table('transaction',  name_short='Transaction', pkey='id')
        transactions.column('id', size='22')
        transactions.column('request', 'DH', notnull='y', indexed='y')
        transactions.column('execution_start', 'DH', indexed='y')
        transactions.column('execution_end', 'DH', indexed='y')
        transactions.column('mode', size='12')
        transactions.column('action', size='12')
        transactions.column('implementor', size='0:200')
        transactions.column('maintable', size='0:200')
        transactions.column('data', notnull='y')
        transactions.column('error_id',  size='0:22', indexed='y').relation('gnr.error.id')
        transactions.column('request_id', size='0:22', indexed='y')
        transactions.column('request_ts', 'DH')
        transactions.column('user_id', size='0:20', indexed='y')
        transactions.column('session_id', size='0:22', indexed='y')
        transactions.column('user_ip', size='0:300')
        transactions.column('file_name')
        transactions.column('queue_id', size='0:22', indexed='y')
        
        error = pkg.table('error', name_short='Err', name_long='Error', pkey='id')
        error.column('id', size='22')
        error.column('ts', 'DH', notnull='y')
        error.column('data')
        
        
class Table_sync_out(object):
    def config_db(self, pkg):
        sync_out = pkg.table('sync_out', pkey='id')
        sync_out.column('id', size='22')
        sync_out.column('transaction_id',  size='22', indexed='y').relation('gnr.transaction.id')
        sync_out.column('request', 'DH', notnull='y', indexed='y')
        sync_out.column('client', size='12', notnull='y', indexed='y')
        sync_out.column('action', size='12', notnull='y')
        sync_out.column('maintable', size='0:200', notnull='y')
        sync_out.column('data', notnull='y')
        
    def writeSync(self, sync_out, maintable, action, record_data, transaction_id=None, transaction_request=None, queue_id=None):
        syncdata = {}
        syncdata['transaction_id'] = transaction_id
        syncdata['request'] = transaction_request or datetime.datetime.now()
        syncdata['action'] = action
        syncdata['maintable'] = maintable
        
        if not isinstance(record_data, Bag):
            record_data = Bag(record_data)
        for k in record_data.keys():
            if k.startswith('@'):
                record_data.pop(k)
        syncdata['data'] = record_data.toXml()
        
        for sync_client in sync_out:
            if sync_client != queue_id:
                syncdata['client'] = sync_client
                self.insert(syncdata)
                
if __name__ == '__main__':
    main()

