# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('item_category', pkey='id', name_long='!!Item category',
                        name_plural='!!Item category')
        self.sysFields(tbl)
        tbl.column('item_id', size='22', group='_', name_long='Item id').relation('item.id', mode='foreignkey',
                                                                                    relation_name='categories',
                                                                                  onDelete='cascade')
        tbl.column('category_id', size='22', group='_', name_long='Category id').relation('category.id',
                                                                                          relation_name='items',
                                                                                          mode='foreignkey',
                                                                                          onDelete='cascade')
        
