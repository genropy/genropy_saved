# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_groups',  pkey='id',name_long='jos_community_groups')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('ownerid', dtype ='I', name_long ='!!Ownerid', notnull ='y')  
        tbl.column('categoryid', dtype ='I', name_long ='!!Categoryid', notnull ='y')  
        tbl.column('name', size ='0:255', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('description', dtype ='T', name_long ='!!Description', notnull ='y')  
        tbl.column('email', size ='0:255', dtype ='A', name_long ='!!Email', notnull ='y')  
        tbl.column('website', size ='0:255', dtype ='A', name_long ='!!Website', notnull ='y')  
        tbl.column('approvals', dtype ='I', name_long ='!!Approvals', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('avatar', dtype ='T', name_long ='!!Avatar', notnull ='y')  
        tbl.column('thumb', dtype ='T', name_long ='!!Thumb', notnull ='y')  
        tbl.column('discusscount', dtype ='I', name_long ='!!Discusscount', notnull ='y')  
        tbl.column('wallcount', dtype ='I', name_long ='!!Wallcount', notnull ='y')  
        tbl.column('membercount', dtype ='I', name_long ='!!Membercount', notnull ='y')  
