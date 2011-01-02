#!/usr/bin/env python
# encoding: utf-8

# form table is the top level table to define the custom form.
# it is the form definition.

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('form', pkey='id', name_long='!!Form', rowcaption='long_name')
        self.sysFields(tbl, id=False)
        tbl.column('id', size='22', group='_', readOnly='y', name_long='Id')
        tbl.column('code', size=':10', name_long='!!Code')
        tbl.column('label', size=':20', name_long='!!Form Label')
        tbl.column('name', 'T', name_long='!!Name')
        tbl.column('pkg_table', size=':40', name_long='!!Package and Table')
        tbl.column('bag_field', size=':30', name_long='!!Bag Field')
        tbl.column('version', size=':30', name_long='!!Version')
        tbl.column('sort_order', size=':5', name_long='!!Sort Order')
        tbl.column('css', 'T', name_long='!!custom css')
