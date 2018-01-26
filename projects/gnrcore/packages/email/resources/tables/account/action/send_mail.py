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
        self.mail_handler = self.page.getService('mail')
        email_to_send = message_tbl.query(where='$in_out=:out AND $send_date IS NULL',
                                        out='O',order_by='$__ins_ts',
                                        bagFields=True).fetch()
        account_dict = self.tblobj.query(where='$smtp_host IS NOT NULL').fetchAsDict('id')
        attachments_dict = self.db.table('email.message_atc').query(where='$maintable_id IN :messages',
                                                                messages=[r['id'] for r in in email_to_send]
                                                                ).fetchGrouped('maintable_id')
        for email in email_to_send:
            try:
                extra_headers = Bag(email['extra_headers'])
                account_rec = account_dict[email['account_id']]
                bcc_address = email['bcc_address']
                attachments =  attachments_dict.get(email['id'],[])
                if account_rec['system_bcc']:
                    bcc_address = '%s,%s' %(bcc_address,account_rec['system_bcc']) if bcc_address else account_rec['system_bcc']
                self.mail_handler.sendmail(to_address=email['to_address'],
                                    body=email['body'], subject=email['subject'],
                                    cc_address=email['cc_address'], bcc_address=bcc_address,
                                    from_address=email['from_address'] or account_rec['smtp_from_address'],
                                    attachments=attachments, 
                                    account=mp['account'],
                                    smtp_host=mp['smtp_host'], port=mp['port'], user=mp['user'], password=mp['password'],
                                    ssl=mp['ssl'], tls=mp['tls'], html=mp['html'], async=False)
            except expression as identifier:
                pass
            finally:
                pass


    def table_script_parameters_pane(self, pane, **kwargs):
        pass
