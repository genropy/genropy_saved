#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.builtins import basestring
from builtins import object
import email, imaplib,datetime
from email.generator import Generator as EmailGenerator
from gnr.core.gnrlang import getUuid
import chardet
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import slugify
import io
detach_dir = '.'
import os
import re
import six
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
        for email_id in items:
            if self.messages_table.checkDuplicate(account_id=self.account_id,uid=email_id):
                continue
            if self.db.application.site.debug:
                msgrec = self.createMessageRecord(email_id, mailbox_id)
            else:
                try:
                    msgrec = self.createMessageRecord(email_id, mailbox_id)
                except Exception as e:
                    msgrec = None
                    print('Error in email',str(e))
            if not msgrec:
                continue
            self.messages_table.insert(msgrec)

        self.account_table.update(dict(id=self.account_id, last_uid=items[-1]))
        self.db.commit()

    def receiveEmail(self, email_id):
        resp, data = self.imap.uid('fetch',email_id, "(RFC822)")
        email_bytes = data[0][1]
        return email_bytes
        

    def createMessageRecord(self, email_id, mailbox_id):
        email_bytes = self.receiveEmail(email_id)
        return self.messages_table.newReceivedMessage(email_bytes, email_id=email_id,
                account_id=self.account_id,
                mailbox_id=mailbox_id)

if __name__=='__main__':
    pass