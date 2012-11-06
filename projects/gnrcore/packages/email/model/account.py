# encoding: utf-8
from gnr.core.gnrbag import Bag
class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('account', rowcaption='$account_name', caption_field='account_name',
                            pkey='id', name_long='!!Account', name_plural='!!Account')
        self.sysFields(tbl)
        tbl.column('account_name',name_long='!!Account Name',unique=True)
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

        tbl.column('smtp_host',name_long='!!SMTP host')
        tbl.column('smtp_from_address',name_long='!!From address')
        tbl.column('smtp_username',name_long='!!Smtp username')
        tbl.column('smtp_password',name_long='!!Smtp password')
        tbl.column('smtp_port',name_long='!!Smtp port',dtype='L')
        tbl.column('smtp_timeout',name_long='!!Smtp timeout',dtype='L')
        tbl.column('smtp_tls',name_long='!!Smtp tls',dtype='B')
        tbl.column('smtp_ssl',name_long='!!Smtp ssl',dtype='B')

        tbl.column('system_bcc',name_long='!!System bcc')

        tbl.column('schedulable',dtype='B',name_long='!!Schedulable',name_short='Sched')
    
    def getSmtpAccountPref(self,account=None,account_name=None):
        if account:
            account = self.recordAs(account,mode='dict')
        elif account_name:
            account = self.record(where='$account_name=:an',an=account_name).output('dict')
        mp = dict()
        mp['smtp_host'] = account['smtp_host']
        mp['from_address'] = account['smtp_from_address']
        mp['user'] = account['smtp_username']
        mp['password'] = account['smtp_password']
        mp['port'] = account['smtp_port']
        mp['ssl'] = account['smtp_ssl']
        mp['tls'] = account['smtp_tls']
        mp['system_bcc'] = account['system_bcc']
        return mp
        
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