#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('element', rowcaption='$hierarchical_name',caption_field='name',
                        pkey='id', name_long='!!Element',name_plural='!!Elements')
        self.sysFields(tbl,hierarchical='name')
        tbl.column('name',name_long='!!Name')
        tbl.column('system_code',name_long='!!System code')
        tbl.column('long_description',name_long='!!Long Description')
        tbl.column('example_link',name_long='!!Example code')
        tbl.column('external_link',name_long='!!Exernal link')