#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('ticket_person', pkey='id', name_long='!!Ticket subscriber', name_plural='!!Ticket subscribers')
        self.sysFields(tbl)
        tbl.column('person_id',size='22' ,group='_',name_long='!!Person').relation('person.id',relation_name='person_tickets',mode='foreignkey',onDelete='raise')
        tbl.column('ticket_id',size='22' ,group='_',name_long='!!Ticket').relation('ticket.id',relation_name='ticket_person',mode='foreignkey',onDelete='cascade')
        tbl.column('role' ,size=':5',name_long='!!Role',values='TEST:Tester,DEV:Developer,SUP:Supervisor')