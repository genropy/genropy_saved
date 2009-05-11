# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jd_gatekeeper',  pkey='None',name_long='jos_jd_gatekeeper')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('ipaddress', size ='0:45', dtype ='A', name_long ='!!Ipaddress', notnull ='y')  
        tbl.column('blocksite', dtype ='I', name_long ='!!Blocksite', notnull ='y')  
        tbl.column('comment', size ='0:255', dtype ='A', name_long ='!!Comment', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
