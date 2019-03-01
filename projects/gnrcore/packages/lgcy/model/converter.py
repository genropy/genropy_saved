#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('converter', rowcaption='$code',caption_field='code',name_long='!!Hosting client',name_plural='!!Hosting clients')
        self.sysFields(tbl, __ins_ts=False, __mod_ts=False, __del_ts=False)
        tbl.column('code', size=':80', name_long='!!Legacy code')

    def insertConversionRow(self, tbl, code):
        pass