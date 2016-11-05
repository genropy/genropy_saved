#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('pkginfo', pkey='pkgid', name_long='!!Package info', name_plural='!!Package info',caption_field='pkgid')
        self.sysFields(tbl,id=False)
        tbl.column('pkgid' ,size=':30',name_long='!!Package')
        tbl.column('prj' ,size=':50',name_long='!!Project')