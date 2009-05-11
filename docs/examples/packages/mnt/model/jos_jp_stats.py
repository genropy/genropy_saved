# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jp_stats',  pkey='id',name_long='jos_jp_stats')
        tbl.column('id', dtype ='L', name_long ='!!Id', notnull ='y')  
        tbl.column('description', size ='0:255', dtype ='A', name_long ='!!Description', notnull ='y')  
        tbl.column('comment', dtype ='T', name_long ='!!Comment')  
        tbl.column('backupstart', dtype ='DH', name_long ='!!Backupstart', notnull ='y')  
        tbl.column('backupend', dtype ='DH', name_long ='!!Backupend', notnull ='y')  
        tbl.column('status', dtype ='A', notnull ='y', size ='0:8', name_long ='!!Status')  
        tbl.column('origin', dtype ='A', notnull ='y', size ='0:8', name_long ='!!Origin')  
        tbl.column('type', dtype ='A', notnull ='y', size ='0:11', name_long ='!!Type')  
        tbl.column('profile_id', dtype ='L', name_long ='!!Profile_Id', notnull ='y')  
        tbl.column('archivename', dtype ='T', name_long ='!!Archivename')  
        tbl.column('absolute_path', dtype ='T', name_long ='!!Absolute_Path')  
