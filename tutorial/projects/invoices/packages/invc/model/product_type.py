#!/usr/bin/env python
# encoding: utf-8
# VISTOAL: 291008
class Table(object):
    """ """
    def config_db(self, pkg):
        """invc.customer"""
        tbl =  pkg.table('product_type',  pkey='code',name_plural = '!!Products Type',
                         name_long=u'!!Products Type', rowcaption='$code,$description:%s - %s')
        self.sysFields(tbl,id=False)
        tbl.column('code', size=':6',name_long = '!!Code',unique=True, 
                    indexed=True,validate_notnull=True,validate_notnull_error='!!Code is required',
                    validate_len=':6',validate_len_max='!!Too long')
        tbl.column('description', size=':24',name_long = '!!Description',unique=True, 
                    indexed=True,validate_notnull=True,validate_notnull_error='!!Description is required')

            