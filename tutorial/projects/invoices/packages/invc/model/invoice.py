# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('invoice',  pkey='id',name_long='!!Invoice',
                      name_plural='!!Invoices')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        self.sysFields(tbl, id=False)
        tbl.column('number',size='10',name_long='!!Number')
        tbl.column('date','D',name_long='!!Date')
        tbl.column('customer_id',validate_notnull=True,validate_notnull_error='!!Customer is mandatory',size='22',name_long='!!Customer_ID').relation('customer.id',
                    onDelete='raise', mode='foreignkey')
        tbl.column('net','N',size='9,3', name_long='!!Net')
        tbl.column('vat','N',size='12', name_long='!!Vat')
        tbl.column('total','N', size='15,2',name_long='!!Total')
        tbl.aliasColumn('customer',relation_path='@customer_id.name')
        tbl.aliasColumn('city',relation_path='@customer_id.city')
        
    def trigger_onUpdating(self, record, old_record):
        if not record.get('number'):
            record['number']=self.getInvoiceNumber(record['date'])

    def trigger_onInserting(self, record):
        record['number']=self.getInvoiceNumber(record['date'])

    def getInvoiceNumber(self,invoiceDate):
        return self.pkg.getCounter(name='Invoice Number',codekey='$K_$YY', output='$K/$YY$NNNNN', code='IN',
                                    date=invoiceDate)

  #  def invoiceTotal(self):
