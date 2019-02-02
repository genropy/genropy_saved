#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('pkgtable', pkey='table_identifier', name_long='!!Table', name_plural='!!Table',caption_field='table_identifier')
        self.sysFields(tbl,id=False)
        tbl.column('name',name_long='!!Name')
        tbl.column('description',name_long='!!Description')
        tbl.column('package_identifier',name_long='!!Package identifier').relation('package.package_identifier',relation_name='tables',mode='foreignkey',onDelete='raise')
        tbl.column('table_identifier',name_long='!!Table identifier')


    def trigger_onInserting(self, record_data):
        record_data['table_identifier'] = "%s/%s" %(record_data['package_identifier'],record_data['name'])