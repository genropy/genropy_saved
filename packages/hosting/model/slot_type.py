# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('slot_type',pkey='code',name_long='!!Slot type',
                      name_plural='!!Slot types')
        self.sysFields(tbl)
        tbl.column('code',size=':12',name_long='!!Code')
        tbl.column('description',name_long='!!Description')        