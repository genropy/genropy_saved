#!/usr/bin/env python
# encoding: utf-8


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('localita')
        tbl.column('is_lovely', dtype='B', name_long='Is Lovely')


    def trigger_onInserting(self, record):
        print 'in test15'