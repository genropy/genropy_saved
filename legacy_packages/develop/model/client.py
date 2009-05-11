# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('client', name_short='Client', name_long='Client',name_plural='Clients',
                            pkey='id',rowcaption='company')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        self.sysFields(tbl, id=False)
        tbl.column('card_id',size='22',name_long='!!Card id') # da decidere bene a cosa collegarlo
        tbl.column('company',size=':30',name_long='!!Company') #in italia ragione sociale
        tbl.column('address',name_long='!!Address')
        tbl.column('phones','X',name_long='!!Phones')
        tbl.column('emails',name_long='!!Emails')
