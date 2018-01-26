# -*- coding: UTF-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag


caption = '!!Send email'
tags = 'admin'
description='!!Send email'


class Main(BaseResourceAction):
    batch_prefix = 'SM'
    batch_title = '!!Send email'
    batch_immediate = True
    
    def do(self):
        message_tbl = self.db.table('email.message')
        email_to_send = message_tbl.query(where='$in_out=:out AND $send_date IS NULL',
                                        out='O',order_by='$__ins_ts',
                                        bagFields=True).fetch()
        for email in email_to_send:
            message_tbl.sendMessage(pkey=email['id'])

    def table_script_parameters_pane(self, pane, **kwargs):
        pass
