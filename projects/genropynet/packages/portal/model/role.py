# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('role', pkey='id', name_long='!!Role',
                        name_plural='!!Roles')
        self.sysFields(tbl)
        tbl.column('description', name_long='!!Description', indexed='y')