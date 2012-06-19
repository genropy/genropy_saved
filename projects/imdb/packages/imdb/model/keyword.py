# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('keyword', pkey='id', name_long='keyword')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('keyword', _childname ='columns.keyword', dtype ='T', name_long ='!!Keyword', notnull ='y')  
        tbl.column('phonetic_code', _childname ='columns.phonetic_code', dtype ='A', name_long ='!!Phonetic_Code', size ='0:5')  
