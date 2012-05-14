# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('package',pkey='id',name_long='!!Package',
                      name_plural='!!Packages')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('description',name_long='!!Description')
        tbl.column('project_id',size='22',group='_',name_long='Project id').relation('project.id', mode='foreignkey', 
                                                                                        onDelete='raise',
                                                                                        relation_name='packages')
