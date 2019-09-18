# encoding: utf-8
from smtplib import SMTPException
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace
import re
import os
import email
from datetime import datetime


EMAIL_PATTERN = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('message', rowcaption='subject', pkey='id',
                     name_long='!!Message', name_plural='!!Messages',partition_account_id='account_id')
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
        tbl.column('message_type',size=':10', group='_', name_long='!!Type'
                    ).relation('message_type.code', relation_name='messages', 
                                mode='foreignkey', onDelete='raise')
        tbl.column('notes', name_long='!!Notes')
        tbl.column('message_date', dtype='D', name_long='!!Date')
        tbl.column('sending_attempt','X', name_long='!!Sending attempt')
        tbl.column('email_bag',dtype='X',name_long='!!Email bag')
        tbl.column('extra_headers',dtype='X',name_long='!!Extra headers')
        tbl.column('weak_attachments', name_long='!!Weak attachments')
        tbl.column('reply_message_id',size='22', group='_', name_long='!!Reply message id'
                    ).relation('email.message.id', relation_name='replies', mode='foreignkey', onDelete='setnull')

    def trigger_onInserting(self, record_data):
        self.explodeAddressRelations(record_data)
        if record_data['in_out']=='I':
            email_bag = Bag(record_data['email_bag'])
            rif_id = email_bag.get('In-Reply-To')
            if rif_id:
                rif_id = rif_id.strip('<>')
                if rif_id and rif_id.startswith('GNR_'):
                    record_data['reply_message_id'] = rif_id[4:26]
    
    def trigger_onUpdating(self, record_data, old_record):
        self.deleteAddressRelations(record_data)
        self.explodeAddressRelations(record_data)
    
    def trigger_onDeleting(self, record_data):
        self.deleteAddressRelations(record_data)
        
    def extractAddresses(self,addresses):
        if not addresses:
            return []
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


    def spamChecker(self,msgrec):
        return
    
    @public_method
    def newMessage(self, account_id=None,to_address=None,from_address=None,
                  subject=None, body=None, cc_address=None, 
                  reply_to=None, bcc_address=None, attachments=None,weak_attachments=None,
                 message_id=None,message_date=None,message_type=None,
                 html=False,doCommit=False,headers_kwargs=None,**kwargs):
        message_date=message_date or self.db.workdate
        extra_headers = Bag(dict(message_id=message_id,message_date=message_date,reply_to=reply_to))
        if headers_kwargs:
            extra_headers.update(headers_kwargs)
        account_id = account_id or self.db.application.getPreference('mail', pkg='adm')['email_account_id']
        if weak_attachments and isinstance(weak_attachments,list):
            site = self.db.application.site
            weak_attachments = ','.join([site.storageNode(p).fullpath for p in weak_attachments])
        message_to_dispatch = self.newrecord(in_out='O',
                            account_id=account_id,
                            to_address=to_address,
                            from_address=from_address,
                            subject=subject,message_date=message_date,
                            body=body,cc_address=cc_address,
                            bcc_address=bcc_address,
                            extra_headers=extra_headers,
                            message_type=message_type,
                            weak_attachments=weak_attachments,
                            html=html,**kwargs)
        message_atc = self.db.table('email.message_atc')
        with self.db.tempEnv(autoCommit=True):
            self.insert(message_to_dispatch)
            if attachments:
                for r in attachments:
                    origin_filepath = r
                    mimetype = None
                    if isinstance(r,tuple):
                        origin_filepath,mimetype = r
                    message_atc.addAttachment(maintable_id=message_to_dispatch['id'],
                                            origin_filepath=origin_filepath,
                                            mimetype=mimetype,
                                            destFolder=self.folderPath(message_to_dispatch),
                                            moveFile=False, copyFile=True)
        if doCommit:
            self.db.commit()
        return message_to_dispatch

    def newMessageFromUserTemplate(self,record_id=None,letterhead_id=None,
                            template_id=None,table=None,template_code=None,
                            attachments=None,to_address=None, subject=None,
                            cc_address=None,bcc_address=None,from_address=None, account_id=None, **kwargs):
        mail_handler=self.db.application.site.getService('mail')

        return self.newMessage(**mail_handler.mailParsFromUserTemplate(record_id=record_id,letterhead_id=letterhead_id,
                            template_id=template_id,table=table,template_code=template_code,
                            attachments=attachments,to_address=to_address, subject=subject,
                            cc_address=cc_address,bcc_address=bcc_address,from_address=from_address, account_id=account_id, **kwargs))
    

    @public_method
    def sendMessage(self,pkey=None):
        site = self.db.application.site
        mail_handler = site.getService('mail')
        with self.recordToUpdate(pkey,for_update='SKIP LOCKED') as message:
            if message['send_date']:
                return
            print 'sending message',pkey
            message['extra_headers'] = Bag(message['extra_headers'])
            extra_headers = message['extra_headers']
            extra_headers['message_id'] = extra_headers['message_id'] or 'GNR_%(id)s' %message
            account_id = message['account_id']
            mp = self.db.table('email.account').getSmtpAccountPref(account_id)
            debug_address = mp.pop('system_debug_address')
            bcc_address = message['bcc_address'] 
            attachments = self.db.table('email.message_atc').query(where='$maintable_id=:mid',mid=message['id']).fetch()
            attachments = [r['filepath'] for r in attachments]
            if message['weak_attachments']:
                attachments.extend(message['weak_attachments'].split(','))
            if mp['system_bcc']:
                bcc_address = '%s,%s' %(bcc_address,mp['system_bcc']) if bcc_address else mp['system_bcc']
            try:
                mail_handler.sendmail(to_address=debug_address or message['to_address'],
                                body=message['body'], subject=message['subject'],
                                cc_address=message['cc_address'], bcc_address=bcc_address,
                                from_address=message['from_address'] or mp['from_address'],
                                attachments=attachments, 
                                smtp_host=mp['smtp_host'], port=mp['port'], user=mp['user'], password=mp['password'],
                                ssl=mp['ssl'], tls=mp['tls'], html=message['html'], async=False,
                                scheduler=False,headers_kwargs=extra_headers.asDict(ascii=True))
                message['send_date'] = datetime.now()
                message['bcc_address'] = bcc_address
            except Exception as e:
                sending_attempt = message['sending_attempt'] = message['sending_attempt'] or Bag()
                ts = datetime.now()
                sending_attempt.setItem('r_%i' %len(sending_attempt),None,ts=ts,error=str(e))
                message['sending_attempt'] = sending_attempt
        self.db.commit()
        
    
    def atc_getAttachmentPath(self,pkey):
        return self.folderPath(self.recordAs(pkey))

    def folderPath(self,message_record=None):
        message_date = message_record['message_date'] or self.db.workdate
        year = str(message_date.year)
        month = '%02i' %message_date.month
        attachment_root= self.pkg.attributes.get('attachment_root') or 'mail'
        return '/'.join(['%s:%s' %(attachment_root,message_record['account_id']),year,
                            month,message_record['id']])
