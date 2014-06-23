# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
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
# 
import os
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace

class SendMail(object):
    def sendMailTemplate(self, tpl, mailto, params, locale=None, **kwargs):
        locale = locale or self.locale
        localelang = locale.split('-')[0]
        mailtpl = self.getMailTemplate(tpl, locale=localelang)

        if mailtpl:
            subject = templateReplace(mailtpl['subject'], params)
            body = templateReplace(mailtpl['body'], params)
            self.application.sendmail(mailtpl['from_address'], mailto, subject, body)
            return 'mail sent'

    def getMailTemplate(self, tpl, locale):
        localelang = locale.split('-')[0]
        tplfile = self.getResource(os.path.join('mail_templates', localelang, tpl))
        if not tplfile:
            tplfile = self.getResource(os.path.join('mail_templates', tpl))
        if tplfile:
            return Bag(tplfile)


    def sendMailTemplateMany(self, tpl, mailto_param, locale_param, params_list, **kwargs):
        mailtpldict = {}
        send_errors = []
        for params in params_list:
            locale = params.get(locale_param) or self.locale
            mailtpl = mailtpldict.get(locale)
            if not mailtpl:
                mailtpl = self.getMailTemplate(tpl, locale=locale)
                mailtpldict[locale] = mailtpl
            try:
                subject = templateReplace(mailtpl['subject'], params)
                body = templateReplace(mailtpl['body'], params)
                self.application.sendmail(mailtpl['from_address'], params[mailto_param], subject, body)
            except:
                send_errors.append(params[mailto_param])
        return send_errors
        