# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('message_address',pkey='id',name_long='!!Message address',
                      name_plural='!!Message addresses')
        self.sysFields(tbl)
        tbl.column('message_id',size='22',name_long='!!Message id').relation('email.message.id', mode='foreignkey', 
                                                                            relation_name='addresses',deferred=True)
        tbl.column('address',name_long='!!Address',indexed=True)
        tbl.column('reason',name_long='!!Reason')