# encoding: utf-8

import logging

gnrlogger = logging.getLogger('gnr')
from gnr.core.gnrlang import errorLog
from datetime import datetime
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import metadata

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('transaction', name_short='Transaction', pkey='id')
        tbl.column('id', size='22')
        tbl.column('request', 'DH', notnull='y', indexed='y')
        tbl.column('execution_start', 'DH', indexed='y')
        tbl.column('execution_end', 'DH', indexed='y')
        tbl.column('mode', size='12')
        tbl.column('action', size='12')
        tbl.column('implementor', size='0:200')
        tbl.column('maintable', size='0:200')
        tbl.column('data', dtype='X',notnull='y')
        tbl.column('error_id', size='0:22', indexed='y').relation('gnr.error.id')
        tbl.column('request_id', size='0:22', indexed='y')
        tbl.column('request_ts', 'DH')
        tbl.column('user_id', size='0:20', indexed='y')
        tbl.column('session_id', size='0:22', indexed='y')
        tbl.column('user_ip', size='0:300')
        tbl.column('file_name')
        tbl.column('queue_id', size='0:22', indexed='y')


    def transactionsToExpand(self,limit=200):
        stoppedQueues = self.query(columns='$queue_id',where="$error_id IS NOT NULL AND $queue_id IS NOT NULL").fetch()

        stoppedQueues = [r[0] for r in stoppedQueues]
        stoppedQuery = ""
        if stoppedQueues:
            stoppedQuery = "AND (NOT ($queue_id IN :stoppedQueues ))"
        return self.query(columns='*',where="""($execution_start IS NULL) %s""" % stoppedQuery,
                        for_update=True,bagFields=True,
                        stoppedQueues=stoppedQueues,order_by="$request", limit=limit).fetch()

    def expandTransaction(self, transaction):
        trargs = {'id': transaction['id'], 'execution_start': datetime.now()}
        

        try:
            tablepath = transaction['maintable']
            data = Bag(transaction['data']) 
            action = transaction['action'].strip()
            mode = transaction['mode'].strip()
            gnrlogger.info("%s -> %s" % (action, tablepath))
            if mode == 'import':
                self.do_import(data, tablepath)
            elif mode == 'sync':
                pkg, table = tablepath.split('.', 1)
                self.do_sync_trigger(data, pkg, table, action)
            else:
                raise "unknown mode: '%s' %s" % (str(mode), str(mode == 'import'))

            trargs['execution_end'] = datetime.now()
            #self.db.execute("UPDATE gnr.gnr_transaction SET execution_start=:ts_start, execution_end=:ts_end WHERE id=:id;", ts_end=datetime.now(), **trargs)
            self.update(trargs,old_record=transaction)
           # self.db.commit() # actually commit only modification to the transaction. do_ methods commits by themself
            result = True
        except :
            self.db.rollback()

            errtbl = self.db.table('gnr.error')
            errid = errtbl.newPkeyValue()
            trargs['error_id'] = errid
            trargs['execution_end'] = datetime.now()

            #self.db.execute("UPDATE gnr.gnr_transaction SET error_id=:err_id, execution_start=:ts_start, execution_end=:ts_end WHERE id=:id;", err_id=err_id, ts_end=ts_end, **trargs)
            self.update(trargs,old_record=transaction)
            tb_text = errorLog('transaction daemon')
            gnrlogger.error(tb_text)

            #self.db.execute("INSERT INTO gnr.gnr_error (id, ts, data) VALUES (:id, :ts, :data);", id=err_id, ts=ts_end, data=tb_text)
            errtbl.insert(dict(id=errid, ts=trargs['execution_end'], data=tb_text))
            result = False
        return result


    def do_import(self, data, tablepath):
        tblobj= self.db.table(tablepath)
        for record_data in data.values():
            if record_data:
                tblobj.insertOrUpdate(record_data.asDict(ascii=True, lower=True))

    def do_sync_trigger(self, data, pkg, table, action):
        record_data = data.pop('data')
        if not record_data:
            return
        record_data = record_data.asDict(ascii=True, lower=True)
        for tr, attr in data.digest('#v,#a'):
            from_attr = attr['from'].lower()
            if '.' in from_attr:
                sub_pkg, sub_table = from_attr.split('.', 1)
            else:
                sub_pkg = pkg
                sub_table = from_attr
            self.do_sync_trigger(tr, sub_pkg, sub_table, attr['mode'])
        self.do_trigger(record_data, '%s.%s' % (pkg, table), action)

    def do_trigger(self, data, tablepath, action):
        tblobj = self.db.table(tablepath)
        if action == 'INS':
            tblobj.insertOrUpdate(data)
        elif action == 'UPD':
            tblobj.insertOrUpdate(data)
        elif action == 'DEL':
            tblobj.delete(data)

    @metadata(doUpdate=True)
    def touch_reset_execution_start(self,record,old_record=None,**kwargs):
        record['execution_start'] = None