# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_friendlist',  pkey='group_id',name_long='jos_community_friendlist')
        tbl.column('group_id', dtype ='I', name_long ='!!Group_Id', notnull ='y')  
        tbl.column('group_name', size ='0:45', dtype ='A', name_long ='!!Group_Name', notnull ='y')  
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id', notnull ='y')  
