# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('user_tag',pkey='id',name_long='!!User tag',
                      name_plural='!!User tags')
        self.sysFields(tbl)
        tbl.column('user_id',size='22',group='_',name_long='User',_sendback=True).relation('user.id', mode='foreignkey', 
                                                                            onDelete='cascade',relation_name='tags')
        tbl.column('tag_id',size='22',group='_',name_long='Tag id').relation('htag.id', mode='foreignkey', onDelete='raise',
                                                                          relation_name='users')
        tbl.aliasColumn('user',relation_path='@user_id.username')
        tbl.aliasColumn('fullname',relation_path='@user_id.fullname')
        tbl.aliasColumn('email',relation_path='@user_id.email')
        tbl.aliasColumn('tag_code',relation_path='@tag_id.code')
        tbl.aliasColumn('tag_description',relation_path='@tag_id.description')
        tbl.aliasColumn('tag_note',relation_path='@tag_id.note')

        #tbl.aliases(relation='@user_id',user='username')
    
    def trigger_onInserted(self, record_data):
        self.setUserAuthTags(record_data)
    
    def trigger_onUpdated(self, record_data, old_record):
        self.setUserAuthTags(record_data)
    
    def trigger_onDeleted(self, record):
        self.setUserAuthTags(record)
    
    def setUserAuthTags(self,record):
        user_id = record['user_id']
        rows = self.query(where='$user_id=:u_id',u_id=user_id,columns='$tag_code',addPkeyColumn=False).fetch()
        tags = ','.join([r['tag_code'] for r in rows])
        self.db.table('adm.user').batchUpdate(dict(auth_tags=tags),where='$id=:pkey',pkey=user_id)


        
