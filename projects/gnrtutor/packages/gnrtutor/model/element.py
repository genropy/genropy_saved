#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('element', rowcaption='$hierarchical_name',caption_field='name',
                        pkey='id', name_long='!!Element',name_plural='!!Elements')
        self.sysFields(tbl,hierarchical='name')
        tbl.column('name',name_long='!!Name')
        tbl.column('system_code',name_long='!!System code')