# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrmail : gnr mail controller
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import smtplib
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.utils import formatdate
import re, htmlentitydefs
import mimetypes
from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrstring import templateReplace
import thread
import os
import datetime
import time

mimetypes.init() # Required for python 2.6 (fixes a multithread bug)
TAG_SELECTOR = '<[^>]*>'

mime_mapping = dict(application=MIMEApplication,
                    image=MIMEImage, text=MIMEText)

def clean_and_unescape(text):
    """Removes HTML or XML character references and entities from a text string.
    Return the plain text, as a Unicode string, if necessary
    
    :param text: The HTML (or XML) source text."""
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as it is written
        
    text = re.sub(TAG_SELECTOR, '', text)
    return re.sub("&#?\w+;", fixup, text)

class MailHandler(GnrBaseService):
    """A class for mail management."""
    service_name = 'mail'
    
    def __init__(self, parent=None):
        self.parent = parent
        self.smtp_accounts = {}
        self.default_smtp_account = None
        self.pop_accounts = {}
        self.default_pop_account = None
        self.imap_accounts = {}
        self.default_imap_account = None
        
    def set_smtp_account(self, name, from_address=None, smtp_host=None, username=None,
                         password=None, port=None, ssl=False, default=False):
        """Set the smtp account
        
        :param name: the account's name
        :param from_address: the email sender
        :param smtp_host: the smtp host to send this email
        :param username: the username
        :param password: the username's password
        :param port: if a non standard port is used then it can be overridden
        :param ssl: boolean. If ``True``, attempt to use the ssl port. Else standard smtp port is used.
        :param default: boolean. TODO"""
        self.smtp_accounts[name] = dict(from_address=from_address,
                                        smtp_host=smtp_host, username=username,
                                        password=password, port=port, ssl=ssl)
        if default:
            self.default_smtp_account = name
            
    def set_smtp_default_account(self, name):
        """Allow to use the saved account parameters for the subsequent SMTP mails
        
        :param name: the default account's name"""
        self.default_smtp_account = name
        
    def set_pop_default_account(self, name):
        """Allow to use the saved account parameters for the subsequent POP mails
        
        :param name: the default account's name"""
        self.default_pop_account = name
        
    def set_imap_default_account(self, name):
        """Allow to use the saved account parameters for the subsequent IMAP mails
        
        :param name: the default account's name"""
        self.default_imap_account = name
        
    def get_account_params(self, account=None, from_address=None, smtp_host=None, port=None,
                           user=None, password=None, ssl=False, tls=False,timeout=None, **kwargs):
        """Set the account parameters and return them
        
        :param account: if an account has been defined previously with :meth:`set_smtp_account()`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained
        :param from_address: the email sender
        :param smtp_host: the smtp host to send this email
        :param port: if a non standard port is used then it can be overridden
        :param user: the username
        :param password: the username's password
        :param ssl: boolean. If ``True``, attempt to use the ssl port. Else standard smtp port is used
        :param tls: boolean. Allow to communicate with an smtp server. You may choose three ways:
                    
                    #. no encryption
                    #. ssl -> all data is encrypted on a ssl layer
                    #. tls -> server and client begin communitation in a unsecure way and after a starttls
                       command they start to encrypt data (this is the way you use to connect to gmail smtp)"""
        account = account or self.default_smtp_account
        if account:
            account_params = self.smtp_accounts[account]
        elif smtp_host:
            account_params = dict(smtp_host=smtp_host, port=port, user=user, password=password,
                                  ssl=ssl, tls=tls, from_address=from_address,timeout=timeout)
        else:
            account_params = dict(self.getDefaultMailAccount())
            account_params['from_address'] = from_address or account_params.get('from_address')
        return account_params

    def getDefaultMailAccount(self):
        dict()
        
    def get_smtp_connection(self, account=None, smtp_host=None, port=None,
                            user=None, password=None, ssl=False, tls=False, timeout=None,**kwargs):
        """Get the smtp connection and return it
        
        :param account: if an account has been defined previously with :meth:`set_smtp_account()`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained
        :param smtp_host: the smtp host to send this email
        :param port: if a non standard port is used then it can be overridden
        :param user: the username
        :param password: the username's password
        :param ssl: boolean. If ``True``, attempt to use the ssl port. Else standard smtp port is used.
        :param tls: allow to communicate with an smtp server. You may choose three ways:
                    
                    #. no encryption
                    #. ssl -> all data is encrypted on a ssl layer
                    #. tls -> server and client begin communitation in a unsecure way and after a starttls
                       command they start to encrypt data (this is the way you use to connect to gmail smtp)"""
        if ssl:
            smtp = getattr(smtplib, 'SMTP_SSL')
        else:
            smtp = getattr(smtplib, 'SMTP')
        if port:
            smtp_connection = smtp(host=str(smtp_host), port=str(port),timeout=timeout)
        else:
            smtp_connection = smtp(host=smtp_host,timeout=timeout)
        if tls:
            smtp_connection.starttls()
        if user:
            smtp_connection.login(str(user), str(password))
        return smtp_connection
        
    def handle_addresses(self, from_address=None, to_address=None, multiple_mode=None):
        """Handle the mail addresses and return them as a list
        
        :param from_address: the email sender
        :param to_address: the email receiver
        :param multiple_mode: TODO"""
        cc = bcc = None
        if isinstance(to_address, basestring):
            to_address = [address.strip() for address in to_address.replace(';', ',').split(',') if address]
        multiple_mode = (multiple_mode or '').lower().strip()
        if multiple_mode == 'to':
            to = [','.join(to_address)]
        elif multiple_mode == 'bcc': # jbe changed this from ccn to bcc
            to = [from_address]
            bcc = ','.join(to_address)
        elif multiple_mode == 'cc':
            to = [from_address]
            cc = ','.join(to_address)
        else:
            to = to_address
        return to, cc, bcc
        
    def build_base_message(self, subject, body, attachments=None, html=None, charset=None):
        """Add???
        
        :param subject: the email subject
        :param body: the email body. If you pass ``html=True`` attribute,
                     then you can pass in the body the html tags
        :param attachments: path of the attachment to be sent with the email
        :param html: TODO
        :param charset: a different charser may be defined by its standard name"""
        charset = charset or 'us-ascii' # us-ascii is the email default, gnr default is utf-8.
                                        # This is used to prevent explicit "charset = None" to be passed
        attachments = attachments or []
        if not html and not attachments:
            msg = MIMEText(body, 'text', charset)
            msg['Subject'] = subject
            return msg
        if html:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg.attach(MIMEText(clean_and_unescape(body), 'text', charset))
            if attachments:
                multi_msg=MIMEMultipart()
                multi_msg.attach(MIMEText(body, 'html', charset))
                self._attachments(multi_msg, attachments)
                msg.attach(multi_msg)
            else:
                msg.attach(MIMEText(body, 'html', charset))
            return msg
        else:
            msg = MIMEMultipart()
            self._attachments(msg, attachments)
            msg.attach(MIMEText(body, 'text', charset))
            msg['Subject'] = subject
            return msg
        
    def _attachments(self, msg, attachments):
        for attachment_path in attachments:
            if isinstance(attachment_path,tuple):
                attachment_path,mime_type = attachment_path
            else:
                mime_type = mimetypes.guess_type(attachment_path)[0]
            mime_family, mime_subtype = mime_type.split('/')
            attachment_file = open(attachment_path, 'rb')
            email_attachment = mime_mapping[mime_family](attachment_file.read(), mime_subtype)
            email_attachment.add_header('content-disposition', 'attachment', filename=os.path.basename(attachment_path))
            msg.attach(email_attachment)
            attachment_file.close()
        
    def sendmail_template(self, datasource, to_address=None, cc_address=None, bcc_address=None, reply_to=None, subject=None,
                          from_address=None, body=None, attachments=None, account=None,
                          smtp_host=None, port=None, user=None, password=None,
                          ssl=False, tls=False, html=False, charset='utf-8', async=False, **kwargs):
        """Add???
        
        :param datasource: TODO
        :param to_address: the email receiver
        :param cc_address: can be a comma deliminated str of email addresses or a list or tuple
        :param bcc_address: can be a comma deliminated str of email addresses or a list or tuple
        :param subject: the email subject
        :param from_address: the email sender
        :param body: the email body. If you pass ``html=True`` attribute,
                     then you can pass in the body the html tags
        :param attachments: path of the attachment to be sent with the email
        :param account: if an account has been defined previously with :meth:`set_smtp_account()`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained
        :param smtp_host: the smtp host to send this email
        :param port: if a non standard port is used then it can be overridden
        :param user: the username
        :param password: the username's password
        :param ssl: boolean. If ``True``, attempt to use the ssl port. Else standard smtp port is used
        :param tls: allow to communicate with an smtp server.
                    
                    You may choose three ways:
                    
                    #. no encryption
                    #. ssl -> all data is encrypted on a ssl layer
                    #. tls -> server and client begin communitation in a unsecure way and after a starttls
                       command they start to encrypt data (this is the way you use to connect to gmail smtp)
        :param html: boolean. If ``True``, html tags can be used in the body of the email.
                     Appropriate headers are attached
        :param charset: a different charser may be defined by its standard name
        :param async: boolean. If ``True``, then a separate process is spawned to send the email and control
                      is returned immediately to the calling function"""
        def get_templated(field):
            value = datasource.getItem('_meta_.%s' % field)
            if not value:
                value = datasource.getItem(field)
            if value:
                return templateReplace(value, datasource)
                
        #datasource--to
        to_address = to_address or get_templated('to_address')
        cc_address = cc_address or get_templated('cc_address')
        bcc_address = bcc_address or get_templated('bcc_address')
        from_address = from_address or get_templated('from_address')
        reply_to = reply_to or get_templated('reply_to')
        subject = subject or get_templated('subject')
        templated_attachments = get_templated('attachments')
        attachments = attachments or templated_attachments.split('\n') if templated_attachments else []
        body = body or get_templated('body')
        body = templateReplace(body, datasource)
        self.sendmail(to_address, subject=subject, body=body, cc_address=cc_address, reply_to=reply_to, bcc_address=bcc_address,
                      attachments=attachments, account=account,
                      from_address=from_address, smtp_host=smtp_host, port=port, user=user, password=password,
                      ssl=ssl, tls=tls, html=html, charset=charset, async=async)
                      
    def sendmail(self, to_address=None, subject=None, body=None, cc_address=None, reply_to=None, bcc_address=None, attachments=None,
                 account=None,timeout=None,
                 from_address=None, smtp_host=None, port=None, user=None, password=None,message_id=None,message_date=None,
                 ssl=False, tls=False, html=False, charset='utf-8', async=False,
                 cb=None, cb_args=None, cb_kwargs=None, **kwargs):
        """Send mail is a function called from the postoffice object to send an email.
        
        :param to_address: the email receiver
        :param subject: the email subject
        :param body: the email body. If you pass ``html=True`` attribute,
                     then you can pass in the body the html tags
        :param cc_address: can be a comma deliminated str of email addresses or a list or tuple.
        :param bcc_address: can be a comma deliminated str of email addresses or a list or tuple.
        :param attachments: path of the attachment to be sent with the email
        :param account: if an account has been defined previously with :meth:`set_smtp_account()`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained 
        :param from_address: the email sender
        :param smtp_host: the smtp host to send this email
        :param port: if a non standard port is used then it can be overridden
        :param user: the username
        :param password: the username's password
        :param ssl: boolean. If ``True``, attempt to use the ssl port. Else standard smtp port is used
        :param tls: allow to communicate with an smtp server. You may choose three ways:
                    
                    #. no encryption
                    #. ssl -> all data is encrypted on a ssl layer
                    #. tls -> server and client begin communitation in a unsecure way and after
                       a starttls command they start to encrypt data (this is the way you use to connect to gmail smtp)
                       
        :param html: boolean. If ``True`` then html tags can be used in the body of the email. Appropriate headers are attached
        :param charset: a different charser may be defined by its standard name
        :param async: if set to true, then a separate process is spawned to send the email and control
                      is returned immediately to the calling function"""
        account_params = self.get_account_params(account=account, from_address=from_address,
                                                 smtp_host=smtp_host, port=str(port) if port else None, user=user, password=password, ssl=ssl,
                                                 tls=tls,timeout=timeout)
        from_address = account_params['from_address']
        msg = self.build_base_message(subject, body, attachments=attachments, html=html, charset=charset)
        msg['From'] = from_address
        msg['To'] = to_address
        if ',' in to_address:
            to_address = to_address.split(',')
        message_date = message_date or datetime.datetime.now()
        if isinstance(message_date,datetime.datetime):
            message_date = formatdate(time.mktime(message_date.timetuple()))
        msg['Date'] = message_date
        if reply_to:
            msg.add_header('reply-to', reply_to)
        if message_id:
            domain = from_address.split('@')[1]
            unique ='%012i' %int(time.time())
            message_id = "<%s_%s@%s>" %(message_id,unique,domain)
            msg['Message-ID'] = message_id
        if  type(cc_address).__name__ in ['list', 'tuple']:
            msg['Cc'] = cc_address and ','.join(cc_address)
        else:
            msg['Cc'] = cc_address
        #if  type(bcc_address).__name__ in ['list', 'tuple']:
        #    msg['Bcc'] = bcc_address and ','.join(bcc_address)
        #else:
        #    msg['Bcc'] = bcc_address
        system_bcc = account_params.pop('system_bcc',None)
        if system_bcc:
            bcc_address = bcc_address or []
            bcc_address.append(system_bcc)
            bcc_address = ','.join(bcc_address)

        msg_string = msg.as_string()
        sendmail_args=(account_params, from_address, to_address, cc_address, bcc_address, msg_string)
        if not async:
            self._sendmail(*sendmail_args)
            if cb:
                cb_args = cb_args or ()
                cb_kwargs = cb_kwargs or {}
                cb(*cb_args, **cb_kwargs)
            
        else:
            thread_params = dict(call=self._sendmail, call_args=sendmail_args, cb=cb, cb_args=None, cb_kwargs=None)
            thread.start_new_thread(self._send_with_cb,(),thread_params)


    def _send_with_cb(self, call=None, call_args=None, call_kwargs=None, cb=None, cb_args=None, cb_kwargs=None):
        call_args = call_args or ()
        call_kwargs = call_kwargs or {}
        call(*call_args, **call_kwargs)
        if cb:
            cb_args = cb_args or ()
            cb_kwargs = cb_kwargs or {}
            cb(*cb_args, **cb_kwargs)
                                    
    def _sendmail(self, account_params, from_address, to_address, cc_address, bcc_address, msg_string):
        smtp_connection = self.get_smtp_connection(**account_params)
        email_address = []
        for dest in (to_address, cc_address, bcc_address):
            dest = dest or []
            if isinstance(dest,(list, tuple)):
                email_address.extend(dest)
            else:
                email_address.append(dest)
        smtp_connection.sendmail(from_address, email_address, msg_string)
        smtp_connection.close()
        
    def sendmail_many(self, to_address, subject, body, attachments=None, account=None,
                      from_address=None, smtp_host=None, port=None, user=None, password=None,
                      ssl=False, tls=False, html=False, multiple_mode=False, progress_cb=None, charset='utf-8',
                      async=False,timeout=None):
        """TODO
        
        :param to_address: the email receiver
        :param subject: the email subject
        :param body: the email body. If you pass ``html=True`` attribute,
                     then you can pass in the body the html tags
        :param attachments: path of the attachment to be sent with the email.
        :param account: if an account has been defined previously with :meth:`set_smtp_account()`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained 
        :param from_address: the email sender
        :param smtp_host: the smtp host to send this email
        :param port: if a non standard port is used then it can be overridden
        :param user: the username
        :param password: the username's password
        :param ssl: boolean. If ``True``, attempt to use the ssl port. Else standard smtp port is used
        :param tls: allow to communicate with an smtp server. You may choose three ways:
                    
                    #. no encryption
                    #. ssl -> all data is encrypted on a ssl layer
                    #. tls -> server and client begin communitation in a unsecure way and after a starttls
                       command they start to encrypt data (this is the way you use to connect to gmail smtp)
        
        :param html: boolean. If ``True``, html tags can be used in the body of the email. Appropriate headers are attached
        :param multiple_mode: allow to send a mail to many addresses. Its parameters are:
                              
                              * ``False`` - single mail for recipient
                              * ``to, To, TO`` - a mail sent to all recipient in to field
                              * ``bcc, Bcc, BCC`` - a mail sent to ourself with all recipient in bcc address
                              
        :param charset: a differnet charser may be defined by its standard name"""
        account_params = self.get_account_params(account=account, from_address=from_address,
                                                 smtp_host=smtp_host, port=port, user=user, password=password, ssl=ssl,
                                                 timeout=timeout,
                                                 tls=tls)
        smtp_connection = self.get_smtp_connection(**account_params)
        to, cc, bcc = self.handle_addresses(from_address=account_params['from_address'],
                                            to_address=to_address, multiple_mode=multiple_mode)
        msg = self.build_base_message(subject, body, attachments=attachments, html=html, charset=charset)
        msg['From'] = from_address
        total_to = len(to)
        for i, address in enumerate(to):
            msg['To'] = address
            msg['Cc'] = cc and ','.join(cc)
            msg['Bcc'] = bcc and ','.join(bcc)
            smtp_connection.sendmail(account_params['from_address'], (address, cc, bcc), msg.as_string())
            if progress_cb:
                progress_cb(i + 1, total_to)
        smtp_connection.close()
        