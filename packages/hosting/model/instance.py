#!/usr/bin/env python
# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('instance', rowcaption='')
        self.sysFields(tbl)
        
        tbl.column('name',size=':10',name_long='!!Instance Name')
        tbl.column('path',dtype='T',name_long='!!Instance Path')
        tbl.column('hello_date', dtype='D',name_long='!!Hello date') # date
        # dtype -> sql
        #   I       int
        #   R       float
        #   DH      datetime
        #   H       time