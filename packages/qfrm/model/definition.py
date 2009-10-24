#!/usr/bin/env python
# encoding: utf-8

# definition table is the top level table to define the custom form.
# it is the form definition.

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('definition',  pkey='id', name_long='!!Definition', rowcaption='long_name')
        self.sysFields(tbl,id=False)
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('code', size=':10',name_long='!!Code')
        tbl.column('pkg_table', size=':60',name_long='!!Package and Table')
        tbl.column('short_name', size=':30',name_long='!!Short Name')
        tbl.column('long_name', size=':60',name_long='!!Long Name')
        
        tbl.column('cols', 'I',name_long='!!Default section columns')
        tbl.column('rows', 'I',name_long='!!Default section rows')
        tbl.column('css', 'T',name_long='!!custom css')
        

