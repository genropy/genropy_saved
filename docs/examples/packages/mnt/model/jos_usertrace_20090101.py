# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_usertrace_20090101',  pkey='id',name_long='jos_usertrace_20090101')
        tbl.column('id', dtype ='L', name_long ='!!Id', notnull ='y')  
        tbl.column('username', size ='0:25', dtype ='A', name_long ='!!Username', notnull ='y')  
        tbl.column('userip', size ='0:15', dtype ='A', name_long ='!!Userip', notnull ='y')  
        tbl.column('useragent', dtype ='T', name_long ='!!Useragent', notnull ='y')  
        tbl.column('userurl', dtype ='T', name_long ='!!Userurl', notnull ='y')  
        tbl.column('userreferer', dtype ='T', name_long ='!!Userreferer', notnull ='y')  
        tbl.column('date', size ='0:8', dtype ='A', name_long ='!!Date', notnull ='y')  
        tbl.column('time', size ='0:8', dtype ='A', name_long ='!!Time', notnull ='y')  
