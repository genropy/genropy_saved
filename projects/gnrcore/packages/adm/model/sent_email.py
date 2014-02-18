#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('sent_email', pkey='id', name_long='Sent email', name_plural='!!Sent email',caption_field='batch_key')
        self.sysFields(tbl)
        tbl.column('code',name_long='!!Code')
        tbl.column('tbl',name_long='!!Table')
        tbl.column('mail_address',name_long='!!Email address')
        tbl.column('sent_ts',dtype='DH',name_long='!!Sent ts')
        tbl.column('record_id',name_long='Record id')
