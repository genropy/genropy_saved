# -*- coding: utf-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag


caption = '!!Send emails'
tags = 'admin'
description='!!Send emails'


class Main(BaseResourceAction):
    batch_prefix = 'SM'
    batch_title = '!!Send emails'
    batch_immediate = True
    
    def do(self):
        message_tbl = self.db.table('email.message')
        email_to_send = message_tbl.query(where='$in_out=:out AND $send_date IS NULL',
                                        out='O',order_by='$__ins_ts',
                                        bagFields=True).fetch()
        print 'sending mail',len(email_to_send)
        for email in email_to_send:
            print '.',
            message_tbl.sendMessage(pkey=email['id'])
        print 'all mail sent'

    def table_script_parameters_pane(self, pane, **kwargs):
        pass
