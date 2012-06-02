# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('transaction',  name_short='Transaction', pkey='id')
        tbl.column('id', size='22')
        tbl.column('request', 'DH', notnull='y', indexed='y')
        tbl.column('execution_start', 'DH', indexed='y')
        tbl.column('execution_end', 'DH', indexed='y')
        tbl.column('mode', size='12')
        tbl.column('action', size='12')
        tbl.column('implementor', size='0:200')
        tbl.column('maintable', size='0:200')
        tbl.column('data', notnull='y')
        tbl.column('error_id',  size='0:22', indexed='y').relation('gnr.error.id')
        tbl.column('request_id', size='0:22', indexed='y')
        tbl.column('request_ts', 'DH')
        tbl.column('user_id', size='0:20', indexed='y')
        tbl.column('session_id', size='0:22', indexed='y')
        tbl.column('user_ip', size='0:300')
        tbl.column('file_name')
        tbl.column('queue_id', size='0:22', indexed='y')
