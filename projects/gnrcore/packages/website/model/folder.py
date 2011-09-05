# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable

class Table(GnrHTable):
    def config_db(self, pkg):
        tbl =  pkg.table('folder',  pkey='id',name_long='!!Folder',
                      name_plural='!!Folders',rowcaption='$code')
        self.sysFields(tbl)
        self.htableFields(tbl)
        tbl.column('title', size=':30',name_long = '!!Title', indexed=True)
        tbl.column('extended_title', size=':50',name_long = '!!Extended Title')
        tbl.column('position', dtype='I',name_long = '!!Position')
        tbl.column('publish',dtype='DH', name_long = '!!Published on')

    def trigger_onInserted(self, record):
        pages_table=self.db.table('website.page')
        pages_table.insert(dict(folder=record['id'],title=record['title'],permalink='index',content='Fill With your own content'))
        
    def treeRowCaption(self):
        return '$description'