#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('host', pkey='id', name_long='Host', name_plural='Hosts')
        self.sysFields(tbl)
        tbl.column('provider' ,size=':10',name_long='!!Provider').relation('deploy.provider.code',
                                                                  mode='foreignkey',
                                                                  relation_name='hosts')
        tbl.column('code' ,size=':25',name_long='!!Code')
        tbl.column('identifier', size=':40',indexed=True,sql_value=":provider||'/'||:code",unique=True)
        tbl.column('name' , size=':30',name_long='!!Name')
        tbl.column('description',name_long='!!Description')
        tbl.column('wsgi_server', size=':10').relation('deploy.wsgi_server', relation_name='hosts')
        tbl.column('address',  size=':20')
        tbl.column('ssh_command', size=':20')
        tbl.column('admin_user',  size=':20')