# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('account', rowcaption='account_name', pkey='id', name_long='!!Account', name_plural='!!Account')
        self.sysFields(tbl)
        tbl.column('account_name',size=':30',name_long='!!Account Name')
        tbl.column('full_name',size=':80',name_long='!!Full Name')
        tbl.column('host',size=':80',name_long='!!Host')
        tbl.column('port','L',name_long='!!Port')
        tbl.column('protocol_code',size=':10',name_long='!!TLS').relation('email.protocol.code', mode='foreignkey', relation_name='accounts')
        tbl.column('tls','B',name_long='!!TLS')
        tbl.column('ssl','B',name_long='!!SSL')
        tbl.column('username',size=':80',name_long='!!Username')
        tbl.column('password',size=':80',name_long='!!Password')
        
        
