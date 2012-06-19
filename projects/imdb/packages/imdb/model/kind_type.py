# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('kind_type', pkey='id', name_long='!!Kind type',
                  name_plural='!!Kind types',rowcaption='$kind',caption_field='kind')
        tbl.column('id',  dtype ='I', notnull ='y', name_long ='!!Id',group='_')  
        tbl.column('kind',  dtype ='A', notnull ='y', size ='0:15', name_long ='!!Kind')  
