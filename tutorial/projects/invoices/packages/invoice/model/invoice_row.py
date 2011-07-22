#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('invoice_row',pkey='id',name_long='!!Invoice_row',
                         name_plural='!!Invoice_rows',rowcaption='$invoice_id')
        tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
        self.sysFields(tbl,id=False)
        tbl.column('invoice_id',size='22',name_long='!!Invoice_ID').relation('invoice.id',mode='foreignkey',
                                                                              onDelete='cascade',deferred=True,
                                                                              relation_name='invoice_rows')
        tbl.column('product_id', size='22', name_long='!!Product_ID').relation('product.id',mode='foreignkey',
                                                                                onDelete='raise')
        tbl.column('quantity','R',name_long='!!Quantity')
        tbl.column('price','R',name_long='!!Price')
        tbl.column('total','R',name_long='!!Total')