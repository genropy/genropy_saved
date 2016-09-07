#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tblinfo_item', pkey='id', name_long='!!Tblinfo item', name_plural='!!Tblinfo items',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name' ,size=':30',name_long='!!Name')
        tbl.column('item_type' ,size=':5',name_long='!!Type',values=self.itemTypeValues())
        tbl.column('data',dtype='X',name_long='!!Data')
        tbl.column('user_group').relation('group.code',relation_name='tblinfo_items',mode='foreignkey')
        tbl.column('tbl').relation('tblinfo.tbl',relation_name='items',mode='foreignkey',onDelete='cascade')


    def itemTypeValues(self):
        return "AUTH:Authorizations,QTREE:Quick tree,FTREE:Full tree"