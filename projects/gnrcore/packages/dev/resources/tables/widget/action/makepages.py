# -*- coding: UTF-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
import os

caption = 'Make example pages'
tags = 'superadmin,_DEV_'
description='Make example pages'

DOCTPL ="""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(name)s</title>
<meta name="author" content="GenroPy">
</head>
<body>
    <h1>About %(name)s</h1>
    %(dfAsTable)s
</body>
</html>
"""

class Main(BaseResourceAction):
    def do(self):
        self.do_rebuild = False
        self.option_indent = 4
        f = self.tblobj.query(columns='*,$child_count').fetch()
        site = self.page.site
        widgetpedia_folder = site.getStaticPath('pkg:dev','webpages','widgetpedia')
        doc_it_folder = site.getStaticPath('pkg:dev','doc','IT','html','webpages','widgetpedia')
        #doc_en_folder = site.getStaticPath('pkg:dev','doc','EN','html','webpages','widgetpedia')

        for r in f:
            w_path = os.path.join(widgetpedia_folder,*r['hierarchical_name'].split('/'))
            d_path = os.path.join(doc_it_folder,*r['hierarchical_name'].split('/'))
            self.prepare_example_file(r,w_path)
            self.prepare_doc_file(r,d_path)

    def prepare_example_file(self,record,path):
        if record['child_count']>1:
            self._prepare_dir(path)
            path = os.path.join(path,'overview_%(name)s' %record)
        path = '%s.py' %path
        if not os.path.isfile(path) or self.do_rebuild:
            with open(path,'w') as f:
                self.write(f,'#!/usr/bin/python')
                self.write(f)
                self.write(f,'class GnrCustomWebPage(object):')
                self.write(f,'py_requires="gnrcomponents/doc_handler/doc_handler:DocHandler"',indent=1)
                self.write(f,'documentation=True',indent=1)
                self.write(f,'def main(self,root,**kwargs):',indent=1)
                self.write(f,'root.div("%(name)s")' %record,indent=2)


    def write(self, out_file, line=None, indent=0):
        line = line or ''
        out_file.write('%s%s\n'%(self.option_indent*indent*' ',line))


    def prepare_doc_file(self,record,path):
        if record['child_count']>1:
            self._prepare_dir(path)
            path = os.path.join(path,'overview_%(name)s' %record)
        path = '%s.html' %path
        if not os.path.isfile(path) or self.do_rebuild:
            print 'doing',path
            record['dfAsTable'] = self.dfAsTable(record)
            with open(path,'w') as f:
                self.write(f,DOCTPL %record)

    def dfAsTable(self,record):
        fields = self.tblobj.df_getFieldsRows(pkey=record['id'])
        rows = []
        for v in fields:
            rows.append('<tr><td>%(code)s</td><td>(%(data_type)s)</td></tr>' %v)
        return "<table id='PARSTABLE'>\n<tbody>%s</tbody>\n</table>" %'\n '.join(rows)
          

    def _prepare_dir(self,path):
        if not os.path.isdir(path):
            os.makedirs(path)
