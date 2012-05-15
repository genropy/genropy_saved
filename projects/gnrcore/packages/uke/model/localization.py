# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('localization',pkey='code',name_long='!!Localization',
                      name_plural='!!Localization')
        self.sysFields(tbl,id=False)
        tbl.column('code',name_long='!!Code')
        tbl.column('topic',name_long='!!Topic')
        tbl.column('identifier',name_long='!!Identifier')