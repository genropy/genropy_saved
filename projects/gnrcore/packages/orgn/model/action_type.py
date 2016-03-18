# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('action_type',pkey='id',name_long='!!Action type',name_plural='!!Action types',caption_field='description')
        self.sysFields(tbl,df=True,counter=True)
        tbl.column('code',size=':10',name_long='Code')
        tbl.column('description',name_long='!!Description')
        tbl.column('extended_description',name_long='!!Extended description')
        tbl.column('restrictions',name_long='!!Restrictions')
        tbl.column('default_priority',size=':2',name_long='!!Priority',values='NW:Now,UR:Urgent,HG:High,LW:Low')
        tbl.column('default_days_before',dtype='I',name_long='!!Days before')
        tbl.column('default_tag',name_long='!!Default tag')

        tbl.column('background_color',name_long='!!Background')
        tbl.column('color',name_long='!!Text color')
        
        tbl.column('text_template',name_long='!!Text template')
        tbl.column('full_template',dtype='X',group='_',name_long='!!Full template')