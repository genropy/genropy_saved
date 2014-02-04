#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
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

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrmailhandler import MailHandler
from gnr.core.gnrbag import Bag
from gnr.web.gnrbaseclasses import TableTemplateToHtml
from gnr.core.gnrstring import templateReplace

class WebMailHandler(MailHandler):
    def getDefaultMailAccount(self):
        mp = self.parent.getUserPreference('mail', pkg='adm') or Bag()
        if not mp['smtp_host'] and not mp['email_account_id']:
            mp = self.parent.getPreference('mail', pkg='adm')
        if not mp['smtp_host'] and not mp['email_account_id']:
            mp = self.parent.db.application.config.getNode('mail').attr
        if mp.get('email_account_id'):
            return self.parent.db.table('email.account').getSmtpAccountPref(mp['email_account_id'])
        return mp

    def sendUserTemplateMail(self,record_id=None,letterhead_id=None,template_id=None,table=None,template_code=None,attachments=None,**kwargs):
        if template_id:
            tpl,table = self.parent.db.table('adm.userobject').readColumns(pkey=template_id,columns='$data,$tbl',bagFields=True)
        elif template_code and table:
            tpl = self.parent.db.table('adm.userobject').readColumns(where='$tbl=:tb AND $code=:tc AND $objtype=:ot',
                                                             ot='template',tc=template_code,tb=table,
                                                             columns='$data',bagFields=True)
        tpl = Bag(tpl)
        metadata = tpl['metadata']
        compiled = tpl['compiled']
        email_compiled = metadata['email_compiled']
        htmlbuilder = TableTemplateToHtml(table=self.parent.db.table(table))
        html_text = htmlbuilder(record=record_id,template=compiled,letterhead_id=letterhead_id or metadata['default_letterhead'])
        to_address = templateReplace(email_compiled.getItem('to_address',''),htmlbuilder.record)
        subject = templateReplace(email_compiled.getItem('subject',''),htmlbuilder.record)
        cc_address = templateReplace(email_compiled.getItem('cc_address',''),htmlbuilder.record)
        bcc_address = templateReplace(email_compiled.getItem('bcc_address',''),htmlbuilder.record)
        from_address = templateReplace(email_compiled.getItem('from_address',''),htmlbuilder.record)
        attachments = attachments or templateReplace(email_compiled.getItem('attachments',''),htmlbuilder.record)
        if attachments and isinstance(attachments,basestring):
            attachments = attachments.replace('\n',',').split(',')

        assert to_address,'Missing email address'
        kwargs.setdefault('html',True)
        self.sendmail(to_address=to_address,subject=subject,cc_address=cc_address, bcc_address=bcc_address,
                      from_address=from_address, body=html_text,attachments=attachments,**kwargs)
    