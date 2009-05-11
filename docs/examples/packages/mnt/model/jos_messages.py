# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_messages',  pkey='message_id',name_long='jos_messages')
        tbl.column('message_id', dtype ='I', name_long ='!!Message_Id', notnull ='y')  
        tbl.column('user_id_from', dtype ='I', name_long ='!!User_Id_From', notnull ='y')  
        tbl.column('user_id_to', dtype ='I', name_long ='!!User_Id_To', notnull ='y')  
        tbl.column('folder_id', dtype ='I', name_long ='!!Folder_Id', notnull ='y')  
        tbl.column('date_time', dtype ='DH', name_long ='!!Date_Time', notnull ='y')  
        tbl.column('state', dtype ='I', name_long ='!!State', notnull ='y')  
        tbl.column('priority', dtype ='I', name_long ='!!Priority', notnull ='y')  
        tbl.column('subject', dtype ='T', name_long ='!!Subject', notnull ='y')  
        tbl.column('message', dtype ='T', name_long ='!!Message', notnull ='y')  
