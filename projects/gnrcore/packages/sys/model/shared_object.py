# encoding: utf-8

from __future__ import print_function
from builtins import object
from gnr.core.gnrbag import Bag
from datetime import datetime

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('shared_object', pkey='id', name_long='!!Shared Object', name_plural='Shared objects')
        self.sysFields(tbl)
        tbl.column('data', 'X', name_long='!!Data')
        tbl.column('backup', 'X', name_long='!!Backup')
        tbl.column('description', size=':50', name_long='Code', indexed=True)
        tbl.column('linked_table', name_long='!!Table')

    def saveSharedObject(self, shared_id, shared_data, backup=None, linked_table=None, description=None):
        with self.recordToUpdate(shared_id, insertMissing=True) as record:
            if not record['id']:
                record['linked_table']=linked_table
                record['description']= description
            if backup:
                if not record['backup']:
                    record['backup'] =  Bag()
                    n = 0
                else:
                    n = int(list(record['backup'].keys())[-1].split('_')[1])+1
                record['backup'].setItem('v_%s' % n, record['data'], ts=datetime.now())
                if len (record['backup']) > backup:
                    record['backup'].popNode('#0')
            record['data'] = shared_data
            print('UPDATED DATA WITH', shared_data)

    def loadSharedObject(self, shared_id, version=None):
        record = self.record(shared_id).output('bag')
        if not version:
            return record['data']
        else:
            return record['backup'].getItem('v_%i'% version)


