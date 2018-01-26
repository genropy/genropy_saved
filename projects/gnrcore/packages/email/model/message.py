# encoding: utf-8
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace
import re
import os
import email


EMAIL_PATTERN = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('message', rowcaption='subject', pkey='id', name_long='!!Message', name_plural='!!Messages')
        self.sysFields(tbl,draftField=True)
        tbl.column('in_out', size='1', name_long='!!Message type', name_short='!!I/O',values='I:Input,O:Output')
        tbl.column('to_address',name_long='!!To',_sendback=True)
        tbl.column('from_address',name_long='!!From',_sendback=True)

        tbl.column('cc_address',name_long='!!Cc',_sendback=True)
        tbl.column('bcc_address',name_long='!!Bcc',_sendback=True)
        tbl.column('uid',name_long='!!UID')
        tbl.column('body',name_long='!!Body')
        tbl.column('body_plain',name_long='!!Plain Body')
        tbl.column('html','B',name_long='!!Html')
        tbl.column('subject',name_long='!!Subject')
        tbl.column('send_date','DH',name_long='!!Send date')
        tbl.column('sent','B',name_long='!!Sent')
        tbl.column('user_id',size='22',name_long='!!User id').relation('adm.user.id', mode='foreignkey', relation_name='messages')
        tbl.column('account_id',size='22',name_long='!!Account id').relation('email.account.id', mode='foreignkey', relation_name='messages')
        tbl.column('mailbox_id',size='22',name_long='!!Mailbox id').relation('email.mailbox.id', mode='foreignkey', relation_name='messages')
        tbl.column('message_tipe',size=':10', group='_', name_long='!!Type'
                    ).relation('message_type.code', relation_name='messages', 
                                mode='foreignkey', onDelete='raise')
        tbl.column('notes', name_long='!!Notes')
        tbl.column('message_date', dtype='D', name_long='!!Date')

        tbl.column('sending_attempt','X', name_long='!!Sending attempt')
        tbl.column('email_bag',dtype='X',name_long='!!Email bag')
        tbl.column('extra_headers',dtype='X',name_long='!!Extra headers')

    def trigger_onInserting(self, record_data):
        self.explodeAddressRelations(record_data)

    
    def trigger_onUpdating(self, record_data, old_record):
        self.deleteAddressRelations(record_data)
        self.explodeAddressRelations(record_data)
    
    def trigger_onDeleting(self, record_data):
        self.deleteAddressRelations(record_data)
        
    def extractAddresses(self,addresses):
        outaddress = dict()
        for match in EMAIL_PATTERN.findall(addresses):
            outaddress[match[0].lower()] = True
        return outaddress.keys()

    def parsedAddress(self,address):
        return email.Utils.parseaddr(address)
            
    def deleteAddressRelations(self,record):
        self.db.table('email.message_address').deleteSelection('message_id',record['id'])
        
    def explodeAddressRelations(self,record):
        tblmsgaddres = self.db.table('email.message_address')
        message_id = record['id']
        for address_type in ('to','from','bcc','cc'):
            addresslist = self.extractAddresses(record['%s_address' %address_type])
            for address in addresslist:
                tblmsgaddres.insert(dict(address=address,message_id=message_id,reason=address_type))
                
    @public_method
    def changeMailbox(self,mailbox_id=None,pkeys=None,alias=False):
        if not alias:
            self.batchUpdate(updater=dict(mailbox_id=mailbox_id),where='$id IN :pk',pk=pkeys)
        else:
            aliastbl = self.db.table('email.message_alias')
            currAlias = aliastbl.query(where='$mailbox_id=:mailbox_id AND $message_id IN :pkeys',pkeys=pkeys,mailbox_id=mailbox_id).fetchAsDict(key='mailbox_id')
            for message_id in pkeys:
                if not message_id in currAlias:
                    aliastbl.insert(dict(mailbox_id=mailbox_id,message_id=message_id))
        self.db.commit()
           
    @public_method
    def receive_imap(self, page=None, account=None, remote_mailbox='Inbox', local_mailbox='Inbox'):
        print 'RECEIVE IMAP'
        from gnrpkg.email.imap import ImapReceiver
        if isinstance(account, basestring):
            account = self.db.table('email.account').record(pkey=account).output('bag')
        imap_checker = ImapReceiver(db=self.db, account=account)
        imap_checker.receive()
        #check_imap(page=page, account=account, remote_mailbox=remote_mailbox, local_mailbox=local_mailbox)

    def sendmail(self, datasource=None, to_address=None, cc_address=None, bcc_address=None, subject=None,
                              from_address=None, body=None, attachments=None, account=None,
                              html=False, charset='utf-8', **kwargs):
        # 
        def get_templated(field):
            value = datasource.getItem('_meta_.%s' % field)
            if not value:
                value = datasource.getItem(field)
            if value:
                return templateReplace(value, datasource)
        if datasource:
            get_templated = get_templated
        else:
            get_templated = lambda x:None
        to_address = to_address or get_templated('to_address')
        cc_address = cc_address or get_templated('cc_address')
        bcc_address = bcc_address or get_templated('bcc_address')
        #from_address = from_address or get_templated('from_address')
        subject = subject or get_templated('subject')
        body = body or get_templated('body')
        body = templateReplace(body, datasource) if datasource else body

    def spamChecker(self,msgrec):
        return
    
    @public_method
    def newMessage(self, account_id=None,to_address=None,from_address=None,
                  subject=None, body=None, cc_address=None, 
                  reply_to=None, bcc_address=None, attachments=None,
                 message_id=None,message_date=None,
                 html=False,doCommit=False,moveAttachment=False,**kwargs):
        message_date=message_date or self.db.workdate
        extra_headers = Bag(dict(message_id=message_id,message_date=message_date))
        message_to_dispatch = self.newrecord(in_out='O',
                            account_id=account_id,
                            to_address=to_address,
                            from_address=from_address,
                            subject=subject,message_date=message_date,
                            body=body,cc_address=cc_address,
                            reply_to=reply_to,bcc_address=bcc_address,
                            message_id=message_id,
                            extra_headers=extra_headers,
                            html=html)
        message_atc = self.db.table('email.message_atc')
        self.insert(message_to_dispatch)
        if attachments:
            for r in attachments:
                origin_filepath = r
                mimetype = None
                if isinstance(r,tuple):
                    origin_filepath,mimetype = r
                message_atc.addAttachment(maintable_id=message_to_dispatch['id'],
                                        origin_filepath=r,
                                        mimetype=mimetype,
                                        destFolder=self.folderPath(message_to_dispatch,True),
                                        moveFile=moveAttachment)
        if doCommit:
            self.db.commit()
        return message_to_dispatch


    
    def atc_getAttachmentPath(self,pkey):
        return self.folderPath(self.recordAs(pkey),relative=True)


    def folderPath(self,message_record=None,relative=None):
        message_date = message_record['message_date'] or self.db.workdate
        year = str(message_date.year)
        month = '%02i' %message_date.month
        attachment_root= self.pkg.attributes.get('attachment_root') or 'mail'
        if relative:
            return os.path.join(attachment_root,message_record['account_id'],year,month,message_record['id'])
        else:
            return self.db.application.site.getStaticPath('vol:%s' %attachment_root,
                                                        message_record['account_id'], 
                                                        year,month,message_record['id'],
                                                        autocreate=True)
