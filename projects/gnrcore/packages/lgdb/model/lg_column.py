# encoding: utf-8

from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('lg_column',
                        pkey='id',
                        name_long='Column',
                        name_plural='Columns',
                        caption_field='name')
        self.sysFields(tbl)
        tbl.column('lg_table_id',size='22',name_long='Table').relation('lg_table.id',
                                                                        relation_name='columns', 
                                                                        mode='foreignkey',
                                                                        onDelete='cascade', 
                                                                        meta_thmode='dialog')
        tbl.column('name', size=':40', name_long='Name')
        tbl.column('full_name', name_long='Full Name')
        tbl.column('data_type', size=':10', name_long='Data Type')
        tbl.column('old_type', size=':10', name_long='Old Type')
        tbl.column('description', name_long='Description')
        tbl.column('notes', name_long='Notes')
        tbl.column('group', name_long='Group', batch_assign=True)


    def importColumn(self, tbl_id, colobj, import_mode=None):
        col_record = dict(lg_table_id = tbl_id, 
                                  name = colobj.name,
                                  full_name='{pkg}.{tbl}.{name}'.format(pkg=colobj.pkg.name,tbl=colobj.table.name,name=colobj.name),
                                  description = colobj.name_long,
                                  data_type=colobj.dtype)
        existing = self.query(where='$lg_table_id=:tbl_id AND $name=:name',
                                for_update=True,
                                tbl_id=tbl_id, name=colobj.name).fetch()
        if not existing:
            self.insert(col_record)
        else:
            old_col_record = dict(existing[0])
            if import_mode == 'restart':
                self.delete(old_col_record)
                self.insert(col_record)
            elif import_mode == 'update':
                col_record['id'] = old_col_record['id']
                self.update(col_record, old_col_record)
            else:
                col_record=old_col_record

        if colobj.relatedTable():
            rel_attributes = colobj.column_relation.attributes

            self.db.table('lgdb.lg_relation').importRelation(column_name=col_record['full_name'], 
                                                              **rel_attributes)