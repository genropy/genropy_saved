#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('comune')
        tbl.column('voto_si',dtype='B',name_long=u'!!Sì')
        tbl.column('voto_no',dtype='B',name_long='!!No')
        tbl.column('voto_astenuto',dtype='B',name_long='!!Astenuto')