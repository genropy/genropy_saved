# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('annotation_type',pkey='id',name_long='!!Annotation type',name_plural='!!Annotation types',caption_field='name')
        self.sysFields(tbl,df=True,counter=True)
        tbl.column('name',name_long='Name')
        tbl.column('code',size=':10',name_long='Code')
        tbl.column('restrictions',name_long='Restrictions')


