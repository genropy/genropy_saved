# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('annotation_type',pkey='id',name_long='!!Annotation type',
                            name_plural='!!Annotation types',caption_field='description')
        self.sysFields(tbl,df=True,counter=True)
        tbl.column('code',size=':30',name_long='!!Code')
        tbl.column('description',name_long='!!Description')
        tbl.column('restrictions',name_long='!!Restrictions')
        tbl.column('background_color',name_long='!!Background')
        tbl.column('color',name_long='!!Text color')
        tbl.column('reserved',dtype='B',name_long='!!Reserved')

    def sysRecord_ACT_CONFIRMED(self):
        return self.newrecord(code='ACT_CONFIRMED',description='Action Confirmed',reserved=True)

    def sysRecord_ACT_CANCELLED(self):
        return self.newrecord(code='ACT_CANCELLED',description='Action Cancelled',reserved=True)

    def sysRecord_ACT_RESCHEDULED(self):
        return self.newrecord(code='ACT_RESCHEDULED',description='Action Rescheduled',reserved=True)



    def systemAnnotations(self):
        return ['ACT_CONFIRMED','ACT_CANCELLED','ACT_RESCHEDULED']



