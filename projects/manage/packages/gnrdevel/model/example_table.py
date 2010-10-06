# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('example', rowcaption='hello_code')
        tbl.column('hello_code',size='4',name_long='!!Hello code') # char(4)
        tbl.column('hello_value',size=':4',name_long='!!Hello value') # varchar(40)
        tbl.column('hello_date', dtype='D',name_long='!!Hello date') # date
        # dtype -> sql
        #   I       int
        #   R       float
        #   DH      datetime
        #   H       time
