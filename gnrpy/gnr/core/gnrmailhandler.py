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
from gnr.core.gnrstring import templateReplace
import thread
mimetypes.init() # Required for python 2.6 (fixes a multithread bug)
TAG_SELECTOR='<[^>]*>'

mime_mapping=dict(application=MIMEApplication,
                    image=MIMEImage, text=MIMEText)

def clean_and_unescape(text):
    """
    Removes HTML or XML character references and entities from a text string.
    
    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary.
    
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
        return text # leave as is
    text=re.sub(TAG_SELECTOR, '', text)
    return re.sub("&#?\w+;", fixup, text)

class MailHandler(object):

    def __init__(self, parent=None):
        self.parent = parent
        self.smtp_accounts = {}
        self.default_smtp_account = None
        self.pop_accounts = {}
        self.default_pop_account = None
        self.imap_accounts = {}
        self.default_imap_account = None
    
    def set_smtp_account(self, name, from_address=None, host=None, username=None, password=None, port=None, ssl=False, default=False):
        self.smtp_accounts[name]= dict(from_address=from_address, 
                                        host=host, username=username, 
                                        password=password, port=port, ssl=ssl)
        if default:
            self.default_smtp_account = name
    
    def set_smtp_default_account(self, name):
        self.default_smtp_account = name
    
    def set_pop_default_account(self, name):
        self.default_pop_account = name

    def set_imap_default_account(self, name):
        self.default_imap_account = name
    
    def get_account_params(self, account=None, from_address=None, host=None, port=None, 
                            user=None, password=None, ssl=False, tls=False, **kwargs):
        account = account or self.default_smtp_account
        if account:
            account_params = self.smtp_accounts[account]
        else:
            account_params = dict(host = host, port = port, user = user, password = password,
                                ssl=ssl, tls=tls, from_address=from_address)
        return account_params

    def get_smtp_connection(self, account=None, host=None, port=None, 
                            user=None, password=None, ssl=False, tls=False, **kwargs):
        if ssl:
            smtp=getattr(smtplib,'SMTP_SSL')
        else:
            smtp=getattr(smtplib,'SMTP')
        if port:
            smtp_connection = smtp(host=host, port=port)
        else:
            smtp_connection = smtp(host=host)
        if tls:
            smtp_connection.starttls()
        if user:
            smtp_connection.login(user, password)
        return smtp_connection
    
    def handle_addresses(self, from_address=None, to_address=None, multiple_mode=None):
        cc = bcc = None
        if isinstance(to_address, basestring):
            to_address = [address.strip() for address in to_address.replace(';',',').split(',') if address]
        multiple_mode = (multiple_mode or '').lower().strip()
        if multiple_mode=='to':
            to = [','.join(to_address)]
        elif multiple_mode=='bcc': # jbe changed this from ccn to bcc
            to = [from_address]
            bcc = ','.join(to_address)
        elif multiple_mode=='cc':
            to = [from_address]
            cc = ','.join(to_address)
        else:
            to = to_address
        return to, cc, bcc
    
    def build_base_message(self, subject, body, attachments=None, html=None, charset=None):
        charset = charset or 'us-ascii' # us-ascii is the email default gnr default is utf-8 this is used to prevent explicit charset = None to be passed
        attachments = attachments or []
        if not html and not attachments:
            msg = MIMEText(body,'text',charset)
            msg['Subject'] = subject
            return msg
        if html:
            msg = MIMEMultipart('alternative')
        else:
            msg = MIMEMultipart()
        msg['Subject'] = subject
        for attachment_path in attachments:
            mime_type = mimetypes.guess_type(attachment_path)[0]
            mime_family,mime_subtype = mime_type.split('/')
            attachment_file = open(attachment_path,'rb')
            email_attachment = mime_mapping[mime_family](attachment_file.read(),mime_subtype)
            msg.attach(email_attachment)
            attachment_file.close()
        if html:
            msg.attach(MIMEText(clean_and_unescape(body),'text',charset))
            msg.attach( MIMEText(body,'html',charset))
        else:
            msg.attach(MIMEText(body,'text',charset))
        return msg
    
    def sendmail_template(self, datasource, to_address=None, cc_address=None, bcc_address=None, subject=None, from_address=None, body=None, attachments=None, account=None,
                            host=None, port=None, user=None, password=None, 
                            ssl=False, tls=False, html=False,  charset='utf-8',async=False):
        def get_templated(field):
            value = datasource.get(field)
            if value:
                return templateReplace(value,datasource)
        to_address = to_address or get_templated('to_address')
        cc_address = cc_address or get_templated('cc_address')
        bcc_address = bcc_address or get_templated('bcc_address')
        from_address = from_address or get_templated('from_address')
        subject = subject or get_templated('subject')
        body = body or get_templated('body')
        self.sendmail(to_address, subject=subject, body=body,cc_address=cc_address,bcc_address=bcc_address, attachments=attachments, account=account,
                            from_address=from_address, host=host, port=port, user=user, password=password, 
                            ssl=ssl, tls=tls, html=html, charset=charset,async=async)
    
    def sendmail(self, to_address, subject, body, cc_address=None,bcc_address=None, attachments=None, account=None,
                        from_address=None, host=None, port=None, user=None, password=None, 
                        ssl=False, tls=False, html=False, charset='utf-8', async=False):
        account_params = self.get_account_params(account=account, from_address=from_address, 
                            host=host, port=port, user=user, password=password, ssl=ssl, tls=tls)
        from_address=account_params['from_address']
        msg = self.build_base_message(subject, body, attachments=attachments, html=html, charset=charset)
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Cc'] = cc_address# and ','.join(cc_address) #JBE found this code was splitting on each character assuming cc_address was a list I think
        msg['Bcc'] = bcc_address# and ','.join(bcc_address)
        msg_string = msg.as_string()
        print 'CC: ', msg['Cc']
        print 'msg: ', msg_string
        if not async:
            self._sendmail(account_params,from_address, to_address, cc_address, bcc_address,msg_string)
        else:
            thread.start_new_thread(self._sendmail, (account_params, from_address, to_address, cc_address, bcc_address, msg_string))
        
    def _sendmail(self, account_params, from_address, to_address, cc_address, bcc_address, msg_string):
        smtp_connection = self.get_smtp_connection(**account_params)
        smtp_connection.sendmail(from_address, (to_address,cc_address,bcc_address), msg_string)
        smtp_connection.close()
    
    def sendmail_many(self, to_address, subject, body, attachments=None, account=None,
                        from_address=None, host=None, port=None, user=None, password=None, 
                        ssl=False, tls=False, html=False, multiple_mode=False, progress_cb=None, charset='utf-8', async=False):
        """
        multiple_mode can be:
                False - single mail for recipient
                to, To, TO - a mail sent to all recipient in to field
                bcc, Bcc, BCC - a mail sent to ourself with all recipient in bcc address
        """
        account_params = self.get_account_params(account=account, from_address=from_address, 
                            host=host, port=port, user=user, password=password, ssl=ssl, tls=tls)
        smtp_connection = self.get_smtp_connection(**account_params)
        to, cc, bcc = self.handle_addresses(from_address=account_params['from_address'],
                        to_address=to_address, multiple_mode=multiple_mode)
        msg = self.build_base_message(subject, body, attachments=attachments, html=html, charset=charset)
        msg['From'] = from_address
        total_to = len(to)
        for i,address in enumerate(to):
            msg['To'] = address
            msg['Cc'] = cc and ','.join(cc)
            msg['Bcc'] = bcc and ','.join(bcc)
            smtp_connection.sendmail(account_params['from_address'], (address,cc,bcc), msg.as_string())
            if progress_cb:
                progress_cb(i+1,total_to)
        smtp_connection.close()
