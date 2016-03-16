# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('action_type',pkey='id',name_long='!!Action type',name_plural='!!Action types',caption_field='name')
        self.sysFields(tbl,df=True,counter=True)
        tbl.column('name',name_long='Name')
        tbl.column('restrictions',name_long='Restrictions')
        tbl.column('code',size=':10',name_long='Code')
        tbl.column('default_priority',size=':2',name_long='!!Priority',values='NW:Now,UR:Urgent,HG:High,LW:Low')
        tbl.column('default_days_before',dtype='I',name_long='!!Days before')
