#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Season """
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
        
