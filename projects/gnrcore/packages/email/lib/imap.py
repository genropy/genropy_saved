#!/usr/bin/env python
# encoding: utf-8

import email, imaplib,datetime
from gnr.core.gnrlang import getUuid
import chardet
detach_dir = '.'
import os
wait = 600

class ImapReceiver(object):
    def __init__(self, db=None, account=None, remote_mailbox='Inbox', local_mailbox='Inbox'):
        self.host = account['host']
        self.port = account['port']
        self.ssl = account['ssl']
        self.username = account['username']
        self.password = account['password']
        self.account_id = account['id']
        self.last_uid = account['last_uid']
        self.db=db
        self.messages_table = self.db.table('email.message')
        self.attachments_table = self.db.table('email.attachment')
        self.account_table = self.db.table('email.account')
        if self.ssl:
            imap_class = imaplib.IMAP4_SSL
        else:
            imap_class = imaplib.IMAP4
        self.imap = imap_class(self.host, str(self.port))
        
        
    def receive(self, remote_mailbox='Inbox', local_mailbox='Inbox'):
        self.imap.login(self.username,self.password)
        self.imap.select(remote_mailbox)
        mailbox_id = self.db.table('email.mailbox').readColumns(columns='$id',where='$account_id=:a_id AND $system_code=:s_code',a_id=self.account_id,s_code='01')
        if self.last_uid:
            searchString = '(UID %s:*)' % self.last_uid
        else:
            searchString = '(ALL)'
        resp, items = self.imap.uid('search',None, searchString)
        items = items[0].split()
        if self.last_uid:
            items = items[1:]
        for emailid in items:
            msgrec = self.createMessageRecord(emailid)
            msgrec['mailbox_id'] = mailbox_id
            self.messages_table.insert(msgrec)
        if items:
            self.account_table.update(dict(id=self.account_id, last_uid=items[-1]))
            self.db.commit()
    
    def fillHeaders(self, mail, new_mail):
        new_mail['from_address'] = unicode(mail['From'])
        new_mail['to_address'] = unicode(mail['To'])
        new_mail['cc_address'] = unicode(mail['Cc'])
        new_mail['bcc_address'] = unicode(mail['Bcc'])
        new_mail['subject'] = mail['Subject']
        datetuple = email.Utils.parsedate(mail['Date'])
        new_mail['send_date'] = datetime.datetime(datetuple[0],datetuple[1],datetuple[2],datetuple[3],datetuple[4])
    
    def parseBody(self, part, new_mail, part_content_type=None):
        if part_content_type == 'text/html':
            content = part.get_payload(decode=True)
            #encoding = chardet.detect(content)['encoding']
            encoding = part.get_content_charset()
            new_mail['body'] = unicode(content.decode(encoding).encode('utf8'))
            new_mail['html'] = True
        elif part_content_type == 'text/plain':
            content = part.get_payload(decode=True)
            #encoding = chardet.detect(content)['encoding']
            encoding = part.get_content_charset()
            new_mail['body_plain'] = unicode(content.decode(encoding).encode('utf8'))
    
    def parseAttachment(self, part, new_mail, part_content_type=None):
        new_attachment = dict(message_id = new_mail['id'])
        filename = part.get_filename()
        counter = 1
        if not filename:
            filename = 'part-%03d%s' % (counter, 'bin')
            counter += 1
        att_data = part.get_payload(decode=True)
        new_attachment['filename'] = filename
        date = new_mail['send_date']
        attachment_path =  self.atc_getAttachmentPath(date,filename)
        year = str(date.year)
        month = '%02i' %date.month
        new_attachment['path'] = os.path.join('mail',self.account_id, year,month, filename)
        with open(attachment_path,'wb') as attachment_file:
            attachment_file.write(att_data)
        self.attachments_table.insert(new_attachment)
    
    def atc_getAttachmentPath(self,date,filename):
        year = str(date.year)
        month = '%02i' %date.month
        return self.db.application.site.getStaticPath('site:mail', self.account_id, year,month, filename,
                                                       autocreate=-1)
        
        
    def createMessageRecord(self, emailid):
        new_mail = dict(account_id=self.account_id)
        new_mail['id'] = getUuid()
        new_mail['uid'] = emailid
        resp, data = self.imap.uid('fetch',emailid, "(RFC822)")
        email_body = data[0][1]
        mail = email.message_from_string(email_body)
        self.fillHeaders(mail, new_mail)
        if mail.get_content_maintype() != 'multipart':
            content = mail.get_payload(decode=True)
            encoding = part.get_content_charset()
            #encoding = chardet.detect(content)['encoding']
            new_mail['body'] = unicode(content.decode(encoding).encode('utf8'))
            new_mail['body_plain'] = new_mail['body']
        else:
            for part in mail.walk():
                part_content_type = part.get_content_type()
                if part_content_type.startswith('multipart'):
                    continue
                if part.get('Content-Disposition') is None: 
                    self.parseBody(part, new_mail, part_content_type=part_content_type)
                else:
                    self.parseAttachment(part, new_mail, part_content_type=part_content_type)
        if not new_mail.get('body'):
            new_mail['body'] = new_mail.get('body_plain')
        
        return new_mail
            
if __name__=='__main__':
    pass