# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_fields',  pkey='id',name_long='Campi extra',rowcaption='$name')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('type', size ='0:255', dtype ='A', name_long ='!!Type', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('min', dtype ='I', name_long ='!!Min', notnull ='y')  
        tbl.column('max', dtype ='I', name_long ='!!Max', notnull ='y')  
        tbl.column('name', size ='0:255', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('tips', dtype ='T', name_long ='!!Tips', notnull ='y')  
        tbl.column('visible', dtype ='I', name_long ='!!Visible')  
        tbl.column('required', dtype ='I', name_long ='!!Required')  
        tbl.column('searchable', dtype ='I', name_long ='!!Searchable')  
        tbl.column('options', dtype ='T', name_long ='!!Options')  
        tbl.column('fieldcode', size ='0:255', dtype ='A', name_long ='!!Fieldcode', notnull ='y')  
