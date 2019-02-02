# encoding: utf-8
from builtins import object
from gnr.core.gnrdecorator import metadata

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('category', pkey='id', name_long='!!Category',
                        name_plural='!!Categories', rowcaption='$description')
        self.sysFields(tbl,hierarchical='description,child_code',counter=True)
        tbl.column('parent_code',group='_',name_long='Legacy parent code').relation('category.code')
        tbl.column('code',group='_',name_long='Legacy code')
        tbl.column('child_code',name_long='!!Code')
        tbl.column('description',name_long='!!Description')
        
    
    @metadata(doUpdate=True,columns='*,@parent_code.id AS old_parent_id')
    def touch_fix_htable(self,record=None,old_record=None):
        record['parent_id'] =  record['old_parent_id']


