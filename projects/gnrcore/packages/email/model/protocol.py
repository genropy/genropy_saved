# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('protocol', rowcaption='code')
        tbl.column('code',size=':10',name_long='!!Protocol Code')
        tbl.column('description',size=':80',name_long='!!Description')
        tbl.column('direction',size='1',name_long='!!Direction') # I- Input, O - Output, B - Both 