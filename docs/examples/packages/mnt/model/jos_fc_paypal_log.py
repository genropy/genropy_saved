# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_paypal_log',  pkey='id',name_long='jos_fc_paypal_log')
        tbl.column('id', dtype ='L', name_long ='!!Id', notnull ='y')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('user_name', dtype ='A', notnull ='y', size ='0:50', name_long ='!!User_Name')  
        tbl.column('txn_id', dtype ='A', notnull ='y', size ='0:25', name_long ='!!Txn_Id')  
        tbl.column('txn_type', dtype ='A', notnull ='y', size ='0:25', name_long ='!!Txn_Type')  
        tbl.column('item_name', dtype ='A', notnull ='y', size ='0:25', name_long ='!!Item_Name')  
        tbl.column('item_number', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Item_Number')  
        tbl.column('post_from', dtype ='A', notnull ='y', size ='0:10', name_long ='!!Post_From')  
        tbl.column('payer_email', dtype ='A', notnull ='y', size ='0:75', name_long ='!!Payer_Email')  
        tbl.column('details', dtype ='T', name_long ='!!Details', notnull ='y')  
        tbl.column('result', dtype ='T', name_long ='!!Result', notnull ='y')  
        tbl.column('paypal_testmode', dtype ='I', name_long ='!!Paypal_Testmode', notnull ='y')  
        tbl.column('gateway', dtype ='I', name_long ='!!Gateway', notnull ='y')  
        tbl.column('instance_id', dtype ='I', name_long ='!!Instance_Id')  
