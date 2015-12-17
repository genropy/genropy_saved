#!/usr/bin/env python
# encoding: utf-8
from redbaron import RedBaron
from importlib import import_module


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('pysource', pkey='id', name_long='!!Py source')
        self.sysFields(tbl,hierarchical='name')
        tbl.column('name',name_long='!!Name')
        tbl.column('rtype' ,size=':10',name_long='!!Block type',
                    values='P:Package,M:Module,C:Class,D:Def')


    def get_redbaron(self,filepath):
        with open(filepath, "r") as f:
            source_code = f.read()
        red = RedBaron(source_code)
        return red
            

    def parseModule(self,hierarchical_name=None):
        filepath = import_module(hierarchical_name.replace('/','.')).__file__.replace('.pyc','.py')
        rb = self.get_redbaron(filepath)
        print x