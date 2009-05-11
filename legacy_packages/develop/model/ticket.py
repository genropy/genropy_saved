# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('ticket', name_short='!!Ticket', name_long='!!Ticket',
                          name_plural='!!Tickets',pkey='id',rowcaption='subject')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='!!Id')
        self.sysFields(tbl, id=False)
        tbl.column('subject',size=':30',name_long='!!Subject')
        tbl.column('description',name_long='!!Descrioption')
        tbl.column('ticket_type',size='3',name_long='!!Type'
                   ).relation('ticket_type.code',mode='foreignkey')
        tbl.column('user_id',size='22',name_long='!!Sender').relation('adm.user.id',mode='foreignkey')
        tbl.column('project_id',size='22',name_long='!!Project').relation('project.id',mode='foreignkey')
        tbl.column('staff_id',size='22',name_long='!!Receiver').relation('staff.id',mode='foreignkey')
        tbl.column('expiry_date','D',name_long='!!Expiry date')
        