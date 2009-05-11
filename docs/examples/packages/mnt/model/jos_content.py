# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_content',  pkey='id',name_long='jos_content')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('title', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Title')  
        tbl.column('alias', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Alias')  
        tbl.column('title_alias', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Title_Alias')  
        tbl.column('introtext', dtype ='T', name_long ='!!Introtext', notnull ='y')  
        tbl.column('fulltext', dtype ='T', name_long ='!!Fulltext', notnull ='y')  
        tbl.column('state', dtype ='I', name_long ='!!State', notnull ='y')  
        tbl.column('sectionid', dtype ='I', name_long ='!!Sectionid', notnull ='y')  
        tbl.column('mask', dtype ='I', name_long ='!!Mask', notnull ='y')  
        tbl.column('catid', dtype ='I', name_long ='!!Catid', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('created_by', dtype ='I', name_long ='!!Created_By', notnull ='y').relation('jos_gusers.id',many_name='Utente',one_name='Contenuti')
        tbl.column('created_by_alias', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Created_By_Alias')  
        tbl.column('modified', dtype ='DH', name_long ='!!Modified', notnull ='y')  
        tbl.column('modified_by', dtype ='I', name_long ='!!Modified_By', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('publish_up', dtype ='DH', name_long ='!!Publish_Up', notnull ='y')  
        tbl.column('publish_down', dtype ='DH', name_long ='!!Publish_Down', notnull ='y')  
        tbl.column('images', dtype ='T', name_long ='!!Images', notnull ='y')  
        tbl.column('urls', dtype ='T', name_long ='!!Urls', notnull ='y')  
        tbl.column('attribs', dtype ='T', name_long ='!!Attribs', notnull ='y')  
        tbl.column('version', dtype ='I', name_long ='!!Version', notnull ='y')  
        tbl.column('parentid', dtype ='I', name_long ='!!Parentid', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('metakey', dtype ='T', name_long ='!!Metakey', notnull ='y')  
        tbl.column('metadesc', dtype ='T', name_long ='!!Metadesc', notnull ='y')  
        tbl.column('access', dtype ='I', name_long ='!!Access', notnull ='y')  
        tbl.column('hits', dtype ='I', name_long ='!!Hits', notnull ='y')  
        tbl.column('metadata', dtype ='T', name_long ='!!Metadata', notnull ='y')  
