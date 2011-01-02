#!/usr/bin/env python
# encoding: utf-8

# item table is used to define the form_items on the form.  They are placed into a group.
# into their own formBuilder within the group formBuider, which in turn is inside the section formBuilder.


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('item', pkey='id', name_long='!!Item', rowcaption='label')
        self.sysFields(tbl, id=False)
        tbl.column('id', size='22', group='_', readOnly='y', name_long='Id')
        tbl.column('section_id', size='22', group='_').relation('section.id',
                                                                many_name='Group',
                                                                one_name='Section',
                                                                mode='foreignkey',
                                                                onDelete='delete',
                                                                one_group='')
        tbl.column('group_id', size='22', group='_').relation('group.id',
                                                              many_name='Form Item',
                                                              one_name='Group',
                                                              mode='relation',
                                                              onDelete='delete',
                                                              one_group='')
        tbl.column('code', size=':20', name_long='!!Code', index=True)
        tbl.column('short_code', size=':10', name_long='!!Short Code', index=True)
        tbl.column('label', 'T', name_long='!!Label')
        tbl.column('name', 'T', name_long='!!Long Name')
        tbl.column('colspan', 'I', name_long='!!Colspan')
        tbl.column('rowspan', 'I', name_long='!!Rowspan')
        tbl.column('version', size=':30', name_long='!!Version')
        tbl.column('sort_order', size=':5', name_long='!!Sort Order')

        #tbl.column('form_text','T', name_long='!!Form Text')
        #tbl.column('form_text_style', size=':20', name_long='!!Text Style')
        tbl.column('answer_type', size=':2', name_long='!!Answer Type')
        tbl.column('value_list',
                   name_long='!!Value List') #comma delimited string of values to be used for dbCombo or filteringSelect
        tbl.column('exclude', 'B', name_long='!!Exclude')
        tbl.column('default_value', 'T', name_long='!!Default Value')
        tbl.column('height', size=':5', name_long='!!Height')
        tbl.column('width', size=':5', name_long='!!Width')
        tbl.column('tooltip', 'T', name_long='!!Tooltip')
        tbl.column('formula', 'T', name_long='!!Formula')

    def trigger_onInserted(self, record_data):
        self.calculateCode(record_data)

    def trigger_onUpdating(self, record_data, old_record=None):
        self.calculateCode(record_data)

    def calculateCode(self, record_data):
        pkey = record_data['section_id']
        form_id = self.db.table('qfrm.section').readColumns(pkey, '$form_id')
        form_code = self.db.table('qfrm.form').readColumns(form_id, '$code')
        record_data['code'] = '%s.%s' % (form_code, record_data['short_code'])
        print record_data['code']
