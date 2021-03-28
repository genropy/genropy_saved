# encoding: utf-8

import os
from gnr.core.gnrdecorator import public_method
from gnr.core import gnrlist


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
        tbl.column('primary_key',name_long='Pkey', indexed=True)
        tbl.column('sqlname', name_long='SqlName', indexed=True)
        tbl.column('description',name_long='Description', indexed=True)
        tbl.column('notes', name_long='Notes')
        tbl.column('group', name_long='Group', batch_assign=True)
    
        tbl.column('multidb', name_long='Multi DB', values='*:Replicated on all databases,one:Replicated on one specific database,true:Only subscripted records')
        tbl.aliasColumn('legacy_db','@lg_pkg.legacy_db',static=True)
        tbl.aliasColumn('legacy_schema','@lg_pkg.legacy_schema',static=True)

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
            

    @public_method(caption='Import columns and relations')
    def actionMenu_importColumns(self,pkey=None,selectedPkeys=None,**kwargs):
        selectedPkeys = selectedPkeys or [pkey]
        f = self.query(where='$id IN :selectedPkeys',selectedPkeys=selectedPkeys).fetch()
        legacy_db = f[0]['legacy_db']
        legacy_schema = f[0]['legacy_schema']
        if not legacy_db:
            return
        extdb = self.db.table('lgdb.lg_pkg').getLegacyDb(legacy_db)
        tblpkeys = []
        for tbl in f:
            self._importColumnsFromTbl(extdb,legacy_schema,tbl)
            tblpkeys.append(tbl['id'])
        lg_rel_tbl = self.db.table('lgdb.lg_relation')
        lg_columns = self.db.table('lgdb.lg_column').query(where='$lg_table_id IN :tblpkeys',
                                                            tblpkeys=tblpkeys).fetchAsDict('full_name')
        relations = extdb.adapter.relations()

        for (many_rel_name, many_schema, many_table, 
            many_cols, one_rel_name, one_schema, 
            one_table, one_cols, upd_rule, 
            del_rule, init_defer) in relations:
            many_field = many_cols[0]
            one_field = one_cols[0]
            column = '%s.%s.%s' % (many_schema, many_table, many_field)
            related_column = '%s.%s.%s' % (one_schema, one_table, one_field)
            if column in lg_columns and related_column in lg_columns:
                rel_record = dict(relation_column = column, 
                                related_column=related_column)
                lg_rel_tbl.insert(rel_record)
        self.db.commit()
    
    def _importColumnsFromTbl(self,extdb,legacy_schema,tbl):
        tbl_name = tbl['name']
        columns = list(extdb.adapter.getColInfo(schema=legacy_schema, table=tbl_name))
        gnrlist.sortByItem(columns, 'position')
        lg_column = self.db.table('lgdb.lg_column')
        lg_column.deleteSelection('lg_table_id',tbl['id'])
        for col_dict in columns:
            col_dict.pop('position')
            colname = col_dict.pop('name')
            length = col_dict.pop('length', 0)
            decimals = col_dict.pop('decimals', 0)
            description = col_dict.pop('description', None)
            dtype = col_dict['dtype']
            if dtype == 'A':
                col_dict['size'] = '0:%s' % length
            elif dtype == 'C':
                col_dict['dtype'] = 'A'
                col_dict['size'] = length
            lg_column.insert(lg_column.newrecord(name=colname,data_type=col_dict['dtype'], description=description, name_long=description,
            lg_column.insert(lg_column.newrecord(name=colname,data_type=col_dict['dtype'], description=col_dict.get('description'),
                                                full_name='{pkg}.{tbl}.{name}'.format(pkg=legacy_schema,tbl=tbl_name,name=colname),
                                                lg_table_id=tbl['id']))


