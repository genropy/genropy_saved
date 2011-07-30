#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2011-07-20.
Copyright (c) 2008 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    py_requires = 'public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def main(self, root, **kwargs):
        pane, top, bottom = self.pbl_rootContentPane(root, title='Prova Form', **kwargs)
        pane.dbSelect(dbtable='invoice.product', value='^aux.product_pkey', _class='gnrfield')
        fb = pane.formbuilder(cols=2,formId='formproduct',datapath='product.record',dbtable='invoice.product')
        fb.field('description')
        fb.button('load',fire='loadproduct')
        fb.button('save',fire='saveproduct')
        fb.field('product_type', validate_notnull=True, validate_notnull_error='!!Required')
        self.formLoader('formproduct',resultPath='product.record',table='invoice.product',pkey='=aux.product_pkey',
                        _fired='^loadproduct',loadingParameters='=gnr.tables.invoice_product.loadingParameters')
        self.formSaver('formproduct',table='invoice.product',_fired='^saveproduct')
        