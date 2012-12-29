#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('menu_page_dir', pkey='id', name_long='Page dirs',caption_field='hierarchical_pagename',rowcaption='$hierarchical_pagename')
        self.sysFields(tbl,counter='dir_id')
        tbl.column('dir_id',size='22' ,group='_',name_long='!!Directory').relation('menu_dir.id',relation_name='dir_pages',mode='foreignkey',onDelete='cascade')
        tbl.column('page_id',size='22' ,group='_',name_long='!!Pages').relation('menu_page.id',relation_name='page_dirs',mode='foreignkey',onDelete='cascade')
        tbl.column('label' ,name_long='!!Label')
        tbl.column('tags' ,name_long='!!Authorization tags')
        tbl.formulaColumn('hierarchical_pagename',"@dir_id.hierarchical_label || '/' ||$label")
        tbl.aliasColumn('dir_hierarchical_pkey',relation_path='@dir_id.hierarchical_pkey')
        tbl.aliasColumn('page_label',relation_path='@page_id.label')
        tbl.aliasColumn('page_filepath',relation_path='@page_id.filepath')
        tbl.aliasColumn('page_tbl',relation_path='@page_id.tbl')
        tbl.aliasColumn('page_metadata',relation_path='@page_id.metadata')