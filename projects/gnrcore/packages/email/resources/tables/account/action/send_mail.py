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
        self.message_tbl = self.db.table('email.message')
        accounts = self.tblobj.query(where='$save_output_message IS TRUE').fetch()
        for account in accounts:
            self.sendEmailsForAccount(account)
    
    def sendEmailsForAccount(self,account):
        email_to_send = self.message_tbl.query(where="""$in_out=:out AND $send_date IS NULL 
                                                        AND $account_id=:acid 
                                                        AND $error_msg IS NULL""",
                                        out='O',order_by='$__ins_ts',
                                        limit=account['send_limit'],
                                        acid=account['id'],
                                        bagFields=True).fetch()
        for message in email_to_send:
            try:
                self.message_tbl.sendMessage(pkey=message['id'])
            except Exception as e:
                raise
                #self.batch_log_write('Error sending mail message {message_id}'.format(message_id=email['id']))

    def table_script_parameters_pane(self, pane, **kwargs):
        pass
