# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('company_type', pkey='id', name_long='company_type',lookup=True)
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('kind', _childname ='columns.kind', dtype ='A', notnull ='y', size ='0:32', name_long ='!!Kind')  
