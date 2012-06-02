# encoding: utf-8

class Table(object):
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