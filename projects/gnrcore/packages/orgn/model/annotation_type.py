# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('annotation_type',pkey='id',name_long='!!Annotation type',
                            name_plural='!!Annotation types',caption_field='description')
        self.sysFields(tbl,df=True,counter=True)
        tbl.column('code',size=':10',name_long='!!Code')
        tbl.column('description',name_long='!!Description')
        tbl.column('restrictions',name_long='!!Restrictions')
        tbl.column('background_color',name_long='!!Background')
        tbl.column('color',name_long='!!Text color')
