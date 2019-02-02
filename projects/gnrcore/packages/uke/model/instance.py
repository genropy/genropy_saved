#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('instance', pkey='id', name_long='!!Instance', name_plural='!!Instances',caption_field='instance_name')
        self.sysFields(tbl)
        tbl.column('instance_name' ,name_long='!!Name')
        tbl.column('customer_id',size='22' ,group='_',name_long='!!Customer').relation('customer.id',relation_name='instances',
                                                                                            mode='foreignkey',onDelete='raise')
        tbl.column('description',name_long='!!Description')


    def getInstanceRecord(self):
        f = self.query(limit=1,).fetch()
        if f:
            r = dict(f[0])
            return r
        import os
        r = dict(instance_name=os.path.split(self.db.application.instanceFolder)[1])
        self.insert(r)
        self.db.commit()
        return r