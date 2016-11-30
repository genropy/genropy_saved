#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrdecorator import metadata

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('htag', pkey='id', name_long='!!Tag',
                        rowcaption='$code,$description',caption_field='hierarchical_description',
                        newrecord_caption='!!New tag',hierarchical_caption_field='description')
        self.sysFields(tbl,hierarchical='code,description')
        #self.htableFields(tbl)
        #tbl.column('parent_code').relation('htag.code',onDelete='cascade')

        tbl.column('code',name_long='!!Code',validate_notnull=True,validate_nodup=True)
        tbl.column('description',name_long='!!Description',validate_notnull=True)
        tbl.column('isreserved', 'B', name_long='!!Reserved')
        tbl.column('note',name_long='!!Notes')


    @metadata(mandatory=True)
    def sysRecord_user(self):
        return self.newrecord(code='user',description='User')

    @metadata(mandatory=True)
    def sysRecord_admin(self):
        return self.newrecord(code='admin',description='Admin')

    @metadata(mandatory=True)
    def sysRecord_superadmin(self):
        return self.newrecord(code='superadmin',description='SuperAdmin',isreserved=True)

    @metadata(mandatory=True)
    def sysRecord__DEV_(self):
        return self.newrecord(code='_DEV_',description='Developer',isreserved=True)

    @metadata(mandatory=True)
    def sysRecord__TRD_(self):
        return self.newrecord(code='_TRD_',description='Translator',isreserved=True)

    @metadata(mandatory=True)
    def sysRecord__DOC_(self):
        return self.newrecord(code='_DOC_',description='Documentation',isreserved=True)


    def adaptToNewHtable(self):
        if self.query(where='$hierarchical_pkey IS NULL').count():
            f = self.query(order_by='$code',columns='*,@parent_code.id AS calc_parent_id',addPkeyColumn=False).fetch()
            for r in f:
                r = dict(r)
                parent_id = r.pop('calc_parent_id')

                old_rec = dict(r)
                r['parent_id'] = parent_id
                self.update(r,old_rec)
            self.db.commit()
