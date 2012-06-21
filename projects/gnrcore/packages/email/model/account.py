# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('account', rowcaption='$account_name', caption_field='account_name',
                            pkey='id', name_long='!!Account', name_plural='!!Account')
        self.sysFields(tbl)
        tbl.column('account_name',name_long='!!Account Name')
        tbl.column('address',name_long='!!Address')
        tbl.column('full_name',size=':80',name_long='!!Full Name')
        tbl.column('host',size=':80',name_long='!!Host')
        tbl.column('port','L',name_long='!!Port')
        tbl.column('protocol_code',size=':10',name_long='!!TLS').relation('email.protocol.code', mode='foreignkey', relation_name='accounts')
        tbl.column('tls','B',name_long='!!TLS')
        tbl.column('ssl','B',name_long='!!SSL')
        tbl.column('username',size=':80',name_long='!!Username')
        tbl.column('password',size=':80',name_long='!!Password')
        tbl.column('last_uid',name_long='!!Last UID')
    
    def standardMailboxes(self):
        return ('Inbox','Outbox','Draft','Trash')
        
    def trigger_onInserted(self, record_data):
        mboxtbl = self.db.table('email.mailbox')
        for i,mbox in enumerate(self.standardMailboxes()):
            mboxtbl.createMbox(mbox,record_data['id'],order=i+1)

    def trigger_onUpdated(self, record_data,old_record=None):
        mboxtbl = self.db.table('email.mailbox')
        if mboxtbl.query(where='$account_id=:account_id',account_id=record_data['id']).count()==0:
            for i,mbox in enumerate(self.standardMailboxes()):
                mboxtbl.createMbox(mbox,record_data['id'],order=i+1)