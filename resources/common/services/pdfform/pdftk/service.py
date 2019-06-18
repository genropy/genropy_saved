#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-


from gnr.lib.services.pdfform import PdfFormService
from gnr.web.gnrbaseclasses import BaseComponent
import pypdftk


class Service(PdfFormService):

    def getFields(self, template=None):
        if not template:
            return
        templateSn = self.parent.storageNode(template)
        with templateSn.local_path() as template_path:
            fields = pypdftk.dump_data_fields(template_path)
        return [f['FieldName'] for f in fields if f['FieldFlags']!='0']

    def fillForm(self,template=None, values=None, output=None):
        if not template:
            return
        templateSn = self.parent.storageNode(template)
        outputSn = self.parent.storageNode(output)
        with templateSn.local_path() as template_path, outputSn.local_path() as output_path:
            pypdftk.fill_form(template_path, datas=values, out_file=output_path)

    def fillFromUserObject(self, userObject=None, table=None, record_id=None, output=None):
        data,meta = self.parent.db.table('adm.userobject').loadUserObject(userObjectIdOrCode=userObject,
                                                                        tbl=table,objtype='pdfform')
        table = meta['tbl']
        pdfFile = data['pdfFile']
        pdfFields = data['pdfFields']
        self.fillFromRecord(pdfFields=pdfFields, pdfFile=pdfFile, table=table, record_id=record_id, output=output)

    def fillFromRecord(self, pdfFields=None, pdfFile=None, table=None, record_id=None, output=None):
        values = pdfFields.values()
        columns = [v['field_path'] if v['field_path'].startswith('@') else '$%(field_path)s' %v  for v in values if v['field_path']]
        tblobj = self.parent.db.table(table)
        f = tblobj.query(columns=','.join(columns),where='$%s=:pk' %tblobj.pkey,pk=record_id).fetch()
        rec = dict(f[0])
        mapfields = {}
        for v in values:
            if v['field_path']:
                colobj = tblobj.column(v['field_path'])
                format = colobj.attributes.get('format')
                dtype = colobj.attributes.get('dtype')
                value = self.parent.currentPage.toText(rec[v['field_path'].replace('@','_').replace('.','_')] or '',
                                        dtype=dtype,format=format)
                mapfields[v['pdf_field']] = value
        self.fillForm(template=pdfFile, values=mapfields,
            output=output)

    def getForms(self, table=None):
        pkg, table = table.split('.')
        formsSn = self.parent.storageNode('pdf_forms:%s'%pkg, table)
        return formsSn.children() or []