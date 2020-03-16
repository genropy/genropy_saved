#!/usr/bin/env python
# encoding: utf-8
from builtins import object
from gnr.core.gnrdecorator import metadata

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('htag', pkey='id', name_long='!!Tag',
                        rowcaption='$code,$description',caption_field='hierarchical_description',
                        newrecord_caption='!!New tag',hierarchical_caption_field='description',
                        sysRecord_masterfield='hierarchical_code')
        self.sysFields(tbl,hierarchical='code:unique,description')
        #self.htableFields(tbl)
        #tbl.column('parent_code').relation('htag.code',onDelete='cascade')

        tbl.column('code',name_long='!!Code',validate_notnull=True,validate_nodup=True,
                    unmodifable=True)
        tbl.column('description',name_long='!!Description',validate_notnull=True)
        tbl.column('isreserved', 'B', name_long='!!Reserved')
        tbl.column('note',name_long='!!Notes')


    @metadata(mandatory=True)
    def sysRecord_user(self):
        return self.newrecord(code='user',description='User',
                                hierarchical_code='user')

    @metadata(mandatory=True)
    def sysRecord_admin(self):
        return self.newrecord(code='admin',description='Admin',
                            hierarchical_code='admin')

    @metadata(mandatory=True)
    def sysRecord_superadmin(self):
        return self.newrecord(code='superadmin',description='SuperAdmin',
                                isreserved=True,hierarchical_code='superadmin')

    @metadata(mandatory=True)
    def sysRecord__DEV_(self):
        return self.newrecord(code='_DEV_',description='Developer',
                                isreserved=True,hierarchical_code='_DEV_')

    @metadata(mandatory=True)
    def sysRecord__TRD_(self):
        return self.newrecord(code='_TRD_',description='Translator',
                                isreserved=True,hierarchical_code='_TRD_')

    @metadata(mandatory=True)
    def sysRecord__DOC_(self):
        return self.newrecord(code='_DOC_',description='Documentation',
                            isreserved=True,hierarchical_code='_DOC_')


    @metadata(mandatory=True)
    def sysRecord__SYSTEM_(self):
        return self.newrecord(code='_SYSTEM_',description='System',
                            isreserved=True,hierarchical_code='_SYSTEM_')

