#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('host', pkey='id', name_long='!![it]Host', name_plural='!![it]hosts')
        self.sysFields(tbl)
        tbl.column('code' ,size='10',name_long='!![it]Code') #contatore
        tbl.column('name' , size=':20',name_long='!![it]Name')
        tbl.column('description',name_long='!![it]Description')
        tbl.column('webserver', values='uwsgi,apache')
        tbl.column('genro_branch', values='master,develop')
        tbl.column('address')
        tbl.column('ssh_command')
        tbl.column('admin_user')
        tbl.column('admin_pwd')