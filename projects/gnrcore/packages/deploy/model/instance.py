#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('instance', pkey='id', name_long='!!Instance', name_plural='!!Instance')
        self.sysFields(tbl)
        tbl.column('code' , size=':20',name_long='!!Code')
        tbl.column('description',name_long='!!Description')
        tbl.column('host_id', size='22').relation('deploy.host.id', mode='foreignkey',
                                                                  relation_name='instances')
        tbl.column('packages', dtype='X')
        