# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_fields_values',  pkey='id',name_long='jos_community_fields_values')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id', notnull ='y').relation('jos_users.id',many_name='Utenti',one_name='Utente')  
        tbl.column('field_id', dtype ='I', name_long ='!!Field_Id', notnull ='y').relation('jos_community_fields.id',many_name='Campo Extra',one_name='Nome campo')  
        tbl.column('value', dtype ='T', name_long ='!!Value', notnull ='y')  
