# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('cd', pkey='id', name_long='!!Cd copy',
                        name_plural='!!Cd copies')
        self.sysFields(tbl)
        tbl.column('album', size='22', group='_').relation('album.id', mode='foreignkey', onDelete='cascade')
        tbl.column('price', 'N', name_long='!!Price')
        tbl.column('edition', name_long='!!Edition')
        
