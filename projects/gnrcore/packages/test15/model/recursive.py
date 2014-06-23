
# # encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        """test table recursive"""
        tbl = pkg.table('recursive', rowcaption='$description',caption_field='description',pkey='id')
        self.sysFields(tbl,hierarchical='description')
        tbl.column('description', name_long='!!Description')
        
