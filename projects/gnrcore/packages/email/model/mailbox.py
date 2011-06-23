# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('example', rowcaption='hello_code')
        self.sysFields(tbl)
        self.htableFields(tbl)
        tbl.column('mailbox_name',size=':40',name_long='!!Mailbox Name')
        
