# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('staff', name_short='staff', name_long='Staff',name_plural='Staff',
                            pkey='id',rowcaption='@user_id.username')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        self.sysFields(tbl, id=False)
        tbl.column('user_id',size='22',name_long='User Info',group='_',
                    ).relation('adm.user.id',mode='foreignkey',one_one=True,onDelete='cascade')
        tbl.column('role',size=':30',group='04',name_long='!!Role')       
        tbl.column('phone',name_long='!!Phone') 
        tbl.aliasColumn('fullname',relation_path='@card_id.fullname',name_long='!!Full name',group='01')
        tbl.aliasColumn('username',relation_path='@user_id.username',name_long='!!Username',group='02')
        tbl.aliasColumn('email',relation_path='@user_id.email',group='03')