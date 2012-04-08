# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable
class Table(GnrHTable):

    def config_db(self, pkg):
        tbl =  pkg.table('mailbox', rowcaption='mailbox_name', pkey='id', name_long='!!Mailbox', name_plural='!!Mailboxes')
        self.sysFields(tbl)
        self.htableFields(tbl)
        tbl.column('mailbox_name',size=':40',name_long='!!Mailbox Name')
        tbl.column('account_id',size='22',group='_',name_long='Account id').relation('account.id', mode='foreignkey', 
                                                                                    onDelete='raise',relation_name='mailboxes')
