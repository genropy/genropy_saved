#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('dashboard_config', pkey='id', name_long='!!Dash configurations', name_plural='!!Dash configurations')
        self.sysFields(tbl)
        tbl.column('username',size=':40',indexed=True)
        tbl.column('dashboard_key',size=':40', group='_', name_long='!!Dashboard'
                    ).relation('dashboard.dashboard_key', relation_name='user_configurations', mode='foreignkey', onDelete='cascade')
        tbl.column('data', dtype='X', name_long='!!Data')

