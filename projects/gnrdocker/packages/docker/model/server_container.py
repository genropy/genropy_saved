#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('server_container', pkey='id', name_long='!!Server container', name_plural='!!Server containers')
        self.sysFields(tbl)
        tbl.column('container_id',size='22' ,group='_',name_long='!!Container').relation('container.id',relation_name='server_container',mode='foreignkey',onDelete='raise')
        tbl.column('server_id',size='22' ,group='_',name_long='!!Server').relation('server.id',relation_name='container_server',mode='foreignkey',onDelete='raise')