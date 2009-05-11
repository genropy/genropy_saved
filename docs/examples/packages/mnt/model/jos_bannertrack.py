# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_bannertrack',  pkey='None',name_long='jos_bannertrack')
        tbl.column('track_date', dtype ='D', name_long ='!!Track_Date', notnull ='y')  
        tbl.column('track_type', dtype ='I', name_long ='!!Track_Type', notnull ='y')  
        tbl.column('banner_id', dtype ='I', name_long ='!!Banner_Id', notnull ='y')  
