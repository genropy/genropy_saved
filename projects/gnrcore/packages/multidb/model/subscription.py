# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('subscription',pkey='id',name_long='!!Subscription',
                      name_plural='!!Subscriptions')
        self.sysFields(tbl)
        tbl.column('package',name_long='!!Package')
        tbl.column('tablename',name_long='!!Tablename')
        tbl.column('rec_pkey',name_long='!!Pkey')
        tbl.column('store_name',name_long='!!Store')