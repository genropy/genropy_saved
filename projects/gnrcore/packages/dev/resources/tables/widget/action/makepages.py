# -*- coding: utf-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
import os
import shutil

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
<link rel="stylesheet" type="text/css" href="%(widgetpedia_css)s">
<link rel="stylesheet" type="text/css" href="%(widgetpedia_static_css)s">
</head>
<body>
    
    %(summary)s
    %(dfAsTable)s
</body>
</html>
"""

class Main(BaseResourceAction):
    def do(self):
        self.do_rebuild = self.batch_parameters.get('do_rebuild',False)

        self.option_indent = 4
        f = self.tblobj.query(columns='*,$child_count').fetch()
        site = self.page.site
        widgetpedia_folder = site.getStaticPath('pkg:dev','webpages','widgetpedia')
        doc_it_folder = site.getStaticPath('pkg:dev','doc','IT','html','webpages','widgetpedia')
        self.widgetpedia_css = site.getStaticPath('pkg:dev','doc','widgetpedia.css')
        self.widgetpedia_static_css = site.getStaticUrl('pkg:dev','doc','widgetpedia.css')
        #doc_en_folder = site.getStaticPath('pkg:dev','doc','EN','html','webpages','widgetpedia')
        if self.do_rebuild:
            shutil.rmtree(doc_it_folder)
        for r in f:
            w_path = os.path.join(widgetpedia_folder,*r['hierarchical_name'].lower().split('/'))
            d_path = os.path.join(doc_it_folder,*r['hierarchical_name'].lower().split('/'))
            self.prepare_example_file(r,w_path)
            self.prepare_doc_file(r,d_path)

    def prepare_example_file(self,record,path):
        lowername = record['name'].lower()
        if record['child_count']>1:
            self._prepare_dir(path)
            path = os.path.join(path,'_overview_%s' %lowername)
        path = '%s.py' %path
        if not os.path.isfile(path):
            with open(path,'w') as f:
                self.write(f,'#!/usr/bin/python')
                self.write(f)
                self.write(f,'class GnrCustomWebPage(object):')
                self.write(f,'py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer"',indent=1)
                self.write(f,'def main(self,root,**kwargs):',indent=1)
                self.write(f,'root.div("%(name)s")' %record,indent=2)


    def write(self, out_file, line=None, indent=0):
        line = line or ''
        out_file.write('%s%s\n'%(self.option_indent*indent*' ',line))


    def prepare_doc_file(self,record,path):
        lowername = record['name'].lower()
        if record['child_count']>1:
            self._prepare_dir(path)
            path = os.path.join(path,'_overview_%s' %lowername)
        path = '%s.html' %path
        record['summary'] = record['summary'] or '<h1>%s</h1>' %record['name']
        if not os.path.isfile(path):
            record['widgetpedia_css'] = os.path.relpath(self.widgetpedia_css,os.path.dirname(path))
            record['widgetpedia_static_css'] = self.widgetpedia_static_css
            record['dfAsTable'] = self.dfAsTable(record)
            with open(path,'w') as f:
                self.write(f,DOCTPL %record)

    def dfAsTable(self,record):
        fields = self.getInheritedDocRows(pkey=record['id'])
        rows = []
        for v in fields:
            v['documentation'] = v['documentation'] or '*missing*'
            rows.append('<tr><td>%(code)s</td><td>%(datatype)s</td><td>%(documentation)s</td></tr>' %v)
        return """
<table id='PARSTABLE' class="documentationTable">
    <thead>
        <tr><th>Parameter</th><th>Type</th><th>Documentation</th></tr>
    </thead>
    <tbody>%s</tbody>
</table>""" %'\n '.join(rows)

    def getInheritedDocRows(self,pkey=None,**kwargs):
        where="$%s=:p" %self.tblobj.pkey
        p = pkey
        columns='*,$docrows'
        hpkey = self.tblobj.readColumns(columns='$hierarchical_pkey' ,pkey=pkey)
        p = hpkey
        where =  " ( :p = $hierarchical_pkey ) OR ( :p ILIKE $hierarchical_pkey || :suffix) "
        order_by='$hlevel'
        result = []
        f = self.tblobj.query(where=where,p=p,suffix='/%%',order_by=order_by,columns=columns).fetch()
        result = Bag()
        for r in f:
            for v in list(Bag(r['docrows']).values()):
                result.setItem(v['code'],v)
        return [v.asDict(ascii=True) for v in list(result.values())]          

    def _prepare_dir(self,path):
        if not os.path.isdir(path):
            os.makedirs(path)

    def table_script_parameters_pane(self,pane,extra_parameters=None,record_count=None,**kwargs):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.checkbox(value='^.do_rebuild',label='Rebuild')