#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('annotation')
        tbl.column('le_documentation_id',size='22' ,group='_',name_long='!!Documentation',
                    linked_service_zoomMode='page',
                    linked_entity='documentation:Documentation').relation('docu.documentation.id',relation_name='annotations',
                                                                mode='foreignkey',onDelete='cascade')