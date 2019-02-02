# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('language',pkey='code',name_long='Language',name_plural='Languages',caption_field='code',lookup=True)
        self.sysFields(tbl,id=False)
        tbl.column('code',size=':2',name_long='Code',unique=True,indexed=True)
        tbl.column('name',size=':50',name_long='Name',unique=True,indexed=True)
