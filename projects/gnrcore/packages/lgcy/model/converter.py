#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('converter', rowcaption='$code',caption_field='code',name_long='!!Legacy converter',name_plural='!!Legacy converters')
        self.sysFields(tbl,id=True ,ins=False, mod=False, ldel=False)
        tbl.column('code', size=':80', name_long='!!Legacy code')

    def insertConversionRow(self, tblobj,pkey, code):
        if ',' in code:
            code = code.split(',')
        else:
            code = [code]
        fkey = '%s_%s' %(tblobj.fullname.replace('.','_'),tblobj.pkey)
        for lcode in code:
            r = self.newrecord(id=self.newPkeyValue(),code=lcode)
            r[fkey] = pkey
            self.raw_insert(r)


    def convertedFields(self):
        return [field for field in sorted(self.columns.keys()) if self.column(field).relatedTable()]


    def use_dbstores(self,**kwargs):
        return True