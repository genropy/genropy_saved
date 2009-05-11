# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('ticket_type', name_short='Ticket type', name_long='Ticket type',
                        name_plural='Ticket types',pkey='code',rowcaption='code')
        tbl.column('code',size='3',name_long='Code',readOnly='y')
        self.sysFields(tbl, id=False)
        tbl.column('name',size=':30',name_long='!!Name')
        tbl.column('description',name_long='!!Description')