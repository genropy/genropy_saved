# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('action_type',pkey='id',name_long='!!Action type',name_plural='!!Action types',caption_field='description')
        self.sysFields(tbl,df=True)
        tbl.column('code',size=':10',name_long='Code')
        tbl.column('description',name_long='!!Description')
        tbl.column('extended_description',name_long='!!Extended description')
        tbl.column('restrictions',name_long='!!Restrictions')
        tbl.column('default_priority',size='1',name_long='!!Priority',values='L:[!!Low],M:[!!Medium],H:[!!High]')
        tbl.column('default_tag',name_long='!!Default tag')
        tbl.column('show_to_all_tag',dtype='B',name_long='!!Show to all in Tag')
        tbl.column('deadline_days',dtype='I',name_long='!!Deadline days',name_short='DL.Days')
        tbl.column('background_color',name_long='!!Background')
        tbl.column('color',name_long='!!Text color')
        
        tbl.column('text_template',name_long='!!Text template')
        tbl.column('full_template',dtype='X',group='_',name_long='!!Full template')
        