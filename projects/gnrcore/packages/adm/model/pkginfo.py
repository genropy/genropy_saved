#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('pkginfo', pkey='pkg', name_long='!!Package info', name_plural='!!Package info',caption_field='pkg')
        self.sysFields(tbl)
        tbl.column('pkg' ,size=':30',name_long='!!Package')
        tbl.column('prj' ,size=':50',name_long='!!Project')