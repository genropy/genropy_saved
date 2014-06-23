#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrlang import getUuid

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tag', pkey='id', name_long='!!Tag', rowcaption='tagname')
        self.sysFields(tbl, md5=True)
        tbl.column('id', size='22', group='_', readOnly='y', name_long='Id')
        tbl.column('tagname', size=':32', name_long='!!Tagname')
        tbl.column('isreserved', 'B', name_long='!!Reserved')
        tbl.column('description', name_long='!!Description')

