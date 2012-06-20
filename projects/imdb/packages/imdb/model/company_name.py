# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('company_name', pkey='id', name_long='!!Company',name_plural='!!Companies',caption_field='name',rowcaption='$name')
        tbl.column('id',  dtype ='I', notnull ='y', name_long ='!!Id',group='_')  
        tbl.column('name',type ='T', name_long ='!!Name', notnull ='y')  
        tbl.column('country_code', dtype ='A', name_long ='!!Country_Code', size ='0:255')  
        tbl.column('imdb_id',  dtype ='I', name_long ='!!Imdb_Id',group='_')  
        tbl.column('name_pcode_nf', dtype ='A', name_long ='!!Name_Pcode_Nf', size ='0:5',group='_')  
        tbl.column('name_pcode_sf', dtype ='A', name_long ='!!Name_Pcode_Sf', size ='0:5',group='_')  
        tbl.column('md5sum',dtype ='A', name_long ='!!Md5Sum', size ='0:32',group='_')  
