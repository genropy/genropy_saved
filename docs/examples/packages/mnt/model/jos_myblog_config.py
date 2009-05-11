# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_config',  pkey='name',name_long='jos_myblog_config')
        tbl.column('name', dtype ='A', notnull ='y', size ='0:64', name_long ='!!Name')  
        tbl.column('value', dtype ='T', name_long ='!!Value', notnull ='y')  
