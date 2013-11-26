#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('client', rowcaption='$code',caption_field='code',name_long='!!Hosting client',name_plural='!!Hosting clients')
        self.sysFields(tbl)

        #tbl.column('anagrafica_id',size=':22',name_long='!!').relation('sw_base.anagrafica.id',
        #            mode='foreignkey', onDelete='raise')
        tbl.column('user_id', size=':22', name_long='!!User ID').relation('adm.user.id', mode='foreignkey',
                                                                          onDelete='raise')
        tbl.column('code', name_long='!!Code')
        tbl.column('hosted_data', 'X', name_long='!!Hosted data')
        # dtype -> sql
        #   I       int
        #   R       float
        #   DH      datetime
        #   H       time
