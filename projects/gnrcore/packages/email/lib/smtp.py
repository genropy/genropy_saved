#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrlang import getUuid
from datetime import datetime
detach_dir = '.'
wait = 600
    
def send_message(page=None,message=None, account=None, attachments=None):
    attachments = attachments or []
    host = account['host']
    port = account['port']
    ssl = account['ssl']
    username = account['username']
    password = account['password']
    account_id = account['id']
    last_uid = account['last_uid']
    db=page.db
    mail_handler = page.site.mail_handler
    to_address=message['to']
    subject = message['subject']
    body = message['body']
    html = message['html']
    from_address=message['from']
    cc_address=message['cc']
    bcc_address=message['bcc']
    attachments=[a['path'] for a in attachments]
    smtp_host = account['host']
    port = account['port']
    user = accounts['username']
    password = account['password']
    ssl=account['ssl']
    tls=account['tls']
    async_ = True
    mail_handler.sendmail(to_address=to_address, subject=subject, body=body, cc_address=cc_address,
                    bcc_address=bcc_address, attachments=attachments,
                 from_address=from_address, smtp_host=smtp_host, port=port, user=user, password=password,
                 ssl=ssl, tls=tls, html=html, async_=async_)
                      

def send_pending(page=None, account=None):
    db=page.db
    mail_handler = page.site.mail_handler
    messages_table = db.table('email.message')
    attachments_table = db.table('email.attachment')
    account_table = db.table('email.account')
    if not account:
        accounts=account_table.query(where='$protocol_code = :smtp', smtp='SMTP').fetchAsDict(key='id')
    else:
        accounts=dict(account['id']=account)
    messages=messages_table.query(where="$sent IS NOT TRUE AND $account_id in :account and date <=:now",now=datetime.now(),
                                            account=list(accounts.keys()),for_update=True).fetch()
    message_pkeys = [m['id'] for m in messages]
    attachments = attachments_table.query(where='$message_id IN :message_pkeys', message_pkeys=message_pkeys).fetchAsDict(key='message_id')
    for account_id,messages in list(account_messages.items()):
        for message in messages:
            send_message(page=page, message=message, account=accounts[message['account_id']], attachments=attachments.get(message['id']))
            message['sent'] = True
            messages_table.update(message)
    db.commit()
    
if __name__=='__main__':
    sent_smtp()