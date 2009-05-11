#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Saverio Porcari on 2007-05-10.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from logging.handlers import SMTPHandler

from gnr.core.gnrlog import gnrlogging

from gnr.core import gnrstring

class Package(object):
    
    def config_attributes(self):
        return dict(sqlschema='gnr', comment='A common admin schema',name_full='Database Administration')

    def config_db(self, pkg):
        user = pkg.table('user', nome_short='Users', pkey='id')
        user.column('id', size='20')
        user.column('name', size='0:60', unique='y')
        user.column('password',  size='0:20')
        user.column('email', size='0:60')
        
        transactiontbl = pkg.externalPackage('gnr').table('transaction')
        transactiontbl.column('user_id').relation('admin.user.id')
        
        group = pkg.table('group', nome_short='Groups', pkey='id')
        group.column('id', size='20')
        group.column('name', size='0:60', unique='y')
        
        user_group = pkg.table('users_groups', name_short='Users in groups', pkey='id')
        user_group.column('id', size='22')
        user_group.column('user_id', size='20', indexed='y').relation('admin.user.id')
        user_group.column('group_id', size='20', indexed='y').relation('admin.group.id')
        
        session = pkg.table('session', nome_short='Sessions', pkey='id')
        session.column('id', size='22')
        session.column('user_id', size='20', indexed='y').relation('admin.user.id')
        session.column('ts_start', 'DH', indexed='y')
        session.column('ts_end', 'DH', indexed='y')
        
        transactiontbl.column('session_id').relation('admin.session.id')
        
    def mailLog(self, subject):
        subject = "[GENROPY_LOG] %s" % subject
        mailhost = self.attributes.get('smtp_server')
        fromaddr = self.attributes.get('emails_db_from')
        toaddrs =  gnrstring.splitAndStrip(self.attributes.get('emails_db_manager', ''), ',')
        if mailhost and toaddrs:
            if ':' in mailhost:
                mailhost = mailhost.split(':')
            mailhandler = SMTPHandler(mailhost, fromaddr, toaddrs, subject)
            mailhandler.setLevel(gnrlogging.ERROR)
            gnrlogging.getLogger('').addHandler(mailhandler)
        
