# encoding: utf-8
from gnr.app.gnrdbo_legacy import GnrHTable

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
        
    def getFolderByCode(self,code=None):
        return self.query(where='$code=:code',code=code).fetch()
        
    def addRootFolder(self,code=None):
        if code and '.' in code:
            code=code.split('.')[-1].strip()
        if code and not self.getFolderByCode(code=code):
            record=dict(title=code,permalink=code.replace(' ','-'),code=code,child_code=code)
            self.insert(record)
            return record
        return None
        