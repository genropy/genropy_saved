#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('py_package', pkey='id', name_long='Package', name_plural='!!Packages',caption_field='name')
        self.sysFields(tbl, hierarchical='name')
        tbl.column('name' ,name_long='!!Name',name_short='name')
        tbl.column('docline', name_long='!!Docline')