# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('action', name_short='!!Action', name_long='!!Action',
                        name_plural='!!Actions',pkey='id',rowcaption='title')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        self.sysFields(tbl, id=False)
        tbl.column('title',size=':30',name_long='!!Title')
        tbl.column('ticket_id',size='22',name_long='!!Ticket'
                    ).relation('ticket.id',mode='foreignkey',onDelete='cascade')
        tbl.column('staff_id',size='22',name_long='!!Author'
                    ).relation('staff.id',mode='foreignkey',onDelete='raise')
        tbl.column('action_date','D',name_long='!!Action date')
        tbl.column('description',name_long='!!Description')