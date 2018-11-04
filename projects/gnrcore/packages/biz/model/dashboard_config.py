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

    def hosting_copyToInstance_onSelectedSourceRows(self,source_instance=None,dest_instance=None,source_rows=None):
        userobjects = []
        for r in source_rows:
            data = Bag(r['data'])
            userobjects += filter(lambda r: r, data['items'].digest('#v.parameters.userobject_id'))
        
        self.db.table('adm.userobject').hosting_copyToInstance(source_instance=source_instance,
                                        dest_instance=dest_instance,where='$id IN :pk',pk=userobjects)