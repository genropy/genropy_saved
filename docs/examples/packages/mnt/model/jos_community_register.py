# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_register',  pkey='id',name_long='jos_community_register')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('token', size ='0:200', dtype ='A', name_long ='!!Token', notnull ='y')  
        tbl.column('name', size ='0:255', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('username', size ='0:150', dtype ='A', name_long ='!!Username', notnull ='y')  
        tbl.column('email', size ='0:100', dtype ='A', name_long ='!!Email', notnull ='y')  
        tbl.column('password', size ='0:100', dtype ='A', name_long ='!!Password', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created')  
