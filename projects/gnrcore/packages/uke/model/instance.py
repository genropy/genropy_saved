# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('instance',pkey='id',name_long='!!Instance',
                      name_plural='!!Instances',rowcaption='$name',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('company_id',size='22',group='_',name_long='Company id').relation('company.id', mode='foreignkey', onDelete='raise',relation_name='instances')
        