# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('staff', pkey='id', name_long='!!Staff',
                        name_plural='!!Staff')
        self.sysFields(tbl)
        tbl.column('user_id', size='22', group='_', name_long='!!User').relation('adm.user.id', mode='foreignkey',
                                                                                 onDelete='cascade')
        tbl.column('roles', name_long='!!Role', indexed='y')
        