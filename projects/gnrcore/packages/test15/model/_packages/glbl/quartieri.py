
# # encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        """test table recursive"""
        tbl = pkg.table('quartieri', rowcaption='$code',pkey='id')
        self.sysFields(tbl)
        tbl.column('code', name_long='!!Code')
        tbl.column('description', name_long='!!Description')
