# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_eventlist_groups',  pkey='id',name_long='jos_eventlist_groups')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:150', name_long ='!!Name')  
        tbl.column('description', dtype ='T', name_long ='!!Description', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
