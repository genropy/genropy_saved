#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('shortcut', pkey='keycode', name_long='!!Shortcut', name_plural='!!Shortcuts',caption_field='phrase',lookup=True)
        self.sysFields(tbl,id=False,counter=True)
        tbl.column('keycode' ,size=':10',name_long='!!Key')
        tbl.column('phrase' ,name_long='!!Phrase')
        tbl.column('groupcode' ,size=':20',name_long='!!Group')