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
import re, htmlentitydefs
import mimetypes
from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrstring import templateReplace
import thread
import os

mimetypes.init() # Required for python 2.6 (fixes a multithread bug)
TAG_SELECTOR = '<[^>]*>'

mime_mapping = dict(application=MIMEApplication,
                    image=MIMEImage, text=MIMEText)

def clean_and_unescape(text):
    """Removes HTML or XML character references and entities from a text string.
    
    :param text: The HTML (or XML) source text.
    :returns: The plain text, as a Unicode string, if necessary.
    """

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
        :param from_address: the address that will appear in the recipients from field.
                             Default value is ``None``
        :param smtp_host: the smtp host to send this email. Default value is ``None``
        :param username: add???. Default value is ``None``
        :param password: the username's password (if a username is required for
                         authentication). Default value is ``None``
        :param port: if a non standard port is used then it can be overridden.
                     Default value is ``None``
        :param ssl: if True, attempt to use the ssl port. Else standard smtp port is used.
                    Default value is ``None``
        :param default: add???. Default value is ``False``
        """
        self.smtp_accounts[name] = dict(from_address=from_address,
                                        smtp_host=smtp_host, username=username,
                                        password=password, port=port, ssl=ssl)
        if default:
            self.default_smtp_account = name
            
    def set_smtp_default_account(self, name):
        """Allow to use the saved account parameters for the subsequent SMTP mails
        
        :param name: the default account's name
        """
        self.default_smtp_account = name
        
    def set_pop_default_account(self, name):
        """Allow to use the saved account parameters for the subsequent POP mails
        
        :param name: the default account's name
        """
        self.default_pop_account = name
        
    def set_imap_default_account(self, name):
        """Allow to use the saved account parameters for the subsequent IMAP mails
        
        :param name: the default account's name
        """
        self.default_imap_account = name
        
    def get_account_params(self, account=None, from_address=None, smtp_host=None, port=None,
                           user=None, password=None, ssl=False, tls=False, **kwargs):
        """Set the account parameters
        
        :param account: if an account has been defined previously with :meth:`set_smtp_account`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained. Default value is ``None``
        :param from_address: the address that will appear in the recipients from field.
                             Default value is ``None``
        :param smtp_host: the smtp host to send this email. Default value is ``None``
        :param port: if a non standard port is used then it can be overridden.
                     Default value is ``None``
        :param user: if a username is required for authentication.
                     Default value is ``None``
        :param password: the username's password (if a username is required for
                         authentication). Default value is ``None``
        :param ssl: if True, attempt to use the ssl port. Else standard smtp port is used.
                    Default value is ``None``
        :param tls: allow to communicate with an smtp server. Default value is ``False``.
                    You may choose three ways:
                    
                    1. no encryption
                    2. ssl -> all data is encrypted on a ssl layer
                    3. tls -> server and client begin communitation in a unsecure way and after a starttls command they start to encrypt data (this is the way you use to connect to gmail smtp)
        :returns: the account parameters
        """
        account = account or self.default_smtp_account
        if account:
            account_params = self.smtp_accounts[account]
        else:
            account_params = dict(smtp_host=smtp_host, port=port, user=user, password=password,
                                  ssl=ssl, tls=tls, from_address=from_address)
        return account_params
        
    def get_smtp_connection(self, account=None, smtp_host=None, port=None,
                            user=None, password=None, ssl=False, tls=False, **kwargs):
        """Get the smtp connection
        
        :param account: if an account has been defined previously with :meth:`set_smtp_account`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained. Default value is ``None``
        :param smtp_host: the smtp host to send this email. Default value is ``None``
        :param port: if a non standard port is used then it can be overridden.
                     Default value is ``None``
        :param user: if a username is required for authentication.
                     Default value is ``None``
        :param password: the username's password (if a username is required for
                         authentication). Default value is ``None``
        :param ssl: if True, attempt to use the ssl port. Else standard smtp port is used.
                    Default value is ``None``
        :param tls: allow to communicate with an smtp server. Default value is ``False``.
                    You may choose three ways:
                    
                    1. no encryption
                    2. ssl -> all data is encrypted on a ssl layer
                    3. tls -> server and client begin communitation in a unsecure way and after a starttls command they start to encrypt data (this is the way you use to connect to gmail smtp)
        :returns: the smtp connection
        """
        if ssl:
            smtp = getattr(smtplib, 'SMTP_SSL')
        else:
            smtp = getattr(smtplib, 'SMTP')
        if port:
            smtp_connection = smtp(host=str(smtp_host), port=str(port))
        else:
            smtp_connection = smtp(host=smtp_host)
        if tls:
            smtp_connection.starttls()
        if user:
            smtp_connection.login(user, password)
        return smtp_connection
        
    def handle_addresses(self, from_address=None, to_address=None, multiple_mode=None):
        """Handle the mail addresses
        
        :param from_address: the address that will appear in the recipients from field.
                             Default value is ``None``
        :param to_address: address where the email will be sent. Default value is ``None``
        :param multiple_mode: add???. Default value is ``None``
        :returns: lists of addresses
        """
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
        
        :param subject: add???
        :param body: body of the email. If you pass ``html=True`` attribute,
                     then you can pass in the body the html tags
        :param attachments: path of the attachment to be sent with the email.
                            Default value is ``None``
        :param html: add???. Default value is ``None``
        :param charset: a different charser may be defined by its standard name.
                        Default value is ``None``.
        :returns: the message
        """
        charset = charset or 'us-ascii' # us-ascii is the email default, gnr default is utf-8.
                                        # This is used to prevent explicit "charset = None" to be passed
        attachments = attachments or []
        if not html and not attachments:
            msg = MIMEText(body, 'text', charset)
            msg['Subject'] = subject
            return msg
        if html:
            msg = MIMEMultipart('alternative')
        else:
            msg = MIMEMultipart()
        msg['Subject'] = subject
        for attachment_path in attachments:
            mime_type = mimetypes.guess_type(attachment_path)[0]
            mime_family, mime_subtype = mime_type.split('/')
            attachment_file = open(attachment_path, 'rb')
            email_attachment = mime_mapping[mime_family](attachment_file.read(), mime_subtype)
            msg.add_header('content-disposition', 'attachment', filename=os.path.basename(attachment_path))
            msg.attach(email_attachment)
            attachment_file.close()
        if html:
            msg.attach(MIMEText(clean_and_unescape(body), 'text', charset))
            msg.attach(MIMEText(body, 'html', charset))
        else:
            msg.attach(MIMEText(body, 'text', charset))
        return msg
        
    def sendmail_template(self, datasource, to_address=None, cc_address=None, bcc_address=None, subject=None,
                          from_address=None, body=None, attachments=None, account=None,
                          smtp_host=None, port=None, user=None, password=None,
                          ssl=False, tls=False, html=False, charset='utf-8', async=False, **kwargs):
        """Add???
        
        :param datasource: add???
        :param to_address: address where the email will be sent. Default value is ``None``
        :param cc_address: can be a comma deliminated str of email addresses or a list or tuple.
                           Default value is ``None``
        :param bcc_address: can be a comma deliminated str of email addresses or a list or tuple.
                            Default value is ``None``
        :param subject: add???. Default value is ``None``
        :param from_address: the address that will appear in the recipients from field.
                             Default value is ``None``
        :param body: body of the email. If you pass ``html=True`` attribute,
                     then you can pass in the body the html tags. Default value is ``None``
        :param attachments: path of the attachment to be sent with the email.
                            Default value is ``None``
        :param account: if an account has been defined previously with :meth:`set_smtp_account`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained. Default value is ``None``
        :param smtp_host: the smtp host to send this email. Default value is ``None``
        :param port: if a non standard port is used then it can be overridden.
                     Default value is ``None``
        :param user: if a username is required for authentication.
                     Default value is ``None``
        :param password: the username's password (if a username is required for
                         authentication). Default value is ``None``
        :param ssl: if True, attempt to use the ssl port. Else standard smtp port is used.
                    Default value is ``None``
        :param tls: allow to communicate with an smtp server. Default value is ``False``.
                    You may choose three ways:
                    
                    1. no encryption
                    2. ssl -> all data is encrypted on a ssl layer
                    3. tls -> server and client begin communitation in a unsecure way and after a starttls command they start to encrypt data (this is the way you use to connect to gmail smtp)
        
        :param html: if True, html tags can be used in the body of the email. Appropriate headers are attached.
                     The default value is ``False``.
        :param charset: a different charser may be defined by its standard name.
                        Default value is ``utf-8``.
        :param async: if True, then a separate process is spawned to send the email and control
                      is returned immediately to the calling function. The default value is ``False``.
        """
        
        def get_templated(field):
            value = datasource.get(field)
            
            if value:
                return templateReplace(value, datasource)
                
        to_address = to_address or get_templated('to_address')
        cc_address = cc_address or get_templated('cc_address')
        bcc_address = bcc_address or get_templated('bcc_address')
        from_address = from_address or get_templated('from_address')
        subject = subject or get_templated('subject')
        body = body or get_templated('body')
        body = templateReplace(body, datasource)
        self.sendmail(to_address, subject=subject, body=body, cc_address=cc_address, bcc_address=bcc_address,
                      attachments=attachments, account=account,
                      from_address=from_address, smtp_host=smtp_host, port=port, user=user, password=password,
                      ssl=ssl, tls=tls, html=html, charset=charset, async=async)
                      
    def sendmail(self, to_address=None, subject=None, body=None, cc_address=None, bcc_address=None, attachments=None,
                 account=None,
                 from_address=None, smtp_host=None, port=None, user=None, password=None,
                 ssl=False, tls=False, html=False, charset='utf-8', async=False, **kwargs):
        """Send mail is a function called from the postoffice object to send an email.
        
        :param to_address: address where the email will be sent
        :param subject: subject of the email
        :param body: body of the email. If you pass ``html=True`` attribute,
                     then you can pass in the body the html tags.
                     Default value is ``None``
        :param cc_address: can be a comma deliminated str of email addresses or a list or tuple.
                           Default value is ``None``
        :param bcc_address: can be a comma deliminated str of email addresses or a list or tuple.
                            Default value is ``None``
        :param attachments: path of the attachment to be sent with the email.
                            Default value is ``None``
        :param account: if an account has been defined previously with :meth:`set_smtp_account`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained. Default value is ``None``
        :param from_address: the address that will appear in the recipients from field.
                             Default value is ``None``
        :param smtp_host: the smtp host to send this email. Default value is ``None``
        :param port: if a non standard port is used then it can be overridden.
                     Default value is ``None``
        :param user: if a username is required for authentication.
                     Default value is ``None``
        :param password: the username's password (if a username is required for
                         authentication). Default value is ``None``
        :param ssl: if True, attempt to use the ssl port. Else standard smtp port is used.
                    Default value is ``None``
        :param tls: allow to communicate with an smtp server (the default value is ``False``). You may choose three ways:
                    
                    1. no encryption
                    
                    2. ssl -> all data is encrypted on a ssl layer
                    
                    3. tls -> server and client begin communitation in a unsecure way and after
                               a starttls command they start to encrypt data (this is the way you use to connect to gmail smtp)
                    
        :param html: if True then html tags can be used in the body of the email. Appropriate headers are attached.
                     The default value is ``False``.
        :param charset: a different charser may be defined by its standard name.
                        Default value is ``utf-8``.
        :param async: if set to true, then a separate process is spawned to send the email and control
                      is returned immediately to the calling function. The default value is ``False``.
        """
        
        account_params = self.get_account_params(account=account, from_address=from_address,
                                                 smtp_host=smtp_host, port=port, user=user, password=password, ssl=ssl,
                                                 tls=tls)
        from_address = account_params['from_address']
        msg = self.build_base_message(subject, body, attachments=attachments, html=html, charset=charset)
        msg['From'] = from_address
        msg['To'] = to_address
        if  type(cc_address).__name__ in ['list', 'tuple']:
            msg['Cc'] = cc_address and ','.join(cc_address)
        else:
            msg['Cc'] = cc_address
        if  type(bcc_address).__name__ in ['list', 'tuple']:
            msg['Bcc'] = bcc_address and ','.join(bcc_address)
        else:
            msg['Bcc'] = bcc_address
        msg_string = msg.as_string()
        if not async:
            self._sendmail(account_params, from_address, to_address, cc_address, bcc_address, msg_string)
        else:
            thread.start_new_thread(self._sendmail,
                                    (account_params, from_address, to_address, cc_address, bcc_address, msg_string))
                                    
    def _sendmail(self, account_params, from_address, to_address, cc_address, bcc_address, msg_string):
        smtp_connection = self.get_smtp_connection(**account_params)
        smtp_connection.sendmail(from_address, (to_address, cc_address, bcc_address), msg_string)
        smtp_connection.close()
        
    def sendmail_many(self, to_address, subject, body, attachments=None, account=None,
                      from_address=None, smtp_host=None, port=None, user=None, password=None,
                      ssl=False, tls=False, html=False, multiple_mode=False, progress_cb=None, charset='utf-8',
                      async=False):
        """
        :param to_address: address where the email will be sent
        :param subject: subject of the email
        :param body: body of the email. If you pass ``html=True`` attribute,
                     then you can pass in the body the html tags
        :param attachments: path of the attachment to be sent with the email.
                            Default value is ``None``
        :param account: if an account has been defined previously with :meth:`set_smtp_account`
                        then this account can be used instead of having to repeat all the mail
                        parameters contained. Default value is ``None``
        :param from_address: the address that will appear in the recipients from field.
                             Default value is ``None``
        :param smtp_host: the smtp host to send this email. Default value is ``None``
        :param port: if a non standard port is used then it can be overridden.
                     Default value is ``None``
        :param user: if a username is required for authentication.
                     Default value is ``None``
        :param password: the username's password (if a username is required for
                         authentication). Default value is ``None``
        :param ssl: if True, attempt to use the ssl port. Else standard smtp port is used.
                    Default value is ``None``
        :param tls: allow to communicate with an smtp server. Default value is ``False``.
                    You may choose three ways:
                    
                    1. no encryption
                    2. ssl -> all data is encrypted on a ssl layer
                    3. tls -> server and client begin communitation in a unsecure way and after a starttls command they start to encrypt data (this is the way you use to connect to gmail smtp)
        
        :param html: if True, html tags can be used in the body of the email. Appropriate headers are attached.
                     The default value is ``False``.
        
        ???
        :param multiple_mode: allow to send a mail to many addresses. Its parameters are:
                              
                              ``False`` - single mail for recipient
                              
                              ``to, To, TO`` - a mail sent to all recipient in to field
                              
                              ``bcc, Bcc, BCC`` - a mail sent to ourself with all recipient in bcc address
                              
                              Default value is ``False``.
        
        :param charset: a different charser may be defined by its standard name.
                        Default value is ``utf-8``.
        """
        account_params = self.get_account_params(account=account, from_address=from_address,
                                                 smtp_host=smtp_host, port=port, user=user, password=password, ssl=ssl,
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
