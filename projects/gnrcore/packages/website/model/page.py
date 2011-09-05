#!/usr/bin/env python
# encoding: utf-8
# VISTOAL: 291008
class Table(object):
   
    def config_db(self, pkg):
        """website.page"""
        tbl =  pkg.table('page', name_plural = u'!!Pages', pkey='id',name_long=u'!!Page', rowcaption='$title')
        self.sysFields(tbl)
        tbl.column('title', size=':30',name_long = '!!Title',base_view=True)
        tbl.column('extended_title', name_long = '!!Extended Title')
        tbl.column('permalink', size=':254',name_long = '!!Permalink')
        tbl.column('content',name_long = '!!Content')
        tbl.column('position', dtype='I',name_long = '!!Position')
        tbl.column('publish',dtype='DH', name_long = '!!Published on')
        tbl.column('folder',size=':22',name_long='!!Folder').relation('website.folder.id',
                                                                        relation_name='pages',
                                                                        mode='foreignkey',
                                                                        onDelete='CASCADE')

    def trigger_onInserting(self, record):
        if record['content']:
            record['content'] = record['content'].replace('../_site','/_site')

    def trigger_onUpdating(self, record,old_record):
        if record['content']:
            record['content'] = record['content'].replace('../_site','/_site')
        
    def folder_view(self,struct):
        r = struct.view().rows()
        r.cell('@folder.title',name='Folder',width='30%')
        r.cell('position',width='10%')
        r.cell('title',name='Title',width='30%')
        r.cell('permalink',name='Permalink',width='30%')
        return struct