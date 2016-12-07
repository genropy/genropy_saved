#!/usr/bin/env python
# encoding: utf-8
import os

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('backup', pkey='id', name_long='!!Backup', name_plural='!!Backups',rowcaption="$name")
        self.sysFields(tbl)
        tbl.column('name' ,name_long='!!Name')
        tbl.column('start_ts',dtype='DH',name_long='!!Backup start ts')
        tbl.column('end_ts',dtype='DH',name_long='!!Backup end ts')
        tbl.formulaColumn('dl_link',""" '/_site/maintenance/backups/'|| $name """)

    def trigger_onDeleted(self,record):
        try:
            path = self.db.application.site.getStaticPath('site:maintenance','backups','%s.zip' %record['name'])
            print 'backup to delete',path
            os.remove(path)
        except Exception:
            pass