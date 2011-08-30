#!/usr/bin/env python
# encoding: utf-8

import email, imaplib
from gnr.core.gnrlang import getUuid
detach_dir = '.'
wait = 600
    
def check_imap(page=None, account=None, remote_mailbox='Inbox', local_mailbox='Inbox'):
    host = account['host']
    port = account['port']
    ssl = account['ssl']
    username = account['username']
    password = account['password']
    account_id = account['id']
    last_uid = account['last_uid']
    db=page.db
    messages_table = db.table('email.message')
    attachments_table = db.table('email.attachment')
    if ssl:
        imap_class = imaplib.IMAP4_SSL
    else:
        imap_class = imaplib.IMAP4
    imap = imap_class(host, port)
    imap.login(username,password)
    imap.select(remote_mailbox)
    if last_uid:
        searchString = '(UID %s:*)' % last_uid
    else:
        searchString = '(ALL)'
    resp, items = imap.uid('search',None, searchString)
    items = items[0].split()
    if last_uid:
        items = items[1:]
    for emailid in items:
        new_mail = dict(account_id=account_id)
        new_mail['id'] = getUuid()
        new_mail['uid'] = emailid
        resp, data = imap.uid('fetch',emailid, "(RFC822)")
        email_body = data[0][1]
        mail = email.message_from_string(email_body)
        new_mail['from'] = mail['From']
        new_mail['to'] = mail['To']
        new_mail['cc'] = mail['Cc']
        new_mail['bcc'] = mail['Bcc']
        new_mail['subject'] = mail['Subject']
        if mail.get_content_maintype() != 'multipart':
            new_mail['body'] = mail.get_payload(decode=True)
            new_mail['body_plain'] = new_mail['body']
        else:
            for part in mail.walk():
                part_content_type = part.get_content_type()
                print part_content_type
                if part_content_type.startswith('multipart'):
                    continue
                if part.get('Content-Disposition') is None: # Is body
                    if part_content_type == 'text/html':
                        new_mail['body'] = part.get_payload(decode=True)
                    elif part_content_type == 'text/plain':
                        new_mail['body_plain'] = part.get_payload(decode=True)
                else: # attachments
                    new_attachment = dict(message_id = new_mail['id'])
                    filename = part.get_filename()
                    counter = 1
                    if not filename:
                        filename = 'part-%03d%s' % (counter, 'bin')
                        counter += 1
                    att_data = part.get_payload(decode=True)
                    new_attachment['filename'] = filename
                    attachment_path=page.site.getStaticPath('site:mail', account['id'], new_mail['uid'], filename,
                                                                   autocreate=-1)
                    new_attachment['path'] = attachment_path
                    with open(attachment_path,'wb') as attachment_file:
                        attachment_file.write(att_data)
                    attachments_table.insert(new_attachment)
        messages_table.insert(new_mail)
        db.commit()
if __name__=='__main__':
    account = dict(host='imap.gmail.com',port=993,ssl=True,username='test@softwell.it',password='testotesto',last_uid = None, id=None)
    e=check_imap(account=account)