# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('aka_name', pkey='id', name_long='aka_name')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('person_id', _childname ='columns.person_id', dtype ='I', name_long ='!!Person_Id', notnull ='y')  
        tbl.column('name', _childname ='columns.name', dtype ='T', name_long ='!!Name', notnull ='y')  
        tbl.column('imdb_index', _childname ='columns.imdb_index', dtype ='A', name_long ='!!Imdb_Index', size ='0:12')  
        tbl.column('name_pcode_cf', _childname ='columns.name_pcode_cf', dtype ='A', name_long ='!!Name_Pcode_Cf', size ='0:5')  
        tbl.column('name_pcode_nf', _childname ='columns.name_pcode_nf', dtype ='A', name_long ='!!Name_Pcode_Nf', size ='0:5')  
        tbl.column('surname_pcode', _childname ='columns.surname_pcode', dtype ='A', name_long ='!!Surname_Pcode', size ='0:5')  
        tbl.column('md5sum', _childname ='columns.md5sum', dtype ='A', name_long ='!!Md5Sum', size ='0:32')  
