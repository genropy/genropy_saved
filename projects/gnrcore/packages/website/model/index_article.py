#!/usr/bin/env python
# encoding: utf-8
# VISTOAL: 291008
class Table(object):
   
    def config_db(self, pkg):
        """website.index_article"""
        tbl =  pkg.table('index_article', name_plural = u'!!Index articles', pkey='id',name_long=u'!!Index articles', rowcaption='@page_id.title')
        self.sysFields(tbl)
        tbl.column('page_id', name_long='!!Page').relation('website.page.id',mode='foreignkey',onDelete='CASCADE')
        tbl.column('_row_counter','L',name_long='!!N')

