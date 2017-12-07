#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('batch_log', pkey='id', name_long='!!Batch log', 
                        name_plural='!!Batch logs',caption_field='log_caption')
        self.sysFields(tbl)
        tbl.column('title', name_long='!!Batch title')
        tbl.column('page_id',size='22', group='_', name_long='!!Page'
                    ).relation('adm.served_page.page_id', relation_name='batches', 
                                onDelete='raise') #no foreignkey
        tbl.column('start_ts', dtype='DH', name_long='!!Start ts')
        tbl.column('end_ts', dtype='DH', name_long='!!End ts')
        tbl.column('notes', name_long='!!Notes')
        tbl.column('logbag', dtype='X', name_long='!!Log')
        tbl.column('tbl', name_long='!!Table')
        tbl.formulaColumn('log_caption',"$tbl || $title")

