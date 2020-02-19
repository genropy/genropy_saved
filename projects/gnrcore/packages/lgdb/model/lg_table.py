# encoding: utf-8

import os
from gnr.core.gnrdecorator import public_method


class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('lg_table',
                        pkey='id', name_long='Legacy table',
                        name_plural='Legacy tables',
                        caption_field='sqlname')
        self.sysFields(tbl)
        tbl.column('lg_pkg', name_long='Package').relation('lg_pkg.code',
                                                            relation_name='lg_tables', 
                                                            mode='foreignkey',
                                                            onDelete='cascade',
                                                            meta_thmode='dialog')
        tbl.column('name',name_long='Name', indexed=True)
        tbl.column('sqlname', name_long='SqlName', indexed=True)
        tbl.column('description',name_long='Description', indexed=True)
        tbl.column('notes', name_long='Notes')
        tbl.column('group', name_long='Group', batch_assign=True)
        
        tbl.column('multidb', name_long='Multi DB', values='*:Replicated on all databases,one:Replicated on one specific database,true:Only subscripted records')

    @public_method
    def importTable(self, pkg_code=None,  tblobj=None, import_mode=None):
        tbl_record = self.newrecord(lg_pkg = pkg_code,
                           name=tblobj.name,
                           sqlname = tblobj.sqlname,
                           description=tblobj.name_long)

        existing = self.query(where='$sqlname=:sqlname',
                                for_update=True,
                                sqlname=tblobj.sqlname).fetch()
        if not existing:
            self.insert(tbl_record)
        else:
            old_tbl_record = dict(existing[0])
            if import_mode == 'restart':
                self.delete(old_tbl_record)
                self.insert(tbl_record)
            elif import_mode == 'update':
                tbl_record['id'] = old_tbl_record['id']
                self.update(tbl_record, old_tbl_record)
            else:
                tbl_record=old_tbl_record

        for col_obj in tblobj.columns.values():
            self.db.table('lgdb.lg_column').importColumn(tbl_record['id'], col_obj, import_mode=None)
            