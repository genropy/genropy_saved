#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('provincia')
        tbl.column('mill_si',dtype='L',name_long=u'!!Mill.Sì')
        tbl.column('mill_no',dtype='L',name_long=u'!!Mill.No')
        tbl.column('mill_ast',dtype='L',name_long=u'!!Mill.Ast.')