# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('topic',pkey='topic',name_long='Topic',name_plural='Topic',caption_field='topic')
        tbl.column('topic',size=':50',name_long='Topic',unique=True,indexed=True)
