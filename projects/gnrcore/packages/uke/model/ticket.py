#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('ticket', pkey='id', name_long='!!Ticket', name_plural='!!Tickets',caption_field='subject')
        self.sysFields(tbl)
        tbl.column('person_id',size='22' ,group='_',name_long='!!Created by').relation('person.id',relation_name='created_tickets',mode='foreignkey',onDelete='raise')
        tbl.column('pagename',name_long='!!Pagename')
        tbl.column('subject',size=':50',name_long='!!Subject',indexed=True)
        tbl.column('ticket_type_code',size=':10' ,name_long='!!Type').relation('ticket_type.code',relation_name='tickets',mode='foreignkey',onDelete='raise')
        tbl.column('summary',name_long='!!Summary')
        tbl.column('description',name_long='!!Description')
        tbl.column('table_identifier',name_long='!!Table').relation('pkgtable.table_identifier',
                                                                relation_name='tickets',mode='foreignkey',
                                                                onDelete='cascade')

