# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('company',pkey='id',name_long='!!Company',
                      name_plural='!!Company',rowcaption='$code',caption_field='code')
        self.sysFields(tbl)
        tbl.column('code',name_long='!!Code')
        tbl.column('description',name_long='!!Description')