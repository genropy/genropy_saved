# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('user_account', rowcaption='id',pkey='id')
        self.sysFields(tbl)
        tbl.column('user_id',size='22',name_long='!!User id').relation('adm.user.id', mode='foreignkey', relation_name='user_accounts')
        tbl.column('account_id',size='22',name_long='!!Account id').relation('email.account.id', mode='foreignkey', relation_name='account_users')
        tbl.column('can_send',dtype='B', name_long='!!Can Send')
        
