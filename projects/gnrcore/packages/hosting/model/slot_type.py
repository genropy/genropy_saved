# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('slot_type', pkey='id', name_long='!!Slot type',caption_field='description',
                        name_plural='!!Slot types', hosting_prepopulate=True)
        self.sysFields(tbl)
        tbl.column('code', size=':12', name_long='!!Code')
        tbl.column('description', name_long='!!Description')