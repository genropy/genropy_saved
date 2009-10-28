#!/usr/bin/env python
# encoding: utf-8

# section table is the top level table to define the custom form.
# it is the form definition.

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('section',  pkey='id', name_long='!!Section', rowcaption='short_name')
        self.sysFields(tbl,id=False)
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('form_id',size='22', group='_').relation('form.id',
                                                                 many_name='Section',
                                                                 one_name='Form',
                                                                 mode='foreignkey',
                                                                 onDelete='delete',
                                                                 one_group='')
        tbl.column('code', size=':10',name_long='!!Code')
        tbl.column('name', size=':60',name_long='!!Short Name')
        tbl.column('long_name', size=':60',name_long='!!Long Name') 
        tbl.column('cols', 'I',name_long='!!Section columns')
        tbl.column('rows', 'I',name_long='!!Section rows')
        tbl.column('sort_order', size=':5',name_long='!!Sort Order')

        

