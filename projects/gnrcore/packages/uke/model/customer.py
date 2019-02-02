# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('customer',pkey='id',name_long='!!Customer',
                      name_plural='!!Customer',rowcaption='$description',caption_field='description')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('description',name_long='!!Description')