# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('message_alias', rowcaption='id',pkey='id', name_long='!!MessageMailbox', name_plural='!!MessageMailbox')
        self.sysFields(tbl)
        tbl.column('message_id',size='22',name_long='!!Message id').relation('email.message.id', mode='foreignkey', relation_name='message_mailboxes')
        tbl.column('mailbox_id',size='22',name_long='!!Mailbox id').relation('email.mailbox.id', mode='foreignkey', relation_name='mailbox_messages')
