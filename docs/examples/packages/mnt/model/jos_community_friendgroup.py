# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_friendgroup',  pkey='None',name_long='jos_community_friendgroup')
        tbl.column('group_id', dtype ='I', name_long ='!!Group_Id', notnull ='y')  
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id', notnull ='y')  
