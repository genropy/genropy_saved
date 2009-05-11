# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdpsgroup_photos',  pkey='id',name_long='jos_hwdpsgroup_photos')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('photoid', dtype ='I', name_long ='!!Photoid')  
        tbl.column('groupid', dtype ='I', name_long ='!!Groupid')  
        tbl.column('memberid', dtype ='I', name_long ='!!Memberid')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
