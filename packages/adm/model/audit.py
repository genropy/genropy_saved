# encoding: utf-8

class Table(object):        
    def config_db(self, pkg):
        tbl =  pkg.table('audit',pkey='id',name_long='!!Audit',name_plural='!!Audit')
        self.sysFields(tbl)
        tbl.column('table_fullname',name_long='!!Table name')
        tbl.column('change_type',size='1',name_long='!!Change type',
                    values='I:Insert,U:Update,D:Delete')
        tbl.column('user',name_long='!!User')
        tbl.column('record_pkey',name_long='!!Record Pkey')
        tbl.column('version','L',name_long='!!Version')
        tbl.column('data','X',name_long='!!Data')
    
    def audit_I(self,tblobj,record):
        pass
    
    def audit_U(self,tblobj,record,old_record):
        pass
    
    def audit_D(self,tblobj,record):
        pass