#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('element_type', rowcaption='$hierarchical_name',caption_field='hierarchical_name', pkey='id', 
                                        name_long='!!Element type',name_plural='!!Element types')
        self.sysFields(tbl,hierarchical='name')
        tbl.column('name',name_long='!!Name')