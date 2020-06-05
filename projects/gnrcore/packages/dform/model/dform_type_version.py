# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('dform_type_version', pkey='id', 
                    name_long='type version', 
                    name_plural='type versions',
                    caption_field='version_code')
        self.sysFields(tbl)
        tbl.column('dform_type_id',size='22', group='_', name_long='type id'
                    ).relation('dform_type.id', 
                    relation_name='versions', mode='foreignkey', onDelete='raise')
        tbl.column('version_code', size=':10', name_long='Version code')
        tbl.column('date_from', dtype='D', name_long='From')
        tbl.column('date_to', dtype='D', name_long='To')

        tbl.formulaColumn('version_name',"""@dform_type_id.hierarchial_name || '_' || $version_code""")