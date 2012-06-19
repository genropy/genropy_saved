# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('person_info', pkey='id', name_long='person_info')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('person_id', _childname ='columns.person_id', dtype ='I', name_long ='!!Person_Id', notnull ='y').relation('imdb.name.id')
        tbl.column('info_type_id', _childname ='columns.info_type_id', dtype ='I', name_long ='!!Info_Type_Id', notnull ='y').relation('imdb.info_type.id')
        tbl.column('info', _childname ='columns.info', dtype ='T', name_long ='!!Info', notnull ='y')  
        tbl.column('note', _childname ='columns.note', dtype ='T', name_long ='!!Note')  
