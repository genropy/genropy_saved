#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('public_key', pkey='id', name_long='Public key', name_plural='!!Public keys')
        self.sysFields(tbl)
        tbl.column('person_id',size='22' ,group='_',name_long='!!Person').relation('person.id',relation_name='public_keys',mode='foreignkey',onDelete='raise')
        tbl.column('public_key',name_long='!!Public key')
