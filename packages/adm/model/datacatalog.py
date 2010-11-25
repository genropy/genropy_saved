# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable
from gnr.core.gnrbag import Bag
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
        tbl.column('pkey_field',name_long='!!Pkey field')#oppure attr per table pkey?
        tbl.column('field_size',name_long='!!Size')
        tbl.column('tbl',name_long='!!Table')
        tbl.column('fld',name_long='!!Field')
        tbl.column('comment',name_long='!!Comment')
        tbl.column('name_full',name_long='!!Name full')
        tbl.column('datacatalog_path',name_long='!!Datacatalog path')
                        
    def datacatalog_rec_types(self):
        result = Bag()
        for k,handler in [(x[8:],getattr(self,x)) for x in dir(self) if x.startswith('rectype_')]:
            result.setItem(k,None,_attributes=handler())
        return result
    
    def rectype_main(self):
        return dict(children='db_root,root')
    
    def rectype_root(self):
        return dict(children='field,group',caption='Root')
    
    def rectype_field(self):
        return dict(caption='Field')
    
    def rectype_group(self):
        return dict(caption='Group',fields='name_long,name_short')

    def rectype_db_root(self):
        return dict(children='db_pkg',caption='Root Db')
        
    def rectype_db_pkg(self):
        return dict(children='db_tbl,db_tgroup',fields='pkg,name_long,name_short',caption='Package')
    
    def rectype_db_tgroup(self):
        return dict(children='db_tbl',fields='name_long,name_short',caption='Group of table')

    def rectype_db_tbl(self):
        return dict(children='db_field,db_fgroup',fields='tbl,pkey_field,name_long,name_short',caption='Table',default_pkey_field='id')

    def rectype_db_fgroup(self):
        return dict(children='db_field',caption='Group of fields',fields='name_long,name_short')
        
    def rectype_db_field(self):
        return dict(caption='Field',fields='name_long,name_short')
        
    
    def make_record_db_pkg(self,idx=None,parent_code=None,name=None,attr=None):
        record = dict(child_code='P%i' %idx,parent_code=None,name_long=attr.get('name_long'),name_full=attr.get('name_full'),
                      name_short=attr.get('name_short'),rec_type='db_pkg',pkg=name)
        return record
    
    def make_record_db_tbl(self,idx=None,parent_code=None,name=None,attr=None):
        record = dict(child_code='T%i' %idx,parent_code=parent_code,name_long=attr.get('name_long'),name_full=attr.get('name_full'),
                      name_short=attr.get('name_short'),pkey_field=attr.get('pkey'),rec_type='db_tbl',tbl=name)
        return record
    
    def make_record_db_col(self,idx=None,parent_code=None,name=None,attr=None,obj=None):
        record = dict(child_code='F%i' %idx,parent_code=parent_code,name_long=attr.get('name_long'),name_full=attr.get('name_full'),
                      name_short=attr.get('name_short'),size=attr.get('size'),fld=name,dtype=attr.get('dtype'),rec_type='db_field')
        return record
        
        
    