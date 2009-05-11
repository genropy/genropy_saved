# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdpslogs_archive',  pkey='id',name_long='jos_hwdpslogs_archive')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('videoid', dtype ='A', name_long ='!!Videoid', size ='0:250')  
        tbl.column('views', dtype ='I', name_long ='!!Views', notnull ='y')  
        tbl.column('number_of_votes', dtype ='I', name_long ='!!Number_Of_Votes', notnull ='y')  
        tbl.column('sum_of_votes', dtype ='I', name_long ='!!Sum_Of_Votes', notnull ='y')  
        tbl.column('rating', dtype ='I', name_long ='!!Rating', notnull ='y')  
        tbl.column('favours', dtype ='I', name_long ='!!Favours', notnull ='y')  
