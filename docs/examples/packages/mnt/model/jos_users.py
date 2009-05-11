# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_users',  pkey='id',name_long='jos_users',plural='utenti',rowcaption='$username')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Name')  
        tbl.column('username', dtype ='A', notnull ='y', size ='0:150', name_long ='!!Username')  
        tbl.column('email', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Email')  
        tbl.column('password', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Password')  
        tbl.column('usertype', dtype ='A', notnull ='y', size ='0:25', name_long ='!!Usertype')  
        tbl.column('block', dtype ='I', name_long ='!!Block', notnull ='y')  
        tbl.column('sendEmail', dtype ='I', name_long ='!!Sendemail')  
        tbl.column('gid', dtype ='I', name_long ='!!Gid', notnull ='y').relation('jos_groups.id',many_name='Utenti',one_name='Gruppo')
        tbl.column('registerDate', dtype ='DH', name_long ='!!Registerdate', notnull ='y')  
        tbl.column('lastvisitDate', dtype ='DH', name_long ='!!Lastvisitdate', notnull ='y')  
        tbl.column('activation', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Activation')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
