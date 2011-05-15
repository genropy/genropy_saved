# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('user_tag',pkey='id',name_long='!!User tag',
                      name_plural='!!User tags')
        self.sysFields(tbl)
        tbl.column('user_id',size='22',group='_',name_long='User').relation('user.id', mode='foreignkey', 
                                                                            onDelete='cascade',relation_name='tags')
        tbl.column('tag_id',size='22',group='_',name_long='Tag').relation('htag.id', mode='foreignkey', onDelete='raise',
                                                                          relation_name='users')
        tbl.aliasColumn('user',relation_path='@user_id.username')
        tbl.aliasColumn('tag_code',relation_path='@tag_id.code')
        tbl.aliasColumn('tag_description',relation_path='@tag_id.description')
        tbl.aliasColumn('tag_note',relation_path='@tag_id.note')

        #tbl.aliases(relation='@user_id',user='username')

        
