# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('help',pkey='id',name_long='!!Help',
                      name_plural='!!Help rows',sync=True,sync_topic='package')
        self.sysFields(tbl)
        tbl.column('topic',name_long='!!Topic')
        tbl.column('type',name_long='!!Type',values='F:Fields,R:Resource')
        tbl.column('identifier',name_long='!!Identifier')
        tbl.column('tip',name_long='!!Tip')
        tbl.column('help',name_long='!!Help')
        tbl.column('localizations','X',name_long='!!Localizations')

        
