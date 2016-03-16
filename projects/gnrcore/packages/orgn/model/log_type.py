# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('log_type',pkey='id',name_long='!!Log type',name_plural='!!Log types',caption_field='name')
        self.sysFields(tbl,hierarchical='name',df=True,counter=True)
        tbl.column('name',name_long='Name')
        tbl.column('code',size=':10',name_long='Code')


