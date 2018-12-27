# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('documentation_visit', pkey='id', name_long='!!Documentation visit', name_plural='!!Documentation visits')
        self.sysFields(tbl)
        tbl.column('visitor_identifier', group='_', name_long='!!Visitor identifier')
        tbl.column('documentation_id',size='22', group='_', name_long='!!Doc.Id'
                    ).relation('documentation.id', relation_name='pages', mode='foreignkey', onDelete='cascade')

        tbl.column('visit_level',size='2', group='_', name_long='!!Visit level',
                    values='!!01:Quick view,02:Have questions,09:Okay')
        tbl.column('notes', name_long='!!Notes')


