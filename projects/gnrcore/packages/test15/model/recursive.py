
# # encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        """test table recursive"""
        tbl = pkg.table('recursive', rowcaption='$code',pkey='id')
        self.sysFields(tbl)
        tbl.column('code', name_long='!!Code')
        tbl.column('description', name_long='!!Description')
        tbl.column('parent_id',size='22',group='_').relation('recursive.id', mode='foreignkey', 
                                                            onDelete='raise',relation_name='children')
