# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('dform_data', pkey='id', name_long='!![en]Dform Data', 
                    name_plural='!![en]Dform data',caption_field='name')
        self.sysFields(tbl,counter='dform_type_version_id')
        tbl.column('dform_type_version_id',size='22', group='_', name_long='!![en]Type version'
                    ).relation('dform_type_version.id', 
                                    relation_name='data_elements', 
                                    mode='foreignkey', onDelete='raise')
        tbl.column('name', size=':30', name_long='!![en]Name')
        tbl.column('date_from', dtype='D', name_long='From')
        tbl.column('date_to', dtype='D', name_long='To')

        tbl.column('values', dtype='X', name_long='!![en]Values')
        tbl.column('options', dtype='X', name_long='!![en]Options')