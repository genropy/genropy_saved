# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_shoutbox',  pkey='id',name_long='jos_shoutbox')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('time', dtype ='I', name_long ='!!Time', notnull ='y')  
        tbl.column('name', size ='0:25', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('text', dtype ='T', name_long ='!!Text', notnull ='y')  
        tbl.column('url', size ='0:225', dtype ='A', name_long ='!!Url', notnull ='y')  
        tbl.column('ip', size ='0:255', dtype ='A', name_long ='!!Ip', notnull ='y')  
