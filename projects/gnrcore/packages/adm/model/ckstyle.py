#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('ckstyle', pkey='id', name_long='Ckeditor style', name_plural='!!Ckeditor styles',caption_field='name',lookup=True)
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('element' ,values='div,span,h1,h2,h3',name_long='!!Dom element',name_short='Element')
        tbl.column('styles',name_long='!!Styles')
        tbl.column('attributes',name_long='!!Attributes')
        tbl.column('stylegroup',name_long='!!Group')