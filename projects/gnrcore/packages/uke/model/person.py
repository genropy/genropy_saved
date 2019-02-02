# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('person',pkey='id',name_long='!!Person',
                      name_plural='!!People',rowcaption='$name',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('company_code',group='_',name_long='Company').relation('company.code', mode='foreignkey',relation_name='people', onDelete='raise')
        tbl.column('user_id',size='22',group='_',name_long='User').relation('adm.user.id', mode='foreignkey',one_one='*', onDelete='raise')
        tbl.column('customer_id',size='22',group='_',name_long='Customer').relation('customer.id', mode='foreignkey',relation_name='people', onDelete='raise')
        tbl.column('role',name_long='!!Role',values='!!D:Developer,U:User,S:Staff')
        tbl.column('email',name_long='!!Email')
        tbl.column('phone',name_long='!!Phone')
        tbl.column('skype',name_long='!!Skype')
        tbl.column('chat',name_long='!!Chat')
        