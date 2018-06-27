#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('instance', pkey='id', name_long='!![it]Instance', name_plural='!![it]Instance')
        self.sysFields(tbl)
        tbl.column('code' , size=':20',name_long='!![it]Code')
        tbl.column('description',name_long='!![it]Description')
        tbl.column('host_id', size='22').relation('deploy..id', mode='foreignkey',
                                                                            relation_name='instances')
        tbl.column('packages', dtype='X')
        