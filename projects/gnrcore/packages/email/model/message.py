# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('message', rowcaption='subject', pkey='id', name_long='!!Message', name_plural='!!Messages')
        self.sysFields(tbl)
        tbl.column('to',name_long='!!To')
        tbl.column('from',name_long='!!From')
        tbl.column('cc',name_long='!!Cc')
        tbl.column('bcc',name_long='!!Bcc')
        tbl.column('body',name_long='!!Body')
        tbl.column('subject',name_long='!!Subject')
        tbl.column('date','DH',name_long='!!Date')
        tbl.column('user_id',size='22',name_long='!!User id').relation('adm.user.id', mode='foreignkey', relation_name='messages')
        tbl.column('account_id',size='22',name_long='!!Account id').relation('email.account.id', mode='foreignkey', relation_name='messages')
        
