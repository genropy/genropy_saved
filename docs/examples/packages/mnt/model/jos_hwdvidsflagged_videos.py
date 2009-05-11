# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdvidsflagged_videos',  pkey='id',name_long='jos_hwdvidsflagged_videos')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('username', dtype ='A', name_long ='!!Username', size ='0:250')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid', notnull ='y')  
        tbl.column('videoid', dtype ='I', name_long ='!!Videoid')  
        tbl.column('status', dtype ='A', notnull ='y', size ='0:250', name_long ='!!Status')  
        tbl.column('ignore', dtype ='I', name_long ='!!Ignore', notnull ='y')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
