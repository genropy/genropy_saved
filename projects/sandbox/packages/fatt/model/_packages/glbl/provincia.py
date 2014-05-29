#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('provincia')
        tbl.column('testpycon')

    def trigger_onUpdating(self,record,old_record):
        print 'ciao',record['sigla']