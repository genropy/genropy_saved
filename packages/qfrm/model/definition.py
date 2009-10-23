#!/usr/bin/env python
# encoding: utf-8

# definition table is the top level table to define the custom form.
# it is the form definition.

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('definition',  pkey='id', name_long='!!Definition', rowcaption='name')
        self.sysFields(tbl,id=False)
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('code', size=':3',name_long='!!Code')
        tbl.column('name', size=':60',name_long='!!Name')
        tbl.column('pkg_table', size=':60',name_long='!!Package and Table')
        tbl.column('cols', 'I',name_long='!!Default columns')
        tbl.column('css', 'T',name_long='!!custom css')
        

