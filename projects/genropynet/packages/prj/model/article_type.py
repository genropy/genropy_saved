# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('article_type',pkey='code',name_long='!!Article type',
                      name_plural='!!Article type')
        self.sysFields(tbl,id=False)
        tbl.column('code',size=':6',name_long='!!Code')
        tbl.column('name',name_long='!!Name')
        tbl.column('description',name_long='!!Description')