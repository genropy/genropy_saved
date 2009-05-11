# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdvidsgroup_videos',  pkey='id',name_long='jos_hwdvidsgroup_videos')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('videoid', dtype ='I', name_long ='!!Videoid')  
        tbl.column('groupid', dtype ='I', name_long ='!!Groupid')  
        tbl.column('memberid', dtype ='I', name_long ='!!Memberid')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('video_status', dtype ='A', name_long ='!!Video_Status', size ='0:255')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
