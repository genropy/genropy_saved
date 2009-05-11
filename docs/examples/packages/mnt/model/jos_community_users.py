# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_users',  pkey='userid',name_long='jos_community_users')
        tbl.column('userid', dtype ='I', name_long ='!!Userid', notnull ='y')  
        tbl.column('status', dtype ='T', name_long ='!!Status', notnull ='y')  
        tbl.column('points', dtype ='I', name_long ='!!Points', notnull ='y')  
        tbl.column('posted_on', dtype ='DH', name_long ='!!Posted_On', notnull ='y')  
        tbl.column('avatar', dtype ='T', name_long ='!!Avatar', notnull ='y')  
        tbl.column('thumb', dtype ='T', name_long ='!!Thumb', notnull ='y')  
        tbl.column('invite', dtype ='I', name_long ='!!Invite', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
        tbl.column('view', dtype ='I', name_long ='!!View', notnull ='y')  
        tbl.column('friendcount', dtype ='I', name_long ='!!Friendcount', notnull ='y')  
