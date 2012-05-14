# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('developer',pkey='id',name_long='!!Developer',
                      name_plural='!!Developer',rowcaption='$name',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('company_id',size='22',group='_',name_long='Company id').relation('company.id', mode='foreignkey', onDelete='raise')
        tbl.column('user_id',size='22',group='_',name_long='User id').relation('adm.user.id', mode='foreignkey', onDelete='raise')
        tbl.column('customer_id',size='22',group='_',name_long='Customer id').relation('customer.id', mode='foreignkey', onDelete='raise')
        tbl.column('role',name_long='!!Role',values='!!D:Developer,U:User,S:Staff')
        tbl.column('email',name_long='!!Email')
        tbl.column('phone',name_long='!!Phone')
        tbl.column('skype',name_long='!!Skype')
        tbl.column('chat',name_long='!!Chat')
        