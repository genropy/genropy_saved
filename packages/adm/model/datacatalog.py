# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable
class Table(GnrHTable):
    def config_db(self, pkg):
        tbl =  pkg.table('datacatalog',  pkey='id',name_long='!!Model catalog',
                      name_plural='!!DC Elements',rowcaption='$description')
        self.sysFields(tbl)
        self.htableFields(tbl)
        tbl.column('dtype',name_long='!!Dtype')
        tbl.column('name_long',name_long='!!Name long')
        tbl.column('name_short',name_long='!!Name short')
        tbl.column('format',name_long='!!Format')
        tbl.column('options',name_long='!!Options')
        tbl.column('maxvalue',name_long='!!Max')
        tbl.column('minvalue',name_long='!!Min')
        tbl.column('dflt',name_long='!!Default')
        tbl.column('tip',name_long='!!Tip')
        tbl.column('purpose',name_long='!!Purpose')
        tbl.column('ext_ref',name_long='!!External referenece')
        tbl.column('pkg',name_long='!!Package')
        tbl.column('tbl',name_long='!!Table')
        
        