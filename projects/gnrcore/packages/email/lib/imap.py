#!/usr/bin/env python
# encoding: utf-8

import email, imaplib,datetime
from email.generator import Generator as EmailGenerator
from gnr.core.gnrlang import getUuid
import chardet
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import slugify
import StringIO
detach_dir = '.'
import os
import re
BASE_RE = re.compile('<base .*?>')
wait = 600

class GnrImapException(Exception):
    pass

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
        self.atc_counter = 0
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
        if resp == 'NO':
            raise GnrImapException(items)
        items = items[0].split()
        if not items:
            return
        if self.last_uid and items[0]== self.last_uid:
            if len(items) == 1:
                return
            items = items[1:]
        for emailid in items:
            if self.messages_table.checkDuplicate(account_id=self.account_id,uid=emailid):
                continue
            msgrec = self.createMessageRecord(emailid)
            if not msgrec:
                continue
            msgrec['mailbox_id'] = mailbox_id
            self.messages_table.insert(msgrec)

        self.account_table.update(dict(id=self.account_id, last_uid=items[-1]))
        self.db.commit()
    
    def fillHeaders(self, mail, new_mail,encoding):
        new_mail['from_address'] = unicode(mail['From'])
        new_mail['to_address'] = unicode(mail['To'])
        new_mail['cc_address'] = unicode(mail['Cc'])
        new_mail['bcc_address'] = unicode(mail['Bcc'])
        new_mail['subject'] = self.smartConverter(mail['Subject'],encoding)
        date = mail['Date']
        if date:
            datetuple = email.Utils.parsedate(date.replace('Date:','').replace('.',':')) #some emails have '.' instead of ':' for time format
            if datetuple:
                new_mail['send_date'] = datetime.datetime(datetuple[0],datetuple[1],datetuple[2],datetuple[3],datetuple[4])
            else:
                new_mail['send_date'] = datetime.today()
         
    
    def parseBody(self, part, new_mail, part_content_type=None):
        if part_content_type == 'text/html':
            content = part.get_payload(decode=True)
            content = BASE_RE.sub('',content)
            #encoding = chardet.detect(content)['encoding']
            encoding = part.get_content_charset()
            new_mail['body'] = self.smartConverter(content,encoding)
            new_mail['html'] = True
        elif part_content_type == 'text/plain':
            content = part.get_payload(decode=True)
            #encoding = chardet.detect(content)['encoding']
            encoding = part.get_content_charset() or 'utf8'
            new_mail['body_plain'] = self.smartConverter(content,encoding)

    def smartConverter(self,m,encoding=None):
        if not m:
            return
        encoding = encoding or chardet.detect(m)['encoding']
        if not encoding:
            return unicode(m,errors='ignore')
        try:
            return unicode(m.decode(encoding).encode('utf8'))
        except UnicodeDecodeError:
            encoding = chardet.detect(m)['encoding']
            try:
                return unicode(m.decode(encoding).encode('utf8'))
            except UnicodeDecodeError:
                return unicode('')
        except LookupError:
            return unicode('')

    
    def parseAttachment(self, part, new_mail, part_content_type=None):
        new_attachment = dict(message_id = new_mail['id'])
        filename = part.get_filename()
        filename = email.Header.decode_header(filename)[0][0]
        filename =  self.smartConverter(filename)
        
        counter = 1
        if not filename:
            filename = 'part-%03d%s' % (counter, 'bin')
            counter += 1
        if part.get_content_type().startswith('message/'):
            att_data = self.getMessagePayload(part)
        else:
            att_data = part.get_payload(decode=True)
        fname,ext = os.path.splitext(filename)
        fname = fname.replace('.','_').replace('~','_').replace('#','_').replace(' ','').replace('/','_')
        #fname = '%i_%s' %(self.atc_counter,fname)
        fname = slugify(fname)
        self.atc_counter+=1
        filename = fname+ext
        new_attachment['filename'] = filename
        date = new_mail['send_date']
        attachment_path =  self.getAttachmentPath(date=date,filename=filename, message_id=new_mail['id'])
        #year = str(date.year)
        #month = '%02i' %date.month

        #new_attachment['path'] = os.path.join('mail',self.account_id, year,month,new_mail['id'], filename)
        new_attachment['path'] = self.getAttachmentPath(date=date,filename=filename, message_id=new_mail['id'],
                        relative=True)
        
        with open(attachment_path,'wb') as attachment_file:
            attachment_file.write(att_data)
        self.attachments_table.insert(new_attachment)
    
    def getMessagePayload(self,part):
        fp = StringIO.StringIO()
        g = EmailGenerator(fp, mangle_from_=False)
        g.flatten(part, unixfrom=False)
        return fp.getvalue()

    def getAttachmentPath(self,date=None,filename=None, message_id = None, relative=None):
        year = str(date.year)
        month = '%02i' %date.month
        if not relative:
            filepath = self.db.application.site.getStaticPath('site:mail', self.account_id, year,month,message_id, filename,
                                                       autocreate=-1)
        else:
            filepath = os.path.join('mail', self.account_id, year,month,message_id, filename)
        fname,ext = os.path.splitext(filepath)
        counter = 0
        while os.path.isfile(filepath):
            filepath = '%s_%i%s'%(fname,counter,ext)
            counter += 1
        return filepath
            


        
    def createMessageRecord(self, emailid):
        new_mail = dict(account_id=self.account_id)
        new_mail['id'] = getUuid()
        new_mail['uid'] = emailid
        resp, data = self.imap.uid('fetch',emailid, "(RFC822)")
        email_body = data[0][1]
        mail = email.message_from_string(email_body)
        #mail = email.message_from_string(unicode(email_body.decode(encoding).encode('utf8')))
        onCreatingCallbacs = [fname for fname in dir(self.messages_table) if fname.startswith('onCreatingMessage_')]
        if onCreatingCallbacs:
            make_message = False
            for fname in onCreatingCallbacs:
                make_message = make_message or getattr(self.messages_table,fname)(mail) is not False
            if make_message is False:
                return False
        encoding = mail.get_content_charset()
        b = Bag(mail)
        for k,v in b.items():
            if isinstance(v,basestring):
                b[k] = self.smartConverter(v,encoding)
        new_mail['email_bag'] = b
        self.fillHeaders(mail, new_mail,encoding)
        if self.messages_table.spamChecker(new_mail) is True:
            return
        if mail.get_content_maintype() not in ('multipart','image'):
            content = mail.get_payload(decode=True)
            encoding = mail.get_content_charset()
            #encoding = chardet.detect(content)['encoding']
            new_mail['body'] = self.smartConverter(content,encoding)
            new_mail['body_plain'] = new_mail['body']
        else:
            for part in mail.walk():
                part_content_type = part.get_content_type()
                if part_content_type.startswith('multipart'):
                    continue
                content_disposition = part.get('Content-Disposition')
                if content_disposition is None and part_content_type in ('text/html','text/plain'): 
                    self.parseBody(part, new_mail, part_content_type=part_content_type)
                else:
                    self.parseAttachment(part, new_mail, part_content_type=part_content_type)
        if new_mail.get('body'):
            g = re.search("<body(.*?)>(.*?)</body>", new_mail['body'], re.S|re.DOTALL)
            new_mail['body'] = g.group(2) if g else new_mail['body']
        else:
            new_mail['body'] = new_mail.get('body_plain')     
        return new_mail
            
if __name__=='__main__':
    pass