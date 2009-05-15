#!/usr/bin/env python
# encoding: utf-8
# VISTOAL: 291008
class Table(object):
    """ """
    def config_db(self, pkg):
        """invc.product"""
        tbl =  pkg.table('product',  pkey='id',name_plural = '!!Products',
                         name_long=u'!!Products', rowcaption='$code,$description:%s - %s')
        self.sysFields(tbl)
        tbl.column('code', size=':6',name_long = '!!Code',unique=True, indexed=True)
        tbl.column('description', size=':24',name_long = '!!Description',unique=True, indexed=True)
        tbl.column('product_type',name_long = '!!Product Type').relation('product_type.code',mode='foreignkey')

        
    def trigger_onUpdating(self, record, old_record):
        if not record.get('code'):
            record['code']=self.getproductcode()
            
    def trigger_onInserting(self, record):
        record['code']=self.getproductcode()
        
    def getproductcode(self):
        return self.pkg.getCounter(name='Product Code',codekey='$K', output='$NNNNNN', code='product')
            