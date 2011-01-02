# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('artist', pkey='id', name_long='!!Artist',
                        name_plural='!!Artist', rowcaption='$fullname')
        self.sysFields(tbl)
        tbl.column('fullname', size=':40', name_long='!!Full name')
        tbl.column('is_band', 'B', name_long='!!Band')
        tbl.column('description', name_long='!!Description')
