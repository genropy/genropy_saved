# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_activities_hide',  pkey='None',name_long='jos_community_activities_hide')
        tbl.column('activity_id', dtype ='I', name_long ='!!Activity_Id', notnull ='y')  
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id', notnull ='y')  
