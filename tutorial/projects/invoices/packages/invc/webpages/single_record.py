#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

class GnrCustomWebPage(object):
    py_requires = 'public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def windowTitle(self):
        return '!!Gestione Form'

    def main(self, root, **kwargs):
        pane, top, bottom = self.pbl_rootContentPane(root, title='Prova Form', **kwargs)
        pane.dbSelect(dbtable='invc.product', value='^aux.product_pkey', _class='gnrfield')
        fb = pane.formbuilder(cols=2, border_spacing='4px', formId='formproduct', datapath='product.record',
                              dbtable='invc.product')
        fb.field('description')
        fb.button('load', fire='loadproduct')
        fb.button('save', fire='saveproduct')
        fb.field('product_type', validate_notnull=True, validate_notnull_error='!!Required')
        self.formLoader('formproduct', resultPath='product.record', table='invc.product', pkey='=aux.product_pkey',
                        _fired='^loadproduct', loadingParameters='=gnr.tables.invc_product.loadingParameters')
        self.formSaver('formproduct', table='invc.product', _fired='^saveproduct')
        