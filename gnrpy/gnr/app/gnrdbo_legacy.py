#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
from gnr.app.gnrdbo import GnrDboTable
from gnr.core.gnrdecorator import public_method
         
class GnrHTable(GnrDboTable):
    """A hierarchical table. More information on the :ref:`classes_htable` section"""
    def htableFields(self, tbl):
        """:param tbl: the :ref:`table` object
        
        Create the necessary :ref:`columns` in order to use the :ref:`h_th` component.
        
        In particular it adds:
        
        * the "code" column: TODO
        * the "description" column: TODO
        * the "child_code" column: TODO
        * the "parent_code" column: TODO
        * the "level" column: TODO
        
        You can redefine the first three columns in your table; if you don't redefine them, they
        are created with the following features::
        
            tbl.column('code', name_long='!!Code', base_view=True)
            tbl.column('description', name_long='!!Description', base_view=True)
            tbl.column('child_code', name_long='!!Child code', validate_notnull=True,
                        validate_notnull_error='!!Required', base_view=True,
                        validate_regex=r'!\.', validate_regex_error='!!Invalid code: "." char is not allowed')"""
                        
        columns = tbl['columns'] or []
        broadcast = [] if 'broadcast' not in tbl.attributes else tbl.attributes['broadcast'].split(',')
        broadcast.extend(['code','parent_code','child_code'])
        tbl.attributes['broadcast'] = ','.join(list(set(broadcast)))
        if not 'code' in columns:
            tbl.column('code', name_long='!!Code', base_view=True,unique=True)
        if not 'description' in columns:
            tbl.column('description', name_long='!!Description', base_view=True)
        if not 'child_code' in columns:
            tbl.column('child_code', name_long='!!Child code', validate_notnull=True,
                        validate_notnull_error='!!Required', base_view=True,
                        validate_regex=r'!\.', validate_regex_error='!!Invalid code: "." char is not allowed'
                        #,unmodifiable=True
                        )
        tbl.column('parent_code', name_long='!!Parent code').relation('%s.code' % tbl.parentNode.label,onDelete='cascade')
        tbl.column('level', name_long='!!Level')
        pkgname = tbl.getAttr()['pkg']
        tblname = '%s.%s_%s' % (pkgname, pkgname, tbl.parentNode.label)
        tbl.formulaColumn('child_count',
                          '(SELECT count(*) FROM %s AS children WHERE children.parent_code=#THIS.code)' % tblname,
                           dtype='L', always=True)
        tbl.formulaColumn('hdescription',
                           """
                           CASE WHEN #THIS.parent_code IS NULL THEN #THIS.description
                           ELSE ((SELECT description FROM %s AS ptable WHERE ptable.code = #THIS.parent_code) || '-' || #THIS.description)
                           END
                           """ % tblname)
        
        tbl.formulaColumn('base_caption',"""CASE WHEN $description IS NULL OR $description='' THEN $child_code 
                                             ELSE $child_code ||'-'||$description END""")
        tbl.attributes.setdefault('caption_field','base_caption')
        if not 'rec_type'  in columns:
            tbl.column('rec_type', name_long='!!Type')
            
    
    def htableAutoCode(self,record=None,old_record=None,evt='I'):
        autocode = self.attributes.get('autocode')
        if not autocode:
            return
        
    def trigger_onInserting(self, record_data):
        """TODO
        
        :param record_data: TODO"""
        parent_code = record_data.get('parent_code')
        self.htableAutoCode(record=record_data,evt='I')
        self.assignCode(record_data)
        if not parent_code:
            return
        parent_children = self.readColumns(columns='$child_count',where='$code=:code',code=parent_code)
        if parent_children==0:
            self.touchRecords(where='$code=:code',code=parent_code)
        
    def trigger_onDeleted(self,record,**kwargs):
        parent_code = record.get('parent_code')
        self.htableAutoCode(record=record,evt='I')
        if not parent_code:
            return
        
       # children = self.query(where='$parent_code=:p',p=record['code'],for_update=True).fetch()
       # if children:
       #     for c in children:
       #         self.delete(c)
        
    def assignCode(self, record_data):
        """TODO
        
        :param record_data: TODO"""
        code_list = [k for k in (record_data.get('parent_code') or '').split('.') + [record_data['child_code']] if k]
        record_data['level'] = len(code_list) - 1
        record_data['code'] = '.'.join(code_list)
    
    @public_method
    def reorderCodes(self,pkey=None,into_pkey=None):
        record = self.record(pkey=pkey,for_update=True).output('record')
        oldrecord = dict(record)
        parent_code = self.record(pkey=into_pkey).output('record')['code'] if into_pkey else None
        code_to_test = '%s.%s' %(parent_code,record['child_code']) if parent_code else record['child_code']
        if not self.checkDuplicate(code=code_to_test):
            record['parent_code'] = parent_code
            self.update(record,oldrecord)
            self.db.commit()
            return True
        return False

    def trigger_onUpdating(self, record_data, old_record=None):
        """TODO
        :param record_data: TODO
        :param old_record: TODO"""
        if old_record and ((record_data['child_code'] != old_record['child_code']) or (record_data['parent_code'] != old_record['parent_code'])):
            old_code = old_record['code']
            self.assignCode(record_data)
            parent_code = record_data['code']
            self.batchUpdate(dict(parent_code=parent_code), where='$parent_code=:old_code', old_code=old_code)
            #if parent_code:
            #    parent_children = self.readColumns(columns='$child_count',where='$code=:code',code=parent_code)
            #    if parent_children==0:
            #        self.touchRecords(where='$code=:code',code=parent_code)

            
    def df_getFieldsRows(self,pkey=None,code=None):
        fieldstable = self.db.table(self.attributes.get('df_fieldstable'))
        code = self.readColumns(pkey=pkey,columns='code')
        return fieldstable.query(where="(:code=@maintable_id.code) OR (:code ILIKE @maintable_id.code || '.%%')",
                                    code=code,order_by='@maintable_id.code,$_row_count',columns='*,$wdg_kwargs').fetch()

class DynamicFieldsTable(GnrDboTable):
    """CustomFieldsTable"""
    def config_db(self,pkg):
        tblname = self._tblname
        tbl = pkg.table(tblname,pkey='id')
        mastertbl = '%s.%s' %(pkg.parentNode.label,tblname.replace('_df',''))
        self.df_dynamicFormFields(tbl,mastertbl)

    def df_dynamicFormFields(self,tbl,mastertbl):
        pkgname,mastertblname = mastertbl.split('.')
        tblname = '%s_df' %mastertblname
        assert tbl.parentNode.label == tblname,'table name must be %s' %tblname
        model = self.db.model
        mastertbl =  model.src['packages.%s.tables.%s' %(pkgname,mastertblname)]
        mastertbl.attributes['df_fieldstable'] = '%s.%s' %(pkgname,tblname)
        mastertbl_name_long = mastertbl.attributes.get('name_long')
        mastertbl.column('df_fbcolumns','L',group='_')
        mastertbl.column('df_custom_templates','X',group='_')
        tbl.attributes.setdefault('caption_field','description')
        tbl.attributes.setdefault('rowcaption','$description')
        tbl.attributes.setdefault('name_long','%s dyn field' %mastertbl_name_long)
        tbl.attributes.setdefault('name_plural','%s dyn fields' %mastertbl_name_long)
        self.sysFields(tbl,id=True, ins=False, upd=False,counter='maintable_id')
        tbl.column('id',size='22',group='_',name_long='Id')
        tbl.column('code',name_long='!!Code')
        tbl.column('default_value',name_long='!!Default value')
        
        tbl.column('description',name_long='!!Description')
        tbl.column('data_type',name_long='!!Data Type')
        tbl.column('calculated','B',name_long='!!Enterable')

        tbl.column('wdg_tag',name_long='!!Wdg type')
        tbl.column('wdg_colspan','L',name_long='!!Colspan')
        tbl.column('wdg_kwargs','X',name_long='!!Wdg kwargs')

        tbl.column('source_combobox',name_long='!!Suggested Values')
        tbl.column('source_dbselect',name_long='!!Db Table')
        tbl.column('source_filteringselect',name_long='!!Allowed Values')
        tbl.column('source_checkboxtext',name_long='!!Checkbox Values')
        tbl.column('checkboxtext_cols','L',name_long='!!Checkbox cols')

        #tbl.column('source_multivalues',name_long='!!Multiple Values')
        
        tbl.column('field_style',name_long='!!Style')
        tbl.column('field_visible',name_long='!!Visible if')
        tbl.column('field_format',name_long='!!Format')
        tbl.column('field_placeholder',name_long='!!Placeholder')

        tbl.column('field_mask',name_long='!!Mask')
        tbl.column('field_tip',name_long='!!Tip')
    
        tbl.column('validate_case',size='1',values='!!u:Uppercase,l:Lowercase,c:Capitalize',name_long='!!Case')
        tbl.column('validate_range',name_long='!!Range')
        
        tbl.column('standard_range','N',name_long='!!Std range')
        tbl.column('formula',name_long='!!Formula')
        #tbl.column('do_summary','B',name_long='!!Do summary')
        tbl.column('mandatory','B',name_long='!!Mandatory')

        tbl.column('maintable_id',size='22',group='_',name_long=mastertblname).relation('%s.%s.%s' %(pkgname,mastertblname,mastertbl.attributes.get('pkey')), 
                    mode='foreignkey', onDelete_sql='cascade', relation_name='dynamicfields',
                    one_group='_',many_group='_')
        if mastertbl.attributes.get('hierarchical'):
            tbl.formulaColumn('hlevel',"""array_length(string_to_array(@maintable_id.hierarchical_pkey,'/'),1)""")

    def onSiteInited(self):
        if self.pkg.attributes.get('df_ok'):
            return
        mastertbl = self.fullname.replace('_df','')
        tblobj = self.db.table(mastertbl)
        if tblobj.column('df_fields') is not None:
            print('IMPORTING DynamicFields FROM LEGACY',mastertbl)
            tblobj.df_importLegacyScript()
            return True
            