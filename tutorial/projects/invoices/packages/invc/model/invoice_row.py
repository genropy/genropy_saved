# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('invoice_row',  pkey='id',name_long='!!Invoice_row',
                      name_plural='!!Invoice_rows')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        self.sysFields(tbl, id=False)
        tbl.column('invoice_id',size='22',name_long='!!Invoice_ID').relation('invoice.id',
                    onDelete='cascade', deferred= True, mode='foreignkey')
        tbl.column('product_id',size='22',name_long='!!Product_ID').relation('product.id',
                    onDelete='raise', mode='foreignkey')
        tbl.column('quantity','R',name_long='!!Quantity')
        tbl.column('price','R',name_long='!!Price')
        tbl.column('total','R',name_long='!!Total')
