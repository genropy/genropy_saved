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
                
    def _datacatalog_fields(self,bag,path=None):
        sub = bag[path]
        sub.setItem('datefield',None,
                dict(caption='Date field',
                rec_type_fld='name_long,name_short,minvalue,maxvalue,tip,dflt',
                dtype='D',rec_type='pkg.table.datefield',datacatalog_path='%s.datefield' %path))

        sub.setItem('textfield',None,
                dict(caption='Text field',
                    rec_type_fld='fld,name_long,name_short,tip,dflt',
                    dtype='T',rec_type='textfield'))
        sub.setItem('decimalfield',None,dict(caption='Decimal field',
                    rec_type_fld='fld,name_long,name_short,minvalue,maxvalue,tip,dflt',
                    dtype='N',rec_type='decimalfield',datacatalog_path='%s.decimalfield' %path))
        sub.setItem('intfield',None,
                    dict(caption='Int field',
                        rec_type_fld='fld,name_long,name_short,minvalue,maxvalue,tip,dflt',
                        dtype='L',rec_type='intfield',datacatalog_path='%s.intfield' %path))
        sub.setItem('relationfield',None,
                    dict(caption='Relation field',
                        rec_type_fld='fld,name_long,name_short,ext_ref',
                        dtype='T',default_field_size=22,rec_type='relationfield',datacatalog_path='%s.relationfield' %path))
                        
    def datacatalog_rec_types(self):
        result = Bag()
        result.setItem('pkg',None,dict(caption='Package',rec_type_fld='pkg,name_long,name_short',datacatalog_path='pkg',rec_type='pkg'))
        result.setItem('pkg.table',Bag(),dict(caption='Table',rec_type_fld='table,pkey_field,name_long,name_short',
                                                datacatalog_path='pkg.table',rec_type='table',default_pkey_field='id'))
        self._datacatalog_fields(result,path='pkg.table')
        result.setItem('pkg.table.fieldgroup',Bag(),dict(caption='Field group',rec_type_fld='name_long,name_short,dflt'),rec_type='pkg.table.fieldgroup')
        self._datacatalog_fields(result,path='pkg.table.fieldgroup')
        return result
        
    
    def package_record(self,code,name,attr):
        record = dict(child_code=code,parent_code=None,name_long=attr.get('name_long'),name_full=attr.get('name_full'),
                      name_short=attr.get('name_short'),rec_type='pkg',pkg=name)
        return record
    
    def table_record(self,code,parent_code,name,attr):
        record = dict(child_code=code,parent_code=parent_code,name_long=attr.get('name_long'),name_full=attr.get('name_full'),
                      name_short=attr.get('name_short'),pkey_field=attr.get('pkey'),
                      rec_type='tbl',tbl=name)
        return record
    
    def col_record(self,code,parent_code,name,attr,obj):
        record = dict(child_code=code,parent_code=parent_code,name_long=attr.get('name_long'),name_full=attr.get('name_full'),
                      name_short=attr.get('name_short'),size=attr.get('size'),fld=name)
        
        dtype = attr['dtype']
        record['dtype'] = dtype
        if dtype=='N':
            rec_type='decimalfield'
            record['min_value'] = attr.get('min')
            record['max_value'] = attr.get('max')
        elif dtype=='L':
            rec_type='intfield'
            record['min_value'] = attr.get('min')
            record['max_value'] = attr.get('max')
        else:
            rec_type = 'textfield'
        if obj.relatedColumn():
            rec_type = 'relationfield'
            print x
            record['ext_ref'] = obj.relatedColumn()
        record['rec_type'] = rec_type
        return record
        
        
    