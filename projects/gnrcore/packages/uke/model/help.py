# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('help',pkey='id',name_long='!!Help',
                      name_plural='!!Help rows')
        self.sysFields(tbl)
        tbl.column('type',name_long='!!Type',values='F:Fields')
        tbl.column('package',name_long='!!Package')
        tbl.column('table',name_long='!!Table')
        tbl.column('tip',name_long='!!Tip')
        tbl.column('help',name_long='!!Help')
