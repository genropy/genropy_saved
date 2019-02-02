# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('project',pkey='code',name_long='!!Projects',
                      name_plural='!!Projects',rowcaption='$code',caption_field='code')
        self.sysFields(tbl,id=False)
        tbl.column('code',name_long='!!Code',unique=True)
        tbl.column('description',name_long='!!Description')
        tbl.column('company_code',name_long='!!Company',group='_').relation('company.code', mode='foreignkey', 
                                                                        onDelete='raise',
                                                                        relation_name='projects')
        tbl.column('customer_id',size='22',name_long='!!Customer',group='_').relation('customer.id', mode='foreignkey',
                                                                                relation_name='projects',
                                                                                 onDelete='raise')
        tbl.column('languages' ,size=':50',name_long='!!Languages')