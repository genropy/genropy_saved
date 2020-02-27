# -*- coding: utf-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag


caption = '!!Send messages'
tags = 'admin'
description='!!Send send messages'


class Main(BaseResourceAction):
    batch_prefix = 'Send Messages'
    batch_title = '!!Send Messages'
    batch_immediate = True
    
    def do(self):
        for message_id in self.get_selection_pkeys():
            try:
                self.message_tbl.sendMessage(pkey=message_id)
            except Exception as e:
                self.batch_log_id('Error sending mail message {message_id}'.format(message_id=message_id))

    def table_script_parameters_pane(self, pane, **kwargs):
        pass
